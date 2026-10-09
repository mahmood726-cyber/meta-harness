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

    python scripts/g1_d12.py import <bindings_counts.json> --ref <branch@commit> --audit <audit_staged_counts.json>
        --audit-ref <branch@commit>   -> registry/d12_counts_for_matching.json
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


def _isd(c):
    """ASCII digits only: superscripts and other scripts are digits to str.isdigit() but not to int() (codex d12-r5 #4)."""
    return bool(c) and all(ch in "0123456789" for ch in c)


def int_tokens(text):
    """Every whole number in the text as an int, digits bounded by non-digits ('1,274' and '1 274' read as 1274; a
    decimal's parts are not whole numbers). Plain scan, no regex."""
    out, s, i = set(), str(text or ""), 0
    while i < len(s):
        if not _isd(s[i]) or (i > 0 and _isd(s[i - 1])):
            i += 1
            continue
        j, digits = i, ""
        while j < len(s):
            if _isd(s[j]):
                digits += s[j]
                j += 1
                continue
            grp = s[j + 1:j + 4]
            if (s[j] in ",  " and len(grp) == 3 and _isd(grp)
                    and (j + 4 == len(s) or not _isd(s[j + 4]))):
                j += 1       # a thousands separator (comma or thin space) followed by exactly three digits
                continue
            break
        decimal = (i > 0 and s[i - 1] == ".") or (j < len(s) - 1 and s[j] == "." and _isd(s[j + 1]))
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


def _held_nct(slug, pmid):
    p = os.path.join(ROOT, "cache", slug, "records.json")
    if not os.path.exists(p):
        return None
    for r in json.load(open(p, encoding="utf-8")).get("records", []):
        if str(r.get("id")) == str(pmid):
            return r.get("nct") or None
    return None


def reader_counts(record_id, pmid=None, nct=None, endpoint_ok=None):
    """(events_t, n_t, events_c, n_c) as the independent second reader's RECORDED response states them, or None."""
    import base64
    p = os.path.join(ROOT, "evidence", "model_calls", "audit", f"{record_id}.json")
    if not os.path.exists(p):
        return None
    try:
        r = json.load(open(p, encoding="utf-8"))
        resp = json.loads(base64.b64decode((r.get("response") or {}).get("b64") or "").decode("utf-8"))
    except (ValueError, TypeError):
        return None
    if r.get("state") != "RAN_OK" or resp.get("state") != "REPORTED":
        return None
    if pmid is not None:
        # the record must be ABOUT this paper (codex d12-r4 #4): one of its recorded inputs is this PMID's held text,
        # and its prompt names the trial's registration when the binding states one
        refs = [str(d.get("ref") or "") for d in r.get("input_digests") or []]
        if not any(f"PMID {pmid}" == x or x.startswith(f"PMID {pmid} ") or f" PMID {pmid} " in f" {x} " for x in refs):
            return None
        if nct:
            pr = r.get("prompt") or {}
            try:
                ptxt = base64.b64decode(pr.get("b64") or "").decode("utf-8") if isinstance(pr, dict) else str(pr)
            except (ValueError, TypeError):
                return None
            if nct not in ptxt:
                return None
    if endpoint_ok is not None and not endpoint_ok(str(resp.get("quote") or "")[:600]):
        # the reader located ANOTHER endpoint of this paper (codex d12-r6 #2): its numbers confirm nothing here
        return None
    vals = tuple(_whole(resp.get(k)) for k in _VALUE_KEYS)
    return None if None in vals else vals


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
        p = os.path.join(self.snap, "outcomes.txt")
        self._outcomes = {}
        with open(p, encoding="utf-8", newline="") as f:
            rd = csv.DictReader(f, delimiter="|")
            if not {"id", "nct_id", "title"} <= set(rd.fieldnames or []):
                raise ValueError(f"{p}: missing id/nct_id/title columns")
            for r in rd:
                if r["id"] in ids:
                    self._outcomes[r["id"]] = r

    def outcome_title(self, nct, oid):
        r = (self._outcomes or {}).get(oid)
        return r.get("title") if r and r.get("nct_id") == nct else None

    def group_title(self, nct, oid, code):
        return next((r.get("title") for r in self._groups
                     if r["nct_id"] == nct and r["outcome_id"] == oid and r["ctgov_group_code"] == code), None)

    def arms(self, nct, oid, classification):
        """{group code: (events, participants)} for that NCT + outcome + classification ('unclassified' = empty). Only a
        COUNT of participants is an event count (codex d12-r1 #4): param_type COUNT_OF_PARTICIPANTS, or NUMBER whose
        units name participants; the value must be a whole number. Anything else is not returned."""
        cls = "" if classification in (None, "", "unclassified") else classification
        # every row is collected per group; a group with MORE THAN ONE candidate row (several categories, or a second
        # denominator such as participant-years) is ambiguous and the outcome is refused, never overwritten (r5 #2 #3)
        n, e = {}, {}
        for r in self._counts:
            if r["nct_id"] == nct and r["outcome_id"] == oid and r.get("scope") == "Measure" and \
                    " ".join((r.get("units") or "").lower().split()) in COUNT_UNITS:
                n.setdefault(r["ctgov_group_code"], []).append(r["count"])
        for r in self._meas:
            if r["nct_id"] != nct or r["outcome_id"] != oid or (r.get("classification") or "") != cls:
                continue
            if (r.get("category") or "").strip():
                # a category splits the measure (alive / dead, a follow-up window ...): which one is the event is not
                # typed here, so a categorised row is never an event count (codex d12-r6 #1)
                e.setdefault(r["ctgov_group_code"], []).extend([None, None])
                continue
            pt, units = (r.get("param_type") or "").upper(), (r.get("units") or "").lower()
            # an ALLOWLIST of units that are a count of people, exactly -- never a substring test, which admitted
            # 'percentage of participants', rates and 'participant-years' (codex d12-r2 #1, r3 #2, r4 #1)
            if not (pt in ("COUNT_OF_PARTICIPANTS", "NUMBER") and " ".join(units.split()) in COUNT_UNITS):
                continue
            e.setdefault(r["ctgov_group_code"], []).append(r["param_value"])
        if any(len(v) != 1 for v in list(n.values()) + list(e.values())):
            return {}
        n = {g: v[0] for g, v in n.items()}
        e = {g: v[0] for g, v in e.items()}
        out = {}
        for g in set(n) & set(e):
            ev, nn = _whole(e[g]), _whole(n[g])
            if ev is not None and nn is not None:
                out[g] = (ev, nn)
        return out


