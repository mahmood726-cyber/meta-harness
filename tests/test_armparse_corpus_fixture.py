"""Recompute the whole pinned corpus; missing history is a failure, never a skip."""
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evidence.fixtures import build_armparse_fixture as corpus
from harness import arm_object, arm_parse, screen


@pytest.fixture(scope="module")
def recomputed():
    try:
        return corpus.build()
    except (subprocess.CalledProcessError, ValueError) as exc:
        pytest.fail(f"Pinned corpus unavailable or invalid (never skip): {exc}", pytrace=False)


def test_json_and_report_recompute_exactly(recomputed):
    raw = (corpus.HERE / "armparse_corpus.json").read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert json.loads(raw) == recomputed
    if raw.decode("utf-8") != json.dumps(recomputed, ensure_ascii=False, indent=2) + "\n":
        pytest.fail("Fixture byte formatting differs: require UTF-8 without BOM, indent=2, LF newlines", pytrace=False)
    assert (corpus.HERE / "ARMPARSE_FIXTURE.md").read_text(encoding="utf-8") == corpus.report(recomputed)


def test_exhaustive_source_coverage_and_served_provenance(recomputed):
    try:
        slugs, src, hashes = corpus.sources()
    except (subprocess.CalledProcessError, ValueError) as exc:
        pytest.fail(f"Pinned commit/blobs missing: {exc}", pytrace=False)
    assert len(slugs) == 32
    assert [t["slug"] for t in recomputed["topics"]] == slugs
    assert recomputed["source_sha256"] == hashes
    expected = {}
    for slug in slugs:
        for collection in ("records", "ctgov"):
            for index, rec in enumerate(src[f"cache/{slug}/records.json"][collection]):
                if len(rec.get("interventions") or []) >= 2:
                    expected[slug, collection, index] = rec
    actual = {(r["slug"], r["collection"], r["index"]): r for r in recomputed["records"]}
    assert len(actual) == len(recomputed["records"])
    assert actual.keys() == expected.keys()
    for key, rec in expected.items():
        row = actual[key]
        assert row["id"] == rec["id"]
        assert [a["parse"]["label"] for a in row["arms"]] == rec["interventions"]
        decisions = src[f"docs/reviews/{row['slug']}/review.json"]["screening"]["records"]
        matches = [d for d in decisions if str(d["id"]) == str(rec["id"]) or
                   (rec.get("id_type") == "nct" and str(rec["id"]) in re.findall(r"\bNCT\d{8}\b", str(d["id"])))]
        assert len(matches) <= 1
        assert row["served_screening"] == (matches[0] if matches else None)
        registry = src[row["registry_source"]]
        assert row["registry_design"] == registry.get(row["registry_key"])
        topic = src[f"topics/{row['slug']}.json"]
        assert row["interest"] == (topic.get("intervention_terms") or topic.get("include", {}).get("intervention_any") or [])
        assert row["ordered_contrast_interest"] == (topic.get("arm_object", {}).get("contrast", {}).get("drug_any") or row["interest"])


def test_both_callers_use_corpus_contract(recomputed, monkeypatch):
    for row in recomputed["records"]:
        labels = [a["parse"]["label"] for a in row["arms"]]
        rec = {"id": row["id"], "interventions": labels,
               "nct": row["registry_key"] if row["registry_key"].startswith("NCT") else None}
        kws = row["interest"]
        assert screen._record_arm_interventions_background_only(rec, kws)[0] == row["screen_fallback_every_arm"]
        monkeypatch.setattr(arm_object.design_key, "registry_designs", lambda _, r=row: {r["registry_key"]: r["registry_design"]})
        obj = arm_object.build(rec, {"slug": row["slug"], "intervention_terms": kws,
                                    "arm_object": {"contrast": {"drug_any": row["ordered_contrast_interest"]}}})
        assert obj["ordered_contrasts"] == row["ordered_contrasts"]
        assert obj["randomised_arm"] == [arm_object._arm(l) for l in labels]
        for contrast in row["ordered_contrasts"]:
            assert contrast["design"] == row["design"]


def test_independent_readings_are_complete_and_not_parser_generated(recomputed, monkeypatch):
    monkeypatch.setattr(arm_parse, "parse_arm", lambda _: pytest.fail("READING must not call parser"))
    monkeypatch.setattr(arm_parse, "exposure", lambda *_: pytest.fail("READING must not call exposure"))
    for row in recomputed["records"]:
        for arm in row["arms"]:
            label = arm["parse"]["label"]
            if any(w in label.lower() for w in ("placebo", "sham", "dummy", "matching")):
                assert arm["READING"] == corpus.reading(label)
                assert arm["reading_disagrees"] == (arm["READING"]["exposure"] != arm["exposure"])
            else:
                assert arm["READING"] is None
    with pytest.raises(ValueError, match="Unreviewed"):
        corpus.reading("previously unseen placebo label")


def test_synthetic_controls_are_separate_and_assert_expected_invariants(recomputed):
    controls = recomputed["controls_excluded_from_totals"]
    assert all(c["id"].startswith("__control_") for c in controls)
    assert all(not str(r["id"]).startswith("__control_") for r in recomputed["records"])
    for c in controls:
        if "expected_exposures" in c:
            assert c["exposures"] == c["expected_exposures"]
        if "expected_every" in c:
            assert c["interest_in_every_arm"] is c["expected_every"]
    by_id = {c["id"]: c for c in controls}
    assert by_id["__control_miro"]["interest_in_every_arm"] is True
    assert by_id["__control_doac"]["interest_in_every_arm"] is True
    design_phrase = by_id["__control_design_phrase"]
    assert "expected_exposures" not in design_phrase and "expected_every" not in design_phrase


def test_denominators_and_every_disagreement_are_reported(recomputed):
    f = recomputed
    rows = f["records"]
    arms = [a for r in rows for a in r["arms"]]
    total = f["totals"]
    assert total["interest_in_every_arm"]["of"] == len(rows)
    assert sum(total[f"exposure_{s}"]["fires"] for s in ("ACTIVE", "MATCHED_PLACEBO", "VARIES_WITHIN_ARM", "ABSENT")) == len(arms)
    assert total["reading_disagrees"]["of"] == sum(a["READING"] is not None for a in arms)
    assert total["reading_disagrees"]["fires"] == sum(a["reading_disagrees"] for a in arms)
    assert total["served_x_contrast_disagrees"]["of"] == sum(r["served_screening"] is not None for r in rows)
    report = corpus.report(f)
    for r in rows:
        d = r["served_screening"]
        mismatch = d is not None and (d["rule_id"] == "X-CONTRAST") != r["interest_in_every_arm"]
        assert r["served_x_contrast_disagrees"] == mismatch
        if mismatch or any(a["reading_disagrees"] for a in r["arms"]):
            assert f"{r['slug']} / {r['id']}" in report
    # README numbers are comparisons, never enforced as corpus outcomes here.
    for key, comparison in f["readme_comparison"].items():
        assert comparison["observed"] == total[key]["fires"]
        assert comparison["agrees"] == (comparison["readme"] == comparison["observed"])
