"""Striscia "ULTIM'ORA": battute brevi generate a parte, salvate in src/data/ticker.json."""
from __future__ import annotations

import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from common import ROOT, forbidden_hits, load_yaml
from generate import chat_json

TICKER = ROOT / "src" / "data" / "ticker.json"
MAX_KEPT = 30
MAX_LEN = 110


def load_ticker() -> list[dict]:
    return json.loads(TICKER.read_text(encoding="utf-8")) if TICKER.exists() else []


def _norm(s: str) -> str:
    return re.sub(r"\W+", " ", s.lower()).strip()


def review_line(text, blocklist: dict, existing: list[str]) -> list[str]:
    if not isinstance(text, str) or not text.strip():
        return ["riga vuota"]
    errors = []
    if not 15 <= len(text.strip()) <= MAX_LEN:
        errors.append("lunghezza non valida")
    if re.search(r"<[a-zA-Z/][^>]*>", text):
        errors.append("HTML non ammesso")
    errors += [f"tema vietato ({h})" for h in forbidden_hits(text, blocklist)]
    if _norm(text) in {_norm(e) for e in existing}:
        errors.append("duplicata")
    return errors


def generate_lines(n: int, existing: list[str]) -> list[str]:
    system = (ROOT / "pipeline" / "prompts" / "ticker.txt").read_text(encoding="utf-8")
    user = f"Scrivi {n} battute."
    if existing:
        user += "\n\nGià pubblicate (non ripetere meccanica né argomento):\n" + "\n".join(f"- {e}" for e in existing[:15])
    data = chat_json(system, user, temperature=1.0)
    lines = (data or {}).get("lines", [])
    return [l.strip() for l in lines if isinstance(l, str)]


def update_ticker(n: int = 3, dry_run: bool = False) -> list[str]:
    """Aggiunge fino a n battute valide in testa alla lista. Restituisce quelle aggiunte."""
    ed = load_yaml("editorial.yaml")
    items = load_ticker()
    texts = [i["text"] for i in items]
    added = []
    for line in generate_lines(n, texts):
        errors = review_line(line, ed["blocklist"], texts + added)
        if errors:
            print(f"[ticker] scartata {line!r}: {'; '.join(errors)}")
        else:
            added.append(line)
    if added and not dry_run:
        now = datetime.now(ZoneInfo("Europe/Rome")).replace(microsecond=0).isoformat()
        items = [{"text": t, "added": now} for t in added] + items
        TICKER.parent.mkdir(exist_ok=True)
        TICKER.write_text(json.dumps(items[:MAX_KEPT], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for t in added:
        print(f"[ticker] {'(dry-run) ' if dry_run else ''}+ {t}")
    return added
