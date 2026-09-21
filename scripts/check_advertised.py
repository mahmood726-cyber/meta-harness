"""Every artefact a bundle ADVERTISES as served must exist in the tree at that path, with the advertised bytes and digest,
under a URL that is SITE_ROOT + served_path.

Why this exists (2026-09-21). The deploy job fetches every file in the per-file production manifest from the live site and
proves body digest == verified digest, so a file that IS in the tree cannot be served wrong. What that cannot see is a path a
bundle advertises that is not in the tree at all: it is never in the manifest, never fetched, and 404s silently. An earlier
round found 14 of 18 advertised artefacts unreachable for exactly that reason; the same night an auditor reached for the
verifier at a path nothing advertises. This check closes the first hole. It does not close the second (see LIMITS).

Checked, per docs/reviews/<slug>/BUNDLE.json: verifier; certificate; source.execution_record; review_files[]; artefacts[] with
state SERVED; supporting_files[] (repo-relative `path`). Each must: exist under docs/; match `bytes`; match `sha256` (a byte
digest in every one of these fields -- artefacts carry their content digest separately as declared_digest); and, where a
served_url is advertised, served_url == SITE_ROOT + served_path. Non-SERVED artefacts must advertise no served path or URL.

LIMITS -- printed on every run, because a gate states its own limits:
  * advertised-and-present, not advertised-and-complete: an artefact the bundle SHOULD advertise and does not is invisible here;
  * offline by default: existence and bytes are checked in the working tree, not on the live site. --live fetches each
    served_url with no-store and compares body digest and length; it is optional and never required for a pass, because a
    gate that needs the network fails offline for the wrong reason;
  * it does not check that any served PAGE names the verifier (the discoverability defect); that is a page.py change.

Exit 0 = PASS, 1 = REFUSED (each failing entry named), 2 = COULD-NOT-EXECUTE.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = "https://mahmood726-cyber.github.io/meta-harness/"
LIMITS = (
    "LIMITS: checks advertised-and-present, not advertised-and-complete; offline against the working tree unless --live; "
    "does not check that a served page names the verifier."
)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def advertised_entries(bundle: dict) -> list[dict]:
    """Flatten every advertised-as-served entry into {where, served_path, served_url, bytes, sha256}."""
    out: list[dict] = []

    def add(where: str, served_path, served_url, nbytes, sha):
        out.append({"where": where, "served_path": served_path, "served_url": served_url, "bytes": nbytes, "sha256": sha})

    v = bundle.get("verifier") or {}
    if v:
        add("verifier", v.get("served_path"), v.get("served_url"), v.get("bytes"), v.get("sha256"))
    c = bundle.get("certificate") or {}
    if c:
        add("certificate", c.get("served_path"), c.get("served_url"), c.get("bytes"), c.get("sha256_of_file") or c.get("sha256"))
    er = ((bundle.get("source") or {}).get("execution_record")) or {}
    if er:
        add("source.execution_record", er.get("served_path"), er.get("served_url"), er.get("bytes"), er.get("sha256"))
    for i, r in enumerate(bundle.get("review_files") or []):
        add(f"review_files[{i}] {r.get('file')}", r.get("served_path"), r.get("served_url"), r.get("bytes"), r.get("sha256"))
    for i, a in enumerate(bundle.get("artefacts") or []):
        if a.get("state") == "SERVED":
            add(f"artefacts[{i}] {a.get('ref')}", a.get("served_path"), a.get("served_url"), a.get("bytes"), a.get("sha256"))
    for i, s in enumerate(bundle.get("supporting_files") or []):
        p = s.get("path")
        served = p[len("docs/"):] if isinstance(p, str) and p.startswith("docs/") else p
        add(f"supporting_files[{i}]", served, s.get("served_url"), s.get("bytes"), s.get("sha256"))
    return out


def check_bundle(bundle_path: str, docs_dir: str, live: bool = False) -> list[str]:
    problems: list[str] = []
    try:
        bundle = json.load(open(bundle_path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"COULD-NOT-EXECUTE: {bundle_path}: {exc}"]
    entries = advertised_entries(bundle)
    if not entries:
        return [f"{bundle_path}: advertises nothing -- a bundle with no served artefacts is not a bundle"]
    for e in entries:
        w, sp = e["where"], e["served_path"]
        if not isinstance(sp, str) or not sp or sp == "None":
            problems.append(f"{w}: no served_path advertised")
            continue
        local = os.path.join(docs_dir, *sp.split("/"))
        if not os.path.isfile(local):
            problems.append(f"{w}: advertised served_path {sp!r} is NOT IN THE TREE under docs/ (would 404 silently)")
            continue
        raw = open(local, "rb").read()
        if e["bytes"] is not None and str(e["bytes"]) != str(len(raw)):
            problems.append(f"{w}: advertised bytes {e['bytes']} != {len(raw)} on disk at {sp}")
        if e["sha256"] and e["sha256"] != _sha(raw):
            problems.append(f"{w}: advertised sha256 {str(e['sha256'])[:12]} != {_sha(raw)[:12]} on disk at {sp}")
        url = e["served_url"]
        if url is not None and url != SITE_ROOT + sp:
            problems.append(f"{w}: served_url {url!r} != SITE_ROOT + served_path ({SITE_ROOT + sp!r})")
        elif live:
            # every advertised path is fetched, whether or not the entry spells out its URL
            problems.extend(_live_check(w, SITE_ROOT + sp, raw))
    for i, a in enumerate(bundle.get("artefacts") or []):
        if a.get("state") != "SERVED" and (a.get("served_url") or (a.get("served_path") not in (None, "None", ""))):
            problems.append(f"artefacts[{i}] {a.get('ref')}: state {a.get('state')} but advertises a served path/url")
    return problems


def _live_check(where: str, url: str, raw: bytes) -> list[str]:
    req = urllib.request.Request(url, headers={"Cache-Control": "no-store", "Pragma": "no-cache", "User-Agent": "check-advertised"})
    try:
        r = urllib.request.urlopen(req, timeout=60)
        body = r.read()
    except urllib.error.HTTPError as exc:
        return [f"{where}: LIVE {url} -> HTTP {exc.code}"]
    except (urllib.error.URLError, OSError) as exc:
        return [f"{where}: LIVE {url} -> could not fetch ({exc})"]
    if body != raw:
        return [f"{where}: LIVE {url} -> body {len(body)} B sha256 {_sha(body)[:12]} != tree {len(raw)} B {_sha(raw)[:12]}"]
    return []


def main(argv=None) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--docs", default=os.path.join(ROOT, "docs"))
    ap.add_argument("--bundle", action="append", default=[], help="a BUNDLE.json to check (default: every docs/reviews/*/BUNDLE.json)")
    ap.add_argument("--live", action="store_true", help="also fetch every served_url with no-store and compare body to the tree")
    a = ap.parse_args(argv)
    bundles = a.bundle or sorted(glob.glob(os.path.join(a.docs, "reviews", "*", "BUNDLE.json")))
    if not bundles:
        print("COULD-NOT-EXECUTE: no BUNDLE.json under", a.docs)
        print(LIMITS)
        return 2
    total = 0
    refused = False
    for bp in bundles:
        try:
            rel = os.path.relpath(bp, ROOT).replace(os.sep, "/")
        except ValueError:                     # a bundle on another drive (Windows): name it absolutely rather than crash
            rel = bp.replace(os.sep, "/")
        problems = check_bundle(bp, a.docs, live=a.live)
        if any(p.startswith("COULD-NOT-EXECUTE") for p in problems):
            # no verdict: an unreadable bundle is neither a pass nor a refusal, and must not exit like either
            print(f"COULD-NOT-EXECUTE {rel}: " + "; ".join(problems))
            print(LIMITS)
            return 2
        n = len(advertised_entries(json.load(open(bp, encoding="utf-8"))))
        total += n
        if problems:
            refused = True
            print(f"REFUSED {rel}: {len(problems)} of {n} advertised entries fail" + (" (live)" if a.live else ""))
            for p in problems:
                print("   ", p)
        else:
            print(f"PASS    {rel}: {n} advertised entries present with advertised bytes and sha256, urls = SITE_ROOT + path"
                  + (", live bodies equal" if a.live else ""))
    print(f"ADVERTISED-ARTEFACTS: {'REFUSED' if refused else 'PASS'} -- {len(bundles)} bundle(s), {total} entries"
          + (" (live)" if a.live else " (offline)"))
    print(LIMITS)
    return 1 if refused else 0


if __name__ == "__main__":
    raise SystemExit(main())
