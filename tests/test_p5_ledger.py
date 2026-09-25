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


# ---- review 4 (2026-09-25): every recovery path re-finds its evidence; the population cannot shrink ---------------
def _build(tmp_path, searches=None, adj=None, ev_mutate=None):
    """Run build_ledger.py's full source with planted inputs; returns the ledger it would write (to tmp)."""
    src = open(os.path.join(PP, "scripts", "build_ledger.py"), encoding="utf-8").read()
    out = tmp_path / "ledger.json"
    src = src.replace('json.dump(out, open(P("evidence", "p5_populations", "ledger.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)',
                      'json.dump(out, open(__OUT__, "w", encoding="utf-8"), indent=1, ensure_ascii=False)')
    assert "__OUT__" in src
    g = {"__file__": os.path.join(PP, "scripts", "build_ledger.py"), "__name__": "bl", "__OUT__": str(out)}
    head, rest = src.split("check_population(EV)\n", 1)   # plants go in BEFORE the population check runs
    exec(compile(head, "build_ledger", "exec"), g)
    if searches is not None:
        g["SEARCHES"] = searches
    if adj is not None:
        g["ENTRY_ADJ"] = adj
    if ev_mutate:
        ev_mutate(g["EV"])
    exec(compile("check_population(EV)\n" + rest, "build_ledger", "exec"), g)
    return json.load(open(out, encoding="utf-8"))


def _state(led, key, fact):
    return next(f["state"] for r in led["rows"] if r["key"] == key for f in r["facts"] if f["fact_id"] == fact)


def _searches():
    return json.load(open(os.path.join(PP, "searches.json"), encoding="utf-8"))


def test_a_search_recovery_whose_span_is_not_in_its_bytes_is_refused(tmp_path):
    s = _searches()
    s["P53-19/registry_parent"] = {"result": "RECOVERED", "evidence": [
        {"ref": "evidence/p5_populations/POLICY.md", "sha256": "0" * 64, "span": "NCT99999999 fabricated registration of this trial"}]}
    assert _state(_build(tmp_path, searches=s), "P53-19", "registry_parent") != "RECOVERED"


def test_established_absent_needs_re_found_evidence(tmp_path):
    s = _searches()
    s["P53-19/registry_parent"] = {"result": "ESTABLISHED_ABSENT", "evidence": []}
    assert _state(_build(tmp_path, searches=s), "P53-19", "registry_parent") != "ESTABLISHED_ABSENT"


def test_a_does_not_state_adjudication_on_a_local_document_is_never_a_recovery(tmp_path):
    adj = json.load(open(os.path.join(PP, "entry_adjudications.json"), encoding="utf-8"))
    adj["P53-41"] = dict(adj["P53-41"], verdict="DOES_NOT_STATE")
    assert "RECOVERED" not in _state(_build(tmp_path, adj=adj), "P53-41", "entry_population")


def test_the_population_cannot_shrink_or_duplicate(tmp_path):
    import pytest
    with pytest.raises(AssertionError):
        _build(tmp_path, ev_mutate=lambda ev: ev["rows"].__setitem__(1, dict(ev["rows"][0])))
    with pytest.raises(AssertionError):
        _build(tmp_path, ev_mutate=lambda ev: ev["rows"][0].__setitem__("facts", []))


def test_a_citation_of_another_trials_document_is_not_the_trials_own():
    src = open(os.path.join(PP, "scripts", "build_ledger.py"), encoding="utf-8").read()
    g = {"__file__": os.path.join(PP, "scripts", "build_ledger.py"), "__name__": "bl"}
    exec(compile(src[:src.index("rows_out, tally, by_fact")], "build_ledger", "exec"), g)
    row = {"trial": "PMID 111", "family_id": "NCT00000001"}
    assert g["own_document"](row, {"record_id": "111", "document_ref": "x.json#/records/0/abstract", "span": "s"})
    assert not g["own_document"](row, {"record_id": "999", "document_ref": "x.txt", "span": "another trial's sentence"})
    assert g["own_document"](row, {"record_id": None, "document_ref": "reg.json", "span": "NCT00000001 masking QUADRUPLE"})


def test_reverify_requires_the_span_inside_its_pointed_value():
    src = open(os.path.join(PP, "scripts", "reverify_ev53.py"), encoding="utf-8").read()
    g = {"__file__": os.path.join(PP, "scripts", "reverify_ev53.py"), "__name__": "rv"}
    exec(compile(src[:src.index("out, tally = {}")], "reverify", "exec"), g)
    pv = g["pointed_value"]
    doc = json.dumps({"records": [{"abstract": "Trial A enrolled adults."}, {"abstract": "Trial B randomized children to drugx."}]})
    vals = pv(doc, "x/records.json#/records/0/abstract")
    assert not any("randomized children" in v for v in vals)          # the span sits in records[1]: NOT at the pointer
    assert pv(doc, "x/records.json#/records/9") is False             # a pointer that does not resolve
    assert "Trial A enrolled adults." in pv(doc, "x/records.json#/records/0/abstract")


def test_a_failed_fetch_is_never_a_zero(monkeypatch):
    import importlib.util, sys
    sys.path.insert(0, os.path.join(PP, "scripts"))
    spec = importlib.util.spec_from_file_location("search_step4", os.path.join(PP, "scripts", "search_step4.py"))
    s4 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s4)
    monkeypatch.setattr(s4, "get", lambda url, held, log, tag: b"")
    monkeypatch.setattr(s4.time, "sleep", lambda x: None)
    total, hits, ok = s4.epmc_all("q", ".", [], "t", 25)
    assert ok is False and hits == []
    assert s4.core("1", ".", []) is None
