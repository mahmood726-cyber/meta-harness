"""Arm orientation: which randomised group is experimental and which is reference, by AACT group id (lane OC, 2026-09-25).

Not in harness/: harness/armcontrast.py is pinned by every release certificate (analysis_code_blobs), so editing it would move
analysis_code_sha256 on every page, and every harness/*.py that no root imports is LISTED in the certificate's scope
(not_covered.in_tree_modules_not_imported_by_any_root), so even a new harness module is a certificate change. An integrity
change must not arrive ahead of the semantic one; this module reuses armcontrast's placebo normaliser and keyword matcher.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness.armcontrast import _kw_matches, _norm_intv  # noqa: E402
# ------------------------------------------------------------------------------------------------------------------------
# ORIENTATION (lane OC, 2026-09-25; external audit). contrast_status() above reduces each trial to (common, differing)
# sets: it proves the intervention of interest is PART OF the randomised difference and nothing more. It receives no
# effect tuple and no numerator/reference assignment, so its answer is invariant to reading 0.87 as drug/placebo or
# placebo/drug -- "parser-confirmed contrast" is an ELIGIBILITY statement, never a direction statement (the auditor's
# armcontrast_direction_probe.py, reproduced against this module in tests/test_ordered_contrast_arms.py).
# The functions below RETAIN the arms: which group is experimental and which is reference, with AACT group ids in F4's
# identity form "<NCT>:<design_group id>" (the arm_id of cache/<slug>/families.json), read from the committed,
# digest-bound AACT row bodies under docs/acquisitions/<slug>/aact_rows_*/rows.json. contrast_status() is unchanged, so
# no served review.json moves; the page wording that says what it claims is queued (evidence/ordered_contrast/).
CLAIM_SCOPE = ("ELIGIBILITY: the intervention of interest is part of the randomised difference (it differs across the "
               "randomised arms). It does NOT establish which arm is the numerator of any reported effect; that is the "
               "ordered contrast (BUNDLE.json analysis_identity.comparator_direction.ordered_contrast).")


class ArmRowsRefused(Exception):
    """The committed AACT row bodies do not reproduce their recorded digests -- no orientation is derived from them."""


def load_arm_groups(slug: str, root=None) -> dict:
    """{NCT: [{arm_id, group_id, group_type, title, active}]} from the newest committed aact_rows_* acquisition for `slug`.
    Every design_groups / interventions / design_group_interventions row must hash (sha256 of canonical JSON) to the digest
    recorded beside it; one mismatch refuses the whole load (fail closed). Absent acquisition -> {} (orientation unknown)."""
    import json
    from pathlib import Path
    from harness.canonical import canonical_json, sha256_text
    base = Path(root or Path(__file__).resolve().parents[1]) / "docs" / "acquisitions" / slug
    dirs = sorted(p for p in base.glob("aact_rows_*") if (p / "rows.json").is_file()) if base.is_dir() else []
    if not dirs:
        return {}
    doc = json.loads((dirs[-1] / "rows.json").read_text(encoding="utf-8"))
    tables = doc.get("tables") or {}
    for t in ("design_groups", "interventions", "design_group_interventions"):
        for r in tables.get(t) or []:
            if sha256_text(canonical_json(r.get("row"))) != r.get("sha256"):
                raise ArmRowsRefused(f"{dirs[-1].name}/rows.json {t} {r.get('keys')}: body does not hash to its recorded digest")
    return arm_groups_from_rows(tables)


def arm_groups_from_rows(tables: dict) -> dict:
    iv = {r["row"]["id"]: _norm_intv(r["row"].get("name")) for r in tables.get("interventions") or []}
    groups: dict[str, dict] = {}
    for r in tables.get("design_groups") or []:
        row = r["row"]
        n = (row.get("nct_id") or "").upper()
        groups.setdefault(n, {})[row["id"]] = {"arm_id": f"{n}:{row['id']}", "group_id": row["id"], "group_type": row.get("group_type"),
                                               "title": row.get("title"), "active": set()}
    for r in tables.get("design_group_interventions") or []:
        row = r["row"]
        g = groups.get((row.get("nct_id") or "").upper(), {}).get(row.get("design_group_id"))
        nm = iv.get(row.get("intervention_id"))
        if g is not None and nm:
            g["active"].add(nm)
    return {n: [dict(g, active=sorted(g["active"])) for _, g in sorted(gs.items())] for n, gs in groups.items()}


def oriented_contrast(nct: str, keywords, arm_groups: dict) -> dict:
    """Which randomised groups carry the intervention of interest (EXPERIMENTAL side) and which do not (REFERENCE side), by
    AACT group id. The side is decided by the coded active interventions (placebo/sham/usual care normalised away, as in
    measure_arm_index); the registry's own group_type is carried beside it as a second, independent witness and a
    disagreement is reported, not resolved. status uses contrast_status's vocabulary; claim_scope says what this is NOT."""
    groups = arm_groups.get((nct or "").upper())
    out = {"nct": (nct or "").upper(), "experimental_arms": [], "reference_arms": [], "claim_scope": CLAIM_SCOPE,
           "effect_direction": "NOT_ESTABLISHED_HERE"}
    if not groups or len(groups) < 2:
        return dict(out, status="unverified_no_arm_data", basis="no committed AACT arm rows for this trial")
    exp, ref = [], []
    for g in groups:
        (exp if _kw_matches(keywords, g["active"]) else ref).append(g)
    if not exp:
        return dict(out, status="unverified_granularity", basis="no coded group carries a keyword-matched active intervention")
    if not ref:
        return dict(out, status="background_only", basis="the intervention of interest is coded in EVERY randomised group")
    typed = {"EXPERIMENTAL": [g["arm_id"] for g in exp], "REFERENCE": [g["arm_id"] for g in ref]}
    disagree = [g["arm_id"] for g in exp if g.get("group_type") in ("PLACEBO_COMPARATOR", "SHAM_COMPARATOR", "NO_INTERVENTION")] + \
               [g["arm_id"] for g in ref if g.get("group_type") == "EXPERIMENTAL"]
    return dict(out, status="verified", experimental_arms=exp, reference_arms=ref, arm_ids=typed,
                basis="experimental = groups whose coded active interventions match the keywords; reference = the remaining groups",
                group_type_witness="AGREES" if not disagree else "DISAGREES: " + ", ".join(disagree))
