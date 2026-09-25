"""Schema-v2 writer (evidence/typed_arms/v2/write_v2.py): coordinates address the HELD document; synthetic tree only."""
import importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location("write_v2", os.path.join(HERE, "..", "evidence", "typed_arms", "v2", "write_v2.py"))
wv = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wv)

TITLE = "A trial of drugx"
ABSTRACT = "We assigned drugx (n=100) or placebo (n=98). The event occurred in 20 (20.0%) and 10 (10.2%) patients, respectively."
PACKET_DOC = f"TITLE: {TITLE}\n\n{ABSTRACT}\n"


def setup(tmp_path):
    root = tmp_path / "repo"
    (root / "cache" / "t").mkdir(parents=True)
    (root / "cache" / "t" / "records.json").write_text(json.dumps({"records": [{"id": "1", "title": TITLE, "abstract": ABSTRACT}]}), encoding="utf-8")
    wv.ROOT = str(root)
    pk = tmp_path / "packets" / "J"
    pk.mkdir(parents=True)
    (pk / "row.json").write_text(json.dumps({"slug": "t", "outcome_name": "event",
                                             "documents": [{"file": "doc_records_pmid_1.txt", "origin": "x"}]}), encoding="utf-8")
    return tmp_path


def W(tok, nth=0, text=PACKET_DOC):
    import re
    s = [m.start() for m in re.finditer(r"(?<![0-9])" + re.escape(tok) + r"(?![0-9])", text)][nth]
    return {"file": "doc_records_pmid_1.txt", "start": s, "end": s + len(tok), "text": tok}


def record(ev0=None, ev1=None, tot1=None):
    return {"job": "J", "held_key": "t/1", "state": "WITNESSED", "held_tuple": {}, "ownership_source": "PROSE_OR_TABLE",
            "arms": [{"role": "intervention", "group_id": None, "arm_name": "drugx", "events": 20, "total": 100,
                      "event_witness": ev0 or W("20"), "total_witness": W("100")},
                     {"role": "comparator", "group_id": None, "arm_name": "placebo", "events": 10, "total": 98,
                      "event_witness": ev1 or W("10"), "total_witness": tot1 or W("98")}]}


def run(tmp, rec):
    d = tmp / "recs"
    d.mkdir(exist_ok=True)
    (d / "J.json").write_text(json.dumps(rec), encoding="utf-8")
    out = tmp / "out.json"
    sys.argv = ["x", "test", str(d), str(tmp / "packets"), str(out)]
    wv.main()
    return json.loads(out.read_text(encoding="utf-8"))


def test_positive_offsets_address_the_held_abstract(tmp_path):
    t = setup(tmp_path)
    doc = run(t, record())
    obs = doc["rows"]["t/1"]["observations"]
    w = obs[0]["event_witness"]
    assert w["document_ref"] == "cache/t/records.json#PMID-1" and ABSTRACT[w["start"]:w["end"]] == "20"
    assert obs[0]["percentage_corroboration"] == [{"reported": "20.0", "agrees": True}]


def test_a_token_in_the_title_is_not_in_the_held_document(tmp_path):
    t = setup(tmp_path)
    s = PACKET_DOC.index("A trial")
    bad = {"file": "doc_records_pmid_1.txt", "start": s, "end": s + 1, "text": "A"}
    doc = run(t, record(ev0=bad))
    assert "t/1" in doc["not_written_rows"]


def test_a_shared_coordinate_is_not_injective(tmp_path):
    t = setup(tmp_path)
    doc = run(t, record(tot1=W("100")))
    assert any("NOT_INJECTIVE" in r for r in doc["not_written_rows"]["t/1"]["reasons"])


def test_wrong_offsets_against_the_held_text_are_refused(tmp_path):
    t = setup(tmp_path)
    w = W("10")
    w["start"] += 1
    w["end"] += 1
    doc = run(t, record(ev1=w))
    assert "t/1" in doc["not_written_rows"]
