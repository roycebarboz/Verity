"""Drafter retry input, tested through run_drafter with only the LLM call faked."""


import pytest

from verity.llm import LLMUsage
from verity.schemas import DrafterOutput, TicketState


def _run(monkeypatch: pytest.MonkeyPatch, state: TicketState) -> str:
    """Run the Drafter and return the user message it sent to the LLM."""
    import verity.agents.drafter as drafter

    sent: list[list[dict]] = []

    def fake_llm(messages, model, schema, **kwargs):
        sent.append(messages)
        usage = LLMUsage(1, 1, 2, 0.001)
        return DrafterOutput(response="new draft", needs_clarification=False), usage

    monkeypatch.setattr(drafter, "parse_json_with_retry", fake_llm)
    drafter.run_drafter(state)
    return next(m["content"] for m in sent[0] if m["role"] == "user")


def test_retry_input_contains_previous_draft_and_failure_reasons(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = TicketState(
        ticket_id="t1",
        raw_text="How do I reset my cluster?", customer_id="c1", channel="web",
        draft_response="Call us at 555-0100 to reset.",
        draft_history=["Call us at 555-0100 to reset."],
        draft_attempts=1,
        verifier_failure_reasons=["Draft contains a phone number"],
    )

    user_content = _run(monkeypatch, state)

    assert "Call us at 555-0100 to reset." in user_content
    assert "Draft contains a phone number" in user_content


def test_first_attempt_input_has_no_retry_section(monkeypatch: pytest.MonkeyPatch) -> None:
    state = TicketState(ticket_id="t1", raw_text="How do I reset my cluster?", customer_id="c1", channel="web")

    user_content = _run(monkeypatch, state)

    assert "rejected" not in user_content
