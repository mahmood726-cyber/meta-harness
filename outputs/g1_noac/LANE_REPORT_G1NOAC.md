> **Superseded census.** This is the Codex lane's report as written, BEFORE integration. Its route census (0 of 8 TWO_SOURCE_VERIFIED) came from two defects fixed at integration: an axis one source does not state (UNKNOWN) could never match, so 19 of 19 pairs were refused on timepoint; and tuples from different analyses (ITT vs on-treatment, 95% vs 97.5% CI) were scored as CONFLICT. Current figures: outputs/g1_noac/G1_NOAC.md.

# LANE_REPORT ? G1NOAC

## FILES

Only these six allowed new files were written:

- `harness/g1_noac.py` ? topic-specific, deterministic primary-source audit and typed gates.
- `scripts/g1_noac_build.py` ? offline snapshot builder plus all-topic census (`--census`). The lane-specific filename whitelist takes precedence over COMMON's generic `<lane>_census.py` suggestion; no additional script was created.
- `tests/test_g1_noac.py` ? defect plants, correct-input controls, and held-data integration checks.
- `outputs/g1_noac/g1_noac.json` ? full selected AACT records, row hashes/line locators, source tuples/spans, routes, comparisons, reproduction arithmetic, and census.
- `outputs/g1_noac/G1_NOAC.md` ? readable source-tuple and comparator audit.
- `LANE_REPORT.md` ? this completion artifact.

No existing harness modules, topics, docs, cache, registries, workbook, index, or git metadata were edited. No commit, staging, checkout, push, network request, or access to `C:\meta-harness` occurred. Read-only git checks used `--no-optional-locks`; tracked diff was empty. Pre-existing untracked COMMON.md, LANE_PROMPT.md, acquisition excerpts, lane.log and lane.pid were left alone.

## RULES

**Named two-source rule:** `harness.g1_noac.TWO_SOURCE_RULE`:

> TWO_SOURCE_VERIFIED requires the same typed tuple at printed precision in two independent primary sources; one primary is SINGLE_SOURCE; disagreement is CONFLICT; comparator-only is SECONDARY_ONLY.

The tuple includes outcome/definition, measure, standard-dose contrast, population, timepoint, CI confidence level, and printed values. Missing metadata does not equal matching metadata. `SINGLE_SOURCE` can therefore mean several held documents with numerical corroboration but no second independently established *complete typed tuple*. `CONFLICT` includes incompatible analysis alternatives; it does not automatically mean a publication is erroneous. No conflicting values are averaged.

1. **Deterministic identity.** Comparator regimen labels/doses are extracted from the comparator's standard-dose paragraph. Identity requires a unique registry acronym/title, or a self-naming held primary abstract with an explicit NCT AND an exact PMID-to-NCT AACT reference. Inventory membership comes from `harness.trial_family.load_registry(ROOT, slug)`. Zero/multiple candidates remain `UNRESOLVED`. AACT `DERIVED` references are accepted only with the self-naming abstract and explicit-NCT corroboration; mere citation association is insufficient. The four NCTs are obtained from the served inventory then independently resolved, not hand-entered as findings.
2. **Units before counts.** `year|patient.?years?|person.?years?|/yr` takes precedence over `NUMBER`; `%`/percent becomes PERCENTAGE. COUNT requires explicit participant/patient/subject/event units, a recognized parameter type, and an exact nonnegative integer. No `int(float(rate))`; no inverse calculation of events from rounded percentages or person-time. Unrecognized units and missing denominators are named refusals.
3. **Outcome and arm binding.** `outcome_key` accepts stroke/systemic embolism without added death/MI/PE/bleeding components. It accepts the standalone major-bleed category but refuses nonmajor composites, ICH-only rows, and TIMI/GUSTO alternatives. Individual stroke/SE component counts are not added: they need not be mutually exclusive people. The standard-dose arm is selected by group title (dabigatran dose; high-dose edoxaban); low-dose arms are refused. High-dose edoxaban/placebo-warfarin is not mistaken for the active warfarin arm. Analyses must link through `outcome_analysis_groups` to exactly standard and control groups.
4. **Primary source extraction and anti-circularity.** AACT rows retain table, line, raw-row SHA-256 and snapshot date. Abstract effect/CI regex binds the appropriate outcome sentence and the immediately preceding dose. FDA numbers come only from the explicitly segmented table body; rate parentheses never become counts. Independent IDs are AACT, each primary PMID, and each FDA document; duplicates of one source do not count twice. Comparator figures are targets only. RELAYED/secondary/unanchored input cannot achieve primary verification. Excerpt header hashes describe held **text extractions**, not PDFs; output names them `source_held_text_sha256` and separately hashes the excerpt bytes. The underlying full regulator files were not assumed present or reverified.
5. **Precision and semantics.** Decimal equality rounds both values at the coarser printed precision; counts require exact equality. ITT, modified ITT, per-protocol, and on-treatment remain distinct. Exact follow-up strings and CI levels are retained. Unknown follow-up/ISTH definition is not filled from the comparator or another source. ENGAGE's abstract 97.5% interval is converted by its stated normal quantile solely for the served-estimate comparison; the AACT 99% interval is separately retained. No conversion silently verifies two sources.
6. **Reproduction gate.** The strong table only sums full count/N tuples satisfying `TWO_SOURCE_VERIFIED`, separately for ITT and on-treatment/safety. Missing trials are named; an empty verified subtotal is explicitly not a four-trial estimate. A separate diagnostic enumerates all available primary count combinations and gives exact target-minus-total residuals, without upgrading single sources or unknown populations. STARTED participant-flow counts are not relabelled as randomized counts. Comparator follow-up censoring is reported explicitly.
7. **Result comparison and proposed sensitivity.** Served values are read from review.json. The proposal takes the FDA HRs for the two formerly unbound bleeding rows and primary-abstract HRs for the other trials, then calls **`harness.synth.pool`**, not the secondary-module pool (whose HK floor differs). It is an explicitly non-admissible sensitivity calculation, never a served or verified pooled result. No investigator-supplied number is used as an input.

