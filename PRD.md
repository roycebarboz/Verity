# Verity — Product Requirements Document

**Product Name:** Verity
**Tagline:** The Citation-Grounded Support Triage Copilot
**Version:** 1.0
**Date:** May 17, 2026
**Status:** Draft for Implementation
**Implementation Tool:** Claude Code

---

## How to Use This Document with Claude Code

This PRD is structured to feed directly into Claude Code as a project specification. Each phase in Section 10 maps to one Claude Code session. Functional requirements (FR1–FR8) double as acceptance criteria — Claude Code can self-verify each milestone against them.

**Recommended kickoff prompt for Claude Code (Phase 1):**

> "Read PRD.md. The synthetic data in `data/kb/` and `data/evals/` is already in place (Phase 0 complete). Create the initial project scaffold for Phase 1 only — directory structure, dependency files, LangGraph state machine, and stub agent functions. Do not implement agent logic yet. Match the technology stack in Section 7.3 exactly."

Run each phase in its own session. Don't ask Claude Code to "build the whole thing" — the project is large enough that scoped sessions produce better code and clearer git history. For the React frontend, give Claude Code explicit scope constraints (see Section 7.6).

---

## 1. Executive Summary

Verity is a multi-agent system that automates the triage, drafting, and routing of customer support tickets while guaranteeing that every customer-facing response is grounded in verifiable internal documentation. The system deliberately separates response drafting from response verification across five specialized AI agents, ensuring that no uncited claim, PII leak, or prompt-injection bypass reaches a customer.

Verity is designed for enterprise clients running customer-facing support operations, where the cost of an incorrect AI response — refund commitments, policy misstatements, regulatory leaks — outweighs the cost of automation itself.

---

## 2. Problem Statement

Enterprise support teams face a structural tension between cost, speed, and correctness:

- Manual ticket triage is slow and expensive at scale
- Out-of-the-box LLM chatbots are fast but unreliable — they hallucinate policies, leak PII, and fall for prompt-injection attacks
- Existing AI support tools optimize for response latency, not response verifiability

The core gap: there is no auditable, observable, and verifiable AI support system that a compliance team would approve for production. Verity is built specifically to close this gap.

---

## 3. Goals and Non-Goals

### Goals
- Automate first-response drafting for incoming support tickets
- Guarantee every sent response is grounded in retrieved internal documentation
- Detect and block prompt-injection attempts at the input boundary
- Provide full end-to-end observability of agent decisions and quality scores
- Maintain a durable, queryable audit trail of every ticket decision
- Demonstrate the pipeline in a clear, single-page React UI suitable for interview demo

### Non-Goals (Out of Scope for v1)
- Multi-turn conversational dialogue — single ticket produces single response
- Voice or phone-based support channels
- Customer authentication or account management
- Real-time human-agent collaboration features
- Multi-language support — English only for v1
- Streaming agent output to the UI (post-hoc rendering only — see Section 7.6)

---

## 4. Target Users

| Persona | Primary Concern | What Verity Gives Them |
|---|---|---|
| Support Operations Manager | Reduce time-to-first-response and tier-1 volume | Automated draft + dispatch for routine tickets |
| Compliance / Risk Officer | Audit trail; zero PII leaks; policy adherence | DynamoDB audit log + Datadog trace per ticket |
| ML / Platform Engineer | Debuggability and continuous quality improvement | Full LLM Observability spans + offline eval suite |

---

## 5. Product Overview

Verity ingests a support ticket via HTTP API and produces exactly one of three outcomes:

1. A verified response sent to the customer
2. An escalation packet routed to a human agent
3. A request for additional information from the customer

The system runs as a sequential pipeline of five specialized agents, with one conditional retry loop between the Drafter and Verifier, and hard escalation exits at the Bouncer and Verifier stages. Every step emits a Datadog LLM Observability span and contributes to a single audit record in DynamoDB.

A single-page React UI provides the demo surface — ticket input on the left, pipeline timeline in the center, final response or escalation packet on the right, with cost and trace ID details in the footer.

---

## 6. Functional Requirements

### FR1 — Ticket Intake
The system shall accept tickets via `POST /triage` with a JSON payload containing `ticket_text`, `customer_id`, and `channel`. Input shall be validated for length (max 4,000 characters), content type, and basic structure before any LLM processing.

