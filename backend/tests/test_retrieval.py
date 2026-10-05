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
