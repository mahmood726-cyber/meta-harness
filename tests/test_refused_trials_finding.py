"""scripts/audit_refused_trials_in_secondary_pools.py lists, never refuses: a refused trial pooled in a secondary/harm
outcome is a FINDING owed adjudication (the registry reasons are written about the primary)."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("audit_rt", ROOT / "scripts" / "audit_refused_trials_in_secondary_pools.py")
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


def _site(tmp_path, harm_trials):
    (tmp_path / "docs" / "reviews" / "t").mkdir(parents=True)
    review = {"slug": "t", "outcomes": [
        {"name": "P", "primary": True, "trials": [{"id": "PMID 22222222"}]},
        {"name": "Harm", "kind": "harm", "trials": [{"id": f"PMID {p}"} for p in harm_trials]}]}
    (tmp_path / "docs" / "reviews" / "t" / "review.json").write_text(json.dumps(review), encoding="utf-8")
    (tmp_path / "docs" / "refusals.json").write_text(json.dumps(
        {"t": [{"trial": "X (PMID 99999999)", "not_pooled_because": "scope"}]}), encoding="utf-8")
    return str(tmp_path)


def test_PLANT_a_refused_trial_in_a_harm_pool_is_listed(tmp_path):
    found, total = audit.findings(_site(tmp_path, ["99999999", "33333333"]))
    assert total == 2 and [(f["trial"], f["adjudication"]) for f in found] == [("99999999", "OWED")]


def test_a_harm_pool_without_refused_trials_lists_nothing(tmp_path):
    assert audit.findings(_site(tmp_path, ["33333333"])) == ([], 1)


def test_the_committed_corpus_finding_is_current():
    committed = json.loads((ROOT / "outputs" / "findings" / "refused_trials_in_secondary_pools_2026-10-02.json")
                           .read_text(encoding="utf-8"))
    found, total = audit.findings()
    assert committed == {"findings": found, "n": len(found), "N": total}