COUNT_UNITS = ("participants", "participant", "subjects", "patients", "number of participants",
               "number or participants with an event", "number of participants with an event")


def _whole(x):
    """int(x) only when x is a whole number written as one ('30', '30.0'); else None (never truncated)."""
    import math
    try:
        f = float(str(x).strip())
    except ValueError:
        return None
    if not math.isfinite(f):        # 'nan' / 'inf' are not counts (codex d12-r3 #5)
        return None
    return int(f) if f == int(f) and f >= 0 else None


_COUNT_NOUNS = ("of ", "/", "events", "event ", "patients", "participants", "subjects", "deaths", "women", "men ")


def count_positions(text, value):
    """Positions where `value` is written AS A COUNT: a whole-number token (not a percentage, not part of a decimal or a
    longer number) followed by 'of N', '/N' or a count noun ('events', 'patients' ...) (codex d12-r1 #1)."""
    s, v, out, i = str(text or ""), str(value), [], 0
    while True:
        i = s.find(v, i)
        if i < 0:
            return out
        j = i + len(v)
        left_ok = i == 0 or not (_isd(s[i - 1]) or s[i - 1] in ".,")
        right = s[j:j + 14].lower()
        right_ok = j == len(s) or not (_isd(s[j]) or (s[j] in ".," and _isd(s[j + 1:j + 2])))
        if left_ok and right_ok and not right.lstrip().startswith("%") and \
                any(right.lstrip(" [(").startswith(w) for w in _COUNT_NOUNS):
            out.append(i)
        i = j


