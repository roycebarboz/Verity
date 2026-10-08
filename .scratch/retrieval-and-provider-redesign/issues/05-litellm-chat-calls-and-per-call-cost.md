# 05: LiteLLM for chat calls, with cost per call

**What to build:** Every agent's LLM call goes through the LiteLLM SDK in-process, with model names coming from configuration (see ADR 0002). Today's models stay as the defaults, so eval quality metrics shouldn't change. The cost shown for each ticket becomes the sum of each call's actual cost, with input and output tokens priced separately.

**Blocked by:** None (can start immediately)

**Status:** done

Parent spec: `.scratch/retrieval-and-provider-redesign/spec.md`

- [x] All chat calls go through LiteLLM; the OpenAI SDK is no longer called directly for chat.
- [x] Each agent's model name comes from configuration, defaulting to today's models, and is defined in one place only.
- [x] LiteLLM's built-in retries replace the hand-written retry helper.
- [x] LiteLLM's capability lookup replaces the hard-coded reasoning-model set, for both JSON mode and the token-limit parameter.
- [x] The Datadog span provider tag is derived from the configured model, not hard-coded as `"openai"`.
- [x] Each LLM call's cost is recorded per agent in workflow state, alongside per-agent tokens.
- [x] The API adds up those costs for the ticket's estimated cost; the hard-coded per-1K price table and the duplicate per-agent model table are removed.
- [x] LiteLLM is pinned to an exact version.
- [x] LLM-wrapper tests (with LiteLLM's completion call faked) cover parsed output and usage, retry on invalid output, per-call cost, and a model that doesn't support JSON mode.
- [x] The API test checks that the estimated cost is the sum of per-agent costs.
- [x] An eval run shows unchanged quality metrics compared with the baseline.
