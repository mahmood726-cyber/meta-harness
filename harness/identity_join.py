"""Offline typed trial identity joins; identity never grants pool admission."""
from __future__ import annotations
import json
import re
from pathlib import Path
from .trial_family import load_registry

ROOT = Path(__file__).resolve().parents[1]
KEYS = ("ncts", "dois", "pmids", "acronyms", "author_years")

def scalar(v):
    if isinstance(v, dict):
        return v.get("value") if v.get("status", "PARSED") == "PARSED" else None
    return v

def normalized(v):
    return re.sub(r"[\s\-\u2010-\u2015]+", "", str(v)).casefold()

def identity(row):
    if "identities" in row:
        return row["identities"]
    out = {k: set() for k in KEYS}
    aliases = row.get("aliases") or {}
    def vals(*fields):
        result = []
        for f in fields:
            v = scalar(row.get(f))
            if v is None:
                v = aliases.get(f)
            result.extend(v if isinstance(v, list) else [v] if v else [])
        return [str(v) for v in result]
    raw = " ".join(vals("registration", "nct", "nct_id", "registry_ids", "id", "family_id", "trial_family_id", "report_id", "report_ids", "pmid", "label"))
    out["ncts"].update(x.upper() for x in re.findall(r"\bNCT\d{8}\b", raw, re.I))
    out["pmids"].update(re.findall(r"\bPMID[ :]+(\d{6,9})\b", raw, re.I))
    for v in vals("pmid", "id", "report_id", "report_ids", "label"):
        if re.fullmatch(r"\d{6,9}", v):
            out["pmids"].add(v)
    for v in vals("doi", "dois"):
        out["dois"].update(x.rstrip(".,;").lower() for x in re.findall(r"10\.\d{4,9}/[^\s<>\"]+", v, re.I))
    for v in vals("acronym", "acronyms"):
        if len(normalized(v)) >= 3:
            out["acronyms"].add(normalized(v))
    label = str(scalar(row.get("label")) or "")
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9 \-\u2010-\u2015]+", label) and not re.search(r"NCT\d|PMID|\b(?:19|20)\d{2}\b", label, re.I):
        if len(normalized(label)) >= 3:
            out["acronyms"].add(normalized(label))
    # Only explicit parenthetical trial acronyms in titles; no arbitrary prose tokens.
    for title in vals("title"):
        for a in re.findall(r"\(([A-Z][A-Z0-9 -]{2,})\)\s+[Tt]rial\b", title):
            out["acronyms"].add(normalized(a))
    author = scalar(row.get("first_author")) or scalar(row.get("author"))
    year = scalar(row.get("year"))
    m = re.match(r"^([\w?'-]+)(?:,?\s+(?:et al\.?\s*)?)((?:19|20)\d{2})[a-z]?$", label)
    if m:
        author, year = m.groups()
    if author and re.fullmatch(r"(?:19|20)\d{2}", str(year)):
        out["author_years"].add(normalized(str(author).split()[0]) + ":" + str(year))
    return out

def join(comparator_trial, ours):
    a = identity(comparator_trial)
    candidates = [(i, identity(r)) for i, r in enumerate(ours)]
    for key in KEYS:
        hits = [(i, sorted(a[key] & b[key])) for i, b in candidates if a[key] & b[key]]
        if hits:
            if len(hits) > 1:
                return dict(status="AMBIGUOUS", reason="REFUSED_AMBIGUOUS_IDENTITY", key=key, candidates=[i for i, _ in hits])
            i, common = hits[0]
            return dict(status="JOINED", key=key, comparator_value=common[0], our_value=common[0], index=i)
        # An explicit conflicting stronger identifier cannot be rescued by a weak alias.
        candidates = [(i,b) for i,b in candidates if not (a[key] and b[key])]
    return dict(status="NOT_JOINED", reason="NO_COMPATIBLE_HELD_IDENTITY")

def our_identities(slug=None, root=ROOT, review=None):
    root = Path(root)
    if slug is not None and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ValueError("REFUSED_INVALID_SLUG")
    if review is None:
        path = root / "docs/reviews" / slug / "review.json"
        if not path.exists():
            raise ValueError("REFUSED_REVIEW_NOT_HELD:" + slug)
        review = json.loads(path.read_text(encoding="utf-8"))
    nodes = []
    def add(row, source, outcome=None, pooled=False):
        ids = identity(row)
        # Coalesce repeated records ONLY on strong identifiers; shared acronyms abstain.
        hits = [n for n in nodes if any(ids[k] & n["identities"][k] for k in KEYS[:3])]
        if len(hits) == 1 and not (ids["ncts"] and hits[0]["identities"]["ncts"] and not ids["ncts"] & hits[0]["identities"]["ncts"]):
            node = hits[0]
        else:
            node = dict(identities={k:set() for k in KEYS}, rows=[])
            nodes.append(node)
        for k in KEYS:
            node["identities"][k].update(ids[k])
        node["rows"].append(dict(row=row, source=source, outcome=outcome, pooled=pooled))
    for f in review.get("trial_families", []):
        f = dict(f)
        f["report_ids"] = [r["report_id"] for r in f.get("reports", [])]
        add(f, "review.trial_families")
    if slug:
        for nct, entry in load_registry(root, slug).items():
            add({"nct":nct}, "family_registry")
            for r in entry.get("raw", {}).get("studies", []):
                add(r, "family_registry.raw.studies")
        path = root / "cache" / slug / "records.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            for r in data if isinstance(data,list) else data.get("records", []) + data.get("ctgov", []):
                add(r, "cache.records")
            if isinstance(data, dict):
                for nct in data.get("ctgov_results", {}):
                    if not re.fullmatch(r"NCT\d{8}", nct, re.I):
                        raise ValueError("REFUSED_CTGOV_RESULTS_ID:" + str(nct))
                    add({"nct":nct}, "cache.ctgov_results")
    for r in review.get("screening", {}).get("records", []):
        add(r, "review.screening")
    for o in review.get("outcomes", []):
        pool = o.get("result") or {}
        refused = pool.get("present") is False or pool.get("suppressed_incompatible") or pool.get("pool_refused")
        for r in o.get("trials", []):
            add(r, "review.outcomes.trials", o.get("name"), not refused)
        refusal = pool.get("design_refusal")
        refused_rows = refusal.get("refused", []) if isinstance(refusal, dict) else []
        for r in o.get("declared_absent_trials", []) + refused_rows:
            add(r, "review.outcomes.declared_absent", o.get("name"))
    for r in review.get("absent_trials", []):
        add(r, "review.absent_trials")
    return nodes

def states(node, outcome):
    result = []
    for item in node["rows"]:
        row = item["row"]
        if item["outcome"] == outcome or item["source"] == "review.absent_trials":
            state = row.get("absence_code") or row.get("reason_code") or row.get("state")
            if state:
                result.append(str(state))
    if not result:
        for item in node["rows"]:
            row = item["row"]
            if row.get("decision"):
                result.append("SCREENING:" + row["decision"] + ":" + str(row.get("rule_id", "UNSPECIFIED")))
    return sorted(set(result)) or ["HELD_WITHOUT_OUTCOME_ROW"]
