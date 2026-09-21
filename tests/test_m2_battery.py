"""M2 battery as a repo test: counterexamples through the real ROUTE TO THE POOL, in process.

The same 28 cases as scripts/m2_battery.py (which runs them through build_topic + the gate, ~3.3 min each, and
writes M2_RESULTS_battery.md), here on the real inputs the core assembles (pipeline.outcome_inputs) with the
primary outcome built by the real _build_outcome, so the gate's unit-test limb re-checks the only property that
matters every time: a hand number is pooled when it BINDS to held bytes, is set aside or refused under the NAMED
code when it does not, and a valid positive is never refused.

Every case keeps the paired shape: the CONTROL (the committed inputs) admits -> ONE input changes -> the changed
row is refused for the named reason with the trial still visible -> the exact inputs restored admit again and
give the control's pool. Cases assert a property and a code, never a number or a message string.

Known misses are strict xfails, named: W4a/W4b (an excluded component treated as included: the layer-1 exclusion
relation, not this object) and W2a/W5b (a canonical span absent from the held document: refused at LOAD for the
whole topic -- right check, wrong scope -- asserted as such so the day it becomes a row refusal is visible).
"""
import copy
import json
import os
import re
import shutil

import pytest

from harness import fetch, hand_binding, pipeline, verified_inputs

SLUG = "glp1-ra-mace-t2d"
PRIMARY = "3-point major adverse cardiovascular events"
SOUL, LEADER, SUSTAIN6, EXSCEL, ELIXA = "40162642", "27295427", "27633186", "28910237", "26630143"
ROOT = pipeline.ROOT
CACHE = os.path.join(ROOT, "cache", SLUG)
COPIED = ("records.json", "verified_effects.json", "verified_arms.json", "comparators.json")

SOUL_RESULT = ("a primary-outcome event occurred in 579 of the 4825 participants (12.0%) in the oral semaglutide "
               "group, as compared with 668 of the 4825 participants (13.8%) in the placebo group (hazard ratio, "
               "0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006)")
ELIXA_HF = ("There were no significant between-group differences in the rate of hospitalization for heart failure "
            "(hazard ratio in the lixisenatide group, 0.96; 95% CI, 0.75 to 1.23)")
ELIXA_DEF = ("for the primary composite end point of cardiovascular death, myocardial infarction, stroke, or "
             "hospitalization for unstable angina")


# ----------------------------------------------------------------------------- the real inputs, once
@pytest.fixture(scope="module")
def inputs():
    config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    records = fetch.ensure(config, "")            # committed cache: no network
    inp = pipeline.outcome_inputs(SLUG, config, records)
    spec = next(s for s, k in pipeline._outcome_specs(config) if s.get("name") == PRIMARY)
    return inp, spec


@pytest.fixture
def lane(tmp_path):
    """A private copy of the held documents the binder reads; ROOT-relative refs resolve into it."""
    root = tmp_path / "lane"
    d = root / "cache" / SLUG
    d.mkdir(parents=True)
    for name in os.listdir(CACHE):
        if name in COPIED or re.match(r"(ft_\d+|pmc_\d+_fulltext)\.txt$", name):
            shutil.copyfile(os.path.join(CACHE, name), d / name)
    # every document a committed hand entry names (some sit outside cache/<slug>, e.g. a held regulatory review)
    for name in ("verified_effects.json", "verified_arms.json"):
        data = json.load(open(os.path.join(CACHE, name), encoding="utf-8"))
        for entries in data.values():
            for e in (entries if isinstance(entries, list) else [entries]):
                ref = str(e.get("document_ref") or "").split("#")[0]
                src = os.path.join(ROOT, ref) if ref else ""
                if ref and os.path.isfile(src) and not (root / ref).exists():
                    (root / ref).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, root / ref)
    return root


