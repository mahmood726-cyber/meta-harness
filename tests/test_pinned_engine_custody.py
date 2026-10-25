"""Isolated pinned RapidMeta Git-blob custody regression.

Synthetic local Git fixture only. Not an R oracle, clinical validation or a
four-repository benchmark execution.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "benchmarks/cross_repo/v0.1/pinned_pairwise_canary.py"
SPEC = importlib.util.spec_from_file_location("pinned_pairwise_custody", MODULE_PATH)
canary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(canary)


def git(*args):
    return subprocess.check_output(["git", *map(str, args)], timeout=15, text=True).strip()


class PinnedEngineCustodyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "meta"
        self.rapid = Path(temp.name) / "rapid"
        self.rapid.mkdir()
        git("init", "-q", self.rapid)
        engine = self.rapid / canary.ENGINE
        engine.parent.mkdir(parents=True)
        self.original_engine = b"// synthetic test-only JS engine\n"
        engine.write_bytes(self.original_engine)
        git("-C", self.rapid, "add", canary.ENGINE)
        git("-C", self.rapid, "-c", "user.name=CI Fixture",
            "-c", "user.email=ci@example.invalid", "commit", "-qm", "frozen fixture")
        self.head = git("-C", self.rapid, "rev-parse", "HEAD")
        source = self.root / canary.SOURCE
        source.parent.mkdir(parents=True, exist_ok=True)
        self.synthetic_source = b"TEST ONLY - not a clinical source\n"
        source.write_bytes(self.synthetic_source)
        manifest = self.root / "benchmarks/cross_repo/v0.1/manifest.json"
        manifest.write_text(json.dumps({
            "repositories": {"rapidmeta-kit": {"commit": self.head}}
        }), encoding="utf-8")
        root_patch = mock.patch.object(canary, "ROOT", self.root)
        source_patch = mock.patch.object(
            canary, "SOURCE_SHA256", hashlib.sha256(self.synthetic_source).hexdigest()
        )
        root_patch.start()
        source_patch.start()
        self.addCleanup(root_patch.stop)
        self.addCleanup(source_patch.stop)

    def test_clean_pinned_engine_matches_immutable_git_blob(self):
        observed_head, observed_digest = canary.preflight(self.rapid)
        self.assertEqual(observed_head, self.head)
        self.assertEqual(observed_digest,
                         hashlib.sha256(self.original_engine).hexdigest())

    def test_dirty_engine_worktree_refused_before_pooling(self):
        (self.rapid / canary.ENGINE).write_bytes(b"// changed synthetic engine\n")
        # The Git HEAD still matches the manifest. The changed bytes must be
        # refused rather than accepted as a legitimate pinned engine.
        self.assertEqual(git("-C", self.rapid, "rev-parse", "HEAD"), self.head)
        with self.assertRaisesRegex(RuntimeError,
                                    "worktree differs from pinned Git blob"):
            canary.preflight(self.rapid)

    def test_missing_engine_file_refused(self):
        (self.rapid / canary.ENGINE).unlink()
        with self.assertRaisesRegex(RuntimeError, "engine unavailable"):
            canary.preflight(self.rapid)


if __name__ == "__main__":
    unittest.main()
