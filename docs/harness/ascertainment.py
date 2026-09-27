"""The B-prime outcome-ascertainment clause, executable (V1.0.1, GLP-1 review).

The GLP-1 protocol's B-prime amendment admits a trial only if "3-point MACE, or its exact three components, was
prospectively specified and systematically ascertained". Before this module, screen_family read the design and
population half of that sentence and deliberately skipped the outcome half, so every family passing the structural
checks was called ELIGIBLE: "145 eligible" was 145 STRUCTURAL passes, not 145 B-prime-eligible trials.

Three states, derived per family and never inferred from a trial's name or size:
  STRUCTURAL_PASS   design, population, intervention and control checks pass (screen_family)
  FULL_ELIGIBLE     STRUCTURAL_PASS and both halves of the clause are evidenced from held bytes:
                      prospective  -- a source dated BEFORE the trial's results were published names 3-point MACE (or
                                      all three components) as a specified outcome
                      ascertained  -- a source states the events were adjudicated / systematically ascertained
  ADMISSIBLE_RESULT per analysis (trial_family.derive_count_chain): a FULL_ELIGIBLE family whose result for that
                    analysis is held and in its pool.
Unknown ascertainment is PENDING with a retrieval task (protocol / SAP / supplement); it is never auto-eligible and
never auto-excluded. A pooled family that is PENDING stays in the pool and is rendered as such, so the result reads
as conditional on it -- removing it would be an automatic exclusion.

A programme-level statement (Husain 2020: the SUSTAIN and PIONEER glycaemic trials recorded MACE "as adjudicated
adverse events ... using the same terms as the CVOTs") supports ASCERTAINMENT for the trials it names; it never
establishes prospective specification, and its pooled post-hoc estimate never enters any pool as a trial.

Evidence: cache/<slug>/ascertainment_evidence.json (scripts/ascertainment_evidence.py). Every quote is located in held
bytes (whitespace- and tag-normalised on both sides) and must match the clause's vocabulary, and every prospective
source's date must precede the results date; otherwise the evidence file is refused.
"""
from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path
from typing import Optional

CLAUSE = "prospectively specified and systematically ascertained"
MACE = re.compile(r"\bMACE\b|major adverse cardiovascular event", re.I)
_CVD = re.compile(r"cardiovascular death|death from cardiovascular causes|\bCV death|cardiovascular \(CV\) death", re.I)
_MI = re.compile(r"myocardial infarction|\bMI\b", re.I)
_STROKE = re.compile(r"stroke", re.I)
ADJ = re.compile(r"adjudicat|events? (?:classification |adjudication |endpoint )?committee|\bCEC\b|\bEAC\b", re.I)
# 'all the components of the primary composite outcome' (EXSCEL) names the MACE composite by its role
_CV_EVENTS = re.compile(r"cardiovascular|\bCV\b|MACE|myocardial infarction|stroke|primary composite (?:outcome|end ?point)", re.I)
RETRIEVAL_TASK = ("retrieve the trial protocol, statistical analysis plan or primary-report supplement (dated before "
                  "the results) that names 3-point MACE or its three components as a specified outcome, and a statement "
                  "that these events were adjudicated or systematically ascertained")


class EvidenceRefused(ValueError):
    pass


def _norm(s) -> str:
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", str(s or "")))).strip()


def names_mace(q: str) -> bool:
    return bool(MACE.search(q) or (_CVD.search(q) and _MI.search(q) and _STROKE.search(q)))


def states_ascertainment(q: str) -> bool:
    return bool(ADJ.search(q) and _CV_EVENTS.search(q))


def clause_required(protocol_line: str) -> bool:
    return CLAUSE in (protocol_line or "")


def acronym_key(s) -> str:
    s = re.sub(r"[™®]", "", str(s or "")).upper()
    return re.sub(r"[\s\-]+", " ", s).strip()


def _doc_text(root, doc) -> str:
    """The held text a quote must be found in -- narrowed to ONE article of a PubMed batch (`pmid`) or ONE row of a
    held AACT extract (`row_id`), so a quote can never be located in a neighbouring record."""
    raw = (Path(root) / doc["document_ref"]).read_text(encoding="utf-8")
    if doc.get("pmid"):
        arts = re.findall(r"<PubmedArticle>.*?</PubmedArticle>", raw, re.S)
        raw = next((a for a in arts if re.search(r"<PMID[^>]*>" + re.escape(str(doc["pmid"])) + r"</PMID>", a)), None)
        if raw is None:
            raise EvidenceRefused(f"PMID {doc['pmid']} not in {doc['document_ref']}")
    elif doc.get("row_id"):
        rows = json.loads(raw)["rows"]
        row = next((r for r in rows if str(r["id"]) == str(doc["row_id"])), None)
        if row is None:
            raise EvidenceRefused(f"row {doc['row_id']} not in {doc['document_ref']}")
        raw = " ".join(str(row.get(k) or "") for k in ("measure", "description"))
    return _norm(raw)


