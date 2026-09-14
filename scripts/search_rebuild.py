"""Concept-query search rebuild (unaided-recall measurement).

The committed spec: build the query from the REGISTERED P/I/C/design and NOTHING else; expand a drug
CLASS to its members (a query on 'GLP-1 receptor agonist' misses a trial titled 'semaglutide'); use
PAGINATION over a structured boolean query, NEVER a top-N relevance cut; and measure UNAIDED recall
(does the query retrieve the trial's PMID without being told it?) against docs/search_test_set.json,
scored ONLY over SOURCE_VERIFIED_ELIGIBLE. The current per-topic pubmed_queries are enumerated
`<uid>[uid]` lists — a hardcoded PMID set that cannot discover anything new; baseline recall is 0/6.

This measures recall; it does NOT yet rewrite the pipeline's fetch (that corpus-moving integration is
the delicate step, done behind a full 32-topic before/after). Uses PubMed esearch (boolean, paginated).
"""
import json, os, sys, io, time, urllib.request, urllib.parse

if __name__ == "__main__":  # guard: reassigning stdout at import closes a caller's wrapper (re-wrap trap)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import lexicon  # noqa: E402

# Drug CLASS -> members, for the class-term expansion (SONIA mechanism: search the molecules, not only
# the class label). Curated for the corpus's classes; a class label in the topic's intervention_terms
# triggers expansion to every member so a member-named trial is retrievable.
CLASS_MEMBERS = {
    "dpp-4 inhibitor": ["sitagliptin", "saxagliptin", "alogliptin", "linagliptin", "vildagliptin",
                        "omarigliptin", "trelagliptin", "gemigliptin", "teneligliptin", "anagliptin"],
    "glp-1 receptor agonist": ["semaglutide", "dulaglutide", "liraglutide", "exenatide", "lixisenatide",
                               "albiglutide", "efpeglenatide"],
    "sglt2 inhibitor": ["empagliflozin", "dapagliflozin", "canagliflozin", "ertugliflozin", "sotagliflozin"],
    "mineralocorticoid receptor antagonist": ["spironolactone", "eplerenone", "finerenone", "canrenone"],
}
_CLASS_TRIGGERS = {  # substrings in an intervention term that mean "this is the class label"
    "dpp-4": "dpp-4 inhibitor", "dpp4": "dpp-4 inhibitor",
    "glp-1": "glp-1 receptor agonist", "glp1": "glp-1 receptor agonist",
    "sglt2": "sglt2 inhibitor", "sglt-2": "sglt2 inhibitor",
    "mineralocorticoid": "mineralocorticoid receptor antagonist", "aldosterone": "mineralocorticoid receptor antagonist",
    "mra": "mineralocorticoid receptor antagonist",
}


def expand_intervention(terms):
    """Registered intervention terms + class-member expansion + abbreviation variants (recall net)."""
    out = set()
    for t in terms or []:
        tl = lexicon.fold(t)
        out.add(tl)
        for trig, cls in _CLASS_TRIGGERS.items():
            if trig in tl:
                out.update(CLASS_MEMBERS.get(cls, []))
        for variant, _ in lexicon.abbrev_variants(tl):
            out.add(variant)
    # drop pure class labels/abbreviations that add noise once members are in (keep the words though)
    return sorted(out)


def _or(terms):
    return " OR ".join(f'"{t}"[tiab]' if " " in t else f"{t}[tiab]" for t in terms if t)


def build_query(cfg):
    """Concept query from registered P/I/C/design. Population OR'd, intervention (class-expanded) OR'd,
    RCT design filter. Comparator is NOT ANDed in (many eligible trials name only the intervention +
    'placebo'); design + intervention + population is the recall-safe concept."""
    inc = cfg.get("include", {})
    interv = expand_intervention(cfg.get("intervention_terms"))
    pop = [lexicon.fold(p) for p in (inc.get("population_any") or [])]
    design = 'randomized controlled trial[pt] OR randomized[tiab] OR randomised[tiab] OR "controlled trial"[tiab]'
    parts = []
    if interv:
        parts.append("(" + _or(interv) + ")")
    if pop:
        parts.append("(" + _or(pop) + ")")
    parts.append("(" + design + ")")
    return " AND ".join(parts)


def esearch_all(query, cap=4000):
    """Return the FULL boolean result set (paginated), never a top-N relevance cut. Resilient: on a
    429/transient error, back off and retry a few times; if it still fails, return what we have so far
    with total=-1 (a sentinel meaning 'incomplete') rather than crashing the caller."""
    ids, retstart, step, total = [], 0, 500, -1
    while retstart < cap:
        params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmode": "json",
                                         "retstart": retstart, "retmax": step})
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + params
        req = urllib.request.Request(url, headers={"User-Agent": "meta-harness/1.0 (research; mahmood726@gmail.com)"})
        j = None
        for attempt in range(4):
            try:
                j = json.load(urllib.request.urlopen(req, timeout=45))
                break
            except Exception as e:
                print(f"  esearch error (attempt {attempt+1}): {e}")
                time.sleep(2.0 * (attempt + 1))  # backoff for 429/transient
        if j is None:
            break
        batch = j.get("esearchresult", {}).get("idlist", [])
        total = int(j.get("esearchresult", {}).get("count", 0))
        ids.extend(batch)
        if not batch or retstart + step >= total:
            break
        retstart += step
        time.sleep(0.5)
    return ids, total


TARGETS = {  # the 6 SOURCE_VERIFIED_ELIGIBLE trials -> (topic, target PMID)
    "PHILO": ("ticagrelor-vs-clopidogrel-acs", "26376600"),
    "J-EMPHASIS-HF": ("spironolactone-hfref-mortality", "28824029"),
    "CLEAR SYNERGY (OASIS-9)": ("colchicine-secondary-cv-prevention", "39555823"),
    "TECOS": ("dpp4-mace-t2d", "26052984"),
    "omarigliptin CV trial": ("dpp4-mace-t2d", "28893244"),
    "SOUL": ("glp1-ra-mace-t2d", "40162642"),
}

if __name__ == "__main__":
    recalled = 0
    for trial, (slug, pmid) in TARGETS.items():
        cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        q = build_query(cfg)
        ids, total = esearch_all(q)
        hit = pmid in ids
        recalled += hit
        print(f"{'RECALL' if hit else 'MISS  '}  {trial:26s} PMID {pmid} in {total} hits ({len(ids)} fetched)  [{slug}]")
        time.sleep(0.34)
    print(f"\nUNAIDED CONCEPT-QUERY RECALL: {recalled} of {len(TARGETS)} (baseline was 0 of 6)")
