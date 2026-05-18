"""Drafter agent — writes customer-facing response grounded in retrieved chunks."""
from __future__ import annotations

from typing import Any

from verity.schemas import TicketState


def run_drafter(state: TicketState) -> dict[str, Any]:
    attempt = state.draft_attempts + 1
    print(f"[Drafter] Drafting response — attempt {attempt}")
    # TODO Phase 2: LLM call; no tool access, only retrieved_chunks as context
    return {
        "draft_response": (
            f"[STUB] Thank you for reaching out. Based on our documentation, "
            f"here is the information relevant to your request. (attempt {attempt})"
        ),
        "draft_attempts": attempt,
    }
