# Retrieval and provider redesign

Status: ready-for-agent

## Problem Statement

Verity's retrieval treats every ticket the same way. The Librarian always writes one to three Retrieval queries, even for a Simple ticket that needs only one. The Chunks those queries find are then sorted together by raw cosine score and the top five are kept. For a Complex ticket, this lets one Sub-query take every slot, and the other parts of the ticket reach the Drafter with no supporting content. Cosine similarity is also a weak ranking signal on its own, and the pipeline has no way to rescore candidates more precisely.

Ingestion splits FAQ documents on `##` headings with no size limit. Every section is small today, but future content could produce an oversized Chunk without anyone noticing.

Every chat and embedding call is hard-wired to OpenAI: model constants, an OpenAI-specific list of reasoning models, hand-written retry handling, a hard-coded price table, and an `"openai"` provider tag on every Datadog span. Trying another provider means editing code in many places, and the cost estimate charges input and output tokens at the same flat rate.

## Solution

- **Ticket complexity drives retrieval.** The Bouncer classifies Ticket complexity next to category and severity. The Librarian writes exactly one Retrieval query for a Simple ticket and two or three Sub-queries for a Complex ticket.
- **Optional Rerank step.** Each Retrieval query's candidate Chunks can be reranked against that same query using a local cross-encoder (Qwen3-Reranker-0.6B). Reranking is on by default, explicitly switched off in production, and Verity refuses to start if reranking is on but the model is unavailable.
- **Fair merge of results.** Results are combined by taking turns, rank by rank, across Retrieval queries (see ADR 0001). Every part of a Complex ticket is represented in the five final Chunks.
- **FAQ safety cap.** Any FAQ section over 512 tokens is split further, with its heading repeated on each piece.
- **All model calls through LiteLLM.** Every chat and embedding call goes through the LiteLLM SDK in-process, with model names from configuration. LiteLLM handles retries, model capability differences and per-call cost (see ADR 0002). The embedding model is recorded with the index, and Verity refuses to query an index built with a different one.

## User Stories

1. As a support operator, I want simple tickets to be searched with a single focused Retrieval query, so that their answers aren't diluted by irrelevant Chunks.
2. As a support operator, I want tickets that span several knowledge-base topics to be broken into Sub-queries, so that every part of the ticket gets supporting content.
3. As a support operator, I want a ticket that asks one question but needs two topics (e.g. "my cluster won't start since I rotated my API key") to be treated as a Complex ticket, so that both topics are retrieved.
4. As a support operator, I want to see the Bouncer's Ticket complexity in the pipeline view, so that I can understand why the Librarian wrote the number of queries it did.
5. As a support operator, I want Ticket complexity in the audit record, so that I can review routing decisions later.
6. As a support operator, I want the final five Chunks for a Complex ticket to include content for each Sub-query, so that the Drafter can address every part of the ticket.
7. As a support operator, I want each displayed Chunk to show whether its score is a cosine or a Rerank score, so that I don't compare numbers that aren't comparable.
8. As a support operator, I want the final Chunk list ordered by Fair merge position, so that I can see which Chunks the Drafter was given first.
9. As a support operator, I want the per-query view to keep showing each Retrieval query's own candidates, so that I can trace where each final Chunk came from.
10. As a customer, I want replies to multi-part tickets to address every part, so that I don't have to write in again.
11. As a developer running Verity locally, I want reranking on by default, so that I'm working with the best retrieval quality without extra configuration.
12. As a developer running Verity locally, I want reranking to use Apple's GPU backend (MPS) when available and fall back to CPU, so that it works on any machine.
13. As a developer, I want Verity to refuse to start, with a clear message naming the missing piece, when reranking is on but the model or its runtime is missing, so that I never run a "reranked" pipeline that silently isn't.
14. As a developer, I want to turn reranking off with a single setting, so that I can compare against cosine-only retrieval.
15. As a developer, I want the reranker's runtime dependencies to be an optional install group, so that the production image and a minimal dev setup stay small.
16. As an operator deploying to Fargate, I want the production task to explicitly turn reranking off, so that the container never tries to load a model it doesn't contain.
17. As an operator deploying to Fargate, I want a missing reranking-off setting to fail the container at startup rather than on the first ticket, so that the mistake is caught by the deploy.
18. As an evaluator, I want reranking to fetch a deeper set of candidates per Retrieval query (20) than cosine-only retrieval (5), so that Rerank can promote a good Chunk that cosine ranked low.
19. As an evaluator, I want the pipeline to always produce five final Chunks, so that precision@5 and recall@5 stay comparable with my existing baseline.
20. As an evaluator, I want every eval result file to record which reranker mode the server ran with, so that I never compare a reranked run against a non-reranked one by mistake.
21. As an evaluator, I want the Bouncer's Ticket complexity scored against labels derived from each eval ticket's expected chunks (two or more expected source documents means complex), so that I can measure the complexity classifier without hand-labelling.
22. As an evaluator, I want to evaluate each change on its own against my baseline, so that I can tell which change moved which metric.
23. As a content author, I want an oversized FAQ section to be split automatically, so that adding long content can't produce a Chunk too big to embed or cite well.
24. As a content author, I want each piece of a split FAQ section to carry the section heading, so that each piece still makes sense on its own when retrieved.
25. As a content author, I want ingesting today's knowledge base to produce the same Chunks as before, so that the safety cap doesn't change current retrieval.
26. As a developer, I want to change any agent's model through configuration, so that I can try another provider without editing code.
27. As a developer, I want the default models to stay what they are today, so that the LiteLLM migration changes no eval metric on its own.
28. As a developer, I want ingestion and query-time embedding to use the same configured embedding model, so that query vectors always match the index.
29. As a developer, I want the index to record which embedding model built it, and Verity to refuse to query it with a different one, so that a configuration change can't silently corrupt retrieval.
30. As a developer, I want retries for rate limits and server errors handled by LiteLLM, so that I don't maintain provider-specific error handling.
31. As a developer, I want JSON-mode and token-limit differences between models handled by LiteLLM's capability lookup, so that adding a reasoning model from any provider needs no code change.
32. As a developer, I want the Datadog provider tag on each span derived from the configured model, so that traces stay accurate when the provider changes.
33. As a support operator, I want the cost shown for each ticket to be the sum of what each LLM call actually cost, priced separately for input and output tokens, so that the cost figure is accurate.
34. As a developer, I want model names to be defined in exactly one place, so that the API response, the cost estimate and the agents can't disagree about which model ran.
35. As a developer, I want the ingestion chunker importable without API credentials, so that it can be tested in isolation.

