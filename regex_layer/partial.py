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
SEP = "    ,"          # thin space, narrow nbsp, nbsp, space, comma
_BEFORE = re.compile(rf"\d[{SEP}]$")
_AFTER = re.compile(rf"^[{SEP}]\d{{3}}(?!\d)")
_DEC_BEFORE = re.compile(r"\d\.$")        # '3' read out of '7.3'
_DEC_AFTER = re.compile(r"^\.\d")         # '7' read out of '7.3'
_DIGIT_BEFORE = re.compile(r"\d$")        # '23' read out of '123'
_DIGIT_AFTER = re.compile(r"^\d")


def fragment_groups(m: re.Match) -> list[int]:
    """Group numbers of match `m` that capture a fragment of a number in m.string (grouped, decimal or digit run)."""
    text, out = m.string, []
    for gi in range(1, (m.re.groups or 0) + 1):
        if m.group(gi) is None or not re.fullmatch(r"\d+(?:\.\d+)?", m.group(gi)):
            continue
        s, e = m.span(gi)
        head, tail = text[max(0, s - 2):s], text[e:e + 5]
        grouped = (_BEFORE.search(head) and re.fullmatch(r"\d{3}", m.group(gi))) or _AFTER.search(tail)
        decimal = _DEC_BEFORE.search(head) or (_DEC_AFTER.search(tail) and "." not in m.group(gi))
        run = _DIGIT_BEFORE.search(head) or _DIGIT_AFTER.search(tail)
        if grouped or decimal or run:
            out.append(gi)
    return out


def partial_groups(name: str, sentence: str) -> list[dict]:
    """Every group of every match of `name` on `sentence` that is a fragment of a number."""
    out = []
    for m in getattr(extract, name).finditer(sentence):
        for gi in fragment_groups(m):
            s, e = m.span(gi)
            out.append({"group": gi, "value": m.group(gi), "context": sentence[max(0, s - 12):e + 12]})
    return out


class RefusePartial:
    """A compiled pattern whose matches that read a fragment of a number are REFUSED (dropped, never repaired).
    Used only to measure the radius of R4 -- not installed anywhere served."""

    def __init__(self, rx: re.Pattern):
        self.rx, self.pattern, self.flags, self.groups = rx, rx.pattern, rx.flags, rx.groups

    def finditer(self, s, *a):
        return (m for m in self.rx.finditer(s, *a) if not fragment_groups(m))

    def search(self, s, *a):
        return next(self.finditer(s, *a), None)

    def findall(self, s, *a):
        ms = list(self.finditer(s, *a))
        if self.rx.groups == 0:
            return [m.group(0) for m in ms]
        return [m.group(1) if self.rx.groups == 1 else m.groups("") for m in ms]

    def match(self, s, *a):
        m = self.rx.match(s, *a)
        return None if m is None or fragment_groups(m) else m

    def sub(self, *a, **k):
        return self.rx.sub(*a, **k)


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
