from webdata_comparator.matcher import compare, normalize, similarity
from webdata_comparator.scraper import Item


def test_normalize_handles_turkish_characters():
    assert normalize("ŞARJ  Aleti!") == "sarj aleti"
    assert normalize("KULAKLIK İncele") == "kulaklik incele"


def test_similarity_ignores_word_order():
    assert similarity("Samsung 27 Odyssey Monitör", "Samsung Odyssey 27 Monitör") == 1.0


def test_compare_matches_and_keeps_unmatched():
    a = [Item("A", "Logitech MX Master 3S Kablosuz Mouse", 1300.0), Item("A", "Anker Şarj Aleti", 900.0)]
    b = [Item("B", "Logitech MX Master 3S Mouse", 1250.0), Item("B", "JBL Kulaklık", 800.0)]
    rows = compare({"A": a, "B": b}, threshold=0.8)
    assert len(rows) == 3
    matched = [r for r in rows if len(r.items) == 2]
    assert len(matched) == 1
    assert matched[0].cheapest().source == "B"
    assert matched[0].spread() == 50.0


def test_one_to_one_matching():
    a = [Item("A", "Mouse X", 10.0)]
    b = [Item("B", "Mouse X", 9.0), Item("B", "Mouse X", 8.0)]
    rows = compare({"A": a, "B": b})
    assert len(rows) == 2


def test_spread_none_when_single_source():
    rows = compare({"A": [Item("A", "Only here", 5.0)]})
    assert rows[0].spread() is None
