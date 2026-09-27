"""Preregistration vs build SHA (audit 20, P0). The displayed protocol SHA is usually a BUILD commit
(protocol + cache + synthesis + page together), which cannot demonstrate the protocol preceded
synthesis. The harness must distinguish a protocol-ONLY prospective commit from the build, render which,
and the gate must refuse a page that CLAIMS prospective registration while citing a build commit.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import registration, gate  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs", "reviews")


def test_preregistration_resolver_shape():
    # every live topic resolves to a well-formed preregistration object
    for slug in sorted(os.listdir(DOCS)):
        if not os.path.exists(os.path.join(DOCS, slug, "review.json")):
            continue
        pre = registration.preregistration_sha(slug)
        assert set(pre) >= {"prospective", "sha", "kind", "build_sha"}, pre
        if pre["prospective"]:
            # a claimed prospective registration MUST be a protocol-only commit
            assert pre["sha"] and not registration.is_build_commit(pre["sha"]), \
                f"{slug}: prospective SHA {pre['sha']} is a build commit"


def test_every_served_page_prereg_claim_is_honest():
    # no served page may claim prospective registration while citing a build commit (the gate limb)
    for slug in sorted(os.listdir(DOCS)):
        rp = os.path.join(DOCS, slug, "review.json")
        if not os.path.exists(rp):
            continue
        assert gate.check_preregistration_not_build(os.path.join(DOCS, slug)) == [], slug


def test_build_commit_classifier():
    # a commit touching cache/ or docs/reviews/ is a build commit; refuse to call it prospective
    # (uses the doac-vte displayed SHA, which audit 20 showed is a build commit)
    rev = json.load(open(os.path.join(DOCS, "doac-vte-recurrence", "review.json"), encoding="utf-8"))
    bsha = ((rev.get("reproduction") or {}).get("preregistration") or {}).get("build_sha")
    if bsha:
        assert registration.is_build_commit(bsha) is True, f"doac-vte build_sha {bsha} should classify as build"
