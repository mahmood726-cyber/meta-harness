"""The exact source passage behind a value -- and the proof that the value is IN it.

passage = {"document_ref": <path relative to the docs root>, "document_sha256": <hex>, "start": int, "end": int,
           "quote": <verbatim text>}
Checks, all fail-closed:
  * the document resolves inside the docs root (no absolute path, no '..'), exists, and its bytes hash to
    document_sha256 -- a passage into a document that has since changed is not evidence of anything;
  * the UTF-8 text at [start:end] (character offsets) is EXACTLY the quote;
  * the value is literally present in the quote: a number as a numeric token (decimal comma/mid-dot, thousands
    separators and the Unicode minus normalised; a '-' between two numbers is a range dash, not a sign), a CI level
    as "95%" or 0.95, an enum by its keyword, free text as a case/whitespace-insensitive substring.
The last check is the one that matters: a quote that is real but does not contain the value is a citation, not a source.
"""
from __future__ import annotations

import hashlib
import os
import re
from decimal import Decimal, InvalidOperation

MIN_QUOTE, MAX_QUOTE = 3, 2000

SCALE_WORDS = {
    "HR": ("hazard ratio", "HR"), "OR": ("odds ratio", "OR"), "RR": ("risk ratio", "relative risk", "rate ratio", "RR"),
    "IRR": ("incidence rate ratio", "rate ratio", "IRR"), "RD": ("risk difference", "absolute difference", "RD"),
    "MD": ("mean difference", "difference in mean", "MD"), "SMD": ("standardised mean difference",
                                                                    "standardized mean difference", "SMD"),
}
SET_WORDS = {
    "ITT": ("intention-to-treat", "intention to treat", "intent-to-treat", "intent to treat", "ITT"),
    "mITT": ("modified intention", "modified intent", "mITT"),
    "PP": ("per-protocol", "per protocol", "PP population"),
    "AS_TREATED": ("as-treated", "as treated", "safety population"),
}
_NUM = re.compile(r"(?<![\d.·,])[-−]?\d+(?:,\d{3})*(?:[.·]\d+)?")


def numbers_in(text: str) -> list[Decimal]:
    out = []
    for m in _NUM.finditer(text or ""):
        tok, s = m.group(0), m.start()
        if tok[0] in "-−" and s > 0 and (text[s - 1].isdigit() or text[s - 1] in "  " and s > 1 and text[s - 2].isdigit()):
            tok = tok[1:]          # '0.71-0.90' / '0.71 -0.90': a range dash, not a minus sign
        tok = tok.replace("−", "-").replace("·", ".")
        if re.fullmatch(r"-?\d{1,3}(,\d{3})+(\.\d+)?", tok):
            tok = tok.replace(",", "")
        try:
            out.append(Decimal(tok))
        except InvalidOperation:
            continue
    return out


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").casefold()).strip()


def _word_in(words, quote) -> bool:
    for w in words:
        if w.isupper() and len(w) <= 4:              # acronyms: whole-token, case-sensitive
            if re.search(rf"(?<![A-Za-z]){re.escape(w)}(?![A-Za-z])", quote):
                return True
        elif _norm(w) in _norm(quote):
            return True
    return False


def value_in_quote(field: str, kind: str, value, quote: str) -> bool:
    if kind in ("int", "float"):
        try:
            target = Decimal(str(value))
        except InvalidOperation:
            return False
        nums = numbers_in(quote)
        if field == "ci_level":
            # ONLY as a percentage: a bare 0.9 in "95% CI 0.4 to 0.9" is the upper limit, not a 90% level
            pct = f"{(target * 100).normalize():f}"
            return bool(re.search(rf"(?<![\d.]){re.escape(pct)}\s?(%|per ?cent)", quote, re.I))
        if kind == "int":
            return any(n == target and n == n.to_integral_value() for n in nums)
        return target in nums
    if field == "effect_scale":
        return _word_in(SCALE_WORDS.get(value, (value,)), quote)
    if field == "analysis_set":
        return _word_in(SET_WORDS.get(value, (value,)), quote)
    return _norm(value) in _norm(quote)


def _resolve(docs_root: str, ref: str) -> str | None:
    if not isinstance(ref, str) or not ref.strip() or os.path.isabs(ref) or re.match(r"^[A-Za-z]:", ref):
        return None
    parts = re.split(r"[\\/]+", ref)
    if ".." in parts:
        return None
    return os.path.join(docs_root, *parts)


def passage_problems(passage, docs_root: str, _cache: dict | None = None) -> list[str]:
    """Problems with the passage itself (empty = it is verbatim text of a pinned, unchanged document)."""
    if not isinstance(passage, dict):
        return ["no passage (every trial-level value must carry the exact source passage it was read from)"]
    ref, sha, start, end, quote = (passage.get(k) for k in ("document_ref", "document_sha256", "start", "end", "quote"))
    if not isinstance(quote, str) or not (MIN_QUOTE <= len(quote) <= MAX_QUOTE):
        return [f"quote missing or outside {MIN_QUOTE}..{MAX_QUOTE} chars (a passage, not a document)"]
    if not (isinstance(start, int) and isinstance(end, int)) or isinstance(start, bool) or isinstance(end, bool) \
            or not 0 <= start < end:
        return [f"offsets {start!r}..{end!r} are not a valid character span"]
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
        return ["document_sha256 missing or not a sha256 (an unpinned document is not evidence)"]
    path = _resolve(docs_root, ref)
    if path is None:
        return [f"document_ref {ref!r} must be a relative path inside the docs root"]
    cache = _cache if _cache is not None else {}
    if path not in cache:
        try:
            with open(path, "rb") as fh:
                b = fh.read()
        except OSError:
            cache[path] = None
        else:
            try:
                cache[path] = (hashlib.sha256(b).hexdigest(), b.decode("utf-8"))
            except UnicodeDecodeError:
                cache[path] = (hashlib.sha256(b).hexdigest(), None)
    got = cache[path]
    if got is None:
        return [f"document {ref!r} not found under the docs root"]
    actual, text = got
    if actual != sha:
        return [f"document {ref!r} changed: sha256 {actual[:12]} != pinned {sha[:12]} (re-read it; never re-pin blindly)"]
    if text is None:
        return [f"document {ref!r} is not UTF-8 text"]
    if text[start:end] != quote:
        return [f"quote is not the text at {ref}[{start}:{end}] (a quote must be verbatim, at the offsets it claims)"]
    return []


def locate(text: str, quote: str) -> tuple[int, int] | None:
    """Offsets of a quote that occurs EXACTLY ONCE in text; None if absent or ambiguous (never guess which)."""
    if not quote or len(quote) < MIN_QUOTE:
        return None
    i = text.find(quote)
    if i < 0 or text.find(quote, i + 1) >= 0:
        return None
    return i, i + len(quote)
