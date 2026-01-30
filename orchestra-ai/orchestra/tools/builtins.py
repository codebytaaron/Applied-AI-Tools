from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from orchestra.tools.registry import ToolRegistry, ToolSpec

def install_builtin_tools(reg: ToolRegistry, data_dir: str) -> None:
    base = Path(data_dir).resolve()
    (base / "files").mkdir(parents=True, exist_ok=True)

    # Calculator (safe-ish)
    calc_spec = ToolSpec(
        name="calc",
        description="Evaluate a simple math expression (numbers, + - * / ^, parentheses).",
        schema={"type":"object","properties":{"expr":{"type":"string"}},"required":["expr"]},
    )

    def calc(args: dict) -> Any:
        expr = str(args.get("expr",""))
        if len(expr) > 200:
            return {"error":"Expression too long"}
        if re.search(r"[^0-9\s\+\-\*\/\^\(\)\.,]", expr):
            return {"error":"Invalid characters"}
        expr = expr.replace("^","**")
        try:
            val = eval(expr, {"__builtins__": {}}, {"math": math})
            return {"value": float(val)}
        except Exception as e:
            return {"error": str(e)}

    reg.register(calc_spec, calc)

    # HTTP GET (read-only)
    http_spec = ToolSpec(
        name="http_get",
        description="Fetch a URL via HTTP GET and return the first N characters.",
        schema={"type":"object","properties":{"url":{"type":"string"},"max_chars":{"type":"integer","default":2000}},"required":["url"]},
    )

    def http_get(args: dict) -> Any:
        url = str(args.get("url",""))
        max_chars = int(args.get("max_chars", 2000))
        if not (url.startswith("http://") or url.startswith("https://")):
            return {"error":"URL must start with http:// or https://"}
        req = Request(url, headers={"User-Agent":"orchestra-ai/0.1"})
        with urlopen(req, timeout=10) as resp:
            data = resp.read(max(0, min(max_chars, 20000)))
        return {"status": 200, "text": data.decode("utf-8", errors="replace")}

    reg.register(http_spec, http_get)

    # File tool (sandboxed)
    write_spec = ToolSpec(
        name="file_write",
        description="Write a text file under ./data/files (sandboxed).",
        schema={"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]},
    )
    read_spec = ToolSpec(
        name="file_read",
        description="Read a text file under ./data/files (sandboxed).",
        schema={"type":"object","properties":{"path":{"type":"string"},"max_chars":{"type":"integer","default":4000}},"required":["path"]},
    )
    list_spec = ToolSpec(
        name="file_list",
        description="List files under ./data/files (sandboxed).",
        schema={"type":"object","properties":{"prefix":{"type":"string","default":""}},"required":[]},
    )

    def _safe_path(rel: str) -> Path:
        rel = rel.strip().lstrip("/").replace("..","")
        p = (base / "files" / rel).resolve()
        if not str(p).startswith(str((base / "files").resolve())):
            raise ValueError("Unsafe path")
        return p

    def file_write(args: dict) -> Any:
        p = _safe_path(str(args.get("path","")))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(args.get("content","")), encoding="utf-8")
        return {"ok": True, "path": str(p)}

    def file_read(args: dict) -> Any:
        p = _safe_path(str(args.get("path","")))
        if not p.exists():
            return {"error":"Not found"}
        max_chars = int(args.get("max_chars", 4000))
        txt = p.read_text(encoding="utf-8", errors="replace")
        return {"path": str(p), "text": txt[:max_chars]}

    def file_list(args: dict) -> Any:
        prefix = str(args.get("prefix","")).strip().lstrip("/").replace("..","")
        start = _safe_path(prefix) if prefix else (base / "files").resolve()
        if start.is_file():
            start = start.parent
        out = []
        for fp in sorted(start.rglob("*")):
            if fp.is_file():
                out.append(str(fp.relative_to((base / "files").resolve())))
        return {"files": out}

    reg.register(write_spec, file_write)
    reg.register(read_spec, file_read)
    reg.register(list_spec, file_list)

    # Text utils
    summarize_spec = ToolSpec(
        name="text_stats",
        description="Return basic statistics about a text (chars, words, lines).",
        schema={"type":"object","properties":{"text":{"type":"string"}},"required":["text"]},
    )
    def text_stats(args: dict) -> Any:
        t = str(args.get("text",""))
        return {"chars": len(t), "words": len(t.split()), "lines": t.count("\n")+1 if t else 0}
    reg.register(summarize_spec, text_stats)
