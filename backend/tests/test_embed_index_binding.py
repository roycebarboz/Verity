"""The embedding model is tied to the index (ADR 0002): mismatch refuses, match opens."""

import pytest

from verity import llm, retrieval


class FakeClient:
    def __init__(self, metadata: dict | None) -> None:
        self.collection = type("C", (), {"metadata": metadata})()

    def get_collection(self, name: str):
        return self.collection


@pytest.fixture(autouse=True)
def isolated(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("CHROMA_DIR", str(tmp_path))
    monkeypatch.delenv("EMBED_MODEL", raising=False)
    retrieval._get_collection.cache_clear()
    yield
    retrieval._get_collection.cache_clear()


def _open_with(monkeypatch: pytest.MonkeyPatch, metadata: dict | None):
    client = FakeClient(metadata)
    monkeypatch.setattr(retrieval.chromadb, "PersistentClient", lambda path: client)
    return retrieval._get_collection()


def test_matching_model_opens_the_index(monkeypatch: pytest.MonkeyPatch) -> None:
    meta = {llm.INDEX_EMBED_MODEL_KEY: "text-embedding-3-small"}
    assert _open_with(monkeypatch, meta) is not None


def test_default_embedding_model_is_todays_model() -> None:
    assert llm.embed_model() == "text-embedding-3-small"


def test_mismatched_model_refuses_and_says_to_reingest(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBED_MODEL", "text-embedding-3-large")
    meta = {llm.INDEX_EMBED_MODEL_KEY: "text-embedding-3-small"}
    with pytest.raises(llm.IndexModelMismatch, match="Re-ingest"):
        _open_with(monkeypatch, meta)


def test_index_without_recorded_model_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(llm.IndexModelMismatch, match="Re-ingest"):
        _open_with(monkeypatch, {"hnsw:space": "cosine"})


def test_embed_uses_configured_model(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = {}

    def fake_embedding(model, input, **kw):
        seen["model"] = model
        return type("R", (), {"data": [{"embedding": [1.0]} for _ in input]})()

    monkeypatch.setattr(llm.litellm, "embedding", fake_embedding)
    monkeypatch.setenv("EMBED_MODEL", "voyage/voyage-3")
    assert llm.embed(["a", "b"]) == [[1.0], [1.0]]
    assert seen["model"] == "voyage/voyage-3"
