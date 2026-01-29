const $ = (id) => document.getElementById(id);

function setStatus(msg) {
  $("status").textContent = msg || "";
}

function pretty(obj) {
  return JSON.stringify(obj, null, 2);
}

function renderList(items) {
  const ul = $("suggestions");
  ul.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "No suggestions. Looks solid.";
    ul.appendChild(li);
    return;
  }
  items.forEach((s) => {
    const li = document.createElement("li");
    li.textContent = s;
    ul.appendChild(li);
  });
}

async function analyze() {
  const payload = {
    target_keyword: $("target").value,
    related_keywords: $("related").value,
    meta_title: $("metaTitle").value,
    meta_description: $("metaDesc").value,
    content: $("content").value
  };

  if (!payload.content.trim()) {
    setStatus("Paste some content first.");
    return;
  }

  setStatus("Analyzing...");
  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
      setStatus(data.error || "Error");
      return;
    }

    $("stats").textContent = pretty(data.stats);
    $("readability").textContent = pretty(data.readability);
    $("headings").textContent = pretty(data.headings);

    const kw = data.keywords || {};
    const kwView = {
      target_keyword: kw.target_keyword,
      target_count: kw.target_count,
      target_density_percent: kw.target_density_percent,
      related_counts: kw.related_counts,
      top_terms: kw.top_terms
    };
    $("keywords").textContent = pretty(kwView);

    renderList(data.suggestions);
    setStatus("Done.");
  } catch (e) {
    setStatus("Failed to analyze.");
  }
}

function loadSample() {
  $("target").value = "local seo for home services";
  $("related").value = "google business profile, reviews, leads, citations";
  $("metaTitle").value = "Local SEO for Home Services: Simple Steps to Get More Leads";
  $("metaDesc").value = "A practical guide to improving your local rankings, getting more calls, and turning traffic into leads.";

  $("content").value =
`# Local SEO for Home Services

If you run a home services business, local SEO can be one of the easiest ways to get consistent leads.
This guide covers the basics you can apply this week.

## Start with your Google Business Profile
Fill out every field, add real photos, and keep your hours updated.
Ask happy customers for reviews, and reply to every review.

## Build trust with clear pages
Create one page per service and one page per service area.
Keep paragraphs short and answer common questions.

## Track what matters
Measure calls, form submissions, and direction requests.
Update your pages based on what converts.`;
}

$("analyzeBtn").addEventListener("click", analyze);
$("sampleBtn").addEventListener("click", loadSample);
