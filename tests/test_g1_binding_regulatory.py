"""PLANTS for the regulatory own-tuple route (scripts/g1_binding_regulatory.py R1-R4 + g1_tracker.ci_at_95): an open FDA
label table prints the trial's 3-point MACE HR with a two-sided CI at a STATED level; the tracker re-checks the tuple and
the level verbatim and re-expresses the interval at 95% on the log scale. A one-sided bound, an unstated level, a
4-point composite or a held file that changed are refused."""
import hashlib
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_binding_regulatory as br  # noqa: E402
import g1_tracker as gt  # noqa: E402

LABEL = ("The primary endpoint in EXAMINE was the time to first occurrence of a MACE. Table 12. Patients with MACE and Type 2 "
         "Diabetes Mellitus in EXAMINE Composite of first event of CV death, nonfatal MI or nonfatal stroke (MACE) NESINA "
         "Placebo Hazard Ratio Number of Patients (%) Rate per 100 PY* Number of Patients (%) Rate per 100 PY* (98% CI) "
         "N=2701 N=2679 305 (11.3) 7.6 316 (11.8) 7.9 0.96 (0.80, 1.16) CV Death 89 (3.3) 2.2 111 (4.1) 2.8")


def test_r1_r4_bind_the_examine_label_row():
    ok, ref = br.candidates(LABEL, "EXAMINE", "dpp4-mace-t2d")
    assert len(ok) == 1 and ref == []
    c = ok[0]
    assert (c["effect"], c["lower"], c["upper"], c["ci_level"]) == ("0.96", "0.80", "1.16", "98")
    assert c["counts"] == {"n_t": 2701, "n_c": 2679, "events_t": 305, "events_c": 316}


def test_refusals():
    ok, ref = br.candidates(LABEL.replace("(98% CI) ", ""), "EXAMINE", "dpp4-mace-t2d")
    assert ok == [] and ref[0]["gate"] == "R3_CI"                              # level not stated
    ok, ref = br.candidates(LABEL.replace("0.96 (0.80, 1.16)", "0.96 (upper 1.16)"), "EXAMINE", "dpp4-mace-t2d")
    assert ok == [] and ref[0]["gate"] == "R4_UNIQUE"                          # one-sided: no two-bound row
    four = LABEL.replace("nonfatal stroke (MACE)", "nonfatal stroke or unstable angina requiring hospitalization (MACE plus)")
    ok, ref = br.candidates(four, "EXAMINE", "dpp4-mace-t2d")
    assert ok == [] and ref[0]["gate"] == "R2_ESTIMAND"                        # a 4th component
    assert br.candidates(LABEL, "TECOS", "dpp4-mace-t2d") == ([], [])          # another trial's table: not named


def test_ci_at_95_rescales_on_the_log_scale():
    lo, hi = gt.ci_at_95({"measure": "HR", "effect": "0.96", "lower": "0.80", "upper": "1.16", "ci_level": "98"})
    se = (math.log(1.16) - math.log(0.80)) / (2 * 2.3263478740408408)
    assert abs(lo - math.exp(math.log(0.96) - 1.959963984540054 * se)) < 1e-9 and abs(hi - 1.1225) < 5e-4
    assert gt.ci_at_95({"measure": "HR", "effect": "0.96", "lower": "", "upper": "1.16", "ci_level": "98"}) is None
    assert gt.ci_at_95({"measure": "HR", "effect": "1.30", "lower": "0.80", "upper": "1.16", "ci_level": "98"}) is None
    lo, hi = gt.ci_at_95({"measure": "MD", "effect": "-4", "lower": "-6", "upper": "-2", "ci_level": "95"})
    assert abs(lo + 6) < 1e-9 and abs(hi + 2) < 1e-9                         # 95 -> 95 is the identity


def _bind(tmp_path, span, values):
    b = {"slug": "dpp4-mace-t2d", "label": "EXAMINE", "own_tuple": True, "tuple_kind": "EFFECT_CI",
         "source_kind": "REGULATORY", "source": "NDA022271 test", "values": values, "span": span}
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"bindings": [b]}), encoding="utf-8")
    o = {"slug": "dpp4-mace-t2d", "trials": [{"label": "EXAMINE", "route": "UNVERIFIED",
                                             "comparator_row": {"measure": "HR", "effect": "0.96", "lower": None, "upper": "1.16"}}]}
    return o, gt.apply_confirm_bindings(o, str(p))


def test_tracker_admits_a_stated_98_ci_and_reexpresses_it(tmp_path):
    ok, _ = br.candidates(LABEL, "EXAMINE", "dpp4-mace-t2d")
    v = {"measure": "HR", "effect": "0.96", "lower": "0.80", "upper": "1.16", "ci_level": "98"}
    o, flipped = _bind(tmp_path, ok[0]["span"], v)
    x = o["trials"][0]
    assert flipped == ["EXAMINE"] and x["route"] == "PRIMARY"
    se = (math.log(1.16) - math.log(0.80)) / (2 * 2.3263478740408408)
    exp_lo, exp_hi = (f"{math.exp(math.log(0.96) + s * 1.959963984540054 * se):.4f}" for s in (-1, 1))
    assert (x["our_value"]["effect"], x["our_value"]["lower"], x["our_value"]["upper"]) == ("0.96", exp_lo, exp_hi)
    assert x["our_value"]["ci_printed"] == {"level": "98", "lower": "0.80", "upper": "1.16"}
    o, flipped = _bind(tmp_path, ok[0]["span"].replace("(98% CI)", ""), v)     # level not in the span
    assert flipped == [] and o["trials"][0]["confirm_binding"]["why"] == "CI_LEVEL_NOT_PRINTED_IN_SPAN"


def test_held_section_matches_its_manifest():
    d = os.path.join(ROOT, "cache", "regulatory", "NDA022271")
    man = json.load(open(os.path.join(d, "manifest.json"), encoding="utf-8"))
    for name, m in man.items():
        assert hashlib.sha256(open(os.path.join(d, name), "rb").read()).hexdigest() == m["text_sha256"]
        assert m["url"].startswith("https://www.accessdata.fda.gov/") and len(m["pdf_sha256"]) == 64
    b = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "bindings_regulatory.json"), encoding="utf-8"))
    for x in b["bindings"]:
        held = open(os.path.join(ROOT, x["source_path"]), encoding="utf-8").read()
        assert x["span"] in held and hashlib.sha256(open(os.path.join(ROOT, x["source_path"]), "rb").read()).hexdigest() == x["source_sha256"]
