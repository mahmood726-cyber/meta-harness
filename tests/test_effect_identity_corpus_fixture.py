"""Pinned git corpus regression; run this file only, with no cache provider."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "evidence" / "fixtures" / "build_effect_identity_fixture.py"
spec = importlib.util.spec_from_file_location("effect_identity_fixture_builder", BUILDER)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


@pytest.fixture(scope="module")
def corpus():
    try:
        return builder.build_fixture()
    except subprocess.CalledProcessError as exc:
        pytest.fail(f"Pinned corpus {builder.PINNED} is required (never skip): "
                    f"{exc.stderr.decode(errors='replace')}", pytrace=False)
    except ValueError as exc:
        pytest.fail(f"Pinned corpus cannot be evaluated: {exc}", pytrace=False)


def test_recomputes_exact_fixture_and_report(corpus):
    fixture = builder.DEST / "effect_identity_corpus.json"
    assert corpus == json.loads(fixture.read_text(encoding="utf-8"))
    assert builder.markdown(corpus) == (builder.DEST / "EFFECT_IDENTITY_FIXTURE.md").read_text(encoding="utf-8")


def test_inventory_and_denominators_do_not_drop_rows(corpus):
    slugs, blobs, _ = builder.pinned_inputs()
    expected = []
    for slug in slugs:
        review = blobs[f"docs/reviews/{slug}/review.json"]
        for oi, outcome in enumerate(review["outcomes"]):
            for ri, row in enumerate(outcome.get("trials") or []):
                expected.append((slug, outcome["name"], row.get("id"), oi, ri))
    assert corpus["slugs"] == slugs
    actual = [(r["slug"], r["outcome"], r["trial_id"], r["outcome_index"], r["row_index"])
              for r in corpus["per_row"]]
    assert actual == expected
    assert len(actual) == len(set(actual))
    assert not any(str(r["trial_id"]).startswith("__control_") for r in corpus["per_row"])
    for rule in builder.DENOMINATORS:
        applicable = [r for r in corpus["per_row"] if r[rule]["applicable"]]
        total = corpus["totals"][rule]
        assert total["of"] == len(applicable)
        assert total["fires"] == sum(r[rule]["fires"] is True for r in applicable)
        assert total["kinds"] == dict(Counter(r[rule]["state"] for r in applicable))
        unknown = [r for r in applicable if r[rule]["state"] == "UNEVALUABLE"]
        recorded = [u for u in corpus["unevaluable"] if u["rule"] == rule]
        assert [builder.identity(r) for r in unknown] == [builder.identity(u) for u in recorded]
        assert all(u["reason"] for u in recorded)
        assert all(r[rule]["reason"] for r in corpus["per_row"] if not r[rule]["applicable"])


@pytest.mark.parametrize("rule", list(builder.DENOMINATORS))
@pytest.mark.parametrize("positive", [True, False], ids=["positive", "negative"])
def test_synthetic_rule_control(corpus, rule, positive):
    controls = [c for c in corpus["controls"] if c["rule"] == rule and c["expected_fire"] is positive]
    assert len(controls) == 1
    control = controls[0]
    assert control["name"].startswith("__control_")
    # JSON serialisation copies row/pool objects: restore the same object identity
    # used by production hr_route's `t is not row` condition.
    inputs = dict(control["inputs"])
    inputs["row"] = inputs["pool"][0]
    computed = builder.evaluate(**inputs)[rule]
    assert computed == control["result"]
    assert computed["state"] != "UNEVALUABLE", f"{control['name']}: {computed.get('reason')}"
    assert computed["applicable"], f"Control must exercise {rule}, not an applicability bypass"
    assert computed["fires"] is positive


def test_missing_commit_is_failure_not_skip(monkeypatch):
    def missing(*args, **kwargs):
        raise subprocess.CalledProcessError(128, ["git", *args], stderr=b"missing pinned commit")
    monkeypatch.setattr(builder, "git", missing)
    with pytest.raises(subprocess.CalledProcessError):
        builder.build_fixture("0" * 40)