### Static versus dynamic disclosure

| Element | Static logic/configuration | Dynamic evidence/value source |
|---|---|---|
| Scope | NOAC topic slug; two endpoint classes; fixed held comparator location | All topics/*.json parsed; other topics explicitly OUT OF SCOPE |
| Trial identities and standard regimens | Unique-match rules, drug/dose parsing grammar | Comparator paragraph, held abstracts, AACT references/titles, family registry |
| Numeric values | Regex grammar and Decimal precision policy only | AACT pipe-delimited rows, abstract bytes, FDA excerpt cells |
| Clinical typing | Unit, dose, population, endpoint/definition rules | Source title, population, time_frame, category, group/analysis links |
| Verification threshold | Two independent primary sources; unknown metadata fails closed | Source IDs and complete parsed tuples |
| Pooling | Existing PM/HKSJ engine and CI conversion formula | Source-extracted HRs and confidence bounds |
| Findings/counts | None hardcoded | Runtime census, sums, differences, source/served comparisons |
| Test plants | Explicit synthetic defect and control inputs | Never included in the research output |

## PLANTS

All test plants are labelled synthetic in the test module. Pre-fix outputs below are actual calls to unedited base harness functions. For `aact_lane`, its AST was compiled with in-memory planted rows and in-memory file handles: no base output file was written and no network-capable acquisition module was imported. `resolve_unit` was similarly exercised on a no-basis plant.

```json

{
  "rate": {
    "NCT00000001": {
      "outcomes": {
        "o": {
          "title": "stroke",
          "time_frame": "1 year",
          "type": "PRIMARY"
        }
      },
      "analyses": [],
      "groups": {
        "o": [
          {
            "group": "g",
            "count": 3,
            "n": 100
          }
        ]
      }
    }
  },
  "single_source": "PRIMARY_VERIFIED",
  "population": {
    "result": "TYPED_MATCH",
    "source": "plant",
    "span": "On-treatment stroke hazard ratio 0.80 (0.70-0.90)"
  },
  "dose": {
    "result": "TYPED_MATCH",
    "source": "low-dose-plant",
    "span": "stroke [trial end]: Hazard Ratio .80 (.70, .90)"
  },
  "anti_circularity": [],
  "identity_without_basis": {
    "pmids": [],
    "ncts": [],
    "basis": []
  },
  "timepoint": {
    "result": "TYPED_MATCH",
    "source": "plant",
    "span": "At 5 years stroke hazard ratio 0.80 (0.70-0.90)"
  },
  "definition": {
    "result": "TYPED_MATCH",
    "source": "plant",
    "span": "stroke or systemic embolism or death hazard ratio 0.80 (0.70-0.90)"
  },
  "confidence_level": null
}

```

| Plant | Pre-fix finding | Post-fix result and negative control |
|---|---|---|
| NUMBER with 3.55 %/year | Base `aact_lane` emitted count 3/N=100 | RATE, never events; literal 3 patients remains COUNT |
| Comparator-only | Existing `g1_countable` returned [] | SECONDARY_ONLY; primary-source control can verify; original anti-circularity preserved |
| One source / duplicate source | Base `verify_typed` returned PRIMARY_VERIFIED for one matching text | SINGLE_SOURCE for one or duplicate IDs; two independently sourced complete matching tuples verify |
| ITT versus on-treatment | Base `typed_match_text` returned TYPED_MATCH | POPULATION_DIFFERS / CONFLICT; identical ITT tuples match |
| Low dose in standard slot | Base `typed_match_registry` returned TYPED_MATCH without checking arm binding | Low-dose refusal; dabigatran 150 mg and high-dose edoxaban controls pass |
| Label without basis | Base `resolve_unit` returned empty PMIDs/NCTs/basis | UNRESOLVED; unique acronym passes, ambiguous acronym refuses; existing refusal preserved |
| Follow-up mismatch/unknown | Base text matcher matched a 5-year result for a 32-month request | TIMEPOINT_DIFFERS; equal known windows match; two unknown windows cannot verify |
| Composite/definition substitution | Base keyword-window matching accepted stroke/SE/death for stroke | Added-component/ICH/nonmajor/TIMI refusals; exact stroke/SE and major-only categories pass |
| CI confidence level | Base text regex refused the particular 99% textual plant (null), preserved | Typed CI_PERCENT_DIFFERS independently catches otherwise identical 95% versus 99% tuples |
| Numeric conflict and rounding | Base matching is a numeric locator, not a complete two-source context gate | Numeric disagreements conflict; 0.707 and 0.71 agree at printed precision; 0.65 and 0.66 do not |

### Verification performed

PowerShell environment: `$env:PYTHONIOENCODING='utf-8'; $env:PYTHONDONTWRITEBYTECODE='1'`.

- Full local acquisition: `python scripts/g1_noac_build.py --aact F:/AACT-storage/AACT/2026-08-30` ? PASS. Read-only streaming scan over studies, study_references, id_information, outcomes, result_groups, outcome_measurements, outcome_counts, outcome_analyses, outcome_analysis_groups, milestones.
- Final replay/census: `python scripts/g1_noac_build.py --reuse-index --census` ? PASS; explicit replay uses the captured AACT row bytes/locators, not a claim that a new snapshot was fetched.
- Required lane test: `python -m pytest -q -p no:cacheprovider tests/test_g1_noac.py` ? **15 passed** (final run: 0.86 seconds).
- Four bounded test passes during implementation, all green (first 14, final three 15). Final source review corrected the regulator header's text-digest label and ensured the RE-LY rate disagreement participates in the row route.
- Serialized JSON and Markdown deterministic replay ? PASS. A preliminary direct Python-object comparison differed because the pooling dataclass has tuples while JSON reload yields lists; serialization-normalized equality passes without changing the calculations.
- Input digest recheck, UTF-8 without BOM, and empty tracked git diff ? PASS.
- Source-level second pass: comparator totals/methods/censoring, AACT PMID?NCT joins and snapshot labels, FDA cells and hash semantics, CI confidence levels, and non-served proposal status reviewed. No release or certification claim.

## CENSUS

This is a **topic-specific** lane: all topic files are parsed and dispatched by scope; the four-trial AACT rules run only on the NOAC topic. Other topics are explicitly out of scope, not claimed clean. Denominators below identify exactly what was examined. `rates_refused_as_events` includes classified rows the old reader already skipped; `base_number_as_count_changed` isolates actual old-predicate acceptances that the new unit rule changes.

Exact census JSON printed by the final build:

```json

{
  "topic_scope": {
    "n": 1,
    "N": 38,
    "n_of_N": "1 of 38",
    "items": [
      "noac-vs-warfarin-af-stroke"
    ]
  },
  "out_of_scope_topics": [
    "antibiotics-vs-appendectomy-appendicitis",
    "azithromycin-copd-exacerbation",
    "balanced-crystalloids-vs-saline-mortality",
    "colchicine-postop-af",
    "colchicine-recurrent-pericarditis",
    "colchicine-secondary-cv-prevention",
    "corticosteroids-cap-mortality",
    "corticosteroids-covid19-mortality",
    "dapagliflozin-hfpef-hosp",
    "denosumab-vertebral-fracture",
    "doac-vte-recurrence",
    "dpp4-mace-t2d",
    "empagliflozin-hfpef-hosp",
    "esketamine-trd-madrs",
    "finerenone-ckd-t2d-renal",
    "glp1-ra-mace-t2d",
    "hfnc-vs-conventional-o2-reintubation",
    "iv-iron-hfref-hosp",
    "melatonin-primary-insomnia-sol",
    "metformin-pcos-ovulation",
    "omega3-cardiovascular-events",
    "pcsk9-mace",
    "probiotics-aad-prevention",
    "prone-positioning-ards-mortality",
    "sacubitril-valsartan-hfref",
    "semaglutide-obesity-mace",
    "semaglutide-obesity-weight",
    "sglt2-ckd-progression",
    "sglt2-hfref-hosp-cvdeath",
    "sglt2-primary-prevention-hf",
    "spironolactone-hfref-mortality",
    "statins-primary-prevention-elderly",
    "ticagrelor-vs-clopidogrel-acs",
    "tocilizumab-covid19-mortality",
    "tranexamic-acid-pph",
    "vitamin-d-acute-respiratory-infection",
    "zinc-common-cold-duration"
  ],
  "k_matched": {
    "n": 4,
    "N": 4,
    "n_of_N": "4 of 4",
    "items": [
      "ARISTOTLE",
      "ENGAGE AF-TIMI 48",
      "RE-LY",
      "ROCKET AF"
    ]
  },
  "routes": {
    "TWO_SOURCE_VERIFIED": {
      "n": 0,
      "N": 8,
      "n_of_N": "0 of 8",
      "items": []
    },
    "SINGLE_SOURCE": {
      "n": 4,
      "N": 8,
      "n_of_N": "4 of 8",
      "items": [
        "ARISTOTLE/major_bleeding",
        "ARISTOTLE/stroke_se",
        "ENGAGE AF-TIMI 48/major_bleeding",
        "ROCKET AF/major_bleeding"
      ]
    },
    "CONFLICT": {
      "n": 4,
      "N": 8,
      "n_of_N": "4 of 8",
      "items": [
        "ENGAGE AF-TIMI 48/stroke_se",
        "RE-LY/major_bleeding",
        "RE-LY/stroke_se",
        "ROCKET AF/stroke_se"
      ]
    },
    "NOT_HELD": {
      "n": 0,
      "N": 8,
      "n_of_N": "0 of 8",
      "items": []
    },
    "SECONDARY_ONLY": {
      "n": 0,
      "N": 8,
      "n_of_N": "0 of 8",
      "items": []
    }
  },
  "served_comparisons": {
    "MATCH": {
      "n": 5,
      "N": 8,
      "n_of_N": "5 of 8",
      "items": [
        "ARISTOTLE/major_bleeding",
        "ARISTOTLE/stroke_se",
        "ENGAGE AF-TIMI 48/major_bleeding",
        "ENGAGE AF-TIMI 48/stroke_se",
        "RE-LY/stroke_se"
      ]
    },
    "DIFFERS": {
      "n": 1,
      "N": 8,
      "n_of_N": "1 of 8",
      "items": [
        "ROCKET AF/stroke_se"
      ]
    },
    "NOT_SERVED": {
      "n": 2,
      "N": 8,
      "n_of_N": "2 of 8",
      "items": [
        "RE-LY/major_bleeding",
        "ROCKET AF/major_bleeding"
      ]
    }
  },
  "rates_refused_as_events": {
    "n": 67,
    "N": 172,
    "n_of_N": "67 of 172",
    "items": [
      "1927245345",
      "1927245346",
      "1927245347",
      "1927245348",
      "1927245349",
      "1927245350",
      "1927245351",
      "1927245352",
      "1927245353",
      "1927245354",
      "1927245355",
      "1927245356",
      "1927245357",
      "1927245358",
      "1927245359",
      "1927245360",
      "1927245361",
      "1927245362",
      "1927245363",
      "1927245364",
      "1927245365",
      "1929132624",
      "1929132625",
      "1929132628",
      "1929132629",
      "1929132632",
      "1929132633",
      "1929132634",
      "1929132635",
      "1929132636",
      "1929132637",
      "1929132638",
      "1929132639",
      "1929132640",
      "1929132641",
      "1929132642",
      "1929132643",
      "1929132644",
      "1929132645",
      "1929132646",
      "1929132647",
      "1929132648",
      "1929132649",
      "1929132650",
      "1929132651",
      "1929132652",
      "1929132653",
      "1929132654",
      "1929132655",
      "1929132656",
      "1929132657",
      "1929132660",
      "1929132661",
      "1929132674",
      "1929132675",
      "1929132678",
      "1929132679",
      "1929132680",
      "1929132681",
      "1929132682",
      "1929132683",
      "1929132684",
      "1929132685",
      "1929132686",
      "1929132687",
      "1929132690",
      "1929132691"
    ]
  },
  "base_number_as_count_changed": {
    "n": 23,
    "N": 82,
    "n_of_N": "23 of 82",
    "items": [
      "1927245345",
      "1927245346",
      "1927245347",
      "1927245348",
      "1927245349",
      "1927245350",
      "1927245351",
      "1927245352",
      "1927245353",
      "1929132624",
      "1929132625",
      "1929132628",
      "1929132629",
      "1929132632",
      "1929132633",
      "1929132660",
      "1929132661",
      "1929132674",
      "1929132675",
      "1929132678",
      "1929132679",
      "1929132690",
      "1929132691"
    ]
  },
  "nonstandard_arms_refused": {
    "n": 15,
    "N": 103,
    "n_of_N": "15 of 103",
    "items": [
      "258397029/837722670",
      "258397030/837722673",
      "258397031/837722676",
      "258397032/837722679",
      "258397033/837722682",
      "258397034/837722685",
      "258761852/838936670",
      "258761853/838936673",
      "258761854/838936676",
      "258761855/838936679",
      "258761856/838936682",
      "258761857/838936685",
      "258761858/838936688",
      "258761859/838936691",
      "258761860/838936694"
    ]
  },
  "numeric_agreement_not_full_verification": {
    "n": 6,
    "N": 8,
    "n_of_N": "6 of 8",
    "items": [
      "ARISTOTLE/major_bleeding",
      "ARISTOTLE/stroke_se",
      "ENGAGE AF-TIMI 48/major_bleeding",
      "ENGAGE AF-TIMI 48/stroke_se",
      "RE-LY/major_bleeding",
      "ROCKET AF/stroke_se"
    ]
  },
  "population_refusals": {
    "n": 16,
    "N": 19,
    "n_of_N": "16 of 19",
    "items": [
      "ARISTOTLE/major_bleeding:F009/F033",
      "ARISTOTLE/stroke_se:F006/F032",
      "ENGAGE AF-TIMI 48/major_bleeding:F021/F036",
      "ENGAGE AF-TIMI 48/stroke_se:F011/F035",
      "ENGAGE AF-TIMI 48/stroke_se:F013/F034",
      "ENGAGE AF-TIMI 48/stroke_se:F013/F035",
      "ENGAGE AF-TIMI 48/stroke_se:F015/F034",
      "ENGAGE AF-TIMI 48/stroke_se:F015/F035",
      "ENGAGE AF-TIMI 48/stroke_se:F017/F034",
      "ENGAGE AF-TIMI 48/stroke_se:F017/F035",
      "ENGAGE AF-TIMI 48/stroke_se:F019/F034",
      "RE-LY/major_bleeding:F004/F037",
      "RE-LY/stroke_se:F002/F026",
      "ROCKET AF/stroke_se:F023/F029",
      "ROCKET AF/stroke_se:F025/F028",
      "ROCKET AF/stroke_se:F025/F029"
    ]
  },
  "timepoint_refusals": {
    "n": 19,
    "N": 19,
    "n_of_N": "19 of 19",
    "items": [
      "ARISTOTLE/major_bleeding:F009/F033",
      "ARISTOTLE/stroke_se:F006/F032",
      "ENGAGE AF-TIMI 48/major_bleeding:F021/F036",
      "ENGAGE AF-TIMI 48/stroke_se:F011/F034",
      "ENGAGE AF-TIMI 48/stroke_se:F011/F035",
      "ENGAGE AF-TIMI 48/stroke_se:F013/F034",
      "ENGAGE AF-TIMI 48/stroke_se:F013/F035",
      "ENGAGE AF-TIMI 48/stroke_se:F015/F034",
      "ENGAGE AF-TIMI 48/stroke_se:F015/F035",
      "ENGAGE AF-TIMI 48/stroke_se:F017/F034",
      "ENGAGE AF-TIMI 48/stroke_se:F017/F035",
      "ENGAGE AF-TIMI 48/stroke_se:F019/F034",
      "ENGAGE AF-TIMI 48/stroke_se:F019/F035",
      "RE-LY/major_bleeding:F004/F037",
      "RE-LY/stroke_se:F002/F026",
      "ROCKET AF/stroke_se:F023/F028",
      "ROCKET AF/stroke_se:F023/F029",
      "ROCKET AF/stroke_se:F025/F028",
      "ROCKET AF/stroke_se:F025/F029"
    ]
  },
  "definition_refusals": {
    "n": 3,
    "N": 19,
    "n_of_N": "3 of 19",
    "items": [
      "ARISTOTLE/major_bleeding:F009/F033",
      "ENGAGE AF-TIMI 48/major_bleeding:F021/F036",
      "RE-LY/major_bleeding:F004/F037"
    ]
  },
  "ci_percent_refusals": {
    "n": 2,
    "N": 19,
    "n_of_N": "2 of 19",
    "items": [
      "ENGAGE AF-TIMI 48/stroke_se:F019/F034",
      "ENGAGE AF-TIMI 48/stroke_se:F019/F035"
    ]
  },
  "measure_refusals": {
    "n": 1,
    "N": 19,
    "n_of_N": "1 of 19",
    "items": [
      "RE-LY/stroke_se:F002/F026"
    ]
  },
  "outcome_binding_refusals": {
    "n": 138,
    "N": 172,
    "n_of_N": "138 of 172",
    "items": [
      "1927245348",
      "1927245349",
      "1927245350",
      "1927245351",
      "1927245352",
      "1927245353",
      "1927245357",
      "1927245358",
      "1927245359",
      "1927245360",
      "1927245361",
      "1927245362",
      "1927245363",
      "1927245364",
      "1927245365",
      "1927245366",
      "1927245367",
      "1927245368",
      "1929132618",
      "1929132619",
      "1929132620",
      "1929132621",
      "1929132622",
      "1929132623",
      "1929132630",
      "1929132631",
      "1929132632",
      "1929132633",
      "1929132634",
      "1929132635",
      "1929132636",
      "1929132637",
      "1929132638",
      "1929132639",
      "1929132640",
      "1929132641",
      "1929132642",
      "1929132643",
      "1929132644",
      "1929132645",
      "1929132646",
      "1929132647",
      "1929132648",
      "1929132649",
      "1929132650",
      "1929132651",
      "1929132652",
      "1929132653",
      "1929132654",
      "1929132655",
      "1929132656",
      "1929132657",
      "1929132658",
      "1929132659",
      "1929132660",
      "1929132661",
      "1929132662",
      "1929132663",
      "1929132664",
      "1929132665",
      "1929132666",
      "1929132667",
      "1929132668",
      "1929132669",
      "1929132670",
      "1929132671",
      "1929132672",
      "1929132673",
      "1929132674",
      "1929132675",
      "1929132676",
      "1929132677",
      "1929132678",
      "1929132679",
      "1929132680",
      "1929132681",
      "1929132682",
      "1929132683",
      "1929132684",
      "1929132685",
      "1929132686",
      "1929132687",
      "1929132688",
      "1929132689",
      "1929132690",
      "1929132691",
      "1929975187",
      "1929975188",
      "1929975189",
      "1929975190",
      "1929975191",
      "1929975192",
      "1929975193",
      "1929975194",
      "1929975195",
      "1929975199",
      "1929975200",
      "1929975201",
      "1929975202",
      "1929975203",
      "1929975204",
      "1929975205",
      "1929975206",
      "1929975207",
      "1929975208",
      "1929975209",
      "1929975210",
      "1929975211",
      "1929975212",
      "1929975213",
      "1929975214",
      "1929975215",
      "1929975216",
      "1929975217",
      "1929975218",
      "1929975219",
      "1929975220",
      "1929975221",
      "1929975222",
      "1929975223",
      "1929975224",
      "1929975225",
      "1931022244",
      "1931022245",
      "1931022246",
      "1931022247",
      "1931022248",
      "1931022249",
      "1931022250",
      "1931022251",
      "1931022252",
      "1931022253",
      "1931022254",
      "1931022255",
      "1931022256",
      "1931022257",
      "1931022258",
      "1931022259"
    ]
  },
  "comparator_only_excluded_from_primary_verification": {
    "n": 2,
    "N": 24,
    "n_of_N": "2 of 24",
    "items": [
      "COMBINE_AF/major_bleeding",
      "COMBINE_AF/stroke_se"
    ]
  },
  "reproduction": [
    {
      "outcome": "stroke_se",
      "population": "ITT",
      "tier": "TWO_SOURCE_VERIFIED_ONLY",
      "state": "INCOMPLETE",
      "k": 0,
      "N": 4,
      "missing": [
        "RE-LY",
        "ROCKET AF",
        "ARISTOTLE",
        "ENGAGE AF-TIMI 48"
      ],
      "verified_subtotal": {
        "events_t": 0,
        "n_t": 0,
        "events_c": 0,
        "n_c": 0
      },
      "target": {
        "events_t": 883,
        "n_t": 29312,
        "events_c": 1080,
        "n_c": 29229
      },
      "unexplained_target_minus_verified_subtotal": {
        "events_t": 883,
        "n_t": 29312,
        "events_c": 1080,
        "n_c": 29229
      },
      "residual_interpretation": "An incomplete subtotal is not a four-trial reproduction residual."
    },
    {
      "outcome": "stroke_se",
      "population": "ON_TREATMENT",
      "tier": "TWO_SOURCE_VERIFIED_ONLY",
      "state": "INCOMPLETE",
      "k": 0,
      "N": 4,
      "missing": [
        "RE-LY",
        "ROCKET AF",
        "ARISTOTLE",
        "ENGAGE AF-TIMI 48"
      ],
      "verified_subtotal": {
        "events_t": 0,
        "n_t": 0,
        "events_c": 0,
        "n_c": 0
      },
      "target": {
        "events_t": 883,
        "n_t": 29312,
        "events_c": 1080,
        "n_c": 29229
      },
      "unexplained_target_minus_verified_subtotal": {
        "events_t": 883,
        "n_t": 29312,
        "events_c": 1080,
        "n_c": 29229
      },
      "residual_interpretation": "An incomplete subtotal is not a four-trial reproduction residual."
    },
    {
      "outcome": "major_bleeding",
      "population": "ITT",
      "tier": "TWO_SOURCE_VERIFIED_ONLY",
      "state": "INCOMPLETE",
      "k": 0,
      "N": 4,
      "missing": [
        "RE-LY",
        "ROCKET AF",
        "ARISTOTLE",
        "ENGAGE AF-TIMI 48"
      ],
      "verified_subtotal": {
        "events_t": 0,
        "n_t": 0,
        "events_c": 0,
        "n_c": 0
      },
      "target": {
        "events_t": 1479,
        "n_t": 29270,
        "events_c": 1733,
        "n_c": 29187
      },
      "unexplained_target_minus_verified_subtotal": {
        "events_t": 1479,
        "n_t": 29270,
        "events_c": 1733,
        "n_c": 29187
      },
      "residual_interpretation": "An incomplete subtotal is not a four-trial reproduction residual."
    },
    {
      "outcome": "major_bleeding",
      "population": "ON_TREATMENT",
      "tier": "TWO_SOURCE_VERIFIED_ONLY",
      "state": "INCOMPLETE",
      "k": 0,
      "N": 4,
      "missing": [
        "RE-LY",
        "ROCKET AF",
        "ARISTOTLE",
        "ENGAGE AF-TIMI 48"
      ],
      "verified_subtotal": {
        "events_t": 0,
        "n_t": 0,
        "events_c": 0,
        "n_c": 0
      },
      "target": {
        "events_t": 1479,
        "n_t": 29270,
        "events_c": 1733,
        "n_c": 29187
      },
      "unexplained_target_minus_verified_subtotal": {
        "events_t": 1479,
        "n_t": 29270,
        "events_c": 1733,
        "n_c": 29187
      },
      "residual_interpretation": "An incomplete subtotal is not a four-trial reproduction residual."
    },
    {
      "outcome": "stroke_se",
      "tier": "SINGLE_SOURCE_DIAGNOSTIC_NOT_VERIFIED",
      "state": "INCOMPLETE",
      "missing": [
        "RE-LY",
        "ARISTOTLE"
      ],
      "combinations": []
    },
    {
      "outcome": "major_bleeding",
      "tier": "SINGLE_SOURCE_DIAGNOSTIC_NOT_VERIFIED",
      "state": "DIAGNOSTIC_ONLY",
      "missing": [],
      "combinations": [
        {
          "facts": [
            "F038",
            "F040",
            "F007",
            "F020"
          ],
          "total": {
            "events_t": 1539,
            "n_t": 29287,
            "events_c": 1793,
            "n_c": 29211
          },
          "target_minus_total": {
            "events_t": -60,
            "n_t": -17,
            "events_c": -60,
            "n_c": -24
          },
          "exact": false,
          "populations": [
            "UNKNOWN",
            "ON_TREATMENT",
            "ON_TREATMENT",
            "ON_TREATMENT"
          ]
        }
      ]
    },
    {
      "outcome": "randomized_standard_n",
      "state": "NOT_VERIFIED",
      "target": 29362,
      "started_diagnostic_sum": 29342,
      "target_minus_started": 20,
      "reason": "STARTED_IS_NOT_PROOF_OF_RANDOMIZED;TWO_SOURCE_N_NOT_HELD"
    }
  ]
}

```

### Primary-source findings and interpretation

**Identity:** all comparator labels map to our inventory. ROCKET AF is anchored by the following held AACT row, corroborated by the abstract's explicit ?ROCKET AF ClinicalTrials.gov number, NCT00403767.? The current held record *does* self-name ROCKET; the older k-gap status assertion that it never self-names is stale for these held bytes.

```json

{
  "id": "430628161",
  "nct_id": "NCT00403767",
  "pmid": "21830957",
  "reference_type": "DERIVED",
  "citation": "Patel MR, Mahaffey KW, Garg J, Pan G, Singer DE, Hacke W, Breithardt G, Halperin JL, Hankey GJ, Piccini JP, Becker RC, Nessel CC, Paolini JF, Berkowitz SD, Fox KA, Califf RM; ROCKET AF Investigators. Rivaroxaban versus warfarin in nonvalvular atrial fibrillation. N Engl J Med. 2011 Sep 8;365(10):883-91. doi: 10.1056/NEJMoa1009638. Epub 2011 Aug 10.",
  "_source": {
    "table": "study_references",
    "line": 471495,
    "row_sha256": "b47a787cb88e50946f2b319898e418b4ed8669f0b6075b5b37fa118d96b1370a",
    "snapshot": "2026-08-30"
  }
}

```

**Comparator evidence**, parsed from its own XML (the source SHA-256 and all exact method/dose spans are in g1_noac.json):


> stroke/systemic embolism (883/29312 [3.01%] vs 1080/29229 [3.69%]; HR 0.81, 95% CI 0.74–0.89)


> major bleeding (1479/29270 [5.05%] vs 1733/29187 [5.94%]; HR 0.86, 95% CI 0.74–1.01)


> [comparator paragraph omitted in this committed copy: NIHMS author manuscript; see G1_NOAC.md sentence excerpts]


> [comparator paragraph omitted in this committed copy: NIHMS author manuscript; see G1_NOAC.md sentence excerpts]


> [comparator paragraph omitted in this committed copy: NIHMS author manuscript; see G1_NOAC.md sentence excerpts]


> [comparator paragraph omitted in this committed copy: NIHMS author manuscript; see G1_NOAC.md sentence excerpts]


The comparator's per-trial status remains NOT_REPORTED_BY_COMPARATOR. Its paragraphs identify the four trials and regimens but do not supply per-trial numerical outcome tuples; trial-specific plots are not transcribed as source data.

- **RE-LY efficacy:** abstract RR 0.66 (0.53?0.82), versus AACT Cox HR 0.65 (0.52?0.81). Both are quoted in the artifact; the measure and numbers differ. Neither is silently substituted.
- **RE-LY bleeding:** FDA supplies HR 0.93 (0.81?1.07), matching the AACT analysis numerically. This corrects the *candidate's* legacy RR label: the FDA table says Hazard Ratio. However, full population/follow-up/ISTH equivalence is not held in the short FDA excerpt. Abstract annualized rates 3.11 versus 3.36 differ from AACT 3.55 versus 3.81; those typed rates force an overall CONFLICT while the effect-only route remains SINGLE_SOURCE. FDA counts 399/6076 versus 421/6022 are a separate single-source tuple, not reconstructed from rates.
- **ROCKET efficacy:** AACT supplies per-protocol/on-treatment and safety/on-treatment analyses, not the abstract ITT tuple. The abstract ITT HR 0.88 (0.74?1.03) matches the served numbers. Served `analysis_set_literal=ITT` contradicts served `analysis_set=per-protocol`, so the served row is DIFFERS on population metadata. This is not a claim that its numeric HR is wrong.
- **ROCKET bleeding:** FDA supplies standalone major bleeding HR 1.04 (0.90?1.20), 395/7111 versus 386/7125, on treatment plus two days. AACT/abstract provide the broader major-or-nonmajor composite HR 1.03 (0.96?1.11); it is refused as a verifier of standalone major bleeding. The new primary support is SINGLE_SOURCE, not two-source completion.
- **ARISTOTLE:** AACT and abstract efficacy HR 0.79 (0.66?0.95), and bleeding HR 0.69 (0.60?0.80), agree numerically. Abstract population/window/ISTH detail is insufficient for full contextual verification. AACT provides bleeding counts 327/9088 versus 462/9052. Its efficacy count endpoint lists stroke/SE components separately; these are not blindly added to create a composite event count.
- **ENGAGE:** AACT retains on-treatment, modified ITT, PP and ITT alternatives. Its ITT HR 0.87 has a **99%** CI 0.709?1.068; the abstract's ITT HR 0.87 has a **97.5%** CI 0.73?1.04. The served 95% CI is correctly recovered from the latter by the declared conversion (approximately 0.745271?1.015604), not equated to the raw AACT bounds. Bleeding HR 0.8 (0.707?0.914) agrees numerically with abstract 0.80 (0.71?0.91); AACT explicitly describes modified ISTH criteria, whereas the abstract does not establish the full definition/window.

**Strong reproduction:** neither endpoint has a complete four-trial two-source count/N set in either candidate population. The verified-only table is INCOMPLETE, not a negative finding about the comparator's arithmetic. Even unrestricted single-source efficacy combinations cannot be completed: RE-LY composite counts and an unambiguous ARISTOTLE composite count are not held in the inspected representations. ROCKET's abstract ITT event numerators are kept as NUMERATORS_ONLY, without inventing arm Ns.

The separate, unverified bleeding-count diagnostic sums to 1539/29287 versus 1793/29211, rather than comparator 1479/29270 versus 1733/29187. Exact comparator-minus-diagnostic residuals are ?60/?17 and ?60/?24. The combination includes an unknown RE-LY analysis window and full-trial source data; these residuals cannot prove how the comparator extracted its 32-month-censored IPD. The standard-arm STARTED sum is 29342, 20 short of printed randomized N=29362; STARTED is not proof of randomized N (ROCKET's flow counts are treated participants), and 20 is not used to manufacture a missing trial value.


**Result versus comparator:** served efficacy estimate 0.8069 (95% CI 0.6611?0.985) rounds to comparator 0.81, so the point agrees at printed precision. Its label is `pooled first-event ratio (3 HR + 1 RR)`. The harness uses trial-level inverse variance, PM tau?, floored HKSJ t intervals; COMBINE AF uses IPD stratified Cox random effects and 32-month censoring. The interval difference is not described as a reproduction failure or merely a rounding issue.

Served bleeding remains HARMS_INCOMPLETE (two extracted rows, no served pooled estimate). The non-served **PROPOSED** four-trial source-anchored HR calculation gives **0.854363 (0.643887?1.133642)**, k=4, using `harness.synth.pool` and its `synth.pool:PM-tau2+HKSJ-t(k-1)+floor-max(1,Q/(k-1)):v1` token. Comparator bleeding HR is 0.86 (0.74?1.01); the proposal rounds to 0.85, not 0.86. These are different analysis methods/windows; the proposal is not a two-source-verified pool and is not admitted or served.


## HOOKS

Exact integration points (descriptive only; no shared code edited):

1. `scripts/k_gap_bulk_acquire.py:114`, `aact_lane`; the outcome projection at lines 119?124 drops units, population, definition, CI confidence and arm linkage. Retain them before applying `measurement_kind` and `aact_facts`. At **line 130**, `int(float(r['param_value_num']))` turns NUMBER rates into counts. Replace that predicate in an integrator change; do not use a post-hoc denominator fix. Preserve category-bound major bleeding rather than dropping all categorized rows.
2. `harness/secondary_meta.py:556`, `typed_match_registry`; its `named` outcome selection at **562** is a keyword match, and the subsequent HR branch does not bind dose, population, confidence level, or analysis groups. It also recognizes ?hazard ratio? but misses AACT's ?Cox Proportional Hazard? label. An integrator should use explicit parameter typing and group links before comparison, with complete contexts supplied to `compare_facts`.
3. `harness/secondary_meta.py:532`, `typed_match_text`; its numerical triple plus nearby keyword must not establish trial/outcome/population/dose/timepoint identity. Use the bounded primary extraction and `compare_facts` as an additional typed gate.
4. `harness/secondary_meta.py:584`, `verify_typed`; **594** upgrades on the first match. Keep its existing general semantics unless deliberately changed, but place this lane's named TWO_SOURCE_RULE/`route` before any claim of G1 two-source verification. Numerical corroboration and full contextual verification are separate outputs.
5. `harness/secondary_meta.py:599`, `g1_countable`: preserve comparator-ID anti-circularity. The new audit does not feed comparator totals into the primary sources. `same_value` at **334** is numerical equality, not a replacement for the new semantic gate.
6. `scripts/k_gap_table.py:199`, `resolve_unit`, and the identity fallback block around **780?800** (particularly `named` at **793**): integrate the exact self-naming PMID?NCT AACT reference chain from `resolve_identity` before leaving ROCKET unresolved. Do not loosen all acronym matching or rely on model guesses. The evidence row is `study_references` id 430628161, physical line 471495 in snapshot 2026-08-30.
7. `harness/synth.py:277`, `pool`: canonical engine used for the PROPOSED calculation. Do not substitute `harness/secondary_meta.py:189` `pool`, whose HK path lacks the served engine's floor. Wiring an approved proposal into serving is outside this lane.
8. `docs/reviews/noac-vs-warfarin-af-stroke/review.json`, efficacy ROCKET trial: fix the conflicting population fields through its generating extractor/compatibility path, not by patching generated JSON. Bleeding RE-LY candidate's RR label must be reconciled against the FDA HR column. Both are integration findings; no served data changed here.

## OPEN

- Full G1 is **not established**: identity is 4/4, but complete primary tuples do not meet the specified two-source rule; the comparator does not print per-trial numerical text rows. No certification or submission-state change is claimed.
- Obtain independent primary spans for missing population, follow-up, standalone ISTH definitions and arm counts; adjudicate RE-LY source-version/rate differences and ENGAGE confidence-level/window alternatives. Numeric agreement alone is deliberately not promoted.
- Reproducing 32-month IPD totals requires compatible per-trial source counts at that censoring window (or reproducible accessible IPD). Current full-trial/safety excerpts cannot supply that. Missing Ns are never back-solved from comparator totals.
- FDA excerpts remedy the absence of an anchored numerical major-bleeding effect for RE-LY and ROCKET, but do not complete full two-source verification. Underlying full regulator text/PDF was not silently assumed accessible; only the held excerpts and their header-described text digests were used.
- The AACT index is explicitly restricted to the four resolved inventory trials. All 38 topic files were considered for scope; there is no claim that the rules were clinically validated on the other 37 topics.
- Shared fixes and any approval to serve the proposal belong to the integrator. This lane stops with this report; no git state, served output, or publication status was changed.
