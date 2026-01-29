export const runtime = "nodejs";

function styleInstruction(style) {
  switch (style) {
    case "formal":
      return "Rewrite in a formal, polished style.";
    case "casual":
      return "Rewrite in a casual, natural style.";
    case "shorter":
      return "Rewrite to be shorter and tighter without losing meaning.";
    case "detailed":
      return "Rewrite with a bit more detail and clarity, without adding new facts.";
    case "clear":
    default:
      return "Rewrite to be clearer and easier to read.";
  }
}

function toneInstruction(tone) {
  switch (tone) {
    case "friendly":
      return "Keep the tone friendly.";
    case "confident":
      return "Keep the tone confident.";
    case "professional":
      return "Keep the tone professional.";
    case "neutral":
    default:
      return "Keep the tone neutral.";
  }
}

export async function POST(req) {
  try {
    const { text, style = "clear", tone = "neutral" } = await req.json();

    if (!text || typeof text !== "string" || text.trim().length < 5) {
      return Response.json({ error: "Please provide at least 5 characters of text." }, { status: 400 });
    }

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return Response.json({ error: "Missing OPENAI_API_KEY in .env.local" }, { status: 500 });
    }

    const model = process.env.OPENAI_MODEL || "gpt-4o-mini";

    const system =
      "You are a helpful writing assistant. Only rewrite the user's text. " +
      "Do not add new facts. Do not include commentary. Output only the rewritten text.";

    const user =
      `${styleInstruction(style)} ${toneInstruction(tone)}\n\n` +
      `Text to rewrite:\n${text}`;

    const resp = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: system },
          { role: "user", content: user }
        ],
        temperature: 0.4
      })
    });

    const data = await resp.json();
    if (!resp.ok) {
      const msg = data?.error?.message || "OpenAI request failed";
      return Response.json({ error: msg }, { status: 500 });
    }

    const rewrite = data?.choices?.[0]?.message?.content?.trim() || "";
    return Response.json({ rewrite });
  } catch (e) {
    return Response.json({ error: e?.message || "Server error" }, { status: 500 });
  }
}