def _pct_after(text, pos, width=70):
    """The first 'x%' / 'x %' within `width` chars after pos, as (value, printed decimals), else None. The decimals are
    read from the printed digits, so '10.0%' keeps its one decimal (codex d12-r2 #5)."""
    seg = str(text or "")[pos:pos + width]
    k = seg.find("%")
    if k < 0:
        return None
    j = k
    while j > 0 and seg[j - 1] == " ":
        j -= 1
    st = j
    while st > 0 and (_isd(seg[st - 1]) or seg[st - 1] == "."):
        st -= 1
    txt = seg[st:j]
    try:
        return float(txt), (len(txt.split(".")[1]) if "." in txt else 0)
    except ValueError:
        return None


def _tied(text, pos, e, n):
    """The count at pos is tied to ITS denominator (codex d12-r1 #3): written 'e of n' / 'e/n', or the first percentage
    after it equals 100*e/n at its printed precision."""
    s = str(text or "")[pos:pos + 40].replace(",", "")
    # the count is written with an explicit denominator: it must BE n -- never fall through to a percentage (r6 #3)
    for sep in (" of ", "/"):
        if s.startswith(f"{e}{sep}"):
            rest = s[len(f"{e}{sep}"):]
            k = 0
            while k < len(rest) and _isd(rest[k]):
                k += 1
            if k:
                return rest[:k] == str(n)
    for pre in (f"{e} of {n}", f"{e}/{n}"):
        # a numeric boundary after the denominator: '10 of 1000' is never '10 of 100' (codex d12-r2 #3)
        if s.startswith(pre) and not _isd(s[len(pre):len(pre) + 1]):
            return True
    got = _pct_after(text, pos)
    if got is None:
        return False
    p, dec = got
    return abs(100.0 * e / n - p) <= 0.5 * 10 ** (-dec) + 1e-9


def _norm(t):
    return " ".join(str(t or "").lower().replace("-", " ").split())


def arm_terms(slug):
    """(treatment terms, control terms) from topics/<slug>.json (intervention agents + terms + class terms; comparator
    terms), lower-cased, hyphens as spaces."""
    p = os.path.join(ROOT, "topics", f"{slug}.json")
    if not os.path.exists(p):
        return [], []
    t = json.load(open(p, encoding="utf-8"))
    tr = set(t.get("intervention_terms") or []) | set(t.get("intervention_class_terms") or [])
    for v in (t.get("intervention_agents") or {}).values():
        tr |= set(v)
    return sorted({_norm(x) for x in tr if x}), sorted({_norm(x) for x in t.get("comparator_terms") or [] if x})


def _first(normtext, terms):
    hits = [normtext.find(x) for x in terms if x and normtext.find(x) >= 0]
    return min(hits) if hits else None


def arms_in_order(span, slug, pos_t, pos_c):
    """The arm each count belongs to, read from the text (codex d12-r1 #2): the treatment count and the control count
    appear in the same order as the first treatment term and the first control term. Positions are mapped through the
    same normalisation (lower case, hyphens as spaces, single spaces)."""
    tr, co = arm_terms(slug)
    nt_ = _norm(span)
    ft, fc = _first(nt_, tr), _first(nt_, co)
    if ft is None or fc is None:
        return False, "K2_ARM_TERMS_NOT_BOTH_IN_SPAN"
    return ((pos_t < pos_c) == (ft < fc)), "K2_COUNTS_NOT_IN_THE_ARMS_ORDER"


