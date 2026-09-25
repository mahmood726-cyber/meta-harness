"""Schema-v2 conformance of the committed OBSERVATIONS files (SCHEMA-count-observations-v2 + the schema owner's answers),
checked on every written row, not on a sample:
- two observations per row, intervention then comparator; required fields and types; aliases agree (arm_id, n);
- group_id carries group_id_scope; every total witness carries derivation, and it is null (the reported-only contract);
- every witness resolves in the repo to a document whose normalized text[start:end] is exactly the witnessed token;
- the four role-specific coordinates are distinct, except a closed-list distributive event witness (S3);
- percentage_corroboration and context_state have the declared shape."""
import importlib.util, json, os, re
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.join(HERE, "..", "evidence", "typed_arms")
spec = importlib.util.spec_from_file_location("write_v2", os.path.join(TA, "v2", "write_v2.py"))
wv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wv)
wv.ROOT = os.path.abspath(os.path.join(HERE, ".."))
_cs = importlib.util.spec_from_file_location("check_witness", os.path.join(TA, "witness", "check_witness.py"))
cw = importlib.util.module_from_spec(_cs)
_cs.loader.exec_module(cw)

OBS_KEYS = {"role", "group_id", "group_id_scope", "arm_name", "arm_id", "events", "total", "n", "event_witness",
            "total_witness", "outcome", "population", "window", "percentage_corroboration", "context_state"}
W_KEYS = {"role", "document_ref", "document_sha256", "text", "representation", "start", "end"}


def rows(pop):
    d = json.load(open(os.path.join(TA, "v2", f"OBSERVATIONS_{pop}.json"), encoding="utf-8"))
    assert d["written"] == len(d["rows"]) and d["written"] + len(d["not_written_rows"]) in (34, 35)
    return list(d["rows"].items())


ALL = [(p, k, r) for p in ("held", "served") for k, r in rows(p)]


@pytest.mark.parametrize("pop,key,row", ALL, ids=[f"{p}:{k}" for p, k, _ in ALL])
def test_every_written_row_conforms(pop, key, row):
    obs = row["observations"]
    assert [o["role"] for o in obs] == ["intervention", "comparator"]
    for o in obs:
        assert OBS_KEYS <= set(o), set(OBS_KEYS) - set(o)
        assert all(type(o[k]) is int for k in ("events", "total", "n")) and o["n"] == o["total"]
        assert 0 <= o["events"] <= o["total"] and o["total"] > 0
        assert o["arm_id"] == o["arm_name"].lower().strip()
        if o["group_id"] is not None:
            assert o["group_id_scope"], "group_id_scope is REQUIRED with group_id"
        assert o["total_witness"].get("derivation", "MISSING") is None, "reported-only: derivation present and null"
        assert set(o["context_state"]) == {"population", "window"}
        assert all(set(pc) == {"reported", "agrees"} and isinstance(pc["agrees"], bool) for pc in o["percentage_corroboration"])
        for fld, val in (("event_witness", o["events"]), ("total_witness", o["total"])):
            w = o[fld]
            assert W_KEYS <= set(w), set(W_KEYS) - set(w)
            assert w["role"] == f"{o['role']}.{'events' if fld == 'event_witness' else 'total'}"
            sha, text, _ = wv.held(w["document_ref"])
            assert sha == w["document_sha256"], (w["document_ref"], "held document changed")
            assert text[w["start"]:w["end"]] == w["text"]
            if not w.get("distributive"):
                assert cw.token_value(w["text"]) == val, (w["text"], val)   # the witnessed token IS the number
    keys = [(w["document_ref"], w["start"], w["end"]) for o in obs for w in (o["event_witness"], o["total_witness"])]
    if len(set(keys)) != 4:   # only S3: one closed-list distributive event token shared by both arms
        assert len(set(keys)) == 3 and keys[0] == keys[2]
        assert all(wv.licensed_distributive(o["event_witness"]) for o in obs)