def load(root, slug) -> Optional[dict]:
    p = Path(root) / "cache" / slug / "ascertainment_evidence.json"
    if not p.exists():
        return None
    ev = json.loads(p.read_text(encoding="utf-8"))
    docs = ev.get("documents") or {}
    texts = {k: _doc_text(root, d) for k, d in docs.items()}

    def check(owner, item, kind):
        if item["doc"] not in docs:
            raise EvidenceRefused(f"{owner}: {kind} cites unknown document {item['doc']}")
        if _norm(item["quote"]) not in texts[item["doc"]]:
            raise EvidenceRefused(f"{owner}: {kind} quote not located in {item['doc']}")
        if kind == "prospective" and not names_mace(item["quote"]):
            raise EvidenceRefused(f"{owner}: prospective quote names neither MACE nor its three components")
        if kind == "ascertained" and not states_ascertainment(item["quote"]):
            raise EvidenceRefused(f"{owner}: ascertainment quote states no adjudication/ascertainment of CV events")

    for fid, f in (ev.get("families") or {}).items():
        for kind in ("prospective", "ascertained"):
            if f.get(kind):
                check(fid, f[kind], kind)
        pro = f.get("prospective")
        if pro:
            src = docs[pro["doc"]].get("earliest_date")
            res = (f.get("results") or {}).get("earliest_date")
            if not (src and res and src < res):
                raise EvidenceRefused(f"{fid}: prospective source dated {src} is not before the results ({res})")
    for pg in ev.get("programmes") or []:
        check(pg["id"], pg, "ascertained")
    return ev


def decide(family_id: str, acronyms, ev: Optional[dict]) -> dict:
    """{'state': MET|PENDING, 'prospective': ..., 'ascertained': ..., 'retrieval_task'?} for one structural pass."""
    fam = ((ev or {}).get("families") or {}).get(family_id) or {}
    docs = (ev or {}).get("documents") or {}
    out = {}
    pro = fam.get("prospective")
    if pro:
        d = docs[pro["doc"]]
        tier = ("DATED_BEFORE_COMPLETION" if fam.get("completion_date") and d["earliest_date"] < fam["completion_date"]
                else "DATED_BEFORE_RESULTS_ONLY")
        out["prospective"] = {"state": "YES", "doc": pro["doc"], "doc_kind": d.get("kind"), "source_date": d["earliest_date"],
                              "results_date": fam["results"]["earliest_date"], "date_tier": tier, "quote": pro["quote"]}
    else:
        out["prospective"] = {"state": "UNKNOWN", "why": fam.get("prospective_gap") or "no dated pre-results source held"}
    asc = fam.get("ascertained")
    keys = {acronym_key(a) for a in acronyms or []}
    prog = next((pg for pg in (ev or {}).get("programmes") or []
                 if keys & {acronym_key(a) for a in pg.get("applies_to_acronyms") or []}), None)
    if asc:
        out["ascertained"] = {"state": "YES", "doc": asc["doc"], "doc_kind": docs[asc["doc"]].get("kind"), "quote": asc["quote"]}
    elif prog:
        out["ascertained"] = {"state": "YES", "doc": prog["doc"], "doc_kind": docs[prog["doc"]].get("kind"),
                              "quote": prog["quote"], "via_programme": prog["id"], "programme_note": prog.get("note")}
    else:
        out["ascertained"] = {"state": "UNKNOWN", "why": "no held statement that the events were adjudicated or systematically ascertained"}
    met = out["prospective"]["state"] == "YES" and out["ascertained"]["state"] == "YES"
    out["state"] = "MET" if met else "PENDING"
    if not met:
        out["retrieval_task"] = RETRIEVAL_TASK
    return out


def render(nodes: list, chain: dict) -> str:
    """The per-state counts and every PENDING family's retrieval task."""
    e = lambda s: _html.escape(str(s), quote=True)  # noqa: E731
    fams = [f for f in nodes if (f.get("eligibility") or {}).get("ascertainment")]
    if not fams:
        return ""
    pend = [f for f in fams if f["eligibility"]["ascertainment"]["state"] != "MET"]
    rows = "".join(
        f"<li><strong>{e(f['family_id'])}</strong> ({e(', '.join((f.get('aliases') or {}).get('acronym') or []) or 'no acronym')}): "
        f"prospective <code>{e(f['eligibility']['ascertainment']['prospective']['state'])}</code>, ascertained "
        f"<code>{e(f['eligibility']['ascertainment']['ascertained']['state'])}</code>"
        + (" -- <strong>in the primary pool</strong>, so the pooled result is conditional on it" if f["family_id"] in (chain.get("pooled_with_ascertainment_pending") or []) else "")
        + "</li>" for f in pend[:400])
    adm = "; ".join(f"{e(k)}: {e(v)}" for k, v in sorted((chain.get("admissible_result") or {}).items()))
    return ("<div class='ascertainment-states'><h5>B-prime eligibility states (outcome-ascertainment clause executed)</h5>"
            f"<p>STRUCTURAL_PASS {e(chain.get('structural_pass'))}; FULL_ELIGIBLE {e(chain.get('eligible_families'))}; "
            f"PENDING (outcome ascertainment not yet evidenced) {e(chain.get('ascertainment_pending'))}. "
            f"ADMISSIBLE_RESULT per analysis: {adm or 'none'}. A PENDING family is neither eligible nor excluded: "
            f"its retrieval task is &ldquo;{e(RETRIEVAL_TASK)}&rdquo;.</p>"
            f"<details><summary>PENDING families ({len(pend)})</summary><ul>{rows}</ul></details></div>")
