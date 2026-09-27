"""Pack the HELD funding sources of every pooled trial into cache/<slug>/funding_sources.json (V1.0.1).

The typed funding object (harness/funding_typed.py) reads only cache, so the page replays offline. This script copies,
from bytes already held under evidence/held/, with each source file's sha256:
  - the publisher funding metadata deposited with the article (Europe PMC core record `grantsList`), and
  - the registry's typed funder list: ClinicalTrials.gov leadSponsor/collaborators with their `class`, or the ANZCTR
    "Funding & Sponsors" table with each funder's "Funding source category".
Nothing is fetched. A trial with no held source gets no entry (absence is visible downstream, never inferred).

usage: python scripts/funding_sources.py [slug|all] [--check]
"""
import hashlib
import html as _html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELD = ROOT / "evidence" / "held"
_REG = re.compile(r"\b(NCT\d{8}|ACTRN\d{14})\b")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def publisher_grants(pmid: str):
    p = HELD / pmid / "europepmc_core.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    res = ((d.get("resultList") or {}).get("result") or [{}])[0]
    if str(res.get("pmid") or "") != pmid:
        return None
    grants = ((res.get("grantsList") or {}).get("grant")) or []
    return {"source": "publisher funding metadata (Europe PMC core grantsList)", "document_ref": _rel(p),
            "document_sha256": _sha(p),
            "funders": [{"name": g.get("agency"), **({"grant_id": g["grantId"]} if g.get("grantId") else {})}
                        for g in grants if g.get("agency")]}


def ctgov_funders(nct: str):
    p = HELD / "registry" / f"{nct}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    sc = (d.get("protocolSection") or {}).get("sponsorCollaboratorsModule") or {}
    rows = []
    if sc.get("leadSponsor"):
        rows.append({"name": sc["leadSponsor"].get("name"), "category": sc["leadSponsor"].get("class"), "role": "lead sponsor"})
    for c in sc.get("collaborators") or []:
        rows.append({"name": c.get("name"), "category": c.get("class"), "role": "collaborator"})
    return {"source": "ClinicalTrials.gov sponsor/collaborators (held API record)", "registry_id": nct,
            "document_ref": _rel(p), "document_sha256": _sha(p), "funders": [r for r in rows if r["name"]]}


def anzctr_funders(actrn: str):
    p = HELD / "registry" / f"{actrn}.html"
    if not p.exists():
        return None
    raw = p.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", raw)))
    rows = []
    for m in re.finditer(r"Funding source category \[(\d+)\] \d+ \d+ (.+?) Query! Name \[\1\] \d+ \d+ (.+?) Query!", text):
        rows.append({"name": m.group(3).strip(), "category": m.group(2).strip(), "role": "funding source"})
    return {"source": "ANZCTR Funding & Sponsors (held registry page)", "registry_id": actrn,
            "document_ref": _rel(p), "document_sha256": _sha(p), "funders": rows}


def trial_ids(slug: str):
    rev = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
    ids = []
    for o in rev.get("outcomes") or []:
        for t in o.get("trials") or []:
            tid = str(t.get("id") or "").replace("PMID ", "").strip()
            if tid and tid not in ids:
                ids.append(tid)
    for f in rev.get("funding") or []:
        tid = str(f.get("id") or "").replace("PMID ", "").strip()
        if tid and tid not in ids:
            ids.append(tid)
    return ids


def build(slug: str) -> dict:
    recs = json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))
    by = {str(r.get("id")): r for k, v in recs.items() if isinstance(v, list) for r in v if isinstance(r, dict)}
    out = {}
    for tid in trial_ids(slug):
        rec = by.get(tid) or {}
        regs = []
        for s in ([tid] if _REG.fullmatch(tid) else []) + [str(rec.get("nct") or "")] + _REG.findall(str(rec.get("abstract") or "")):
            if _REG.fullmatch(s or "") and s not in regs:
                regs.append(s)
        entry = []
        if tid.isdigit():
            g = publisher_grants(tid)
            if g:
                entry.append(g)
        for r in regs:
            reg = ctgov_funders(r) if r.startswith("NCT") else anzctr_funders(r)
            if reg:
                entry.append(reg)
        if entry:
            out[tid] = entry
    return {"schema": "funding-sources-v1", "slug": slug,
            "note": "copied from held bytes under evidence/held/ (sha256 per source); nothing fetched", "trials": out}


def main(argv):
    target = argv[1] if len(argv) > 1 and not argv[1].startswith("--") else "all"
    check = "--check" in argv
    slugs = sorted(p.parent.name for p in (ROOT / "cache").glob("*/records.json")) if target == "all" else [target]
    slugs = [s for s in slugs if (ROOT / "docs" / "reviews" / s / "review.json").exists()]
    bad = 0
    for slug in slugs:
        doc = build(slug)
        path = ROOT / "cache" / slug / "funding_sources.json"
        text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
        if not doc["trials"]:
            if path.exists() and not check:
                path.unlink()
            continue
        same = path.exists() and path.read_text(encoding="utf-8") == text
        if check:
            bad += not same
        elif not same:
            path.write_text(text, encoding="utf-8", newline="\n")
        print(slug, len(doc["trials"]), "CURRENT" if same else ("STALE" if check else "WRITTEN"))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
