"""The rebuild-invariance gate must FAIL before it passes: a dropped block, two added blocks, and one added block that is not the
expected one each refuse; the unchanged tree passes with 0 additions. Runs on a doctored COPY of the base's docs/reviews.

The copy equals the base BY CONSTRUCTION: it is read from the base ref the script itself resolves (harness.honest_ratchet.
_resolve_base -- merge-base with origin/main on a branch, HEAD~1 on main), never from the working tree and never from a second,
independently computed base. The plant is a SYNTHETIC block whose marker occurs on no base, so the counts below do not depend on
which notices the base already carries. 2026-09-21: an earlier version computed its own `merge-base HEAD origin/main` and injected
the real PRE-RELEASE block; on the branch both bases said 8b1fb37d and the tests passed, on main the script fell back to HEAD~1
while the test's base was HEAD (which carries the block), the copy kept a block the base lacked, and five tests failed on a commit
that had passed the same tests an hour earlier -- a control anchored to the live corpus, retiring itself."""
import shutil
import subprocess
import sys

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import harness.honest_ratchet as hr  # noqa: E402

SCRIPT = ROOT / "scripts" / "rebuild_invariance.py"
PLANT = "<div class='absent' data-invariance-plant='PLANT'><strong>PLANT — on no base.</strong> planted</div>"
PLANT_TEXT = "PLANT — on no base."
PLANT_MARKER = "data-invariance-plant='PLANT'"
OTHER = "<div class='absent'><strong>SOME OTHER NOTICE.</strong> planted</div>"


@pytest.fixture(autouse=True)
def _reclaim_tmp_path(tmp_path):
    """Test hygiene: reclaim this test's tmp_path in teardown -- AFTER the test body and all its assertions -- so a session's basetemp
    peaks at one fixture (~60-150 MB) instead of the sum (~2.8 GB measured 2026-09-20). Nothing a test asserts depends on the
    fixture surviving teardown; equivalence was measured file by file with and without this fixture (identical verdicts and counts)."""
    yield
    import shutil
    shutil.rmtree(tmp_path, ignore_errors=True)


def _git_bytes(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, stdin=subprocess.DEVNULL).stdout


def _base_ref():
    """The SAME base the script will compare against -- one resolution, the script's own."""
    base, _source, err = hr._resolve_base(ROOT, None)
    assert base, err
    return base


def _copy_docs(tmp_path):
    """A copy of docs/reviews that EQUALS the base by construction: every index.html and review.json is read from the base ref
    with `git show`, so a run with no plants is a diff of nothing, whatever the working tree carries."""
    base = _base_ref()
    dst = tmp_path / "docs" / "reviews"
    dst.mkdir(parents=True)
    names = _git_bytes("ls-tree", "-r", "--name-only", base, "--", "docs/reviews").decode("utf-8").split("\n")
    slugs = sorted({n.split("/")[2] for n in names if n.startswith("docs/reviews/") and n.endswith("/index.html")})
    assert slugs, f"no review pages at base {base}"
    for slug in slugs:
        (dst / slug).mkdir()
        (dst / slug / "index.html").write_bytes(_git_bytes("show", f"{base}:docs/reviews/{slug}/index.html"))
        (dst / slug / "review.json").write_bytes(_git_bytes("show", f"{base}:docs/reviews/{slug}/review.json"))
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
    s = p.read_text(encoding="utf-8")
    i = s.rfind("<div class='absent'", 0, s.find("STALE"))            # the STALE notice, wherever it sits among the page's blocks
    j = s.find("</div>", i) + 6
    p.write_text(s[:i] + s[j:], encoding="utf-8", newline="")
    rc, out = _run(docs, "--expect-added", "0")
    assert rc == 1 and "31 of 32 pages PASS" in out and "FAIL: ['sacubitril-valsartan-hfref']" in out
    assert "LOST   [absent] STALE" in out


def test_two_added_blocks_refuse_when_one_is_expected(tmp_path):
    docs = _copy_docs(tmp_path)
    for d in (docs / "reviews").iterdir():
        _inject(docs, d.name, PLANT)
    _inject(docs, "glp1-ra-mace-t2d", OTHER)                     # one page adds two
    rc, out = _run(docs, "--expect-added", "1", "--added-text", PLANT_TEXT, "--added-marker", PLANT_MARKER)
    assert rc == 1 and "31 of 32 pages PASS" in out and "FAIL: ['glp1-ra-mace-t2d']" in out
    assert "added 2 block(s), expected 1" in out


def test_one_added_block_that_is_not_the_expected_one_refuses(tmp_path):
    docs = _copy_docs(tmp_path)
    for d in (docs / "reviews").iterdir():
        _inject(docs, d.name, PLANT)
    p = docs / "reviews" / "sacubitril-valsartan-hfref" / "index.html"
    p.write_text(p.read_text(encoding="utf-8").replace(PLANT, OTHER, 1), encoding="utf-8", newline="")   # right count, wrong block
    rc, out = _run(docs, "--expect-added", "1", "--added-text", PLANT_TEXT, "--added-marker", PLANT_MARKER)
    assert rc == 1 and "FAIL: ['sacubitril-valsartan-hfref']" in out
    assert "is not the expected one" in out and "marker" in out


def test_all_pages_with_exactly_the_expected_block_pass_and_a_declared_exception_is_printed(tmp_path):
    docs = _copy_docs(tmp_path)
    for d in (docs / "reviews").iterdir():
        _inject(docs, d.name, PLANT)
    _inject(docs, "dapagliflozin-hfpef-hosp", OTHER)
    rc, out = _run(docs, "--expect-added", "1", "--added-text", PLANT_TEXT, "--added-marker", PLANT_MARKER,
                   "--exception", "dapagliflozin-hfpef-hosp=2:withdrawn page gains the consumer-linked hazard block")
    assert rc == 0 and "32 of 32 pages PASS" in out, out[-800:]
    assert "[EXCEPTION n=2: withdrawn page gains the consumer-linked hazard block]" in out
