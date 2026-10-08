# 01: FAQ safety cap

**What to build:** When the knowledge base is re-ingested, any FAQ section longer than 512 tokens is split into smaller Chunks, each starting with the section's heading. Today's knowledge base, where every FAQ section is well under the cap, produces exactly the same Chunks as before. First, make the ingestion chunking logic importable without creating any model client, so it can be tested on its own.

**Blocked by:** None (can start immediately)

**Status:** done

Parent spec: `.scratch/retrieval-and-provider-redesign/spec.md`

- [x] Ingestion chunking can be imported and called with no API credentials present.
- [x] FAQ documents still split on `##` headings; sections at or under 512 tokens are unchanged.
- [x] A section over 512 tokens is split using the existing fixed-size token splitter and overlap, and every piece starts with the section heading.
- [x] Chunk positions stay sequential within each document.
- [x] Runbook, policy and escalation document chunking is unchanged.
- [x] A regression test confirms that chunking today's FAQ documents produces the same Chunks as the previous behaviour.
- [x] Tests cover an oversized section (heading on each piece, sequential positions) and an under-cap section.
