from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from cpgqls_client import CPGQLSClient, import_code_query

from code_graph_ai_summarizer.joern.queries import joern_queries, reachable_by_flows_query


def project_name_for(repo_path: Path) -> str:
    digest = hashlib.sha1(str(repo_path.resolve()).encode()).hexdigest()[:8]
    return f"{repo_path.name}-{digest}"


def parse_joern_json(stdout: str) -> Any:
    """Parse JSON returned by Joern .toJson.

    Depending on server/client versions, output can be raw JSON, a JSON string,
    or REPL-style text like: res0: String = "[{...}]".
    """
    text = stdout.strip()

    def try_json(value: str) -> Any | None:
        try:
            return json.loads(value)
        except Exception:
            return None

    direct = try_json(text)
    if direct is not None:
        if isinstance(direct, str):
            nested = try_json(direct)
            return nested if nested is not None else direct
        return direct

    triple = re.search(r'"""(.*?)"""', text, re.DOTALL)
    if triple:
        parsed = try_json(triple.group(1).strip())
        if parsed is not None:
            return parsed

    quoted = re.search(r'=\s*("(?:\\.|[^"])*")\s*$', text, re.DOTALL)
    if quoted:
        decoded = try_json(quoted.group(1))
        if isinstance(decoded, str):
            nested = try_json(decoded)
            return nested if nested is not None else decoded

    for left, right in [("[", "]"), ("{", "}")]:
        start = text.find(left)
        end = text.rfind(right)
        if start >= 0 and end > start:
            parsed = try_json(text[start : end + 1])
            if parsed is not None:
                return parsed

    raise ValueError(f"Could not parse Joern JSON output:\n{text[:1000]}")


class JoernRunner:
    """A class to interact with a Joern server for importing code repositories and running queries."""
    def __init__(self, server: str) -> None:
        self.client = CPGQLSClient(server)

    def import_repo(self, repo_path: Path, project_name: str) -> None:
        print(f"[joern] importing repo: {repo_path}")
        result = self.client.execute(import_code_query(str(repo_path), project_name))
        stdout = result.get("stdout", "") if isinstance(result, dict) else str(result)
        if stdout:
            print(stdout[:1000])

    def run_json_query(self, name: str, query: str) -> Any:
        print(f"[joern] query: {name}")
        result = self.client.execute(query)
        stdout = result.get("stdout", "") if isinstance(result, dict) else str(result)
        return parse_joern_json(stdout)

    def run_raw_query(self, name: str, query: str) -> str:
        print(f"[joern] raw query: {name}")
        result = self.client.execute(query)
        return result.get("stdout", "") if isinstance(result, dict) else str(result)

    def collect_facts(self, max_items: int) -> dict[str, Any]:
        """Collect facts from the Joern server by running predefined queries.

        Args:
            max_items (int): The maximum number of items to retrieve for each query.
        Returns:
            dict[str, Any]: A dictionary containing the results of the queries, keyed by query name.
        """
        facts: dict[str, Any] = {}

        for name, query in joern_queries(max_items).items():
            try:
                facts[name] = self.run_json_query(name, query)
            except Exception as exc:
                print(f"[warn] Joern query failed: {name}: {exc}")
                facts[name] = []

        try:
            facts["raw_reachable_by_flows"] = self.run_raw_query(
                "raw_reachable_by_flows",
                reachable_by_flows_query(),
            )[:8000]
        except Exception as exc:
            print(f"[warn] Joern reachableByFlows query failed: {exc}")
            facts["raw_reachable_by_flows"] = ""

        return facts
