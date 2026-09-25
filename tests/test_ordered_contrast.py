"""Ordered contrast and estimator are VALUE-checked, not state-checked (lane OC, 2026-09-25; external audit).

The defect: scripts/verify_bundle.py emitted "vs placebo (named in the result clause)" whenever 'placebo' appeared, P10 compared only
the BASIS of comparator_direction and estimator, P11 never looked at the registered contrast ("GLP-1 RA vs placebo") or estimator
("hazard ratio, time to first event"), effect_less_than_1_favours was never consumed, and pool() took log(effect) of whatever it
was given. 0.87 served as liraglutide/placebo from a source that states placebo/liraglutide passed every check.

Layout of this file:
  1. a phrasing battery with KNOWN answers (synthetic clauses; a control must have an answer no corpus edit can move), run against
     BOTH implementations -- the verifier's stdlib copy and the producer's scripts/contrast_order.py;
  2. the served corpus: all 8 GLP-1 rows order, the two implementations agree row by row, canonical PASS (the positive control that
     keeps the fix from becoming reject-everything);
  3. every OC --corrupt limb through the real verifier, refused FOR ITS OWN CODE, no other row moved, restore -> PASS;
  4. served-tree plants (only BUNDLE.json edited) run against the PRE-FIX verifier (the blob at the lane's base commit) and the
     current one: each plant must PASS before the fix and FAIL after -- a plant that never fired proves nothing;
  5. the producer leg: build_bundle.build() on planted inputs -> the producer's own admission (the gate the bundle records)."""
import copy
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import verify_bundle as vb          # noqa: E402  test-side: the functions under test; the verifier itself imports nothing
import contrast_order as co                # noqa: E402  scripts/contrast_order.py, the producer's implementation

SLUG = "glp1-ra-mace-t2d"
VERIFIER = os.path.join(ROOT, "scripts", "verify_bundle.py")
LEADER = "27295427"
PREFIX_BASE = "c9d665e022a36111f31cb9e1d7b5867fe6e8fb2d"    # origin/main when lane OC branched: the verifier WITHOUT the value checks
TOPIC = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
VOCAB = vb.contrast_vocabulary(TOPIC)


# ------------------------------------------------------------------------------------------------ 1. battery, known answers
BATTERY = [
    # (clause, expected numerator side or None for UNORDERED, expected witness rule)
    ("The event occurred in 10 of 100 patients in the liraglutide group and in 20 of 100 in the placebo group (hazard ratio, 0.50; 95% CI, 0.30 to 0.80).",
     "EXPERIMENTAL", "ORDER_OF_MENTION"),
    ("The event occurred in 20 of 100 patients in the placebo group and in 10 of 100 in the liraglutide group (hazard ratio, 2.00; 95% CI, 1.25 to 3.33).",
     "REFERENCE", "ORDER_OF_MENTION"),
    ("Fewer patients had the event in the liraglutide group than in the placebo group (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).",
     "EXPERIMENTAL", "COMPARATIVE_CONNECTIVE"),
    ("More patients had the event in the placebo group than in the liraglutide group (hazard ratio, 1.15; 95% CI, 1.03 to 1.28).",
     "REFERENCE", "COMPARATIVE_CONNECTIVE"),
    ("Compared with placebo, liraglutide reduced the risk of the event (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).",
     "EXPERIMENTAL", "COMPARATIVE_CONNECTIVE"),
    ("The hazard ratio for placebo versus liraglutide was 1.15 (95% CI, 1.03 to 1.28).", "REFERENCE", "NUMERATOR_NAMED"),   # rule 0 wins; rule 1 agrees
    ("Semaglutide vs placebo: hazard ratio 0.74 (95% CI 0.58 to 0.95).", "EXPERIMENTAL", "COMPARATIVE_CONNECTIVE"),
    ("The hazard ratio vs placebo was 0.87 (95% CI, 0.78 to 0.97).", "EXPERIMENTAL", "COMPARATIVE_CONNECTIVE"),
    ("In this placebo-controlled trial of liraglutide the hazard ratio was 0.87 (95% CI, 0.78 to 0.97).", None, None),
    ("With better glycaemic control the hazard ratio was 0.87 (95% CI, 0.78 to 0.97).", None, None),
    ("Liraglutide versus placebo, as compared with liraglutide: hazard ratio 0.87 (95% CI, 0.78 to 0.97).", None, None),
    # from the blind reading (evidence/ordered_contrast/blind_reading/): a ratio 'for' an arm names the numerator -- the parser
    # read this placebo/liraglutide by order of mention before rule 0 existed (item C09)
    ("Events occurred in 694 placebo recipients and 608 liraglutide recipients (hazard ratio for liraglutide, 0.87; 95% CI, 0.78 to 0.97).",
     "EXPERIMENTAL", "NUMERATOR_NAMED"),
]