**Acceptance:** Invalid payloads return HTTP 400 with structured error. Valid payloads return HTTP 200 with a decision object.

### FR2 — Safety Classification (Bouncer)
The system shall classify every incoming ticket for `category`, `severity`, and `injection_risk` before further processing. Tickets flagged as injection attempts shall bypass the pipeline and route directly to human escalation, with the original input quoted but never executed.

**Acceptance:** All tickets in the injection subset of the eval set are correctly flagged and escalated.

### FR3 — Knowledge Retrieval (Librarian)
The system shall rewrite the user's ticket into 1–3 retrieval queries and return the top 5 most relevant document chunks from the Chroma vector index, each tagged with source document name and chunk index.

**Acceptance:** Retrieval precision@5 ≥ 0.7 on the eval set ground truth.

### FR4 — Grounded Drafting (Drafter)
The system shall generate a customer-facing response using only the retrieved chunks as source material. The Drafter agent shall have no access to external information, the internet, or any database.

**Acceptance:** Drafter prompt explicitly forbids external knowledge use. Drafter agent has no tool access configured.

### FR5 — Response Verification (Verifier)
The system shall verify that every claim in the draft maps to a retrieved chunk, contains no PII, and meets tone and policy guidelines. Failed verifications trigger up to 2 retry attempts before forced escalation.

**Acceptance:** Zero PII leaks across the eval set. Verifier rejection reasons are logged on every failure.

### FR6 — Routing Decision (Dispatcher)
The system shall route every verified response to exactly one of three outcomes: `send_to_customer`, `escalate_to_human`, or `request_more_info`.

**Acceptance:** Every pipeline run terminates with exactly one routing decision.

### FR7 — Audit Logging
Every ticket shall produce exactly one DynamoDB record containing the full pipeline decision trail, linked to its Datadog trace ID, with PII redacted from stored input fields.

**Acceptance:** A DynamoDB query by `ticket_id` returns the full audit record with all agent decisions, attempt counts, and the Datadog trace ID.

### FR8 — Observability
Every agent call shall emit a Datadog LLM Observability span with consistent tags. Faithfulness and custom citation coverage evaluations shall attach to every Drafter span.

**Acceptance:** A single ticket produces one workflow trace with five named LLM spans, viewable in the Datadog UI with all required tags present.

---

## 7. System Architecture

### 7.1 Agent Roster

| # | Agent | Role | Model | Cost/Latency Tier |
|---|---|---|---|---|
| 1 | Bouncer | Classify; detect injection | `gpt-4.1-nano` | Lowest |
| 2 | Librarian | Query rewrite; vector search | `gpt-4.1-nano` + `text-embedding-3-small` | Lowest |
| 3 | Drafter | Write grounded reply | `gpt-4.1-mini` | Medium |
| 4 | Verifier | Citation + PII + policy check | `gpt-5-mini` | Reasoning (highest) |
| 5 | Dispatcher | Route to outcome | `gpt-4.1-nano` | Lowest |

**Model selection rationale:** Reasoning capacity is concentrated at the Verifier, where the cost of a missed hallucination is highest. Cheap models handle deterministic classification and routing tasks. The Drafter sits in the middle — fluent enough for customer-facing prose, not paying for reasoning it doesn't need.

### 7.2 Embedding Model Selection

| Model | Dimensions | Cost (per 1M tokens) | Used In v1 |
|---|---|---|---|
| `text-embedding-3-small` | 1536 | $0.02 | **Yes** |
| `text-embedding-3-large` | 3072 | $0.13 | No — production-scale future option |
| `text-embedding-ada-002` | 1536 | $0.10 | No — superseded by 3-small |

**Decision:** Use `text-embedding-3-small` for v1. At demo scale (60 documents, ~300–500 chunks), retrieval quality is bottlenecked by corpus design, not embedding dimensionality. The larger model would double index size and storage cost with no measurable quality gain on this corpus.

**Production-scale upgrade path:** For heterogeneous corpora (Confluence, PDFs, mixed-quality sources), benchmark `text-embedding-3-large` against `3-small` on a held-out retrieval eval set. Upgrade only if precision@5 improvement justifies the 6.5× cost increase.

