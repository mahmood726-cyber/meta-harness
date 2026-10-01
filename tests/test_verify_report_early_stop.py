"""G2 (REPLAY): an outsider running the verifier must always see WHY a bundle is refused. A verification that stops early -- the
certificate pins no bundle (BUNDLE_DIGEST_MISMATCH), so no pool, anchors or binding states are computed -- crashed the text report with
KeyError: 'recomputed' before printing any FAIL line (2026-09-29, GLP-1 on the served 91f057a4 pages). Plant: copy a served bundle,
remove its pin, run the verifier's TEXT report as an outsider would."""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "glp1-ra-mace-t2d"


def test_an_unpinned_bundle_is_refused_with_its_reason_and_no_traceback(tmp_path):
    src = os.path.join(ROOT, "docs", "reviews", SLUG)
    dst = tmp_path / "docs" / "reviews" / SLUG
    shutil.copytree(src, dst)
    cert_path = dst / "CERTIFICATE.json"
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    cert.pop("bundle_core_sha256", None)                      # the outsider's case: no pin in the release
    cert_path.write_text(json.dumps(cert, indent=1) + "\n", encoding="utf-8", newline="\n")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "verify_bundle.py"), "--root", str(tmp_path / "docs"), "--slug", SLUG],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=600,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    out = p.stdout + p.stderr
    assert "Traceback" not in out, out[-2000:]
    assert "FAIL: BUNDLE_DIGEST_MISMATCH" in out, out[-2000:]
    assert "verdict PASS" not in out and p.returncode == 1
