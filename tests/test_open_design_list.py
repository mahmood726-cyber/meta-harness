"""X-DESIGN audit: a design list states open-label without the word 'label' -- colchicine-postop-af Zarpelon [20]
(PMID 27223641, PMC4976950): 'a prospective, randomized, open, single-center clinical assay' read BLINDING_NOT_STATED."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_exclusion_audit as ea  # noqa: E402


def test_open_in_a_design_list_is_open_label():
    for s in ("This is a prospective, randomized, open, single-center clinical assay",
              "DESIGN AND SETTING: Open randomized controlled trial in 17 units", "An open, prospective, comparative study",
              "an open-label trial"):
        assert ea.OPEN.search(s), s


def test_open_elsewhere_is_not():
    for s in ("randomized open heart surgery patients", "the trial was open to all patients", "open study visits",
              "patients undergoing open-heart surgery were randomized"):
        assert not ea.OPEN.search(s), s




def test_an_open_label_title_decides_x_design():
    # omega3 JELIS (17398308), the held record: the title says 'randomised open-label', the abstract does not
    import json
    cfg = json.load(open(os.path.join(ROOT, "topics", "omega3-cardiovascular-events.json"), encoding="utf-8"))
    R = json.load(open(os.path.join(ROOT, "cache", "omega3-cardiovascular-events", "records.json"), encoding="utf-8"))
    recs = R if isinstance(R, list) else R.get("records") or list(R.values())
    rec = next(r for r in recs if str(r.get("id")) == "17398308")
    assert ea.OPEN.search(rec["title"]) and not ea.OPEN.search(rec.get("abstract") or "")
    cls, sub, base = ea.classify(rec, cfg)
    assert (cls, sub.split(" ")[0]) == ("TRUE_SCOPE_DIFFERENCE", "OPEN_LABEL_STATED") and base["span"]["field"] == "title"


def test_full_text_evidence_never_re_screens_the_record():
    # colchicine-postop Zarpelon (27223641): its full text cites 'a randomized, placebo-controlled study' (another trial);
    # appended to the record and re-screened, the record was INCLUDED and the item read INCONSISTENT
    import json
    cfg = json.load(open(os.path.join(ROOT, "topics", "colchicine-postop-af.json"), encoding="utf-8"))
    rec = {"id": "27223641", "id_type": "pmid", "pubtypes": ["Journal Article", "Randomized Controlled Trial"],
           "title": "Colchicine to Reduce Atrial Fibrillation in the Postoperative Period of Myocardial Revascularization.",
           "abstract": "Between May 2012 and November 2013, 140 patients submitted to myocardial revascularization surgery "
                       "were randomized, 69 to the control group and 71 to the colchicine group."}
    ft = ("This is a prospective, randomized, open, single-center clinical assay, whose 140 participants were recruited. "
          "The AF rate was estimated based on the results of a randomized, placebo-controlled study.")
    both = dict(rec, abstract=rec["abstract"] + "\n\n" + ft)
    cls, sub, base = ea.classify(both, cfg, decide_rec=rec)
    assert cls == "TRUE_SCOPE_DIFFERENCE" and sub.startswith("OPEN_LABEL_STATED") and "open, single-center" in base["span"]["text"]
