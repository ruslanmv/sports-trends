"""Generate sitemap URL entries for the sports section."""

from __future__ import annotations

from typing import Any

from ..config import SITE_BASE_URL
from ..ingestion.normalize_matches import slugify

STATIC_PATHS = ("", "tomorrow/", "live/", "trending/", "predictions/", "rankings/",
                "football/", "basketball/", "tennis/", "cricket/", "baseball/", "esports/")


def sitemap_urls(matches: list[dict[str, Any]] | None = None) -> list[str]:
    base = SITE_BASE_URL.rstrip("/")
    urls = [f"{base}/{p}" for p in STATIC_PATHS]
    for m in (matches or []):
        if m.get("match_id"):
            urls.append(f"{base}/match/{m['match_id']}/")
    return urls


def generate_sitemap(matches: list[dict[str, Any]] | None = None) -> str:
    items = "".join(f"  <url><loc>{u}</loc></url>\n" for u in sitemap_urls(matches))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{items}</urlset>\n")
