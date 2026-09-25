"""R4 of the regex layer: a regex match that reads a FRAGMENT of a number is refused, never repaired.

'48 488' (thin space), '1,139', '7.3' are each one number. A capture group that begins inside one ('488' out of
'48 488', '3' out of '7.3') or ends inside one ('2' out of 'n = 2,523', '0' out of 'interaction = 0.92') returns a
value the source does not state. Such a match is dropped, so the extractor sees no match there and falls back to its
existing refuse / declare-absent path -- the same as any sentence it cannot read.

The single definition: regex_layer (partial-number scan, radius) imports this, so what is measured is what runs.
"""
from __future__ import annotations

import re

SEP = "    ,"                 # thin space, narrow no-break space, no-break space, space, comma
_GROUPED_BEFORE = re.compile(rf"\d[{SEP}]$")
_GROUPED_AFTER = re.compile(rf"^[{SEP}]\d{{3}}(?!\d)")
_DEC_BEFORE = re.compile(r"\d\.$")           # '3' read out of '7.3'
_DEC_AFTER = re.compile(r"^\.\d")            # '7' read out of '7.3'
_DIGIT_BEFORE = re.compile(r"\d$")           # '23' read out of '123'
_DIGIT_AFTER = re.compile(r"^\d")
_NUMBER = re.compile(r"\d+(?:\.\d+)?")


def fragment_groups(m: re.Match) -> list[int]:
    """Group numbers of match `m` whose numeric capture is a fragment of a longer number in m.string."""
    text, out = m.string, []
    for gi in range(1, (m.re.groups or 0) + 1):
        g = m.group(gi)
        if g is None or not _NUMBER.fullmatch(g):
            continue
        s, e = m.span(gi)
        head, tail = text[max(0, s - 2):s], text[e:e + 5]
        grouped = (_GROUPED_BEFORE.search(head) and re.fullmatch(r"\d{3}", g)) or _GROUPED_AFTER.search(tail)
        decimal = _DEC_BEFORE.search(head) or (_DEC_AFTER.search(tail) and "." not in g)
        run = _DIGIT_BEFORE.search(head) or _DIGIT_AFTER.search(tail)
        if grouped or decimal or run:
            out.append(gi)
    return out


class WholeNumbers:
    """A compiled pattern whose fragment-reading matches are refused. Same interface as the pattern for the methods the
    harness calls (search / finditer / findall / match / sub), and it exposes the compiled pattern as .rx."""

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


def whole_numbers(rx: re.Pattern) -> WholeNumbers:
    return WholeNumbers(rx)