@pytest.mark.parametrize("impl", [vb, co], ids=["verifier", "producer"])
@pytest.mark.parametrize("clause,num,rule", BATTERY)
def test_battery_orders_every_known_phrasing_and_refuses_to_guess(impl, clause, num, rule):
    oc = impl.ordered_contrast(clause, [None, None, None], VOCAB, None)
    if num is None:
        assert oc["state"] == "UNORDERED" and oc["numerator_side"] is None, oc
        assert oc.get("reason")
    else:
        assert oc["state"] == "ORDERED" and oc["numerator_side"] == num, (clause, oc)
        assert oc["direction_witness"]["rule"] == rule, oc["direction_witness"]
        w = oc["direction_witness"]
        assert clause[w["clause_start"]:w["clause_end"]] == w["text"]          # the witness is a located span, not a paraphrase


@pytest.mark.parametrize("impl", [vb, co], ids=["verifier", "producer"])
def test_rates_that_contradict_the_convention_leave_the_contrast_unordered(impl):
    """Item C05 of the blind reading: placebo is named first, so ORDER_OF_MENTION says placebo/semaglutide -- and so did the blind
    reader -- but the stated rates (6.6% vs 8.9%) with an estimate of 0.74 can only be semaglutide/placebo. Two witnesses that disagree
    order nothing: UNORDERED, never the convention's guess."""
    c = "The outcome occurred in 8.9% of the placebo group and in 6.6% of the semaglutide group; the hazard ratio was 0.74 (95% CI, 0.58 to 0.95)."
    oc = impl.ordered_contrast(c, [0.74, 0.58, 0.95], VOCAB, None)
    assert oc["state"] == "UNORDERED" and oc["rate_witness"]["state"] == "CONTRADICTS" and "disagree" in oc["reason"]
    agree = "The outcome occurred in 6.6% of the semaglutide group and in 8.9% of the placebo group; the hazard ratio was 0.74 (95% CI, 0.58 to 0.95)."
    ok = impl.ordered_contrast(agree, [0.74, 0.58, 0.95], VOCAB, None)
    assert ok["state"] == "ORDERED" and ok["numerator_side"] == "EXPERIMENTAL" and ok["rate_witness"]["state"] == "AGREES"
    near_null = "In 12.0% of the exenatide group and 12.2% of the placebo group (hazard ratio, 0.98; 95% CI, 0.90 to 1.07)."
    assert impl.ordered_contrast(near_null, [0.98, 0.9, 1.07], VOCAB, None)["rate_witness"]["state"] == "NOT_INFORMATIVE"


def test_the_producer_copy_of_the_rules_is_byte_identical_to_the_verifiers():
    """Two COPIES of one implementation, not two implementations (the independent readings are the blind reader and the AACT route).
    What this pins is that the producer never serves a contrast the verifier would compute differently."""
    v = open(VERIFIER, encoding="utf-8").read()
    p = open(os.path.join(ROOT, "scripts", "contrast_order.py"), encoding="utf-8").read()
    span = v[v.index('RATIO_MEASURES = ("HR", "OR", "RR", "IRR")'):v.index("def contrast_value_check(")].rstrip()
    assert span in p


