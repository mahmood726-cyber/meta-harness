"""Typed funding object per pooled trial (V1.0.1), replacing the single public-vs-industry label.

    {funders[], material_support[], funder_role_statement, list_completeness, industry_tie, label, funding_state}

Why: the old label came from the first funding sentence found. LoDoCo2's abstract reads "(Funded by the National
Health Medical Research Council of Australia and others; ...)" and was served as public/non-profit, while its
publisher funding metadata names "Teva, Haarlem, Disphar, Baarn and Tiofarma" and its registry types Teva, Disphar,
Tiofarma, Aspen and GenesisCare as "Commercial sector/Industry". "A public funder and others" is a PARTIAL list and
never establishes the absence of an industry tie.

Sources, each carried with its own span or document hash:
  - the full-text funding statement (held ft_*.txt), read by regex: funders, material support, the funder-role
    statement ("the funders had no role in ...");
  - the abstract funding sentence;
  - the publisher funding metadata and the registry's typed funder list (cache/<slug>/funding_sources.json, packed
    from held bytes by scripts/funding_sources.py);
  - the AACT sponsor rows (lead / collaborator, agency_class).

A funder is classified INDUSTRY or PUBLIC by a registry category that names it, else by the name markers of
harness/funding.py; otherwise it stays UNCLASSIFIED -- and an unclassified funder is listed as needing a proposal.
A model proposal (cache/<slug>/funding_proposals.json, recorded with model, time and prompt hash) is SHOWN, never
applied: it cannot turn NOT_ESTABLISHED into ABSENT.

industry_tie:
  PRESENT          any source names an industry funder, sponsor, collaborator or material supplier
  ABSENT           a complete funding statement is held (no 'and others'), every named funder is classified
                   non-industry, no material support is from industry, and no other source names industry
  NOT_ESTABLISHED  otherwise (a partial list, registry-only declarations, unclassified funders, nothing held)
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from . import funding as _f

PRESENT, ABSENT, NOT_ESTABLISHED = "PRESENT", "ABSENT", "NOT_ESTABLISHED"
LABELS = {
    PRESENT: "industry tie present",
    ABSENT: "no industry tie (complete funding statement held)",
}
_PARTIAL = re.compile(r"\b(?:and|among) others\b|\bamong other (?:sources|funders)\b|\bet al\b|\binter alia\b", re.I)
_STATEMENT = re.compile(
    r"(?:\bfunded by\b|\bsupported by\b|\bfunding(?: source)?\s*:|\bfinancial support\b|\bgrants? from\b|\bsponsored by\b"
    r"|\bthis (?:study|trial|work|research) was (?:funded|supported|sponsored)\b|\bfunding for this)", re.I)
_ROLE = re.compile(
    r"[^.]*\b(?:funders?|sponsors?|funding (?:source|sources|bod(?:y|ies)|agenc(?:y|ies)|organi[sz]ations?)|"
    r"compan(?:y|ies)|consortium|manufacturers?)\b[^.]*\b(?:no|not|nor|without)\b[^.]*"
    r"\b(?:role|involvement|involved|influence|control|input|say)\b[^.]*\.", re.I)
_ROLE_WORDS = (("design", r"\bdesign"), ("conduct", r"\bconduct"), ("data collection", r"\bcollect"),
               ("analysis", r"\banaly[sz]"), ("interpretation", r"\binterpret"),
               ("reporting", r"\breport|\bwriting|\bmanuscript|\bpreparation"),
               ("decision to submit", r"\bsubmi|\bpublication"))
_SUPPLY = re.compile(r"(?:provided|supplied|donated|manufactured|furnished|gifted)\s+(?:free of charge\s+)?by\s+([^.;()]+)",
                     re.I)
# active voice: "Roche provided the drug and its distribution to the centers"
_SUPPLY_ACTIVE = re.compile(r"\b([A-Z][\w&.'-]*(?:\s+[A-Z][\w&.'-]*){0,4})\s+(?:kindly\s+|generously\s+)?(?:provided|supplied|"
                            r"donated|manufactured|furnished)\s+(?:the\s+|all\s+)?(?:study\s+|trial\s+|active\s+)?"
                            r"(?:drugs?|medications?|tablets|capsules|placebo|colchicine|products?)\b")
# an author's conflict-of-interest disclosure is not the trial's funding statement
# author-level disclosures only: the word 'disclosure' alone is often a SECTION HEADING that tag-stripping merges into
# the funding sentence ("Acknowledgment/disclosure All the studies ... were supported by Neurim Pharmaceuticals")
_COI = re.compile(r"\breported (?:receiving|grants|personal|consult)|\bdisclosed (?:receiving|that)|\bhas (?:received|served)"
                  r"|\bhonorari|\bspeaker(?:s'? bureau| fees)|\badvisory board|\bstock(?:holder| ownership)", re.I)
_WORD = re.compile(r"[A-Za-z][A-Za-z&'-]{3,}")


def _clean(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text or "") if s.strip()]


def statement(fulltext: str) -> dict:
    """Regex reading of a held full text's funding statement: the funding sentences, the material-support sentences
    and the funder-role statement, each verbatim."""
    import html as _h
    text = _clean(_h.unescape(re.sub(r"<[^>]+>", " ", fulltext or "")))       # held JATS/HTML: tags are not text
    sents = _sentences(text)
    fund = [s for s in sents if _STATEMENT.search(s) and not _ROLE.fullmatch(s) and not _COI.search(s)]
    role = [_clean(m.group(0)) for m in _ROLE.finditer(text)]
    supply = [s for s in sents if not _COI.search(s) and (_SUPPLY_ACTIVE.search(s) or (
        _SUPPLY.search(s) and re.search(r"drug|medication|tablet|capsule|placebo|colchicine|product|device|kit|supplies", s, re.I)))]
    return {"funding_sentences": fund[:4], "role_sentences": role[:2], "supply_sentences": supply[:3]}


def _registry_index(sources: list) -> dict:
    """name-word -> category, from the registry's typed funder rows."""
    idx = {}
    for src in sources:
        if not src.get("registry_id"):
            continue
        for row in src.get("funders") or []:
            cat = _category(row.get("category"))
            if not cat:
                continue
            for w in _WORD.findall(row.get("name") or ""):
                if w.lower() not in {"australia", "netherlands", "foundation", "research", "council", "national", "health",
                                     "medical", "university", "hospital", "institute", "the", "and", "pharma", "care"}:
                    idx.setdefault(w.lower(), set()).add((cat, row["name"]))
    return idx


