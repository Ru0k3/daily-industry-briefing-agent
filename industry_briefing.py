"""Daily industry briefing agent: RSS ingestion, LLM synthesis, PDF rendering, Gmail delivery."""
from __future__ import annotations

import html
import json
import logging
import os
import re
import smtplib
import ssl
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import feedparser
import requests
from openai import OpenAI
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("industry-briefing")

@dataclass
class Article:
    title: str
    url: str
    source: str
    published: datetime
    summary: str


def env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value or ""


def parse_dt(entry: object) -> datetime:
    parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if parsed:
        from calendar import timegm
        return datetime.fromtimestamp(timegm(parsed), tz=timezone.utc)
    return datetime.now(timezone.utc)


def clean_text(value: str, limit: int = 1800) -> str:
    value = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]


def fetch_articles(since: datetime, feeds: Iterable[str], max_per_feed: int) -> list[Article]:
    articles: list[Article] = []
    for feed_url in feeds:
        LOG.info("Fetching %s", feed_url)
        try:
            response = requests.get(feed_url, timeout=20, headers={"User-Agent": "daily-industry-briefing/1.0"})
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
            source = parsed.feed.get("title") or urlparse(feed_url).netloc
            count = 0
            for entry in parsed.entries:
                published = parse_dt(entry)
                if published < since or count >= max_per_feed:
                    continue
                url = entry.get("link", "").strip()
                title = clean_text(entry.get("title", "Untitled"), 240)
                if not url or not title:
                    continue
                articles.append(Article(title, url, source, published, clean_text(entry.get("summary", ""))))
                count += 1
        except Exception as exc:
            LOG.warning("Feed failed (%s): %s", feed_url, exc)
    unique: dict[str, Article] = {article.url: article for article in articles}
    return sorted(unique.values(), key=lambda item: item.published, reverse=True)


def synthesize(articles: list[Article], now: datetime) -> dict:
    model = env("LLM_MODEL", "gpt-4o-mini")
    base_url = os.getenv("LLM_BASE_URL")
    client = OpenAI(api_key=env("LLM_API_KEY", required=True), base_url=base_url or None)
    corpus = "\n\n".join(
        f"[{i}] {a.title}\nSource: {a.source}\nPublished: {a.published.isoformat()}\nURL: {a.url}\nRaw text: {a.summary}"
        for i, a in enumerate(articles, 1)
    )
    prompt = f"""You are a senior technical intelligence analyst. Create a high-value daily briefing from the supplied articles published in the last 24 hours.

Requirements:
- Return valid JSON with keys: headline, executive_summary, themes (array of objects with title, analysis, implications), watchlist (array of strings), articles (array of objects with index, title, source, url, significance).
- Prioritize concrete technical, regulatory, product, security, and market disclosures over hype.
- Separate reported facts from inference. Do not invent facts or sources.
- Explain why each theme matters to an engineering or technology leadership audience.
- Keep the final briefing concise enough for a 4-6 page PDF.

Current UTC time: {now.isoformat()}
Articles:
{corpus or 'No qualifying articles were found. Return a useful empty-briefing explanation.'}
"""
    result = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You produce precise, source-grounded technical briefings."},
            {"role": "user", "content": prompt},
        ],
    )
    content = result.choices[0].message.content or "{}"
    return json.loads(content)


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(html.escape(str(text)).replace("\n", "<br/>"), style)


def render_pdf(brief: dict, articles: list[Article], output: Path, now: datetime) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=27, alignment=TA_CENTER, textColor=colors.HexColor("#16324F"), spaceAfter=8)
    subtitle = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#52606D"), spaceAfter=16)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#16324F"), spaceBefore=14, spaceAfter=6)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9.5, leading=14, textColor=colors.HexColor("#1F2933"), spaceAfter=7)
    small = ParagraphStyle("Small", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#52606D"))
    story = [p("Daily Industry Intelligence", title), p(f"{now.strftime('%d %B %Y')} · Coverage window: previous 24 hours · Generated {now.strftime('%H:%M UTC')}", subtitle), HRFlowable(width="100%", color=colors.HexColor("#CBD5E0")), p(brief.get("headline", "Daily briefing"), h1), p(brief.get("executive_summary", "No summary was generated."), body)]
    story.append(p("Key themes", h1))
    for theme in brief.get("themes", []):
        story += [p(theme.get("title", "Untitled theme"), ParagraphStyle("Theme", parent=body, fontName="Helvetica-Bold", textColor=colors.HexColor("#2B6CB0"))), p(theme.get("analysis", ""), body), p(f"Implication: {theme.get('implications', '')}", body)]
    story.append(p("Watchlist", h1))
    for item in brief.get("watchlist", []):
        story.append(p(f"• {item}", body))
    story.append(p("Source digest", h1))
    rows = [[p("#", small), p("Article", small), p("Source", small), p("Significance", small)]]
    for item in brief.get("articles", []):
        rows.append([p(item.get("index", ""), small), p(item.get("title", ""), small), p(item.get("source", ""), small), p(item.get("significance", ""), small)])
    table = Table(rows, colWidths=[9 * mm, 60 * mm, 30 * mm, 75 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6EEF5")), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E0")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story += [table, Spacer(1, 8), p("This briefing is machine-generated from public RSS/news feeds. Verify material claims against the linked source before making operational or investment decisions.", small)]
    SimpleDocTemplate(str(output), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=14 * mm, bottomMargin=14 * mm, title="Daily Industry Intelligence").build(story)


def send_email(pdf: Path, brief: dict, now: datetime) -> None:
    msg = EmailMessage()
    recipient = env("GMAIL_TO", required=True)
    msg["Subject"] = f"Daily Industry Intelligence — {now.strftime('%Y-%m-%d')}"
    msg["From"] = env("GMAIL_FROM", required=True)
    msg["To"] = recipient
    msg.set_content(f"Attached is your daily industry intelligence briefing for {now.strftime('%Y-%m-%d')} UTC.\n\n{brief.get('headline', '')}\n\nGenerated automatically by GitHub Actions.")
    msg.add_attachment(pdf.read_bytes(), maintype="application", subtype="pdf", filename=pdf.name)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(env("SMTP_HOST", "smtp.gmail.com"), int(env("SMTP_PORT", "465")), context=context) as smtp:
        smtp.login(env("GMAIL_FROM", required=True), env("GMAIL_APP_PASSWORD", required=True))
        smtp.send_message(msg)
    LOG.info("Briefing emailed to configured recipient")


def main() -> int:
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=int(env("LOOKBACK_HOURS", "24")))
    feeds = [line.strip() for line in env("RSS_FEEDS", "https://news.ycombinator.com/rss,https://feeds.arstechnica.com/arstechnica/index,https://www.theverge.com/rss/index.xml").split(",") if line.strip()]
    articles = fetch_articles(since, feeds, int(env("MAX_ARTICLES_PER_FEED", "12")))
    LOG.info("Collected %d qualifying articles", len(articles))
    brief = synthesize(articles, now)
    output = Path(env("OUTPUT_DIR", "artifacts")) / f"industry-briefing-{now.strftime('%Y-%m-%d')}.pdf"
    render_pdf(brief, articles, output, now)
    send_email(output, brief, now)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        LOG.exception("Daily briefing failed")
        raise
