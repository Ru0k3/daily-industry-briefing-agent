from datetime import datetime, timezone
from pathlib import Path
from industry_briefing import Article, render_pdf

out = Path("/tmp/industry-briefing-smoke.pdf")
render_pdf(
    {
        "headline": "Smoke-test briefing",
        "executive_summary": "A deterministic rendering check.",
        "themes": [{"title": "Theme one", "analysis": "Observed fact.", "implications": "Engineering teams should monitor it."}],
        "watchlist": ["Follow the next disclosure."],
        "articles": [{"index": 1, "title": "Example article", "source": "Example", "url": "https://example.com", "significance": "Test source."}],
    },
    [Article("Example article", "https://example.com", "Example", datetime.now(timezone.utc), "Example")],
    out,
    datetime.now(timezone.utc),
)
assert out.exists() and out.stat().st_size > 1000
print(out, out.stat().st_size)
