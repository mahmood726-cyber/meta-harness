"""The ONE deterministic text representation a span is checked against. A span in an evidence record is a
substring of render(source); render is a pure function of the held bytes, so the check is re-runnable by anyone
who holds (or re-fetches and hash-checks) the same bytes.

  *.xml (JATS)            -> tags stripped to single spaces, entities unescaped, whitespace collapsed
  registry/NCT*.json      -> the ClinicalTrials.gov v2 record flattened to labelled lines (see _ctgov)
  records.json#/<list>/<i> -> that record's `title` + `abstract`, whitespace collapsed
  europepmc_core.json     -> title + abstractText, tags stripped, whitespace collapsed
  *.html (held_local)     -> script/style removed, tags stripped to spaces, entities unescaped, whitespace collapsed
  *.txt                   -> text, whitespace collapsed
"""
import html, json, os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _strip(s):
    s = re.sub(r"<(xref|sup)[^>]*>(.*?)</\1>", lambda m: m.group(0) if m.group(1) == "sup" else " ", s or "", flags=re.S)
    return _ws(html.unescape(re.sub(r"<[^>]+>", " ", s)))


def _ctgov(d):
    L = []
    ps = d.get("protocolSection", {})
    idm = ps.get("identificationModule", {})
    L.append(f"NCT: {idm.get('nctId')} | TITLE: {idm.get('officialTitle') or idm.get('briefTitle')}")
    el = ps.get("eligibilityModule", {})
    L.append(f"ELIGIBILITY: {_ws(el.get('eligibilityCriteria'))}")
    for c in ps.get("conditionsModule", {}).get("conditions", []) or []:
        L.append(f"CONDITION: {c}")
    for a in ps.get("armsInterventionsModule", {}).get("armGroups", []) or []:
        L.append(f"ARM: {a.get('label')} [{a.get('type')}] {_ws(a.get('description'))}")
    for o in ps.get("outcomesModule", {}).get("primaryOutcomes", []) or []:
        L.append(f"PROTOCOL PRIMARY OUTCOME: {_ws(o.get('measure'))} | {_ws(o.get('description'))} | TIME FRAME: {_ws(o.get('timeFrame'))}")
    rs = d.get("resultsSection", {})
    for i, om in enumerate(rs.get("outcomeMeasuresModule", {}).get("outcomeMeasures", []) or []):
        L.append(f"RESULT OUTCOME {i} [{om.get('type')}]: {_ws(om.get('title'))} | DESCRIPTION: {_ws(om.get('description'))}"
                 f" | TIME FRAME: {_ws(om.get('timeFrame'))} | POPULATION: {_ws(om.get('populationDescription'))}"
                 f" | PARAM: {om.get('paramType')} | UNIT: {om.get('unitOfMeasure')}")
        gt = {g.get('id'): g.get('title') for g in om.get("groups", []) or []}
        for g in om.get("groups", []) or []:
            L.append(f"RESULT OUTCOME {i} GROUP {g.get('id')}: {g.get('title')} | {_ws(g.get('description'))}")
        for dn in om.get("denoms", []) or []:
            L.append(f"RESULT OUTCOME {i} DENOM {dn.get('units')}: " + "; ".join(f"{gt.get(c.get('groupId'))}={c.get('value')}" for c in dn.get("counts", []) or []))
        for cl in om.get("classes", []) or []:
            for dn in cl.get("denoms", []) or []:
                L.append(f"RESULT OUTCOME {i} CLASS DENOM {cl.get('title')} {dn.get('units')}: " + "; ".join(
                    f"{gt.get(c.get('groupId'))}={c.get('value')}" for c in dn.get("counts", []) or []))
            for cat in cl.get("categories", []) or []:
                lab = " / ".join(x for x in (cl.get("title"), cat.get("title")) if x)
                L.append(f"RESULT OUTCOME {i} MEASUREMENT {lab}: " + "; ".join(
                    f"{gt.get(m.get('groupId'))}={m.get('value')}" + (f" (spread {m.get('spread')})" if m.get('spread') else "")
                    + (f" ({m.get('lowerLimit')} to {m.get('upperLimit')})" if m.get('lowerLimit') is not None else "")
                    for m in cat.get("measurements", []) or []))
        for j, an in enumerate(om.get("analyses", []) or []):
            L.append(f"RESULT OUTCOME {i} ANALYSIS {j}: groups {', '.join(str(gt.get(g)) for g in an.get('groupIds', []) or [])}"
                     f" | {an.get('paramType')} {an.get('paramValue')} ({an.get('ciPctValue')}% CI {an.get('ciLowerLimit')} to {an.get('ciUpperLimit')})"
                     f" | p {an.get('pValue')} | METHOD {an.get('statisticalMethod')} | {_ws(an.get('statisticalComment'))} {_ws(an.get('estimateComment'))}")
    # APPEND-ONLY below this line: spans already bound are substrings of the text above, so anything a later
    # version surfaces goes after it (a line inserted mid-text once broke a verified multi-line span).
    for i, om in enumerate(rs.get("outcomeMeasuresModule", {}).get("outcomeMeasures", []) or []):
        if om.get("dispersionType"):
            L.append(f"RESULT OUTCOME {i} DISPERSION TYPE: {om.get('dispersionType')}")
    if el.get("minimumAge") or el.get("maximumAge") or el.get("sex"):
        L.append(f"ELIGIBILITY AGE/SEX: minimum age {el.get('minimumAge')} | maximum age {el.get('maximumAge')} | sex {el.get('sex')}")
    return "\n".join(L)


def render(ref):
    path, _, frag = ref.partition("#")
    full = os.path.join(ROOT, path) if not os.path.isabs(path) else path
    raw = open(full, "rb").read()
    if path.endswith("records.json") and frag:
        d = json.loads(raw.decode("utf-8"))
        parts = frag.strip("/").split("/")
        r = d[parts[0]][int(parts[1])]
        return _ws((r.get("title") or "") + " " + (r.get("abstract") or ""))
    if path.endswith("europepmc_core.json"):
        r = json.loads(raw.decode("utf-8"))["resultList"]["result"][0]
        return _strip((r.get("title") or "") + " " + (r.get("abstractText") or ""))
    if path.endswith(".json") and "/registry/" in path.replace("\\", "/"):
        return _ctgov(json.loads(raw.decode("utf-8")))
    if path.endswith(".html"):
        t = raw.decode("utf-8", errors="replace")
        t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S)
        return _ws(html.unescape(re.sub(r"<[^>]+>", " ", t)))
    if path.endswith(".xml"):
        t = raw.decode("utf-8")
        t = re.sub(r"<(ref-list|back)\b.*?</\1>", " ", t, flags=re.S)
        return _strip(t)
    return _ws(raw.decode("utf-8", errors="strict"))
