"""ADMITTED-BY-TRACKER count for the forest reader's rows, and the PRE-FILTER that spends reads only on metas whose own
words can pass admission (5 Oct, after the captain's recount: 0 accepted rows reached the tracker).

  admission  every row of an ACCEPTED / ACCEPTED_SECOND_SOURCE_ONLY figure is built EXACTLY as secondary_meta_build's
             dual-row hook builds it (SecondaryRow from the row; timepoint = the figure caption's, else the meta's text
             for a core-mortality topic) and run through the tracker's OWN gate, harness.secondary_meta.admit, with the
             topic's spec (secondary_meta_build.spec_of: the registered protocol's estimand, outcome keywords, core,
             timepoint) and the build's family resolver (family_of_factory(our_trials(slug))). Nothing is loosened.
             A row is ADMITTED when admit() leaves it un-REFUSED. Caveat: our_trials here runs without the untracked
             local AACT store, so family resolution can only be weaker than the captain's; the count is a lower bound.
  prefilter  before a read: the candidate figure's caption must pass outcome_identity; its caption or the meta's own
             text must state the protocol's timepoint (when one with a length is registered); and the meta must state
             the protocol's measure (hazard ratio for HR topics; for RR/OR topics a risk/odds-ratio statement or
             per-arm counts in the figure). The family gate needs the trial in OUR pool and cannot be pre-checked.

    python scripts/g1_admission_check.py SLUG ...        -> registry/model_proposals/g1_forest_admission.json
"""
from __future__ import annotations

import collections
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402
import secondary_meta_build as smb  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402

OUT = os.path.join(ROOT, "registry", "model_proposals", "g1_forest_admission.json")
MEASURE_WORDS = {"HR": r"hazard ratio|\bHRs?\b",
                 "RR": r"risk ratio|relative risk|\bRRs?\b|rate ratio",
                 "OR": r"odds ratio|\bORs?\b"}


def rows_as_hook(slug, spec):
    """[(figure_key, SecondaryRow)] exactly as the dual-row hook constructs them."""
    o = gfr._j(gfr.OUT)
    out = []
    figs = [(k, v) for sec in ("results", "meta_results") for k, v in o[sec].items()
            if (v.get("slug") or k.split("::")[0]) == slug and v.get("state") in ("ACCEPTED", gfr.SECOND_SOURCE_ONLY)]
    for key, v in figs:
        for d in v.get("secondary_rows") or []:
            pm = d["meta_pmid"]
            tp_text = smb.meta_timepoint(gfr.held_text(pm)) if spec.get("core") else None
            r = sm.SecondaryRow(**{k: x for k, x in d.items() if k in sm.SecondaryRow.__dataclass_fields__})
            r.timepoint = smb.meta_timepoint(r.outcome_definition) or tp_text
            out.append((key, r))
    return out


def admission(slug):
    spec = smb.spec_of(slug)
    fam = smb.family_of_factory(smb.our_trials(slug))
    res = collections.defaultdict(lambda: {"rows": 0, "admitted": 0, "reasons": collections.Counter(), "admitted_rows": []})
    built = rows_as_hook(slug, spec)
    for _, r in built:
        sm.admit(r, spec, fam)
    sm.consolidate([r for _, r in built])          # the build's next step: one row per trial family per meta
    for key, r in built:
        f = res[key]
        f["rows"] += 1
        if r.state != sm.REFUSED:
            f["admitted"] += 1
            f["admitted_rows"].append({"label": r.trial_label, "family": r.family_id})
        for x in r.reasons:
            f["reasons"][re.sub(r"_\d+_ROWS_IN_META_\d+|:.*", "", x)] += 1
    figs = {k: {"rows": v["rows"], "admitted": v["admitted"], "reasons": dict(v["reasons"]),
                "admitted_rows": v["admitted_rows"]} for k, v in res.items()}
    comp = gfr.comparator_of(slug)
    nonc = {k: v for k, v in figs.items() if k != slug and k.split("::")[1] != comp}
    return {"spec": {k: spec[k] for k in ("estimand", "timepoint", "core")},
            "rows": sum(v["rows"] for v in figs.values()), "admitted": sum(v["admitted"] for v in figs.values()),
            # the new route takes data from NON-comparator sources only: the count that matters
            "noncomparator_rows": sum(v["rows"] for v in nonc.values()),
            "noncomparator_admitted": sum(v["admitted"] for v in nonc.values()),
            "figures": figs}


def prefilter(slug, pmid, caption, spec=None):
    """(passes, why) for a CANDIDATE figure before any read, from the meta's own words only."""
    spec = spec or smb.spec_of(slug)
    probe = sm.SecondaryRow(meta_pmid=pmid, meta_doi="", location={}, source_digest="", provenance="PREFILTER",
                            trial_label="x", measure=spec["estimand"], outcome_definition=caption[:300])
    why = []
    if sm.outcome_identity(probe, spec.get("keywords") or [], (), tuple(spec.get("core") or ())):
        why.append("CAPTION_NOT_THE_TOPICS_OUTCOME")
    text = gfr.held_text(pmid) or ""
    if sm._days(spec.get("timepoint") or "") is not None:
        probe.timepoint = smb.meta_timepoint(caption) or (smb.meta_timepoint(text) if spec.get("core") else None)
        if sm.timepoint_identity(probe, spec.get("timepoint")):
            why.append("TIMEPOINT_NOT_STATED_AS_PROTOCOL")
    est = spec["estimand"]
    pat = MEASURE_WORDS.get(est)
    if pat and not re.search(pat, caption + " " + text[:20000], re.I):
        why.append(f"MEASURE_{est}_NOT_STATED")
    return not why, why


def main(argv):
    slugs = [a for a in argv if not a.startswith("--")]
    out = gfr._j(OUT) if os.path.exists(OUT) else {}
    for s in slugs:
        out[s] = admission(s)
        a = out[s]
        print(f"{s}: admitted-by-tracker (non-comparator) {a['noncomparator_admitted']} of {a['noncomparator_rows']}"
              f"  [all rows incl. comparator {a['admitted']} of {a['rows']}]  spec {a['spec']}")
        for k, f in sorted(a["figures"].items(), key=lambda x: -x[1]["rows"]):
            print(f"   {k[:60]:60s} {f['admitted']}/{f['rows']} {f['reasons']}")
    gfr._save(OUT, out)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
