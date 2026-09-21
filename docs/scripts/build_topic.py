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
from harness.synth import method_text as _method_text  # noqa: E402
from harness.census import build_review_dir  # noqa: E402
from harness.page import render_page  # noqa: E402
from harness.index import write_index  # noqa: E402
from execution_record import write_execution_record  # noqa: E402  (scripts/execution_record.py)
from harness.registration import protocol_sha  # noqa: E402
from harness import registration as _reg  # noqa: E402

SALT = "mh-blind-v1"


def _token(slug, role):
    return "m" + hashlib.sha1(f"{slug}|{role}|{SALT}".encode()).hexdigest()[:8]


def _protocol_sha(slug):
    out = protocol_sha(slug)
    if not out:
        raise SystemExit(f"protocols/{slug}.md not committed — register it first")
    return out


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def main(slug, now, argv=None):
    config = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    protocol_sha = _protocol_sha(slug)
    records = fetch.ensure(config, now)  # network only if cache absent

    core = build_review_core(slug, config, records, protocol_sha)
    prim = [o for o in core["outcomes"] if o.get("primary")][0]
    # declared_method = the primary outcome's DECLARED estimand's method (from config/protocol).
    # served_method  = the method for the scale the pool ACTUALLY produced for the primary outcome.
    # These come from DIFFERENT sources, so gate.check_limb1's declared==served can genuinely fail
    # (before this it compared the single METHOD constant to itself and could not fire) -- the fix
    # for the melatonin cold-audit "a check that cannot fail looks like a clean corpus" class.
    _declared_method = core.get("method_declared", METHOD)
    _served_scale = (prim.get("result") or {}).get("scale")
    _served_method = _method_text(_served_scale) if _served_scale else _declared_method
    manifest_meta = {"slug": slug, "declared_method": _declared_method, "served_method": _served_method,
                     "generator": "harness", "build_utc": now,
                     "comparator": {k: core["comparator"][k] for k in
                                    ("name", "year", "journal", "pmid", "doi", "url", "open_access", "overlap")}}
    review_dir = os.path.join(ROOT, "docs", "reviews", slug)
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True, certify=True)

    comp_core = build_comparator_core(slug, config, records)
    tok_h, tok_c = _token(slug, "harness"), _token(slug, "comparator")
    ours_final = dict(core, reproduction={"failures": 0, "protocol_sha": protocol_sha,
                                          "review_sha256": manifest["review_sha256"], "from_cache": True,
                                          "preregistration": _reg.preregistration_sha(slug)})
    _write(os.path.join(ROOT, "docs", "m", tok_h, "index.html"), render_page(ours_final, neutral=True))
    _write(os.path.join(ROOT, "docs", "m", tok_c, "index.html"), render_page(comp_core, neutral=True))
    _write(os.path.join(ROOT, "registry", "blind_map.json"), json.dumps(
        {"slug": slug, "pages": {tok_h: {"role": "harness", "url": f"docs/m/{tok_h}/"},
                                 tok_c: {"role": "comparator", "url": f"docs/m/{tok_c}/"}}}, indent=2))
    write_index(os.path.join(ROOT, "docs"))
    # LAST: which tree produced this directory (scripts/execution_record.py). Written after the certificate so it can name
    # release_sha256; never an input to any digest the certificate covers.
    write_execution_record(review_dir, slug, argv if argv is not None else sys.argv, now)

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
    main(args[0], now, list(sys.argv))
