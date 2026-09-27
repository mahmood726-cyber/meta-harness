"""Search execution records, one per DECLARED source (V1.0.1, GLP-1 review).

The GLP-1 protocol declares PubMed/MEDLINE, Europe PMC, Cochrane CENTRAL, ClinicalTrials.gov via AACT, WHO ICTRP, ISRCTN,
citation chasing and trial-family assembly. The page's source-status table said "Europe PMC: RAN_OK" because records
had been merged -- an INFERRED default, with no query, date or returned identifiers behind it. Every declared source
now carries an execution record built only from held artefacts:

  query, date, returned IDs (or 'not held'), dispositions (screening / registry decisions), family links, and
  entered_via -- EXECUTED_QUERY (an independent concept query), SEEDED_IDENTIFIER (a PMID/NCT/DOI enumeration of known
  items), MANUAL_ADDITION (a recorded link a person added), LEGACY_UNRECORDED (a retrieval with no per-query record).

A declared source with no execution is NOT_EXECUTED, never absent. Seeded and manual rows are rendered visibly
distinct from independently retrieved ones. A run whose raw responses are not held (the 15 Sep search_v2 run: its
funnels and queries are recorded in docs/evidence/search-v2-2026-09-15/02-source-funnels.txt, its response bodies are
not) is EXECUTED_IDS_NOT_HELD and marked as not the retrieval behind this page's screening.
"""
from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

DECLARED = (("PubMed/MEDLINE", r"PubMed"), ("Europe PMC", r"Europe PMC"), ("Cochrane CENTRAL", r"CENTRAL"),
            ("ClinicalTrials.gov (AACT)", r"ClinicalTrials\.gov|AACT"), ("WHO ICTRP", r"ICTRP"), ("ISRCTN", r"ISRCTN"),
            ("Citation chasing", r"citation chasing"), ("Trial-family assembly", r"trial-family assembly"))
_KIND_SOURCE = (("PUBMED", "PubMed/MEDLINE"), ("EUROPEPMC", "Europe PMC"), ("EPMC_NCT", "Europe PMC"),
                ("EPMC_", "Citation chasing"), ("CITATION", "Citation chasing"), ("COMPARATOR_REFERENCE", "Citation chasing"),
                ("PUBMED_ELINK", "Citation chasing"), ("CTGOV", "ClinicalTrials.gov (AACT)"), ("AACT", "ClinicalTrials.gov (AACT)"),
                ("REGISTRY_FIRST", "ClinicalTrials.gov (AACT)"), ("ISRCTN", "ISRCTN"))


def declared_sources(root, slug) -> list:
    p = Path(root) / "protocols" / f"{slug}.md"
    if not p.exists():
        return []
    line = next((x for x in p.read_text(encoding="utf-8").splitlines() if x.startswith("- **Search.**")), None)
    if not line:
        return []
    return [name for name, rx in DECLARED if re.search(rx, line, re.I)]


def _source_of(kind: str) -> str:
    k = str(kind or "").upper()
    if "LEGACY" in k:
        return "Legacy unrecorded retrieval"
    for prefix, src in sorted(_KIND_SOURCE, key=lambda x: -len(x[0])):
        if k.startswith(prefix) or prefix in k:
            return src
    return "Unattributed"


def _entered_via(kind: str) -> str:
    k = str(kind or "").upper()
    if "LEGACY" in k:
        return "LEGACY_UNRECORDED"
    if "ENUMERATION" in k or "NCT_LINK" in k or "EXTRA_PMIDS" in k or "CONTROL_PMIDS" in k:
        return "SEEDED_IDENTIFIER"
    return "EXECUTED_QUERY"


def _v2_funnels(root, slug) -> list:
    p = Path(root) / "docs" / "evidence" / "search-v2-2026-09-15" / "02-source-funnels.txt"
    if not p.exists():
        return []
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"^## " + re.escape(slug) + r"\n(.*?)(?=^## |\Z)", txt, re.S | re.M)
    out = []
    for ln in (m.group(1).splitlines() if m else []):
        r = re.match(r"- (\S+) (\S+) state=(\S+) hits=(\S+) .*?query=(.*)$", ln)
        if r:
            out.append({"source_id": r[1], "kind": r[2], "state": r[3], "hits": None if r[4] == "None" else int(r[4]),
                        "query": r[5], "date": "2026-09-15"})
    return out


