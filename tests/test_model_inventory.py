"""Every place a model is reachable, and every model output the repo holds, is NAMED here with its reason -- a new
one fails until it is either routed through reproducible_ai.model_call_live (recorded, replayable, inert until
countersigned) or listed with a reason a reviewer can check. An entry that stops being true must be removed.

This is a ratchet, not a certificate of health: the lists below include debt (a legacy codex caller, and committed
model judgments without the contract's record that the build reads). Listing it is the point -- the repo's earlier
sweep counted calls in the certificate closure only and read "none" (see reproducible_ai/model_inventory.py).
"""
from __future__ import annotations

from pathlib import Path

from reproducible_ai import model_inventory as mi

ROOT = Path(__file__).resolve().parents[1]

# (file, what) -> why it is allowed. Verified by reading each site on 2026-09-24.
MODEL_CALL_SITES = {
    ("reproducible_ai/model_call_live.py", "shutil.which('codex')"): "the contract's single caller: resolves the client",
    ("reproducible_ai/model_call_live.py", "argv head 'codex'"): "the redacted argv stored IN the record (not a call)",
    # (scripts/outcome_judgments.py was a second, unrecorded codex caller until 2026-09-24; it now calls
    #  reproducible_ai.model_call_live and is no longer a call site of its own.)
    ("tests/test_no_model_call_in_pinned_path.py", "argv head 'codex'"): "a planted argv in a test fixture",
}

# (file, argv expression) -> what it runs. A subprocess whose program is not a literal cannot be classified by reading
# the call; each was traced to its assignment.
UNRESOLVED_SUBPROCESS = {
    ("docs/evidence/fix-ladder-2026-09-14/lane_j_tools.py", "cmd"): "python (cmd = [sys.executable, SELF, 'run-case', ...])",
    ("reproducible_ai/model_call_live.py", "[_codex_exe(), '--version']"): "codex --version (client version for the record)",
    ("reproducible_ai/model_call_live.py", "argv"): "codex exec -- THE recorded model call",
    ("scripts/build_search_benchmark.py", "cmd"): "python scripts/measure_search_recall.py (the `commands` list)",
    ("scripts/m2_battery.py", "cmd"): "python build_topic.py / python -m harness.gate (run([PY, ...]) callers)",
    ("scripts/verify_all.py", "cmd"): "python -m pytest / python scripts/... (_run([sys.executable, ...]) callers)",
    ("tests/test_certificate_code_closure.py", "args"): "python scripts/audit_certificate_stdlib.py",
    ("tests/test_gate_scorecard.py", "cmd"): "git init / add / commit on a fixture repo",
}

# committed model outputs -> what reads them and what they can change
MODEL_OUTPUTS = {
    "cache/balanced-crystalloids-vs-saline-mortality/outcome_judgments.json":
        "DEBT, served path: harness/pipeline.py::_load_outcome_judgments (topic outcome_identity=true) admits/refuses "
        "CT.gov outcome measures; recorded as model='hand/model via --write' -- no prompt bytes, no response hash. "
        "(The script that writes it now records every call, and names a hand author; this FILE predates that.)",
    "cache/antibiotics-vs-appendectomy-appendicitis/locate_judgments.json":
        "DEBT, served path: harness/locate.py (topic locate_gate=true) can REMOVE a trial from a pool; model='fable-5.1', "
        "dated, span given; no prompt bytes, no response hash",
    "cache/probiotics-aad-prevention/locate_judgments.json": "DEBT, served path: as above (locate gate)",
    "cache/vitamin-d-acute-respiratory-infection/locate_judgments.json": "DEBT, served path: as above (locate gate)",
    **{f"cache/{s}/screen_adjudication.json":
       "advisory: harness/pipeline.py renders the adjudicator's disagreement flags; the served decision is the rule's"
       for s in ("colchicine-postop-af", "colchicine-recurrent-pericarditis", "colchicine-secondary-cv-prevention",
                 "finerenone-ckd-t2d-renal", "omega3-cardiovascular-events", "probiotics-aad-prevention",
                 "sglt2-ckd-progression", "statins-primary-prevention-elderly", "ticagrelor-vs-clopidogrel-acs")},
}


def test_every_model_call_site_is_named():
    found = {(f, what) for f, _, what in mi.call_sites(ROOT)}
    assert found - set(MODEL_CALL_SITES) == set(), "new model call site(s): route through reproducible_ai.model_call_live"
    assert set(MODEL_CALL_SITES) - found == set(), "listed site(s) no longer exist: remove them from the list"


def test_every_unreadable_subprocess_program_is_traced():
    found = {(f, expr) for f, _, expr in mi.unresolved_subprocess(ROOT)}
    assert found - set(UNRESOLVED_SUBPROCESS) == set(), "subprocess with a non-literal program: trace it and list it"
    assert set(UNRESOLVED_SUBPROCESS) - found == set(), "listed site(s) no longer exist: remove them"


def test_every_committed_model_output_is_named_and_none_is_silently_recorded_or_unrecorded():
    found = {o["path"]: o for o in mi.model_outputs(ROOT)}
    assert set(found) - set(MODEL_OUTPUTS) == set(), "new committed model output: record it (registry/model_calls) or list it"
    assert set(MODEL_OUTPUTS) - set(found) == set(), "listed output(s) gone: remove them"
    # the day one of them carries the contract's record, this list must say so (it is not debt any more)
    assert all(o["state"] == "UNRECORDED" for o in found.values() if "DEBT" in MODEL_OUTPUTS[o["path"]])


# ------------------------------------------------------------------------------------------------ plants
def test_the_sweeps_fire_on_planted_sites(tmp_path):
    (tmp_path / "a.py").write_text("import subprocess\nsubprocess.run(['claude', '-p', 'x'])\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("import subprocess\ncmd = ['codex', 'exec']\nsubprocess.run(cmd)\n", encoding="utf-8")
    (tmp_path / "c.py").write_text("import shutil\nexe = shutil.which('gemini')\n", encoding="utf-8")
    (tmp_path / "d.py").write_text("import anthropic\n", encoding="utf-8")
    (tmp_path / "e.py").write_text("import subprocess, sys\nsubprocess.run([sys.executable, '-V'])\nNAMES = ('codex',)\n",
                                   encoding="utf-8")
    files = ["a.py", "b.py", "c.py", "d.py", "e.py"]
    sites = {(f, what) for f, _, what in mi.call_sites(tmp_path, files)}
    assert sites == {("a.py", "argv head 'claude'"), ("b.py", "argv head 'codex'"),
                     ("c.py", "shutil.which('gemini')"), ("d.py", "import anthropic")}
    assert {(f, e) for f, _, e in mi.unresolved_subprocess(tmp_path, files)} == {("b.py", "cmd")}


def test_the_output_sweep_fires_and_tells_recorded_from_unrecorded(tmp_path):
    (tmp_path / "cache" / "t").mkdir(parents=True)
    (tmp_path / "registry" / "model_calls").mkdir(parents=True)
    (tmp_path / "registry" / "model_calls" / "mc-abc.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cache" / "t" / "u.json").write_text('{"x": {"y": {"model": "m", "is_match": true}}}', encoding="utf-8")
    (tmp_path / "cache" / "t" / "r.json").write_text('{"x": {"model": "m", "record_id": "mc-abc"}}', encoding="utf-8")
    (tmp_path / "cache" / "t" / "n.json").write_text('{"x": 1}', encoding="utf-8")
    got = {o["path"]: o["state"] for o in mi.model_outputs(tmp_path)}
    assert got == {"cache/t/u.json": "UNRECORDED", "cache/t/r.json": "RECORDED"}
