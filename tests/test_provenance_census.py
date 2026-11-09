"""Plants for the provenance gate (Mahmood 6 Oct: every served value and every G1 tracker row traces to a deterministic
extractor or a recorded model call that replays offline; nothing hand-entered, nothing unrecorded)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import provenance_census as pc  # noqa: E402


def _c(served=(), tracker=()):
    return {"served": {"rows": list(served)}, "tracker": {"rows": list(tracker)}}


def test_an_untraced_row_is_refused():
    row = {"slug": "s", "outcome": "o", "id": "PMID 1", "class": "UNTRACED", "why": "x"}
    assert any(p.startswith("UNTRACED") for p in pc.problems(_c(served=[row]), {"rows": []}))


def test_a_hand_entered_row_must_be_on_the_burn_down_list():
    row = {"slug": "s", "outcome": "o", "id": "PMID 1", "class": "HAND_ENTERED", "why": "x"}
    assert any(p.startswith("HAND_ENTERED") for p in pc.problems(_c(served=[row]), {"rows": []}))
    assert not pc.problems(_c(served=[row]), {"rows": ["served|s|o|PMID 1"]})


def test_a_row_naming_a_record_not_in_the_tree_is_untraced():
    t = {"provenance": "model_read", "source": "x", "note": "read by mc-" + "0" * 32}
    assert pc.classify_served(t)[0] == "UNTRACED"


def test_an_extractor_row_needs_its_span():
    assert pc.classify_served({"provenance": "abstract", "source": "HR 0.8 (0.7-0.9)"})[0] == "EXTRACTOR"
    assert pc.classify_served({"provenance": "abstract", "source": ""})[0] == "UNTRACED"
    assert pc.classify_served({"provenance": "abstract_verified", "source": "x"})[0] == "HAND_ENTERED"


def test_the_committed_tree_has_no_untraced_row_and_no_unlisted_hand_entry():
    c = pc.census()
    hl = pc._j(pc.HAND_LIST)
    assert pc.problems(c, hl) == []
    # the burn-down list may only shrink: every listed row must still exist as a HAND_ENTERED row
    live = {f"{part}|{pc._key(x)}" for part in ("served", "tracker") for x in c[part]["rows"] if x["class"] == "HAND_ENTERED"}
    assert set(hl["rows"]) <= live, sorted(set(hl["rows"]) - live)[:5]     # converted rows are removed from the list


def test_plant_a_tracker_row_for_a_signed_refusal_is_a_disclosed_lag_not_untraced():
    """V15-C: the served page refuses TECOS under a signed decision, but the G1 tracker (lane-built; regenerating it by
    script wiped tocilizumab's lane curation, 13 Oct) still pools it. That row is traced to the SIGNED refusal -- a
    disclosed lag -- never UNTRACED, and never silently counted as served."""
    review = {"outcomes": [{"name": "MACE", "primary": True, "trials": [], "declared_absent_trials": [
        {"id": "PMID 26052984", "state": "REFUSED_ON_EVIDENCE", "enforcement": {"decision": "REFUSE", "basis": "b"}},
        {"id": "PMID 1", "state": "EXTRACTION_DEBT"}]}]}
    sr = pc.signed_refusals("dpp4", review)
    assert set(sr) == {("dpp4", "26052984")}
    cls, why = pc.classify_tracker({"in_our_pool": True, "family": "PMID 26052984"}, "dpp4", sr)
    assert cls == "SIGNED_REFUSAL" and "signed" in why
    assert pc.problems({"served": {"rows": []}, "tracker": {"rows": [{"slug": "dpp4", "label": "TECOS", "route": "R",
                                                                     "class": cls, "why": why}]}}, None) == []
