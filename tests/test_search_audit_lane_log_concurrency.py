"""Plant (search+screen audit, 2026-10-06): concurrent model calls must never split a lane-log line.

registry/model_calls/lane_log/search-screen-audit.jsonl line 675 was a stray 2,405-byte tail of another line (no line it
joins parses): five worker threads wrote multi-kilobyte lines (redacted transcripts) to one file through buffered text
appends, and the writes interleaved. Every line of a lane log must be one whole JSON object, whatever the concurrency."""
from __future__ import annotations

import json
import threading

from reproducible_ai import model_call_live as mcl


def _facts(i):
    return {"tokens_used": i, "tool_calls_n": 0, "tool_calls_rejected_n": 0, "tool_calls": [], "files_read": [],
            "outside_workdir_reads": 0, "transcript_redacted": (f"line {i} " + "x" * 40000)}


def test_concurrent_writers_never_split_a_line(tmp_path):
    path = tmp_path / "lane.jsonl"

    errors = []

    def worker(k):
        try:
            for j in range(25):
                rec = {"record_id": f"mc-{k}-{j}", "state": "RAN_OK", "caller": {"lane": "t"}}
                mcl.log_call(rec, _facts(j), path=path)
        except Exception as e:   # a thread's exception is otherwise swallowed and the test reads an empty file
            errors.append(repr(e))
    ts = [threading.Thread(target=worker, args=(k,)) for k in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert not errors, errors[:3]
    lines = path.read_bytes().split(b"\n")
    body = [x for x in lines if x.strip()]
    assert len(body) == 200
    for x in body:
        json.loads(x)                     # every line is one whole JSON object
