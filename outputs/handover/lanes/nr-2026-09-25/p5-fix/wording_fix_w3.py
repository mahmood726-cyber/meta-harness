"""W3 in memory: a notice must not print a pooled number the page's own outcome withholds (claim state
HARMS_INCOMPLETE, claim.present false). Which of the 54 notices change hash under W1+W2+W3?"""
import json
import re
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
sys.path.insert(0, r"C:/mh-lanes/nr/work")
from harness import page, result_changes  # noqa: E402
from scripts import countersign_result_change as cli  # noqa: E402
import wording_fix as w  # noqa: E402  (runs W1+W2 report on import)

ledger = w.ledger
orig_annot = cli._annotated
_fmt_withheld = ("a pooled number is computed (k = {k}) but this page withholds it: {basis}")


def annotated_fixed(n):
    item = orig_annot(n)
    rev = W / "docs" / "reviews" / n["slug"] / "review.json"
    if rev.exists():
        o = next((o for o in json.loads(rev.read_text(encoding="utf-8")).get("outcomes") or []
                  if o.get("name") == n["outcome"]), None)
        claim = ((o or {}).get("result") or {}).get("claim") or {}
        if claim.get("state") == "HARMS_INCOMPLETE" and not claim.get("present") and (n.get("after") or {}).get("estimate") is not None:
            item["after_withheld"] = _fmt_withheld.format(k=(n.get("after") or {}).get("k"), basis=claim.get("basis"))
    return item


def block_fixed3(n):
    html = w.block_fixed(n)
    if n.get("after_withheld"):
        html = re.sub(r"Now: [^<]*?\. (?=(<strong>|The direction|No pooled|Left|Entered|Why))",
                      "Now: " + n["after_withheld"] + ". ", html, count=1)
    return html


result_changes.conclusion_changed, page.result_change_block, cli._annotated = w.cc_fixed, block_fixed3, annotated_fixed
after3 = [cli._block_and_sha(n)[2] for n in ledger]
texts = {i: " ".join(re.sub(r"<[^>]+>", " ", cli._block_and_sha(ledger[i])[1]).split()) for i in range(len(ledger))}
result_changes.conclusion_changed, page.result_change_block, cli._annotated = w.orig_cc, w.orig_block, orig_annot
changed = [w.audit.get((n["slug"], n["outcome"], n["when_utc"]), f"signed-before-24Sep[{i}]")
           for i, n in enumerate(ledger) if after3[i] != w.before_sha[i]]
print("\nW1+W2+W3 changes:", changed)
print("to-sign or ruling notices affected:", sorted(set(changed) & (w.SIGN | w.RULING)))
print("already-signed (13) affected:", [c for c in changed if c.startswith("signed-before")])
for aid in ("N06", "N27"):
    i = next(i for i, n in enumerate(ledger) if w.audit.get((n["slug"], n["outcome"], n["when_utc"])) == aid)
    print(f"\n{aid} as it would render:\n  " + texts[i][:400])
