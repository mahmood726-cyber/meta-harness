"""Shared vocabulary normalisation layer (lexicon.fold) — the ONE layer consumed by every matcher.

The class this closes: British-spelled source text silently failing to match an American keyword
(AFFIRM-AHF: 'total heart failure hospitalisations ... RR 0.74 (0.58-0.94)' never matched the
American 'hospitalization' keyword). Each rule carries a PLANT that fails pre-fold.
"""
import harness.lexicon as L
import harness.extract as E
import harness.screen as S


def test_fold_british_to_american_spelling():
    assert L.fold("hospitalisation") == "hospitalization"
    assert L.fold("hospitalisations") == "hospitalizations"
    assert L.fold("randomised") == "randomized"
    assert L.fold("ischaemic") == "ischemic"
    assert L.fold("oedema") == "edema"
    assert L.fold("haemorrhage") == "hemorrhage"
    assert L.fold("diarrhoea") == "diarrhea"


def test_fold_is_noop_on_american_words():
    # folding an already-American word must not corrupt it (no double-fold, no spurious change)
    for w in ("hospitalization", "randomized", "ischemic", "edema", "hemorrhage", "mortality"):
        assert L.fold(w) == w


def test_fold_idempotent():
    for w in ("Hospitalisation", "HAEMOGLOBIN", "Randomised Controlled Trial"):
        once = L.fold(w)
        assert L.fold(once) == once


def test_fold_normalises_mid_dot_and_case_and_space():
    assert L.fold("RR 0·74") == "rr 0.74"
    assert L.fold("heart   failure") == "heart failure"


def test_fold_greek_letters_to_words():
    assert L.fold("ω-3 fatty acids") == "omega-3 fatty acids"
    assert L.fold("β-blocker") == "beta-blocker"
    assert L.fold("α-blocker") == "alpha-blocker"
    assert L.fold("omega-3") == "omega-3"  # spelled form is a no-op


def test_PLANT_greek_omega_matches_spelled_keyword():
    # PLANT: pre-fold 'omega-3' is not a substring of a 'ω-3' sentence; the Greek fold makes it match.
    sent = "patients were given ω-3 fatty acids daily"
    assert "omega-3" not in sent.lower()
    assert E._kw_in_sentence("omega-3 fatty acids", sent)


# --- abbreviations: available for query-building, HELD OUT of the extraction matcher (ELIXA risk) ---

def test_abbrev_variants_curated_pairs():
    # expansion phrase -> whole-token abbreviation
    vs = dict(L.abbrev_variants(L.fold("myocardial infarction")))
    assert vs.get("mi") is True  # whole-token
    vs2 = dict(L.abbrev_variants(L.fold("mace")))  # abbreviation -> expansion (substring-safe)
    assert "major adverse cardiovascular events" in vs2 and vs2["major adverse cardiovascular events"] is False


def test_abbreviations_are_NOT_wired_into_extraction():
    # HELD: abbreviation expansion must NOT rebind a pooled number in the extractor. Its own
    # before/after moved colchicine-postop-af 0.67->0.77 (END-AF 27502857 mis-bound its 63-patient
    # TOTAL as an arm on an 'af' match). So a bare 'af' keyword must NOT match an 'AF' sentence here.
    # the full phrase keyword must NOT expand to its abbreviation in the extractor
    assert not E._kw_in_sentence("atrial fibrillation", "the primary end point of AF occurred in 63 patients")
    assert not E._kw_in_sentence("myocardial infarction", "the rate of MI was 5%")


def test_fold_does_not_expand_abbreviations():
    # abbreviation expansion is a SEPARATE, later change (ELIXA risk). fold must never do it.
    assert "cardiovascular" not in L.fold("cv death")
    assert "myocardial infarction" not in L.fold("mi")
    assert "heart failure" not in L.fold("hf hospitalisation").replace("hospitalization", "")


def test_PLANT_british_sentence_matches_american_keyword():
    # PLANT: pre-fold a plain lowercase substring test MISSES the British spelling; the shared fold
    # is what makes the match. (This is the AFFIRM-AHF class, on matching phrasing.)
    british = "the patient had a hospitalisation for heart failure during follow-up"
    american_kw = "hospitalization for heart failure"
    assert american_kw not in british.lower()          # pre-fold: miss
    assert E._kw_in_sentence(american_kw, british)      # with fold: match


def test_PLANT_screening_matches_british_exclusion_term():
    # PLANT: an exclusion term written American ('paediatric'->'pediatric') must catch a British record.
    assert S._has("a paediatric cohort was enrolled", ["pediatric"]) == "pediatric"
    # and the reverse spelling on the record side
    assert S._has("a pediatric cohort", ["paediatric"]) == "paediatric"


# --- nesting guard (match time): a bare head must not bind a qualified subtype ---

def test_nesting_guard_rejects_qualified_subtype():
    assert L.matches_only_as_subtype("mortality", L.fold("cardiovascular mortality was 4%"))
    assert L.matches_only_as_subtype("stroke", L.fold("ischaemic stroke occurred in 12"))
    assert L.matches_only_as_subtype("death", L.fold("death due to bleeding in 3 patients"))


def test_nesting_guard_allows_broad_outcome():
    assert not L.matches_only_as_subtype("mortality", L.fold("all-cause mortality was 10%"))
    assert not L.matches_only_as_subtype("mortality", L.fold("total mortality 10% vs 12%"))
    # both subtype AND broad present -> broad is really there, allow
    assert not L.matches_only_as_subtype("mortality", L.fold("all-cause mortality 10%; cardiovascular mortality 4%"))
    # a multi-word keyword carries its own scope -> never guarded
    assert not L.matches_only_as_subtype("cardiovascular mortality", L.fold("cardiovascular mortality 4%"))


def test_PLANT_kw_in_sentence_rejects_subtype_only():
    # PLANT: pre-guard a bare 'mortality' keyword substring-matched 'cardiovascular mortality' and bound
    # a CV-death number to an all-cause outcome. The match-time guard rejects it.
    cv_only = "cardiovascular mortality was 4% versus 5%"
    assert "mortality" in cv_only          # pre-guard: naive substring matches
    assert not E._kw_in_sentence("mortality", cv_only)   # guard: rejected
    # but a genuine all-cause sentence still matches the bare keyword
    assert E._kw_in_sentence("mortality", "all-cause mortality was 10% versus 12%")