def _build(inp, spec, root, rec_by_id=None):
    """The primary outcome from the lane's verified inputs (validated exactly as the real loader does)."""
    veffs = verified_inputs.load(SLUG, cache_root=os.path.join(root, "cache"))["verified_effects.json"] or None
    old = hand_binding.ROOT, pipeline.ROOT
    hand_binding.ROOT = pipeline.ROOT = str(root)
    try:
        return pipeline.build_outcome_from_inputs(inp, spec, "efficacy", SLUG, veffs=veffs,
                                                  rec_by_id=rec_by_id if rec_by_id is not None else inp["rec_by_id"])
    finally:
        hand_binding.ROOT, pipeline.ROOT = old


def _pool(outcome):
    return {t["id"].replace("PMID ", ""): (t.get("endpoint_admissibility"), t.get("hand_binding_state"))
            for t in outcome.get("trials") or []}


def _absent(outcome, pid):
    return next((a for a in outcome.get("declared_absent_trials") or [] if a["id"].replace("PMID ", "") == pid), None)


# ----------------------------------------------------------------------------- input edits (one per case)
def _ve(root):
    return json.load(open(root / "cache" / SLUG / "verified_effects.json", encoding="utf-8"))


def _save_ve(root, d):
    json.dump(d, open(root / "cache" / SLUG / "verified_effects.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)


def set_entry(d, pid, entry):
    """Replace/add the entry for entry['outcome'] on trial pid, keeping the trial's OTHER outcome entries."""
    cur = d.get(pid)
    items = [] if cur is None else (cur if isinstance(cur, list) else [cur])
    items = [x for x in items if x.get("outcome") != entry["outcome"]] + [entry]
    d[pid] = items if len(items) > 1 else items[0]


def primary_entry(d, pid):
    cur = d[pid]
    items = cur if isinstance(cur, list) else [cur]
    return next(x for x in items if x.get("outcome") == PRIMARY)


def edit_ve(root, fn):
    d = _ve(root)
    fn(d)
    _save_ve(root, d)


def edit_abstract(root, inp, pid, old, new):
    """Change ONE held abstract in the lane (file + the records the abstract route reads)."""
    p = root / "cache" / SLUG / "records.json"
    data = json.load(open(p, encoding="utf-8"))
    rec = next(r for r in data["records"] if r["id"] == pid)
    assert rec["abstract"].count(old) == 1, (pid, old[:50])
    rec["abstract"] = rec["abstract"].replace(old, new)
    json.dump(data, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    rec_by_id = copy.deepcopy(inp["rec_by_id"])
    rec_by_id[pid]["abstract"] = rec_by_id[pid]["abstract"].replace(old, new)
    return rec_by_id


def leader_ft():
    return open(os.path.join(CACHE, f"ft_{LEADER}.txt"), encoding="utf-8").read()


def leader_row(prefix):
    t = leader_ft()
    i = t.find(prefix)
    assert i > 0, prefix
    return t[t.rfind("<tr>", 0, i):t.find("</tr>", i) + 5]


def leader_mace_prose():
    t = leader_ft()
    j = t.find("The primary composite outcome occurred in fewer patients in the liraglutide group")
    return t[j:t.find("for superiority)", j) + len("for superiority)")]


def leader_entry(effect, lo, hi, span, **extra):
    d = {"outcome": PRIMARY, "effect": effect, "ci_low": lo, "ci_high": hi, "scale": "HR",
         "kind": "extracted_effect", "override": True, "source_level": 1,
         "document_ref": f"cache/{SLUG}/ft_{LEADER}.txt", "source_span": span,
         "verification": "LEADER Table 1 / results prose, hand-transcribed (M2 battery)"}
    d.update(extra)
    return d


# id, changed trial, expected code (None = load-time raise), the edit, notes
ATTACKS = [
    ("W1a", SOUL, "ENDPOINT_UNBOUND", lambda r, i: edit_ve(r, lambda d: primary_entry(d, SOUL).update(ci_high=0.98)),
     "wrong interval, source unchanged"),
    ("W1b", SOUL, "ENDPOINT_UNBOUND", lambda r, i: edit_ve(r, lambda d: primary_entry(d, SOUL).update(scale="OR")),
     "wrong effect measure: the held abstract says hazard ratio"),
    ("W1c", SOUL, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: primary_entry(d, SOUL).update(effect=0.68)),
     "point outside its own interval, source string unchanged"),
    ("W1d", SOUL, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: primary_entry(d, SOUL).update(
        effect=0.68, source=primary_entry(d, SOUL)["source"].replace("hazard ratio, 0.86;", "hazard ratio, 0.68;"))),
     "coherent lie: effect AND the hand-written source say 0.68"),
    ("W1e", SOUL, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: primary_entry(d, SOUL).update(
        effect=0.14, source=primary_entry(d, SOUL)["source"].replace("hazard ratio, 0.86;", "hazard ratio, 0.14;"))),
     "RR complement 1-0.86"),
    ("W2b", EXSCEL, "ENDPOINT_UNBOUND", lambda r, i: edit_ve(r, lambda d: set_entry(d, EXSCEL, dict(
        copy.deepcopy(primary_entry(d, SOUL)), override=True, verification="filed under EXSCEL: the digits are SOUL's"))),
     "SOUL's digits filed as an override under EXSCEL"),
    ("W3a", LEADER, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.86, 0.73, 1.00, leader_row("0.86 (0.73")))), "MI-only table row claimed as 3-point MACE"),
    ("W3b", ELIXA, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: set_entry(d, ELIXA, {
        "outcome": PRIMARY, "effect": 0.96, "ci_low": 0.75, "ci_high": 1.23, "scale": "HR",
        "source": "ELIXA (PMID 26630143) abstract: " + ELIXA_HF, "verification": "abstract sentence; claimed as MACE"})),
     "HF-hospitalisation HR claimed as 3-point MACE"),
    ("W5a", SOUL, "ENDPOINT_UNBOUND", lambda r, i: edit_abstract(r, i, SOUL,
        "(hazard ratio, 0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006)",
        "(hazard ratio, 0.88; 95% confidence interval, 0.79 to 0.98; P = 0.006)"),
     "stale approval: the held abstract was corrected after the entry was approved"),
    ("L1", LEADER, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.86, 0.73, 1.00, leader_row("0.86 (0.73")))), "LEADER MI row as MACE"),
    ("L2", LEADER, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.86, 0.71, 1.06, leader_row("0.86 (0.71")))), "LEADER stroke row as MACE"),
    ("L3", LEADER, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.88, 0.81, 0.96, leader_row("0.88 (0.81")))), "LEADER expanded composite as 3-point MACE"),
    ("L4", LEADER, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.78, 0.66, 0.93, leader_row("0.78 (0.66")))), "LEADER CV death as MACE"),
    ("L5", LEADER, "ENDPOINT_UNBOUND", lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        1.15, 1.03, 1.28, leader_mace_prose(), comparator_direction="placebo vs liraglutide"))),
     "inverted tuple: not in the held document"),
    ("L6", LEADER, "RESULT_INCOMPATIBLE", lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.87, 0.78, 0.97, leader_row("0.87 (0.78"), comparator_direction="placebo vs liraglutide"))),
     "declared direction contradicts the column headers"),
    ("L7", LEADER, "ENDPOINT_UNBOUND", lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.87, 0.78, 0.97, leader_mace_prose(), analysis_set="per-protocol"))),
     "declared analysis set is not the held analysis"),
    ("L9", LEADER, "ENDPOINT_UNBOUND", lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.86, None, None, _leader_table1()))), "point only over the whole Table 1: two owners -> abstain"),
]


