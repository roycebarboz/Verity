"""Retrieval metrics in scripts/run_eval.py, tested through evaluate()."""

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "run_eval", Path(__file__).parents[2] / "scripts" / "run_eval.py"
)
run_eval = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run_eval)


def _ticket(expected_chunks: list[str]) -> dict:
    return {
        "ticket_id": "t1",
        "expected_action": "send",
        "is_injection_attempt": False,
        "is_pii_test": False,
        "expected_chunks": expected_chunks,
    }


def _result(sources: list[str]) -> dict:
    return {
        "final_action": "send",
        "final_response": "ok",
        "citations": [{"source": s} for s in sources],
    }


def test_precision_at_5_is_hits_over_five_slots() -> None:
    score = run_eval.evaluate(
        _ticket(["faq_a.md"]),
        _result(["faq_a.md", "x.md", "y.md", "z.md", "w.md"]),
    )
    assert score["precision_at_5"] == 0.2


def test_recall_at_5_is_fraction_of_expected_chunks_found() -> None:
    score = run_eval.evaluate(
        _ticket(["faq_a.md", "policy_b.md"]),
        _result(["faq_a.md", "x.md", "y.md", "z.md", "w.md"]),
    )
    assert score["recall_at_5"] == 0.5
    assert score["precision_at_5"] == 0.2


def test_precision_counts_every_relevant_chunk_from_an_expected_file() -> None:
    score = run_eval.evaluate(
        _ticket(["faq_slack_pagerduty.md"]),
        _result(["faq_slack_pagerduty.md"] * 4 + ["faq_api_key_rotation.md"]),
    )
    assert score["precision_at_5"] == 0.8
    assert score["recall_at_5"] == 1.0
