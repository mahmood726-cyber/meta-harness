"""Reproduction census.

Two-level design:

  Level A (always): fresh-clone integrity + determinism.
    From the committed review.json alone, re-derive review_sha256 (over the core)
    and re-render the page; both must byte-match the committed manifest hashes and
    the committed index.html. This catches non-determinism and ANY hand-edit of the
    served HTML or the review data after the census ran.

  Level B (attaches when a topic pipeline exists): offline replay.
    Re-run fetch(from committed cache) -> screen -> extract -> synthesise and confirm
    the regenerated review core matches the committed one. Recorded as from_cache.

build_review_dir() writes a review directory with page + manifest + REPRODUCTION.json.
verify() performs Level A against an on-disk directory (this is what a fresh clone runs).
"""
from __future__ import annotations
import json
import os
from typing import Callable, Optional

from .canonical import canonical_json, review_core, review_sha256, sha256_text
from .page import render_page


def _parity_row(root: str, slug: str):
    """This topic's row from the committed docs/parity.json (a measurement snapshot), or None.
    Shared by census (build) and reproduce_review (replay) so the reproduction block byte-matches."""
    p = os.path.join(root, "docs", "parity.json")
    if not slug or not os.path.exists(p):
        return None
    try:
        for row in json.load(open(p, encoding="utf-8")):
            if row.get("slug") == slug:
                return row
    except (ValueError, OSError):
        return None
    return None


def build_review_dir(
    review_core_obj: dict,
    manifest_meta: dict,
    out_dir: str,
    protocol_sha: str,
    from_cache: bool = False,
) -> dict:
    """Assemble a publishable review directory. Returns the manifest dict."""
    os.makedirs(out_dir, exist_ok=True)
    core_sha = review_sha256(review_core_obj)  # excludes 'reproduction' by construction

    # Level A self-check while building: rendering the core twice is byte-stable.
    core_review = dict(review_core_obj)
    core_review.pop("reproduction", None)
    h1 = render_page(core_review)
    h2 = render_page(json.loads(canonical_json(core_review)))
    failures = 0
    checks = []
    det_ok = (h1 == h2)
    checks.append({"check": "render is deterministic", "ok": det_ok})
    if not det_ok:
        failures += 1

    reproduction = {
        "failures": failures,
        "protocol_sha": protocol_sha,
        "review_sha256": core_sha,
        "from_cache": from_cache,
    }
    # Re-search diff (item 1): committed, outside the core hash by living in 'reproduction', so it can
    # never affect the analysis sha or replay. Present only where scripts/research_diff.py has run.
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _rd = os.path.join(_root, "cache", manifest_meta.get("slug", ""), "research_diff.json")
    if os.path.exists(_rd):
        try:
            reproduction["research_diff"] = json.load(open(_rd, encoding="utf-8"))
        except (ValueError, OSError):
            pass
    # Parity snapshot (docs/parity.json): this topic's row, outside the core hash. Rendered so a
    # reader sees our k vs the comparable comparator k on the page itself, not only on the index.
    _pa = _parity_row(_root, manifest_meta.get("slug", ""))
    if _pa:
        reproduction["parity"] = _pa
    final_review = dict(review_core_obj)
    final_review["reproduction"] = reproduction
    html = render_page(final_review)
    html_sha = sha256_text(html)

    manifest = {
        "slug": manifest_meta["slug"],
        "title": review_core_obj.get("title"),
        "declared_method": manifest_meta["declared_method"],
        "served_method": manifest_meta["served_method"],
        "protocol_sha": protocol_sha,
        "generator": manifest_meta.get("generator", "harness"),
        "review_sha256": core_sha,
        "html_sha256": html_sha,
        "comparator": manifest_meta.get("comparator"),
        "build_utc": manifest_meta.get("build_utc"),
    }

    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="") as f:
        f.write(html)
    with open(os.path.join(out_dir, "review.json"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(final_review, ensure_ascii=False, indent=2))
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2))
    with open(os.path.join(out_dir, "REPRODUCTION.json"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps({**reproduction, "html_sha256": html_sha, "checks": checks},
                           ensure_ascii=False, indent=2))
    return manifest


def verify(review_dir: str, replay: Optional[Callable[[dict], dict]] = None) -> dict:
    """Fresh-clone census. Returns {'failures': int, 'checks': [...]}.

    replay: optional Level-B fn taking the manifest and returning a regenerated
    review core (from committed cache, offline). If given, its output must match
    the committed review core.
    """
    checks = []
    failures = 0

    def _fail(name, ok, detail=""):
        nonlocal failures
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        if not ok:
            failures += 1

    try:
        with open(os.path.join(review_dir, "manifest.json"), encoding="utf-8") as f:
            manifest = json.load(f)
        with open(os.path.join(review_dir, "review.json"), encoding="utf-8") as f:
            review = json.load(f)
        with open(os.path.join(review_dir, "index.html"), encoding="utf-8") as f:
            served_html = f.read()
    except (OSError, ValueError) as exc:
        return {"failures": 1, "checks": [{"check": "load artifacts", "ok": False, "detail": str(exc)}]}

    # 1. review core hash reproduces
    core_sha = review_sha256(review)
    _fail("review_sha256 reproduces from committed review.json",
          core_sha == manifest.get("review_sha256"),
          f"{core_sha} vs {manifest.get('review_sha256')}")

    # 2. served HTML byte-matches a re-render of the committed review (catches hand-edits)
    rerender = render_page(review)
    _fail("served index.html byte-matches re-render of review.json",
          sha256_text(rerender) == sha256_text(served_html))
    _fail("served index.html sha matches manifest.html_sha256",
          sha256_text(served_html) == manifest.get("html_sha256"))

    # 3. Level B replay if provided
    if replay is not None:
        try:
            regen = replay(manifest)
            _fail("offline replay reproduces review core",
                  review_sha256(regen) == manifest.get("review_sha256"))
        except Exception as exc:  # noqa: BLE001 - report, do not mask
            _fail("offline replay executed", False, str(exc))

    return {"failures": failures, "checks": checks}
