"""Synthetic, isolated regressions for actual-artifact cross-OS comparator.

These tests are fixtures; workflow comparison consumes *real* matrix artifacts.
"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PROGRAM = Path(__file__).resolve().parents[1] / "benchmarks/cross_repo/v0.1/compare_cross_os_016.py"
SPEC = importlib.util.spec_from_file_location("compare_cross_os_016", PROGRAM)
comparator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(comparator)


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class ArchivedArtifactParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.reg = root / "registration.json"
        self.source = b"SYNTHETIC source only\n"
        self.engine_sha = "a" * 64
        self.spec = {
            "case_id": "CROSS-EXCH-016", "registered_status": "NOT_RUN",
            "input_type": "SYNTHETIC_FIXTURE_ONLY",
            "runtime": {"os": ["ubuntu-24.04", "windows-2025"],
                        "python": "3.13.7", "node": "22.14.0"},
            "repositories": {"meta-harness": {"commit": "a" * 40},
                             "rapidmeta-kit": {"commit": "b" * 40}},
            "frozen_source": {"sha256": comparator.digest(self.source)},
            "scenarios": {"allow_rr_itt": {"importer": "ACCEPTED", "consumer": "SYNTHETIC_ENGINE_EXECUTED"},
                          "refuse": {"importer": "REFUSED", "consumer": "REFUSED"},
                          "manual_review": {"importer": "REFUSED", "consumer": "REFUSED"}}
        }
        self.reg.write_bytes(wire(self.spec))
        self.ubuntu = root / "ubuntu"
        self.windows = root / "windows"
        self._write_archive(self.ubuntu, "ubuntu-24.04", "Linux")
        self._write_archive(self.windows, "windows-2025", "Windows")

    def _write_archive(self, directory, label, family, raw_modifier=None, engine_sha=None):
        (directory / "inputs").mkdir(parents=True, exist_ok=True)
        (directory / "results").mkdir(parents=True, exist_ok=True)
        (directory / "source.txt").write_bytes(self.source)
        digests = {"source.txt": comparator.digest(self.source)}
        for case, status in self.spec["scenarios"].items():
            raw = wire({"case": case, "decision": "ALLOW" if case == "allow_rr_itt" else case.upper()})
            if case == "refuse" and raw_modifier:
                raw = raw_modifier(raw)
            source_hash = comparator.digest(raw)
            consumer = {"case": case, "status": status["consumer"],
                        "input_sha256": source_hash,
                        "engine_invoked": case == "allow_rr_itt"}
            if case == "allow_rr_itt":
                consumer["engine_output"] = {"k_used": 2, "measure": "RR", "mu_log": 0.3, "tau2": 0.0}
            else:
                consumer["refusal"] = f"synthetic downstream refusal: {case}"
            output = {"name": case, "raw_sha256": source_hash,
                      "cli_status": status["importer"], "api_status": status["importer"],
                      "api_refusal": (f"synthetic import refusal: {case}"
                                      if status["importer"] == "REFUSED" else None),
                      "consumer": consumer}
            for path, contents in ((directory / "inputs" / f"{case}.json", raw),
                                   (directory / "results" / f"{case}.json", wire(output))):
                path.write_bytes(contents)
                digests[path.relative_to(directory).as_posix()] = comparator.digest(contents)
        index = {
            "case_id": "CROSS-EXCH-016", "registration_sha256": comparator.digest(self.reg.read_bytes()),
            "evidence_scope": "SYNTHETIC_FROZEN_TWO_REPOSITORY_CLI_API_HANDOFF_ONLY",
            "observed_runner": {"runner_image_label": label, "observed_system": family},
            "meta_harness_commit": "a" * 40, "rapidmeta_commit": "b" * 40,
            "source_sha256": comparator.digest(self.source), "rapidmeta_engine_sha256": engine_sha or self.engine_sha,
            "python_runtime": "3.13.7", "node_runtime": "v22.14.0",
            "external_R_oracle": "NOT_TESTED", "four_repo_suite": "NOT_RUN",
            "human_adjudication": "NOT_TESTED", "digests": digests,
        }
        (directory / "index.json").write_bytes(wire(index))

    def _rewrite_result(self, case, mutate):
        """Alter an archived outcome and update its SHA receipt as a failure injection."""
        target = self.windows / "results" / f"{case}.json"
        data = json.loads(target.read_text(encoding="utf-8"))
        mutate(data)
        target.write_bytes(wire(data))
        index_path = self.windows / "index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index["digests"][f"results/{case}.json"] = comparator.digest(target.read_bytes())
        index_path.write_bytes(wire(index))

    def test_matching_archives_pass(self):
        result = comparator.compare(self.reg, self.ubuntu, self.windows)
        self.assertEqual((result["case_count"], result["refused_without_pooling"]), (3, 2))
        self.assertEqual(result["numerical_output_cross_os_comparison"], "PINNED_SYNTHETIC_SMOKE_ONLY_PASS")
        self.assertEqual(result["numerical_smoke_controls"]["allow_rr_itt"]["ubuntu-24.04"]["mu_log"], 0.3)

    def test_individually_valid_sha_receipts_can_mask_cross_os_input_drift(self):
        # A matrix test checking each OS against statuses alone misses this.
        self._write_archive(self.windows, "windows-2025", "Windows",
                            lambda raw: raw.replace(b'"refuse"', b'"refuse-changed"'))
        with self.assertRaisesRegex(ValueError, "cross-OS decisions"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_cross_os_mu_log_drift_refuses_with_recomputed_sha_receipt(self):
        # These are synthetic archive fixtures, not real GitHub Actions output.
        self._rewrite_result("allow_rr_itt", lambda data:
                             data["consumer"]["engine_output"].__setitem__("mu_log", 0.31))
        with self.assertRaisesRegex(ValueError, "cross-OS pinned synthetic engine smoke drift"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_cross_os_tau2_drift_refuses_with_recomputed_sha_receipt(self):
        self._rewrite_result("allow_rr_itt", lambda data:
                             data["consumer"]["engine_output"].__setitem__("tau2", 0.02))
        with self.assertRaisesRegex(ValueError, "cross-OS pinned synthetic engine smoke drift"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_cross_os_roundoff_within_declared_tolerance_accepted(self):
        self._rewrite_result("allow_rr_itt", lambda data:
                             data["consumer"]["engine_output"].__setitem__("mu_log", 0.3 + 1e-13))
        report = comparator.compare(self.reg, self.ubuntu, self.windows)
        self.assertEqual(report["numerical_smoke_tolerance"]["rel_tol"], 1e-12)
        self.assertEqual(report["case_count"], 3)

    def test_engine_binary_drift_refuses_even_when_statuses_match(self):
        self._write_archive(self.windows, "windows-2025", "Windows", engine_sha="b" * 64)
        with self.assertRaisesRegex(ValueError, "cross-OS rapidmeta_engine_sha256"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_archive_one_byte_tamper_refuses(self):
        target = self.windows / "inputs" / "manual_review.json"
        target.write_bytes(target.read_bytes() + b"X")
        with self.assertRaisesRegex(ValueError, "archived SHA256 integrity failure"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_refused_case_engine_invocation_refuses_even_with_updated_receipt(self):
        result_path = self.windows / "results" / "manual_review.json"
        result = json.loads(result_path.read_text())
        result["consumer"]["engine_invoked"] = True
        result_path.write_bytes(wire(result))
        index_path = self.windows / "index.json"
        index = json.loads(index_path.read_text())
        index["digests"]["results/manual_review.json"] = comparator.digest(result_path.read_bytes())
        index_path.write_bytes(wire(index))
        with self.assertRaisesRegex(ValueError, "engine invocation"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_spoofed_os_refuses(self):
        index_path = self.windows / "index.json"
        index = json.loads(index_path.read_text())
        index["observed_runner"]["runner_image_label"] = "ubuntu-24.04"
        index_path.write_bytes(wire(index))
        with self.assertRaisesRegex(ValueError, "runner"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_changed_downstream_refusal_reason_refuses_despite_matching_status_and_receipt(self):
        self._rewrite_result("manual_review", lambda data:
                             data["consumer"].__setitem__("refusal", "different OS refusal"))
        with self.assertRaisesRegex(ValueError, "cross-OS decisions"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_changed_api_refusal_reason_refuses_despite_matching_status_and_receipt(self):
        self._rewrite_result("refuse", lambda data:
                             data.__setitem__("api_refusal", "different OS import refusal"))
        with self.assertRaisesRegex(ValueError, "cross-OS decisions"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_mislabelled_downstream_case_identity_refuses(self):
        self._rewrite_result("manual_review", lambda data:
                             data["consumer"].__setitem__("case", "refuse"))
        with self.assertRaisesRegex(ValueError, "consumer case identity"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_missing_api_refusal_reason_refuses(self):
        self._rewrite_result("refuse", lambda data:
                             data.__setitem__("api_refusal", None))
        with self.assertRaisesRegex(ValueError, "missing importer refusal reason"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_missing_downstream_refusal_reason_refuses(self):
        self._rewrite_result("manual_review", lambda data:
                             data["consumer"].pop("refusal"))
        with self.assertRaisesRegex(ValueError, "missing downstream refusal reason"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_valid_pool_cannot_carry_import_refusal_diagnostic(self):
        self._rewrite_result("allow_rr_itt", lambda data:
                             data.__setitem__("api_refusal", "pretend refused"))
        with self.assertRaisesRegex(ValueError, "accepted importer carried refusal reason"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_valid_pool_cannot_carry_downstream_refusal_diagnostic(self):
        self._rewrite_result("allow_rr_itt", lambda data:
                             data["consumer"].__setitem__("refusal", "pretend refused"))
        with self.assertRaisesRegex(ValueError, "pooled result carried refusal reason"):
            comparator.compare(self.reg, self.ubuntu, self.windows)

    def test_duplicate_archive_result_keys_refuse(self):
        target = self.windows / "results" / "refuse.json"
        original = target.read_bytes()
        target.write_bytes(original.replace(b'"cli_status":"REFUSED"',
                                            b'"cli_status":"ACCEPTED","cli_status":"REFUSED"'))
        index_path = self.windows / "index.json"
        index = json.loads(index_path.read_text())
        index["digests"]["results/refuse.json"] = comparator.digest(target.read_bytes())
        index_path.write_bytes(wire(index))
        with self.assertRaisesRegex(ValueError, "duplicate archived JSON member"):
            comparator.compare(self.reg, self.ubuntu, self.windows)


if __name__ == "__main__":
    unittest.main()
