"""Offline replay of every topic's recorded comparator proposal; JSON on stdout."""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.comparator_extract import norm
from harness.meta_match import _join, match, value
from harness.proposal_gate import to_comparator, verify
from harness.trial_family import load_registry


def metric(items, denominator):
    return {"n": len(items), "N": denominator, "n_of_N": f"{len(items)} of {denominator}", "items": items}


def link_for_comparison(review, comparator, registry):
    """Resolve accepted labels using exact held registry acronyms, never knowledge.

    Enrich copies only. No proposal numeric value is filled from the registry.
    Publication links use held review-family reports or registry study_references.
    Ambiguous aliases and conflicting strong identifiers are never overwritten.
    """
    review, comparator = deepcopy(review), deepcopy(comparator)
    acronyms, reports = defaultdict(set), defaultdict(set)
    for nct, entry in registry.items():
        if not re.fullmatch(r"NCT\d{8}", nct):
            continue
        for row in entry.get("raw", {}).get("studies", []):
            if row.get("nct_id") == nct and row.get("acronym"):
                acronyms[norm(row["acronym"])].add(nct)
        for row in entry.get("raw", {}).get("study_references", []):
            if row.get("nct_id") == nct and row.get("pmid"):
                reports[str(row["pmid"])].add(nct)
    for family in review.get("trial_families", []):
        ncts = set(re.findall(r"\bNCT\d{8}\b", str(family.get("family_id", ""))))
        if len(ncts) == 1:
            for report in family.get("reports", []):
                rid = str(report.get("report_id", ""))
                if re.fullmatch(r"\d{6,9}", rid):
                    reports[rid].update(ncts)
    links = []
    for row in comparator["trial_set"]:
        if value(row, "registration") is not None:
            continue
        candidates = acronyms.get(norm(row["label"]), set())
        if len(candidates) == 1:
            nct = next(iter(candidates))
            row["registration"] = nct
            links.append({"side": "comparator", "label": row["label"], "registration": nct,
                          "source": "family_registry.raw.studies.acronym", "rule": "unique_exact_normalized_acronym"})
    for outcome in review.get("outcomes", []):
        for row in outcome.get("trials", []):
            rid = str(row.get("label", ""))
            if not re.fullmatch(r"\d{6,9}", rid):
                m = re.fullmatch(r"PMID\s+(\d{6,9})", str(row.get("id", "")))
                rid = m[1] if m else ""
            candidates = reports.get(rid, set())
            if len(candidates) == 1 and not row.get("registration") and not row.get("nct"):
                row["registration"] = next(iter(candidates))
                if outcome.get("primary"):
                    links.append({"side": "ours", "label": row.get("label"), "registration": row["registration"],
                                  "source": "held review family report / registry study_references",
                                  "rule": "unique_report_to_registration"})
    rows = comparator["trial_set"]
    if any(_join(a, b) for i, a in enumerate(rows) for b in rows[i + 1:]):
        comparator["membership_complete"] = False
    return review, comparator, links


