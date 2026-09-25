"""Execute every sign command printed on FINAL_SIGNING_LIST.md exactly as printed, except:
  --by 'Mahmood' -> --by 'NR-LANE-TEST-NOT-A-SIGNATURE' and the PowerShell --basis (Read-Host ...) -> --basis 'test'.
Writes go to a TEMPORARY COPY of the ledger (cli.PATH redirected); the repository ledger is byte-checked unchanged.
Each written signature is then checked with the gate's own harness.result_changes.signature_problem on the block
the page renders, and must carry the judgement it names."""
import json
import re
import shlex
import shutil
import sys
import tempfile
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
from harness import result_changes  # noqa: E402
from scripts import countersign_result_change as cli  # noqa: E402

real = cli.PATH
before = real.read_bytes()
text = Path(r"C:/mh-lanes/nr/FINAL_SIGNING_LIST_2026-09-25.md").read_text(encoding="utf-8")
cmds = re.findall(r"^python scripts/countersign_result_change\.py sign .*$", text, re.M)
print(f"commands on the list: {len(cmds)}")
tmp = Path(tempfile.mkdtemp(prefix="nr-signcheck-")) / "result_changes.json"
shutil.copyfile(real, tmp)
cli.PATH = tmp
ok = 0
for c in cmds:
    c2 = c.replace("--by 'Mahmood'", "--by 'NR-LANE-TEST-NOT-A-SIGNATURE'")
    c2 = re.sub(r"--basis \(Read-Host '[^']*'\)", "--basis 'test'", c2)
    args = shlex.split(c2)[2:]
    try:
        cli.main(args)
    except SystemExit as e:
        print("  REFUSED:", c[:90], "->", e)
        continue
    idx = int(args[args.index("--notice-index") + 1])
    judgement = args[args.index("--judgement") + 1]
    n = json.loads(tmp.read_text(encoding="utf-8"))["notices"][idx]
    _, block, sha = cli._block_and_sha(n)
    problem = result_changes.signature_problem(cli._annotated(n), block)
    sig = n["reviewer_countersignature"]
    good = problem is None and sig.get("judgement_id") == judgement and sig["rendered_sha256"] == sha
    ok += good
    print(f"  {'OK ' if good else 'BAD'} index {idx} {n['slug']} / {n['outcome'][:40]}: {sig['state']} "
          f"judgement={sig.get('judgement_id')} problem={problem}")
cli.PATH = real
shutil.rmtree(tmp.parent)
print(f"{ok} of {len(cmds)} commands write a signature the gate accepts; repository ledger unchanged: "
      f"{real.read_bytes() == before}")
