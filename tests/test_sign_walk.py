"""Real-ledger read-only walker contracts; no signature command is executed."""
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import countersign_result_change as cli, sign_walk as walk

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def loaded():
    return walk.load_walk()


def test_order_is_mandatory_then_contiguous_shared_groups_then_remainder(loaded):
    audit, _, _, _ = loaded
    ordered = walk.ordered_notices(audit)
    expected_mandatory = [row["audit_id"] for row in audit["notices"] if row["individual_review_required_by_lane"]]
    assert len(expected_mandatory) == 18  # Denominator: 41 audited OPEN notices at audit time.
    grouped = [member for group in audit["decision_groups"] for member in group["members"]]
    rest = [row["audit_id"] for row in audit["notices"] if row["audit_id"] not in expected_mandatory + grouped]
    assert [row["audit_id"] for row in ordered] == expected_mandatory + grouped + rest
    assert len(ordered) == len({row["audit_id"] for row in ordered}) == 41
    assert "D01" not in {row["audit_id"] for row in ordered}


def test_every_notice_presents_exact_live_selection_digest_and_audit_recommendation(loaded):
    audit, notices, chains, mapping = loaded
    ledger_before = cli.PATH.read_bytes()
    for position, row in enumerate(walk.ordered_notices(audit), 1):
        output = walk.present(*loaded, position)
        notice = notices[mapping[row["audit_id"]]]
        assert output.count("python scripts/countersign_result_change.py sign ") == 1
        assert f"--notice-index {mapping[row['audit_id']]}" in output
        assert f"--expect-digest {cli._block_and_sha(notice)[2]}" in output
        assert row["recommendation_reason"] in output
        assert "HARNESS-TEAM RECOMMENDATION: " + row["recommendation"] in output
        assert row["direction_explanation"] in output
        assert row["mechanism_detail"] in output
        assert f"Before (ledger): {walk._json(notice['before'])}" in output
        assert f"After (ledger): {walk._json(notice['after'])}" in output
        assert "D01 (J-EMPHASIS-HF): NOT SIGNABLE" in output
        assert "--batch" not in output and "sign all" not in output.lower()
        assert "--basis (Read-Host " in output
        assert output.endswith("Another notice requires another explicit invocation.")
    assert cli.PATH.read_bytes() == ledger_before


def test_all_duplicate_chains_name_actual_previous_signature(loaded):
    _, notices, chains, mapping = loaded
    positions = {row["audit_id"]: i for i, row in enumerate(walk.ordered_notices(loaded[0]), 1)}
    checked = 0
    for chain in chains:
        if len(chain["indices"]) == 1:
            continue
        previous, current = chain["indices"]
        audit_id = next(key for key, index in mapping.items() if index == current)
        output = walk.present(*loaded, positions[audit_id])
        signature = notices[previous]["reviewer_countersignature"]
        assert "notice 2 of 2 notices for this exact (slug, outcome)" in output
        assert f"signed {signature['when_utc']} by {signature['by']}" in output
        checked += 1
    assert checked == 6  # Denominator: all outcome groups with successive notices.


def test_group_argument_once_in_order_and_explicit_reread(loaded):
    positions = {row["audit_id"]: i for i, row in enumerate(walk.ordered_notices(loaded[0]), 1)}
    for group in loaded[0]["decision_groups"]:
        outputs = [walk.present(*loaded, positions[member]) for member in group["members"]]
        assert sum(group["shared_sentence"] in output for output in outputs) == 1
        assert group["shared_sentence"] in outputs[0]
        assert "--show-group-reason" in outputs[1]
        assert group["shared_sentence"] in walk.present(*loaded, positions[group["members"][1]], True)


@pytest.mark.parametrize("args", [[], ["--notice", "N20"], ["--position", "19"], ["--notice", "D01"]])
def test_process_presents_one_then_exits_without_writing(args):
    ledger = cli.PATH.read_bytes()
    proc = subprocess.run([sys.executable, "-B", "scripts/sign_walk.py", *args], cwd=ROOT,
                          capture_output=True, encoding="utf-8", check=False)
    assert proc.returncode == 0, proc.stderr
    if args == ["--notice", "D01"]:
        assert "NOT SIGNABLE" in proc.stdout
        assert "--expect-digest" not in proc.stdout
        assert "python scripts/countersign_result_change.py sign" not in proc.stdout
    else:
        assert proc.stdout.count("Walk position ") == 1
        assert proc.stdout.count("Rendered block sha256: ") == 1
        assert proc.stdout.count("STOP.") == 1
    assert cli.PATH.read_bytes() == ledger


@pytest.mark.parametrize("args", [["--notice", "missing"], ["--position", "0"], ["--position", "42"]])
def test_invalid_explicit_selection_offers_no_command(args, capsys):
    assert walk.main(args) == 1
    captured = capsys.readouterr()
    assert not captured.out
    assert "no signing command offered" in captured.err


def _mock_ledger_read(monkeypatch, notices):
    """Override only the read in memory; no clinical ledger copy is written."""
    original = Path.read_text

    def read(path, *args, **kwargs):
        return json.dumps({"notices": notices}) if path == cli.PATH else original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read)