def verify(b, aact=None, endpoint_ok=None):
    """(True, basis) when the binding verifies under D12, else (False, why). endpoint_ok(title) -> bool: the topic's own
    outcome gate (g1_tracker.binding_verdict), applied to a K1 outcome's registered title."""
    v = b.get("values") or {}
    if b.get("tuple_kind") != "COUNTS" or not b.get("own_tuple") or any(
            not isinstance(v.get(k), int) or isinstance(v.get(k), bool) for k in _VALUE_KEYS):
        return False, "NOT_AN_OWN_COUNTS_TUPLE"
    et, nt, ec, nc = (v[k] for k in _VALUE_KEYS)
    if not (0 <= et <= nt and 0 <= ec <= nc and nt > 0 and nc > 0):
        return False, "IMPOSSIBLE_COUNTS"
    rule = b.get("rule")
    if rule == "K1":
        nct, oid = _aact_source(b.get("source"))
        if not nct or not oid or nct not in (b.get("ncts") or []):
            return False, "K1_SOURCE_NOT_AN_AACT_OUTCOME_OF_THIS_TRIAL"
        # the trial's own held report must carry that registration (codex d12-r1 #5): the binding's NCT list is not
        # evidence on its own
        if _held_nct(b.get("slug"), b.get("pmid")) != nct:
            return False, "K1_HELD_REPORT_DOES_NOT_CARRY_THIS_NCT"
        if aact is None:
            return False, "K1_NOT_VERIFIABLE:NO_AACT_SNAPSHOT"
        # the AACT outcome must be OUR endpoint, by the tracker's own binding gate on its registered title (r5 #1)
        otitle = aact.outcome_title(nct, oid)
        if endpoint_ok is None:
            return False, "K1_ENDPOINT_NOT_CHECKABLE"
        if not otitle or not endpoint_ok(otitle):
            return False, f"K1_OUTCOME_NOT_OUR_ENDPOINT:{(otitle or '')[:80]}"
        arms = aact.arms(nct, oid, b.get("classification"))
        if len(arms) != 2:
            return False, f"K1_AACT_ROWS_DIFFER:{sorted(arms.items())}"
        # each group's ROLE is read from its own AACT title, never from its values (codex d12-r4 #2 #3): the treatment
        # group's title names a treatment term and no control term, the control group's a control term and no treatment
        # term. A title naming both (a double-dummy arm, 'Dabigatran + placebo warfarin') or neither is refused.
        tr, co = arm_terms(b.get("slug"))
        role = {}
        for g in arms:
            tt = _norm(aact.group_title(nct, oid, g))
            is_t, is_c = _first(tt, tr) is not None, _first(tt, co) is not None
            if is_t == is_c:
                return False, f"K1_GROUP_ROLE_AMBIGUOUS:{g}"
            role[g] = "t" if is_t else "c"
        if sorted(role.values()) != ["c", "t"]:
            return False, f"K1_NOT_ONE_TREATMENT_AND_ONE_CONTROL_GROUP:{role}"
        g_t = next(g for g, r in role.items() if r == "t")
        g_c = next(g for g, r in role.items() if r == "c")
        if arms[g_t] != (et, nt) or arms[g_c] != (ec, nc):
            return False, f"K1_AACT_ROWS_DIFFER:{sorted(arms.items())}"
        # the span names each (events, N) pair with ITS OWN AACT group title
        span = b.get("span") or ""
        for g, (e_, n_) in arms.items():
            title = aact.group_title(nct, oid, g)
            if not title or f"{title}: {e_} of {n_} participants" not in span:
                return False, f"K1_SPAN_DOES_NOT_STATE_AACT_GROUP:{g}"
        return True, f"K1: AACT {os.path.basename(aact.snap)} {nct} outcome {oid} ({b.get('classification')}): " \
                     f"groups {sorted(arms.items())}"
    if rule == "K2":
        # A free-text span's numbers cannot be certified as THIS endpoint, THIS population and THESE arms by syntax alone
        # (codex d12-r1/r2: percentages, arm order, safety denominators, another endpoint). The checks below are
        # necessary, not sufficient: a K2 binding is used only when the binding lane's INDEPENDENT recorded second
        # reader -- which never saw the staged values -- CONFIRMED these exact counts, and its record is held here.
        sr = b.get("second_reader") or {}
        if sr.get("verdict") != "CONFIRMED" or not sr.get("record_id"):
            return False, f"K2_NO_INDEPENDENT_CONFIRMATION:{sr.get('verdict') or 'NONE'}"
        ab = _held_abstract(b.get("slug"), b.get("pmid"))
        span = b.get("span") or ""
        if not ab or not span or span not in ab:
            return False, "K2_SPAN_NOT_VERBATIM_IN_HELD_ABSTRACT"
        pt, pc = count_positions(span, et), count_positions(span, ec)
        if et == ec:
            # both arms print the same count (codex d12-r3 #4): exactly two occurrences, owned in the arms' order
            if len(pt) != 2:
                return False, "K2_EVENT_COUNTS_NOT_WRITTEN_ONCE_AS_COUNTS_IN_SPAN"
            tr, co = arm_terms(b.get("slug"))
            ft, fc = _first(_norm(span), tr), _first(_norm(span), co)
            if ft is None or fc is None:
                return False, "K2_ARM_TERMS_NOT_BOTH_IN_SPAN"
            pt, pc = ([pt[0]], [pt[1]]) if ft < fc else ([pt[1]], [pt[0]])
        if len(pt) != 1 or len(pc) != 1 or pt[0] == pc[0]:
            return False, "K2_EVENT_COUNTS_NOT_WRITTEN_ONCE_AS_COUNTS_IN_SPAN"
        if not (_tied(span, pt[0], et, nt) and _tied(span, pc[0], ec, nc)):
            return False, "K2_COUNT_NOT_TIED_TO_ITS_DENOMINATOR"
        ok, why = arms_in_order(span, b.get("slug"), pt[0], pc[0])
        if not ok:
            return False, why
        # the RECORD is read, not the label (codex d12-r3 #1): its own response must state these four counts, arm for arm
        if endpoint_ok is None:
            return False, "K2_ENDPOINT_NOT_CHECKABLE"
        got = reader_counts(sr["record_id"], pmid=str(b.get("pmid")), nct=(b.get("ncts") or [None])[0],
                            endpoint_ok=endpoint_ok)
        if got != (et, nt, ec, nc):
            return False, f"K2_SECOND_READER_RECORD_DOES_NOT_STATE_THESE_COUNTS:{got}"
        st = int_tokens(span)
        if nt in st and nc in st:
            return True, f"K2: PMID {b['pmid']} held abstract span (events and Ns in the span, arms in order)"
        ns = str(b.get("n_source") or "")
        if ns == "abstract":
            at = int_tokens(ab)
            if nt in at and nc in at:
                return True, f"K2: PMID {b['pmid']} held abstract span (events, arms in order, % = events/N); " \
                             f"Ns stated in the same held abstract"
            return False, "K2_NS_NOT_IN_HELD_ABSTRACT"
        nct, oid = _aact_source(ns)
        if nct and oid and nct in (b.get("ncts") or []) and _held_nct(b.get("slug"), b.get("pmid")) == nct:
            if aact is None:
                return False, "K2_N_NOT_VERIFIABLE:NO_AACT_SNAPSHOT"
            n = {r["ctgov_group_code"]: _whole(r["count"]) for r in aact._counts
                 if r["nct_id"] == nct and r["outcome_id"] == oid and r.get("scope") == "Measure"}
            if len(n) == 2 and sorted(n.values()) == sorted([nt, nc]):
                return True, f"K2: PMID {b['pmid']} held abstract span (events, arms in order, % = events/N); " \
                             f"Ns AACT {nct} outcome {oid} counts"
            return False, f"K2_AACT_NS_DIFFER:{sorted(n.items())}"
        return False, "K2_NS_UNSOURCED"
    if rule == "K5":
        return verify_k5(b, endpoint_ok)
    return False, f"RULE_NOT_UNDER_D12:{rule}"


