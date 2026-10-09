"""The RapidMeta tab contract (rapidmeta-v1, harness/review_tabs.py), on every committed review and every served page.

Requirement (Mahmood, 8 Oct: "complete reviews on their URLs in rapid meta style, fully transparent tabs"): every topic
page carries Protocol, Search, Screening, Included studies, Data extraction, Risk of bias & GRADE, Analysis, Results &
conclusions, Comparison with the published meta-analysis, Changes & signatures and Reproduce; no tab is empty unless it
states why; every pooled number shows its passage and a digest an outsider can recompute; signed notices keep the bytes
their signature covers; the topic's ACTIVE / ABANDONED_BY_DECISION state comes from the committed registry. Each clause
has a plant that must fire.
"""
from __future__ import annotations

import hashlib
import html as H
import json
import re
from pathlib import Path

import pytest

from harness import page, review_tabs as T

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = sorted((ROOT / "docs" / "reviews").glob("*/review.json"))


def _review(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def test_there_are_32_committed_reviews():
    assert len(REVIEWS) >= 32


@pytest.mark.parametrize("path", REVIEWS, ids=lambda p: p.parent.name)
def test_every_committed_review_renders_every_required_tab(path):
    r = json.loads(path.read_text(encoding="utf-8"))
    assert T.tab_contract_problems(page.render_page(r)) == []


@pytest.mark.parametrize("path", sorted((ROOT / "docs" / "reviews").glob("*/index.html")), ids=lambda p: p.parent.name)
def test_every_served_page_keeps_the_tab_contract(path):
    assert T.tab_contract_problems(path.read_text(encoding="utf-8")) == []


def test_plant_an_empty_tab_is_named(monkeypatch):
    monkeypatch.setitem(page._R, "included", lambda r, n: "")
    probs = T.tab_contract_problems(page.render_page(_review("dpp4-mace-t2d")))
    assert any("tab included is empty" in p for p in probs), probs


def test_plant_a_missing_tab_is_named(monkeypatch):
    monkeypatch.setattr(page, "TABS", [t for t in page.TABS if t[0] != "changes"])
    probs = T.tab_contract_problems(page.render_page(_review("dpp4-mace-t2d")))
    assert any("tab changes is missing" in p for p in probs), probs


def test_plant_a_tab_with_neither_table_nor_reason_is_named(monkeypatch):
    monkeypatch.setitem(page._R, "analysis", lambda r, n: "<p>Analysis.</p>")
    probs = T.tab_contract_problems(page.render_page(_review("dpp4-mace-t2d")))
    assert any("tab analysis shows neither" in p for p in probs), probs


def test_status_comes_from_the_registry_and_plant_flips_it(monkeypatch):
    reg = json.loads((ROOT / "registry" / "g1_abandoned.json").read_text(encoding="utf-8"))
    abandoned = {t["slug"] for t in reg["topics"] if t["state"] == "ABANDONED_BY_DECISION"}
    assert len(abandoned) == 10
    for p in REVIEWS:
        slug = p.parent.name
        want = "ABANDONED_BY_DECISION" if slug in abandoned else "ACTIVE"
        assert T.topic_status(slug)["state"] == want
    # plant: drop one topic from the registry -> its banner must read ACTIVE (the page has no other source)
    one = sorted(abandoned)[0]
    planted = dict(reg, topics=[t for t in reg["topics"] if t["slug"] != one])
    monkeypatch.setattr(T, "_registry", lambda name: planted if name == "g1_abandoned.json" else json.loads(
        (ROOT / "registry" / name).read_text(encoding="utf-8")))
    assert "data-topic-status='ACTIVE'" in T.status_banner(one)


def test_changes_tab_carries_the_signed_notice_bytes_unchanged():
    notices = [n for n in json.loads((ROOT / "docs" / "result_changes.json").read_text(encoding="utf-8"))["notices"]]
    slug = notices[0]["slug"]
    r = _review(slug)
    embedded = (r.get("reproduction") or {}).get("result_changes") or []
    assert embedded, "a topic with a notice must embed it"
    tab = T.changes_tab(r)
    for n in embedded:
        assert page.result_change_block(n) in tab       # the exact bytes the countersignature hashes
    assert "result-changes-pointer" in page._reproduction(r, False)


def test_extraction_digest_is_recomputable_from_the_shown_passage():
    r = _review("dpp4-mace-t2d")
    tab = T.extraction_tab(r)
    pairs = re.findall(r"<blockquote class='span'>(.*?)</blockquote><code class='digest'>sha256 ([0-9a-f]{64})</code>", tab, re.S)
    assert pairs
    for shown, digest in pairs:
        assert hashlib.sha256(H.unescape(shown).encode("utf-8")).hexdigest() == digest


def test_plant_a_reason_never_counts_as_the_thing_it_explains():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import review_tab_inventory as I
    r = _review("dpp4-mace-t2d")
    html = page.render_page(r)
    dec = I.g1_decision_ids(ROOT)
    notices = json.loads((ROOT / "docs" / "result_changes.json").read_text(encoding="utf-8"))["notices"]
    rob = I.check("dpp4-mace-t2d", html, r, notices, dec)["riskofbias"]
    assert rob["status"] == "REASONED" and not rob["elements"]["D11 reproducible-AI sign-off"]
    # plant: a recorded sign-off marker makes it COMPLETE -- so the check can pass, and only on the real thing
    planted = html.replace("<h4 id='d11-signoff'>", "<h4 id='d11-signoff' data-d11-signoff='RECORDED'>", 1)
    assert I.check("dpp4-mace-t2d", planted, r, notices, dec)["riskofbias"]["status"] == "COMPLETE"


def test_neutral_pages_carry_no_harness_provenance_tabs():
    html = page.render_page(_review("dpp4-mace-t2d"), neutral=True)
    for t in ("included", "extraction", "analysis", "changes", "comparator", "verify"):
        assert f'id="tab-{t}"' not in html
    assert "data-topic-status" not in html and "g1_decisions.json" not in html
    assert T.tab_contract_problems(html, neutral=True) == []


def test_heading_order_and_keyboard_tabs():
    html = page.render_page(_review("dpp4-mace-t2d"))
    levels = [int(x) for x in re.findall(r"<h([1-6])[\s>]", html)]
    assert levels[:3] == [1, 2, 3], levels[:3]               # h1 title, h2 'Review sections', h3 first tab name
    js = page._JS
    for need in ("role','tablist'", "role','tab'", "role','tabpanel'", "ArrowRight", "ArrowLeft", "aria-selected"):
        assert need in js


def test_extraction_tab_states_the_census_class_for_every_row(monkeypatch):
    """The page's provenance class is the provenance-census gate's class, row for row (one shared function)."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import provenance_census as pc
    cen = {}
    for x in pc.census(str(ROOT))["served"]["rows"]:
        cen.setdefault((x["slug"], x["outcome"], str(x["id"])), set()).add(x["class"])
    n = 0
    for p in REVIEWS:
        r = json.loads(p.read_text(encoding="utf-8"))
        for row in T.extraction_rows(r):
            assert row["class"] in cen[(r["slug"], row["outcome"], str(row["id"]))], (r["slug"], row["outcome"], row["id"])
            n += 1
    assert n > 50
    # plant: drop the recorded-read conversion from the page's path -> a converted row reads HAND_ENTERED and differs
    from harness import provenance_class as PC
    monkeypatch.setattr(PC, "recorded_reads", lambda root=None: {})
    r = _review("sacubitril-valsartan-hfref")
    planted = {(row["outcome"], str(row["id"])): row["class"] for row in T.extraction_rows(r)}
    assert any(v == "HAND_ENTERED" and "RECORDED_MODEL_CALL" in cen[(r["slug"], o, i)] for (o, i), v in planted.items())
