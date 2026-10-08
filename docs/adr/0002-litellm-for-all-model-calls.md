# All model calls go through the LiteLLM SDK; the embedding model is tied to the index

To avoid being locked into OpenAI, every chat and embedding call goes through the LiteLLM SDK in-process, with model names coming from configuration. We also hand LiteLLM the provider-specific details we used to maintain ourselves: retries, model capability differences (such as which models support JSON mode), and cost per call. We chose not to run the LiteLLM proxy, because a second service adds deployment cost and gives nothing at this scale.

## Consequences

- The embedding model is part of the Chroma index, not a runtime setting. Changing it means re-ingesting, and query-time code refuses to run if its configured embedding model doesn't match the one the index was built with.
- Do not add provider-specific branches (model-name sets, per-provider token parameters, hard-coded price tables). Without LiteLLM handling those, the project would be tied to one provider again.
- Cost per call comes from LiteLLM (input and output tokens priced separately) and is recorded per agent; a ticket's estimated cost is the sum. Do not reintroduce a per-1K price table.
