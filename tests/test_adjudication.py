"""The adjudication object and its content reference (harness/adjudication.py), with the plants that fired
on the pre-fix join (main 9d4f4894, claimgraph.regulatory_fact): a served row cited an adjudication by NAME,
joined by NCT to the LAST proposal for the trial, with `state: PROPOSED` and `countersigned: False` as
literals. The pre-fix function is executed from git against a throwaway repository, so each plant is a
measurement, not a reading of the old code."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import adjudication, claimgraph  # noqa: E402

def _clean_env():
    """No repository-location variables: a throwaway `git init` must never act on a hook's GIT_DIR (ws/HOOKENV)."""
    import os
    return {k: v for k, v in os.environ.items() if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR', 'GIT_PREFIX')}

PRE_FIX = "9d4f4894"


def _record(**over):
    rec = {"id": "ADJ-T-001", "trial": "T", "nct": "NCT00000001",
           "question": "Which row?", "reviewer_A": {"value": "HR 1.24"}, "reviewer_B": {"value": "HR 1.36"},
           "rule_applied": "timepoint", "decision": "End-of-study row adopted: HR 1.24"}
    rec.update(over)
    return adjudication.seal(rec)


# ---------------------------------------------------------------- the object

def test_hash_covers_the_decision_and_not_the_countersignature():
    a = _record()
    edited = adjudication.seal({**a, "decision": "End-of-treatment row adopted: HR 1.36"})
    assert edited["sha256"] != a["sha256"], "changing the decision must move the hash"
    signed = adjudication.seal({**a, "status": "COUNTERSIGNED",
                                "countersignature": {"by": "M", "date_utc": "2026-09-19T00:00:00Z", "record_sha256": a["sha256"]}})
    assert signed["sha256"] == a["sha256"], "countersigning signs the hash; it must not move it"
    assert adjudication.validate(signed) == []


def test_validate_refuses_an_edited_record_and_a_bad_signature():
    a = _record()
    a["decision"] = "quietly changed"
    assert any("edited after sealing" in p for p in adjudication.validate(a))
    b = _record(status="COUNTERSIGNED", countersignature={"by": "M", "date_utc": "x", "record_sha256": "0" * 64})
    assert any("countersignature signs" in p for p in adjudication.validate(b))
    c = _record()
    c["countersignature"] = {"by": "M", "date_utc": "x", "record_sha256": c["sha256"]}
    assert any("carries a countersignature but status" in p for p in adjudication.validate(c))


def test_reference_is_built_from_the_record_never_typed():
    a = _record()
    ref = adjudication.reference(a)
    assert ref == {"adjudication_id": "ADJ-T-001", "adjudication_sha256": a["sha256"], "status": "PROPOSED", "countersigned": False}


def test_resolve_refuses_missing_none_and_withdrawn():
    reg = {"ADJ-T-001": _record(), "ADJ-T-002": _record(id="ADJ-T-002", status="WITHDRAWN")}
    with pytest.raises(adjudication.AdjudicationError, match="names no adjudication_id"):
        adjudication.resolve(None, reg)
    with pytest.raises(adjudication.AdjudicationError, match="ADJ-T-009: not in"):
        adjudication.resolve("ADJ-T-009", reg)
    with pytest.raises(adjudication.AdjudicationError, match="WITHDRAWN"):
        adjudication.resolve("ADJ-T-002", reg)


def test_check_object_refuses_stale_hash_name_only_and_prose_dangling():
    a = _record()
    reg = {a["id"]: a}
    good = {"held_regulatory_facts": [{"decision": {"adjudication_id": "ADJ-T-001"}, "adjudication": adjudication.reference(a)}]}
    assert adjudication.check_object(good, reg, "x") == []
    stale = copy.deepcopy(good)
    stale["held_regulatory_facts"][0]["adjudication"]["adjudication_sha256"] = "f" * 64
    assert any("the decision changed under the citation" in p for p in adjudication.check_object(stale, reg, "x"))
    legacy = {"held_regulatory_facts": [{"adjudication": {"id": "ADJ-T-001", "state": "PROPOSED", "countersigned": False}}]}
    assert any("name-only citation" in p for p in adjudication.check_object(legacy, reg, "x"))
    prose = {"note": "adjudicated: ADJ-T-777"}
    assert any("mentions ADJ-T-777, not in the registry" in p for p in adjudication.check_object(prose, reg, "x"))
    signed_since = copy.deepcopy(good)
    reg2 = {a["id"]: adjudication.seal({**a, "status": "COUNTERSIGNED",
                                         "countersignature": {"by": "M", "date_utc": "x", "record_sha256": a["sha256"]}})}
    assert any("cited as PROPOSED, registry says COUNTERSIGNED" in p for p in adjudication.check_object(signed_since, reg2, "x"))


# ---------------------------------------------------------------- the plants

def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=_clean_env()).stdout.strip()


