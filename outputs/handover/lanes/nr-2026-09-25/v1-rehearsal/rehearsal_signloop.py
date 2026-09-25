"""REHEARSAL: every sign command on the rehearsal signing list, replayed as printed except for a test signer and a
fixed basis, into a TEMPORARY ledger copy; then verify_notice_signatures.verify_ledger on that copy must say VALID for
every one. Also replays the OLD N28 command (B2 hash and judgement) against the changed candidate: it must refuse."""
import json
import re
import shlex
import shutil
import sys
import tempfile
from pathlib import Path

T = Path(r"C:/mh-lanes/nr/rehwt")
sys.path.insert(0, str(T))
from scripts import countersign_result_change as cli  # noqa: E402
from scripts import verify_notice_signatures as v  # noqa: E402

rows = json.loads(Path(r"C:/mh-lanes/nr/reh_list.json").read_text(encoding="utf-8"))["rows"]
real = cli.PATH
before = real.read_bytes()
tmp = Path(tempfile.mkdtemp(prefix="nr-reh-")) / "result_changes.json"
shutil.copyfile(real, tmp)
cli.PATH = tmp
refused = []


def run(cmd):
    c2 = cmd.replace("--by 'Mahmood'", "--by 'REHEARSAL-TEST-SIGNER'")
    c2 = re.sub(r"--basis \(Read-Host '[^']*'\)", "--basis 'rehearsal'", c2)
    cli.main(shlex.split(c2)[2:])


for r in rows:
    try:
        run(r["command"])
    except SystemExit as e:
        refused.append((r["audit_id"], str(e)[:120]))
old = ("python scripts/countersign_result_change.py sign 'pcsk9-mace' 'Major adverse cardiovascular events' "
       "--notice-index 40 --expect-digest {sha} --by 'Mahmood' --judgement B2-N28 --basis (Read-Host 'x')")
old_sha = json.loads(Path(r"C:/mh-lanes/nr/wt/outputs/handover/lanes/nr-2026-09-25/signing_list.json")
                     .read_text(encoding="utf-8"))["rows"]
old_sha = next(x["rendered_block_sha256"] for x in old_sha if x["audit_id"] == "N28")
shutil.copyfile(real, tmp.with_name("fresh.json"))
cli.PATH = tmp.with_name("fresh.json")
try:
    run(old.format(sha=old_sha))
    old_result = "ACCEPTED (wrong)"
except SystemExit as e:
    old_result = "REFUSED: " + str(e)[:140]
cli.PATH = tmp
audit = json.loads((T / "registry/notice_adjudication.json").read_text(encoding="utf-8"))
verdicts = v.verify_ledger(json.loads(tmp.read_text(encoding="utf-8"))["notices"], audit)
cli.PATH = real
shutil.rmtree(tmp.parent)
from collections import Counter
print(f"commands replayed: {len(rows)}; refused: {len(refused)} {refused[:3]}")
print("verifier on the signed copy:", dict(Counter(x['verdict'] for x in verdicts)))
print("old N28 command (B2 hash + judgement) against the changed candidate:", old_result)
print("repository ledger unchanged:", real.read_bytes() == before)
