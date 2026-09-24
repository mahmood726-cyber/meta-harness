"""Plants for the regex sites of harness/eligibility_chain.py and harness/compat_check.py (keys as regex_layer.inventory
names them).

protocol_criteria() reads the design / comparator sites on _fold(md_text) (lowercase, whitespace collapsed), and the
**Population** / **Timepoint** sites on the raw protocol markdown (re.I). compat_check's adult site reads a lowercased
comparator text; _summarize_follow reads derived follow-up value strings ('56 days', 'during treatment plus 30 days').
"""

SITE_SPECS: dict = {
    # ---- harness/eligibility_chain.py ----------------------------------------------------------------------------
    "eligibility_chain.py:_PMID_RE": {
        "kind": "search",
        "what": "_pid: the PMID digits of a trial id / label ('PMID 29146535' or a bare 7-9 digit id)",
        "plants": {"accept": [("PMID 29146535", ("29146535",)), ("29146535", ("29146535",)),
                              ("SUSTAIN-6 (PMID 27633186)", ("27633186",))],
                   "refuse": ["NCT01720446", "n=123456"]}},
    "eligibility_chain.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_norm: collapse whitespace runs before protocol wording is matched",
        "plants": {"accept": [("double-blind\n  placebo-controlled", None), ("usual\tcare", None)],
                   "refuse": ["double-blind", "placebo-controlled"]}},
    "eligibility_chain.py:search:0278e60920": {
        "kind": "search",
        "what": "protocol_criteria: the protocol admits trials that are double-blind OR placebo-controlled",
        "plants": {"accept": [("include trials that are double-blind or placebo-controlled", None),
                              ("double blind or placebo controlled", None)],
                   "refuse": ["double-blind, placebo-controlled trials", "double-blind and placebo-controlled"]}},
    "eligibility_chain.py:search:e9857d1c69": {
        "kind": "search",
        "what": "protocol_criteria: the protocol requires double-blind AND placebo-controlled (comma / juxtaposed form)",
        "plants": {"accept": [("randomised, double-blind, placebo-controlled trials", None),
                              ("double-blind placebo-controlled", None)],
                   "refuse": ["double-blind or placebo-controlled", "open-label, placebo-controlled"]}},
    "eligibility_chain.py:search:4744a336ec": {
        "kind": "search",
        "what": "protocol_criteria: the protocol requires double-blind AND placebo-controlled ('and' form)",
        "plants": {"accept": [("trials must be double-blind and placebo-controlled", None),
                              ("double blind and placebo controlled", None)],
                   "refuse": ["double-blind or placebo-controlled", "double-blind and open-label"]}},
    "eligibility_chain.py:search:3a8e5df5f4": {
        "kind": "search",
        "what": "protocol_criteria: the value of the protocol's **Population** line (read for the analysis set)",
        "plants": {"accept": [("- **Population** - intention-to-treat as randomised.", ("intention-to-treat as randomised",)),
                              ("**Population**: per-protocol set\n", ("per-protocol set",)),
                              ("- **Population:** adults, intention-to-treat.", None),
                              ("- **Population** — intention-to-treat as randomised.", None)],
                   "refuse": ["Population: adults with heart failure", "**Timepoint** - 28 days."]}},
    "eligibility_chain.py:search:47eac977e0": {
        "kind": "search",
        "what": "protocol_criteria: the value of the protocol's **Timepoint** line (the follow-up window)",
        "plants": {"accept": [("- **Timepoint** - 28 days.", ("28 days",)),
                              ("**Timepoint**: 1 year for the primary outcome\n", ("1 year for the primary outcome",)),
                              ("- **Timepoint** — longest recurrence follow-up each trial reports.", None)],
                   "refuse": ["Timepoint: 28 days", "**Population** - adults."]}},
    "eligibility_chain.py:search:36706f6be6": {
        "kind": "search", "what": "protocol_criteria: the protocol states a comparator (placebo / usual care / control)",
        "plants": {"accept": [("colchicine versus placebo", None), ("compared with usual care", None),
                              ("colchicine vs no colchicine", None), ("the control arm", None)],
                   "refuse": ["randomised controlled trials of colchicine", "uncontrolled cohort studies"]}},
    # ---- harness/compat_check.py ---------------------------------------------------------------------------------
    "compat_check.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_norm_ws: collapse whitespace runs in a span",
        "plants": {"accept": [("hazard  ratio\n0.8", None), ("a\tb", None)],
                   "refuse": ["hazard-ratio", "0.8"]}},
    "compat_check.py:findall:6ce8847b51": {
        "kind": "search", "what": "_summarize_follow: the day counts in per-trial follow-up values (for a min-max d range)",
        "plants": {"accept": [("56 days", ("56",)), ("during treatment plus 30 days", ("30",)), ("1 day", ("1",))],
                   "refuse": ["within 8 weeks", "1.5 years"]}},
    "compat_check.py:search:854c55479d": {
        "kind": "search", "what": "comparator scope: the comparator review is ADULT-ONLY (vs a pool with paediatric trials)",
        "plants": {"accept": [("probiotics for antibiotic-associated diarrhoea in adults", None),
                              ("an adult population", None), ("adult inpatients", None)],
                   "refuse": ["probiotics for antibiotic-associated diarrhoea in children", "into adulthood",
                              "corticosteroids for treating sepsis in children and adults"]}},
}
