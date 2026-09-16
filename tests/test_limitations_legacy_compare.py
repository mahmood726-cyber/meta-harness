import json
from collections import Counter
from pathlib import Path

from harness.honest_ratchet import blocks
from harness import claimgraph
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


def _page_limitation_block_texts(review):
    return Counter(
        block["text"]
        for block in blocks(render_page(review))
        if not block["text"].startswith("UNRENDERABLE claimgraph object")
    )


def test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews():
    rows = []
    for review_dir in _review_dirs():
        review = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
        assert "limitations" in review, review["slug"]
        page_texts = _page_limitation_block_texts(review)
        object_texts = _limitation_block_texts(review)
        rows.append((review["slug"], sum(page_texts.values()), sum(object_texts.values())))
        if object_texts == page_texts:
            continue
        stale_codes = {v["code"] for v in claimgraph.check(review)}
        extra_objects = object_texts - page_texts
        extra_pages = page_texts - object_texts
        assert not review.get("claimgraph"), review["slug"]
        all_extra = list(extra_objects.elements()) + list(extra_pages.elements())
        assert all("Does the result survive dropping" in text for text in all_extra), review["slug"]
        if any("see coverage" in text for text in extra_objects):
            assert "PROSE_PREDICATE_FALSE" in stale_codes, review["slug"]
        else:
            sens = review.get("rob_sensitivity") or {}
            assert sens.get("low_only_informative") is True, review["slug"]

    assert len(rows) == 32
    assert all(
        page_count == object_count
        or "PROSE_PREDICATE_FALSE" in {v["code"] for v in claimgraph.check(
            json.loads((REVIEWS / slug / "review.json").read_text(encoding="utf-8"))
        )}
        for slug, page_count, object_count in rows
    )
