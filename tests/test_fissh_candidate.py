"""FISSH (PMID 28729329, NCT02748382) is a family CANDIDATE for balanced-crystalloids: linked and decided, never pooled."""
import importlib.util, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "evidence", "family_candidates", "build_fissh.py")
OUT = os.path.join(ROOT, "evidence", "family_candidates", "balanced-crystalloids-vs-saline-mortality", "NCT02748382_FISSH.json")
SLUG = "balanced-crystalloids-vs-saline-mortality"


def _mod():
    spec = importlib.util.spec_from_file_location("build_fissh", P)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_committed_candidate_rebuilds_exactly():
    assert _mod().main(check=True) == 0


def test_every_located_span_resolves():
    m = _mod()
    d = json.load(open(OUT, encoding="utf-8"))
    spans = [v for k in ("I1", "I3") for v in ([d["adjudication"][k]["evidence"]] if isinstance(d["adjudication"][k]["evidence"], dict)
                                               else d["adjudication"][k]["evidence"])]
    spans += [s for s in d["adjudication"]["I2"]["evidence"] if "start" in s] + list(d["adjudication"]["rules"].values())
    for s in spans:
        text = m.textrep.render(s["document_ref"]) if s["document_ref"].endswith(".json") else \
            open(os.path.join(ROOT, s["document_ref"]), encoding="utf-8").read()
        assert text[s["start"]:s["end"]] == s["quote"], s["quote"]


def test_decision_is_eligible_result_not_available_and_never_pooled():
    d = json.load(open(OUT, encoding="utf-8"))
    assert d["family_id"] == "NCT02748382" and d["pooled"] is False and d["in_topic_records"] is False
    assert d["decision"]["eligibility"].startswith("ELIGIBLE") and d["decision"]["target_result_status"] == "RESULT_NOT_AVAILABLE"
    assert d["structural_screen"]["result"]["absence_code"] == "INSUFFICIENT_PICD_EVIDENCE"
    recs = json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))["records"]
    assert not {"28729329", "NCT02748382"} & {str(r.get("id")) for r in recs}
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))
    pooled = {str(t.get("family_id")) for o in rev["outcomes"] for t in o.get("trials") or []}
    assert "NCT02748382" not in pooled