## Implementation Decisions

**Ticket complexity (Bouncer)**
- Bouncer output gains `complexity: simple | complex` and the workflow state gains a matching field.
- A Complex ticket is one whose answer draws on more than one knowledge-base topic, even when the customer asked only one thing. This definition goes into a new Bouncer prompt version.
- The regex fast path for prompt injection does not set complexity. Those tickets are escalated before the Librarian runs.
- Complexity is part of the Bouncer's visible pipeline output and audit record.

**Retrieval queries (Librarian)**
- The Librarian reads Ticket complexity. A Simple ticket gets exactly one rewritten Retrieval query; the raw ticket is never used as the query. A Complex ticket gets two or three Sub-queries.
- The query count is enforced by validating output against the complexity, not just requested in the prompt. A mismatch counts as a parse failure and goes through the existing retry-on-invalid-output path.
- This needs a new Librarian prompt version.

**Rerank**
- New reranker module with one interface: rerank a Retrieval query's candidate Chunks against that query and return them with Rerank scores, best first.
- The implementation is Qwen3-Reranker-0.6B loaded from the local models directory, running on MPS when available and otherwise CPU. It's built from the existing prototype script.
- Controlled by a reranker mode setting (`qwen` or `none`), defaulting to `qwen`.
- When the mode is `qwen`, the model and its runtime are loaded and checked at application startup. If either is missing, startup fails with a message naming the missing piece and telling the user to download the model or set the mode to `none`.
- The production task definition sets the mode to `none`.
- torch, transformers and related packages go into an optional dependency group that isn't installed in the production image.

**Retrieval depth and Fair merge**
- Candidate depth per Retrieval query: 20 when reranking, 5 when not.
- Each Retrieval query's candidates are ranked independently: by Rerank score against that query when reranking, by cosine otherwise. They are never reranked against the whole ticket.
- Fair merge produces the five final Chunks:
  - Take each query's #1, then each query's #2, and so on.
  - A Chunk already taken (same source and position) is skipped, and that query's next candidate is used.
  - When queries tie at a rank, take them in query order.
  - For a single Retrieval query, Fair merge is just its top five.
- The existing merge-by-score is replaced. ADR 0001 records why.
- Each retrieved Chunk gains a field saying which kind of score it carries (`cosine` or `rerank`) and keeps its own score. The order of the final list is the ranking; scores are not expected to decrease down the list.
- The per-query retrieval record is kept and reflects each query's ranked candidates.

**FAQ safety cap (ingestion)**
- FAQ documents still split on `##` headings.
- Any section over 512 tokens is split again with the existing fixed-size token splitter and its overlap. The section heading is repeated at the top of each piece.
- Chunk positions stay sequential within the document.
- Other document types are unchanged. Re-ingesting today's knowledge base must produce the same Chunks.
- The chunking logic must be importable without creating any model client.

