import socket
from pathlib import Path

import pytest

from code_graph_ai_summarizer.joern.client import parse_joern_json, project_name_for
from code_graph_ai_summarizer.joern.queries import joern_queries, reachable_by_flows_query


JOERN_HOST = "localhost"
JOERN_PORT = 8080


def is_joern_server_running() -> bool:
    """Return True if Joern CPGQL server is reachable."""
    try:
        with socket.create_connection((JOERN_HOST, JOERN_PORT), timeout=1):
            return True
    except OSError:
        return False


def test_parse_joern_json_from_raw_json():
    output = '[{"file": "app/main.py", "name": "main"}]'

    parsed = parse_joern_json(output)

    assert parsed == [{"file": "app/main.py", "name": "main"}]


def test_project_name_for_is_stable(tmp_path: Path):
    repo_path = tmp_path / "demo-repo"
    repo_path.mkdir()

    name_1 = project_name_for(repo_path)
    name_2 = project_name_for(repo_path)

    assert name_1 == name_2
    assert name_1.startswith("demo-repo-")


def test_joern_queries_have_required_sections():
    queries = joern_queries(max_items=50)

    assert "files" in queries
    assert "methods" in queries
    assert "types" in queries
    assert "call_edges" in queries
    assert "entry_candidates" in queries
    assert "source_sink_calls" in queries

    for query in queries.values():
        assert "take(50)" in query
        assert "toJson" in query


def test_reachable_by_flows_query_is_defined():
    query = reachable_by_flows_query()

    assert "reachableByFlows" in query
    assert "def source" in query
    assert "def sink" in query


def test_joern_server_optional_health_check():
    """
    Highlight:
    - If Joern server is NOT running, this test skips.
    - If Joern server IS running, this test checks that the client can connect.
    """
    if not is_joern_server_running():
        pytest.skip("Joern server is not running. Start it with: joern --server")

    from cpgqls_client import CPGQLSClient

    client = CPGQLSClient(f"{JOERN_HOST}:{JOERN_PORT}")
    result = client.execute("1 + 1")

    assert result is not None