# ---- K5: a held DOCUMENT's table row (binding lane, final-5, 8 Oct) -------------------------------------------------
# K2 reads the held abstract only; CONFIRM-HF (Table 2) and RECOVERY's ventilated subgroup (supplementary Table S2)
# print their counts only in a table. A K5 binding names the document (a committed CC text, or a LOCAL git-ignored copy
# of a non-redistributable one, pinned by the sha256 of its text: absent or changed -> unused, as K1 without a snapshot),
# the table's caption, header and row (each verbatim, in that order), which span names the outcome, and which cells of
# the row hold the two counts. tests/test_g1_d12_k5.py plants every refusal.
K5_TABLE_REACH = 6000      # caption -> header -> row must sit within one table's reach of each other


def _plain(t, fmt="xml"):
    """The rendered text a span is matched against, whitespace collapsed. Markup ('xml': a held JATS text) has its tags
    stripped and entities decoded; a plain 'text' document (a PDF's extracted text) is matched AS PRINTED -- stripping
    '<...>' there deleted RECOVERY's Table S2 between '(<0.5%)' and '>0.05' (8 Oct)."""
    import html
    import re
    s = str(t or "")
    if fmt == "xml":
        s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s).strip()


def _held_doc(doc):
    """(plain text, None) for a held document whose text hashes to doc['text_sha256'], else (None, why)."""
    p = os.path.join(ROOT, str((doc or {}).get("path") or ""))
    if not (doc or {}).get("path") or not os.path.isfile(p):
        return None, "K5_DOCUMENT_NOT_HELD"
    raw = open(p, encoding="utf-8", errors="strict").read()
    if hashlib.sha256(raw.encode("utf-8")).hexdigest() != doc.get("text_sha256"):
        return None, "K5_DOCUMENT_CHANGED"
    if doc.get("format") not in ("xml", "text"):
        return None, "K5_DOCUMENT_FORMAT_UNDECLARED"
    return _plain(raw, doc["format"]), None


