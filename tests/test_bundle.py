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


# ---------------------------------------------------------------------------------------------------------------
# fourth audit (2026-09-19): two identities per document, value -> digest in one hop, source identity of served bytes
# ---------------------------------------------------------------------------------------------------------------

def test_every_artefact_names_its_representation(bundle):
    """A single document_sha256 conflates the acquired original with a representation derived from it. Every entry
    must say which it is; a DERIVED entry must name its transform and say whether the original was retained."""
    kinds = set(bundle["representation_kinds"])
    for a in bundle["artefacts"]:
        rep = a["representation"]
        assert rep["kind"] in kinds, a["ref"]
        orig = rep["acquired_original"]
        if rep["kind"] == "DERIVED":
            assert "retained" in orig, a["ref"]
            assert rep["derived_representations"] and all(d.get("transform") for d in rep["derived_representations"]), a["ref"]
            if orig["retained"] is False:
                assert orig.get("note"), a["ref"] + ": an unretained original must be stated, not implied"
        if rep["kind"] == "ACQUIRED_AS_STORED":
            assert orig.get("is_this_file") is True and "acquisition_digest_recorded" in orig, a["ref"]
        assert rep["upstream_identity"], a["ref"]


def test_derived_text_points_at_an_original_with_the_recorded_digest(bundle):
    """The FDA text exports are derived from PDFs whose digests were recorded at acquisition. Where the PDF is served,
    its served bytes must carry that digest; where it is held off-tree (MedR, 37 MB), the entry must say so and still
    state the digest."""
    by_ref = {a["ref"]: a for a in bundle["artefacts"]}
    exports = [a for a in bundle["artefacts"] if a["ref"].endswith(".pdf.txt")]
    assert len(exports) == 4
    off_tree = 0
    for a in exports:
        orig = a["representation"]["acquired_original"]
        assert orig["sha256"] and orig["acquisition_digest_recorded"] is True, a["ref"]
        if orig["ref"]:
            assert by_ref[orig["ref"]]["sha256"] == orig["sha256"], a["ref"]
        else:
            off_tree += 1
            assert orig["served"] is False and orig["location"] and orig["note"], a["ref"]
    assert off_tree == 1, "exactly the MedR original is held off-tree"


def test_value_index_reaches_a_document_digest_in_one_hop(bundle):
    """Every rendered per-trial row of every outcome is present, carries the value the page shows, and points at a
    served document digest (or says NO_DOCUMENT_IN_BUNDLE); nothing here claims 'verified' without saying against
    which representation."""
    review = _load(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"))
    expected = {(o["name"], t["id"]) for o in review["outcomes"] for t in o["trials"]}
    rows = [v for v in bundle["value_index"] if v["entry"] == "TRIAL_ROW"]
    assert {(v["outcome"], v["trial"]["id"]) for v in rows} == expected
    by_key = {(o["name"], t["id"]): t for o in review["outcomes"] for t in o["trials"]}
    for v in rows:
        t = by_key[(v["outcome"], v["trial"]["id"])]
        assert v["value"] == {"scale": t.get("scale"), "effect": t.get("effect"), "ci_low": t.get("ci_low"), "ci_high": t.get("ci_high")}
        assert v["span_match"] in ("VERBATIM", "NORMALISED", "NOT_LOCATED", "NO_SPAN")
        assert v["span_location"], v["outcome_effect_id"]
        for d in v["span_location"]:
            if d.get("document_ref"):
                assert len(d["document_sha256"]) == 64 and d["served_path"] or d.get("state") == "WITHHELD", d
    pooled = [v for v in bundle["value_index"] if v["entry"] == "POOLED" and v["primary"]]
    assert len(pooled) == 1 and pooled[0]["k"] == 8


def test_value_index_records_non_verbatim_spans_instead_of_calling_them_verified(bundle):
    """The auditor's class, made mechanical: REWIND (31189511) and Harmony (30291013) render Lancet spans with the
    middle-dot decimals normalised; they must be reported NORMALISED, never VERBATIM. If a rebuild makes them
    verbatim, update this deliberately -- it is the record of what the page did."""
    rows = {v["trial"]["id"]: v for v in bundle["value_index"]
            if v["entry"] == "TRIAL_ROW" and v["outcome"].startswith("3-point")}
    assert rows["PMID 31189511"]["span_match"] == "NORMALISED"
    assert rows["PMID 30291013"]["span_match"] == "NORMALISED"
    assert all("middle dot" in step for v in (rows["PMID 31189511"], rows["PMID 30291013"])
               for d in v["span_location"] if d.get("match") == "NORMALISED" for step in d["normalisation"][-1:])
    assert rows["PMID 40162642"]["span_match"] == "VERBATIM"   # SOUL: verbatim in OUR cache -- the cache itself is stitched
    assert "our copy" in rows["PMID 40162642"]["what_verified_means_here"]


def test_locate_ladder():
    assert build_bundle.locate("HR 0.88 (0.79-0.99)", "... HR 0.88 (0.79-0.99) ...")["match"] == "VERBATIM"
    r = build_bundle.locate("HR 0.88 (0.79-0.99)", "... HR 0·88 (0·79–0·99) ...")
    assert r["match"] == "NORMALISED" and "middle dot" in r["normalisation"][-1]
    assert build_bundle.locate("HR 0.88 (0.79-0.99)", "... HR 0.86 (0.77-0.96) ...")["match"] == "NOT_LOCATED"
    assert build_bundle.locate("", "anything")["match"] == "NO_SPAN"


def test_source_block_names_a_commit_that_holds_the_served_bytes(bundle):
    """content_commit must contain exactly the served blobs (checkable by anyone with the repository), and the
    generating commit must be stated as NOT_RECORDED rather than borrowed from build_utc or packaging HEAD."""
    src = bundle["source"]
    assert src["generating_commit"] == "NOT_RECORDED"
    for name, blob in src["served_blob_git_sha1"].items():
        at = subprocess.run(["git", "rev-parse", f"{src['content_commit']}:docs/reviews/{SLUG}/{name}"],
                            cwd=ROOT, capture_output=True, text=True).stdout.strip()
        assert at == blob, (name, at, blob)
        with open(os.path.join(ROOT, "docs", "reviews", SLUG, name), "rb") as f:
            data = f.read()
        assert hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() == blob, name
    assert "may lag" in src["served_copy_may_lag"] and "refs/heads/main" in " ".join(src["how_to_check_currency"])


def test_manifest_carries_the_same_source_block(bundle):
    manifest = _load(os.path.join(ROOT, "docs", "reviews", SLUG, "manifest.json"))
    assert manifest["source"] == bundle["source"]
    assert manifest["build_utc"] and manifest["build_utc"] not in manifest["source"].values(), "build_utc is not repurposed"
    for k in ("review_sha256", "html_sha256", "protocol_sha"):
        assert manifest[k], k
