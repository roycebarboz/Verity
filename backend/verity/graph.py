from __future__ import annotations

from langgraph.graph import END, StateGraph

from verity.agents.bouncer import run_bouncer
from verity.agents.dispatcher import run_dispatcher
from verity.agents.drafter import run_drafter
from verity.agents.librarian import run_librarian
from verity.agents.verifier import run_verifier
from verity.schemas import TicketState

# 1 original attempt + up to 2 retries = 3 total drafter calls
MAX_DRAFT_ATTEMPTS = 3
# PRD §8.4: hard cap — escalate instead of retrying if budget exhausted
TOKEN_BUDGET = 8_000


def _route_after_bouncer(state: TicketState) -> str:
    return "escalate" if state.injection_detected else "continue"


def _route_after_verifier(state: TicketState) -> str:
    if state.verifier_passed:
        return "dispatch"
    if state.draft_attempts < MAX_DRAFT_ATTEMPTS and state.total_tokens < TOKEN_BUDGET:
        return "retry"
    # Forced escalation — dispatcher will see verifier_passed=False
    return "dispatch"


def build_graph() -> object:
    builder = StateGraph(TicketState)

    builder.add_node("bouncer", run_bouncer)
    builder.add_node("librarian", run_librarian)
    builder.add_node("drafter", run_drafter)
    builder.add_node("verifier", run_verifier)
    builder.add_node("dispatcher", run_dispatcher)

    builder.set_entry_point("bouncer")

    builder.add_conditional_edges(
        "bouncer",
        _route_after_bouncer,
        {"escalate": "dispatcher", "continue": "librarian"},
    )

    builder.add_edge("librarian", "drafter")
    builder.add_edge("drafter", "verifier")

    builder.add_conditional_edges(
        "verifier",
        _route_after_verifier,
        {"dispatch": "dispatcher", "retry": "drafter"},
    )

    builder.add_edge("dispatcher", END)

    return builder.compile()


# Compiled once at import time; reused per request
pipeline = build_graph()
