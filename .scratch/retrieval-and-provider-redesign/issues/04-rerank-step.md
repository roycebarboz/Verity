# 04: Rerank step

**What to build:** Each Retrieval query's candidate Chunks can be reranked against that same query using a local Qwen3-Reranker-0.6B model, before the Fair merge. Reranking is on by default and controlled by a single setting. When it's on, each query fetches a deeper set of candidates so Rerank can bring forward Chunks that cosine ranked low. Verity refuses to start if reranking is on but the model or its runtime is missing. Production turns reranking off. Eval results record which mode the server used.

**Blocked by:** 03 (Fair merge, plus a score type on each Chunk)

**Status:** done

Parent spec: `.scratch/retrieval-and-provider-redesign/spec.md`

- [x] A reranker interface reranks one Retrieval query's candidate Chunks against that query and returns them with Rerank scores, best first. Tests fake this interface.
- [x] The Qwen implementation, built from the existing prototype script, loads the model from the local models directory and runs on MPS when available, otherwise CPU.
- [x] A reranker mode setting accepts `qwen` or `none` and defaults to `qwen`.
- [x] When reranking, each Retrieval query fetches 20 candidates, reranks them against its own query (never the whole ticket), and passes them to the Fair merge with score kind `rerank`.
- [x] When the mode is `none`, each query fetches 5 candidates ranked by cosine, as before.
- [x] With the mode set to `qwen`, application startup fails if the model or its runtime is missing, with a message naming what's missing and telling the user to download the model or set the mode to `none`.
- [x] The reranker's runtime dependencies are an optional install group, not installed in the production image.
- [x] The production task definition sets the reranker mode to `none`.
- [x] The triage API response reports the reranker mode, and the eval script records it in its metrics file.
- [x] Tests cover candidate depth by mode, ranking by Rerank score per query, the startup failure, and the reported and recorded mode.
