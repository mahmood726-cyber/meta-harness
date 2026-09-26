"""Plants for regex sites whose pattern is BUILT at run time (kind 'built:*' in regex_layer.inventory).

A built pattern has no fixed text to test, so its plant calls the FUNCTION that builds and uses it, with chosen
arguments, and asserts the function's result. Each site: {"call": "harness.<module>.<function>", "what": ...,
"plants": {"accept": [(args, expected)], "refuse": [(args, expected)]}, "defects": {<plant id>: <reason>}}.
'accept' plants are inputs the site must find; 'refuse' plants are inputs it must not (typically the same shape made
wrong, e.g. a regex metacharacter that must be taken literally, or a number fragment). A plant listed in "defects" is a
located defect: it runs as a strict xfail, so fixing the defect flips it to a pass and its entry must be removed.
Held by tests/test_built_plants.py.
"""
from __future__ import annotations

BUILT_SPECS: dict[str, dict] = {
    # ---- owned files (harness/extract.py, harness/compat_check.py): strict
    "extract.py:finditer:built:44d6d17811": {
        "call": "harness.extract._kw_only_in_null_result",
        "what": "every occurrence of an outcome keyword (taken literally, re.escape) sits in a null-result clause",
        "plants": {
            "accept": [(("Discontinuation rates were similar in both groups.", ["discontinuation"]), True),
                       (("C-reactive protein (CRP) levels were similar between groups.", ["c-reactive protein (crp)"]),
                        True)],
            "refuse": [(("Discontinuation occurred in 12 patients.", ["discontinuation"]), False),
                       # '.' in the keyword is literal: 's.roke' must not find 'stroke'
                       (("Stroke rates were similar.", ["s.roke"]), False)]}},
    "extract.py:search:built:68d753f055": {
        "call": "harness.extract._arm_ns",
        "what": "per-arm randomised n from the arm term (taken literally) and one of the arm-size phrasings",
        "plants": {
            "accept": [(("We randomised 1200 adults: colchicine (n=600) and placebo (n=598).", ["colchicine"],
                         ["placebo"]), {"i": 600, "c": 598}),
                       (("Of these, 264 received high-flow oxygen and 263 conventional oxygen therapy.", ["high-flow"],
                         ["conventional oxygen"]), {"i": 264, "c": 263})],
            "refuse": [(("colchicine (n=600) vs placebo", ["c.lchicine"], ["placebo"]), {})]}},
    "compat_check.py:search:built:1fd38d5cbd": {
        "call": "harness.compat_check._search",
        "what": "search a criterion pattern case-insensitively and across line breaks (re.I | re.S)",
        "plants": {
            "accept": [(("follow-up.*weeks", "Follow-up\nfor 12 WEEKS"), "MATCH")],
            "refuse": [(("weeks", "follow-up for 12 months"), None)]}},
}
from regex_layer.specs_built_other import BUILT_SPECS_OTHER as _OTHER; BUILT_SPECS.update(_OTHER)