def _category(raw) -> Optional[str]:
    s = str(raw or "").lower()
    if not s:
        return None
    if "industry" in s or "commercial" in s:
        return "INDUSTRY"
    if s in {"nih", "fed", "other_gov", "network", "other", "indiv", "ambig"} or any(
            k in s for k in ("government", "charit", "societ", "foundation", "hospital", "university", "universit")):
        return "PUBLIC" if s not in {"other", "indiv", "ambig", "unknown"} else None
    return None


def classify(name: str, reg_idx: dict) -> tuple:
    """(INDUSTRY|PUBLIC|UNCLASSIFIED, basis)."""
    hits = {(cat, rn) for w in _WORD.findall(name or "") for (cat, rn) in reg_idx.get(w.lower(), ())}
    if any(c == "INDUSTRY" for c, _ in hits):
        rn = sorted(r for c, r in hits if c == "INDUSTRY")
        return "INDUSTRY", "registry category Commercial sector/Industry names " + "; ".join(rn)
    if hits:
        return "PUBLIC", "registry category names " + "; ".join(sorted(r for _, r in hits))
    if _f._INDUSTRY.search(name or ""):
        return "INDUSTRY", "industry name marker: " + _f._INDUSTRY.search(name).group(0)
    if _f._PUBLIC.search(name or ""):
        return "PUBLIC", "public/non-profit name marker: " + _f._PUBLIC.search(name).group(0)
    return "UNCLASSIFIED", "no registry category and no name marker"


