"""Plants for harness/analysis_set.py (lane G1, colchicine-postop-af). Texts are written as the module reads them
(whitespace-collapsed held abstracts; patterns are re.I where compiled so)."""

SITE_SPECS: dict = {
    "analysis_set.py:_ARM_N": {
        "kind": "search", "what": "an arm's randomised size stated as 'arm (...; n=N)'",
        "plants": {"accept": [("randomized to receive placebo (n=180) or colchicine", None),
                              ("colchicine (0.5 mg twice daily in patients >=70 kg or 0.5 mg once daily; n=180)", None)],
                   "refuse": ["placebo (180 patients)", "n = 180 in total"]}},
    "analysis_set.py:_COUNT": {
        "kind": "search", "what": "one arm's events (and n) inside a count group: 'arm, E patients' / 'arm, E/N patients'",
        "plants": {"accept": [("colchicine, 61 patients [33.9%]", None), ("; placebo, 61/148 patients [41.2%]", None)],
                   "refuse": ["occurred in 35 patients assigned to colchicine", "colchicine 61 patients"]}},
    "analysis_set.py:_SET": {
        "kind": "search", "what": "the analysis set named in the clause before a count group",
        "plants": {"accept": [("in the prespecified on-treatment analysis", None), ("the per-protocol population", None),
                              ("modified intention-to-treat", None), ("ITT", None)],
                   "refuse": ["the treatment arm", "protocol amendment"]}},
    "analysis_set.py:_PAREN": {
        "kind": "search", "what": "a parenthetical group without nested parentheses",
        "plants": {"accept": [("postoperative AF (colchicine, 61 patients [33.9%]; placebo, 75 patients)", None)],
                   "refuse": ["no parentheses here", "unclosed (group"]}},
    "analysis_set.py:_SENT": {
        "kind": "search", "what": "a sentence boundary",
        "plants": {"accept": [("trial. Patients were randomized", None)], "refuse": ["n=180", "0.5 mg"]}},
    "analysis_set.py:_WS": {
        "kind": "search", "what": "a whitespace run",
        "plants": {"accept": [("on-treatment  analysis", None), ("AF\n(colchicine", None)], "refuse": ["AF", "61/148"]}},
    "analysis_set.py:_N_TO_GROUP": {
        "kind": "search", "what": "an arm size stated as 'N to the X group'",
        "plants": {"accept": [("140 patients were randomized, 69 to the control group and 71 to the colchicine group", None)],
                   "refuse": ["the control group had 69 patients", "69 in the control group"]}},
    "analysis_set.py:_PCT_PAIR": {
        "kind": "search", "what": "a percentage pair for two arms ('7.04% versus 13.04%')",
        "plants": {"accept": [("(7.04% versus 13.04%, respectively", None), ("12.0% vs 22.0%", None)],
                   "refuse": ["7.04% of patients", "p = 0.271"]}},
}
