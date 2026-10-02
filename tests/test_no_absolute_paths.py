"""Portability guard (plant).

A test must not write to an absolute drive-letter path: the suite then passes only on a machine that
happens to have that drive. Found on the MAHMOOD worker 2026-10-01, where tests/test_claim_object.py
handed an F: path to census.build_review_dir and the suite failed with WinError 3 on a box with no F:
drive, while CI (which has one) stayed green.

Fails if a quoted drive-letter path appears in tests/ outside the allowlist. The allowlist holds the
two cases that are NOT filesystem destinations: test_codex_call_log.py (a drive path inside a
captured log string being parsed) and test_witness.py (an os.environ default). Use tmp_path for
anything actually written.
"""
import os
import re

ALLOWLIST = {"test_codex_call_log.py", "test_witness.py", "test_no_absolute_paths.py"}
DRIVE = re.compile(r"[A-Za-z]:[\\/]")  # a drive letter, a colon, then a separator
QUOTES = (chr(34), chr(39))


def test_no_absolute_drive_paths_in_tests():
    here = os.path.dirname(os.path.abspath(__file__))
    offenders = []
    for name in sorted(os.listdir(here)):
        if not name.startswith("test_") or not name.endswith(".py") or name in ALLOWLIST:
            continue
        with open(os.path.join(here, name), encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for m in DRIVE.finditer(line):
                    i = m.start()
                    if i > 0 and line[i - 1] in QUOTES:
                        offenders.append("{}:{}: {}".format(name, lineno, line.strip()[:110]))
    assert not offenders, "quoted absolute drive paths in tests (use tmp_path): " + "; ".join(offenders)
