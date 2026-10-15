"""Run the generator (scripts/build_topic.py, a pinned root of the certificate's analysis_code_blobs) and then write
docs/reviews/<slug>/EXECUTION_RECORD.json naming the tree it ran in.

History and current state. This wrapper was written for the frozen pre-release 316d2e48, whose build_topic.py wrote no record:
the certificate pins build_topic.py byte-for-byte, so wiring the record into it was a release change, and until that release
change was made the record was written HERE, after the generator returned and after CERTIFICATE.json existed. The PRE-RELEASE
relabel commit (2026-09-20) IS that release change: build_topic.py now writes the record itself, last, after the certificate.
Running this wrapper on that tree or later therefore writes the record twice -- once by the generator and once here, with the
same argv and the same content -- which is harmless and redundant; it is kept so the replay commands recorded for 316d2e48 /
4b9dd46b (docs/reviews/glp1-ra-mace-t2d/REPLAY.md) still run as written. This file is not in the import closure and is not
pinned; the record's command.argv names whichever entry point ran.

Usage: python scripts/build_topic_recorded.py <slug> [--now YYYY-MM-DD] [--bootstrap-draft]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import build_topic  # noqa: E402  (the certified generator, unchanged)
from execution_record import write_execution_record  # noqa: E402


def main(argv):
    args = list(argv)
    bootstrap_draft = "--bootstrap-draft" in args
    if bootstrap_draft:
        args.remove("--bootstrap-draft")
    now = "2026-09-11"
    if "--now" in args:
        now = args[args.index("--now") + 1]
        args = [a for a in args if a != now and a != "--now"]
    if len(args) != 1:
        raise SystemExit("usage: python scripts/build_topic_recorded.py <slug> [--now YYYY-MM-DD] [--bootstrap-draft]")
    slug = args[0]
    if bootstrap_draft:
        # The ordinary pipeline returns the complete pooled core before census/certificate.
        # Only this non-servable intermediate is persisted; never call a renderer here.
        config = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        from harness.served_comparator import served_config
        config = served_config(slug, config)
        protocol_sha = build_topic._protocol_sha(slug)
        records = build_topic.fetch.ensure(config, now)
        core = build_topic.build_review_core(slug, config, records, protocol_sha)
        draft = dict(core, status="DRAFT_BOOTSTRAP")
        draft.pop("reproduction", None)
        build_topic._write(os.path.join(ROOT, "docs", "reviews", slug, "review.json"),
                           json.dumps(draft, ensure_ascii=False, indent=2))
        print(f"DRAFT_BOOTSTRAP: docs/reviews/{slug}/review.json (never servable)")
        return 0
    build_topic.main(slug, now)
    rec = write_execution_record(os.path.join(ROOT, "docs", "reviews", slug), slug, [sys.executable, __file__, *argv], now)
    print(f"EXECUTION_RECORD.json: generating_commit={rec['tree']['generating_commit']} tree_state={rec['tree']['tree_state']} "
          f"release_sha256={rec['release']['release_sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
