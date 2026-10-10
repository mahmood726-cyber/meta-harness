"""What a reader who DOWNLOADS the harness is told to run must work for what they downloaded (starter-kit check, pva
2026-10-09, lane_status/starter_kit.md).

Measured: on a no-.git export of main 018563127, `scripts/replay_offline.py dpp4-mace-t2d` PASSED and
`scripts/reproduce_review.py dpp4-mace-t2d` FAILED ("fatal: not a git repository"). The Reproduce tab linked main.zip and
told the downloader to run the reproduce_review command, so every zip reader was handed a command that cannot pass.
"""
from __future__ import annotations

import re
from pathlib import Path

from harness import review_tabs as T

ROOT = Path(__file__).resolve().parents[1]
ZIP = "archive/refs/heads/main.zip"
SLUGS = sorted(p.name for p in (ROOT / "docs" / "reviews").iterdir() if (p / "manifest.json").is_file())


def _zip_command(html: str) -> str:
    """The first <pre> block after the first main.zip link: the command the zip reader is given."""
    at = html.find(ZIP)
    assert at >= 0, "the tab no longer links the zip download"
    m = re.search(r"<pre>(.*?)</pre>", html[at:], re.S)
    return m.group(1) if m else ""


def test_the_zip_reader_is_sent_to_the_offline_replay_not_the_git_replay():
    with_bundle = [s for s in SLUGS if (ROOT / "docs" / "reviews" / s / "BUNDLE.json").is_file()]
    without = [s for s in SLUGS if s not in with_bundle]
    assert with_bundle and without, "need both kinds of topic to test both renderings"
    for slug in (with_bundle[0], without[0]):
        html = T.reproduce_additions({"slug": slug})
        cmd = _zip_command(html)
        assert f"scripts/replay_offline.py {slug}" in cmd, (slug, cmd)
        assert "reproduce_review.py" not in cmd and "git clone" not in cmd, (slug, cmd)
        # the git route is still offered, and stays the clone route
        assert "git clone" in html and f"scripts/reproduce_review.py {slug}" in html


def test_the_no_bundle_reason_does_not_point_the_zip_reader_at_the_git_command():
    without = next(s for s in SLUGS if not (ROOT / "docs" / "reviews" / s / "BUNDLE.json").is_file())
    html = T.reproduce_additions({"slug": without})
    assert "(or clone it) and run the command above" not in html
    assert "run the zip replay above" in html


def test_every_served_page_that_links_the_zip_names_the_offline_replay():
    served = [s for s in SLUGS if ZIP in (ROOT / "docs" / "reviews" / s / "index.html").read_text(encoding="utf-8")]
    assert len(served) == len(SLUGS), "a served review page lost the download link (denominator)"
    for s in served:
        page = (ROOT / "docs" / "reviews" / s / "index.html").read_text(encoding="utf-8")
        assert f"scripts/replay_offline.py {s}" in page, s


# ------------------------------------------------------------------------------- the historical GLP-1 release
GLP1 = ROOT / "docs" / "releases" / "glp1-ra-mace-t2d" / "1b3b0b8dcf3d"


def test_the_glp1_release_is_labelled_historical_where_it_is_served():
    """The only packaged release is pinned to 1b3b0b8dc (24 Sep 2026), long behind main. Its served README (beside the
    frozen zip; the zip and RELEASE.json stay byte-frozen) must say so before anything else."""
    first = (GLP1 / "README.md").read_text(encoding="utf-8").split("\n\n", 1)[0]
    assert "HISTORICAL (pinned 1b3b0b8dc, 24 Sep)" in first, first
    assert "not the current harness" in first
    assert b"\r" not in (GLP1 / "README.md").read_bytes()



# ------------------------------------------------------------------------------- the published release (10 Oct)
def test_the_index_and_every_reproduce_tab_link_the_published_release():
    from harness import index as I
    rel = T.RELEASE
    assert rel["asset"] == f"meta-harness-{rel['tag']}.zip" and rel["sums"] == "SHA256SUMS"   # the starter fetch's names
    assert rel["url"] in I.build_index(str(ROOT / "docs"))
    for slug in SLUGS[:2]:
        html = T.reproduce_additions({"slug": slug})
        assert rel["url"] in html and "DOI pending (v1.0.1)" in html


def test_every_served_page_links_the_release():
    for s in SLUGS:
        assert T.RELEASE["url"] in (ROOT / "docs" / "reviews" / s / "index.html").read_text(encoding="utf-8"), s
    assert T.RELEASE["url"] in (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
