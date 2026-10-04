"""IMPORT THE TOPIC LANES' G1 RESULTS INTO THE TRACKER FORMAT (outputs/k_gap/g1/<slug>.json, schema_version 1).

A topic owned by another lane is never computed by this lane's batch: its result is taken from that lane's committed
artefact, PINNED by branch commit + blob sha256 (recorded as lane_source), and converted when the lane writes its own
format. The owners are listed in outputs/k_gap/g1_lanes.json:

    {"<slug>": {"lane": ..., "branch": "g1/noac", "path": "outputs/g1_noac/g1_noac.json", "format": "g1_noac_v1",
                "outcome": "stroke_se"}}

Formats:
  tracker_v1   the lane already writes the tracker schema: taken as is, g1_status (re)computed here
  g1_noac_v1   harness/g1_noac.py output: per-trial verification states are the LANE's, mapped without upgrading --
                 TWO_SOURCE_VERIFIED (two independent primary sources agree)       -> route PRIMARY
                 SINGLE_SOURCE / INCOMPARABLE / CONFLICT / SECONDARY_ONLY          -> route UNVERIFIED (reasons kept)
               pool membership, comparator rows and the result comparison come from this lane's tracker on the same
               topic (scripts/g1_tracker.topic); the lane's identities are recorded beside them

    python scripts/g1_import_lanes.py [SLUG ...]        (reads origin/<branch>; run `git fetch` first)
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "outputs", "k_gap")
LANES = os.path.join(OUT, "g1_lanes.json")
NOAC_STATE_ROUTE = {"TWO_SOURCE_VERIFIED": "PRIMARY"}       # everything else -> UNVERIFIED


def _git(*a):
    p = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)
    if p.returncode:
        raise RuntimeError(f"git {' '.join(a)}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p.stdout


def lane_artefact(spec):
    """(bytes, lane_source) of a lane's committed artefact at the CURRENT tip of its remote branch."""
    commit = _git("rev-parse", f"origin/{spec['branch']}").decode().strip()
    b = _git("show", f"{commit}:{spec['path']}")
    return b, {"lane": spec.get("lane"), "branch": spec["branch"], "commit": commit, "path": spec["path"],
               "sha256": hashlib.sha256(b).hexdigest(), "format": spec["format"]}


def with_lane_identities(slug, T, d):
    """A k-gap row with NO identity (empty ncts and pmids) takes the owning lane's MATCHED identity for the same label,
    with the lane's evidence basis recorded -- the lane resolved it deterministically (ROCKET AF: self-naming abstract
    + AACT study_references NCT00403767|21830957 + explicit NCT). A row that already has an identity is never changed."""
    import copy
    T = copy.deepcopy(T)
    ident = {i.get("label"): i for i in d.get("identities") or [] if i.get("state") == "MATCHED" and i.get("nct")}
    for t in T["trials"]:
        i = ident.get(t["label"]) if t["slug"] == slug else None
        if i and not (t.get("ncts") or t.get("pmids")):
            ev = next((e for e in i.get("evidence") or [] if e.get("pmid")), {})
            t["ncts"], t["pmids"] = [i["nct"]], ([ev["pmid"]] if ev.get("pmid") else [])
            t["identity_basis"] = [f"LANE:{ev.get('basis') or 'MATCHED'}"]
    return T