@pytest.mark.parametrize("impl", [vb, co], ids=["verifier", "producer"])
def test_measure_is_read_from_the_tuples_own_clause(impl):
    assert impl.clause_measure("(hazard ratio, 0.87; 95% CI, 0.78 to 0.97)")["measure"] == "HR"
    assert impl.clause_measure("(HR 0.87, 95% CI 0.78-0.97)")["measure"] == "HR"
    assert impl.clause_measure("(odds ratio 0.8; 95% CI 0.6 to 1.0)")["measure"] == "OR"
    assert impl.clause_measure("(hazard ratio 0.9) and (odds ratio 0.8)")["state"] == "UNRESOLVED"
    assert impl.clause_measure("occurred less often (0.87; 0.78 to 0.97)")["state"] == "UNSTATED"
    assert impl.scale_measure("HR") == "HR" and impl.scale_measure("OR") == "OR" and impl.scale_measure("") is None
    assert impl.scale_measure("OR") != impl.scale_measure("RR")          # OR is not RR: no class mapping in the value check


@pytest.mark.parametrize("impl", [vb, co], ids=["verifier", "producer"])
def test_declared_reciprocal_reproduces_to_printed_precision_and_nothing_else(impl):
    leader = {"estimate": 0.87, "ci_low": 0.78, "ci_high": 0.97}
    recip = {"estimate": 1.1494, "ci_low": 1.0309, "ci_high": 1.2821}           # LEADER 0.87 -> ~1.149, CI -> [1/0.97, 1/0.78]
    assert impl.reciprocal_reproduces(leader, recip) and impl.reciprocal_reproduces(recip, leader)
    assert impl.reciprocal_reproduces({"estimate": 1.15, "ci_low": 1.03, "ci_high": 1.28}, leader)   # printed at 2 dp both sides
    assert not impl.reciprocal_reproduces(leader, {"estimate": 1.1494, "ci_low": 1.2821, "ci_high": 1.0309})   # endpoints not swapped
    assert not impl.reciprocal_reproduces(leader, {"estimate": 1.17, "ci_low": 1.0309, "ci_high": 1.2821})     # off by 0.02
    assert not impl.reciprocal_reproduces(leader, leader)                                                   # a reversal must change the number


def test_served_value_parses_legacy_and_ordered_forms():
    assert vb.served_orientation({"value": "vs placebo (named in the result clause)"}, VOCAB) == "EXPERIMENTAL"
    assert vb.served_orientation({"value": "liraglutide vs placebo"}, VOCAB) == "EXPERIMENTAL"
    assert vb.served_orientation({"value": "placebo vs liraglutide"}, VOCAB) == "REFERENCE"
    assert vb.served_orientation({"value": "GLP-1 RA vs placebo"}, VOCAB) == "EXPERIMENTAL"          # the registered contrast
    # a typed object beside the value is never preferred to it: a value edit cannot hide behind a stale typed field
    assert vb.served_orientation({"value": "placebo vs liraglutide", "ordered_contrast": {"numerator_side": "EXPERIMENTAL"}}, VOCAB) == "REFERENCE"


def test_absent_policy_forbids_a_reversal():
    assert vb.normalisation_policy({}) == "FORBIDDEN" and co.normalisation_policy(None) == "FORBIDDEN"
    assert vb.normalisation_policy({"contrast_normalisation": {"reciprocal_for_ratio_measures": "PERMITTED_WHEN_DECLARED"}}).startswith("PERMITTED")


