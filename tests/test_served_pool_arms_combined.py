"""Plants for V9-02 (Mahmood 7 Oct, 'yes to all'; V9-02Q allows the Cochrane Handbook 6.5.2.10 arm merge into a served
pool): a continuous MD row whose intervention arms were COMBINED enters the served pool only through the signed-notice
register, only from a committed typed AACT binding whose verbatim span prints every arm's mean, SD and N, and only when
the merge re-derived from those printed numbers equals the tracker's combined value. The served row carries the printed
arms and the derivation; the combined numbers are never presented as printed."""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import build_served_pool_additions as bspa  # noqa: E402
import g1_fill_notices as fn  # noqa: E402
from harness import served_pool_additions as spa  # noqa: E402

SLUG = "esketamine-trd-madrs"


def _row():
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", f"{SLUG}.json"), encoding="utf-8"))
    return next(t for t in o["trials"] if "TRANSFORM-1" in t["label"])


def test_PLANT_a_combined_md_row_fills_on_the_md_scale():
    v = dict(_row()["our_value"], trial="TRANSFORM-1")
    st, why = fn.fill_study(v, "MD")
    assert st is not None, why
    assert (st.nc1, st.nc2) == (209, 108) and abs(st.mean2 + 14.8) < 1e-9
    st, why = fn.fill_study(v, "RR")
    assert st is None                                        # never on another scale


def test_PLANT_the_register_admits_the_arms_combined_row_from_its_printed_arms():
    row, why = bspa.pipeline_row(SLUG, _row(), "MD")
    assert row is not None, why
    assert row["nc1"] == 209 and row["nc2"] == 108 and abs(row["mean2"] + 14.8) < 1e-9
    assert abs(row["mean1"] - (-18.9062)) < 5e-5 and abs(row["sd1"] - 13.9491) < 5e-5
    assert "6.5.2.10" in row["derivation"] and len(row["arms_printed"]) == 3
    assert all(a["mean"] in row["source"] for a in row["arms_printed"])


def test_PLANT_an_arm_value_missing_from_the_span_refuses(monkeypatch):
    real = bspa._aact_binding

    def bad(slug, x):
        b = copy.deepcopy(real(slug, x))
        b["span"] = b["span"].replace("Standard Deviation 14.12", "Standard Deviation 14.2")
        return b
    monkeypatch.setattr(bspa, "_aact_binding", bad)
    row, why = bspa.pipeline_row(SLUG, _row(), "MD")
    assert row is None and "span" in why


def test_PLANT_a_tracker_value_the_printed_arms_do_not_reproduce_refuses():
    x = _row()
    x = dict(x, our_value=dict(x["our_value"], mean_t="-19.5"))
    row, why = bspa.pipeline_row(SLUG, x, "MD")
    assert row is None and "reproduce" in why


def test_PLANT_a_signed_row_supersedes_a_known_reported_not_yet_extracted_absence():
    assert "KNOWN_REPORTED_NOT_YET_EXTRACTED" in spa.SUPERSEDABLE


def test_PLANT_the_signed_notice_states_the_conclusion_change_and_the_reinstatement():
    """The committed V9-02 notice (immutable once signed) and the generator's conclusion statement."""
    import g1_served_pool_notices as sp
    from harness import result_changes as rc
    n = next(n for n in rc.load() if n["slug"] == SLUG and n.get("entered_pool") == ["NCT02417064"])
    assert n["after"] == {"k": 4, "estimate": -3.3436, "ci_low": -6.0691, "ci_high": -0.618}
    assert "CONCLUSION CHANGE" in n["reason"] and "'no difference shown' to 'a difference shown'" in n["reason"]
    assert "REINSTATES NCT02417064" in n["reason"] and "6.5.2.10" in n["reason"]
    assert "None" not in n["reason"].split("Excluded")[0]
    assert bspa.served_id(SLUG, _row()) == "NCT02417064"
    assert sp.conclusion_change({"k": 2, "estimate": 0.9, "ci_low": 0.8, "ci_high": 0.95},
                                {"k": 3, "estimate": 0.9, "ci_low": 0.8, "ci_high": 0.95}, "HR") == ""
    assert sp.conclusion_change({"k": 2, "estimate": 0.9, "ci_low": 0.8, "ci_high": 0.95},
                                {"k": 3, "estimate": 0.95, "ci_low": 0.85, "ci_high": 1.05}, "HR").startswith(
        "CONCLUSION CHANGE")


