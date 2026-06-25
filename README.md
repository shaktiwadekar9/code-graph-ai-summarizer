# Code Graph AI Summarizer

Production-ready Python project for generating a structured AI repository summary from a local repo using:

- **Joern** for Code Property Graph facts behind the scenes
- **Python analysis modules** for ranking architecture, runtime-flow, and data-flow candidates
- **OpenAI-compatible LLM APIs** for the final Markdown summary

The output contains:

1. repo purpose
2. repo map
3. architecture
4. critical runtime flows
5. critical data flows
6. important files
7. important symbols
8. unknowns / not detected

## Folder structure

```text
code-graph-ai-summarizer/
├── src/
│   └── code_graph_ai_summarizer/
│       ├── cli/                  # command-line entry point
│       │   └── main.py
│       ├── config/               # environment/config loading
│       │   └── settings.py
│       ├── joern/                # Joern client + CPGQL queries
│       │   ├── client.py
│       │   └── queries.py
│       ├── analysis/             # graph analysis and ranking
│       │   ├── architecture.py
│       │   ├── classify.py
│       │   ├── flows.py
│       │   ├── graph.py
│       │   ├── patterns.py
│       │   └── repo_map.py
│       ├── summarization/        # LLM facts + prompts
│       │   ├── facts_builder.py
│       │   └── prompts.py
│       ├── llm/                  # OpenAI-compatible LLM client
│       │   └── client.py
│       ├── output/               # output file helpers
│       │   └── files.py
│       └── utils/                # shared utilities
│           └── text.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## How it works

```text
local repo
  -> Joern imports repo into CPG
  -> CPGQL queries extract files, methods, types, call edges, calls, entry candidates
  -> Python derives repo map, architecture signals, runtime flow candidates, data flow candidates
  -> LLM writes repo_summary.md from only those facts
```

This is static analysis. Runtime/data flows are graph-derived candidates, not guaranteed real production traces.

## Requirements

- Python 3.11+
- uv
- Joern installed and running
- API key for one OpenAI-compatible provider:
  - Groq
  - OpenRouter
  - Gemini AI Studio OpenAI-compatible endpoint
  - Cerebras
  - OpenAI

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env`:

```bash
LLM_PROVIDER=groq
LLM_API_KEY=your_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
```

## Start Joern

In a separate terminal:

```bash
joern --server
```

Default server expected by this tool:

```text
localhost:8080
```

## Run

```bash
uv run python -m code_graph_ai_summarizer /path/to/local/repo
```

Or use the console script:

```bash
uv run code-graph-ai-summarizer /path/to/local/repo
```

Output:

```text
outputs/<repo-name>/
├── joern_facts.json
├── summary_facts.json
└── repo_summary.md
```

## Notes

- Joern is the current backend for graph facts.
- Python ranks important files, paths, and signals.
- The LLM only writes the final natural-language summary.
- The prompt tells the LLM not to invent files, APIs, tests, runtime flows, or data flows.