**LiteLLM (all model calls)**
- Every chat call goes through the LiteLLM SDK in-process. The OpenAI SDK is no longer used directly.
- Every embedding call goes through it too, at both ingestion and query time, sharing one configured embedding model.
- Model names per agent, plus the embedding model, come from configuration. The defaults are today's models.
- LiteLLM's built-in retries replace the hand-written retry helper.
- LiteLLM's capability lookup replaces the hard-coded reasoning-model set, for JSON mode and token-limit parameters.
- Each LLM call's cost is computed by LiteLLM and recorded per agent in workflow state, alongside per-agent tokens. The API sums it to produce the ticket's estimated cost.
- The API's hard-coded per-1K price table and its duplicate per-agent model table are removed. The API reads model names from the same configuration the agents use.
- The Datadog span provider tag is derived from the configured model through LiteLLM's provider resolution.
- Ingestion stores the embedding model name in the index metadata. When Verity opens the index, it compares that with the configured embedding model and refuses to run on a mismatch.
- ADR 0002 records the decision and the rule against adding new provider-specific branches. Using the LiteLLM proxy was considered and rejected.

**API contract**
- The triage response's Bouncer step output includes `complexity`.
- Each Chunk in the citations and per-query results includes its score kind.
- The response reports the reranker mode the server ran with, so the eval script, which calls the API over HTTP, can record it.

**Eval**
- The eval script records the server's reranker mode in its metrics file.
- It derives expected complexity per ticket from the number of distinct source documents in that ticket's expected chunks (two or more means complex), and reports Bouncer complexity accuracy.
- The existing precision@5 and recall@5 definitions are unchanged.

## Testing Decisions

- **What makes a good test here:** check what a module returns from its public entry point given controlled inputs, not internal helpers or call order. Fake only what can't run in CI (LLM calls, the vector store, the embedder, the reranker model), at the highest point that still lets the test control it.
- **Librarian node (main seam):** takes workflow state, returns the state update. LLM output, the vector store, the embedder and the reranker are faked. It covers:
  - Simple versus Complex ticket query counts.
  - A query-count mismatch being rejected.
  - Candidate depth of 20 versus 5 depending on reranker mode.
  - Ordering by Rerank score versus cosine.
  - Fair merge round-robin order, skipping duplicates, and tie-breaking by query order.
  - Always exactly five final Chunks.
  - The score kind on each Chunk.
  - The per-query record.

  Prior art: the existing retrieval tests, which already fake the collection and embedder and drive the Librarian node.
- **Reranker interface:** the new seam that lets Librarian tests run without the model. The real Qwen implementation isn't tested in CI.
- **Ingestion heading chunker:** a pure function from document text to Chunks. It covers:
  - Sections under the cap being unchanged.
  - An oversized section splitting into pieces that each start with the heading.
  - Sequential positions.
  - A guard that today's FAQ documents produce the same Chunks as before.

  This module has no tests today.
- **JSON-mode LLM wrapper:** LiteLLM's completion call is faked. It covers:
  - Parsed output and usage being returned.
  - Retry on invalid output still working.
  - Per-call cost being returned.
  - Correct handling of a model without JSON mode, via the capability lookup.

  Prior art: the drafter retry and verifier tests, which fake one level above this.
- **Bouncer node:** with a faked LLM call, complexity reaches the state update. One thin test.
- **API response:** using the existing faked-pipeline test, check that estimated cost is the sum of per-agent costs, that complexity and score kind appear in the response, and that the reranker mode is reported. Prior art: the existing API triage test.
- **Startup checks:**
  - Reranker mode `qwen` with the model missing fails startup with the expected message.
  - An embedding model that doesn't match the index refuses to run.

  Both are tested directly at the startup function and the index-opening function.
- **Eval script:** expected-complexity derivation and reranker-mode recording, extending the existing eval metrics tests.

## Out of Scope

- Deploying the reranker to production, whether in the container or as a hosted API.
- Changing chunking for runbooks, policies or escalation guides, or splitting on `###` or paragraph boundaries.
- Changing the default models or the embedding model, or re-ingesting with a new one.
- Running the LiteLLM proxy as a separate service.
- Adding a hand-labelled complexity field to the eval set.
- Changes to the Drafter, Verifier or Dispatcher beyond the shared LLM wrapper and cost recording.
- Any frontend redesign beyond showing complexity and score kind.

## Further Notes

- Suggested landing order, with an eval against the baseline after each step:
  1. FAQ safety cap
  2. Ticket complexity and Rerank
  3. Fair merge
  4. LiteLLM

  The LiteLLM step should leave every quality metric unchanged.
- Terms are as defined in the project glossary: Ticket complexity, Simple ticket, Complex ticket, Retrieval query, Sub-query, Chunk, Fair merge, Rerank.
- Related decisions: ADR 0001 (Fair merge instead of sorting by score) and ADR 0002 (all model calls through LiteLLM; the embedding model is tied to the index).
- The Qwen prototype script at the backend root is the reference for the reranker's prompt format and its yes/no scoring. It remains untracked.
