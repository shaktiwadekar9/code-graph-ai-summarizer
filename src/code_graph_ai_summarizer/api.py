from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from code_graph_ai_summarizer.config.settings import LLMConfig, load_llm_config
from code_graph_ai_summarizer.joern.client import JoernRunner, project_name_for
from code_graph_ai_summarizer.llm.client import generate_repo_summary
from code_graph_ai_summarizer.output.files import ensure_dir, write_json, write_text
from code_graph_ai_summarizer.summarization.facts_builder import build_summary_facts


@dataclass(frozen=True)
class RepoSummaryResult:
    """Result returned by the public repo summarization API."""

    repo_path: Path
    project_name: str
    summary: str
    joern_facts: dict[str, Any]
    summary_facts: dict[str, Any]
    out_dir: Path | None = None
    joern_facts_path: Path | None = None
    summary_facts_path: Path | None = None
    summary_path: Path | None = None


def summarize_repository(
    repo_path: str | Path,
    *,
    out_dir: str | Path | None = None,
    joern_server: str = "localhost:8080",
    project_name: str | None = None,
    max_items: int = 3000,
    skip_import: bool = False,
    write_outputs: bool = False,
    llm_config: LLMConfig | None = None,
    load_env: bool = True,
) -> RepoSummaryResult:
    """Generate a graph-backed AI summary for a local repository.

    Args:
        repo_path: Path to the local repository to summarize.
        out_dir: Optional base output directory. Used only when write_outputs=True.
        joern_server: Joern CPGQL server address.
        project_name: Optional Joern project name. Auto-generated if not provided.
        max_items: Max number of CPG items collected per query.
        skip_import: Skip Joern import if the repo is already imported.
        write_outputs: Whether to write joern_facts.json, summary_facts.json, and repo_summary.md.
        llm_config: Optional explicit LLM config. If not passed, environment config is loaded.
        load_env: Whether to load .env before reading LLM settings.

    Returns:
        RepoSummaryResult containing the final summary and supporting facts.
    """

    if load_env:
        load_dotenv()

    resolved_repo_path = Path(repo_path).expanduser().resolve()

    if not resolved_repo_path.exists() or not resolved_repo_path.is_dir():
        raise ValueError(
            f"Repo path does not exist or is not a directory: {resolved_repo_path}"
        )

    effective_project_name = project_name or project_name_for(resolved_repo_path)
    effective_llm_config = llm_config or load_llm_config()

    print(f"[config] repo: {resolved_repo_path}")
    print(f"[config] joern server: {joern_server}")
    print(f"[config] joern project: {effective_project_name}")
    print(f"[config] llm provider: {effective_llm_config.provider}")
    print(f"[config] llm model: {effective_llm_config.model}")

    joern = JoernRunner(joern_server)

    if not skip_import:
        joern.import_repo(resolved_repo_path, effective_project_name)

    joern_facts = joern.collect_facts(max_items)
    summary_facts = build_summary_facts(resolved_repo_path, joern_facts)

    print("[llm] generating repo summary")
    summary = generate_repo_summary(summary_facts, effective_llm_config)

    resolved_out_dir: Path | None = None
    joern_facts_path: Path | None = None
    summary_facts_path: Path | None = None
    summary_path: Path | None = None

    if write_outputs:
        base_out_dir = Path(out_dir or "outputs").expanduser().resolve()
        resolved_out_dir = base_out_dir / resolved_repo_path.name
        ensure_dir(resolved_out_dir)

        joern_facts_path = resolved_out_dir / "joern_facts.json"
        summary_facts_path = resolved_out_dir / "summary_facts.json"
        summary_path = resolved_out_dir / "repo_summary.md"

        write_json(joern_facts_path, joern_facts)
        write_json(summary_facts_path, summary_facts)
        write_text(summary_path, summary)

    return RepoSummaryResult(
        repo_path=resolved_repo_path,
        project_name=effective_project_name,
        summary=summary,
        joern_facts=joern_facts,
        summary_facts=summary_facts,
        out_dir=resolved_out_dir,
        joern_facts_path=joern_facts_path,
        summary_facts_path=summary_facts_path,
        summary_path=summary_path,
    )