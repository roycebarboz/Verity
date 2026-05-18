"""FastAPI application — POST /triage implements the full five-agent pipeline."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Load .env when running locally
_env = Path(__file__).parent.parent.parent / ".env"
if _env.exists():
    load_dotenv(_env)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from verity.observability import init_llmobs
    init_llmobs()
    yield


app = FastAPI(title="Verity API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class TicketRequest(BaseModel):
    ticket_text: str = Field(..., min_length=1, max_length=4000)
    customer_id: str = Field(..., min_length=1, max_length=100)
    channel: Literal["email", "web", "chat"]


# ---------------------------------------------------------------------------
# Cost estimation (rough mid-2026 pricing; update if OpenAI changes rates)
# ---------------------------------------------------------------------------

_COST_PER_1K: dict[str, float] = {
    "gpt-4.1-nano": 0.0002,
    "gpt-4.1-mini": 0.0008,
    "gpt-5-mini": 0.0015,
}


def _estimate_cost(agent_tokens: dict[str, int], agent_models: dict[str, str]) -> float:
    total = 0.0
    for agent, tokens in agent_tokens.items():
        model = agent_models.get(agent, "gpt-4.1-nano")
        total += tokens * _COST_PER_1K.get(model, 0.001) / 1000
    return round(total, 6)


# ---------------------------------------------------------------------------
# Build API response from final TicketState
# ---------------------------------------------------------------------------

_AGENT_MODELS = {
    "bouncer": "gpt-4.1-nano",
    "librarian": "gpt-4.1-nano",
    "drafter": "gpt-4.1-mini",
    "verifier": "gpt-5-mini",
    "dispatcher": "gpt-4.1-nano",
}

_AGENT_OUTPUTS: dict[str, list[str]] = {
    "bouncer": ["category", "severity", "injection_detected"],
    "librarian": ["retrieved_chunks"],
    "drafter": ["draft_response", "draft_attempts", "draft_history"],
    "verifier": ["verifier_passed", "verifier_failure_reasons", "pii_detected", "citation_coverage"],
    "dispatcher": ["final_action"],
}


def _build_response(state, total_latency_ms: float, cost_usd: float) -> dict[str, Any]:
    from verity.schemas import AgentStepResult, PipelineMetrics, TriageResponse

    def step(name: str) -> AgentStepResult:
        state_dict = state.model_dump()
        output = {k: state_dict.get(k) for k in _AGENT_OUTPUTS[name]}
        return AgentStepResult(
            model=_AGENT_MODELS[name],
            latency_ms=state.agent_timings.get(name, 0.0),
            tokens=state.agent_tokens.get(name, 0),
            output=output,
            attempt=state.draft_attempts if name in ("drafter", "verifier") else 1,
        )

    return TriageResponse(
        ticket_id=state.ticket_id,
        dd_trace_id=state.dd_trace_id,
        pipeline={name: step(name) for name in _AGENT_MODELS},
        final_action=state.final_action or "escalate",
        final_response=state.final_response or "",
        citations=state.retrieved_chunks,
        metrics=PipelineMetrics(
            total_latency_ms=round(total_latency_ms, 1),
            total_tokens=state.total_tokens,
            estimated_cost_usd=cost_usd,
        ),
    ).model_dump()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage")
async def triage(request: TicketRequest) -> dict[str, Any]:
    from verity.audit import write_audit_record
    from verity.graph import pipeline
    from verity.schemas import AgentStepResult, PipelineMetrics, TicketState, TriageResponse

    start = time.monotonic()

    initial = TicketState(
        raw_text=request.ticket_text,
        customer_id=request.customer_id,
        channel=request.channel,
    )

    try:
        result = pipeline.invoke(initial.model_dump())
        final = TicketState.model_validate(result)
    except Exception as exc:
        # PRD §8.4: unhandled exceptions short-circuit to deterministic escalation
        total_latency_ms = (time.monotonic() - start) * 1000
        _stub = AgentStepResult(model="n/a", latency_ms=0, tokens=0, output={})
        return TriageResponse(
            ticket_id=initial.ticket_id,
            pipeline={name: _stub for name in _AGENT_MODELS},
            final_action="escalate",
            final_response=f"[System error — escalated] {exc}",
            metrics=PipelineMetrics(
                total_latency_ms=round(total_latency_ms, 1),
                total_tokens=0,
                estimated_cost_usd=0.0,
            ),
        ).model_dump()

    total_latency_ms = (time.monotonic() - start) * 1000
    cost_usd = _estimate_cost(final.agent_tokens, _AGENT_MODELS)

    write_audit_record(final, total_latency_ms, cost_usd)

    return _build_response(final, total_latency_ms, cost_usd)


# ---------------------------------------------------------------------------
# Serve React static build (Phase 3 — no-op if dist/ doesn't exist yet)
# ---------------------------------------------------------------------------

_frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="static")