def _row_cells(row):
    """The row's value tokens after its label: '10', '7.6', '95/324' (an 'e/N' cell is one token). A percentage keeps its
    sign ('10%', '10 %' -> '10%') and a decimal comma its comma ('0,5%'), so neither can ever equal a count (codex
    final5-binding-r1a g1#1, r2 g1#1). A thousands separator is read away ('1,274' -> '1274')."""
    import re
    m = re.search(r"\d", row)
    out = []
    for n, dec, den, pct in (re.findall(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+(?!\d)|\d+)((?:[.,]\d+)?)((?:/\d+)?)(\s*%)?",
                                        row[m.start():]) if m else []):
        out.append((n.replace(",", "") if not dec else n) + dec + den + ("%" if pct else ""))
    return out


def _declares_percent_units(text):
    """True when a caption / header declares its values as percentages: '(%)' or the word percent / percentage. Not a
    '95% CI', and not 'n (%)' / 'no. (%)' / 'number (%)' (counts WITH percentages)."""
    import re
    t = str(text or "")
    t = re.sub(r"\b(?:n|no\.?|number|events?|patients?)\s*\(\s*%\s*\)", " ", t, flags=re.I)
    if re.search(r"\bnumbers?\s+of\s+(?:patients|participants|subjects|events)\b", t, re.I):
        return False          # 'numbers of patients (percentages in parentheses)': counts WITH % (v12-r1 g1#1)
    return bool(re.search(r"\(\s*%\s*\)|\bper ?cent(?:ages?)?\b", t, re.I))


def _header_ns(header):
    import re
    return [int(x.replace(",", "")) for x in re.findall(r"\(\s*n\s*=\s*([\d,]+)\s*\)", header, re.I)]