def _leader_table1():
    t = leader_ft()
    i = t.find("0.87 (0.78")
    return t[t.rfind("<table-wrap", 0, i):t.find("</table-wrap>", i) + len("</table-wrap>")]


POSITIVES = [
    ("P1", SOUL, None, "control: the served inputs"),
    ("P2", SOUL, lambda r, i: edit_abstract(r, i, SOUL,
        "(hazard ratio, 0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006)",
        "(hazard ratio, 0·86; 95% confidence interval, 0·77 to 0·96; P = 0.006)"),
     "representation variant: Lancet middle-dot decimals"),
    ("P3", LEADER, lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.87, 0.78, 0.97, leader_mace_prose()))), "legitimate full-text prose override"),
    ("P4", SOUL, lambda r, i: edit_ve(r, lambda d: primary_entry(d, SOUL).update(
        kind="extracted_effect", source_span=SOUL_RESULT, document_ref=f"cache/{SLUG}/records.json", source_level=1)),
     "canonical hand entry: verbatim span + document_ref"),
    ("L0", LEADER, lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.87, 0.78, 0.97, leader_row("0.87 (0.78")))), "Table 1 primary row: bound through label + column headers"),
    ("L8", LEADER, lambda r, i: edit_ve(r, lambda d: set_entry(d, LEADER, leader_entry(
        0.87, 0.78, 0.97, leader_row("0.87 (0.78"), ci_pct=95, scale="HR",
        normalisation="en dash -> hyphen; 'Hazard Ratio (95% CI)' column header -> HR"))),
     "declared harmless normalisation"),
]


