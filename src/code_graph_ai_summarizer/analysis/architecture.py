from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from code_graph_ai_summarizer.analysis.classify import categories_for_text
from code_graph_ai_summarizer.utils.text import split_multi


def derive_architecture(facts: dict[str, Any]) -> dict[str, Any]:
    methods = facts.get("methods", [])
    call_edges = facts.get("call_edges", [])
    calls = facts.get("calls", [])

    method_to_file = {
        method.get("fullName"): method.get("file")
        for method in methods
        if method.get("fullName") and method.get("file")
    }

    file_edge_counts: Counter[tuple[str, str]] = Counter()
    file_scores: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    file_categories: dict[str, Counter[str]] = defaultdict(Counter)

    for edge in call_edges:
        caller_file = edge.get("callerFile")
        if not caller_file:
            continue

        internal_callees = split_multi(edge.get("callees"))
        external_callees = split_multi(edge.get("externalCallees"))
        file_scores[caller_file] += len(internal_callees) + len(external_callees)

        for callee in internal_callees:
            callee_file = method_to_file.get(callee)
            if callee_file and callee_file != caller_file:
                file_edge_counts[(caller_file, callee_file)] += 1
                file_scores[callee_file] += 2

        for external in external_callees:
            add_categories(external, caller_file, category_counts, file_categories, file_scores)

    for call in calls:
        text = f"{call.get('name')} {call.get('code')} {call.get('target')}"
        add_categories(text, call.get("file"), category_counts, file_categories, file_scores)

    return {
        "file_call_edges": [
            {"from": src, "to": dst, "call_count": count}
            for (src, dst), count in file_edge_counts.most_common(80)
        ],
        "central_files": [
            {
                "file": file,
                "score": score,
                "categories": dict(file_categories[file].most_common()),
            }
            for file, score in file_scores.most_common(30)
        ],
        "category_counts": dict(category_counts.most_common()),
    }


def add_categories(
    text: str,
    file: str | None,
    category_counts: Counter[str],
    file_categories: dict[str, Counter[str]],
    file_scores: Counter[str],
) -> None:
    for category in categories_for_text(text):
        category_counts[category] += 1
        if file:
            file_categories[file][category] += 1
            file_scores[file] += 1
