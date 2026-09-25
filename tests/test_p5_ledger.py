"""P5 population ledger (evidence/p5_populations): an entry fact is never RECOVERED on another lane's ruling alone.
The blind second reading found a cited span that exists in the bytes but does not state the fact (P53-41); the gate
now requires evid2's own adjudicated span, re-found in sha-pinned bytes. Plants must be refused."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PP = os.path.join(HERE, "..", "evidence", "p5_populations")


def _gate():
    src = open(os.path.join(PP, "scripts", "build_ledger.py"), encoding="utf-8").read()
    g = {"__file__": os.path.join(PP, "scripts", "build_ledger.py"), "__name__": "build_ledger_top"}
    exec(compile(src[:src.index("rows_out, tally, by_fact")], "build_ledger", "exec"), g)
    return g["refind_adjudicated"]


def test_every_entry_fact_recovered_via_evid_carries_evid2s_own_adjudicated_span():
    led = json.load(open(os.path.join(PP, "ledger.json"), encoding="utf-8"))
    adj = json.load(open(os.path.join(PP, "entry_adjudications.json"), encoding="utf-8"))
    n = 0
    for r in led["rows"]:
        for f in r["facts"]:
            if f["fact_id"] == "entry_population" and "evid's span" in (f.get("basis") or "") and f["state"] == "RECOVERED":
                n += 1
                mine = [e for e in f["evidence"] if e.get("from") == "evid2 entry adjudication"]
                assert mine and mine[0]["span"] == adj[r["key"]]["span"], r["key"]
    assert n == len(adj) == 10


def test_a_planted_span_that_is_not_in_the_bytes_is_refused():
    refind = _gate()
    adj = json.load(open(os.path.join(PP, "entry_adjudications.json"), encoding="utf-8"))
    real = next(a for a in adj.values() if not a["ref"].startswith("LOCAL_ONLY:"))
    if not os.path.exists(os.path.join(HERE, "..", real["ref"].split("#")[0])):
        import pytest
        pytest.skip("cited cache file not held in this checkout")
    assert refind(real)
    assert refind(dict(real, span=real["span"] + " and every participant was taking antibiotics.")) is None
    assert refind(dict(real, sha256="0" * 64)) is None
