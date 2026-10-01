"""scripts/build_bundle.py must import on its own, from a clean process -- not only after some other module happens to have put
scripts/ on sys.path. It imports its sibling `contrast_order` bare; before V1.1 that resolved only when an earlier test file
(tests/test_bundle.py) had inserted scripts/ into sys.path, so `python -m scripts.freedom2_acceptance` could not run at all and
the parked FREEDOM-2 / F6 tests passed or failed by collection order. Plant: fired on the pre-fix producer."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_bundle_imports_in_a_clean_process_as_a_package_module():
    p = subprocess.run([sys.executable, "-c", "import scripts.build_bundle"], cwd=ROOT, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL, timeout=300)
    assert p.returncode == 0, p.stderr[-800:]