def build(root, slug, review: dict) -> dict | None:
    decl = declared_sources(root, slug)
    if not decl:
        return None
    cache = Path(root) / "cache" / slug
    recs = {str(r.get("id")): r for r in (review.get("screening") or {}).get("records") or []}
    fam_of = {str(r["report_id"]): f["family_id"] for f in review.get("trial_families") or [] for r in f.get("reports") or []}

    def dispositions(ids):
        d = {}
        for i in ids:
            s = recs.get(str(i))
            key = f"{s['decision']} ({s.get('rule_id')})" if s else "not screened on this page"
            d[key] = d.get(key, 0) + 1
        return d

    execs = []
    led = json.loads((cache / "retrieval_ledger.json").read_text(encoding="utf-8")) if (cache / "retrieval_ledger.json").exists() else {}
    found = {}
    for rid, v in (led.get("records") or {}).items():
        for sid in v.get("found_by") or []:
            found.setdefault(sid, []).append(rid)
    for s in led.get("sources") or []:
        ids = s.get("record_ids") or found.get(s["source_id"]) or []
        execs.append({"source": _source_of(s.get("kind")), "id": s["source_id"], "entered_via": _entered_via(s.get("kind")),
                      "query": s.get("query"), "date": s.get("run_utc"), "state": s.get("state"),
                      "returned_ids": sorted(ids) if ids else None, "n_returned": len(ids) if ids else None,
                      "dispositions": dispositions(ids) if ids else None,
                      "family_links": len({fam_of[str(i)] for i in ids if str(i) in fam_of}) if ids else None,
                      "integrated": True})
    if (cache / "family_query.json").exists():
        fq = json.loads((cache / "family_query.json").read_text(encoding="utf-8"))
        ids = fq.get("record_ids") or []
        dec = {}
        for d in fq.get("decisions") or []:
            k = f"{d.get('decision')} ({d.get('reason_code') or 'retained'})"
            dec[k] = dec.get(k, 0) + 1
        execs.append({"source": "ClinicalTrials.gov (AACT)", "id": fq["source_id"], "entered_via": "EXECUTED_QUERY",
                      "query": fq.get("query"), "date": fq.get("run_utc"), "state": fq.get("state"), "returned_ids": ids,
                      "n_returned": len(ids), "dispositions": dec or None,
                      "family_links": len({f["family_id"] for f in review.get("trial_families") or []} & set(ids)),
                      "integrated": True})
    if (cache / "family_pub_links.json").exists():
        for x in json.loads((cache / "family_pub_links.json").read_text(encoding="utf-8")).get("links") or []:
            execs.append({"source": "Trial-family assembly", "id": f"family_pub_link:{x['nct']}->{x['pmid']}",
                          "entered_via": "MANUAL_ADDITION", "query": f"recorded link bound by '{x['binding_token']}' ({x.get('reported_by')})",
                          "date": x.get("retrieved_utc"), "state": "RAN_OK", "returned_ids": [x["pmid"]], "n_returned": 1,
                          "dispositions": dispositions([x["pmid"]]), "family_links": 1, "integrated": True})
    v2 = _v2_funnels(root, slug)
    # calls logged in the latest held search_v2 snapshot index with no funnel record (e.g. ISRCTN): the call is on
    # record, its outcome is not
    snaps = sorted((cache / "snapshots").glob("*search_v2/raw/INDEX.json")) if (cache / "snapshots").exists() else []
    if snaps:
        have = {v["source_id"] for v in v2}
        calls = {}
        for c in json.loads(snaps[-1].read_text(encoding="utf-8")):
            calls.setdefault(c["source_id"], c)
        for sid, c in calls.items():
            if sid not in have:
                p = c.get("params") or {}
                execs.append({"source": _source_of(sid.split("#")[0]), "id": "search_v2:" + sid,
                              "entered_via": _entered_via(sid.split("#")[0]), "query": p.get("term") or p.get("query") or p.get("q") or json.dumps(p)[:200],
                              "date": c.get("fetched_utc"), "state": "CALL_LOGGED_ONLY", "returned_ids": None, "n_returned": None,
                              "dispositions": None, "family_links": None, "integrated": False,
                              "note": f"call logged in {snaps[-1].parent.parent.name} (HTTP status {c.get('status')}); no funnel or response body held"})
    for v in v2:
        execs.append({"source": _source_of(v["kind"]), "id": "search_v2:" + v["source_id"], "entered_via": _entered_via(v["kind"]),
                      "query": v["query"], "date": v["date"], "state": v["state"], "returned_ids": None, "n_returned": v["hits"],
                      "dispositions": None, "family_links": None, "integrated": False,
                      "note": "search_v2 run of 15 Sep 2026: query and funnel recorded, response bodies not held; not the retrieval behind this page's screening"})
    rows = []
    for name in decl + sorted({e["source"] for e in execs} - set(decl)):
        ex = [e for e in execs if e["source"] == name]
        indep = [e for e in ex if e["entered_via"] == "EXECUTED_QUERY" and e["state"] in ("RAN_OK", "RAN_ZERO")]
        if any(e["integrated"] and e["returned_ids"] is not None for e in indep):
            state = "EXECUTED"
        elif indep:
            state = "EXECUTED_IDS_NOT_HELD"
        elif any(e["state"] == "CALL_LOGGED_ONLY" and e["entered_via"] == "EXECUTED_QUERY" for e in ex):
            state = "CALLED_NO_RESULT_RECORD"
        elif any(e["entered_via"] == "SEEDED_IDENTIFIER" for e in ex):
            state = "SEEDED_ONLY"
        elif any(e["entered_via"] == "MANUAL_ADDITION" for e in ex):
            state = "MANUAL_ONLY"
        elif ex:
            state = "LEGACY_UNRECORDED_ONLY"
        else:
            state = "NOT_EXECUTED"
        rows.append({"source": name, "declared": name in decl, "state": state, "executions": ex})
    status = (review.get("search") or {}).get("source_status") or {}
    return {"declared": decl, "rows": rows,
            "status_table_note": ("the source-status table's RAN_OK for a group without a recorded execution is INFERRED "
                                  "from merged records, not an execution record") if status else None}