def build(trial_id: str, abstract: str, fulltext: str, sources: list, aact_rows: list,
          proposals: Optional[dict] = None) -> dict:
    reg_idx = _registry_index(sources)
    funders, supply, completeness = [], [], []

    def add(name, source, span=None, category=None, role=None, grant=None):
        name = _clean(name).strip(" ,;.")
        if len(name) < 3:
            return
        cls, basis = (_category(category), "registry category: " + str(category)) if _category(category) else classify(name, reg_idx)
        funders.append({"name": name, "class": cls or "UNCLASSIFIED", "class_basis": basis if cls else "no category",
                        "source": source, **({"span": span} if span else {}), **({"role": role} if role else {}),
                        **({"grant_id": grant} if grant else {})})

    ft = statement(fulltext) if fulltext else None
    if ft:
        for s in ft["funding_sentences"]:
            for n in _f._split_sponsors(s):
                add(n, "full-text funding statement", s)
            completeness.append(("full-text funding statement", "PARTIAL" if _PARTIAL.search(s) else "COMPLETE", s))
        for s in ft["supply_sentences"]:
            m = _SUPPLY_ACTIVE.search(s) or _SUPPLY.search(s)
            who = _clean(m.group(1))
            cls, basis = classify(who, reg_idx)
            supply.append({"supplier": who, "class": cls, "class_basis": basis, "source": "full text", "span": s})
    # the sentence classifier's full-text reading is a witness too: the typed object must never know LESS than the
    # legacy label did (a missed statement would silently drop an industry tie)
    ftd = _f.detect(fulltext or "", "fulltext", "full text", "full text") if fulltext else None
    if ftd and ftd.get("span"):
        for n in _f._split_sponsors(ftd["span"]):
            add(n, "full-text funding sentence (sentence classifier)", ftd["span"])
        if ftd.get("note") == "study drug supplied by industry" and ftd.get("span"):
            supply.append({"supplier": "; ".join(_f._split_sponsors(ftd["span"])) or "industry (see span)",
                           "class": "INDUSTRY", "class_basis": "sentence classifier: study drug supplied by industry",
                           "source": "full text", "span": ftd["span"]})
    ab = _f.detect(abstract or "", "abstract", "abstract")
    if ab and ab.get("span"):
        for n in _f._split_sponsors(ab["span"]):
            add(n, "abstract funding sentence", ab["span"])
        completeness.append(("abstract funding sentence", "PARTIAL" if _PARTIAL.search(ab["span"]) else "COMPLETE",
                             ab["span"]))
    for src in sources:
        for row in src.get("funders") or []:
            add(row.get("name"), src["source"], None, row.get("category"), row.get("role"), row.get("grant_id"))
    for row in aact_rows or []:
        add(row.get("name"), "AACT sponsors", None, row.get("agency_class"), row.get("lead_or_collaborator"))

    role = {"state": "FULL_TEXT_NOT_HELD"}
    if ft is not None:
        if ft["role_sentences"]:
            q = ft["role_sentences"][0]
            role = {"state": "STATED", "quote": q, "source": "full text",
                    "roles_excluded": [n for n, p in _ROLE_WORDS if re.search(p, q, re.I)]}
        else:
            role = {"state": "NOT_STATED_IN_HELD_FULL_TEXT"}

    industry = [x for x in funders if x["class"] == "INDUSTRY"] + [x for x in supply if x["class"] == "INDUSTRY"]
    complete = [c for c in completeness if c[0] == "full-text funding statement" and c[1] == "COMPLETE"]
    partial = [c for c in completeness if c[1] == "PARTIAL"]
    if industry:
        tie = PRESENT
        why = "industry named by: " + "; ".join(sorted({f"{x.get('name') or x.get('supplier')} ({x['source']})" for x in industry}))
    elif complete and not partial and funders and all(x["class"] == "PUBLIC" for x in funders) \
            and not any(x["class"] != "PUBLIC" for x in supply):
        tie, why = ABSENT, "complete full-text funding statement; every named funder is non-industry"
    else:
        tie = NOT_ESTABLISHED
        bits = []
        if partial:
            bits.append("the funder list is partial ('" + _PARTIAL.search(partial[0][2]).group(0) + "' in the "
                        + partial[0][0] + ")")
        if not complete:
            bits.append("no complete funding statement is held")
        unc = [x["name"] for x in funders if x["class"] == "UNCLASSIFIED"]
        if unc:
            bits.append("unclassified funder(s): " + "; ".join(unc[:4]))
        why = "; ".join(bits) or "no funder named in any held source"
    ambiguous = [x["name"] for x in funders if x["class"] == "UNCLASSIFIED"]
    public_named = any(x["class"] == "PUBLIC" for x in funders)
    label = LABELS.get(tie) or ("public funder named; industry tie not established" if public_named else None)
    state = {PRESENT: "INDUSTRY_TIE_PRESENT", ABSENT: "NO_INDUSTRY_TIE"}.get(tie) or (
        "INDUSTRY_TIE_NOT_ESTABLISHED" if funders else None)
    sponsor_class = None
    if tie == PRESENT:
        sponsor_class = "industry" if all(x["class"] == "INDUSTRY" for x in funders if x["class"] != "UNCLASSIFIED") else "mixed"
    elif tie == ABSENT:
        sponsor_class = "public"
    elif public_named:
        sponsor_class = "public_named_tie_not_established"
    out = {"schema": "funding-typed-v1", "trial": trial_id,
           "funders": funders, "material_support": supply, "funder_role_statement": role,
           "list_completeness": [{"source": s, "state": st} for s, st, _ in completeness],
           "industry_tie": tie, "industry_tie_basis": why,
           "label": label, "funding_state": state, "sponsor_class": sponsor_class,
           "needs_proposal": ambiguous}
    rec = (proposals or {}).get(trial_id)
    if rec:
        out["proposal"] = dict(rec, applied=False,
                               note="a recorded model proposal, shown only; it does not change industry_tie")
    elif ambiguous:
        out["proposal"] = {"state": "PROPOSAL_NOT_REQUESTED", "applied": False}
    return out


