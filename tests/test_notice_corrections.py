"""Correction plants: the original signed rendering is immutable."""
import copy
import json
from pathlib import Path

import pytest

from harness import page, result_changes as rc


def original():
    n = {"slug": "test", "outcome": "Outcome", "when_utc": "2026-09-20T23:30:00Z",
         "before": {"k": 2, "estimate": 1.1296}, "after": {"k": 2, "estimate": 1.0},
         "scale": "HR", "reason": "Historical reason", "by": "Reviewer"}
    block = page.result_change_block(n).split("<p class='muted'>Reviewer countersignature")[0]
    n["reviewer_countersignature"] = {"state": "SEEN_AND_SIGNED",
        "rendered_sha256": rc.rendered_sha256(block)}
    return n


def test_correction_preserves_signed_original_bytes_and_hash():
    n = original()
    saved = copy.deepcopy(n)
    html = page.result_change_block(n)
    c = rc.direction_correction(n, "Codex", "2026-10-17T00:00:00Z")
    assert n == saved
    assert page.result_change_block(n) == html
    assert c["corrects"]["rendered_sha256"] == n["reviewer_countersignature"]["rendered_sha256"]
    assert c["reviewer_countersignature"] == {"state": "OPEN"}
    assert "The direction of the estimate is changed." in page.correction_block(c, n)
    assert page.result_change_block(n) == html


@pytest.mark.parametrize("field,value", [("reason", "tampered"), ("when_utc", "wrong date")])
def test_correction_plant_rejects_changed_original(field, value):
    n = original()
    c = rc.direction_correction(n, "Codex", "2026-10-17T00:00:00Z")
    n[field] = value
    with pytest.raises(ValueError):
        page.correction_block(c, n)


def test_correction_plant_rejects_wrong_reference_hash():
    n = original()
    c = rc.direction_correction(n, "Codex", "2026-10-17T00:00:00Z")
    c["corrects"]["rendered_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        page.correction_block(c, n)


def test_correction_append_preserves_original_json_bytes(tmp_path, monkeypatch):
    from scripts import correct_result_change as script
    n = original()
    raw = json.dumps({"notices": [n]}, indent=3).encode() + b"\n"
    path = tmp_path / "notices.json"
    path.write_bytes(raw)
    monkeypatch.setattr(script, "_annotated", lambda n: n)
    corrections = script.draft(path, "test", "Outcome", "Codex", "2026-10-17T00:00:00Z")
    assert len(corrections) == 1
    assert path.read_bytes().startswith(raw[:raw.rfind(b"}")].rstrip())
    assert json.loads(path.read_bytes())["notices"] == [n]
    saved = path.read_bytes()
    script.draft(path, "test", "Outcome", "Codex", "2026-10-18T00:00:00Z")
    assert path.read_bytes() == saved


def test_correction_drafts_adjacent_to_signed_originals_on_page():
    from harness import review_tabs
    from scripts.countersign_result_change import _annotated
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "docs/result_changes.json").read_bytes())
    corrections = data.get("corrections", [])
    assert len(corrections) == 2
    review = json.loads((root / "docs/reviews/dpp4-mace-t2d/review.json").read_bytes())
    tab = review_tabs.changes_tab(review)
    served = (root / "docs/reviews/dpp4-mace-t2d/index.html").read_text(encoding="utf-8")
    for c in corrections:
        ref = c["corrects"]
        n, = [n for n in data["notices"] if all(n[k] == ref[k] for k in ("slug", "outcome", "when_utc"))]
        original_html = page.result_change_block(_annotated(n))
        correction_html = page.correction_block(c, _annotated(n))
        assert original_html + correction_html in tab
        assert original_html + correction_html in served
        assert c["reviewer_countersignature"]["state"] == "OPEN"