def census(root=ROOT):
    root = Path(root)
    topics = sorted((root / "topics").glob("*.json"))
    all_fields, topic_rows, trials, ks, kmatches, refusals, missing = [], [], [], [], [], [], []
    gap_topics = defaultdict(set)
    for topic_path in topics:
        slug = topic_path.stem
        topic = json.loads(topic_path.read_text(encoding="utf-8"))
        entry = {"slug": slug, "comparator_pmid": str(topic.get("comparator_pmid", "")),
                 "accepted_k": None, "our_k": None, "K_MATCH": "UNKNOWN", "gaps": [],
                 "trials": [], "identity_links": []}
        review_path = root / "docs/reviews" / slug / "review.json"
        review = json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else None
        if review is not None:
            primary = [o for o in review.get("outcomes", []) if o.get("primary") is True and
                       norm(o.get("name")) == norm(topic["primary_outcome"]["name"])]
            if len(primary) == 1:
                pool = primary[0].get("result") or {}
                refused = pool.get("present") is False or pool.get("suppressed_incompatible") or pool.get("pool_refused")
                entry["our_k"] = None if refused else len(primary[0].get("trials", []))
                entry["our_pool_state"] = "WITHHELD_OR_REFUSED" if refused else "PRESENT"
        proposal_path = root / "evidence/g1_proposals" / (slug + ".json")
        if not proposal_path.exists():
            missing.append(slug)
            entry["gaps"].append("NO_PROPOSAL")
            panel_path = root / "cache" / slug / "comparators.json"
            entry["source_state"] = "NO_COMPARATOR_PANEL" if not panel_path.exists() else "PROPOSAL_MISSING"
            entry["fields"] = metric([], 0)
        else:
            p = json.loads(proposal_path.read_text(encoding="utf-8"))
            checked = verify(p, root)
            entry["gate_status"] = checked["status"]
            entry["scope_note"] = p["scope_note"]
            entry["trial_set_scope"] = p.get("trial_set_scope", "included_studies_only")
            entry["not_found"] = p["not_found"]
            fs = [{"item": slug + "::" + f["path"], **f} for f in checked["fields"] if f["status"] != "not_proposed"]
            all_fields.extend(fs)
            entry["fields"] = metric([f["path"] for f in fs if f["status"] == "accepted"], len(fs))
            entry["rejected_fields"] = [f for f in fs if f["status"] == "rejected"]
            entry["gaps"] += sorted({x.split(":", 1)[0] for x in p["not_found"]})
            if checked["accepted"] is None:
                refusals.append({"item": slug, "reason": checked["reason"]})
                entry["gaps"].append(checked["reason"])
            else:
                c = to_comparator(p, root)
                entry["accepted_k"] = value(c["pooled"], "k")
                if entry["accepted_k"] is not None:
                    ks.append(slug)
                if review is None:
                    entry["gaps"].append("REVIEW_NOT_HELD")
                else:
                    registry = load_registry(root, slug)
                    linked_review, linked_c, links = link_for_comparison(review, c, registry)
                    # Citation identities come only from the hash-verified held comparator.
                    from harness.inventory_queue import source, resolve
                    _, text, _ = source(slug, root)
                    for row in linked_c["trial_set"]:
                        proposed = [r for r in p["trials"] if r["label"] == row["label"]]
                        if len(proposed) == 1:
                            resolved, _, _, _ = resolve(proposed[0], text)
                            for key in ("doi", "pmid", "nct", "author", "year"):
                                if resolved.get(key) is not None and value(row, key) is None:
                                    row[key] = resolved[key]
                    diff = match(linked_review, linked_c, root=root)
                    entry["K_MATCH"] = diff["K_MATCH"]
                    entry["identity_links"] = links
                    entry["trials"] = diff["trials"]
                    if diff["K_MATCH"] == "yes":
                        kmatches.append(slug)
                    for i, row in enumerate(diff["trials"]):
                        trials.append({"item": f"{slug}::{i}::{row['label']}", **row})
                        if row["status"] != "MATCH":
                            entry["gaps"].append(row["status"] + "/" + str(row.get("reason") or row.get("our_state") or ""))
        compared = [r for r in entry["trials"] if r["side"] == "comparator"]
        entry["identity_census"] = {status: metric([r["label"] for r in compared if r["status"] == status], len(compared))
            for status in ("MISSING_FROM_OURS", "IN_INVENTORY_UNPOOLED", "MATCH", "VALUE_DIFFERS", "ABSTAIN")}
        entry["unpooled_by_state"] = {state: metric([r["label"] for r in compared if state in r.get("our_states", [])], len(compared))
            for state in sorted({s for r in compared for s in r.get("our_states", [])})}
        entry["gaps"] = sorted(set(entry["gaps"]))
        for gap in entry["gaps"]:
            gap_topics[gap].add(slug)
        topic_rows.append(entry)
    rules = {}
    for status in ("accepted", "rejected"):
        rules["field_" + status] = metric([f["item"] for f in all_fields if f["status"] == status], len(all_fields))
    for reason in sorted({f["reason"] for f in all_fields if f["reason"]}):
        rules[reason] = metric([f["item"] for f in all_fields if f["reason"] == reason], len(all_fields))
    for status in ("MATCH", "VALUE_DIFFERS", "MISSING_FROM_OURS", "IN_INVENTORY_UNPOOLED", "EXTRA_IN_OURS", "ABSTAIN"):
        denominator = sum(t["side"] == ("ours" if status == "EXTRA_IN_OURS" else "comparator") for t in trials)
        if status == "ABSTAIN":
            denominator = len(trials)
        rules[status] = metric([t for t in trials if t["status"] == status], denominator)
    for key in ("ncts", "dois", "pmids", "acronyms", "author_years"):
        rules["identity_join/" + key] = metric([r["item"] for r in trials
            if r.get("identity_join", {}).get("status") == "JOINED" and r["identity_join"].get("key") == key],
            sum(r["side"] == "comparator" for r in trials))
    rules["REFUSED_AMBIGUOUS_IDENTITY"] = metric([r["item"] for r in trials
        if r.get("reason") == "AMBIGUOUS_IDENTITY"], sum(r["side"] == "comparator" for r in trials))
    # Keep zero-hit refusal rules visible; absence of a defect is not a missing rule.
    numeric = {"k", "effect", "ci_low", "ci_high", "events_1", "n_1", "events_2", "n_2"}
    checks = {}
    for name, applicable, reasons in (
        ("span_containment", all_fields, {"REFUSED_SPAN_NOT_HELD", "REFUSED_SPAN_OUTSIDE_COMPARATOR_RECORD"}),
        ("typed_numeric_binding", [f for f in all_fields if f["path"].split(".")[-1] in numeric],
         {"REFUSED_NONFINITE_OR_NONNUMERIC", "REFUSED_COUNT_TYPE_OR_RANGE", "REFUSED_NUMBER_ROLE_NOT_IN_OWN_SPAN"}),
        ("literal_identity_and_measure", [f for f in all_fields if f["path"].split(".")[-1] not in numeric],
         {"REFUSED_STRING_TYPE", "REFUSED_LITERAL_NOT_IN_OWN_SPAN", "REFUSED_REGISTRATION_TYPE", "REFUSED_PMID_ROLE", "REFUSED_MEASURE_TYPE"}),
        ("interval_and_count_consistency", [f for f in all_fields if f["path"].split(".")[-1] in numeric],
         {"REFUSED_INTERVAL_ORDER", "REFUSED_RATIO_RANGE", "REFUSED_EVENTS_EXCEED_N", "REFUSED_MIXED_ESTIMATE_BINDINGS"}),
        ("relayed_not_data", all_fields, {"REFUSED_RELAYED_NOT_DATA"}),
    ):
        checks[name] = metric([f["item"] for f in applicable if f["reason"] in reasons], len(applicable))
    checks["source_or_schema_refused"] = metric(refusals, len(topics) - len(missing))
    return {
        "interpretation": "Lexical acceptance verifies source support, not truth, eligibility or clinical equivalence. K_MATCH is literal cardinality under the recorded closest-scope proposal; no pool admission. Missing labels without a verified identity link do not prove actual trial absence. General included-study lists abstain on outcome membership; EXTRA requires recorded completeness plus accepted k, all labels and unique identities.",
        "denominators": "Field N is non-null proposed clinical leaf fields (scope, pooled, trial); metadata/spans/nulls excluded. Topic N is every topics/*.json. Trial status N is comparator rows except EXTRA (ours unmatched rows) and ABSTAIN (all diff rows).",
        "topics_with_proposal": metric([r["slug"] for r in topic_rows if r["slug"] not in missing], len(topics)),
        "accepted_pooled_k": metric(ks, len(topics)), "K_MATCH": metric(kmatches, len(topics)),
        "rules": rules, "gate_checks_flagged": checks, "topics": topic_rows, "source_refusals": refusals,
        "open_by_prevalence": [{"gap": gap, **metric(sorted(slugs), len(topics))}
            for gap, slugs in sorted(gap_topics.items(), key=lambda x: (-len(x[1]), x[0]))],
    }


if __name__ == "__main__":
    print(json.dumps(census(), ensure_ascii=False, sort_keys=True, indent=2))
