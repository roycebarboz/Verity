# Fair merge of sub-query results instead of sorting by score

A Complex ticket's Sub-queries each target a different part of the ticket, but sorting all their Chunks by score let one Sub-query take every slot and left the other parts of the ticket with no supporting content. We take Chunks round-robin by rank across Sub-queries instead (skipping duplicates, breaking ties by Sub-query order), so each part of the ticket gets a fair share of the final set. Scores also aren't comparable across Sub-queries: cosine scores differ in scale from query to query, and the same goes, to a lesser degree, for Rerank scores taken against different queries.

## Consequences

- The final Chunk list is in merge order, not score order; a lower-scored Chunk can appear above a higher-scored one from a different Sub-query. Each Chunk keeps its own score and records whether it is a `cosine` or `rerank` score.
- We considered Reciprocal Rank Fusion and fixed per-query quotas. RRF still lets one Sub-query take most of the slots, and quotas waste slots when one Sub-query finds little.
