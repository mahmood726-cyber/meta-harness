"""A committed 'full text' that is front matter + abstract only must be labelled ABSTRACT_ONLY, and nothing may say it
scanned the full text of that article (melatonin: ft_12790159.txt, Almeida Montes -- 'The publisher of this article
does not allow downloading of the full text in XML form.'). 'No SD found' there never means the article lacks one."""
import json
import os

from harness import fetch, fulltext_coverage as fc, pipeline

ROOT = pipeline.ROOT
SLUG = "melatonin-primary-insomnia-sol"
FT = os.path.join(ROOT, "cache", SLUG, "ft_12790159.txt")


def test_the_publisher_disallowed_file_is_abstract_only():
    c = fc.classify(open(FT, encoding="utf-8").read())
    assert c["coverage"] == fc.ABSTRACT_ONLY and "does not allow" in c["basis"]


def test_a_real_full_text_and_plain_text_are_full_text():
    body = "<article><front><abstract><p>a</p></abstract></front><body><sec><title>Methods</title><p>x</p></sec></body></article>"
    assert fc.classify(body)["coverage"] == fc.FULL_TEXT
    assert fc.classify("Introduction Insomnia is ... Methods ... Results ... Table 2 ...")["coverage"] == fc.FULL_TEXT
    # PLANT: JATS with only an abstract (no <body>), no publisher comment -> still abstract only
    assert fc.classify("<article><front><abstract><p>a</p></abstract></front></article>")["coverage"] == fc.ABSTRACT_ONLY


def test_no_consumer_says_it_scanned_the_full_text_of_an_abstract_only_file():
    config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    rv = pipeline.build_review_core(SLUG, config, fetch.ensure(config, ""), "test")
    fund = next((f for f in rv.get("funding") or [] if "12790159" in f["id"]), None)
    if fund:
        assert fund["scanned"] != "full text" and "full text scanned" not in fund["type"]
    cov = rv["fulltext_coverage"]["12790159"]
    assert cov["coverage"] == fc.ABSTRACT_ONLY
    from harness.consumer_consistency import fulltexts_by_id
    assert "12790159" not in fulltexts_by_id(SLUG, fetch.ensure(config, ""))
