# 06: LiteLLM embeddings, with the embedding model tied to the index

**What to build:** Ingestion and query-time retrieval both embed through LiteLLM using a single configured embedding model. The index records which embedding model built it, and Verity refuses to query an index built with a different model, so a configuration change can't silently corrupt retrieval (see ADR 0002).

**Blocked by:** 01 (FAQ safety cap), 05 (LiteLLM for chat calls, with cost per call)

**Status:** ready-for-agent

Parent spec: `.scratch/retrieval-and-provider-redesign/spec.md`

- [ ] Ingestion and query-time embedding both go through LiteLLM; the OpenAI SDK is no longer used anywhere.
- [ ] Both use the same configured embedding model, defaulting to today's model.
- [ ] Ingestion stores the embedding model name in the index metadata.
- [ ] Opening the index compares the stored model with the configured one and refuses to run on a mismatch, with a message telling the user to re-ingest.
- [ ] Re-ingesting today's knowledge base with the default model leaves retrieval results unchanged.
- [ ] Tests cover the mismatch refusal and the matching-model path.
