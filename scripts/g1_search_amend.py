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


if __name__ == "__main__" and not {"--round2", "--cap", "--active"} & set(sys.argv):
    main(sys.argv[1:])        # never re-run for --round2: it would overwrite amendments.json with ALREADY_AMENDED


HEAD2 = "## Amendment 2026-10-06 -- identification sources, query audit round 2 (search+screen audit)"


def round2(dry=False):
    """A4: blind concept queries ACCEPTED by round r2 (independent proposer, gpt-5.5) or by the precise variant (the
    over-cap topics, with a volume target): validated against the queries registered NOW (after the 2026-10-05
    amendment), so only a genuine further recall gain is admitted. ADDED, never replacing."""
    out = {}
    srcs = []
    for name, label in (("query_audit_r2.json", "round 2 (independent blind proposer)"),
                        ("query_audit_precise.json", "precision variant (over-cap topic, volume target, still blind)")):
        p = os.path.join(SA, name)
        if os.path.exists(p):
            srcs.append((label, _j(p)["topics"]))
    slugs = sorted({s for _, t in srcs for s in t})
    for slug in slugs:
        acc = [(label, t[slug]) for label, t in srcs if slug in t and
               str((t[slug].get("validation") or {}).get("verdict", "")).startswith("ACCEPT")]
        if not acc:
            continue
        tp, pp = os.path.join(ROOT, "topics", f"{slug}.json"), os.path.join(ROOT, "protocols", f"{slug}.md")
        md = open(pp, encoding="utf-8").read()
        if HEAD2 in md:
            out[slug] = {"state": "ALREADY_AMENDED"}
            continue
        cfg = _j(tp)
        lines, added = ["", HEAD2, ""], []
        for label, q in acc:
            v, pq = q["validation"], q["proposal"]["pubmed_query"]
            if pq in (cfg.get("pubmed_queries") or []) or pq in added:
                continue
            added.append(pq)
            lines.append(f"- **A4 Concept query added, {label}** (union; none removed): `{pq}`. Proposed blind (recorded call "
                         f"{q.get('record')}, model {q.get('model')}); returns {v.get('proposed_pubmed_count')} records "
                         f"today; on the comparator's eligible trials the queries registered after the 2026-10-05 "
                         f"amendment match {v['recall_current']['n']} of {v['recall_current']['N']} and with this query "
                         f"{v['recall_union']['n']} of {v['recall_union']['N']}. Limitation: the proposer may know "
                         f"well-known trials from training.")
        if not added:
            continue
        out[slug] = {"state": "DRY_RUN" if dry else "AMENDED", "added": added}
        if dry:
            continue
        cfg["pubmed_queries"] = list(cfg.get("pubmed_queries") or []) + added
        with open(tp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(cfg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(pp, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
    json.dump(out, open(os.path.join(SA, "amendments_round2.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    print(out)


if __name__ == "__main__" and "--round2" in sys.argv:
    round2("--dry-run" in sys.argv)


HEAD3 = "## Amendment 2026-10-06 -- search volume cap raised to 10,000 (decision under Mahmood's delegation)"


def cap_decision(dry=False):
    """A5: the 4 topics whose blind concept query gained recall only above the original 5,000-record cap. Decision
    (captain, under Mahmood's delegation, 6 Oct): cap raised to 10,000 for these topics. The query added is the one
    scripts/g1_expanded_search.py chose by its fixed rule (smallest volume with the maximal measured recall gain);
    its run and rule screen are recorded in outputs/search_audit/expanded/<slug>.json."""
    out = {}
    for slug in ("omega3-cardiovascular-events", "probiotics-aad-prevention", "semaglutide-obesity-mace",
                 "sglt2-primary-prevention-hf"):
        e = _j(os.path.join(SA, "expanded", f"{slug}.json"))
        ch, rec = e["chosen"], e["recall"]
        tp, pp = os.path.join(ROOT, "topics", f"{slug}.json"), os.path.join(ROOT, "protocols", f"{slug}.md")
        md = open(pp, encoding="utf-8").read()
        if HEAD3 in md:
            out[slug] = {"state": "ALREADY_AMENDED"}
            continue
        cfg = _j(tp)
        text = (f"\n{HEAD3}\n\n- **A5 Volume cap 10,000 (was 5,000) for this topic; concept query added** (union; none "
                f"removed): `{ch['query']}`. Decided 2026-10-06 by the captain under Mahmood's delegation. Reason: the "
                f"blind query audit ({ch['source']}, recorded call {ch['record']}) measured a recall gain on the "
                f"comparator's eligible trials -- registered queries {ch['recall_current_at_audit']['n']} of "
                f"{ch['recall_current_at_audit']['N']}, with this query {ch['recall_union_at_audit']['n']} of "
                f"{ch['recall_union_at_audit']['N']} -- at {ch['volume_at_audit']} records, above the old 5,000 cap. Run "
                f"in full on 2026-10-06: {e['esearch']['count']} records, {e['new_records']} not already held; rule "
                f"screen of the new records: {e['rule_screen']}. Eligible comparator trials identified: "
                f"{rec['identified_before']} -> {rec['identified_after']} of {rec['eligible']} "
                f"({rec['newly_identified_and_screen_included']} of the {rec['newly_identified']} newly identified pass "
                f"the screen). Recorded: outputs/search_audit/expanded/{slug}.json.\n")
        out[slug] = {"state": "DRY_RUN" if dry else "AMENDED", "query": ch["query"]}
        if dry:
            print(text)
            continue
        if ch["query"] not in (cfg.get("pubmed_queries") or []):
            cfg["pubmed_queries"] = list(cfg.get("pubmed_queries") or []) + [ch["query"]]
        cfg["search_volume_cap"] = {"n": 10000, "decided": "2026-10-06", "by": "captain under Mahmood's delegation"}
        with open(tp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(cfg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(pp, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    json.dump(out, open(os.path.join(SA, "amendments_cap.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    print({k: v["state"] for k, v in out.items()})


HEAD4 = "## Amendment 2026-10-07 -- search re-validated against the current comparator (active topics)"


def active_decision(slugs, dry=False):
    """A6: active G1 topics still short on search recall against their CURRENT comparator (V8 adoptions). Instruction
    (captain, under Mahmood's delegation, 7 Oct: 'run the expanded searches ... for any whose recall is still short').
    The query added is the one scripts/g1_expanded_search.py --active chose by the fixed rule (smallest volume with the
    maximal recall measured on the current comparator, volume <= 10,000) among the recorded blind proposals."""
    out = {}
    for slug in slugs:
        e = _j(os.path.join(SA, "expanded", f"{slug}.json"))
        ch, rec = e["chosen"], e["recall"]
        tp, pp = os.path.join(ROOT, "topics", f"{slug}.json"), os.path.join(ROOT, "protocols", f"{slug}.md")
        md = open(pp, encoding="utf-8").read()
        if HEAD4 in md:
            out[slug] = {"state": "ALREADY_AMENDED"}
            continue
        cfg = _j(tp)
        over = "; ".join(f"{o['round']} ({o['record']}) {o['volume']} records, recall {o['recall_union']['n']} of "
                         f"{o['recall_union']['N']}" for o in ch.get("over_cap") or [])
        text = (f"\n{HEAD4}\n\n- **A6 Concept query added** (union; none removed): `{ch['query']}`. Decided 2026-10-07 by "
                f"the captain under Mahmood's delegation. Reason: against the CURRENT comparator (PMID "
                f"{cfg.get('comparator_pmid')}) the registered queries identify {ch['recall_current_at_audit']['n']} of "
                f"{ch['recall_current_at_audit']['N']} eligible comparator trials; this blind proposal ({ch['source']}, "
                f"recorded call {ch['record']}; written without sight of any comparator trial) identifies "
                f"{ch['recall_union_at_audit']['n']} of {ch['recall_union_at_audit']['N']} together with them, at "
                f"{ch['volume_at_audit']} records (cap 10,000). Run in full on 2026-10-07: {e['esearch']['count']} "
                f"records, {e['new_records']} not already held; rule screen of the new records: {e['rule_screen']}. "
                f"Eligible comparator trials identified: {rec['identified_before']} -> {rec['identified_after']} of "
                f"{rec['eligible']} ({rec['newly_identified_and_screen_included']} of the {rec['newly_identified']} newly "
                f"identified pass the rule screen). Recorded: outputs/search_audit/expanded/{slug}.json."
                + (f" Not adopted, over the cap: {over}." if over else "")
                + " The standing REVIEW_REFERENCE_LIST route (A1) reads the topic's current comparator.\n")
        out[slug] = {"state": "DRY_RUN" if dry else "AMENDED", "query": ch["query"]}
        if dry:
            print(text)
            continue
        if ch["query"] not in (cfg.get("pubmed_queries") or []):
            cfg["pubmed_queries"] = list(cfg.get("pubmed_queries") or []) + [ch["query"]]
        with open(tp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(cfg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(pp, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    json.dump(out, open(os.path.join(SA, "active", "amendments_a6.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    print({k: v["state"] for k, v in out.items()})


if __name__ == "__main__" and "--cap" in sys.argv:
    cap_decision("--dry-run" in sys.argv)
if __name__ == "__main__" and "--active" in sys.argv:
    active_decision([a for a in sys.argv[1:] if not a.startswith("--")], "--dry-run" in sys.argv)
