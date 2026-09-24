"""The committed typed-arm records are REPRODUCIBLE from the repo alone: rebuild every extraction packet from the held
bytes (make_packets.py), drop in the committed extractor artefact (evidence/typed_arms/extractions/<row>/out.json),
re-run the gate, and every record must come back with the same state, the same arm ids, the same F4B slots and the
same ownership relations. A packet whose rebuilt document bytes differ from the ones the extractor was shown is a
refusal (G1 'bytes changed'), so held-source drift cannot pass silently.

Skipped, with the reason printed, when the checkout does not hold the cited cache files (a sparse clone)."""
import importlib.util, json, os, shutil, subprocess, sys
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TA = os.path.join(ROOT, "evidence", "typed_arms")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(TA, "scripts", name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_every_committed_record_reproduces(tmp_path):
    pop = json.load(open(os.path.join(TA, "population.json"), encoding="utf-8"))
    missing = sorted({r["slug"] for r in pop["rows"] if not os.path.exists(os.path.join(ROOT, "cache", r["slug"], "records.json"))})
    if missing:
        pytest.skip(f"cache not held in this checkout for {len(missing)} topics: {missing[:3]}")
    jobs = tmp_path / "jobs"
    r = subprocess.run([sys.executable, os.path.join(TA, "scripts", "make_packets.py"), str(jobs)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    cta = _load("check_typed_arms")
    n = 0
    for row in pop["rows"]:
        src = os.path.join(TA, "extractions", row["row_id"])
        for f in os.listdir(src):
            shutil.copy(os.path.join(src, f), jobs / row["row_id"] / f)
        rec = cta.check_row(row, str(jobs))
        want = json.load(open(os.path.join(TA, "records", row["row_id"] + ".json"), encoding="utf-8"))
        assert rec["state"] == want["state"], (row["row_id"], rec["reasons"])
        assert rec["reasons"] == want["reasons"], row["row_id"]
        got_arms = [(a["arm_id"], a["f4b_slot"], a["events"], a["total"], a.get("events_ownership"), a.get("total_ownership"))
                    for a in rec["arm_observations"]]
        want_arms = [(a["arm_id"], a["f4b_slot"], a["events"], a["total"], a.get("events_ownership"), a.get("total_ownership"))
                     for a in want["arm_observations"]]
        assert got_arms == want_arms, row["row_id"]
        n += 1
    assert n == pop["n"] == 35  # the frozen population; it never shrinks
