"""A6 (lc lane, 11 Oct): the index's Cochrane head-to-head sentence printed 'our single-trial OR 8.25 (k=1)' -- first
as code literals, then from docs/cochrane_headtohead.json, whose 'ours' was frozen when the topic held one trial. The
served metformin pool is k=3. Our side is read from the SERVED review; when the head-to-head was built on another pool
the sentence says so and prints both, never the stale one as 'ours'."""
import json
import os
import shutil

from harness import index

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H2H = {"cochrane_review": "CD013505 Metformin", "cochrane_pooled": {"measure": "OR", "effect": 2.64, "k": 13},
       "ours": {"k": 1, "estimate": 8.25, "scale": "OR"}}


def _docs(tmp_path, k, est):
    d = tmp_path / "docs"
    (d / "reviews" / "metformin-pcos-ovulation").mkdir(parents=True)
    (d / "cochrane_headtohead.json").write_text(json.dumps(H2H), encoding="utf-8")
    review = {"outcomes": [{"primary": True, "result": {"k": k, "estimate": est, "scale": "OR"}}]}
    (d / "reviews" / "metformin-pcos-ovulation" / "review.json").write_text(json.dumps(review), encoding="utf-8")
    return str(d)


def test_PLANT_a_moved_served_pool_is_printed_as_ours_and_the_headtohead_is_dated(tmp_path):
    s = index._cochrane_headtohead_line(_docs(tmp_path, 3, 2.0733))
    assert "OR 2.07 (k=3)" in s and "single-trial OR 8.25" not in s
    assert "OR 8.25 (k=1)" in s and "built when" in s


def test_an_unmoved_pool_keeps_the_original_sentence(tmp_path):
    s = index._cochrane_headtohead_line(_docs(tmp_path, 1, 8.2491))
    assert "our single-trial OR 8.25 (k=1)" in s and "built when" not in s


def test_no_served_review_no_comparison(tmp_path):
    d = _docs(tmp_path, 3, 2.07)
    shutil.rmtree(os.path.join(d, "reviews"))
    assert index._cochrane_headtohead_line(d) == ""
