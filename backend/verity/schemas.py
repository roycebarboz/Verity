from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


def _ticket_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"tkt_{ts}_{uuid.uuid4().hex[:8]}"


class RetrievedChunk(BaseModel):
    content: str
    source: str
    doc_title: str
    chunk_index: int
    score: float = 0.0


# --- Structured outputs for each agent (used with OpenAI JSON mode) ---

class BouncerOutput(BaseModel):
    category: str
    severity: Literal["low", "medium", "high"]
    injection_detected: bool
    injection_reasoning: Optional[str] = None


class LibrarianOutput(BaseModel):
    queries: list[str] = Field(..., min_length=1, max_length=3)


class DrafterOutput(BaseModel):
    response: str
    needs_clarification: bool = False


class VerifierOutput(BaseModel):
    passed: bool
    failure_reasons: list[str] = Field(default_factory=list)
    pii_detected: bool
    citation_coverage: float = Field(ge=0.0, le=1.0)


class DispatcherOutput(BaseModel):
    action: Literal["send", "escalate", "request_info"]
    reasoning: str
    final_response: str


# --- LangGraph state ---

class TicketState(BaseModel):
    ticket_id: str = Field(default_factory=_ticket_id)
    raw_text: str
    customer_id: str
    channel: Literal["email", "web", "chat"]

    # Bouncer outputs
    category: Optional[str] = None
    severity: Optional[Literal["low", "medium", "high"]] = None
    injection_detected: Optional[bool] = None

    # Librarian outputs
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)

    # Drafter outputs
    draft_response: Optional[str] = None
    draft_attempts: int = 0
    draft_history: list[str] = Field(default_factory=list)  # one entry per attempt
    draft_needs_clarification: bool = False  # ticket too vague to answer — route request_info

    # Verifier outputs
    verifier_passed: Optional[bool] = None
    verifier_failure_reasons: list[str] = Field(default_factory=list)
    pii_detected: Optional[bool] = None
    citation_coverage: Optional[float] = None

    # Dispatcher outputs
    final_action: Optional[Literal["send", "escalate", "request_info"]] = None
    final_response: Optional[str] = None

    # Metadata
    dd_trace_id: Optional[str] = None
    total_tokens: int = 0

    # Operational metrics — populated by agents, used to build API response
    agent_timings: dict[str, float] = Field(default_factory=dict)
    agent_tokens: dict[str, int] = Field(default_factory=dict)


class AgentStepResult(BaseModel):
    model: str
    latency_ms: float
    tokens: int
    output: dict[str, Any]
    attempt: int = 1


class PipelineMetrics(BaseModel):
    total_latency_ms: float
    total_tokens: int
    estimated_cost_usd: float


class TriageResponse(BaseModel):
    ticket_id: str
    dd_trace_id: Optional[str] = None
    pipeline: dict[str, AgentStepResult]
    final_action: Literal["send", "escalate", "request_info"]
    final_response: str
    citations: list[RetrievedChunk] = Field(default_factory=list)
    metrics: PipelineMetrics
