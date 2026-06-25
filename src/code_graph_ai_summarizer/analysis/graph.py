from __future__ import annotations

from collections import defaultdict
from typing import Any

from code_graph_ai_summarizer.analysis.classify import categories_for_text
from code_graph_ai_summarizer.utils.text import split_multi


def build_method_graph(facts: dict[str, Any]) -> tuple[dict[str, list[str]], dict[str, str]]:
    methods = facts.get("methods", [])
    call_edges = facts.get("call_edges", [])

    method_to_file = {
        method.get("fullName"): method.get("file")
        for method in methods
        if method.get("fullName") and method.get("file")
    }

    graph: dict[str, list[str]] = defaultdict(list)

    for edge in call_edges:
        caller = edge.get("caller")
        if not caller:
            continue

        for callee in split_multi(edge.get("callees")):
            if callee in method_to_file:
                graph[caller].append(callee)

    return graph, method_to_file


def path_score(path: list[str], method_to_file: dict[str, str]) -> tuple[int, list[str]]:
    text = " ".join(path + [method_to_file.get(method, "") for method in path])
    categories = categories_for_text(text)

    score = len(path) + 4 * len(set(categories))
    important = {"api_web", "storage_db", "filesystem", "llm", "network", "auth", "queue_worker"}
    score += 5 * len(important.intersection(categories))

    return score, sorted(set(categories))
