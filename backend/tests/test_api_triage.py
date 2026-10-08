"""POST /triage tested through the FastAPI app with a fake LangGraph pipeline."""

import json

import pytest
from fastapi.testclient import TestClient


def _chunk(q: int, i: int) -> dict:
    return {
        "content": "c", "source": f"doc_{q}_{i}.md", "doc_title": "T",
        "chunk_index": i, "score": 0.5,
    }


class FakePipeline:
    async def astream(self, initial: dict):
        yield {
            "librarian": {
                "retrieved_chunks": [_chunk(0, 0)],
                "retrieval_by_query": [
                    {"query": f"q{q}", "chunks": [_chunk(q, i) for i in range(5)]}
                    for q in range(3)
                ],
                "agent_timings": {"librarian": 1.0},
            }
        }
        yield {"dispatcher": {"final_action": "send", "final_response": "hi",
                              "agent_timings": {"librarian": 1.0, "dispatcher": 1.0}}}


def _pipeline_done(body: str) -> dict:
    event = None
    for line in body.splitlines():
        if line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:") and event == "pipeline_done":
            return json.loads(line[5:])
    raise AssertionError("no pipeline_done event")


def test_pipeline_done_includes_five_chunks_per_query(monkeypatch: pytest.MonkeyPatch) -> None:
    import verity.graph
    from verity.api import app

    monkeypatch.setattr(verity.graph, "pipeline", FakePipeline())

    resp = TestClient(app).post(
        "/triage", json={"ticket_text": "help", "customer_id": "c", "channel": "web"}
    )

    done = _pipeline_done(resp.text)
    by_query = done["retrieval_by_query"]
    assert [q["query"] for q in by_query] == ["q0", "q1", "q2"]
    assert sum(len(q["chunks"]) for q in by_query) == 15
    assert len(done["citations"]) == 1  # citations stay the merged top-5


def test_estimated_cost_is_sum_of_per_agent_costs(monkeypatch: pytest.MonkeyPatch) -> None:
    import verity.graph
    from verity.api import app

    class CostPipeline:
        async def astream(self, initial: dict):
            yield {
                "bouncer": {
                    "agent_timings": {"bouncer": 1.0},
                    "agent_costs": {"bouncer": 0.000123},
                }
            }
            yield {
                "drafter": {
                    "agent_timings": {"bouncer": 1.0, "drafter": 1.0},
                    "agent_costs": {"bouncer": 0.000123, "drafter": 0.000456},
                }
            }

    monkeypatch.setattr(verity.graph, "pipeline", CostPipeline())

    resp = TestClient(app).post(
        "/triage", json={"ticket_text": "help", "customer_id": "c", "channel": "web"}
    )

    assert _pipeline_done(resp.text)["metrics"]["estimated_cost_usd"] == pytest.approx(0.000579)
