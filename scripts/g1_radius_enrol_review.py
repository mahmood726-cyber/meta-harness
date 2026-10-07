"""Dual Codex review of the records whose rule decision the 7 Oct enrolment-verb fix ('were treated with') turns into an
INCLUDE (radius: outputs/search_audit/active/screen_fix_radius_enrol_verb*.json). Same instrument as
g1_screen_dual_codex.py (reader A gpt-6-astra, reader B gpt-5.5, adjudicator on disagreement / cannot-tell).

  python scripts/g1_radius_enrol_review.py [--run]   -> outputs/search_audit/active/radius_enrol_review.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import g1_screen_dual_codex as X  # noqa: E402
import g1_screen_dual_review as D  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

SA = ROOT / "outputs" / "search_audit" / "active"
EXP_TEXTS = Path(os.environ.get("MH_EXPANDED_TEXTS", str(Path.home() / "mh-expanded-texts")))
ACT_TEXTS = Path(os.environ.get("MH_ACTIVE_TEXTS", str(Path.home() / "mh-active-texts")))


def items():
    rad = json.load(open(SA / "screen_fix_radius_enrol_verb_expanded.json", encoding="utf-8"))
    act = {str(r["id"]): r for r in json.load(open(ACT_TEXTS / "records.json", encoding="utf-8"))}
    out = []
    for name, v in rad.items():
        slug = name.split("#")[0]
        texts = act if "#" in name else {str(r["id"]): r for r in
                                         json.load(open(EXP_TEXTS / f"{slug}.records.json", encoding="utf-8"))}
        for f in v["flips"]:
            if (f["new"] or [None])[0] != "include":
                continue                     # an exclude -> exclude change (X2 -> X3) changes no inclusion
            rec = texts[f["pmid"]]
            ht = D.P.held_text_screening(rec)
            out.append({"slug": slug, "record": f["pmid"], "rule_decision": "include", "rule": {"rule_id": "INCLUDE"},
                        "old_rule": f["old"], "item_id": f"{slug}::radius-enrol-verb::{f['pmid']}", "held_text": ht,
                        "held_sha256": D._sha(ht.encode("utf-8")),
                        "held_ref": f"pubmed:{f['pmid']} ({'comparator record fetched by PMID' if '#' in name else 'expanded search'})"})
    return out


def main(argv):
    its = items()
    have, known = D._have()
    if "--run" in argv:
        todo = [(pb, dg, m, f"G1 enrolment-verb radius review, {tag}, {it['item_id']}", None)
                for it in its for (pb, dg), m, tag in ((X.prompt_a(it), X.MODEL_A, "reader A"), (X.prompt_b(it), X.MODEL_B, "reader B"))
                if D._sha(pb) not in have]
        X._run_batch(todo, 5, known)
        have, known = D._have()
    rows = []
    for it in its:
        row = {k: it[k] for k in ("slug", "record", "rule_decision", "old_rule", "item_id", "held_ref", "held_sha256")}
        for tag, (pb, _) in (("A", X.prompt_a(it)), ("B", X.prompt_b(it))):
            hr = have.get(D._sha(pb))
            if hr:
                row[f"reader_{tag}"] = {"record": hr[0], "v": ms.verify_screening(D._claim(hr[1]), it["held_text"], "include")}
        a, b = ((row.get(f"reader_{t}") or {}).get("v", {}).get("model_decision") for t in "AB")
        if a and b and (a != b or "CANNOT_TELL" in (a, b)):
            pa, pb_ = (D._claim(have[D._sha(X.prompt_a(it)[0])][1]), D._claim(have[D._sha(X.prompt_b(it)[0])][1]))
            apb, adg = X.adj_prompt(it, pa, pb_)
            if "--run" in argv and D._sha(apb) not in have:
                X._run_batch([(apb, adg, X.MODEL_ADJ, f"G1 enrolment-verb radius review, adjudicator, {it['item_id']}", "high")],
                             1, known)
                have, known = D._have()
            hr = have.get(D._sha(apb))
            if hr:
                row["adjudicator"] = {"record": hr[0], "v": ms.verify_screening(D._claim(hr[1]), it["held_text"], "include")}
        adj = (row.get("adjudicator") or {}).get("v", {}).get("model_decision")
        row["final"] = (a if a == b and a in ("ELIGIBLE", "INELIGIBLE") else adj if adj in ("ELIGIBLE", "INELIGIBLE")
                        else "UNRESOLVED") if a and b else None
        rows.append(row)
        print(it["item_id"], a, b, adj, "->", row["final"])
    json.dump({"schema": 1, "rows": rows}, open(SA / "radius_enrol_review.json", "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1:])
