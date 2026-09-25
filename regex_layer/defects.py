"""Located regex defects: plant id -> why the CURRENT pattern fails it. Each runs as a strict xfail in
tests/test_regex_plants.py, so a fix flips it to a pass (and must remove the entry) and a regression cannot hide."""

# plant id -> why the current pattern fails it (a located defect, not a wish)
KNOWN_DEFECTS: dict[str, str] = {
    "target_endpoint.py:search:714a13cd06-refuse-2":
        "RX-TE1 (found 2026-09-24 by this plant): 'death.{0,30}cardiovascular' spans a conjunction, so the all-cause "
        "death + CV-hospitalization composite ('death from any cause or cardiovascular hospitalization') is read as "
        "naming cardiovascular death. Reachable phrasing: present verbatim in held cache/spironolactone-hfref-mortality "
        "records; effect on a served row not measured. Fix is in pinned code (harness/target_endpoint.py).",
    "target_endpoint.py:search:aa4a355e65-refuse-2":
        "RX-TE2 (found 2026-09-24 by this plant): '\\bvascular death' fires after the hyphen in 'non-vascular death', so "
        "non-vascular death is read as cardiovascular death (the same defect the non-cardiovascular mask fixed for "
        "'non-cardiovascular'). Reachable phrasing: present in held cache/omega3-cardiovascular-events (ft_30415637) and "
        "pcsk9-mace records; effect on a served row not measured. Fix is in pinned code (harness/target_endpoint.py).",
    "target_endpoint.py:search:4a4f5b989a-refuse-2":
        "RX-TE3 (found 2026-09-24 by this plant): '\\bfatal\\b' fires inside 'non-fatal' and '.{0,25}' then reaches a later "
        "'hf', so 'non-fatal stroke or hf hospitalization' adds a heart-failure DEATH component. Latent for this exact "
        "phrasing (held dpp4-mace records carry only the ambiguous 'fatal/non-fatal MI or HF'); not measured. Fix is in "
        "pinned code (harness/target_endpoint.py).",
    "eligibility_chain.py:search:3a8e5df5f4-accept-2":
        "RX-EC1 (found 2026-09-24 by this plant): the **Population** site requires the separator AFTER the closing '**', "
        "so the '**Population:**' style (colon inside the bold) is never read. Reachable in held text: "
        "protocols/denosumab-vertebral-fracture.md and esketamine-trd-madrs.md use it; no criterion is lost today "
        "because neither line carries analysis-set wording. Fix is in pinned code (harness/eligibility_chain.py).",
    "eligibility_chain.py:search:3a8e5df5f4-accept-3":
        "RX-EC2 (found 2026-09-24 by this plant): the separator class [-:] excludes the em dash, so '**Population** — "
        "...' is not read. Reachable: protocols/colchicine-recurrent-pericarditis.md; masked today because the "
        "'intention-to-treat' prose fallback yields the same analysis_set. Fix is in pinned code (harness/eligibility_chain.py).",
    "eligibility_chain.py:search:47eac977e0-accept-2":
        "RX-EC2 (found 2026-09-24 by this plant): same em-dash separator miss on the **Timepoint** line. Reachable and "
        "consequential: protocol_criteria() on protocols/colchicine-recurrent-pericarditis.md returns NO "
        "follow_up_window criterion although the protocol states one (measured 2026-09-24). Fix is in pinned code "
        "(harness/eligibility_chain.py).",
    "compat_check.py:search:854c55479d-refuse-2":
        "RX-EC3 (found 2026-09-24 by this plant): the site's result is used as 'adult-only comparator', but it fires on "
        "any mention of adults, so a comparator covering 'children and adults' is declared adult-only and a pool with "
        "paediatric trials is marked scope-invalid. The phrasing ('...sepsis in children and adults') is in held "
        "cache/comparators/32876694 bytes; whether it reaches comp_text for a pool with paediatric trials is not measured. "
        "Fix is in pinned code (harness/compat_check.py).",
}

