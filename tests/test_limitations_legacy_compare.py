import json
from collections import Counter
from pathlib import Path

from harness.honest_ratchet import blocks
from harness.limitations import render_limitation
from harness.page import render_page


ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "docs" / "reviews"


def _review_dirs():
    return sorted(path for path in REVIEWS.iterdir() if (path / "review.json").is_file())


def _limitation_block_texts(review):
    texts = []
    for obj in review.get("limitations") or []:
        found = blocks(render_limitation(obj))
        assert len(found) == 1, obj["limitation_id"]
        texts.append(found[0]["text"])
    return Counter(texts)


def test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews():
    rows = []
    for review_dir in _review_dirs():
        review = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
        assert "limitations" in review, review["slug"]
        page_texts = Counter(block["text"] for block in blocks(render_page(review)))
        object_texts = _limitation_block_texts(review)
        rows.append((review["slug"], sum(page_texts.values()), sum(object_texts.values())))
        assert object_texts == page_texts, review["slug"]

    assert len(rows) == 32
    assert all(page_count == object_count for _, page_count, object_count in rows)
