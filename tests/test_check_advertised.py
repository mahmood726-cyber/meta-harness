"""scripts/check_advertised.py must FAIL before it is trusted: an advertised served_path that is not in the tree, a served_url
that is not SITE_ROOT + served_path, and advertised bytes that disagree with the file each refuse AND name the entry; the real
bundle passes (the check is not merely strict). Plants run on a doctored COPY of the bundle against the real docs/ tree."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_advertised.py"
REAL = ROOT / "docs" / "reviews" / "glp1-ra-mace-t2d" / "BUNDLE.json"


@pytest.fixture(autouse=True)
def _reclaim_tmp_path(tmp_path):
    yield
    shutil.rmtree(tmp_path, ignore_errors=True)


def _run(*extra):
    p = subprocess.run([sys.executable, str(SCRIPT), *extra], capture_output=True, text=True, encoding="utf-8",
                       stdin=subprocess.DEVNULL, cwd=ROOT)
    return p.returncode, p.stdout


def _doctored(tmp_path, mutate):
    b = json.load(open(REAL, encoding="utf-8"))
    mutate(b)
    p = tmp_path / "BUNDLE.json"
    p.write_text(json.dumps(b), encoding="utf-8")
    return str(p)


def test_the_real_bundle_passes_and_the_limits_are_printed():
    rc, out = _run("--bundle", str(REAL))
    assert rc == 0 and "ADVERTISED-ARTEFACTS: PASS" in out, out[-600:]
    assert "LIMITS:" in out and "advertised-and-complete" in out         # a gate prints what it does not check


def test_an_advertised_path_missing_from_the_tree_refuses_and_is_named(tmp_path):
    bp = _doctored(tmp_path, lambda b: b["verifier"].update({"served_path": "scripts/verify_bundle_v2.py",
                                                             "served_url": "https://mahmood726-cyber.github.io/meta-harness/scripts/verify_bundle_v2.py"}))
    rc, out = _run("--bundle", bp)
    assert rc == 1 and "ADVERTISED-ARTEFACTS: REFUSED" in out, out[-600:]
    assert "verifier: advertised served_path 'scripts/verify_bundle_v2.py' is NOT IN THE TREE" in out


def test_a_served_url_that_is_not_site_root_plus_path_refuses_and_is_named(tmp_path):
    bp = _doctored(tmp_path, lambda b: b["verifier"].update(
        {"served_url": "https://mahmood726-cyber.github.io/meta-harness/reviews/glp1-ra-mace-t2d/verify_bundle.py"}))
    rc, out = _run("--bundle", bp)
    assert rc == 1 and "verifier: served_url" in out and "!= SITE_ROOT + served_path" in out, out[-600:]


def test_wrong_advertised_bytes_or_digest_refuse_and_are_named(tmp_path):
    bp = _doctored(tmp_path, lambda b: b["review_files"][0].update({"bytes": "1"}))
    rc, out = _run("--bundle", bp)
    assert rc == 1 and "review_files[0]" in out and "advertised bytes 1 !=" in out, out[-600:]
    bp = _doctored(tmp_path, lambda b: b["artefacts"][0].update({"sha256": "0" * 64}))
    rc, out = _run("--bundle", bp)
    assert rc == 1 and "artefacts[0]" in out and "advertised sha256 000000000000 !=" in out, out[-600:]


def test_an_unreadable_bundle_is_could_not_execute_not_a_refusal(tmp_path):
    rc, out = _run("--bundle", str(tmp_path / "missing.json"))
    assert rc == 2 and out.startswith("COULD-NOT-EXECUTE"), (rc, out[-300:])     # no verdict is not a verdict
    bad = tmp_path / "bad.json"; bad.write_text("{not json", encoding="utf-8")
    rc, out = _run("--bundle", str(bad))
    assert rc == 2 and out.startswith("COULD-NOT-EXECUTE"), (rc, out[-300:])


def test_a_withheld_artefact_that_advertises_a_url_refuses(tmp_path):
    def mutate(b):
        a = next(x for x in b["artefacts"] if x.get("state") != "SERVED")
        a["served_url"] = "https://mahmood726-cyber.github.io/meta-harness/cache/x.txt"
    bp = _doctored(tmp_path, mutate)
    rc, out = _run("--bundle", bp)
    assert rc == 1 and "but advertises a served path/url" in out, out[-600:]
