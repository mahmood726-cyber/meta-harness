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
    r"(?:\bfunded by\b|\bsupported by\b|\bfunding(?:/support| source)?\s*:|\bfinancial support\b|\bgrants? from\b"
    r"|\bsponsored by\b|\bfinanced by\b|\bfunding (?:was|is) provided by\b"
    r"|(?<!writing )(?<!editorial )\bsupport (?:was|is) provided by\b"
    r"|\bthis (?:study|trial|work|research) was (?:funded|supported|sponsored)\b|\bfunding for this)", re.I)
# an author-contribution line ("Obtained funding: Hermine, Mariette.") names who raised money, not who gave it
# ... and "Funding: HABF, BV." lists authors by initials under a contributions heading
_CONTRIB = re.compile(r"\bobtained funding\s*:|^funding\s*:\s*(?-i:[A-Z]{2,5})(?:\s*(?:,|and)\s*(?-i:[A-Z]{2,5}))*\.?$", re.I)
_ROLE = re.compile(
    r"[^.]*\b(?:funders?|sponsors?|funding (?:source|sources|bod(?:y|ies)|agenc(?:y|ies)|organi[sz]ations?)|"
    r"compan(?:y|ies)|consortium|manufacturers?)\b[^.]*\b(?:no|not|nor|without)\b[^.]*"
    r"\b(?:role|involvement|involved|influence|control|input|say)\b[^.]*\.", re.I)
_ROLE_WORDS = (("design", r"\bdesign"), ("conduct", r"\bconduct"), ("data collection", r"\bcollect"),
               ("analysis", r"\banaly[sz]"), ("interpretation", r"\binterpret"),
               ("reporting", r"\breport|\bwriting|\bmanuscript|\bpreparation"),
               ("decision to submit", r"\bsubmi|\bpublication"))
# "provided free of charge for this study by Roche"; a company suffix or initial keeps its period ("Wecare Probiotics
# Co. Ltd.", "Winclove Probiotics B.V")
_SUPPLY = re.compile(r"(?:provided|supplied|donated|manufactured|furnished|gifted)\s+"
                     r"(?:(?:free of charge|for (?:this|the) (?:study|trial)|for study purposes)\s+){0,3}by\s+"
                     r"((?:[^.;()]|(?<=\bCo)\.|(?<=\bLtd)\.|(?<=(?<![\w/])[A-Z])\.|(?<=\bB\.V)\.){1,200})", re.I)
_PRODUCT = re.compile(r"drug|medication|tablet|capsule|placebo|colchicine|product|device|kit|supplies|\bagents?\b|probiotic"
                      r"|\bstrains?\b|study drink|supplement", re.I)
# active voice: "Roche provided the drug and its distribution to the centers"; "Novo Nordisk A/S provided the
# investigational drug"; "BASF (Omacor fish oil) donated the study agents"; "AbbVie contributed some supplies of ..."
_SUPPLY_ACTIVE = re.compile(r"\b([A-Z][\w&.'/+-]*(?:\s+[A-Z][\w&.'/+-]*){0,4})(?:\s+\([^()]{1,60}\))?\s+(?:kindly\s+|generously\s+)?"
                            r"(?:(?:provided|supplied|manufactured|furnished)\s+(?:the\s+|all\s+|free\s+)?"
                            r"(?:study\s+|trial\s+|active\s+|investigational\s+|matching\s+){0,2}"
                            r"(?:drugs?|medications?|tablets|capsules|placebos?|colchicine|products?|agents?|LcS)\b"
                            r"|donated\b|contributed\s+(?:some\s+)?supplies\b)")
