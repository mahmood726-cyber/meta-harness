"""Per-trial funding / conflict-of-interest disclosure (ME-32).

A documented reporting-bias dimension: industry-funded trials tend to report more favourable results
than independently funded ones. The harness cannot ADJUST for this (the direction/magnitude per trial
is not quantifiable from a funding line), so — like the unit-of-analysis caveat — this is a RENDERED
DISCLOSURE, not a gate and not an adjustment: for each pooled trial, classify the funding source from a
VERBATIM statement located in the committed source (full text preferred, abstract fallback) and show it,
or state plainly that funding is not stated in the available source. Never inferred; refuse-on-absence.

Conservative on purpose: an industry/public marker only classifies when it sits in the FUNDING sentence
(a window around a funding anchor), so a company named in an unrelated sentence does not mislabel a trial.
Pure and fixture-tested; runs on committed text, so it replays offline and reproduces byte-for-byte.
"""
from __future__ import annotations

import re

# Funding statement anchors. STRONG anchors are unambiguously about who paid for the trial. The WEAK
# anchor ("supported by") is only accepted when an industry/public marker sits in its window, so
# "supported by evidence"/"supported by the data" does not masquerade as a funding statement.
_STRONG_ANCHOR = re.compile(
    r"(funded by|funding was provided|funding:|financial support|grants?\s+from|sponsored by|study sponsor"
    r"|role of the (?:funding source|sponsor)|this (?:study|trial|work|research) was (?:funded|supported|sponsored))",
    re.I)
_WEAK_ANCHOR = re.compile(r"supported by", re.I)

# Industry markers — a curated sponsor list plus generic corporate-entity suffixes.
_INDUSTRY = re.compile(
    r"\b(pharmaceutical|pharmaceuticals|biopharmaceutical|Inc\.|Incorporated|Ltd\.?|GmbH|LLC|Co\.,? Ltd"
    r"|manufacturer|Novo Nordisk|Pfizer|Janssen|AstraZeneca|Boehringer|Novartis|Bayer|Merck|MSD|Sanofi"
    r"|GlaxoSmithKline|GSK|Eli Lilly|Lilly|AbbVie|Amgen|Bristol[- ]Myers|Takeda|Roche|Genentech|Gilead"
    r"|Servier|Daiichi|Otsuka|Lundbeck|Actelion|Vertex|Vifor|CSL|Mylan|Teva|UCB|Grünenthal|Grunenthal"
    r"|Astellas|Bausch|Reckitt|Mundipharma|Cipla|Amarin"
    r"|Pharma\b|Pharma,|Therapeutics\b|Biosciences\b|Biotech|Laboratories\b|Sciences, Inc)\b", re.I)

# Public / non-profit markers, including explicit "no external funding" statements.
_PUBLIC = re.compile(
    r"\b(National Institutes of Health|NIH\b|NIHR|National Institute for Health(?: and Care)? Research"
    r"|Medical Research Council|MRC\b|Wellcome|Bill (?:& |and )?Melinda Gates|Gates Foundation|foundation"
    r"|university|college of|government|Ministry of Health|Department of Health|European (?:Commission|Union)"
    r"|Horizon 20\d\d|Canadian Institutes of Health|NHMRC|charit(?:y|able)|academic|institutional funds"
    r"|received no (?:specific |external )?funding|no external funding|no specific grant|not (?:externally )?funded)\b",
    re.I)


# Industry DRUG SUPPLY (an investigator-initiated trial can be publicly funded yet have its study drug
# donated by the manufacturer — a disclosable industry tie that is NOT a funding statement). Detected
# separately so it is surfaced, not lost to "not stated".
_DRUG_SUPPLY = re.compile(
    r"(study drug|study medication|trial (?:drug|medication)|active drug|investigational (?:drug|product|agent)"
    r"|drugs?|medication|tablets|capsules|treatment|placebo)s?\s+(?:and (?:matching )?placebo\s+)?"
    r"(?:were|was|is|are)?\s*(?:kindly |generously )?(?:provided|supplied|donated|manufactured|furnished|gifted)\s+by",
    re.I)

# A pointer that says funding IS declared but the detail lives outside the retrieved source (supplement /
# appendix / on request). This is "stated elsewhere, not here" — distinct from genuine silence.
_FUNDING_POINTER = re.compile(
    r"funding[^.]{0,70}(supplement|appendix|supporting information|available (?:on request|online))", re.I)


def _sentence_window(text: str, at: int, back: int = 15, fwd: int = 240) -> str:
    # Anchor-FORWARD: the sponsor follows the anchor ("funded by <X>"), so look mostly ahead. A small
    # look-back keeps the anchor phrase itself in view without catching a company named in the PRECEDING
    # sentence (which would misattribute funding), and makes the rendered span begin at the funding phrase.
    lo = max(0, at - back)
    hi = min(len(text), at + fwd)
    return text[lo:hi]


