import pytest
from app.services.document import chunk_text, count_tokens, extract_text
import tempfile
import os

class TestChunking:
    def test_chunk_short_text(self):
        text = "Hello world. This is a test."
        chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
        assert len(chunks) == 1
        assert chunks[0].strip() == text

    def test_chunk_long_text(self):
        # Create text that's definitely longer than 500 tokens
        text = "This is a sentence with several words. " * 200
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=10)
        assert len(chunks) > 1

    def test_chunk_overlap(self):
        text = "word " * 300  # ~300 tokens
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
        assert len(chunks) >= 3

    def test_chunk_empty_text(self):
        chunks = chunk_text("", chunk_size=500, chunk_overlap=50)
        assert len(chunks) == 0

    def test_chunk_whitespace_only(self):
        chunks = chunk_text("   \n\n  ", chunk_size=500, chunk_overlap=50)
        assert len(chunks) == 0

class TestTokenCount:
    def test_count_tokens_simple(self):
        count = count_tokens("Hello world")
        assert count > 0
        assert count < 10

    def test_count_tokens_empty(self):
        count = count_tokens("")
        assert count == 0

class TestExtractText:
    def test_extract_text_from_txt_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Hello, this is test content.")
            f.flush()
            text = extract_text(f.name, "text/plain")
            assert "Hello, this is test content." in text
            os.unlink(f.name)

    def test_extract_text_from_markdown(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Title\n\nSome markdown content.")
            f.flush()
            text = extract_text(f.name, "text/markdown")
            assert "Title" in text
            assert "markdown content" in text
            os.unlink(f.name)
