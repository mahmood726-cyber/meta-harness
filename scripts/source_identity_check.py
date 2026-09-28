"""Executable source-identity check (harness/source_identity.py): every held article's own title must be its target's
record; a quarantined document is listed, never passed. Exit 1 on any mismatch.
  PYTHONPATH=. python scripts/source_identity_check.py"""
import sys

from harness import source_identity


def main() -> int:
    r = source_identity.ledger_check()
    print(f"source identity: {len(r['ok'])} verified, {len(r['quarantined'])} quarantined, "
          f"{len(r['no_record'])} without a record, {len(r['mismatch'])} MISMATCHED")
    for x in r["quarantined"]:
        print("  QUARANTINED", x)
    for x in r["mismatch"]:
        print("  MISMATCH", x)
    return 1 if r["mismatch"] else 0


if __name__ == "__main__":
    sys.exit(main())
