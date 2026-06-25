from code_graph_ai_summarizer.analysis.repo_map import build_repo_map


def test_build_repo_map_groups_files_by_folder():
    repo_map = build_repo_map([
        "src/app/main.py",
        "src/app/service.py",
        "tests/test_app.py",
    ])

    assert repo_map["file_count"] == 3
    assert repo_map["top_folders"]
