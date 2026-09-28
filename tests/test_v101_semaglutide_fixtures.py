"""V1.0.1 (semaglutide-obesity MACE and weight reviews). MACE: Stefanou 2024's MACE plot (7 of its 16 trials, held
image) as the outcome's membership, WEIGHT CONCENTRATION, the engine positive control, and its Egger
COMPARATOR_METHOD_INCONSISTENCY. Weight: WRITTEN vs EXECUTABLE exclusions (STEP 9 is adjudicated, never
keyword-excluded) and the Medicine 2026 comparator bound row by row. Plants are synthetic."""
import hashlib
import json
from pathlib import Path

import pytest

from harness import comparator_analysis as ca
from harness import comparator_models as cm
from harness import comparator_panel as cp
from harness import positive_control as pc
from harness import rule_trace as rt
from harness import screen

ROOT = Path(__file__).resolve().parents[1]
MACE, WEIGHT = "semaglutide-obesity-mace", "semaglutide-obesity-weight"


def _review(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _page(slug):
    return (ROOT / "docs" / "reviews" / slug / "index.html").read_text(encoding="utf-8")


# ---- MACE -----------------------------------------------------------------------------------------------------------
def test_mace_membership_is_the_7_plot_rows_shared_1_ours_only_0():
    r = _review(MACE)
    ov = r["comparator"]["overlap"]
    assert (ov["relation"], ov["ours_k"], ov["theirs_k"], ov["shared_k"], ov["only_ours"]) == ("SUBSET", 1, 7, 1, [])
    assert len(r["comparator"]["overlap_relation"]["theirs"]["out_of_scope"]) == 9      # listed, never dropped


def test_mace_weight_concentration_is_select():
    wc = _review(MACE)["comparator"]["analysis"]["membership"]["weight_concentration"]
    assert (wc["top"], wc["top_share"], wc["top_crude"]) == ("SELECT, 2023", 97.44, 0.7985)
    assert "not 7-trial corroboration" in _page(MACE)


def test_mace_positive_control_reproduces_with_our_engine():
    c = next(x for x in pc.load(ROOT) if x["id"] == "stefanou-2024-glp1-obesity-mace")
    got = pc.reproduce(c, ROOT)
    assert pc.compare(c, got) == [] and got["k"] == 7


def test_mace_egger_conflict_is_recorded_without_importing_either_side():
    r, page = _review(MACE), _page(MACE)
    m = [x for x in r["comparator"]["internal_mismatches"] if x.get("code") == "COMPARATOR_METHOD_INCONSISTENCY"]
    assert m and m[0]["evidence_state"] == "BOTH_SIDES_HELD"
    assert "does not repeat the reassuring wording" in page and "does not claim small-study bias" in page


def test_not_machine_exposed_is_derived_from_what_is_held():
    assert "per-trial inputs are not machine-exposed" not in _page(MACE)
    assert "ARE machine-exposed for the 7 rows" in _page(MACE)


# ---- MACE plants ----------------------------------------------------------------------------------------------------
def test_plant_weight_concentration_names_the_dominant_trial_and_leaves_out_double_zero_rows():
    rows = [{"label": "BIG", "counts": [500, 5000, 600, 5000]}, {"label": "small", "counts": [2, 100, 3, 100]},
            {"label": "empty", "counts": [0, 50, 0, 50]}]
    wc = ca.weight_concentration(rows, "OR")
    assert wc["top"] == "BIG" and wc["top_share"] > 95 and wc["no_events_left_out"] == ["empty"]
    assert ca.weight_concentration(rows, "MD") is None


def test_plant_a_quote_containing_a_less_than_sign_is_located_by_the_mismatch_loader(tmp_path):
    c = tmp_path / "cache" / "s"
    c.mkdir(parents=True)
    (c / "held.txt").write_text("<p>threshold set at p &lt; 0.10. Results follow.</p>", encoding="utf-8")
    doc = {"mismatches": [{"code": "COMPARATOR_METHOD_INCONSISTENCY", "kind": "k", "reading": "r", "sides": [
        {"state": "HELD", "document_ref": "cache/s/held.txt", "quote": "threshold set at p < 0.10."}]}]}
    (c / "comparator_reported_mismatches.json").write_text(json.dumps(doc), encoding="utf-8")
    assert cm.load_reported(tmp_path, "s")
    doc["mismatches"][0].pop("reading")
    (c / "comparator_reported_mismatches.json").write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(cm.FigureRefused, match="reading"):
        cm.load_reported(tmp_path, "s")


def _analysis_root(tmp_path, panel_rows, fig_bytes=b"img", sha=None):
    c = tmp_path / "cache" / "s"
    c.mkdir(parents=True)
    (c / "held.txt").write_text("the caption of the figure is here", encoding="utf-8")
    (c / "fig.jpg").write_bytes(fig_bytes)
    (c / "comparators.json").write_text(json.dumps([{"id": "1", "trial_set": [{"family_id": "A"}, {"family_id": "B"}]}]),
                                        encoding="utf-8")
    q = {"document_ref": "cache/s/held.txt", "quote": "the caption of the figure"}
    doc = {"outcome": "o", "governing": dict(q, k=2, n=40, scale="OR"),
           "membership": {"figure": {"caption": q, "document_ref": "cache/s/fig.jpg",
                                     "sha256": sha or hashlib.sha256(b"img").hexdigest()},
                          "rows": [{"label": "r1", "counts": [1, 10, 2, 10], "panel_row": panel_rows[0]},
                                   {"label": "r2", "counts": [1, 10, 2, 10], "panel_row": panel_rows[1]}]}}
    (c / "comparator_analysis.json").write_text(json.dumps(doc), encoding="utf-8")
    return tmp_path


def test_plant_plot_rows_must_name_distinct_rows_of_the_panel(tmp_path):
    assert ca.load(_analysis_root(tmp_path / "ok", ["A", "B"]), "s")
    for bad in (["A", "A"], ["A", "Z"]):
        with pytest.raises(ca.AnalysisRefused, match="distinct row"):
            ca.load(_analysis_root(tmp_path / "".join(bad), bad), "s")


def test_plant_a_held_figure_is_pinned_by_its_bytes(tmp_path):
    with pytest.raises(ca.AnalysisRefused, match="sha256"):
        ca.load(_analysis_root(tmp_path, ["A", "B"], fig_bytes=b"changed"), "s")


# ---- weight: written vs executable ----------------------------------------------------------------------------------
def test_weight_untraced_exclusions_are_exactly_the_ones_no_written_rule_states():
    t = _review(WEIGHT)["rule_trace"]
    assert t["enforced"] is True
    assert t["untraced"] == ["type 1 diabetes", "knee osteoarthritis", "heart failure", "bimagrumab", "cagrilintide"]
    served = _review(WEIGHT)["protocol"]["eligibility"]
    assert "knee osteoarthritis" not in served and "heart failure" not in served


def test_weight_records_hit_by_an_untraced_term_await_adjudication_and_the_pool_is_unchanged():
    r = _review(WEIGHT)
    adj = {str(d["id"]) for d in r["screening"]["records"] if d["decision"] == rt.ADJUDICATE}
    assert adj == {"41772149", "41290376", "41045908", "40544433"}
    o = next(o for o in r["outcomes"] if o.get("primary"))
    assert sorted(str(t["label"]) for t in o["trials"]) == ["33567185", "33625476"]


def _step9():
    from harness.fetch import parse_pubmed_xml
    rec = parse_pubmed_xml((ROOT / "tests" / "fixtures" / "step9_pubmed.xml").read_text(encoding="utf-8"))[0]
    rec["nct"] = ""          # no registry arm lookup (network) in a unit test
    return rec


def test_fixture_step9_is_adjudicated_not_keyword_excluded():
    cfg = json.loads((ROOT / "topics" / f"{WEIGHT}.json").read_text(encoding="utf-8"))
    rec = _step9()
    assert "Knee Osteoarthritis" in rec["title"] and "68-week" in rec["abstract"]
    d = screen.run([rec], cfg)["decisions"][0]
    assert d["decision"] == rt.ADJUDICATE and "knee osteoarthritis" in d["reason"].lower()


def test_fixture_step9_was_keyword_excluded_without_the_trace(monkeypatch):
    monkeypatch.setattr(rt, "load", lambda root, slug: None)
    cfg = json.loads((ROOT / "topics" / f"{WEIGHT}.json").read_text(encoding="utf-8"))
    d = screen.run([_step9()], cfg)["decisions"][0]
    assert d["decision"] == "exclude"                     # the defect the trace removes


def test_plant_a_trace_must_quote_the_protocol(tmp_path):
    (tmp_path / "protocols").mkdir()
    (tmp_path / "protocols" / "s.md").write_text("Exclude a different GLP-1 agonist.", encoding="utf-8")
    (tmp_path / "registry" / "rule_trace").mkdir(parents=True)
    p = tmp_path / "registry" / "rule_trace" / "s.json"
    p.write_text(json.dumps({"terms": {"liraglutide": {"protocol_quote": "a different GLP-1 agonist", "why": "w"}}}),
                 encoding="utf-8")
    t = rt.trace(tmp_path, "s", {"population_none": ["liraglutide", "heart failure"]})
    assert [r["state"] for r in t["rows"]] == ["TRACED_BY_CLAUSE", "UNTRACED"] and t["untraced"] == ["heart failure"]
    p.write_text(json.dumps({"terms": {"liraglutide": {"protocol_quote": "any incretin at all", "why": "w"}}}),
                 encoding="utf-8")
    with pytest.raises(rt.TraceRefused):
        rt.trace(tmp_path, "s", {"population_none": ["liraglutide"]})


# ---- weight comparator ----------------------------------------------------------------------------------------------
def test_weight_comparator_is_bound_row_by_row_and_is_not_the_same_question():
    r = _review(WEIGHT)
    ov = r["comparator"]["overlap"]
    assert (ov["relation"], ov["ours_k"], ov["theirs_k"], ov["shared_k"]) == ("SUBSET", 2, 4, 2)
    assert r["comparator"]["overlap_relation"]["only_theirs"] == ["O’Neil 2018", "Rubino 2021"]
    assert r["comparator"]["scope"]["same_question"]["label"] != "SAME_QUESTION"
    page = _page(WEIGHT)
    assert "4 vs 2 is not 2 trials missing from ours" in page and "not validation" in page


def test_plant_an_author_year_row_must_name_exactly_one_reference(tmp_path):
    def build(extra_ref):
        xml = ("<table><tbody><tr><td>Smith, 2020</td><td>1</td></tr></tbody></table>"
               '<ref id="R1"><surname>Smith</surname><year>2020</year><pub-id pub-id-type="pmid">111</pub-id></ref>'
               + extra_ref)
        (tmp_path / "j.xml").write_bytes(xml.encode("utf-8"))
        sha = hashlib.sha256(xml.encode("utf-8")).hexdigest()
        a, b = xml.index("<tr>"), xml.index("</tr>") + 5
        ra = xml.index('<ref id="R1">')
        rb = xml.index("</ref>", ra) + 6
        row, ref = {"start": a, "end": b, "quote": xml[a:b]}, {"start": ra, "end": rb, "quote": xml[ra:rb]}
        return {"held": True, "document_ref": "j.xml", "document_sha256": sha, "trial_set_document": {"document_ref": "j.xml", "document_sha256": sha},
                "trial_set": [{"family_id": "Smith 2020", "name_in_source": "Smith", "span": row, "endpoint": None,
                               "aliases": [{"id": "111", "document_ref": "j.xml", "document_sha256": sha, "span": ref,
                                            "author_year_row": row}]}]}
    cp.validate(build(""), tmp_path)
    with pytest.raises(ValueError, match="exactly one reference"):
        cp.validate(build('<ref id="R2"><surname>Smith</surname><year>2020</year></ref>'), tmp_path)


def test_plant_the_mismatch_gate_counts_each_record_under_its_own_code(tmp_path):
    from harness import gate
    rev = {"comparator": {"internal_mismatches": [{"code": "COMPARATOR_METHOD_INCONSISTENCY", "kind": "k"},
                                                  {"code": "COMPARATOR_INTERNAL_MISMATCH", "kind": "k"}]}}
    (tmp_path / "review.json").write_text(json.dumps(rev), encoding="utf-8")
    both = "<code>COMPARATOR_METHOD_INCONSISTENCY</code> ... <code>COMPARATOR_INTERNAL_MISMATCH</code>"
    assert gate.check_comparator_internal_mismatch_kept(tmp_path, both) == []
    missing = gate.check_comparator_internal_mismatch_kept(tmp_path, "<code>COMPARATOR_INTERNAL_MISMATCH</code>")
    assert missing and "COMPARATOR_METHOD_INCONSISTENCY" in missing[0]
