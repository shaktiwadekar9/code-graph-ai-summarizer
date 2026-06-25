from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path


def build_repo_map(files: list[str]) -> dict:
    folder_counter: Counter[str] = Counter()
    folder_examples: dict[str, list[str]] = defaultdict(list)

    clean_files = [
        file for file in files
        if file and not file.startswith("<") and file not in {"N/A", "UNKNOWN"}
    ]

    for file in clean_files:
        path = Path(file)
        parts = path.parts
        folder = "." if len(parts) <= 1 else str(Path(*parts[: min(2, len(parts) - 1)]))
        folder_counter[folder] += 1

        if len(folder_examples[folder]) < 8:
            folder_examples[folder].append(file)

    return {
        "file_count": len(clean_files),
        "top_folders": [
            {
                "folder": folder,
                "file_count": count,
                "examples": folder_examples[folder],
            }
            for folder, count in folder_counter.most_common(30)
        ],
        "files_sample": clean_files[:100],
    }
