#!/usr/bin/env python3
"""Frozen, downloadable release archive of one served review, read from ONE commit -- never from the working tree.

    python scripts/release_archive.py build  --slug glp1-ra-mace-t2d --commit <sha> [--out docs/releases]
    python scripts/release_archive.py check  <archive.zip>        # stdlib; the same check the archive's README gives

What goes in (every path, and why, is listed in RELEASE.json inside the archive):
  - every file the review's BUNDLE.json advertises as served at that commit (artefacts, acquisitions, supporting files,
    review files, the verifier) -- the bundle's own definition of what a verifier needs;
  - every module the review's CERTIFICATE.json pins (analysis_code_blobs), from the served mirror under docs/;
  - the whole served review directory docs/reviews/<slug>/ (page, review core, certificate, manifest, bundle, record,
    REPLAY.md);
  - the two verifiers the page names (docs/scripts/verify_bundle.py, docs/scripts/audit_certificate_stdlib.py);
  - the production-record attestation of that commit, if the production-records branch holds one, copied verbatim.
Layout inside the zip:  <name>/site/<served path>  (the site root, so --root site resolves every served path unmodified),
<name>/RELEASE.json, <name>/README.md, <name>/SHA256SUMS (sha256sum -c format over every other file in <name>/),
<name>/check_sha256sums.py (stdlib, for machines with no sha256sum), <name>/plant_control.py (a control that must fail).

Frozen means: bytes come from `git show <commit>:<path>`; each file's Git blob id is recorded beside its sha256, so the
archive can be checked against any clone holding that commit (`git rev-parse <commit>:<path>`). The zip's own bytes are
not claimed reproducible across zlib versions; the per-file digests are the content identity and are.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = "https://mahmood726-cyber.github.io/meta-harness/"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
VERIFIERS = ("scripts/verify_bundle.py", "scripts/audit_certificate_stdlib.py")

CHECK_SUMS = '''#!/usr/bin/env python3
"""Check SHA256SUMS in this directory (for machines without sha256sum). Exit 0 iff every line matches."""
import hashlib, sys
from pathlib import Path
here = Path(__file__).resolve().parent
bad = n = 0
for line in (here / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
    digest, name = line.split("  ", 1)
    p = here / name
    ok = p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == digest
    n += 1
    bad += not ok
    if not ok:
        print("FAILED", name)
print(f"{n - bad} of {n} files match SHA256SUMS")
sys.exit(1 if bad else 0)
'''

# A control that must FAIL, on disk, from the archive alone. (`verify_bundle.py --corrupt` is NOT such a control: it
# mutates one row in memory and reports which rows change admissibility, and its verdict stays PASS by design --
# measured 2026-09-24 in a fresh directory: `--corrupt 27633186 effect` -> "verdict PASS", exit 0.)
PLANT_CONTROL = '''#!/usr/bin/env python3
"""Control that must FAIL: copy site/ to a temporary directory, change ONE served value (the primary pooled estimate in
review.json, x1.01 -- a value change, not whitespace), and run the archived verifier on the copy. Then run it on the
untouched site/. Exit 0 iff the damaged copy does NOT pass and the untouched site does. Standard library only."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
here = Path(__file__).resolve().parent
slug = json.loads((here / "RELEASE.json").read_text(encoding="utf-8"))["slug"]
verifier = here / "site" / "scripts" / "verify_bundle.py"
def verdict(root):
    p = subprocess.run([sys.executable, str(verifier), "--root", str(root), "--slug", slug], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    return next((l for l in p.stdout.splitlines() if "verdict" in l), "no verdict line").strip()
with tempfile.TemporaryDirectory() as tmp:
    copy = Path(tmp) / "site"
    shutil.copytree(here / "site", copy)
    rv = copy / "reviews" / slug / "review.json"
    doc = json.loads(rv.read_text(encoding="utf-8"))
    prim = next(o for o in doc["outcomes"] if o.get("primary"))
    before = prim["result"]["estimate"]
    prim["result"]["estimate"] = before * 1.01
    rv.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    damaged = verdict(copy)
clean = verdict(here / "site")
print(f"damaged copy (primary estimate {before} -> {before * 1.01}): {damaged}")
print(f"untouched site: {clean}")
fired = "verdict PASS" not in damaged and "verdict PASS" in clean
print("CONTROL FIRED" if fired else "CONTROL DID NOT FIRE -- do not trust a PASS from this verifier")
sys.exit(0 if fired else 1)
'''


def _git(*args: str) -> bytes:
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise SystemExit(f"REFUSED: git {' '.join(args)}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def _show(commit: str, path: str) -> bytes:
    return _git("show", f"{commit}:{path}")


def _blob(commit: str, path: str) -> str:
    return _git("rev-parse", f"{commit}:{path}").decode().strip()


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _served_paths(bundle: dict) -> dict[str, set]:
    """Every served path the bundle advertises, keyed by site-root-relative path -> the bundle sections naming it."""
    out: dict[str, set] = {}

    def walk(o, why):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "served_path" and isinstance(v, str):
                    out.setdefault(v.lstrip("/"), set()).add(why)
                elif k == "path" and isinstance(v, str) and v.startswith("docs/"):
                    out.setdefault(v[len("docs/"):], set()).add(why)
                else:
                    walk(v, why)
        elif isinstance(o, list):
            for v in o:
                walk(v, why)

    for key in ("artefacts", "acquisitions", "supporting_files", "review_files", "documents", "verifier", "certificate", "source"):
        walk(bundle.get(key), key)
    return out


def _attestation(commit: str) -> tuple[str | None, bytes | None]:
    """The production-records entry for this commit (the deploy job's record that served bytes == committed bytes)."""
    for ref in ("origin/production-records", "production-records"):
        r = subprocess.run(["git", "-C", str(ROOT), "log", ref, "--format=%H %s"], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL)
        if r.returncode != 0:
            continue
        for line in r.stdout.splitlines():
            h, _, subject = line.partition(" ")
            if commit[:12] in subject or commit in subject:
                files = _git("show", "--name-only", "--format=", h).decode().split()
                if files:
                    return subject, _git("show", f"{h}:{files[0]}")
                return subject, None
    return None, None


def build(slug: str, commit: str, out_root: Path) -> Path:
    commit = _git("rev-parse", commit + "^{commit}").decode().strip()
    c12 = commit[:12]
    name = f"{slug}-{c12}"
    rdir = f"docs/reviews/{slug}"
    bundle = json.loads(_show(commit, f"{rdir}/BUNDLE.json"))
    cert = json.loads(_show(commit, f"{rdir}/CERTIFICATE.json"))
    manifest = json.loads(_show(commit, f"{rdir}/manifest.json"))
    review = json.loads(_show(commit, f"{rdir}/review.json"))
    why = _served_paths(bundle)
    for p, v in cert["analysis_code_blobs"].items():
        if v != "NOT_PRESENT":
            why.setdefault(p, set()).add("pinned_module")
    for p in _git("ls-tree", "--name-only", f"{commit}:{rdir}").decode().split():
        why.setdefault(f"reviews/{slug}/{p}", set()).add("review_directory")
    for v in VERIFIERS:
        why.setdefault(v, set()).add("named_verifier")
    files, blobs = {}, {}
    for p in sorted(why):
        files[p] = _show(commit, "docs/" + p)            # refuses (exits) if the commit does not hold it
        blobs[p] = _blob(commit, "docs/" + p)
    for p, v in cert["analysis_code_blobs"].items():      # the served mirror must be the pinned bytes
        if v != "NOT_PRESENT" and blobs[p] != v:
            raise SystemExit(f"REFUSED: docs/{p} at {c12} is blob {blobs[p]}, the certificate pins {v}")
    subject, record = _attestation(commit)
    status = review.get("release_status") or {}
    release = {
        "archive": name,
        "slug": slug,
        "commit": commit,
        "tree": _git("rev-parse", commit + "^{tree}").decode().strip(),
        "site_root": SITE_ROOT,
        "release_status": status.get("status"),
        "release_status_note": ("the review is served under a PRE-RELEASE label (registry/release_status.json); this archive "
                                "freezes what was served at the commit above and is NOT a version-1 release"
                                if status.get("status") == "PRE-RELEASE" else None),
        "release_sha256": cert.get("release_sha256"),
        "review_sha256": cert.get("review_sha256"),
        "html_sha256": manifest.get("html_sha256"),
        "production_record": {"subject": subject, "file": "production_record.json" if record else None,
                              "state": ("COPIED" if record else "NOT_FOUND_ON_production-records_AT_BUILD_TIME")},
        "definition": ("every path the review's BUNDLE.json advertises as served, every module its CERTIFICATE.json pins, "
                       "the served review directory, and the verifiers the page names -- all read from the commit above"),
        "files": [{"path": "site/" + p, "served_path": p, "served_url": SITE_ROOT + p, "bytes": len(files[p]),
                   "sha256": _sha(files[p]), "git_blob": blobs[p], "why": sorted(why[p])} for p in sorted(files)],
    }
    readme = _readme(release)
    members: dict[str, bytes] = {f"site/{p}": b for p, b in files.items()}
    members["RELEASE.json"] = (json.dumps(release, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    members["README.md"] = readme.encode("utf-8")
    members["check_sha256sums.py"] = CHECK_SUMS.encode("utf-8")
    members["plant_control.py"] = PLANT_CONTROL.encode("utf-8")
    if record:
        members["production_record.json"] = record
    members["SHA256SUMS"] = "".join(f"{_sha(members[m])}  {m}\n" for m in sorted(members)).encode("utf-8")
    dest = out_root / slug / c12
    dest.mkdir(parents=True, exist_ok=True)
    zpath = dest / f"{name}.zip"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for m in sorted(members):
            info = zipfile.ZipInfo(f"{name}/{m}", date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, members[m])
    zpath.write_bytes(buf.getvalue())
    (dest / "README.md").write_bytes(members["README.md"])
    (dest / "RELEASE.json").write_bytes(members["RELEASE.json"])
    # bytes, not write_text: on Windows write_text turns "\n" into CRLF, and `sha256sum -c` then reads the CR as part of
    # the file name (served that way at 00b8337c; tests/test_release_archive.py::test_served_sha256sums_is_what_sha256sum_c_reads)
    (dest / "SHA256SUMS").write_bytes(f"{_sha(buf.getvalue())}  {zpath.name}\n".encode("ascii"))
    print(f"wrote {zpath} ({len(buf.getvalue()):,} bytes, {len(files)} served files) sha256 {_sha(buf.getvalue())}")
    return zpath


def _readme(r: dict) -> str:
    slug, name, c = r["slug"], r["archive"], r["commit"]
    site = r["site_root"]
    rel = f"releases/{slug}/{c[:12]}/"
    lines = [
        f"# Frozen release archive: {slug} at {c[:12]}",
        "",
        f"This archive freezes the bytes served for the `{slug}` review at commit `{c}` "
        f"(tree `{r['tree']}`). Release status: **{r['release_status']}**."
        + (f" {r['release_status_note']}." if r.get("release_status_note") else ""),
        "",
        f"- `release_sha256` {r['release_sha256']}",
        f"- `review_sha256` {r['review_sha256']}",
        f"- `html_sha256` {r['html_sha256']}",
        f"- {len(r['files'])} served files under `site/`, each listed in `RELEASE.json` with its sha256, its Git blob id at "
        f"the commit, its served URL and why it is included. Definition: {r['definition']}.",
        f"- production record: {r['production_record']['subject'] or 'none found on the production-records branch when the archive was built'}"
        + (" (copied verbatim as `production_record.json`)" if r["production_record"]["file"] else ""),
        "",
        "## Get it",
        "",
        f"- Download: `{site}{rel}{name}.zip`; its sha256 is in `{site}{rel}SHA256SUMS` and in the repository at "
        f"`docs/{rel}SHA256SUMS`. Take the digest from a second channel (a clone, a colleague, the page) if you can.",
        "- Check the download: `sha256sum " + name + ".zip` (Windows: `certutil -hashfile " + name + ".zip SHA256`).",
        f"- Unpack: `python -m zipfile -e {name}.zip .` then `cd {name}`.",
        "",
        "## Replay: what runs from this archive alone (no network, Python 3.9+ standard library, no git)",
        "",
        "```",
        "python check_sha256sums.py          # or: sha256sum -c SHA256SUMS -- every file in this archive",
        f"python site/scripts/verify_bundle.py --root site --slug {slug}",
        f"python site/scripts/audit_certificate_stdlib.py site/reviews/{slug}/CERTIFICATE.json site",
        "python plant_control.py             # the control: damages a copy of site/ and must see the verifier NOT pass",
        "```",
        "",
        "The first must print every file matching. The second must print `verdict PASS`; the third `RESULT REPRODUCED`; the "
        "control must print `CONTROL FIRED` (a verifier that cannot fail proves nothing). Each verifier prints `NOT checked:` "
        "-- those limits apply to you. Compare the `release_sha256` the auditor prints with the one above and with the one "
        f"printed on `site/reviews/{slug}/index.html`.",
        "",
        "Two traps, both measured in a fresh directory with the network blocked when this archive was made:",
        "",
        f"- `verify_bundle.py --corrupt <pmid> <limb>` is **not** a must-fail control. It mutates one row in memory and "
        "reports which rows stop being ADMISSIBLE (read its `corruption` line); its verdict stays `PASS` and it exits 0. "
        f"(`site/reviews/{slug}/REPLAY.md` calls it \"a control: must refuse\"; measured, it does not.)",
        "- `verify_bundle.py --anchor live` with no network printed `verdict PASS` with **0 of 11** live fetches made. The "
        "verdict does not say whether the live observation happened: read each `anchor` line's `live: fetched=` field. "
        "`fetched=False` everywhere means no external observation was made, whatever the verdict says.",
        "",
        "## Replay: what needs a clone",
        "",
        "Regenerating the page from its inputs (the review core, certificate and page bytes) needs the repository at the "
        "commit, because the build reads the committed cache, protocol and topic configuration, which are not all served. "
        "A checkout is ~1.9 GB of files (plus history; a full clone of every blob is far larger). **This lane did not run "
        "the steps below for this archive** (the machine that built it had under 2 GB free); they are the commands the "
        "execution record names, and `REPLAY.md` records the last measured replay and its tolerances:",
        "",
        "```",
        "git clone --filter=blob:none https://github.com/mahmood726-cyber/meta-harness.git && cd meta-harness",
        f"git checkout {c}",
        "git status --porcelain                       # must print nothing",
        f"python scripts/build_topic.py {slug} --now 2026-09-11",
        f"python scripts/build_bundle.py {slug}",
        f"git diff --stat -- docs/reviews/{slug}/     # expect only the execution record and the bundle's build fields",
        "```",
        "",
        f"`docs/reviews/{slug}/REPLAY.md` (in this archive at `site/reviews/{slug}/REPLAY.md`) states per output what "
        "reproduces exactly and what within a declared tolerance.",
        "",
        "## What an outsider can and cannot do, by network",
        "",
        "| machine | can | cannot |",
        "|---|---|---|",
        "| full network | download the archive or clone; everything below; `verify_bundle.py --url " + site + " --slug "
        + slug + "` against the live site; `--anchor live` (re-fetch PubMed now) | -- |",
        "| github.com and github.io reachable, `raw.githubusercontent.com` blocked | download the archive from the Pages URL; "
        "clone over git (github.com); every offline check; `--url` against the live site (it fetches from github.io, not "
        "raw) | anything that fetches from raw.githubusercontent.com; `--anchor live` if NCBI is also blocked |",
        "| no DNS / no network | the offline checks above, on an archive carried in by hand, after checking its sha256 "
        "against a digest obtained out of band | download, clone, `--url`, `--anchor live`; establishing that the live site "
        "still serves these bytes; regenerating the page (needs the clone) |",
        "",
        "## What a PASS here does not establish",
        "",
        "- that the live site serves these bytes today (only the production record, or a fetch, says what was served);",
        "- anything the verifiers print under `NOT checked:` -- upstream fidelity of any held representation, completeness of "
        "the source set, clinical interpretation, and more;",
        "- that the review is a version-1 release: it is served " + str(r["release_status"]) + ".",
        "",
    ]
    return "\n".join(lines)


def check(zpath: Path) -> int:
    """Unpack into a fresh temporary directory and run the archive's own offline replay. Exit 0 iff all pass."""
    sys.path.insert(0, "")
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)
        (root,) = [p for p in Path(tmp).iterdir() if p.is_dir()]
        rel = json.loads((root / "RELEASE.json").read_text(encoding="utf-8"))
        kw = dict(cwd=root, capture_output=True, text=True, stdin=subprocess.DEVNULL, env={**os.environ, "PYTHONPATH": ""})
        runs = [("check_sha256sums.py", subprocess.run([sys.executable, "check_sha256sums.py"], **kw)),
                ("verify_bundle.py --root site", subprocess.run(
                    [sys.executable, "site/scripts/verify_bundle.py", "--root", "site", "--slug", rel["slug"]], **kw)),
                ("audit_certificate_stdlib.py ... site", subprocess.run(
                    [sys.executable, "site/scripts/audit_certificate_stdlib.py",
                     f"site/reviews/{rel['slug']}/CERTIFICATE.json", "site"], **kw)),
                ("plant_control.py", subprocess.run([sys.executable, "plant_control.py"], **kw))]
        bad = 0
        for label, p in runs:
            lines = p.stdout.splitlines()
            last = next((ln for ln in lines if ln.startswith(("bundle schema", "RESULT", "CONTROL"))
                         or ln.endswith("match SHA256SUMS")), (lines or [""])[-1])
            print(f"rc={p.returncode} {label}\n    {last}")
            bad += p.returncode != 0
        return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--slug", required=True)
    b.add_argument("--commit", required=True)
    b.add_argument("--out", default=str(ROOT / "docs" / "releases"))
    c = sub.add_parser("check")
    c.add_argument("zip")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        build(a.slug, a.commit, Path(a.out))
        return 0
    return check(Path(a.zip))


if __name__ == "__main__":
    sys.exit(main())