# ----------------------------------------------------------------------------- the paired shape
def _control(inp, spec, lane):
    out = _build(inp, spec, lane)
    pool = _pool(out)
    assert pool[SOUL] == ("EXACT_TARGET", "BOUND") and LEADER in pool and EXSCEL in pool, pool
    return pool


@pytest.mark.parametrize(("cid", "trial", "code", "edit", "why"), ATTACKS, ids=[a[0] for a in ATTACKS])
def test_attack_is_refused_for_the_named_reason_and_the_restored_inputs_admit(inputs, lane, cid, trial, code, edit, why):
    inp, spec = inputs
    control = _control(inp, spec, lane)                       # 1. the committed inputs admit
    rec_by_id = edit(lane, inp)                               # 2. ONE input changes
    out = _build(inp, spec, lane, rec_by_id)
    assert trial not in _pool(out), f"{cid} ({why}): the changed row was POOLED"
    absent = _absent(out, trial)
    assert absent is not None, f"{cid}: the trial vanished instead of staying visible as set aside / refused"
    assert absent.get("reason_code") == code, (cid, absent.get("reason_code"), absent.get("reason"))
    # 3. exact restoration admits and gives the control's pool
    for name in COPIED:
        shutil.copyfile(os.path.join(CACHE, name), lane / "cache" / SLUG / name)
    assert _pool(_build(inp, spec, lane)) == control, f"{cid}: restored inputs did not give the control's pool"


@pytest.mark.parametrize(("cid", "trial", "edit", "why"), POSITIVES, ids=[p[0] for p in POSITIVES])
def test_positive_is_admitted_and_bound(inputs, lane, cid, trial, edit, why):
    """A suite that only tests attacks ratchets toward refusing everything: every positive is mandatory."""
    inp, spec = inputs
    rec_by_id = edit(lane, inp) if edit else None
    out = _build(inp, spec, lane, rec_by_id)
    pool = _pool(out)
    assert trial in pool, f"{cid} ({why}): a valid positive was REFUSED: {_absent(out, trial)}"
    assert pool[trial] == ("EXACT_TARGET", "BOUND"), (cid, pool[trial])


def test_P5_documented_decision_is_recorded_as_such(inputs, lane):
    inp, spec = inputs
    edit_ve(lane, lambda d: set_entry(d, ELIXA, {
        "outcome": PRIMARY, "kind": "typed_refusal", "provenance": "REFUSED_ON_EVIDENCE",
        "document_ref": f"cache/{SLUG}/records.json", "source_span": ELIXA_DEF, "source_level": 1,
        "reason": "ELIXA's primary composite is 4-point (adds hospitalization for unstable angina); the 3-point "
                  "MACE is not reported in the held abstract -- documented decision, reviewer M.A., 2026-09-20"}))
    out = _build(inp, spec, lane)
    absent = _absent(out, ELIXA)
    assert ELIXA not in _pool(out) and absent is not None
    assert absent.get("absent_kind") == "adjudicated_absent" and absent.get("reason"), absent


