"""CLI entry point: python -m verity.cli "<ticket text>" [customer_id] [channel]"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Load .env from repo root before importing anything that needs API keys
_env = Path(__file__).parent.parent.parent / ".env"
if _env.exists():
    from dotenv import load_dotenv
    load_dotenv(_env)


def main(ticket_text: str, customer_id: str = "cli_user", channel: str = "web") -> None:
    from verity.graph import pipeline
    from verity.schemas import TicketState

    initial = TicketState(
        raw_text=ticket_text,
        customer_id=customer_id,
        channel=channel,  # type: ignore[arg-type]
    )

    print(f"\n{'=' * 60}")
    print(f"Ticket ID : {initial.ticket_id}")
    print(f"Input     : {ticket_text[:80]}{'...' if len(ticket_text) > 80 else ''}")
    print(f"{'=' * 60}\n")

    result = pipeline.invoke(initial.model_dump())
    final = TicketState.model_validate(result)

    print(f"\n{'=' * 60}")
    print("Final state:")
    print(json.dumps(final.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python -m verity.cli "<ticket text>" [customer_id] [channel]', file=sys.stderr)
        sys.exit(1)
    args = sys.argv[1:]
    main(args[0], args[1] if len(args) > 1 else "cli_user", args[2] if len(args) > 2 else "web")
