"""Radius of a candidate regex change, measured by re-running harness.extract.extract_trial -- the served producer's own
entry point (harness/pipeline.py:1197 abstract, :1235 PMC full text) -- on every cached record for every declared
outcome of its topic, BEFORE and AFTER the change is installed in-process. Nothing is written except the report.

  python -m regex_layer.radius refuse_partial   -> outputs/regex_layer/RADIUS_refuse_partial.json

A differing output is radius. Each is marked SERVED when the record's id is a trial on the committed page
(docs/reviews/<slug>/review.json), otherwise UNSERVED (screened out, or not bound to an arm). The question it answers:
would this change move a served number (then it is held for Mahmood), or only refuse / alter unserved extractions.
"""
from __future__ import annotations

import contextlib
import json
import os
import re
import sys
from pathlib import Path

from harness import extract
from harness import whole_numbers as wn
from regex_layer.partial import RefusePartial
from regex_layer.specs import SPECS

ROOT = Path(__file__).resolve().parents[1]
# data (topics/, cache/, docs/reviews/) may be read from another tree, so a PATCHED harness package can be measured
# against the committed data without a second full checkout; the harness imported is whatever sys.path resolves
DATA = Path(os.environ.get("REGEX_LAYER_DATA_ROOT") or ROOT)


@contextlib.contextmanager
def refuse_partial():
    names = [n for n, s in SPECS.items() if s["kind"] == "extractor"]
    old = {n: getattr(extract, n) for n in names}
    try:
        for n in names:
            setattr(extract, n, RefusePartial(old[n]))
        yield
    finally:
        for n, rx in old.items():
            setattr(extract, n, rx)


class _Dead:
    groups = 0

    def finditer(self, *a):
        return iter(())

    def search(self, *a):
        return None

    def findall(self, *a):
        return []

    def match(self, *a):
        return None


@contextlib.contextmanager
def plant_dead_extractors():
    """PLANT: every extractor matches nothing. Its radius must be large, or the radius tool measures nothing."""
    names = [n for n, s in SPECS.items() if s["kind"] == "extractor"]
    old = {n: getattr(extract, n) for n in names}
    try:
        for n in names:
            setattr(extract, n, _Dead())
        yield
    finally:
        for n, rx in old.items():
            setattr(extract, n, rx)


@contextlib.contextmanager
def _swap(name: str, rx: re.Pattern):
    old = getattr(extract, name)
    try:
        setattr(extract, name, rx)
        yield
    finally:
        setattr(extract, name, old)


# R4 candidate fixes, each measured on its own before it may enter the pinned patch
NEQ_BOUNDARY = re.compile(r"(?<![A-Za-z])n\s*=\s*(\d+)", re.I)      # 'interactio[n = 0].92' is not n = 0
DENOM_EACH_FIXED = re.compile(r"(\d+)\s+(?:patients?\s+)?(?:were\s+)?(?:randomly\s+)?(?:assigned|allocated|randomi[sz]ed)\s+to\s+each",
                              re.I)                                  # RX-D1: 'patients were randomly assigned to each'


def neq_boundary():
    return _swap("_NEQ", NEQ_BOUNDARY)


def denom_each_fix():
    return _swap("_DENOM_EACH", DENOM_EACH_FIXED)


# R4 candidates of outputs/regex_layer/R4_CANDIDATE_FIXES.md, compiled as written there. The doc elides the number-word
# list with '…' ("one lookbehind per number word", "one|two|…|twenty"); it is expanded here to exactly the words
# harness.extract._WORDNUM maps (one..twenty), in that order, and nothing else is added. A multi-line pattern in the doc
# is its lines joined with the layout indentation removed (none of these patterns is compiled with re.X).
_NUMBER_WORDS = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
                 "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty")
