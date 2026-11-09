"""Chiama OpenRouter per trasformare uno spunto in un pezzo satirico (JSON strutturato)."""
from __future__ import annotations

import json
import os
import random
import time
import urllib.request

from common import ARTICLES_DIR, ROOT, load_yaml

API = "https://openrouter.ai/api/v1/chat/completions"


N_TECHNIQUES = 8  # numero di tecniche elencate in prompts/system.txt


def recent_titles(limit: int = 12) -> list[str]:
    """Ultimi titoli pubblicati (per nome file, che inizia con la data)."""
    titles = []
    for p in sorted(ARTICLES_DIR.glob("*.md"), reverse=True)[:limit]:
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.startswith("title:"):
                titles.append(json.loads(line[len("title:"):].strip()))
                break
    return titles


def build_user_message(candidate: dict, avoid: list[str], techniques: list[int]) -> str:
    msg = (f"Categoria: {candidate['category']}\nTitolo reale: {candidate['title']}\n"
           f"Sommario reale: {candidate['summary']}\n"
           f"Tecniche da usare per questo pezzo (numeri dell'elenco): {', '.join(map(str, techniques))}")
    if avoid:
        msg += ("\n\nTitoli già pubblicati di recente. Non ripetere la loro meccanica comica né la loro struttura:\n"
                + "\n".join(f"- {t}" for t in avoid))
    return msg


def generate(candidate: dict, avoid: list[str] | None = None) -> dict | None:
    """Restituisce i campi dell'articolo, oppure None se il modello dichiara skip.

    `avoid` = titoli generati nella stessa run, da aggiungere agli ultimi pubblicati.
    """
    model = os.environ.get("OPENROUTER_MODEL") or load_yaml("editorial.yaml")["model"]
    system = (ROOT / "pipeline" / "prompts" / "system.txt").read_text(encoding="utf-8")
    user = build_user_message(candidate, (avoid or []) + recent_titles(), sorted(random.sample(range(1, N_TECHNIQUES + 1), 2)))
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_object"},
        "temperature": 0.9,
    }
    req = urllib.request.Request(
        API, json.dumps(payload).encode(),
        {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            body = json.loads(urllib.request.urlopen(req, timeout=60).read())
            data = json.loads(body["choices"][0]["message"]["content"])
            return None if data.get("skip") else data
        except Exception as e:
            print(f"[generate] tentativo {attempt + 1} fallito: {e}")
            time.sleep(2 ** attempt)
    return None
