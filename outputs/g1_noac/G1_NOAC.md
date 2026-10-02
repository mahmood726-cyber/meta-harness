# G1 NOAC primary-source audit

TWO_SOURCE_VERIFIED requires the same typed tuple at printed precision in two independent primary sources: trial, outcome, kind, measure and CI level stated and equal in both, no axis stated differently by the two (population, dose, timepoint, definition), and every value equal; an axis stated by only one source is listed as silent, never assumed to agree. Tuples that differ on a stated axis are different analyses (INCOMPARABLE), not a conflict. One primary is SINGLE_SOURCE; same tuple with different values is CONFLICT (both quoted, never averaged); comparator-only is SECONDARY_ONLY.

Identity matching is separate from verified value matching. Nothing here changes served results.

| Trial/outcome | Route | Served estimate comparison |
|---|---|---|
| RE-LY/stroke_se | SINGLE_SOURCE | MATCH |
| RE-LY/major_bleeding | CONFLICT | NOT_SERVED |
| ROCKET AF/stroke_se | TWO_SOURCE_VERIFIED | DIFFERS |
| ROCKET AF/major_bleeding | SINGLE_SOURCE | NOT_SERVED |
| ARISTOTLE/stroke_se | TWO_SOURCE_VERIFIED | MATCH |
| ARISTOTLE/major_bleeding | TWO_SOURCE_VERIFIED | MATCH |
| ENGAGE AF-TIMI 48/stroke_se | TWO_SOURCE_VERIFIED | MATCH |
| ENGAGE AF-TIMI 48/major_bleeding | TWO_SOURCE_VERIFIED | MATCH |

## Comparator evidence

> stroke/systemic embolism (883/29312 [3.01%] vs 1080/29229 [3.69%]; HR 0.81, 95% CI 0.74–0.89)

> major bleeding (1479/29270 [5.05%] vs 1733/29187 [5.94%]; HR 0.86, 95% CI 0.74–1.01)

> For these analyses, a standard-dose DOAC treatment strategy was defined as dabigatran 150mg twice daily (RE-LY), rivaroxaban 20mg (or 15mg if dose reduction criteria were met) once daily (ROCKET AF), apixaban 5mg (or 2.5mg if dose reduction criteria were met) twice daily (ARISTOTLE), or edoxaban 60mg (or 30mg if dose reduction criteria were met) once daily (ENGAGE AF-TIMI 48). [paragraph sha256 cbbfd1e541b7]

> A total of 71,683 patients were included in these analyses (Supplement Figure 1; n=29,362 randomized to standard-dose DOAC, n=13,049 randomized to lower-dose DOAC, and n=29,272 randomized to warfarin). [paragraph sha256 f437cb3b4bbd]

> A total of 71,683 patients were included (29,362 on standard-dose DOAC, 13,049 on lower-dose DOAC, 29,272 on warfarin). [paragraph sha256 38f589a21c67]

> Cox models were stratified by trial allowing random effects to account for cross-trial heterogeneity. [paragraph sha256 801b4124ae41]

> Efficacy outcomes were assessed using an intention-to-treat population, while safety outcomes and net clinical benefits were assessed in the safety population as defined by the individual trials. [paragraph sha256 dea0fe60003a]

> To account for differences in follow-up duration between trials, patients were censored at 32-months, which was the point at which < 10% of patients remained at risk across all studies (Supplement Table 2). [paragraph sha256 dea0fe60003a]

> The primary safety outcome was major bleeding as defined by the International Society on Thrombosis and Haemostasis (ISTH).13 Secondary safety outcomes included fatal bleeding, major or clinically relevant non-major bleeding, any bleeding (including fatal, major, clinically relevant non-major, or minor bleeding), intracranial bleeding, and gastrointestinal bleeding (adjudicated major bleeding events determined to be from gastrointestinal bleeding events only). [paragraph sha256 f4c91a7a9d1e]

## Source tuples

Full AACT records, row hashes, excerpts and abstract spans are in g1_noac.json.

