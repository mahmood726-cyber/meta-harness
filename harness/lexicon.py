"""ONE shared vocabulary normalisation layer, consumed by all matchers (screening, extraction,
outcome-matching, comparator-matching, and — when it lands — query-building). Before this module the
same word was normalised differently (or not at all) in each consumer, so a fix in the extractor left
the same form broken in the screener. That is the class that dropped AFFIRM-AHF: the iv-iron outcome
keywords are American ("hospitalization") and require "worsening", so the trial's own effect sentence
— "217 total heart failure hospitalisations ... (RR 0.74; 95% CI 0.58-0.94)" (British spelling) — was
never matched and a present effect+CI was declared absent.

Design: the shared, LOW-RISK normalisation is a FOLD (spelling / mid-dot / case / whitespace). The
match STYLE stays with each consumer (screening wants whole-token matching so 'rat' does not match
'preparation'; extraction wants phrase-substring). Both call fold() on BOTH sides first.

Explicitly NOT here yet: abbreviation expansion (CV<->cardiovascular, MI<->myocardial infarction,
HF<->heart failure). Abbreviations carry the ELIXA over-broadening risk and land LAST, separately,
with their own corpus-wide before/after. fold() must never expand an abbreviation.
"""
import re

# --- British -> American spelling fold ---------------------------------------------------------
# CURATED stems, each a British form that cannot corrupt an already-American word (folding the
# American form is a no-op because its stem does not appear). British->American is a normalisation
# direction, not a claim that one spelling is correct. Guarded per the ha?emoglobin lesson: we map
# the whole British stem to the American stem rather than a blind [ae] class.
_SPELLING = [
    ("hospitalis", "hospitaliz"),   # hospitalisation(s) -> hospitalization(s)  [the AFFIRM-AHF miss]
    ("randomis", "randomiz"),       # randomised / randomisation
    ("normalis", "normaliz"),
    ("haemorrhag", "hemorrhag"),
    ("haemoglob", "hemoglob"),
    ("haematolog", "hematolog"),
    ("ischaemi", "ischemi"),        # ischaemic / ischaemia
    ("anaemi", "anemi"),
    ("oedema", "edema"),
    ("oesophag", "esophag"),
    ("oestrogen", "estrogen"),
    ("paediatric", "pediatric"),
    ("diarrhoea", "diarrhea"),
    ("caesarean", "cesarean"),
    ("foetal", "fetal"),
    ("favour", "favor"),
    ("behaviour", "behavior"),
    ("tumour", "tumor"),
    ("litre", "liter"),
    ("fibre", "fiber"),
    ("centre", "center"),
]

_MID_DOTS = ("·", "‧", "∙")


def fold(text: str) -> str:
    """Shared canonical fold for matching: normalise the mid-dot decimal separator, lowercase, apply
    the British->American spelling fold, and collapse internal whitespace. Idempotent. Never expands
    abbreviations and never removes hyphens (hyphen/space equivalence is decided at match time so it
    can be scoped away from the generic anchors that the ELIXA regression showed must stay exact)."""
    t = text or ""
    for d in _MID_DOTS:
        t = t.replace(d, ".")
    t = t.lower()
    for brit, amer in _SPELLING:
        if brit in t:
            t = t.replace(brit, amer)
    t = re.sub(r"\s+", " ", t)
    return t


# --- mortality <-> death synonym (moved here from extract; a single source for all consumers) -----
_MORT_Y = re.compile(r"\bmortalit(?:y|ies)\b", re.I)
_MORT_D = re.compile(r"\bdeaths?\b", re.I)


def mort_variants(kl: str) -> set:
    """Synonym-swapped variants of a PHRASE keyword naming death/mortality. 'in-hospital death' also
    matches 'in-hospital mortality'. Only the one word is swapped; the qualifier is kept, so a bare
    'died' is never broadened into matching any 'mortality' sentence."""
    out = set()
    if _MORT_Y.search(kl):
        out.add(_MORT_Y.sub("death", kl))
    if _MORT_D.search(kl):
        out.add(_MORT_D.sub("mortality", kl))
    return out
