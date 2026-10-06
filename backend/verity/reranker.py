"""Rerank: rescore a Retrieval query's candidate Chunks against that same query."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Protocol

from verity.schemas import RetrievedChunk

RerankerMode = Literal["qwen", "none"]
DEFAULT_MODE: RerankerMode = "qwen"
DEFAULT_MODEL_DIR = Path(__file__).parent.parent.parent / "models" / "Qwen3-Reranker-0.6B"

# Candidates fetched per Retrieval query: deeper when Rerank can promote low-ranked Chunks.
RERANK_DEPTH = 20
COSINE_DEPTH = 5


class RerankerUnavailable(RuntimeError):
    """Reranking is switched on but the model or its runtime is missing."""


class Reranker(Protocol):
    def rerank(self, query: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        """Return the chunks scored against query (score_kind "rerank"), best first."""
        ...


def get_reranker_mode() -> RerankerMode:
    mode = os.environ.get("RERANKER_MODE", DEFAULT_MODE).strip().lower()
    if mode not in ("qwen", "none"):
        raise ValueError(f"RERANKER_MODE must be 'qwen' or 'none', got {mode!r}")
    return mode  # type: ignore[return-value]


_PREFIX = (
    "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query "
    'and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n'
    "<|im_start|>user\n"
)
_SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
_INSTRUCTION = "Given a web search query, retrieve relevant passages that answer the query"


class QwenReranker:
    """Qwen3-Reranker-0.6B: scores P("yes") that a Chunk answers the query."""

    def __init__(self, model_dir: Path) -> None:
        if not model_dir.is_dir():
            raise RerankerUnavailable(
                f"Reranker model not found at {model_dir}. Download Qwen3-Reranker-0.6B "
                "there (or set RERANKER_MODEL_DIR), or set RERANKER_MODE=none."
            )
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RerankerUnavailable(
                f"Reranker runtime missing ({exc.name}). Install it with "
                "`pip install -e backend[rerank]`, or set RERANKER_MODE=none."
            ) from exc

        self._torch = torch
        self._device = "mps" if torch.backends.mps.is_available() else "cpu"
        dtype = torch.float16 if self._device == "mps" else torch.float32
        self._tok = AutoTokenizer.from_pretrained(str(model_dir), padding_side="left")
        self._model = (
            AutoModelForCausalLM.from_pretrained(str(model_dir), dtype=dtype)
            .to(self._device)
            .eval()
        )
        self._yes = self._tok.convert_tokens_to_ids("yes")
        self._no = self._tok.convert_tokens_to_ids("no")

    def rerank(self, query: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        if not chunks:
            return []
        torch = self._torch
        head = f"{_PREFIX}<Instruct>: {_INSTRUCTION}\n<Query>: {query}\n<Document>: "
        texts = [f"{head}{c.content}{_SUFFIX}" for c in chunks]
        inputs = self._tok(
            texts, padding=True, truncation=True, max_length=4096, return_tensors="pt"
        ).to(self._device)
        with torch.no_grad():
            logits = self._model(**inputs).logits[:, -1, :]
        scores = torch.softmax(
            torch.stack([logits[:, self._no], logits[:, self._yes]], 1), dim=1
        )[:, 1].tolist()
        ranked = sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)
        return [
            c.model_copy(update={"score": round(s, 4), "score_kind": "rerank"}) for c, s in ranked
        ]


@lru_cache(maxsize=1)
def _load_qwen() -> Reranker:
    model_dir = Path(os.environ.get("RERANKER_MODEL_DIR", DEFAULT_MODEL_DIR))
    return QwenReranker(model_dir)


def get_reranker() -> Reranker | None:
    """The configured reranker, or None when reranking is off."""
    return _load_qwen() if get_reranker_mode() == "qwen" else None


def check_reranker_startup() -> None:
    """Fail fast (RerankerUnavailable) if reranking is on but cannot run."""
    get_reranker()
