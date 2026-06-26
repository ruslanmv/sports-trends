"""Generate SEO meta descriptions for sports pages."""

from __future__ import annotations

from typing import Any


def generate_meta_descriptions(pages: list[dict[str, Any]] | None = None) -> list[str]:
    """Return placeholder descriptions for provided pages."""
    return [page.get("description") or f"Sports intelligence for {page.get('title', 'upcoming games')}" for page in (pages or [])]