_OF_GUARD = r"(?<!\d of )" + "".join(rf"(?<!(?i:{w}) of )" for w in _NUMBER_WORDS)
FIX_ARMP = re.compile(
    r"(?<![/\w.-])" + _OF_GUARD + r"(\d+|(?i:" + "|".join(_NUMBER_WORDS) + r"))\s+"
    r"(?:(?:hospital\s+)?(?:patients?|participants?|cases?|subjects?|deaths?|events?|hospitali[sz]ations?|admissions?|women|men)\s*)?"
    r"[\(\[]\s*(\d+(?:\.\d+)?)\s*%\s*[\)\]]")
FIX_K = re.compile(
    r"(?<![\w-])(\d+|(?:(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-)?(?:one|two|three|four|five|six|seven|eight|nine)"
    r"|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
    r"\s+(?:(?:eligible|included|additional|large|larger|small|smaller|published|separate|individual)\s+)?"
    r"(?:randomi[sz]ed\s+(?:controlled\s+)?trials|controlled\s+(?:clinical\s+)?trials|RCTs)", re.I)
FIX_SUBGROUP = re.compile(
    r"\bper[-\s]?protocol\b|\bpost[-\s]?hoc\b|\bsubgroups?\b|\bsensitivity analys[ie]s\b|\bas[-\s]?treated\b|\blowest in\b|"
    r"\bhighest in\b|\bamong those (?:with|who)\b|\brestricted to\b|\bexploratory analys[ie]s\b", re.I)
FIX_ANCHOR_RX = re.compile(
    r"\b(?:co-?primary|primary)\s+"
    r"(?:composite\s+|study\s+|efficacy\s+|main\s+|clinical\s+)*"
    r"(?:outcome|end[\s-]?point)s?\b", re.I)
FIX_RECURRENT_PERSONTIME = re.compile(
    r"(?<![\d.,])\d[\d,]*\s+times\b(?!\s+(?:more|less|higher|lower|greater|smaller|larger|as|stronger|weaker|a|an|per|daily|weekly|monthly|each|every)\b)"
    r"|per\s+(?:1[,\s]?000\s+|100\s+|10[,\s]?000\s+)?(?:patient|person)[-\s]?(?:years?|months?|cycles?|days?)"
    r"|\btotal\s+(?:number\s+of\s+)?[\w\s]{0,30}?(?:hospitali[sz]ation|event)s\b"
    r"|recurrent[-\s](?:events?|hospitali[sz]ations?|admissions?|exacerbations?|episodes?)\b"
    r"|\bnumber\s+of\s+(?:recurrences|exacerbations|episodes|relapses)\b", re.I)
# _K's candidate needs the tens and the hyphenated compounds in _WORDNUM ('fifty-five' -> 55), per the doc's "Downstream"
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_UNITS = {w: i for i, w in enumerate(("one", "two", "three", "four", "five", "six", "seven", "eight", "nine"), 1)}
WORDNUM_EXTENDED = {**extract._WORDNUM, **_TENS,
                    **{f"{t}-{u}": tv + uv for t, tv in _TENS.items() for u, uv in _UNITS.items()}}
# RX-X5: harness/whole_numbers.py SEP += U+2007 (figure space) and U+2008 (punctuation space)
SEP_FIXED = wn.SEP + "  "


@contextlib.contextmanager
def _swap_many(obj, pairs: dict):
    old = {k: getattr(obj, k) for k in pairs}
    try:
        for k, v in pairs.items():
            setattr(obj, k, v)
        yield
    finally:
        for k, v in old.items():
            setattr(obj, k, v)


def fix_armp():
    return _swap("_ARMP", wn.whole_numbers(FIX_ARMP))     # wrapped as served: only the regex changes


class _WordCountMatch:
    """A match whose count group (1) reads a number word as its digits -- the doc's stated downstream requirement for
    RX-X2 ('_arm_counts does int(m.group(1)), so a word count needs the _WORDNUM mapping'), emulated at the match so that
    harness/extract.py is not edited. Everything else delegates to the real match."""

    def __init__(self, m):
        self._m = m

    def group(self, *g):
        if g in ((1,),) and not self._m.group(1).isdigit():
            return str(extract._WORDNUM[self._m.group(1).lower()])
        return self._m.group(*g)

    def __getattr__(self, a):
        return getattr(self._m, a)


