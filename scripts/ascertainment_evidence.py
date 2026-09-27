"""Build cache/<slug>/ascertainment_evidence.json for the B-prime outcome-ascertainment clause (harness/ascertainment.py).

Holds every document the evidence cites -- a PubMed batch (request, time, sha256), PMC full texts (CC BY-NC, request
recorded), the held AACT outcome rows -- and records, per family, the quote that evidences each half of the clause.
The quotes were chosen by Claude and cross-read by an independent codex lane (ASC-A1, gpt-6-astra, every quote
located); harness/ascertainment.load re-verifies each against the held bytes, the clause vocabulary and the dates.

usage: python scripts/ascertainment_evidence.py <slug> <aact_rows.txt>   (network: PubMed E-utilities, PMC)
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
CONTACT = "tool=meta-harness&email=meta-harness%40example.org"
MON = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

# family -> results report, prospective (doc, quote), ascertained (doc, quote); None = not evidenced (PENDING)
SPEC = {
 "NCT01144338": {"results": "28910237", "completion_date": "2017-04-24",
    "prospective": ("pm:26995376", "The trial will continue until 1,360 confirmed primary composite cardiovascular end points, defined as cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke, have occurred."),
    "ascertained": ("ft:28910237", "An independent clinical events classification committee whose members were unaware of the trial-group assignments adjudicated all the components of the primary composite outcome")},
 "NCT01179048": {"results": "27295427", "completion_date": "2015-12-17",
    "prospective": ("pm:24176437", "The primary end point is the time from randomization to a composite outcome consisting of the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke."),
    "ascertained": ("ft:27295427", "Prespecified exploratory outcomes included an expanded composite cardiovascular outcome (death from cardiovascular causes, nonfatal myocardial infarction, nonfatal stroke, coronary revascularization, or hospitalization for unstable angina pectoris or heart failure), death from any cause, a composite renal and retinal microvascular outcome (nephropathy [defined as the new onset of macroalbuminuria or a doubling of the serum creatinine level and an eGFR of ≤45 ml per minute per 1.73 m 2 , the need for continuous renal-replacement therapy, or death from renal disease] and retinopathy [defined as the need for retinal photocoagulation or treatment with intravitreal agents, vitreous hemorrhage, or the onset of diabetes-related blindness]), neoplasms, and pancreatitis — all of which were adjudicated in a blinded fashion by an external, independent event-adjudication committee.")},
 "NCT01394952": {"results": "31189511", "completion_date": "2018-08-21",
    "prospective": ("pm:28573765", "The primary cardiovascular outcome is the first occurrence of the composite of cardiovascular death or non-fatal myocardial infarction or non-fatal stroke."),
    "ascertained": ("pm:31924562", "cerebrovascular and other cardiovascular outcomes were ascertained and adjudicated")},
 "NCT01720446": {"results": "27633186", "completion_date": "2016-03-15",
    "prospective": None,
    "prospective_gap": ("no version-dated pre-results source held: the EU Clinical Trials Register record (EudraCT 2012-002839-28, "
                        "first entered 2012-12-06) names the MACE primary end point, but the register displays the CURRENT "
                        "protocol version, so the date does not date that text; the dated protocol in the primary report's "
                        "supplement is not held"),
    "ascertained": ("pmc:PMC7064975", "the incidences of the adjudicated three‐component MACE and its individual components were analysed using individual patient‐level data from the combined population of SUSTAIN 6 and PIONEER 6")},
 "NCT02465515": {"results": "30291013", "completion_date": "2018-03-14",
    "prospective": ("pm:30015066", "confirmed primary outcome events (CV death, myocardial infarction, or stroke)"),
    "ascertained": ("aact:1415454341", "Time to MACE defined as the time to first occurrence of Cardiovascular Endpoint Committee (CEC)-adjudicated MACE (CV death, myocardial infarction \\[MI\\] or stroke)")},
 "NCT02692716": {"results": "31185157", "completion_date": "2018-09-25",
    "prospective": ("pmc:PMC6587508", "The primary composite endpoint is time to first occurrence of CV death or non‐fatal myocardial infarction or non‐fatal stroke."),
    "ascertained": ("pmc:PMC6587508", "CV events and other selected types of events are adjudicated by an independent blinded external event adjudication committee.")},
 "NCT03496298": {"results": "34215025", "completion_date": "2020-12-10",
    "prospective": ("pm:33026143", "The primary outcome is a major adverse CV event defined as non-fatal myocardial infarction, non-fatal stroke or CV death."),
    "ascertained": ("aact:1413884700", "All MACE positively adjudicated by the clinical endpoint committee (CEC) were used in the analysis of the composite outcome of first occurrence to CV death, non-fatal myocardial infarction (MI), and non-fatal stroke.")},
 "NCT03914326": {"results": "40162642", "completion_date": "2024-08-23",
    "prospective": ("pm:36945734", "The primary outcome is time from randomization to first occurrence of a major adverse CV event (MACE; a composite of CV death, nonfatal myocardial infarction or nonfatal stroke)."),
    "ascertained": ("pm:36945734", "This event-driven trial will continue until 1225 first adjudication-confirmed MACEs have occurred.")},
 "NCT03819153": {"results": "38785209", "completion_date": "2024-01-09",
    "prospective": ("pmc:PMC10469096", "time to first occurrence of three-point MACE (comprising non-fatal myocardial infarction, non-fatal stroke or death from CV causes)"),
    "ascertained": ("pmc:PMC10469096", "Events including deaths, those leading to kidney replacement therapy, acute coronary syndrome, stroke or transient ischaemic attack, and MALE are reviewed by an independent external EAC in a blinded manner.")},
 "NCT01147250": {"results": "26630143", "completion_date": "2015-02-28",
    "prospective": ("pm:25965710", "The primary efficacy end point is a composite of time to CV death, nonfatal myocardial infarction, nonfatal stroke, or hospitalization for unstable angina."),
    "ascertained": ("pm:25965710", "The study will continue until the positive adjudication of the protocol-specified number of primary CV events.")},
}
PROGRAMMES = [{
    "id": "husain-2020-sustain-pioneer", "doc": "pmc:PMC7064975",
    "quote": "In these trials, MACE were recorded as adjudicated adverse events (AEs) using the same terms as the CVOTs (MI, stroke and CV death).",
    "applies_to_acronyms": ["SUSTAIN 1", "SUSTAIN 2", "SUSTAIN 3", "SUSTAIN 4", "SUSTAIN 5", "PIONEER 1", "PIONEER 2",
                            "PIONEER 3", "PIONEER 4", "PIONEER 5", "PIONEER 7", "PIONEER 8", "PIONEER 9", "PIONEER 10"],
    "named_in_source": "SUSTAIN 1-5 and two SUSTAIN JAPAN trials, and PIONEER 1-5, 7-8 and the two PIONEER Japanese trials [9 and 10] (the two SUSTAIN Japan trials are not bound: the source does not name them)",
    "note": ("Husain et al. 2020 (post hoc, individual patient data): a statement of HOW events were ascertained in the named "
             "glycaemic trials. It supports ascertainment only -- prospective specification needs each trial's own protocol -- "
             "and its pooled post-hoc estimate never enters any pool as a trial.")}]


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "meta-harness"}), timeout=90) as r:
        return r.read()


def date_of(art):
    cands = []
    ad = art.find(".//Article/ArticleDate")
    if ad is not None:
        cands.append(f"{ad.findtext('Year')}-{int(ad.findtext('Month')):02d}-{int(ad.findtext('Day')):02d}")
    for h in art.findall(".//PubmedData/History/PubMedPubDate"):
        if h.get("PubStatus") in ("pubmed", "entrez"):
            cands.append(f"{h.findtext('Year')}-{int(h.findtext('Month')):02d}-{int(h.findtext('Day')):02d}")
    pd = art.find(".//Journal/JournalIssue/PubDate")
    if pd is not None and pd.findtext("Year"):
        m = pd.findtext("Month") or "Jan"
        m = MON.get(m[:3], int(m) if m.isdigit() else 1)
        cands.append(f"{pd.findtext('Year')}-{m:02d}-{int(pd.findtext('Day') or 1):02d}")
    return min(cands) if cands else None


def main(slug, aact_rows_txt):
    cdir = os.path.join(ROOT, "cache", slug)
    pmids = sorted({v["results"] for v in SPEC.values()} | {d.split(":")[1] for v in SPEC.values()
                   for k in ("prospective", "ascertained") if v.get(k) for d in [v[k][0]] if d.startswith("pm:")}
                   | {"30284349", "36651820", "31903692"})      # the PubMed records of the three PMC documents (dates)
    url = f"{E}?db=pubmed&id={','.join(pmids)}&retmode=xml&{CONTACT}"
    body = get(url)
    open(os.path.join(cdir, "ascertainment_pubmed.xml"), "wb").write(body)
    root = ET.fromstring(body)
    arts = {a.findtext(".//MedlineCitation/PMID"): a for a in root.findall(".//PubmedArticle")}
    held = {"request": url, "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "response_sha256": hashlib.sha256(body).hexdigest()}
    docs = {}
    for p in pmids:
        docs[f"pm:{p}"] = {"kind": "PubMed record", "document_ref": f"cache/{slug}/ascertainment_pubmed.xml", "pmid": p,
                           "title": arts[p].findtext(".//ArticleTitle"), "earliest_date": date_of(arts[p]), **held}
    for p in ("27295427", "28910237"):
        docs[f"ft:{p}"] = {"kind": "held full text of the primary report", "document_ref": f"cache/{slug}/ft_{p}.txt",
                           "earliest_date": docs[f"pm:{p}"]["earliest_date"] if f"pm:{p}" in docs else None}
    for pmc in ("PMC6587508", "PMC10469096", "PMC7064975"):
        u = f"{E}?db=pmc&id={pmc[3:]}&retmode=xml&{CONTACT}"
        b = get(u)
        lic = re.findall(rb'<license[^>]*xlink:href="([^"]+)"', b)
        open(os.path.join(cdir, f"ascertainment_{pmc}.xml"), "wb").write(b)
        docs[f"pmc:{pmc}"] = {"kind": "PMC full text", "document_ref": f"cache/{slug}/ascertainment_{pmc}.xml",
                              "licence": lic[0].decode() if lic else None, "request": u,
                              "response_sha256": hashlib.sha256(b).hexdigest()}
    # dates of PMC documents come from their PubMed records where held
    for pmc, pm in (("PMC6587508", "30284349"), ("PMC10469096", "36651820"), ("PMC7064975", "31903692")):
        if f"pm:{pm}" in docs:
            docs[f"pmc:{pmc}"]["earliest_date"] = docs[f"pm:{pm}"]["earliest_date"]
            docs[f"pmc:{pmc}"]["pmid"] = None
    rows = []
    for line in open(aact_rows_txt, encoding="utf-8"):
        f = line.rstrip("\n").split("|")
        rows.append({"id": f[0], "nct_id": f[1], "outcome_type": f[2], "measure": f[3], "time_frame": f[4],
                     "population": f[5], "description": "|".join(f[6:]), "row_sha256": hashlib.sha256(line.encode()).hexdigest()})
    json.dump({"snapshot": "AACT 2026-08-30", "table": "design_outcomes", "rows": rows},
              open(os.path.join(cdir, "ascertainment_aact_rows.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    for r in rows:
        docs[f"aact:{r['id']}"] = {"kind": "registry outcome description (AACT design_outcomes)",
                                   "document_ref": f"cache/{slug}/ascertainment_aact_rows.json", "row_id": r["id"]}
    fams = {}
    for fid, s in SPEC.items():
        f = {"results": {"doc": f"pm:{s['results']}", "earliest_date": docs[f"pm:{s['results']}"]["earliest_date"]},
             "completion_date": s["completion_date"]}
        for k in ("prospective", "ascertained"):
            if s.get(k):
                f[k] = {"doc": s[k][0], "quote": s[k][1]}
        if s.get("prospective_gap"):
            f["prospective_gap"] = s["prospective_gap"]
        fams[fid] = f
    doc = {"schema": "ascertainment-evidence-v1", "slug": slug,
           "clause": "3-point MACE, or its exact three components, was prospectively specified and systematically ascertained",
           "rule": ("prospective: a source dated before the results report names MACE or its three components; ascertained: a "
                    "source states the events were adjudicated or systematically ascertained. Quotes chosen by Claude, cross-read "
                    "by codex lane ASC-A1; re-verified by harness/ascertainment.load against the held bytes and dates."),
           "documents": docs, "families": fams, "programmes": PROGRAMMES}
    open(os.path.join(cdir, "ascertainment_evidence.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print("wrote", len(docs), "documents,", len(fams), "families")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
