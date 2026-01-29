function escapeCSV(value) {
  const s = String(value ?? "");
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

export function toJSON(rows) {
  return JSON.stringify(rows, null, 2);
}

export function toCSV(rows) {
  if (!rows || rows.length === 0) return "";
  const keys = Array.from(
    rows.reduce((set, r) => {
      Object.keys(r).forEach((k) => set.add(k));
      return set;
    }, new Set())
  );

  const header = keys.join(",");
  const lines = rows.map((r) => keys.map((k) => escapeCSV(r[k])).join(","));
  return [header, ...lines].join("\n");
}
