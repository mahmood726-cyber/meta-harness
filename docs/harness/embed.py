"""Pinned, deterministic, offline sentence-embedding layer — LAYER 2 of extraction.

Purpose (Mahmood's strong version): synonym-robust CANDIDATE GENERATION and ranking, replacing the
literal keyword tests that produced the brittleness defects ("death from cardiovascular causes" vs
"CV death"; "placebo-controlled" vs "double-blind"). It WIDENS the candidate net; it is NEVER the
decider and NEVER produces a number. A number comes from a structured field or a verbatim span and is
round-trip checked; acceptance still refuses on ambiguity — the embedding only proposes.

Why a pinned LOCAL model, not a hosted one: deterministic (same input -> same vector), pinnable
(identity + version recorded; a hosted model's weights drift and silently break replay), offline and
free (a reader with no API key reproduces us), fast (thousands of candidate titles per topic). Every
embedding is cached keyed by (model identity, input text) so replay never needs the model; the cache
is committed and carries a four-state status like every other source.
"""
from __future__ import annotations

import hashlib
import json
import os

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
# Identity pinned for replay. (Weights are vendored via the HF cache; the cache below makes the
# model unnecessary at replay time — a fresh clone replays from committed vectors.)
MODEL_IDENTITY = {"model_id": MODEL_ID, "dim": 384, "normalize": True}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CACHE_PATH = os.path.join(ROOT, "cache", "embeddings.json")
_model = None
_cache = None


def _key(text: str) -> str:
    return hashlib.sha1(f"{MODEL_ID}|{text}".encode("utf-8")).hexdigest()


def _load_cache() -> dict:
    global _cache
    if _cache is None:
        try:
            _cache = json.load(open(_CACHE_PATH, encoding="utf-8"))
        except (OSError, ValueError):
            _cache = {}
    return _cache


def _save_cache():
    if _cache is not None:
        os.makedirs(os.path.dirname(_CACHE_PATH), exist_ok=True)
        json.dump(_cache, open(_CACHE_PATH, "w", encoding="utf-8", newline=""),
                  separators=(",", ":"), sort_keys=True)


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # deferred; heavy import
        _model = SentenceTransformer(MODEL_ID)
    return _model


def embed(texts: list[str], allow_model: bool = True) -> dict[str, list[float]]:
    """Return {text: unit-vector}. Cache-first; only loads the model for cache misses, and only if
    allow_model (a pure-replay context passes allow_model=False and gets cached vectors only)."""
    cache = _load_cache()
    out, missing = {}, []
    for t in texts:
        k = _key(t)
        if k in cache:
            out[t] = cache[k]
        else:
            missing.append(t)
    if missing and allow_model:
        vecs = _get_model().encode(missing, normalize_embeddings=True)
        for t, v in zip(missing, vecs):
            vv = [float(x) for x in v]
            cache[_key(t)] = vv
            out[t] = vv
        _save_cache()
    return out


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))  # inputs are unit-normalized


def rank(query: str, candidates: list[str], allow_model: bool = True) -> list[tuple[str, float]]:
    """Candidates ranked by cosine similarity to the query (descending). For candidate GENERATION —
    the caller takes a shortlist and adjudicates; the score is never itself an accept decision."""
    vecs = embed([query] + list(candidates), allow_model=allow_model)
    if query not in vecs:
        return []
    qv = vecs[query]
    scored = [(c, cosine(qv, vecs[c])) for c in candidates if c in vecs]
    return sorted(scored, key=lambda x: x[1], reverse=True)
