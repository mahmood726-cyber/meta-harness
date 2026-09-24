"""The bundle's analysis_window rule must read the follow-up sentences it missed.

Found by the reproducible-AI estimand pilot (registry/model_proposals/estimand.json): on 3 of the 9 fields the bundle
regex left REGISTERED_DEFAULT, the model quoted a sentence stating follow-up that the rule did not match -- Lancet
middle-dot decimals (5·4) and the phrasings "followed for a median of" / "evaluated for a median duration of".
The sentences are read from the committed held abstracts (never retyped here), and the SAME table is checked in every
copy that runs it: the builder, the verifier, and the verifier's served mirror.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COPIES = ("scripts/build_bundle.py", "scripts/verify_bundle.py", "docs/scripts/verify_bundle.py")
PMIDS = ("28910237", "30291013", "31189511")


def _mod(rel):
    spec = importlib.util.spec_from_file_location("_fx_" + rel.replace("/", "_").replace(".", "_"), ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _window_values(mod, text):
    import re
    return sorted({v for rx, v in mod._ESTIMAND["analysis_window"] if re.search(rx, text, re.I)})


def _held_sentences():
    """The model's quotes, each checked to be verbatim in the committed abstract it came from."""
    q = json.loads((ROOT / "registry" / "model_proposals" / "estimand.json").read_text(encoding="utf-8"))
    recs = {str(r["id"]): r for r in json.loads((ROOT / "cache" / "glp1-ra-mace-t2d" / "records.json").read_text(encoding="utf-8"))["records"]}
    out = {}
    for e in q["items"]:
        pmid = e["item_id"].split("PMID ")[-1].split("::")[0]
        quote = (e.get("claim") or {}).get("quote")
        if pmid in PMIDS and quote:
            assert quote in recs[pmid]["abstract"], pmid
            out[pmid] = quote
    assert sorted(out) == sorted(PMIDS)
    return out


@pytest.mark.parametrize("rel", COPIES)
def test_follow_up_sentences_the_rule_missed_are_read(rel):
    mod = _mod(rel)
    for pmid, sentence in _held_sentences().items():
        assert "follow-up stated" in _window_values(mod, sentence), (rel, pmid, sentence)


@pytest.mark.parametrize("rel", COPIES)
def test_the_widened_rule_does_not_read_non_follow_up_sentences(rel):
    mod = _mod(rel)
    for s in ("The median age was 65·2 years.", "Patients were followed for adverse events.",
              "A median of 3 visits occurred.", "HbA1c fell by a median of 0·5%."):
        assert "follow-up stated" not in _window_values(mod, s), (rel, s)


def test_the_three_copies_still_agree():
    tables = [_mod(rel)._ESTIMAND for rel in COPIES]
    assert tables[0] == tables[1] == tables[2]
