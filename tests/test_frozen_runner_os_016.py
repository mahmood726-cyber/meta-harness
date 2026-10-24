"""Negative OS-attestation regressions for the frozen two-repository wire canary.

These are synthetic unit tests, distinct from executing RapidMeta on either OS.
"""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path, PureWindowsPath, PurePosixPath
import unittest
from unittest import mock

RUNNER = Path(__file__).resolve().parents[1] / "benchmarks/cross_repo/v0.1/frozen_cli_api_handoff_016.py"
spec_module = importlib.util.spec_from_file_location("frozen_runner_os_016", RUNNER)
if spec_module is None or spec_module.loader is None:
    raise RuntimeError("frozen runner missing")
runner = importlib.util.module_from_spec(spec_module)
spec_module.loader.exec_module(runner)

class RunnerIdentityTests(unittest.TestCase):
    def setUp(self):
        self.registration = {"runtime": {"os": ["ubuntu-24.04", "windows-2025"]}}

    def test_correct_ubuntu(self):
        with mock.patch.dict(os.environ, {"BENCHMARK_RUNNER_IMAGE": "ubuntu-24.04"}), \
             mock.patch.object(runner.platform, "system", return_value="Linux"), \
             mock.patch.object(runner.platform, "freedesktop_os_release",
                               return_value={"ID": "ubuntu", "VERSION_ID": "24.04"}):
            result = runner.runner_image(self.registration)
        self.assertEqual((result["runner_image_label"], result["observed_system"]),
                         ("ubuntu-24.04", "Linux"))

    def test_correct_windows_family(self):
        with mock.patch.dict(os.environ, {"BENCHMARK_RUNNER_IMAGE": "windows-2025"}), \
             mock.patch.object(runner.platform, "system", return_value="Windows"):
            result = runner.runner_image(self.registration)
        self.assertEqual((result["runner_image_label"], result["observed_system"]),
                         ("windows-2025", "Windows"))

    def test_spoofed_windows_image_on_linux_refused(self):
        with mock.patch.dict(os.environ, {"BENCHMARK_RUNNER_IMAGE": "windows-2025"}), \
             mock.patch.object(runner.platform, "system", return_value="Linux"):
            with self.assertRaisesRegex(ValueError, "inconsistent"):
                runner.runner_image(self.registration)

    def test_wrong_ubuntu_version_refused(self):
        with mock.patch.dict(os.environ, {"BENCHMARK_RUNNER_IMAGE": "ubuntu-24.04"}), \
             mock.patch.object(runner.platform, "system", return_value="Linux"), \
             mock.patch.object(runner.platform, "freedesktop_os_release",
                               return_value={"ID": "ubuntu", "VERSION_ID": "22.04"}):
            with self.assertRaisesRegex(ValueError, "distro/version"):
                runner.runner_image(self.registration)

    def test_unknown_image_refused(self):
        with mock.patch.dict(os.environ, {"BENCHMARK_RUNNER_IMAGE": "windows-latest"}), \
             mock.patch.object(runner.platform, "system", return_value="Windows"):
            with self.assertRaisesRegex(ValueError, "not in frozen"):
                runner.runner_image(self.registration)

    def test_absent_image_label_refused(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "not in frozen"):
                runner.runner_image(self.registration)

    def test_archive_receipt_keys_are_posix_even_on_windows(self):
        windows_path = PureWindowsPath("inputs", "refuse.json")
        self.assertEqual(runner.receipt_key(windows_path), "inputs/refuse.json")
        self.assertEqual(runner.receipt_key(PurePosixPath("results", "refuse.json")),
                         "results/refuse.json")

    def test_registration_must_pin_both_runners(self):
        with mock.patch.dict(os.environ, {"BENCHMARK_RUNNER_IMAGE": "ubuntu-24.04"}):
            with self.assertRaisesRegex(ValueError, "explicitly list"):
                runner.runner_image({"runtime": {"os": "ubuntu-24.04"}})

if __name__ == "__main__":
    unittest.main()
