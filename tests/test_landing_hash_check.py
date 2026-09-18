"""The landing hash gate must read the review OBJECT, never the wrapper.

PLANT (proven pre-fix): a landing that changes ONLY the page wrapper (index.html + manifest html_sha256) while every review
object is byte-identical (review.json, manifest review_sha256) must make the gate report FAILURE. The pre-fix script
(scripts/landing_hash_check.py at 237e9094, executed from git) reported it MOVED and exited 0 -- the container-as-contents
defect. Measured live the same night: 237e9094 -> 75cc9a46 moved glp1's html_sha256 (fede8d29 -> 72fadf26) with review_sha256
unchanged (98726cc1) and the chain logged "32 MOVED".

Each test builds a throwaway git repository with two commits; nothing touches the real repository.
"""
import json
import os
import subprocess
import sys
import types

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX_SHA = "237e90946f5b257265b0a3b1c986a8907d12eded"


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _write(cwd, rel, text):
    p = os.path.join(cwd, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _repo(tmp_path, slugs=("glp1", "other")):
    cwd = str(tmp_path / "repo")
    os.makedirs(cwd)
    _git(cwd, "init", "-q")
    _git(cwd, "config", "user.email", "t@t")
    _git(cwd, "config", "user.name", "t")
    _git(cwd, "config", "core.hooksPath", os.devnull)
    for s in slugs:
        _write(cwd, f"docs/reviews/{s}/review.json", json.dumps({"slug": s, "k": 8}))
        _write(cwd, f"docs/reviews/{s}/index.html", f"<html>{s} v1</html>")
        _write(cwd, f"docs/reviews/{s}/manifest.json", json.dumps({"review_sha256": f"aaaa{s}" * 4, "html_sha256": f"h1{s}" * 6}))
    _git(cwd, "add", "-A")
    _git(cwd, "commit", "-q", "-m", "A")
    a = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True).stdout.strip()
    return cwd, a


def _commit(cwd, msg):
    _git(cwd, "add", "-A")
    _git(cwd, "commit", "-q", "-m", msg)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True).stdout.strip()


def _wrapper_only_landing(cwd, slug="glp1"):
    """Commit B: the page bytes change, the review object does not."""
    _write(cwd, f"docs/reviews/{slug}/index.html", f"<html>{slug} v2 -- new banner, same object</html>")
    _write(cwd, f"docs/reviews/{slug}/manifest.json", json.dumps({"review_sha256": f"aaaa{slug}" * 4, "html_sha256": f"h2{slug}" * 6}))
    return _commit(cwd, "B wrapper only")


def _object_landing(cwd, slug="glp1"):
    _write(cwd, f"docs/reviews/{slug}/review.json", json.dumps({"slug": slug, "k": 7}))
    _write(cwd, f"docs/reviews/{slug}/index.html", f"<html>{slug} v2 k=7</html>")
    _write(cwd, f"docs/reviews/{slug}/manifest.json", json.dumps({"review_sha256": f"bbbb{slug}" * 4, "html_sha256": f"h2{slug}" * 6}))
    return _commit(cwd, "B object moved")


def _run_live(cwd, *args):
    p = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "landing_hash_check.py"), *args],
                       cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout + p.stderr


def _run_prefix(cwd, *args):
    """The gate as it was at 237e9094, read from git and executed in-process against the scratch repo."""
    src = subprocess.run(["git", "show", f"{PREFIX_SHA}:scripts/landing_hash_check.py"], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8").stdout
    assert "(ra != rb) or (ha != hb)" in src, "pre-fix source no longer has the defect line; re-pin the plant"
    mod = types.ModuleType("_prefix_gate")
    exec(compile(src, "landing_hash_check@237e9094", "exec"), mod.__dict__)
    printed = []
    mod.print = lambda *a, **k: printed.append(" ".join(str(x) for x in a))
    here = os.getcwd()
    os.chdir(cwd)
    try:
        code = mod.main(list(args))
    finally:
        os.chdir(here)
    return code, "\n".join(printed)


def test_PLANT_prefix_gate_certified_a_wrapper_only_landing(tmp_path):
    cwd, a = _repo(tmp_path)
    b = _wrapper_only_landing(cwd)
    code, out = _run_prefix(cwd, a, b)
    assert code == 0, out                      # the defect: PASS
    assert "MOVED" in out and "UNCHANGED" not in out, out


def test_wrapper_only_landing_is_refused(tmp_path):
    cwd, a = _repo(tmp_path)
    b = _wrapper_only_landing(cwd)
    code, out = _run_live(cwd, a, b)
    assert code == 1, out
    assert "glp1" in out and "UNCHANGED" in out and "REFUSED" in out, out
    assert "aaaaglp1" in out, out             # the identical object hash is NAMED, old and new
    assert "MOVED" not in out.replace("moved its review_sha256", ""), out


def test_object_landing_passes_and_names_both_hashes(tmp_path):
    cwd, a = _repo(tmp_path)
    b = _object_landing(cwd)
    code, out = _run_live(cwd, a, b)
    assert code == 0, out
    line = next(l for l in out.splitlines() if l.strip().startswith("glp1"))
    assert "aaaaglp1" in line and "bbbbglp1" in line and "MOVED" in line, line
    assert "html" in line and "informational" in line, line


def test_require_change_needs_the_object_to_move_not_just_a_touch(tmp_path):
    cwd, a = _repo(tmp_path)
    b = _wrapper_only_landing(cwd)                       # glp1 touched, object identical
    code, out = _run_live(cwd, a, b, "--require-change", "glp1")
    assert code == 1 and "REQUIRED" in out, out
    # pre-fix: --require-change only checked that the slug was touched
    code_pre, out_pre = _run_prefix(cwd, a, b, "--require-change", "glp1")
    assert code_pre == 0, out_pre


def test_require_change_on_an_untouched_review_is_refused(tmp_path):
    cwd, a = _repo(tmp_path)
    b = _object_landing(cwd, slug="other")
    code, out = _run_live(cwd, a, b, "--require-change", "glp1")
    assert code == 1 and "glp1" in out and "REQUIRED" in out, out


def test_declared_wrapper_only_is_the_only_pass_for_a_renderer_change(tmp_path):
    cwd, a = _repo(tmp_path)
    b = _wrapper_only_landing(cwd)
    code, out = _run_live(cwd, a, b, "--allow-wrapper-only", "glp1")
    assert code == 0 and "WRAPPER-ONLY" in out, out
    code, out = _run_live(cwd, a, b, "--allow-wrapper-only", "glp1", "--require-change", "glp1")
    assert code == 1, out


def test_no_aggregate_verdict_line(tmp_path):
    """The verdict is per review; the summary never says 'N MOVED'."""
    cwd, a = _repo(tmp_path)
    b = _object_landing(cwd)
    _, out = _run_live(cwd, a, b)
    import re
    assert not re.search(r"\b\d+ (review\(s\) )?MOVED\b", out), out
