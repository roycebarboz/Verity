"""run_verifier failure reasons describe the current draft only, with the LLM call faked."""

import pytest

from verity.agents import verifier
from verity.schemas import RetrievedChunk, TicketState, VerifierOutput


def _state(*, prior_reasons: list[str]) -> TicketState:
    return TicketState(
        raw_text="How do I reset my cluster?",
        customer_id="c1",
        channel="web",
        draft_response="Reset it from the dashboard.",
        draft_attempts=2,
        verifier_failure_reasons=prior_reasons,
        retrieved_chunks=[
            RetrievedChunk(content="Use the dashboard.", source="kb.md", doc_title="KB", chunk_index=0)
        ],
    )


def _fake_llm(monkeypatch: pytest.MonkeyPatch, output: VerifierOutput) -> None:
    monkeypatch.setattr(verifier, "parse_json_with_retry", lambda *a, **k: (output, None))


def test_failure_reasons_are_only_from_the_current_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_llm(monkeypatch, VerifierOutput(
        passed=False, pii_detected=False, citation_coverage=0.2,
        failure_reasons=["Claim not in context"],
    ))

    result = verifier.run_verifier(_state(prior_reasons=["Draft contains a phone number"]))

    assert result["verifier_failure_reasons"] == ["Claim not in context"]


def test_passing_attempt_clears_reasons_from_earlier_attempts(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_llm(monkeypatch, VerifierOutput(passed=True, pii_detected=False, citation_coverage=1.0))

    result = verifier.run_verifier(_state(prior_reasons=["Draft contains a phone number"]))

    assert result["verifier_failure_reasons"] == []
