"""A comparator row belongs to ONE comparator trial (g1_tracker.topic). Two comparator trials can share a family -- one
paper reports both (pcsk9: ODYSSEY FH I and FH II, 26330422) -- or carry a wrong one (PACMAN-AMI mapped to LONG TERM's
25773378); the family path handed the family's first row to both (5 copies in 4 topics before the fix). The comparator's
own supplement (PMC9755489 Data_Sheet_1 p7, Suppl Fig 3A) prints FH II 2/167 vs 2/81 and PACMAN-AMI 16/148 vs 31/152."""
import collections
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G1 = os.path.join(ROOT, "outputs", "k_gap", "g1")
FIXED = ["pcsk9-mace", "semaglutide-obesity-mace", "ticagrelor-vs-clopidogrel-acs", "balanced-crystalloids-vs-saline-mortality"]


def _o(slug):
    return json.load(open(os.path.join(G1, f"{slug}.json"), encoding="utf-8"))


def test_no_comparator_row_is_given_to_two_trials():
    for slug in FIXED:
        c = collections.defaultdict(list)
        for x in _o(slug)["trials"]:
            pr = x.get("comparator_row_provenance") or {}
            if x.get("comparator_row") and pr.get("row_label"):
                c[(pr["row_label"], json.dumps(x["comparator_row"], sort_keys=True))].append(x["label"])
        assert not {k[0]: v for k, v in c.items() if len(v) > 1}, slug


def test_pcsk9_fh2_and_pacman_carry_their_own_rows_or_none():
    t = {x["label"]: x for x in _o("pcsk9-mace")["trials"]}
    for lab, want in (("ODYSSEY FH II NCT01709500", (2, 167, 2, 81)), ("PACMAN - AMI NCT03067844", (16, 148, 31, 152))):
        cr = t[lab].get("comparator_row")
        got = tuple(cr.get(k) for k in ("events_t", "n_t", "events_c", "n_c")) if cr else None
        assert got in (want, None), (lab, got)          # its own row, or none -- never another trial's
