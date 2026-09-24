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

and, when the review's other served files sit beside the certificate (review.json, manifest.json,
index.html -- the layout of docs/reviews/<slug>/ and of the served site), the links from the
certificate to the numbers and the page:

  review_sha256         = sha256(canonical(review.json without 'reproduction'))  == certificate's
  review.json's embedded reproduction.certificate                               == CERTIFICATE.json
  manifest.json review_sha256                                                   == certificate's
  manifest.json html_sha256                                                     == sha256(index.html bytes)
  the release_sha256 index.html prints (exactly one)                            == certificate's

where canonical(x) = json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
encoded as UTF-8. Exit 0 iff every recomputed value equals the stored one; each mismatch is
printed with both values. NOT_PRESENT entries are checked as absence of the file. A sibling file
that is absent is reported as NOT CHECKED on the RESULT line -- never counted as a pass.

What it does NOT check is NOT_CHECKED below; it is printed on every run, and every served review
page quotes it from these bytes (harness/page.py), so the page and the script cannot disagree.
tests/test_page_verifier.py plants each item and shows this script still prints REPRODUCED.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

NOT_CHECKED = [
    "that the page's content is a rendering of review.json: the page is tied to it only through manifest.json's html_sha256, which the certificate does not cover -- a page and manifest changed together pass; only re-rendering (scripts/reproduce_review.py in a clone) checks the content",
    "no input digest (protocol, records, retrieval and screening ledgers, extraction objects, trial families, RoB, held documents, config, manuscript) is compared with any file's bytes",
    "no effect estimate, interval or pooled result is recomputed, and no number is compared with its source: review_sha256 ties the numbers to the certificate, not to the evidence",
    "without a source tree, analysis_code_blobs is not compared with any code bytes; with one, the bytes are shown to match the pins, not that the pinned code is correct",
    "without review.json, manifest.json and index.html beside the certificate, none of the links to the numbers or the page is checked (the RESULT line then says so)",
]

_PRINTED_RELEASE = re.compile(r"release_sha256</strong> <code[^>]*>([0-9a-f]{64})")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def blob_sha1(path):
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _links(cert, here, failures):
    """The certificate -> numbers -> page links, from the files beside the certificate. Returns the scope checked."""
    rj, mj, ih = here / "review.json", here / "manifest.json", here / "index.html"
    absent = [p.name for p in (rj, mj, ih) if not p.is_file()]
    if absent:
        print(f"links                 NOT CHECKED: {', '.join(absent)} not beside the certificate")
        return "certificate only; links to the numbers and the page NOT CHECKED (" + ", ".join(absent) + " absent)"
    review = json.loads(rj.read_text(encoding="utf-8"))
    manifest = json.loads(mj.read_text(encoding="utf-8"))
    page = ih.read_bytes()
    core = {k: v for k, v in review.items() if k != "reproduction"}
    got = sha256(canonical(core))
    print(f"review_sha256         stored {cert.get('review_sha256')}")
    print(f"                      recomputed from review.json {got}")
    if got != cert.get("review_sha256"):
        failures.append("review_sha256: review.json does not hash to the certificate's review_sha256")
    embedded = (review.get("reproduction") or {}).get("certificate")
    print(f"embedded certificate  {'equal' if canonical(embedded) == canonical(cert) else 'DIFFERENT'} (review.json reproduction.certificate vs this file)")
    if canonical(embedded) != canonical(cert):
        failures.append("review.json's embedded certificate differs from CERTIFICATE.json")
    if manifest.get("review_sha256") != cert.get("review_sha256"):
        failures.append(f"manifest.json review_sha256 {manifest.get('review_sha256')} != certificate's")
    html = hashlib.sha256(page).hexdigest()
    print(f"html_sha256           manifest {manifest.get('html_sha256')}")
    print(f"                      index.html {html}")
    if manifest.get("html_sha256") != html:
        failures.append("index.html does not hash to manifest.json's html_sha256")
    printed = _PRINTED_RELEASE.findall(page.decode("utf-8", errors="replace"))
    print(f"page prints           release_sha256 {printed}")
    if printed != [cert.get("release_sha256")]:
        failures.append(f"index.html prints release_sha256 {printed}, not exactly the certificate's")
    return "certificate + review.json + manifest.json + index.html"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cert_path = Path(argv[1])
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
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

    scope = _links(cert, cert_path.resolve().parent, failures)

    for failure in failures:
        print("MISMATCH", failure)
    print("NOT checked: " + "; ".join(NOT_CHECKED))
    print("RESULT", ("REPRODUCED" if not failures else f"NOT REPRODUCED ({len(failures)} mismatches)") + f" [scope: {scope}]")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
