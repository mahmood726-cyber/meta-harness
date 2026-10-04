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
        v, why, src = gate_one(p, x.get("comparator_row"), terms, iv, cp, held_texts(t["slug"], t["pmids"]))
        decisions.append({"slug": key[0], "label": key[1], "lane": p["_lane"], "proposed": p.get("verdict"),
                          "verdict": v, "why": why, "source": src})
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
