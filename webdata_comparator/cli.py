"""Command line interface."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .matcher import compare
from .report import write_csv, write_markdown
from .scraper import scrape_source


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="webdata_comparator", description="Compare product data across web sources.")
    p.add_argument("--config", required=True, type=Path, help="path to a JSON config file")
    p.add_argument("--out", type=Path, default=Path("reports"), help="output directory (default: reports)")
    p.add_argument("--threshold", type=float, help="name similarity threshold 0..1 (overrides config)")
    p.add_argument("--ignore-robots", action="store_true", help="do not check robots.txt (use responsibly)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    threshold = args.threshold if args.threshold is not None else config.get("threshold", 0.8)
    delay = config.get("delay_seconds", 1)

    items_by_source = {}
    for source in config["sources"]:
        try:
            items = scrape_source(source, respect_robots=not args.ignore_robots)
        except Exception as exc:  # keep going if one source fails
            print(f"[warn] {source['name']}: {exc}", file=sys.stderr)
            continue
        print(f"[ok]   {source['name']}: {len(items)} items")
        items_by_source[source["name"]] = items
        if source.get("url"):
            time.sleep(delay)

    if len(items_by_source) < 2:
        print("[error] need at least two working sources to compare", file=sys.stderr)
        return 1

    rows = compare(items_by_source, threshold)
    sources = list(items_by_source)
    write_csv(rows, sources, args.out / "comparison.csv")
    write_markdown(rows, sources, args.out / "comparison.md")
    print(f"[done] {len(rows)} products, reports written to {args.out}/")
    return 0
