# Lane L2 independent A7 oracle report

The comparison is against LANE_PROMPT.md, not a release certification. All oracle inputs are synthetic.

Agreement: **3194 of 3246 cases**. There are 46 hand-built cases and 3,200 generated cases (1,600 per function), seed 20261014.

| Function | Agree | Total | Disagree |
|---|---:|---:|---:|
| reported | 1578 | 1630 | 52 |
| percent | 1616 | 1616 | 0 |

Disagreement families: zero-cell OR: 41, previous-semicolon leakage: 11.

Each disagreement is retained under its fixed case ID with `pytest.mark.xfail(strict=True, reason="ORACLE DISAGREES: ...")`. The list is frozen in the test file; current outputs do not determine marks. Any resolved disagreement becomes a failing XPASS. Hand-case expected answers are independently asserted as well as documented in comments.

## Independence and scope

Neither harness/extract.py nor harness/absence.py was opened. Function signatures and runtime results were inspected; the oracle uses only the real _arm_ns helper as required. No oracle or generator reads cache/ or docs/. The separately requested existing regression tests retain their own fixture access. No harness files changed. The initial worktree contained only untracked LANE_PROMPT.md and lane.log. No commit, push, full-suite run, project-status promotion, or workbook/index modification was performed.

## Static versus dynamic disclosure

| Item | Kind | Source / purpose |
|---|---|---|
| Thresholds, label vocabulary, exclusions | Static | Lane specification |
| Hand examples, seed, sentence templates, frozen xfail IDs | Static | Synthetic contract coverage, not research outputs |
| Expected counts | Dynamic | Exhaustive integer search using Decimal rounding/truncation inequalities |
| Arm-size extraction | Dynamic shared dependency | Real _arm_ns, explicitly outside the independent test boundary |
| Derived effects, classifications, comparison counts | Dynamic | Oracle computation and real runtime calls |

## Validation

- python -m pytest -q tests/test_a7_oracle.py -p no:cacheprovider: **3240 passed, 52 xfailed** (24.84s), exit 0. This includes 46 hand-expectation checks in addition to 3246 differential cases; 3194/3246 differential cases agree.
- python -m pytest -q tests/test_reported_vs_derived.py tests/test_a7_picu.py -p no:cacheprovider --tb=short: **31 passed, 5 failed** (42.81s), exit 1. All five failures are FileNotFoundError for cache/probiotics-aad-prevention/records.json; exact-path existence check returned False. No fixture was fabricated or copied. See STUCK_FAILURES.md.
- Initial unmarked oracle run: 3240 passed, 52 failed; each observed disagreement was reviewed and frozen as a strict xfail. A generator correction ensures integer-precision positive reported values print consistently; the final disagreement set remains 52.
- Second-pass review: all disagreement inputs are synthetic; 41 zero-cell OR cases and 11 semicolon-boundary cases follow the stated spec rationale below. No clinical identifiers, study dates, or research claims were introduced.
- The regression failures are unresolved fixture blockers, not a green regression result.

## Every disagreement

Inputs below are the four positional function arguments. Answers are normalized as `[state, gross, terminal, [ai,n1i,ci,n2i]]`, or `null` for None. Percentage answers would be `[ai,n1i,ci,n2i]`; none disagreed. The CI and count-span literals are synthetic metadata, not measured claims.

### or-zero-nonevent

