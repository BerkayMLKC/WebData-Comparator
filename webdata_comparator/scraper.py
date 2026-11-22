"""Fetching and parsing of product listings."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "WebDataComparator/0.1 (portfolio project)"
_PRICE_RE = re.compile(r"\d[\d.,]*")


@dataclass(frozen=True)
class Item:
    source: str
    name: str
    price: float | None
    url: str | None = None


def parse_price(text: str | None) -> float | None:
    """Turn strings like '1.299,90 TL' or '$1,299.50' into a float.

    Handles both Turkish/European (1.299,90) and US (1,299.50) formats.
    A lone comma is read as a decimal comma, a lone dot as a decimal point.
    """
    if not text:
        return None
    match = _PRICE_RE.search(text)
    if not match:
        return None
    raw = match.group(0).rstrip(".,")
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif raw.count(",") > 1:
        raw = raw.replace(",", "")
    elif "," in raw:
        raw = raw.replace(",", ".")
    elif raw.count(".") > 1:
        raw = raw.replace(".", "")
    try:
        return float(raw)
    except ValueError:
        return None


def allowed_by_robots(url: str) -> bool:
    """Check the site's robots.txt. If it cannot be read, assume allowed."""
    parts = urlparse(url)
    parser = robotparser.RobotFileParser()
    parser.set_url(f"{parts.scheme}://{parts.netloc}/robots.txt")
    try:
        parser.read()
    except Exception:
        return True
    return parser.can_fetch(USER_AGENT, url)


def load_html(source: dict, respect_robots: bool = True, timeout: int = 15) -> str:
    """Load HTML from a local file ('path') or over HTTP ('url')."""
    if source.get("path"):
        return Path(source["path"]).read_text(encoding="utf-8")
    url = source["url"]
    if respect_robots and not allowed_by_robots(url):
        raise PermissionError(f"robots.txt disallows fetching {url}")
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_items(html: str, source: dict) -> list[Item]:
    """Extract items from HTML using the CSS selectors in the source config."""
    selectors = source["selectors"]
    soup = BeautifulSoup(html, "html.parser")
    base = source.get("base_url") or source.get("url") or ""
    items: list[Item] = []
    for node in soup.select(selectors["item"]):
        name_node = node.select_one(selectors["name"])
        if name_node is None:
            continue
        name = name_node.get_text(" ", strip=True)
        if not name:
            continue
        price_node = node.select_one(selectors["price"])
        price = parse_price(price_node.get_text(" ", strip=True)) if price_node else None
        link = None
        if selectors.get("link"):
            link_node = node.select_one(selectors["link"])
            if link_node is not None and link_node.get("href"):
                link = urljoin(base, link_node["href"])
        items.append(Item(source["name"], name, price, link))
    return items


def scrape_source(source: dict, respect_robots: bool = True) -> list[Item]:
    return parse_items(load_html(source, respect_robots), source)
