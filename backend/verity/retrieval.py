"""Chroma vector store query helper."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import chromadb

from verity.llm import EMBED_MODEL, get_client
from verity.schemas import QueryRetrieval, RetrievedChunk

COLLECTION_NAME = "verity_kb"
TOP_K = 5


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
    resp = get_client().embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in resp.data]


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
    """Embed queries, query Chroma, deduplicate by source+chunk, return top_k."""
    return fair_merge(query_kb_by_query(queries, top_k), top_k)


def query_kb_by_query(queries: list[str], top_k: int = TOP_K) -> list[QueryRetrieval]:
    """Return the top_k chunks for each query separately (no merge, no dedupe)."""
    collection = _get_collection()
    results = collection.query(
        query_embeddings=_embed(queries),
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        QueryRetrieval(
            query=query,
            chunks=[
                RetrievedChunk(
                    content=doc,
                    source=meta["source"],
                    doc_title=meta["doc_title"],
                    chunk_index=meta["chunk_index"],
                    score=round(1.0 - float(dist), 4),
                )
                for doc, meta, dist in zip(docs, metas, dists)
            ],
        )
        for query, docs, metas, dists in zip(
            queries, results["documents"], results["metadatas"], results["distances"]
        )
    ]
