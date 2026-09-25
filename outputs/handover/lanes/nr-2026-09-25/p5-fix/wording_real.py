"""With the real (temporarily patched) harness modules: which ledger notices change rendered hash vs the recorded
pre-patch hashes (computed first, from the unpatched files, into wording_before.json)?"""
import json
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
from scripts import countersign_result_change as cli  # noqa: E402

ledger = json.loads(cli.PATH.read_text(encoding="utf-8"))["notices"]
shas = [cli._block_and_sha(n)[2] for n in ledger]
out = Path(r"C:/mh-lanes/nr/work") / sys.argv[1]
out.write_text(json.dumps(shas))
if sys.argv[1] == "wording_after.json":
    before = json.loads((Path(r"C:/mh-lanes/nr/work") / "wording_before.json").read_text())
    audit = {(r["slug"], r["outcome"], r["when_utc"]): r["audit_id"]
             for r in json.loads((W / "registry/notice_adjudication.json").read_text(encoding="utf-8"))["notices"]}
    changed = [audit.get((n["slug"], n["outcome"], n["when_utc"]), f"signed-before-24Sep[{i}]")
               for i, n in enumerate(ledger) if before[i] != shas[i]]
    print("real patched modules: notices whose hash changes:", changed)
