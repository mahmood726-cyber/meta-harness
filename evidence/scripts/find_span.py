"""Locate a quote (copied from a web page) in the lane's deterministic render of a held source and return the EXACT
render substring to pin. Web copies differ from the held bytes in whitespace, dashes, quotes and non-breaking spaces,
so matching is done on a normalised form and mapped back to the original offsets; the returned span is always a
verbatim substring of textrep.render(ref) (asserted). Proposes only: the lane reviews every binding.
  python find_span.py <ref> "<quote>"      or   import find_span; find_span.locate(ref, quote)"""
import os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
import textrep

FOLD = {"‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
        "‘": "'", "’": "'", "“": '"', "”": '"', " ": " ", " ": " ", " ": " "}


def _norm(s):
    """Normalised text plus, for each normalised character, the index of the original character it came from."""
    out, idx = [], []
    prev_space = True
    for i, ch in enumerate(s):
        ch = FOLD.get(ch, ch)
        ch = unicodedata.normalize("NFKC", ch)
        for c in ch:
            if c.isspace():
                if prev_space:
                    continue
                c, prev_space = " ", True
            else:
                prev_space = False
            out.append(c.lower()); idx.append(i)
    return "".join(out), idx


def locate(ref, quote):
    text = textrep.render(ref)
    nt, idx = _norm(text)
    nq = _norm(quote)[0].strip()
    if not nq:
        return None
    k = nt.find(nq)
    if k < 0:
        return None
    start, end = idx[k], idx[k + len(nq) - 1] + 1
    span = text[start:end]
    assert span in text
    return span


if __name__ == "__main__":
    s = locate(sys.argv[1], sys.argv[2])
    print(repr(s) if s else "NOT_FOUND")
