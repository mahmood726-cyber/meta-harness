"""Plant (6 Oct, forest lane): every agy (Gemini) call crashed AFTER the model answered -- log_call requires
'outside_workdir_reads' (added with the record writer's redaction, 07cbbc6c) and only the codex path supplied it.
The agy facts must carry every key log_call reads; agy reads no files (its tool calls are all denied), so 0."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_call_live as mcl  # noqa: E402


def test_agy_log_facts_satisfy_the_lane_log(tmp_path):
    facts = mcl.agy_log_facts({"usage": {"total_tokens": 7}}, [{"display_name": "cat x", "action": "deny"}], "log")
    assert facts["outside_workdir_reads"] == 0 and facts["files_read"] == []
    rec = {"record_id": "mc-x", "state": "RAN_OK", "caller": {"lane": "t"}}
    mcl.log_call(rec, facts, path=tmp_path / "lane.jsonl")
    assert '"outside_workdir_reads": 0' in (tmp_path / "lane.jsonl").read_text(encoding="utf-8")
