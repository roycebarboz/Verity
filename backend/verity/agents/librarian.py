"""Librarian agent — rewrites query and retrieves KB chunks from Chroma."""
from __future__ import annotations

import time
from typing import Any

from verity.llm import LIBRARIAN_MODEL, parse_json_with_retry
from verity.observability import annotate_span, llm_span
from verity.prompts.librarian_v1 import SYSTEM, VERSION
from verity.retrieval import query_kb
from verity.schemas import LibrarianOutput, TicketState


def run_librarian(state: TicketState) -> dict[str, Any]:
    print(f"[Librarian] Retrieving chunks for ticket {state.ticket_id}")
    start = time.monotonic()

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Support ticket:\n\n{state.raw_text}"},
    ]

    with llm_span(
        "librarian",
        "openai",
        LIBRARIAN_MODEL,
        state.ticket_id,
        severity=state.severity,
        prompt_version=VERSION,
    ) as span:
        output, usage = parse_json_with_retry(
            messages, LIBRARIAN_MODEL, LibrarianOutput, max_tokens=128
        )
        annotate_span(
            span,
            messages,
            output.model_dump_json(),
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )

    print(f"[Librarian] Queries: {output.queries}")
    chunks = query_kb(output.queries)
    print(f"[Librarian] Retrieved {len(chunks)} chunks")

    ms = (time.monotonic() - start) * 1000
    tokens = usage.total_tokens if usage else 0

    return {
        "retrieved_chunks": [c.model_dump() for c in chunks],
        "agent_timings": {**state.agent_timings, "librarian": round(ms, 1)},
        "agent_tokens": {**state.agent_tokens, "librarian": tokens},
        "total_tokens": state.total_tokens + tokens,
    }
