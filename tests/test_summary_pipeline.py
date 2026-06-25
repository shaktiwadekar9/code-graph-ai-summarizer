from pathlib import Path

from code_graph_ai_summarizer.cli.main import main
from code_graph_ai_summarizer.summarization.facts_builder import build_summary_facts
from code_graph_ai_summarizer.summarization.prompts import build_summary_prompt


def sample_graph_facts():
    return {
        "files": [
            "app/main.py",
            "app/api.py",
            "app/service.py",
            "app/db.py",
        ],
        "methods": [
            {"file": "app/main.py", "name": "main", "fullName": "app.main.main"},
            {"file": "app/api.py", "name": "chat_endpoint", "fullName": "app.api.chat_endpoint"},
            {"file": "app/service.py", "name": "answer_question", "fullName": "app.service.answer_question"},
            {"file": "app/db.py", "name": "save_answer", "fullName": "app.db.save_answer"},
        ],
        "types": [
            {"file": "app/service.py", "name": "ChatService", "fullName": "app.service.ChatService"},
        ],
        "call_edges": [
            {
                "callerFile": "app/main.py",
                "caller": "app.main.main",
                "callees": "app.api.chat_endpoint",
                "externalCallees": "",
            },
            {
                "callerFile": "app/api.py",
                "caller": "app.api.chat_endpoint",
                "callees": "app.service.answer_question",
                "externalCallees": "",
            },
            {
                "callerFile": "app/service.py",
                "caller": "app.service.answer_question",
                "callees": "app.db.save_answer",
                "externalCallees": "openai.chat.completions.create",
            },
            {
                "callerFile": "app/db.py",
                "caller": "app.db.save_answer",
                "callees": "",
                "externalCallees": "sqlite.execute",
            },
        ],
        "calls": [
            {
                "file": "app/api.py",
                "method": "app.api.chat_endpoint",
                "name": "request",
                "code": "request.body()",
                "target": "fastapi.Request",
            },
            {
                "file": "app/service.py",
                "method": "app.service.answer_question",
                "name": "create",
                "code": "openai.chat.completions.create(...)",
                "target": "openai.chat.completions.create",
            },
            {
                "file": "app/db.py",
                "method": "app.db.save_answer",
                "name": "execute",
                "code": "db.execute('insert into answers values (?)')",
                "target": "sqlite.execute",
            },
        ],
        "entry_candidates": [
            {"file": "app/main.py", "name": "main", "fullName": "app.main.main"},
        ],
        "source_sink_calls": [
            {
                "file": "app/api.py",
                "method": "app.api.chat_endpoint",
                "name": "request",
                "code": "request.body()",
                "target": "fastapi.Request",
            },
            {
                "file": "app/db.py",
                "method": "app.db.save_answer",
                "name": "execute",
                "code": "db.execute('insert into answers values (?)')",
                "target": "sqlite.execute",
            },
        ],
        "raw_reachable_by_flows": "sample joern data-flow output",
    }


def test_build_summary_facts_extracts_core_repo_sections():
    facts = build_summary_facts(Path("/tmp/demo_repo"), sample_graph_facts())

    assert facts["repo_name"] == "demo_repo"
    assert facts["repo_map"]["file_count"] == 4

    edges = {
        (edge["from"], edge["to"])
        for edge in facts["architecture_signals"]["file_call_edges"]
    }

    assert ("app/main.py", "app/api.py") in edges
    assert ("app/api.py", "app/service.py") in edges
    assert ("app/service.py", "app/db.py") in edges

    assert facts["critical_runtime_flow_candidates"]
    assert facts["critical_data_flow_candidates"]
    assert "important_symbols" in facts


def test_summary_prompt_includes_important_symbols():
    facts = {
        "repo_name": "demo_repo",
        "repo_map": {"file_count": 1},
        "important_symbols": {
            "methods": [
                {"fullName": "ImportantSymbolThatShouldAppearInPrompt"}
            ]
        },
    }

    prompt = build_summary_prompt(facts)

    assert "important_symbols" in prompt
    assert "ImportantSymbolThatShouldAppearInPrompt" in prompt
    assert "# Repository Summary" in prompt


def test_cli_entrypoint_imports():
    assert callable(main)