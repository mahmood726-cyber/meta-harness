"""A search record must reconcile with the identifiers it lists -- by a command, not by reading. OPT-IN; not a gate.

Ported (port M-D, 2026-10-21) from e156-ecosystem-starter scripts/search-record-reconcile.py and adapted to this
repo's search record: one SOURCE of a retrieval ledger (cache/<slug>/retrieval_ledger.json and
cache/<slug>/snapshots/<name>/retrieval_ledger.json; schema in harness/acquisition.py). Each source carries
`record_ids` (the list) and `funnel` {hits, fetched, retained, cap {kind, n, remainder}}.

WHY. harness/acquisition.validate() checks each source's STATE against its funnel (RAN_ERROR fetched 0, RAN_ZERO hits
0, a cap names its remainder) but never compares the funnel's numbers with the list the source names. A source whose
list carries an id twice, or whose fetch stopped short of the reported hit count while the source says RAN_OK, passes
it. The source harness measured the second failure on one of its own topics: a null cursor after 100+100+3 = 203
against a reported 430. A finished-looking pagination is corroboration; THE PROOF IS THE SUM, RECONCILED AGAINST THE
REPORTED TOTAL.

WHAT IT CHECKS, per source (each code names a different failure):

    DUPLICATE_IDS        len(record_ids) != len(set(record_ids)) -- inflates a denominator while every other
                         number still reconciles; invisible to everything but a set comparison
    LIST_NE_RETAINED     len(record_ids) != funnel.retained -- the list is not the list the funnel counted
    FETCHED_LT_RETAINED  funnel.fetched < funnel.retained -- more kept than was ever fetched
    FETCHED_NE_LIST      funnel.fetched != len(record_ids) -- the pages summed (esearch_all accumulates every page
                         into `fetched`) to a number the list does not hold: records fetched and silently lost
                         between fetch and retain, with nothing in the funnel declaring the loss
    TOTAL_NE_FETCHED     funnel.hits != fetched + cap.remainder (remainder 0 when cap.kind == "none") -- an
                         unexhausted pagination, or a fetch that overran the reported total. When the source's
                         state is RAN_OK this is the source claiming completeness the sum does not support.

VERDICTS (per source):
    RECONCILES          listed == distinct == retained == fetched == hits - remainder
    RECONCILES_NO_TOTAL every list check holds but the total is unrecorded (hits null, or a relevance_top_n cap
                        with an unknown remainder). Counted separately: the total limb was NOT checked.
    NOT_ASSESSABLE      the source names no identifiers and no number contradicts that. NEVER a pass.
    REFUSED             at least one code above fired.

WHAT THIS DOES NOT ESTABLISH
  - NOT that the ids are the RIGHT ones or that the query was well aimed: it compares a record against itself.
  - NOT recall. That is harness/search_completeness.py (wired into scripts/verify_all.py) and the sealed register.
  - NOTHING about the ledger-level `records` map (acquisition.validate() owns found_by consistency).

OPT-IN. Nothing runs this: it is not imported by harness/, not a verify_all limb, not a G1 input, not a CI step. A
lane opts in by running it, or by importing `check_source` / `check_ledger` from a script or test of its own.

USAGE
    python scripts/search_record_reconcile.py cache/<slug>/retrieval_ledger.json
    python scripts/search_record_reconcile.py cache/                     # every retrieval_ledger.json beneath it
    python scripts/search_record_reconcile.py --json cache/<slug>        # machine-readable rows on stdout
    python scripts/search_record_reconcile.py --selftest                 # can-fire proof, then exit

EXIT CODES
    0  every assessable source reconciles
    1  at least one source REFUSED, or --selftest failed
    2  no input given, or no retrieval ledger readable at the path

Standard library only. Offline. No network, no subprocess, no model call.
"""
from __future__ import annotations

import io
import json
import os
import sys

__version__ = "1.0.0"

LEDGER_FILENAME = "retrieval_ledger.json"

RECONCILES = "RECONCILES"
RECONCILES_NO_TOTAL = "RECONCILES_NO_TOTAL"
NOT_ASSESSABLE = "NOT_ASSESSABLE"
REFUSED = "REFUSED"
VERDICTS = (RECONCILES, RECONCILES_NO_TOTAL, NOT_ASSESSABLE, REFUSED)