# ------------------------------------------------------------------------------------------------ 2. the served corpus
def _run(*extra, root="docs", verifier=VERIFIER):
    p = subprocess.run([sys.executable, verifier, "--root", root, "--slug", SLUG, "--json", *extra], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    assert p.stdout.strip(), "verifier produced NO JSON -- a crash, not a verdict: " + p.stderr[-800:]
    return json.loads(p.stdout)


@pytest.fixture(scope="module")
def baseline():
    return _run()


def test_canonical_passes_every_row_orders_and_the_pool_is_one_measure(baseline):
    assert baseline["verdict"] == "PASS", baseline["failures"]
    ocs = baseline["ordered_contrasts"]
    assert len(ocs) == 8
    for pmid, v in ocs.items():
        o = v["recomputed"]
        assert o["state"] == "ORDERED" and o["numerator_side"] == "EXPERIMENTAL", (pmid, o)
        assert o["measure"]["measure"] == "HR" and v["measure"] == "HR" and not v["p10"] and not v["p11"], (pmid, v)
        assert o["experimental_arm"]["arm_ids"] and o["reference_arm"]["arm_ids"], (pmid, o)        # F4 identities carried
        assert o["rate_witness"]["state"] == "AGREES", (pmid, o["rate_witness"])                   # the numeric witness corroborates every row
        assert all(a.startswith(f"{a.split(':')[0]}:") and a.split(":")[0].startswith("NCT") for a in o["experimental_arm"]["arm_ids"])
    leader = ocs[LEADER]["recomputed"]
    assert leader["experimental_arm"]["arm_ids"] == ["NCT01179048:433876840"] and leader["reference_arm"]["arm_ids"] == ["NCT01179048:433876841"]
    assert leader["direction_witness"]["rule"] == "COMPARATIVE_CONNECTIVE" and "than in the placebo" in leader["direction_witness"]["text"]
    g = baseline["pool_measure_guard"]
    assert not g["refused"] and set(g["measures"].values()) == {"HR"}
    assert baseline["pool"]["refused_before_logs"] is None and baseline["pool"]["reproduced_to_1e-9"]


def test_producer_and_verifier_implementations_agree_on_every_served_clause(baseline):
    bundle = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    for r in bundle["verification_rows"]:
        pmid = r["trial"]["id"].replace("PMID ", "")
        served = r["analysis_identity"]["comparator_direction"]
        typed = served.get("ordered_contrast")
        assert typed and typed["state"] == "ORDERED", pmid
        mine = baseline["ordered_contrasts"][pmid]["recomputed"]
        for k in ("numerator_side", "estimate", "ci_low", "ci_high"):
            assert typed[k] == mine[k], (pmid, k)
        assert typed["direction_witness"]["text"] == mine["direction_witness"]["text"]
        assert typed["experimental_arm"]["arm_ids"] == mine["experimental_arm"]["arm_ids"]
        assert served["value"] == co.contrast_value(typed) and "placebo" in served["value"]
        assert served["effect_less_than_1_favours"] == "the experimental arm"
    reg = bundle["registered_estimand"]
    assert reg["contrast"] == "GLP-1 RA vs placebo" and reg["contrast_normalisation"]["reciprocal_for_ratio_measures"] == "FORBIDDEN"
    assert reg["contrast_normalisation"]["registered_in_protocol"] is False          # a harness policy, stated as one


# ------------------------------------------------------------------------------------------------ 3. limbs, through the verifier
LIMBS = {
    # limb: (verdict, LEADER final, codes that must appear in failures)
    "contrast_reverse": ("FAIL", "INADMISSIBLE", ["COMPARATOR_DIRECTION_MISMATCH"]),
    "contrast_reverse_served": ("FAIL", "INADMISSIBLE", ["COMPARATOR_DIRECTION_MISMATCH", "BOUND_TO_UNREGISTERED_ESTIMAND"]),
    "estimator_swap": ("FAIL", "INADMISSIBLE", ["ESTIMATOR_MISMATCH", "BOUND_TO_UNREGISTERED_ESTIMAND", "POOL_MEASURE_MIXED"]),
    "measure_unidentified": ("FAIL", "INADMISSIBLE", ["ESTIMATOR_MISMATCH", "POOL_MEASURE_UNIDENTIFIED"]),
    "pool_input_reciprocal": ("FAIL", "ADMISSIBLE", ["POOL_INPUT_DISAGREES_WITH_ROW"]),
    "contrast_reverse_declared_forbidden": ("FAIL", "INADMISSIBLE", ["CONTRAST_NORMALISATION_NOT_PERMITTED"]),
    "contrast_reverse_declared_permitted": ("PASS", "ADMISSIBLE", []),
    # the served bundle's own policy: the protocol registers no re-orientation, so the producer emits FORBIDDEN (fail closed) and
    # even a correctly declared reciprocal is refused; under an in-memory PERMITTED policy (above) the same limb passes, and a
    # reciprocal AWAY from registration (LEADER 0.87 -> 1.149 pooled as placebo/liraglutide) is refused at P11 whatever the policy
    "contrast_reverse_declared": ("FAIL", "INADMISSIBLE", ["CONTRAST_NORMALISATION_NOT_PERMITTED"]),
    "contrast_reverse_declared_away": ("FAIL", "INADMISSIBLE", ["BOUND_TO_UNREGISTERED_ESTIMAND"]),
}


def _served_digests():
    import hashlib
    out = {}
    for rel in (("docs", "reviews", SLUG, "BUNDLE.json"), ("docs", "cache", SLUG, "records.json"),
                ("docs", "acquisitions", SLUG, "pubmed_efetch_2026-09-19", f"{LEADER}.xml")):
        out[rel] = hashlib.sha256(open(os.path.join(ROOT, *rel), "rb").read()).hexdigest()
    return out


@pytest.mark.parametrize("limb", sorted(LIMBS))
def test_limb_is_refused_for_its_own_code_moves_no_other_row_and_restores(baseline, limb):
    verdict, final, codes = LIMBS[limb]
    before = _served_digests()
    rep = _run("--corrupt", LEADER, limb)
    assert rep["corruption"] == {"pmid": LEADER, "limb": limb}
    row = next(r for r in rep["rows"] if r["pmid"] == LEADER)
    assert rep["verdict"] == verdict, (limb, rep["failures"])
    assert row["final"] == final, (limb, row["final"], row["predicates"])
    for code in codes:
        assert any(f.startswith(code) for f in rep["failures"]), (limb, code, rep["failures"])
    if verdict == "PASS":
        assert not rep["failures"] and rep["ordered_contrasts"][LEADER]["recomputed"]["numerator_side"] == "REFERENCE"
    others_now = {r["pmid"]: (r["final"], r["predicates"]) for r in rep["rows"] if r["pmid"] != LEADER}
    others_base = {r["pmid"]: (r["final"], r["predicates"]) for r in baseline["rows"] if r["pmid"] != LEADER}
    assert others_now == others_base
    assert _served_digests() == before                                  # the corruption lived in memory only
    restored = _run()
    assert restored["verdict"] == "PASS" and next(r for r in restored["rows"] if r["pmid"] == LEADER)["final"] == "ADMISSIBLE"


def test_the_declared_reversal_changes_the_number_the_row_states_and_not_the_pool():
    rep = _run("--corrupt", LEADER, "contrast_reverse_declared_permitted")
    d = rep["ordered_contrasts"][LEADER]
    assert d["recomputed"]["estimate"] == 1.15 and d["detail"]["normalisation"]["operation"] == "RECIPROCAL"
    assert d["pooled"] == {"estimate": 0.87, "ci_low": 0.78, "ci_high": 0.97} and d["detail"]["pooled_numerator_side"] == "EXPERIMENTAL"
    assert rep["pool"]["reproduced_to_1e-9"] is True


# ------------------------------------------------------------------------------------------------ 4. plants before and after
def _prefix_verifier(tmp_path):
    p = subprocess.run(["git", "show", f"{PREFIX_BASE}:scripts/verify_bundle.py"], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)
    if p.returncode != 0:
        pytest.skip(f"the pre-fix verifier blob at {PREFIX_BASE[:8]} is not in this clone's history (shallow clone?) -- NOT a pass")
    out = tmp_path / "verify_bundle_prefix.py"
    out.write_bytes(p.stdout)
    return str(out)


def _bundle_plants():
    """Plants that edit ONLY the served BUNDLE.json (the verification API is not digest-bound; the verifier trusts none of its states)."""
    def row(b):
        return next(r for r in b["verification_rows"] if r["trial"]["id"] == f"PMID {LEADER}")

    def served_reverse(b):
        cd = row(b)["analysis_identity"]["comparator_direction"]
        cd["value"] = "placebo vs liraglutide"
        cd.pop("ordered_contrast", None)                  # the typed object removed too: the VALUE alone must be read

    def estimator_swap(b):
        r = row(b)
        r["effect"]["scale"] = "OR"
        r["analysis_identity"]["estimator"]["value"] = "odds ratio"

    def unidentified(b):
        row(b)["effect"]["scale"] = None

    def pool_reciprocal(b):
        i = next(x for x in b["pooled_reference"]["inputs"] if x["id"] == f"PMID {LEADER}")
        i.update(effect=round(1 / 0.87, 4), ci_low=round(1 / 0.97, 4), ci_high=round(1 / 0.78, 4))
        b["pooled_reference"]["expected"] = {k: v for k, v in vb.pool(b["pooled_reference"]["inputs"]).items()}
    def effect_copy(b):                                    # the F4 lane's warning: the bundle copy edited, review.json untouched
        row(b)["effect"]["estimate"] = 0.99
    return {"served_contrast_reverse": (served_reverse, "COMPARATOR_DIRECTION_MISMATCH"),
            "served_effect_copy_edited": (effect_copy, "ROW_EFFECT_COPIES_DISAGREE"),
            "served_estimator_swap": (estimator_swap, "ESTIMATOR_MISMATCH"),
            "served_measure_unidentified": (unidentified, "POOL_MEASURE_UNIDENTIFIED"),
            "served_pool_input_reciprocal": (pool_reciprocal, "POOL_INPUT_DISAGREES_WITH_ROW")}


@pytest.fixture(scope="module")
def served_copy(tmp_path_factory):
    bundle = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    root = tmp_path_factory.mktemp("oc_site")
    paths = {a["served_path"] for a in bundle["artefacts"] if a["state"] == "SERVED"}
    paths |= {f["path"].removeprefix("docs/") for f in bundle["supporting_files"]}
    paths |= {r["served_path"] for r in bundle["review_files"]} | {f"reviews/{SLUG}/BUNDLE.json", f"topics/{SLUG}.json"}
    for p in paths:
        out = root.joinpath(*p.split("/"))
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, "docs", *p.split("/")), out)
    yield str(root), bundle
    shutil.rmtree(root, ignore_errors=True)


