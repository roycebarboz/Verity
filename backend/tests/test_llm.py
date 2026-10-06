"""LLM wrapper tested with LiteLLM's completion call faked; responses are real ModelResponses
so token usage and per-call cost come from LiteLLM itself."""

import litellm
import pytest
from pydantic import BaseModel

from verity import llm


class Out(BaseModel):
    answer: str


def _resp(content: str, model: str = "gpt-4.1-mini", prompt: int = 1000, completion: int = 1000):
    return litellm.ModelResponse(
        model=model,
        choices=[{"message": {"role": "assistant", "content": content}}],
        usage={
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": prompt + completion,
        },
    )


class FakeCompletion:
    def __init__(self, *responses) -> None:
        self.responses = list(responses)
        self.calls: list[dict] = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses[len(self.calls) - 1]


def _fake(monkeypatch: pytest.MonkeyPatch, *responses) -> FakeCompletion:
    fake = FakeCompletion(*responses)
    monkeypatch.setattr(llm.litellm, "completion", fake)
    return fake


MSGS = [{"role": "user", "content": "hi"}]


def test_returns_parsed_output_and_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _fake(monkeypatch, _resp('{"answer": "ok"}'))

    out, usage = llm.parse_json_with_retry(MSGS, "gpt-4.1-mini", Out)

    assert out == Out(answer="ok")
    assert (usage.prompt_tokens, usage.completion_tokens, usage.total_tokens) == (1000, 1000, 2000)
    assert fake.calls[0]["num_retries"] == llm.LLM_NUM_RETRIES  # transport retries are LiteLLM's


def test_cost_prices_input_and_output_separately(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake(monkeypatch, _resp('{"answer": "ok"}', prompt=1000, completion=0))
    _, input_only = llm.parse_json_with_retry(MSGS, "gpt-4.1-mini", Out)
    _fake(monkeypatch, _resp('{"answer": "ok"}', prompt=0, completion=1000))
    _, output_only = llm.parse_json_with_retry(MSGS, "gpt-4.1-mini", Out)

    expected_in, expected_out = litellm.cost_per_token(
        model="gpt-4.1-mini", prompt_tokens=1000, completion_tokens=1000
    )
    assert input_only.cost_usd == pytest.approx(expected_in)
    assert output_only.cost_usd == pytest.approx(expected_out)
    assert expected_out > expected_in


def test_invalid_output_is_retried_and_cost_sums_over_attempts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _fake(monkeypatch, _resp("not json"), _resp('{"answer": "ok"}'))

    out, usage = llm.parse_json_with_retry(MSGS, "gpt-4.1-mini", Out)

    assert out.answer == "ok"
    assert len(fake.calls) == 2
    assert "Invalid JSON" in fake.calls[1]["messages"][-1]["content"]
    assert usage.total_tokens == 4000
    single = sum(litellm.cost_per_token(model="gpt-4.1-mini", prompt_tokens=1000, completion_tokens=1000))
    assert usage.cost_usd == pytest.approx(2 * single)


def test_persistent_invalid_output_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake(monkeypatch, _resp("x"), _resp("x"), _resp("x"))

    with pytest.raises(ValueError):
        llm.parse_json_with_retry(MSGS, "gpt-4.1-mini", Out)


def test_json_mode_and_max_tokens_for_standard_model(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _fake(monkeypatch, _resp('{"answer": "ok"}'))

    llm.parse_json_with_retry(MSGS, "gpt-4.1-mini", Out, max_tokens=100)

    assert fake.calls[0]["response_format"] == {"type": "json_object"}
    assert fake.calls[0]["max_tokens"] == 100
    assert "max_completion_tokens" not in fake.calls[0]


def test_reasoning_model_gets_completion_token_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _fake(monkeypatch, _resp('{"answer": "ok"}', model="gpt-5-mini"))

    llm.parse_json_with_retry(MSGS, "gpt-5-mini", Out, max_tokens=100)

    assert fake.calls[0]["max_completion_tokens"] == 400
    assert "max_tokens" not in fake.calls[0]


def test_model_without_json_mode_gets_no_response_format(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _fake(monkeypatch, _resp('{"answer": "ok"}'))
    monkeypatch.setattr(llm.litellm, "get_supported_openai_params", lambda model: ["max_tokens"])

    out, _ = llm.parse_json_with_retry(MSGS, "some-model", Out)

    assert out.answer == "ok"
    assert "response_format" not in fake.calls[0]


def test_unpriced_model_costs_zero_instead_of_failing(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake(monkeypatch, _resp('{"answer": "ok"}', model="not-a-real-model"))

    _, usage = llm.parse_json_with_retry(MSGS, "not-a-real-model", Out)

    assert usage.cost_usd == 0.0


def test_model_names_come_from_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    assert llm.agent_model("drafter") == "gpt-4.1-mini"
    monkeypatch.setenv("DRAFTER_MODEL", "claude-haiku-4-5-20251001")
    assert llm.agent_model("drafter") == "claude-haiku-4-5-20251001"
    assert llm.provider_for("claude-haiku-4-5-20251001") == "anthropic"
    assert llm.provider_for("gpt-4.1-mini") == "openai"


def test_default_reasoning_model_capabilities_come_from_litellm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Real capability lookups (no fakes): the verifier's default model is a reasoning model."""
    fake = _fake(monkeypatch, _resp('{"answer": "ok"}', model="gpt-5-mini"))

    llm.parse_json_with_retry(MSGS, llm.agent_model("verifier"), Out, max_tokens=50)

    assert "max_completion_tokens" in fake.calls[0]
    assert ("response_format" in fake.calls[0]) == (
        "response_format" in litellm.get_supported_openai_params("gpt-5-mini")
    )