# ----------------------------------------------------------------------------- named misses, strict
@pytest.mark.xfail(strict=True, reason="W2a: a canonical span absent from the named document is refused at LOAD "
                                       "for the whole topic (right check, wrong scope; design note section 3)")
def test_W2a_wrong_document_is_a_row_refusal_not_a_whole_topic_refusal(inputs, lane):
    inp, spec = inputs
    edit_ve(lane, lambda d: primary_entry(d, SOUL).update(kind="extracted_effect", source_span=SOUL_RESULT,
                                                          document_ref=f"cache/{SLUG}/ft_{LEADER}.txt", source_level=1))
    out = _build(inp, spec, lane)      # today: ValueError('... source_span absent from held document ...')
    assert SOUL not in _pool(out) and _absent(out, SOUL) is not None


@pytest.mark.xfail(strict=True, reason="W5b: same erratum with a canonical span: refused at LOAD, whole topic")
def test_W5b_stale_canonical_span_is_a_row_refusal_not_a_whole_topic_refusal(inputs, lane):
    inp, spec = inputs
    rec_by_id = edit_abstract(lane, inp, SOUL, "(hazard ratio, 0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006)",
                              "(hazard ratio, 0.88; 95% confidence interval, 0.79 to 0.98; P = 0.006)")
    edit_ve(lane, lambda d: primary_entry(d, SOUL).update(kind="extracted_effect", source_span=SOUL_RESULT,
                                                          document_ref=f"cache/{SLUG}/records.json", source_level=1))
    out = _build(inp, spec, lane, rec_by_id)
    assert SOUL not in _pool(out) and _absent(out, SOUL) is not None


def test_W2a_and_W5b_refuse_at_load_today():
    """The current (wrong-scope) behaviour, asserted so a change of scope is visible in both directions."""
    with pytest.raises(ValueError, match="source_span absent"):
        verified_inputs._validate(verified_inputs.normalise({
            "outcome": PRIMARY, "effect": 0.86, "ci_low": 0.77, "ci_high": 0.96, "scale": "HR",
            "kind": "extracted_effect", "source_span": SOUL_RESULT, "document_ref": f"cache/{SLUG}/ft_{LEADER}.txt",
            "source_level": 1}), __import__("pathlib").Path(CACHE), SOUL, canonical=True)


@pytest.mark.xfail(strict=True, reason="W4a: an excluded component treated as included -- the layer-1 exclusion "
                                       "relation, not the hand-row object")
def test_W4a_exclusion_stated_in_the_held_abstract_refuses_the_hand_row(inputs, lane):
    inp, spec = inputs
    rec_by_id = edit_abstract(lane, inp, SOUL,
        "(a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke)",
        "(a composite of death from cardiovascular causes or nonfatal myocardial infarction; nonfatal stroke was "
        "excluded from the primary outcome)")
    out = _build(inp, spec, lane, rec_by_id)
    assert SOUL not in _pool(out)


@pytest.mark.xfail(strict=True, reason="W4b: the same exclusion on the machine (abstract) route")
def test_W4b_exclusion_stated_in_the_held_abstract_refuses_the_abstract_row(inputs, lane):
    inp, spec = inputs
    rec_by_id = edit_abstract(lane, inp, SUSTAIN6,
        "The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial "
        "infarction, or nonfatal stroke.",
        "The primary composite outcome was the first occurrence of cardiovascular death or nonfatal myocardial "
        "infarction; nonfatal stroke was excluded from the primary composite outcome.")
    out = _build(inp, spec, lane, rec_by_id)
    assert SUSTAIN6 not in _pool(out)
