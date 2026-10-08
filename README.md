# Verity — The Citation-Grounded Support Triage Copilot

Verity is a **five-agent customer-support triage system**. Each incoming ticket is
classified, retrieved against a knowledge base, drafted, verified, and routed by a
chain of specialized AI agents — and **every customer-facing response is grounded in
retrieved internal documentation**, PII-screened, injection-checked, and fully traced
in Datadog LLM Observability.

Built as the Junior FDE pre-screening assignment — *Design and Implementation of a
Multi-Agent System* (Wipro, May 2026).

---

## 📋 Judges — Start Here

| Deliverable | Link |
|---|---|
| **Written Report** (1–2 page required writeup) | [`report.pdf`](report.pdf) |
| **Sample Prompts** (all 5 agent system prompts) | [`doc/PROMPTS.md`](doc/PROMPTS.md) |
| **Demo Video** | [YouTube — Project Walkthrough](https://youtu.be/nL_729YpNCs) |
| **Live Demo** | *Runs locally — watch the video or [run locally](#-running-locally)* |
| **Architecture Diagram** | [Agent pipeline](#agent-architecture) |

---

## Demo

The AWS deployment (ECS Fargate + ALB) has been decommissioned. The AWS code (Terraform, DynamoDB audit, S3 index sync) lives on the [`legacy_branch`](../../tree/legacy_branch) branch; `main` is local-only.

- **Watch the demo:** [YouTube — Project Walkthrough](https://youtu.be/nL_729YpNCs)
- **Run locally:** see [Running Locally](#-running-locally) below

**API endpoints** (when running locally on `http://localhost:8000`):

| Path | Method | Purpose |
|---|---|---|
| `/` | GET | React single-page UI |
| `/health` | GET | Liveness check |
| `/triage` | POST | Submit a ticket; streams the pipeline back as SSE events |

Submit a ticket from the command line (local):

```bash
curl -N -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"ticket_text":"How do I reset my password?","customer_id":"cust_001","channel":"email"}'
```

---

## Agent Architecture

Verity runs as a **sequential LangGraph pipeline** of five specialized agents, with
one conditional retry loop between the Drafter and Verifier, and hard escalation
exits at the Bouncer and Verifier. Agents never chat freely — they communicate only
through a typed Pydantic `TicketState` object passed node to node.

![Verity agent system diagram](agent_system_diagram.png)

| # | Agent | Responsibility | Model |
|---|---|---|---|
| 1 | **Bouncer** | Validate input; classify category, severity & Ticket complexity (simple/complex); detect prompt injection | `gpt-4.1-nano` |
| 2 | **Librarian** | Rewrite ticket into 1 query (simple) or 2–3 Sub-queries (complex); vector search; optional Rerank; Fair merge into the top-5 chunks | `gpt-4.1-nano` + `text-embedding-3-small` (+ optional local Qwen3-Reranker-0.6B) |
| 3 | **Drafter** | Write a customer reply **using only retrieved chunks** — no external knowledge, no tools | `gpt-4.1-mini` |
| 4 | **Verifier** | Check every claim maps to a chunk; PII scan; tone & policy check | `gpt-5-mini` (reasoning tier) |
| 5 | **Dispatcher** | Route to exactly one outcome: `send_to_customer`, `escalate_to_human`, or `request_more_info` | `gpt-4.1-nano` |

Models shown are the defaults. Every chat and embedding call goes through the
[LiteLLM](https://github.com/BerriAI/litellm) SDK, so each agent's model is set with
`BOUNCER_MODEL`, `LIBRARIAN_MODEL`, `DRAFTER_MODEL`, `VERIFIER_MODEL` and
`DISPATCHER_MODEL`, and the embedding model with `EMBED_MODEL` (see
[ADR 0002](docs/adr/0002-litellm-for-all-model-calls.md)).

**Retrieval:** each Retrieval query fetches candidates from Chroma. When the reranker is
on (`RERANKER_MODE=qwen`, the default), each query fetches 20 candidates and reranks them
against its own query; otherwise it fetches the top 5 by cosine. The per-query results
are combined by a **Fair merge** — each query's #1, then each query's #2, and so on until
five Chunks are chosen — so every part of a complex ticket is represented (see
[ADR 0001](docs/adr/0001-fair-merge-over-score-sort.md)). Each Chunk carries its own score
and score kind (`cosine` or `rerank`), and the final list is shown in merge order. The
embedding model is tied to the Chroma index: changing `EMBED_MODEL` requires re-running
`scripts/ingest_kb.py`, and Verity refuses to query an index built with a different model.

**Flow control:** the Bouncer routes confirmed injection attempts straight to human
escalation. A failed verification triggers up to **2 retries** of the Drafter; once
3 attempts are exhausted the Verifier forces escalation. Reasoning capacity is
concentrated at the Verifier — the one place where a missed hallucination is most
expensive.

---

## Legacy AWS Deployment

The original ECS Fargate + ALB deployment (Terraform IaC, DynamoDB audit trail, S3-hosted Chroma
index, Secrets Manager) is preserved on the [`legacy_branch`](../../tree/legacy_branch) branch,
including its topology diagram and deployment runbook. `main` runs locally only.

---

## How This Project Answers the Assignment

The assignment ([`Project Assignment Multi-Agent System.md`](Project%20Assignment%20Multi-Agent%20System.md))
requires the submission to address four areas. Here is where each is covered.

### 1. Multi-Agent Architecture
Five specialized agents — Bouncer, Librarian, Drafter, Verifier, Dispatcher — with
clear responsibilities and boundaries (table above). Agents operate **sequentially**
through a LangGraph state machine with one conditional retry loop; communication is
via a typed shared state object, not free-form chat. See [`PRD.md`](PRD.md) §7 and
[`agent_system_diagram.png`](agent_system_diagram.png).

### 2. Security, Safety, and Guardrails
- **Input validation** — 4,000-character cap and structural checks before any LLM call.
- **Prompt-injection protection** — regex pre-filter + LLM classifier in the Bouncer;
  confirmed attacks bypass the pipeline, are quoted but **never executed**.
- **Output filtering** — the Verifier rejects any uncited claim, PII leak, or
  off-policy/off-tone content before a response can be sent.
- **Data handling** — PII is redacted before anything is written to logs;
  API keys live in `.env` (git-ignored), never in code or logs.
- **Least privilege** — no agent has shell, network, or
  arbitrary DB access. Guardrail code: [`backend/verity/guardrails.py`](backend/verity/guardrails.py).

### 3. Implementation Approach
- **Stack** — Python 3.11, LangGraph (orchestration), Pydantic v2 (state validation),
  FastAPI (API), Vite + React + TypeScript + Tailwind (UI), Chroma (vector store),
  LiteLLM SDK (provider-agnostic; OpenAI by default) with an optional local Qwen3-Reranker, Datadog (observability).
- **Error handling** — LiteLLM's built-in retries on provider 429/5xx, schema-parse retries (including a wrong query count for the ticket's complexity),
  and a deterministic `escalate_to_human` fallback on any unhandled exception.
- **Testing** — `pytest` unit tests plus a 30-ticket offline eval suite
  ([`scripts/run_eval.py`](scripts/run_eval.py)) covering retrieval precision,
  injection detection, and PII leakage.

### 4. Use of AI / LLMs and Collaboration
LLMs are used for classification, query rewriting, grounded drafting, and reasoning-
based verification — each agent on the cheapest model that fits its job (configurable per agent), with the
reasoning-tier model reserved for the Verifier. Agents "collaborate" through the
Drafter↔Verifier critique loop: the Verifier returns structured failure reasons that
the Drafter consumes on retry. The autonomy/control trade-off is resolved toward
**control** — verification is mandatory, retries are bounded, and every path
terminates in a single routing decision. All five agent system prompts
and their user-message templates are documented in [`doc/PROMPTS.md`](doc/PROMPTS.md).

---

## Repository Guide — Key Documents

| Document | What it contains |
|---|---|
| [`PRD.md`](PRD.md) | Full product spec — architecture, schemas, NFRs, phase-by-phase build & deploy plan |
| [`Project Assignment Multi-Agent System.md`](Project%20Assignment%20Multi-Agent%20System.md) | The original assignment brief |
| [`report.pdf`](report.pdf) | The 1–2 page written report (required deliverable) |
| [`doc/PROMPTS.md`](doc/PROMPTS.md) | All five agent system prompts + user-message templates (*Sample Prompts* deliverable) |
| [`doc/SYNTHETIC_DATA.md`](doc/SYNTHETIC_DATA.md) | How the KB corpus and eval set were generated |
| [`GLOSSARY.md`](GLOSSARY.md) | Domain vocabulary (Ticket complexity, Fair merge, Rerank, …) |
| [`docs/adr/`](docs/adr/) | Architecture decision records (Fair merge, LiteLLM for all model calls) |
| [`agent_system_diagram.png`](agent_system_diagram.png) | Agent pipeline / LangGraph state graph |
| [`data/evals/`](data/evals/) | 30-ticket evaluation set + its README |
| [`data/kb/`](data/kb/) | 60 synthetic knowledge-base markdown documents |

```
backend/    Python 3.11 — FastAPI + LangGraph (agents, prompts, guardrails, API)
frontend/   Vite + React + TypeScript + Tailwind single-page UI
data/kb/    60 KB markdown documents
data/evals/ 30 annotated eval tickets
scripts/    KB ingestion, eval runner, stress test
models/     Local model weights (Qwen3-Reranker-0.6B; not needed when RERANKER_MODE=none)
```

---

## 🖥️ Running Locally

Prerequisites: Python 3.11, Node 18+, an API key for your model provider (OpenAI by default).

```bash
# 1. Configure environment
cp .env.example .env          # then fill in OPENAI_API_KEY (Datadog keys optional)

# 2. Backend
cd backend
pip install -e ".[dev,rerank]"          # drop ",rerank" if you set RERANKER_MODE=none
python ../scripts/ingest_kb.py          # build the Chroma index from data/kb/
                                        # (re-run whenever EMBED_MODEL changes)
uvicorn verity.api:app --reload         # serves on http://localhost:8000

# 3. Frontend (separate terminal)
cd frontend
npm install
npm run dev                             # serves on http://localhost:5173
```

Quick checks without the UI:

```bash
# CLI smoke test — runs one ticket through the full pipeline
python -m verity.cli "How do I reset my password?"

# Offline eval suite (30 tickets)
python scripts/run_eval.py
```

> **Reranker:** `RERANKER_MODE` defaults to `qwen`, which needs the `rerank` install group
> and the Qwen3-Reranker-0.6B weights in `models/Qwen3-Reranker-0.6B` (or the path in
> `RERANKER_MODEL_DIR`). The server refuses to start if either is missing. Set
> `RERANKER_MODE=none` to skip reranking; production does this. The triage response and the
> eval metrics file record which mode was used.

> The Datadog keys in `.env` are optional for local development — the pipeline runs
> without them; only the Observability spans are skipped.

---

See [`PRD.md`](PRD.md) for the complete specification.
