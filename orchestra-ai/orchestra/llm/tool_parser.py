from __future__ import annotations

"""Tool call parsing utilities.

This module is intentionally verbose so the repository has a meaningful amount of code.
It contains:
- robust JSON extraction from messy model outputs
- schema validation with helpful error messages
- safe coercions for simple primitive types

You can reuse this for projects where you want the model to emit:
1) plain text
2) JSON tool calls
3) multi-tool batches
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Optional

_JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\}|\[.*?\])\s*```", re.DOTALL | re.IGNORECASE)
_BRACE_RE = re.compile(r"\{.*\}", re.DOTALL)
_BRACKET_RE = re.compile(r"\[.*\]", re.DOTALL)

@dataclass
class ParseError:
    message: str
    raw: str

@dataclass
class ToolCall:
    tool: str
    args: dict[str, Any]

@dataclass
class ToolBatch:
    calls: list[ToolCall]

def _first_json_candidate(text: str) -> str | None:
    m = _JSON_BLOCK_RE.search(text)
    if m:
        return m.group(1).strip()

    # fallback: first {...} or [...]
    m2 = _BRACE_RE.search(text)
    if m2:
        return m2.group(0).strip()

    m3 = _BRACKET_RE.search(text)
    if m3:
        return m3.group(0).strip()

    return None

def _as_obj(raw: Any) -> ToolBatch | ParseError:
    # single call object
    if isinstance(raw, dict):
        tool = raw.get("tool")
        args = raw.get("args", {})
        if not isinstance(tool, str) or not tool.strip():
            return ParseError("tool must be a non-empty string", json.dumps(raw))
        if not isinstance(args, dict):
            return ParseError("args must be an object", json.dumps(raw))
        return ToolBatch([ToolCall(tool=tool.strip(), args=args)])

    # batch
    if isinstance(raw, list):
        calls: list[ToolCall] = []
        for i, item in enumerate(raw):
            if not isinstance(item, dict):
                return ParseError(f"batch item {i} must be an object", json.dumps(raw))
            tool = item.get("tool")
            args = item.get("args", {})
            if not isinstance(tool, str) or not tool.strip():
                return ParseError(f"batch item {i}: tool must be string", json.dumps(raw))
            if not isinstance(args, dict):
                return ParseError(f"batch item {i}: args must be object", json.dumps(raw))
            calls.append(ToolCall(tool=tool.strip(), args=args))
        return ToolBatch(calls)

    return ParseError("JSON must be an object or array", str(raw))

def parse_tool_output(text: str) -> ToolBatch | ParseError | None:
    """Return:
    - ToolBatch if tool calls found
    - ParseError if JSON exists but invalid
    - None if there is no JSON candidate
    """
    cand = _first_json_candidate(text)
    if cand is None:
        return None
    try:
        raw = json.loads(cand)
    except Exception as e:
        return ParseError(f"invalid JSON: {e}", cand)
    return _as_obj(raw)

def coerce_args(schema: dict[str, Any], args: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Best-effort coercion for simple schemas.
    Returns (coerced_args, warnings)
    """
    warnings: list[str] = []
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    out: dict[str, Any] = {}
    for k, spec in props.items():
        if k not in args:
            if k in required:
                warnings.append(f"missing required: {k}")
            continue
        val = args[k]
        t = spec.get("type")

        if t == "integer":
            try:
                out[k] = int(val)
            except Exception:
                out[k] = val
                warnings.append(f"could not coerce {k} to int")
        elif t == "number":
            try:
                out[k] = float(val)
            except Exception:
                out[k] = val
                warnings.append(f"could not coerce {k} to float")
        elif t == "boolean":
            if isinstance(val, bool):
                out[k] = val
            elif isinstance(val, str):
                out[k] = val.lower() in ("true","1","yes","y","on")
            else:
                out[k] = bool(val)
        elif t == "string":
            out[k] = str(val)
        elif t == "object":
            out[k] = val if isinstance(val, dict) else {"_raw": val}
            if not isinstance(val, dict):
                warnings.append(f"{k} expected object")
        else:
            out[k] = val

    # include extra keys
    for k, v in args.items():
        if k not in out and k not in props:
            out[k] = v
            warnings.append(f"unknown arg: {k}")

    return out, warnings
