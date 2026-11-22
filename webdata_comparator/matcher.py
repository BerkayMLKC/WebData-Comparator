"""Matching the same product across different sources."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from .scraper import Item


def normalize(name: str) -> str:
    """Lowercase, strip accents/punctuation and collapse whitespace."""
    name = name.replace("ı", "i").replace("İ", "i")
    name = unicodedata.normalize("NFKD", name.casefold())
    name = "".join(ch for ch in name if not unicodedata.combining(ch))
    name = re.sub(r"[^\w\s]", " ", name)
    return " ".join(name.split())


def similarity(a: str, b: str) -> float:
    """0..1 similarity, robust to word order differences."""
    na, nb = normalize(a), normalize(b)
    direct = SequenceMatcher(None, na, nb).ratio()
    sorted_ = SequenceMatcher(None, " ".join(sorted(na.split())), " ".join(sorted(nb.split()))).ratio()
    return max(direct, sorted_)


@dataclass
class Row:
    name: str
    items: dict[str, Item] = field(default_factory=dict)

    def _priced(self) -> list[Item]:
        return [i for i in self.items.values() if i.price is not None]

    def cheapest(self) -> Item | None:
        priced = self._priced()
        return min(priced, key=lambda i: i.price) if priced else None

    def spread(self) -> float | None:
        """Price difference between the most and least expensive source."""
        prices = [i.price for i in self._priced()]
        return max(prices) - min(prices) if len(prices) >= 2 else None


def compare(items_by_source: dict[str, list[Item]], threshold: float = 0.8) -> list[Row]:
    """Group items from all sources into rows of matching products.

    The first source acts as the reference. For every following source,
    items are matched one-to-one with the best-scoring existing row;
    anything unmatched starts a new row.
    """
    rows: list[Row] = []
    for source, items in items_by_source.items():
        candidates = []
        for i, item in enumerate(items):
            for j, row in enumerate(rows):
                if source in row.items:
                    continue
                score = similarity(item.name, row.name)
                if score >= threshold:
                    candidates.append((score, i, j))
        candidates.sort(key=lambda c: (-c[0], c[1], c[2]))

        used_items: set[int] = set()
        used_rows: set[int] = set()
        for _, i, j in candidates:
            if i in used_items or j in used_rows:
                continue
            rows[j].items[source] = items[i]
            used_items.add(i)
            used_rows.add(j)

        for i, item in enumerate(items):
            if i not in used_items:
                rows.append(Row(item.name, {source: item}))
    return rows
