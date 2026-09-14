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

# Greek letters -> spelled words (unambiguous, general): a paper writes 'ω-3', 'β-blocker',
# 'α-blocker', the registered keyword writes 'omega-3', 'beta-blocker'. Folding the letter to its
# word lets them match. Only the letters that actually occur in this clinical corpus.
_GREEK = [("ω", "omega"), ("Ω", "omega"),   # ω Ω
          ("α", "alpha"), ("Α", "alpha"),   # α Α
          ("β", "beta"), ("Β", "beta"),     # β Β
          ("γ", "gamma"), ("Γ", "gamma"),   # γ Γ
          ("κ", "kappa"), ("Κ", "kappa"),    # κ Κ
          ("μ", "micro")]                          # µ (micro-)


def fold(text: str) -> str:
    """Shared canonical fold for matching: normalise the mid-dot decimal separator, lowercase, apply
    the British->American spelling fold, and collapse internal whitespace. Idempotent. Never expands
    abbreviations and never removes hyphens (hyphen/space equivalence is decided at match time so it
    can be scoped away from the generic anchors that the ELIXA regression showed must stay exact)."""
    t = text or ""
    for d in _MID_DOTS:
        t = t.replace(d, ".")
    for gl, word in _GREEK:
        if gl in t:
            t = t.replace(gl, word)
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


# --- nesting guard at MATCH TIME --------------------------------------------------------------
# A broad head term denotes a DIFFERENT (narrower) outcome when it appears only as a qualified
# subtype: 'mortality' inside 'cardiovascular mortality', 'stroke' inside 'ischaemic stroke',
# 'death' inside 'death due to bleeding'. Binding a broad keyword to such a sentence is the
# right-number-wrong-endpoint defect. The subtype qualifier can sit BEFORE the head ('cardiovascular
# mortality') or introduce a cause AFTER it ('death due to/from bleeding'). Guard is checked at match
# time (as the HFmrEF case is), never encoded per topic.
_SUBTYPE_HEADS = {
    "mortality": {"pre": ["cardiovascular", "cardiac", "cancer", "vascular", "coronary", "non-cardiovascular",
                          "noncardiovascular", "sudden", "cerebrovascular", "respiratory", "infection-related",
                          "pump-failure", "arrhythmic"], "cause": True},
    "death": {"pre": ["cardiovascular", "cardiac", "cancer", "vascular", "coronary", "sudden",
                      "cerebrovascular", "arrhythmic"], "cause": True},
    "stroke": {"pre": ["ischaemic", "ischemic", "haemorrhagic", "hemorrhagic", "fatal", "non-fatal",
                       "nonfatal", "disabling", "embolic"], "cause": False},
}
_CAUSE_RE = re.compile(r"^\s*(?:due to|from|caused by|attributable to|related to|secondary to)\b")


def matches_only_as_subtype(keyword_folded: str, text_folded: str) -> bool:
    """True if `keyword_folded` is a BARE head term (mortality/death/stroke, no qualifier of its own)
    that appears in `text_folded` ONLY as a qualified subtype (every occurrence preceded by a subtype
    qualifier, or followed by a 'due to <cause>'), so a match would bind a narrower, different outcome.
    Returns False for a multi-word keyword (it already carries its own scope) and whenever the head
    appears unqualified at least once (then the broad outcome is genuinely present)."""
    head = keyword_folded.strip()
    spec = _SUBTYPE_HEADS.get(head)
    if not spec:
        return False  # not a guarded bare head (multi-word keywords carry their own scope)
    pres = spec["pre"]
    idxs = [m.start() for m in re.finditer(r"(?<![a-z])" + re.escape(head) + r"(?![a-z])", text_folded)]
    if not idxs:
        return False
    for i in idxs:
        pre = text_folded[max(0, i - 22):i].rstrip()
        pre_qualified = any(pre.endswith(q) for q in pres)
        after = text_folded[i + len(head):]
        cause_qualified = spec["cause"] and bool(_CAUSE_RE.match(after))
        if not (pre_qualified or cause_qualified):
            return False  # an UNqualified occurrence -> the broad outcome is really present
    return True  # every occurrence was a qualified subtype
