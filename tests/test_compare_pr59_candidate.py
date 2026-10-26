"""Negative mutations for independent PR59 synthetic CI archive parity.

These local fixtures are not a completed common benchmark or human validation.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path, PureWindowsPath, PurePosixPath
import sys
import tempfile
import unittest

BENCHMARK_DIR = Path(__file__).resolve().parents[1] / "benchmarks/cross_repo/v0.1"
sys.path.insert(0, str(BENCHMARK_DIR))
import compare_pr59_candidate as candidate  # noqa: E402
import pinned_pairwise_canary as producer  # noqa: E402


def encoded(obj):
    return (json.dumps(obj, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def frozen_cases():
    original = producer.produce("ALLOW")
    good = producer.wire(original)
    shadow = good.replace(b'"decision":"ALLOW"',
                          b'"decision":"REFUSE","decision":"ALLOW"', 1)
    wrong_source = copy.deepcopy(original)
    wrong_source["rows"][0]["source"]["sha256"] = "f" * 64
    wrong_trial = copy.deepcopy(original)
    wrong_trial["rows"][0]["trial_id"] = "SYN-TRIAL-99"
    return {
        "allow_synthetic_control": good,
        "refuse": producer.wire(producer.produce("REFUSE")),
        "manual_review": producer.wire(producer.produce("MANUAL_REVIEW")),
        "shadowed_refuse": shadow,
        "source_hash_drift": producer.wire(wrong_source),
        "source_trial_mismatch": producer.wire(wrong_trial),
    }


class ArchivedCandidateParityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.meta_sha = "1" * 40
        self.engine_sha = "2" * 64
        self.os_dirs = [self.root / "ubuntu", self.root / "windows"]
        raws = frozen_cases()
        self.assertEqual(
            {name: hashlib.sha256(raw).hexdigest() for name, raw in raws.items()},
            candidate.RAW_SHA, "independently frozen producer wire inputs changed"
        )
        for folder in self.os_dirs:
            (folder / "inputs").mkdir(parents=True)
            (folder / "results").mkdir()
            receipts = {}
            for name, raw in raws.items():
                input_path = folder / "inputs" / f"{name}.json"
                input_path.write_bytes(raw)
                receipts[f"inputs/{name}.json"] = hashlib.sha256(raw).hexdigest()
                allowed = name == "allow_synthetic_control"
                result = {
                    "case": name, "input_sha256": receipts[f"inputs/{name}.json"],
                    "engine_invoked": allowed,
                    "status": "SYNTHETIC_ENGINE_EXECUTED" if allowed else "REFUSED",
                }
                if allowed:
                    result["engine_output"] = {"k_used": 2, "measure": "RR",
                                               "mu_log": -0.42, "tau2": 0.012}
                else:
                    result["refusal"] = f"synthetic fixture refused {name}"
                result_path = folder / "results" / f"{name}.json"
                result_path.write_bytes(encoded(result))
                receipts[f"results/{name}.json"] = hashlib.sha256(
                    result_path.read_bytes()).hexdigest()
            index = {
                "runner_checkout_sha": self.meta_sha,
                "rapidmeta_pinned_sha": candidate.RAPIDMETA_SHA,
                "consumer_profile": "rapidmeta-pr59-20261026",
                "consumer_engine_git_blob": candidate.RAPIDMETA_BLOB,
                "registered_manifest_rapidmeta_sha_unchanged": candidate.REGISTERED_SHA,
                "source_sha256": candidate.SOURCE_SHA,
                "rapidmeta_engine_sha256": self.engine_sha,
                "python_runtime": "3.13.7", "node_runtime": "v22.14.0",
                "digests": receipts, **candidate.SCOPES,
            }
            (folder / "index.json").write_bytes(encoded(index))

    def compare(self):
        return candidate.compare(*self.os_dirs, self.meta_sha, self.engine_sha)

    def reseal_result(self, folder, name):
        index_path = folder / "index.json"
        index = json.loads(index_path.read_bytes())
        result_path = folder / "results" / f"{name}.json"
        index["digests"][f"results/{name}.json"] = hashlib.sha256(
            result_path.read_bytes()).hexdigest()
        index_path.write_bytes(encoded(index))

    def test_receipt_keys_canonical_across_native_path_flavours(self):
        self.assertEqual(
            producer.receipt_key(
                PureWindowsPath(r"archive\inputs\refuse.json"),
                PureWindowsPath("archive")),
            "inputs/refuse.json")
        self.assertEqual(
            producer.receipt_key(
                PurePosixPath("archive/inputs/refuse.json"),
                PurePosixPath("archive")),
            "inputs/refuse.json")

    def test_exact_two_archive_comparison_passes(self):
        result = self.compare()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["no_pool_count"], 5)
        self.assertEqual(result["archived_receipts_verified"], 24)

    def test_refused_case_marked_pooled_is_rejected_even_when_resealed(self):
        folder = self.os_dirs[1]
        result_path = folder / "results/refuse.json"
        record = json.loads(result_path.read_bytes())
        record["engine_invoked"] = True
        result_path.write_bytes(encoded(record))
        self.reseal_result(folder, "refuse")
        with self.assertRaisesRegex(ValueError, "no-pool execution decision"):
            self.compare()

    def test_numerical_drift_is_not_masked_by_matching_statistical_status(self):
        folder = self.os_dirs[1]
        result_path = folder / "results/allow_synthetic_control.json"
        record = json.loads(result_path.read_bytes())
        record["engine_output"]["mu_log"] = -0.98
        result_path.write_bytes(encoded(record))
        self.reseal_result(folder, "allow_synthetic_control")
        with self.assertRaisesRegex(ValueError, "cross-platform synthetic numerical drift"):
            self.compare()

    def test_coordinated_input_and_receipt_rewrite_cannot_change_frozen_wire(self):
        for folder in self.os_dirs:
            path = folder / "inputs/refuse.json"
            path.write_bytes(path.read_bytes().replace(b"REFUSE", b"ALLOW"))
            index_path = folder / "index.json"
            index = json.loads(index_path.read_bytes())
            index["digests"]["inputs/refuse.json"] = hashlib.sha256(
                path.read_bytes()).hexdigest()
            index_path.write_bytes(encoded(index))
        with self.assertRaisesRegex(ValueError, "independently frozen raw input"):
            self.compare()

    def test_duplicate_raw_index_members_are_rejected(self):
        path = self.os_dirs[0] / "index.json"
        path.write_bytes(path.read_bytes().replace(
            b'"python_runtime":',
            b'"python_runtime":"0.0.0","python_runtime":', 1
        ))
        with self.assertRaisesRegex(ValueError, "duplicate archived JSON member"):
            self.compare()

    def test_extra_artifact_result_is_rejected(self):
        (self.os_dirs[1] / "results/unregistered.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "unexpected or missing archived files"):
            self.compare()

    def test_unresealed_result_change_is_rejected(self):
        path = self.os_dirs[1] / "results/refuse.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "archived input/result digest"):
            self.compare()


if __name__ == "__main__":
    unittest.main()