| Fact | NCT / outcome | Source | Kind / population / definition | Values |
|---|---|---|---|---|
| F001 | NCT00262600 / stroke_se | AACT | RATE / ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"t": "1.11", "c": "1.71"} |
| F002 | NCT00262600 / stroke_se | AACT | EFFECT / ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.65", "lower": "0.52", "upper": "0.81"} |
| F003 | NCT00262600 / major_bleeding | AACT | RATE / ITT / UNKNOWN | {"t": "3.55", "c": "3.81"} |
| F004 | NCT00262600 / major_bleeding | AACT | EFFECT / ITT / UNKNOWN | {"effect": "0.93", "lower": "0.81", "upper": "1.07"} |
| F005 | NCT00412984 / stroke_se | AACT | RATE / ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"t": "1.27", "c": "1.60"} |
| F006 | NCT00412984 / stroke_se | AACT | EFFECT / ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.79", "lower": "0.66", "upper": "0.95"} |
| F007 | NCT00412984 / major_bleeding | AACT | COUNTS / ON_TREATMENT / ISTH | {"events_t": 327, "n_t": 9088, "events_c": 462, "n_c": 9052} |
| F008 | NCT00412984 / major_bleeding | AACT | RATE / ON_TREATMENT / ISTH | {"t": "2.13", "c": "3.09"} |
| F009 | NCT00412984 / major_bleeding | AACT | EFFECT / ON_TREATMENT / ISTH | {"effect": "0.69", "lower": "0.6", "upper": "0.8"} |
| F010 | NCT00781391 / stroke_se | AACT | COUNTS / ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"events_t": 182, "n_t": 7012, "events_c": 232, "n_c": 7012} |
| F011 | NCT00781391 / stroke_se | AACT | EFFECT / ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.79", "lower": "0.632", "upper": "0.985"} |
| F012 | NCT00781391 / stroke_se | AACT | COUNTS / MODIFIED_ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"events_t": 292, "n_t": 7012, "events_c": 336, "n_c": 7012} |
| F013 | NCT00781391 / stroke_se | AACT | EFFECT / MODIFIED_ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.86", "lower": "0.719", "upper": "1.029"} |
| F014 | NCT00781391 / stroke_se | AACT | COUNTS / PER_PROTOCOL_ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"events_t": 182, "n_t": 6995, "events_c": 231, "n_c": 6996} |
| F015 | NCT00781391 / stroke_se | AACT | EFFECT / PER_PROTOCOL_ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.79", "lower": "0.634", "upper": "0.989"} |
| F016 | NCT00781391 / stroke_se | AACT | COUNTS / PER_PROTOCOL / STROKE_OR_SYSTEMIC_EMBOLISM | {"events_t": 292, "n_t": 6995, "events_c": 335, "n_c": 6993} |
| F017 | NCT00781391 / stroke_se | AACT | EFFECT / PER_PROTOCOL / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.86", "lower": "0.72", "upper": "1.032"} |
| F018 | NCT00781391 / stroke_se | AACT | COUNTS / ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"events_t": 296, "n_t": 7035, "events_c": 337, "n_c": 7036} |
| F019 | NCT00781391 / stroke_se | AACT | EFFECT / ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.87", "lower": "0.709", "upper": "1.068"} |
| F020 | NCT00781391 / major_bleeding | AACT | COUNTS / ON_TREATMENT / ISTH_MODIFIED | {"events_t": 418, "n_t": 7012, "events_c": 524, "n_c": 7012} |
| F021 | NCT00781391 / major_bleeding | AACT | EFFECT / ON_TREATMENT / ISTH_MODIFIED | {"effect": "0.8", "lower": "0.707", "upper": "0.914"} |
| F022 | NCT00403767 / stroke_se | AACT | COUNTS / PER_PROTOCOL_ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"events_t": 188, "n_t": 6958, "events_c": 241, "n_c": 7004} |
| F023 | NCT00403767 / stroke_se | AACT | EFFECT / PER_PROTOCOL_ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.79", "lower": "0.66", "upper": "0.96"} |
| F024 | NCT00403767 / stroke_se | AACT | COUNTS / ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"events_t": 189, "n_t": 7061, "events_c": 243, "n_c": 7082} |
| F025 | NCT00403767 / stroke_se | AACT | EFFECT / ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.79", "lower": "0.65", "upper": "0.95"} |
| F026 | NCT00262600 / stroke_se | PUBMED:19717844 | EFFECT / UNKNOWN / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.66", "lower": "0.53", "upper": "0.82"} |
| F027 | NCT00262600 / major_bleeding | PUBMED:19717844 | RATE / UNKNOWN / UNKNOWN | {"t": "3.11", "c": "3.36"} |
| F028 | NCT00403767 / stroke_se | PUBMED:21830957 | EFFECT / PER_PROTOCOL_ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.79", "lower": "0.66", "upper": "0.96"} |
| F029 | NCT00403767 / stroke_se | PUBMED:21830957 | EFFECT / ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.88", "lower": "0.74", "upper": "1.03"} |
| F030 | NCT00403767 / stroke_se | PUBMED:21830957 | NUMERATORS_ONLY / UNKNOWN / UNKNOWN | {"events_t": 188, "events_c": 241} |
| F031 | NCT00403767 / stroke_se | PUBMED:21830957 | NUMERATORS_ONLY / ITT / UNKNOWN | {"events_t": 269, "events_c": 306} |
| F032 | NCT00412984 / stroke_se | PUBMED:21870978 | EFFECT / UNKNOWN / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.79", "lower": "0.66", "upper": "0.95"} |
| F033 | NCT00412984 / major_bleeding | PUBMED:21870978 | EFFECT / UNKNOWN / UNKNOWN | {"effect": "0.69", "lower": "0.60", "upper": "0.80"} |
| F034 | NCT00781391 / stroke_se | PUBMED:24251359 | EFFECT / ON_TREATMENT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.79", "lower": "0.63", "upper": "0.99"} |
| F035 | NCT00781391 / stroke_se | PUBMED:24251359 | EFFECT / ITT / STROKE_OR_SYSTEMIC_EMBOLISM | {"effect": "0.87", "lower": "0.73", "upper": "1.04"} |
| F036 | NCT00781391 / major_bleeding | PUBMED:24251359 | EFFECT / UNKNOWN / UNKNOWN | {"effect": "0.80", "lower": "0.71", "upper": "0.91"} |
| F037 | NCT00262600 / major_bleeding | FDA:RELY_FDA2010_Table2_major_bleeding.tables.txt | EFFECT / UNKNOWN / UNKNOWN | {"effect": "0.93", "lower": "0.81", "upper": "1.07"} |
| F038 | NCT00262600 / major_bleeding | FDA:RELY_FDA2010_Table2_major_bleeding.tables.txt | COUNTS / UNKNOWN / UNKNOWN | {"events_t": 399, "n_t": 6076, "events_c": 421, "n_c": 6022} |
| F039 | NCT00403767 / major_bleeding | FDA:ROCKET_FDA2022_Table5_major_bleeding.tables.txt | EFFECT / ON_TREATMENT / UNKNOWN | {"effect": "1.04", "lower": "0.90", "upper": "1.20"} |
| F040 | NCT00403767 / major_bleeding | FDA:ROCKET_FDA2022_Table5_major_bleeding.tables.txt | COUNTS / ON_TREATMENT / UNKNOWN | {"events_t": 395, "n_t": 7111, "events_c": 386, "n_c": 7125} |

