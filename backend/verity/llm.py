"""OpenAI client singleton with exponential-backoff retry on 429/5xx."""
from __future__ import annotations

import os
import random
import time
from typing import Callable, TypeVar

from openai import APIStatusError, OpenAI, RateLimitError

# Model names as specified in PRD Section 7.1
BOUNCER_MODEL = "gpt-4.1-nano"
LIBRARIAN_MODEL = "gpt-4.1-nano"
DRAFTER_MODEL = "gpt-4.1-mini"
VERIFIER_MODEL = "gpt-5-mini"
DISPATCHER_MODEL = "gpt-4.1-nano"
EMBED_MODEL = "text-embedding-3-small"

_client: OpenAI | None = None

T = TypeVar("T")


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


def call_with_retry(fn: Callable[[], T], max_attempts: int = 3) -> T:
    """Retry fn on 429 or 5xx with exponential backoff + jitter."""
    for attempt in range(max_attempts):
        try:
            return fn()
        except RateLimitError:
            if attempt == max_attempts - 1:
                raise
        except APIStatusError as e:
            if e.status_code < 500 or attempt == max_attempts - 1:
                raise
        wait = (2**attempt) + random.uniform(0, 1)
        time.sleep(wait)
    raise RuntimeError("unreachable")


# Reasoning models: require max_completion_tokens and don't support json_object mode
_REASONING_MODELS = {"gpt-5-mini", "o1", "o1-mini", "o3", "o3-mini", "o4-mini"}


def parse_json_with_retry(
    messages: list[dict],
    model: str,
    schema_cls: type,
    max_parse_attempts: int = 3,
    max_tokens: int = 512,
) -> tuple[object, object]:
    """Call OpenAI in JSON mode, validate against schema_cls, retry on parse failure.

    Returns (parsed_object, usage).
    """
    client = get_client()
    msgs = list(messages)

    is_reasoning = model in _REASONING_MODELS
    # Reasoning models split budget between internal thinking and visible output —
    # multiply by 4 so there's room for both reasoning tokens and the JSON response.
    effective_tokens = max_tokens * 4 if is_reasoning else max_tokens
    token_kwarg = {"max_completion_tokens": effective_tokens} if is_reasoning else {"max_tokens": max_tokens}
    # Reasoning models don't support response_format=json_object — prompt instructs JSON instead
    format_kwarg = {} if is_reasoning else {"response_format": {"type": "json_object"}}

    for attempt in range(max_parse_attempts):
        resp = call_with_retry(
            lambda: client.chat.completions.create(
                model=model,
                messages=msgs,
                **token_kwarg,
                **format_kwarg,
            )
        )
        content = resp.choices[0].message.content or ""
        try:
            parsed = schema_cls.model_validate_json(content)
            return parsed, resp.usage
        except Exception as exc:
            if attempt == max_parse_attempts - 1:
                raise ValueError(f"Schema parse failed after {max_parse_attempts} attempts: {exc}") from exc
            # Append error and ask model to fix
            msgs = msgs + [
                {"role": "assistant", "content": content},
                {"role": "user", "content": f"Invalid JSON. Error: {exc}. Return valid JSON only."},
            ]

    raise RuntimeError("unreachable")