### 7.3 Communication Pattern

Sequential pipeline with one conditional retry loop between Drafter and Verifier (max 2 retries). Agents communicate exclusively through a typed Pydantic state object (`TicketState`) passed through a LangGraph state machine. No free-form agent-to-agent chat.

### 7.4 Technology Stack

| Layer | Choice | Rationale |
|---|---|---|
| Backend language | Python 3.11 | LangGraph + Datadog SDK ecosystem |
| Orchestration | LangGraph | Native state-machine model fits pipeline + retry loop |
| State validation | Pydantic v2 | Schema enforcement at every agent boundary |
| API layer | FastAPI | Async, OpenAPI docs, ddtrace-instrumented, CORS for React client |
| Frontend | Vite + React + TypeScript | Single-page demo UI; Claude Code generates rapidly |
| Frontend styling | Tailwind CSS | Professional default styling without art direction |
| Vector store | Chroma (embedded) | Zero infrastructure overhead at demo scale; index persisted to S3 |
| LLM provider | OpenAI API | Per available model list |
| Observability | Datadog LLM Obs + APM | LLM Observability quota available; differentiator for FDE role |
| Audit storage | DynamoDB | On-demand pricing, free tier covers demo |
| Compute | AWS ECS Fargate | Smallest container task; no GPU needed |
| Ingress | Application Load Balancer | HTTPS termination, single public endpoint |
| Static hosting | FastAPI static route | React build served from same container — avoids cross-origin complexity |
| Secrets | AWS Secrets Manager | OpenAI key, Datadog API key |
| IaC | Terraform or AWS CDK | One-shot deploy/teardown |

### 7.5 Vector Store Notes

Chroma runs embedded in the FastAPI container. On container start, the app checks for a Chroma index directory on local disk; if absent, it downloads the prebuilt index from S3. Index rebuilds happen offline via an ingestion script and are pushed to S3 manually.

Future migration path: Amazon S3 Vector Buckets (now generally available) for production scale. Out of scope for v1.

### 7.6 Frontend Specification

The frontend is a single-page React application built with Vite and styled with Tailwind. It must demonstrate the pipeline clearly enough for a 20-minute interview audience to follow along without explanation.

**Scope constraints (give to Claude Code verbatim):**
> Build a single-page React app with three panels and a footer. No routing. No authentication. No dark mode toggle. No settings page. No user accounts. The page calls `POST /triage` once per submission and renders the response. Post-hoc rendering only — do not implement streaming or server-sent events.

**Layout:**

| Region | Content |
|---|---|
| Header | Verity logo + tagline; "View Repo" link |
| Left panel | Ticket input textarea, customer ID field, channel selector, "Triage" button, 4–5 preset example tickets as quick-load buttons (including one injection attempt and one PII-containing ticket) |
| Center panel | Pipeline timeline: five collapsed cards (Bouncer, Librarian, Drafter, Verifier, Dispatcher), each expanding to show: model used, latency ms, token count, structured output, attempt number |
| Right panel | Final outcome card: action taken (send/escalate/request_info), final response text, retrieved citation list, verifier reasoning |
| Footer | Total latency (ms), total tokens, and Datadog trace ID with copy-to-clipboard |

**Visual requirements:**
- Each agent card has a status color: gray (pending), blue (running), green (passed), amber (retry), red (failed)
- The Drafter↔Verifier retry loop is visually indicated — if attempt count > 1, show both attempts in the Drafter card
- Citations in the right panel link to the source markdown filename (display only, no navigation)
- Use Tailwind defaults; do not add custom CSS files
- Mobile-responsive is out of scope — desktop only

**Components Claude Code should create:**
- `<TicketInput />` — left panel
- `<PipelineTimeline />` — wraps five `<AgentCard />` instances
- `<AgentCard />` — individual agent step display
- `<OutcomePanel />` — right panel
- `<MetricsFooter />` — bottom metrics + Datadog link
- `<App />` — composition root, holds the single `triageResult` state

### 7.7 Data Schemas

