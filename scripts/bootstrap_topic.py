"""Fail-closed first-topic bootstrap; each step records its exit code."""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]


def run_step(name, command, log):
    print(f"STEP {name}: {command}", flush=True)
    env = dict(os.environ, CAPTAIN_NO_WORKTREE_SCAN="1", PYTHONIOENCODING="utf-8")
    with log.with_suffix(f".{name}.txt").open("wb") as output:
        try:
            rc = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, env=env).returncode
        except OSError as exc:
            output.write(str(exc).encode("utf-8"))
            rc = 1
    with log.open("a", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps({"step": name, "argv": command, "rc": rc}) + "\n")
    print(f"{name}: rc={rc}", flush=True)
    return rc


def acquire(slug, now):
    from harness import fetch
    from harness.served_comparator import served_config
    config = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
    fetch.ensure(served_config(slug, config), now)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("--now", default=date.today().isoformat(), type=lambda s: date.fromisoformat(s).isoformat())
    parser.add_argument("--acquire-only", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    slug = args.slug
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        parser.error("invalid topic slug")
    log = ROOT / ".codex_logs" / f"bootstrap_{slug}.jsonl"
    log.parent.mkdir(exist_ok=True)
    # No expansion-batch fallback: this exact protocol must exist in HEAD.
    check = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"HEAD:protocols/{slug}.md"],
                           capture_output=True)
    if args.acquire_only:
        if check.returncode:
            print(f"REFUSED: protocols/{slug}.md is not committed")
            return check.returncode
        acquire(slug, args.now)
        return 0
    with log.open("w", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps({"step": "committed_protocol", "rc": check.returncode}) + "\n")
    print(f"committed_protocol: rc={check.returncode}", flush=True)
    if check.returncode:
        print(f"REFUSED: protocols/{slug}.md is not committed")
        return check.returncode
    py = sys.executable
    steps = []
    if not (ROOT / "cache" / slug / "comparators.json").is_file():
        steps.append(("comparators", [py, "scripts/seed_comparator_panels.py", "--slug", slug, "--from-protocol"]))
    steps.extend([
        ("acquisition", [py, "scripts/bootstrap_topic.py", slug, "--now", args.now, "--acquire-only"]),
        ("draft", [py, "scripts/build_topic_recorded.py", slug, "--now", args.now, "--bootstrap-draft"]),
        ("rob2", [py, "scripts/rob2_build.py", slug, "--write"]),
        ("build", [py, "scripts/build_topic_recorded.py", slug, "--now", args.now]),
        ("replay", [py, "scripts/generate_replay.py", "--slug", slug]),
        ("census", [py, "scripts/provenance_census.py", "--slug", slug, "--write"]),
        ("gate", [py, "-m", "harness.gate", str(ROOT / "docs/reviews" / slug)]),
    ])
    for name, command in steps:
        rc = run_step(name, command, log)
        if rc:
            print(f"REFUSED: {name}; stopped. See {log.with_suffix(f'.{name}.txt')}")
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