def verify_k5(b, endpoint_ok):
    vals = b.get("values") or {}
    et, nt, ec, nc = (_whole(vals.get(k)) for k in _VALUE_KEYS)
    if None in (et, nt, ec, nc) or not (0 <= et <= nt and 0 <= ec <= nc):
        return False, "K5_VALUES_NOT_COUNTS"
    text, why = _held_doc(b.get("doc"))
    if text is None:
        return False, why
    fmt = b["doc"]["format"]
    spans = {k: _plain(b.get(k), fmt) for k in ("caption_span", "header_span", "row_span")}
    for k, s in spans.items():
        if len(s) < 12 or s not in text:
            return False, f"K5_SPAN_NOT_VERBATIM:{k}"
    # in table order, within one table's reach: the header follows its caption and the row follows its header
    # EVERY occurrence of the caption is tried: a contents page repeats it far from its table (RECOVERY, 8 Oct)
    placed, cp = False, text.find(spans["caption_span"])
    while cp >= 0 and not placed:
        hp = text.find(spans["header_span"], cp)
        rp = text.find(spans["row_span"], hp) if hp >= 0 else -1
        placed = hp >= 0 and rp >= 0 and hp - cp <= K5_TABLE_REACH and rp - hp <= K5_TABLE_REACH
        cp = text.find(spans["caption_span"], cp + 1)
    if not placed:
        return False, "K5_SPANS_NOT_IN_TABLE_ORDER"
    if endpoint_ok is None:
        return False, "K5_ENDPOINT_NOT_CHECKABLE"
    src = b.get("outcome_from")
    if src not in ("row", "caption"):
        return False, "K5_OUTCOME_SPAN_UNDECLARED"
    if not endpoint_ok(spans["row_span"] if src == "row" else spans["caption_span"]):
        return False, "K5_OUTCOME_NOT_OUR_ENDPOINT"
    # arm order from the header's own arm terms
    tr, co = arm_terms(b.get("slug"))
    hn = _norm(spans["header_span"])
    ft, fc = _first(hn, tr), _first(hn, co)
    if ft is None or fc is None:
        return False, "K5_ARM_TERMS_NOT_BOTH_IN_HEADER"
    # a row whose LABEL declares percentages holds no counts, whatever its separators ('Mortality (%) 12,345'; codex
    # final5-binding-r3 g1#1)
    import re as _re
    lab = _re.split(r"\d", spans["row_span"], maxsplit=1)[0]
    # ... but 'n (%)' / 'no. (%)' / 'number (%)' declares counts WITH percentages (codex final5-binding-r4 g1#1)
    if (("%" in lab or _re.search(r"\bper ?cent", lab, _re.I))
            and not _re.search(r"\b(?:n|no\.?|number|events?|patients?)\s*\(\s*%\s*\)", lab, _re.I)):
        return False, "K5_ROW_IS_PERCENTAGES"
    # the caption or header may declare the table's unit too (captain codex final5-binding-captain g1#3)
    if _declares_percent_units(spans["caption_span"]) or _declares_percent_units(spans["header_span"]):
        return False, "K5_TABLE_IS_PERCENTAGES"
    cells, idx = _row_cells(spans["row_span"]), b.get("cells") or {}
    it, ic = idx.get("events_t"), idx.get("events_c")
    if not (type(it) is int and type(ic) is int and 0 <= it < len(cells) and 0 <= ic < len(cells) and it != ic):
        return False, "K5_CELLS_UNDECLARED"
    if (it < ic) != (ft < fc):
        return False, "K5_CELLS_NOT_IN_THE_HEADER_ARM_ORDER"
    for cell, e, n in ((cells[it], et, nt), (cells[ic], ec, nc)):
        if "/" in cell:
            if cell != f"{e}/{n}":          # an e/N cell carries its OWN denominator
                return False, f"K5_CELL_IS_NOT_THE_COUNT:{cell}"
        elif cell != str(e):
            return False, f"K5_CELL_IS_NOT_THE_COUNT:{cell}"
    if "/" not in cells[it] or "/" not in cells[ic]:
        want = [nt, nc] if ft < fc else [nc, nt]
        if _header_ns(spans["header_span"]) != want:
            return False, "K5_NS_NOT_THE_HEADER_NS_IN_ARM_ORDER"
    ok, why = _k5_second_reader(b, text, (et, nt, ec, nc), spans["row_span"], fmt)
    if not ok:
        return False, why
    return True, (f"K5: PMID {b.get('pmid')} held document {b['doc'].get('path')} (text sha256 "
                  f"{b['doc'].get('text_sha256')[:12]}...), table row '{spans['row_span'][:60]}', {why}")


def _k5_second_reader(b, text, want, row, fmt):
    import base64
    sr = b.get("second_reader") or {}
    if sr.get("kind") == "RECORDED_READERS":
        ids = [r for r in sr.get("record_ids") or [] if r]
        if not ids:
            return False, "K5_NO_SECOND_READER"
        for rid in ids:
            p = os.path.join(ROOT, str(sr.get("dir") or ""), f"{rid}.json")
            try:
                r = json.load(open(p, encoding="utf-8"))
                resp = json.loads(base64.b64decode((r.get("response") or {}).get("b64") or "").decode("utf-8"))
            except (OSError, ValueError, TypeError):
                return False, f"K5_SECOND_READER_DIFFERS:{rid}:UNREADABLE"
            refs = [str(d.get("ref") or "") for d in r.get("input_digests") or []]
            if not any(x == f"PMID {b.get('pmid')}" or x.startswith(f"PMID {b.get('pmid')} ") for x in refs):
                return False, f"K5_SECOND_READER_NOT_ABOUT_THIS_PAPER:{rid}"
            got = tuple(_whole(resp.get(k)) for k in _VALUE_KEYS)
            if r.get("state") != "RAN_OK" or resp.get("state") != "FOUND" or got != want:
                return False, f"K5_SECOND_READER_DIFFERS:{rid}:{got}"
            parts = [_plain(x, fmt) for x in str(resp.get("quote") or "").splitlines() if _plain(x, fmt)]
            if not parts or any(len(x) < 20 or x not in text for x in parts):
                return False, f"K5_SECOND_READER_QUOTE_NOT_IN_DOCUMENT:{rid}"
        return True, f"second readers {', '.join(ids)} state the same counts"
    if sr.get("kind") == "SECOND_EXTRACTION":
        d1, d2 = b.get("doc") or {}, sr.get("doc") or {}
        if d2.get("path") == d1.get("path") or d2.get("text_sha256") == d1.get("text_sha256"):
            return False, "K5_SECOND_EXTRACTION_IS_THE_SAME_DOCUMENT"
        t2, why = _held_doc(d2)
        if t2 is None:
            return False, why.replace("K5_", "K5_SECOND_EXTRACTION_")
        r2 = _plain(sr.get("row_span"), d2.get("format"))
        if len(r2) < 12 or r2 not in t2:
            return False, "K5_SECOND_EXTRACTION_ROW_NOT_VERBATIM"
        if _row_cells(r2)[:len(_row_cells(row))] != _row_cells(row):
            return False, "K5_SECOND_READER_DIFFERS:SECOND_EXTRACTION_CELLS"
        return True, f"second extraction {d2.get('path')} holds the same row cells"
    return False, "K5_NO_SECOND_READER"