# ---- other-lane files (harness/rob2.py, funding.py, hand_binding.py): planted and measured by the regex layer, READ
# only. "Reachable" = the phrasing is in the held text that site reads (rob2: the D5 inputs recorded in
# cache/*/rob2.json; funding: held title+abstract / full text; hand_binding: held PMC full text / abstract prose).
_OL = " The fix belongs to the owning lane (not the regex layer), filed 2026-09-24."
KNOWN_DEFECTS.update({
    "rob2.py:search:b4e124d7bc-accept-3":
        "RX-OL1 (found 2026-09-24 by this plant): 'montgomery[- ]?a?sberg' needs an ASCII 'a' and a hyphen/space, so the "
        "scale's own spelling 'Montgomery–Åsberg' (en dash, Å) is not read as MADRS unless the text also says 'MADRS'. "
        "Latent: all 11 held D5 texts naming the scale spell it 'Asberg' and carry '(MADRS)'." + _OL,
    "rob2.py:search:74ee9684cf-accept-2":
        "RX-OL2 (found 2026-09-24 by this plant): only the word 'recurrent' marks a recurrence, so 'VTE recurrence' / "
        "'recurrence of VTE' never yields RECURRENT_VTE. Latent: 0 held D5 texts use that phrasing." + _OL,
    "rob2.py:search:2ee9bddbd6-accept-3":
        "RX-OL3 (found 2026-09-24 by this plant): 'deep vein thrombosis' is listed but 'deep venous thrombosis' is not, "
        "so that spelling (with no VTE/DVT abbreviation) is not read as a VTE event. Latent: 0 held D5 texts." + _OL,
    "rob2.py:search:2302517c9d-accept-2":
        "RX-OL4 (found 2026-09-24 by this plant): only 'all-cause mortality' is read, so 'all-cause death' / 'death from "
        "any cause' yield no ALL_CAUSE_MORTALITY component. Reachable: held D5 inputs of dpp4-mace-t2d 28893244 "
        "('Number of Participants With an Event of All-Cause Death'; 'All-cause death was death from any cause') and "
        "doac-vte-recurrence 23808982; the recorded D5 levels are 'low', effect on a verdict not measured." + _OL,
    "rob2.py:search:2302517c9d-accept-3":
        "RX-OL4 (found 2026-09-24 by this plant): 'death from any cause' is not read as all-cause mortality (see "
        "accept-2). Reachable in held dpp4-mace-t2d 28893244 D5 description." + _OL,
    "rob2.py:search:052d9d5ea5-accept-4":
        "RX-OL5 (found 2026-09-24 by this plant): CV death is read only as 'cv death' / 'cardiovascular [(..)] death' / "
        "'death from cardiovascular causes', so 'CV-related death' is missed. Reachable and consequential in held text: "
        "dpp4-mace-t2d 28893244's registered MACE measure '(Confirmed CV-Related Death, Fatal and Nonfatal MI, and Fatal "
        "and Nonfatal Stroke)' reads as {NONFATAL_MI, NONFATAL_STROKE} -- no CV death, so not 3-point MACE; the recorded "
        "D5 basis cites a secondary-outcome match instead, and whether this defect is why is not measured." + _OL,
    "rob2.py:search:052d9d5ea5-accept-5":
        "RX-OL5 (found 2026-09-24 by this plant): 'death due to cardiovascular causes' (and held 'Death Due to CV Cause', "
        "noac-vs-warfarin-af-stroke 24251359) is not read as CV death (see accept-4)." + _OL,
    "rob2.py:search:052d9d5ea5-refuse-2":
        "RX-OL6 (found 2026-09-24 by this plant): '\\bcardiovascular' fires after the hyphen in 'non-cardiovascular death', "
        "so non-CV death adds a CV_DEATH component (the defect target_endpoint masks and RX-TE2 names for 'vascular'). "
        "Reachable: held D5 description of omega3-cardiovascular-events 33190147 reads as ['CV_DEATH'] through this "
        "phrase; recorded D5 level 'low', effect on a verdict not measured." + _OL,
    "rob2.py:search:4494298990-accept-4":
        "RX-OL7 (found 2026-09-24 by this plant): 'hospitali[sz](?:ation|ed)\\b' has no plural, so 'hospitalisations for "
        "heart failure' / 'heart failure hospitalizations' yield no HF_HOSPITALISATION component. Reachable: the held "
        "registered measure of iv-iron-hfref-hosp 40159390 ('Rate of total (first and recurrent) events of "
        "hospitalisations for heart failure (HF)') reads as an empty component set; recorded D5 level 'low' (matched on "
        "another registered outcome), effect not measured." + _OL,
    "rob2.py:search:a26bd545ce-accept-3":
        "RX-OL8 (found 2026-09-24 by this plant): 'major adverse cardiac events' (a common expansion of MACE) is not a MACE "
        "term. Latent: all 5 held D5 texts using it also carry '(MACE)'." + _OL,
    "funding.py:_INDUSTRY-accept-3":
        "RX-OL9 (found 2026-09-24 by this plant): the group ends in '\\b', and after 'Inc.' a boundary needs a following "
        "word character, so 'Inc.' before a space / end never marks industry. Reachable and consequential: with 'Inc.' "
        "matched, funding.detect() changes from no class to industry on 2 held documents "
        "(sglt2-primary-prevention-hf records.json#27025436 'FUNDING: Corvia Medical Inc.'; probiotics-aad-prevention "
        "ft_22371721 'BIO K+ International Inc.'), measured 2026-09-24 with a scratch-patched pattern; whether those "
        "reach a served funding row is not measured." + _OL,
    "funding.py:_PUBLIC-accept-3":
        "RX-OL10 (found 2026-09-24 by this plant): the public-funder list has no NHLBI (nor the other NIH institutes by "
        "name), so 'funded by the National Heart, Lung, and Blood Institute' alone is not public. Latent: adding it "
        "changes funding.detect() on 0 held documents (the NIH is named alongside)." + _OL,
    "funding.py:_DRUG_SUPPLY-accept-3":
        "RX-OL11 (found 2026-09-24 by this plant): only the passive form ('<drug> was provided by X') is read, so "
        "'X provided the study drug' is not a drug-supply statement. The phrasing is in held full text "
        "(semaglutide-obesity-weight ft_41778920, tocilizumab-covid19-mortality ft_33080005); effect not measured." + _OL,
    "funding.py:_INDUSTRY_AUTHORS-accept-2":
        "RX-OL12 (found 2026-09-24 by this plant): the employer list is 8 companies, so employees of any other company "
        "are not industry authors. Reachable: held iv-iron-hfref-hosp ft_25176939 states 'V.L. and B.R. are employees of "
        "Vifor Pharma Ltd.' and industry_authors_present is False for it." + _OL,
    "funding.py:_INDUSTRY_AUTHORS-refuse-1":
        "RX-OL13 (found 2026-09-24 by this plant): '.*?' under re.S lets 'employee of' reach a company named in any later "
        "sentence, so a university employee plus 'funded by Pfizer' reads as industry authors. Latent: the 2 held "
        "matches longer than 250 chars (glp1-ra-mace-t2d ft_27295427, ft_28910237) are 'employees of the sponsor' "
        "where the sponsor is that company, so the verdict happens to be right." + _OL,
    "funding.py:L84-accept-2":
        "RX-OL14 (found 2026-09-24 by this plant): 'analys(?:ed|is|es)|analyz(?:ed|es|ing)' has no 'analysing', so the "
        "British spelling of a funder's analysis role is missed. Latent: 0 served held basis spans use it." + _OL,
    "funding.py:split:d3389b2de7-refuse-2":
        "RX-OL15 (found 2026-09-24 by this plant): the sponsor split on ',', 'and' and '&' cuts inside one sponsor's name. "
        "Reachable and served: 9 held detect() sponsor lists are fragmented, e.g. doac-vte-recurrence "
        "records.json#21830957 -> ['Johnson', 'Johnson', 'Bayer']." + _OL,
    "funding.py:split:d3389b2de7-refuse-3":
        "RX-OL15 (found 2026-09-24 by this plant): 'Bill & Melinda Gates Foundation' is split into 'Bill' / 'Melinda Gates "
        "Foundation' (held: tranexamic-acid-pph records.json#39461793, #41519151; iv-iron-hfref-hosp #28919117)." + _OL,
    "funding.py:split:d3389b2de7-refuse-4":
        "RX-OL15 (found 2026-09-24 by this plant): 'National Heart, Lung, and Blood Institute' is split into 3 sponsors "
        "(held: colchicine-recurrent-pericarditis records.json#34051877)." + _OL,
    "hand_binding.py:_REF_JUNK-accept-5":
        "RX-OL16 (found 2026-09-24 by this plant): the DOI marker '10\\.\\d{4}/' needs exactly 4 registrant digits, so a "
        "5-digit DOI such as the Crossref funder registry's '10.13039/...' is not debris. Reachable: 5 held full-text "
        "prose sentences carry one and are kept in the definition pool (omega3-cardiovascular-events ft_38199870, "
        "semaglutide-obesity-weight ft_41778920); effect on a binding not measured." + _OL,
    "hand_binding.py:findall:ea304f7fe8-accept-1":
        "RX-OL17 (found 2026-09-24 by this plant): '<tr>.*?</tr>' needs a bare '<tr>', so a row with attributes "
        "(<tr style=...>, <tr content-type=...>) is not a row. Reachable and consequential: table_rows() drops 17 held "
        "table-body rows carrying numeric cells (colchicine-secondary-cv-prevention ft_32295417, probiotics-aad-prevention "
        "ft_39497860), so no hand binding can locate a result in them." + _OL,
    "hand_binding.py:_RESULT_PAREN-accept-2":
        "RX-OL18 (found 2026-09-24 by this plant): a result parenthesis must say '95%' or 'CI', so the older '95 percent "
        "confidence interval' form is not a result and _owning_clause treats the sentence as one clause. Reachable: 12 "
        "held abstract sentences (e.g. sacubitril-valsartan-hfref records.json#2057034); effect not measured." + _OL,
})

