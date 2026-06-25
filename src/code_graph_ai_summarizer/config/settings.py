from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    api_key: str
    model: str
    base_url: str
    temperature: float = 0.1
    max_tokens: int = 5000


@dataclass(frozen=True)
class AppConfig:
    repo_path: Path
    out_dir: Path
    joern_server: str
    project_name: str | None
    max_items: int
    skip_import: bool
    llm: LLMConfig


PROVIDER_ENV = {
    "ollama": {
        "api_key_env": None,
        "model_env": "OLLAMA_MODEL",
        "base_url_env": "OLLAMA_BASE_URL",
        "default_api_key": "ollama",
        "default_model": "qwen2.5-coder:7b",
        "default_base_url": "http://localhost:11434/v1",
    },
    "groq": {
        "api_key_env": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "base_url_env": "GROQ_BASE_URL",
        "default_api_key": "",
        "default_model": "llama-3.3-70b-versatile",
        "default_base_url": "https://api.groq.com/openai/v1",
    },
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "base_url_env": "GEMINI_BASE_URL",
        "default_api_key": "",
        "default_model": "gemini-2.5-flash",
        "default_base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "cerebras": {
        "api_key_env": "CEREBRAS_API_KEY",
        "model_env": "CEREBRAS_MODEL",
        "base_url_env": "CEREBRAS_BASE_URL",
        "default_api_key": "",
        "default_model": "llama-4-scout-17b-16e-instruct",
        "default_base_url": "https://api.cerebras.ai/v1",
    },
    "openrouter": {
        "api_key_env": "OPENROUTER_API_KEY",
        "model_env": "OPENROUTER_MODEL",
        "base_url_env": "OPENROUTER_BASE_URL",
        "default_api_key": "",
        "default_model": "openai/gpt-4o-mini",
        "default_base_url": "https://openrouter.ai/api/v1",
    },
}


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name, "").strip()
    return float(value) if value else default


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    return int(value) if value else default


def load_llm_config() -> LLMConfig:
    """Loads the LLM configuration from environment variables.

    Returns:
        LLMConfig: The loaded LLM configuration.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider not in PROVIDER_ENV:
        valid = ", ".join(PROVIDER_ENV)
        raise RuntimeError(f"Invalid LLM_PROVIDER='{provider}'. Use one of: {valid}")

    env = PROVIDER_ENV[provider]

    api_key_env = env["api_key_env"]
    api_key = env["default_api_key"]

    if api_key_env:
        api_key = os.getenv(api_key_env, "").strip()

    model = os.getenv(env["model_env"], env["default_model"]).strip()
    base_url = os.getenv(env["base_url_env"], env["default_base_url"]).strip()

    if provider != "ollama" and not api_key:
        raise RuntimeError(
            f"Missing API key for provider '{provider}'. "
            f"Set {api_key_env} in your .env file."
        )

    if not model:
        raise RuntimeError(f"Missing model for provider '{provider}'.")

    if not base_url:
        raise RuntimeError(f"Missing base URL for provider '{provider}'.")

    return LLMConfig(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
        temperature=_get_float_env("LLM_TEMPERATURE", 0.1),
        max_tokens=_get_int_env("LLM_MAX_TOKENS", 5000),
    )