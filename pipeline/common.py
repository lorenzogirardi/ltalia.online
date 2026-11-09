"""Percorsi e configurazione condivisi dalla pipeline."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "src" / "content" / "articles"
PROCESSED = ROOT / "data" / "processed.json"
CATEGORIES = {"cronaca", "politica", "sport", "gossip", "cucina", "tecnologia", "economia", "societa"}


def load_yaml(name: str) -> dict:
    return yaml.safe_load((ROOT / "config" / name).read_text(encoding="utf-8"))


def load_processed() -> dict:
    return json.loads(PROCESSED.read_text(encoding="utf-8")) if PROCESSED.exists() else {}


def save_processed(data: dict) -> None:
    PROCESSED.parent.mkdir(exist_ok=True)
    PROCESSED.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def forbidden_hits(text: str, blocklist: dict) -> list[str]:
    """Restituisce 'tema:parola' per ogni parola vietata (parola intera, case-insensitive)."""
    hits = []
    for topic, words in blocklist.items():
        for w in words:
            if re.search(rf"(?<!\w){re.escape(w)}(?!\w)", text, re.IGNORECASE):
                hits.append(f"{topic}:{w}")
    return hits
