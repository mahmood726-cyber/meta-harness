"""V1.0.1 round 14 (Mahmood 2026-09-30, "use codex hard"): condition-as-outcome on the PubMed side of screening
(surfaced, never applied), forest-plot rows bound by a held acronym, and the recorded two-reader codex workloads."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from harness import condition_role as cr

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / "registry" / "model_proposals"


def _review(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def test_plants_fire_on_the_prefix_record_and_not_on_this_harness():
    pre = json.loads((ROOT / "evidence/v101_integrated/round14_plants/prefix_7ade54d0.json").read_text(encoding="utf-8"))
    assert all(v["fired"] for k, v in pre.items() if k.startswith("Q")) and not any(
        v["fired"] for k, v in pre.items() if k.startswith("C"))
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "plants_round14.py"), "--harness-root", str(ROOT)],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    assert not any(v["fired"] for v in json.loads(out).values())


def test_only_a_question_that_enrols_people_without_the_condition_is_condition_as_outcome():
    flagged = []
    for p in sorted((ROOT / "topics").glob("*.json")):
        if not (ROOT / "docs" / "reviews" / p.stem).is_dir():
            continue
        cfg = json.loads(p.read_text(encoding="utf-8"))
        if cr.question_outcome_conditions(cfg.get("question") or "", cfg.get("include") or {}):
            flagged.append(p.stem)
    assert flagged == ["probiotics-aad-prevention"]          # doac-vte, pericarditis, TXA enrol people WITH it


def test_candidates_are_surfaced_and_never_screened_in():
    rev = _review("probiotics-aad-prevention")
    cands = rev["screening"]["condition_as_outcome_candidates"]
    rows = {r["id"].split(" · ")[-1]: r for r in rev["screening"]["records"]}
    assert len(cands) == 8 and all(c["status"].startswith("PROPOSED") for c in cands)
    assert all(rows[c["id"]]["decision"] == "exclude" and rows[c["id"]]["rule_id"] == "X2" for c in cands)


def test_tocilizumab_rows_bind_by_held_acronym_and_the_relation_is_computed():
    o = _review("tocilizumab-covid19-mortality")["comparator"]["overlap_relation"]
    bound = {m["name"]: m["family"] for m in o["theirs"]["members"] if m.get("family")}
    assert bound == {"ARCHITECTS": "NCT04412772", "COVACTA": "NCT04320615", "EMPACTA": "NCT04372186",
                     "RECOVERY": "NCT04381936", "TOCIBRAS": "NCT04403685"}
    assert (o["relation"], o["theirs_k"], o["shared_k"]) == ("SUBSET", 19, 1)


@pytest.mark.parametrize("task,n", [("registry_measure_identity", 176), ("row_binding", 85)])
def test_two_recorded_readers_on_one_frozen_population(task, n):
    pop = json.loads((Q / f"{task}.population.json").read_text(encoding="utf-8"))["items"]
    r1 = json.loads((Q / f"{task}.json").read_text(encoding="utf-8"))["items"]
    r2 = json.loads((Q / f"{task}_reader2.json").read_text(encoding="utf-8"))["items"]
    assert len(pop) == len(r1) == len(r2) == n
    assert all(e.get("status") == "PROPOSED" for e in r1 + r2)


def test_row_binding_verifier_refuses_an_unlisted_family_and_a_none_with_a_quote():
    from reproducible_ai import model_source as ms
    assert ms.verify_row_binding({"family": "NCT0", "quote": "x"}, "x", ["NCT1"])["state"] == "VERIFIER_REFUSED"
    assert ms.verify_row_binding({"family": "NONE", "quote": "x"}, "x", ["NCT1"])["state"] == "VERIFIER_REFUSED"
    ok = ms.verify_row_binding({"family": "NCT1", "quote": "RECOVERY"}, "THEIR ROW RECOVERY", ["NCT1"])
    assert ok["state"] == "VERIFIER_PASS" and ok["agreement"].startswith("RULE_MODEL_DISAGREE")


def test_a_transcript_that_read_outside_the_workdir_or_searched_the_web_is_withheld():
    # round 14: one row_binding call's client printed the head of the user's own project index (following the injected
    # ~/.codex/AGENTS.md) and six searched the web; the committed lane log must carry neither content nor path
    from reproducible_ai import model_call_live as m
    b = chr(92)
    err = ("exec\n\"powershell.exe\" -Command \"Get-Content F:" + b + "Private" + b + "INDEX.md -TotalCount 5\" in <w>\n"
           " succeeded in 5ms:\n# PRIVATE HEADER\nweb search: x\ntokens used\n12\n")
    f = m.transcript_facts(err, b"P")
    assert f["outside_workdir_reads"] == 1 and f["web_search_used"] is True
    assert "PRIVATE" not in f["transcript_redacted"] and "Private" not in json.dumps(f["tool_calls"])
    assert f["transcript_redacted"].startswith("<transcript withheld")


def test_no_committed_record_or_lane_log_line_carries_a_local_path():
    import re
    rx = re.compile(r"[A-Za-z]:\\(?!WINDOWS)|\\Users\\\\")
    for p in (ROOT / "registry" / "model_calls").glob("mc-*.json"):
        assert not rx.search(p.read_text(encoding="utf-8")), p.name
    log = (ROOT / "registry" / "model_calls" / "lane_log" / "evid2.jsonl").read_text(encoding="utf-8")
    assert "INDEX.md" not in log and "rewrite-workbook" not in log


def test_every_live_call_disables_web_search():
    import inspect
    from reproducible_ai import model_call_live as m
    assert "web_search=\"disabled\"" in inspect.getsource(m.codex_runner)
