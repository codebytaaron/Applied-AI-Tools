function slugify(s) {
  return String(s || "")
    .toLowerCase()
    .trim()
    .replace(/['"]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function detectFormat(text) {
  const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);

  if (lines.some((l) => l.includes("|") && l.trim().startsWith("|"))) return "md";
  if (lines.some((l) => l.includes("\t"))) return "tsv";
  if (lines.some((l) => l.includes(",") && !l.includes("\t"))) return "csv";
  return "spaced";
}

function parseMarkdownTable(lines) {
  // expects:
  // | Rank | Player | City |
  // | --- | --- | --- |
  // | 1 | Name | Town |
  const tableLines = lines.filter((l) => l.trim().startsWith("|"));
  if (tableLines.length < 2) return { header: null, rows: [] };

  const header = tableLines[0]
    .split("|")
    .map((s) => s.trim())
    .filter(Boolean);

  const dataLines = tableLines.slice(2);
  const rows = dataLines.map((l) =>
    l
      .split("|")
      .map((s) => s.trim())
      .filter(Boolean)
  );

  return { header, rows };
}

function splitSpacedLine(line) {
  // Split by 2+ spaces to preserve values with single spaces (like "Old Greenwich")
  return line.trim().split(/\s{2,}/g).map((s) => s.trim());
}

function parseDelimited(lines, delim) {
  const out = [];
  for (const line of lines) {
    const parts = line.split(delim).map((s) => s.trim());
    out.push(parts);
  }
  return out;
}

function guessHeader(lines) {
  // Look for a header-ish line containing common column names
  const headerWords = ["rank", "player", "name", "city", "school", "type", "rating"];
  for (const line of lines.slice(0, 25)) {
    const low = line.toLowerCase();
    const hits = headerWords.filter((w) => low.includes(w)).length;
    if (hits >= 3) return line;
  }
  return null;
}

function normalizeKey(k) {
  return String(k || "")
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "_")
    .replace(/[^a-z0-9_]/g, "");
}

function coerceRank(v) {
  if (v == null) return null;
  const s = String(v).trim();
  const m = s.match(/#?(\d+)/);
  return m ? Number(m[1]) : null;
}

function coerceNumber(v) {
  if (v == null) return null;
  const s = String(v).trim();
  const m = s.match(/-?\d+(\.\d+)?/);
  return m ? Number(m[0]) : null;
}

export function parseInput(rawText, opts = {}) {
  const { columns = null, addId = true, meta = {} } = opts;

  const linesAll = rawText
    .replace(/\u00a0/g, " ")
    .split(/\r?\n/)
    .map((l) => l.replace(/\s+$/g, ""))
    .filter((l) => l.trim().length > 0);

  const format = detectFormat(rawText);
  let header = null;
  let rows = [];

  if (format === "md") {
    const parsed = parseMarkdownTable(linesAll);
    header = parsed.header;
    rows = parsed.rows;
  } else if (format === "tsv") {
    const headerLine = guessHeader(linesAll);
    if (headerLine) {
      const idx = linesAll.indexOf(headerLine);
      header = headerLine.split("\t").map((s) => s.trim());
      rows = parseDelimited(linesAll.slice(idx + 1), "\t");
    } else {
      header = null;
      rows = parseDelimited(linesAll, "\t");
    }
  } else if (format === "csv") {
    const headerLine = guessHeader(linesAll);
    if (headerLine) {
      const idx = linesAll.indexOf(headerLine);
      header = headerLine.split(",").map((s) => s.trim());
      rows = parseDelimited(linesAll.slice(idx + 1), ",");
    } else {
      header = null;
      rows = parseDelimited(linesAll, ",");
    }
  } else {
    // spaced
    const headerLine = guessHeader(linesAll);
    if (headerLine) {
      const idx = linesAll.indexOf(headerLine);
      header = splitSpacedLine(headerLine);
      rows = linesAll.slice(idx + 1).map(splitSpacedLine);
    } else {
      header = null;
      rows = linesAll.map(splitSpacedLine);
    }
  }

  const finalHeader = (columns && columns.length > 0)
    ? columns
    : (header && header.length > 0 ? header : null);

  const results = [];
  for (const r of rows) {
    // skip separators and junk
    const joined = r.join(" ").toLowerCase();
    if (joined.includes("---")) continue;
    if (r.length === 1 && r[0].length < 2) continue;

    const obj = {};

    if (finalHeader) {
      for (let i = 0; i < finalHeader.length; i++) {
        const key = normalizeKey(finalHeader[i]);
        obj[key] = r[i] ?? "";
      }
    } else {
      // fallback columns: col1..colN
      for (let i = 0; i < r.length; i++) obj[`col${i + 1}`] = r[i] ?? "";
    }

    // Coercions for common keys
    if ("rank" in obj) obj.rank = coerceRank(obj.rank);
    if ("rating" in obj) obj.rating = coerceNumber(obj.rating);

    // Auto id
    if (addId) {
      const base =
        obj.player || obj.name || obj.full_name || obj.col2 || obj.col1 || "row";
      const id = slugify(`${base}-${obj.rank ?? results.length + 1}`);
      obj.id = id;
    }

    // Attach metadata
    for (const [k, v] of Object.entries(meta || {})) obj[k] = v;

    results.push(obj);
  }

  // If rank exists, sort by it
  if (results.length && results[0].rank != null) {
    results.sort((a, b) => (a.rank ?? 999999) - (b.rank ?? 999999));
  }

  return results;
}
