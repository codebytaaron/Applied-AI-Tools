import React, { useMemo, useState } from "react";

type Tone = "professional" | "friendly" | "urgent";

function clean(s: string) {
  return (s || "").replace(/\s+/g, " ").trim();
}

function titleCase(s: string) {
  const t = clean(s);
  if (!t) return "";
  return t.charAt(0).toUpperCase() + t.slice(1);
}

function pickKeywords(text: string) {
  const t = (text || "").toLowerCase();
  const candidates = [
    { k: "invoice", hits: ["invoice", "billing", "payment", "pay"] },
    { k: "booking", hits: ["book", "booking", "schedule", "appointment", "reserve"] },
    { k: "proposal", hits: ["proposal", "quote", "estimate", "pricing"] },
    { k: "update", hits: ["update", "status", "progress"] },
    { k: "meeting", hits: ["meet", "meeting", "call", "zoom"] },
    { k: "contract", hits: ["contract", "agreement", "signature", "sign"] }
  ];

  const found: string[] = [];
  for (const c of candidates) {
    if (c.hits.some((h) => t.includes(h))) found.push(c.k);
  }
  return found.slice(0, 2);
}

function generateSubjectLines(opts: {
  biz: string;
  purpose: string;
  tone: Tone;
  includePersonal: boolean;
}) {
  const biz = titleCase(opts.biz) || "Quick";
  const purpose = clean(opts.purpose);
  const tone = opts.tone;

  const kws = pickKeywords(purpose);
  const kw1 = kws[0] ? ` ${kws[0]}` : "";
  const kw2 = kws[1] ? ` + ${kws[1]}` : "";

  const base = [
    `${biz}${kw1}: quick question`,
    `${biz}${kw1}: 2 minute update`,
    `${biz}${kw1}: next step`,
    `${biz}${kw1}: can you confirm this?`,
    `${biz}${kw1}: action needed`,
    `${biz}${kw1}: your options`,
    `${biz}${kw1}: timeline + details`,
    `${biz}${kw1}${kw2}: simple fix`,
    `${biz}${kw1}: following up`,
    `${biz}${kw1}: request`
  ];

  const friendly = [
    `Quick check in, ${biz}`,
    `${biz} — hope you’re doing well`,
    `${biz} — small update`
  ];

  const urgent = [
    `${biz}: time sensitive`,
    `${biz}: quick approval needed`,
    `${biz}: deadline today`
  ];

  let lines = [...base];

  if (tone === "friendly") lines = [...friendly, ...lines].slice(0, 10);
  if (tone === "urgent") lines = [...urgent, ...lines].slice(0, 10);

  if (opts.includePersonal && purpose) {
    lines[0] = `${biz}: ${purpose.slice(0, 48)}${purpose.length > 48 ? "…" : ""}`;
  }

  // unique + clean
  const seen = new Set<string>();
  const out: string[] = [];
  for (const s of lines) {
    const v = clean(s);
    if (!v) continue;
    const key = v.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(v);
    if (out.length >= 10) break;
  }
  return out;
}

async function copyToClipboard(text: string) {
  await navigator.clipboard.writeText(text);
}

export default function App() {
  const [biz, setBiz] = useState("Solaris Racquet Club");
  const [purpose, setPurpose] = useState("confirm next steps for the schedule");
  const [tone, setTone] = useState<Tone>("professional");
  const [includePersonal, setIncludePersonal] = useState(true);

  const subjects = useMemo(
    () => generateSubjectLines({ biz, purpose, tone, includePersonal }),
    [biz, purpose, tone, includePersonal]
  );

  const [copied, setCopied] = useState<string | null>(null);

  return (
    <div className="container">
      <div className="header">
        <div>
          <h1>Subject Line Generator</h1>
          <p className="sub">
            Paste a quick context and generate 10 clean subject lines instantly. No backend.
          </p>
        </div>
        <div className="badge">Vercel-ready</div>
      </div>

      <div className="card">
        <div className="grid">
          <div>
            <label>Business / Recipient</label>
            <input value={biz} onChange={(e) => setBiz(e.target.value)} placeholder="Ex: Frame & Save" />
          </div>

          <div>
            <label>Tone</label>
            <select value={tone} onChange={(e) => setTone(e.target.value as Tone)}>
              <option value="professional">Professional</option>
              <option value="friendly">Friendly</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
        </div>

        <label>What is the email about?</label>
        <textarea
          value={purpose}
          onChange={(e) => setPurpose(e.target.value)}
          placeholder="Ex: sharing the quote and confirming the install date"
        />

        <div className="row">
          <button
            className="ghost"
            onClick={() => setIncludePersonal((v) => !v)}
            type="button"
            title="First subject uses your exact purpose"
          >
            {includePersonal ? "Personalized: ON" : "Personalized: OFF"}
          </button>

          <button
            className="primary"
            onClick={async () => {
              const all = subjects.map((s) => `- ${s}`).join("\n");
              await copyToClipboard(all);
              setCopied("all");
              setTimeout(() => setCopied(null), 900);
            }}
            type="button"
          >
            {copied === "all" ? "Copied" : "Copy all"}
          </button>
        </div>

        <hr className="sep" />

        <div className="list">
          {subjects.map((s) => (
            <div className="item" key={s}>
              <code>{s}</code>
              <button
                className="ghost"
                type="button"
                onClick={async () => {
                  await copyToClipboard(s);
                  setCopied(s);
                  setTimeout(() => setCopied(null), 800);
                }}
              >
                {copied === s ? "Copied" : "Copy"}
              </button>
            </div>
          ))}
        </div>

        <p className="small">
          Note: This is a lightweight generator using clean templates + simple keyword detection. If you want, we can
          add a small API route later for a real LLM.
        </p>
      </div>
    </div>
  );
}
