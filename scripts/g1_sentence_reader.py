"""Conservative, deterministic prose candidates; never an admission decision.

Static rules: count/CI grammar, subgroup veto, arm cues, metadata vocabulary.
Dynamic inputs: supplied text and protocol terms; no fitted or invented results.
Offsets are Python character offsets; digests cover the original trimmed sentence.
Multiple candidates must be treated as AMBIGUOUS by callers.

The runtime-only census reuses the diagnostic's offline held-copy lookup. Its
metadata fields are presence booleans, not quotations. Labels/slugs are supplied
metadata, with digits spelled out so only n_candidates contains numeric digits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from harness.lexicon import fold, matches_only_as_subtype  # noqa: E402
from g1_trial_acquire import outcome_row_terms  # noqa: E402

INTEGER = r"(?:\d{1,3}(?:,\d{3})+|\d+)"
DECIMAL = r"(?:\d+(?:[.·]\d+)?|[.·]\d+)"
PERCENT = rf"\(\s*{DECIMAL}\s*%\s*\)"
COUNTS = re.compile(rf"(?<![\w.,/%+−-])(?P<e>{INTEGER})\s*(?:{PERCENT}\s*)?"
                    rf"(?:of\s+|/\s*)(?P<n>{INTEGER})(?![\w.,/%])", re.I)
RATIO = re.compile(
    rf"\b(?P<measure>hazard\s+ratio|odds\s+ratio|risk\s+ratio|HR|OR|RR)\s*"
    rf"(?:was\s+|of\s+|[=:]\s*)?(?P<effect>{DECIMAL})(?![\d.])\s*[,;(]?\s*"
    rf"(?:two[- ]sided\s+)?95\s*%\s*(?:CI|confidence\s+interval)\s*[:=,]?\s*[([]?\s*"
    rf"(?P<lower>{DECIMAL})\s*(?:to|[-–—,])\s*(?P<upper>{DECIMAL})(?![\d.])", re.I)
SUBGROUP = re.compile(r"\b(?:among\s+patients\s+aged|in\s+the\s+subgroup|in\s+women|"
                      r"subgroups?|among\s+(?:women|men)|in\s+men)\b", re.I)
POPULATION = re.compile(r"\b(?:modified(?:[- ]intention[- ]to[- ]treat)?|"
                        r"intention[- ]to[- ]treat|per[- ]protocol|safety)\b", re.I)
TIME = re.compile(r"\b(?:(?:at\s+)?\d+\s+(?:days?|weeks?|months?|years?)|"
                  r"(?:day|week|month|year)\s+\d+|in[- ]hospital)\b", re.I)


def _sentences(text):
    protected = set()
    for m in re.finditer(r"\bet\s+al\.|\bvs\.|\bi\.e\.|\bFig\.|\bTable\.", text, re.I):
        protected.update(range(m.start(), m.end()))
    start = 0
    for m in re.finditer(r"[.!?](?=\s|$)", text):
        if m.start() in protected:
            continue
        chunk = text[start:m.end()]
        if chunk.strip():
            yield start + len(chunk) - len(chunk.lstrip()), chunk.strip()
        start = m.end()
    if text[start:].strip():
        yield start + len(text[start:]) - len(text[start:].lstrip()), text[start:].strip()


def _term(text, terms):
    normalized = fold(text)
    return next((t for t in terms if t and re.search(
        r"(?<!\w)" + re.escape(fold(t)) + r"(?!\w)", normalized)
        and not matches_only_as_subtype(fold(t), normalized)), None)


def _arm(fragment, cfg):
    # Inspect the FIRST group cue, including unknown groups. Never skip an
    # unknown nearest group in favour of a later recognisable intervention.
    cue = re.search(r"\b(?:in\s+(?:the\s+)?|with\s+|receiving\s+)"
                    r"(?P<pre>[^,;:.!?]+)|\b(?P<post>[\w-]+(?:\s+[\w-]+){0,4})\s+arm\b",
                    fragment, re.I)
    if not cue:
        return None
    phrase = cue.group("pre") or cue.group("post")
    phrase = re.split(r"\b(?:group|arm|and|versus|vs|compared|had|were|died)\b", phrase, maxsplit=1,
                      flags=re.I)[0].strip()
    t = _term(phrase, cfg.get("intervention_terms") or [])
    c = _term(phrase, list(cfg.get("comparator_terms") or []) + ["placebo", "usual care", "standard care"])
    if bool(t) == bool(c):
        return None
    return ("t", t) if t else ("c", c)


def sentence_candidates(text, cfg):
    """Return printed tuples and bounded metadata, never the sentence itself."""
    result, previous = [], ""
    terms = outcome_row_terms(cfg)
    for offset, sentence in _sentences(text or ""):
        outcome = _term(sentence, terms)
        pop = POPULATION.search(sentence) or POPULATION.search(previous)
        previous = sentence
        if not outcome or SUBGROUP.search(sentence):
            continue
        time = TIME.search(sentence)
        flags = re.findall(r"\b(?:primary|secondary)\b", sentence, re.I)
        meta = dict(outcome_term=outcome, timepoint_text=time.group(0)[:40] if time else None,
                    population_text=pop.group(0)[:40] if pop else None,
                    flag=",".join(sorted(set(f.lower() for f in flags))) or None,
                    offset=offset, sentence_sha256=hashlib.sha256(sentence.encode("utf-8")).hexdigest())
        counts = list(COUNTS.finditer(sentence))
        # Adjacent pairs only: never cross an unattributed or extra arm count.
        for i in range(0, len(counts) - 1, 2):
            pair = counts[i:i + 2]
            mapped = {}
            for j, m in enumerate(pair, start=i):
                end = counts[j + 1].start() if j + 1 < len(counts) else len(sentence)
                arm = _arm(sentence[m.end():end], cfg)
                e, n = (int(m.group(k).replace(",", "")) for k in ("e", "n"))
                if arm and 0 <= e <= n and n > 0:
                    side, term = arm
                    mapped[side] = (e, n, term)
            if set(mapped) == {"t", "c"}:
                candidate = dict(meta)
                for side, (e, n, term) in mapped.items():
                    candidate.update({f"events_{side}": e, f"n_{side}": n, f"arm_{side}_term": term})
                result.append(candidate)
        if re.search(r"\b(?:one|1)[- ]sided\b|\b(?:90|98)\s*%\s*(?:CI|confidence)", sentence, re.I):
            continue
        ratios = list(RATIO.finditer(sentence))
        for i, m in enumerate(ratios):
            end = ratios[i + 1].start() if i + 1 < len(ratios) else len(sentence)
            contrast = re.split(r"\b(?:versus|vs\.?|compared\s+(?:with|to))\s+",
                                sentence[m.end():end], maxsplit=1, flags=re.I)
            if len(contrast) != 2:
                # A named contrast may precede its estimate. Bound it by the
                # previous ratio rather than borrowing from another result.
                start = ratios[i - 1].end() if i else 0
                contrast = re.split(r"\b(?:versus|vs\.?|compared\s+(?:with|to))\s+",
                                    sentence[start:m.start()], maxsplit=1, flags=re.I)
            if len(contrast) != 2:
                continue
            left, right = _arm(contrast[0], cfg), _arm("with " + contrast[1], cfg)
            # A reversed contrast cannot be inverted: only printed values leave.
            if not left or not right or (left[0], right[0]) != ("t", "c"):
                continue
            values = {k: float(m.group(k).replace("·", ".")) for k in ("effect", "lower", "upper")}
            if not 0 < values["lower"] <= values["effect"] <= values["upper"] or values["lower"] == values["upper"]:
                continue
            measure = m.group("measure").lower()
            measure = {"hazard ratio": "HR", "odds ratio": "OR", "risk ratio": "RR"}.get(
                re.sub(r"\s+", " ", measure), measure.upper())
            result.append(dict(meta, measure=measure, **values, arm_t_term=left[1], arm_c_term=right[1]))
    return result


def census_summary(candidates):
    """No quotations or result numbers; text-named fields denote presence only."""
    return dict(n_candidates=len(candidates), has_counts=any("events_t" in c for c in candidates),
                has_effect=any("effect" in c for c in candidates),
                timepoint_text=any(c["timepoint_text"] is not None for c in candidates),
                population_text=any(c["population_text"] is not None for c in candidates),
                ambiguous=len(candidates) > 1)


def _identifier(value):
    # Metadata only. This injective escape also prevents trial-year digits from
    # violating the census's no-digits-except-candidate-counts contract.
    words = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
    return "".join("~" + words[int(c)] + "~" if c in "0123456789" else "~~" if c == "~" else c
                   for c in value)


def run_census(labels):
    import g1_table_failure_diag as diag
    import g1_registry_fill as rf
    import g1_tracker as gt

    if not isinstance(labels, list) or any(not isinstance(r, dict) or
            not isinstance(r.get("label"), str) or not isinstance(r.get("slug"), str) or
            not re.fullmatch(r"[A-Za-z0-9_-]+", r["slug"]) for r in labels):
        raise ValueError("INVALID_LABELS")
    selected = {(r["slug"], r["label"]) for r in labels}
    base = ROOT / "outputs" / "k_gap"
    missing, configs = set(), {}
    for slug in sorted({s for s, _ in selected}):
        tracker = json.loads((base / "g1" / (slug + ".json")).read_text(encoding="utf-8"))
        missing.update((slug, r["label"]) for r in tracker["trials"] if not r.get("scope_difference")
                       and not r.get("in_our_pool") and (not gt.is_matched(r) or r.get("route") == "SECONDARY_SINGLE"))
        configs[slug] = rf.config(slug)
    collected, seen = {}, set()
    for suffix, folder in (("", "phase3"), ("_REGISTERED", "phase3_registered"),
                           ("_COMPANIONS", "phase3_companions")):
        canonical = base / "registry_fill" / ("PHASE3_OPEN_CENSUS" + suffix + ".json")
        paths = [canonical] if canonical.is_file() else [base / "registry_fill" / folder / (s + ".json")
                                                        for s in sorted(configs)]
        for path in paths:
            if not path.is_file():
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            for row in doc["rows"]:
                key = (row.get("slug") or doc.get("slug"), row["label"])
                if key not in selected or key not in missing:
                    continue
                text, _ = diag._held_text(row)
                if not text.strip():
                    continue
                digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                if (key, digest) in seen:
                    continue
                seen.add((key, digest))
                collected.setdefault(key, []).extend(sentence_candidates(text, configs[key[0]]))
    rows = [dict(slug=_identifier(s), label=_identifier(l), **census_summary(c))
            for (s, l), c in sorted(collected.items())]
    output = base / "registry_fill" / "SENTENCE_CENSUS.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"rows": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("topic | trials | candidates | ambiguous")
    for slug in sorted({_identifier(s) for s, _ in selected}):
        group = [r for r in rows if r["slug"] == slug]
        print(slug, len(group), sum(r["n_candidates"] for r in group), sum(r["ambiguous"] for r in group), sep=" | ")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("census").add_argument("--labels", required=True)
    args = parser.parse_args(argv)
    try:
        labels = json.loads(args.labels) if args.labels.lstrip().startswith("[") else json.loads(
            Path(args.labels).read_text(encoding="utf-8"))
        return run_census(labels)
    except Exception:
        # Never expose exceptions which might contain held source material.
        print("SENTENCE_CENSUS_FAILED", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