```json
{
  "input": [
    [
      10,
      10,
      5,
      10
    ],
    [
      "OR",
      0.5,
      0.1,
      3.0
    ],
    "OR .50",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      10,
      10,
      5,
      10
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0005

```json
{
  "input": [
    [
      0,
      7,
      0,
      80
    ],
    [
      "OR",
      1.0,
      0.1,
      3.0
    ],
    "odds ratio 1 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      0,
      7,
      0,
      80
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0031

```json
{
  "input": [
    [
      6,
      6,
      32,
      131
    ],
    [
      "OR",
      1.97,
      0.1,
      3.0
    ],
    "multivariate OR 1.97 adjusted HR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      6,
      6,
      32,
      131
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0041

```json
{
  "input": [
    [
      118,
      168,
      32,
      56
    ],
    [
      "RR",
      0.84,
      0.1,
      3.0
    ],
    "control for age; RR .84.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      118,
      168,
      32,
      56
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-0132

```json
{
  "input": [
    [
      140,
      166,
      26,
      55
    ],
    [
      "RR",
      2.463,
      0.1,
      3.0
    ],
    "control for age; risk ratio 2.463.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      140,
      166,
      26,
      55
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-0175

```json
{
  "input": [
    [
      32,
      32,
      34,
      78
    ],
    [
      "OR",
      1.68,
      0.1,
      3.0
    ],
    "odds ratio 1.68 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      32,
      32,
      34,
      78
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0201

```json
{
  "input": [
    [
      193,
      193,
      77,
      82
    ],
    [
      "OR",
      1.631,
      0.1,
      3.0
    ],
    "control for age; odds ratio 1.631 adjusted HR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      193,
      193,
      77,
      82
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0216

```json
{
  "input": [
    [
      12,
      40,
      69,
      174
    ],
    [
      "OR",
      1.1,
      0.1,
      3.0
    ],
    "control for age; OR 1.1.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      12,
      40,
      69,
      174
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-0217

```json
{
  "input": [
    [
      27,
      27,
      37,
      155
    ],
    [
      "OR",
      2.46,
      0.1,
      3.0
    ],
    "unadjusted odds ratio 2.46 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      27,
      27,
      37,
      155
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0259

```json
{
  "input": [
    [
      14,
      14,
      81,
      112
    ],
    [
      "OR",
      1.0,
      0.1,
      3.0
    ],
    "unadjusted odds ratio 1.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      14,
      14,
      81,
      112
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0265

```json
{
  "input": [
    [
      97,
      141,
      55,
      134
    ],
    [
      "RR",
      2.17,
      0.1,
      3.0
    ],
    "control for age; RR 2.17.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      97,
      141,
      55,
      134
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-0344

```json
{
  "input": [
    [
      51,
      79,
      183,
      183
    ],
    [
      "OR",
      1.29,
      0.1,
      3.0
    ],
    "unadjusted odds ratio 1.29 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      51,
      79,
      183,
      183
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0360

```json
{
  "input": [
    [
      92,
      109,
      16,
      16
    ],
    [
      "OR",
      2.0,
      0.1,
      3.0
    ],
    "control for age; OR 2 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      92,
      109,
      16,
      16
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0386

```json
{
  "input": [
    [
      0,
      82,
      159,
      200
    ],
    [
      "OR",
      0.7,
      0.1,
      3.0
    ],
    "odds ratio 0.7.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      0,
      82,
      159,
      200
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0421

```json
{
  "input": [
    [
      19,
      19,
      18,
      22
    ],
    [
      "OR",
      1.0,
      0.1,
      3.0
    ],
    "unadjusted odds ratio 1.0 adjusted HR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      19,
      19,
      18,
      22
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0546

```json
{
  "input": [
    [
      54,
      132,
      119,
      162
    ],
    [
      "RR",
      0.624,
      0.1,
      3.0
    ],
    "control for age; risk ratio 0.624.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      54,
      132,
      119,
      162
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-0553

```json
{
  "input": [
    [
      106,
      189,
      0,
      21
    ],
    [
      "OR",
      1.4,
      0.1,
      3.0
    ],
    "adjusted odds ratio 1.4 adjusted HR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      106,
      189,
      0,
      21
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0562

```json
{
  "input": [
    [
      111,
      111,
      107,
      155
    ],
    [
      "OR",
      2.0,
      0.1,
      3.0
    ],
    "multivariate odds ratio 2; adjusted OR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      111,
      111,
      107,
      155
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0626

```json
{
  "input": [
    [
      0,
      18,
      20,
      161
    ],
    [
      "OR",
      1.63,
      0.1,
      3.0
    ],
    "control for age; OR 1.63 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      0,
      18,
      20,
      161
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0630

```json
{
  "input": [
    [
      16,
      16,
      69,
      77
    ],
    [
      "OR",
      1.67,
      0.1,
      3.0
    ],
    "unadjusted OR 1.67 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      16,
      16,
      69,
      77
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0641

```json
{
  "input": [
    [
      89,
      89,
      71,
      87
    ],
    [
      "OR",
      0.42,
      0.1,
      3.0
    ],
    "unadjusted odds ratio .42.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      89,
      89,
      71,
      87
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0657

```json
{
  "input": [
    [
      46,
      78,
      0,
      17
    ],
    [
      "OR",
      2.3,
      0.1,
      3.0
    ],
    "control for age; OR 2.3 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      46,
      78,
      0,
      17
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0699

```json
{
  "input": [
    [
      0,
      8,
      137,
      177
    ],
    [
      "OR",
      1.989,
      0.1,
      3.0
    ],
    "unadjusted OR 1.989 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      0,
      8,
      137,
      177
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0720

```json
{
  "input": [
    [
      60,
      154,
      2,
      10
    ],
    [
      "OR",
      1.342,
      0.1,
      3.0
    ],
    "control for age; odds ratio 1.342.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      60,
      154,
      2,
      10
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-0750

```json
{
  "input": [
    [
      36,
      36,
      145,
      154
    ],
    [
      "OR",
      0.5,
      0.1,
      3.0
    ],
    "multivariate OR 0.5.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      36,
      36,
      145,
      154
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0754

```json
{
  "input": [
    [
      20,
      20,
      20,
      175
    ],
    [
      "OR",
      2.0,
      0.1,
      3.0
    ],
    "OR 2 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      20,
      20,
      20,
      175
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0755

```json
{
  "input": [
    [
      0,
      11,
      26,
      186
    ],
    [
      "OR",
      0.89,
      0.1,
      3.0
    ],
    "unadjusted OR 0.89 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      0,
      11,
      26,
      186
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0768

```json
{
  "input": [
    [
      0,
      90,
      95,
      112
    ],
    [
      "OR",
      2.3,
      0.1,
      3.0
    ],
    "adjusted odds ratio 2.3 adjusted HR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      0,
      90,
      95,
      112
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0770

```json
{
  "input": [
    [
      0,
      43,
      28,
      79
    ],
    [
      "OR",
      1.233,
      0.1,
      3.0
    ],
    "odds ratio 1.233 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      0,
      43,
      28,
      79
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0783

```json
{
  "input": [
    [
      112,
      124,
      16,
      43
    ],
    [
      "RR",
      1.484,
      0.1,
      3.0
    ],
    "control for age; risk ratio 1.484.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      112,
      124,
      16,
      43
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-0796

```json
{
  "input": [
    [
      65,
      130,
      0,
      57
    ],
    [
      "OR",
      1.848,
      0.1,
      3.0
    ],
    "odds ratio 1.848 adjusted HR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      65,
      130,
      0,
      57
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0799

```json
{
  "input": [
    [
      0,
      36,
      54,
      85
    ],
    [
      "OR",
      1.0,
      0.1,
      3.0
    ],
    "unadjusted OR 1 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      0,
      36,
      54,
      85
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0851

```json
{
  "input": [
    [
      1,
      112,
      0,
      6
    ],
    [
      "OR",
      0.78,
      0.1,
      3.0
    ],
    "control for age; odds ratio 0.78 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      1,
      112,
      0,
      6
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0893

```json
{
  "input": [
    [
      32,
      95,
      107,
      132
    ],
    [
      "RR",
      0.72,
      0.1,
      3.0
    ],
    "control for age; RR .72.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      32,
      95,
      107,
      132
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-0903

```json
{
  "input": [
    [
      53,
      99,
      0,
      60
    ],
    [
      "OR",
      2.35,
      0.1,
      3.0
    ],
    "unadjusted OR 2.35.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      53,
      99,
      0,
      60
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0907

```json
{
  "input": [
    [
      19,
      19,
      1,
      58
    ],
    [
      "OR",
      2.0,
      0.1,
      3.0
    ],
    "multivariate odds ratio 2 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      19,
      19,
      1,
      58
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0908

```json
{
  "input": [
    [
      67,
      105,
      55,
      108
    ],
    [
      "OR",
      1.1,
      0.1,
      3.0
    ],
    "control for age; OR 1.1.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      67,
      105,
      55,
      108
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-0918

```json
{
  "input": [
    [
      31,
      31,
      0,
      87
    ],
    [
      "OR",
      1.2,
      0.1,
      3.0
    ],
    "adjusted odds ratio 1.2; adjusted OR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      31,
      31,
      0,
      87
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-0936

```json
{
  "input": [
    [
      107,
      107,
      23,
      63
    ],
    [
      "OR",
      1.571,
      0.1,
      3.0
    ],
    "OR 1.571 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      107,
      107,
      23,
      63
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1006

```json
{
  "input": [
    [
      69,
      93,
      102,
      143
    ],
    [
      "OR",
      2.23,
      0.1,
      3.0
    ],
    "control for age; odds ratio 2.23.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      69,
      93,
      102,
      143
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-1028

```json
{
  "input": [
    [
      93,
      93,
      19,
      153
    ],
    [
      "OR",
      2.0,
      0.1,
      3.0
    ],
    "adjusted odds ratio 2.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      93,
      93,
      19,
      153
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1029

```json
{
  "input": [
    [
      74,
      191,
      0,
      17
    ],
    [
      "OR",
      2.0,
      0.1,
      3.0
    ],
    "control for age; OR 2 adjusted HR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      74,
      191,
      0,
      17
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1075

```json
{
  "input": [
    [
      15,
      15,
      6,
      10
    ],
    [
      "OR",
      1.8,
      0.1,
      3.0
    ],
    "control for age; odds ratio 1.8 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      15,
      15,
      6,
      10
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1163

```json
{
  "input": [
    [
      8,
      8,
      53,
      134
    ],
    [
      "OR",
      2.0,
      0.1,
      3.0
    ],
    "adjusted OR 2.0 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      8,
      8,
      53,
      134
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1184

```json
{
  "input": [
    [
      7,
      7,
      9,
      22
    ],
    [
      "OR",
      1.0,
      0.1,
      3.0
    ],
    "control for age; OR 1.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      7,
      7,
      9,
      22
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1224

```json
{
  "input": [
    [
      10,
      12,
      0,
      11
    ],
    [
      "OR",
      2.4,
      0.1,
      3.0
    ],
    "unadjusted OR 2.4 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      10,
      12,
      0,
      11
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1265

```json
{
  "input": [
    [
      23,
      23,
      97,
      196
    ],
    [
      "OR",
      1.79,
      0.1,
      3.0
    ],
    "control for age; odds ratio 1.79 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      23,
      23,
      97,
      196
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1306

```json
{
  "input": [
    [
      63,
      63,
      16,
      161
    ],
    [
      "OR",
      1,
      0.1,
      3.0
    ],
    "multivariate odds ratio 1 (95% CI .1-3.0).",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      63,
      63,
      16,
      161
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1389

```json
{
  "input": [
    [
      24,
      24,
      26,
      192
    ],
    [
      "OR",
      0.38,
      0.1,
      3.0
    ],
    "adjusted odds ratio .38 adjusted for age.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      24,
      24,
      26,
      192
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1461

```json
{
  "input": [
    [
      31,
      181,
      2,
      30
    ],
    [
      "RR",
      1.497,
      0.1,
      3.0
    ],
    "control for age; RR 1.497.",
    "Synthetic arm counts"
  ],
  "oracle": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    false,
    true,
    [
      31,
      181,
      2,
      30
    ]
  ],
  "real": null
}
```

Oracle follows the spec: control for age is before the preceding semicolon and outside the reported value's own clause. The positive derived effect is not grossly different but exceeds the printed rounding tolerance, so the result must be terminal.

### generated-r-1485

```json
{
  "input": [
    [
      0,
      157,
      26,
      51
    ],
    [
      "OR",
      2.0,
      0.1,
      3.0
    ],
    "multivariate OR 2; adjusted OR .75",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      0,
      157,
      26,
      51
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

### generated-r-1587

```json
{
  "input": [
    [
      116,
      116,
      17,
      17
    ],
    [
      "OR",
      0.6,
      0.1,
      3.0
    ],
    "OR 0.6.",
    "Synthetic arm counts"
  ],
  "oracle": null,
  "real": [
    "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE",
    true,
    false,
    [
      116,
      116,
      17,
      17
    ]
  ]
}
```

Oracle follows the spec: the OR table has a zero event or non-event cell. Without continuity correction the OR is undefined or zero, so return None before gross classification.

## Patch creation

The requested live-index `git add -N` was denied at `.git/index.lock`. A temporary index then hit a read-only object-database error; the isolated-object fallback did not finish and was stopped. Therefore `lane.patch` was assembled with `git diff --no-index -- NUL <file>` for each new artifact. This preserves a standard Git patch including the untracked test without changing the live index. It is the documented deviation from the requested index-based command. No commit or push was made.
