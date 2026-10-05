"""scripts/eval_one.py tested as a CLI against a fake /triage SSE server."""

import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "scripts" / "eval_one.py"

PIPELINE_DONE = {
    "final_action": "send",
    "final_response": "Use the reset link.",
    "citations": [{"source": "faq_password_reset.md"}, {"source": "x.md"}],
    "metrics": {"total_tokens": 10, "total_latency_ms": 5},
    "retrieval_by_query": [
        {
            "query": f"query {q}",
            "chunks": [
                {"source": f"doc_{q}_{i}.md", "chunk_index": i, "score": 0.9 - i / 10}
                for i in range(5)
            ],
        }
        for q in range(3)
    ],
}


@pytest.fixture()
def triage_url():
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            self.rfile.read(int(self.headers["content-length"]))
            body = f"event: pipeline_done\ndata: {json.dumps(PIPELINE_DONE)}\n\n".encode()
            self.send_response(200)
            self.send_header("content-type", "text/event-stream")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args) -> None:
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}/triage"
    server.shutdown()


def run_cli(args: list[str], url: str, results_dir: Path) -> subprocess.CompletedProcess:
    env = {"TRIAGE_URL": url, "EVAL_RESULTS_DIR": str(results_dir), "PATH": ""}
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env
    )


def test_scores_a_ticket_by_id(triage_url: str, tmp_path: Path) -> None:
    proc = run_cli(["eval_001"], triage_url, tmp_path)

    assert proc.returncode == 0, proc.stderr
    score = json.loads(proc.stdout)["score"]
    assert score["action_correct"] is True
    assert score["recall_at_5"] == 1.0
    assert score["precision_at_5"] == 0.2


def test_unreachable_endpoint_exits_nonzero_with_message(tmp_path: Path) -> None:
    proc = run_cli(["eval_001"], "http://127.0.0.1:1/triage", tmp_path)

    assert proc.returncode == 1
    assert "no response" in proc.stderr.lower()
    assert "Traceback" not in proc.stderr


def test_scores_ad_hoc_text_with_expectations(triage_url: str, tmp_path: Path) -> None:
    proc = run_cli(
        [
            "Where is my invoice?",
            "--expected-action", "escalate",
            "--expected-chunks", "faq_password_reset.md,billing.md",
        ],
        triage_url,
        tmp_path,
    )

    assert proc.returncode == 0, proc.stderr
    score = json.loads(proc.stdout)["score"]
    assert score["action_correct"] is False  # fake server returns "send"
    assert score["recall_at_5"] == 0.5


def test_writes_detail_file_with_score_and_raw_result(triage_url: str, tmp_path: Path) -> None:
    proc = run_cli(["eval_001"], triage_url, tmp_path)

    assert proc.returncode == 0, proc.stderr
    files = list(tmp_path.glob("detail_one_*.json"))
    assert len(files) == 1
    detail = json.loads(files[0].read_text())
    assert detail["score"]["recall_at_5"] == 1.0
    assert detail["result"]["final_response"] == "Use the reset link."
    assert [c["source"] for c in detail["result"]["citations"]][0] == "faq_password_reset.md"


def test_prints_five_chunks_for_each_of_three_queries(triage_url: str, tmp_path: Path) -> None:
    proc = run_cli(["eval_001"], triage_url, tmp_path)

    assert proc.returncode == 0, proc.stderr
    retrieval = json.loads(proc.stdout)["retrieval"]
    assert [r["query"] for r in retrieval] == ["query 0", "query 1", "query 2"]
    sources = [c["source"] for r in retrieval for c in r["chunks"]]
    assert len(sources) == 15
    assert sources[0] == "doc_0_0.md"
    assert sources[-1] == "doc_2_4.md"
