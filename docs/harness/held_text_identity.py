"""A held comparator full text must be the comparator's OWN text (V1.0.1, DOAC-VTE review).

records.json carries comparator_fulltext fetched from PMC. Before f32c307a the fetcher took the first PMC link
elink returned; when the comparator is not itself in PMC, elink returns only 'pubmed_pmc_refs' (articles that CITE
it), so a citing article's text was stored under the comparator's PMID. van Es 2014 (PMID 24963045) was held as a
review of DOAC interference with thrombophilia testing; Imazio 2012 (22442198) as a later network meta-analysis;
Cheema 2024 (38128217) as another CAP meta-analysis.

cache/<slug>/pmc_links.json (scripts/pmc_links.py: the elink response with its request, time and sha256) is the
proof. comparator_fulltext is used only when that record shows the comparator's own 'pubmed_pmc' link; otherwise it
is REFUSED -- never read, and the refusal is disclosed. A missing record refuses too (fail closed).
"""
from __future__ import annotations

import json
import os

REFUSED = "HELD_TEXT_NOT_THE_COMPARATOR"


def comparator_text_state(root: str, slug: str, records: dict) -> dict:
    if not (records.get("comparator_fulltext") or ""):
        return {"state": "NONE_HELD"}
    p = os.path.join(root, "cache", slug, "pmc_links.json")
    if not os.path.exists(p):
        return {"state": REFUSED, "why": f"no cache/{slug}/pmc_links.json: the held text's identity is not proved"}
    doc = json.load(open(p, encoding="utf-8"))
    if str(doc.get("pmid")) != str(records.get("comparator_pmid")):
        return {"state": REFUSED, "why": f"cache/{slug}/pmc_links.json records PMID {doc.get('pmid')}, "
                                         f"not the comparator PMID {records.get('comparator_pmid')}"}
    if doc.get("state") == "OWN_PMC_LINK" and doc.get("own_pmcid"):
        return {"state": "OWN_TEXT", "pmcid": doc["own_pmcid"], "evidence": f"cache/{slug}/pmc_links.json"}
    return {"state": REFUSED, "evidence": f"cache/{slug}/pmc_links.json", "linknames": doc.get("linknames"),
            "why": ("PubMed lists no PMC copy of the comparator itself (elink returns only "
                    "'pubmed_pmc_refs', the articles that cite it), so the held PMC text is another article's: it "
                    "was fetched before the same-article link rule (f32c307a) and is not read")}


def sanitize(root: str, slug: str, records: dict) -> dict:
    """records with comparator_fulltext emptied when it is not proved to be the comparator's own text; the decision
    is kept on records['comparator_fulltext_identity'] for the page."""
    st = comparator_text_state(root, slug, records)
    if st["state"] != REFUSED:
        return dict(records, comparator_fulltext_identity=st) if st["state"] == "OWN_TEXT" else records
    out = dict(records)
    out["comparator_fulltext"] = ""
    out["comparator_fulltext_identity"] = dict(st, held_chars=len(records.get("comparator_fulltext") or ""))
    return out


def render(identity: dict) -> str:
    import html
    if not identity or identity.get("state") != REFUSED:
        return ""
    e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
    return (f"<p class='comparator-text-refused'><strong>Held comparator full text refused</strong> "
            f"(<code>{e(REFUSED)}</code>): {e(identity.get('why'))}. Evidence: {e(identity.get('evidence'))}. "
            f"Everything on this page about the comparator is read from its abstract and any separately held, "
            f"identity-checked text only.</p>")