@pytest.mark.parametrize("plant", sorted(_bundle_plants()))
def test_plant_passed_the_prefix_verifier_and_is_refused_now(served_copy, tmp_path, plant):
    root, bundle = served_copy
    edit, code = _bundle_plants()[plant]
    b = copy.deepcopy(bundle)
    edit(b)
    target = os.path.join(root, "reviews", SLUG, "BUNDLE.json")
    try:
        with open(target, "w", encoding="utf-8") as f:
            json.dump(b, f, ensure_ascii=False, indent=1)
        before = _run(root=root, verifier=_prefix_verifier(tmp_path))
        now = _run(root=root)
    finally:
        with open(target, "w", encoding="utf-8") as f:     # restore the canonical copy for the next plant
            json.dump(bundle, f, ensure_ascii=False, indent=1)
    assert before["verdict"] == "PASS", (plant, "the plant must be INVISIBLE to the pre-fix verifier, else it proves nothing", before["failures"])
    assert now["verdict"] == "FAIL" and any(f.startswith(code) for f in now["failures"]), (plant, now["failures"])
    restored = _run(root=root)
    assert restored["verdict"] == "PASS", restored["failures"]


# ------------------------------------------------------------------------------------------------ 5. the producer leg
@pytest.fixture(scope="module")
def producer_planted():
    """build_bundle.build() -- the real producer -- on planted INPUTS (LEADER's held record reversed in memory; LEADER's rendered row
    relabelled OR). The producer's admission object is the gate the bundle records; it must refuse, for the planted reason."""
    import build_bundle as bb
    real = bb._read_json
    held = vb._OC_LEADER_HELD

    def planted(path):
        obj = real(path)
        p = str(path).replace("\\", "/")
        if p.endswith(f"cache/{SLUG}/records.json"):
            obj = copy.deepcopy(obj)
            r = next(x for x in obj["records"] if str(x["id"]) == LEADER)
            r["abstract"] = r["abstract"].replace(held, vb._OC_LEADER_SWAPPED)
        elif p.endswith(f"reviews/{SLUG}/review.json"):
            obj = copy.deepcopy(obj)
            for o in obj["outcomes"]:
                if o.get("primary"):
                    for t in o["trials"]:
                        if str(t["id"]).endswith(LEADER):
                            t["endpoint_result_span"] = t["endpoint_result_span"].replace(held, vb._OC_LEADER_SWAPPED)
                        if str(t["id"]).endswith("40162642"):
                            t["scale"] = "OR"                     # the estimator plant rides on a second row (SELECT)
        return obj
    bb._read_json = planted
    try:
        bundle, problems = bb.build(SLUG, check_only=True)
    finally:
        bb._read_json = real
    return {r["trial"]["id"].replace("PMID ", ""): r for r in bundle["verification_rows"]}


