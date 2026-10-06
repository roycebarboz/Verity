"""verity.retrieval tested with the embedder and Chroma collection faked."""

import pytest

from verity import retrieval


class FakeCollection:
    """Returns n_results chunks per query embedding; query q gets docs named doc_q_i."""

    def query(self, query_embeddings, n_results, include):
        docs, metas, dists = [], [], []
        for q, _ in enumerate(query_embeddings):
            docs.append([f"text {q}-{i}" for i in range(n_results)])
            metas.append(
                [
                    {"source": f"doc_{q}_{i}.md", "doc_title": "T", "chunk_index": i}
                    for i in range(n_results)
                ]
            )
            dists.append([0.1 * (i + 1) for i in range(n_results)])
        return {"documents": docs, "metadatas": metas, "distances": dists}


@pytest.fixture(autouse=True)
def fake_backends(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(retrieval, "_get_collection", lambda: FakeCollection())
    monkeypatch.setattr(retrieval, "_embed", lambda texts: [[0.0] for _ in texts])


def test_query_kb_by_query_returns_five_chunks_for_each_query() -> None:
    result = retrieval.query_kb_by_query(["a", "b", "c"])

    assert [r.query for r in result] == ["a", "b", "c"]
    assert [len(r.chunks) for r in result] == [5, 5, 5]
    assert result[1].chunks[0].source == "doc_1_0.md"
    assert result[2].chunks[4].source == "doc_2_4.md"


def test_librarian_node_records_per_query_chunks_alongside_top_five(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    from verity.agents import librarian
    from verity.schemas import LibrarianOutput, TicketState

    monkeypatch.setattr(
        librarian,
        "parse_json_with_retry",
        lambda *a, **k: (
            LibrarianOutput(queries=["a", "b", "c"]),
            SimpleNamespace(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        ),
    )
    state = TicketState(raw_text="help", customer_id="c", channel="web")

    update = librarian.run_librarian(state)

    assert len(update["retrieved_chunks"]) == 5
    by_query = update["retrieval_by_query"]
    assert [q["query"] for q in by_query] == ["a", "b", "c"]
    assert sum(len(q["chunks"]) for q in by_query) == 15


def _chunk(source: str, idx: int = 0, score: float = 0.5):
    from verity.schemas import RetrievedChunk

    return RetrievedChunk(
        content=f"{source}-{idx}", source=source, doc_title="T", chunk_index=idx, score=score
    )


def _run_librarian_with(monkeypatch: pytest.MonkeyPatch, by_query):
    from types import SimpleNamespace

    from verity.agents import librarian
    from verity.schemas import LibrarianOutput, TicketState

    queries = [r.query for r in by_query]
    monkeypatch.setattr(librarian, "query_kb_by_query", lambda qs: by_query)
    monkeypatch.setattr(
        librarian,
        "parse_json_with_retry",
        lambda *a, **k: (
            LibrarianOutput(queries=queries),
            SimpleNamespace(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        ),
    )
    state = TicketState(raw_text="help", customer_id="c", channel="web")
    return librarian.run_librarian(state)


def _retrieval(query: str, chunks):
    from verity.schemas import QueryRetrieval

    return QueryRetrieval(query=query, chunks=chunks)


def test_librarian_takes_chunks_round_robin_by_rank_not_by_score(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    by_query = [
        _retrieval("a", [_chunk("a1", score=0.9), _chunk("a2", score=0.8), _chunk("a3", score=0.7)]),
        _retrieval("b", [_chunk("b1", score=0.2), _chunk("b2", score=0.1)]),
    ]

    update = _run_librarian_with(monkeypatch, by_query)

    assert [c["source"] for c in update["retrieved_chunks"]] == ["a1", "b1", "a2", "b2", "a3"]


def test_librarian_skips_duplicate_chunk_and_uses_next_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    by_query = [
        _retrieval("a", [_chunk("x", 0), _chunk("a2"), _chunk("a3")]),
        _retrieval("b", [_chunk("x", 0), _chunk("b2"), _chunk("b3")]),
    ]

    update = _run_librarian_with(monkeypatch, by_query)

    assert [c["source"] for c in update["retrieved_chunks"]] == ["x", "b2", "a2", "b3", "a3"]


def test_librarian_same_source_different_position_is_not_a_duplicate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    by_query = [
        _retrieval("a", [_chunk("x", 0)]),
        _retrieval("b", [_chunk("x", 1)]),
    ]

    update = _run_librarian_with(monkeypatch, by_query)

    assert [(c["source"], c["chunk_index"]) for c in update["retrieved_chunks"]] == [("x", 0), ("x", 1)]


def test_librarian_single_query_returns_its_top_five_in_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    by_query = [_retrieval("a", [_chunk(f"a{i}", score=0.9 - i / 10) for i in range(5)])]

    update = _run_librarian_with(monkeypatch, by_query)

    assert [c["source"] for c in update["retrieved_chunks"]] == [f"a{i}" for i in range(5)]


def test_librarian_fills_five_when_one_query_runs_dry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    by_query = [
        _retrieval("a", [_chunk(f"a{i}") for i in range(5)]),
        _retrieval("b", [_chunk("b0")]),
    ]

    update = _run_librarian_with(monkeypatch, by_query)

    assert [c["source"] for c in update["retrieved_chunks"]] == ["a0", "b0", "a1", "a2", "a3"]


def test_chunks_keep_own_score_and_record_score_kind(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    by_query = [_retrieval("a", [_chunk("a0", score=0.42)])]

    update = _run_librarian_with(monkeypatch, by_query)

    assert update["retrieved_chunks"][0]["score"] == 0.42
    assert update["retrieved_chunks"][0]["score_kind"] == "cosine"
    assert update["retrieval_by_query"][0]["chunks"][0]["score_kind"] == "cosine"
