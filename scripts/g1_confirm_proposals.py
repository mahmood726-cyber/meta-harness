"""DETERMINISTIC GATE for model-located primary bindings (G1 confirm-unverified, Mahmood 4 Oct: 'recorded model calls
only as proposals'). Codex lanes CONFPROP1..3 (gpt-5.5, offline, their prompts in /f/codex-lanes/briefs/CONFPROP.md,
their outputs committed here as outputs/k_gap/g1_confirm/proposals_CONFPROP*.json) READ each UNVERIFIED trial's held
open texts and propose where the trial prints the comparator's tuple. A proposal is only a pointer: nothing it says is
believed until every check below passes on the HELD bytes.

ADMIT a PRINTED_SAME proposal only when ALL hold:
  Q  every quote is verbatim in a held primary text of that trial (secondary_meta_build.primary_sources, whitespace and
     dashes folded) -- else QUOTE_NOT_IN_HELD_TEXT
  V  the values it reports equal the comparator's row (counts as integers; effect/lower/upper at printed precision)
     -- else NOT_THE_COMPARATOR_TUPLE
  N  every count (or the effect and both CI bounds) is printed, as a whole number / verbatim, in the joined quotes
     -- else VALUES_NOT_IN_QUOTES (the single_primary_source rule)
  O  a topic outcome term is named in the joined quotes -- else OUTCOME_NOT_NAMED
  S  no subgroup / per-protocol / completers / post-hoc language in the quotes (harness.extract detector + the binder's
     SUBGROUP_EXTRA) -- else SUBGROUP_OR_POST_HOC
  A  (counts) both arm labels the proposal names are in the quotes, and the treatment count's label is an intervention
     term while the control count's is a comparator term -- else ARMS_NOT_ESTABLISHED / ARMS_SWAPPED. Stricter than the
     regex route on purpose: a model chose the span.
Admitted proposals are written as bindings (route PRIMARY_TEXT_PROPOSAL) that the tracker hook re-checks again
(apply_confirm_bindings). PRINTED_DIFFERENT proposals that pass Q are recorded as comparator-discrepancy CANDIDATES
(never a flip, never a correction).

    python scripts/g1_confirm_proposals.py   -> outputs/k_gap/g1_confirm/proposal_gate.json, merges into bindings.json
"""
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import re
import sys
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import extract  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402
import g1_confirm_bind as cb  # noqa: E402
import secondary_meta_build as smb  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_confirm")
GATE = os.path.join(OUT, "proposal_gate.json")


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[‐-―−]", "-", s)
    return re.sub(r"\s+", " ", s).strip()


def held_texts(slug, pmids):
    out = []
    for p in pmids or []:
        for kind, ref, pl in smb.primary_sources(slug, p):
            if kind == "text" and isinstance(pl, str):
                out.append((ref, norm(pl)))
    return out


def _int(v):
    try:
        f = float(str(v).replace(",", ""))
        return int(f) if f == int(f) else None
    except (TypeError, ValueError):
        return None


