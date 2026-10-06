"""Chunking in scripts/ingest_kb.py, imported with no API credentials."""

import importlib.util
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]

os.environ.pop("OPENAI_API_KEY", None)
_SPEC = importlib.util.spec_from_file_location("ingest_kb", ROOT / "scripts" / "ingest_kb.py")
ingest_kb = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ingest_kb)


def _previous_heading_chunks(content: str) -> list[tuple[str, int]]:
    """The pre-cap behaviour: one Chunk per non-empty ## section."""
    chunks: list[tuple[str, int]] = []
    heading, lines = "", []

    def flush() -> None:
        body = "\n".join(lines).strip()
        if body:
            chunks.append((f"{heading}\n\n{body}" if heading else body, len(chunks)))

    for line in content.splitlines():
        if line.startswith("## "):
            flush()
            heading, lines = line[3:].strip(), []
        else:
            lines.append(line)
    flush()
    return chunks


FAQ_FILES = sorted((ROOT / "data" / "kb").glob("faq_*.md"))


@pytest.mark.parametrize("path", FAQ_FILES, ids=lambda p: p.name)
def test_current_faq_documents_chunk_as_before(path: Path) -> None:
    content = path.read_text(encoding="utf-8")

    assert ingest_kb._chunk_by_heading(content) == _previous_heading_chunks(content)


def test_section_under_cap_is_one_chunk() -> None:
    content = "## Q1\n\nshort answer\n\n## Q2\n\nanother"

    assert ingest_kb._chunk_by_heading(content) == [
        ("Q1\n\nshort answer", 0),
        ("Q2\n\nanother", 1),
    ]


def test_oversized_section_is_split_with_heading_on_each_piece() -> None:
    long_body = " ".join(f"word{i}" for i in range(1500))
    content = f"## Small\n\nhello\n\n## Big\n\n{long_body}\n\n## After\n\nbye"

    chunks = ingest_kb._chunk_by_heading(content)

    assert [i for _, i in chunks] == list(range(len(chunks)))
    assert len(chunks) > 3
    assert chunks[0][0] == "Small\n\nhello"
    assert chunks[-1][0] == "After\n\nbye"
    big = [t for t, _ in chunks[1:-1]]
    assert all(t.startswith("Big\n\n") for t in big)
    assert all(ingest_kb._count_tokens(t) <= ingest_kb.CHUNK_TOKENS + 10 for t in big)