def detect(text: str) -> dict | None:
    """Return {'type': industry|public/non-profit|mixed|declared (unclassified), 'span': <verbatim>} for a
    funding statement located in `text`, else None (no funding statement in this source). Industry/public
    are decided within the FUNDING sentence window only, so an unrelated company mention does not classify."""
    if not text:
        return None
    ftype = span = note = None
    m = _STRONG_ANCHOR.search(text)
    strong = bool(m)
    if not m:
        m = _WEAK_ANCHOR.search(text)
    if m:
        win = _sentence_window(text, m.start())
        # For FUNDING classification, drop any drug-supply clause inside the window: a company that
        # "supplied/donated the study drug" is a SUPPLIER, not a funder, and must not flip a publicly
        # funded trial to industry/mixed. The supply tie is captured separately as a note below.
        _ds_in = _DRUG_SUPPLY.search(win)
        fund_win = win[:_ds_in.start()] if _ds_in else win
        ind = bool(_INDUSTRY.search(fund_win))
        pub = bool(_PUBLIC.search(fund_win))
        if ind and pub:
            ftype = "mixed"
        elif ind:
            ftype = "industry"
        elif pub:
            ftype = "public/non-profit"
        elif strong:
            ftype = "declared (source unclassified)"
        # a weak "supported by" with no funder marker in the window is NOT a funding statement -> ftype stays None
        if ftype:
            span = re.sub(r"\s+", " ", win).strip()
    # Industry drug-supply tie (a disclosable COI even without a funding statement). Surfaced so an
    # investigator-initiated / publicly funded trial with donated study drug is not scored "not stated".
    ds = _DRUG_SUPPLY.search(text)
    if ds:
        dwin = _sentence_window(text, ds.start(), back=5, fwd=140)
        if _INDUSTRY.search(dwin):
            if ftype and ftype not in ("industry",):
                note = "study drug supplied by industry"
            elif not ftype:
                ftype = "industry (drug supply)"
                span = re.sub(r"\s+", " ", dwin).strip()
    if ftype:
        out = {"type": ftype, "span": span}
        if note:
            out["note"] = note
        return out
    # Funding declared but detail is outside the retrieved source (supplement/appendix/on request).
    p = _FUNDING_POINTER.search(text)
    if p:
        return {"type": "stated (detail in supplement, not in retrieved source)",
                "span": re.sub(r"\s+", " ", _sentence_window(text, p.start(), back=5, fwd=120)).strip()}
    return None


def scan_pooled(review: dict, rec_by_id: dict, fulltext_by_pmid: dict | None = None) -> list:
    """Return [{id, type, span, source}] for every pooled trial (across all outcomes), classifying its
    funding from the committed full text (preferred — funding lines live there) then the abstract. A trial
    whose available source carries no funding statement is reported with type 'not stated in source' so the
    disclosure is honest about silence rather than omitting the trial."""
    fulltext_by_pmid = fulltext_by_pmid or {}
    seen, out = set(), []
    for o in review.get("outcomes", []) or []:
        for t in o.get("trials", []) or []:
            raw = str(t.get("id", ""))
            pid = raw.replace("PMID ", "").strip()
            if not pid or pid in seen:
                continue
            seen.add(pid)
            rec = rec_by_id.get(pid) or {}
            ft = fulltext_by_pmid.get(pid) or ""
            abs_ = (rec.get("title", "") + " " + rec.get("abstract", "")).strip()
            # scan DEPTH: whether we had the full text or only the abstract. This makes "not stated"
            # honest — a not-found in FULL TEXT (scanned deeply, genuinely silent) is a different claim
            # from a not-found in an ABSTRACT alone (full text not retrieved). The RAN_OK vs RAN_ZERO/
            # NOT_RUN distinction, applied to a disclosure field: absence of evidence is labelled with the
            # depth of the look, never presented as evidence of absence.
            scanned = "full text" if ft else "abstract only"
            ft_hit = detect(ft)
            hit = ft_hit or detect(abs_)
            if hit:
                row = {"id": t.get("id"), "type": hit["type"], "span": hit["span"],
                       "source": "full text" if ft_hit else "abstract", "scanned": scanned}
                if hit.get("note"):
                    row["note"] = hit["note"]
                out.append(row)
            else:
                out.append({"id": t.get("id"),
                            "type": ("not stated (full text scanned)" if ft
                                     else "not stated (abstract only — full text not retrieved)"),
                            "span": "", "source": scanned, "scanned": scanned})
    return out
