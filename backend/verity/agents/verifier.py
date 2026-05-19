"""Verifier agent — citation, PII, and policy check on the draft response."""
from __future__ import annotations

import time
from typing import Any

from verity.guardrails import compute_citation_coverage, detect_pii
from verity.llm import VERIFIER_MODEL, parse_json_with_retry
from verity.observability import annotate_span, llm_span
from verity.prompts.verifier_v1 import SYSTEM, VERSION
from verity.schemas import TicketState, VerifierOutput


def _build_verifier_input(state: TicketState) -> str:
    chunks_text = "\n\n".join(
        f"[{i}] {c.source}\n{c.content}"
        for i, c in enumerate(state.retrieved_chunks, 1)
    )
    return (
        f"Original ticket:\n{state.raw_text}\n\n"
        f"Draft response to verify:\n{state.draft_response}\n\n"
        f"Retrieved context chunks:\n{chunks_text}"
    )


def run_verifier(state: TicketState) -> dict[str, Any]:
    attempt = state.draft_attempts
    print(f"[Verifier] Checking draft — attempt {attempt}")
    start = time.monotonic()

    # Hard PII gate: only fail if the *draft* leaks PII to the customer
    if detect_pii(state.draft_response or ""):
        ms = (time.monotonic() - start) * 1000
        return {
            "verifier_passed": False,
            "verifier_failure_reasons": ["PII detected in draft by regex scanner"],
            "pii_detected": True,
            "citation_coverage": 0.0,
            "agent_timings": {**state.agent_timings, "verifier": round(ms, 1)},
            "agent_tokens": {**state.agent_tokens, "verifier": 0},
        }

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": _build_verifier_input(state)},
    ]

    with llm_span(
        "verifier",
        "openai",
        VERIFIER_MODEL,
        state.ticket_id,
        attempt=attempt,
        severity=state.severity,
        prompt_version=VERSION,
    ) as span:
        output, usage = parse_json_with_retry(
            messages, VERIFIER_MODEL, VerifierOutput, max_tokens=512
        )
        annotate_span(
            span,
            messages,
            output.model_dump_json(),
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )

    # Programmatic citation coverage overrides LLM estimate for the metric
    prog_coverage = compute_citation_coverage(
        state.draft_response or "", state.retrieved_chunks
    )

    # Use stricter of LLM and programmatic coverage as the stored score
    final_coverage = min(output.citation_coverage, prog_coverage) if prog_coverage > 0 else output.citation_coverage

    ms = (time.monotonic() - start) * 1000
    tokens = usage.total_tokens if usage else 0

    # Accumulate failure reasons across retry attempts
    new_reasons = state.verifier_failure_reasons + output.failure_reasons

    return {
        "verifier_passed": output.passed and not output.pii_detected,
        "verifier_failure_reasons": new_reasons,
        "pii_detected": output.pii_detected,
        "citation_coverage": round(final_coverage, 3),
        "agent_timings": {**state.agent_timings, "verifier": round(ms, 1)},
        "agent_tokens": {**state.agent_tokens, "verifier": tokens},
        "total_tokens": state.total_tokens + tokens,
    }
