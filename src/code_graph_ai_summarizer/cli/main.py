from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from code_graph_ai_summarizer.config.settings import AppConfig, load_llm_config
from code_graph_ai_summarizer.output.files import ensure_dir, write_json, write_text
from code_graph_ai_summarizer.joern.client import JoernRunner, project_name_for
from code_graph_ai_summarizer.llm.client import generate_repo_summary
from code_graph_ai_summarizer.summarization.facts_builder import build_summary_facts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a structured repo summary using Joern + OpenAI-compatible LLM."
    )
    parser.add_argument("repo_path", help="Path to local repo")
    parser.add_argument("--out", default="outputs", help="Output directory")
    parser.add_argument("--joern-server", default="localhost:8080", help="Joern CPGQL server")
    parser.add_argument("--project-name", default=None, help="Optional Joern project name")
    parser.add_argument("--max-items", type=int, default=3000, help="Max CPG items per query")
    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Skip Joern import if project is already active/imported",
    )
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> AppConfig:
    """Builds the application configuration from command-line arguments.
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments.
        
    Returns:
        AppConfig: The application configuration object.
    """
    repo_path = Path(args.repo_path).expanduser().resolve()

    if not repo_path.exists() or not repo_path.is_dir():
        raise RuntimeError(f"Repo path does not exist or is not a directory: {repo_path}")

    return AppConfig(
        repo_path=repo_path,
        out_dir=(Path(args.out).expanduser().resolve() / repo_path.name),
        joern_server=args.joern_server,
        project_name=args.project_name,
        max_items=args.max_items,
        skip_import=args.skip_import,
        llm=load_llm_config(),
    )


def run(config: AppConfig) -> None:
    """Run the main logic of the application. 
    This function orchestrates the process of importing a code repository into Joern, 
    collecting facts, generating a summary, and writing outputs to files.

    Args:
        config (AppConfig): The configuration object containing all necessary parameters.
    """
    ensure_dir(config.out_dir)

    project_name = config.project_name or project_name_for(config.repo_path)

    print(f"[config] repo: {config.repo_path}")
    print(f"[config] output: {config.out_dir}")
    print(f"[config] joern server: {config.joern_server}")
    print(f"[config] joern project: {project_name}")
    print(f"[config] llm provider: {config.llm.provider}")
    print(f"[config] llm model: {config.llm.model}")

    joern = JoernRunner(config.joern_server)

    if not config.skip_import:
        joern.import_repo(config.repo_path, project_name)

    facts = joern.collect_facts(config.max_items)
    summary_facts = build_summary_facts(config.repo_path, facts)

    facts_path = config.out_dir / "joern_facts.json"
    compact_path = config.out_dir / "summary_facts.json"
    summary_path = config.out_dir / "repo_summary.md"

    write_json(facts_path, facts)
    write_json(compact_path, summary_facts)

    print("[llm] generating repo summary")
    summary = generate_repo_summary(summary_facts, config.llm)
    write_text(summary_path, summary)

    print("\nDone.")
    print(f"Raw Joern facts:      {facts_path}")
    print(f"Compact summary JSON: {compact_path}")
    print(f"Repo summary:         {summary_path}")


def main() -> None:
    load_dotenv()
    config = build_config(parse_args())
    run(config)
