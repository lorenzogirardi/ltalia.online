import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))

from common import ARTICLES_DIR, forbidden_hits, load_yaml  # noqa: E402
from review import review  # noqa: E402

ED = load_yaml("editorial.yaml")


def good():
    return {
        "title": "Il Comune apre lo sportello per prenotare lo sportello",
        "description": "Per prenotare servirà un appuntamento, da prenotare allo sportello.",
        "body": "Primo paragrafo comico. " * 20,
        "emoji": "📄",
        "tags": ["burocrazia"],
        "real_news_summary": "Un Comune ha introdotto un nuovo servizio di prenotazione.",
        "sources": [{"name": "ANSA", "url": "https://www.ansa.it/x"}],
    }


def test_good_article_passes():
    assert review(good(), ED) == []


def test_missing_source_rejected():
    a = good(); a["sources"] = []
    assert "fonte mancante" in review(a, ED)


def test_html_rejected():
    a = good(); a["body"] += " <script>x</script>"
    assert "HTML non ammesso" in review(a, ED)


def test_forbidden_topics_rejected():
    for word in ["guerra", "terrorista", "razzismo", "violenza", "papa", "armi", "Kiev"]:
        a = good(); a["body"] += f" Una storia di {word}."
        assert any("tema vietato" in e for e in review(a, ED)), word


def test_whole_word_only():
    assert forbidden_hits("Roma, il Dioscuri e la romana", ED["blocklist"]) == []


def test_all_published_articles_respect_constraint():
    for p in ARTICLES_DIR.glob("*.md"):
        assert forbidden_hits(p.read_text(encoding="utf-8"), ED["blocklist"]) == [], p.name


def test_user_message_has_techniques_and_avoid_list():
    from generate import build_user_message, recent_titles
    cand = {"category": "sport", "title": "T", "summary": "S"}
    msg = build_user_message(cand, ["Titolo uno", "Titolo due"], [2, 5])
    assert "2, 5" in msg and "- Titolo uno" in msg and "Non ripetere" in msg
    assert "Non ripetere" not in build_user_message(cand, [], [1, 3])
    assert recent_titles(3) and all(isinstance(t, str) for t in recent_titles(3))
