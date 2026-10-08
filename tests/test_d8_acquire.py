"""D8 OPEN_SOURCES_ONLY (registry/g1_decisions.json, 7 Oct) in the acquisition lane, both sides:

  PROMPT (a recorded prompt is a committed, public record): a held full text is shown only when scripts/g1_licence.py
         keeps it -- the ARTICLE's Europe PMC licence is CC BY / CC0 and the copy is open; an unknown licence is closed.
  READER ('no paywalled text is read, even by a regex reader'): the deterministic readers take only a legitimately open
         copy (a CC copy or a PMC author manuscript); a free copy with no licence (bronze) is never read.

The case: PARALLEL-HF (Tsutsui 2021) is open on J-STAGE under CC BY-NC-ND; Europe PMC records no licence for the article.
Its text may be read by the extractor proposer, but no prompt may carry it -- and a model answer that rests on it (a
reader-1 call made under the older any-CC prompt rule) is refused."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_licence as gl  # noqa: E402
import g1_trial_acquire as A  # noqa: E402

SACVAL = json.load(open(os.path.join(ROOT, "topics", "sacubitril-valsartan-hfref.json"), encoding="utf-8"))
SENT = ("Over a median follow up of 33.9 months, no significant between-group difference was observed for the primary "
        "composite outcome of CV death and HF hospitalization (HR 1.09; 95% CI 0.65-1.82; P=0.6260). ")


def _held(doi_licence="cc-by-nc-nd", d8_prompt=False):
    return {"text": SENT * 2, "terms": A.outcome_terms(SACVAL), "comp": "36722326", "pmid": "33731544",
            "slug": "sacubitril-valsartan-hfref", "sha": "s", "text_origin": "UNPAYWALL", "doi": "10.1253/x",
            "doi_licence": doi_licence, "text_url": None, "reg": {}, "euctr": {}, "aact": {}, "d8_prompt": d8_prompt}


def test_the_prompt_takes_only_a_cc_by_or_cc0_article_and_unknown_is_closed(monkeypatch):
    monkeypatch.setattr(gl, "licence", lambda pmid, offline=False: {"license": None, "open": False})
    monkeypatch.setattr(gl, "repo_open", lambda pmid, kind, offline=False: True)
    assert not A.d8_promptable("33731544", "UNPAYWALL", "cc-by-nc-nd")
    assert not A.d8_promptable("33731544", "PMC")
    monkeypatch.setattr(gl, "licence", lambda pmid, offline=False: {"license": "cc by", "open": True})
    assert A.d8_promptable("1", "PMC")
    assert not A.d8_promptable("1", "OPEN_LOCATION", "cc-by-nc-nd")   # the copy's own host licence counts too
    assert A.d8_promptable("1", "OPEN_LOCATION", "cc-by")

    def boom(pmid, offline=False):
        raise RuntimeError("Europe PMC unreachable")
    monkeypatch.setattr(gl, "licence", boom)
    assert not A.d8_promptable("1", "PMC")                            # cannot be read -> closed


def test_an_open_non_cc_by_copy_is_read_deterministically_but_a_licence_less_copy_is_not():
    v, adm = A.typed_first({"slug": "sacubitril-valsartan-hfref", "pmid": "33731544"}, SACVAL, _held())
    assert v == "ADMITTED" and adm["kind"] == "TEXT_EXTRACTOR"
    # a free copy with no licence at all (bronze) is never read, by any reader
    assert A.typed_first({"slug": "sacubitril-valsartan-hfref", "pmid": "33731544"}, SACVAL,
                         _held(doi_licence=None)) == (None, None)


def test_a_model_answer_resting_on_a_text_no_prompt_may_carry_is_refused():
    resp = {"verdict": "FOUND", "source": "PMC_TEXT", "source_ref": "33731544", "quote": SENT.strip(), "measure": "HR",
            "events_t": None, "n_t": None, "events_c": None, "n_c": None, "effect": "1.09", "lower": "0.65",
            "upper": "1.82"}
    assert A.gate(resp, _held(), SACVAL, "sacubitril-valsartan-hfref")[0] == "REFUSED:TEXT_NOT_PROMPTABLE_UNDER_D8"
    assert A.gate(resp, _held(doi_licence="cc-by", d8_prompt=True), SACVAL, "sacubitril-valsartan-hfref")[0] == \
        "ADMITTED"
