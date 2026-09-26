"""V1.1 (not V1): the estimand VALUES the ordered-contrast check does not reach. From the external auditor's pass against the live release
57dcc327, 2026-09-26. The live verifier d1ba9320 passed all three one-value LEADER mutations. V1 (lane OC, 23642e0d) closes two of them:
comparator_direction -> COMPARATOR_DIRECTION_MISMATCH and estimator -> ESTIMATOR_MISMATCH. It leaves open:
  - analysis_set's VALUE changed while its basis stays REGISTERED_DEFAULT            -> REGISTERED_DEFAULT_VALUE_MISMATCH
  - a default field's `registered` swapped                                           -> REGISTERED_DEFAULT_VALUE_MISMATCH
  - analysis_identity_key edited alone (never recomputed for ordinary rows)          -> ANALYSIS_IDENTITY_KEY_MISMATCH
  - the key omits comparator_direction (format 3.19 puts it in the key)              -> ANALYSIS_IDENTITY_KEY_MISMATCH at 3.19

Each plant runs through the REAL verifier on the REAL LEADER row. The served tree is read from git objects at the pinned commit
23642e0d, so it is immutable: a control anchored to a live corpus would retire itself. Only one value of BUNDLE.json is changed, in
memory. Every plant must PASS the pre-fix verifier (the blob at 23642e0d) and FAIL the current one FOR ITS OWN CODE. The canonical
control must PASS both, or nothing here means anything."""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import verify_bundle as vb          # noqa: E402

PINNED = "23642e0d42457beff74b3930a0ccb0e5284e8db2"   # oc/ordered-contrast, the V1 integration input
SLUG, LEADER = "glp1-ra-mace-t2d", "27295427"
BUNDLE = f"reviews/{SLUG}/BUNDLE.json"


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)


if _git("cat-file", "-e", f"{PINNED}:docs/{BUNDLE}").returncode != 0:
    pytest.fail(f"the pinned served tree {PINNED} is not in this clone: fetch history; this control must not silently skip", pytrace=False)


def _load(src_bytes, name):
    d = tempfile.mkdtemp()
    p = os.path.join(d, f"{name}.py")
    open(p, "wb").write(src_bytes)
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PRE_FIX = _load(_git("show", f"{PINNED}:scripts/verify_bundle.py").stdout, "vb_prefix_identity")


def _run(mod, mutate):
    class GitStore(mod.Store):
        def __init__(self):
            super().__init__(None, None)

        def get(self, path):
            if path not in self.cache:
                p = _git("cat-file", "blob", f"{PINNED}:docs/{path}")
                if p.returncode != 0:
                    raise mod.Refusal("ARTEFACT_UNREACHABLE", f"{path} is not present in the served tree")
                self.cache[path] = p.stdout
            return self.cache[path]
    s = GitStore()
    b = json.loads(s.get(BUNDLE).decode("utf-8"))
    if mutate:
        mutate(b, next(r for r in b["verification_rows"] if r["trial"]["id"].replace("PMID ", "") == LEADER))
    s.cache[BUNDLE] = json.dumps(b).encode("utf-8")
    rep = mod.run(s, SLUG, None)
    return rep["verdict"], sorted({f.split(" ")[0] for f in rep["failures"] if LEADER in f})


def _analysis_set_value(b, r):
    r["analysis_identity"]["analysis_set"]["value"] = "per-protocol"


def _registered_swapped(b, r):
    r["analysis_identity"]["analysis_set"]["registered"] = "per-protocol"


def _key_edited(b, r):
    ai = r["analysis_identity"]
    ai["analysis_identity_key"] = ai["analysis_identity_key"].replace("default)[REG]", "default)[STA]")


PLANTS = [("analysis_set_value", _analysis_set_value, "REGISTERED_DEFAULT_VALUE_MISMATCH"),
          ("registered_swapped", _registered_swapped, "REGISTERED_DEFAULT_VALUE_MISMATCH"),
          ("key_edited_alone", _key_edited, "ANALYSIS_IDENTITY_KEY_MISMATCH")]


@pytest.mark.parametrize("mod", [PRE_FIX, vb], ids=["pre_fix", "current"])
def test_canonical_control_passes(mod):
    assert _run(mod, None) == ("PASS", [])


@pytest.mark.parametrize("name,plant,code", PLANTS, ids=[p[0] for p in PLANTS])
def test_plant_passes_pre_fix_and_is_refused_for_its_own_code_now(name, plant, code):
    assert _run(PRE_FIX, plant)[0] == "PASS", f"{name}: a plant that never fired proves nothing"
    verdict, codes = _run(vb, plant)
    assert verdict == "FAIL" and code in codes, (name, verdict, codes)


def test_key_at_319_must_carry_the_comparator():
    ai = {k: {"value": v, "basis": "STATED_IN_OWNING_EVIDENCE"} for k, v in
          (("analysis_set", "ITT"), ("treatment_strategy", "tp"), ("follow_up_window", "w"), ("comparator_direction", "A vs B"), ("estimator", "hazard ratio"))}
    legacy = vb.identity_key(ai, vb.IDENTITY_KEY_FIELDS_LEGACY)
    assert "comparator_direction" not in legacy
    ai["analysis_identity_key"] = legacy
    assert [c for c, _ in vb.identity_value_check(ai, {}, {}, "3.18")] == []
    assert [c for c, _ in vb.identity_value_check(ai, {}, {}, "3.19")] == ["ANALYSIS_IDENTITY_KEY_MISMATCH"]
    ai["analysis_identity_key"] = vb.identity_key(ai, vb.IDENTITY_KEY_FIELDS)
    assert [c for c, _ in vb.identity_value_check(ai, {}, {}, "3.19")] == []
    flipped = copy.deepcopy(ai)
    flipped["comparator_direction"]["value"] = "B vs A"
    assert vb.identity_key(flipped, vb.IDENTITY_KEY_FIELDS) != ai["analysis_identity_key"]


def test_the_producer_key_is_the_verifiers_key():
    src = open(os.path.join(ROOT, "scripts", "build_bundle.py"), encoding="utf-8").read()
    assert 'FORMAT_REVISION = "3.19"' in src
    assert '("analysis_set", "treatment_strategy", "follow_up_window", "comparator_direction", "estimator")' in src
    assert vb.IDENTITY_KEY_FIELDS == ("analysis_set", "treatment_strategy", "follow_up_window", "comparator_direction", "estimator")
