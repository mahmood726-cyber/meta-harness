"""Bounded offline lane build/replay. Logs full command output without shell redirection."""
import contextlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def no_network(*args, **kwargs):
    raise RuntimeError("CMP lane forbids network access")


def main(mode):
    socket.socket.connect = no_network
    socket.create_connection = no_network
    from scripts.build_topic import main as build
    from scripts.reproduce_review import reproduce
    paths = sorted((ROOT / "docs/reviews").glob("*/review.json"))
    logs = ROOT / "outputs/comparator-lane"
    logs.mkdir(parents=True, exist_ok=True)
    if mode == "reproduce":
        empty = ROOT / ".tmp/cmp-empty-aact"
        empty.mkdir(parents=True, exist_ok=True)
        assert not list(empty.iterdir())
        os.environ["AACT_DIR"] = str(empty)
    rows = []
    for path in paths:
        slug = path.parent.name
        assert (ROOT / "cache" / slug / "records.json").exists(), slug
        log = io.StringIO()
        try:
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                if mode == "build":
                    build(slug, "2026-09-11")
                    ok, reasons = True, []
                else:
                    ok, reasons = reproduce(slug)
        except Exception as exc:
            ok, reasons = False, [repr(exc)]
        rows.append({"slug": slug, "ok": ok, "reasons": reasons})
        (logs / f"{mode}-{slug}.txt").write_text(log.getvalue() + "\n" + str(reasons), encoding="utf-8")
        print(mode, slug, "PASS" if ok else "FAIL", reasons, flush=True)
    (logs / f"{mode}.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"{mode}: {sum(r['ok'] for r in rows)} of {len(rows)}")
    return int(not all(r["ok"] for r in rows))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