**`TicketState` (LangGraph state object):**
```python
class TicketState(BaseModel):
    ticket_id: str
    raw_text: str
    customer_id: str
    channel: Literal["email", "web", "chat"]

    # Bouncer outputs
    category: Optional[str] = None
    severity: Optional[Literal["low", "medium", "high"]] = None
    injection_detected: Optional[bool] = None

    # Librarian outputs
    retrieved_chunks: list[RetrievedChunk] = []

    # Drafter outputs
    draft_response: Optional[str] = None
    draft_attempts: int = 0

    # Verifier outputs
    verifier_passed: Optional[bool] = None
    verifier_failure_reasons: list[str] = []
    pii_detected: Optional[bool] = None
    citation_coverage: Optional[float] = None

    # Dispatcher outputs
    final_action: Optional[Literal["send", "escalate", "request_info"]] = None
    final_response: Optional[str] = None

    # Metadata
    dd_trace_id: Optional[str] = None
    total_tokens: int = 0
```

**API response schema (returned to React client):**
```typescript
interface TriageResponse {
  ticket_id: string;
  dd_trace_id: string;
  pipeline: {
    bouncer: AgentStepResult;
    librarian: AgentStepResult;
    drafter: AgentStepResult;
    verifier: AgentStepResult;
    dispatcher: AgentStepResult;
  };
  final_action: "send" | "escalate" | "request_info";
  final_response: string;
  metrics: {
    total_latency_ms: number;
    total_tokens: number;
    estimated_cost_usd: number;
  };
}
```

**DynamoDB audit record** — see Section 9.2.

---

## 8. Non-Functional Requirements

### 8.1 Security
- All inputs validated and length-capped at API boundary
- Prompt-injection detection runs before any reasoning agent
- PII redaction applied before any persistent storage (DynamoDB, logs)
- OpenAI and Datadog keys stored in AWS Secrets Manager, never in code or logs
- IAM roles follow least-privilege; the Fargate task can read exactly one secret and write to exactly one DynamoDB table
- No agent has shell access, network access, or arbitrary database access
- Fargate runs in a public subnet with security group restricting ingress to the ALB only (no NAT gateway — cost containment)
- React frontend served as static assets from the same FastAPI container — no separate origin, no exposed secrets, no CORS attack surface in production
- During local development, CORS configured to allow only the Vite dev server origin (`http://localhost:5173`)

### 8.2 Observability Requirements
- Every workflow produces exactly one Datadog trace with five named LLM spans (`bouncer`, `librarian`, `drafter`, `verifier`, `dispatcher`)
- Each span tagged with: `agent_name`, `model`, `ticket_id`, `severity`, `attempt_number`, `prompt_template_version`
- Built-in Datadog evaluations enabled: faithfulness, answer relevancy
- Custom evaluation: citation coverage score, attached to every Drafter span
- Two operational dashboards:
  - **Operations:** request rate, P50/P95 latency, cost per ticket, escalation rate, retry rate
  - **Quality:** faithfulness distribution, citation coverage distribution, injection detection count, Verifier rejection reasons

### 8.3 Performance
- End-to-end P50 latency: ≤ 6 seconds
- End-to-end P95 latency: ≤ 12 seconds
- Cost per ticket: ≤ $0.005 at demo scale (5 agent calls, total ~1.5K tokens)
- Frontend initial page load: ≤ 2 seconds

### 8.4 Reliability
- OpenAI API calls wrapped in exponential backoff (3 attempts, jittered) on 429/5xx
- Schema-parse failures retry the same agent up to 2 times with parse error appended to prompt
- Unhandled exceptions short-circuit to deterministic `escalate_to_human` outcome
- Per-request total token budget: 8,000 tokens hard cap
- Frontend shows graceful error state on API failure (no white-screen crashes)

---

## 9. Data Model

### 9.1 Knowledge Base Corpus
60 markdown documents covering a fictional SaaS company. See `SYNTHETIC_DATA.md` for full generation specification. Document types:
- FAQs (split by `##` heading, no chunking)
- Runbooks (fixed-size chunking, 512 tokens, 75-token overlap)
- Policy documents (fixed-size chunking)
- Escalation guides (fixed-size chunking)

Each chunk stored with metadata: `source`, `doc_title`, `chunk_index`.

### 9.2 DynamoDB Audit Record Schema

