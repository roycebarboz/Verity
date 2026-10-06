"""Chroma vector store query helper."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import chromadb
import litellm

from verity.llm import EMBED_MODEL
from verity.reranker import COSINE_DEPTH, RERANK_DEPTH, Reranker, get_reranker
from verity.schemas import QueryRetrieval, RetrievedChunk

COLLECTION_NAME = "verity_kb"
TOP_K = 5  # final Chunks after Fair merge


def _download_from_s3(chroma_dir: str) -> None:
    """Pull prebuilt Chroma index from S3 when running in Fargate (no local disk)."""
    bucket = os.environ.get("S3_CHROMA_BUCKET")
    if not bucket:
        return
    import boto3
    print(f"[retrieval] Downloading Chroma index from s3://{bucket}/chroma/ → {chroma_dir}")
    s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix="chroma/"):
        for obj in page.get("Contents", []):
            key: str = obj["Key"]
            local_path = Path(chroma_dir) / key[len("chroma/"):]
            local_path.parent.mkdir(parents=True, exist_ok=True)
            s3.download_file(bucket, key, str(local_path))
    print("[retrieval] Chroma index download complete")


@lru_cache(maxsize=1)
def _get_collection() -> chromadb.Collection:
    chroma_dir = os.environ.get(
        "CHROMA_DIR",
        str(Path(__file__).parent.parent.parent / "data" / "chroma"),
    )
    if not Path(chroma_dir).exists():
        _download_from_s3(chroma_dir)
    client = chromadb.PersistentClient(path=chroma_dir)
    return client.get_collection(COLLECTION_NAME)


def _embed(texts: list[str]) -> list[list[float]]:
    resp = litellm.embedding(model=EMBED_MODEL, input=texts)
    return [item["embedding"] for item in resp.data]


def fair_merge(by_query: list[QueryRetrieval], top_k: int = TOP_K) -> list[RetrievedChunk]:
    """Fair merge: take each query's #1, then each query's #2, ... until top_k (ADR 0001).

    A Chunk already taken (same source and position) is skipped in favour of that
    query's next candidate. Ties at a rank resolve in query order.
    """
    seen: set[tuple[str, int]] = set()
    merged: list[RetrievedChunk] = []
    cursors = [0] * len(by_query)
    while len(merged) < top_k:
        progressed = False
        for i, retrieval in enumerate(by_query):
            while cursors[i] < len(retrieval.chunks):
                chunk = retrieval.chunks[cursors[i]]
                cursors[i] += 1
                key = (chunk.source, chunk.chunk_index)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(chunk)
                progressed = True
                break
            if len(merged) == top_k:
                return merged
        if not progressed:
            break
    return merged


def query_kb(queries: list[str], top_k: int = TOP_K) -> list[RetrievedChunk]:
    """Embed queries, query Chroma, rank each query's candidates, Fair merge to top_k."""
    return fair_merge(query_kb_by_query(queries), top_k)


def query_kb_by_query(queries: list[str], reranker: Reranker | None = None) -> list[QueryRetrieval]:
    """Return each query's ranked candidates (no merge).

    With a reranker (default: the configured one) each query fetches 20 candidates and
    ranks them by Rerank score against its own query; otherwise 5, ranked by cosine.
    """
    if reranker is None:
        reranker = get_reranker()
    depth = RERANK_DEPTH if reranker else COSINE_DEPTH
    collection = _get_collection()
    results = collection.query(
        query_embeddings=_embed(queries),
        n_results=depth,
        include=["documents", "metadatas", "distances"],
    )
    retrievals = []
    for query, docs, metas, dists in zip(
        queries, results["documents"], results["metadatas"], results["distances"]
    ):
        chunks = [
            RetrievedChunk(
                content=doc,
                source=meta["source"],
                doc_title=meta["doc_title"],
                chunk_index=meta["chunk_index"],
                score=round(1.0 - float(dist), 4),
            )
            for doc, meta, dist in zip(docs, metas, dists)
        ]
        if reranker:
            chunks = reranker.rerank(query, chunks)
        retrievals.append(QueryRetrieval(query=query, chunks=chunks))
    return retrievals
