"""Bouncer agent — classifies ticket and detects prompt injection."""
from __future__ import annotations

import time
from typing import Any

from verity.guardrails import regex_injection_detected
from verity.llm import BOUNCER_MODEL, parse_json_with_retry
from verity.observability import annotate_span, llm_span
from verity.prompts.bouncer_v1 import SYSTEM, VERSION
from verity.schemas import BouncerOutput, TicketState


def run_bouncer(state: TicketState) -> dict[str, Any]:
    print(f"[Bouncer] Classifying ticket {state.ticket_id}")
    start = time.monotonic()

    # Fast regex pre-filter — catches obvious injections without an LLM call
    if regex_injection_detected(state.raw_text):
        ms = (time.monotonic() - start) * 1000
        return {
            "category": "injection_attempt",
            "severity": "high",
            "injection_detected": True,
            "agent_timings": {**state.agent_timings, "bouncer": round(ms, 1)},
            "agent_tokens": {**state.agent_tokens, "bouncer": 0},
        }

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Support ticket:\n\n{state.raw_text}"},
    ]

    with llm_span(
        "bouncer", "openai", BOUNCER_MODEL, state.ticket_id, prompt_version=VERSION
    ) as span:
        output, usage = parse_json_with_retry(
            messages, BOUNCER_MODEL, BouncerOutput, max_tokens=256
        )
        annotate_span(
            span,
            messages,
            output.model_dump_json(),
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )
        # Bouncer runs first — capture the workflow trace ID for audit + frontend
        dd_trace_id = str(span.trace_id) if span is not None else None

    ms = (time.monotonic() - start) * 1000
    tokens = usage.total_tokens if usage else 0

    return {
        "category": output.category,
        "severity": output.severity,
        "injection_detected": output.injection_detected,
        "dd_trace_id": dd_trace_id,
        "agent_timings": {**state.agent_timings, "bouncer": round(ms, 1)},
        "agent_tokens": {**state.agent_tokens, "bouncer": tokens},
        "total_tokens": state.total_tokens + tokens,
    }
