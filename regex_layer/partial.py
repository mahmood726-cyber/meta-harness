"""R4 -- partial-number matches: an extractor group that captures PART of a number -- of a digit-grouped number,
of a decimal ('3' out of '7.3'), or of a longer digit run.

'48 488' (thin space, U+2009), '48,488' or '48 488' is one number. A group that starts right after "<digit><separator>"
or ends right before "<separator><3 digits>" has read a fragment: the value it returns is wrong, not merely unrefused.
This module finds such matches over EVERY held sentence (not a sample) so the radius of a fix is a count, not a guess.

  python -m regex_layer.partial      -> outputs/regex_layer/PARTIAL_NUMBERS.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from harness import extract
from regex_layer.measure import held_sentences
from regex_layer.specs import ROLES, SPECS

ROOT = Path(__file__).resolve().parents[1]
# the single definition lives in the served code; this module only measures with it
from harness.whole_numbers import SEP, WholeNumbers as RefusePartial, fragment_groups  # noqa: E402,F401


def partial_groups(name: str, sentence: str) -> list[dict]:
    """Every group of every match of `name`'s RAW pattern on `sentence` that is a fragment of a number (the served
    pattern may be wrapped in harness.whole_numbers and refuse these itself; the scan measures what the raw regex reads)."""
    out = []
    rx = getattr(extract, name)
    for m in getattr(rx, "rx", rx).finditer(sentence):
        for gi in fragment_groups(m):
            s, e = m.span(gi)
            out.append({"group": gi, "value": m.group(gi), "context": sentence[max(0, s - 12):e + 12]})
    return out


def scan() -> dict:
    extractors = [n for n, s in SPECS.items() if s["kind"] == "extractor"]
    seen, per = set(), {n: {"sentences": 0, "groups": 0, "examples": []} for n in extractors}
    total = 0
    for slug, rid, k, s in held_sentences():
        if s in seen:
            continue
        seen.add(s)
        total += 1
        for n in extractors:
            hits = partial_groups(n, s)
            if hits:
                c = per[n]
                c["sentences"] += 1
                c["groups"] += len(hits)
                if len(c["examples"]) < 5:
                    c["examples"].append({"ref": f"cache/{slug}/records.json#{rid} sentence {k}", "hits": hits})
    return {"held_sentences_scanned": total, "separators": [hex(ord(c)) for c in SEP],
            "patterns": {n: {**per[n], "role": ROLES[n], "of": f"{per[n]['sentences']} of {total}"} for n in extractors}}


if __name__ == "__main__":
    res = scan()
    out = ROOT / "outputs" / "regex_layer" / "PARTIAL_NUMBERS.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("held sentences", res["held_sentences_scanned"])
    for n, c in res["patterns"].items():
        if c["sentences"]:
            print(f"{n:14s} {c['of']:>14s} groups {c['groups']:>3}  role {c['role']}")
