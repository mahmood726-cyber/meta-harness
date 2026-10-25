"""Isolated negative controls for frozen archived refusal replay.

These tests use fabricated local canary modules. Their passing is not evidence
that the two frozen repositories, either OS, or external R was exercised.
"""
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

PROGRAM = (Path(__file__).resolve().parents[1] /
           "benchmarks/cross_repo/v0.1/replay_archived_refusal_016.py")
sys.path.insert(0, str(PROGRAM.parent))
SPEC = importlib.util.spec_from_file_location("replay_archived_refusal_016", PROGRAM)
replay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replay)


class FrozenRefusalReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.meta, self.rapid = self.root / "meta", self.root / "rapid"
        self.rapid.mkdir()
        self.canary = (self.meta /
                       "benchmarks/cross_repo/v0.1/pinned_pairwise_canary.py")
        self.canary.parent.mkdir(parents=True)
        self.raw = b'{"rows":[{"decision":"MANUAL_REVIEW"}]}'

    def stub(self, invokes_engine=False):
        self.canary.write_text(
            """import hashlib
import subprocess

def consume(raw, rapid, label):
    if %s:
        subprocess.run(['node', '--version'])
    return {'case': label, 'input_sha256': hashlib.sha256(raw).hexdigest(),
            'status': 'REFUSED', 'engine_invoked': False,
            'refusal': ('duplicate JSON object member: decision' if label == 'duplicate_shadow'
                        else 'Declared trial_id does not match verbatim source'
                        if label == 'source_trial_mismatch'
                        else 'row 0: estimand mismatch (measure/population/outcome/timepoint)'
                        if label == 'estimand_mismatch'
                        else 'row 0: source SHA-256 mismatch'
                        if label == 'source_sha_tamper'
                        else 'requires manual review')}
""" % ("True" if invokes_engine else "False"), encoding="utf-8"
        )

    def test_child_interpreter_executes_refusal_without_pooling(self):
        self.stub()
        observed, stdout_sha = replay.replay_frozen_bytes(
            self.meta, self.rapid, self.raw)
        self.assertEqual(observed["status"], "REFUSED")
        self.assertFalse(observed["engine_invoked"])
        self.assertEqual(len(stdout_sha), 64)
        replay.verify_replay_observation(observed, dict(observed), self.raw)

    def test_subprocess_invocation_fails_closed(self):
        self.stub(invokes_engine=True)
        with self.assertRaisesRegex(RuntimeError, "NO_POOL: subprocess invoked"):
            replay.replay_frozen_bytes(self.meta, self.rapid, self.raw)

    def test_direct_popen_invocation_fails_closed(self):
        # A direct Popen call bypassed the original run-only tripwire.
        self.stub()
        source = self.canary.read_text(encoding="utf-8")
        self.canary.write_text(source.replace(
            "    return {'case': label,",
            "    subprocess.Popen(['node', '--version'])\n    return {'case': label,"
        ), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "NO_POOL: subprocess invoked"):
            replay.replay_frozen_bytes(self.meta, self.rapid, self.raw)

    def test_numeric_zero_cannot_impersonate_refused_no_pool_receipt(self):
        # A real isolated refusal replay yields a Boolean. Rehashing the
        # archive cannot legitimise an integer/float zero in its place.
        self.stub()
        observed, _ = replay.replay_frozen_bytes(self.meta, self.rapid, self.raw)
        self.assertIs(observed["engine_invoked"], False)
        for provenance in ("replayed", "archived"):
            for numeric_zero in (0, 0.0):
                with self.subTest(provenance=provenance, value=numeric_zero):
                    replayed, archived = dict(observed), dict(observed)
                    target = replayed if provenance == "replayed" else archived
                    target["engine_invoked"] = numeric_zero
                    with self.assertRaisesRegex(
                        ValueError, provenance + " engine_invoked must be JSON boolean"
                    ):
                        replay.verify_replay_observation(
                            replayed, archived, self.raw, "manual_review"
                        )

    def test_different_archived_refusal_reason_is_rejected(self):
        self.stub()
        observed, _ = replay.replay_frozen_bytes(self.meta, self.rapid, self.raw)
        forged = dict(observed, refusal="a different decision")
        with self.assertRaisesRegex(ValueError, "archived/frozen refusal provenance"):
            replay.verify_replay_observation(observed, forged, self.raw)

    def test_refusal_with_archived_pool_fields_is_rejected(self):
        self.stub()
        observed, _ = replay.replay_frozen_bytes(self.meta, self.rapid, self.raw)
        forged = dict(observed, engine_output={"mu_log": 0.2})
        with self.assertRaisesRegex(ValueError, "refused replay contains pool output"):
            replay.verify_replay_observation(observed, forged, self.raw)

    def test_archived_input_sha_mismatch_is_rejected(self):
        self.stub()
        observed, _ = replay.replay_frozen_bytes(self.meta, self.rapid, self.raw)
        forged = dict(observed, input_sha256="f" * 64)
        with self.assertRaisesRegex(ValueError, "archived consumer input_sha256"):
            replay.verify_replay_observation(observed, forged, self.raw)

    def test_refuse_label_replays_separately_without_pooling(self):
        self.stub()
        raw_refuse = self.raw.replace(b"MANUAL_REVIEW", b"REFUSE")
        observed, digest = replay.replay_frozen_bytes(
            self.meta, self.rapid, raw_refuse, "refuse")
        self.assertEqual(observed["case"], "refuse")
        self.assertEqual(observed["status"], "REFUSED")
        self.assertFalse(observed["engine_invoked"])
        self.assertEqual(len(digest), 64)
        replay.verify_replay_observation(observed, dict(observed),
                                         raw_refuse, "refuse")

    def test_refuse_label_is_not_accepted_as_manual_review(self):
        self.stub()
        raw_refuse = self.raw.replace(b"MANUAL_REVIEW", b"REFUSE")
        observed, _ = replay.replay_frozen_bytes(
            self.meta, self.rapid, raw_refuse, "refuse")
        with self.assertRaisesRegex(ValueError, "label/decision mismatch"):
            replay.verify_replay_observation(
                observed, dict(observed), raw_refuse, "manual_review")

    def test_refuse_label_with_manual_review_wire_is_refused(self):
        self.stub()
        with self.assertRaisesRegex(ValueError, "label/decision mismatch"):
            replay.replay_frozen_bytes(
                self.meta, self.rapid, self.raw, "refuse")

    def test_duplicate_raw_decision_cannot_shadow_scenario(self):
        self.stub()
        raw = b'{"rows":[{"decision":"REFUSE","decision":"MANUAL_REVIEW"}]}'
        with self.assertRaisesRegex(ValueError, "duplicate replay result member"):
            replay.replay_frozen_bytes(
                self.meta, self.rapid, raw, "refuse")


    def test_shadowed_decision_raw_json_replayed_in_isolated_child_without_pooling(self):
        # Fixture wire with a literal duplicate raw object member. The real
        # frozen wire and its independent SHA are checked in cross-OS CI.
        raw = b'{"rows":[{"decision":"REFUSE","decision":"ALLOW"}]}'
        self.stub()
        with mock.patch.object(replay, "SHADOWED_REFUSAL_SHA256",
                               hashlib.sha256(raw).hexdigest()):
            observed, receipt = replay.replay_frozen_bytes(
                self.meta, self.rapid, raw, "duplicate_shadow")
            replay.verify_replay_observation(
                observed, dict(observed), raw, "duplicate_shadow")
        self.assertEqual(observed["refusal"], replay.DUPLICATE_KEY_REFUSAL)
        self.assertFalse(observed["engine_invoked"])
        self.assertEqual(len(receipt), 64)

    def test_shadowed_decision_rejects_byte_drift_and_parser_bypass(self):
        raw = b'{"rows":[{"decision":"REFUSE","decision":"ALLOW"}]}'
        self.stub()
        frozen = hashlib.sha256(raw).hexdigest()
        with mock.patch.object(replay, "SHADOWED_REFUSAL_SHA256", frozen):
            with self.assertRaisesRegex(ValueError, "registered shadowed-decision input SHA256 mismatch"):
                replay.replay_frozen_bytes(
                    self.meta, self.rapid, raw + b" ", "duplicate_shadow")
        no_duplicate = b'{"rows":[{"decision":"ALLOW"}]}'
        with mock.patch.object(replay, "SHADOWED_REFUSAL_SHA256",
                               hashlib.sha256(no_duplicate).hexdigest()):
            with self.assertRaisesRegex(ValueError, "accepted by strict preparse"):
                replay.replay_frozen_bytes(
                    self.meta, self.rapid, no_duplicate, "duplicate_shadow")

    def test_shadowed_decision_refusal_cannot_attempt_pool_subprocess(self):
        raw = b'{"rows":[{"decision":"REFUSE","decision":"ALLOW"}]}'
        self.stub(invokes_engine=True)
        with mock.patch.object(replay, "SHADOWED_REFUSAL_SHA256",
                               hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(RuntimeError, "NO_POOL: subprocess invoked"):
                replay.replay_frozen_bytes(
                    self.meta, self.rapid, raw, "duplicate_shadow")

    def trial_wire(self, *, claim="SYN-TRIAL-99", decision="ALLOW"):
        # Standalone fixture: not the immutable two-row pinned source. Real CI
        # independently replays the archived frozen producer on both OSes.
        return json.dumps({"rows": [{
            "decision": decision, "trial_id": claim,
            "source_span": {"verbatim": "SYN-TRIAL-01 tE=4 tN=20 cE=5 cN=20"}
        }]}).encode("utf-8")

    def test_accepted_importer_trial_bridge_replays_without_pool(self):
        self.stub()
        raw = self.trial_wire()
        observed, receipt = replay.replay_frozen_bytes(
            self.meta, self.rapid, raw, "source_trial_mismatch")
        self.assertEqual(observed["refusal"], replay.TRIAL_BRIDGE_REFUSAL)
        self.assertEqual(observed["status"], "REFUSED")
        self.assertFalse(observed["engine_invoked"])
        self.assertEqual(len(receipt), 64)
        replay.verify_replay_observation(
            observed, dict(observed), raw, "source_trial_mismatch")

    def test_accepted_importer_trial_bridge_trips_if_pool_attempted(self):
        self.stub(invokes_engine=True)
        with self.assertRaisesRegex(RuntimeError, "NO_POOL: subprocess invoked"):
            replay.replay_frozen_bytes(
                self.meta, self.rapid, self.trial_wire(), "source_trial_mismatch")

    def test_trial_bridge_refuses_wire_without_actual_discrepancy(self):
        self.stub()
        with self.assertRaisesRegex(ValueError, "exactly one source/trial mismatch"):
            replay.replay_frozen_bytes(
                self.meta, self.rapid, self.trial_wire(claim="SYN-TRIAL-01"),
                "source_trial_mismatch")

    def test_trial_bridge_refuses_wrong_importer_decision(self):
        self.stub()
        with self.assertRaisesRegex(ValueError, "label/decision mismatch"):
            replay.replay_frozen_bytes(
                self.meta, self.rapid, self.trial_wire(decision="REFUSE"),
                "source_trial_mismatch")

    def test_trial_bridge_requires_specific_replayed_refusal(self):
        self.stub()
        raw = self.trial_wire()
        observed, _ = replay.replay_frozen_bytes(
            self.meta, self.rapid, raw, "source_trial_mismatch")
        forged = dict(observed, refusal="some unrelated error")
        with self.assertRaisesRegex(ValueError, "archived/frozen refusal provenance"):
            replay.verify_replay_observation(
                observed, forged, raw, "source_trial_mismatch")
        with self.assertRaisesRegex(ValueError, "accepted-importer source/trial bridge refusal"):
            replay.verify_replay_observation(
                forged, forged, raw, "source_trial_mismatch")

    def test_unknown_replay_label_fails_before_child_or_engine(self):
        self.stub()
        with self.assertRaisesRegex(ValueError, "unregistered negative replay label"):
            replay.replay_frozen_bytes(
                self.meta, self.rapid, self.raw, "allow_rr_itt")
        with self.assertRaisesRegex(ValueError, "unregistered negative replay label"):
            replay.verify_replay_observation(
                {"case": "refuse"}, {"case": "refuse"}, self.raw,
                "allow_rr_itt")

    def test_ambiguous_replay_json_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate replay result member"):
            json.loads('{"status":"REFUSED","status":"ACCEPTED"}',
                       object_pairs_hook=replay._unique)



    def test_full_run_passes_independent_engine_pin_and_fails_closed(self):
        # Regression for exact-head CI #40141321387: comparator gained a
        # mandatory immutable-engine argument, but replay.run omitted it.
        # These are mocked routing checks only; the CI matrix runs the
        # genuine pinned producer/consumer and archived refusal replay.
        registration = self.root / "registration.json"
        registration.write_text('{"record_version":"fixture-only"}', encoding="utf-8")
        ubuntu, windows = self.root / "ubuntu", self.root / "windows"
        pinned = "d" * 64
        with (mock.patch.object(replay, "exact_checkout_checks",
                                return_value={"engine_sha256": pinned}) as check,
              mock.patch.object(replay, "compare",
                                side_effect=ValueError("pinned RapidMeta engine SHA256")) as comparator,
              mock.patch.object(replay, "replay_frozen_bytes") as replay_child):
            with self.assertRaisesRegex(ValueError, "pinned RapidMeta engine SHA256"):
                replay.run(registration, ubuntu, windows, self.meta, self.rapid)
        check.assert_called_once()
        comparator.assert_called_once_with(registration, ubuntu, windows, pinned)
        replay_child.assert_not_called()

    def test_post_comparison_regular_refusal_input_drift_refuses_before_child(self):
        """A substituted *regular* file must not inherit a prior SHA PASS.

        Synthetic local unit fixture only. The two OS CI archives and the
        frozen producer/consumer are exercised by separate live workflows.
        """
        frozen = b'{"rows":[{"decision":"REFUSE","trial_id":"SYN-TRIAL-01"}]}'
        substituted = b'{"rows":[{"decision":"REFUSE","trial_id":"SYN-TRIAL-02"}]}'
        registration = self.root / "registration.json"
        registration.write_text(json.dumps({"negative_input_sha256": {
            "refuse": hashlib.sha256(frozen).hexdigest()
        }}), encoding="utf-8")
        ubuntu, windows = self.root / "ubuntu", self.root / "windows"
        target = ubuntu / "inputs" / "refuse.json"
        target.parent.mkdir(parents=True)
        target.write_bytes(substituted)
        # The file is not a link, its JSON is valid, and REFUSE remains REFUSE.
        self.assertFalse(target.is_symlink())
        self.assertEqual(json.loads(substituted)["rows"][0]["decision"], "REFUSE")
        with (mock.patch.object(replay, "exact_checkout_checks",
                                return_value={"engine_sha256": "d" * 64}),
              mock.patch.object(replay, "compare",
                                return_value={"overall": "PASS"}) as comparison,
              mock.patch.object(replay, "replay_frozen_bytes") as child):
            with self.assertRaisesRegex(
                ValueError, "post-comparison registered negative input SHA256 drift: refuse"
            ):
                replay.run(registration, ubuntu, windows, self.meta, self.rapid)
            comparison.assert_called_once()
            child.assert_not_called()

    def test_post_comparison_refusal_sha_accepts_only_exact_frozen_wire(self):
        raw = b'{"rows":[{"decision":"MANUAL_REVIEW"}]}'
        registration = {"negative_input_sha256": {
            "manual_review": hashlib.sha256(raw).hexdigest()
        }}
        replay.assert_registered_replay_sha256(raw, "manual_review", registration)
        with self.assertRaisesRegex(ValueError, "registered negative input SHA256 drift"):
            replay.assert_registered_replay_sha256(
                raw + b" ", "manual_review", registration)
        with self.assertRaisesRegex(ValueError, "missing registered negative replay"):
            replay.assert_registered_replay_sha256(raw, "refuse", registration)

    def test_post_comparison_archive_input_link_refuses_before_replay(self):
        """A path substituted after archive comparison must not enter the child.

        The independent comparator already rejects linked files. This checks
        that replay independently repeats the path-custody guard rather than
        trusting a previously checked path after an archive mutation.
        A mocked link bit works on both Windows and Linux CI runners.
        """
        registration = self.root / "registration.json"
        registration.write_text('{"fixture":"synthetic only"}', encoding="utf-8")
        ubuntu, windows = self.root / "ubuntu", self.root / "windows"
        target = ubuntu / "inputs" / "refuse.json"
        target.parent.mkdir(parents=True)
        target.write_bytes(self.raw.replace(b"MANUAL_REVIEW", b"REFUSE"))
        with (mock.patch.object(replay, "exact_checkout_checks",
                                return_value={"engine_sha256": "d" * 64}),
              mock.patch.object(replay, "compare",
                                return_value={"overall": "PASS"}) as comparison,
              mock.patch.object(replay, "replay_frozen_bytes") as child,
              mock.patch.object(Path, "is_symlink", autospec=True,
                                side_effect=lambda p: p == target)):
            with self.assertRaisesRegex(ValueError, "archive file is a symlink"):
                replay.run(registration, ubuntu, windows, self.meta, self.rapid)
            comparison.assert_called_once()
            child.assert_not_called()

    def estimand_wire(self, *, measure="OR", row_decision="ALLOW"):
        return json.dumps({"proposed_pool": {"estimand": {
            "measure": measure, "population": "ITT", "outcome": "synthetic event",
            "timepoint": "12 months"}}, "rows": [
            {"decision": row_decision, "estimand": {
                "measure": "RR", "population": "ITT", "outcome": "synthetic event",
                "timepoint": "12 months"}},
            {"decision": "ALLOW", "estimand": {
                "measure": "RR", "population": "ITT", "outcome": "synthetic event",
                "timepoint": "12 months"}}]}).encode("utf-8")

    def test_pinned_estimand_negative_replays_without_pooling(self):
        # Fabricated isolated fixture only; the workflow uses real frozen bytes.
        raw = self.estimand_wire()
        self.stub()
        with mock.patch.object(replay, "ESTIMAND_MISMATCH_SHA256",
                               hashlib.sha256(raw).hexdigest()):
            observed, receipt = replay.replay_frozen_bytes(
                self.meta, self.rapid, raw, "estimand_mismatch")
            replay.verify_replay_observation(observed, dict(observed), raw,
                                             "estimand_mismatch")
        self.assertEqual(observed["refusal"], replay.ESTIMAND_MISMATCH_REFUSAL)
        self.assertFalse(observed["engine_invoked"])
        self.assertEqual(len(receipt), 64)

    def test_estimand_negative_refuses_hash_drift_and_hidden_refuse(self):
        raw = self.estimand_wire()
        self.stub()
        with mock.patch.object(replay, "ESTIMAND_MISMATCH_SHA256",
                               hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(ValueError, "registered estimand-mismatch input SHA256"):
                replay.replay_frozen_bytes(self.meta, self.rapid, raw + b" ",
                                           "estimand_mismatch")
        hidden = self.estimand_wire(row_decision="REFUSE")
        with mock.patch.object(replay, "ESTIMAND_MISMATCH_SHA256",
                               hashlib.sha256(hidden).hexdigest()):
            with self.assertRaisesRegex(ValueError, "label/decision mismatch"):
                replay.replay_frozen_bytes(self.meta, self.rapid, hidden,
                                           "estimand_mismatch")

    def test_estimand_negative_pool_attempt_is_refused(self):
        raw = self.estimand_wire()
        self.stub(invokes_engine=True)
        with mock.patch.object(replay, "ESTIMAND_MISMATCH_SHA256",
                               hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(RuntimeError, "NO_POOL: subprocess invoked"):
                replay.replay_frozen_bytes(self.meta, self.rapid, raw,
                                           "estimand_mismatch")

    def test_estimand_negative_requires_actual_measure_mismatch(self):
        raw = self.estimand_wire(measure="RR")
        self.stub()
        with mock.patch.object(replay, "ESTIMAND_MISMATCH_SHA256",
                               hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(ValueError, "lacks registered RR-row versus OR-pool"):
                replay.replay_frozen_bytes(self.meta, self.rapid, raw,
                                           "estimand_mismatch")



    def source_digest_wire(self, *, tamper=True, decision="ALLOW"):
        return json.dumps({"rows": [
            {"decision": decision, "source": {
                "path": "benchmarks/cross_repo/v0.1/synthetic-binary-arms.txt",
                "sha256": "f" * 64 if tamper else replay.FROZEN_SOURCE_SHA256}},
            {"decision": "ALLOW", "source": {
                "path": "benchmarks/cross_repo/v0.1/synthetic-binary-arms.txt",
                "sha256": replay.FROZEN_SOURCE_SHA256}}
        ]}, sort_keys=True).encode("utf-8")

    def test_source_digest_pinned_negative_replays_without_pooling(self):
        # Isolated stub; real frozen importer/consumer replay runs in exact-head CI.
        self.stub()
        raw = self.source_digest_wire()
        with mock.patch.object(replay, "SOURCE_TAMPER_SHA256", hashlib.sha256(raw).hexdigest()):
            observed, stdout_digest = replay.replay_frozen_bytes(
                self.meta, self.rapid, raw, "source_sha_tamper")
            replay.verify_replay_observation(observed, dict(observed), raw,
                                             "source_sha_tamper")
        self.assertEqual(observed["refusal"], replay.SOURCE_TAMPER_REFUSAL)
        self.assertFalse(observed["engine_invoked"])
        self.assertEqual(len(stdout_digest), 64)

    def test_source_digest_negative_rejects_hash_drift_and_nonattack(self):
        self.stub()
        raw = self.source_digest_wire()
        with mock.patch.object(replay, "SOURCE_TAMPER_SHA256", hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(ValueError, "registered source-tamper input SHA256 mismatch"):
                replay.replay_frozen_bytes(self.meta, self.rapid,
                                           raw + b" ", "source_sha_tamper")
        good = self.source_digest_wire(tamper=False)
        with mock.patch.object(replay, "SOURCE_TAMPER_SHA256", hashlib.sha256(good).hexdigest()):
            with self.assertRaisesRegex(ValueError, "lacks one deliberately corrupt"):
                replay.replay_frozen_bytes(self.meta, self.rapid, good,
                                           "source_sha_tamper")

    def test_source_digest_negative_refuses_hidden_refuse_and_pool_attempt(self):
        self.stub()
        hidden = self.source_digest_wire(decision="REFUSE")
        with mock.patch.object(replay, "SOURCE_TAMPER_SHA256", hashlib.sha256(hidden).hexdigest()):
            with self.assertRaisesRegex(ValueError, "label/decision mismatch"):
                replay.replay_frozen_bytes(self.meta, self.rapid, hidden,
                                           "source_sha_tamper")
        raw = self.source_digest_wire()
        self.stub(invokes_engine=True)
        with mock.patch.object(replay, "SOURCE_TAMPER_SHA256", hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(RuntimeError, "NO_POOL: subprocess invoked"):
                replay.replay_frozen_bytes(self.meta, self.rapid, raw,
                                           "source_sha_tamper")

    def test_source_digest_negative_requires_specific_provenance(self):
        self.stub()
        raw = self.source_digest_wire()
        with mock.patch.object(replay, "SOURCE_TAMPER_SHA256", hashlib.sha256(raw).hexdigest()):
            observed, _ = replay.replay_frozen_bytes(
                self.meta, self.rapid, raw, "source_sha_tamper")
            forged = dict(observed, refusal="unrelated failure")
            with self.assertRaisesRegex(ValueError, "frozen source SHA mismatch importer refusal"):
                replay.verify_replay_observation(forged, forged, raw,
                                                 "source_sha_tamper")

if __name__ == "__main__":
    unittest.main()