class _WordCountArmp(wn.WholeNumbers):
    def finditer(self, s, *a):
        return (_WordCountMatch(m) for m in super().finditer(s, *a))


def fix_armp_wordnum():
    """SUPPLEMENTARY (not the candidate as written): the _ARMP candidate plus the _WORDNUM mapping its doc says RX-X2
    needs downstream. fix_armp alone crashes _arm_counts on every word count."""
    return _swap("_ARMP", _WordCountArmp(FIX_ARMP))


def fix_k():
    """_K acts through _parse_k (extract_meta), not extract_trial -- scripts/radius_k.py measures its served radius;
    under extract_trial this should (and is expected to) show 0."""
    return _swap_many(extract, {"_K": wn.whole_numbers(FIX_K), "_WORDNUM": WORDNUM_EXTENDED})


def fix_subgroup():
    return _swap("_SUBGROUP", FIX_SUBGROUP)


def fix_anchor_rx():
    return _swap("_ANCHOR_RX", FIX_ANCHOR_RX)


def fix_recurrent_persontime():
    return _swap("_RECURRENT_PERSONTIME", FIX_RECURRENT_PERSONTIME)


def fix_whole_numbers_sep():
    """fragment_groups reads the module globals _GROUPED_BEFORE/_GROUPED_AFTER, so recompiling them with the extended SEP
    changes every wrapped pattern at once (the eleven in extract.py), exactly as editing SEP would."""
    return _swap_many(wn, {"SEP": SEP_FIXED, "_GROUPED_BEFORE": re.compile(rf"\d[{SEP_FIXED}]$"),
                           "_GROUPED_AFTER": re.compile(rf"^[{SEP_FIXED}]\d{{3}}(?!\d)")})


CHANGES = {"refuse_partial": refuse_partial, "plant_dead_extractors": plant_dead_extractors,
           "neq_boundary": neq_boundary, "denom_each_fix": denom_each_fix,
           "fix_armp": fix_armp, "fix_armp_wordnum": fix_armp_wordnum, "fix_k": fix_k, "fix_subgroup": fix_subgroup, "fix_anchor_rx": fix_anchor_rx,
           "fix_recurrent_persontime": fix_recurrent_persontime, "fix_whole_numbers_sep": fix_whole_numbers_sep}

# R4 AMBIGUITY: one refuse-on-disagreement change per site of regex_layer/ambiguity.py (python -m regex_layer.radius
# r4_<site>). _parse_k / extract_meta / comparator_effect / composite_heterogeneity are not reached by extract_trial;
# scripts/radius_r4_comparator.py measures those served paths.
from regex_layer import ambiguity as _amb  # noqa: E402

for _site in _amb.SITES:
    CHANGES[f"r4_{_site}"] = (lambda s: (lambda: _amb.change(s)))(_site)


def outcomes(cfg: dict) -> list[dict]:
    out = []
    for key in ("primary_outcome", "secondary_outcomes", "harm_outcomes"):
        v = cfg.get(key)
        for o in (v if isinstance(v, list) else [v] if v else []):
            if isinstance(o, dict) and o.get("keywords"):
                out.append(o)
    return out


def served_keys(slug: str) -> set[tuple[str, str, str]]:
    """(record id, source, outcome name) of every trial row the committed page POOLS (outcomes[*].trials[*]) -- not every
    id the page mentions (screening rows are ids too, and are not served numbers)."""
    p = DATA / "docs" / "reviews" / slug / "review.json"
    if not p.exists():
        return set()
    out = set()
    for o in json.loads(p.read_text(encoding="utf-8")).get("outcomes") or []:
        for t in o.get("trials") or []:
            rid = re.sub(r"^(?:PMID|NCT)\s+", "", str(t.get("id") or ""))
            out.add((rid, t.get("provenance") or "", o.get("name") or ""))
    return out


