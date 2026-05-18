"""Verifier agent — checks citation coverage, PII, and tone in the draft."""
from __future__ import annotations

from typing import Any

from verity.schemas import TicketState


def run_verifier(state: TicketState) -> dict[str, Any]:
    print(f"[Verifier] Checking draft — attempt {state.draft_attempts}")
    # TODO Phase 2: reasoning model checks each claim against retrieved_chunks,
    #              runs PII regex suite, evaluates tone/policy compliance
    return {
        "verifier_passed": True,
        "verifier_failure_reasons": [],
        "pii_detected": False,
        "citation_coverage": 0.90,
    }
