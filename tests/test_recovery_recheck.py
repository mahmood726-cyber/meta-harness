"""Recovery-induced-incompatibility recheck (item 3) + the removed stale estimand sentence (item 1).

item 1: the old "reported labels differ (OR, RR) ... SAME compatibility class ... pooled as
compatible, not an estimand conflict" REASSURANCE contradicted the shipped compat key and is gone.
item 3: after a recovery integrates, the compatibility contract is re-run on the whole pool; a pool
mixing effect-measure labels at small k (spironolactone: RALES RR + EMPHASIS HR + reconstructed
J-EMPHASIS RR, k=3) is DISCLOSED as an approximation, never reassured away, and a recovery that
would pool a different effect-measure CLASS (RATE into FIRST_EVENT) is a hard incompatibility.
"""
import harness.recovery_recheck as RR
import harness.compat as compat


def _outcome(trials, scale, k, labels, classes, canonicals=None):
    return {
        "name": "X",
        "result": {"k": k, "scale": scale,
                   "estmeasure": {"status": "incompatible" if len(classes) > 1 else "compatible_labels",
                                  "classes": classes, "labels": labels,
                                  "canonicals": canonicals or []}},
        "trials": trials,
    }


def test_label_mix_small_k_is_disclosed_not_reassured():
    o = _outcome(
        trials=[{"label": "RALES", "derivation": "reported"},
                {"label": "EMPHASIS", "derivation": "reported"},
                {"label": "J-EMPHASIS", "derivation": "reconstructed"}],
        scale="RR/HR", k=3, labels=["RR", "HR"], classes=["FIRST_EVENT_RATIO"])
    v = RR.recheck_outcome(o, {"outcomes": [o]})
    assert v["label_mix_small_k"] and not v["hard_incompatible"], v
    assert "J-EMPHASIS" in v["reconstructed_members"]
    d = RR.disclosure(v)
    assert d and "approximation" in d.lower()
    # it must NOT reassure -- the banned stance from the deleted sentence
    assert "not an estimand conflict" not in d
    assert "pooled as compatible" not in d


def test_hard_incompatible_class_mix_is_caught_PLANT():
    # PLANT: a recovery pools a RATE trial (IRR) into a FIRST_EVENT pool (RR) -> hard incompatible.
    o = _outcome(
        trials=[{"label": "A", "derivation": "reported"}, {"label": "B", "derivation": "reported"}],
        scale="mixed", k=2, labels=["RR", "IRR"],
        classes=["FIRST_EVENT_RATIO", "RATE"], canonicals=["RISK_RATIO", "RATE_RATIO"])
    v = RR.recheck_outcome(o, {"outcomes": [o]})
    assert v["hard_incompatible"], v
    # the incompatibility banner owns the disclosure; the soft note stays silent
    assert RR.disclosure(v) is None


def test_large_k_label_mix_does_not_fire():
    # k > small-k threshold: a label mix in a well-powered pool is not flagged (avoid ELIXA-style
    # over-firing). One influential trial cannot dominate a large pool.
    o = _outcome(
        trials=[{"label": str(i), "derivation": "reported"} for i in range(7)],
        scale="RR/HR", k=7, labels=["RR", "HR"], classes=["FIRST_EVENT_RATIO"])
    v = RR.recheck_outcome(o, {"outcomes": [o]})
    assert not v["label_mix_small_k"] and not v["hard_incompatible"], v
    assert RR.disclosure(v) is None


def test_homogeneous_pool_is_silent():
    o = _outcome(
        trials=[{"label": "A", "derivation": "reported"}, {"label": "B", "derivation": "reported"}],
        scale="RR", k=2, labels=["RR"], classes=["FIRST_EVENT_RATIO"])
    v = RR.recheck_outcome(o, {"outcomes": [o]})
    assert not v["label_mix_small_k"] and not v["hard_incompatible"]
    assert RR.disclosure(v) is None


def test_suppressed_pool_returns_none():
    o = {"name": "X", "result": {"k": 2, "suppressed_incompatible": True}, "trials": []}
    assert RR.recheck_outcome(o, {"outcomes": [o]}) is None