def gate_one(p, comparator_row, terms, interv, comp, texts):
    """(verdict, why, source_ref) for one proposal against the HELD texts."""
    if p.get("verdict") not in ("PRINTED_SAME", "PRINTED_DIFFERENT"):
        return "NOT_PROPOSED", p.get("verdict") or "NO_VERDICT", None
    quotes = [norm(q.get("text")) for q in p.get("quotes") or [] if norm(q.get("text"))]
    if not quotes:
        return "REFUSED", "NO_QUOTES", None
    src = None
    for q in quotes:
        hit = next((ref for ref, t in texts if q in t), None)
        if hit is None:
            return "REFUSED", "QUOTE_NOT_IN_HELD_TEXT:" + q[:80], None
        src = src or hit
    joined = " … ".join(quotes)
    flat = joined.replace(",", "")
    if p["verdict"] == "PRINTED_DIFFERENT":
        return "DISCREPANCY_CANDIDATE", "quotes verbatim in held text; numbers differ from the comparator row", src
    vp, cr = p.get("values_printed") or {}, comparator_row or {}
    keys = ("events_t", "n_t", "events_c", "n_c")
    by_counts = all(_int(cr.get(k)) is not None for k in keys) and all(_int(vp.get(k)) is not None for k in keys)
    if by_counts:
        if any(_int(vp[k]) != _int(cr[k]) for k in keys):
            return "REFUSED", "NOT_THE_COMPARATOR_TUPLE", src
        if not all(re.search(rf"(?<![\d.]){_int(cr[k])}(?![\d])", flat) for k in keys):
            return "REFUSED", "VALUES_NOT_IN_QUOTES", src
    else:
        if not all(cr.get(k) not in (None, "") for k in ("effect", "lower", "upper")):
            return "REFUSED", "COMPARATOR_ROW_HAS_NO_TYPED_TUPLE", src
        if not all(sm._eq_printed(vp.get(k), cr.get(k)) for k in ("effect", "lower", "upper")):
            return "REFUSED", "NOT_THE_COMPARATOR_TUPLE", src
        if not all(str(vp.get(k)) in flat for k in ("effect", "lower", "upper")):
            return "REFUSED", "VALUES_NOT_IN_QUOTES", src
    low = joined.lower()
    if not any(t and t.lower() in low for t in terms):
        return "REFUSED", "OUTCOME_NOT_NAMED", src
    if extract._is_subgroup_sentence(joined) or cb.SUBGROUP_EXTRA.search(joined):
        return "REFUSED", "SUBGROUP_OR_POST_HOC", src
    if by_counts:
        arms = p.get("arm_of_each_count") or {}
        lt, lc = norm(arms.get("events_t")).lower(), norm(arms.get("events_c")).lower()
        if not lt or not lc or lt not in low or lc not in low:
            return "REFUSED", "ARMS_NOT_ESTABLISHED", src
        iv = [w.lower() for w in list(interv or []) + cb.GENERIC_INTERV if w]
        cp = [w.lower() for w in list(comp or []) + cb.GENERIC_COMP if w]
        t_is_i, t_is_c = any(w in lt for w in iv), any(w in lt for w in cp)
        c_is_i, c_is_c = any(w in lc for w in iv), any(w in lc for w in cp)
        if (t_is_c and not t_is_i) or (c_is_i and not c_is_c):
            return "REFUSED", "ARMS_SWAPPED", src
        if not (t_is_i and c_is_c):
            return "REFUSED", "ARMS_NOT_ESTABLISHED", src
    return "ADMITTED", "all checks passed", src


_PCT_AFTER = r"\s*\(\s*(\d{1,3}(?:\.\d+)?)\s*%?\s*\)"


def n_quote(text, label, n):
    """A held span stating an arm's size next to its own label ('(EPA group; n=9326)'), or None: the label and
    'n = N' / '(n=N)' within 60 characters, nothing between them that names another number of patients."""
    t = norm(text)
    for m in re.finditer(re.escape(norm(label)), t, re.I):
        w = t[max(0, m.start() - 60): m.end() + 60]
        if re.search(rf"\b[nN]\s*=\s*{n:,}(?!\d)|\b[nN]\s*=\s*{n}(?!\d)", w):
            return w
    return None


