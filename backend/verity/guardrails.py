"""PII detection/redaction and prompt-injection regex pre-filter."""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# PII patterns
# ---------------------------------------------------------------------------

_EMAIL = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

_PHONE = re.compile(
    r"(?:\+?1[\s\-.]?)?"           # optional US country code
    r"(?:\(?\d{3}\)?[\s\-.]?)"     # area code
    r"\d{3}[\s\-.]"                # exchange
    r"\d{4}"                       # subscriber
)

_SSN = re.compile(r"\b\d{3}[- ]\d{2}[- ]\d{4}\b")

# Simple Luhn-ignored card pattern; catches most 13-16 digit groups
_CREDIT_CARD = re.compile(r"\b(?:\d[ \-]?){13,16}\b")

_AWS_KEY = re.compile(r"AKIA[A-Z0-9]{16}")

_PII_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("email", _EMAIL),
    ("phone", _PHONE),
    ("ssn", _SSN),
    ("credit_card", _CREDIT_CARD),
    ("aws_key", _AWS_KEY),
]

# ---------------------------------------------------------------------------
# Injection pre-filter patterns (fast regex before any LLM call)
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"disregard\s+(all\s+)?",
        r"forget\s+(all\s+)?instructions",
        r"new\s+instructions?\s*:",
        r"you\s+are\s+now\s+",
        r"act\s+as\s+(if\s+you\s+are|a\s+)",
        r"system\s*:\s*you",
        r"<\s*/?\s*system\s*>",
        r"===\s*[A-Z_]+\s*===",              # ===SYSTEM===, ===USER=== delimiter attacks
        r"\[INST\]",
        r"\bDAN\b",
        r"jailbreak",
        r"prompt\s*injection",
        r"override\s+(your\s+)?(instructions|prompt|system)",
    ]
]


def regex_injection_detected(text: str) -> bool:
    return any(p.search(text) for p in _INJECTION_PATTERNS)


def detect_pii(text: str) -> bool:
    return any(pattern.search(text) for _, pattern in _PII_PATTERNS)


def find_pii_types(text: str) -> list[str]:
    return [label for label, pattern in _PII_PATTERNS if pattern.search(text)]


def redact_pii(text: str) -> str:
    result = _EMAIL.sub("[EMAIL REDACTED]", text)
    result = _PHONE.sub("[PHONE REDACTED]", result)
    result = _SSN.sub("[SSN REDACTED]", result)
    result = _CREDIT_CARD.sub("[CARD REDACTED]", result)
    result = _AWS_KEY.sub("[KEY REDACTED]", result)
    return result


def compute_citation_coverage(draft: str, chunks: list) -> float:
    """Naive 3-gram substring overlap: fraction of draft sentences covered by chunks."""
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", draft) if len(s.split()) >= 5]
    if not sentences:
        return 1.0

    all_chunk_text = " ".join(c.content.lower() for c in chunks)

    covered = 0
    for sentence in sentences:
        words = sentence.lower().split()
        for i in range(max(1, len(words) - 2)):
            ngram = " ".join(words[i : i + 3])
            if ngram in all_chunk_text:
                covered += 1
                break

    return covered / len(sentences)
