"""Chroma vector store query helper."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import chromadb

from verity.llm import EMBED_MODEL, get_client
from verity.schemas import RetrievedChunk

COLLECTION_NAME = "verity_kb"
TOP_K = 5


@lru_cache(maxsize=1)
def _get_collection() -> chromadb.Collection:
    chroma_dir = os.environ.get(
        "CHROMA_DIR",
        str(Path(__file__).parent.parent.parent / "data" / "chroma"),
    )
    client = chromadb.PersistentClient(path=chroma_dir)
    return client.get_collection(COLLECTION_NAME)


def _embed(texts: list[str]) -> list[list[float]]:
    resp = get_client().embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in resp.data]


def query_kb(queries: list[str], top_k: int = TOP_K) -> list[RetrievedChunk]:
    """Embed queries, query Chroma, deduplicate by source+chunk, return top_k."""
    collection = _get_collection()
    embeddings = _embed(queries)

    results = collection.query(
        query_embeddings=embeddings,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    seen: set[str] = set()
    chunks: list[RetrievedChunk] = []

    for docs, metas, dists in zip(
        results["documents"], results["metadatas"], results["distances"]
    ):
        for doc, meta, dist in zip(docs, metas, dists):
            uid = f"{meta['source']}_{meta['chunk_index']}"
            if uid in seen:
                continue
            seen.add(uid)
            chunks.append(
                RetrievedChunk(
                    content=doc,
                    source=meta["source"],
                    doc_title=meta["doc_title"],
                    chunk_index=meta["chunk_index"],
                    score=round(1.0 - float(dist), 4),
                )
            )

    chunks.sort(key=lambda c: c.score, reverse=True)
    return chunks[:top_k]
