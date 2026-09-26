"""Plants for the built-pattern regex sites outside extract.py / compat_check.py (kind 'built:*' in
regex_layer.inventory). Same contract as regex_layer/specs_built.py, which merges this dict into BUILT_SPECS.

Every expected value below was recorded by running the named harness function on the plant's arguments; a plant listed
in a site's "defects" is a located defect and runs as a strict xfail (expected = the correct result, which the code
does not yet return).

Sites left OUT (see the lane report): comparator_panel.py validate (its refusal is a raised ValueError, which a
result == expected plant cannot express, and it needs a hash-pinned held document file); trial_family.py prepare
(:406, :421) (reached only through prepare(), which reads cache/<slug>/family_registry.json and family_discovery.json
from a repository root, so it cannot be called without on-disk fixtures).
"""
from __future__ import annotations

_D12 = ("PVA-D12: _present refuses a following digit but not '.' or ',' -- a fragment of a longer number is found "
        "(pva: 0 of 132 served hand-bound values depend on it)")

_ARMS = [{"arm_id": "A", "linkage_complete": True, "active_interventions": ["metformin", "semaglutide"], "span": "s1"},
         {"arm_id": "B", "linkage_complete": True, "active_interventions": ["metformin"], "span": "s2"}]

BUILT_SPECS_OTHER: dict[str, dict] = {
    "comparator_second_pass.py:search:built:3092d6467d": {
        "call": "harness.comparator_second_pass._contains",
        "what": "a comparator term (taken literally, re.escape) appears in the text, case-insensitively",
        "plants": {
            "accept": [(("C-reactive protein (CRP) was lower", "protein (crp)"), True)],
            "refuse": [(("C-reactive protein CRP was lower", "protein (crp)"), False),
                       # '.' in the term is literal: 's.roke' must not find 'Stroke'
                       (("Stroke rates were similar", "s.roke"), False)]}},
    "comparator_second_pass.py:search:built:3092d6467d#2": {
        "call": "harness.comparator_second_pass._snippet",
        "what": "the compacted text around the first literal occurrence of a term, or '' when absent",
        "plants": {
            "accept": [(("Results: CRP (mg/L) fell by 30%.", "crp (mg/l)"), "Results: CRP (mg/L) fell by 30%.")],
            "refuse": [(("Results: CRP mg/L fell by 30%.", "crp (mg/l)"), ""),
                       (("Stroke rates were similar", "s.roke"), "")]}},
    "comparator_truth.py:search:built:68d753f055": {
        "call": "harness.comparator_truth.span_or_not_held",
        "what": "locate a rendered numeric comparator value (thousands-grouped int / float with trailing zeros) in text",
        "plants": {
            "accept": [(("A total of 10,033 patients were randomised.", 10033),
                        {"value": 10033, "status": "FOUND", "span": "A total of 10,033 patients were randomised.",
                         "start": 11, "end": 17}),
                       (("The HR was 0.80 overall.", 0.8),
                        {"value": 0.8, "status": "FOUND", "span": "The HR was 0.80 overall.", "start": 11, "end": 15})],
            "refuse": [(("The HR was 0.85 overall.", 0.8),
                        {"value": 0.8, "status": "NOT_IN_HELD_TEXT", "span": None, "start": None, "end": None}),
                       (("A total of 110033 patients.", 10033),
                        {"value": 10033, "status": "NOT_IN_HELD_TEXT", "span": None, "start": None, "end": None}),
                       (("The HR was 1.03 overall.", 1),
                        {"value": 1, "status": "NOT_IN_HELD_TEXT", "span": None, "start": None, "end": None})]},
        "defects": {"refuse-2": "span_or_not_held: the integer pattern refuses an adjacent digit but not a following "
                                "'.', so the count 1 is FOUND inside '1.03' (a fragment of a longer number)"}},
    "hand_binding.py:search:built:b859a4d155": {
        "call": "harness.hand_binding._present",
        "what": "any number form is present in text as a whole number (not preceded by digit/'.', not followed by digit)",
        "plants": {
            "accept": [(("HR 1.03 (95% CI 0.9-1.2)", {"1.03"}), True)],
            "refuse": [(("HR 1.035", {"1.03"}), False),
                       (("HR 11.03", {"1.03"}), False),
                       # '.' in the form is literal
                       (("HR 1x03", {"1.03"}), False),
                       (("HR 1.03", {"1"}), False),
                       (("10,033 patients", {"10"}), False)]},
        "defects": {"refuse-3": _D12, "refuse-4": _D12}},
    "hand_binding.py:search:built:0b98b8dede": {
        "call": "harness.hand_binding._effect_pattern_ok",
        "what": "effect point precedes its CI bounds in one clause, each located as a whole number",
        "plants": {
            "accept": [(("HR 0.80 (95% CI 0.70-0.90)", {"effect": 0.8, "ci_low": 0.7, "ci_high": 0.9}), True)],
            "refuse": [(("95% CI 0.70-0.90, HR 0.80", {"effect": 0.8, "ci_low": 0.7, "ci_high": 0.9}), False),
                       (("HR 1.03 (95% CI 0.5-2)", {"effect": 1, "ci_low": 0.5, "ci_high": 2}), False)]},
        "defects": {"refuse-1": "PVA-D12 (same class): _effect_pattern_ok refuses a following digit but not '.', so "
                                "effect 1 is located inside '1.03' -- a fragment of a longer number is found"}},
    "hand_binding.py:search:built:50e721e49c": {
        "call": "harness.hand_binding._scale_ok",
        "what": "the declared effect scale is named in the located span (\\b-anchored abbreviations case-sensitive)",
        "plants": {
            "accept": [(("HR", {"text": "hazard ratio 0.80 (0.70-0.90)"}), None),
                       (("HR", {"text": "HR 0.80"}), None)],
            # word boundary: 'HRQOL' does not state HR
            "refuse": [(("HR", {"text": "HRQOL improved 0.80"}), "scale 'HR' is not stated in the located span")]}},
    "hand_binding.py:search:built:50e721e49c#2": {
        "call": "harness.hand_binding._scale_ok",
        "what": "on a scale mismatch, list the scales the span does state",
        "plants": {
            "accept": [(("RR", {"text": "OR 0.80 and HR 0.9"}),
                        "scale 'RR' is not stated in the located span (the span states HR, OR)")],
            "refuse": [(("RR", {"text": "the HRs were 0.80"}), "scale 'RR' is not stated in the located span"),
                       # \bOR\b is case-sensitive: lower-case 'or' is the conjunction, not a stated scale
                       (("RR", {"text": "or 0.80"}), "scale 'RR' is not stated in the located span")]}},
    "hand_binding.py:search:built:382fc65ba1": {
        "call": "harness.hand_binding._ci_pct_ok",
        "what": "the declared CI level appears as '<level>%' not preceded by a digit or '.'",
        "plants": {
            "accept": [((95, {"text": "HR 0.80 (95% CI 0.70-0.90)"}), None),
                       ((95, {"text": "HR 0.80", "column_header": "95 % CI"}), None)],
            "refuse": [((5, {"text": "HR 0.80 (95% CI 0.70-0.90)"}),
                        "declared CI level 5% is not stated in the located span"),
                       ((5, {"text": "HR 0.80 (99.5% CI 0.70-0.90)"}),
                        "declared CI level 5% is not stated in the located span"),
                       ((95, {"text": "HR 0.80 (95 CI 0.70-0.90)"}),
                        "declared CI level 95% is not stated in the located span")]}},
    "lexicon.py:finditer:built:3cfae50550": {
        "call": "harness.lexicon.matches_only_as_subtype",
        "what": "every whole-word occurrence of a bare head term is a qualified subtype",
        "plants": {
            "accept": [(("mortality", "cardiovascular mortality was lower"), True),
                       # 'strokes' is not a whole-word occurrence of 'stroke'
                       (("stroke", "ischemic stroke and strokes overall"), True)],
            "refuse": [(("mortality", "all-cause mortality was lower"), False),
                       (("stroke", "ischemic stroke and stroke overall"), False)]}},
    "second_source.py:search:built:68d753f055": {
        "call": "harness.second_source._canon_component_text",
        "what": "canonical endpoint components named in a text",
        "plants": {
            "accept": [(("Cardiovascular death or MI",), {"cardiovascular death", "myocardial infarction"})],
            # word boundary: the 'mi' inside 'admission' is not MI
            "refuse": [(("hospital admission",), set())]}},
    "trial_family.py:search:built:1fd38d5cbd": {
        "call": "harness.trial_family.report_role",
        "what": "a report's role from the first ROLES pattern its title matches",
        "plants": {
            "accept": [(({"title": "A randomized controlled trial of semaglutide"},),
                        ("PRIMARY", {"source": "record.title", "quote": "A randomized controlled trial of semaglutide",
                                     "match": "randomized controlled trial"})),
                       (({"title": "Open-label extension of the SUSTAIN trial"},),
                        ("EXTENSION", {"source": "record.title", "quote": "Open-label extension of the SUSTAIN trial",
                                       "match": "extension"}))],
            # word boundary: '\bextension\b' must not fire on 'Extensional'
            "refuse": [(({"title": "Extensional viscosity in a laboratory study"},),
                        ("ROLE_UNRESOLVED", {"absence_code": "NO_TYPED_ROLE_EVIDENCE"}))]}},
    "trial_family.py:search:built:e794c3afa8": {
        "call": "harness.trial_family.randomised_contrasts",
        "what": "an agent (taken literally, whole word) differs between two completely linked arms",
        "plants": {
            "accept": [((_ARMS, ["semaglutide"], True),
                        [{"arm_ids": ["A", "B"], "drug": "semaglutide", "background_therapy": ["metformin"],
                          "span": ["s1", "s2"]}])],
            "refuse": [((_ARMS, ["sema"], True), []),
                       ((_ARMS, ["s.maglutide"], True), [])]}},
    "verify.py:sub:built:b4e83caafd": {
        "call": "harness.verify._digits_in",
        "what": "spelled small integers (whole words) are normalised to digits before each value is looked up",
        "plants": {
            "accept": [(("Eighteen of 245 patients", 18, 245), True),
                       (("10,033 patients", 10033), True)],
            "refuse": [(("Eighteenth of 245 patients", 18, 245), False),
                       (("fourteen patients", 4), False),
                       (("10,033 patients", 10), False),
                       (("HR 1.03", 1), False)]},
        "defects": {"refuse-3": "PVA-D12 (same class): _digits_in refuses an adjacent digit but not a following '.', so "
                                "the count 1 is found inside '1.03' -- a fragment of a longer number is found"}},
}
