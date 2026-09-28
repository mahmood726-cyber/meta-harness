"""FAMILY INVARIANT: every quantitative input belongs to exactly ONE adjudicated family, and the number of contributing
families equals the number of independent populations actually analysed.

Metformin-PCOS (2026-09-27): three trials were pooled for ovulation while the family count said '1 contributing
family' -- the two trials without a registry link were 'unresolved report candidates', outside the family count, while
their data were in the pool. They now carry a stable publication-anchored identity (PMID:<primary report>) and count.

  problems(review) -> blocking FAMILY_INVARIANT for
    * a pooled input with no family, or with a family that is not in the review's trial families;
    * one family pooled twice in one outcome (two reports of one trial counted as two populations);
    * a contributing-family count that differs from the number of distinct families behind the pooled inputs.
"""
from __future__ import annotations

from typing import Any


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    fams = {f.get("family_id"): f for f in review.get("trial_families") or []}
    chain = review.get("family_count_chain") or {}
    if not fams or not chain:
        return []
    out, contributing = [], set()
    for o in review.get("outcomes") or []:
        seen = {}
        for t in o.get("trials") or []:
            fid = t.get("family_id")
            if not fid or fid not in fams:
                out.append({"kind": "FAMILY_INVARIANT", "report_id": str(t.get("id")),
                            "detail": f"{o.get('name')}: input {t.get('id')} belongs to no adjudicated family ({fid!r})"})
                continue
            if fid in seen:
                out.append({"kind": "FAMILY_INVARIANT", "report_id": str(t.get("id")),
                            "detail": f"{o.get('name')}: {t.get('id')} and {seen[fid]} are the same family {fid}, pooled twice"})
            seen[fid] = t.get("id")
            contributing.add(fid)
    if contributing and chain.get("contributing") != len(contributing):
        out.append({"kind": "FAMILY_INVARIANT", "report_id": "family_count_chain",
                    "detail": (f"the family count says {chain.get('contributing')} contributing famil(ies); the pooled inputs "
                               f"come from {len(contributing)} independent populations: {sorted(contributing)}")})
    # ONE RECORD, ONE DESIGN DECISION (sacubitril-HFrEF, PARALLEL-HF): a family that contributes data may not have one
    # of its reports excluded for its DESIGN -- the trial is either eligible by design or it is not. The publication
    # read as 'not double-blind' from an abstract that is silent on masking, while the same trial pooled via its
    # registry (and the paper's full text says double-blind), was that contradiction.
    rules = {str(r.get("id")): r for r in (review.get("screening") or {}).get("records") or []}
    for fid in sorted(contributing):
        for rep in fams[fid].get("reports") or []:
            r = rules.get(str(rep.get("report_id"))) or {}
            if r.get("decision") == "exclude" and r.get("rule_id") == "X-DESIGN":
                out.append({"kind": "FAMILY_DESIGN_CONFLICT", "report_id": str(rep.get("report_id")),
                            "detail": (f"family {fid} contributes pooled data while its report {rep.get('report_id')} is "
                                       f"excluded for its design ({r.get('reason')})")})
    return out
