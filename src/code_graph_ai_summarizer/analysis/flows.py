from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from code_graph_ai_summarizer.analysis.classify import is_sink_call, is_source_call
from code_graph_ai_summarizer.analysis.graph import build_method_graph, path_score


def find_runtime_flows(facts: dict[str, Any], max_flows: int = 12) -> list[dict[str, Any]]:
    graph, method_to_file = build_method_graph(facts)
    entries = [entry.get("fullName") for entry in facts.get("entry_candidates", []) if entry.get("fullName")]

    if not entries:
        entries = sorted(graph.keys(), key=lambda method: len(graph[method]), reverse=True)[:30]

    candidates: list[dict[str, Any]] = []

    for entry in entries[:50]:
        queue = deque([[entry]])
        seen_paths = 0

        while queue and seen_paths < 80:
            path = queue.popleft()
            seen_paths += 1

            if len(path) >= 3:
                score, signals = path_score(path, method_to_file)
                if signals:
                    candidates.append(runtime_candidate(entry, path, method_to_file, score, signals))

            if len(path) >= 5:
                continue

            for next_method in graph.get(path[-1], [])[:12]:
                if next_method not in path:
                    queue.append(path + [next_method])

    return dedupe_candidates(candidates, max_flows)


def find_data_flows(facts: dict[str, Any], max_flows: int = 12) -> list[dict[str, Any]]:
    graph, method_to_file = build_method_graph(facts)
    source_calls_by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    sink_calls_by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for call in facts.get("source_sink_calls", []):
        method = call.get("method")
        if not method:
            continue
        if is_source_call(call):
            source_calls_by_method[method].append(call)
        if is_sink_call(call):
            sink_calls_by_method[method].append(call)

    candidates: list[dict[str, Any]] = []

    for source_method, source_calls in source_calls_by_method.items():
        queue = deque([[source_method]])
        visited = {source_method}

        while queue:
            path = queue.popleft()
            current = path[-1]

            if current in sink_calls_by_method:
                score, signals = path_score(path, method_to_file)
                candidates.append(
                    data_candidate(
                        source_method,
                        current,
                        path,
                        method_to_file,
                        source_calls,
                        sink_calls_by_method[current],
                        score + 10,
                        signals,
                    )
                )

            if len(path) >= 5:
                continue

            for next_method in graph.get(current, [])[:12]:
                if next_method not in visited:
                    visited.add(next_method)
                    queue.append(path + [next_method])

    return dedupe_data_candidates(candidates, max_flows)


def runtime_candidate(
    entry: str,
    path: list[str],
    method_to_file: dict[str, str],
    score: int,
    signals: list[str],
) -> dict[str, Any]:
    return {
        "entry": entry,
        "score": score,
        "signals": signals,
        "path": [{"method": method, "file": method_to_file.get(method, "unknown")} for method in path],
    }


def data_candidate(
    source_method: str,
    sink_method: str,
    path: list[str],
    method_to_file: dict[str, str],
    source_calls: list[dict[str, Any]],
    sink_calls: list[dict[str, Any]],
    score: int,
    signals: list[str],
) -> dict[str, Any]:
    return {
        "score": score,
        "signals": signals,
        "source_method": source_method,
        "sink_method": sink_method,
        "source_examples": compact_call_examples(source_calls),
        "sink_examples": compact_call_examples(sink_calls),
        "path": [{"method": method, "file": method_to_file.get(method, "unknown")} for method in path],
    }


def compact_call_examples(calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"file": call.get("file"), "line": call.get("line"), "code": call.get("code")}
        for call in calls[:3]
    ]


def dedupe_candidates(candidates: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    candidates.sort(key=lambda item: item["score"], reverse=True)
    result = []
    seen = set()

    for candidate in candidates:
        key = tuple(step["method"] for step in candidate["path"])
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
        if len(result) >= limit:
            break

    return result


def dedupe_data_candidates(candidates: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    candidates.sort(key=lambda item: item["score"], reverse=True)
    result = []
    seen = set()

    for candidate in candidates:
        key = (
            candidate["source_method"],
            candidate["sink_method"],
            tuple(step["method"] for step in candidate["path"]),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
        if len(result) >= limit:
            break

    return result
