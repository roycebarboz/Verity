# 03: Fair merge, plus a score type on each Chunk

**What to build:** The Chunks found by each Retrieval query are combined by Fair merge instead of being sorted together by score (see ADR 0001): each query's #1, then each query's #2, and so on, until there are five. Every part of a Complex ticket is therefore represented in what the Drafter sees. Each Chunk keeps its own score and says what kind of score it is. The final list is shown in merge order.

**Blocked by:** None (can start immediately)

**Status:** done

Parent spec: `.scratch/retrieval-and-provider-redesign/spec.md`

- [x] The five final Chunks are taken round-robin by rank across Retrieval queries.
- [x] A Chunk that's already been taken (same source and position) is skipped, and that query's next candidate is used.
- [x] When queries tie at a rank, they are taken in query order.
- [x] With a single Retrieval query, the result is that query's top five.
- [x] Exactly five final Chunks are produced whenever enough candidates exist.
- [x] The old merge-by-score behaviour is removed.
- [x] Each Chunk has a score-kind field (`cosine` for now) and keeps its own score; the API response and UI show the final list in merge order along with the score kind.
- [x] The per-query retrieval record is unchanged.
- [x] Librarian-node tests cover round-robin order, skipping duplicates, tie-breaking, the single-query case and the score kind.