def gate_own_tuple(p, terms, interv, comp, texts):
    """OWN-TUPLE admission (Mahmood 3 Oct: matched = ANY verified typed tuple for the comparator's trial, not only the
    comparator's numbers): the trial's OWN printed counts for the topic outcome, whole randomized comparison. Counts only
    (the single_primary_source rule). Returns (verdict, why, src, parts)."""
    vp = p.get("values_printed") or {}
    keys = ("events_t", "n_t", "events_c", "n_c")
    if not all(_int(vp.get(k)) is not None for k in keys):
        return "REFUSED", "OWN_TUPLE_NEEDS_TYPED_COUNTS", None, []
    et, nt, ec, nc = (_int(vp[k]) for k in keys)
    if not (0 <= et <= nt and 0 <= ec <= nc and nt > 0 and nc > 0):
        return "REFUSED", "OWN_TUPLE_COUNTS_IMPOSSIBLE", None, []
    parts = [norm(q.get("text")) for q in p.get("quotes") or [] if norm(q.get("text"))]
    src = None
    for q in parts:
        hit = next((ref for ref, t in texts if q in t), None)
        if hit is None:
            return "REFUSED", "QUOTE_NOT_IN_HELD_TEXT:" + q[:80], None, []
        src = src or hit
    arms = p.get("arm_of_each_count") or {}
    lt, lc = norm(arms.get("events_t")), norm(arms.get("events_c"))
    # an arm size missing from the quotes is looked up in the held text next to that arm's OWN label
    for lab, n in ((lt, nt), (lc, nc)):
        flat = " ".join(parts).replace(",", "")
        if not re.search(rf"(?<![\d.]){n}(?![\d])", flat) and lab:
            got = next((w for _r, t in texts for w in [n_quote(t, lab, n)] if w), None)
            if got:
                parts.append(got)
    joined = " … ".join(parts)
    flat = joined.replace(",", "")
    if not all(re.search(rf"(?<![\d.]){v}(?![\d])", flat) for v in (et, nt, ec, nc)):
        return "REFUSED", "VALUES_NOT_IN_QUOTES", src, []
    # a count printed with a percentage must be consistent with its N at the printed precision
    for e, n in ((et, nt), (ec, nc)):
        for m in re.finditer(rf"(?<![\d.]){e}(?:\s*(?:/|of|out of)\s*{n}(?![\d])[^()]{{0,20}}?)?{_PCT_AFTER}", flat):
            d = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
            if abs(100.0 * e / n - float(m.group(1))) > 0.5 * 10 ** -d + 1e-9:
                return "REFUSED", f"PERCENT_INCONSISTENT_WITH_N:{e}/{n}~{m.group(1)}%", src, []
    low = joined.lower()
    # no comparator number anchors an own tuple, so the outcome must be named by a NON-GENERIC topic term (the shared
    # table-location gate's rule): 'primary outcome' / 'primary endpoint' name SOME composite, not this topic's
    # (LoDoCo's ACS + cardiac arrest + stroke; JELIS's major coronary events)
    if not any(t and t.lower() not in extract.GENERIC_ANCHORS and t.lower() in low for t in terms):
        return "REFUSED", ("OUTCOME_NAMED_ONLY_GENERICALLY" if any(t and t.lower() in low for t in terms)
                           else "OUTCOME_NOT_NAMED"), src, []
    if extract._is_subgroup_sentence(joined) or cb.SUBGROUP_EXTRA.search(joined) or \
            re.search(r"\badjusted\b", low):
        return "REFUSED", "SUBGROUP_OR_POST_HOC_OR_ADJUSTED", src, []
    if re.search(r"\bhospitali[sz]ations\b|\bepisodes\b|\bevents occurred\b", low) and \
            not re.search(r"\bpatients?\b|\bparticipants?\b", low):
        return "REFUSED", "EVENT_COUNTS_NOT_PATIENTS", src, []
    if not lt or not lc or lt.lower() not in low or lc.lower() not in low:
        return "REFUSED", "ARMS_NOT_ESTABLISHED", src, []
    iv = [w.lower() for w in list(interv or []) + cb.GENERIC_INTERV if w]
    cp = [w.lower() for w in list(comp or []) + cb.GENERIC_COMP if w] + ["no " + w.lower() for w in interv or [] if w]
    t_i, t_c = any(w in lt.lower() for w in iv), any(w in lt.lower() for w in cp)
    c_i, c_c = any(w in lc.lower() for w in iv), any(w in lc.lower() for w in cp)
    if (t_c and not t_i) or (c_i and not c_c):
        return "REFUSED", "ARMS_SWAPPED", src, []
    if not (t_i and c_c):
        return "REFUSED", "ARMS_NOT_ESTABLISHED", src, []
    return "ADMITTED_OWN_TUPLE", "trial's own counts for the topic outcome, all checks passed", src, parts


