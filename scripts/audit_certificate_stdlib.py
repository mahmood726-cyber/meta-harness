#!/usr/bin/env python3
"""Independent recomputation of an evidence certificate's self-consistency, standard library only.

    python audit_certificate_stdlib.py <CERTIFICATE.json> [<source tree>]

Imports nothing from the harness, on purpose: this script is what a third party runs to check
that the certificate's digests follow from its own contents and from source bytes, using the
procedure the certificate states, not the code the certificate pins. It recomputes:

  release_sha256        = sha256(canonical(certificate without 'release_sha256'))
  analysis_code_sha256  = sha256(canonical(analysis_code_blobs))
  analysis_code_blobs   = for each path, sha1('blob ' + len + NUL + LF-normalised bytes)
                          of <source tree>/<path>   (only when a source tree is given)

where canonical(x) = json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
encoded as UTF-8. Exit 0 iff every recomputed value equals the stored one; each mismatch is
printed with both values. NOT_PRESENT entries are checked as absence of the file.
"""
import hashlib
import json
import sys
from pathlib import Path


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def blob_sha1(path):
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cert = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    tree = Path(argv[2]) if len(argv) > 2 else None
    failures = []

    body = {k: v for k, v in cert.items() if k != "release_sha256"}
    release = sha256(canonical(body))
    print(f"release_sha256        stored {cert.get('release_sha256')}")
    print(f"                      recomputed {release}")
    if release != cert.get("release_sha256"):
        failures.append("release_sha256")

    blobs = cert.get("analysis_code_blobs")
    code = sha256(canonical(blobs))
    print(f"analysis_code_sha256  stored {cert.get('analysis_code_sha256')}")
    print(f"                      recomputed {code}")
    if code != cert.get("analysis_code_sha256"):
        failures.append("analysis_code_sha256")

    if tree is not None and isinstance(blobs, dict):
        checked = 0
        for ref, stored in sorted(blobs.items()):
            path = tree / ref
            if stored == "NOT_PRESENT":
                if path.exists():
                    failures.append(f"{ref}: stored NOT_PRESENT but file exists")
                continue
            if not path.is_file():
                failures.append(f"{ref}: stored {stored} but file absent")
                continue
            got = blob_sha1(path)
            checked += 1
            if got != stored:
                failures.append(f"{ref}: stored {stored} recomputed {got}")
        print(f"analysis_code_blobs   {checked} blob identities recomputed from {tree}, "
              f"{sum(1 for v in blobs.values() if v == 'NOT_PRESENT')} NOT_PRESENT checked as absent")
    elif tree is None:
        print("analysis_code_blobs   not checked against source bytes (no source tree given)")

    for failure in failures:
        print("MISMATCH", failure)
    print("RESULT", "REPRODUCED" if not failures else f"NOT REPRODUCED ({len(failures)} mismatches)")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
