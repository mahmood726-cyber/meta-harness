"""Embedding candidate-generation layer, offline replay test: uses the COMMITTED cache
(cache/embeddings.json), no model load. Asserts outcome-identity synonymy cases score well above the
appendicitis mismatch — the candidate net widens for true synonyms and does NOT admit the negative."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import embed  # noqa: E402

SYN = [  # outcome-identity synonyms literal matching misses
    ("cardiovascular death", "death from cardiovascular causes"),
    ("cardiovascular death or hospitalization for heart failure", "CV Death or HHF"),
    ("rate ratio", "age-adjusted rate ratio"),
    ("stroke or systemic embolism", "stroke or systemic embolic event"),
]
NEG = ("treatment failure or complication at 1 year", "Resolution of Appendicitis Symptoms at 30 Days")
THR = 0.40


def _cos(q, c):
    r = embed.rank(q, [c], allow_model=False)  # cache-only: proves replay without the model
    return r[0][1] if r else None


def test_synonym_cases_recovered_from_committed_cache():
    for q, c in SYN:
        cos = _cos(q, c)
        assert cos is not None, f"embedding not cached for {q!r}/{c!r} (commit cache/embeddings.json)"
        assert cos >= THR, f"synonym {q!r}~{c!r} cos {cos:.3f} < {THR}"


def test_appendicitis_negative_rejected():
    cos = _cos(*NEG)
    assert cos is not None
    assert cos < THR, f"negative {NEG} cos {cos:.3f} should be < {THR}"


def test_separation():
    pos = [_cos(q, c) for q, c in SYN]
    neg = _cos(*NEG)
    assert min(pos) > neg, f"min positive {min(pos):.3f} must exceed negative {neg:.3f}"
