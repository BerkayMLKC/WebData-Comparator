import json
from pathlib import Path

import pytest

from webdata_comparator.scraper import parse_items, parse_price

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("text,expected", [
    ("1.299,90 TL", 1299.90),
    ("₺1.249,00", 1249.00),
    ("$1,299.50", 1299.50),
    ("12,5 TL", 12.5),
    ("899", 899.0),
    ("1.299.000", 1299000.0),
    ("fiyat yok", None),
    ("", None),
    (None, None),
])
def test_parse_price(text, expected):
    assert parse_price(text) == expected


def test_parse_items_from_both_example_stores():
    config = json.loads((ROOT / "config.example.json").read_text(encoding="utf-8"))
    for source in config["sources"]:
        source["path"] = str(ROOT / source["path"])
        html = Path(source["path"]).read_text(encoding="utf-8")
        items = parse_items(html, source)
        assert len(items) == 4
        assert all(i.price is not None and i.url for i in items)


def test_parse_items_skips_nodes_without_name():
    source = {"name": "x", "selectors": {"item": ".p", "name": ".n", "price": ".c"}}
    html = '<div class="p"><span class="c">5</span></div><div class="p"><span class="n">A</span><span class="c">5</span></div>'
    items = parse_items(html, source)
    assert [i.name for i in items] == ["A"]
