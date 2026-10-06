"""Librarian agent — rewrites query and retrieves KB chunks from Chroma."""
from __future__ import annotations

import time
from typing import Any

from verity.llm import agent_model, parse_json_with_retry, provider_for
from verity.observability import annotate_span, llm_span
from verity.prompts.librarian_v2 import SYSTEM, VERSION
from verity.retrieval import fair_merge, query_kb_by_query
from verity.schemas import TicketState, librarian_output_for


def run_librarian(state: TicketState) -> dict[str, Any]:
    print(f"[Librarian] Retrieving chunks for ticket {state.ticket_id}")
    start = time.monotonic()

    messages = [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": (
                f"Ticket complexity: {state.complexity or 'simple'}\n\n"
                f"Support ticket:\n\n{state.raw_text}"
            ),
        },
    ]

    model = agent_model("librarian")
    with llm_span(
        "librarian",
        provider_for(model),
        model,
        state.ticket_id,
        severity=state.severity,
        prompt_version=VERSION,
    ) as span:
        output, usage = parse_json_with_retry(
            messages, model, librarian_output_for(state.complexity), max_tokens=128
        )
        annotate_span(
            span,
            messages,
            output.model_dump_json(),
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )

    print(f"[Librarian] Queries: {output.queries}")
    by_query = query_kb_by_query(output.queries)
    chunks = fair_merge(by_query)
    print(f"[Librarian] Retrieved {len(chunks)} chunks")

    ms = (time.monotonic() - start) * 1000
    tokens = usage.total_tokens if usage else 0
    cost = usage.cost_usd if usage else 0.0

    return {
        "retrieved_chunks": [c.model_dump() for c in chunks],
        "retrieval_by_query": [r.model_dump() for r in by_query],
        "agent_timings": {**state.agent_timings, "librarian": round(ms, 1)},
        "agent_tokens": {**state.agent_tokens, "librarian": tokens},
        "agent_costs": {
            **state.agent_costs,
            "librarian": state.agent_costs.get("librarian", 0.0) + cost,  # summed across retries
        },
        "total_tokens": state.total_tokens + tokens,
    }