def test_producer_refuses_the_reversed_source_at_its_own_admission(producer_planted):
    r = producer_planted[LEADER]
    oc = r["analysis_identity"]["comparator_direction"]["ordered_contrast"]
    assert oc["numerator_side"] == "REFERENCE" and oc["direction_witness"]["rule"] == "COMPARATIVE_CONNECTIVE"
    p11 = r["admission"]["predicates"]["P11_registered_estimand"]
    assert p11["state"] == "FAIL" and any(d[0] == "contrast" for d in p11["departures"]), p11
    assert r["admission"]["final"] == "INADMISSIBLE"


def test_producer_refuses_the_relabelled_estimator_and_admits_the_untouched_rows(producer_planted):
    r = producer_planted["40162642"]
    p11 = r["admission"]["predicates"]["P11_registered_estimand"]
    assert p11["state"] == "FAIL" and any(d[0] == "estimator" for d in p11["departures"]) and r["admission"]["final"] == "INADMISSIBLE"
    untouched = [p for p in producer_planted if p not in (LEADER, "40162642", "30291013")]   # HARMONY is refused at baseline (P5)
    assert len(untouched) == 5 and all(producer_planted[p]["admission"]["final"] == "ADMISSIBLE" for p in untouched)


def test_a_contrast_refusal_the_bundle_already_discloses_is_reported_not_a_second_defect(served_copy):
    """F4 lane's constraint: admission is computed and disclosed; it must not by itself refuse publication. The same contrast defect
    as served_contrast_reverse, but the bundle RECORDS the row INADMISSIBLE: the verifier refuses the row (it is never admitted) and
    lists the code under disclosed_refusals, and the verdict does not fail on a refusal nobody hid."""
    root, bundle = served_copy
    b = copy.deepcopy(bundle)
    r = next(x for x in b["verification_rows"] if x["trial"]["id"] == f"PMID {LEADER}")
    r["analysis_identity"]["comparator_direction"]["value"] = "placebo vs liraglutide"
    r["analysis_identity"]["comparator_direction"].pop("ordered_contrast", None)
    r["admission"]["final"] = "INADMISSIBLE"
    for k in ("P10_estimand_evidence", "P11_registered_estimand"):
        if k in r["admission"]["predicates"]:
            r["admission"]["predicates"][k]["state"] = "FAIL"
    target = os.path.join(root, "reviews", SLUG, "BUNDLE.json")
    try:
        with open(target, "w", encoding="utf-8") as f:
            json.dump(b, f, ensure_ascii=False, indent=1)
        rep = _run(root=root)
    finally:
        with open(target, "w", encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False, indent=1)
    row = next(x for x in rep["rows"] if x["pmid"] == LEADER)
    assert row["final"] == "INADMISSIBLE" and row["agrees_with_bundle"] is True
    assert any(d.startswith("COMPARATOR_DIRECTION_MISMATCH") for d in rep["disclosed_refusals"])
    assert not any(f.startswith("COMPARATOR_DIRECTION_MISMATCH") for f in rep["failures"]), rep["failures"]
