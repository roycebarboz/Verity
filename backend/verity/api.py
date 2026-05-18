"""FastAPI application — stub for Phase 1; fully implemented in Phase 2."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Verity API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage")
async def triage_stub() -> dict[str, str]:
    # TODO Phase 2: validate request body, run pipeline, return TriageResponse
    return {"status": "stub — Phase 2 not yet implemented"}
