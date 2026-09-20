"""Run the certified generator (scripts/build_topic.py, a pinned root of the certificate's analysis_code_blobs) and then write
docs/reviews/<slug>/EXECUTION_RECORD.json naming the tree it ran in.

Why a wrapper: the certificate pins build_topic.py byte-for-byte, so wiring the record into it is a release change (it moves
analysis_code_sha256 and release_sha256). Until a new release is cut, the record is written HERE, after the certified generator
returns and after CERTIFICATE.json exists -- so the record can name release_sha256 and the certificate cannot name the record
(the ordering sentence in harness/execution_record.py). This file is not in the import closure and is not pinned; the record it
writes says so in command.argv.

Usage: python scripts/build_topic_recorded.py <slug> [--now YYYY-MM-DD]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import build_topic  # noqa: E402  (the certified generator, unchanged)
from execution_record import write_execution_record  # noqa: E402


def main(argv):
    args = list(argv)
    now = "2026-09-11"
    if "--now" in args:
        now = args[args.index("--now") + 1]
        args = [a for a in args if a != now and a != "--now"]
    if len(args) != 1:
        raise SystemExit("usage: python scripts/build_topic_recorded.py <slug> [--now YYYY-MM-DD]")
    slug = args[0]
    build_topic.main(slug, now)
    rec = write_execution_record(os.path.join(ROOT, "docs", "reviews", slug), slug, [sys.executable, __file__, *argv], now)
    print(f"EXECUTION_RECORD.json: generating_commit={rec['tree']['generating_commit']} tree_state={rec['tree']['tree_state']} "
          f"release_sha256={rec['release']['release_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
