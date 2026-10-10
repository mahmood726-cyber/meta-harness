"""V14-04 (signed "sign v14", option A -- CONDITIONAL): admit FLOW to glp1-ra-mace-t2d 3-point MACE.

Applied only if the topic's G1 state is unchanged before/after (otherwise the item returns to Mahmood); the captain
checks that with scripts/g1_tracker.py on the trial build before keeping this commit.

Typed, reproducible, nothing hand-entered:
  1. fetch the FLOW prespecified CV analysis (PMID 39211948, Eur Heart J 2024, PMC11931213) through the harness's own
     PMC reader (harness.fetch._pmc_fulltext), whitespace-collapsed, and REFUSE unless its PMC permissions carry a
     Creative Commons licence (D8; the statement is recorded verbatim) and both signed spans are in it verbatim;
  2. hold it at outputs/held_fulltexts/pmc_PMC11931213.txt (+ manifest.json with licence statement and sha256);
  3. regex the HR out of the signed result span and write a canonical extracted_effect row into
     cache/glp1-ra-mace-t2d/verified_effects.json under FLOW's pool id 38785209 (NCT03819153).
The Ozempic US label (209637s025, held) independently prints HR 0.82 (0.68-0.98), 212/1767 v 254/1766.

    python scripts/v14_04_flow_mace.py [--offline]
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT]
SLUG = "glp1-ra-mace-t2d"
PID = "38785209"
PMID, PMCID, NCT = "39211948", "PMC11931213", "NCT03819153"
ITEM = "V14-04"
OUTCOME = "3-point major adverse cardiovascular events"
HELD_DIR = os.path.join(ROOT, "outputs", "held_fulltexts")
HELD_NAME = f"pmc_{PMCID}.txt"
DEF_SPAN = "the composite of CV death, non-fatal MI or non-fatal stroke (hereafter CV death/MI/stroke)"
RES_SPAN = ("In the overall population, semaglutide reduced rates of the composite of CV death/MI/stroke compared with "
            "placebo [HR 0.82 (95% CI 0.68–0.98)]")
_HR = re.compile(r"HR\s+(\d+\.\d+)\s*\(95% CI\s+(\d+\.\d+)\s*[–-]\s*(\d+\.\d+)\)")


def _licence(http, fetch):
    x = http.get_text(f"{fetch.EUTILS}/efetch.fcgi", {"db": "pmc", "id": PMCID, "retmode": "xml",
                                                      "tool": "meta-harness", "email": "meta-harness@example.org"})
    perm = " ".join(re.findall(r"<permissions>.*?</permissions>", x, re.S))
    stmt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", perm)).strip()
    m = re.search(r"creativecommons\.org/(licenses/by/\d\.\d|publicdomain/zero/\d\.\d)/", perm)
    if not m:
        raise SystemExit("REFUSED: PMC permissions carry no CC BY / CC0 licence (D8)")
    return m.group(1), stmt


def main(argv):
    offline = "--offline" in argv
    path = os.path.join(HELD_DIR, HELD_NAME)
    mp = os.path.join(HELD_DIR, "manifest.json")
    man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"documents": {}}
    if offline:
        text = open(path, encoding="utf-8", newline="").read()
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != man["documents"][HELD_NAME]["sha256"]:
            raise SystemExit("REFUSED: held text does not match its manifest digest")
    else:
        from harness import fetch, http
        lic, stmt = _licence(http, fetch)
        text = re.sub(r"\s+", " ", fetch._pmc_fulltext(PMID) or "").strip()
    if DEF_SPAN not in text or RES_SPAN not in text:
        raise SystemExit("REFUSED: a signed span is not verbatim in the held text")
    m = _HR.search(RES_SPAN)
    e, lo, hi = (float(x) for x in m.groups())
    if not lo < e < hi:
        raise SystemExit("REFUSED: effect outside its interval")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if not offline:
        os.makedirs(HELD_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        man["documents"][HELD_NAME] = {
            "pmid": PMID, "pmcid": PMCID, "nct": NCT, "source": f"harness.fetch._pmc_fulltext('{PMID}') ({PMCID})",
            "licence": lic, "licence_statement": stmt[:400],
            "normalisation": "the harness's PMC OA reader output, whitespace collapsed", "sha256": sha,
            "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "held_for": f"{ITEM} {SLUG} '{OUTCOME}'"}
        with open(mp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(man, f, indent=2, sort_keys=True)
            f.write("\n")
    row = {"kind": "extracted_effect", "outcome": OUTCOME, "scale": "HR", "override": True,
           "effect": e, "ci_low": lo, "ci_high": hi,
           "source": (f"FLOW (PMID {PMID}, {NCT}) prespecified CV analysis, PMC OA full text ({PMCID}, CC BY): "
                      f"definition '{DEF_SPAN}'; result HR {e:.2f} ({lo:.2f}-{hi:.2f}), overall population"),
           "verification": f"{ITEM}: both spans verbatim in the held CC BY text (sha256 {sha})",
           "source_span": RES_SPAN, "document_ref": f"outputs/held_fulltexts/{HELD_NAME}", "source_level": 1,
           "provenance": "fulltext_verified",
           "reason": (f"{ITEM} (signed by Mahmood, 'sign v14', conditional on an unchanged G1 state): FLOW eligible "
                      f"under B-prime per protocol line 79 (V14-07); binding lane review10_flow_elixa, two recorded "
                      f"readers agree.")}
    vpath = os.path.join(ROOT, "cache", SLUG, "verified_effects.json")
    data = json.load(open(vpath, encoding="utf-8"))
    cur = data.get(PID)
    cur = [] if cur is None else (cur if isinstance(cur, list) else [cur])
    data[PID] = [x for x in cur if x.get("outcome") != OUTCOME] + [row]
    with open(vpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"effect": e, "ci_low": lo, "ci_high": hi, "sha256": sha}))


if __name__ == "__main__":
    main(sys.argv[1:])
