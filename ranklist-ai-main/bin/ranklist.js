#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parseInput } from "../src/parse.js";
import { toCSV, toJSON } from "../src/output.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function help() {
  console.log(`
ranklist - convert ranking text into JSON or CSV

Usage:
  ranklist --in input.txt --out rankings.json --format json
  ranklist --in input.txt --format csv
  cat input.txt | ranklist --format json

Options:
  --in        Input file path (optional if piping stdin)
  --out       Output file path (optional, prints to stdout if omitted)
  --format    json | csv (default: json)
  --columns   Comma list of columns if your text has no header
              Example: "rank,player,city,school,type,rating"
  --meta      Add metadata fields as key=value pairs
              Example: --meta state=CT --meta class=2027 --meta gender=Men
  --no-id     Disable auto id field
  --help      Show help

Tips:
  Works best with:
  - TSV (tabs)
  - CSV
  - Markdown tables
  - Aligned text with 2+ spaces between columns
`.trim());
}

function getArg(flag) {
  const idx = process.argv.indexOf(flag);
  if (idx === -1) return null;
  return process.argv[idx + 1] ?? null;
}

function hasFlag(flag) {
  return process.argv.includes(flag);
}

function getMetaArgs() {
  const meta = {};
  for (let i = 0; i < process.argv.length; i++) {
    if (process.argv[i] === "--meta") {
      const pair = process.argv[i + 1] || "";
      const eq = pair.indexOf("=");
      if (eq > 0) {
        const k = pair.slice(0, eq).trim();
        const v = pair.slice(eq + 1).trim();
        if (k) meta[k] = v;
      }
    }
  }
  return meta;
}

async function readStdin() {
  return new Promise((resolve) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data));
  });
}

async function main() {
  if (hasFlag("--help")) {
    help();
    process.exit(0);
  }

  const inPath = getArg("--in");
  const outPath = getArg("--out");
  const format = (getArg("--format") || "json").toLowerCase();
  const columnsArg = getArg("--columns");
  const addId = !hasFlag("--no-id");
  const meta = getMetaArgs();

  let raw = "";
  if (inPath) {
    raw = fs.readFileSync(path.resolve(process.cwd(), inPath), "utf8");
  } else {
    if (process.stdin.isTTY) {
      console.error("No --in file provided and no stdin piped. Use --help.");
      process.exit(1);
    }
    raw = await readStdin();
  }

  const columns = columnsArg
    ? columnsArg.split(",").map((s) => s.trim()).filter(Boolean)
    : null;

  const rows = parseInput(raw, { columns, addId, meta });

  let out = "";
  if (format === "csv") out = toCSV(rows);
  else if (format === "json") out = toJSON(rows);
  else {
    console.error("Invalid --format. Use json or csv.");
    process.exit(1);
  }

  if (outPath) {
    fs.writeFileSync(path.resolve(process.cwd(), outPath), out, "utf8");
  } else {
    process.stdout.write(out + "\n");
  }
}

main().catch((err) => {
  console.error("Error:", err?.message || err);
  process.exit(1);
});
bin/ranklist.js
