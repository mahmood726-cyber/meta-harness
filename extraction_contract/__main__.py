"""CLI.  python -m extraction_contract <command>

  version                                   print the contract version
  check BUNDLE --docs-root DIR [--records DIR] [--out REPORT.json]
        exit 0 = ALLOW_MATCH_CLAIM with checked call records, 1 = noncertifying metadata/REFUSE,
        2 = could not execute (fail closed: never a pass)
  extract --docs-root DIR --document REF --trial ID --measure M --claude-model ID --codex-model ID
          [--codex-effort E] --out READINGS.json [--records-out DIR]
        the live dual reading (two recorded model calls); writes the readings and the call records
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

from . import CONTRACT_VERSION


def _load_records(d):
    recs = {}
    if d:
        for name in os.listdir(d):
            if name.endswith(".json"):
                with open(os.path.join(d, name), encoding="utf-8") as fh:
                    r = json.load(fh)
                if isinstance(r, dict) and r.get("record_id"):
                    recs[r["record_id"]] = r
    return recs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="extraction_contract")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("version")
    c = sub.add_parser("check")
    c.add_argument("bundle")
    c.add_argument("--docs-root", required=True)
    c.add_argument("--records")
    c.add_argument("--out")
    e = sub.add_parser("extract")
    for a in ("--docs-root", "--document", "--trial", "--measure", "--claude-model", "--codex-model", "--out"):
        e.add_argument(a, required=True)
    e.add_argument("--codex-effort", default="medium")
    e.add_argument("--records-out")
    a = ap.parse_args(argv)
    if a.cmd == "version":
        print(CONTRACT_VERSION)
        return 0
    if a.cmd == "check":
        from .gate import ALLOW, check_bundle
        try:
            with open(a.bundle, encoding="utf-8") as fh:
                bundle = json.load(fh)
            # No --records is diagnostic metadata-only review, NEVER an
            # authoritative ALLOW_MATCH_CLAIM result. Explicitly supplied,
            # even empty, records must prove call separation or fail closed.
            records = _load_records(a.records) if a.records is not None else None
            report = check_bundle(bundle, a.docs_root, records)
        except Exception as exc:  # noqa: BLE001 -- fail closed: a check that cannot run is never a pass
            print(f"P3 GATE: COULD-NOT-EXECUTE ({exc!r}) -- refusing", file=sys.stderr)
            return 2
        if a.out:
            with open(a.out, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"P3 GATE ({CONTRACT_VERSION}): {report['verdict']}  "
              f"trials ok {report.get('summary', {}).get('trials_ok', 0)}/{report.get('summary', {}).get('trials', 0)}")
        if a.records is None:
            print("  provenance: CALL_RECORDS_NOT_VERIFIED (NONCERTIFYING metadata-only mode; "
                  "no verified model call separation or external human validation)")
        for p in report["problems"]:
            print(f"  bundle: {p}")
        for t in report["trials"]:
            for p in t["problems"]:
                print(f"  {t['trial_id']}: {p}")
        return 0 if report["verdict"] == ALLOW else 1
    if a.cmd == "extract":
        from .readers import run_dual
        out = run_dual(docs_root=a.docs_root, document_ref=a.document, trial_id=a.trial, measure=a.measure,
                       claude_model=a.claude_model, codex_model=a.codex_model, codex_effort=a.codex_effort,
                       caller={"file": "extraction_contract/__main__.py", "line": "extract",
                               "purpose": f"P3 dual independent extraction of {a.trial} ({a.measure})"})
        if a.records_out:
            os.makedirs(a.records_out, exist_ok=True)
            for r in out["records"]:
                with open(os.path.join(a.records_out, f"{r['record_id']}.json"), "w", encoding="utf-8") as fh:
                    json.dump(r, fh, indent=1, ensure_ascii=False)
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump({"readings": out["readings"],
                       "records": [r["record_id"] for r in out["records"]]}, fh, indent=2, ensure_ascii=False)
        states = [r["state"] for r in out["records"]]
        print(f"P3 extract: claude={states[0]} codex={states[1]} -> {a.out}")
        return 0 if all(s == "RAN_OK" for s in states) else 1
    return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.exit(main())
