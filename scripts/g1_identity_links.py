"""IDENTITY LINKS (reader, main): a comparator unit cited by a PubMed report that names no registration, joined to the
registered trial we already pool (gap list 8 Oct, sacubitril-valsartan-hfref: the comparator's 'Tsutsui, 2021' = PMID
33731544 is PARALLEL-HF, pooled as NCT02468232, but PubMed's record carries no NCT and CT.gov lists no reference, so no
join existed and the trial read NO_ROW while our own pool held it).

registry/identity_links.json holds a link PMID -> NCT only where TWO independent typed facts agreed, each with its verbatim
span and digest (ONE_NCT_STATED_IN_OWN_REPORT from a legitimately open copy; TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM against
the CT.gov acronym). The links are WRITTEN by the k-gap lane's builder (acq/k-gap 125802eb5, scripts/g1_identity_links.py
there, which needs that lane's open-source routes); this module only READS them. The tracker joins a comparator unit
through a link ONLY to a registration already in our pool (join(), the same shape as SCREENED_VIA_OTHER_REPORT); it never
adds a trial to a pool.
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS = os.path.join(ROOT, "registry", "identity_links.json")


RULES = ("ONE_NCT_STATED_IN_OWN_REPORT", "TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM")


def load(path=None):
    """The committed links. A MISSING file is an error, never 'no links' (codex idlink-r1 #2): the file is committed, so
    its absence is a broken checkout, and reading it as empty would silently un-match every linked trial."""
    p = path or LINKS
    if not os.path.exists(p):
        raise FileNotFoundError(f"identity links not found: {os.path.relpath(p, ROOT)} (committed file missing)")
    return json.load(open(p, encoding="utf-8"))


def supported(lk):
    """True only when the link carries BOTH typed facts, each with its span, and they agree with the link's NCT: the
    report's own span states that NCT, and the acronym span sits in the recorded title (codex idlink-r1 #1)."""
    if not isinstance(lk, dict) or not str(lk.get("nct") or "").startswith("NCT"):
        return False
    rules = {r.get("rule"): r for r in (lk.get("rules") or []) if isinstance(r, dict)}
    if set(rules) != set(RULES) or len(lk.get("rules") or []) != 2:
        return False
    one, acro = rules[RULES[0]], rules[RULES[1]]
    return (isinstance(one.get("span"), str) and lk["nct"] in one["span"] and len(str(one.get("text_sha256") or "")) == 64
            and isinstance(acro.get("span"), str) and acro["span"].strip() != ""
            and acro["span"] in str(acro.get("title") or ""))


def join(trials, comp_rows, rp, nct_pool, pooled_ids, matched_ids, routes, links=None):
    """Join each comparator unit we do not pool, whose report PMID has an identity LINK to a registration already in our
    pool (and not already matched), to that pool row. Returns [(x, pool_row_id, link)] for the caller to value. Never
    adds a trial to a pool: a link to a registration we do not pool does nothing."""
    links = load() if links is None else links
    out = []
    for x, t in zip(trials, comp_rows):
        p = rp.get(id(t))
        lk = links.get(str(p)) if p else None
        if x.get("in_our_pool") or not lk or not supported(lk):
            continue
        via = nct_pool.get(lk["nct"])
        if not via or via not in pooled_ids or via in matched_ids:
            continue
        matched_ids.add(via)
        routes[x["route"]] = routes.get(x["route"], 0) - 1
        routes["PRIMARY"] = routes.get("PRIMARY", 0) + 1
        x.update(in_our_pool=True, route="PRIMARY", family=via, g1_countable=True, our_refusal=None,
                 basis=f"same registered trial {lk['nct']}: pooled as {via}; the comparator cites PMID {p}, joined by "
                       f"identity link ({' + '.join(r['rule'] for r in lk['rules'])}; registry/identity_links.json)",
                 matched_via_identity_link={"nct": lk["nct"], "pool_row": via, "comparator_cites": p,
                                            "rules": lk["rules"]})
        out.append((x, via, lk))
    return out
