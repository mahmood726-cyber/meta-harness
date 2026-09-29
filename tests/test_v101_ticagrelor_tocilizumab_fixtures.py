"""V1.0.1 round 8 (ticagrelor-ACS and tocilizumab-COVID reviews). Plants are synthetic or held records; the served
checks read the committed pages.

Ticagrelor: D5 is identity -> timing -> judgment (PLATO's CV composite no longer 'matches' bleeding; PHILO's
registered MACE is found); Tan 2017 pools PLATO twice (Cannon 2010's 13,408 inside Wallentin 2009's 18,624).
Tocilizumab: 'standard-of-care (SOC)' is a comparator; REACT states 27 IL-6 trials and 19 tocilizumab; membership is
never decided by a publication date; REACT's tocilizumab fixed effect reproduces exactly."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from harness import comparator_nesting as cn
from harness import date_membership as dm
from harness import positive_control as pc
from harness import rob2
from harness import screen
from harness import term_normal as tn

ROOT = Path(__file__).resolve().parents[1]
TICA, TOCI = "ticagrelor-vs-clopidogrel-acs", "tocilizumab-covid19-mortality"
POOLED = "Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke"


def _review(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def test_d5_bleeding_never_matches_a_cv_composite_and_vascular_death_is_cv_death():
    assert rob2._component_set("Participants With Non-CABG Related Major Bleeding") == {"BLEEDING"}
    assert rob2._component_set("death from vascular causes, MI and stroke") == {"CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"}
    # ASCEND's serious vascular event includes TIA: not 3-point MACE
    assert "TIA" in rob2._component_set("vascular death, MI, stroke or transient ischaemic attack")


def test_d5_served_identity_chain_never_auto_low():
    r = _review(TICA)
    for tid, label in (("19717846", "Death From Vascular Causes"), ("26376600", "Major Adverse Cardiac Events")):
        d5 = r["rob2"]["trials"][tid]["domains"]["D5_selective_reporting"]
        assert d5["level"] == "not assessed" and label in d5["inputs"]["comparison"]["registered_label"]
        assert d5["inputs"]["chain"]["timing"] == "NOT_ASSESSED" and d5["inputs"]["chain"]["judgment"] == "NOT_MADE"
    for p in (ROOT / "cache").glob("*/rob2.json"):
        for t in json.loads(p.read_text(encoding="utf-8"))["trials"].values():
            assert t["domains"]["D5_selective_reporting"]["level"] != "low", p


def test_tan_2017_counts_plato_twice_and_is_not_a_benchmark():
    n = _review(TICA)["comparator"]["nesting"]
    assert (n["state"], n["report_overlap"], n["trial_overlap"], n["shared_registrations"]) == \
        ("DUPLICATED_POPULATION", 2, 1, ["NCT00391872"])
    x = n["nested"][0]
    assert (x["row"]["label"], x["parent"]["label"], x["duplicated_participants"]) == ("Cannon 2010", "Wallentin 2009", 13408)
    assert x["proof"]["quote"] == "13 408 (72.0%) of 18 624"


def test_standard_of_care_hyphenated_and_abbreviated_is_a_comparator_but_other_abbreviations_are_not_expanded():
    t = "tocilizumab plus standard-of-care (SOC) or SOC alone; patients without AAD as the control group (AAD)"
    out = tn.comparator_text(t, ["standard of care", "control"])
    assert "standard of care alone" in out and "without AAD as the control" in out
    recs = json.loads((ROOT / "cache" / TOCI / "records.json").read_text(encoding="utf-8"))
    rec = next(r for r in recs["records"] if str(r.get("id")) == "38485912")
    cfg = dict(json.loads((ROOT / "topics" / f"{TOCI}.json").read_text(encoding="utf-8")), slug="plant-no-protocol")
    assert screen.run([dict(rec)], cfg)["decisions"][0]["decision"] == "include"


def test_talaschian_now_included_adds_no_mortality_input():
    r = _review(TOCI)
    row = next(x for x in r["screening"]["records"] if x["id"].endswith("38485912"))
    assert row["decision"] == "include"
    prim = next(o for o in r["outcomes"] if o.get("primary"))
    assert all("38485912" not in str(t.get("id")) for t in prim["trials"])


def test_react_counts_and_date_rule():
    a = _review(TOCI)["comparator"]["analysis"]
    assert (a["stated_counts"]["class_k"]["value"], a["stated_counts"]["drug_k"]["value"]) == (27, 19)
    notes = {x["row"]: x["state"] for x in a["row_notes"]}
    assert notes == {"PreToVid": "TIMEPOINT_EXCEPTION", "ImmCoVA": "ALREADY_ANALYSED"}
    assert dm.claims("IMMCoVA is a new trial not in the comparator because it was published after the review.")
    assert not dm.claims("Publication year is never used to decide membership: a paper can post-date a comparator.")


def test_react_tocilizumab_fixed_effect_reproduces_exactly():
    c = next(x for x in pc.load(ROOT) if x["id"] == "react-2021-tocilizumab-28d-mortality")
    got = pc.reproduce(c, ROOT)
    assert got["k"] == 16 and pc.compare(c, got) == []


def test_round8_plants_fire_on_the_pre_fix_harness_and_not_on_this_one():
    rec = json.loads((ROOT / "evidence" / "v101_integrated" / "round8_plants.json").read_text(encoding="utf-8"))
    assert rec["pre_fix"]["fired"] == rec["pre_fix"]["of"] == 7
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "plants_round8.py"), "--harness-root", str(ROOT)],
                         capture_output=True, text=True, encoding="utf-8", timeout=900)
    lines = [l for l in out.stdout.splitlines() if l.startswith(("FIRED", "NOT FIRED"))]
    assert out.returncode == 0 and len(lines) == 7 and all(l.startswith("NOT FIRED") for l in lines), out.stdout + out.stderr[-1500:]


def test_round8_corpus_sweeps_recorded():
    d5 = json.loads((ROOT / "evidence" / "v101_integrated" / "d5_identity_sweep.json").read_text(encoding="utf-8"))
    assert (d5["false_reassurance"]["n"], d5["false_concern"]["n"]) == (1, 1)
    s = json.loads((ROOT / "evidence" / "v101_integrated" / "round8_sweeps.json").read_text(encoding="utf-8"))
    assert (s["comparator_term"]["n_flip"], s["comparator_term"]["N"]) == (1, 145)
    assert s["nesting"]["n_with_rows_of_one_registration"] == 1 and s["date_claims"]["n_pages_with_claims"] == 0
