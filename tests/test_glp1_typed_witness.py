"""Typed per-arm / per-field witnesses for FLOW's and ELIXA's 3-point MACE rows
(evidence/typed_arms/v2/glp1/build_glp1_typed.py). The committed file must rebuild byte-for-byte; every witness must
resolve in the held bytes; and each role-anchor defect planted into one source must be REFUSED, not written."""
import copy, hashlib, importlib.util, json, os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "evidence", "typed_arms", "v2", "glp1", "build_glp1_typed.py")


def _load():
    spec = importlib.util.spec_from_file_location("build_glp1_typed", P)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def mod():
    return _load()


def _dec(m, trial):
    return json.load(open(os.path.join(m.ROOT, "evidence", "glp1_adjudication", f"{trial}.json"), encoding="utf-8"))


def test_committed_file_rebuilds_exactly(mod):
    assert mod.main(check=True) == 0


def test_every_witness_resolves_in_the_held_bytes(mod):
    d = json.load(open(mod.OUT, encoding="utf-8"))
    assert sorted(d["rows"]) == ["ELIXA", "FLOW"] and d["refused"] == {}
    for trial, r in d["rows"].items():
        ws = [w for o in r["observations"] for w in (o["event_witness"], o["total_witness"])]
        ws += [a[k] for a in r["role_anchors"] for k in ("header", "row", "sentence", "measurement", "denominator") if k in a]
        ws += list(r["field_witnesses"].values())
        for w in ws:
            raw = open(os.path.join(mod.ROOT, w["document_ref"]), "rb").read()
            assert hashlib.sha256(raw).hexdigest() == w["document_sha256"], (trial, w["document_ref"])
            assert mod.textrep.render(w["document_ref"])[w["start"]:w["end"]] == w["text"], (trial, w["role"])
        for o in r["observations"]:
            assert mod.num(o["event_witness"]["text"]) == o["events"] and mod.num(o["total_witness"]["text"]) == o["total"]
            assert o["total_witness"]["derivation"] is None
        coords = {(w["document_ref"], w["start"], w["end"]) for o in r["observations"]
                  for w in (o["event_witness"], o["total_witness"])}
        assert len(coords) == 4
        assert all(a["roles"] == {o["role"]: o["events"] for o in r["observations"]} for a in r["role_anchors"])


def _planted(m, ref, old, new):
    """Replace `old` with `new` in the render of one held source (bytes' sha kept: the planted defect is in the TEXT)."""
    sha, t = m.doc(ref)
    assert t.count(old) == 1, old
    m._cache[ref] = (sha, t.replace(old, new))


@pytest.mark.parametrize("trial,ref_attr,old,new,why", [
    ("FLOW", "FLOW_REG", "MEASUREMENT : Semaglutide=212; Placebo=254", "MEASUREMENT : Semaglutide=254; Placebo=212",
     "role anchors disagree"),
    ("FLOW", "LABEL", "Placebo N=1766 (%) OZEMPIC 1 mg N=1767", "OZEMPIC 1 mg N=1767 (%) Placebo N=1766",
     "role anchors disagree"),
    ("ELIXA", "STATR", "392 and 400 in placebo and lixisenatide group, respectively",
     "392 and 400 in lixisenatide and placebo group, respectively", "role anchors disagree"),
    ("ELIXA", "STATR", "MACE endpoint (on-study) 1.02", "Placebo (N=3,034) Lixisenatide (N=3,034) MACE endpoint (on-study) 1.02",
     "not the nearest header"),
    ("FLOW", "FLOW_REG", "DENOM Participants: Semaglutide=1767; Placebo=1766\nRESULT OUTCOME 11 MEASUREMENT",
     "DENOM Participants: Semaglutide=1766; Placebo=1767\nRESULT OUTCOME 11 MEASUREMENT", "registry denominators"),
])
def test_PLANT_role_anchor_defects_are_refused(trial, ref_attr, old, new, why):
    m = _load()
    _planted(m, getattr(m, ref_attr), old, new)
    with pytest.raises(m.Refused, match=why):
        getattr(m, trial.lower())(_dec(m, trial))


def test_PLANT_changed_held_bytes_are_refused():
    m = _load()
    dec = copy.deepcopy(_dec(m, "FLOW"))
    dec["bound_result"]["endpoint"]["sha256"] = "0" * 64
    with pytest.raises(m.Refused, match="held bytes changed"):
        m.flow(dec)


def test_PLANT_decision_events_that_differ_from_the_witnessed_ones_are_refused():
    m = _load()
    dec = copy.deepcopy(_dec(m, "ELIXA"))
    dec["bound_result"]["events"] = {"lixisenatide": 392, "placebo": 400}
    with pytest.raises(m.Refused, match="differ from the witnessed"):
        m.elixa(dec)