def from_g1_noac(slug, d, spec, T):
    import g1_tracker as gt
    T = gt.with_identity_chain(with_lane_identities(slug, T, d))
    o = gt.topic(slug, T)                                   # our pool / comparator side on the same topic
    rows = {r["nct"]: r for r in d.get("rows") or [] if r.get("outcome") == spec["outcome"]}
    ident = {i.get("nct"): i for i in d.get("identities") or [] if i.get("nct")}
    tk = {t["label"]: t for t in T["trials"] if t["slug"] == slug}
    for x in o["trials"]:
        ncts = (tk.get(x["label"]) or {}).get("ncts") or []
        nct = next((n for n in ncts if n in rows), None)
        if nct is None:                                      # our side may know the trial only by its lane identity
            nct = next((n for n, i in ident.items() if i.get("label") == x["label"] and n in rows), None)
        r = rows.get(nct)
        if r is None:
            x.update(route="NO_ROW", basis=f"{spec['branch']}: no row for outcome {spec['outcome']}",
                     g1_countable=False)
            continue
        st = (r.get("route") or {}).get("state")
        x["route"] = NOAC_STATE_ROUTE.get(st, "UNVERIFIED")
        x["basis"] = f"{spec['branch']} {st}" + (f": {', '.join((r.get('route') or {}).get('reasons') or [])}"
                                                 if (r.get("route") or {}).get("reasons") else
                                                 " (two independent primary sources agree)")
        x["g1_countable"] = x["route"] == "PRIMARY" and x["in_our_pool"]
        x["lane_identity"] = {k: (ident.get(nct) or {}).get(k) for k in ("label", "state", "nct")}
        x["lane_row"] = {"item": r.get("item"), "route": r.get("route"), "effect_route": r.get("effect_route")}
    # kgap's own two-PRIMARY-source verifications (scripts/g1_two_primary.py) are shown beside the lane's verdict. They
    # turn a row's route only when the POOLED input is the verified tuple; otherwise the swap is listed as pending.
    tp_p = os.path.join(OUT, "two_primary", f"{slug}.json")
    tp = {r["nct"]: r for r in (json.load(open(tp_p, encoding="utf-8")).get("rows") or [])} if os.path.exists(tp_p) else {}
    for x in o["trials"]:
        nct = (x.get("lane_identity") or {}).get("nct")
        v = tp.get(nct)
        if not v:
            continue
        x["kgap_two_primary"] = {k: v.get(k) for k in ("state", "measure", "registry", "regulator", "silent_axes")}
        ov = x.get("our_value") or {}
        pooled_is_tuple = v["state"] == "TWO_SOURCE_VERIFIED" and (ov.get("measure") or "").upper() == v["measure"] and \
            all(gt.sm._eq_printed(ov.get(a), v["registry"][a]) for a in ("effect", "lower", "upper"))
        if pooled_is_tuple:
            x["route"], x["g1_countable"] = "PRIMARY", x["in_our_pool"]
            x["basis"] += f" | kgap TWO_SOURCE_VERIFIED (AACT + regulator) on the pooled tuple"
        elif v["state"] == "TWO_SOURCE_VERIFIED":
            x["pending_input_swap"] = {"from": {k: ov.get(k) for k in ("measure", "effect", "lower", "upper")},
                                       "to": {"measure": v["measure"], **{k: v["registry"][k] for k in
                                                                          ("effect", "lower", "upper")}},
                                       "why": "the pooled input is not the two-source-verified tuple"}
            x["basis"] += (f" | kgap: {v['measure']} {v['registry']['effect']} ({v['registry']['lower']}-"
                           f"{v['registry']['upper']}) TWO_SOURCE_VERIFIED (AACT + regulator); pooled input differs")
    o["routes"] = dict(Counter(x["route"] for x in o["trials"]))
    co = ((d.get("comparator") or {}).get("outcomes") or {}).get(spec["outcome"]) or {}
    if co.get("effect"):
        e = co["effect"]
        o["comparator"] = {"outcome": spec["outcome"], "estimate": float(e["effect"]), "ci_low": float(e["lower"]),
                           "ci_high": float(e["upper"]), "scale": e.get("measure") or o["comparator"].get("scale")}
        o["comparator_basis"] = f"{spec['branch']}: comparator {spec['outcome']} as typed by the lane"
    o["lane_result_comparison"] = {k: (d.get("result_comparison") or {}).get(k)
                                   for k in ("point_agrees_at_comparator_precision", "method_difference")}
    o["lane_two_source_rule"] = d.get("two_source_rule")
    o.pop("same_trials_per_trial", None)
    wp = gt.whole_pool_comparison(dict(o, same_trials={}))
    if wp:
        o["same_trials"] = wp
    o["g1_status"] = gt.g1_status(o)
    return o


RESOLUTIONS = os.path.join(OUT, "g1_readers_differ_resolutions.json")


