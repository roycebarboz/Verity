"""Chat calls through the LiteLLM SDK (see docs/adr/0002). Chat model names are defined here only."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

import litellm

logger = logging.getLogger(__name__)

# Per-agent model names: today's models by default, overridable via e.g. DRAFTER_MODEL.
_DEFAULT_AGENT_MODELS = {
    "bouncer": "gpt-4.1-nano",
    "librarian": "gpt-4.1-nano",
    "drafter": "gpt-4.1-mini",
    "verifier": "gpt-5-mini",
    "dispatcher": "gpt-4.1-nano",
}
_DEFAULT_EMBED_MODEL = "text-embedding-3-small"
# Chroma collection metadata key recording which embedding model built the index.
INDEX_EMBED_MODEL_KEY = "embedding_model"

LLM_NUM_RETRIES = 3


def agent_model(agent: str) -> str:
    return os.environ.get(f"{agent.upper()}_MODEL") or _DEFAULT_AGENT_MODELS[agent]


def embed_model() -> str:
    """The one embedding model for ingestion and query time (override with EMBED_MODEL)."""
    return os.environ.get("EMBED_MODEL") or _DEFAULT_EMBED_MODEL


def embed(texts: list[str]) -> list[list[float]]:
    resp = litellm.embedding(model=embed_model(), input=texts, num_retries=LLM_NUM_RETRIES)
    return [item["embedding"] for item in resp.data]


class IndexModelMismatch(RuntimeError):
    pass


def check_index_embed_model(index_metadata: dict | None) -> None:
    """Refuse an index built with a different embedding model than the configured one (ADR 0002)."""
    built_with = (index_metadata or {}).get(INDEX_EMBED_MODEL_KEY)
    configured = embed_model()
    if built_with != configured:
        raise IndexModelMismatch(
            f"The index was built with embedding model {built_with!r} but {configured!r} is "
            "configured. Re-ingest the knowledge base (python scripts/ingest_kb.py) or set "
            "EMBED_MODEL back to match."
        )


def agent_names() -> list[str]:
    return list(_DEFAULT_AGENT_MODELS)


def provider_for(model: str) -> str:
    """Provider tag for a model (e.g. "openai"), resolved by LiteLLM."""
    try:
        return litellm.get_llm_provider(model)[1]
    except Exception:
        return "unknown"


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    def add(self, resp: object) -> None:
        usage = getattr(resp, "usage", None)
        self.prompt_tokens += getattr(usage, "prompt_tokens", 0) or 0
        self.completion_tokens += getattr(usage, "completion_tokens", 0) or 0
        self.total_tokens += getattr(usage, "total_tokens", 0) or 0
        try:
            self.cost_usd += litellm.completion_cost(completion_response=resp) or 0.0
        except Exception as exc:  # model missing from LiteLLM's price map — don't fail the call
            logger.warning("LLM cost unavailable, counting as 0: %s", exc)


def parse_json_with_retry(
    messages: list[dict],
    model: str,
    schema_cls: type,
    max_parse_attempts: int = 3,
    max_tokens: int = 512,
) -> tuple[object, LLMUsage]:
    """Call the model, validate JSON against schema_cls, retry on parse failure.

    Transport retries (429/5xx) are LiteLLM's. Returns (parsed_object, usage summed over attempts).
    """
    msgs = list(messages)
    usage = LLMUsage()

    kwargs: dict = {}
    if litellm.supports_reasoning(model):
        # Reasoning models split budget between thinking and visible output — leave room for both.
        kwargs["max_completion_tokens"] = max_tokens * 4
    else:
        kwargs["max_tokens"] = max_tokens
    if "response_format" in (litellm.get_supported_openai_params(model) or []):
        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(max_parse_attempts):
        resp = litellm.completion(
            model=model, messages=msgs, num_retries=LLM_NUM_RETRIES, **kwargs
        )
        usage.add(resp)
        content = resp.choices[0].message.content or ""
        try:
            return schema_cls.model_validate_json(content), usage
        except Exception as exc:
            if attempt == max_parse_attempts - 1:
                raise ValueError(
                    f"Schema parse failed after {max_parse_attempts} attempts: {exc}"
                ) from exc
            msgs = msgs + [
                {"role": "assistant", "content": content},
                {"role": "user", "content": f"Invalid JSON. Error: {exc}. Return valid JSON only."},
            ]

    raise RuntimeError("unreachable")
