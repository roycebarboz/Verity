# 02: Ticket complexity drives the query count

**What to build:** The Bouncer classifies each ticket's Ticket complexity as simple or complex. A Complex ticket is one whose answer needs more than one knowledge-base topic, even if the customer asked only one thing. The Librarian then writes exactly one Retrieval query for a Simple ticket and two or three Sub-queries for a Complex ticket. Operators can see the complexity in the pipeline view, the API response and the audit record. The eval reports how accurately the Bouncer classifies complexity.

**Blocked by:** None (can start immediately)

**Status:** done

Parent spec: `.scratch/retrieval-and-provider-redesign/spec.md`

- [x] Bouncer output and the workflow state include `complexity: simple | complex`, defined in a new Bouncer prompt version.
- [x] Tickets that take the regex injection fast path don't need a complexity value and are still escalated before the Librarian runs.
- [x] The Librarian (new prompt version) writes exactly one rewritten Retrieval query for a Simple ticket and two or three Sub-queries for a Complex ticket. The raw ticket text is never used as the query.
- [x] A query count that doesn't match the complexity is treated as invalid output and goes through the existing retry-on-invalid-output path.
- [x] Complexity appears in the Bouncer's step output in the API response, in the pipeline UI and in the audit record.
- [x] The eval script derives each ticket's expected complexity (two or more distinct expected source documents means complex) and reports Bouncer complexity accuracy.
- [x] Librarian-node tests (with the LLM, vector store and embedder faked) cover the query count for Simple and Complex tickets and rejection of a wrong count. A thin Bouncer test checks that complexity reaches the state update.
