# Verity — Claude Code Project Guide

## Project Overview
Verity is a five-agent support triage system. The full specification is in `PRD.md`.
Read PRD.md before making non-trivial changes.

## What You Should NOT Do
- Do not run Phase 0. Synthetic data in `data/kb/` and `data/evals/` is already complete.
- Do not implement streaming, SSE, or WebSocket support. Post-hoc rendering only.
- Do not add features beyond what PRD.md specifies. No dark mode, auth, routing, settings.
- Do not use any LLM model not listed in PRD Section 7.1 and 7.2.
- Do not commit secrets. OpenAI and Datadog keys come from AWS Secrets Manager.
- Do not introduce new dependencies without explicit approval. The stack is fixed in PRD Section 7.4.

## Repository Layout
backend/        Python 3.11 FastAPI + LangGraph
frontend/       Vite + React + TypeScript + Tailwind
data/kb/        60 markdown KB documents (do not regenerate)
data/evals/     30 eval tickets in eval_set.json (do not regenerate)
infra/          Terraform or AWS CDK
scripts/        One-off scripts (ingestion, eval runner)

## Coding Standards
- Python: type hints required on all public functions. Pydantic v2 for all schemas.
- Python formatter: `ruff format`. Linter: `ruff check`.
- TypeScript: strict mode. No `any` types without a comment explaining why.
- All agent prompts live in `backend/verity/prompts/` as separate `.py` files, version-tagged.
- All structured outputs validated against Pydantic schemas before being added to state.

## Testing
- `pytest` for backend unit tests
- Eval suite runs via `python scripts/run_eval.py` against the deployed endpoint
- Do not write integration tests that hit OpenAI in CI — use mocked responses

## Common Commands
- Run backend locally: `uvicorn verity.api:app --reload`
- Run CLI smoke test: `python -m verity.cli "ticket text"`
- Ingest KB into Chroma: `python scripts/ingest_kb.py`
- Run frontend dev server: `cd frontend && npm run dev`
- Build frontend for prod: `cd frontend && npm run build`
- Run eval suite: `python scripts/run_eval.py`

## Session Workflow
This project is built across multiple Claude Code sessions:
- Session 1: Backend (Phases 1+2 from PRD)
- Session 2: Infrastructure deployment (Phase 3 afternoon)
- Session 3: Frontend (Phase 3 morning, run against live backend)
- Session 4: Polish, eval, demo prep (Phase 4)

Each session should stop at its phase boundary. Do not implement work from a later phase.

## Session 3 — Frontend Visual Verification
When building or polishing the React UI, follow `.claude/rules/screenshot-loop.md`.
Reference design: `mock_design.html` in the repo root.
Minimum 2 screenshot comparison rounds before calling any UI task complete.
Puppeteer (via `npx`, not installed permanently) is approved for screenshot capture during Session 3 only.

## Git Hygiene
- Commit per logical unit of work, not per file
- Commit messages: imperative mood, scoped prefix (e.g. "agents: implement Verifier prompt v1")
- Never commit `.env` files or anything from `data/secrets/`