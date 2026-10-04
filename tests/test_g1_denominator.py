"""The G1 denominator can only shrink with a typed, spanned reason (dispatch 2026-10-04).

outputs/k_gap/G1_DENOMINATOR.json (scripts/g1_denominator_ledger.py) lists every comparator row that left the pinned
367-row baseline (docs/evidence/g1-denominator/baseline-6efd9c00.json) with kind, rule ID and a span copied verbatim from
a held source (sha256 recorded), and every row that joined. These tests close the population: a row that leaves the
tracker WITHOUT a ledger record, a record without rule or span, a span not in its source, or arithmetic that does not
close, fails -- the plant builds each of those and the check must refuse it."""
import copy
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_denominator_ledger as dl  # noqa: E402

LED = json.load(open(dl.LEDGER, encoding="utf-8"))
BASE = json.load(open(dl.BASE, encoding="utf-8"))


def _current():
    out = {}
    for p in glob.glob(os.path.join(ROOT, "outputs", "k_gap", "g1", "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        out[d["slug"]] = d
    return out


def test_every_removal_has_a_rule_and_a_span_found_in_its_held_source():
    assert dl.problems(LED) == []


def test_the_ledger_covers_every_row_that_left_and_every_row_that_joined():
    cur = _current()
    left, joined = set(), set()
    for slug, b in BASE["topics"].items():
        now = {t["label"] for t in (cur.get(slug) or {}).get("trials") or []}
        left |= {(slug, l) for l in b["rows"] if l not in now}
        joined |= {(slug, l) for l in now if l not in b["rows"]}
    recorded = {(r["slug"], r["label"]) for r in LED["removed"]}
    relabels = {(r["slug"], r["now_label"]) for r in LED["removed"] if r["kind"] == "RELABELLED"}
    assert left == recorded, sorted(left ^ recorded)
    assert joined == {(a["slug"], a["label"]) for a in LED["added"]} | relabels
    assert LED["current"]["N"] == sum(d["N_comparator_trials"] for d in cur.values())
    assert LED["baseline"]["N"] == BASE["N"] == 367


def test_PLANT_an_unexplained_or_unspanned_removal_is_refused():
    r0 = next(r for r in LED["removed"] if r["kind"] == "NOT_A_TRIAL")
    for mutate, why in ((lambda r: r.update(rule_id=None), "no rule"),
                        (lambda r: r.update(kind="UNEXPLAINED"), "no rule"),
                        (lambda r: r.update(span=None), "no span"),
                        (lambda r: r["span"].update(text="Gitsels et al. 2016 enrolled 4 million patients"), "not in its source"),
                        (lambda r: r["span"].update(source_sha256="0" * 64), "changed")):
        led = copy.deepcopy(LED)
        r = next(x for x in led["removed"] if x["label"] == r0["label"] and x["slug"] == r0["slug"])
        mutate(r)
        assert any(why in p for p in dl.problems(led)), why


def test_PLANT_arithmetic_that_does_not_close_is_refused():
    led = copy.deepcopy(LED)
    led["removed_n"] += 1
    assert any(p.startswith("arithmetic") for p in dl.problems(led))


def test_the_denominator_reasons_are_the_ones_audited():
    kinds = {}
    for r in LED["removed"]:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    assert kinds == {"NOT_A_TRIAL": 15, "DUPLICATE_UNIT": 1, "OTHER_AGENT": 1, "NOT_IN_COMPARATOR_TABLE": 2, "RELABELLED": 1}
    smart = next(r for r in LED["removed"] if r["kind"] == "DUPLICATE_UNIT")
    assert smart["label"] == "Semler [15]" and smart["duplicate_of"] == "Semler (SMART trial)"
    assert "29485925" in smart["identity"]["pmids"]
    emp = next(r for r in LED["removed"] if r["kind"] == "OTHER_AGENT")
    assert "Empagliflozin" in emp["span"]["text"] and emp["slug"] == "dapagliflozin-hfpef-hosp"


def test_the_tracker_artefact_itself_carries_every_removal_with_rule_and_span():
    assert dl.tracker_problems(LED) == []
    src = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "G1_SOURCE.json"), encoding="utf-8"))
    assert src["denominator"]["baseline_N"] == 367 and src["denominator"]["current_N"] == LED["current"]["N"]
    assert src["denominator"]["by_kind"]["NOT_A_TRIAL"] == 15


def test_PLANT_a_tracker_removal_without_rule_or_span_is_refused(tmp_path, monkeypatch):
    import shutil
    d = tmp_path / "outputs" / "k_gap" / "g1"
    shutil.copytree(os.path.join(ROOT, "outputs", "k_gap", "g1"), d)
    p = d / "statins-primary-prevention-elderly.json"
    o = json.load(open(p, encoding="utf-8"))
    o["removed_comparator_rows"][0]["span"] = None
    p.write_text(json.dumps(o), encoding="utf-8")
    monkeypatch.setattr(dl, "OUT", str(tmp_path / "outputs" / "k_gap"))
    assert any("without rule + span" in x for x in dl.tracker_problems(LED))
    o["removed_comparator_rows"] = o["removed_comparator_rows"][1:]           # a removal missing from the tracker
    p.write_text(json.dumps(o), encoding="utf-8")
    assert any("differ from the ledger" in x for x in dl.tracker_problems(LED))
