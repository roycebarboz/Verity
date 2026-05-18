"""Bouncer agent — classifies ticket and detects prompt injection."""
from __future__ import annotations

from typing import Any

from verity.schemas import TicketState


def run_bouncer(state: TicketState) -> dict[str, Any]:
    print(f"[Bouncer] Classifying ticket {state.ticket_id}")
    # TODO Phase 2: LLM call with structured output + regex pre-filter
    return {
        "category": "billing_inquiry",
        "severity": "medium",
        "injection_detected": False,
    }
