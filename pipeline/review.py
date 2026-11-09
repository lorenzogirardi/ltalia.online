"""Validazione deterministica: ogni errore blocca la pubblicazione."""
from __future__ import annotations

import re

from common import forbidden_hits, load_yaml

_EMOJI = re.compile(r"[☀-➿\U0001F300-\U0001FAFF]")


def review(article: dict, editorial: dict | None = None) -> list[str]:
    ed = editorial or load_yaml("editorial.yaml")
    errors = []
    for field in ("title", "description", "body", "emoji", "tags", "real_news_summary"):
        if not article.get(field):
            errors.append(f"campo mancante: {field}")
    if errors:
        return errors
    if not 10 <= len(article["title"]) <= 160:
        errors.append("titolo di lunghezza non valida")
    if not 10 <= len(article["description"]) <= 300:
        errors.append("description di lunghezza non valida")
    if not ed["min_body_chars"] <= len(article["body"]) <= ed["max_body_chars"]:
        errors.append("corpo di lunghezza non valida")
    if not isinstance(article["tags"], list) or not all(isinstance(t, str) for t in article["tags"]):
        errors.append("tags non valido")
    if not _EMOJI.search(article["emoji"]):
        errors.append("emoji non valida")
    if re.search(r"<[a-zA-Z/][^>]*>", article["body"] + article["title"]):
        errors.append("HTML non ammesso")
    if not article.get("sources"):
        errors.append("fonte mancante")
    for s in article.get("sources", []):
        if not str(s.get("url", "")).startswith("https://"):
            errors.append(f"URL fonte non valido: {s.get('url')}")
    text = " ".join(str(article[k]) for k in ("title", "description", "body", "real_news_summary"))
    errors += [f"tema vietato ({h})" for h in forbidden_hits(text, ed["blocklist"])]
    return errors
