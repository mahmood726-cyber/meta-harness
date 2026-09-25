# Regex sites outside extract.py -- R2 precision / sampled recall

Measured: **95 of 367** owned sites. Labels: recorded model proposals (`registry/model_proposals/site_label_v2.json`, `site_label_ol.json`, `site_label_deep.json` when present), **not countersigned**; recall is sampled recall.

| site | precision | sampled recall | labelled |
|---|---|---|---|
| `absence.py:_ARMS` | 34 of 40 | 34 of 37 | 80 |
| `absence.py:_BARE_OUTCOME_COUNTS` | 1 of 1 | 1 of 1 | 41 |
| `absence.py:_COUNT_WITH_PERCENT` | 32 of 40 | 32 of 34 | 80 |
| `absence.py:_EFFECT` | 36 of 40 | 36 of 36 | 80 |
| `absence.py:_PRIMARY_RESULT` | 40 of 40 | 40 of 57 | 80 |
| `arm_object.py:_AGE_RANGE` | 38 of 40 | 38 of 43 | 80 |
| `arm_object.py:_DOSE` | 31 of 40 | 31 of 32 | 80 |
| `arm_object.py:_WEEK` | 25 of 40 | 25 of 46 | 80 |
| `arm_object.py:search:1543b331b8` | 40 of 40 | 40 of 44 | 80 |
| `consumer_consistency.py:search:5994968a29` | 2 of 2 | 2 of 4 | 42 |
| `consumer_consistency.py:search:6270a59386` | 32 of 40 | 32 of 32 | 80 |
| `consumer_consistency.py:search:6ecd1e4cdd` | 2 of 2 | 2 of 5 | 42 |
| `consumer_consistency.py:search:ce09041473` | 0 of 0 | 0 of 0 | 40 |
| `consumer_consistency.py:search:ce14d051b1` | 2 of 2 | 2 of 4 | 42 |
| `design_key.py:_NO_INTERACTION_RE` | 3 of 3 | 3 of 8 | 43 |
| `eligibility_chain.py:search:0278e60920` | 2 of 2 | 2 of 19 | 42 |
| `eligibility_chain.py:search:36706f6be6` | 28 of 40 | 28 of 37 | 80 |
| `eligibility_chain.py:search:3a8e5df5f4` | 6 of 8 | 6 of 6 | 48 |
| `eligibility_chain.py:search:4744a336ec` | 0 of 5 | 0 of 0 | 45 |
| `eligibility_chain.py:search:47eac977e0` | 22 of 22 | 22 of 24 | 45 |
| `eligibility_chain.py:search:e9857d1c69` | 10 of 10 | 10 of 10 | 50 |
| `estmeasure.py:_COX` | 15 of 15 | 15 of 15 | 30 |
| `estmeasure.py:_RATE_MODEL` | 11 of 15 | 11 of 11 | 30 |
| `funding.py:_DRUG_SUPPLY` | 0 of 0 | 0 of 0 | 40 |
| `funding.py:_FUNDING_POINTER` | 0 of 0 | 0 of 0 | 40 |
| `funding.py:_INDUSTRY_AUTHORS` | 0 of 0 | 0 of 0 | 40 |
| `funding.py:_NCT_RE` | 40 of 40 | 40 of 40 | 80 |
| `funding.py:_STRONG_ANCHOR` | 40 of 40 | 40 of 40 | 80 |
| `funding.py:_WEAK_ANCHOR` | 18 of 40 | 18 of 19 | 80 |
| `gate.py:search:f3bc3e60aa` | 9 of 35 | 9 of 9 | 46 |
| `hand_binding.py:_REF_JUNK` | 10 of 10 | 10 of 10 | 50 |
| `hand_binding.py:_RESULT_PAREN` | 36 of 40 | 36 of 53 | 80 |
| `harms.py:_EFFECT_OR_COMPARISON` | 8 of 15 | 8 of 8 | 30 |
| `known_missing.py:search:352ce1b856` | 0 of 0 | 0 of 0 | 15 |
| `lexicon.py:_MORT_D` | 15 of 15 | 15 of 15 | 30 |
| `lexicon.py:_MORT_Y` | 15 of 15 | 15 of 15 | 15 |
| `page.py:search:2a82269e03` | 24 of 40 | 24 of 29 | 80 |
| `page.py:search:e9a52114b2` | 18 of 40 | 18 of 20 | 80 |
| `protocol_compiler.py:ELIGIBILITY_BULLET` | 1 of 1 | 1 of 5 | 41 |
| `protocol_compiler.py:ELIGIBILITY_HEADING` | 6 of 6 | 6 of 7 | 46 |
| `protocol_compiler.py:finditer:bf8a0d70a0` | 0 of 0 | 0 of 6 | 19 |
| `protocol_compiler.py:search:249cd61f88` | 8 of 8 | 8 of 9 | 48 |
| `protocol_compiler.py:search:4715c0c46f` | 1 of 1 | 1 of 2 | 2 |
| `protocol_compiler.py:search:5851103837` | 1 of 1 | 1 of 2 | 6 |
| `protocol_compiler.py:search:6d4338abae` | 26 of 26 | 26 of 29 | 47 |
| `protocol_compiler.py:search:7b2c2a25c9` | 1 of 1 | 1 of 1 | 4 |
| `protocol_compiler.py:search:9a8cc773b0` | 24 of 36 | 24 of 24 | 76 |
| `protocol_compiler.py:search:cbbabbb69a` | 9 of 16 | 9 of 10 | 56 |
| `protocol_compiler.py:search:dcfda9493e` | 2 of 2 | 2 of 20 | 42 |
| `protocol_compiler.py:search:f3b63c4300` | 1 of 1 | 1 of 3 | 12 |
| `protocol_compiler.py:start_re` | 38 of 40 | 38 of 38 | 80 |
| `reason_audit.py:_ASSIGNED` | 31 of 40 | 31 of 37 | 80 |
| `reason_audit.py:_COUNT_WITH_PERCENT` | 31 of 40 | 31 of 32 | 80 |
| `reason_audit.py:_EVENT_IN_GROUP` | 4 of 5 | 4 of 8 | 45 |
| `reason_audit.py:_EXPLICIT_FRACTION` | 35 of 40 | 35 of 39 | 80 |
| `reason_audit.py:_GROUP_WORD` | 27 of 40 | 27 of 37 | 80 |
| `reason_audit.py:_TWO_ARM_EVENT_COUNTS` | 19 of 21 | 19 of 23 | 61 |
| `scope_identity.py:_AMENDMENT_RE` | 4 of 4 | 4 of 6 | 19 |
| `scope_identity.py:search:153b0980f5` | 15 of 29 | 15 of 15 | 69 |
| `scope_identity.py:search:46590dd2ae` | 1 of 1 | 1 of 1 | 41 |
| `scope_identity.py:search:bb9c1a634d` | 1 of 1 | 1 of 1 | 41 |
| `search_v2.py:_NCT_RE` | 40 of 40 | 40 of 40 | 80 |
| `source_hierarchy.py:_EFFECT_CANDIDATE` | 15 of 15 | 15 of 15 | 30 |
| `target_endpoint.py:_EFFECT_RE` | 40 of 40 | 40 of 48 | 80 |
| `target_endpoint.py:_MACE_RX` | 39 of 40 | 39 of 40 | 80 |
| `target_endpoint.py:_NAMED_COMPOSITE_RX` | 39 of 40 | 39 of 45 | 80 |
| `target_endpoint.py:_ORDINAL_RX` | 6 of 8 | 6 of 6 | 48 |
| `target_endpoint.py:_POPULATION_RX` | 31 of 40 | 31 of 46 | 80 |
| `target_endpoint.py:_QUALIFIER_RX` | 34 of 40 | 34 of 36 | 80 |
| `target_endpoint.py:_TIMEPOINT_RX` | 30 of 40 | 30 of 42 | 80 |
| `target_endpoint.py:search:3994cff820` | 0 of 0 | 0 of 3 | 40 |
| `target_endpoint.py:search:3cac5c21b4` | 40 of 40 | 40 of 41 | 80 |
| `target_endpoint.py:search:4a4f5b989a` | 1 of 3 | 1 of 1 | 43 |
| `target_endpoint.py:search:714a13cd06` | 34 of 40 | 34 of 38 | 80 |
| `target_endpoint.py:search:722dd482f3` | 28 of 40 | 28 of 30 | 80 |
| `target_endpoint.py:search:8c575f0c81` | 40 of 40 | 40 of 46 | 80 |
| `target_endpoint.py:search:a8e12cadeb` | 34 of 35 | 34 of 34 | 75 |
| `target_endpoint.py:search:aa4a355e65` | 5 of 5 | 5 of 10 | 45 |
| `target_endpoint.py:search:b01e38dc40` | 4 of 4 | 4 of 4 | 44 |
| `target_endpoint.py:search:bb8366c955` | 35 of 40 | 35 of 35 | 80 |
| `target_endpoint.py:search:bb8366c955#2` | 35 of 40 | 35 of 35 | 80 |
| `target_endpoint.py:search:c2741ecf04` | 13 of 40 | 13 of 21 | 80 |
| `target_endpoint.py:search:c511b01726` | 0 of 12 | 0 of 0 | 52 |
| `target_endpoint.py:sub:0b02262c07` | 20 of 40 | 20 of 20 | 80 |
| `target_endpoint.py:sub:cb26b534c7` | 14 of 16 | 14 of 21 | 29 |
| `target_endpoint.py:sub:fce6fbe7f9` | 11 of 25 | 11 of 11 | 65 |
| `target_endpoint.py:sub:ff4ae8621b` | 7 of 22 | 7 of 7 | 35 |
| `trial_family.py:REGISTRY` | 40 of 40 | 40 of 40 | 80 |
| `trial_family.py:search:51bc07b8ef` | 1 of 2 | 1 of 4 | 42 |
| `trial_family.py:search:76b3356c9e` | 3 of 40 | 3 of 3 | 80 |
| `trial_family.py:search:e13d2a5bf6` | 1 of 1 | 1 of 26 | 41 |
| `unit_of_analysis.py:_CLUSTER` | 9 of 10 | 9 of 14 | 50 |
| `unit_of_analysis.py:_CROSSOVER` | 30 of 32 | 30 of 31 | 72 |
| `unit_of_analysis.py:_FACTORIAL` | 18 of 19 | 18 of 25 | 50 |
| `unit_of_analysis.py:_STEPPED_WEDGE` | 3 of 3 | 3 of 3 | 8 |

