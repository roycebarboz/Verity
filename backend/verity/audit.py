"""DynamoDB audit trail — best-effort, never raises on failure."""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from verity.schemas import TicketState

TABLE_NAME = os.getenv("DYNAMODB_TABLE", "verity-audit")
_table: Any = None


def _get_table() -> Any:
    global _table
    if _table is None:
        import boto3

        region = os.getenv("AWS_REGION", "us-east-1")
        _table = boto3.resource("dynamodb", region_name=region).Table(TABLE_NAME)
    return _table


def write_audit_record(
    state: TicketState,
    total_latency_ms: float,
    estimated_cost_usd: float,
) -> None:
    try:
        _get_table().put_item(Item=_build_record(state, total_latency_ms, estimated_cost_usd))
    except Exception as exc:
        print(f"[audit] DynamoDB write skipped: {exc}")


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def _f(value: float | None) -> Any:
    """DynamoDB requires Decimal for floats."""
    from decimal import Decimal
    return Decimal(str(value)) if value is not None else None


def _build_record(
    state: TicketState,
    total_latency_ms: float,
    estimated_cost_usd: float,
) -> dict[str, Any]:
    from verity.guardrails import redact_pii

    return {
        "ticket_id": state.ticket_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dd_trace_id": state.dd_trace_id or "",
        "input": {
            "raw_text_redacted": redact_pii(state.raw_text),
            "channel": state.channel,
            "customer_id_hash": _hash(state.customer_id),
        },
        "bouncer": {
            "category": state.category,
            "severity": state.severity,
            "injection_detected": state.injection_detected,
        },
        "retriever": {
            "chunks_retrieved": [c.source for c in state.retrieved_chunks],
        },
        "drafter": {
            "attempts": state.draft_attempts,
            "tokens_used": state.agent_tokens.get("drafter", 0),
        },
        "verifier": {
            "passed": state.verifier_passed,
            "attempts_taken": state.draft_attempts,
            "failure_reasons": state.verifier_failure_reasons,
            "pii_detected": state.pii_detected,
            "citation_coverage_score": _f(state.citation_coverage),
        },
        "dispatcher": {
            "action": state.final_action,
        },
        "final_response": state.final_response or "",
        "pipeline_metadata": {
            "total_latency_ms": _f(round(total_latency_ms, 1)),
            "total_tokens": state.total_tokens,
            "estimated_cost_usd": _f(round(estimated_cost_usd, 6)),
        },
    }
