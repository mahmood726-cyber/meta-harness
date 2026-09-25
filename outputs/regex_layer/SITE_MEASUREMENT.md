# Regex sites outside extract.py -- R2 precision / sampled recall

Measured: **57 of 181** owned sites. Labels: recorded model proposals (`registry/model_proposals/site_label_v2.json`, `site_label_ol.json`, `site_label_deep.json` when present), **not countersigned**; recall is sampled recall.

| site | precision | sampled recall | labelled |
|---|---|---|---|
| `absence.py:_ARMS` | 14 of 15 | 14 of 14 | 30 |
| `absence.py:_BARE_OUTCOME_COUNTS` | 1 of 1 | 1 of 1 | 16 |
| `absence.py:_COUNT_WITH_PERCENT` | 10 of 15 | 10 of 10 | 30 |
| `absence.py:_EFFECT` | 13 of 15 | 13 of 13 | 30 |
| `absence.py:_PRIMARY_RESULT` | 15 of 15 | 15 of 20 | 30 |
| `eligibility_chain.py:search:0278e60920` | 2 of 2 | 2 of 19 | 42 |
| `eligibility_chain.py:search:36706f6be6` | 28 of 40 | 28 of 37 | 80 |
| `eligibility_chain.py:search:3a8e5df5f4` | 6 of 8 | 6 of 6 | 48 |
| `eligibility_chain.py:search:4744a336ec` | 0 of 5 | 0 of 0 | 45 |
| `eligibility_chain.py:search:47eac977e0` | 22 of 22 | 22 of 24 | 45 |
| `eligibility_chain.py:search:e9857d1c69` | 10 of 10 | 10 of 10 | 50 |
| `funding.py:_DRUG_SUPPLY` | 0 of 0 | 0 of 0 | 40 |
| `funding.py:_FUNDING_POINTER` | 0 of 0 | 0 of 0 | 40 |
| `funding.py:_INDUSTRY_AUTHORS` | 0 of 0 | 0 of 0 | 40 |
| `funding.py:_NCT_RE` | 40 of 40 | 40 of 40 | 80 |
| `funding.py:_STRONG_ANCHOR` | 40 of 40 | 40 of 40 | 80 |
| `funding.py:_WEAK_ANCHOR` | 18 of 40 | 18 of 19 | 80 |
| `gate.py:search:f3bc3e60aa` | 4 of 15 | 4 of 4 | 26 |
| `hand_binding.py:_REF_JUNK` | 10 of 10 | 10 of 10 | 50 |
| `hand_binding.py:_RESULT_PAREN` | 36 of 40 | 36 of 53 | 80 |
| `protocol_compiler.py:ELIGIBILITY_BULLET` | 1 of 1 | 1 of 3 | 16 |
| `protocol_compiler.py:ELIGIBILITY_HEADING` | 6 of 6 | 6 of 7 | 21 |
| `protocol_compiler.py:finditer:bf8a0d70a0` | 0 of 0 | 0 of 5 | 15 |
| `protocol_compiler.py:search:249cd61f88` | 8 of 8 | 8 of 8 | 23 |
| `protocol_compiler.py:search:4715c0c46f` | 1 of 1 | 1 of 2 | 2 |
| `protocol_compiler.py:search:5851103837` | 1 of 1 | 1 of 2 | 6 |
| `protocol_compiler.py:search:6d4338abae` | 15 of 15 | 15 of 17 | 30 |
| `protocol_compiler.py:search:7b2c2a25c9` | 1 of 1 | 1 of 1 | 4 |
| `protocol_compiler.py:search:9a8cc773b0` | 9 of 15 | 9 of 9 | 30 |
| `protocol_compiler.py:search:cbbabbb69a` | 8 of 15 | 8 of 9 | 30 |
| `protocol_compiler.py:search:dcfda9493e` | 2 of 2 | 2 of 10 | 17 |
| `protocol_compiler.py:search:f3b63c4300` | 1 of 1 | 1 of 3 | 12 |
| `protocol_compiler.py:start_re` | 15 of 15 | 15 of 15 | 30 |
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

## Not measured (listed, never dropped)

- `absence.py:_ESTIMAND_SUFFIX`: TEXT_SOURCE_NOT_HELD_HERE: an outcome keyword from a topic's keyword list (absence._terms)
- `absence.py:_TAG`: NOT_LABELLABLE: XML/HTML tag stripper; matches markup, not meaning
- `absence.py:split:ee27e721ca`: NOT_LABELLABLE: clause splitter after . ; ) ; matches formatting, not meaning
- `absence.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _strip_markup; matches formatting, not meaning
- `absence.py:sub:7b4eac99d8#2`: NOT_LABELLABLE: whitespace normalisation in _norm_space; matches formatting, not meaning
- `absence.py:sub:bdbb968f46`: NOT_LABELLABLE: non-alphanumeric stripper on a keyword; matches formatting, not meaning
- `compat_check.py:findall:6ce8847b51`: TEXT_SOURCE_NOT_HELD_HERE: a derived per-trial follow-up window value string (e.g. '56 days', 'within 8 weeks')
- `compat_check.py:search:854c55479d`: TEXT_SOURCE_NOT_HELD_HERE: comparator review name + journal + record title + abstract
- `compat_check.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _norm_ws; matches formatting, not meaning
- `eligibility_chain.py:_PMID_RE`: TEXT_SOURCE_NOT_HELD_HERE: a pooled trial's id or label
- `eligibility_chain.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _norm; matches formatting, not meaning
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
- `protocol_compiler.py:bullet_re`: NOT_LABELLABLE: next-bold-bullet boundary; matches markdown structure, not meaning
- `protocol_compiler.py:search:1e08a0ee7b`: NOT_LABELLABLE: next-section heading boundary; matches markdown structure, not meaning
- `protocol_compiler.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation in _norm_text; matches formatting, not meaning
- `protocol_compiler.py:sub:e3839b281a`: NOT_LABELLABLE: punctuation-to-space fold in _fold_for_prose; matches formatting, not meaning
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
- `target_endpoint.py:search:8cbbf29039`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov results analysis paramType string
- `target_endpoint.py:search:bd7f86d57b`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov results analysis paramType string
- `target_endpoint.py:search:dafd757c05`: TEXT_SOURCE_NOT_HELD_HERE: a CT.gov results analysis paramType string
- `target_endpoint.py:split:4634658391`: NOT_LABELLABLE: sentence-boundary splitter (whitespace after . ? !); matches formatting, not meaning
- `target_endpoint.py:sub:7b4eac99d8`: NOT_LABELLABLE: whitespace normalisation of a captured population string; matches formatting, not meaning
- `target_endpoint.py:sub:7b4eac99d8#2`: NOT_LABELLABLE: whitespace normalisation inside _fold; matches formatting, not meaning
- `target_endpoint.py:sub:a7bc694bbb`: NOT_LABELLABLE: punctuation/non-word stripping to build a dedupe key; matches formatting, not meaning
