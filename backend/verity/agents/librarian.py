"""Librarian agent — rewrites query and retrieves KB chunks from Chroma."""
from __future__ import annotations

from typing import Any

from verity.schemas import RetrievedChunk, TicketState


def run_librarian(state: TicketState) -> dict[str, Any]:
    print(f"[Librarian] Retrieving chunks for ticket {state.ticket_id}")
    # TODO Phase 2: LLM query rewrite + Chroma vector search
    stub_chunks = [
        RetrievedChunk(
            content="[STUB] Chunk 1: Policy information about billing.",
            source="policy_billing.md",
            doc_title="Billing Policy",
            chunk_index=0,
            score=0.92,
        ),
        RetrievedChunk(
            content="[STUB] Chunk 2: FAQ answer about subscription changes.",
            source="faq_cancel_subscription.md",
            doc_title="Subscription FAQ",
            chunk_index=0,
            score=0.87,
        ),
        RetrievedChunk(
            content="[STUB] Chunk 3: Runbook for billing escalation.",
            source="escalation_tier2.md",
            doc_title="Tier 2 Escalation Guide",
            chunk_index=2,
            score=0.81,
        ),
    ]
    return {"retrieved_chunks": [c.model_dump() for c in stub_chunks]}
