"""Rerank step: candidate depth, per-query ranking, startup check and reported mode."""

import json

import pytest
from fastapi.testclient import TestClient

from verity import reranker, retrieval
from verity.llm import LLMUsage


class FakeCollection:
    def __init__(self) -> None:
        self.n_results: int | None = None

    def query(self, query_embeddings, n_results, include):
        self.n_results = n_results
        docs, metas, dists = [], [], []
        for q, _ in enumerate(query_embeddings):
            docs.append([f"text {q}-{i}" for i in range(n_results)])
            metas.append(
                [
                    {"source": f"d{q}_{i}.md", "doc_title": "T", "chunk_index": i}
                    for i in range(n_results)
                ]
            )
            dists.append([0.01 * (i + 1) for i in range(n_results)])
        return {"documents": docs, "metadatas": metas, "distances": dists}


class ReverseReranker:
    """Ranks the last candidate best; records which query each call was against."""

    def __init__(self) -> None:
        self.queries: list[str] = []

    def rerank(self, query, chunks):
        self.queries.append(query)
        n = len(chunks)
        return [
            c.model_copy(update={"score": (i + 1) / n, "score_kind": "rerank"})
            for i, c in enumerate(reversed(chunks))
        ]


@pytest.fixture
def collection(monkeypatch: pytest.MonkeyPatch) -> FakeCollection:
    fake = FakeCollection()
    monkeypatch.setattr(retrieval, "_get_collection", lambda: fake)
    monkeypatch.setattr(retrieval, "_embed", lambda texts: [[0.0] for _ in texts])
    return fake


def test_reranking_fetches_twenty_candidates_per_query(collection: FakeCollection) -> None:
    retrieval.query_kb_by_query(["a", "b"], reranker=ReverseReranker())

    assert collection.n_results == 20


def test_mode_none_fetches_five_candidates_ranked_by_cosine(collection: FakeCollection) -> None:
    result = retrieval.query_kb_by_query(["a"])

    assert collection.n_results == 5
    assert [c.source for c in result[0].chunks] == [f"d0_{i}.md" for i in range(5)]
    assert {c.score_kind for c in result[0].chunks} == {"cosine"}


def test_each_query_is_reranked_against_its_own_query(collection: FakeCollection) -> None:
    fake = ReverseReranker()

    result = retrieval.query_kb_by_query(["first", "second"], reranker=fake)

    assert fake.queries == ["first", "second"]
    assert result[0].chunks[0].source == "d0_19.md"  # reranker's best, not cosine's
    assert result[1].chunks[0].source == "d1_19.md"
    assert {c.score_kind for r in result for c in r.chunks} == {"rerank"}


def test_default_reranker_comes_from_the_configured_mode(
    collection: FakeCollection, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = ReverseReranker()
    monkeypatch.setattr(retrieval, "get_reranker", lambda: fake)

    result = retrieval.query_kb_by_query(["a"])

    assert fake.queries == ["a"]
    assert result[0].chunks[0].score_kind == "rerank"


def test_librarian_merges_reranked_candidates_into_five_rerank_chunks(
    collection: FakeCollection, monkeypatch: pytest.MonkeyPatch
) -> None:
    from verity.agents import librarian
    from verity.schemas import SimpleLibrarianOutput, TicketState

    monkeypatch.setattr(retrieval, "get_reranker", lambda: ReverseReranker())
    monkeypatch.setattr(
        librarian,
        "parse_json_with_retry",
        lambda *a, **k: (
            SimpleLibrarianOutput(queries=["a"]),
            LLMUsage(1, 1, 2, 0.001),
        ),
    )

    update = librarian.run_librarian(TicketState(raw_text="x", customer_id="c", channel="web"))

    sources = [c["source"] for c in update["retrieved_chunks"]]
    assert sources == [f"d0_{i}.md" for i in (19, 18, 17, 16, 15)]
    assert {c["score_kind"] for c in update["retrieved_chunks"]} == {"rerank"}


def test_mode_defaults_to_qwen_and_rejects_unknown_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RERANKER_MODE")
    assert reranker.get_reranker_mode() == "qwen"

    monkeypatch.setenv("RERANKER_MODE", "bogus")
    with pytest.raises(ValueError, match="RERANKER_MODE"):
        reranker.get_reranker_mode()


def test_startup_fails_naming_the_missing_model_when_mode_is_qwen(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    monkeypatch.setenv("RERANKER_MODE", "qwen")
    monkeypatch.setenv("RERANKER_MODEL_DIR", str(tmp_path / "nope"))
    reranker._load_qwen.cache_clear()

    with pytest.raises(reranker.RerankerUnavailable) as err:
        reranker.check_reranker_startup()

    assert "Qwen3-Reranker-0.6B" in str(err.value)
    assert "RERANKER_MODE=none" in str(err.value)


def test_startup_fails_naming_the_missing_runtime(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    import builtins

    real_import = builtins.__import__

    def no_torch(name, *a, **k):
        if name == "torch":
            raise ImportError("no torch", name="torch")
        return real_import(name, *a, **k)

    monkeypatch.setenv("RERANKER_MODE", "qwen")
    monkeypatch.setenv("RERANKER_MODEL_DIR", str(tmp_path))
    monkeypatch.setattr(builtins, "__import__", no_torch)
    reranker._load_qwen.cache_clear()

    with pytest.raises(reranker.RerankerUnavailable, match="torch.*RERANKER_MODE=none"):
        reranker.check_reranker_startup()


def test_startup_passes_when_mode_is_none() -> None:
    reranker.check_reranker_startup()


@pytest.mark.parametrize("mode", ["qwen", "none"])
def test_triage_response_reports_reranker_mode(monkeypatch: pytest.MonkeyPatch, mode: str) -> None:
    import verity.graph
    from verity.api import app

    class Pipeline:
        async def astream(self, initial):
            yield {"dispatcher": {"final_action": "send", "final_response": "hi",
                                  "agent_timings": {"dispatcher": 1.0}}}

    monkeypatch.setenv("RERANKER_MODE", mode)
    monkeypatch.setattr(verity.graph, "pipeline", Pipeline())

    resp = TestClient(app).post(
        "/triage", json={"ticket_text": "help", "customer_id": "c", "channel": "web"}
    )

    done = next(
        json.loads(line[5:]) for line in resp.text.splitlines() if line.startswith("data:")
        and "reranker_mode" in line
    )
    assert done["reranker_mode"] == mode
