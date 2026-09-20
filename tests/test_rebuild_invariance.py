"""The rebuild-invariance gate must FAIL before it passes: a dropped block, two added blocks, and one added block that is not the
expected one each refuse; the unchanged tree passes with 0 additions. Runs on a doctored COPY of docs/reviews against the real base."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rebuild_invariance.py"
PRE = "<div class='absent' data-release-status='PRE-RELEASE'><strong>PRE-RELEASE — not the reference release.</strong> planted</div>"
OTHER = "<div class='absent'><strong>SOME OTHER NOTICE.</strong> planted</div>"


def _copy_docs(tmp_path):
    dst = tmp_path / "docs" / "reviews"
    dst.mkdir(parents=True)
    for d in sorted((ROOT / "docs" / "reviews").iterdir()):
        if (d / "index.html").exists():
            (dst / d.name).mkdir()
            for name in ("index.html", "review.json"):
                shutil.copyfile(d / name, dst / d.name / name)
    return tmp_path / "docs"


def _run(docs, *extra):
    p = subprocess.run([sys.executable, str(SCRIPT), "--docs", str(docs), *extra], capture_output=True, text=True, encoding="utf-8",
                       stdin=subprocess.DEVNULL, cwd=ROOT)
    return p.returncode, p.stdout


def _inject(docs, slug, html_fragment):
    p = docs / "reviews" / slug / "index.html"
    s = p.read_text(encoding="utf-8")
    i = s.find("<h2")
    p.write_text(s[:i] + html_fragment + s[i:], encoding="utf-8", newline="")


def test_unchanged_tree_passes_with_zero_additions(tmp_path):
    docs = _copy_docs(tmp_path)
    rc, out = _run(docs, "--expect-added", "0")
    assert rc == 0 and "32 of 32 pages PASS" in out, out[-600:]
    assert "sacubitril-valsartan-hfref=PASS" in out           # ARNI named in the output, not implied by the total


def test_a_dropped_block_refuses(tmp_path):
    docs = _copy_docs(tmp_path)
    p = docs / "reviews" / "sacubitril-valsartan-hfref" / "index.html"
    s = p.read_text(encoding="utf-8"); i = s.find("<div class='absent'"); j = s.find("</div>", i) + 6
    p.write_text(s[:i] + s[j:], encoding="utf-8", newline="")
    rc, out = _run(docs, "--expect-added", "0")
    assert rc == 1 and "31 of 32 pages PASS" in out and "FAIL: ['sacubitril-valsartan-hfref']" in out
    assert "LOST   [absent] STALE" in out


def test_two_added_blocks_refuse_when_one_is_expected(tmp_path):
    docs = _copy_docs(tmp_path)
    for d in (docs / "reviews").iterdir():
        _inject(docs, d.name, PRE)
    _inject(docs, "glp1-ra-mace-t2d", OTHER)                     # one page adds two
    rc, out = _run(docs, "--expect-added", "1", "--added-text", "PRE-RELEASE — not the reference release.", "--added-marker", "data-release-status='PRE-RELEASE'")
    assert rc == 1 and "31 of 32 pages PASS" in out and "FAIL: ['glp1-ra-mace-t2d']" in out
    assert "added 2 block(s), expected 1" in out


def test_one_added_block_that_is_not_the_expected_one_refuses(tmp_path):
    docs = _copy_docs(tmp_path)
    for d in (docs / "reviews").iterdir():
        _inject(docs, d.name, PRE)
    p = docs / "reviews" / "sacubitril-valsartan-hfref" / "index.html"
    p.write_text(p.read_text(encoding="utf-8").replace(PRE, OTHER, 1), encoding="utf-8", newline="")   # right count, wrong block
    rc, out = _run(docs, "--expect-added", "1", "--added-text", "PRE-RELEASE — not the reference release.", "--added-marker", "data-release-status='PRE-RELEASE'")
    assert rc == 1 and "FAIL: ['sacubitril-valsartan-hfref']" in out
    assert "is not the expected one" in out and "marker" in out


def test_all_pages_with_exactly_the_expected_block_pass_and_a_declared_exception_is_printed(tmp_path):
    docs = _copy_docs(tmp_path)
    for d in (docs / "reviews").iterdir():
        _inject(docs, d.name, PRE)
    _inject(docs, "dapagliflozin-hfpef-hosp", OTHER)
    rc, out = _run(docs, "--expect-added", "1", "--added-text", "PRE-RELEASE — not the reference release.", "--added-marker", "data-release-status='PRE-RELEASE'",
                   "--exception", "dapagliflozin-hfpef-hosp=2:withdrawn page gains the consumer-linked hazard block")
    assert rc == 0 and "32 of 32 pages PASS" in out, out[-800:]
    assert "[EXCEPTION n=2: withdrawn page gains the consumer-linked hazard block]" in out
