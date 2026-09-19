"""A held abstract that carries a recorded fetch must be the text extracted from that fetch's raw body.

PLANT (2026-09-19, external audit): SOUL's (40162642) held abstract in cache/glp1-ra-mace-t2d/records.json was a
condensed, hand-entered version of PubMed's -- randomisation clause joined to the result sentence, incidence qualifiers
and the follow-up sentence dropped -- and the span check proved spans against it. Corpus sweep against live PubMed:
2 of 100 pooled records condensed (SOUL; omarigliptin 28893244 in dpp4, whose early-termination sentences and hHF
endpoint were dropped). Both now carry `held_text` (source, url, retrieved_utc, raw_file, body_sha256, abstract_sha256)
and the raw efetch body is held in the cache. This test re-derives the abstract from the raw body and compares."""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _abstract_from_efetch(body: bytes) -> str:
    x = body.decode("utf-8", "replace")
    segs = []
    for attrs, txt in re.findall(r"<AbstractText([^>]*)>(.*?)</AbstractText>", x, re.S):
        lab = re.search(r'Label="([^"]+)"', attrs)
        t = html.unescape(re.sub(r"<[^>]+>", "", txt)).replace(" ", " ").replace(" ", " ")
        t = re.sub(r"\s+", " ", t).strip()
        segs.append((lab.group(1) + ": " if lab else "") + t)
    return " ".join(segs)


def _recorded():
    for rp in sorted((ROOT / "cache").glob("*/records.json")):
        for rec in json.loads(rp.read_text(encoding="utf-8")).get("records", []):
            if isinstance(rec.get("held_text"), dict):
                yield rp.parent.name, rec


def test_every_recorded_held_text_matches_its_raw_body():
    n = 0
    for slug, rec in _recorded():
        ht = rec["held_text"]
        raw = (ROOT / ht["raw_file"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == ht["body_sha256"], (slug, rec["id"], "raw body digest")
        assert _abstract_from_efetch(raw) == rec["abstract"], (slug, rec["id"], "abstract is not the text of the raw body")
        assert hashlib.sha256(rec["abstract"].encode("utf-8")).hexdigest() == ht["abstract_sha256"]
        ledger = json.loads((ROOT / "cache" / slug / "retrieval_ledger.json").read_text(encoding="utf-8"))
        assert ledger["records"][str(rec["id"])]["held_text"]["body_sha256"] == ht["body_sha256"]
        n += 1
    assert n >= 2, "SOUL and omarigliptin must carry recorded held text"


def test_soul_result_span_carries_the_incidence_qualifiers():
    review = json.loads((ROOT / "docs/reviews/glp1-ra-mace-t2d/review.json").read_text(encoding="utf-8"))
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    row = next(t for t in primary["trials"] if "40162642" in str(t.get("id")))
    span = row["endpoint_result_span"]
    assert "incidence, 3.1 events per 100 person-years" in span and "incidence, 3.7 events per 100 person-years" in span
    assert not span.startswith("Among the 9650 participants who had undergone randomization, a primary-outcome event")
    assert (row["effect"], row["ci_low"], row["ci_high"]) == (0.86, 0.77, 0.96)
