"""Mirror every certificate-pinned module into docs/, and refuse if any pin is unserved.

A CERTIFICATE's `analysis_code_blobs` is the AST import closure of the declared roots, and
`scripts/release_archive.py` requires that every pinned path `p` is also SERVED at `docs/<p>` with
exactly the pinned blob:

    if served.get(p) != v:
        raise SystemExit(f"REFUSED: docs/{p} ... is blob {served.get(p)}; {slug}'s certificate pins {v}")

Nothing in the tree kept the two in step. The mirror was populated by hand when the closure was
introduced, so editing a pinned module -- or adding one, which the closure does automatically the
moment something imports it -- left `docs/` stale and the refusal surfaced hours later inside a
gate run. That is the kind of rule that depends on someone remembering, and it fails silently.

This is that step, written down: derive the pin set from the certificates themselves (never a
hand-kept list, which is the defect the closure was introduced to remove), copy what differs, and
then VERIFY by re-hashing rather than by trusting the copy. Exit 1 if any pin is still unserved,
so it can be used as a check as well as a fix.

    python scripts/sync_served_code.py            # report only, exit 1 if out of step
    python scripts/sync_served_code.py --write    # copy, then verify
"""
import glob
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pinned_paths():
    """{path: blob} union over every served certificate. NOT_PRESENT is a declared absence."""
    pins = {}
    for cert_path in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "CERTIFICATE.json"))):
        with open(cert_path, encoding="utf-8") as fh:
            cert = json.load(fh)
        for path, blob in (cert.get("analysis_code_blobs") or {}).items():
            if blob == "NOT_PRESENT":
                continue
            pins.setdefault(path, set()).add(blob)
    return pins


def blob_of(rel):
    out = subprocess.run(["git", "hash-object", rel], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def main(write):
    pins = pinned_paths()
    copied, missing, mismatch, disagreeing = [], [], [], []

    for path, blobs in sorted(pins.items()):
        if len(blobs) > 1:
            # Two certificates pinning different bytes for one module means the topics were built
            # against different code; syncing would hide it, so it is reported instead.
            disagreeing.append((path, sorted(blobs)))
            continue
        want = next(iter(blobs))
        src = os.path.join(ROOT, *path.split("/"))
        dst = os.path.join(ROOT, "docs", *path.split("/"))
        if not os.path.exists(src):
            missing.append(path)
            continue
        if write and (not os.path.exists(dst) or open(src, "rb").read() != open(dst, "rb").read()):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            copied.append(path)
        got = blob_of("docs/" + path)
        if got != want:
            mismatch.append((path, got or "MISSING", want))

    print(f"pinned modules: {len(pins)}   copied: {len(copied)}")
    for path in copied:
        print(f"  copied  docs/{path}")
    for path in missing:
        print(f"  REFUSED source missing for a pinned module: {path}")
    for path, blobs in disagreeing:
        print(f"  REFUSED certificates disagree on {path}: {blobs}")
    for path, got, want in mismatch:
        print(f"  UNSERVED docs/{path}: served {got}, certificates pin {want}")

    if missing or disagreeing or mismatch:
        print("REFUSED: the served code mirror does not match what the certificates pin.")
        return 1
    print("every certificate-pinned module is served at docs/<path> with the pinned blob.")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv[1:]))
