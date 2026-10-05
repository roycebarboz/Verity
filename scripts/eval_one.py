#!/usr/bin/env python3
"""Evaluate a single query against the live triage endpoint.

Usage:
    python scripts/eval_one.py eval_007
    python scripts/eval_one.py "Where is my invoice?" \\
        --expected-action send --expected-chunks billing_faq.md,refund_policy.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import run_eval


def build_ticket(query: str, args: argparse.Namespace) -> dict:
    """Resolve `query` to an eval-set ticket by ID, else build an ad-hoc one."""
    for ticket in json.loads(run_eval.EVAL_SET.read_text()):
        if ticket["ticket_id"] == query:
            return ticket
    return {
        "ticket_id": "adhoc",
        "ticket_text": query,
        "expected_action": args.expected_action,
        "expected_chunks": [c for c in args.expected_chunks.split(",") if c],
        "is_injection_attempt": False,
        "is_pii_test": False,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="eval ticket ID, or ticket text")
    parser.add_argument("--expected-action", default="")
    parser.add_argument("--expected-chunks", default="", help="comma-separated KB filenames")
    args = parser.parse_args(argv)

    ticket = build_ticket(args.query, args)
    result = run_eval.call_triage(ticket)
    if result is None:
        print("No response from triage endpoint", file=sys.stderr)
        return 1
    score = run_eval.evaluate(ticket, result)
    detail = {"ticket": ticket, "result": result, "score": score}

    results_dir = Path(os.environ.get("EVAL_RESULTS_DIR", run_eval.RESULTS_DIR))
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    (results_dir / f"detail_one_{ts}.json").write_text(json.dumps(detail, indent=2, default=str))

    print(json.dumps({"score": score, "retrieval": result.get("retrieval_by_query", [])}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
