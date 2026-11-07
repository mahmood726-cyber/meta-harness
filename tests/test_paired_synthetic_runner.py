"""Synthetic-only negative controls for the isolated benchmark test launcher."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from benchmarks.run_paired_synthetic_tests import RunnerRefusal, run_synthetic_tests


class PairedSyntheticRunnerTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        (self.root / 'benchmarks').mkdir()
        (self.root / 'tests').mkdir()
        (self.root / 'cache').mkdir()
        (self.root / 'benchmarks' / 'paired_false_positive.py').write_text('VALUE = 3\n')
        for name in ('test_paired_false_positive.py', 'test_paired_discrimination.py'):
            (self.root / 'tests' / name).write_text(
                'import unittest\n'
                'from benchmarks.paired_false_positive import VALUE\n'
                'class Positive(unittest.TestCase):\n'
                '    def test_staged_module(self): self.assertEqual(VALUE, 3)\n'
            )

    def test_only_allowlisted_sources_are_executed(self):
        (self.root / 'tests' / 'test_legacy_scary.py').write_text('raise RuntimeError("legacy ran")\n')
        (self.root / 'cache' / 'article.txt').write_text('held and forbidden fixture')
        with contextlib.redirect_stdout(io.StringIO()):
            result = run_synthetic_tests(self.root, expected_tests=2)
        self.assertEqual(result, 0)

    def test_missing_expected_test_is_fail_closed(self):
        (self.root / 'tests' / 'test_paired_discrimination.py').unlink()
        with self.assertRaisesRegex(RunnerRefusal, 'missing'):
            run_synthetic_tests(self.root, expected_tests=2)

    def test_mismatched_test_count_fails(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_synthetic_tests(self.root, expected_tests=3), 1)

    def test_symlink_source_is_refused(self):
        target = self.root / 'cache' / 'secret.py'
        target.write_text('SECRET = "content"\n')
        link = self.root / 'benchmarks' / 'paired_false_positive.py'
        link.unlink()
        try:
            link.symlink_to(target)
        except (NotImplementedError, OSError):
            self.skipTest('symlinks unsupported here')
        with self.assertRaisesRegex(RunnerRefusal, 'regular non-symlink'):
            run_synthetic_tests(self.root, expected_tests=2)

    def test_symlink_parent_is_refused(self):
        real = self.root / 'tests'
        real.rename(self.root / 'real_tests')
        try:
            real.symlink_to(self.root / 'real_tests', target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest('symlinks unsupported here')
        with self.assertRaisesRegex(RunnerRefusal, 'directory'):
            run_synthetic_tests(self.root, expected_tests=2)

    def test_held_cache_not_exposed_to_tests(self):
        (self.root / 'cache' / 'article.txt').write_text('held material')
        (self.root / 'tests' / 'test_paired_discrimination.py').write_text(
            'import unittest\nfrom pathlib import Path\n'
            'class Negative(unittest.TestCase):\n'
            '    def test_no_cache_accessible(self):\n'
            '        self.assertFalse(Path("cache/article.txt").exists())\n'
        )
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_synthetic_tests(self.root, expected_tests=2), 0)


    def test_skipped_case_fails_closed_even_when_count_matches(self):
        (self.root / 'tests' / 'test_paired_discrimination.py').write_text(
            'import unittest\n'
            'class Skipped(unittest.TestCase):\n'
            '    @unittest.skip("not authorized")\n'
            '    def test_skipped(self): self.fail("not executed")\n'
        )
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_synthetic_tests(self.root, expected_tests=2), 1)

    def test_expected_failure_fails_closed_even_when_count_matches(self):
        (self.root / 'tests' / 'test_paired_discrimination.py').write_text(
            'import unittest\n'
            'class ExpectedFailure(unittest.TestCase):\n'
            '    @unittest.expectedFailure\n'
            '    def test_expected_failure(self): self.fail("not passing")\n'
        )
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_synthetic_tests(self.root, expected_tests=2), 1)


if __name__ == '__main__':
    unittest.main()
