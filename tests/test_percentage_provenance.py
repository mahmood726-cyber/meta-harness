"""Percentage-synthesized counts may never be badged source-verified (external audit P0).

EMPHASIS-HF hyperkalemia shipped as 161/1367 vs 99/1376, provenance `aact_verified` — but those
counts were synthesized as (11.8% x 1367) / (7.2% x 1376): the counts are NOT in the source (only
the percentages are) and the denominators (summing to 2743) are not the trial's randomised 2737.
A rounded-percentage x an unverified denominator is HARNESS-RECONSTRUCTED, never source-verified.

Rule: any committed arm-count entry whose provenance CLAIMS verification (aact_verified /
abstract_verified / fulltext_verified*) must have its counts locatable in the source it cites --
as digits OR as number-words ("seven of 44"). A count that only round-trips to a percentage token,
with the exact count absent from the source, is a synthesis and must instead be `published_rate`
(which additionally grounds the denominator) or declared absent.
"""
import glob
import json
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
          "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
_VERIFIED_PROV = {"aact_verified", "abstract_verified", "fulltext_verified", "fulltext_verified_arms"}


def _num_in(text, n):
    if n is None:
        return True
    t = (text or "").lower()
    if re.search(rf"(?<!\d){n}(?!\d)", t):
        return True
    for w, v in _WORDS.items():
        if v == n and re.search(rf"\b{w}\b", t):
            return True
    return False


def _pct_tokens(text):
    return [float(p) for p in re.findall(r"(\d+\.?\d*)\s*%", text or "")]


def _entries():
    for f in glob.glob(os.path.join(_ROOT, "cache", "*", "verified_arms.json")) + \
             glob.glob(os.path.join(_ROOT, "cache", "*", "verified_effects.json")):
        slug = os.path.basename(os.path.dirname(f))
        for pmid, e in json.load(open(f, encoding="utf-8")).items():
            if isinstance(e, dict):
                yield slug, pmid, e


def _is_percentage_synthesis(e):
    """True if this looks like counts synthesized from a % (round-trips to a % token) while the exact
    counts are NOT locatable in the cited source (digits or words)."""
    ai, n1, ci, n2 = e.get("ai"), e.get("n1i"), e.get("ci"), e.get("n2i")
    if ai is None or n1 is None:
        return False
    src = (e.get("source") or "") + " " + (e.get("verification") or "")
    pcts = _pct_tokens(src)
    if not pcts:
        return False
    round_trips = any(abs(ai / n1 * 100 - p) <= 0.2 for p in pcts)
    counts_in_source = _num_in(src, ai) and _num_in(src, ci)
    return round_trips and not counts_in_source


def test_no_verified_entry_is_percentage_synthesized():
    offenders = [f"{slug}::{pmid} ({e.get('provenance')})"
                 for slug, pmid, e in _entries()
                 if e.get("provenance") in _VERIFIED_PROV and not e.get("absent")
                 and _is_percentage_synthesis(e)]
    assert not offenders, ("percentage-synthesized counts badged source-verified (must be "
                           "published_rate or declared absent): " + "; ".join(offenders))


def test_PLANT_percentage_synthesis_under_verified_is_caught():
    # PLANT: the exact EMPHASIS-HF shape must be flagged as a synthesis under a verified provenance.
    planted = {"ai": 161, "n1i": 1367, "ci": 99, "n2i": 1376, "provenance": "aact_verified",
               "source": "occurred in 11.8% of patients in the eplerenone group and 7.2% of those in placebo"}
    assert planted["provenance"] in _VERIFIED_PROV and _is_percentage_synthesis(planted)


def test_explicit_counts_are_not_flagged():
    # a genuine entry whose counts ARE in the source (as words) must NOT be flagged
    ok = {"ai": 7, "n1i": 44, "ci": 16, "n2i": 45, "provenance": "aact_verified",
          "source": "diarrhea occurred in seven of 44 patients (15.9%) ... 16 of 45 patients (35.6%)"}
    assert not _is_percentage_synthesis(ok)
