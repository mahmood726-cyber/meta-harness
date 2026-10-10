"""C6: mixed input measures must remain visible in pooled-result labels."""
import copy
import html
import json
from pathlib import Path
import re

import pytest

from harness import manuscript, page
from harness.estmeasure import display_measure

REVIEWS = Path(__file__).resolve().parents[1] / "docs" / "reviews"
SINGLE = r"(?:HR|RR|IRR|OR|MD|SMD)"
BAD = re.compile(
    rf"Estimand\s+{SINGLE}(?=\s|$)|"
    rf"pooled\s+{SINGLE}\b(?![,/])|"
    rf"Pooling[^.]*?(?:gave\s+{SINGLE}\s|point estimate\s*\({SINGLE}\s)|"
    rf"[-+]?\d+(?:\.\d+)?\s*\({SINGLE}\)(?=, 95% CI|; no pooled)"
)


def plain(text):
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


@pytest.mark.parametrize("metadata", [
    {"scale_mixed": ["HR", "RR"]},
    {"estmeasure": {"status": "compatible_labels", "labels": ["HR", "RR"],
                    "classes": ["FIRST_EVENT_RATIO"]}},
])
def test_plant(metadata):
    # Deliberately constructed display-only fixture; no research result is generated.
    result = {"scale": "HR", "effect_label": "pooled HR", "k": 2,
              "estimate": 0.8, "ci_low": 0.6, "ci_high": 1.1,
              "estimate_fixed": 0.8, "ci_low_fixed": 0.7, "ci_high_fixed": 0.9,
              **metadata}
    original = copy.deepcopy(result)
    forest = manuscript.forest_for({"result": result, "trials": [
        {"label": "fixture", "scale": "HR", "effect": 0.8, "ci_low": 0.6, "ci_high": 1.1}
    ]})
    assert "mixed HR/RR" in forest
    assert not BAD.search(plain(forest))
    for refused in (False, True):
        if refused:
            result["pooled_ci_refused"] = {"reason": "constructed refusal"}
        rows = page._effect_rows(result) + [page._common_effect_row(result)]
        text = plain(" ".join(str(cell) for row in rows if row for cell in row))
        assert "mixed HR/RR" in text
        assert not BAD.search(text)
    result.pop("pooled_ci_refused")
    assert result == original
    assert display_measure({"scale": "HR"}) == "HR"


def sweep():
    paths = sorted(REVIEWS.glob("*/review.json"))
    assert len(paths) == 32
    violations = []
    for path in paths:
        review = json.loads(path.read_text(encoding="utf-8"))
        original = copy.deepcopy(review)
        # Render every review, including Analysis, claim and GRADE surfaces.
        rendered = page.render_page(review)
        assert rendered
        for outcome in review.get("outcomes", []):
            result = outcome.get("result") or {}
            em = result.get("estmeasure") or {}
            labels = set(em.get("labels") or []) | set(result.get("scale_mixed") or [])
            if len(labels) < 2:
                continue
            sections = [page.render_outcome_block(outcome)]
            if outcome is page._primary(review):
                sections += [page.render_overview(review), manuscript.render(review)]
            for section in sections:
                # Individual trial labels and source quotes are not pooled labels.
                for match in BAD.finditer(plain(section)):
                    violations.append((path.parent.name, match.group()))
        assert review == original, path.parent.name
    return violations


def test_sweep():
    assert sweep() == []