# ---- other-lane files, batch 2 (harness/absence.py, gate.py, protocol_compiler.py, pipeline.py): same terms as above.
_OL2 = " The fix belongs to the owning lane (not the regex layer), filed 2026-09-25."
KNOWN_DEFECTS.update({
    "absence.py:_ESTIMAND_SUFFIX-refuse-1":
        "RX-OL23 (found 2026-09-25 by this plant): under re.I the estimand word 'OR' also matches the conjunction 'or', "
        "so _terms strips it out of an outcome keyword: 'CV death or HHF' -> 'cv death hhf', which can never be a "
        "substring of a sentence saying 'CV death or HHF'; 'adjusted odds ratio' -> 'adjusted'. Reachable and "
        "consequential: 41 distinct held keywords in 11 topics are rewritten, and 25 held abstract sentences in 7 topics "
        "that carry such a keyword verbatim match no term, so _candidate_sentences drops them -- e.g. doac-vte-recurrence "
        "'The primary efficacy outcome was recurrent symptomatic venous thromboembolism or death related to venous "
        "thromboembolism.' (measured 2026-09-25). Effect on a served absence state not measured." + _OL2,
    "protocol_compiler.py:search:6d4338abae-accept-2":
        "RX-OL27 (found 2026-09-25 by this plant): the separator class [-:–] has no em dash, so '**Estimand** — ...' is "
        "not read (the RX-EC2 miss, in a second parser). Reachable: parse_prose(protocols/colchicine-recurrent-"
        "pericarditis.md) returns estimand None, so compare() cannot check ESTIMAND_DIVERGENCE for that topic; masked "
        "today -- with the dash read, compare() returns the same divergence list (config RR agrees)." + _OL2,
    "protocol_compiler.py:search:249cd61f88-accept-1":
        "RX-OL27 (found 2026-09-25 by this plant): same em-dash miss on '**Population** — ...': parse_prose returns "
        "population None for protocols/colchicine-recurrent-pericarditis.md, so compare() cannot check "
        "POPULATION_DIVERGENCE; masked today (config intention-to-treat agrees)." + _OL2,
    "absence.py:_PRIMARY_RESULT-accept-2":
        "RX-OL22 (found 2026-09-25 by this plant): 'primary' must be followed directly by outcome/end point/event, so "
        "'primary composite outcome' / 'primary efficacy outcome' is not a primary-result sentence and the primary-anchor "
        "pull-in in _candidate_sentences skips it. Reachable: 122 held abstract sentences (e.g. 'A primary composite "
        "outcome event occurred in 839 of 7356 patients'); effect on a served absence state not measured." + _OL2,
    "absence.py:_EFFECT-refuse-1":
        "RX-OL19 (found 2026-09-25 by this plant): under re.I 'OR' matches the conjunction 'or', so any 'X or Y ... 3.1' "
        "reads as an effect estimate. Reachable: 220 held abstract sentences fire ONLY through a conjunction 'or'. "
        "Direction: classify() then says the outcome's numbers ARE present (EXTRACTION_NOT_PERFORMED) instead of absent -- "
        "the module's stated safe direction, but a false 'present' claim; effect on a served state not measured." + _OL2,
    "absence.py:_ARMS-refuse-1":
        "RX-OL20 (found 2026-09-25 by this plant): 'N/MM' also matches a blood-pressure reading ('130/80 mm Hg') as arm "
        "counts. Reachable: 5 held abstract sentences fire only on a mm Hg reading; same safe direction as RX-OL19; "
        "effect not measured." + _OL2,
    "protocol_compiler.py:search:249cd61f88-accept-2":
        "RX-OL28 (found 2026-09-25 by this plant): the separator must follow the closing '**', so '**Population:** ...' "
        "is not read (the RX-EC1 miss, in a second parser). Reachable in 4 held protocols (denosumab-vertebral-fracture, "
        "esketamine-trd-madrs, melatonin-primary-insomnia-sol, semaglutide-obesity-weight); none of those lines carries "
        "analysis-set wording, so no population is lost today." + _OL2,
    "pipeline.py:_PMID_LITERAL_RE-refuse-2":
        "RX-OL30 (found 2026-09-25 by this plant): the lookbehind only excludes a preceding digit, so the 8 digits of "
        "'NCT00113685' are also read as a PMID literal. Reachable: 182 held files carry NCT-list queries, each adding "
        "spurious pmid_literal features; the query class cannot change (nct_literal already makes it "
        "IDENTIFIER_SEEDED)." + _OL2,
    "absence.py:_COUNT_WITH_PERCENT-accept-3":
        "RX-OL21 (found 2026-09-25 by this plant): only '%' marks a percentage, so NEJM's older '452 patients (35.2 "
        "percent)' is not a count with its percentage. Latent: 0 held abstract sentences carry that exact form." + _OL2,
    "gate.py:sub:0441b19e00-refuse-1":
        "RX-OL24 (found 2026-09-25 by this plant): every 19xx/20xx token is dropped as a publication year, so a count "
        "such as '2047 patients' escapes the 'every manuscript numeral is object-derived' check (fails open). Latent: 0 "
        "counts in that range beside patients/participants/events in the 32 held reviews' rendered manuscripts." + _OL2,
    "gate.py:search:f3bc3e60aa-refuse-1":
        "RX-OL26 (found 2026-09-25 by this plant): any 'dose' / 'amendment' / 'approved' in the protocol satisfies "
        "'documents a dose-selection rule', so 'low-dose aspirin' passes (fails open). Latent: 0 held reviews carry a "
        "dose_selection override, so the check never runs today." + _OL2,
    "gate.py:_PARITY_EXCL_CUE-refuse-2":
        "RX-OL25 (found 2026-09-25 by this plant): the cue ignores negation, so 'SELECT was not excluded' names SELECT as "
        "excluded and a pooled SELECT raises a false L1 (fails closed). Latent: 0 held parity reasons negate a cue." + _OL2,
    "protocol_compiler.py:search:cbbabbb69a-accept-2":
        "RX-OL29 (found 2026-09-25 by this plant): only the hyphenated 'double-blind' is read, so 'double blind, "
        "placebo-controlled' sets no AND masking. Latent: the 3 held protocols spelling it unhyphenated say 'double "
        "blinding is not required', where None is right." + _OL2,
})
