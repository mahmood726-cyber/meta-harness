"""Isolated lexical helper transcriptions, NOT the production screener.

Reference: meta-harness 0730234d0b4f, harness/screen.py lines 22-88 and
comparator branch at lines 550-557; harness/lexicon.py fold().
The caller uses short SOURCE-INFORMED PARAPHRASES, not full source records.
No registry lookup, integrity guard, overrides, endpoint extraction or publication
path is executed. These tests diagnose phrase recognition only.
"""
import re

_SPELLING = [
    ('hospitalis','hospitaliz'), ('randomis','randomiz'), ('normalis','normaliz'),
    ('haemorrhag','hemorrhag'), ('haemoglob','hemoglob'), ('haematolog','hematolog'),
    ('ischaemi','ischemi'), ('anaemi','anemi'), ('oedema','edema'),
    ('oesophag','esophag'), ('oestrogen','estrogen'), ('paediatric','pediatric'),
    ('diarrhoea','diarrhea'), ('caesarean','cesarean'), ('foetal','fetal'),
    ('favour','favor'), ('behaviour','behavior'), ('tumour','tumor'),
    ('litre','liter'), ('fibre','fiber'), ('centre','center'),
]
_MID_DOTS = ('·','‧','∙')
_GREEK = [('ω','omega'),('Ω','omega'),('α','alpha'),('Α','alpha'),
          ('β','beta'),('Β','beta'),('γ','gamma'),('Γ','gamma'),
          ('κ','kappa'),('Κ','kappa'),('μ','micro')]

def fold(text: str) -> str:
    t = text or ''
    for d in _MID_DOTS:
        t = t.replace(d, '.')
    for letter, word in _GREEK:
        t = t.replace(letter, word)
    t = t.lower()
    for brit, amer in _SPELLING:
        t = t.replace(brit, amer)
    return re.sub(r'\s+', ' ', t)

_BOUND_CACHE = {}
_PLURAL_CACHE = {}
_NEGATION = re.compile(
    r'(?:\bno\b|\bnot\b|\bwithout\b|\bfree of\b|\babsence of\b|\babsent\b|\bnever\b|'
    r'\block of\b|\black of\b|\bnegative for\b|\bnil\b)[\w\s,\'"()-]{0,18}$', re.I)

def _boundary_re(term):
    r = _BOUND_CACHE.get(term)
    if r is None:
        if term.endswith('*'):
            r = re.compile(r'(?<![a-z0-9])' + re.escape(term[:-1]))
        else:
            r = re.compile(r'(?<![a-z0-9])' + re.escape(term) + r'(?![a-z0-9])')
        _BOUND_CACHE[term] = r
    return r

def _negated_at(text_lower, start):
    return bool(_NEGATION.search(text_lower[max(0,start-26):start]))

def _plural_re(term):
    if term.endswith('*'):
        return _boundary_re(term)
    r = _PLURAL_CACHE.get(term)
    if r is None:
        r = _PLURAL_CACHE[term] = re.compile(
            r'(?<![a-z0-9])' + re.escape(term) + r'(?:e?s)?(?![a-z0-9])')
    return r

def has(text, terms, plural=False):
    t = fold(text)
    for term in terms or []:
        tl = fold(term or '').strip()
        if not tl:
            continue
        for m in (_plural_re(tl) if plural else _boundary_re(tl)).finditer(t):
            if not _negated_at(t, m.start()):
                return term
    return None
