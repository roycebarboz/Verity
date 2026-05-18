"""Dispatcher agent — routes verified response to one of three outcomes."""
from __future__ import annotations

import time
from typing import Any

from verity.llm import DISPATCHER_MODEL, parse_json_with_retry
from verity.observability import annotate_span, llm_span
from verity.prompts.dispatcher_v1 import SYSTEM, VERSION
from verity.schemas import DispatcherOutput, TicketState

# Always escalate without calling LLM for these deterministic cases
_ESCALATE_CATEGORIES = {"compliance", "legal"}


def run_dispatcher(state: TicketState) -> dict[str, Any]:
    print(f"[Dispatcher] Routing ticket {state.ticket_id}")
    start = time.monotonic()

    # Deterministic escalations — no LLM needed
    if state.injection_detected:
        return _fast_escalate(state, start, "Prompt injection detected by Bouncer")

    if state.verifier_passed is False:
        return _fast_escalate(
            state, start, "Response could not be verified after maximum retry attempts"
        )

    if state.category in _ESCALATE_CATEGORIES:
        return _fast_escalate(state, start, f"Category '{state.category}' requires human review")

    user_content = (
        f"Ticket category: {state.category} | Severity: {state.severity}\n\n"
        f"Customer ticket:\n{state.raw_text}\n\n"
        f"Verified draft response:\n{state.draft_response}\n\n"
        f"Verifier passed: {state.verifier_passed} | "
        f"Citation coverage: {state.citation_coverage}"
    )

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_content},
    ]

    with llm_span(
        "dispatcher",
        "openai",
        DISPATCHER_MODEL,
        state.ticket_id,
        severity=state.severity,
        prompt_version=VERSION,
    ) as span:
        output, usage = parse_json_with_retry(
            messages, DISPATCHER_MODEL, DispatcherOutput, max_tokens=512
        )
        annotate_span(
            span,
            messages,
            output.model_dump_json(),
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )

    ms = (time.monotonic() - start) * 1000
    tokens = usage.total_tokens if usage else 0

    return {
        "final_action": output.action,
        "final_response": output.final_response,
        "agent_timings": {**state.agent_timings, "dispatcher": round(ms, 1)},
        "agent_tokens": {**state.agent_tokens, "dispatcher": tokens},
        "total_tokens": state.total_tokens + tokens,
    }


def _fast_escalate(state: TicketState, start: float, reason: str) -> dict[str, Any]:
    ms = (time.monotonic() - start) * 1000
    return {
        "final_action": "escalate",
        "final_response": f"[Escalated] {reason}.",
        "agent_timings": {**state.agent_timings, "dispatcher": round(ms, 1)},
        "agent_tokens": {**state.agent_tokens, "dispatcher": 0},
    }
