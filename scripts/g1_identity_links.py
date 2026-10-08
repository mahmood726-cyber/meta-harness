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


def nct_ids_in(text):
    """Every distinct 'NCT' + exactly 8 digits in the text, bounded by non-alphanumerics. Plain scan, no regex."""
    out, up, i = set(), (text or "").upper(), 0
    while True:
        i = up.find("NCT", i)
        if i < 0:
            return out
        j = i + 3
        while j < len(up) and up[j].isdigit():
            j += 1
        if j - i == 11 and (i == 0 or not up[i - 1].isalnum()) and (j == len(up) or not up[j].isalnum()):
            out.add(up[i:j])
        i += 3


def _fold(s):
    return "".join(ch for ch in str(s or "").upper() if ch.isalnum())


def registry_acronym_from_aact(nct, snap):
    """The registered acronym of `nct` from an AACT snapshot's studies.txt (typed read, no model): (acronym, source)."""
    import csv
    csv.field_size_limit(10 ** 9)
    p = os.path.join(snap, "studies.txt")
    with open(p, encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f, delimiter="|")
        if not {"nct_id", "acronym"} <= set(rd.fieldnames or []):
            # a broken snapshot is not 'no registered acronym' (codex idlink-r3 #2)
            raise ValueError(f"{p}: studies.txt lacks nct_id/acronym columns ({(rd.fieldnames or [])[:8]})")
        for row in rd:
            if row.get("nct_id") == nct:
                return (row.get("acronym") or "").strip() or None, f"AACT {os.path.basename(snap)} studies.txt {nct} acronym"
    return None, f"AACT {os.path.basename(snap)} studies.txt: {nct} not found"


def supported(lk):
    """True only when the link carries BOTH typed facts, each with its span, and they agree with the link's NCT
    (codex idlink-r1 #1, r2 #1 #2):
      ONE_NCT_STATED_IN_OWN_REPORT -- the report span names exactly ONE registration, and it is the link's NCT (a span
        naming another trial's NCT, or two, never supports it); the whole-text check is the builder's, pinned by text_sha256
      TITLE_ACRONYM_EQUALS_REGISTRY_ACRONYM -- the acronym span sits in the recorded PubMed title AND equals (folded) the
        REGISTRY's acronym for that NCT, recorded with its source (registry_acronym / registry_acronym_source)."""
    if not isinstance(lk, dict) or not str(lk.get("nct") or "").startswith("NCT"):
        return False
    rules = {r.get("rule"): r for r in (lk.get("rules") or []) if isinstance(r, dict)}
    if set(rules) != set(RULES) or len(lk.get("rules") or []) != 2:
        return False
    one, acro = rules[RULES[0]], rules[RULES[1]]
    if not (isinstance(one.get("span"), str) and nct_ids_in(one["span"]) == {lk["nct"].upper()}
            and len(str(one.get("text_sha256") or "")) == 64):
        return False
    span = acro.get("span")
    return (isinstance(span, str) and _fold(span) != "" and span in str(acro.get("title") or "")
            and _fold(span) == _fold(acro.get("registry_acronym")) and bool(acro.get("registry_acronym_source"))
            and title_names_own_study(acro.get("title"), span))


def title_names_own_study(title, acro):
    """The title presents the acronym as ITS OWN study, not as a trial it compares with or cites (codex idlink-r3 #1):
    'the <ACRO> study/trial' anywhere ('Results From the PARALLEL-HF Study'), or the title opens '<ACRO>:'. A title that
    names it after 'versus' / 'compared with' / 'than' / 'like' / 'unlike' / 'vs' is never its own study. Plain scan."""
    t = " ".join(str(title or "").split())
    low, a = t.lower(), str(acro or "").lower()
    if not a:
        return False
    if low.startswith(a + ":"):
        return True
    i = low.find(a)
    while i >= 0:
        before = low[:i].rstrip()
        after = low[i + len(a):].lstrip(" ")
        if before.endswith(" the") and (after.startswith("study") or after.startswith("trial")):
            # 'versus the X trial': the word before 'the' marks a comparison -> not its own study
            if not any(before[:-4].rstrip().endswith(w) for w in (" versus", " vs", " vs.", " compared with",
                                                                   " compared to", " than", " like", " unlike")):
                return True
        i = low.find(a, i + 1)
    return False


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
