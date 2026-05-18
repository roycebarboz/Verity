"""Dispatcher agent — routes verified response to one of three outcomes."""
from __future__ import annotations

from typing import Any

from verity.schemas import TicketState


def run_dispatcher(state: TicketState) -> dict[str, Any]:
    print(f"[Dispatcher] Routing ticket {state.ticket_id}")
    # TODO Phase 2: LLM call to decide send/escalate/request_info based on state

    if state.injection_detected:
        return {
            "final_action": "escalate",
            "final_response": "[STUB] Ticket escalated: possible prompt injection detected.",
        }

    if state.verifier_passed is False:
        return {
            "final_action": "escalate",
            "final_response": (
                "[STUB] Ticket escalated: response could not be verified "
                "after maximum retry attempts."
            ),
        }

    return {
        "final_action": "send",
        "final_response": state.draft_response or "[STUB] No draft available.",
    }