## Proposed arithmetic only

```json
{
  "label": "PROPOSED_SENSITIVITY_NOT_SERVED_NOT_ALL_INPUTS_TWO_SOURCE_VERIFIED",
  "admissible_to_verified_pool": false,
  "inputs": [
    "F037",
    "F039",
    "F033",
    "F036"
  ],
  "inputs_two_source_verified": [
    "F037",
    "F033",
    "F036"
  ],
  "reason": "3 of 4 input HRs are two-source verified; populations and definitions differ across trials (safety vs unstated populations; ISTH vs modified-ISTH); source-anchored HR arithmetic only, never served.",
  "result": {
    "scale": "HR",
    "k": 4,
    "tau2": 0.026648007724361378,
    "mu_log": -0.15739857026735737,
    "se_log": 0.08887309774537376,
    "ci_low": 0.6438867439171664,
    "ci_high": 1.1336418100896692,
    "pi_low": 0.47288199376252765,
    "pi_high": 1.543592150885661,
    "Q": 18.14968966191982,
    "estimate": 0.8543634670718311,
    "per_study": [
      [
        "NCT00262600",
        -0.07257069283483537,
        0.0050433474453907825
      ],
      [
        "NCT00403767",
        0.03922071315328133,
        0.005386038135064363
      ],
      [
        "NCT00412984",
        -0.37106368139083207,
        0.005386038135064367
      ],
      [
        "NCT00781391",
        -0.2231435513142097,
        0.004008446488792781
      ]
    ],
    "ci_low_fixed": 0.7951416073113924,
    "ci_high_fixed": 0.9118600368599102,
    "estimate_fixed": 0.8515032914509577,
    "ci_provenance": "synth.pool:PM-tau2+HKSJ-t(k-1)+floor-max(1,Q/(k-1)):v1"
  }
}
```