## Not measured (listed, never dropped)

- `aact.py:_PARTICIPANT_TITLE`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov outcome title
- `aact.py:_RECURRENT_TITLE`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov outcome title
- `absence.py:_ESTIMAND_SUFFIX`: TEXT_SOURCE_NOT_HELD_HERE: an outcome keyword from a topic's keyword list (absence._terms)
- `absence.py:_TAG`: NOT_LABELLABLE: XML/HTML tag stripper; matches markup, not meaning
- `absence.py:split:ee27e721ca`: NOT_LABELLABLE: clause splitter after . ; ) ; matches formatting, not meaning
- `absence.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _strip_markup; matches formatting, not meaning
- `absence.py:sub:7b4eac99d8#2`: NOT_LABELLABLE: whitespace normalisation in _norm_space; matches formatting, not meaning
- `absence.py:sub:bdbb968f46`: NOT_LABELLABLE: non-alphanumeric stripper on a keyword; matches formatting, not meaning
- `architecture_identity.py:SHA40_RE`: TEXT_SOURCE_NOT_HELD_HERE: a GitHub Actions workflow YAML line (architecture_identity)
- `architecture_identity.py:match:6b3929cc6f`: NOT_LABELLABLE: YAML 'jobs:' key finder; matches file structure, not meaning
- `architecture_identity.py:match:6cffb73cad`: NOT_LABELLABLE: YAML 'needs:' key reader (by indentation); matches file structure, not meaning
- `architecture_identity.py:match:704b8dda9d`: TEXT_SOURCE_NOT_HELD_HERE: a GitHub Actions workflow YAML line (architecture_identity)
- `architecture_identity.py:match:983fd0398b`: NOT_LABELLABLE: YAML 'if:' key reader (by indentation); matches file structure, not meaning
- `architecture_identity.py:match:a48edd0621`: NOT_LABELLABLE: YAML job-name key finder (by indentation); matches file structure, not meaning
- `armcontrast.py:_PLACEBO`: TEXT_SOURCE_NOT_HELD_HERE: a registry intervention / arm name
- `certificate.py:REF`: TEXT_SOURCE_NOT_HELD_HERE: a certificate input / page text
- `cites.py:_DOI_RE`: TEXT_SOURCE_NOT_HELD_HERE: a Crossref reference field or a DOI / PMID value (cites; fetched, not held)
- `cites.py:_PMID_RE`: TEXT_SOURCE_NOT_HELD_HERE: a Crossref reference field or a DOI / PMID value (cites; fetched, not held)
- `cites.py:_TAG_RE`: NOT_LABELLABLE: tag stripper; matches markup, not meaning
- `cites.py:split:d0a94246b5`: NOT_LABELLABLE: first-sentence splitter on a title; matches formatting, not meaning
- `cites.py:sub:4e68c4d713`: NOT_LABELLABLE: 'doi:' label stripper; matches DOI formatting, not meaning
- `cites.py:sub:dd5e50e9d6`: NOT_LABELLABLE: doi.org resolver-prefix stripper; matches DOI formatting, not meaning
- `cites.py:sub:e3839b281a`: NOT_LABELLABLE: punctuation-to-space title fold; matches formatting, not meaning
- `claim.py:_ASSERT_NULL`: TEXT_SOURCE_NOT_HELD_HERE: a rendered page surface (outcome block, overview, manuscript)
- `claim.py:_ASSERT_SIG`: TEXT_SOURCE_NOT_HELD_HERE: a rendered page surface (outcome block, overview, manuscript)
- `claimgraph.py:_NCT_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `claimgraph.py:_PMID_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `claimgraph.py:findall:7efba48385`: NOT_LABELLABLE: PDF page-marker line finder; matches file format, not meaning
- `claimgraph.py:search:0a97f189e1`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason
- `claimgraph.py:search:b1f76ed2f3`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason
- `claimgraph.py:split:74aca78d9f`: NOT_LABELLABLE: '+' list splitter; matches formatting, not meaning
- `comparator_panel.py:FORBIDDEN`: TEXT_SOURCE_NOT_HELD_HERE: a rendered page surface (outcome block, overview, manuscript)
- `comparator_panel.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `comparator_panel.py:sub:ebbe919eb3`: NOT_LABELLABLE: tag stripper; matches markup, not meaning
- `comparator_second_pass.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `comparator_truth.py:_N_LVEF40`: TEXT_SOURCE_NOT_HELD_HERE: comparator review text (the held comparator source), as comparator_truth reads it
- `comparator_truth.py:_ONLY_TWO`: TEXT_SOURCE_NOT_HELD_HERE: comparator review text (the held comparator source), as comparator_truth reads it
- `comparator_truth.py:_WS`: NOT_LABELLABLE: whitespace normalisation in _flat; matches formatting, not meaning
- `comparator_truth.py:finditer:82a1fa9ce1`: TEXT_SOURCE_NOT_HELD_HERE: comparator review text (the held comparator source), as comparator_truth reads it
- `comparator_truth.py:search:0c19981303`: TEXT_SOURCE_NOT_HELD_HERE: comparator review text (the held comparator source), as comparator_truth reads it
- `comparator_truth.py:search:3be5b26f67`: NOT_LABELLABLE: first-number finder in a value string; matches number shape, not meaning
- `comparator_truth.py:search:9378a79674`: TEXT_SOURCE_NOT_HELD_HERE: comparator review text (the held comparator source), as comparator_truth reads it
- `comparator_truth.py:split:a4601f97a8`: NOT_LABELLABLE: sentence splitter; matches formatting, not meaning
- `comparator_truth.py:sub:0b2060d20b`: NOT_LABELLABLE: non-digit stripper; matches a character class, not meaning
- `compat_check.py:findall:6ce8847b51`: TEXT_SOURCE_NOT_HELD_HERE: a derived per-trial follow-up window value string (e.g. '56 days', 'within 8 weeks')
- `compat_check.py:search:854c55479d`: TEXT_SOURCE_NOT_HELD_HERE: comparator review name + journal + record title + abstract
- `compat_check.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _norm_ws; matches formatting, not meaning
- `compat_direction.py:_ENDPOINT_HETERO_RE`: TEXT_SOURCE_NOT_HELD_HERE: a review's compat-key limitation / timepoint / population text (compat_direction)
- `compat_direction.py:_HETERO_RE`: TEXT_SOURCE_NOT_HELD_HERE: a review's compat-key limitation / timepoint / population text (compat_direction)
- `compat_direction.py:search:0c34b57e0a`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `compat_direction.py:sub:9bca43bba5`: NOT_LABELLABLE: non-alphanumeric-to-'_' code builder; matches formatting, not meaning
- `compat_direction.py:sub:9bca43bba5#2`: NOT_LABELLABLE: non-alphanumeric-to-'_' code builder; matches formatting, not meaning
- `consumer_consistency.py:_PUBLISHED_EFFECT_IN_SOURCE`: TEXT_SOURCE_NOT_HELD_HERE: a pooled row's source string (consumer_consistency)
- `consumer_consistency.py:search:ee18f71fc1`: TEXT_SOURCE_NOT_HELD_HERE: a pooled row's source string (consumer_consistency)
- `consumer_consistency.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _clip; matches formatting, not meaning
- `ctgov_results.py:search:193897396a`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov outcome title (lowercased)
- `ctgov_results.py:search:e1f2c9fd48`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov outcome title (lowercased)
- `design_key.py:_ALT_RE`: TEXT_SOURCE_NOT_HELD_HERE: a pooled row's source span (design_key._published_alternative)
- `design_key.py:split:9bca43bba5`: NOT_LABELLABLE: estimand token splitter; matches formatting, not meaning
- `design_key.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `design_key.py:sub:7b4eac99d8#2`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `design_key.py:sub:7b4eac99d8#3`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `design_variance.py:search:56325787a0`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `design_variance.py:search:d460b12256`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `eligibility_chain.py:_PMID_RE`: TEXT_SOURCE_NOT_HELD_HERE: a pooled trial's id or label
- `eligibility_chain.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _norm; matches formatting, not meaning
- `endpoint_canonical.py:sub:1850cf21f4`: NOT_LABELLABLE: non-alphanumeric-to-'_' token builder; matches formatting, not meaning
- `endpoint_canonical.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `fda.py:_NCT_RE`: TEXT_SOURCE_NOT_HELD_HERE: a fetched FDA label section (not held)
- `fda.py:_SECTION_RE`: NOT_LABELLABLE: FDA label section-14 splitter; matches label layout, not meaning
- `fda.py:search:89dbcde840`: TEXT_SOURCE_NOT_HELD_HERE: a fetched FDA label section (not held)
- `fetch.py:_NCT_RE`: TEXT_SOURCE_NOT_HELD_HERE: a fetched registry / PubMed field
- `fetch.py:findall:43a3a2d613`: TEXT_SOURCE_NOT_HELD_HERE: a literature search query string
- `fetch.py:search:3348df34b8`: NOT_LABELLABLE: PMC OA ftp package-link extractor; matches markup, not meaning
- `fetch.py:search:9d3135bb10`: NOT_LABELLABLE: PMC OA https package-link extractor; matches markup, not meaning
- `fixstate.py:SHA1_RE`: TEXT_SOURCE_NOT_HELD_HERE: a fix-state / scorecard / prospective-ledger field
- `fixstate.py:SHA256_RE`: TEXT_SOURCE_NOT_HELD_HERE: a fix-state / scorecard / prospective-ledger field
- `fixstate.py:findall:4850140664`: TEXT_SOURCE_NOT_HELD_HERE: a fix-state / scorecard / prospective-ledger field
- `fixstate.py:search:3954d27b9b`: TEXT_SOURCE_NOT_HELD_HERE: a fix-state / scorecard / prospective-ledger field
- `fulltext.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `funding.py:L81`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `funding.py:L82`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `funding.py:L83`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `funding.py:L84`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `funding.py:L85`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `funding.py:_INDUSTRY`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `funding.py:_PUBLIC`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `funding.py:search:a4601f97a8`: NOT_LABELLABLE: sentence-boundary finder for the funding window; matches formatting, not meaning
- `funding.py:split:88ba5636a3`: NOT_LABELLABLE: finds where the sponsor list ends (;, sentence end, registration statement); a boundary, not a statement
- `funding.py:split:d3389b2de7`: NOT_LABELLABLE: list-separator splitter (, and &) between sponsor names; matches formatting, not meaning
- `funding.py:sub:5150d3bfe8`: NOT_LABELLABLE: leading-article stripper on a sponsor name; matches formatting, not meaning
- `funding.py:sub:70a43250a0`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `funding.py:sub:7282f3a795`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `funding.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _clean; matches formatting, not meaning
- `funding.py:sub:a8c5be7f86`: TEXT_SOURCE_NOT_HELD_HERE: the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)
- `gate.py:_PARITY_ACRONYM`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason, or a pooled trial's source string (gate.check_parity_our_k)
- `gate.py:_PARITY_EXCL_CUE`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason, or a pooled trial's source string (gate.check_parity_our_k)
- `gate.py:findall:17a0a13bd9`: NOT_LABELLABLE: decimal-number shape; matches number formatting, not meaning
- `gate.py:findall:51811c45be`: NOT_LABELLABLE: 'N of M' number shape; matches number formatting, not meaning
- `gate.py:findall:8caff6711a`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason, or a pooled trial's source string (gate.check_parity_our_k)
- `gate.py:findall:8cbf399ebf`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason, or a pooled trial's source string (gate.check_parity_our_k)
- `gate.py:findall:b5d71114cf`: NOT_LABELLABLE: integer shape; matches number formatting, not meaning
- `gate.py:search:159a89219d`: NOT_LABELLABLE: any-digit test; matches a character class, not meaning
- `gate.py:search:3f33b77a44`: TEXT_SOURCE_NOT_HELD_HERE: the rendered review page text (gate surface checks)
- `gate.py:search:8aebad504f`: TEXT_SOURCE_NOT_HELD_HERE: the rendered review page text (gate surface checks)
- `gate.py:search:9a92bea520`: TEXT_SOURCE_NOT_HELD_HERE: the rendered review page text (gate surface checks)
- `gate.py:search:e1d3371bfb`: NOT_LABELLABLE: harms-tab panel extractor; matches markup, not meaning
- `gate.py:sub:02dd231974`: NOT_LABELLABLE: the 'k - 1' degrees-of-freedom formula token; matches notation, not a statement
- `gate.py:sub:0441b19e00`: TEXT_SOURCE_NOT_HELD_HERE: the rendered manuscript text of a review (gate.check_paper_numerals)
- `gate.py:sub:17a0a13bd9`: NOT_LABELLABLE: decimal-number shape; matches number formatting, not meaning
- `gate.py:sub:2d78918e2a`: TEXT_SOURCE_NOT_HELD_HERE: the rendered manuscript text of a review (gate.check_paper_numerals)
- `gate.py:sub:4755f742a5`: NOT_LABELLABLE: <pre> block remover; matches markup, not meaning
- `gate.py:sub:b2b1cda05a`: NOT_LABELLABLE: <svg> block remover; matches markup, not meaning
- `gate.py:sub:caf616cd71`: NOT_LABELLABLE: tag stripper; matches markup, not meaning
- `gate_scorecard.py:ISO_UTC_RE`: TEXT_SOURCE_NOT_HELD_HERE: a fix-state / scorecard / prospective-ledger field
- `gate_scorecard.py:SHA_RE`: TEXT_SOURCE_NOT_HELD_HERE: a fix-state / scorecard / prospective-ledger field
- `gate_scorecard.py:fullmatch:09fc75115e`: TEXT_SOURCE_NOT_HELD_HERE: a fix-state / scorecard / prospective-ledger field
- `gate_scorecard.py:sub:282549ad30`: NOT_LABELLABLE: non-alphanumeric-to-'-' slug builder; matches formatting, not meaning
- `hand_binding.py:_LEADING_JOIN`: NOT_LABELLABLE: strips a leading conjunction (as was / and / whereas / while / but) from an attached clause; matches clause syntax, not a statement
- `hand_binding.py:_TEXT_TABLES_MARK`: NOT_LABELLABLE: serialisation marker opening the flattened tables section; matches file format, not meaning
- `hand_binding.py:findall:1af9a0dc3c`: NOT_LABELLABLE: JATS table-cell extractor; matches markup, not meaning
- `hand_binding.py:findall:3ab362c751`: NOT_LABELLABLE: JATS <thead> block finder; matches markup, not meaning
- `hand_binding.py:findall:d83cacfc5a`: NOT_LABELLABLE: JATS caption extractor; matches markup, not meaning
- `hand_binding.py:findall:e1bb2e6e84`: NOT_LABELLABLE: JATS table-footnote extractor; matches markup, not meaning
- `hand_binding.py:findall:ea304f7fe8`: NOT_LABELLABLE: JATS table-row finder; matches markup, not meaning
- `hand_binding.py:finditer:2fa8c78f40`: NOT_LABELLABLE: JATS <table-wrap> block finder; matches markup, not meaning
- `hand_binding.py:match:43cb536653`: TEXT_SOURCE_NOT_HELD_HERE: a hand row's declared comparator-direction string
- `hand_binding.py:search:159a89219d`: NOT_LABELLABLE: any-digit test telling a data row from a heading cell; matches a character class, not meaning
- `hand_binding.py:search:159a89219d#2`: NOT_LABELLABLE: any-digit test telling a data row from a heading cell; matches a character class, not meaning
- `hand_binding.py:search:b44342a693`: NOT_LABELLABLE: JATS <tbody> block finder; matches markup, not meaning
- `hand_binding.py:search:b4ef0d080a`: NOT_LABELLABLE: number-shape test telling a header row from a data row; matches number formatting, not meaning
- `hand_binding.py:split:59b745f04e`: NOT_LABELLABLE: sentence splitter after ').' before a digit; matches formatting, not meaning
- `hand_binding.py:sub:07d45602cf`: NOT_LABELLABLE: non-letter stripper on a table label; matches formatting, not meaning
- `hand_binding.py:sub:2abf06a9a2`: NOT_LABELLABLE: JATS front/back-matter element remover; matches markup, not meaning
- `hand_binding.py:sub:2fa8c78f40`: NOT_LABELLABLE: JATS <table-wrap> remover; matches markup, not meaning
- `hand_binding.py:sub:575187a28f`: NOT_LABELLABLE: word-final 's' stripper for plural tolerance; matches spelling, not meaning
- `hand_binding.py:sub:575187a28f#2`: NOT_LABELLABLE: word-final 's' stripper for plural tolerance; matches spelling, not meaning
- `hand_binding.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _plain; matches formatting, not meaning
- `hand_binding.py:sub:8782f4efdb`: NOT_LABELLABLE: JATS <xref> citation-marker remover; matches markup, not meaning
- `hand_binding.py:sub:caf616cd71`: NOT_LABELLABLE: XML tag stripper in _plain; matches markup, not meaning
- `hand_binding.py:sub:caf616cd71#2`: NOT_LABELLABLE: XML tag stripper in prose_of; matches markup, not meaning
- `hand_binding.py:sub:ddb5c10500`: NOT_LABELLABLE: JATS <ref-list> remover; matches markup, not meaning
- `hand_binding.py:sub:e6e9990818`: NOT_LABELLABLE: JATS <article-id> remover; matches markup, not meaning
- `harms.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `harms.py:sub:7b4eac99d8#2`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `harms.py:sub:bc55264a26`: NOT_LABELLABLE: non-alphanumeric stripper on a keyword; matches formatting, not meaning
- `heldout.py:IDENTIFIER_RE`: NOT_LABELLABLE: identifier-shaped token finder; matches a character pattern, not meaning
- `honest_ratchet.py:L53`: TEXT_SOURCE_NOT_HELD_HERE: the rendered text of a served page
- `honest_ratchet.py:sub:627bb26cb4`: NOT_LABELLABLE: <script>/<style> block remover; matches markup, not meaning
- `honest_ratchet.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `honest_ratchet.py:sub:7b4eac99d8#2`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `honest_ratchet.py:sub:caf616cd71`: NOT_LABELLABLE: tag stripper; matches markup, not meaning
- `index.py:findall:17a0a13bd9`: NOT_LABELLABLE: decimal-number shape; matches number formatting, not meaning
- `index.py:findall:51811c45be`: NOT_LABELLABLE: 'N of M' number shape; matches number formatting, not meaning
- `index.py:findall:b5d71114cf`: NOT_LABELLABLE: integer shape; matches number formatting, not meaning
- `index.py:search:5c88386f0c`: TEXT_SOURCE_NOT_HELD_HERE: the index page's static banner prose / its generated capture text
- `index.py:sub:0441b19e00`: TEXT_SOURCE_NOT_HELD_HERE: the index page's static banner prose / its generated capture text
- `index.py:sub:17a0a13bd9`: NOT_LABELLABLE: decimal-number shape; matches number formatting, not meaning
- `index.py:sub:caf616cd71`: NOT_LABELLABLE: tag stripper; matches markup, not meaning
- `index.py:sub:f2d4b3ad26`: TEXT_SOURCE_NOT_HELD_HERE: the index page's static banner prose / its generated capture text
- `integrity.py:_PMID`: NOT_LABELLABLE: PubMed XML PMID-element extractor; matches markup, not meaning
- `integrity.py:_PMID_BLOCK`: NOT_LABELLABLE: PubMed XML article-block extractor; matches markup, not meaning
- `integrity.py:_PUBTYPE`: NOT_LABELLABLE: PubMed XML PublicationType extractor; matches markup, not meaning
- `integrity.py:_REFTYPE`: NOT_LABELLABLE: PubMed XML CommentsCorrections RefType extractor; matches markup, not meaning
- `invalidation.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `invalidation.py:sub:e3839b281a`: NOT_LABELLABLE: punctuation fold; matches formatting, not meaning
- `invalidation.py:sub:e3839b281a#2`: NOT_LABELLABLE: slug builder; matches formatting, not meaning
- `invalidation.py:sub:e3839b281a#3`: NOT_LABELLABLE: compacting fold; matches formatting, not meaning
- `known_missing.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `lexicon.py:_CAUSE_RE`: TEXT_SOURCE_NOT_HELD_HERE: the text following an outcome term
- `lexicon.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in fold; matches formatting, not meaning
- `limitations.py:sub:1850cf21f4`: NOT_LABELLABLE: slug builder; matches formatting, not meaning
- `membership.py:_NCT_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial id / record id / source string (membership canonical ids)
- `membership.py:_NEGATIVE_PARITY_RE`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason (membership.parity_conflicts)
- `membership.py:_NUMERIC_PMID_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial id / record id / source string (membership canonical ids)
- `membership.py:_PMID_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial id / record id / source string (membership canonical ids)
- `membership.py:findall:693f9b4595`: TEXT_SOURCE_NOT_HELD_HERE: a trial id / record id / source string (membership canonical ids)
- `membership.py:findall:ac0fc4ac8d`: TEXT_SOURCE_NOT_HELD_HERE: a trial id / record id / source string (membership canonical ids)
- `membership.py:search:3d23717e76`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason (membership.parity_conflicts)
- `membership.py:split:373165b5f8`: NOT_LABELLABLE: sentence splitter; matches formatting, not meaning
- `page.py:sub:062e5ca288`: NOT_LABELLABLE: legacy Screened-in row extractor; matches markup, not meaning
- `page.py:sub:4f38856489`: NOT_LABELLABLE: legacy 'records screened' sentence extractor; matches markup, not meaning
- `page.py:sub:af38ae76fc`: NOT_LABELLABLE: legacy PRISMA-flow table extractor; matches markup, not meaning
- `parity_relation.py:_PATIENT_PCT`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason
- `parity_relation.py:_RATIO`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason
- `pipeline.py:_ACRONYM_TOKEN_RE`: NOT_LABELLABLE: capitalised-token shape; the trial / non-trial decision is made downstream by _trial_acronym_tokens
- `pipeline.py:_DOI_RE`: TEXT_SOURCE_NOT_HELD_HERE: a literature search query string (pipeline._query_classification)
- `pipeline.py:_JOURNAL_RE`: TEXT_SOURCE_NOT_HELD_HERE: a literature search query string (pipeline._query_classification)
- `pipeline.py:_NAMED_HELD_PATH`: TEXT_SOURCE_NOT_HELD_HERE: a hand row's source string
- `pipeline.py:_PMID_LITERAL_RE`: TEXT_SOURCE_NOT_HELD_HERE: a literature search query string (pipeline._query_classification)
- `pipeline.py:_TITLE_FIELD_RE`: TEXT_SOURCE_NOT_HELD_HERE: a literature search query string (pipeline._query_classification)
- `pipeline.py:_YEAR_RE`: TEXT_SOURCE_NOT_HELD_HERE: a literature search query string (pipeline._query_classification)
- `pipeline.py:findall:56325787a0`: TEXT_SOURCE_NOT_HELD_HERE: a literature search query string (pipeline._query_classification)
- `pipeline.py:findall:e902435e30`: NOT_LABELLABLE: alphanumeric tokeniser; matches formatting, not meaning
- `pipeline.py:search:c2741ecf04`: TEXT_SOURCE_NOT_HELD_HERE: an endpoint name (lowercased)
- `propositions.py:_NCT_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `propositions.py:_PMID_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `propositions.py:search:3c5b448a8e`: TEXT_SOURCE_NOT_HELD_HERE: a review's evidence-base caveat
- `propositions.py:search:3d174448cd`: TEXT_SOURCE_NOT_HELD_HERE: a review's stored parity reason
- `prospective.py:SAFE_NAME_RE`: NOT_LABELLABLE: filesystem-safe name check; matches a character class, not meaning
- `prospective.py:fullmatch:30c6674876`: TEXT_SOURCE_NOT_HELD_HERE: a fix-state / scorecard / prospective-ledger field
- `prospective.py:match:7085b2958e`: NOT_LABELLABLE: numbered-list-item line finder; matches markdown structure, not meaning
- `protocol_compiler.py:bullet_re`: NOT_LABELLABLE: next-bold-bullet boundary; matches markdown structure, not meaning
- `protocol_compiler.py:search:1e08a0ee7b`: NOT_LABELLABLE: next-section heading boundary; matches markdown structure, not meaning
- `protocol_compiler.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _norm_text; matches formatting, not meaning
- `protocol_compiler.py:sub:e3839b281a`: NOT_LABELLABLE: punctuation-to-space fold in _fold_for_prose; matches formatting, not meaning
- `reason_audit.py:_NCT_OR_PMID`: TEXT_SOURCE_NOT_HELD_HERE: a trial id / label string (reason_audit.canonical_trial_id)
- `reason_audit.py:_TAG`: NOT_LABELLABLE: tag stripper; matches markup, not meaning
- `reason_audit.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in norm_space; matches formatting, not meaning
- `registry_first.py:_ISRCTN_CANONICAL_RE`: NOT_LABELLABLE: ISRCTN XML attribute extractor; matches markup, not meaning
- `registry_first.py:_ISRCTN_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `registry_first.py:_NCT_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `registry_first.py:_PMID_RE`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `registry_first.py:search:00dd9077fe`: NOT_LABELLABLE: ISRCTN XML totalCount extractor; matches markup, not meaning
- `registry_multi.py:_EUDRACT_RE`: TEXT_SOURCE_NOT_HELD_HERE: fetched EU-CTR / ICTRP registry HTML (not held in this repo)
- `registry_multi.py:_ICTRP_ROW_RE`: NOT_LABELLABLE: ICTRP result-row extractor; matches markup, not meaning
- `registry_multi.py:findall:01ccab1c69`: NOT_LABELLABLE: href extractor; matches markup, not meaning
- `registry_multi.py:findall:01ccab1c69#2`: NOT_LABELLABLE: href extractor; matches markup, not meaning
- `registry_multi.py:pattern`: TEXT_SOURCE_NOT_HELD_HERE: a registry search query string
- `registry_multi.py:search:0e30ce316a`: NOT_LABELLABLE: ICTRP trial-id span extractor; matches markup, not meaning
- `registry_multi.py:search:59e7e1f76c`: NOT_LABELLABLE: EU-CTR Full Title cell extractor; matches markup, not meaning
- `registry_multi.py:search:808134fb4a`: NOT_LABELLABLE: EU-CTR protocol-page field extractor (title between its label and A.3.1); matches page layout, not meaning
- `registry_multi.py:search:c2f5733989`: NOT_LABELLABLE: EU-CTR EudraCT-number cell extractor; matches markup, not meaning
- `registry_multi.py:search:d0b77052c3`: NOT_LABELLABLE: ICTRP Trial2.aspx link extractor; matches markup, not meaning
- `registry_multi.py:sub:caf616cd71`: NOT_LABELLABLE: tag stripper in _clean_text; matches markup, not meaning
- `rob2.py:search:052d9d5ea5`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:07c0729508`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:145e8c3798`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:217d388541`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:2302517c9d`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:2ee9bddbd6`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:39f51c3310`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:4494298990`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:4ae0272c1d`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:6a51f42d5e`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:6cd81436fb`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:74ee9684cf`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:75347cb965`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:95e6c448a9`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:a26bd545ce`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:ac07acacc3`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:b4e124d7bc`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:c958964040`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:search:e1fe9ad18e`: TEXT_SOURCE_NOT_HELD_HERE: a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 D5 reads them (after _norm_text, lowercased)
- `rob2.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _norm_text; matches formatting, not meaning
- `rob2.py:sub:e3839b281a`: NOT_LABELLABLE: punctuation-to-space normalisation in _simple_matches; matches formatting, not meaning
- `rob2.py:sub:e3839b281a#2`: NOT_LABELLABLE: punctuation-to-space normalisation in _simple_matches; matches formatting, not meaning
- `scope_identity.py:search:2cdeb7a7ad`: TEXT_SOURCE_NOT_HELD_HERE: an amendment / cache timestamp value
- `scope_identity.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `screen_entry.py:_CONTROL`: TEXT_SOURCE_NOT_HELD_HERE: a registry intervention / arm name
- `search_v2.py:_DOI_RE`: TEXT_SOURCE_NOT_HELD_HERE: a search-v2 registry record field (id, DOI, date)
- `search_v2.py:_ISRCTN_RE`: TEXT_SOURCE_NOT_HELD_HERE: a search-v2 registry record field (id, DOI, date)
- `search_v2.py:_PMID_RE`: TEXT_SOURCE_NOT_HELD_HERE: a search-v2 registry record field (id, DOI, date)
- `search_v2.py:_WORD_SPLIT_RE`: NOT_LABELLABLE: whitespace word splitter; matches formatting, not meaning
- `search_v2.py:search:b19728903c`: TEXT_SOURCE_NOT_HELD_HERE: a search-v2 registry record field (id, DOI, date)
- `search_v2.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation of XML text; matches formatting, not meaning
- `second_source.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `source_hierarchy.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `target_endpoint.py:search:8cbbf29039`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov results analysis paramType string
- `target_endpoint.py:search:bd7f86d57b`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov results analysis paramType string
- `target_endpoint.py:search:dafd757c05`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov results analysis paramType string
- `target_endpoint.py:split:4634658391`: NOT_LABELLABLE: sentence-boundary splitter (whitespace after . ? !); matches formatting, not meaning
- `target_endpoint.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation of a captured population string; matches formatting, not meaning
- `target_endpoint.py:sub:7b4eac99d8#2`: NOT_LABELLABLE: whitespace normalisation inside _fold; matches formatting, not meaning
- `target_endpoint.py:sub:a7bc694bbb`: NOT_LABELLABLE: punctuation/non-word stripping to build a dedupe key; matches formatting, not meaning
- `trial_family.py:fullmatch:32005ef657`: TEXT_SOURCE_NOT_HELD_HERE: a trial / registry id string
- `trial_family.py:fullmatch:e45e5b124d`: TEXT_SOURCE_NOT_HELD_HERE: a registry minimum-age value
- `unit_of_analysis.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation; matches formatting, not meaning
- `verify.py:search:39f6421668`: TEXT_SOURCE_NOT_HELD_HERE: the committed source of one pooled row, for that row's value (the pattern is formatted per value)
- `verify.py:search:3a8ce1b5db`: TEXT_SOURCE_NOT_HELD_HERE: the committed source of one pooled row, for that row's value (the pattern is formatted per value)
- `verify.py:search:a74619243b`: TEXT_SOURCE_NOT_HELD_HERE: the committed source of one pooled row, for that row's value (the pattern is formatted per value)
- `verify.py:search:f57813b775`: TEXT_SOURCE_NOT_HELD_HERE: the committed source of one pooled row, for that row's value (the pattern is formatted per value)
