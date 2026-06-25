from __future__ import annotations

import json
from typing import Any


def build_summary_prompt(summary_facts: dict[str, Any]) -> str:

    # The symbols are too many, so removing it for testing.
    # summary_facts_for_prompt = dict(summary_facts)
    # summary_facts_for_prompt.pop("important_symbols", None)

    # facts_json = json.dumps(summary_facts_for_prompt, indent=2)
    facts_json = json.dumps(summary_facts, indent=2)

    return f"""
You are generating a repository summary using Joern Code Property Graph facts.

Use only the supplied graph facts.
Do not invent files, folders, APIs, tests, classes, functions, runtime flows, or data flows.
Separate detected facts from inferred conclusions.
For runtime flows and data flows, include only the critical ones, not every path.
If something is weakly supported, say "likely".
If something is not supported, say "not detected".

Return Markdown with exactly these sections:

# Repository Summary

## 1. Repository Purpose
Explain the likely purpose. Mark it as inferred from graph evidence.

## 2. Repository Map
Summarize major folders/files and their roles.

## 3. Architecture
Describe layers/components using graph evidence:
- entry/UI/API/CLI layer
- service/business logic layer
- storage layer
- external integration layer
- worker/background layer if detected

## 4. Critical Runtime Flows
Give at most 5 important flows.
Each flow should include:
- flow name
- path
- evidence files/methods
- confidence: high/medium/low

## 5. Critical Data Flows
Give at most 5 important data flows.
Each flow should include:
- data source
- transformations / method path
- sink
- evidence files/methods
- confidence: high/medium/low

## 6. Important Files
List important files and why they matter.

## 7. Important Symbols
List important classes/functions/methods.

## 8. Not Detected / Unknown
Mention what the graph could not prove.

Here are the Joern-derived facts:

```json
{facts_json}
```
""".strip()
