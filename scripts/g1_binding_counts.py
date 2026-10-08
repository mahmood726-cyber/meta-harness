"""OUR OWN per-arm COUNTS for in-pool and unverified trials (gap list 7 Oct, binding share; Mahmood 8 Oct: "yes do all
that"). Deterministic first -- no model:

  K1 AACT     the trial's posted outcome whose TITLE passes g1_tracker.binding_verdict for the topic's primary outcome;
              participant-unit counts (classified rows allowed); the analysis denominator from outcome_counts; arms
              mapped by OUR intervention / comparator terms (g1_outcomes._two_arms: dose arms summed, one control).
              Several timepoint classifications: those naming a post-treatment / observational / extension period are
              dropped when the protocol timepoint is the TREATMENT period; exactly one must remain. Exactly one outcome
              must survive (a PRIMARY-type outcome is preferred over its duplicates).
  K2 ABSTRACT the sentence naming the primary outcome prints, per arm, 'X of N ... (p%)' or 'X events/patients ... (p%)'
              with N stated elsewhere in the abstract ('1731 given rivaroxaban') or, failing that, the AACT
              denominator of the SAME posted outcome; every X/N is corroborated by its printed percentage (rounded
              agreement), and each arm is the one NAMED beside its number.
The comparator's numbers are never an input (anti-circularity): agreement with them is measured afterwards.

    python scripts/g1_binding_counts.py SLUG=LABEL:PMID:NCT ...   -> outputs/k_gap/g1_binding/bindings_counts.json
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "bindings_counts.json")
PEOPLE = re.compile(r"participant|patient|subject|people|persons", re.I)
NOT_TREATMENT = re.compile(r"post[- ]?treatment|\bptp\b|observational|extension|follow[- ]?up period|after (?:the )?end", re.I)


TABLES = ("outcomes.txt", "result_groups.txt", "outcome_counts.txt", "outcome_measurements.txt")
_ROWS = {}


def prefetch(ncts):
    """ONE pass per AACT table for every target NCT (a pass per call streamed each multi-GB table ~90 times, 8 Oct)."""
    from kgap import aact_adapter as aa
    want = {n for n in ncts if n}
    for name in TABLES:
        for r in aa._rows(name, want):
            _ROWS.setdefault((name, r["nct_id"]), []).append(r)
        for n in want:
            _ROWS.setdefault((name, n), [])


def _rows(name, nct):
    if (name, nct) not in _ROWS:
        prefetch([nct])
    return _ROWS[(name, nct)]


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def topic(slug):
    return _j(os.path.join(ROOT, "topics", slug + ".json"))


def _int(x):
    try:
        f = float(str(x).replace(",", ""))
    except (TypeError, ValueError):
        return None
    return int(f) if f == int(f) and f >= 0 else None


# ---------------------------------------------------------------------------------------------------------------- K1
def aact_counts(nct, slug):
    """-> (binding or None, [refusals])."""
    import g1_tracker as gt
    import g1_outcomes as go
    from kgap import aact_adapter as aa
    t = topic(slug)
    po = t["primary_outcome"]
    kws = [k for k in po.get("keywords") or [] if len(k) >= 4]
    snap = (aa.snapshot() or {}).get("id")
    outs = {r["id"]: r for r in _rows("outcomes.txt", nct)}
    titles = {(r["outcome_id"], r["ctgov_group_code"]): r.get("title") for r in _rows("result_groups.txt", nct)
              if (r.get("result_type") or "").lower() == "outcome"}
    ns = {(r["outcome_id"], r["ctgov_group_code"]): _int(r.get("count")) for r in _rows("outcome_counts.txt", nct)
          if (r.get("scope") or "").lower() == "measure" and PEOPLE.search(r.get("units") or "")}
    meas = {}
    for r in _rows("outcome_measurements.txt", nct):
        if r["outcome_id"] in outs and (r.get("param_type") or "").upper() in ("NUMBER", "COUNT_OF_PARTICIPANTS") and \
                PEOPLE.search(r.get("units") or "") and not re.search(r"percent|proportion|rate|per 100", r.get("units") or "", re.I):
            meas.setdefault(r["outcome_id"], []).append(r)
    refusals, cands = [], []
    for oid, rows in meas.items():
        o = outs[oid]
        bv = gt.binding_verdict(po["name"], kws, o.get("title"), 2)
        if bv["verdict"] != "BINDABLE":
            refusals.append({"outcome_id": oid, "title": (o.get("title") or "")[:120], "gate": bv["gate"]})
            continue
        cls = sorted({(r.get("classification") or r.get("category") or "") for r in rows})
        if len(cls) > 1:
            keep = [c for c in cls if not NOT_TREATMENT.search(c)]
            if len(keep) != 1:
                refusals.append({"outcome_id": oid, "gate": "TIMEPOINT_AMBIGUOUS", "classifications": cls})
                continue
            cls = keep
        rows = [r for r in rows if (r.get("classification") or r.get("category") or "") == cls[0]]
        groups = [(titles.get((oid, r["ctgov_group_code"])), _int(r.get("param_value")), ns.get((oid, r["ctgov_group_code"])))
                  for r in rows]
        v, why = go._two_arms(groups, t)
        if not v:
            refusals.append({"outcome_id": oid, "gate": "ARMS", "why": why})
            continue
        if any(e > n for e, n in ((v[0], v[1]), (v[2], v[3]))):
            refusals.append({"outcome_id": oid, "gate": "EVENTS_EXCEED_N"})
            continue
        span = (f"{o.get('title')} | {cls[0] or 'unclassified'} | "
                + " | ".join(f"{g[0]}: {g[1]} of {g[2]} participants" for g in groups))
        cands.append({"outcome_id": oid, "type": o.get("outcome_type"), "values": dict(zip(("events_t", "n_t", "events_c", "n_c"), v)),
                      "span": span, "classification": cls[0] or None})
    if len(cands) > 1:
        prim = [c for c in cands if (c["type"] or "").upper() == "PRIMARY"]
        if len(prim) == 1:
            refusals += [{"outcome_id": c["outcome_id"], "gate": "NOT_THE_PRIMARY_DUPLICATE"} for c in cands if c is not prim[0]]
            cands = prim
    if len(cands) != 1:
        return None, refusals + ([{"gate": "UNIQUE", "why": f"{len(cands)} outcomes survive"}] if cands else [])
    c = cands[0]
    return {"source_kind": "AACT", "source": f"AACT {snap} {nct} outcome {c['outcome_id']}", "rule": "K1",
            "values": c["values"], "span": c["span"], "classification": c["classification"]}, refusals


# ---------------------------------------------------------------------------------------------------------------- K2
_XN = re.compile(r"(?<![\d.,])(\d[\d,]*) of (?:the )?(\d[\d,]*)\b[^()\[\]]{0,80}?[\(\[]\s*(\d+(?:\.\d+)?)\s*%")
_XE = re.compile(r"(?<![\d.,])(\d[\d,]*)\s+(?:events?|patients?|participants?)\b[^()\[\]]{0,80}?[\(\[]\s*(\d+(?:\.\d+)?)\s*%")
_NGIVEN = r"(?<![\d.,])(\d[\d,]*)\s+(?:were\s+)?(?:given|assigned to|randomi[sz]ed to|received|in the)\s+"


def _pct_ok(x, n, p):
    return n > 0 and abs(100.0 * x / n - p) <= 0.5 * 10 ** (-len(str(p).split(".")[1]) if "." in str(p) else 0) + 1e-9


def names_our_outcome(text, kws):
    """Every content word of one of our keywords appears in the text, in any order ('recurrent venous thromboembolism'
    in 'recurrent symptomatic venous thromboembolism')."""
    w = set(re.findall(r"[a-z]+", (text or "").lower()))
    return any(set(re.findall(r"[a-z]{3,}", k)) and set(re.findall(r"[a-z]{3,}", k)) <= w for k in kws)


def _arm_named(text, t):
    """The arm a phrase names, hyphen-tolerant ('conventional-therapy' names 'conventional therapy')."""
    import g1_outcomes as go
    return go._arm(text, t) or go._arm((text or "").replace("-", " "), t)


def abstract_counts(abstract, slug, aact_n=None):
    """-> (binding or None, refusal or None). The primary-outcome sentence only (it names the outcome or 'primary
    (efficacy) outcome'); one hit per arm, the arm being the one named in the 120 characters after the number (or, for a
    sentence that names one arm before the numbers, that arm for the first)."""
    t = topic(slug)
    po = t["primary_outcome"]
    import g1_binding_aact as ba
    # generic anchors never name an outcome: sglt2-pp's keywords carry 'hazard ratio', which every results sentence
    # prints (8 Oct: an EMPA-REG MACE sentence bound as HHF through it)
    generic = {g.lower() for g in ba.GENERIC} | {"hazard ratio", "risk ratio", "relative risk", "odds ratio",
                                                  "mean difference"}
    kws = [k.lower() for k in po.get("keywords") or [] if len(k) >= 6 and k.lower() not in generic]
    sents = re.split(r"(?<=[a-z\)\]])\.\s+(?=[A-Z])", abstract or "")
    # the generic 'primary (efficacy) outcome' names OUR outcome only when the abstract's own definition of it does
    # (sglt2-pp, 8 Oct: ours is HHF, the trials' primary is MACE -- K2 had read MACE sentences as ours)
    if any(names_our_outcome(m.group(1), kws) for m in
           re.finditer(r"primary (?:efficacy )?(?:outcome|end ?point) (?:was|were|for both studies was)\s+([^.]{5,300})",
                       abstract or "", re.I)):
        kws += ["primary efficacy outcome", "primary outcome"]
    for s in sents:
        if not any(k in s.lower() for k in kws):
            continue
        hits = []
        for m in _XN.finditer(s):
            x, n, p = _int(m.group(1)), _int(m.group(2)), float(m.group(3))
            if x is None or n is None or not _pct_ok(x, n, p):
                continue
            hits.append((m, x, n, p))
        mode = "X_OF_N"
        if len(hits) != 2:
            hits, mode = [], "EVENTS_PLUS_N"
            for m in _XE.finditer(s):
                x, p = _int(m.group(1)), float(m.group(2))
                if x is not None:
                    hits.append((m, x, None, p))
        if len(hits) != 2:
            continue
        roles = []
        for m, *_ in hits:
            # the arm named INSIDE the match ('51 events with enoxaparin-vitamin K antagonist [3.0%') or right after it,
            # up to the next comparison word ('... in the apixaban group, as compared with ...')
            inside = re.sub(r"^\d[\d,]*", "", m.group(0))
            ctx = re.split(r"[;,]\s*(?:as compared|vs|versus|and|compared)", s[m.end():m.end() + 120])[0]
            roles.append(_arm_named(inside, t) or _arm_named(ctx, t))
        if None in roles and roles.count(None) == 1:
            pre = _arm_named(s[:hits[0][0].start()][-160:], t)            # 'rivaroxaban had ... (36 events [2.1%] vs 51 ...'
            roles = [pre if r is None and i == 0 else r for i, r in enumerate(roles)]
        if sorted(r or "" for r in roles) != ["control", "intervention"]:
            return None, f"ARMS_NOT_NAMED: {roles}"
        it, ct = (hits[0], hits[1]) if roles[0] == "intervention" else (hits[1], hits[0])
        if mode == "EVENTS_PLUS_N":
            nt = _n_given(abstract, t, "intervention")
            nc = _n_given(abstract, t, "control")
            nsrc = "abstract"
            if nt is None or nc is None:
                if not aact_n:
                    return None, "N_NOT_PRINTED"
                nt, nc, nsrc = aact_n[0], aact_n[1], aact_n[2]
            if not (_pct_ok(it[1], nt, it[3]) and _pct_ok(ct[1], nc, ct[3])):
                return None, f"PERCENT_DOES_NOT_CORROBORATE: {it[1]}/{nt} {it[3]}%, {ct[1]}/{nc} {ct[3]}%"
        else:
            nt, nc, nsrc = it[2], ct[2], "abstract"
        return {"source_kind": "TEXT", "rule": "K2", "n_source": nsrc,
                "values": {"events_t": it[1], "n_t": nt, "events_c": ct[1], "n_c": nc},
                "span": s.strip()[:700]}, None
    return None, "NO_PRIMARY_SENTENCE_WITH_TWO_CORROBORATED_ARMS"


def _n_given(abstract, t, role):
    import g1_outcomes as go
    # the arm phrase stops at ' and <number>': '1731 given rivaroxaban and 1718 given enoxaparin' names ONE arm each
    for m in re.finditer(_NGIVEN + r"((?:(?!\s+and\s+\d)[^,;.]){3,80})", abstract or ""):
        if go._arm(m.group(2), t) == role:
            return _int(m.group(1))
    return None


def aact_n_of_primary(nct, slug):
    """(n_t, n_c, label) -- the posted analysis denominators of the ONE posted outcome that names our primary, when the
    measurement itself is a percentage (EINSTEIN-PE): used ONLY as N for K2, never for events."""
    import g1_tracker as gt
    import g1_outcomes as go
    from kgap import aact_adapter as aa
    t = topic(slug)
    po = t["primary_outcome"]
    kws = [k for k in po.get("keywords") or [] if len(k) >= 4]
    outs = [r for r in _rows("outcomes.txt", nct) if (r.get("outcome_type") or "").upper() == "PRIMARY"
            and gt.binding_verdict(po["name"], kws, r.get("title"), 2)["verdict"] == "BINDABLE"]
    if len(outs) != 1:
        return None
    oid = outs[0]["id"]
    titles = {r["ctgov_group_code"]: r.get("title") for r in _rows("result_groups.txt", nct) if r.get("outcome_id") == oid}
    groups = [(titles.get(r["ctgov_group_code"]), 0, _int(r.get("count"))) for r in _rows("outcome_counts.txt", nct)
              if r["outcome_id"] == oid and (r.get("scope") or "").lower() == "measure"]
    v, _ = go._two_arms(groups, t)
    return (v[1], v[3], f"AACT {nct} outcome {oid} analysis denominators") if v else None


def bind(slug, label, pmid, nct):
    recs = {r["id"]: r for r in _j(os.path.join(ROOT, "cache", slug, "records.json"))["records"]}
    out = {"slug": slug, "label": label, "pmid": pmid, "ncts": [nct] if nct else [], "own_tuple": True, "tuple_kind": "COUNTS",
           "outcome": topic(slug)["primary_outcome"]["name"]}
    refusals = []
    if nct:
        b, refusals = aact_counts(nct, slug)
        if b:
            return dict(out, **b, refused_alternatives=refusals)
    ab = (recs.get(pmid) or {}).get("abstract") or ""
    b, why = abstract_counts(ab, slug, aact_n_of_primary(nct, slug) if nct else None)
    if b:
        return dict(out, **b, source=f"PMID {pmid} abstract", refused_alternatives=refusals)
    return dict(out, state="NOT_BOUND", why=why, aact_refusals=refusals)


def main(args):
    data = _j(OUT) if os.path.exists(OUT) else {"bindings": [], "not_bound": []}
    prefetch([(a.split("=", 1)[1].split(":") + [None, None, None])[2] for a in args])
    for a in args:
        slug, rest = a.split("=", 1)
        label, pmid, nct = (rest.split(":") + [None, None])[:3]
        r = bind(slug, label, pmid or None, nct or None)
        key = (slug, label)
        data["bindings"] = [b for b in data["bindings"] if (b["slug"], b["label"]) != key]
        data["not_bound"] = [b for b in data["not_bound"] if (b["slug"], b["label"]) != key]
        (data["not_bound"] if r.get("state") == "NOT_BOUND" else data["bindings"]).append(r)
        v = r.get("values") or {}
        print(slug, "|", label, "|", r.get("state") or r["rule"], v.get("events_t"), v.get("n_t"), v.get("events_c"),
              v.get("n_c"), "|", r.get("why") or r.get("source"), flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


# ---------------------------------------------------------------------------------------------------------------- K3
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "counts_acquire")


def k3_items():
    """One recorded read per target K1 and K2 left NOT_BOUND: g1_trial_acquire.evidence (AACT posted results + prompt-open
    regulatory windows + a CC full text if any), the topic's primary outcome; only targets with an open source."""
    import g1_trial_acquire as ta
    data = _j(OUT)
    items, skipped = [], []
    for nb in data["not_bound"]:
        cfg = topic(nb["slug"])
        tg = {"slug": nb["slug"], "label": nb["label"], "pmid": nb.get("pmid"), "ncts": nb.get("ncts") or []}
        ev, held = ta.evidence(tg, cfg, str(cfg["comparator_pmid"]))
        if not any(a.get("state") == "POSTED" for a in ev["aact"].values()) and not held["text"] and not ev.get("regulatory"):
            skipped.append((nb["slug"], nb["label"], "NO_OPEN_SOURCE"))
            continue
        p = (ta.INSTR + "\n\n=== EVIDENCE ===\n" + json.dumps(ev, ensure_ascii=False, indent=0, default=str)).encode("utf-8")
        import hashlib
        items.append({"key": f"countsacq::{nb['slug']}::{nb['label']}", "slug": nb["slug"], "label": nb["label"],
                      "prompt": p, "schema": ta.SCHEMA, "_held": held, "_cfg": cfg, "_nb": nb,
                      "digests": [{"ref": "evidence", "sha256": hashlib.sha256(p).hexdigest(),
                                   "what": "inline evidence: AACT snapshot rows, prompt-open FDA / EMA windows, CC text "
                                           "(g1_trial_acquire.evidence, topic primary outcome)"}]})
    return items, skipped


