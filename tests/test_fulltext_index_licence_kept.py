"""Plant (5 Oct, forest lane): caching a PMC full text must not drop the copy's recorded licence (copy_licence /
copy_statement / copy_pmcid, written by harness.copy_licence) -- k_gap_counterfactual.pmc_fulltext_cached replaced the
whole index entry, so EFFECT-HF's CC mark vanished and the licence guard refused its (CC) record."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_counterfactual as cfm  # noqa: E402


def test_caching_a_text_keeps_the_copy_licence_and_other_entries(tmp_path, monkeypatch):
    out = tmp_path / "k_gap"
    out.mkdir()
    (out / "fulltext_index.json").write_text(json.dumps({"111": {"copy_licence": "CC", "copy_statement": "cc-by",
                                                                  "copy_pmcid": "PMC9"}}), encoding="utf-8")
    monkeypatch.setattr(cfm, "OUT", str(out))
    monkeypatch.setattr(cfm, "FT_DIR", str(out / "_ft"))
    from harness import fetch, http
    monkeypatch.setattr(http, "get_json", lambda *a, **k: {"records": [{"pmcid": "PMC9"}]})
    monkeypatch.setattr(fetch, "_pmc_fulltext", lambda pmid, with_supplements=True: "BODY " * 50)
    monkeypatch.setattr(cfm.time if hasattr(cfm, "time") else __import__("time"), "sleep", lambda s: None)

    def other_writer_meanwhile(pmid, with_supplements=True):   # a concurrent writer adds another entry
        idx = json.loads((out / "fulltext_index.json").read_text(encoding="utf-8"))
        idx["222"] = {"state": "HELD"}
        (out / "fulltext_index.json").write_text(json.dumps(idx), encoding="utf-8")
        return "BODY " * 50
    monkeypatch.setattr(fetch, "_pmc_fulltext", other_writer_meanwhile)
    assert cfm.pmc_fulltext_cached("111", offline=False)
    idx = json.loads((out / "fulltext_index.json").read_text(encoding="utf-8"))
    assert idx["111"]["state"] == "HELD" and idx["111"]["copy_licence"] == "CC" and idx["111"]["copy_pmcid"] == "PMC9"
    assert "222" in idx                                              # the other writer's entry survives
