"""The served evidence bundle: every object the certificate commits a digest to is reachable from BUNDLE.json,
byte-identical to the digest, and never silently omitted.

Closes the 2026-09-19 defect: CERTIFICATE.json committed digests to files that 404'd on the served site
(14 of 18 probed URLs). See scripts/build_bundle.py for the design and the CRLF trap it guards.
"""
import hashlib
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import build_bundle  # noqa: E402

SLUG = "glp1-ra-mace-t2d"
BUNDLE = os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json")
CERT = os.path.join(ROOT, "docs", "reviews", SLUG, "CERTIFICATE.json")


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _check_attr(path):
    out = subprocess.run(["git", "check-attr", "text", "--", path], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return out.rsplit(":", 1)[-1].strip()


@pytest.fixture(scope="module")
def bundle():
    if not os.path.exists(BUNDLE):
        pytest.fail("docs/reviews/%s/BUNDLE.json absent -- python scripts/build_bundle.py %s" % (SLUG, SLUG))
    return _load(BUNDLE)


def test_bundle_is_current():
    """A stale bundle is the same defect as no bundle: a digest table that does not describe the served bytes."""
    _, problems = build_bundle.build(SLUG, check_only=True)
    assert not problems, "\n".join(problems)


def test_certificate_unmodified(bundle):
    with open(CERT, "rb") as f:
        raw = f.read()
    assert bundle["certificate_unmodified"] is True
    assert bundle["certificate"]["sha256_of_file"] == hashlib.sha256(raw).hexdigest()
    assert bundle["certificate"]["bytes"] == len(raw)
    assert bundle["certificate"]["release_sha256"] == json.loads(raw)["release_sha256"]


def test_every_certificate_input_appears_in_one_state(bundle):
    """No silent omission: each input the certificate reads is SERVED or WITHHELD-with-reason, never absent."""
    cert = _load(CERT)
    expected = {e["ref"] for e in build_bundle.enumerate_inputs(SLUG, cert)}
    expected |= {h["ref"] for h in cert["held_documents"]}
    listed = {a["ref"] for a in bundle["artefacts"]}
    assert listed == expected, {"missing": sorted(expected - listed), "extra": sorted(listed - expected)}
    states = {a["state"] for a in bundle["artefacts"]}
    assert states <= {"SERVED", "WITHHELD"}
    assert bundle["counts"]["certificate_inputs"] == len(bundle["artefacts"])
    assert bundle["counts"]["served"] + bundle["counts"]["withheld"] == len(bundle["artefacts"])


def test_served_bytes_match_declared_digests(bundle):
    """The served file at docs/<ref> hashes to what BUNDLE.json says AND to what the certificate committed."""
    for a in bundle["artefacts"]:
        if a["state"] != "SERVED":
            continue
        assert a["served_path"] == a["ref"], a["ref"]
        p = os.path.join(ROOT, "docs", *a["ref"].split("/"))
        assert os.path.isfile(p), "not served: docs/" + a["ref"]
        with open(p, "rb") as f:
            data = f.read()
        assert len(data) == a["bytes"], a["ref"]
        assert hashlib.sha256(data).hexdigest() == a["sha256"], a["ref"]
        if a["declared_digest"] is not None:
            assert build_bundle.recompute(a, data) == a["declared_digest"], (a["ref"], a["role"])


def test_withheld_entries_name_a_reason_and_still_verify(bundle):
    """WITHHELD is a licence statement, not a gap: the reason and a route to the bytes are stated, and the bytes
    we hold (tracked at the same ref) still hash to the certificate's digest."""
    withheld = [a for a in bundle["artefacts"] if a["state"] == "WITHHELD"]
    assert withheld, "the bundle declares no WITHHELD input; if that is now true, delete this assertion deliberately"
    for a in withheld:
        assert a["served_path"] is None
        assert len(a["reason"]) > 40, a["ref"]
        assert a["obtain_from"].startswith("https://"), a["ref"]
        assert not os.path.exists(os.path.join(ROOT, "docs", *a["ref"].split("/"))), "withheld but served: " + a["ref"]
        with open(os.path.join(ROOT, *a["ref"].split("/")), "rb") as f:
            data = f.read()
        assert hashlib.sha256(data).hexdigest() == a["sha256"] == a["declared_digest"], a["ref"]


def test_mirror_paths_are_never_normalised(bundle):
    """The CRLF trap. Every served mirror path must carry -text; a CR-bearing export under text=auto would be
    rewritten on checkin and served off its digest. Checked with git's own attribute resolution, not by reading
    .gitattributes."""
    crlf_seen = 0
    for a in bundle["artefacts"]:
        if a["state"] != "SERVED":
            continue
        rel = "docs/" + a["ref"]
        assert _check_attr(rel) == "unset", rel + " is not -text"
        with open(os.path.join(ROOT, *rel.split("/")), "rb") as f:
            crlf_seen += b"\r" in f.read()
    assert crlf_seen >= 3, "the plant is gone: no CR-bearing served file remains to exercise the rule"
    # The rule is scoped to the mirror, not the whole of docs/: the served pages keep the repo-wide LF contract.
    assert _check_attr("docs/reviews/%s/review.json" % SLUG) == "auto"


def test_normalised_copy_would_be_refused(bundle):
    """Plant: strip CRs from a CR-bearing export and confirm the digest check would refuse it."""
    victim = next(a for a in bundle["artefacts"] if a["state"] == "SERVED"
                  and a["role"] == "held_documents" and a["ref"].endswith(".pdf.txt")
                  and b"\r" in open(os.path.join(ROOT, *a["ref"].split("/")), "rb").read())
    with open(os.path.join(ROOT, *victim["ref"].split("/")), "rb") as f:
        data = f.read()
    normalised = data.replace(b"\r\n", b"\n")
    assert normalised != data
    assert build_bundle.recompute(victim, normalised) != victim["declared_digest"]
    assert build_bundle.recompute(victim, data) == victim["declared_digest"]


def test_review_files_listed_with_current_digests(bundle):
    review_dir = os.path.join(ROOT, "docs", "reviews", SLUG)
    listed = {r["file"]: r for r in bundle["review_files"]}
    on_disk = {n for n in os.listdir(review_dir) if os.path.isfile(os.path.join(review_dir, n)) and n != "BUNDLE.json"}
    assert set(listed) == on_disk
    for name, row in listed.items():
        with open(os.path.join(review_dir, name), "rb") as f:
            data = f.read()
        assert row["bytes"] == len(data) and row["sha256"] == hashlib.sha256(data).hexdigest(), name
        assert row["served_path"] == "reviews/%s/%s" % (SLUG, name)


def test_path_scheme_resolves_from_review_root(bundle):
    """A reader at reviews/<slug>/BUNDLE.json reaches every served object by ../../<ref>; no path is guessed."""
    for a in bundle["artefacts"]:
        if a["state"] == "SERVED":
            assert a["served_url"] == bundle["path_scheme"]["site_root"] + a["ref"]
            assert ".." not in a["ref"] and not a["ref"].startswith("/")