def load_sources(root, slug) -> dict:
    p = Path(root) / "cache" / slug / "funding_sources.json"
    return json.loads(p.read_text(encoding="utf-8")).get("trials", {}) if p.exists() else {}


def load_proposals(root, slug) -> dict:
    p = Path(root) / "cache" / slug / "funding_proposals.json"
    return json.loads(p.read_text(encoding="utf-8")).get("trials", {}) if p.exists() else {}


def render_cells(item: dict):
    """(funding cell, funders cell) HTML for a row that carries the typed object, or None."""
    import html as _h
    t = item.get("typed") or {}
    if not t.get("industry_tie"):
        return None
    e = lambda s: _h.escape(str(s), quote=True)  # noqa: E731
    role = t.get("funder_role_statement") or {}
    role_txt = ({"STATED": "funder-role statement: “" + str(role.get("quote")) + "”",
                 "NOT_STATED_IN_HELD_FULL_TEXT": "no funder-role statement in the held full text",
                 "FULL_TEXT_NOT_HELD": "funder-role statement: full text not held"}).get(role.get("state"), "")
    comp = "; ".join(f"{c['source']}: {c['state']}" for c in t.get("list_completeness") or [])
    cell1 = "<br>".join(x for x in (
        f"<strong>{e(t.get('label') or item.get('type') or '')}</strong>",
        f"industry tie: <code>{e(t['industry_tie'])}</code> &mdash; {e(t.get('industry_tie_basis') or '')}",
        f"list completeness: {e(comp)}" if comp else "",
        e(role_txt),
        (f"<em>first-sentence label was: {e(item.get('label_from_first_sentence'))}</em>"
         if item.get("label_from_first_sentence") and item.get("label_from_first_sentence") != t.get("label") else ""),
    ) if x)
    seen, rows = set(), []
    for f in t.get("funders") or []:
        key = (f["name"].lower(), f["class"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(f"{e(f['name'])} <code>{e(f['class'])}</code> <em>({e(f['source'])})</em>")
    for m in t.get("material_support") or []:
        rows.append(f"material support: {e(m['supplier'])} <code>{e(m['class'])}</code> &mdash; “{e(m['span'])}”")
    if t.get("needs_proposal"):
        rows.append("<em>unclassified (no registry category, no name marker): "
                    + e("; ".join(dict.fromkeys(t["needs_proposal"]))) + "</em>")
    return cell1, ("<br>".join(rows) or "&mdash;")
