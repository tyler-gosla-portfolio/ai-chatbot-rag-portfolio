from app.services.rag import RagService


def test_chunking_and_similarity():
    rag = RagService()
    chunks = rag.chunk_text("One two three four five\n\nSix seven eight nine ten")
    assert len(chunks) >= 1

    sim = rag.cosine_similarity([1.0, 0.0], [1.0, 0.0])
    low = rag.cosine_similarity([1.0, 0.0], [0.0, 1.0])
    assert sim > low
