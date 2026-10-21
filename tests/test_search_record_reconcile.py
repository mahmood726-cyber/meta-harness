"""scripts/search_record_reconcile.py (opt-in; port M-D from e156-ecosystem-starter): a retrieval-ledger source must
reconcile listed == distinct == retained == fetched == hits - cap remainder. Plants: each mismatch is REFUSED with its
own code; a clean source, and a hard cap whose remainder is declared, reconcile; a source naming nothing never passes.
Also: nothing in harness/ imports it (opt-in means nothing that already runs can start behaving differently)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import search_record_reconcile as S  # noqa: E402

NONE_CAP = {"kind": "none", "n": None, "remainder": None}


def _source(ids, hits=None, fetched=None, retained=None, cap=None, state="RAN_OK", sid="pubmed_concept_query#1"):
    n = len(ids)
    return {"source_id": sid, "kind": "PUBMED_CONCEPT_QUERY", "query": "q", "run_utc": "2026-10-21", "state": state,
            "error": None, "discovery_capable": True, "record_ids": list(ids),
            "funnel": {"hits": n if hits is None else hits, "fetched": n if fetched is None else fetched,
                       "retained": n if retained is None else retained, "cap": cap or dict(NONE_CAP)}}


def _ledger(*sources):
    return {"version": 1, "slug": "plant", "snapshot": {"mode": "REFRESH"}, "sources": list(sources), "records": {}}


def test_version_constant():
    assert S.__version__ == "1.0.0"


def test_clean_source_reconciles():
    row = S.check_source(_source(["111", "222", "333"]))
    assert row["verdict"] == S.RECONCILES and row["codes"] == []


def test_planted_duplicate_ids_refused_though_every_count_agrees():
    row = S.check_source(_source(["111", "222", "222"]))  # retained == fetched == hits == 3 == len(list)
    assert row["verdict"] == S.REFUSED
    assert row["codes"] == ["DUPLICATE_IDS"]
    assert "'222'" in row["why"]


def test_planted_page_sum_ne_list_refused():
    row = S.check_source(_source(["111", "222", "333"], hits=4, fetched=4))  # 4 fetched, 3 kept, loss undeclared
    assert row["verdict"] == S.REFUSED
    assert row["codes"] == ["FETCHED_NE_LIST"]


def test_planted_total_ne_list_refused_and_names_the_shortfall():
    ids = [str(i) for i in range(203)]
    row = S.check_source(_source(ids, hits=430))  # the source harness's measured case: 203 against 430
    assert row["verdict"] == S.REFUSED
    assert row["codes"] == ["TOTAL_NE_FETCHED"]
    assert "+227 never returned WHILE THE SOURCE REPORTS RAN_OK" in row["why"]


def test_planted_list_ne_retained_refused():
    row = S.check_source(_source(["111", "222"], hits=3, fetched=3, retained=3))
    assert row["verdict"] == S.REFUSED
    assert "LIST_NE_RETAINED" in row["codes"]


def test_planted_retained_exceeding_fetched_refused():
    row = S.check_source(_source(["111", "222", "333"], hits=2, fetched=2))
    assert "FETCHED_LT_RETAINED" in row["codes"]


def test_declared_hard_cap_remainder_reconciles_and_undeclared_does_not():
    ok = S.check_source(_source(["1", "2"], hits=5, cap={"kind": "hard_hits_cap", "n": 2, "remainder": 3}))
    assert ok["verdict"] == S.RECONCILES
    bad = S.check_source(_source(["1", "2"], hits=5, cap={"kind": "hard_hits_cap", "n": 2, "remainder": 1}))
    assert bad["verdict"] == S.REFUSED and bad["codes"] == ["TOTAL_NE_FETCHED"]


def test_unrecorded_total_is_counted_separately_not_a_full_pass():
    src = _source(["111"])
    src["funnel"]["hits"] = None
    assert S.check_source(src)["verdict"] == S.RECONCILES_NO_TOTAL


def test_source_naming_nothing_is_never_a_pass():
    src = _source([], state="RAN_ERROR")
    src["funnel"]["hits"] = None
    assert S.check_source(src)["verdict"] == S.NOT_ASSESSABLE
    # but an empty list contradicted by its own funnel is refused, not merely unassessable
    assert S.check_source(_source([], hits=7, fetched=7, retained=0))["verdict"] == S.REFUSED


def test_cli_exit_codes_on_planted_ledgers(tmp_path, capsys):
    good = tmp_path / "good" / "retrieval_ledger.json"
    bad = tmp_path / "bad" / "snapshots" / "s1" / "retrieval_ledger.json"
    for p, ledger in ((good, _ledger(_source(["1", "2"]))),
                      (bad, _ledger(_source(["1", "2"]), _source(["3", "3"], sid="ctgov_nct_link#1")))):
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps(ledger), encoding="utf-8")
    assert S.main([str(good)]) == 0
    assert S.main([str(tmp_path)]) == 1  # directory walk finds the snapshot ledger too
    assert "ctgov_nct_link#1" in capsys.readouterr().out
    assert S.main(["--json", str(tmp_path)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["tally"][S.REFUSED] == 1 and payload["codes"]["DUPLICATE_IDS"] == 1
    assert S.main([str(tmp_path / "nothing-here")]) == 2


def test_selftest_passes():
    assert S.selftest(out=_Sink()) == 0


def test_opt_in_nothing_in_harness_or_verify_all_imports_it():
    for p in list((ROOT / "harness").rglob("*.py")) + [ROOT / "scripts" / "verify_all.py"]:
        assert "search_record_reconcile" not in p.read_text(encoding="utf-8", errors="replace"), p


def test_runs_on_a_real_committed_ledger():
    path = ROOT / "cache" / "colchicine-postop-af" / "snapshots" / "2026-09-15r3-search_v2" / "retrieval_ledger.json"
    rows = S.check_ledger(json.loads(path.read_text(encoding="utf-8")))
    assert rows and all(r["verdict"] in S.VERDICTS for r in rows)
    assert any(r["verdict"] == S.RECONCILES for r in rows)


class _Sink:
    def write(self, _):
        pass
