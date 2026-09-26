"""Losing endpoint identity must never INCREASE admissibility (external audit, 2026-09-26; BUNDLE limit L10_admit_rows_fail_open).

harness.target_endpoint.admissibility() refused a classified non-target row (DIFFERENT_OUTCOME / NEAR_MATCH undeclared /
ENDPOINT_UNBOUND) but sent a row with NO class to a legacy branch that ran only composite_component_mismatch() on its prose and
otherwise returned admissible=True / UNBOUND_LEGACY, which admit_rows() kept. Deleting the class made the row MORE admissible.
It now abstains: ENDPOINT_IDENTITY_MISSING, never admissible.

Every row here is built from HELD BYTES (the GLP-1 records.json abstracts at the pinned candidate 3876a62d, read from git objects:
an immutable control that no corpus edit can retire). Classification is the real classify_bound(); verdicts are the real
admissibility() and admit_rows(). The plant runs against the PRE-FIX producer (harness/ exported from 3876a62d, target_endpoint
blob 1b309c5b), where it must be ADMITTED, and against the current one, where it must be refused. A plant that never fired
proves nothing. The pinned commit missing from history is a FAILURE, not a skip."""
import copy
import importlib.util
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPRO = os.path.join(ROOT, "evidence", "unbound_legacy", "repro.py")
PRE_FIX = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
PRE_FIX_BLOB = "1b309c5bd5c49592f50d29f38515aaa9ab6b55dc"

if subprocess.run(["git", "cat-file", "-e", f"{PRE_FIX}:harness/target_endpoint.py"], cwd=ROOT, capture_output=True).returncode != 0:
    pytest.fail(f"{PRE_FIX[:8]} is not in this clone's history: the pre-fix leg cannot run (fetch history; never a skip)", pytrace=False)

_spec = importlib.util.spec_from_file_location("unbound_repro", REPRO)
repro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(repro)

PRE = repro.load_harness(PRE_FIX)
NOW = repro.load_harness(None)
SPEC, ABSTRACTS, ELIXA, LEADER = repro.fixtures()


def _rows(te):
    e = repro.classified(te, SPEC, ABSTRACTS["26630143"], ELIXA)
    l = repro.classified(te, SPEC, ABSTRACTS["27295427"], LEADER)
    return e, l


def _strip(row):
    return {k: v for k, v in row.items() if not k.startswith("target_endpoint")}


def test_the_pre_fix_producer_is_the_blob_the_audit_names():
    got = subprocess.run(["git", "rev-parse", f"{PRE_FIX}:harness/target_endpoint.py"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    assert got == PRE_FIX_BLOB


def test_the_real_classifier_reads_the_held_text_as_the_audit_describes():
    for te in (PRE, NOW):
        e, l = _rows(te)
        assert l["target_endpoint_class"] == "EXACT_TARGET"                  # LEADER: 3-point MACE, the declared composite
        assert e["target_endpoint_class"] == "NEAR_MATCH"                    # ELIXA: 3-point + hospitalisation for unstable angina
        assert e["extra_components"] and not e["missing_components"]      # classify_bound names them without the prefix


@pytest.mark.parametrize("te,label", [(PRE, "pre_fix"), (NOW, "current")], ids=["pre_fix", "current"])
def test_authentic_3_point_passes_and_classified_non_target_is_refused_on_both(te, label):
    e, l = _rows(te)
    assert repro.verdict(te, SPEC, l) == {"admissible": True, "verdict": "EXACT_TARGET", "kept_by_admit_rows": True, "refused_code": None}
    v = repro.verdict(te, SPEC, e)
    assert v["admissible"] is False and not v["kept_by_admit_rows"] and v["verdict"] == "RESULT_INCOMPATIBLE"
    forced = dict(e, target_endpoint_class="DIFFERENT_OUTCOME")            # the auditor's framing: classified DIFFERENT_OUTCOME
    v = repro.verdict(te, SPEC, forced)
    assert v["admissible"] is False and not v["kept_by_admit_rows"] and v["verdict"] == "RESULT_INCOMPATIBLE"


def test_plant_class_deleted_is_admitted_by_the_pre_fix_producer():
    e, _ = _rows(PRE)
    v = repro.verdict(PRE, SPEC, _strip(e))
    assert v == {"admissible": True, "verdict": "UNBOUND_LEGACY", "kept_by_admit_rows": True, "refused_code": None}, \
        "the plant must FIRE on the pre-fix producer, else this test proves nothing"


@pytest.mark.parametrize("mutate", ["deleted", "none", "unknown_string"])
def test_losing_endpoint_identity_never_increases_admissibility(mutate):
    e, _ = _rows(NOW)
    row = _strip(e) if mutate == "deleted" else dict(e, target_endpoint_class=None if mutate == "none" else "SOMETHING_ELSE")
    v = NOW.admissibility(SPEC, copy.deepcopy(row))
    assert v["admissible"] is False and v["verdict"] == "ENDPOINT_IDENTITY_MISSING" and v.get("abstain") is True, v
    kept, refused = NOW.admit_rows(SPEC, [copy.deepcopy(row)])
    assert not kept and refused[0]["reason_code"] == "ENDPOINT_IDENTITY_MISSING" and refused[0]["state"] == "EXTRACTION_DEBT"
    assert refused[0]["candidate_tuple"] == {"effect": 1.02, "ci_low": 0.89, "ci_high": 1.17, "scale": "HR"}   # the number stays visible


def test_the_invariant_across_every_class_the_row_could_carry():
    """Admissibility with the class removed is never greater than with any class present (False < True)."""
    e, l = _rows(NOW)
    for row in (e, l):
        without = NOW.admissibility(SPEC, copy.deepcopy(_strip(row)))["admissible"]
        for cls in ("EXACT_TARGET", "NEAR_MATCH", "DIFFERENT_OUTCOME", "ENDPOINT_UNBOUND"):
            assert bool(without) <= bool(NOW.admissibility(SPEC, copy.deepcopy(dict(row, target_endpoint_class=cls)))["admissible"])


def test_restore_passes_again():
    e, l = _rows(NOW)
    assert repro.verdict(NOW, SPEC, l)["kept_by_admit_rows"] is True
    assert repro.verdict(NOW, SPEC, e)["verdict"] == "RESULT_INCOMPATIBLE"


def test_the_composite_mismatch_refusal_still_precedes_the_abstain():
    """A classless row whose own prose names a composite with an extra component keeps the stronger, evidence-based refusal."""
    e, _ = _rows(NOW)
    row = _strip(e)
    row["source"] = ("hand-verified: primary composite of cardiovascular death, myocardial infarction, stroke, or hospitalization "
                     "for unstable angina: HR 1.02 (0.89-1.17)")
    assert NOW.extract.composite_component_mismatch(SPEC["name"], row["source"])    # the check must actually fire on this prose
    v = NOW.admissibility(SPEC, copy.deepcopy(row))
    assert v["admissible"] is False and v["verdict"] == "RESULT_INCOMPATIBLE"
    row["source"] = "hand-verified effect+CI (HR): 1.02 (0.89-1.17)"               # no composite named: nothing to refuse on
    assert not NOW.extract.composite_component_mismatch(SPEC["name"], row["source"])
    assert NOW.admissibility(SPEC, copy.deepcopy(row))["verdict"] == "ENDPOINT_IDENTITY_MISSING"
