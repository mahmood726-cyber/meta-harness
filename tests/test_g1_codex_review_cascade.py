"""Cross-vendor (codex) review of the tocilizumab cascade and the second-meta reader (registry/model_proposals/
g1_codex_review.json, group cascade_and_meta2): each finding's OWN failing input, asserting the expected behaviour. Each
reproduced on the code before the fix (the review's 'actual'); each passes after it."""
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_toci_cascade as c  # noqa: E402
import g1_toci_meta2_forest as m  # noqa: E402


def _row(label, a, n1, b, n2, eff=""):
    return {"label": label, "events_t": str(a), "total_t": str(n1), "events_c": str(b), "total_c": str(n2),
            "effect": eff, "lower": "", "upper": ""}


def test_1_a_row_with_no_printed_effect_is_never_admitted():
    text = ("The only trial reported 100/1000 treatment deaths and 200/1000 control deaths. "
            "Risk ratio 0.50 (95% CI 0.40 to 0.62).")
    resp = {"legible": True, "measure": "Risk Ratio", "subgroup_read": "RCTs", "notes": "",
            "rows": [_row("Only trial", 900, 1000, 100, 1000)], "pooled": {"effect": "0.50", "lower": "0.40", "upper": "0.62"}}
    with patch.object(m.kfp, "pooled_in_text", return_value=True):
        r = m.gate(resp, text)
    assert r["state"] == "REFUSED" and r["rows"] == []
    assert any(p.startswith("G2_NO_PRINTED_EFFECT") for p in r["problems"])


def test_2_readers_must_give_the_counts_to_the_same_trial():
    g = [{"state": "PASS", "rows": [_row("Trial A", 10, 100, 20, 100), _row("Trial B", 30, 100, 40, 100)]},
         {"state": "PASS", "rows": [_row("Trial A", 30, 100, 40, 100), _row("Trial B", 10, 100, 20, 100)]}]
    assert m.admit(g, {"state": "INDEPENDENT"})[1] == []
    # control: the same trial under different printed forms of its label still agrees
    g[1]["rows"] = [_row("Trial A et al.12", 10, 100, 20, 100)]
    assert [r["label"] for r in m.admit(g, {"state": "INDEPENDENT"})[1]] == ["Trial A"]


def test_3_a_shared_registration_binds_one_population_only():
    labels, why = c.binding({"title": "CORIMUNO: tocilizumab for moderate COVID pneumonia",
                             "abstract": "Registration NCT04331808. This report includes ward patients only.",
                             "pub_types": ["Randomized Controlled Trial"]})
    assert labels == ["CORIMUNO-TOCI-1"], (labels, why)
    # ... and with no population in the title, to neither
    assert c.binding({"title": "CORIMUNO: tocilizumab for COVID", "abstract": "Registration NCT04331808.",
                      "pub_types": ["Randomized Controlled Trial"]})[0] == []


def test_4_a_newline_after_ref_still_counts_and_ref_list_is_not_a_ref():
    x = ('<article><ref-list><ref id="a">Another publication</ref><ref\nid="b"><pub-id pub-id-type="pmid">34228774'
         '</pub-id></ref></ref-list></article>')
    r = m.independence(x)
    assert (r["state"], r["n_refs"]) == ("CITES_COMPARATOR:34228774", 2)


def test_5_a_meta_citing_the_comparator_is_never_admitted_even_from_replay():
    g = [{"state": "PASS", "rows": [_row("Trial A", 10, 100, 20, 100)]},
         {"state": "PASS", "rows": [_row("Trial A", 10, 100, 20, 100)]}]
    st, rows, why = m.admit(g, {"state": "CITES_COMPARATOR:34228774"})
    assert (st, rows, why) == ("REFUSED", [], "CITES_COMPARATOR:34228774")
    assert m.admit(g, {"state": "INDEPENDENT"})[0] == "PASS"         # control


def test_6_preprint_files_are_rebound():
    seen = []
    with patch.object(c.os, "listdir", return_value=["CASCADE.md", "PPR123456.json"]), \
            patch("builtins.open", side_effect=lambda fp, *a, **k: seen.append(os.path.basename(fp)) or 1 / 0):
        try:
            c.rebind()
        except ZeroDivisionError:
            pass
    assert seen and seen[0] == "PPR123456.json"


def test_7_an_error_status_is_a_failed_rung_not_absence():
    with patch.object(c, "get", return_value=(503, b'{"error":"Service unavailable"}', "https://example.invalid")), \
            patch.object(c.time, "sleep"):
        outs = [c.rung_pmc("12345678")[0]["outcome"], c.rung_epmc("12345678")[0]["outcome"],
                c.rung_preprints("CORIMUNO-TOCI-1", "NCT04331808")["outcome"]]
    assert all(o.startswith("RUNG_FAILED") and "503" in o for o in outs), outs