```json
{
  "ticket_id": "tkt_20260516_a3f9",
  "timestamp": "2026-05-16T14:32:11Z",
  "dd_trace_id": "7234891023847102938",
  "input": {
    "raw_text_redacted": "...",
    "channel": "email",
    "customer_id_hash": "..."
  },
  "bouncer": { "category": "...", "severity": "...", "injection_detected": false },
  "retriever": { "queries_used": [...], "chunks_retrieved": [...] },
  "drafter": { "attempts": 2, "final_draft": "...", "tokens_used": 412 },
  "verifier": {
    "passed": true,
    "attempts_taken": 2,
    "failure_reasons_on_attempt_1": [...],
    "pii_detected": false,
    "citation_coverage_score": 0.94
  },
  "dispatcher": { "action": "send", "reasoning": "..." },
  "final_response": "...",
  "pipeline_metadata": {
    "total_latency_ms": 4821,
    "total_tokens": 1047,
    "estimated_cost_usd": 0.0018
  }
}
```

### 9.3 Evaluation Dataset
30 hand-curated tickets stored as JSON. See `SYNTHETIC_DATA.md` for full generation specification. Each entry contains:
- `ticket_text` (input)
- `expected_category` and `expected_severity`
- `expected_chunks` (list of source documents that should be retrieved)
- `expected_action` (send / escalate / request_info)
- `is_injection_attempt` (boolean)
- `is_pii_test` (boolean)

---

## 10. Development Plan

### Phase 0 — Synthetic Data (before Day 1)
**Goal:** Generate the KB corpus and eval set required by all subsequent phases.

See `SYNTHETIC_DATA.md` for the complete recipe. Run in a **separate Claude or ChatGPT session**, not your project Claude Code session.

Deliverables:
- 60 markdown files in `data/kb/`
- `data/evals/eval_set.json` with 30 annotated tickets
- All quality checks from `SYNTHETIC_DATA.md` Section 2.5 pass

**Estimated time:** 3–4 hours.

### Phase 1 — Foundation (Day 1, Saturday May 16)
**Goal:** End-to-end backend skeleton with stub agents.

Deliverables:
- Repository scaffold with `backend/`, `frontend/`, `data/`, `infra/`
- Backend: `pyproject.toml`, `Dockerfile`, Pydantic schemas
- LangGraph state machine with 5 stub agent nodes
- CLI entry point: `python -m verity.cli "ticket text"` runs through stub pipeline and prints state at each node
- Chroma ingestion script: reads `data/kb/`, builds index, saves to local directory
- Smoke test: ingestion script runs cleanly on the synthetic KB

**Acceptance:** Running the CLI on any test ticket completes without error and prints the final state object.

### Phase 2 — Agents, Guardrails, and API (Day 2, Sunday May 17)
**Goal:** Production-quality agent implementations, full guardrail stack, and HTTP API ready for frontend.

Deliverables:
- Final system prompts for all five agents, version-tagged
- Injection detection (LLM + regex pre-filter)
- PII regex suite (email, phone, SSN, credit card, common patterns)
- Citation verification (start with naive substring overlap; upgrade only if eval results demand it)
- Schema-validated structured outputs at every agent
- FastAPI HTTP layer with `POST /triage` returning the response schema in Section 7.7
- CORS configured for local React dev server (`http://localhost:5173`)
- Local Datadog LLM Observability integration verified — traces appear in Datadog UI

**Acceptance:** A `curl` POST to localhost returns a valid response matching the API schema; the same request appears as a 5-span trace in Datadog.

### Phase 3 — Frontend, Deployment, and Observability (Day 3, Monday May 18)
**Goal:** Live public endpoint with React UI and full observability.

**Morning — Frontend:**
- Vite + React + TypeScript + Tailwind project scaffold in `frontend/`
- Components from Section 7.6: `<App />`, `<TicketInput />`, `<PipelineTimeline />`, `<AgentCard />`, `<OutcomePanel />`, `<MetricsFooter />`
- 4–5 preset example tickets loaded from `data/evals/eval_set.json`
- Frontend calls local FastAPI endpoint and renders full pipeline result

