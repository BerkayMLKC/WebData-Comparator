"""CSV and Markdown report writers."""
from __future__ import annotations

import csv
from pathlib import Path

from .matcher import Row


def _fmt(price: float | None) -> str:
    return "" if price is None else f"{price:,.2f}"


def write_csv(rows: list[Row], sources: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerow(["product", *sources, "cheapest_source", "price_difference"])
        for row in rows:
            cheapest = row.cheapest() if len(row.items) > 1 else None
            writer.writerow([
                row.name,
                *[_fmt(row.items[s].price) if s in row.items else "" for s in sources],
                cheapest.source if cheapest else "",
                _fmt(row.spread()),
            ])


def write_markdown(rows: list[Row], sources: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    matched = [r for r in rows if len(r.items) > 1]
    lines = [
        "# Price Comparison Report",
        "",
        f"- Sources: {', '.join(sources)}",
        f"- Products found: {len(rows)}",
        f"- Matched across sources: {len(matched)}",
        "",
        "| Product | " + " | ".join(sources) + " | Cheapest | Difference |",
        "|---|" + "---:|" * len(sources) + "---|---:|",
    ]
    for row in rows:
        cheapest = row.cheapest()
        cells = []
        for s in sources:
            if s not in row.items:
                cells.append("-")
                continue
            text = _fmt(row.items[s].price) or "n/a"
            if cheapest and len(row.items) > 1 and row.items[s] is cheapest:
                text = f"**{text}**"
            cells.append(text)
        winner = cheapest.source if cheapest and len(row.items) > 1 else "-"
        lines.append(f"| {row.name} | " + " | ".join(cells) + f" | {winner} | {_fmt(row.spread()) or '-'} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
