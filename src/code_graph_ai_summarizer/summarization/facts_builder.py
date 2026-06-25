from __future__ import annotations

from pathlib import Path
from typing import Any

from code_graph_ai_summarizer.analysis.architecture import derive_architecture
from code_graph_ai_summarizer.analysis.flows import find_data_flows, find_runtime_flows
from code_graph_ai_summarizer.analysis.repo_map import build_repo_map


def build_summary_facts(repo_path: Path, facts: dict[str, Any]) -> dict[str, Any]:
    """Builds a structured summary of the repository based on collected facts.
    
    Args:
        repo_path (Path): The path to the local repository.
        facts (dict[str, Any]): Collected facts about the repository.

    Returns:
        dict[str, Any]: A structured summary of the repository, including repo name, path, 
                        architecture signals, entry points, critical flow candidates, 
                        important symbols, and limits.    
    """
    repo_map = build_repo_map(facts.get("files", []))
    architecture = derive_architecture(facts)

    return {
        "repo_name": repo_path.name,
        "repo_path": str(repo_path),
        "repo_map": repo_map,
        "architecture_signals": architecture,
        "entry_points": facts.get("entry_candidates", [])[:40],
        "critical_runtime_flow_candidates": find_runtime_flows(facts),
        "critical_data_flow_candidates": find_data_flows(facts),
        "important_symbols": important_symbols(facts, architecture),
        "raw_joern_reachable_by_flows_sample": facts.get("raw_reachable_by_flows", "")[:8000],
        "limits": {
            "note": (
                "This is static analysis. Runtime/data flows are graph-derived "
                "candidates, not guaranteed actual production traces."
            )
        },
    }


def important_symbols(facts: dict[str, Any], architecture: dict[str, Any]) -> dict[str, Any]:
    """Filters and returns important methods and types based on central files in the architecture.
    
    Args:
        facts (dict[str, Any]): Collected facts about the repository.
        architecture (dict[str, Any]): Derived architecture signals of the repository.
        
    Returns:
        dict[str, Any]: A dictionary containing filtered methods and types that are considered important.
    """
    central_files = {item["file"] for item in architecture.get("central_files", [])[:20]}

    return {
        "methods": [
            method for method in facts.get("methods", [])
            if method.get("file") in central_files
        ][:80],
        "types": [
            type_decl for type_decl in facts.get("types", [])
            if type_decl.get("file") in central_files
        ][:80],
    }