_AACT_CACHE = {}


def for_topic(slug, trials, snap=None, reg=None, endpoint_ok=None):
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
        # K1 may join through its NCT (the held report must carry it, verify()); K2 is the paper's own text, so it joins
        # by that paper's PMID only (codex d12-r2 #7)
        # K1 joins through its SOURCE NCT only -- the one verify() authenticates -- never another listed NCT (r3 #3)
        src_nct = _aact_source(b.get("source"))[0] if b.get("rule") == "K1" else None
        ids = {f"PMID {b.get('pmid')}"} | ({src_nct} if src_nct else set())
        xs = [x for x in trials if x.get("in_our_pool") and str(x.get("family")) in ids]
        if len(xs) != 1:
            refused.append({"trial": b.get("label"), "why": f"IDENTITY:{len(xs)}_MATCHED_TRIALS"})
            continue
        ok, why = verify(b, aact, endpoint_ok)
        if not ok:
            refused.append({"trial": b.get("label"), "why": why})
            continue
        out[xs[0]["label"]] = {"row": {k: b["values"][k] for k in _VALUE_KEYS}, "basis": why,
                               "source": b.get("source"), "span": b.get("span"), "rule": b.get("rule")}
    return out, refused


def import_bindings(src_path, ref, audit_path=None, audit_ref=None):
    raw = open(src_path, "rb").read()
    d = json.loads(raw.decode("utf-8"))
    keep = [b for b in d.get("bindings") or [] if b.get("own_tuple") and b.get("tuple_kind") == "COUNTS"]
    audit_sha = None
    if audit_path:
        araw = open(audit_path, "rb").read()
        audit_sha = hashlib.sha256(araw).hexdigest()
        rows = {(r.get("slug"), str(r.get("pmid"))): r for r in json.loads(araw.decode("utf-8")).get("rows") or []}
        for b in keep:
            r = rows.get((b.get("slug"), str(b.get("pmid"))))
            if r:
                b["second_reader"] = {"verdict": r.get("verdict"), "record_id": r.get("record_id"),
                                      "source": f"{audit_ref}:outputs/k_gap/g1_binding/audit_staged_counts.json"}
    out = {"decision": DECISION,
           "rule": "Own-trial per-arm counts for the G1 same-trial comparison ONLY (scripts/g1_d12.py); never served.",
           "imported_from": {"ref": ref, "path": "outputs/k_gap/g1_binding/bindings_counts.json",
                             "sha256": hashlib.sha256(raw).hexdigest(), "bindings_kept": len(keep),
                             "second_reader_audit": {"ref": audit_ref, "sha256": audit_sha} if audit_path else None,
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
        r = import_bindings(a[1], a[a.index("--ref") + 1], a[a.index("--audit") + 1] if "--audit" in a else None,
                            a[a.index("--audit-ref") + 1] if "--audit-ref" in a else None)
        print(f"wrote {os.path.relpath(REG, ROOT)}: {len(r['bindings'])} bindings from {r['imported_from']['ref']}")
    else:
        print(__doc__)