def main():
    props = []
    for f in sorted(glob.glob(os.path.join(OUT, "proposals_CONFPROP*.json"))):
        body = open(f, "rb").read()
        for p in json.loads(body.decode("utf-8")):
            props.append(dict(p, _lane=os.path.basename(f)[10:-5], _file_sha256=hashlib.sha256(body).hexdigest()))
    bp = os.path.join(OUT, "bindings.json")
    B = json.load(open(bp, encoding="utf-8"))
    nb = {(x["slug"], x["label"]): x for x in B.get("not_bound") or []}
    decisions, new = [], []
    import g1_confirm_acquire as acq
    tg = {(t["slug"], t["label"]): t for t in acq.unverified_targets()}
    for p in props:
        key = (p.get("slug"), p.get("label"))
        t = tg.get(key)
        if not t:
            decisions.append({"slug": key[0], "label": key[1], "lane": p["_lane"], "verdict": "REFUSED",
                              "why": "NOT_A_CURRENT_TARGET"})
            continue
        g = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", t["slug"] + ".json"), encoding="utf-8"))
        x = next(r for r in g["trials"] if r["label"] == t["label"])
        spec = smb.spec_of(t["slug"])
        terms = [k for k in (spec.get("keywords") or []) if k] + list(spec.get("core") or [])
        iv, cp = cb.arm_terms(t["slug"])
        texts = held_texts(t["slug"], t["pmids"])
        v, why, src = gate_one(p, x.get("comparator_row"), terms, iv, cp, texts)
        own_parts = []
        if v == "DISCREPANCY_CANDIDATE" or (v == "REFUSED" and why in ("NOT_THE_COMPARATOR_TUPLE",
                                                                         "COMPARATOR_ROW_HAS_NO_TYPED_TUPLE")):
            ov, owhy, osrc, own_parts = gate_own_tuple(p, terms, iv, cp, texts)
            if ov == "ADMITTED_OWN_TUPLE":
                v, why, src = ov, owhy, osrc
            else:
                why = f"{why} | own-tuple: {owhy}"
        decisions.append({"slug": key[0], "label": key[1], "lane": p["_lane"], "proposed": p.get("verdict"),
                          "verdict": v, "why": why, "source": src})
        if v == "ADMITTED_OWN_TUPLE" and key in nb:
            vp = p.get("values_printed") or {}
            new.append({"slug": key[0], "label": key[1], "pmid": None, "ncts": t["ncts"], "source_kind": "TEXT",
                        "source": src, "route": "PRIMARY_TEXT_PROPOSAL_OWN_TUPLE", "span": " … ".join(own_parts),
                        "span_parts": own_parts, "tuple_kind": "COUNTS", "own_tuple": True,
                        "values": {k: _int(vp.get(k)) for k in ("events_t", "n_t", "events_c", "n_c")},
                        "arm_check": "PROPOSAL_ARMS_ESTABLISHED", "search_key": "TOPIC_OUTCOME (reading lane)",
                        "proposal": {"lane": p["_lane"], "model": "codex gpt-5.5", "file_sha256": p["_file_sha256"],
                                     "note": "the lane was shown the comparator row"}})
        if v == "ADMITTED" and key in nb:
            cr = x.get("comparator_row") or {}
            by_counts = all(_int(cr.get(k)) is not None for k in ("events_t", "n_t", "events_c", "n_c"))
            parts = [norm(q.get("text")) for q in p.get("quotes") or []]
            new.append({"slug": key[0], "label": key[1], "pmid": None, "ncts": t["ncts"], "source_kind": "TEXT",
                        "source": src, "route": "PRIMARY_TEXT_PROPOSAL", "span": " … ".join(parts),
                        "span_parts": parts, "tuple_kind": "COUNTS" if by_counts else "EFFECT_CI",
                        "values": ({k: _int(cr.get(k)) for k in ("events_t", "n_t", "events_c", "n_c")} if by_counts
                                   else {k: cr.get(k) for k in ("measure", "effect", "lower", "upper")}),
                        "arm_check": "PROPOSAL_ARMS_ESTABLISHED" if by_counts else "NOT_APPLICABLE",
                        "search_key": "COMPARATOR_ROW",
                        "proposal": {"lane": p["_lane"], "model": "codex gpt-5.5", "file_sha256": p["_file_sha256"]},
                        "agreement_with_comparator_row": "NOT_INDEPENDENT:SEARCH_KEYED_BY_COMPARATOR_ROW"})
    if new:
        done = {(b["slug"], b["label"]) for b in new}
        B["bindings"] = (B.get("bindings") or []) + new
        B["not_bound"] = [x for x in B.get("not_bound") or [] if (x["slug"], x["label"]) not in done]
        B.setdefault("tally", {})["TEXT_PROPOSAL"] = len(new)
        with open(bp + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
            json.dump(B, fh, indent=1, ensure_ascii=False)
        os.replace(bp + ".tmp", bp)
    from collections import Counter
    res = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "proposals": len(props),
           "admitted_own_tuple": [d for d in decisions if d["verdict"] == "ADMITTED_OWN_TUPLE"],
           "by_verdict": dict(Counter(d["verdict"] for d in decisions)),
           "refusals": dict(Counter(d["why"].split(":")[0] for d in decisions if d["verdict"] == "REFUSED")),
           "admitted": [d for d in decisions if d["verdict"] == "ADMITTED"],
           "discrepancy_candidates": [d for d in decisions if d["verdict"] == "DISCREPANCY_CANDIDATE"],
           "decisions": decisions}
    with open(GATE + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    os.replace(GATE + ".tmp", GATE)
    print(json.dumps({k: res[k] for k in ("proposals", "by_verdict", "refusals")}))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