## Census and reproduction

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
      "n": 5,
      "N": 8,
      "n_of_N": "5 of 8",
      "items": [
        "ARISTOTLE/major_bleeding",
        "ARISTOTLE/stroke_se",
        "ENGAGE AF-TIMI 48/major_bleeding",
        "ENGAGE AF-TIMI 48/stroke_se",
        "ROCKET AF/stroke_se"
      ]
    },
    "SINGLE_SOURCE": {
      "n": 2,
      "N": 8,
      "n_of_N": "2 of 8",
      "items": [
        "RE-LY/stroke_se",
        "ROCKET AF/major_bleeding"
      ]
    },
    "CONFLICT": {
      "n": 1,
      "N": 8,
      "n_of_N": "1 of 8",
      "items": [
        "RE-LY/major_bleeding"
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
    "n": 1,
    "N": 8,
    "n_of_N": "1 of 8",
    "items": [
      "RE-LY/major_bleeding"
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
  ],
  "denominator_reproduction": {
    "aact_started": {
      "RE-LY": {
        "t": 6076,
        "c": 6022,
        "source": "AACT milestones STARTED"
      },
      "ROCKET AF": {
        "t": 7111,
        "c": 7125,
        "source": "AACT milestones STARTED"
      },
      "ARISTOTLE": {
        "t": 9120,
        "c": 9081,
        "source": "AACT milestones STARTED"
      },
      "ENGAGE AF-TIMI 48": {
        "t": 7035,
        "c": 7036,
        "source": "AACT milestones STARTED"
      }
    },
    "targets": {
      "randomized": {
        "t": {
          "comparator": 29362,
          "aact_started_sum": 29342,
          "residual": 20,
          "implied_if_others_exact": {
            "RE-LY": 6096,
            "ROCKET AF": 7131,
            "ARISTOTLE": 9140,
            "ENGAGE AF-TIMI 48": 7055
          }
        },
        "c": {
          "comparator": 29272,
          "aact_started_sum": 29264,
          "residual": 8,
          "implied_if_others_exact": {
            "RE-LY": 6030,
            "ROCKET AF": 7133,
            "ARISTOTLE": 9089,
            "ENGAGE AF-TIMI 48": 7044
          }
        }
      },
      "stroke_se_analysed": {
        "t": {
          "comparator": 29312,
          "aact_started_sum": 29342,
          "residual": -30,
          "implied_if_others_exact": {
            "RE-LY": 6046,
            "ROCKET AF": 7081,
            "ARISTOTLE": 9090,
            "ENGAGE AF-TIMI 48": 7005
          }
        },
        "c": {
          "comparator": 29229,
          "aact_started_sum": 29264,
          "residual": -35,
          "implied_if_others_exact": {
            "RE-LY": 5987,
            "ROCKET AF": 7090,
            "ARISTOTLE": 9046,
            "ENGAGE AF-TIMI 48": 7001
          }
        }
      },
      "major_bleeding_analysed": {
        "t": {
          "comparator": 29270,
          "aact_started_sum": 29342,
          "residual": -72,
          "implied_if_others_exact": {
            "RE-LY": 6004,
            "ROCKET AF": 7039,
            "ARISTOTLE": 9048,
            "ENGAGE AF-TIMI 48": 6963
          }
        },
        "c": {
          "comparator": 29187,
          "aact_started_sum": 29264,
          "residual": -77,
          "implied_if_others_exact": {
            "RE-LY": 5945,
            "ROCKET AF": 7048,
            "ARISTOTLE": 9004,
            "ENGAGE AF-TIMI 48": 6959
          }
        }
      }
    },
    "label": "DENOMINATOR_ARITHMETIC_ONLY: AACT STARTED is participant flow, not proof of randomisation (ROCKET AF STARTED counts treated participants); implied values are not held in any primary source"
  }
}
```
