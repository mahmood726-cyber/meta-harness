"""Replay held G1 queue against the labelled search_v2 run. Offline; stdout only."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.g1_recall import read, candidate_records, recall_trial, metric, metrics, ceiling, screen
from harness.identity_join import identity, join, our_identities
from harness.inventory_queue import verify, source, resolve, build_queue
from harness.proposal_gate import to_comparator
from harness.trial_family import load_registry
from scripts.g1_proposal_census import census as baseline_census, link_for_comparison


def census(root=ROOT):
    root = Path(root)
    payload = read(root / "outputs/search_v2/candidates-2026-09-15r3-all.json")
    base = baseline_census(root)
    topics, all_rows, all_extras, all_included = [], [], [], []
    for baseline in base["topics"]:
        slug = baseline["slug"]
        topic = read(root / "topics" / (slug + ".json"))
        queue_path = root / "evidence/g1_inventory_queue" / (slug + ".json")
        entries = []
        if queue_path.exists():
            queue = read(queue_path)
            verify(queue, root, base)
            entries = queue["missing"]
        elif any(t["status"] == "MISSING_FROM_OURS" for t in baseline["trials"]):
            raise ValueError("REFUSED_MISSING_QUEUE:" + slug)
        entry = dict(slug=slug, comparator_k=baseline["accepted_k"], our_k=baseline["our_k"],
                     source_state=payload.get("topics", {}).get(slug, {}).get("state", "NOT_RUN"))
        try:
            records = candidate_records(root, payload, slug)
        except (ValueError, OSError) as exc:
            entry.update(refusal=str(exc), candidates=0)
            rows = [dict(item=slug + "::" + q["label"], label=q["label"], resolution=q["resolution"],
                         status="UNAVAILABLE", reason=str(exc)) for q in entries]
            extras, included = [], []
            entry["opposite_refusal"] = str(exc)
        else:
            entry["candidates"] = len(records)
            entry["sources_ran_error"] = payload["topics"][slug].get("sources_ran_error")
            ids = [{"identities": identity(r)} for r in records]
            rows = [dict(item=slug + "::" + q["label"], **recall_trial(q, records, topic, ids)) for q in entries]
            ours = our_identities(slug, root)
            comparator = None
            if (root / "evidence/g1_proposals" / (slug + ".json")).exists():
                p, text, _ = source(slug, root)
                c = to_comparator(p, root)
                _, c, _ = link_for_comparison(read(root / "docs/reviews" / slug / "review.json"), c, load_registry(root, slug))
                for row in c["trial_set"]:
                    proposals = [r for r in p["trials"] if r["label"] == row["label"]]
                    if len(proposals) == 1:
                        resolved, _, _, _ = resolve(proposals[0], text)
                        row.update({k: v for k, v in resolved.items() if k != "spans" and v is not None})
                comparator = [{"identities": identity(r)} for r in c["trial_set"]]
                entry["comparator_membership_complete"] = c["membership_complete"]
            else:
                entry["opposite_refusal"] = "REFUSED_COMPARATOR_MEMBERSHIP_UNAVAILABLE"
            extras, included, ambiguous = [], [], []
            for rec, rid in zip(records, ids):
                if screen(rec, topic)["decision"] != "include":
                    continue
                name = slug + "::" + str(rec["id"]) + "::" + (rec.get("title") or rec.get("acronym") or "")
                included.append(name)
                if comparator is None:
                    continue
                a, b = join(rid, ours), join(rid, comparator)
                if a["status"] == b["status"] == "NOT_JOINED":
                    extras.append(name)
                elif "AMBIGUOUS" in (a["status"], b["status"]):
                    ambiguous.append(name)
            entry["opposite_ambiguous"] = metric(ambiguous, len(included))
        entry.update(rules=metrics(rows), trials=rows, ceiling=ceiling(entry["our_k"], rows),
                     opposite_unmatched=metric(extras, len(included)), opposite_top20=extras[:20])
        if entry.get("refusal"):
            entry["ceiling"]["k"] = None
            entry["ceiling"]["additions"] = None
        topics.append(entry)
        all_rows.extend(rows)
        all_extras.extend(extras)
        all_included.extend(included)
    return dict(interpretation="Held snapshot recall only; source errors limit absence claims. Ambiguity abstains. Opposite counts are candidate records unmatched to held inventory and parsed comparator identities, not established new trials; incomplete comparator lists cannot prove absence. Ceilings assume distinct eligible trials and successful extraction; RELAYED rows never contribute. Unknown k remains null.",
                snapshot_name=payload["snapshot_name"], metadata_warning="Top-level _doc and stop_reason are stale; per-topic states and bound snapshot records determine coverage.",
                topics_examined=metric([t["slug"] for t in topics], len(list((root / "topics").glob("*.json")))),
                search_available=metric([t["slug"] for t in topics if not t.get("refusal")], len(topics)),
                rules=metrics(all_rows), opposite_unmatched=metric(all_extras, len(all_included)), topics=topics)


if __name__ == "__main__":
    print(json.dumps(census(), ensure_ascii=False, sort_keys=True, indent=2))