def texts(slug: str, rec: dict):
    yield "abstract", rec.get("abstract") or ""
    ft = DATA / "cache" / slug / f"ft_{rec.get('id')}.txt"
    if ft.exists():
        yield "pmc_fulltext", ft.read_text(encoding="utf-8", errors="replace")


def run_all(slug, cfg, recs):
    interv = cfg.get("intervention_terms", ["colchicine"])
    comp = cfg.get("comparator_terms", ["placebo", "control"])
    res = {}
    for rec in recs:
        for src, text in texts(slug, rec):
            if not text:
                continue
            for o in outcomes(cfg):
                dc = extract.declared_is_composite(o.get("name", ""))
                try:
                    ex = extract.extract_trial(text, o["keywords"], interv, comp, declared_composite=dc,
                                               estimand=o.get("estimand"))
                except Exception as exc:  # a crash is an output too
                    ex = {"CRASH": repr(exc)}
                res[(str(rec.get("id")), src, o.get("name"))] = json.dumps(ex, sort_keys=True, default=str)
    return res


def main(change: str, only: str | None = None) -> int:
    rows, n, served_n, served_reached, unreached = [], 0, 0, 0, []
    for cfgp in sorted((DATA / "topics").glob("*.json")):
        if only and cfgp.stem != only:
            continue
        slug = cfgp.stem
        rp = DATA / "cache" / slug / "records.json"
        if not rp.exists():
            continue
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        recs = json.loads(rp.read_text(encoding="utf-8")).get("records") or []
        before = run_all(slug, cfg, recs)
        with CHANGES[change]():
            after = run_all(slug, cfg, recs)
        served = served_keys(slug)
        n += len(before)
        served_n += len(served)
        reached = served & set(before)
        served_reached += len(reached)
        # served rows whose provenance is not an extract_trial output (hand-verified, ctgov_results, published rate...)
        # are not produced by this producer; they are listed by provenance, never folded into "no radius"
        unreached += [list(k) + [slug] for k in sorted(served - reached)]
        for k in sorted(before):
            if before[k] != after.get(k):
                rows.append({"slug": slug, "id": k[0], "source": k[1], "outcome": k[2],
                             "served": k in served, "before": json.loads(before[k]), "after": json.loads(after[k])})
        print(f"{slug}: {len(before)} extractions, {sum(1 for r in rows if r['slug'] == slug)} differ", flush=True)
    res = {"change": change, "extractions": n, "differ": len(rows), "differ_served": sum(r["served"] for r in rows),
           "of": f"{len(rows)} of {n}",
           # a served row the re-run never reached cannot show up as radius -- counted, never assumed zero
           "served_rows_reached": f"{served_reached} of {served_n}", "served_rows_not_reached": unreached,
           "served_rows_not_reached_by_provenance": {p: sum(1 for u in unreached if u[1] == p)
                                                     for p in sorted({u[1] for u in unreached})},
           "rows": rows}
    out = ROOT / "outputs" / "regex_layer" / f"RADIUS_{change}.json"
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(f"RADIUS {change}: {res['of']} extractions differ; served {res['differ_served']}; "
          f"served rows reached {res['served_rows_reached']}")
    return 0


def snapshot(path: str) -> int:
    """Every extraction of the CURRENT source, keyed "<slug>|<id>|<source>|<outcome>": a source edit (R1) is compared by
    diffing two snapshots taken on the two trees."""
    res = {}
    for cfgp in sorted((DATA / "topics").glob("*.json")):
        rp = DATA / "cache" / cfgp.stem / "records.json"
        if not rp.exists():
            continue
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        for k, v in run_all(cfgp.stem, cfg, json.loads(rp.read_text(encoding="utf-8")).get("records") or []).items():
            res["|".join((cfgp.stem,) + k)] = v
    Path(path).write_text(json.dumps(res, sort_keys=True, indent=0) + "\n", encoding="utf-8")
    print(f"snapshot: {len(res)} extractions -> {path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "snapshot":
        raise SystemExit(snapshot(sys.argv[2]))
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "refuse_partial", sys.argv[2] if len(sys.argv) > 2 else None))
