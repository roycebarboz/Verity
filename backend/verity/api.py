"""FastAPI application — POST /triage streams SSE events via LangGraph .astream()."""
from __future__ import annotations

import json
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
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


def _step_from_state(node_name: str, state: Any) -> Any:
    """Build an AgentStepResult from the TicketState after a node completes."""
    from verity.schemas import AgentStepResult
    state_dict = state.model_dump()
    output = {k: state_dict.get(k) for k in _AGENT_OUTPUTS[node_name]}
    return AgentStepResult(
        model=_AGENT_MODELS[node_name],
        latency_ms=state.agent_timings.get(node_name, 0.0),
        tokens=state.agent_tokens.get(node_name, 0),
        output=output,
        attempt=state.draft_attempts if node_name in ("drafter", "verifier") else 1,
    )


def _build_response(state: Any, total_latency_ms: float, cost_usd: float) -> dict[str, Any]:
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
        pipeline={name: step(name) for name in _AGENT_MODELS if name in state.agent_timings},
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
async def triage(request: TicketRequest) -> StreamingResponse:
    from verity.audit import write_audit_record
    from verity.graph import pipeline
    from verity.schemas import TicketState

    initial = TicketState(
        raw_text=request.ticket_text,
        customer_id=request.customer_id,
        channel=request.channel,
    )
    start = time.monotonic()

    async def event_stream():
        from verity.guardrails import detect_pii, find_pii_types
        if detect_pii(request.ticket_text):
            types = find_pii_types(request.ticket_text)
            print(f"[PII] Input contains PII ({', '.join(types)}) for ticket {initial.ticket_id} — audit will redact")

        last_state: TicketState = initial
        accumulated: dict = initial.model_dump()

        try:
            async for chunk in pipeline.astream(initial.model_dump()):
                node_name, partial = next(iter(chunk.items()))
                accumulated.update(partial)
                last_state = TicketState.model_validate(accumulated)
                step = _step_from_state(node_name, last_state)
                payload = {"agent": node_name, "step": step.model_dump()}
                yield f"event: agent_step\ndata: {json.dumps(payload)}\n\n"

        except Exception as exc:
            err_payload = {"message": str(exc), "ticket_id": initial.ticket_id}
            yield f"event: error\ndata: {json.dumps(err_payload)}\n\n"
            last_state.final_action = "escalate"
            last_state.final_response = f"[System error — escalated] {exc}"

        # Always emit pipeline_done so the frontend leaves its loading state,
        # even if audit/response-building fails. The audit module already swallows
        # its own errors, but _build_response could still raise on malformed state.
        total_latency_ms = (time.monotonic() - start) * 1000
        try:
            cost_usd = _estimate_cost(last_state.agent_tokens, _AGENT_MODELS)
            write_audit_record(last_state, total_latency_ms, cost_usd)
            done_payload = _build_response(last_state, total_latency_ms, cost_usd)
        except Exception as exc:
            err_payload = {"message": f"post-stream failure: {exc}", "ticket_id": initial.ticket_id}
            yield f"event: error\ndata: {json.dumps(err_payload)}\n\n"
            done_payload = {
                "ticket_id": initial.ticket_id,
                "dd_trace_id": last_state.dd_trace_id,
                "pipeline": {},
                "final_action": "escalate",
                "final_response": f"[System error — escalated] {exc}",
                "citations": [],
                "metrics": {
                    "total_latency_ms": round(total_latency_ms, 1),
                    "total_tokens": last_state.total_tokens,
                    "estimated_cost_usd": 0.0,
                },
            }

        yield f"event: pipeline_done\ndata: {json.dumps(done_payload)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Serve React static build — check container path first, then local dev path
# ---------------------------------------------------------------------------

_static_candidates = [
    Path(__file__).parent.parent / "static",                    # /app/static in container
    Path(__file__).parent.parent.parent / "frontend" / "dist",  # local dev
]
for _static_path in _static_candidates:
    if (_static_path / "index.html").exists():
        app.mount("/", StaticFiles(directory=str(_static_path), html=True), name="static")
        break