# an author's conflict-of-interest disclosure is not the trial's funding statement
# author-level disclosures only: the word 'disclosure' alone is often a SECTION HEADING that tag-stripping merges into
# the funding sentence ("Acknowledgment/disclosure All the studies ... were supported by Neurim Pharmaceuticals")
_COI = re.compile(r"\breported (?:receiving|grants|personal|consult)|\bdisclosed (?:receiving|that)|\bhas (?:received|served)"
                  r"|\bhonorari|\bspeaker(?:s'? bureau| fees)|\badvisory board|\bstock(?:holder| ownership)"
                  # V1.0.1 funding audit: with every matching sentence now read, author disclosures that name companies
                  # must not become the trial's funders ("personal fees from Bayer", "... outside the submitted work")
                  r"|\boutside (?:of )?the submitted work|\bpersonal fees\b|\b(?:lecture|consult(?:ing|ancy)?) fees\b"
                  r"|\bfunds for lectures\b|\breports? (?:receiving|grants|personal|consult|financial support|research support"
                  r"|nonfinancial|non-financial|equipment)|\breported\s+(?:\w+\s+){0,3}?(?:grants?|fees|funding|support|honoraria)\b"
                  r"|\bequipment, drugs,? or supplies\b"
                  # an author named by initials: "LKD receives a research grant from ...", "OB received grants from ..."
                  r"|(?-i:\b[A-Z]{2,4}\s+(?:receives|received|reports|reported|declares|declared|serves|served)\b)", re.I)
_WORD = re.compile(r"[A-Za-z][A-Za-z&'-]{3,}")
_SUFFIX_ONLY = re.compile(r"Inc|Incorporated|Ltd\.?|GmbH|LLC|B\.V|A/S|Co\.,? Ltd", re.I)


