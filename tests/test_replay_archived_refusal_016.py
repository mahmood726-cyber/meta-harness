"""Isolated negative controls for frozen archived refusal replay.

These tests use fabricated local canary modules. Their passing is not evidence
that the two frozen repositories, either OS, or external R was exercised.
"""
import importlib.util
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
            'refusal': 'requires manual review'}
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

if __name__ == "__main__":
    unittest.main()
