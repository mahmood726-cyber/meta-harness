"""V15-C: the signed binding decision for every unbound served pooled row (Mahmood, 13 Oct, ruling 1).

Generated from outputs/m2_pretriage/classified.json (rebuilt from the stored codex / agy / adjudicator records by
`scripts/m2_pretriage.py outputs/m2_pretriage --reclassify`) and the signed rulings below -- no value is typed here.

The rule Mahmood signed: admit the confirmed rows; refuse TECOS, both esketamine rows and JUPITER >=70; keep RE-LY; for
every other row a written recommendation backed by the codex + agy + adjudicator read against the source, then apply
it -- and any row where the panel disagrees, or the source is absent, is a documented refusal: refuse, don't admit.
The signed summary also recommended keeping the colchicine rows as the declared conversion of the stated RRR and the
ENGAGE row on its signed V12-01 (EPAR) value; "do as you suggested for all" signs those.

    python scripts/v15c_decisions.py           writes registry/v15c_decisions.json and prints the counts
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASSIFIED = os.path.join(ROOT, "outputs", "m2_pretriage", "classified.json")
OUT = os.path.join(ROOT, "registry", "v15c_decisions.json")

SIGNED = {"by": "Mahmood", "via": "Dispatch", "when": "2026-10-13", "words": "sign and do as you suggested for all",
          "packet": "lane_status/v15c_enforcement_packet_DRAFT.md",
          "packet_sha256": "6067c4f1fdb5bda59b481004b6fdd5e0edb63159bbb965d17af28971e7508913",
          "summary_sha256": "6bf07e9d1cf314bb594c3ed2dd2eb70cf526913f797d5e930344a9f93c63ffa6",
          "state": "SEEN_AND_SIGNED"}
# (slug, PMID) -> the signed disposition; every other row follows the rule
REFUSE_SIGNED = {("dpp4-mace-t2d", "26052984"): "TECOS: the stated composite adds unstable-angina hospitalisation (4-point)",
                 ("esketamine-trd-madrs", "31109201"): "an MMRM least-squares difference, not the observed-case raw MD",
                 ("esketamine-trd-madrs", "37025256"): "an MMRM least-squares difference, not the observed-case raw MD",
                 ("statins-primary-prevention-elderly", "20404379"): "JUPITER >=70: the age cut-point was chosen after "
                                                                     "the trial (post hoc), not pre-specified"}
KEEP_SIGNED = {("noac-vs-warfarin-af-stroke", "19717844"): "RE-LY: kept (signed). The abstract states RR 0.66 (0.53 to "
                                                           "0.82) for dabigatran 150 mg v warfarin; agy bound it, codex "
                                                           "and the adjudicator refused on RR v HR"}
# the numbers each signed keep signs, as the signed packet states them (v15c packet: RE-LY "RR 0.66 (0.53 to 0.82)";
# ENGAGE "Served 0.87 (0.744-1.017) is the SIGNED V12-01 value")
SIGNED_SNAPSHOT = {("noac-vs-warfarin-af-stroke", "19717844"): {"effect": 0.66, "ci_low": 0.53, "ci_high": 0.82},
                   ("noac-vs-warfarin-af-stroke", "24251359"): {"effect": 0.87, "ci_low": 0.744, "ci_high": 1.017}}
CONVERSION_SIGNED = {("colchicine-recurrent-pericarditis", "21873705")}
EPAR_SIGNED = {("noac-vs-warfarin-af-stroke", "24251359"): "ENGAGE AF-TIMI 48: the signed V12-01 value (EMA EPAR "
                                                           "printed 95% CI); the abstract prints the 97.5% CI"}
# panel REFUSE reason codes that say the source shows a DIFFERENT result (refused on evidence); any other refusal is an
# abstention -- the row could not be bound, nothing shows it wrong
ON_EVIDENCE = {"DIFFERENT_ENDPOINT", "SUBGROUP_OR_SECONDARY_ANALYSIS", "OUTCOME_NOT_IN_SOURCE"}
SERVED_KEYS = ("effect", "ci_low", "ci_high", "ai", "n1i", "ci", "n2i")


def _pmid(row):
    return str(row.get("id") or "").replace("PMID ", "").strip()


def _readers(row):
    return {"codex": row.get("codex_record"), "agy": row.get("agy_record"),
            "adjudicator": row.get("adjudicator_record"), "state": row.get("state")}


def _conversion_ok(row):
    """served RR == 1 - stated RRR, bounds swapped, to the served precision (2 dp)."""
    n = (row.get("proposal") or {}).get("numbers") or {}
    s = row.get("served") or {}
    if "reduction" not in str(n.get("measure") or "").lower():
        return False
    want = (round(1 - n["effect"], 2), round(1 - n["ci_high"], 2), round(1 - n["ci_low"], 2))
    return want == (s.get("effect"), s.get("ci_low"), s.get("ci_high"))


_SERVED_OF = {"effect": "effect", "ci_low": "ci_low", "ci_high": "ci_high",
              "events_t": "ai", "n_t": "n1i", "events_c": "ci", "n_c": "n2i"}
_WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                      "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}


def _readers_agree_on_served(row):
    """Every reader (codex, agy, adjudicator where called) bound EVERY served number, and to the served value."""
    served = {k: v for k, v in (row.get("served") or {}).items() if v is not None}
    readers = [row.get(r) for r in ("codex", "agy", "adjudicator") if row.get(r)]
    if not served or len(readers) < 2:
        return False
    for rd in readers:
        if (rd or {}).get("decision") != "BIND":
            return False
        bound = {_SERVED_OF[k]: v for k, v in ((rd.get("numbers") or {}).items()) if k in _SERVED_OF
                 and isinstance(v, (int, float)) and not isinstance(v, bool)}
        if any(k not in bound or abs(float(bound[k]) - float(v)) > 1e-9 for k, v in served.items()):
            return False
    return True


def locate(span, served):
    """{served key: the token in the verbatim span that states it} -- digits (unicode minus folded) or an English number
    word (zero..twenty, recorded as the word); None when any served number is not stated in the span."""
    # ROLE, not just value (codex v15cenf-cap-r1 #1: '4%' passed as a death count of 4). A count is located only as one
    # side of an 'X of N' pair (events of denominator); an effect / CI bound only as a number NOT followed by '%'
    s = (span or "").replace("−", "-").replace("–", "-")
    word = r"(?:\d+|" + "|".join(_WORDS) + r")"
    pairs = [(m.group(1), m.group(2)) for m in re.finditer(r"\b(" + word + r")\s+of\s+(\d[\d,]*)\b", s, re.I)]

    def val(tok):
        tok = tok.lower().replace(",", "")
        return float(_WORDS[tok]) if tok in _WORDS else float(tok)
    effects = [(float(m.group(0)), m.group(0)) for m in re.finditer(r"(?:(?<![\d.])-)?\d+(?:\.\d+)?(?!\d|\s*%)", s)]
    out = {}
    for ev, den in (("ai", "n1i"), ("ci", "n2i")):
        if ev in served or den in served:
            hit = next(((e, n) for e, n in pairs if (ev not in served or abs(val(e) - float(served[ev])) < 1e-9)
                        and (den not in served or abs(val(n) - float(served[den])) < 1e-9)), None)
            if hit is None:
                return None
            if ev in served:
                out[ev] = hit[0].lower()
            if den in served:
                out[den] = hit[1]
    for k in ("effect", "ci_low", "ci_high"):
        if k in served:
            hit = next((tok for x, tok in effects if abs(x - float(served[k])) < 1e-9), None)
            if hit is None:
                return None
            out[k] = hit
    return out


def decide(cls, row):
    key = (row["slug"], _pmid(row))
    base = {"slug": row["slug"], "outcome": row["outcome"], "id": row["id"], "label": row.get("label"),
            "primary": row.get("primary"), "class": cls, "readers": _readers(row),
            "served": {k: row["served"][k] for k in SERVED_KEYS if (row.get("served") or {}).get(k) is not None},
            "span": (row.get("proposal") or {}).get("span") or None, "source_ref": row.get("source_ref"),
            "source_sha256": row.get("source_sha256")}
    if key in REFUSE_SIGNED:
        return dict(base, decision="REFUSE", kind="refused_on_evidence", basis="signed refusal: " + REFUSE_SIGNED[key])
    if key in KEEP_SIGNED or key in EPAR_SIGNED:
        # a signed keep signs THESE numbers, not the paper (codex v15cenf-cap-r1 #2): the row must serve exactly the
        # value the signed packet states, or generation stops -- never a signature for numbers nobody saw
        if base["served"] != SIGNED_SNAPSHOT[key]:
            raise SystemExit(f"{key}: served {base['served']} is not the signed {SIGNED_SNAPSHOT[key]} -- not admitted")
        return dict(base, decision="ADMIT", basis=(KEEP_SIGNED.get(key) or EPAR_SIGNED[key]))
    if key in CONVERSION_SIGNED:
        if not _conversion_ok(row):
            raise SystemExit(f"{key}: the served value is not the exact conversion of the stated RRR -- not admitted")
        return dict(base, decision="ADMIT", basis="signed conversion: the source states a relative risk REDUCTION; the "
                                                  "served RR is 1 - RRR with the bounds swapped (checked here)")
    if cls == "BIND_CONFIRMS_SERVED":
        return dict(base, decision="ADMIT", basis=f"{row['state']}: every served number is in the verbatim span of "
                                                  "the held abstract, read by codex and agy (and the adjudicator)")
    if cls == "REFUSE":
        rc = (row.get("proposal") or {}).get("reason_code")
        split = any(((row.get(r) or {}) or {}).get("decision") == "BIND" for r in ("codex", "agy", "adjudicator"))
        return dict(base, decision="REFUSE", kind="refused_on_evidence" if rc in ON_EVIDENCE else "abstain",
                    basis=f"panel refusal ({rc})" + ("; the panel was split, and a split panel refuses" if split else ""),
                    recommendation="refuse (rule: panel refused or disagreed)")
    if cls == "BIND_DIFFERS_FROM_SERVED":
        return dict(base, decision="REFUSE", kind="abstain",
                    basis="the panel bound different numbers from the served ones: the served number has no span",
                    recommendation="refuse the served number; the bound numbers are a candidate for a signed admission",
                    bound=(row.get("proposal") or {}).get("numbers"))
    if cls == "UNRESOLVED":
        # the signed rule refuses where the panel DISAGREES or the source is ABSENT. A row the bind checker could not
        # confirm (number words: 'four of 119') but on which every reader bound the served numbers, each stated in the
        # verbatim span, is neither: admitted, with the token that states each number recorded
        loc = locate(base["span"], base["served"]) if _readers_agree_on_served(row) else None
        if loc:
            return dict(base, decision="ADMIT", located=loc,
                        basis="panel unanimous on every served number (codex, agy, adjudicator); each served number is "
                              "stated in the verbatim span of the held abstract (located: " +
                              ", ".join(f"{k}={v}" for k, v in loc.items()) + "); the bind checker's number-word limit "
                              "is a logged V1 failure class, not a disagreement")
        return dict(base, decision="REFUSE", kind="abstain",
                    basis=f"no agreed, checkable reading ({row['state']}; checks: codex {row.get('codex_bind_check')}, "
                          f"agy {row.get('agy_bind_check')}, adjudicator {row.get('adjudicator_check')})",
                    recommendation="refuse now; human adjudication from the source (V1 freeze: no new reader rule)")
    if cls == "NEEDS_OPEN_SOURCE":
        return dict(base, decision="REFUSE", kind="abstain", basis="no open source text held: never sent to a model",
                    recommendation="refuse until an open source is held")
    raise SystemExit(f"unknown class {cls}")


def build():
    c = json.load(open(CLASSIFIED, encoding="utf-8"))
    rows = [decide(k, r) for k, v in c.items() for r in v]
    keys = [(r["slug"], r["outcome"], str(r["id"])) for r in rows]
    if len(set(keys)) != len(keys):
        raise SystemExit("two decisions for one row")
    # every signed key must have met its row (a signed decision that matches nothing is a defect, never a no-op)
    seen = {(r["slug"], str(r["id"]).replace("PMID ", "").strip()) for r in rows}
    missing = (set(REFUSE_SIGNED) | set(KEEP_SIGNED) | set(EPAR_SIGNED) | CONVERSION_SIGNED) - seen
    if missing:
        raise SystemExit(f"signed decisions that match no row: {sorted(missing)}")
    return {"_doc": __doc__.split("\n\n")[0], "signed": SIGNED, "classified_from": "outputs/m2_pretriage/classified.json",
            "n": len(rows), "admit": sum(r["decision"] == "ADMIT" for r in rows),
            "refuse": sum(r["decision"] == "REFUSE" for r in rows),
            "rows": sorted(rows, key=lambda r: (r["slug"], r["outcome"], str(r["id"])))}


def main():
    doc = build()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"{doc['n']} rows: ADMIT {doc['admit']}, REFUSE {doc['refuse']}")


if __name__ == "__main__":
    main()
