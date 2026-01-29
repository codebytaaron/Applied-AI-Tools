from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Tuple

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

WORD_RE = re.compile(r"[A-Za-z0-9']+")

@dataclass
class AnalysisResult:
    stats: Dict
    keywords: Dict
    headings: Dict
    readability: Dict
    suggestions: List[str]


def normalize_text(s: str) -> str:
    # Normalize whitespace and common “smart” quotes
    s = s.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize_words(text: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def split_sentences(text: str) -> List[str]:
    # Simple sentence splitting: good enough for MVP
    parts = re.split(r"[.!?]+(?:\s|$)", text.strip())
    return [p.strip() for p in parts if p.strip()]


def count_syllables(word: str) -> int:
    # Simple English syllable estimator (works OK for readability scoring)
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0

    vowels = "aeiouy"
    syllables = 0
    prev_vowel = False

    for ch in w:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            syllables += 1
        prev_vowel = is_vowel

    # Silent 'e'
    if w.endswith("e") and syllables > 1 and not w.endswith(("le", "ye")):
        syllables -= 1

    return max(1, syllables)


def flesch_reading_ease(words: List[str], sentences: List[str]) -> float:
    if not words or not sentences:
        return 0.0

    syllable_count = sum(count_syllables(w) for w in words)
    wps = len(words) / max(1, len(sentences))  # words per sentence
    spw = syllable_count / max(1, len(words))  # syllables per word

    # Flesch Reading Ease
    score = 206.835 - (1.015 * wps) - (84.6 * spw)
    return round(score, 1)


def score_band(flesch: float) -> str:
    # Common bands
    if flesch >= 90:
        return "Very easy"
    if flesch >= 80:
        return "Easy"
    if flesch >= 70:
        return "Fairly easy"
    if flesch >= 60:
        return "Standard"
    if flesch >= 50:
        return "Fairly difficult"
    if flesch >= 30:
        return "Difficult"
    return "Very difficult"


def extract_headings(text: str) -> Dict[str, int]:
    """
    Detect headings in either:
    - Markdown: #, ##, ### ...
    - HTML: <h1>, <h2>, ...
    """
    md_counts = Counter()
    html_counts = Counter()

    for line in text.splitlines():
        m = re.match(r"^\s*(#{1,6})\s+\S+", line)
        if m:
            level = len(m.group(1))
            md_counts[f"h{level}"] += 1

    for level in range(1, 7):
        html_counts[f"h{level}"] = len(re.findall(fr"<h{level}\b", text, flags=re.IGNORECASE))

    combined = Counter()
    combined.update(md_counts)
    combined.update(html_counts)

    # Ensure all levels exist
    return {f"h{i}": int(combined.get(f"h{i}", 0)) for i in range(1, 7)}


def keyword_metrics(words: List[str], target: str, related: str) -> Tuple[Dict, Dict]:
    total_words = len(words)
    freq = Counter(words)

    target_clean = target.strip().lower()
    related_list = [r.strip().lower() for r in related.split(",") if r.strip()]

    # Target count supports multi-word phrases by checking normalized text too
    # For density we’ll estimate via phrase matches; fall back to token counts for 1-word.
    target_phrase_count = 0
    if target_clean:
        joined = " ".join(words)
        # phrase match on word boundaries
        target_phrase_count = len(
            re.findall(rf"\b{re.escape(target_clean)}\b", joined, flags=re.IGNORECASE)
        )

    density = 0.0
    if total_words > 0:
        # density based on occurrences vs total words (approx)
        density = (target_phrase_count / total_words) * 100

    related_counts = {r: freq.get(r, 0) for r in related_list}

    top_words = [
        (w, c) for (w, c) in freq.most_common(25)
        if len(w) > 2 and not w.isdigit()
    ]

    kw = {
        "target_keyword": target_clean,
        "target_count": target_phrase_count,
        "target_density_percent": round(density, 2),
        "related_keywords": related_list,
        "related_counts": related_counts,
        "top_terms": top_words[:15],
    }

    # SEO-ish heuristics (simple, not “magic”)
    flags = {
        "has_target": bool(target_clean) and target_phrase_count > 0,
        "density_low": bool(target_clean) and density < 0.5,
        "density_high": bool(target_clean) and density > 3.0,
    }
    return kw, flags


def make_suggestions(
    text: str,
    words: List[str],
    sentences: List[str],
    headings: Dict[str, int],
    kw: Dict,
    kw_flags: Dict,
    meta_title: str,
    meta_desc: str
) -> List[str]:
    suggestions: List[str] = []
    word_count = len(words)
    sentence_count = len(sentences)

    if word_count < 300:
        suggestions.append("Add more depth. Aim for at least 300 to 800 words for most posts.")
    elif word_count > 2000:
        suggestions.append("Consider trimming or adding subheadings. Very long posts need strong structure.")

    if sentence_count > 0:
        avg_sentence_len = word_count / sentence_count
        if avg_sentence_len > 22:
            suggestions.append("Shorten sentences. Average sentence length is a bit high.")

    # Headings
    if headings.get("h1", 0) == 0:
        suggestions.append("Add one clear H1 title (or a top-level heading) to define the page topic.")
    elif headings.get("h1", 0) > 1:
        suggestions.append("Use only one H1. Convert extra H1s into H2s.")

    if headings.get("h2", 0) == 0:
        suggestions.append("Add H2 subheadings to break up sections and improve scan-ability.")
    if headings.get("h3", 0) == 0 and word_count >= 700:
        suggestions.append("Add some H3 subheadings for details inside each section.")

    # Keyword guidance
    target = kw.get("target_keyword", "")
    if target:
        if not kw_flags.get("has_target", False):
            suggestions.append("Include your target keyword at least once, ideally in the first 100 words.")
        if kw_flags.get("density_low", False):
            suggestions.append("Target keyword density looks low. Add it naturally 1 to 3 times.")
        if kw_flags.get("density_high", False):
            suggestions.append("Target keyword density looks high. Reduce repetition and use synonyms.")
    else:
        suggestions.append("Add a target keyword to get keyword density and placement feedback.")

    # Meta title / description checks
    mt = meta_title.strip()
    md = meta_desc.strip()

    if not mt:
        suggestions.append("Add a meta title. Keep it clear and specific.")
    else:
        if len(mt) < 35:
            suggestions.append("Meta title may be short. Many titles perform well around 45 to 60 characters.")
        if len(mt) > 65:
            suggestions.append("Meta title may be long. Consider shortening to about 60 characters.")

        if target and target not in mt.lower():
            suggestions.append("Try including the target keyword in the meta title, if it fits naturally.")

    if not md:
        suggestions.append("Add a meta description. Summarize the value in 1 to 2 sentences.")
    else:
        if len(md) < 90:
            suggestions.append("Meta description may be short. Many descriptions perform well around 120 to 160 characters.")
        if len(md) > 170:
            suggestions.append("Meta description may be long. Consider trimming to about 160 characters.")

        if target and target not in md.lower():
            suggestions.append("Try including the target keyword in the meta description, if it fits naturally.")

    # Paragraph length heuristic
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    long_paras = [p for p in paras if len(p.split()) > 110]
    if long_paras:
        suggestions.append("Break up long paragraphs. Aim for tighter blocks so it’s easier to read.")

    return suggestions


def analyze(payload: Dict) -> AnalysisResult:
    raw_text = payload.get("content", "") or ""
    target_keyword = payload.get("target_keyword", "") or ""
    related = payload.get("related_keywords", "") or ""
    meta_title = payload.get("meta_title", "") or ""
    meta_desc = payload.get("meta_description", "") or ""

    text = normalize_text(raw_text)
    words = tokenize_words(text)
    sentences = split_sentences(text)

    # Basic stats
    word_count = len(words)
    char_count = len(text)
    sentence_count = len(sentences)
    paragraph_count = len([p for p in re.split(r"\n\s*\n", raw_text) if p.strip()])

    avg_words_per_sentence = round(word_count / max(1, sentence_count), 2)

    # Readability
    flesch = flesch_reading_ease(words, sentences)
    readability = {
        "flesch_reading_ease": flesch,
        "level": score_band(flesch),
        "avg_words_per_sentence": avg_words_per_sentence,
    }

    # Headings
    heading_counts = extract_headings(raw_text)

    # Keywords
    kw, kw_flags = keyword_metrics(words, target_keyword, related)

    # Suggestions
    suggestions = make_suggestions(
        raw_text, words, sentences, heading_counts, kw, kw_flags, meta_title, meta_desc
    )

    return AnalysisResult(
        stats={
            "word_count": word_count,
            "character_count": char_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
        },
        keywords=kw,
        headings=heading_counts,
        readability=readability,
        suggestions=suggestions,
    )


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_route():
    try:
        payload = request.get_json(force=True, silent=False)
        if not isinstance(payload, dict):
            return jsonify({"error": "Invalid JSON payload"}), 400

        result = analyze(payload)
        return jsonify({
            "stats": result.stats,
            "keywords": result.keywords,
            "headings": result.headings,
            "readability": result.readability,
            "suggestions": result.suggestions,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
