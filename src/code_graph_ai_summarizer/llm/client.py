from __future__ import annotations

import os

from openai import OpenAI

from code_graph_ai_summarizer.config.settings import LLMConfig
from code_graph_ai_summarizer.summarization.prompts import build_summary_prompt


def make_client(config: LLMConfig) -> OpenAI:
    """Creates an OpenAI client with the specified configuration.
    
    Args:
        config (LLMConfig): Configuration for the LLM, including API key and base URL.

    Returns:
        OpenAI: An instance of the OpenAI client.
    """
    default_headers = None

    if config.provider == "openrouter":
        default_headers = {
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
            "X-OpenRouter-Title": os.getenv(
                "OPENROUTER_APP_NAME",
                "code-graph-ai-summarizer",
            ),
        }

    return OpenAI(
        api_key=config.api_key,
        base_url=config.base_url,
        default_headers=default_headers,
    )


def generate_repo_summary(summary_facts: dict, config: LLMConfig) -> str:
    """Generates a structured summary of a code repository using an LLM.
    
    Args:
        summary_facts (dict): A dictionary containing facts about the repository.
        config (LLMConfig): Configuration for the LLM, including model, temperature, and max tokens.

    Returns:
        str: The generated summary of the repository.
    """
    client = make_client(config)

    response = client.chat.completions.create(
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise static-analysis repo summarizer. "
                    "You must not hallucinate unsupported repo facts."
                ),
            },
            {
                "role": "user",
                "content": build_summary_prompt(summary_facts),
            },
        ],
    )

    return response.choices[0].message.content or ""