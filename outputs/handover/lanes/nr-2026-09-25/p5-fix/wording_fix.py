"""Proposed notice-wording fix (W1, W2), executed in memory: which of the 54 ledger notices change rendered hash?
Only the notices whose wording is wrong may change; every to-sign notice and every already-signed notice must not."""
import json
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
from harness import page, result_changes  # noqa: E402
from scripts import countersign_result_change as cli  # noqa: E402

ledger = json.loads(cli.PATH.read_text(encoding="utf-8"))["notices"]
audit = {(r["slug"], r["outcome"], r["when_utc"]): r["audit_id"]
         for r in json.loads((W / "registry/notice_adjudication.json").read_text(encoding="utf-8"))["notices"]}
before_sha = [cli._block_and_sha(n)[2] for n in ledger]

orig_cc, orig_block = result_changes.conclusion_changed, page.result_change_block
NO_ESTIMATE_EITHER = ("No pooled estimate was served before and none is served now; only the candidate trials "
                      "changed, and no conclusion is withdrawn.")


def cc_fixed(before, after, scale):
    b, a = result_changes.significance(before, scale), result_changes.significance(after, scale)
    if before.get("estimate") is None and after.get("estimate") is None:
        return None  # W1: nothing was served, so nothing is withdrawn (the block says so, see block_fixed)
    if b is None and before.get("estimate") is not None and a == "excludes_null":
        return ("an interval is now served and it excludes the null: a difference is now claimed; no interval "
                "was served before")  # W2
    return orig_cc(before, after, scale)


def block_fixed(n):
    html = orig_block(n)
    b, a = n.get("before") or {}, n.get("after") or {}
    if b.get("estimate") is None and a.get("estimate") is None:
        html = html.replace("The direction of the estimate is unchanged. ", NO_ESTIMATE_EITHER + " ", 1)
    return html


result_changes.conclusion_changed, page.result_change_block = cc_fixed, block_fixed
after_sha = [cli._block_and_sha(n)[2] for n in ledger]
result_changes.conclusion_changed, page.result_change_block = orig_cc, orig_block

SIGN = {"N02", "N03", "N04", "N05", "N07", "N10", "N11", "N12", "N16", "N22", "N24", "N31", "N33", "N34", "N36", "N37", "N41"}
RULING = {"N08", "N23"}
changed = []
for i, n in enumerate(ledger):
    aid = audit.get((n["slug"], n["outcome"], n["when_utc"]), f"signed-before-24Sep[{i}]")
    if before_sha[i] != after_sha[i]:
        changed.append(aid)
print("notices whose rendered hash changes under W1+W2:", changed)
print("to-sign or ruling notices affected:", sorted(set(changed) & (SIGN | RULING)))
print("already-signed (13) notices affected:", [c for c in changed if c.startswith("signed-before")])
for aid in ("N28", "N30"):
    i = next(i for i, n in enumerate(ledger) if audit.get((n["slug"], n["outcome"], n["when_utc"])) == aid)
    result_changes.conclusion_changed, page.result_change_block = cc_fixed, block_fixed
    import re
    txt = re.sub(r"<[^>]+>", " ", cli._block_and_sha(ledger[i])[1])
    result_changes.conclusion_changed, page.result_change_block = orig_cc, orig_block
    print(f"\n{aid} as it would render:\n  " + " ".join(txt.split())[:420])
