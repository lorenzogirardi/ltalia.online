"""Scrive l'articolo approvato come Markdown e registra la fonte come processata."""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

from common import ARTICLES_DIR, load_processed, save_processed


def slugify(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60]


def q(value) -> str:
    return json.dumps(value, ensure_ascii=False)  # JSON è YAML valido


def publish(article: dict, candidate: dict, now: datetime | None = None) -> str:
    now = (now or datetime.now(ZoneInfo("Europe/Rome"))).replace(microsecond=0)
    name = f"{now:%Y-%m-%d}-{slugify(article['title'])}"
    fm = [
        f"title: {q(article['title'])}",
        f"description: {q(article['description'])}",
        f"published_at: {now.isoformat()}",
        f"category: {candidate['category']}",
        f"emoji: {q(article['emoji'])}",
        f"tags: {q(article['tags'])}",
        "featured: false",
        "satire: true",
        "ai_assisted: true",
        f"sources: {q(article['sources'])}",
        f"real_news_summary: {q(article['real_news_summary'])}",
    ]
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    (ARTICLES_DIR / f"{name}.md").write_text("---\n" + "\n".join(fm) + "\n---\n\n" + article["body"].strip() + "\n", encoding="utf-8")
    processed = load_processed()
    processed[candidate["id"]] = {"link": candidate["link"], "article": name}
    save_processed(processed)
    return name
