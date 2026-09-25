"""The signature verifier: every verdict path, on in-memory ledgers only. Nothing here writes a ledger or a registry,
and no signature is ever made in anyone's name: the test signer is fictional."""
import copy
import json
from pathlib import Path

import pytest

from scripts import countersign_result_change as cli
from scripts import notice_anchor
from scripts import verify_notice_signatures as v

ROOT = Path(__file__).resolve().parents[1]
TEST_SIGNER = "TEST-SIGNER-NOT-A-REVIEWER"


@pytest.fixture(scope="module")
def base():
    ledger = json.loads(cli.PATH.read_text(encoding="utf-8"))["notices"]
    audit = json.loads((ROOT / "registry/notice_adjudication.json").read_text(encoding="utf-8"))
    return ledger, audit


def _signed(ledger, audit, audit_id, **overrides):
    ledger = copy.deepcopy(ledger)
    row = next(r for r in audit["notices"] if r["audit_id"] == audit_id)
    n = next(x for x in ledger if all(x[k] == row[k] for k in ("slug", "outcome", "when_utc")))
    sig = {"state": "SEEN_AND_SIGNED", "by": TEST_SIGNER, "when_utc": "2000-01-01T00:00:00Z",
           "rendered_sha256": cli._block_and_sha(n)[2], "how_it_reached_the_reviewer": "test: read the walker output",
           "judgement_id": notice_anchor.current_judgement(row)["judgement_id"]}
    sig.update(overrides)
    n["reviewer_countersignature"] = {k: val for k, val in sig.items() if val is not None}
    return ledger


def _verdict(rows, audit_id):
    return next(r for r in rows if r["audit_id"] == audit_id)


def test_the_committed_ledger_has_no_valid_signature_yet(base):
    rows = v.verify_ledger(*base)
    assert len(rows) == 41 and {r["verdict"] for r in rows} == {"MISSING"}


def test_a_signature_on_the_current_hash_and_judgement_is_valid(base):
    ledger, audit = base
    r = _verdict(v.verify_ledger(_signed(ledger, audit, "N04"), audit), "N04")
    assert r["verdict"] == "VALID", r["why"]


@pytest.mark.parametrize("override", [{"rendered_sha256": "0" * 64}, {"judgement_id": "B1-N04"},
                                      {"judgement_id": None}])
def test_a_signature_on_a_superseded_hash_or_judgement_is_stale(base, override):
    ledger, audit = base
    r = _verdict(v.verify_ledger(_signed(ledger, audit, "N04", **override), audit), "N04")
    assert r["verdict"] == "STALE"


@pytest.mark.parametrize("override,why", [
    ({"how_it_reached_the_reviewer": ""}, "how_it_reached_the_reviewer"),
    ({"how_it_reached_the_reviewer": v._DELEGATED_BASIS}, "DELEGATED_IS_NOT_A_SIGNATURE"),
    ({"authorised_by": "Dispatch"}, "DELEGATED_IS_NOT_A_SIGNATURE"),
])
def test_a_signature_the_gate_must_refuse_is_refused(base, override, why):
    ledger, audit = base
    r = _verdict(v.verify_ledger(_signed(ledger, audit, "N04", **override), audit), "N04")
    assert r["verdict"] == "REFUSED" and why in r["why"]


def test_a_signature_on_a_notice_whose_page_no_longer_serves_it_is_refused(base, monkeypatch):
    ledger, audit = base
    row = next(r for r in audit["notices"] if r["audit_id"] == "N04")
    page = ROOT / row["page_evidence"]["html_path"]
    original = Path.read_bytes
    monkeypatch.setattr(Path, "read_bytes",
                        lambda p: b"<html>rebuilt without the block</html>" if Path(p).resolve() == page.resolve()
                        else original(p))
    r = _verdict(v.verify_ledger(_signed(ledger, audit, "N04"), audit), "N04")
    assert r["verdict"] == "REFUSED" and "STALE" in r["why"]


def test_the_cli_on_head_reports_forty_one_missing(capsys):
    assert v.main(["--ref", "HEAD", "--base", "HEAD"]) == 0
    assert "0 of 41 VALID" in capsys.readouterr().out
