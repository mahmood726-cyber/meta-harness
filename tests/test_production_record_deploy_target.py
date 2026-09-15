"""The deploy job has no checkout; production_record.py must name its target from the manifest there, and must still
refuse a tampered artifact. 2026-09-15: 14 consecutive main deploys died on ModuleNotFoundError(harness) before any
check ran -- verify green, site stale -- and with harness shipped they would have died on `ref not resolvable: HEAD`."""
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sim(tmp_path, tamper: bool):
    pr = tmp_path / "pr"
    (pr / "docs" / "_production").mkdir(parents=True)
    (pr / "scripts").mkdir()
    (pr / "harness").mkdir()
    shutil.copy(os.path.join(ROOT, "scripts", "production_record.py"), pr / "scripts" / "production_record.py")
    for name in ("__init__.py", "target.py"):
        shutil.copy(os.path.join(ROOT, "harness", name), pr / "harness" / name)
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<p>served</p>\n", encoding="utf-8")
    (site / "a.json").write_text("{}\n", encoding="utf-8")
    import hashlib
    files = {rel: hashlib.sha256((site / rel).read_bytes()).hexdigest() for rel in ("index.html", "a.json")}
    man = {"commit_sha": "0123456789abcdef0123456789abcdef01234567", "files": files, "n_files": 2}
    (pr / "docs" / "_production" / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
    if tamper:
        (site / "index.html").write_text("<p>served</p>\n<!-- tampered -->\n", encoding="utf-8")
    tar_path = tmp_path / "artifact.tar"
    with tarfile.open(tar_path, "w") as tf:
        for rel in files:
            tf.add(site / rel, arcname="./" + rel)
    proc = subprocess.run([sys.executable, str(pr / "scripts" / "production_record.py"), "check-artifact",
                           "--manifest", str(pr / "docs" / "_production" / "manifest.json"), "--tar", str(tar_path)],
                          cwd=tmp_path, capture_output=True, text=True, encoding="utf-8")
    return proc


def test_deploy_job_without_checkout_names_its_target_from_the_manifest_and_passes_an_intact_artifact(tmp_path):
    assert not (tmp_path / ".git").exists()
    proc = _sim(tmp_path, tamper=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "TARGET production_record.check_artifact: head=0123456789abcdef0123456789abcdef01234567 base=none tree=artifact:manifest-sha256=" in proc.stdout
    assert "artifact == manifest: 2 files" in proc.stdout


def test_deploy_job_without_checkout_still_refuses_a_tampered_artifact(tmp_path):
    proc = _sim(tmp_path, tamper=True)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "ARTIFACT REFUSED" in proc.stdout and "index.html" in proc.stdout


def test_workflow_ships_harness_target_with_the_production_record_artifact():
    text = io.open(os.path.join(ROOT, ".github", "workflows", "verify.yml"), encoding="utf-8").read()
    block = text.split("name: production-record", 1)[1].split("retention-days", 1)[0]
    assert "harness/__init__.py" in block and "harness/target.py" in block and "scripts/production_record.py" in block
