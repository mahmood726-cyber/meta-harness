"""The served label of the NI policy (outputs/robgrade/NI_POLICY.md section 5), rendered from the objects. Written
before robgrade/rob2_tab.py. The label states only what was computed, and never changes the judgement word."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from robgrade import rob2_formal as rf  # noqa: E402
from robgrade import rob2_tab as tab  # noqa: E402


def _dom(dom, **kw):
    return rf.domain_object(dom, {q.replace("_", "."): {"answer": v} for q, v in kw.items()})


def test_PLANT_ni_driven_domain_label():
    d = _dom("D1", **{"1_1": "Y", "1_2": "NI", "1_3": "N"})
    assert tab.domain_label(d) == "Some concerns (NI-driven: 1.2 not reported; Low if reported favourably)"


def test_PLANT_a_domain_not_ni_driven_shows_the_judgement_alone():
    assert tab.domain_label(_dom("D1", **{"1_1": "Y", "1_2": "N", "1_3": "NI"})) == "High"
    assert tab.domain_label(_dom("D1", **{"1_1": "Y", "1_2": "Y", "1_3": "NI"})) == "Low"


def test_PLANT_joint_resolution_is_said_as_such():
    lab = {"judgement": "SOME_CONCERNS", "ni": {"ni_driven": True, "if_ni_resolved_favourably": "LOW",
                                               "ni_questions": ["2.1", "2.6"], "decisive_ni_questions": []}}
    assert tab.domain_label(lab) == "Some concerns (NI-driven: 2.1, 2.6 not reported (together); Low if reported favourably)"


def test_PLANT_insufficient_is_not_an_ni_label():
    d = rf.domain_object("D3", {}, insufficient=True)
    assert tab.domain_label(d) == "Not assessed (no open source)"


def test_PLANT_overall_label_names_the_domains_and_the_review_flag():
    ans = {q: rf.answer(v, how="t", span="s", source_sha256="0" * 64) if v != "NI" else rf.answer("NI", how="t")
           for q, v in {"1.1": "Y", "1.2": "NI", "1.3": "N", "2.1": "N", "2.2": "N", "2.6": "Y", "3.1": "Y", "4.1": "N",
                        "4.2": "N", "4.3": "N", "5.1": "NI", "5.2": "N", "5.3": "N"}.items()}
    o = rf.assessment("PMID 1", "o", ans)
    assert tab.overall_label(o["overall"]) == ("Some concerns (NI-driven: D1, D5; Low if the missing answers were "
                                               "reported favourably) [several domains with some concerns: for a review "
                                               "author's judgement]")


def test_PLANT_the_preview_never_writes_to_docs():
    src = open(os.path.join(ROOT, "robgrade", "rob2_tab.py"), encoding="utf-8").read()
    assert '"docs"' not in src and "'docs'" not in src


# ---- contextual answers (CONTEXTUAL_POLICY C5): never silent
def test_PLANT_a_contextual_answer_is_named_in_the_label():
    a = rf.answer("PY", how="contextual", span="central web-based randomisation", source_sha256="a" * 64)
    a["basis"] = "contextual"
    d = rf.domain_object("D1", {"1.1": {"answer": "Y", "span": "s", "source_sha256": "0" * 64}, "1.2": a,
                                "1.3": {"answer": "N", "span": "s", "source_sha256": "0" * 64}})
    assert tab.domain_label(d) == "Low [contextual: 1.2 probably yes, from 'central web-based randomisation']"


def test_PLANT_contextual_and_ni_driven_are_both_shown():
    # 5.1 PY (contextual) with 5.2 NI: Some concerns, and Low if 5.2 were N -- NI-driven (guidance Table 14)
    a = rf.answer("PY", how="contextual", span="a registered statistical analysis plan", source_sha256="a" * 64)
    a["basis"] = "contextual"
    d = rf.domain_object("D5", {"5.1": a, "5.2": {"answer": "NI"}, "5.3": {"answer": "N", "span": "s", "source_sha256": "0" * 64}})
    lab = tab.domain_label(d)
    assert lab.startswith("Some concerns (NI-driven: 5.2 not reported;") and "[contextual: 5.1 probably yes, from" in lab


def test_PLANT_the_contextual_preview_renders_the_contextual_objects(tmp_path, monkeypatch):
    # codex/agy round 1: the display path must read the contextual objects, and the note must reach the HTML
    import json
    a = rf.answer("PY", how="contextual", span="central web-based randomisation", source_sha256="a" * 64)
    a["basis"] = "contextual"
    o = rf.assessment("PMID 1", "o", {"1.1": rf.answer("Y", how="t", span="s", source_sha256="0" * 64), "1.2": a,
                                      "1.3": rf.answer("N", how="t", span="s", source_sha256="0" * 64)})
    (tmp_path / "outputs" / "robgrade" / "rob2_ctx").mkdir(parents=True)
    (tmp_path / "outputs" / "robgrade" / "rob2_ctx" / "s.json").write_text(json.dumps({"trials": {"1": o}}), encoding="utf-8")
    monkeypatch.setattr(tab, "ROOT", str(tmp_path))
    tab.main(["--ctx", "s"])
    out = (tmp_path / "outputs" / "robgrade" / "tab_preview_ctx" / "s.html").read_text(encoding="utf-8")
    assert "[contextual: 1.2 probably yes, from &#x27;central web-based randomisation&#x27;]" in out
