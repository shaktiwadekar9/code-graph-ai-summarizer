from __future__ import annotations

import argparse

from code_graph_ai_summarizer.api import summarize_repository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a structured repo summary using Joern + OpenAI-compatible LLM."
    )

    parser.add_argument("repo_path", help="Path to local repo")
    parser.add_argument("--out", default="outputs", help="Output directory")
    parser.add_argument(
        "--joern-server",
        default="localhost:8080",
        help="Joern CPGQL server",
    )
    parser.add_argument(
        "--project-name",
        default=None,
        help="Optional Joern project name",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=3000,
        help="Max CPG items per query",
    )
    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Skip Joern import if project is already active/imported",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    result = summarize_repository(
        repo_path=args.repo_path,
        out_dir=args.out,
        joern_server=args.joern_server,
        project_name=args.project_name,
        max_items=args.max_items,
        skip_import=args.skip_import,
        write_outputs=True,
    )

    print("\nDone.")

    if result.joern_facts_path:
        print(f"Raw Joern facts: {result.joern_facts_path}")

    if result.summary_facts_path:
        print(f"Compact summary JSON: {result.summary_facts_path}")

    if result.summary_path:
        print(f"Repo summary: {result.summary_path}")


if __name__ == "__main__":
    main()