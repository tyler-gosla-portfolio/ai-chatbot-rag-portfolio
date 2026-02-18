import pytest
from app.services.rag import build_rag_prompt

class TestBuildRAGPrompt:
    def test_basic_prompt_assembly(self):
        sources = [
            {
                "document_title": "Test Doc",
                "chunk_index": 0,
                "content": "This is chunk content.",
                "content_preview": "This is chunk content.",
                "similarity": 0.85,
                "document_id": "doc-1",
            }
        ]
        messages = build_rag_prompt("What is this about?", sources)

        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "system"
        assert messages[2]["role"] == "user"
        assert "What is this about?" in messages[2]["content"]
        assert "This is chunk content." in messages[1]["content"]

    def test_prompt_with_no_sources(self):
        messages = build_rag_prompt("Hello?", [])
        assert len(messages) == 3
        assert "No relevant context found" in messages[1]["content"]

    def test_custom_system_prompt(self):
        messages = build_rag_prompt(
            "test query",
            [],
            system_prompt="You are a specialized assistant."
        )
        assert "specialized assistant" in messages[0]["content"]

    def test_multiple_sources(self):
        sources = [
            {
                "document_title": f"Doc {i}",
                "chunk_index": i,
                "content": f"Content {i}",
                "content_preview": f"Content {i}",
                "similarity": 0.8,
                "document_id": f"doc-{i}",
            }
            for i in range(3)
        ]
        messages = build_rag_prompt("multi-source query", sources)
        context = messages[1]["content"]
        assert "Doc 0" in context
        assert "Doc 1" in context
        assert "Doc 2" in context
