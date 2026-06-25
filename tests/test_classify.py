from code_graph_ai_summarizer.analysis.classify import categories_for_text, is_sink_call, is_source_call


def test_categories_for_text_detects_llm_and_storage():
    categories = categories_for_text("openai chat completion save sqlite")

    assert "llm" in categories
    assert "storage_db" in categories


def test_source_and_sink_detection():
    assert is_source_call({"name": "read", "code": "read user input", "target": ""})
    assert is_sink_call({"name": "save", "code": "save result", "target": ""})
