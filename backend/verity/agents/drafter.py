"""Drafter agent — writes customer-facing response grounded in retrieved chunks."""
from __future__ import annotations

import time
from typing import Any

from verity.llm import DRAFTER_MODEL, parse_json_with_retry
from verity.observability import annotate_span, llm_span, submit_citation_score
from verity.prompts.drafter_v1 import SYSTEM, VERSION
from verity.schemas import DrafterOutput, TicketState


def _build_context(state: TicketState) -> str:
    if not state.retrieved_chunks:
        return "No context available."
    parts = []
    for i, chunk in enumerate(state.retrieved_chunks, 1):
        parts.append(f"[{i}] Source: {chunk.source}\n{chunk.content}")
    return "\n\n".join(parts)


def run_drafter(state: TicketState) -> dict[str, Any]:
    attempt = state.draft_attempts + 1
    print(f"[Drafter] Drafting response — attempt {attempt}")
    start = time.monotonic()

    context = _build_context(state)
    user_content = (
        f"Customer ticket:\n{state.raw_text}\n\n"
        f"Knowledge base context:\n{context}"
    )

    # On retry: append previous failure reasons to steer the model
    if state.verifier_failure_reasons:
        reasons = "\n".join(f"- {r}" for r in state.verifier_failure_reasons)
        user_content += f"\n\nPrevious draft was rejected. Fix these issues:\n{reasons}"

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_content},
    ]

    with llm_span(
        "drafter",
        "openai",
        DRAFTER_MODEL,
        state.ticket_id,
        attempt=attempt,
        severity=state.severity,
        prompt_version=VERSION,
    ) as span:
        output, usage = parse_json_with_retry(
            messages, DRAFTER_MODEL, DrafterOutput, max_tokens=512
        )
        # Pass the plain response string (not JSON) as output so Datadog's
        # built-in faithfulness + answer relevancy evals can parse it correctly
        annotate_span(
            span,
            messages,
            output.response,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )
        # Custom citation coverage evaluation attached to this span
        from verity.guardrails import compute_citation_coverage
        coverage = compute_citation_coverage(output.response, state.retrieved_chunks)
        submit_citation_score(span, coverage)

    ms = (time.monotonic() - start) * 1000
    tokens = usage.total_tokens if usage else 0

    return {
        "draft_response": output.response,
        "draft_attempts": attempt,
        "draft_history": state.draft_history + [output.response],
        "draft_needs_clarification": output.needs_clarification,
        "agent_timings": {**state.agent_timings, "drafter": round(ms, 1)},
        "agent_tokens": {**state.agent_tokens, "drafter": tokens},
        "total_tokens": state.total_tokens + tokens,
    }