CODES = ("DUPLICATE_IDS", "LIST_NE_RETAINED", "FETCHED_LT_RETAINED", "FETCHED_NE_LIST", "TOTAL_NE_FETCHED")


def _int(value):
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def check_source(source: dict) -> dict:
    """One verdict row for one ledger source: {source_id, verdict, codes, why, numbers}."""
    sid = (source or {}).get("source_id") or "<unknown>"
    ids = source.get("record_ids") if isinstance(source, dict) else None
    ids = [str(x) for x in ids] if isinstance(ids, list) else []
    funnel = source.get("funnel") if isinstance(source.get("funnel"), dict) else {}
    cap = funnel.get("cap") if isinstance(funnel.get("cap"), dict) else {}
    retained, fetched, hits = _int(funnel.get("retained")), _int(funnel.get("fetched")), _int(funnel.get("hits"))
    cap_kind = cap.get("kind") or "none"
    remainder = 0 if cap_kind == "none" else _int(cap.get("remainder"))
    listed, distinct = len(ids), len(set(ids))
    numbers = {"listed": listed, "distinct": distinct, "retained": retained, "fetched": fetched, "hits": hits,
               "cap_kind": cap_kind, "remainder": remainder}

    codes, why = [], []
    if distinct != listed:
        dupes = sorted({x for x in ids if ids.count(x) > 1})
        codes.append("DUPLICATE_IDS")
        why.append(f"{listed - distinct} duplicate id(s) in record_ids: {dupes[:6]}")
    if retained is not None and retained != listed:
        codes.append("LIST_NE_RETAINED")
        why.append(f"record_ids lists {listed} but funnel.retained says {retained}")
    if fetched is not None and retained is not None and fetched < retained:
        codes.append("FETCHED_LT_RETAINED")
        why.append(f"funnel.retained {retained} exceeds funnel.fetched {fetched}")
    if fetched is not None and fetched != listed:
        codes.append("FETCHED_NE_LIST")
        why.append(f"the pages summed to {fetched} fetched but record_ids lists {listed} -- "
                   f"{fetched - listed:+d} undeclared between fetch and list")
    total_checked = hits is not None and fetched is not None and remainder is not None
    if total_checked and fetched + remainder != hits:
        codes.append("TOTAL_NE_FETCHED")
        short = hits - fetched - remainder
        claim = " WHILE THE SOURCE REPORTS RAN_OK" if source.get("state") == "RAN_OK" and short > 0 else ""
        why.append(f"reported hits {hits} != fetched {fetched} + cap remainder {remainder} "
                   f"({short:+d} never returned{claim})")

    if codes:
        verdict = REFUSED
    elif not ids:
        verdict = NOT_ASSESSABLE
        why.append("record_ids is empty, so nothing can be checked against it. THIS IS NOT A PASS.")
    elif not total_checked:
        verdict = RECONCILES_NO_TOTAL
        why.append("listed == distinct == retained == fetched; the reported total is unrecorded, so the "
                   "total limb was not checked")
    else:
        verdict = RECONCILES
        why.append("listed == distinct == retained == fetched == hits - remainder")
    return {"source_id": sid, "verdict": verdict, "codes": codes, "why": "; ".join(why), "numbers": numbers}


def check_ledger(ledger: dict) -> list[dict]:
    """Every source of one retrieval ledger, in ledger order."""
    sources = ledger.get("sources") if isinstance(ledger, dict) else None
    return [check_source(s) for s in sources if isinstance(s, dict)] if isinstance(sources, list) else []


def _targets(argv):
    files = []
    for arg in argv:
        if os.path.isdir(arg):
            for dirpath, dirnames, filenames in os.walk(arg):
                dirnames.sort()
                if LEDGER_FILENAME in filenames:
                    files.append(os.path.join(dirpath, LEDGER_FILENAME))
        elif os.path.isfile(arg):
            files.append(arg)
    return files