def test_PLANT_a_trial_served_under_its_nct_is_never_proposed_again():
    import g1_served_pool_notices as sp
    pm, nc = sp.served_identity({"trials": [{"id": "NCT02417064"}, {"id": "PMID 37025256"}]})
    assert "NCT02417064" in nc


def test_PLANT_a_signed_row_replaces_the_pipelines_own_row_of_the_same_trial():
    """V9-02 build: the pipeline still carried TRANSFORM-1's 20 Sep hand-transcribed row under the same id, so the signed
    row was skipped as a duplicate and the hand row was then refused -- the served pool stayed k=3."""
    own = {"id": "NCT02417064", "provenance": "fulltext_verified_arms", "mean1": -18.91}
    other = {"id": "PMID 1", "provenance": "abstract"}
    signed = {"id": "NCT02417064", "provenance": "served_pool_signed_notice", "mean1": -18.9062}
    out = spa.merge_signed([own, other], [signed], withdrawn=False)
    assert [t["provenance"] for t in out] == ["abstract", "served_pool_signed_notice"]
    assert out[1]["served_pool_admission"]["replaced_pipeline_row"]["provenance"] == "fulltext_verified_arms"
    assert spa.merge_signed([other], [], withdrawn=False) == [other]


def test_PLANT_an_arm_count_is_matched_as_a_whole_number_never_a_prefix(monkeypatch):
    """codex v9-apply g1#1: 'N 10' matched the held 'N 108' as a substring."""
    real = bspa._aact_binding

    def short(slug, x):
        b = copy.deepcopy(real(slug, x))
        for a in b["arms"]:
            if a["role"] == "control":
                a["n"] = "10"
        return b
    monkeypatch.setattr(bspa, "_aact_binding", short)
    x = _row()
    x = dict(x, our_value=dict(x["our_value"], n_c=10))
    row, why = bspa.pipeline_row(SLUG, x, "MD")
    assert row is None and "verbatim" in why


def test_PLANT_each_arm_tuple_is_bound_to_its_own_segment_and_counts_are_whole(monkeypatch):
    """codex v9-apply-r2: #1 two intervention arms reusing the control's printed values passed (values not bound to
    their arm); #2 a fractional printed N was truncated by int()."""
    real = bspa._aact_binding

    def reuse(slug, x):
        b = copy.deepcopy(real(slug, x))
        c = next(a for a in b["arms"] if a["role"] == "control")
        for a in b["arms"]:
            if a["role"] == "intervention":
                a.update(mean=c["mean"], sd=c["sd"], n=c["n"])
        return b
    monkeypatch.setattr(bspa, "_aact_binding", reuse)
    row, why = bspa.pipeline_row(SLUG, _row(), "MD")
    assert row is None

    def frac(slug, x):
        b = copy.deepcopy(real(slug, x))
        a = next(a for a in b["arms"] if a["role"] == "control")
        b["span"] = b["span"].replace(f"N {a['n']}", f"N {a['n']}.5")
        a["n"] = f"{a['n']}.5"
        return b
    monkeypatch.setattr(bspa, "_aact_binding", frac)
    row, why = bspa.pipeline_row(SLUG, _row(), "MD")
    assert row is None and "whole" in why


def test_PLANT_fill_refuses_a_fractional_sample_size():
    """codex v9-apply-r3 #1: the MD branch of fill_study int()-truncated a fractional N."""
    v = dict(_row()["our_value"], trial="TRANSFORM-1", n_t="209.5")
    st, why = fn.fill_study(v, "MD")
    assert st is None and "whole" in why


def test_PLANT_a_non_finite_arm_value_is_refused(monkeypatch):
    """codex v9-apply-r4 #1: abs(expected - NaN) > 1e-9 is False, so a NaN control mean passed the reproduction check."""
    real = bspa._aact_binding

    def nan(slug, x):
        b = copy.deepcopy(real(slug, x))
        a = next(a for a in b["arms"] if a["role"] == "control")
        b["span"] = b["span"].replace(f"MEAN {a['mean']} Standard Deviation {a['sd']} N {a['n']}",
                                      f"MEAN nan Standard Deviation {a['sd']} N {a['n']}")
        a["mean"] = "nan"
        return b
    monkeypatch.setattr(bspa, "_aact_binding", nan)
    row, why = bspa.pipeline_row(SLUG, _row(), "MD")
    assert row is None and "finite" in why
