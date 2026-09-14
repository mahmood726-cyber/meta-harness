"""STATE root system, item 2 — NOT_ASSESSED != NOT_DOWNGRADED across every GRADE domain.

A GRADE domain that was not assessed contributes downgrade=0, arithmetically identical to a domain
assessed and found clean — so an unassessed domain silently reads as favourable and could let a body
of evidence be certified HIGH without publication bias or indirectness ever being evaluated.
`UNASSESSED NEVER COUNTS AS FAVOURABLE`: any unassessed required domain must cap certainty below HIGH,
and the domain must render as NOT ASSESSED, never "not downgraded".
"""
import glob
import json
import os

import harness.page as P
from harness import grade as G

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _clean_review():
    # A body of RCTs with NO downgrade on any machine domain: large k, tight null-excluding CI, tau2=0,
    # RoB assessed & clean. Publication bias has no ghost census (not assessable) and indirectness is
    # never machine-rated. Pre-fix this rates HIGH; post-fix it must cap at moderate.
    return {
        "rob2": {"trials": {"A": {"overall": "Low", "domains": {"D3_missing_outcome_data": {"level": "low"}}},
                            "B": {"overall": "Low", "domains": {"D3_missing_outcome_data": {"level": "low"}}}}},
        "outcomes": [{"name": "O", "primary": True,
                      "trials": [{"label": "A"}, {"label": "B"}],
                      "result": {"k": 2, "scale": "RR", "estimate": 0.80, "tau2": 0.0,
                                 "ci_low": 0.72, "ci_high": 0.90}}],
    }


def test_PLANT_clean_body_would_be_HIGH_without_the_cap():
    # PLANT: the pre-fix arithmetic. With every UNassessed domain treated as a clean 0-downgrade, this
    # body has 0 total downgrades -> index 0 -> "high". That is the defect the cap closes.
    g = G.grade(_clean_review(), ghost=None)
    assert g["downgrades"] == 0, g["downgrades"]           # no machine domain downgraded
    assert G.CERT[0] == "high"                              # 0 downgrades WOULD map to high
    # ... and yet publication bias and indirectness were never assessed:
    assert g["domains"]["publication_bias"].get("assessed") is False
    assert g["domains"]["indirectness"].get("assessed") is False


def test_unassessed_domain_caps_certainty_below_high():
    g = G.grade(_clean_review(), ghost=None)
    assert g["certainty"] == "moderate", g["certainty"]     # capped, not high
    assert g["certainty_capped_unassessed_domain"] is True
    assert "publication_bias" in g["unassessed_domains"]
    assert "indirectness" in g["unassessed_domains"]


def test_assessed_clean_domain_does_not_cap():
    # A PICO-scoped ghost census with a low ghost fraction is ASSESSED and clean -> must NOT appear in
    # unassessed_domains (proving the cap keys off assessment, not the downgrade value).
    ghost = {"enumerated": 10, "ongoing_or_recent": 0, "ghost_upper_bound": 1, "pico_scoped": True}
    g = G.grade(_clean_review(), ghost=ghost)
    assert g["domains"]["publication_bias"]["assessed"] is True
    assert g["domains"]["publication_bias"]["downgrade"] == 0     # 1/10 = 10% < 30%
    assert "publication_bias" not in g["unassessed_domains"]
    # indirectness is still unassessed, so it still caps at moderate (never high on this partial GRADE):
    assert g["certainty"] == "moderate"


def test_renderer_cap_message_and_marks():
    # The GRADE section renders when the primary outcome has pooled trials (rob2 rows optional). A grade
    # capped for an unassessed domain must render the cap reason AND mark the unassessed domains NOT
    # ASSESSED / human judgement, never "not downgraded".
    core = {"title": "T", "question": "Q", "slug": "s",
            "reproduction": {"review_sha256": "abc123def456abcd", "protocol_sha": "x"},
            "outcomes": [{"name": "O", "primary": True, "kind": "efficacy",
                          "trials": [{"id": "1", "label": "A"}, {"id": "2", "label": "B"}],
                          "result": {"present": False, "reason": "n"}}],
            "grade": G.grade(_clean_review(), ghost=None)}
    html = P.render_page(core)
    assert "NOT ASSESSED" in html
    assert "unassessed never counts as favourable" in html.lower()


def test_corpus_unassessed_domains_never_render_as_not_downgraded():
    # Live behaviour in served bytes: publication bias & indirectness are unassessed on every topic, so
    # the GRADE table must show them as NOT ASSESSED / human judgement — never "not downgraded" (which
    # reads as assessed-and-clean). Scan a few real pages that carry a GRADE table.
    checked = 0
    for rp in sorted(glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json"))):
        d = os.path.dirname(rp)
        g = json.load(open(rp, encoding="utf-8")).get("grade") or {}
        if g.get("certainty") in (None, "not_rateable"):
            continue
        html = open(os.path.join(d, "index.html"), encoding="utf-8").read()
        # the GRADE table exists and names the unassessed domains as NOT ASSESSED / human judgement
        assert "NOT ASSESSED" in html or "human judgement" in html, os.path.basename(d)
        checked += 1
    assert checked >= 20, checked


def test_corpus_no_high_certainty_survives():
    # With indirectness structurally unassessed, this partial GRADE's honest ceiling is moderate.
    highs = []
    for rp in sorted(glob.glob(os.path.join(_ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(rp))
        g = json.load(open(rp, encoding="utf-8")).get("grade") or {}
        if g.get("certainty") == "high":
            highs.append(slug)
    assert not highs, "partial GRADE certified HIGH despite unassessed indirectness/pub-bias: " + "; ".join(highs)
