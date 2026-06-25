from __future__ import annotations

from typing import Any

from code_graph_ai_summarizer.analysis.patterns import CATEGORY_PATTERNS, SINK_PATTERNS, SOURCE_PATTERNS
from code_graph_ai_summarizer.utils.text import normalize_text


def categories_for_text(text: str) -> list[str]:
    lower = normalize_text(text)
    return [
        category
        for category, patterns in CATEGORY_PATTERNS.items()
        if any(pattern in lower for pattern in patterns)
    ]


def is_source_call(call: dict[str, Any]) -> bool:
    text = normalize_text(f"{call.get('name')} {call.get('code')} {call.get('target')}")
    return any(pattern in text for pattern in SOURCE_PATTERNS)


def is_sink_call(call: dict[str, Any]) -> bool:
    text = normalize_text(f"{call.get('name')} {call.get('code')} {call.get('target')}")
    return any(pattern in text for pattern in SINK_PATTERNS)
