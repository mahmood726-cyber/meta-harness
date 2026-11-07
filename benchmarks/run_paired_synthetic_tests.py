"""Run only paired *synthetic* benchmark tests in a minimal temporary tree.

This is a supplementary offline measurement command, NOT the repository's
protected verify gate, a source-rights authorization, or a sandbox for untrusted
Python. It never reads cache/, topics/, docs/, publication or model fixtures.
Use with already approved local source files; do not add it to legacy verify CI.
"""
from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

# An explicit three-file allowlist, not discovery from the original checkout.
BENCHMARK_SOURCES = (
    'benchmarks/paired_false_positive.py',
    'tests/test_paired_false_positive.py',
    'tests/test_paired_discrimination.py',
)
EXPECTED_TESTS = 31  # intentional ratchet: a silently absent test is a failure


class RunnerRefusal(RuntimeError):
    """Missing, linked, irregular, or unreadable allowlisted source."""


def _read_allowlisted_file(root: Path, relative: str) -> bytes:
    if not relative or '/' not in relative or any(
        part in ('', '.', '..') for part in relative.split('/')
    ):
        raise RunnerRefusal('invalid allowlisted relative path')
    parent_name, filename = relative.split('/', 1)
    parent = root / parent_name
    try:
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise RunnerRefusal(f'{parent_name}: expected real directory')
        source = parent / filename
        if not stat.S_ISREG(source.lstat().st_mode):
            raise RunnerRefusal(f'{relative}: expected regular non-symlink source')
        flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
        fd = os.open(source, flags)
        with os.fdopen(fd, 'rb') as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise RunnerRefusal(f'{relative}: source changed during open')
            return handle.read()
    except FileNotFoundError as exc:
        raise RunnerRefusal(f'{relative}: missing allowlisted source') from exc
    except OSError as exc:
        raise RunnerRefusal(f'{relative}: unable to read allowlisted source') from exc


_TEST_CODE = (
    'import os, sys, unittest\n'
    'sys.path.insert(0, os.getcwd())\n'
    'suite = unittest.defaultTestLoader.discover('
    'start_dir="tests", pattern="test_paired*.py", top_level_dir=".")\n'
    'result = unittest.TextTestRunner(verbosity=2).run(suite)\n'
    'sys.exit(0 if result.wasSuccessful() and result.testsRun == int(sys.argv[1]) '
    'and not result.skipped and not result.expectedFailures '
    'and not result.unexpectedSuccesses else 1)\n'
)


def run_synthetic_tests(root: Path, *, expected_tests: int = EXPECTED_TESTS) -> int:
    """Execute only staged synthetic pair tests, return 0 on exact-count success.

    Python's isolated flags and the allowlist limit ordinary accidental imports;
    they are not a hardened execution sandbox for hostile code. The full gate
    remains required separately and may be withheld under source-rights hold.
    """
    if type(expected_tests) is not int or expected_tests < 1:
        raise RunnerRefusal('expected_tests must be a positive integer')
    root = Path(root).absolute()
    if not stat.S_ISDIR(root.lstat().st_mode):
        raise RunnerRefusal('root must be a real directory')
    contents = {name: _read_allowlisted_file(root, name) for name in BENCHMARK_SOURCES}

    with tempfile.TemporaryDirectory(prefix='synthetic-paired-only-') as location:
        stage = Path(location)
        (stage / 'benchmarks').mkdir()
        (stage / 'tests').mkdir()
        (stage / 'benchmarks' / '__init__.py').write_bytes(b'')
        (stage / 'tests' / '__init__.py').write_bytes(b'')
        for name, content in contents.items():
            (stage / name).write_bytes(content)
            print(f'STAGED {name} SHA256={hashlib.sha256(content).hexdigest()}')
        env = {'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1'}
        if 'SystemRoot' in os.environ:
            env['SystemRoot'] = os.environ['SystemRoot']
        try:
            proc = subprocess.run(
                [sys.executable, '-I', '-S', '-B', '-c', _TEST_CODE, str(expected_tests)],
                cwd=stage, env=env, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=120, check=False,
            )
        except subprocess.TimeoutExpired:
            print('FAIL: isolated synthetic tests exceeded 120 seconds', file=sys.stderr)
            return 1
        print(proc.stdout, end='')
        print(proc.stderr, end='', file=sys.stderr)
        print(f'ISOLATED_SYNTHETIC_TEST_RESULT={"PASS" if proc.returncode == 0 else "FAIL"}')
        return 0 if proc.returncode == 0 else 1


if __name__ == '__main__':
    try:
        raise SystemExit(run_synthetic_tests(Path(__file__).resolve().parents[1]))
    except (RunnerRefusal, OSError) as exc:
        print(f'ISOLATED_SYNTHETIC_TEST_RESULT=REFUSED: {exc}', file=sys.stderr)
        raise SystemExit(2) from None
