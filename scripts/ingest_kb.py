#!/usr/bin/env python3
"""Ingest knowledge base markdown files into a persistent Chroma vector store.

Run from the repo root:
    python scripts/ingest_kb.py

Reads data/kb/*.md, chunks by document type, embeds with the configured embedding model (EMBED_MODEL),
and writes the index to data/chroma/.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import chromadb
import tiktoken
from dotenv import load_dotenv

from verity.llm import INDEX_EMBED_MODEL_KEY, embed, embed_model  # noqa: E402

load_dotenv(Path(__file__).parent.parent / ".env")

REPO_ROOT = Path(__file__).parent.parent
KB_DIR = REPO_ROOT / "data" / "kb"
CHROMA_DIR = REPO_ROOT / "data" / "chroma"
COLLECTION_NAME = "verity_kb"
CHUNK_TOKENS = 512
OVERLAP_TOKENS = 75
EMBED_BATCH_SIZE = 100

_enc = tiktoken.get_encoding("cl100k_base")


# ---------------------------------------------------------------------------
# Chunking helpers
# ---------------------------------------------------------------------------

def _count_tokens(text: str) -> int:
    return len(_enc.encode(text))


def _chunk_by_heading(content: str) -> list[tuple[str, int]]:
    """Split FAQ-style docs on ## headings. Returns (text, chunk_index) pairs."""
    chunks: list[tuple[str, int]] = []
    current_heading = ""
    current_lines: list[str] = []

    def _flush(heading: str, lines: list[str]) -> None:
        body = "\n".join(lines).strip()
        if not body:
            return
        text = f"{heading}\n\n{body}" if heading else body
        if _count_tokens(text) <= CHUNK_TOKENS:
            chunks.append((text, len(chunks)))
            return
        # Oversized section: split the body, repeating the heading on each piece.
        for piece, _ in _chunk_fixed(body):
            piece = piece.strip()
            chunks.append((f"{heading}\n\n{piece}" if heading else piece, len(chunks)))

    for line in content.splitlines():
        if line.startswith("## "):
            _flush(current_heading, current_lines)
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    _flush(current_heading, current_lines)
    return chunks


def _chunk_fixed(content: str) -> list[tuple[str, int]]:
    """Fixed-size token chunking with overlap."""
    tokens = _enc.encode(content)
    chunks: list[tuple[str, int]] = []
    start = 0
    idx = 0

    while start < len(tokens):
        end = start + CHUNK_TOKENS
        chunk_text = _enc.decode(tokens[start:end])
        chunks.append((chunk_text, idx))
        idx += 1
        if end >= len(tokens):
            break
        start = end - OVERLAP_TOKENS

    return chunks


def _doc_title(content: str, stem: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return stem.replace("_", " ").title()


def _doc_type(name: str) -> str:
    for prefix in ("faq_", "runbook_", "policy_", "escalation_"):
        if name.startswith(prefix):
            return prefix.rstrip("_")
    return "general"


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def _embed_batch(texts: list[str]) -> list[list[float]]:
    return embed(texts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    md_files = sorted(p for p in KB_DIR.glob("*.md") if p.name != "README.md")
    if not md_files:
        print(f"No markdown files found in {KB_DIR}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(md_files)} KB documents in {KB_DIR}")

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", INDEX_EMBED_MODEL_KEY: embed_model()},
    )

    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict] = []

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        title = _doc_title(content, md_file.stem)
        dtype = _doc_type(md_file.name)

        raw_chunks = _chunk_by_heading(content) if dtype == "faq" else _chunk_fixed(content)

        for text, chunk_idx in raw_chunks:
            ids.append(f"{md_file.stem}__chunk_{chunk_idx}")
            docs.append(text)
            metas.append({
                "source": md_file.name,
                "doc_title": title,
                "doc_type": dtype,
                "chunk_index": chunk_idx,
            })

        print(f"  {md_file.name:45s} {len(raw_chunks):3d} chunks")

    print(f"\nTotal chunks: {len(docs)}")
    print("Generating embeddings (this may take a moment)...")

    all_embeddings: list[list[float]] = []
    for i in range(0, len(docs), EMBED_BATCH_SIZE):
        batch = docs[i : i + EMBED_BATCH_SIZE]
        all_embeddings.extend(_embed_batch(batch))
        done = min(i + EMBED_BATCH_SIZE, len(docs))
        print(f"  Embedded {done}/{len(docs)}")

    print("Writing to Chroma...")
    collection.add(ids=ids, documents=docs, embeddings=all_embeddings, metadatas=metas)

    count = collection.count()
    print(f"\nDone. '{COLLECTION_NAME}' has {count} chunks at {CHROMA_DIR}")


if __name__ == "__main__":
    main()
