"""Typed primary-outcome diff. Absence of evidence never establishes parity."""
from __future__ import annotations
import math
import re
from .comparator_extract import norm
from .identity_join import join, our_identities, states, ROOT


def value(row, key):
    v = row.get(key)
    if isinstance(v, dict):
        return v.get("value") if v.get("status", "PARSED") == "PARSED" else None
    return v


def identities(row):
    raw = " ".join(str(value(row, k) or "") for k in ("registration", "nct", "pmid", "id", "family_id", "trial_family_id", "label"))
    nct = set(re.findall(r"\bNCT\d{8}\b", raw, re.I))
    pmid = set(re.findall(r"\bPMID\s*[: ]\s*(\d+)\b", raw, re.I))
    if value(row, "pmid"):
        pmid.add(str(value(row, "pmid")))
    label = str(value(row, "label") or "")
    if re.fullmatch(r"\d{6,9}", label):
        pmid.add(label)
        label = ""
    label = re.sub(r"\bet\s+al\.?", "", label, flags=re.I)
    label = re.sub(r"\[\s*\d+\s*\]|\(\s*\d{1,3}\s*\)", "", label)
    return [set(x.upper() for x in nct), pmid, {norm(label)} if label else set()]


def _join(a, b):
    return join(a, [b])["status"] == "JOINED"


def _ours(row, outcome):
    result = dict(row)
    effect = row.get("study_effect") or {}
    for key, aliases in {
        "n1": ("n1i",), "n2": ("n2i",), "events1": ("ai",), "events2": ("ci",),
        "measure": ("scale",), "timepoint": ("follow_up_window",), "population": ("analysis_set",),
    }.items():
        if value(result, key) is None:
            result[key] = next((row[x] for x in aliases if row.get(x) is not None), None)
    # Preserve only actual row values, not an outcome-wide presumed follow-up.
    if result.get("population") is None:
        result["population"] = effect.get("analysis_population")
    if result.get("measure") is None:
        result["measure"] = (row.get("effect_object") or {}).get("reported_label")
    if result.get("effect") is None:
        result["effect"] = effect.get("effect_estimate")
    return result


def _compare(ours, theirs):
    if any(isinstance(v, dict) and v.get("status") == "RELAYED" for row in (ours, theirs) for v in row.values()):
        return "ABSTAIN", "RELAYED_NOT_DATA"
    for field, reason in (("measure", "MEASURE_DIFFERS"), ("timepoint", "TIMEPOINT_DIFFERS"), ("population", "POPULATION_DIFFERS")):
        a, b = value(ours, field), value(theirs, field)
        if a is not None and b is not None and norm(a) != norm(b):
            return "VALUE_DIFFERS", reason
    comparable = False
    incomplete = False
    for field in ("n", "n1", "n2", "events1", "events2"):
        a, b = value(ours, field), value(theirs, field)
        if b is not None:
            if a is None:
                incomplete = True
            elif a != b:
                return "VALUE_DIFFERS", "COUNTS_DIFFER"
            else:
                comparable = True
    for field in ("effect", "ci_low", "ci_high"):
        a, b = value(ours, field), value(theirs, field)
        if b is not None:
            if a is None:
                incomplete = True
            elif value(theirs, "measure") not in {"RR", "OR", "HR", "IRR"}:
                incomplete = True  # no log-scale rule for MD/SMD
            elif not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x > 0 for x in (a, b)):
                incomplete = True
            elif abs(math.log(a) - math.log(b)) > 0.005:
                return "VALUE_DIFFERS", "UNKNOWN"
            else:
                comparable = True
    if not comparable or incomplete or any(value(ours, x) is None or value(theirs, x) is None for x in ("timepoint", "population", "measure")):
        return "ABSTAIN", "UNPARSED_VALUES_OR_SCOPE"
    return "MATCH", None


def match(review: dict, comparator: dict, *, root=ROOT) -> dict:
    primary = comparator["primary_outcome"]
    outcomes = [o for o in review.get("outcomes", []) if o.get("primary") is True and norm(o.get("name")) == norm(primary)]
    if len(outcomes) != 1:
        rows = [{"label": r["label"], "side": "comparator", "status": "ABSTAIN", "reason": "PRIMARY_OUTCOME_UNRESOLVED"}
                for r in comparator.get("trial_set", []) if value(r, "outcome") is None or norm(value(r, "outcome")) == norm(primary)]
        return {"status": "ABSTAIN", "reason": "PRIMARY_OUTCOME_UNRESOLVED", "trials": rows, "K_MATCH": "UNKNOWN", "ESTIMATE_WITHIN_CI": "UNKNOWN"}
    outcome = outcomes[0]
    pool = outcome.get("result") or {}
    refused = pool.get("present") is False or pool.get("suppressed_incompatible") or pool.get("pool_refused")
    ours = [_ours(r, outcome) for r in outcome.get("trials", [])] if not refused else []
    all_theirs = comparator.get("trial_set", [])
    theirs = [r for r in all_theirs if norm(value(r, "outcome")) == norm(primary)]
    output = {"status": "DIFF", "trials": [], "K_MATCH": "UNKNOWN", "ESTIMATE_WITHIN_CI": "UNKNOWN"}
    for row in all_theirs:
        if value(row, "outcome") is None:
            output["trials"].append({"label": row["label"], "side": "comparator", "status": "ABSTAIN", "reason": "OUTCOME_UNPARSED"})
    inventory = our_identities(review.get("slug"), root, review)
    used = set()
    for row in theirs:
        linked = join(row, inventory)
        entry = {"label": row["label"], "side": "comparator", "identity_join": linked}
        hits = []
        if linked["status"] == "JOINED":
            node = inventory[linked["index"]]
            hits = [i for i, r in enumerate(ours) if join(r, inventory).get("index") == linked["index"]]
        duplicates = [r for r in theirs if _join(r, row)]
        if linked["status"] == "AMBIGUOUS" or len(hits) > 1 or len(duplicates) > 1:
            used.update(hits)
            entry.update(status="ABSTAIN", reason="AMBIGUOUS_IDENTITY")
        elif hits:
            i = hits[0]
            used.add(i)
            status, reason = _compare(ours[i], row)
            entry.update(status=status, reason=reason, our_label=ours[i].get("label"))
        elif linked["status"] == "JOINED":
            held_states = states(node, primary)
            entry.update(status="IN_INVENTORY_UNPOOLED", our_state=held_states[0], our_states=held_states)
        else:
            entry.update(status="MISSING_FROM_OURS", our_state="NOT_IN_INVENTORY")
        output["trials"].append(entry)
    for i, row in enumerate(ours):
        if i not in used:
            output["trials"].append({"label": row.get("label") or row.get("id"), "side": "ours", "status": "EXTRA_IN_OURS" if comparator.get("membership_complete") else "ABSTAIN", "reason": None if comparator.get("membership_complete") else "COMPARATOR_MEMBERSHIP_INCOMPLETE"})
    pooled = comparator.get("pooled", {})
    k = value(pooled, "k")
    if k is not None and not refused:
        output["K_MATCH"] = "yes" if len(ours) == k else "no"
    estimate, lo, hi = pool.get("estimate"), value(pooled, "ci_low"), value(pooled, "ci_high")
    if not refused and all(isinstance(x, (int, float)) and math.isfinite(x) for x in (estimate, lo, hi)) and pool.get("scale") == value(pooled, "measure"):
        output["ESTIMATE_WITHIN_CI"] = "yes" if lo <= estimate <= hi else "no"
    return output
