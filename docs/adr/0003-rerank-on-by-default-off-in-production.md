# Rerank is on by default locally and off in production, behind one setting

Rerank improves which Chunks each Retrieval query surfaces, but it needs a local Qwen3-Reranker-0.6B model plus torch and transformers, which don't fit the 0.25 vCPU / 512 MB Fargate task or its image. We make it a single `RERANKER_MODE` setting (`qwen` or `none`), default `qwen`, with the runtime dependencies in an optional `rerank` install group that the production image doesn't install. The production task definition sets `none`.

## Consequences

- With `qwen`, each Retrieval query fetches 20 candidates and reranks them against its own query; with `none` it fetches 5 by cosine. Both feed the Fair merge (ADR 0001), tagged with score kind `rerank` or `cosine`.
- Startup fails fast if the mode is `qwen` and the model or runtime is missing, rather than silently falling back to cosine, so a misconfigured server can't quietly degrade retrieval.
- The triage API response reports the mode, and eval results record it, so metrics from the two modes aren't compared by accident.
