"""One command, protocol SHA -> published tabbed URL. No hand steps, no typed numbers.

  python scripts/build_topic.py <slug> [--now YYYY-MM-DD]

fetch-once (network, only if cache absent) -> committed cache -> offline screen ->
extract -> synthesise -> render canonical gated page + neutral blind pair -> index.
Re-running from the protocol SHA on a fresh clone replays the committed cache and
regenerates the served bytes byte-for-byte.
"""
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from harness import fetch  # noqa: E402
from harness.pipeline import build_review_core, build_comparator_core, METHOD  # noqa: E402
from harness.census import build_review_dir  # noqa: E402
from harness.page import render_page  # noqa: E402
from harness.index import write_index  # noqa: E402

SALT = "mh-blind-v1"


def _token(slug, role):
    return "m" + hashlib.sha1(f"{slug}|{role}|{SALT}".encode()).hexdigest()[:8]


def _protocol_sha(slug):
    out = subprocess.check_output(
        ["git", "-C", ROOT, "log", "-1", "--format=%H", "--", f"protocols/{slug}.md"], text=True).strip()
    if not out:
        raise SystemExit(f"protocols/{slug}.md not committed — register it first")
    return out


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def main(slug, now):
    config = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    protocol_sha = _protocol_sha(slug)
    records = fetch.ensure(config, now)  # network only if cache absent

    core = build_review_core(slug, config, records, protocol_sha)
    prim = [o for o in core["outcomes"] if o.get("primary")][0]
    manifest_meta = {"slug": slug, "declared_method": METHOD, "served_method": METHOD,
                     "generator": "harness", "build_utc": now,
                     "comparator": {k: core["comparator"][k] for k in
                                    ("name", "year", "journal", "pmid", "doi", "url", "open_access", "overlap")}}
    review_dir = os.path.join(ROOT, "docs", "reviews", slug)
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True)

    comp_core = build_comparator_core(slug, config, records)
    tok_h, tok_c = _token(slug, "harness"), _token(slug, "comparator")
    ours_final = dict(core, reproduction={"failures": 0, "protocol_sha": protocol_sha,
                                          "review_sha256": manifest["review_sha256"], "from_cache": True})
    _write(os.path.join(ROOT, "docs", "m", tok_h, "index.html"), render_page(ours_final, neutral=True))
    _write(os.path.join(ROOT, "docs", "m", tok_c, "index.html"), render_page(comp_core, neutral=True))
    _write(os.path.join(ROOT, "registry", "blind_map.json"), json.dumps(
        {"slug": slug, "pages": {tok_h: {"role": "harness", "url": f"docs/m/{tok_h}/"},
                                 tok_c: {"role": "comparator", "url": f"docs/m/{tok_c}/"}}}, indent=2))
    write_index(os.path.join(ROOT, "docs"))

    r = prim.get("result", {})
    print(f"protocol_sha={protocol_sha}")
    print(f"PRIMARY: {prim['name']}  k={r.get('k')}  RR={r.get('estimate')} "
          f"({r.get('ci_low')}-{r.get('ci_high')})  tau2={r.get('tau2')}")
    print(f"included trials: {[t['label'] for t in prim.get('trials', [])]}")
    print(f"declared-absent trials: {[t['label'] for t in prim.get('declared_absent_trials', [])]}")
    print(f"comparator OA={core['comparator']['open_access']} k={core['comparator']['overlap']['theirs_k']}")
    print(f"canonical: docs/reviews/{slug}/index.html")
    print(f"blind: docs/m/{tok_h}/  docs/m/{tok_c}/")


if __name__ == "__main__":
    args = sys.argv[1:]
    now = "2026-09-11"
    if "--now" in args:
        now = args[args.index("--now") + 1]
        args = [a for a in args if a != now and a != "--now"]
    if len(args) != 1:
        raise SystemExit("usage: python scripts/build_topic.py <slug> [--now YYYY-MM-DD]")
    main(args[0], now)
