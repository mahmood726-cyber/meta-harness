"""V14-05 (signed "sign v14", option A): record the licence exception on every RETAINED_* tracked full text.

Derived, never typed by hand: the exception is stamped only when registry/v14_signatures.json holds V14-05 as
SEEN_AND_SIGNED with choice A, and only on rows whose state is RETAINED_NUMBER_DEPENDS / RETAINED_CLAIM_DEPENDS. The key
is prefixed 'retained_' so scripts/classify_tracked_fulltexts.py carries it forward. Behaviour is unchanged: these
texts were already typed/regex-only and never enter a model prompt (D8); the exception records WHY they stay.

    python scripts/v14_05_licence_exception.py
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIC = os.path.join(ROOT, "registry", "tracked_fulltext_licences.json")
SIG = os.path.join(ROOT, "registry", "v14_signatures.json")
RETAINED = ("RETAINED_NUMBER_DEPENDS", "RETAINED_CLAIM_DEPENDS")


def main():
    sig = json.load(open(SIG, encoding="utf-8"))
    item = (sig.get("items") or {}).get("V14-05") or {}
    if item.get("state") != "SEEN_AND_SIGNED" or item.get("choice") != "A":
        raise SystemExit("REFUSED: V14-05 is not signed with option A")
    exc = {"item": "V14-05", "choice": "A", "quote": item.get("quote"),
           "packet_sha256": item.get("packet_sha256"), "item_section_sha256": item.get("item_section_sha256"),
           "terms": ("kept under a recorded licence exception: typed/regex use only, never in a model prompt; each fact "
                     "is re-sourced from an open source as one becomes available")}
    doc = json.load(open(LIC, encoding="utf-8"))
    n = 0
    for r in doc["rows"]:
        if r.get("state") in RETAINED:
            r["retained_exception"] = exc
            n += 1
    with open(LIC, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"stamped {n} retained rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