def render(obj: dict | None) -> str:
    if not obj:
        return ""
    e = lambda s: _html.escape(str(s), quote=True)  # noqa: E731
    trs = []
    for r in obj["rows"]:
        if not r["executions"]:
            trs.append(f"<tr class='not-executed'><td>{e(r['source'])}</td><td><code>{e(r['state'])}</code></td>"
                       "<td colspan='6'>declared by the protocol; no execution record held</td></tr>")
        for x in r["executions"]:
            cls = {"SEEDED_IDENTIFIER": "seeded", "MANUAL_ADDITION": "manual", "LEGACY_UNRECORDED": "legacy"}.get(x["entered_via"], "independent")
            ids = ("not held" if x["returned_ids"] is None else f"{len(x['returned_ids'])} held")
            trs.append(f"<tr class='{cls}'><td>{e(r['source'])}</td><td><code>{e(r['state'])}</code></td>"
                       f"<td><strong>{e(x['entered_via'])}</strong>{' (not integrated)' if not x['integrated'] else ''}</td>"
                       f"<td><code>{e(str(x['query'])[:300])}</code></td><td>{e(x['date'])}</td>"
                       f"<td>{e(x['n_returned'])} returned; IDs {e(ids)}</td>"
                       f"<td>{e('; '.join(f'{k}: {v}' for k, v in sorted((x['dispositions'] or {}).items())) or '—')}</td>"
                       f"<td>{e(x['family_links'] if x['family_links'] is not None else '—')}</td></tr>")
    return ("<section id='search-execution'><h4>Search execution records (one per declared source)</h4>"
            "<p>Rows marked SEEDED_IDENTIFIER, MANUAL_ADDITION or LEGACY_UNRECORDED did not retrieve independently; only "
            "EXECUTED_QUERY rows can find an unknown trial. " + (e(obj["status_table_note"]) + ".</p>" if obj.get("status_table_note") else "</p>")
            + "<div style='overflow-x:auto'><table class='recs search-exec'><thead><tr><th>Declared source</th><th>State</th>"
            "<th>Entered via</th><th>Query</th><th>Date</th><th>Returned</th><th>Dispositions</th><th>Family links</th></tr></thead>"
            "<tbody>" + "".join(trs) + "</tbody></table></div></section>")
