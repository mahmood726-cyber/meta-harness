"""D12 COUNTS_FOR_MATCHING (Mahmood, 8 Oct 2026: "approve d12"; registry/g1_decisions.json).

A trial's OWN typed per-arm counts -- AACT posted results, or a held primary span, verbatim -- may be used for the G1
same-trial comparison on the COMPARATOR'S measure. The served pool keeps its registered estimand; nothing served changes.

registry/d12_counts_for_matching.json holds the count bindings (imported verbatim from the binding lane's staged file,
with its branch, commit and sha256). A binding is USED only when it verifies at build time:
  K1 (AACT)  the AACT snapshot's own rows for that NCT + outcome id: the two groups' participant counts (outcome_counts,
             scope Measure) and their event counts (outcome_measurements, the binding's classification) are exactly the
             binding's (events_t, n_t) and (events_c, n_c), each pair from ONE group. No snapshot -> not verifiable -> unused.
  K2 (TEXT)  the span is verbatim in the trial's held abstract (cache/<slug>/records.json); both event counts are number
             tokens of the span; both arm Ns are tokens of the span, or (n_source 'abstract') of the held abstract, or
             (n_source 'AACT ... outcome <id> ...') the AACT outcome_counts of that outcome.
A binding that does not verify is never used, and the reason is recorded.

THE SEPARATION THAT D12 RESTS ON: this module is read only by scripts/g1_tracker.py's same-trials comparison. Nothing
that builds or serves a pool (harness/, scripts/build_served_pool_additions.py, scripts/g1_served_pool_notices.py)
imports it or reads its registry file (tests/test_g1_d12.py plants this), and the tracker never writes these counts into
a trial's our_value.

    python scripts/g1_d12.py import <bindings_counts.json> --ref <branch@commit>   -> registry/d12_counts_for_matching.json
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "registry", "d12_counts_for_matching.json")
DECISION = "D12-COUNTS_FOR_MATCHING"
PROVENANCE = "D12_OWN_COUNTS"
_VALUE_KEYS = ("events_t", "n_t", "events_c", "n_c")


def load(path=None):
    p = path or REG
    if not os.path.exists(p):
        # the path as given: relpath across drives raises on Windows
        raise FileNotFoundError(f"D12 count bindings not found: {p} (committed file missing)")
    return json.load(open(p, encoding="utf-8"))


def int_tokens(text):
    """Every whole number in the text as an int, digits bounded by non-digits ('1,274' and '1 274' read as 1274; a
    decimal's parts are not whole numbers). Plain scan, no regex."""
    out, s, i = set(), str(text or ""), 0
    while i < len(s):
        if not s[i].isdigit() or (i > 0 and s[i - 1].isdigit()):
            i += 1
            continue
        j, digits = i, ""
        while j < len(s):
            if s[j].isdigit():
                digits += s[j]
                j += 1
                continue
            grp = s[j + 1:j + 4]
            if (s[j] in ",  " and len(grp) == 3 and grp.isdigit()
                    and (j + 4 == len(s) or not s[j + 4].isdigit())):
                j += 1       # a thousands separator (comma or thin space) followed by exactly three digits
                continue
            break
        decimal = (i > 0 and s[i - 1] == ".") or (j < len(s) - 1 and s[j] == "." and s[j + 1].isdigit())
        if not decimal:
            out.add(int(digits))
        i = j
    return out


def _held_abstract(slug, pmid):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return ""
    for r in json.load(open(p, encoding="utf-8")).get("records", []):
        if str(r.get("id")) == str(pmid):
            return r.get("abstract") or ""
    return ""


def _aact_source(source):
    """(nct, outcome_id) from 'AACT ... NCT######## outcome ########', else (None, None). Plain token scan."""
    toks = str(source or "").replace("(", " ").replace(")", " ").split()
    nct = next((t for t in toks if t.startswith("NCT") and len(t) == 11 and t[3:].isdigit()), None)
    oid = next((toks[i + 1] for i, t in enumerate(toks[:-1]) if t == "outcome" and toks[i + 1].isdigit()), None)
    return (nct, oid) if str(source or "").startswith("AACT") or "AACT" in toks else (None, None)


class Aact:
    """The few AACT rows D12 needs, read once per build from a snapshot directory."""

    def __init__(self, snap):
        self.snap = snap
        self._counts, self._meas = None, None

    def _scan(self, name, want_outcomes):
        p = os.path.join(self.snap, name)
        csv.field_size_limit(10 ** 9)
        rows = []
        with open(p, encoding="utf-8", newline="") as f:
            rd = csv.DictReader(f, delimiter="|")
            need = {"nct_id", "outcome_id", "ctgov_group_code"}
            if not need <= set(rd.fieldnames or []):
                raise ValueError(f"{p}: missing columns {sorted(need - set(rd.fieldnames or []))}")
            for r in rd:
                if r["outcome_id"] in want_outcomes:
                    rows.append(r)
        return rows

    def load(self, outcome_ids):
        ids = set(outcome_ids)
        self._counts = self._scan("outcome_counts.txt", ids)
        self._meas = self._scan("outcome_measurements.txt", ids)
        self._groups = self._scan("result_groups.txt", ids)

    def group_title(self, nct, oid, code):
        return next((r.get("title") for r in self._groups
                     if r["nct_id"] == nct and r["outcome_id"] == oid and r["ctgov_group_code"] == code), None)

    def arms(self, nct, oid, classification):
        """{group code: (events, participants)} for that NCT + outcome + classification ('unclassified' = empty)."""
        cls = "" if classification in (None, "", "unclassified") else classification
        n = {r["ctgov_group_code"]: r["count"] for r in self._counts
             if r["nct_id"] == nct and r["outcome_id"] == oid and r.get("scope") == "Measure"}
        e = {r["ctgov_group_code"]: r["param_value"] for r in self._meas
             if r["nct_id"] == nct and r["outcome_id"] == oid and (r.get("classification") or "") == cls}
        out = {}
        for g in set(n) & set(e):
            try:
                out[g] = (int(float(e[g])), int(float(n[g])))
            except ValueError:
                continue
        return out


def verify(b, aact=None):
    """(True, basis) when the binding verifies under D12, else (False, why)."""
    v = b.get("values") or {}
    if b.get("tuple_kind") != "COUNTS" or not b.get("own_tuple") or any(not isinstance(v.get(k), int) for k in _VALUE_KEYS):
        return False, "NOT_AN_OWN_COUNTS_TUPLE"
    et, nt, ec, nc = (v[k] for k in _VALUE_KEYS)
    if not (0 <= et <= nt and 0 <= ec <= nc and nt > 0 and nc > 0):
        return False, "IMPOSSIBLE_COUNTS"
    rule = b.get("rule")
    if rule == "K1":
        nct, oid = _aact_source(b.get("source"))
        if not nct or not oid or nct not in (b.get("ncts") or []):
            return False, "K1_SOURCE_NOT_AN_AACT_OUTCOME_OF_THIS_TRIAL"
        if aact is None:
            return False, "K1_NOT_VERIFIABLE:NO_AACT_SNAPSHOT"
        arms = aact.arms(nct, oid, b.get("classification"))
        pairs = sorted(arms.values())
        if len(arms) != 2 or pairs != sorted([(et, nt), (ec, nc)]):
            return False, f"K1_AACT_ROWS_DIFFER:{sorted(arms.items())}"
        # the span names each (events, N) pair with ITS OWN AACT group title: which arm is ours is the binding's mapping,
        # and the span must state it exactly as AACT does (a swapped span never verifies)
        span = b.get("span") or ""
        for g, (e_, n_) in arms.items():
            title = aact.group_title(nct, oid, g)
            if not title or f"{title}: {e_} of {n_} participants" not in span:
                return False, f"K1_SPAN_DOES_NOT_STATE_AACT_GROUP:{g}"
        return True, f"K1: AACT {os.path.basename(aact.snap)} {nct} outcome {oid} ({b.get('classification')}): " \
                     f"groups {sorted(arms.items())}"
    if rule == "K2":
        ab = _held_abstract(b.get("slug"), b.get("pmid"))
        span = b.get("span") or ""
        if not ab or not span or span not in ab:
            return False, "K2_SPAN_NOT_VERBATIM_IN_HELD_ABSTRACT"
        st = int_tokens(span)
        if et not in st or ec not in st:
            return False, "K2_EVENT_COUNTS_NOT_IN_SPAN"
        if nt in st and nc in st:
            return True, f"K2: PMID {b['pmid']} held abstract span (events and Ns in the span)"
        ns = str(b.get("n_source") or "")
        if ns == "abstract":
            at = int_tokens(ab)
            if nt in at and nc in at:
                return True, f"K2: PMID {b['pmid']} held abstract span (events); Ns stated in the same held abstract"
            return False, "K2_NS_NOT_IN_HELD_ABSTRACT"
        nct, oid = _aact_source(ns)
        if nct and oid and nct in (b.get("ncts") or []):
            if aact is None:
                return False, "K2_N_NOT_VERIFIABLE:NO_AACT_SNAPSHOT"
            n = {r["ctgov_group_code"]: r["count"] for r in aact._counts
                 if r["nct_id"] == nct and r["outcome_id"] == oid and r.get("scope") == "Measure"}
            if sorted(int(float(x)) for x in n.values()) == sorted([nt, nc]) and len(n) == 2:
                return True, f"K2: PMID {b['pmid']} held abstract span (events); Ns AACT {nct} outcome {oid} counts"
            return False, f"K2_AACT_NS_DIFFER:{sorted(n.items())}"
        return False, "K2_NS_UNSOURCED"
    return False, f"RULE_NOT_UNDER_D12:{rule}"


_AACT_CACHE = {}


def for_topic(slug, trials, snap=None, reg=None):
    """{trial label: {'row': counts dict, 'basis': ..., 'binding': ...}} for this topic's MATCHED trials whose identity
    (family 'PMID n' or an NCT) is the binding's own, verified now; plus [refusals]. Identity, never the label, joins."""
    reg = load() if reg is None else reg
    mine = [b for b in reg.get("bindings") or [] if b.get("slug") == slug]
    if not mine:
        return {}, []
    snap = snap if snap is not None else (os.environ.get("AACT_SNAPSHOT") or os.environ.get("AACT_DIR"))
    aact = None
    if snap and os.path.isdir(snap):
        ids = set()
        for b in mine:
            for src in (b.get("source"), b.get("n_source")):
                _n, o = _aact_source(src)
                if o:
                    ids.add(o)
        key = (os.path.abspath(snap), frozenset(ids))
        if key not in _AACT_CACHE:
            a = Aact(snap)
            a.load(ids)
            _AACT_CACHE[key] = a
        aact = _AACT_CACHE[key]
    out, refused = {}, []
    for b in mine:
        ids = {f"PMID {b.get('pmid')}"} | set(b.get("ncts") or [])
        xs = [x for x in trials if x.get("in_our_pool") and str(x.get("family")) in ids]
        if len(xs) != 1:
            refused.append({"trial": b.get("label"), "why": f"IDENTITY:{len(xs)}_MATCHED_TRIALS"})
            continue
        ok, why = verify(b, aact)
        if not ok:
            refused.append({"trial": b.get("label"), "why": why})
            continue
        out[xs[0]["label"]] = {"row": {k: b["values"][k] for k in _VALUE_KEYS}, "basis": why,
                               "source": b.get("source"), "span": b.get("span"), "rule": b.get("rule")}
    return out, refused


def import_bindings(src_path, ref):
    raw = open(src_path, "rb").read()
    d = json.loads(raw.decode("utf-8"))
    keep = [b for b in d.get("bindings") or [] if b.get("own_tuple") and b.get("tuple_kind") == "COUNTS"]
    out = {"decision": DECISION,
           "rule": "Own-trial per-arm counts for the G1 same-trial comparison ONLY (scripts/g1_d12.py); never served.",
           "imported_from": {"ref": ref, "path": "outputs/k_gap/g1_binding/bindings_counts.json",
                             "sha256": hashlib.sha256(raw).hexdigest(), "bindings_kept": len(keep),
                             "not_bound": [{k: x.get(k) for k in ("slug", "label", "pmid", "why")}
                                           for x in d.get("not_bound") or []]},
           "bindings": keep}
    with open(REG, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if a[:1] == ["import"] and "--ref" in a:
        r = import_bindings(a[1], a[a.index("--ref") + 1])
        print(f"wrote {os.path.relpath(REG, ROOT)}: {len(r['bindings'])} bindings from {r['imported_from']['ref']}")
    else:
        print(__doc__)
