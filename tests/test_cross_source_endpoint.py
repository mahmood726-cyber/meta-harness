import json
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.page import render_page  # noqa: E402
from harness.pipeline import (  # noqa: E402
    CROSS_SOURCE_LOG_TOL,
    _classify_endpoint_match,
    _cross_source,
    build_review_core,
)
from harness.registration import protocol_sha  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git_show(path):
    return subprocess.check_output(
        ["git", "show", f"aa8ed28a:{path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )


def _load_json(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def _fourier_row(review):
    outcome = next(o for o in review["outcomes"] if o.get("name") == "Major adverse cardiovascular events")
    return next(t for t in outcome["trials"] if t.get("label") == "28304224")


def _rebuilt_core(slug):
    cfg = _load_json("topics", slug + ".json")
    records = _load_json("cache", slug, "records.json")
    return build_review_core(slug, cfg, records, protocol_sha(slug))


def _om(ai, n1, ci, n2, title="All-cause mortality"):
    return {
        "title": title,
        "type": "PRIMARY",
        "paramType": "COUNT_OF_PARTICIPANTS",
        "groups": [{"id": "g1", "title": "Drug"}, {"id": "g2", "title": "Placebo"}],
        "classes": [{"categories": [{"measurements": [
            {"groupId": "g1", "value": str(ai)},
            {"groupId": "g2", "value": str(ci)},
        ]}]}],
        "denoms": [{"units": "Participants", "counts": [
            {"groupId": "g1", "value": str(n1)},
            {"groupId": "g2", "value": str(n2)},
        ]}],
    }


def test_prefix_fourier_corroboration_plant_refuses_endpoint_mismatch():
    old_review = json.loads(_git_show("docs/reviews/pcsk9-mace/review.json"))
    old_row = _fourier_row(old_review)
    old_cs = old_row["cross_source"]
    registry_title = _load_json("cache", "pcsk9-mace", "records.json")["ctgov_results"]["NCT01764633"][0]["title"]

    assert old_cs["ctgov_rr"] == 0.666
    assert old_row["effect"] == 0.85
    assert abs(math.log(old_row["effect"] / old_cs["ctgov_rr"])) > CROSS_SOURCE_LOG_TOL

    verdict = _classify_endpoint_match(
        {"name": "Major adverse cardiovascular events", "keywords": ["major adverse cardiovascular events", "MACE"]},
        registry_title,
        old_row["effect"],
        old_cs["ctgov_rr"],
        registry_measure_type="COUNT_OF_PARTICIPANTS",
        pooled_scale="HR",
    )
    assert verdict["endpoint_match"] == "SECOND_SOURCE_DIFFERENT_ENDPOINT"
    assert verdict["identity"]["component_match"] is False
    assert "component set is not available" in verdict["endpoint_match_reason"]

    old_html = _git_show("docs/reviews/pcsk9-mace/index.html")
    assert "CT.gov RR 0.666" in old_html
    assert "shown for corroboration only" in old_html


def test_rebuilt_fourier_row_is_different_measure_not_corroboration():
    core = _rebuilt_core("pcsk9-mace")
    row = _fourier_row(core)
    cs = row["cross_source"]

    assert cs["endpoint_match"] == "SECOND_SOURCE_DIFFERENT_MEASURE"
    assert cs["corroborates_endpoint"] is False
    assert cs["registry_measure_type"] == "KM_ESTIMATE"
    assert cs["identity"]["measure_type"] == "KM estimate ratio"

    html = render_page(dict(core, reproduction={"failures": 0}))
    anchor = html.index("SECOND_SOURCE_DIFFERENT_MEASURE")
    snippet = html[anchor:anchor + 700]
    assert "✓ corroborated" not in snippet
    assert "KM_ESTIMATE" in snippet


def test_synthetic_same_endpoint_control_is_counted():
    cs = _cross_source(
        {"ai": 80, "n1i": 1000, "ci": 100, "n2i": 1000},
        "NCT1",
        {"NCT1": [_om(80, 1000, 100, 1000)]},
        {"name": "All-cause mortality", "keywords": ["all-cause mortality", "mortality"]},
        ["drug"],
        ["placebo"],
    )
    assert cs["endpoint_match"] == "IDENTICAL_ENDPOINT"
    assert cs["corroborates_endpoint"] is True
    assert cs["ctgov_rr"] == 0.8