def apply_resolutions(slug, o, path=RESOLUTIONS):
    """A lane trial whose two readers of the comparator's figure differ (READERS_DIFFER:...) takes the comparator row
    that scripts/g1_forest_adjudicate.py RESOLVED (two new model families + the row's own printed arithmetic / row
    identity), and its agreement is recomputed against it by the tracker's own rule. The resolution is attached; an
    unresolved or refused case leaves the lane's READERS_DIFFER untouched."""
    import re
    import g1_tracker as gt
    from collections import Counter
    if not os.path.exists(path):
        return o
    res = json.load(open(path, encoding="utf-8")).get("resolutions") or {}
    fold = lambda s: re.sub(r"[^a-z0-9]", "", str(s or "").lower())  # noqa: E731
    for x in o.get("trials") or []:
        if not str(x.get("agreement_with_comparator_row") or "").startswith("READERS_DIFFER"):
            continue
        hit = next((v for v in res.values() if str(v.get("state", "")).startswith("RESOLVED")
                    and (v.get("case") or {}).get("slug") == slug and "probe_for" not in (v.get("case") or {})
                    and fold((v.get("case") or {}).get("row")) and fold(v["case"]["row"]) in fold(x.get("label"))), None)
        if not hit:
            continue
        c = hit["case"]
        row = dict(c["undisputed"], **hit["resolved"])
        theirs = gt._row({"meta_pmid": c["pmid"], "meta_doi": "", "location": {"kind": "figure", "id": c["fig_id"]},
                          "source_digest": c["image_sha256"], "provenance": "READERS_DIFFER_RESOLVED",
                          "trial_label": x.get("label"), "measure": (x.get("our_value") or {}).get("measure") or "HR",
                          "outcome_definition": "", **row})
        prev = x["agreement_with_comparator_row"]
        x["comparator_row"] = dict(row, measure=theirs.measure)
        x["agreement_with_comparator_row"] = gt.agreement(x.get("our_value"), theirs)
        dk = next(iter(hit["resolved"]))
        admits = ((hit.get("rounded") or {}).get(dk)) or []
        ours_v = str((x.get("our_value") or {}).get(dk) or "")
        if x["agreement_with_comparator_row"].startswith("DISAGREE") and ours_v in admits:
            # the comparator's OWN printed log[HR]/SE admit our printed value too: a one-unit rounding boundary, on
            # neither side -- named so, never called a comparator error
            x["disagreement_side"] = (f"ROUNDING_BOUNDARY: comparator {dk} {hit['resolved'][dk]} vs trial report "
                                      f"{ours_v}; the comparator's printed log[HR] {hit.get('log_hr')} / SE "
                                      f"{hit.get('se')} admit {admits} at printed precision -- neither side wrong")
        x["readers_differ_resolution"] = {"was": prev, "state": hit["state"], "resolved": hit["resolved"],
                                          "records": hit.get("records"), "basis": hit.get("basis"),
                                          "wrong_row_readers": hit.get("wrong_row_readers"),
                                          "source": "outputs/k_gap/g1_readers_differ_resolutions.json"}
    o["per_trial_agreement"] = dict(Counter(x["agreement_with_comparator_row"] for x in o.get("trials") or []
                                            if x.get("in_our_pool")))
    return o


def main(argv):
    import g1_tracker as gt
    lanes = json.load(open(LANES, encoding="utf-8"))
    T = json.load(open(os.path.join(OUT, "k_gap_table.json"), encoding="utf-8"))
    for slug, spec in lanes.items():
        if argv and slug not in argv:
            continue
        b, src = lane_artefact(spec)
        if spec["format"] == "tracker_v1":
            o = apply_resolutions(slug, json.loads(b.decode("utf-8")))
            try:
                o["g1_status"] = gt.g1_status(o)
            except (KeyError, TypeError) as exc:
                o["g1_status"] = {"state": "SCHEMA_INCOMPLETE", "why": f"{type(exc).__name__}: {exc}"}
        elif spec["format"] == "g1_noac_v1":
            o = from_g1_noac(slug, json.loads(b.decode("utf-8")), spec, T)
        else:
            raise ValueError(f"{slug}: unknown lane format {spec['format']}")
        o["lane_source"] = src
        # the lane's named scope differences must carry rule + span like ours; unspanned ones go back to eligible
        gt.cite_or_demote(o, slug)
        gt.apply_sweep(o, slug)           # trials the two-source sweep verified count as matched, by route
        gt.apply_single_primary(o)        # ONE_SOURCE rows bound to a single PRIMARY source, typed (2 Oct decision)
        gt.attach_forest_reader_provenance(o, slug)   # dual-read provenance for rows whose counts it prints identically
        if not (o.get("g1r_reproduction") or {}).get("state"):
            o["g1r_reproduction"] = gt.g1r_from_trials(o)
        gt.demote_unstructured_secondary_single(o)   # prose-only provenance never counts (page rule)
        gt.apply_coverage(o)              # COVERAGE (incl. COMPARATOR_SOURCED) beside INDEPENDENTLY CONFIRMED
        bad = gt.scope_citation_violations(o)
        if bad:
            raise SystemExit(f"{slug}: lane artefact non-eligible without rule + span: {bad}")
        if "g1_status" in o and o["g1_status"].get("state") != "SCHEMA_INCOMPLETE":
            o["g1_status"] = gt.g1_status(o)
        p = os.path.join(gt.G1_DIR, f"{slug}.json")
        tmp = f"{p}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(o, fh, indent=1, ensure_ascii=False)
        os.replace(tmp, p)
        print(slug, "<-", src["branch"], src["commit"][:9], o["k_matched"], "of", o.get("N_eligible"),
              o["routes"], o["g1_status"]["state"], o["g1_status"].get("unmet"))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
