"""Run the cheap verify_all limbs against a clone before paying for the 12-minute hook.
usage: python precheck.py <clone_root> [limb ...]
Prints each limb's verdict line; exit 1 if any limb is not PASS. Never a substitute for the hook."""
import importlib.util
import os
import sys

root = os.path.abspath(sys.argv[1])
os.chdir(root)
sys.path.insert(0, root)
spec = importlib.util.spec_from_file_location("verify_all", os.path.join(root, "scripts", "verify_all.py"))
va = importlib.util.module_from_spec(spec)
spec.loader.exec_module(va)
want = sys.argv[2:] or ["limb_index_currency", "limb_leak_scan", "limb_fixstate", "limb_honest_ratchet",
                        "limb_gate_scorecard", "limb_gate_gaps", "limb_gate_every_page"]
bad = 0
for name in want:
    fn = getattr(va, name)
    verdict, detail = fn()
    first = str(detail).splitlines()[0] if detail else ""
    print(f"{name:26s} {verdict}  {first[:150]}")
    if verdict != va.PASS:
        bad += 1
        for line in str(detail).splitlines()[1:12]:
            print("      " + line[:200])
sys.exit(1 if bad else 0)