def test_stale_audited_notice_refuses_before_command(loaded, monkeypatch, capsys):
    notices = copy.deepcopy(loaded[1])
    notices[loaded[3]["N04"]]["reason"] += " IN-MEMORY TEST MUTATION"
    _mock_ledger_read(monkeypatch, notices)
    assert walk.main(["--notice", "N04"]) == 1
    output = capsys.readouterr()
    assert not output.out and "notice changed since registry/notice_adjudication.json" in output.err


def test_broken_chain_refuses_before_command(loaded, monkeypatch, capsys):
    notices = copy.deepcopy(loaded[1])
    notices[loaded[3]["N20"]]["before"]["estimate"] += 0.1
    _mock_ledger_read(monkeypatch, notices)
    assert walk.main(["--notice", "N20"]) == 1
    output = capsys.readouterr()
    assert not output.out and "ledger chain integrity failed" in output.err


def test_new_open_notice_without_audit_is_not_silently_skipped(loaded, monkeypatch, capsys):
    notices = copy.deepcopy(loaded[1])
    synthetic = {key: value for key, value in notices[loaded[3]["N04"]].items()
                 if key != "reviewer_countersignature"}
    synthetic.update(slug="synthetic-unaudited", outcome="Synthetic unaudited outcome")
    notices.append(synthetic)
    _mock_ledger_read(monkeypatch, notices)
    assert walk.main([]) == 1
    output = capsys.readouterr()
    assert not output.out and "OPEN notice has no adjudication" in output.err


def test_changed_held_source_refuses_before_command(monkeypatch, capsys):
    original = Path.read_bytes
    target = ROOT / "docs/reviews/esketamine-trd-madrs/review.json"

    def read(path):
        return b"in-memory changed source" if path == target else original(path)

    monkeypatch.setattr(Path, "read_bytes", read)
    assert walk.main(["--notice", "N20"]) == 1
    output = capsys.readouterr()
    assert not output.out and "STALE" in output.err  # decision B: a page that no longer serves the judged result


def test_already_signed_synthetic_notice_offers_no_signing_command(monkeypatch):
    # Entirely fictional input in RAM, separate from every clinical notice.
    notice = {
        "slug": "synthetic-signed", "outcome": "Synthetic outcome", "when_utc": "2000-01-01T00:00:00Z",
        "before": {"k": 3, "estimate": 2}, "after": {"k": 2, "estimate": 3},
        "left_pool": [], "entered_pool": [], "reason": "Synthetic test only.", "by": "Test author",
    }
    notice["reviewer_countersignature"] = {
        "state": "SEEN_AND_SIGNED", "by": "Test reviewer", "when_utc": "2000-01-01T00:00:00Z",
        "how_it_reached_the_reviewer": "In-memory test", "rendered_sha256": cli._block_and_sha(notice)[2],
    }
    row = dict(notice, audit_id="TEST", scale_before="MD", scale_after="MD", declared_estimand="MD", null_value=0,
               direction="SYNTHETIC", direction_explanation="Synthetic", mechanism="SYNTHETIC", mechanism_detail="Synthetic",
               individual_review_required_by_lane=True, individual_review_triggers=[], additional_individual_review_reason=None,
               gate_requires_per_notice_signature=True, recommendation="SYNTHETIC", recommendation_reason="Synthetic test only.",
               departing_trials=[], recovery_evidence=[])
    audit = {"notices": [row], "decision_groups": []}
    chains = [{"slug": notice["slug"], "outcome": notice["outcome"], "indices": [0], "ok": True, "problems": []}]
    # Fictional notice: no page exists, so the decision-B guard is replaced by a fictional judgement in RAM only.
    judgement = {"judgement_id": "TEST-J", "judged_utc": "2000-01-01T00:00:00Z", "served_commit": "0" * 40,
                 "proposed_commit": "0" * 40, "anchors": [], "before_after": "synthetic", "defects": []}
    monkeypatch.setattr(walk.notice_anchor, "guard", lambda *a, **k: (judgement, []))
    output = walk.present(audit, [notice], chains, {"TEST": 0}, 1)
    assert "Walk position 1 of 1 audited notices" in output
    assert "Valid for this block." in output
    assert "python scripts/countersign_result_change.py sign" not in output


def test_audit_identifiers_and_candidate_values_resolve_to_held_source_records(loaded):
    for row in loaded[0]["notices"]:
        review = json.loads((ROOT / row["page_evidence"]["review_path"]).read_text(encoding="utf-8"))
        assert {trial["trial_id"] for trial in row["departing_trials"]} == set(row["left_pool"])
        for trial in row["departing_trials"]:
            record = review
            for token in trial["current_pointer"].strip("/").split("/"):
                record = record[int(token)] if isinstance(record, list) else record[token]
            assert trial["trial_id"] == record["id"]
            assert trial["family_id"] == record["family_id"]
            assert trial["candidate_tuple"] == record["candidate_tuple"]
            assert trial["absence_code"] == record["absence_code"]
            assert record["source"].startswith(trial["source_excerpt"])


def test_powershell_literals_do_not_interpret_shell_characters():
    assert walk._ps("it's $x `test`") == "'it''s $x `test`'"
