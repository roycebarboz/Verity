"""run_verifier tested with the LLM call faked; the regex PII gate runs for real."""

import pytest

from verity.agents import verifier
from verity.schemas import RetrievedChunk, TicketState, VerifierOutput


@pytest.fixture(autouse=True)
def llm_approves(monkeypatch: pytest.MonkeyPatch) -> None:
    ok = VerifierOutput(passed=True, pii_detected=False, citation_coverage=1.0)
    monkeypatch.setattr(
        verifier, "parse_json_with_retry", lambda *a, **k: (ok, None)
    )


def _state(draft: str, *chunk_texts: str) -> TicketState:
    return TicketState(
        raw_text="How do I reach billing?",
        customer_id="c1",
        channel="web",
        draft_response=draft,
        draft_attempts=1,
        retrieved_chunks=[
            RetrievedChunk(content=t, source="kb.md", doc_title="KB", chunk_index=i)
            for i, t in enumerate(chunk_texts)
        ],
    )


def test_email_quoted_from_a_retrieved_chunk_is_not_flagged_as_pii() -> None:
    state = _state(
        "Please write to billing@acme.com for invoice questions.",
        "Contact billing@acme.com for invoice questions.",
    )

    result = verifier.run_verifier(state)

    assert result["verifier_passed"] is True
    assert result["pii_detected"] is False


def test_email_absent_from_every_chunk_is_still_flagged_as_pii() -> None:
    state = _state(
        "Please write to ceo@acme.com for invoice questions.",
        "Contact billing@acme.com for invoice questions.",
    )

    result = verifier.run_verifier(state)

    assert result["verifier_passed"] is False
    assert result["pii_detected"] is True


def test_phone_quoted_from_a_retrieved_chunk_is_not_flagged_as_pii() -> None:
    state = _state(
        "You can call support at 1-800-555-0199 any weekday.",
        "Call support at 1-800-555-0199 any weekday.",
    )

    result = verifier.run_verifier(state)

    assert result["verifier_passed"] is True


def test_ssn_is_flagged_even_when_it_appears_in_a_retrieved_chunk() -> None:
    state = _state(
        "Your record shows 123-45-6789 on file with billing@acme.com.",
        "Record 123-45-6789 belongs to billing@acme.com.",
    )

    result = verifier.run_verifier(state)

    assert result["verifier_passed"] is False
    assert result["pii_detected"] is True