def cmd_k3(run=False):
    import hashlib
    import g1_swap as sw
    import g1_trial_acquire as ta
    from kgap import runs_store
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    import k_gap_forest_plot as fp
    runs = runs_store.load()
    items, skipped = k3_items()
    done = lambda it: (runs.get(it["key"]) or {}).get("prompt_sha256") == hashlib.sha256(it["prompt"]).hexdigest() and \
        (runs.get(it["key"]) or {}).get("state") == "RAN_OK" and \
        os.path.exists(os.path.join(REC_DIR, str(runs[it["key"]].get("record_id")) + ".json"))
    print("K3 items", len(items), "skipped", skipped, "recovered", sw.recover(items, runs, REC_DIR), flush=True)
    if run:
        sw._run_calls([it for it in items if not done(it)], runs, REC_DIR, mcl, ms, fp, sorted({it["slug"] for it in items}),
                      purpose=lambda it: f"G1 counts (close-4, staged for D12): {it['slug']} / {it['label']} -- open "
                                         f"sources only, g1_trial_acquire gates", line="k3", batch="countsacq",
                      caller_file="scripts/g1_binding_counts.py")
    data = _j(OUT)
    for it in items:
        nb = it["_nb"]
        if not done(it):
            nb["k3"] = {"state": "NOT_RUN"}
            continue
        rid = runs[it["key"]]["record_id"]
        resp = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, rid + ".json"))).decode("utf-8"))
        verdict, adm = ta.gate(resp, it["_held"], it["_cfg"], it["slug"])
        w = (adm or {}).get("row")
        v = {k: getattr(w, k, None) for k in ("events_t", "n_t", "events_c", "n_c")} if w is not None else {}
        if verdict == "ADMITTED" and all(isinstance(v.get(k), int) for k in v) and len(v) == 4:
            data["not_bound"] = [b for b in data["not_bound"] if (b["slug"], b["label"]) != (nb["slug"], nb["label"])]
            data["bindings"].append({k: nb.get(k) for k in ("slug", "label", "pmid", "ncts", "outcome")} |
                                    {"own_tuple": True, "tuple_kind": "COUNTS", "rule": "K3", "source_kind": adm["kind"],
                                     "source": adm["source"], "values": v, "span": adm.get("span"), "quote": adm.get("quote"),
                                     "record_id": rid})
            print(it["slug"], it["label"], "K3 ADMITTED", v, adm["source"][:90], flush=True)
        else:
            for b in data["not_bound"]:
                if (b["slug"], b["label"]) == (nb["slug"], nb["label"]):
                    b["k3"] = {"state": verdict, "record_id": rid, "model_verdict": resp.get("verdict"),
                               "why": (resp.get("why") or "")[:300]}
                    if verdict == "ADMITTED":
                        # the gate admitted an EFFECT (VERTIS-CV: AACT HR 0.70) -- not per-arm counts, so not a D12 binding
                        b["k3"]["admitted_tuple_not_counts"] = {k: getattr(w, k, None) for k in ("measure", "effect",
                                                                                                "lower", "upper")}
                        b["k3"]["admitted_source"] = adm.get("source")
            print(it["slug"], it["label"], "K3", verdict, (resp.get("why") or "")[:120], flush=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if sys.argv[1:2] == ["k3"]:
        cmd_k3(run="--run" in sys.argv)
    else:
        main(sys.argv[1:])