def _clean(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _sentences(text: str):
    # a company suffix or an initial is not a sentence end ("Yakult Honsha Co. Ltd.", "Funded by F. Hoffmann-La Roche")
    # a tag-stripped section heading is a boundary whatever precedes it ("... from Winclove B.V. Funding/Support: Both
    # the placebo ..." would otherwise merge an author's disclosure into the funding statement)
    return [s.strip() for s in re.split(r"(?<=[.!?])(?<!\bCo\.)(?<!(?<![\w/])[A-Z]\.)\s+(?=[A-Z(])"
                                        r"|\s+(?=(?:Funding(?:/Support)?|Role of the (?:Funder|Sponsor)(?:/Sponsor)?"
                                        r"|Conflict of Interest Disclosures|Author Contributions)\s*:)"
                                        r"|\s+(?=(?:Competing [Ii]nterests?|Conflicts? of [Ii]nterests?"
                                        r"|Declaration of (?:[Cc]ompeting )?[Ii]nterests?)\b)", text or "")
            if s.strip()]


# V1.0.1 COI lane (COI-C1): a sentence that OPENS an author-disclosure section, or whose subject is one author ("Semler
# was supported in part by grants from the NHLBI", "WGH was funded by an MRC award"), is not the trial's funding
_COI_HEAD = re.compile(r"(?:Competing interests?|Conflicts? of interests?|Declaration of (?:competing )?interests?"
                       r"|Conflict of Interest Disclosures)\b", re.I)
_AUTHOR_SUBJECT = re.compile(r"(?:Dr\.?\s+)?(?:[A-Z][a-z]+|[A-Z]{2,3})(?:\s+(?:and|&)\s+(?:[A-Z][a-z]+|[A-Z]{2,3}))?"
                             r"\s+(?:is|are|was|were)\s+(?:supported|funded)\b")
# an author's company role blocks ABSENT: "Sue Plummer is a Director of Cultech Ltd." (the trial's funder may be public)
_AUTHOR_ROLE = re.compile(r"\b(?:is|are|was|were)\s+(?:an?\s+|the\s+)?(?:[Mm]anaging\s+)?(?:[Dd]irector|[Ee]mployee|"
                          r"[Ss]hareholder|[Ff]ounder|[Cc]o-founder|[Ss]tockholder)s?\s+(?:of|at|for)\s+([A-Z][^.;]{2,80})")


def _disclosure(s: str) -> bool:
    return bool(_COI.search(s) or _COI_HEAD.match(s) or _AUTHOR_SUBJECT.match(s))


def statement(fulltext: str) -> dict:
    """Regex reading of a held full text's funding statement: the funding sentences, the material-support sentences
    and the funder-role statement, each verbatim."""
    import html as _h
    text = _clean(_h.unescape(re.sub(r"<[^>]+>", " ", fulltext or "")))       # held JATS/HTML: tags are not text
    sents = _sentences(text)
    fund = [s for s in sents if _STATEMENT.search(s) and not _ROLE.fullmatch(s) and not _disclosure(s)
            and not _CONTRIB.search(s)]
    role = [_clean(m.group(0)) for m in _ROLE.finditer(text)]
    supply = [s for s in sents if not _disclosure(s) and (_SUPPLY_ACTIVE.search(s) or (
        _SUPPLY.search(s) and (_PRODUCT.search(s) or _f._INDUSTRY.search(re.split(r",|\band\b", _SUPPLY.search(s).group(1))[0]))))]
    # every matching sentence is kept: a fixed cap is a reach limit, and a real statement after the cap was silently
    # dropped (EMPA-KIDNEY's 'sponsored by Boehringer Ingelheim' was the 5th match; COLCHICINE-PCI's supplier the 4th)
    roles = [s for s in sents if any(_f._INDUSTRY.search(m.group(1)) for m in _AUTHOR_ROLE.finditer(s))]
    return {"funding_sentences": fund, "role_sentences": role[:2], "supply_sentences": supply,
            "author_industry_roles": roles}


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
        mk = re.match(r"industry name marker: (.*)$", basis or "")
        if cls == "INDUSTRY" and category and mk and _SUFFIX_ONLY.fullmatch(mk.group(1).strip()):
            # FUND-F3: the registry classes the sponsor non-industry (AACT 'OTHER'); a bare company suffix does not
            # overrule it ("TriHealth Inc." is a non-profit hospital system). A named company still does.
            cls, basis = "UNCLASSIFIED", (f"registry class {category} against the company suffix '{mk.group(1)}': "
                                          "neither settles it")
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
            active = _SUPPLY_ACTIVE.search(s)
            m = active or _SUPPLY.search(s)
            who = _clean(m.group(1))
            cls, basis = classify(who, reg_idx)
            if cls == "UNCLASSIFIED" and active:
                # a list of donors is the verb's whole subject ("Pharmavite LLC ... and BASF (Omacor fish oil) donated"):
                # the regex keeps the last name only, so the subject clause is classified too
                subj = _clean(re.split(r"[;:]|\.\s", s[max(0, m.start() - 200):m.start(1)] + who)[-1])
                c2, b2 = classify(subj, reg_idx)
                if c2 == "INDUSTRY":
                    who, cls, basis = subj, c2, b2
            elif cls == "UNCLASSIFIED" and re.search(r"\bmanufactured\b", s[max(0, m.start() - 40):m.start(1)], re.I):
                # "manufactured and supplied by BioGaia": the supplier is named as the product's manufacturer
                cls, basis = "INDUSTRY", "named as the manufacturer of the study product"
            supply.append({"supplier": who, "class": cls, "class_basis": basis, "source": "full text", "span": s})
    # the sentence classifier's full-text reading is a witness too: the typed object must never know LESS than the
    # legacy label did (a missed statement would silently drop an industry tie)
    # read from the same tag-stripped text as statement(): raw JATS has no sentence boundary between an author's
    # conflict-of-interest paragraph and the funding paragraph, so the two merged into one 'funding sentence'
    import html as _h
    plain = _clean(_h.unescape(re.sub(r"<[^>]+>", " ", fulltext or ""))) if fulltext else ""
    ftd = _f.detect(plain, "fulltext", "full text", "full text") if plain else None
    if ftd and ftd.get("span") and _COI.search(ftd["span"]):
        ftd = None                                   # an author's disclosure is not the trial's funding
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
            and not any(x["class"] != "PUBLIC" for x in supply) and ft and ft.get("author_industry_roles"):
        # public money, but an author holds a company role: "no industry tie" would be false
        tie = NOT_ESTABLISHED
        why = ("every named funder is non-industry, but the held text gives an author a company role: '"
               + ft["author_industry_roles"][0][:200] + "'")
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