def _throwaway(tmp_path: Path):
    """A committed repository holding one 'document' and its extracted text, as regulatory_fact expects."""
    repo = tmp_path / "repo"
    (repo / "held").mkdir(parents=True)
    doc = repo / "held" / "doc.pdf"
    doc.write_bytes(b"%PDF-throwaway\n")
    text = repo / "held" / "doc.pdf.txt"
    text.write_bytes(b"### PAGE 1\nTable 19 HR 1.24 (0.90, 1.70)\n")
    _git(repo, "init", "-q")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.test", "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.test", "commit", "-q", "-m", "base")
    source = {"document_path": "held/doc.pdf", "document_sha256": hashlib.sha256(doc.read_bytes()).hexdigest(),
              "extracted_text_path": "held/doc.pdf.txt", "extracted_text_sha256": hashlib.sha256(text.read_bytes()).hexdigest()}
    decision = {"trial": "T", "trial_key": "1", "nct": "NCT00000001", "decision": "EXTRACTED",
                "span": "Table 19 HR 1.24 (0.90, 1.70)", "span_page_pdf": 1}
    return repo, source, decision


def _prefix_regulatory_fact():
    """claimgraph.regulatory_fact as it was at the pre-fix commit, loaded from git."""
    src = subprocess.run(["git", "show", f"{PRE_FIX}:harness/claimgraph.py"], cwd=ROOT, check=True,
                         capture_output=True, text=True, encoding="utf-8", env=_clean_env()).stdout
    mod = types.ModuleType("claimgraph_prefix")
    mod.__package__ = "harness"
    exec(compile(src, f"<{PRE_FIX}:harness/claimgraph.py>", "exec"), mod.__dict__)
    return mod.regulatory_fact


def test_plant_prefix_citation_was_a_container(tmp_path):
    """PLANT on 9d4f4894: delete the adjudication -> the row still says PROPOSED (id None); edit the decision
    -> the served citation is byte-identical; add a later proposal for the same trial -> the row cites it,
    whatever the decision was decided by."""
    repo, source, decision = _throwaway(tmp_path)
    fact_prefix = _prefix_regulatory_fact()
    adj1 = {"id": "ADJ-T-001", "nct": "NCT00000001", "decision": "End-of-study row adopted: HR 1.24"}
    cited = fact_prefix(str(repo), source, decision, [adj1])["adjudication"]
    assert cited == {"id": "ADJ-T-001", "state": "PROPOSED", "countersigned": False}
    # (a) deletion: no record at all, still a PROPOSED citation
    deleted = fact_prefix(str(repo), source, decision, [])["adjudication"]
    assert deleted == {"id": None, "state": "PROPOSED", "countersigned": False}
    # (b) edit: the decision flips to the other reviewer's row; the citation does not move
    edited = fact_prefix(str(repo), source, decision, [{**adj1, "decision": "End-of-treatment row adopted: HR 1.36"}])["adjudication"]
    assert json.dumps(edited, sort_keys=True) == json.dumps(cited, sort_keys=True)
    # (c) join by NCT, last wins
    later = fact_prefix(str(repo), source, decision, [adj1, {"id": "ADJ-T-002", "nct": "NCT00000001"}])["adjudication"]
    assert later["id"] == "ADJ-T-002"


def test_postfix_citation_is_a_content_reference(tmp_path):
    repo, source, decision = _throwaway(tmp_path)
    a = _record()
    registry = {a["id"]: a}
    named = {**decision, "adjudication_id": "ADJ-T-001"}
    fact = claimgraph.regulatory_fact(str(repo), source, named, registry)
    assert fact["adjudication"] == adjudication.reference(a)
    # (a) deletion refuses, naming the id
    with pytest.raises(adjudication.AdjudicationError, match="ADJ-T-001: not in"):
        claimgraph.regulatory_fact(str(repo), source, named, {})
    # (b) edit moves the reference's hash
    edited = adjudication.seal({**a, "decision": "End-of-treatment row adopted: HR 1.36"})
    fact2 = claimgraph.regulatory_fact(str(repo), source, named, {edited["id"]: edited})
    assert fact2["adjudication"]["adjudication_sha256"] != fact["adjudication"]["adjudication_sha256"]
    # (c) a later record for the same trial is not what the decision names
    other = _record(id="ADJ-T-002")
    fact3 = claimgraph.regulatory_fact(str(repo), source, named, {a["id"]: a, other["id"]: other})
    assert fact3["adjudication"]["adjudication_id"] == "ADJ-T-001"
    # a decision that names nothing carries None, never a synthetic PROPOSED
    assert claimgraph.regulatory_fact(str(repo), source, decision, registry)["adjudication"] is None


def test_registry_on_this_tree_loads_and_every_served_citation_resolves():
    registry = adjudication.load(str(ROOT))
    assert registry, "registry/adjudications.json is empty"
    ok, problems = adjudication.check(str(ROOT))
    assert ok, problems
    s = adjudication.summary(str(ROOT))
    assert s["citations"] > 0 and s["records_cited"] > 0
