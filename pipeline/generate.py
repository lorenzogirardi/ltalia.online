"""Chiama OpenRouter per trasformare uno spunto in un pezzo satirico (JSON strutturato)."""
from __future__ import annotations

import json
import os
import time
import urllib.request

from common import ROOT, load_yaml

API = "https://openrouter.ai/api/v1/chat/completions"


def generate(candidate: dict) -> dict | None:
    """Restituisce i campi dell'articolo, oppure None se il modello dichiara skip."""
    model = os.environ.get("OPENROUTER_MODEL") or load_yaml("editorial.yaml")["model"]
    system = (ROOT / "pipeline" / "prompts" / "system.txt").read_text(encoding="utf-8")
    user = f"Categoria: {candidate['category']}\nTitolo reale: {candidate['title']}\nSommario reale: {candidate['summary']}"
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
