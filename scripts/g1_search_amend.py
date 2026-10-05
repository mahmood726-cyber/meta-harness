"""DATED PROTOCOL AMENDMENTS for the G1 search+screen audit's identification fixes -- the only way a registered search
changes (never silently). Per topic, from the recorded evidence:

  A1 REVIEW_REFERENCE_LIST (every topic with a comparator): the standing route -- the comparator's backward reference
     list (PubMed elink + Europe PMC) and forward citations, plus up to 2 other open metas' backward lists
     (reference_list_metas, chosen by the rule in scripts/g1_rrl_probe.py) -- with what it identifies, measured
     (outputs/search_audit/rrl_probe.json + SEARCH_SCREEN_AUDIT.json).
  A2 CT.gov pagination (topics whose registered CT.gov query was silently truncated at 30): no query change; the
     amendment records that the registered query is now retrieved in full (count today vs retained before).
  A3 Concept query (topics whose blind query audit ACCEPTED a proposal, outputs/search_audit/query_audit.json): the
     proposed PubMed query is ADDED to the registered ones (union; nothing removed), with its measured volume and the
     recall gain on the comparator's eligible trials, and the record id of the model call that proposed it.

Writes: topics/<slug>.json (reference_list_metas; pubmed_queries += accepted) and appends '## Amendment 2026-10-05 --
identification sources (search+screen audit)' to protocols/<slug>.md. Idempotent: a topic already carrying this
amendment is skipped. A summary goes to outputs/search_audit/amendments.json.

  python scripts/g1_search_amend.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SA = os.path.join(ROOT, "outputs", "search_audit")
DATE = "2026-10-05"
HEAD = f"## Amendment {DATE} -- identification sources (search+screen audit)"


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv):
    dry = "--dry-run" in argv
    audit = {t["slug"]: t for t in _j(os.path.join(SA, "SEARCH_SCREEN_AUDIT.json"))["topics"]}
    rrl = _j(os.path.join(SA, "rrl_probe.json"))["topics"]
    vol = _j(os.path.join(SA, "search_volume_probe.json"))["topics"]
    qa_p = os.path.join(SA, "query_audit.json")
    qa = _j(qa_p)["topics"] if os.path.exists(qa_p) else {}
    out = {}
    for slug, t in sorted(audit.items()):
        tp, pp = os.path.join(ROOT, "topics", f"{slug}.json"), os.path.join(ROOT, "protocols", f"{slug}.md")
        md = open(pp, encoding="utf-8").read() if os.path.exists(pp) else None
        if md is None:
            out[slug] = {"state": "NO_PROTOCOL_FILE (amendment not written)"}
            continue
        if HEAD in md:
            out[slug] = {"state": "ALREADY_AMENDED"}
            continue
        cfg = _j(tp)
        r, v, q = rrl.get(slug) or {}, vol.get(slug) or {}, qa.get(slug) or {}
        lines, changes = ["", HEAD, ""], {}
        # A1
        metas = r.get("reference_list_metas") or []
        if cfg.get("comparator_pmid"):
            changes["reference_list_metas"] = metas
            lines.append(
                f"- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID "
                f"{cfg['comparator_pmid']}) backward reference list (PubMed elink and Europe PMC) and its forward citations"
                + (f", and the backward reference lists of {len(metas)} other open meta-analys{'is' if len(metas) == 1 else 'es'} "
                   f"(PMID {', '.join(metas)}; rule: most trial rows read by the secondary-meta lane, ties to the newer)"
                   if metas else "; no other open meta-analysis is held for this topic yet")
                + f". Rationale: the registered search identified {t['search_recall']['n']} of {t['search_recall']['N']} of "
                f"the comparator's eligible trials; with this route and the full retrieval below, "
                f"{t['fixed_identification_recall']['n']} of {t['fixed_identification_recall']['N']} "
                f"({t['fixed_identification_recall_independent']['n']} of {t['fixed_identification_recall_independent']['N']} "
                f"without the comparator's own reference list, which contains its trials by construction). The route "
                f"retrieves {r.get('union_n')} records (recorded: outputs/search_audit/rrl_probe.json). Identification only: "
                f"every record still passes the registered screen.")
        # A2
        if v.get("ctgov_truncated"):
            lines.append(f"- **A2 ClinicalTrials.gov retrieval.** The registered query {json.dumps(v.get('ctgov_query'))} is "
                         f"unchanged. It returns {v.get('ctgov_count_today')} studies; the earlier retrieval kept the first "
                         f"{v.get('ctgov_retained')} (a one-page cap in harness.fetch, now paginated with the source's own "
                         f"total recorded).")
        # A3
        val = (q.get("validation") or {})
        if str(val.get("verdict", "")).startswith("ACCEPT"):
            pq = q["proposal"]["pubmed_query"]
            changes["pubmed_queries_added"] = [pq]
            lines.append(
                f"- **A3 Concept query added** (union with the registered queries; none removed): `{pq}`. Proposed blind "
                f"(the proposer saw the PICO and the current queries with their volumes, never the comparator's trials or "
                f"our misses; recorded call {q.get('record')}); returns {val.get('proposed_pubmed_count')} records today; on "
                f"the comparator's eligible trials the registered queries match {val['recall_current']['n']} of "
                f"{val['recall_current']['N']} and the union {val['recall_union']['n']} of {val['recall_union']['N']}. "
                f"Limitation: the proposer may know well-known trials from training.")
        elif val:
            lines.append(f"- **A3 Concept query: not adopted** ({val.get('verdict')}; recorded call {q.get('record')}).")
        if len(lines) <= 3:
            out[slug] = {"state": "NOTHING_TO_AMEND"}
            continue
        out[slug] = {"state": "AMENDED" if not dry else "DRY_RUN", "changes": changes, "text": "\n".join(lines[1:])}
        if dry:
            continue
        if "reference_list_metas" in changes:
            cfg["reference_list_metas"] = changes["reference_list_metas"]
        for pq in changes.get("pubmed_queries_added") or []:
            if pq not in (cfg.get("pubmed_queries") or []):
                cfg.setdefault("pubmed_queries", []).append(pq)
        with open(tp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(cfg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(pp, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(("\n" if not md.endswith("\n") else "") + "\n".join(lines) + "\n")
    json.dump(out, open(os.path.join(SA, "amendments.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    tally = {}
    for v in out.values():
        tally[v["state"]] = tally.get(v["state"], 0) + 1
    print(tally)


if __name__ == "__main__":
    main(sys.argv[1:])