def run(argv, out=None) -> int:
    out = out or sys.stdout
    as_json = "--json" in argv
    paths = [a for a in argv if a != "--json"]
    files = _targets(paths)
    if not files:
        sys.stderr.write(f"no {LEDGER_FILENAME} at: {' '.join(paths)}\n")
        return 2
    tally = {v: 0 for v in VERDICTS}
    code_tally = {c: 0 for c in CODES}
    rows, read_any = [], False
    for path in files:
        try:
            with io.open(path, "r", encoding="utf-8") as fh:
                ledger = json.load(fh)
        except (OSError, ValueError) as exc:
            sys.stderr.write(f"could not read {path}: {exc}\n")
            continue
        if not isinstance(ledger, dict) or not isinstance(ledger.get("sources"), list):
            sys.stderr.write(f"not a retrieval ledger (no sources list): {path}\n")
            continue
        read_any = True
        file_rows = check_ledger(ledger)
        for row in file_rows:
            row["path"] = path.replace("\\", "/")
            tally[row["verdict"]] += 1
            for c in row["codes"]:
                code_tally[c] += 1
        rows.extend(file_rows)
        if not as_json:
            refused = [r for r in file_rows if r["verdict"] == REFUSED]
            out.write(f"{path.replace(chr(92), '/')}: {len(file_rows)} sources, {len(refused)} REFUSED\n")
            for r in refused:
                out.write(f"    {r['source_id']:<40} {','.join(r['codes'])}: {r['why'][:160]}\n")
    if not read_any:
        sys.stderr.write("no file read was a retrieval ledger\n")
        return 2
    if as_json:
        out.write(json.dumps({"version": __version__, "tally": tally, "codes": code_tally, "rows": rows},
                             indent=1, sort_keys=True) + "\n")
    else:
        out.write("\n" + "  ".join(f"{v} {tally[v]}" for v in VERDICTS) + "\n")
        out.write("codes: " + "  ".join(f"{c} {code_tally[c]}" for c in CODES) + "\n")
        out.write("NOT_ASSESSABLE (no ids) and RECONCILES_NO_TOTAL (total unrecorded) are counted separately; "
                  "neither is a full pass.\n")
    return 1 if tally[REFUSED] else 0


def _src(ids, retained=None, fetched=None, hits=None, cap=None, state="RAN_OK"):
    n = len(ids)
    return {"source_id": "plant#1", "state": state, "record_ids": list(ids),
            "funnel": {"hits": n if hits is None else hits, "fetched": n if fetched is None else fetched,
                       "retained": n if retained is None else retained,
                       "cap": cap or {"kind": "none", "n": None, "remainder": None}}}


def selftest(out=None) -> int:
    """CAN-FIRE PROOF. A detector never shown to fire on a known-bad input is not a detector."""
    out = out or sys.stdout
    cases = [
        ("clean: listed 3 == distinct == retained == fetched == hits", _src(["1", "2", "3"]), RECONCILES, []),
        ("duplicate id: every count says 3, distinct is 2", _src(["1", "2", "2"]), REFUSED, ["DUPLICATE_IDS"]),
        ("page sum 4 != list 3", _src(["1", "2", "3"], fetched=4, hits=4), REFUSED, ["FETCHED_NE_LIST"]),
        ("total 430 != fetched 203, RAN_OK", _src([str(i) for i in range(203)], hits=430), REFUSED,
         ["TOTAL_NE_FETCHED"]),
        ("hard cap with its remainder declared reconciles",
         _src(["1", "2"], hits=5, cap={"kind": "hard_hits_cap", "n": 2, "remainder": 3}), RECONCILES, []),
        ("hits unrecorded -> total limb not checked", _src(["1"], hits=None) | {"funnel": {
            "hits": None, "fetched": 1, "retained": 1, "cap": {"kind": "none"}}}, RECONCILES_NO_TOTAL, []),
        ("empty list, nothing contradicts -> never a pass", _src([], hits=None) | {"funnel": {
            "hits": None, "fetched": 0, "retained": 0, "cap": {"kind": "none"}}}, NOT_ASSESSABLE, []),
    ]
    failures = 0
    for name, source, want, want_codes in cases:
        row = check_source(source)
        ok = row["verdict"] == want and all(c in row["codes"] for c in want_codes)
        failures += not ok
        out.write(f"  {name:<62} {'ok' if ok else 'FAIL'}  {row['verdict']} {row['codes']}\n")
    out.write(f"{len(cases) - failures} of {len(cases)} selftest cases passed (v{__version__}).\n")
    return 1 if failures else 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    if argv[0] == "--selftest":
        return selftest()
    return run(argv)


if __name__ == "__main__":
    sys.exit(main())
