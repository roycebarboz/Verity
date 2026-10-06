import pytest


@pytest.fixture(autouse=True)
def reranker_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests never load the real model; the ones about reranking opt in explicitly."""
    monkeypatch.setenv("RERANKER_MODE", "none")
