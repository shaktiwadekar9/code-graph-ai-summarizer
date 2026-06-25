# Code Graph AI Summarizer

Production-ready Python project for generating a structured AI repository summary of a local repo using:

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

## Explainer Article

I wrote a detailed explainer on the core idea behind this project:

**[Stop Letting LLMs Hallucinate Your Codebase: A Graph-First Way to Summarize Repos](https://medium.com/towards-artificial-intelligence/stop-letting-llms-hallucinate-your-codebase-a-graph-first-way-to-summarize-repos-8a803db9c931)**


## Folder Structure

```text
code-graph-ai-summarizer/
├── src/
│   └── code_graph_ai_summarizer/
│       ├── __init__.py              # package exports
│       ├── api.py                   # public Python API
│       ├── cli/                     # command-line entry point
│       │   └── main.py
│       ├── config/                  # environment/config loading
│       │   └── settings.py
│       ├── joern/                   # Joern client + CPGQL queries
│       │   ├── client.py
│       │   └── queries.py
│       ├── analysis/                # graph analysis and ranking
│       ├── summarization/           # LLM facts + prompts
│       ├── llm/                     # OpenAI-compatible LLM client
│       ├── output/                  # output file helpers
│       └── utils/                   # shared utilities
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## How It Works

```text
local repo
  -> Joern imports the repo into a Code Property Graph
  -> CPGQL queries extract files, methods, types, calls, and entry candidates
  -> Python builds compact summary facts
  -> LLM generates the final repo summary
  -> Summary is returned through the Python API or written as repo_summary.md
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

## Run as a CLI

Generate a repo summary for any local repository:

```bash
uv run code-graph-ai-summarizer /path/to/local/repo
```

Example:

```bash
uv run code-graph-ai-summarizer ../some-other-repo
```

This creates the following output:

```text
outputs/<repo-name>/
├── joern_facts.json
├── summary_facts.json
└── repo_summary.md
```

The main output file is:

```text
outputs/<repo-name>/repo_summary.md
```

## Use as a Python Package

You can use this repo as a package directly from GitHub inside another Python project.

### 1. Install from GitHub

From your other project, run:

```bash
uv add "code-graph-ai-summarizer @ git+https://github.com/shaktiwadekar9/code-graph-ai-summarizer.git"
```

This installs `code-graph-ai-summarizer` as a dependency.

### 2. Use it in Python

```python
from code_graph_ai_summarizer import summarize_repository

result = summarize_repository("/path/to/local/repo")

repo_summary = result.summary
```

`repo_summary` now contains the generated Markdown summary as a Python string.

### 3. Write output files also

If you want the package to also write files like `repo_summary.md`, use:

```python
from code_graph_ai_summarizer import summarize_repository

result = summarize_repository(
    "/path/to/local/repo",
    write_outputs=True,
)

print(result.summary)
print(result.summary_path)
```

This writes output files under:

```text
outputs/<repo-name>/
├── joern_facts.json
├── summary_facts.json
└── repo_summary.md
```

## Run Tests

This project uses `pytest` for running tests.


### Run tests with detailed output

```bash
uv run pytest -v
```

### Run one test file

```bash
uv run pytest tests/test_file_name.py
```

## Notes

- Joern is the current backend for graph facts.
- Python ranks important files, paths, and signals.
- The LLM only writes the final natural-language summary.
- The prompt tells the LLM not to invent files, APIs, tests, runtime flows, or data flows.
