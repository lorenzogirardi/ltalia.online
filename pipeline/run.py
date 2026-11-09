"""Orchestratore: collect -> generate -> review -> publish."""
from __future__ import annotations

import argparse

from collect import collect
from common import load_processed, load_yaml, save_processed
from generate import generate
from publish import publish
from review import review


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="non scrive file")
    ap.add_argument("--max", type=int, help="override max_articles_per_run")
    args = ap.parse_args()
    ed = load_yaml("editorial.yaml")
    limit = args.max or ed["max_articles_per_run"]
    published = 0
    for cand in collect():
        if published >= limit:
            break
        art = generate(cand)
        rejected = None
        if art is None:
            rejected = "skip/errore del modello"
        else:
            art["sources"] = [{"name": cand["source"], "url": cand["link"]}]
            errors = review(art, ed)
            rejected = "; ".join(errors) if errors else None
        if rejected:
            print(f"[run] scartato {cand['id']}: {rejected}")
            if not args.dry_run:  # non ritentare all'infinito lo stesso spunto
                p = load_processed(); p[cand["id"]] = {"link": cand["link"], "rejected": rejected}; save_processed(p)
            continue
        if args.dry_run:
            print(f"[run] OK (dry-run): {art['title']}")
        else:
            print(f"[run] pubblicato {publish(art, cand)}")
        published += 1
    print(f"[run] {published} articoli")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
