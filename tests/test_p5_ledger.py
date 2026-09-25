"""P5 population ledger (evidence/p5_populations): an entry fact is never RECOVERED on the EVID LANE'S ruling alone.
The blind second reading found a cited span that exists in the bytes but does not state the fact (P53-41); that branch
now requires evid2's own adjudicated span, re-found in sha-pinned bytes. Plants must be refused.
Scope, stated so the title does not claim more than it tests: the 24 entry facts RECOVERED through EV53's own
ESTABLISHES ruling are NOT adjudicated here; their semantic check is the blind second reading, which agreed on all 24
(second_reader/SECOND_READING.json)."""
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


def test_an_empty_or_short_span_and_an_absent_local_copy_are_never_re_found(monkeypatch):
    refind = _gate()
    adj = json.load(open(os.path.join(PP, "entry_adjudications.json"), encoding="utf-8"))
    real = next(a for a in adj.values() if not a["ref"].startswith("LOCAL_ONLY:"))
    for span in ("", "the", "were randomly assigned"):
        assert refind(dict(real, span=span)) is None
    local = next(a for a in adj.values() if a["ref"].startswith("LOCAL_ONLY:"))
    src = open(os.path.join(PP, "scripts", "build_ledger.py"), encoding="utf-8").read()
    env = {"__file__": os.path.join(PP, "scripts", "build_ledger.py"), "__name__": "bl"}
    monkeypatch.setenv("EVID2_HELD", os.path.join(HERE, "no-such-dir"))
    exec(compile(src[:src.index("rows_out, tally, by_fact")], "build_ledger", "exec"), env)
    assert env["refind_adjudicated"](local) is None
