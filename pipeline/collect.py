"""Raccoglie spunti dai feed RSS, scartando vecchi, già processati e a tema vietato."""
from __future__ import annotations

import hashlib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from common import forbidden_hits, load_processed, load_yaml


def item_id(link: str) -> str:
    return hashlib.sha1(link.encode()).hexdigest()[:16]


def parse_feed(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    out = []
    for it in root.iter("item"):
        pub = it.findtext("pubDate")
        out.append({
            "title": (it.findtext("title") or "").strip(),
            "summary": (it.findtext("description") or "").strip(),
            "link": (it.findtext("link") or "").strip(),
            "published": parsedate_to_datetime(pub) if pub else None,
        })
    return out


def collect(now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    cfg, editorial = load_yaml("sources.yaml"), load_yaml("editorial.yaml")
    seen = load_processed()
    cutoff = now - timedelta(hours=cfg["max_age_hours"])
    candidates = []
    for feed in cfg["feeds"]:
        try:
            req = urllib.request.Request(feed["url"], headers={"User-Agent": "ltalia-online-bot"})
            items = parse_feed(urllib.request.urlopen(req, timeout=20).read())
        except Exception as e:  # un feed rotto non ferma la run
            print(f"[collect] {feed['name']}: {e}")
            continue
        for it in items:
            if not it["link"] or item_id(it["link"]) in seen:
                continue
            if it["published"] is None or it["published"] < cutoff:
                continue
            if forbidden_hits(f"{it['title']} {it['summary']}", editorial["blocklist"]):
                continue  # on_forbidden_source: skip
            candidates.append({**it, "id": item_id(it["link"]), "category": feed["category"], "source": feed["name"]})
    return sorted(candidates, key=lambda c: c["published"], reverse=True)
