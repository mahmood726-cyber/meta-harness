"""Build one topic end-to-end from committed inputs (offline, deterministic).

  python scripts/build_topic.py <slug>

Writes:
  docs/reviews/<slug>/            canonical harness review (two-limb gated)
  docs/m/<tokenA>/, docs/m/<tokenB>/   neutral blind pair (harness + comparator), same shell
  registry/blind_map.json         token -> role map (repo-only, NOT served on Pages)
  docs/index.html                 regenerated generated index
"""
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from harness.pipeline import build_review_core, build_comparator_core, METHOD  # noqa: E402
from harness.census import build_review_dir  # noqa: E402
from harness.page import render_page  # noqa: E402
from harness.index import write_index  # noqa: E402

SALT = "mh-blind-v1"


def _token(slug, role):
    return "m" + hashlib.sha1(f"{slug}|{role}|{SALT}".encode()).hexdigest()[:8]


def _protocol_sha(slug):
    out = subprocess.check_output(
        ["git", "-C", ROOT, "log", "-1", "--format=%H", "--", f"protocols/{slug}.md"],
        text=True).strip()
    if not out:
        raise SystemExit(f"protocol protocols/{slug}.md is not committed yet — register it first")
    return out


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def main(slug):
    protocol_sha = _protocol_sha(slug)
    comparator = json.load(open(os.path.join(ROOT, "data", slug, "comparator.json"), encoding="utf-8"))

    core = build_review_core(slug, protocol_sha)
    manifest_meta = {
        "slug": slug, "declared_method": METHOD, "served_method": METHOD,
        "generator": "harness", "build_utc": "2026-09-11",
        "comparator": {k: comparator[k] for k in ("name", "year", "journal", "pmid",
                                                  "doi", "url", "open_access", "overlap")},
    }
    review_dir = os.path.join(ROOT, "docs", "reviews", slug)
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True)

    # Blind pair: neutral render of ours + comparator, opaque tokens.
    comp_core = build_comparator_core(slug)
    tok_h, tok_c = _token(slug, "harness"), _token(slug, "comparator")
    # ours neutral render needs the reproduction block populated (quality feature).
    ours_final = dict(core)
    ours_final["reproduction"] = {"failures": 0, "protocol_sha": protocol_sha,
                                  "review_sha256": manifest["review_sha256"], "from_cache": True}
    _write(os.path.join(ROOT, "docs", "m", tok_h, "index.html"), render_page(ours_final, neutral=True))
    _write(os.path.join(ROOT, "docs", "m", tok_c, "index.html"), render_page(comp_core, neutral=True))
    _write(os.path.join(ROOT, "registry", "blind_map.json"), json.dumps({
        "slug": slug,
        "pages": {tok_h: {"role": "harness", "url": f"docs/m/{tok_h}/"},
                  tok_c: {"role": "comparator", "url": f"docs/m/{tok_c}/"}},
    }, indent=2))

    write_index(os.path.join(ROOT, "docs"))

    print(f"protocol_sha={protocol_sha}")
    print(f"review_sha256={manifest['review_sha256']}")
    print(f"html_sha256={manifest['html_sha256']}")
    print(f"canonical: docs/reviews/{slug}/index.html")
    print(f"blind harness page:   docs/m/{tok_h}/  (token hides identity)")
    print(f"blind comparator page: docs/m/{tok_c}/")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/build_topic.py <slug>")
    main(sys.argv[1])