**Afternoon — Deploy:**
- Frontend built to static assets, served by FastAPI on `/` route
- Container pushed to ECR
- Fargate service + ALB + DynamoDB + S3 + Secrets Manager deployed via IaC
- Datadog dashboards built (Operations + Quality)
- Custom citation coverage evaluation deployed and attaching to traces
- Offline eval suite (`scripts/run_eval.py`) executes 30 tickets against live endpoint and writes results to `eval_results/`
- Results committed to repo

**Acceptance:** Public URL returns the React UI; submitting any preset ticket triggers full pipeline; Datadog shows traces from production endpoint; eval suite passes acceptance thresholds in Section 11.

### Phase 4 — Polish and Delivery (Day 4, Tuesday May 19)
**Goal:** Ship the assignment.

Deliverables:
- Frontend visual polish (spacing, colors, copy edits — no new features)
- Written report (1–2 pages) covering all four assignment sections
- Recorded demo video as backup (record morning of Day 4)
- Two full demo rehearsals against the live endpoint (afternoon)
- Submission email sent before 11:59 PM ET deadline

---

## 11. Success Metrics

| Metric | Target | Measured By |
|---|---|---|
| Pipeline pass rate | ≥ 60% | Offline eval suite |
| Mean citation coverage on sent responses | ≥ 0.85 | Custom Datadog evaluation |
| Verifier rejection rate | ≤ 25% | Datadog Quality dashboard |
| PII leaks in sent responses | 0 | Eval subset (`is_pii_test=true`) |
| Successful prompt injections | 0 | Eval subset (`is_injection_attempt=true`) |
| Retrieval precision@5 | ≥ 0.7 | Offline eval suite |
| Frontend page load (P50) | ≤ 2s | Manual measurement during demo rehearsal |

---

## 12. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AWS networking issues delay deployment | Medium | High | Use public subnet; avoid NAT gateway; keep ngrok-from-laptop fallback ready |
| Datadog evaluation pipeline harder to wire than expected | High | Medium | Follow Datadog quickstart literally; budget half of Day 2 afternoon |
| Citation verifier produces false positives | Medium | Medium | Start with naive substring check; upgrade to embedding similarity only if eval scores demand it |
| Live demo fails on stage | Low | High | Record full walkthrough video Day 4 morning; submit with recording as primary |
| AWS credit burn exceeds $50 | Medium | Medium | Set $30 billing alarm Day 1; tear down stack within 24 hours of presentation |
| Synthetic KB corpus reads as inconsistent | Medium | High | Lock company name, product names, error codes in Phase 0; never deviate |
| Claude Code over-scopes the React frontend | Medium | Medium | Use the explicit scope-constraint prompt in Section 7.6 verbatim |
| Frontend-backend CORS issues in deploy | Medium | Low | FastAPI serves React static build from same container — no cross-origin in production |

---

## 13. Future Versions (Out of Scope for v1)

- Migration to S3 Vector Buckets for production scale
- Migration to `text-embedding-3-large` for heterogeneous corpora (only if A/B benchmarking justifies the cost)
- Streaming agent output to frontend via SSE or WebSocket
- Multi-turn conversation support
- Multi-language ticket handling (Spanish, French priority)
- Active learning from human escalation outcomes
- Per-customer prompt personalization
- Integration with Salesforce/Zendesk/Freshdesk ticket APIs
- Cost-optimized routing (escalate to cheaper models when severity is low)
- Mobile-responsive frontend

---

## 14. Glossary

- **Agent** — A specialized LLM call with a defined role, system prompt, and structured output schema
- **Citation Coverage** — The proportion of claims in a generated response that map to retrieved source chunks
- **Faithfulness** — Datadog-computed score measuring whether response content is supported by retrieved context
- **KB (Knowledge Base)** — The corpus of internal documents from which all customer responses must be grounded
- **PII** — Personally Identifiable Information: emails, phone numbers, account numbers, SSNs, payment details
- **Prompt Injection** — An attack where user input contains instructions designed to override the LLM's system prompt
- **LangGraph** — A library for building stateful, multi-step LLM applications as graphs
- **Span** — A single traced operation in Datadog APM; one agent call = one LLM span
- **Post-hoc rendering** — UI strategy where the full result is rendered after the backend completes, rather than streaming partial state during execution