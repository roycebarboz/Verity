"""Datadog LLM Observability helpers.

Wraps ddtrace so that all agents can emit consistent LLM spans without
importing ddtrace directly. Falls back silently when DD_LLMOBS_ENABLED is unset.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Generator

_enabled = False


def init_llmobs() -> None:
    global _enabled
    if not os.getenv("DD_LLMOBS_ENABLED"):
        return
    try:
        from ddtrace.llmobs import LLMObs

        LLMObs.enable(
            ml_app=os.getenv("DD_LLMOBS_ML_APP", "verity"),
            api_key=os.getenv("DD_API_KEY"),
            site=os.getenv("DD_SITE", "datadoghq.com"),
            agentless_enabled=True,
            # Opt in to Datadog built-in evaluations (faithfulness, answer relevancy)
            # These are scored server-side against the annotated input/output data.
            # Must also be enabled per-app in the Datadog LLM Observability UI.
        )
        _enabled = True
        print("[observability] Datadog LLM Observability enabled")
    except Exception as exc:
        print(f"[observability] Datadog init failed (continuing without): {exc}")


@contextmanager
def llm_span(
    name: str,
    model_provider: str,
    model_name: str,
    ticket_id: str,
    attempt: int = 1,
    severity: str | None = None,
    prompt_version: str = "v1",
) -> Generator[Any, None, None]:
    """Context manager that yields a Datadog LLM span (or None if disabled)."""
    if not _enabled:
        yield None
        return

    from ddtrace.llmobs import LLMObs

    with LLMObs.llm(
        model_provider=model_provider,
        model_name=model_name,
        name=name,
        session_id=ticket_id,
    ) as span:
        if span is not None:
            tags: dict[str, str] = {
                "agent_name": name,
                "model": model_name,
                "ticket_id": ticket_id,
                "attempt_number": str(attempt),
                "prompt_template_version": prompt_version,
            }
            if severity:
                tags["severity"] = severity
            span.set_tags(tags)
        yield span


def annotate_span(
    span: Any,
    input_messages: list[dict],
    output_content: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> None:
    if not _enabled or span is None:
        return
    from ddtrace.llmobs import LLMObs

    LLMObs.annotate(
        span=span,
        input_data=input_messages,
        output_data=[{"role": "assistant", "content": output_content}],
        metrics={
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
    )


def submit_citation_score(span: Any, score: float) -> None:
    if not _enabled or span is None:
        return
    from ddtrace.llmobs import LLMObs

    LLMObs.submit_evaluation(
        span={"span_id": str(span.span_id), "trace_id": str(span.trace_id)},
        label="citation_coverage",
        metric_type="score",
        value=score,
    )
