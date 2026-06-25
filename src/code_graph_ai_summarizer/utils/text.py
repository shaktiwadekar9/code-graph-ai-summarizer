from __future__ import annotations

from typing import Any


def normalize_text(value: Any) -> str:
    return str(value or "").lower()


def split_multi(value: Any) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in str(value).split("|||") if part.strip()]
