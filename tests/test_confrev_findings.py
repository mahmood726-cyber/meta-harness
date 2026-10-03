"""CONFREV adversarial findings for g1/confirm-unverified.

Strict xfails written by CONFREV (gpt-5.5) against 16b21391b, kept as REGRESSION tests now that each is fixed.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

import g1_confirm_bind as cb  # noqa: E402
import g1_tracker as gt  # noqa: E402


TERMS = ["antibiotic-associated diarrhea", "diarrhoea", "diarrhea"]


def trial(label="Trial A", **cr):
    return {"label": label, "route": "UNVERIFIED", "comparator_row": cr}


def run_bind(monkeypatch, text, x):
    monkeypatch.setattr(cb.smb, "primary_sources", lambda slug, p, nct=None: [("text", f"PMID {p} abstract", text)])
    return cb.bind_one("topic", x, ["111"], [], TERMS)


def binding_labels():
    p = ROOT / "outputs" / "k_gap" / "g1_confirm" / "bindings.json"
    return {(b["slug"], b["label"]) for b in json.loads(p.read_text(encoding="utf-8"))["bindings"]}


def test_control_non_swapped_counts_still_bind(monkeypatch):
    b, why = run_bind(
        monkeypatch,
        "RESULTS: Antibiotic-associated diarrhea occurred in 4/23 patients in the probiotic group "
        "and 6/16 patients in the placebo group.",
        trial(events_t="4", n_t="23", events_c="6", n_c="16", measure="RR"),
    )
    assert why == "BOUND"
    assert b["tuple_kind"] == "COUNTS"


# CONFREV finding (was strict xfail on 16b21391b): "text count binding ignores explicit arm ownership"
def test_xfail_binder_refuses_swapped_arm_counts_in_text(monkeypatch):
    b, why = run_bind(
        monkeypatch,
        "RESULTS: Antibiotic-associated diarrhea occurred in 4/23 patients in the placebo group "
        "and 6/16 patients in the probiotic group.",
        trial(events_t="4", n_t="23", events_c="6", n_c="16", measure="RR"),
    )
    assert b is None
    assert why == "ARM_COUNTS_SWAPPED"


def _bindings(tmp_path, span):
    p = tmp_path / "bindings.json"
    p.write_text(
        json.dumps(
            {
                "bindings": [
                    {
                        "slug": "topic",
                        "label": "Trial A",
                        "source_kind": "TEXT",
                        "source": "PMID 111 abstract",
                        "tuple_kind": "COUNTS",
                        "values": {"events_t": 4, "n_t": 23, "events_c": 6, "n_c": 16},
                        "span": span,
                        "search_key": "COMPARATOR_ROW",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return str(p)


# CONFREV finding (was strict xfail on 16b21391b): "tracker recheck only verifies count presence, not arm ownership"
def test_xfail_tracker_refuses_swapped_arm_binding(tmp_path):
    o = {
        "slug": "topic",
        "trials": [dict(trial(events_t="4", n_t="23", events_c="6", n_c="16", measure="RR"), g1_countable=False)],
        "open_gaps": ["Trial A"],
    }
    span = (
        "Antibiotic-associated diarrhea occurred in 4/23 patients in the placebo group "
        "and 6/16 patients in the probiotic group."
    )
    assert gt.apply_confirm_bindings(o, _bindings(tmp_path, span)) == []
    assert o["trials"][0]["route"] == "UNVERIFIED"
    assert o["trials"][0]["confirm_binding"]["why"] == "ARM_COUNTS_SWAPPED"


# CONFREV finding (was strict xfail on 16b21391b): "ELIXA binding is a 4-point primary CV composite, not the 3-point topic MACE"
def test_xfail_committed_elixa_different_estimand_not_bound():
    assert ("glp1-ra-mace-t2d", "ELIXA") not in binding_labels()


# CONFREV finding (was strict xfail on 16b21391b): "Siebert 2009 uses clomiphene with/without metformin, not the topic placebo contrast"
def test_xfail_committed_siebert_wrong_comparison_not_bound():
    assert ("metformin-pcos-ovulation", "Siebert 2009") not in binding_labels()


# CONFREV finding (was strict xfail on 16b21391b): "Wenus et al72 binding is explicitly per-protocol completers, not whole trial"
def test_xfail_committed_wenus_per_protocol_not_bound():
    assert ("probiotics-aad-prevention", "Wenus et al72") not in binding_labels()
