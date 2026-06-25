from __future__ import annotations

CATEGORY_PATTERNS = {
    "api_web": [
        "fastapi", "flask", "django", "express", "router", "route",
        "controller", "request", "response", "http", "endpoint",
    ],
    "cli": [
        "argparse", "click", "typer", "commander", "cobra",
        "process.argv", "main", "command", "cli",
    ],
    "storage_db": [
        "sqlite", "postgres", "mysql", "mongodb", "redis", "sqlalchemy",
        "prisma", "typeorm", "save", "insert", "update", "delete",
        "select", "execute", "commit", "query",
    ],
    "filesystem": [
        "open(", "readfile", "writefile", "fs.", "pathlib", "file",
        "files.", "read", "write",
    ],
    "llm": [
        "openai", "ollama", "anthropic", "gemini", "groq", "cerebras",
        "completion", "chat.completions", "llm", "model", "generate",
    ],
    "network": [
        "requests", "httpx", "urllib", "axios", "fetch", "grpc",
        "post", "put", "send", "client",
    ],
    "auth": ["jwt", "oauth", "token", "password", "auth", "login", "permission"],
    "queue_worker": [
        "celery", "rabbit", "kafka", "queue", "worker", "consumer",
        "cron", "schedule", "job",
    ],
}

SOURCE_PATTERNS = [
    "request", "input", "read", "upload", "file", "argv", "args",
    "getenv", "env", "body", "param", "query",
]

SINK_PATTERNS = [
    "write", "save", "insert", "update", "delete", "execute",
    "commit", "chat", "completion", "generate", "post", "put",
    "send", "return", "response",
]
