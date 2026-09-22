# Lane V — enforcement-gate reproduction and red-team audit

Audit complete. No commits requested or made. Served pages were not edited or rebuilt.

Key findings, with the full commands and evidence in the four parts below:

- Pre-fix plants: 12 of 12 fail, consisting of 11 of 12 ImportError and 1 of 12 KeyError; no semantic assertion failure. The independent real-page witness passes with 11 of 11 primary family states UNKNOWN.
- Post-fix plants: 12 of 12 pass. Untouched-page enforcement refuses 32 of 32 pages; recomputation marks 53 of 87 primary pooled rows INADMISSIBLE. The stamp census exits with code `1`, with 127 of 127 pooled rows unstamped.
- Red team: 6 of 6 variants refuse. V1/V3 detect the vanished trial internally but omit its name from emitted reasons; V2 shrinks the included denominator from 57 of 57 to 56 of 57 and loses that signal. V6 is an admission refusal, not merely a hash catch.
- The global single-computing-site claim fails: 3 distinct algorithms across 4 physical sites; only 1 of 4 sites is the shared in-build verdict. Details distinguish the bundle builder, independent verifier, and identical shipped verifier mirror.
- Preservation: 194 of 194 served review files and 937 of 937 cache files match the baseline. Tracked served/cache diff is empty, and HEAD is unchanged.

## Scope and evidence handling

The commands below run with Windows `python` in this checkout. Command output is recorded verbatim, including denominator lines and native exit codes. Counts in interpretation are expressed against their named denominator; identifiers, source line numbers, versions, and verbatim output retain their original notation.

Initial preflight: `git status --short` showed only `LANE_PROMPT.md`, `lane.log`, and `source.patch` untracked. `git rev-parse HEAD` returned `38c04411484dbea035a8e4c8e22c57c2794f9495`. `python --version` returned `Python 3.13.13`. The project index and rewrite workbook were read first, but their large output was truncated; a targeted `rg -n 'meta-harness|mh-g-V'` over both returned no matches. Neither is edited by this lane. No portfolio or submission status is changed.

Operational disclosure: the initial oversized context read was polled with a Ctrl-C input while the lane instructions were being retrieved. The response reported that the process had already completed with exit code zero; no termination was reported. Subsequent processes were allowed to finish naturally; no further stop, kill, or signal operation was issued.

| Material | Static or dynamic | Disclosure |
| --- | --- | --- |
| `source.patch` and baseline served/cache files | Static supplied inputs | Inspected from disk; no live acquisition or clinical claim validation is inferred. |
| Pre/post tests and census | Dynamic measured results | Actual process output and exit status recorded below. |
| `.tmp/rt` variants | Deliberately altered copies | Forged eligibility/stamps are adversarial fixtures, never research output. |
| Reader inventory and gap analysis | Source-derived | File/line evidence and bounded conclusions; no second verdict implementation added. |

## Part 1 — pre-fix plants and served gate


### Test-only patch application

Command:

```text
git apply --include=tests/* source.patch
```

Real output:

```text

```

Native exit code: `0`.

### Pre-fix admission plants

Command:

```text
python -m pytest tests/test_admission_enforced.py -q -p no:cacheprovider --basetemp .tmp/pt1
```

Real output:

```text
FFFFFFFFFFFF                                                             [100%]
================================== FAILURES ===================================
___ test_build_sets_aside_a_row_whose_family_eligibility_is_not_established ___

    def test_build_sets_aside_a_row_whose_family_eligibility_is_not_established():
        """P5 FAIL by UNKNOWN: the candidate extraction is rejected, the trial is not."""
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:78: ImportError
_______ test_build_refuses_on_evidence_a_row_whose_family_is_ineligible _______

    def test_build_refuses_on_evidence_a_row_whose_family_is_ineligible():
        """P5 FAIL by INELIGIBLE (a positive finding with a span): refused on evidence, span carried, trial kept."""
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:95: ImportError
____________ test_build_keeps_the_migration_state_pooled_and_named ____________

    def test_build_keeps_the_migration_state_pooled_and_named():
        """An unbound_legacy row whose family is ELIGIBLE is the bundle's MIGRATION state: pooled, counted separately."""
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:104: ImportError
______________ test_build_handed_no_family_ledger_admits_nothing ______________

    def test_build_handed_no_family_ledger_admits_nothing():
        """ON by default: a build that has no family ledger cannot establish P5 and pools nothing."""
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:114: ImportError
________ test_the_producer_route_reads_the_decision_on_the_real_inputs ________

    def test_the_producer_route_reads_the_decision_on_the_real_inputs():
        """The real route (pipeline.outcome_inputs + the real _build_outcome) on committed glp1 inputs: flipping ONE
        family's eligibility to INELIGIBLE removes exactly that trial from the pool, keeps it on the outcome as a
        refusal, and the restored ledger gives the control pool back. Paired shape; no number asserted."""
        from harness import fetch
        config = json.load(open(os.path.join(pipeline.ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
        records = fetch.ensure(config, "")
        inp = pipeline.outcome_inputs(SLUG, config, records)
        spec = next(s for s, k in pipeline._outcome_specs(config) if s.get("name") == PRIMARY)
        control = pipeline.build_outcome_from_inputs(inp, spec, "efficacy", SLUG)
>       pooled = [t for t in control["trials"] if t["admission_verdict"]["final"] == "ADMISSIBLE"]
                                                  ^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'admission_verdict'

tests\test_admission_enforced.py:130: KeyError
_ test_gate_refuses_a_page_that_pools_an_unstamped_row_whose_family_is_not_eligible _

    def test_gate_refuses_a_page_that_pools_an_unstamped_row_whose_family_is_not_eligible():
        """RED on today's pages: no stamp AND the page's own families say UNKNOWN. The refusal names the trial,
        the family, the state and the absence code, and prints the scope of what it checked."""
        with tempfile.TemporaryDirectory() as tmp:
>           d = _page(tmp, [_row("1")], [_family("fam-1", "1", state="UNKNOWN", code="INTERVENTION_CONTRAST_NOT_PROVEN")], stamp=False)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_admission_enforced.py:180: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

tmp = 'F:\\mh-g-V\\.tmp\\tmphopt_3of'
rows = [{'ci_high': 0.9, 'ci_low': 0.7, 'effect': 0.8, 'endpoint_admissibility': 'EXACT_TARGET', ...}]
fams = [{'aliases': {'acronym': []}, 'arms': [], 'eligibility': {'absence_code': 'INTERVENTION_CONTRAST_NOT_PROVEN', 'state': 'UNKNOWN'}, 'family_id': 'fam-1', ...}]
stamp = False, screening_ids = None

    def _page(tmp, rows, fams, stamp=True, screening_ids=None):
        """A synthetic served page: the review carries its own trial_families copy and (optionally) stamped rows."""
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:151: ImportError
_ test_gate_refuses_a_stamped_row_whose_stamp_disagrees_with_the_page_families _

    def test_gate_refuses_a_stamped_row_whose_stamp_disagrees_with_the_page_families():
        """A stamp is not trusted: ADMISSIBLE on the row while the page's own families read UNKNOWN is refused."""
        with tempfile.TemporaryDirectory() as tmp:
            fams = [_family("fam-1", "1")]
>           d = _page(tmp, [_row("1")], fams)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_admission_enforced.py:192: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

tmp = 'F:\\mh-g-V\\.tmp\\tmp01imuwj9'
rows = [{'ci_high': 0.9, 'ci_low': 0.7, 'effect': 0.8, 'endpoint_admissibility': 'EXACT_TARGET', ...}]
fams = [{'aliases': {'acronym': []}, 'arms': [], 'eligibility': {'span': {'design': {'allocation': 'RANDOMIZED'}, 'population': {'quote': 'adults with the condition'}}, 'state': 'ELIGIBLE'}, 'family_id': 'fam-1', ...}]
stamp = True, screening_ids = None

    def _page(tmp, rows, fams, stamp=True, screening_ids=None):
        """A synthetic served page: the review carries its own trial_families copy and (optionally) stamped rows."""
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:151: ImportError
_______ test_gate_refuses_a_page_from_which_a_screened_in_row_vanished ________

    def test_gate_refuses_a_page_from_which_a_screened_in_row_vanished():
        """Not satisfiable by dropping rows: a record screened IN that is neither pooled nor set aside is a refusal."""
        with tempfile.TemporaryDirectory() as tmp:
            fams = [_family("fam-1", "1"), _family("fam-2", "2")]
>           d = _page(tmp, [_row("1"), _row("2")], fams)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_admission_enforced.py:203: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

tmp = 'F:\\mh-g-V\\.tmp\\tmpdy16be41'
rows = [{'ci_high': 0.9, 'ci_low': 0.7, 'effect': 0.8, 'endpoint_admissibility': 'EXACT_TARGET', ...}, {'ci_high': 0.9, 'ci_low': 0.7, 'effect': 0.8, 'endpoint_admissibility': 'EXACT_TARGET', ...}]
fams = [{'aliases': {'acronym': []}, 'arms': [], 'eligibility': {'span': {'design': {'allocation': 'RANDOMIZED'}, 'population...'RANDOMIZED'}, 'population': {'quote': 'adults with the condition'}}, 'state': 'ELIGIBLE'}, 'family_id': 'fam-2', ...}]
stamp = True, screening_ids = None

    def _page(tmp, rows, fams, stamp=True, screening_ids=None):
        """A synthetic served page: the review carries its own trial_families copy and (optionally) stamped rows."""
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:151: ImportError
_______ test_gate_accepts_a_consistent_stamped_page_and_names_its_scope _______

    def test_gate_accepts_a_consistent_stamped_page_and_names_its_scope():
        """Control: stamped, consistent, nothing vanished -> the admission check adds no refusal."""
        with tempfile.TemporaryDirectory() as tmp:
>           d = _page(tmp, [_row("1"), _row("2", binding="unbound_legacy")], [_family("fam-1", "1"), _family("fam-2", "2")])
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_admission_enforced.py:215: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

tmp = 'F:\\mh-g-V\\.tmp\\tmpp6t3z3cb'
rows = [{'ci_high': 0.9, 'ci_low': 0.7, 'effect': 0.8, 'endpoint_admissibility': 'EXACT_TARGET', ...}, {'ci_high': 0.9, 'ci_low': 0.7, 'effect': 0.8, 'endpoint_admissibility': 'EXACT_TARGET', ...}]
fams = [{'aliases': {'acronym': []}, 'arms': [], 'eligibility': {'span': {'design': {'allocation': 'RANDOMIZED'}, 'population...'RANDOMIZED'}, 'population': {'quote': 'adults with the condition'}}, 'state': 'ELIGIBLE'}, 'family_id': 'fam-2', ...}]
stamp = True, screening_ids = None

    def _page(tmp, rows, fams, stamp=True, screening_ids=None):
        """A synthetic served page: the review carries its own trial_families copy and (optionally) stamped rows."""
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:151: ImportError
______ test_summary_over_nothing_evaluated_reads_not_evaluated_not_zero _______

    def test_summary_over_nothing_evaluated_reads_not_evaluated_not_zero():
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:223: ImportError
___________ test_scope_names_what_is_and_is_not_evaluated_in_build ____________

    def test_scope_names_what_is_and_is_not_evaluated_in_build():
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:235: ImportError
_______________________ test_vocabulary_is_the_bundles ________________________

    def test_vocabulary_is_the_bundles():
        """One decision, one vocabulary: the verdict words and predicate ids the build stamps are the words the served
        bundle defines (docs/reviews/<slug>/BUNDLE.json, predicate_definitions / final)."""
>       from harness import admission
E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)

tests\test_admission_enforced.py:248: ImportError
=========================== short test summary info ===========================
FAILED tests/test_admission_enforced.py::test_build_sets_aside_a_row_whose_family_eligibility_is_not_established
FAILED tests/test_admission_enforced.py::test_build_refuses_on_evidence_a_row_whose_family_is_ineligible
FAILED tests/test_admission_enforced.py::test_build_keeps_the_migration_state_pooled_and_named
FAILED tests/test_admission_enforced.py::test_build_handed_no_family_ledger_admits_nothing
FAILED tests/test_admission_enforced.py::test_the_producer_route_reads_the_decision_on_the_real_inputs
FAILED tests/test_admission_enforced.py::test_gate_refuses_a_page_that_pools_an_unstamped_row_whose_family_is_not_eligible
FAILED tests/test_admission_enforced.py::test_gate_refuses_a_stamped_row_whose_stamp_disagrees_with_the_page_families
FAILED tests/test_admission_enforced.py::test_gate_refuses_a_page_from_which_a_screened_in_row_vanished
FAILED tests/test_admission_enforced.py::test_gate_accepts_a_consistent_stamped_page_and_names_its_scope
FAILED tests/test_admission_enforced.py::test_summary_over_nothing_evaluated_reads_not_evaluated_not_zero
FAILED tests/test_admission_enforced.py::test_scope_names_what_is_and_is_not_evaluated_in_build
FAILED tests/test_admission_enforced.py::test_vocabulary_is_the_bundles - Imp...
12 failed in 11.42s
```

Native exit code: `1`.

### Pre-fix served probiotics gate

Command:

```text
python -c "exec(open('.tmp/lane_pre_gate.py', encoding='utf-8').read())"
```

Real output:

```text
gate: PASS []
[('PMID 35727573', 'UNKNOWN'), ('PMID 32035998', 'UNKNOWN'), ('PMID 24772726', 'UNKNOWN'), ('PMID 23932219', 'UNKNOWN'), ('PMID 18701826', 'UNKNOWN'), ('PMID 18410562', 'UNKNOWN'), ('PMID 15740542', 'UNKNOWN'), ('PMID 11560298', 'UNKNOWN'), ('PMID 7872284', 'UNKNOWN'), ('PMID 21165295', 'UNKNOWN'), ('PMID 18026577', 'UNKNOWN')]
```

Native exit code: `0`.

### Pre-fix interpretation

The plants failed **12 of 12 collected tests**; **0 of 12 passed**. Of the failures, **11 of 12 are ImportError**, **1 of 12 is KeyError**, and **0 of 12 are AssertionError**. This demonstrates missing API/stamp support, not observed semantic gate rejection for those plants. The real served-page check is the independent witness: the unpatched gate returned `PASS []` with **11 of 11 primary pooled rows** in families whose eligibility is `UNKNOWN`. These are stored family states, not independently adjudicated clinical eligibility.

| Failing test | First error line (verbatim) |
| --- | --- |
| `test_build_sets_aside_a_row_whose_family_eligibility_is_not_established` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_build_refuses_on_evidence_a_row_whose_family_is_ineligible` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_build_keeps_the_migration_state_pooled_and_named` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_build_handed_no_family_ledger_admits_nothing` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_the_producer_route_reads_the_decision_on_the_real_inputs` | `E       KeyError: 'admission_verdict'` |
| `test_gate_refuses_a_page_that_pools_an_unstamped_row_whose_family_is_not_eligible` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_gate_refuses_a_stamped_row_whose_stamp_disagrees_with_the_page_families` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_gate_refuses_a_page_from_which_a_screened_in_row_vanished` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_gate_accepts_a_consistent_stamped_page_and_names_its_scope` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_summary_over_nothing_evaluated_reads_not_evaluated_not_zero` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_scope_names_what_is_and_is_not_evaluated_in_build` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |
| `test_vocabulary_is_the_bundles` | `E       ImportError: cannot import name 'admission' from 'harness' (F:\mh-g-V\harness\__init__.py)` |

The inline Python body was saved unchanged to `.tmp/lane_pre_gate.py` because PowerShell does not support Bash heredoc syntax. Exact body:

```python
import json,os
from harness.gate import gate_page
d=os.path.join("docs","reviews","probiotics-aad-prevention")
ok,reasons=gate_page(d)
r=json.load(open(os.path.join(d,"review.json"),encoding="utf-8"))
fams={f["family_id"]:f for f in r["trial_families"]}
prim=next(o for o in r["outcomes"] if o.get("primary"))
print("gate:", "PASS" if ok else "REFUSE", reasons)
print([(t["id"], fams[t["family_id"]]["eligibility"].get("state")) for t in prim["trials"]])
```

## Part 2 - full patch, post-fix plants, and untouched served pages

### Remaining source patch application

Command:

```text
git apply --exclude=tests/* source.patch
```

Real output:

```text

```

Native exit code: `0`.

### Admission module presence

Command:

```text
python -c "from pathlib import Path; p=Path('harness/admission.py'); print(str(p), 'exists:', p.is_file())"
```

Real output:

```text
harness\admission.py exists: True
```

Native exit code: `0`.

### Post-fix admission plants

Command:

```text
python -m pytest tests/test_admission_enforced.py -q -p no:cacheprovider --basetemp .tmp/pt
```

Real output:

```text
............                                                             [100%]
12 passed in 13.32s
```

Native exit code: `0`.

### Untouched served-page recomputation

Command:

```text
python -c "exec(open('.tmp/lane_served_census.py', encoding='utf-8').read())"
```

Real output:

```text
pages 32 refused 32
primary pooled rows 87 INADMISSIBLE primary 53 non-primary 28
{('UNKNOWN', 'ENTRY_POPULATION_NOT_ESTABLISHED'): 16, ('UNKNOWN', 'INTERVENTION_CONTRAST_NOT_PROVEN'): 16, ('UNKNOWN', 'REGISTRY_PARENT_UNRESOLVED'): 16, ('UNKNOWN', 'INSUFFICIENT_PICD_EVIDENCE'): 4, ('INELIGIBLE', None): 1}
```

Native exit code: `0`.

### Stamp-only census and PowerShell exit status

Command:

```text
powershell -NoProfile -Command "python scripts/admission_census.py; echo $?; echo $LASTEXITCODE; exit $LASTEXITCODE"
```

Real output:

```text
rule: final = ADMISSIBLE if no evaluated predicate fails; MIGRATION_STATE_UNBOUND_LEGACY if P8 is the only failing predicate and the binding is unbound_legacy; INADMISSIBLE otherwise. A row with no family ledger fails P5.
topics with a review: 32; review dirs without review.json (named, not dropped): none
PRIMARY outcomes: candidate rows that reached admission N = 87 = pooled 87 + set aside 0; outcomes 32 {'NOT_EVALUATED': 30, 'NO_CANDIDATE_ROWS': 2}
   pooled by verdict: {None: 87}; unstamped pooled rows: 87
   pooled bound by a route the bundle's P8 does not name (OTHER_ROUTE): 0
   set aside by (state, eligibility, absence_code): {}
ALL outcomes: candidate rows that reached admission N = 127 = pooled 127 + set aside 0; outcomes 97 {'NOT_EVALUATED': 59, 'NO_CANDIDATE_ROWS': 38}
   pooled by verdict: {None: 127}; unstamped pooled rows: 127
   pooled bound by a route the bundle's P8 does not name (OTHER_ROUTE): 0
   set aside by (state, eligibility, absence_code): {}
LIMITS: counts read from the build's stamps (harness/admission.py); in-build admission evaluates P5_family_eligible, P8_endpoint_bound only; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them); a verdict from the bundle itself exists for 1 of 32 topics. in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
REFUSED: 127 pooled row(s) carry no admission verdict (this census does not compute one): balanced-crystalloids-vs-saline-mortality/PMID 35041780; balanced-crystalloids-vs-saline-mortality/PMID 34375394; balanced-crystalloids-vs-saline-mortality/PMID 35041780; colchicine-postop-af/PMID 42132185; colchicine-postop-af/PMID 32720823; colchicine-postop-af/PMID 25172965; colchicine-recurrent-pericarditis/PMID 24694983; colchicine-recurrent-pericarditis/PMID 21873705 ...
False
1
```

Native exit code: `1`.

### Post-fix interpretation

The patched plants pass **12 of 12 collected tests** (failures **0 of 12**). Admission enforcement refuses **32 of 32 served review pages** without rebuilding them. Recomputed verdicts mark **53 of 87 primary pooled rows** INADMISSIBLE; the primary inadmissible subset consists of **52 of 53 UNKNOWN** and **1 of 53 INELIGIBLE**. Within that subset, absence codes are ENTRY_POPULATION_NOT_ESTABLISHED **16 of 53**, INTERVENTION_CONTRAST_NOT_PROVEN **16 of 53**, REGISTRY_PARENT_UNRESOLVED **16 of 53**, and INSUFFICIENT_PICD_EVIDENCE **4 of 53**; the INELIGIBLE row has no absence code (**1 of 53**). Non-primary INADMISSIBLE is **28 of 40 non-primary pooled rows**, where the non-primary denominator is all pooled rows minus primary pooled rows (`127 - 87 = 40`).

The stamp census does **not** recompute those verdicts: it reports **87 of 87 primary pooled rows** and **127 of 127 pooled rows across all outcomes** without stamps, and exits with native code `1`. PowerShell `echo $?` immediately after the census prints `False`; `echo $LASTEXITCODE` prints `1`. Candidate denominators and outcome denominators are quoted above, not inferred from a headline. Primary outcome states: NOT_EVALUATED **30 of 32**, NO_CANDIDATE_ROWS **2 of 32**. Across all outcomes: NOT_EVALUATED **59 of 97**, NO_CANDIDATE_ROWS **38 of 97**. A bundle verdict exists for **1 of 32 reviewed topics**, as printed by the census.

Exact recomputation script (unchanged body from the lane prompt):

```python
import json,glob,os,collections
from harness import admission, gate
refused=0; pages=0; inad=[]; prim=0
for d in sorted(glob.glob("docs/reviews/*")):
    if not os.path.isfile(os.path.join(d,"review.json")): continue
    pages+=1
    if gate.check_admission_enforced(d): refused+=1
    r=json.load(open(os.path.join(d,"review.json"),encoding="utf-8"))
    fams={f["family_id"]:f for f in r.get("trial_families") or []}
    for o in r["outcomes"]:
        for t in o.get("trials") or []:
            if o.get("primary"): prim+=1
            v=admission.verdict(t,fams.get(t.get("family_id")))
            if v["final"]=="INADMISSIBLE": inad.append((r["slug"],t["id"],bool(o.get("primary")),v["predicates"]["P5_family_eligible"]["eligibility_state"],v["predicates"]["P5_family_eligible"]["absence_code"]))
print("pages",pages,"refused",refused)
print("primary pooled rows",prim,"INADMISSIBLE primary",sum(1 for x in inad if x[2]),"non-primary",sum(1 for x in inad if not x[2]))
print(dict(collections.Counter((x[3],x[4]) for x in inad if x[2])))
```

## Part 3 - copied-page red team and denominator analysis

Each variant starts from a fresh whole-directory copy. Only its review.json is altered. The victim is selected deterministically as the first on-disk primary pooled row; this is an identifier read from the supplied source, not an invented trial. All original manifest, certificate, HTML, and bundle files remain in each copy. Exact fixture construction:

```python
import copy
import json
from pathlib import Path
import shutil
import sys

from harness import admission

source = Path('docs/reviews/probiotics-aad-prevention')
original = json.loads((source / 'review.json').read_text(encoding='utf-8'))
primary = next(o for o in original['outcomes'] if o.get('primary'))
victim = primary['trials'][0]
print('Victim selected from the on-disk primary pool:', victim['id'], 'family:', victim['family_id'])
print('Primary pooled row denominator:', len(primary['trials']))
for variant in ('V1', 'V2', 'V3', 'V4', 'V5', 'V6'):
    target = Path('.tmp/rt') / variant
    shutil.copytree(source, target)
    review = copy.deepcopy(original)
    outcome = next(o for o in review['outcomes'] if o.get('primary'))
    if variant in ('V1', 'V2', 'V3'):
        outcome['trials'] = [t for t in outcome['trials'] if t['id'] != victim['id']]
    if variant == 'V2':
        review['screening']['records'] = [r for r in review['screening']['records']
                                           if admission.identity._norm(r['id']) != admission.identity._norm(victim['id'])]
    if variant == 'V3':
        review['trial_families'] = [f for f in review['trial_families'] if f['family_id'] != victim['family_id']]
    families = {f['family_id']: f for f in review['trial_families']}
    if variant in ('V4', 'V6'):
        for row in outcome['trials']:
            families[row['family_id']]['eligibility'] = {'state': 'ELIGIBLE', 'span': {'forged': True}}
    if variant in ('V5', 'V6'):
        for row in outcome['trials']:
            stamp = admission.verdict(row, families[row['family_id']])
            stamp['final'] = 'ADMISSIBLE'
            stamp['failing'] = []
            stamp['predicates']['P5_family_eligible'].update(state='PASS', eligibility_state='ELIGIBLE', absence_code=None)
            stamp['predicates']['P8_endpoint_bound']['state'] = 'PASS'
            row['admission_verdict'] = stamp
    (target / 'review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(variant, 'copied files', len([p for p in target.rglob('*') if p.is_file()]),
          'of source files', len([p for p in source.rglob('*') if p.is_file()]),
          'primary rows', len(outcome['trials']), 'of original', len(primary['trials']),
          'screening records', len(review['screening']['records']), 'of original', len(original['screening']['records']),
          'families', len(families), 'of original', len(original['trial_families']))
```

### Create the six adversarial copies

Command:

```text
python -c "exec(open('.tmp/lane_variants.py', encoding='utf-8').read())"
```

Real output:

```text
Victim selected from the on-disk primary pool: PMID 35727573 family: NCT03334604
Primary pooled row denominator: 11
V1 copied files 6 of source files 6 primary rows 10 of original 11 screening records 468 of original 468 families 404 of original 404
V2 copied files 6 of source files 6 primary rows 10 of original 11 screening records 467 of original 468 families 404 of original 404
V3 copied files 6 of source files 6 primary rows 10 of original 11 screening records 468 of original 468 families 403 of original 404
V4 copied files 6 of source files 6 primary rows 11 of original 11 screening records 468 of original 468 families 404 of original 404
V5 copied files 6 of source files 6 primary rows 11 of original 11 screening records 468 of original 468 families 404 of original 404
V6 copied files 6 of source files 6 primary rows 11 of original 11 screening records 468 of original 468 families 404 of original 404
```

Native exit code: `0`.

### Gate V1

Command:

```text
python -m harness.gate .tmp/rt/V1
```

Real output:

```text
GATE REFUSE .tmp/rt/V1
    - L1: live census reproduced 2 failure(s): review_sha256 reproduces from committed review.json; served index.html byte-matches re-render of review.json
    - CERTIFICATE.json release_sha256 mismatch: recomputed 06722a0b11a026c3c62825822be38101b9280c8d4f1807f165de665bac8346fb vs saved 9f088de34eda85e0741c5dc36870defa9d7de70cc0340ceac9195444e34afbb8
    - COMPARATOR_PANEL: registered source panel missing
    - L1: admission not enforced -- no admission stamp on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 7872284 in 'Antibiotic-associated diarrhoea' (family SYN-e445a1f4ca49, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; +9 more; scope: evaluated in-build P5_family_eligible, P8_endpoint_bound; not evaluated in-build P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them); migration-state rows pooled under the named exception: none
    - L1: offline replay does NOT regenerate the committed numbers (replay 8fe3a4b5c1768adf04c9b6a0d0221b67b19056d1de160c114c1176b33d7353ff vs committed 23d2942113573e22dc650892260da27134d24562bc586fc247583dbc23522b42)
    - L1: claimgraph violations remain (stale dependent result-bearing object): [{"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/0 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/0"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/1 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/1"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/2 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/2"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/3 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/3"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/4 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/4"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/5 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/5"}]
```

Native exit code: `1`.

### Admission detail V1

Command:

```text
python -c "exec(open('.tmp/lane_diagnose.py', encoding='utf-8').read())" V1
```

Real output:

```text
V1 check_admission_enforced: REFUSE
Every internal admission diagnostic before the gate presentation cap:
no admission stamp on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 7872284 in 'Antibiotic-associated diarrhoea' (family SYN-e445a1f4ca49, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 21165295 in 'Antibiotic-associated diarrhoea' (family SYN-2163745e2514, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18026577 in 'Antibiotic-associated diarrhoea' (family SYN-750512ad72a7, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
vanished row(s) in 'Antibiotic-associated diarrhoea': screened IN but neither pooled nor set aside nor refused: PMID 35727573 -- a refused extraction is set aside with its reason, never dropped
admission summary on 'Antibiotic-associated diarrhoea' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 10 pooled row(s), 10 without a verdict (PMID 32035998, PMID 24772726, PMID 23932219, PMID 18701826, PMID 18410562, PMID 15740542, PMID 11560298, PMID 7872284, PMID 21165295, PMID 18026577); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 41699149 in 'Any adverse events' (family SYN-dd9903025721, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
no admission stamp on pooled row PMID 39529939 in 'Any adverse events' (family NCT05607056, eligibility UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Any adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 2 pooled row(s), 2 without a verdict (PMID 41699149, PMID 39529939); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 34541475 in 'Serious adverse events' (family SYN-23fe0dd26422, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Serious adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 1 pooled row(s), 1 without a verdict (PMID 34541475); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
screened_in_not_pooled: ['PMID 35727573']
PMID 32035998 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 24772726 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 23932219 raw eligibility UNKNOWN effective eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18701826 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18410562 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 15740542 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 11560298 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 7872284 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 21165295 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18026577 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
```

Native exit code: `0`.

### Gate V2

Command:

```text
python -m harness.gate .tmp/rt/V2
```

Real output:

```text
GATE REFUSE .tmp/rt/V2
    - L1: live census reproduced 2 failure(s): review_sha256 reproduces from committed review.json; served index.html byte-matches re-render of review.json
    - CERTIFICATE.json release_sha256 mismatch: recomputed c09389f9932024488b272030b3cc49b83c9b05e4bcf6c4a4a453f22485e9333a vs saved 9f088de34eda85e0741c5dc36870defa9d7de70cc0340ceac9195444e34afbb8
    - COMPARATOR_PANEL: registered source panel missing
    - L1: admission not enforced -- no admission stamp on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 7872284 in 'Antibiotic-associated diarrhoea' (family SYN-e445a1f4ca49, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; +8 more; scope: evaluated in-build P5_family_eligible, P8_endpoint_bound; not evaluated in-build P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them); migration-state rows pooled under the named exception: none
    - L1: offline replay does NOT regenerate the committed numbers (replay 8fe3a4b5c1768adf04c9b6a0d0221b67b19056d1de160c114c1176b33d7353ff vs committed 23d2942113573e22dc650892260da27134d24562bc586fc247583dbc23522b42)
    - L1: claimgraph violations remain (stale dependent result-bearing object): [{"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/0 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/0"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/1 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/1"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/2 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/2"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/3 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/3"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/4 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/4"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/5 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/5"}]
```

Native exit code: `1`.

### Admission detail V2

Command:

```text
python -c "exec(open('.tmp/lane_diagnose.py', encoding='utf-8').read())" V2
```

Real output:

```text
V2 check_admission_enforced: REFUSE
Every internal admission diagnostic before the gate presentation cap:
no admission stamp on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 7872284 in 'Antibiotic-associated diarrhoea' (family SYN-e445a1f4ca49, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 21165295 in 'Antibiotic-associated diarrhoea' (family SYN-2163745e2514, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18026577 in 'Antibiotic-associated diarrhoea' (family SYN-750512ad72a7, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
admission summary on 'Antibiotic-associated diarrhoea' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 10 pooled row(s), 10 without a verdict (PMID 32035998, PMID 24772726, PMID 23932219, PMID 18701826, PMID 18410562, PMID 15740542, PMID 11560298, PMID 7872284, PMID 21165295, PMID 18026577); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 41699149 in 'Any adverse events' (family SYN-dd9903025721, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
no admission stamp on pooled row PMID 39529939 in 'Any adverse events' (family NCT05607056, eligibility UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Any adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 2 pooled row(s), 2 without a verdict (PMID 41699149, PMID 39529939); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 34541475 in 'Serious adverse events' (family SYN-23fe0dd26422, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Serious adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 1 pooled row(s), 1 without a verdict (PMID 34541475); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
screened_in_not_pooled: []
PMID 32035998 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 24772726 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 23932219 raw eligibility UNKNOWN effective eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18701826 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18410562 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 15740542 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 11560298 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 7872284 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 21165295 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18026577 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
```

Native exit code: `0`.

### Gate V3

Command:

```text
python -m harness.gate .tmp/rt/V3
```

Real output:

```text
GATE REFUSE .tmp/rt/V3
    - L1: live census reproduced 2 failure(s): review_sha256 reproduces from committed review.json; served index.html byte-matches re-render of review.json
    - CERTIFICATE.json release_sha256 mismatch: recomputed a9505cc26b990ac9d69e1eee1dcbcbc62cbbfde9c7a1eb24d8e239d4425871f2 vs saved 9f088de34eda85e0741c5dc36870defa9d7de70cc0340ceac9195444e34afbb8
    - COMPARATOR_PANEL: registered source panel missing
    - L1: admission not enforced -- no admission stamp on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 7872284 in 'Antibiotic-associated diarrhoea' (family SYN-e445a1f4ca49, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; +9 more; scope: evaluated in-build P5_family_eligible, P8_endpoint_bound; not evaluated in-build P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them); migration-state rows pooled under the named exception: none
    - L1: offline replay does NOT regenerate the committed numbers (replay 8fe3a4b5c1768adf04c9b6a0d0221b67b19056d1de160c114c1176b33d7353ff vs committed 23d2942113573e22dc650892260da27134d24562bc586fc247583dbc23522b42)
    - L1: claimgraph violations remain (stale dependent result-bearing object): [{"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/0 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/0"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/1 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/1"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/2 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/2"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/3 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/3"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/4 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/4"}, {"code": "STALE_DEPENDENT", "kind": "membership_state", "claim_id": "260697fdb1f718e0", "detail": "/outcomes/0/declared_absent_trials/5 depends on 7e1c703f6a0a23af35b1fc1c53b8a7fc72e5a98d1ae9048bf9852be9eda6da9d, current input_set_version is 694f84d0e1bf30327b1d85c0fc5907a1f35e2784c8bf16f73bb5fccb398af0d7", "object_path": "/outcomes/0/declared_absent_trials/5"}]
```

Native exit code: `1`.

### Admission detail V3

Command:

```text
python -c "exec(open('.tmp/lane_diagnose.py', encoding='utf-8').read())" V3
```

Real output:

```text
V3 check_admission_enforced: REFUSE
Every internal admission diagnostic before the gate presentation cap:
no admission stamp on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 7872284 in 'Antibiotic-associated diarrhoea' (family SYN-e445a1f4ca49, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 21165295 in 'Antibiotic-associated diarrhoea' (family SYN-2163745e2514, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18026577 in 'Antibiotic-associated diarrhoea' (family SYN-750512ad72a7, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
vanished row(s) in 'Antibiotic-associated diarrhoea': screened IN but neither pooled nor set aside nor refused: PMID 35727573 -- a refused extraction is set aside with its reason, never dropped
admission summary on 'Antibiotic-associated diarrhoea' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 10 pooled row(s), 10 without a verdict (PMID 32035998, PMID 24772726, PMID 23932219, PMID 18701826, PMID 18410562, PMID 15740542, PMID 11560298, PMID 7872284, PMID 21165295, PMID 18026577); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 41699149 in 'Any adverse events' (family SYN-dd9903025721, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
no admission stamp on pooled row PMID 39529939 in 'Any adverse events' (family NCT05607056, eligibility UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Any adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 2 pooled row(s), 2 without a verdict (PMID 41699149, PMID 39529939); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 34541475 in 'Serious adverse events' (family SYN-23fe0dd26422, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Serious adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 1 pooled row(s), 1 without a verdict (PMID 34541475); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
screened_in_not_pooled: ['PMID 35727573']
PMID 32035998 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 24772726 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 23932219 raw eligibility UNKNOWN effective eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18701826 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18410562 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 15740542 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 11560298 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 7872284 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 21165295 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18026577 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
```

Native exit code: `0`.

### Gate V4

Command:

```text
python -m harness.gate .tmp/rt/V4
```

Real output:

```text
GATE REFUSE .tmp/rt/V4
    - L1: live census reproduced 2 failure(s): review_sha256 reproduces from committed review.json; served index.html byte-matches re-render of review.json
    - CERTIFICATE.json release_sha256 mismatch: recomputed 64297c8c136f92a373257441efb68dcea81c835aafd571b57ec2a7ccc74e8a0c vs saved 9f088de34eda85e0741c5dc36870defa9d7de70cc0340ceac9195444e34afbb8
    - COMPARATOR_PANEL: registered source panel missing
    - L1: admission not enforced -- no admission stamp on pooled row PMID 35727573 in 'Antibiotic-associated diarrhoea' (family NCT03334604, eligibility ELIGIBLE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield MIGRATION_STATE_UNBOUND_LEGACY failing ['P8_endpoint_bound']; no admission stamp on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility ELIGIBLE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield MIGRATION_STATE_UNBOUND_LEGACY failing ['P8_endpoint_bound']; no admission stamp on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; no admission stamp on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']; +9 more; scope: evaluated in-build P5_family_eligible, P8_endpoint_bound; not evaluated in-build P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them); migration-state rows pooled under the named exception: none
    - L1: offline replay does NOT regenerate the committed numbers (replay 8fe3a4b5c1768adf04c9b6a0d0221b67b19056d1de160c114c1176b33d7353ff vs committed 23d2942113573e22dc650892260da27134d24562bc586fc247583dbc23522b42)
```

Native exit code: `1`.

### Admission detail V4

Command:

```text
python -c "exec(open('.tmp/lane_diagnose.py', encoding='utf-8').read())" V4
```

Real output:

```text
V4 check_admission_enforced: REFUSE
Every internal admission diagnostic before the gate presentation cap:
no admission stamp on pooled row PMID 35727573 in 'Antibiotic-associated diarrhoea' (family NCT03334604, eligibility ELIGIBLE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield MIGRATION_STATE_UNBOUND_LEGACY failing ['P8_endpoint_bound']
no admission stamp on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility ELIGIBLE, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield MIGRATION_STATE_UNBOUND_LEGACY failing ['P8_endpoint_bound']
no admission stamp on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 7872284 in 'Antibiotic-associated diarrhoea' (family SYN-e445a1f4ca49, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 21165295 in 'Antibiotic-associated diarrhoea' (family SYN-2163745e2514, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
no admission stamp on pooled row PMID 18026577 in 'Antibiotic-associated diarrhoea' (family SYN-750512ad72a7, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
admission summary on 'Antibiotic-associated diarrhoea' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 11 pooled row(s), 11 without a verdict (PMID 35727573, PMID 32035998, PMID 24772726, PMID 23932219, PMID 18701826, PMID 18410562, PMID 15740542, PMID 11560298, PMID 7872284, PMID 21165295, PMID 18026577); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 41699149 in 'Any adverse events' (family SYN-dd9903025721, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
no admission stamp on pooled row PMID 39529939 in 'Any adverse events' (family NCT05607056, eligibility UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Any adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 2 pooled row(s), 2 without a verdict (PMID 41699149, PMID 39529939); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 34541475 in 'Serious adverse events' (family SYN-23fe0dd26422, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Serious adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 1 pooled row(s), 1 without a verdict (PMID 34541475); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
screened_in_not_pooled: []
PMID 35727573 raw eligibility ELIGIBLE effective eligibility ELIGIBLE None expected MIGRATION_STATE_UNBOUND_LEGACY failing ['P8_endpoint_bound']
PMID 32035998 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 24772726 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 23932219 raw eligibility ELIGIBLE effective eligibility ELIGIBLE None expected MIGRATION_STATE_UNBOUND_LEGACY failing ['P8_endpoint_bound']
PMID 18701826 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18410562 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 15740542 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 11560298 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 7872284 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 21165295 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18026577 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
```

Native exit code: `0`.

### Gate V5

Command:

```text
python -m harness.gate .tmp/rt/V5
```

Real output:

```text
GATE REFUSE .tmp/rt/V5
    - L1: live census reproduced 1 failure(s): review_sha256 reproduces from committed review.json
    - CERTIFICATE.json release_sha256 mismatch: recomputed 046d8923d59082b20db79946e05669aec0d9d92b7a93e0fd742d1300874dbe5f vs saved 9f088de34eda85e0741c5dc36870defa9d7de70cc0340ceac9195444e34afbb8
    - COMPARATOR_PANEL: registered source panel missing
    - L1: admission not enforced -- stamp disagrees with the page's own families on pooled row PMID 35727573 in 'Antibiotic-associated diarrhoea' (family NCT03334604, eligibility UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; +9 more; scope: evaluated in-build P5_family_eligible, P8_endpoint_bound; not evaluated in-build P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them); migration-state rows pooled under the named exception: none
    - L1: offline replay does NOT regenerate the committed numbers (replay 8fe3a4b5c1768adf04c9b6a0d0221b67b19056d1de160c114c1176b33d7353ff vs committed 23d2942113573e22dc650892260da27134d24562bc586fc247583dbc23522b42)
```

Native exit code: `1`.

### Admission detail V5

Command:

```text
python -c "exec(open('.tmp/lane_diagnose.py', encoding='utf-8').read())" V5
```

Real output:

```text
V5 check_admission_enforced: REFUSE
Every internal admission diagnostic before the gate presentation cap:
stamp disagrees with the page's own families on pooled row PMID 35727573 in 'Antibiotic-associated diarrhoea' (family NCT03334604, eligibility UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 7872284 in 'Antibiotic-associated diarrhoea' (family SYN-e445a1f4ca49, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 21165295 in 'Antibiotic-associated diarrhoea' (family SYN-2163745e2514, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 18026577 in 'Antibiotic-associated diarrhoea' (family SYN-750512ad72a7, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
admission summary on 'Antibiotic-associated diarrhoea' is absent, not EVALUATED: Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 11: admissible 11; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 0. in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
no admission stamp on pooled row PMID 41699149 in 'Any adverse events' (family SYN-dd9903025721, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
no admission stamp on pooled row PMID 39529939 in 'Any adverse events' (family NCT05607056, eligibility UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Any adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 2 pooled row(s), 2 without a verdict (PMID 41699149, PMID 39529939); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 34541475 in 'Serious adverse events' (family SYN-23fe0dd26422, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Serious adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 1 pooled row(s), 1 without a verdict (PMID 34541475); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
screened_in_not_pooled: []
PMID 35727573 raw eligibility UNKNOWN effective eligibility UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 32035998 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 24772726 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 23932219 raw eligibility UNKNOWN effective eligibility UNKNOWN INSUFFICIENT_PICD_EVIDENCE expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18701826 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18410562 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 15740542 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 11560298 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 7872284 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 21165295 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18026577 raw eligibility UNKNOWN effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
```

Native exit code: `0`.

### Gate V6

Command:

```text
python -m harness.gate .tmp/rt/V6
```

Real output:

```text
GATE REFUSE .tmp/rt/V6
    - L1: live census reproduced 2 failure(s): review_sha256 reproduces from committed review.json; served index.html byte-matches re-render of review.json
    - CERTIFICATE.json release_sha256 mismatch: recomputed 91c1e81f72a9192e54369818df5e7d04fce350aadc67239783c72f01041a668e vs saved 9f088de34eda85e0741c5dc36870defa9d7de70cc0340ceac9195444e34afbb8
    - COMPARATOR_PANEL: registered source panel missing
    - L1: admission not enforced -- stamp disagrees with the page's own families on pooled row PMID 35727573 in 'Antibiotic-associated diarrhoea' (family NCT03334604, eligibility ELIGIBLE, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated MIGRATION_STATE_UNBOUND_LEGACY ['P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility ELIGIBLE, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated MIGRATION_STATE_UNBOUND_LEGACY ['P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; stamp disagrees with the page's own families on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']; +9 more; scope: evaluated in-build P5_family_eligible, P8_endpoint_bound; not evaluated in-build P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them); migration-state rows pooled under the named exception: none
    - L1: offline replay does NOT regenerate the committed numbers (replay 8fe3a4b5c1768adf04c9b6a0d0221b67b19056d1de160c114c1176b33d7353ff vs committed 23d2942113573e22dc650892260da27134d24562bc586fc247583dbc23522b42)
```

Native exit code: `1`.

### Admission detail V6

Command:

```text
python -c "exec(open('.tmp/lane_diagnose.py', encoding='utf-8').read())" V6
```

Real output:

```text
V6 check_admission_enforced: REFUSE
Every internal admission diagnostic before the gate presentation cap:
stamp disagrees with the page's own families on pooled row PMID 35727573 in 'Antibiotic-associated diarrhoea' (family NCT03334604, eligibility ELIGIBLE, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated MIGRATION_STATE_UNBOUND_LEGACY ['P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 32035998 in 'Antibiotic-associated diarrhoea' (family SYN-0419eae8aeb8, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 24772726 in 'Antibiotic-associated diarrhoea' (family SYN-94f93929fa67, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 23932219 in 'Antibiotic-associated diarrhoea' (family ISRCTN70017204, eligibility ELIGIBLE, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated MIGRATION_STATE_UNBOUND_LEGACY ['P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 18701826 in 'Antibiotic-associated diarrhoea' (family SYN-3bb36b8c9d29, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 18410562 in 'Antibiotic-associated diarrhoea' (family SYN-a2a3bd246f45, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 15740542 in 'Antibiotic-associated diarrhoea' (family SYN-962dc41d54af, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 11560298 in 'Antibiotic-associated diarrhoea' (family SYN-0b772df8adc9, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 7872284 in 'Antibiotic-associated diarrhoea' (family SYN-e445a1f4ca49, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 21165295 in 'Antibiotic-associated diarrhoea' (family SYN-2163745e2514, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
stamp disagrees with the page's own families on pooled row PMID 18026577 in 'Antibiotic-associated diarrhoea' (family SYN-750512ad72a7, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding unbound_legacy): stamped ADMISSIBLE [], re-evaluated INADMISSIBLE ['P5_family_eligible', 'P8_endpoint_bound']
admission summary on 'Antibiotic-associated diarrhoea' is absent, not EVALUATED: Admission evaluated in-build on P5_family_eligible, P8_endpoint_bound only (P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are not evaluated here: scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them). Pooled 11: admissible 11; migration state (unbound_legacy, pooled and counted separately) 0; bound by a producer route the bundle's P8 does not name 0. Set aside on P5 (family eligibility) 0. in-build P8 passes every producer binding route other than unbound_legacy; the bundle's P8 passes only the definition-span route (rows bound by another route read INADMISSIBLE there: a rule limit raised with the bundle lane, recorded per row as bundle_rule_agreement).
no admission stamp on pooled row PMID 41699149 in 'Any adverse events' (family SYN-dd9903025721, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
no admission stamp on pooled row PMID 39529939 in 'Any adverse events' (family NCT05607056, eligibility UNKNOWN ENTRY_POPULATION_NOT_ESTABLISHED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Any adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 2 pooled row(s), 2 without a verdict (PMID 41699149, PMID 39529939); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
no admission stamp on pooled row PMID 34541475 in 'Serious adverse events' (family SYN-23fe0dd26422, eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED, binding result_span_enumerates_components): the page was built before the build read the admission decision; the page's own families yield INADMISSIBLE failing ['P5_family_eligible']
admission summary on 'Serious adverse events' is absent, not EVALUATED: Admission NOT EVALUATED on this outcome: 1 pooled row(s), 1 without a verdict (PMID 34541475); a page built before the build read the admission decision. In-build scope would be P5_family_eligible, P8_endpoint_bound; P1_source_bytes, P2_span_located, P3_effect_tokens_in_span, P4_endpoint_components, P6_no_unresolved_conflict, P7_coverage_adequate_for_claim, P9_span_target_mention, P10_estimand_evidence, P11_registered_estimand, P12_ci_level, P13_no_extra_components, P14_missing_components_consistent are evaluated only by the bundle (scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, after the build, for the topics that carry a bundle; scripts/verify_bundle.py re-checks them).
screened_in_not_pooled: []
PMID 35727573 raw eligibility ELIGIBLE effective eligibility ELIGIBLE None expected MIGRATION_STATE_UNBOUND_LEGACY failing ['P8_endpoint_bound']
PMID 32035998 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 24772726 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 23932219 raw eligibility ELIGIBLE effective eligibility ELIGIBLE None expected MIGRATION_STATE_UNBOUND_LEGACY failing ['P8_endpoint_bound']
PMID 18701826 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18410562 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 15740542 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 11560298 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 7872284 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 21165295 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
PMID 18026577 raw eligibility ELIGIBLE effective eligibility UNKNOWN REGISTRY_PARENT_UNRESOLVED expected INADMISSIBLE failing ['P5_family_eligible', 'P8_endpoint_bound']
```

Native exit code: `0`.

### Red-team denominators and emitted names

Command:

```text
python -c "exec(open('.tmp/lane_metrics.py', encoding='utf-8').read())"
```

Real output:

```text
V1 gate refused 1 of 1 variant affected trials named in emitted refusal 0 of 1 affected trials named in emitted admission reason 0 of 1
  included denominator 57 of 57 original included records; vanished ['PMID 35727573']
V2 gate refused 1 of 1 variant affected trials named in emitted refusal 0 of 1 affected trials named in emitted admission reason 0 of 1
  included denominator 56 of 57 original included records; vanished []
V3 gate refused 1 of 1 variant affected trials named in emitted refusal 0 of 1 affected trials named in emitted admission reason 0 of 1
  included denominator 57 of 57 original included records; vanished ['PMID 35727573']
V4 gate refused 1 of 1 variant affected trials named in emitted refusal 8 of 11 affected trials named in emitted admission reason 8 of 11
  included denominator 57 of 57 original included records; vanished []
  recomputed primary finals {'MIGRATION_STATE_UNBOUND_LEGACY': 2, 'INADMISSIBLE': 9} denominator 11 primary rows
V5 gate refused 1 of 1 variant affected trials named in emitted refusal 8 of 11 affected trials named in emitted admission reason 8 of 11
  included denominator 57 of 57 original included records; vanished []
V6 gate refused 1 of 1 variant affected trials named in emitted refusal 8 of 11 affected trials named in emitted admission reason 8 of 11
  included denominator 57 of 57 original included records; vanished []
  recomputed primary finals {'MIGRATION_STATE_UNBOUND_LEGACY': 2, 'INADMISSIBLE': 9} denominator 11 primary rows
gate refused variants 6 of 6 requested variants
victim source record lookup: [('35727573', 'NCT03334604')]
verifier mirror byte-identical True
```

Native exit code: `0`.

Supplementary diagnostic command body:

```python
import json
from pathlib import Path
import sys
from harness import gate, membership, admission

variant = sys.argv[1]
directory = Path('.tmp/rt') / variant
review = json.loads((directory / 'review.json').read_text(encoding='utf-8'))
outcome = next(o for o in review['outcomes'] if o.get('primary'))
capture = {}
def observe(frame, event, arg):
    if frame.f_code is gate.check_admission_enforced.__code__ and event == 'return':
        capture['bad'] = list(frame.f_locals.get('bad', []))
    return observe
sys.settrace(observe)
try:
    reasons = gate.check_admission_enforced(str(directory))
finally:
    sys.settrace(None)
print(variant, 'check_admission_enforced:', 'REFUSE' if reasons else 'PASS')
print('Every internal admission diagnostic before the gate presentation cap:')
for reason in capture.get('bad', []):
    print(reason)
print('screened_in_not_pooled:', membership.build_outcome_membership(outcome, review['screening']['records'])['screened_in_not_pooled'])
fams = {f['family_id']: f for f in review['trial_families']}
for row in outcome['trials']:
    v = admission.verdict(row, fams.get(row.get('family_id')))
    print(row['id'], 'raw eligibility', (fams.get(row.get('family_id'), {}).get('eligibility') or {}).get('state'),
          'effective eligibility', v['predicates']['P5_family_eligible']['eligibility_state'],
          v['predicates']['P5_family_eligible']['absence_code'], 'expected', v['final'], 'failing', v['failing'])
```

Denominator and emitted-name measurement body:

```python
import collections
import json
from pathlib import Path
from harness import admission, membership

source = json.loads(Path('docs/reviews/probiotics-aad-prevention/review.json').read_text(encoding='utf-8'))
primary = next(o for o in source['outcomes'] if o.get('primary'))
victim = primary['trials'][0]
base_in = {membership.canonical_trial_key(r['id']) for r in source['screening']['records'] if r.get('decision') == 'include'}
refused = 0
for name in ('V1','V2','V3','V4','V5','V6'):
    text = Path('.tmp', f'Gate_{name}.log').read_text(encoding='utf-8')
    detail = Path('.tmp', f'Admission_detail_{name}.log').read_text(encoding='utf-8')
    r = json.loads(Path('.tmp/rt', name, 'review.json').read_text(encoding='utf-8'))
    o = next(o for o in r['outcomes'] if o.get('primary'))
    affected = [victim['id']] if name in ('V1','V2','V3') else [t['id'] for t in primary['trials']]
    admission_reason = '\n'.join(line for line in text.splitlines() if 'L1: admission not enforced' in line)
    is_refused = text.startswith('GATE REFUSE')
    refused += is_refused
    screened = {membership.canonical_trial_key(x['id']) for x in r['screening']['records'] if x.get('decision') == 'include'}
    print(name, 'gate refused', int(is_refused), 'of 1 variant',
          'affected trials named in emitted refusal', sum(t in text for t in affected), 'of',len(affected),
          'affected trials named in emitted admission reason',sum(t in admission_reason for t in affected),'of',len(affected))
    print('  included denominator',len(screened),'of',len(base_in),'original included records;',
          'vanished',membership.build_outcome_membership(o,r['screening']['records'])['screened_in_not_pooled'])
    if name in ('V4','V6'):
        fs={f['family_id']:f for f in r['trial_families']}
        counts=collections.Counter(admission.verdict(t,fs[t['family_id']])['final'] for t in o['trials'])
        print('  recomputed primary finals',dict(counts),'denominator',len(o['trials']),'primary rows')
print('gate refused variants',refused,'of 6 requested variants')
records=json.loads(Path('cache/probiotics-aad-prevention/records.json').read_text(encoding='utf-8'))
matches=[(x['id'],x.get('nct')) for x in records['records'] if str(x['id']) == victim['id'].replace('PMID ','')]
print('victim source record lookup:',matches)
print('verifier mirror byte-identical',Path('scripts/verify_bundle.py').read_bytes()==Path('docs/scripts/verify_bundle.py').read_bytes())
```

### Red-team interpretation

The requested variants are refused **6 of 6**. This is not evidence that every attempted deletion receives a visible, trial-specific admission refusal.

| Variant | Full gate | Does an emitted refusal name the affected trial? | What actually catches it |
| --- | --- | --- | --- |
| V1: remove the primary row | REFUSE | No: **0 of 1 dropped trials** named | The vanished-row check internally identifies `PMID 35727573`, but the output cap hides it. Visible refusals include stale review/render hashes, certificate mismatch, replay mismatch, dependent claimgraph state, and missing stamps on other rows. |
| V2: also remove its screening record | REFUSE | No: **0 of 1 dropped trials** named | The independent-in-shape denominator shrinks to **56 of 57 originally included records** and the vanished list becomes empty. The deletion is covered here by integrity/dependency/replay failures, not by a trial-specific admission catch. |
| V3: also remove its family, retaining screening | REFUSE | No: **0 of 1 dropped trials** named | The screening denominator stays **57 of 57 originally included records**. The vanished-row check still internally identifies the dropped trial, hidden by the same cap. Family deletion does not shrink the membership denominator. |
| V4: forge primary family eligibility | REFUSE | Yes: **8 of 11 altered trials** named | Unstamped-row refusals name altered trials. Raw ELIGIBLE does not override missing registry parents. This experiment does not demonstrate rejection of the forged span itself. |
| V5: forge primary ADMISSIBLE stamps only | REFUSE | Yes: **8 of 11 altered trials** named | The gate recomputes from unchanged UNKNOWN families and reports stamp disagreement. |
| V6: forge both family cells and stamps | REFUSE | Yes: **8 of 11 altered trials** named | `check_admission_enforced` itself refuses: **2 of 11 primary rows** recompute as MIGRATION_STATE_UNBOUND_LEGACY, and **9 of 11** as INADMISSIBLE with REGISTRY_PARENT_UNRESOLVED. Every supplied ADMISSIBLE stamp disagrees. |

The dropped row is verified against the held `cache/probiotics-aad-prevention/records.json`: record `35727573` carries `NCT03334604`, matching the on-disk pooled row. Its source identity is read, not fabricated. The fixture copies each preserve **6 of 6 source directory files**. V1–V3 retain **10 of 11 original primary pooled rows**; V4–V6 retain **11 of 11**.

The cap is `bad[:8]` in `harness/gate.py:1381`, with a `+... more` suffix. The report preserves every CLI refusal verbatim above. The supplementary diagnostic uses `sys.settrace` only to read the local `bad` list when the unmodified check returns; it exposes hidden reasons without changing the gate or implementing a second decision function. Those supplemental reasons must not be misreported as reasons printed by the CLI. The raw CLI and diagnostic outputs distinguish them.

All copies also emit `COMPARATOR_PANEL: registered source panel missing`. This is a copy-path confound, not an attack catch: `harness/gate.py:1235` derives the comparator cache slug from the directory basename (`V1`, etc.), rather than the review's stored slug. The replay and certificate failures likewise include the already-applied source change; a refusal in those categories alone cannot establish that a specific attack is caught. The untouched-page results were measured independently in Part 2.

V6 also retains absent summaries and unstamped non-primary rows. The branch in the prompt conditional on V6 *not* being refused is not reached. In this run the cache/page eligibility-state comparison is bypassed for primary rows by the earlier stamp-disagreement `continue`; it is incorrect to attribute the V6 refusal to that comparison. `effective_eligibility` preserves a forged ELIGIBLE cell when the family already has registry identity and held report IDs; it does not validate `span={"forged": true}`.

### Which denominator is independent, and what shrinks it?

`harness/gate.py:1325` reads `review.json.screening.records`, and `:1364` passes that list directly to `membership.build_outcome_membership`. The latter (`harness/membership.py:134`) selects `decision == "include"`, converts record IDs, and deduplicates them; `:139` canonicalizes the IDs accounted for by `trials`, `declared_absent_trials`, and `design_refusals`. `screened_in_not_pooled` is the difference. It recomputes this membership rather than trusting an outcome's saved membership object.

This denominator is independent of the outcome's pooled rows and its `trial_families`, but **not independent of the editable review object**. Deleting a screening record, changing its decision away from include, blanking its ID, or making IDs collapse under canonicalization can shrink it. Deleting the screening block altogether supplies an empty list. Removing an outcome avoids that outcome's check. Deleting only a trial family does not shrink it. Adding the trial ID to an absent/refusal list can discharge the accounting obligation without demonstrating that the associated reason or evidence is sound.

| Other protection | What it covers | Boundary |
| --- | --- | --- |
| Live census / manifest / served HTML | Byte or canonical-object edits without consistent regeneration | Integrity and consistency, not semantic truth. V1–V6 show stale-review/render failures. |
| Certificate (`harness/certificate.py:177`, `:243`) | Recomputes review, manuscript, code, corpus, extraction, family-map and other hashes; rejects stale saved certificates | The screening digest is `_hash(review['screening'])` at `:208`; it is not a separately acquired denominator. `trial_family_map_sha256` at `:210` hashes current family-cache content. A newly consistent certificate authenticates consistency with those inputs, not truth of their eligibility assertions. |
| Screening ledger SHA | Detects a screening edit against the saved certificate | A consistent regenerated certificate can carry the new screening digest. Hash equality does not re-adjudicate exclusions. |
| Offline replay (`harness/gate.py:640`) | Regenerates the review from committed records/config and registration identity, and compares the regenerated review hash to the manifest | A forged review/denominator that the actual producer cannot generate is caught, even after merely updating its hashes. It is not an independently acquired source-of-truth check for coordinated edits to producer inputs. |
| Certified-family comparison (`harness/gate.py:1354`) | On rows that reach it, requires a matching family and matching *effective state* in the nonempty cache | Compares state only, not eligibility spans or absence-code details; does not run for an absent/empty certified map and does not validate semantic evidence. Missing stamp or stamp mismatch returns to the row loop before this comparison. |
| Honest ratchet (`harness/honest_ratchet.py:170`, `:207`, `:242`, `:306`) | Cross-version rendered marker decreases, lost tracked absent/banner blocks, parity changes, and changed pooled result tuples require applicable acknowledgements/notices, including entered/left IDs for changed results | A separate whole-tree check, called by `scripts/verify_all.py:233`, not by `gate_page`. `compare_results` skips an unchanged result tuple and skips an outcome missing from the new review. It is not a general immutable inclusion ledger. Byte-edited variants retaining original result fields do not by themselves demonstrate this ratchet catch. |

**What these checks do not establish:** semantic validity of an eligibility span, correctness of a fresh screening exclusion, completeness of a jointly revised source corpus, or authorization/independent truth of internally consistent producer assertions. The admission check also compares only stamp `final`/`failing`, not all stamped predicate detail, and accepts summary state labels without comparing the full summary to recomputation. No claim is made that those gaps alone yield a passing full-page exploit; other checks may reject a particular inconsistent construction.

**Forged-cache rebuild distinction:** changing only `cache/<slug>/families.json` is not a demonstrated full-gate bypass. The ordinary producer calls `trial_family.prepare` (`harness/pipeline.py:1825`) using records and `family_registry.json`/discovery/protocol ingredients (`harness/trial_family.py:380`), rather than loading the stored `families.json` as its admission input. Its regenerated UNKNOWN states can disagree with a forged cache; a forged review that cannot be reproduced is also rejected. `scripts/build_families.py:20` offers `--offline --check` to regenerate and compare family-cache bytes. Conversely, if an attacker controls the actual eligibility-producing ingredients and regenerates all dependent review/cache/certificate objects consistently, shared state equality, current-input hashes, and replay alone do not establish the truth of that evidence. The honest ratchet may still require notices for changed results or removed disclosures. This is a source-level trust-boundary finding, not an executed successful consistent-rebuild attack. No served page was rebuilt to test it.

## Part 4 — reader inventory and second implementations


### Patched-tree executable reader grep

Command:

```text
rg -n verification_rows|admission_verdict|admission_summary|effective_eligibility --glob *.py --glob *.js --glob *.ts --glob *.html --glob !.tmp/** --glob !docs/evidence/** --glob !docs/reviews/** .
```

Real output:

```text
.\docs\scripts\verify_bundle.py:750:    for br in bundle["verification_rows"]:
.\docs\scripts\verify_bundle.py:788:    bundle_rows = {r["trial"]["id"].replace("PMID ", ""): r for r in bundle["verification_rows"]}
.\docs\scripts\verify_bundle.py:1158:                                   for r in bundle["verification_rows"] if "statistical_input" in r}
.\harness\trial_family.py:462:def effective_eligibility(f):
.\harness\trial_family.py:499:        f['eligibility'] = effective_eligibility(f)
.\harness\pipeline.py:1464:    out["admission_summary"] = admission_mod.summary(out)
.\harness\page.py:1646:    rendered from the outcome's admission_summary object, never typed. A page with no summary renders no block --
.\harness\page.py:1649:    s = o.get("admission_summary")
.\harness\gate.py:1300:    from .trial_family import effective_eligibility as _eff
.\harness\gate.py:1336:            stamp = t.get("admission_verdict") if isinstance(t.get("admission_verdict"), dict) else None
.\harness\gate.py:1372:        s = o.get("admission_summary")
.\harness\admission.py:14:    P5_family_eligible   the trial family's EFFECTIVE eligibility state == ELIGIBLE (trial_family.effective_eligibility:
.\harness\admission.py:38:from .trial_family import effective_eligibility
.\harness\admission.py:54:    "where_the_rest_is_evaluated": "scripts/build_bundle.py (verification_rows) against the bundle's own acquisition, "
.\harness\admission.py:84:    el = effective_eligibility(family) if family else None
.\harness\admission.py:88:          "basis": "trial_family.effective_eligibility on the family ledger the build was handed" if family else
.\harness\admission.py:112:    el = effective_eligibility(family) if family else {}
.\harness\admission.py:124:        "admission_verdict": v,
.\harness\admission.py:140:    """Stamp every candidate row with its verdict (row key admission_verdict -- `admission` is the eligibility chain's
.\harness\admission.py:149:        t["admission_verdict"] = v
.\harness\admission.py:164:    stamped = [t for t in pooled if isinstance(t.get("admission_verdict"), dict)]
.\harness\admission.py:165:    unstamped = [str(t.get("id")) for t in pooled if not isinstance(t.get("admission_verdict"), dict)]
.\harness\admission.py:166:    finals = {str(t.get("id")): t["admission_verdict"].get("final") for t in stamped}
.\harness\admission.py:182:                                   if t["admission_verdict"]["predicates"]["P8_endpoint_bound"].get("bundle_rule_agreement") == "OTHER_ROUTE"),
.\harness\absence.py:281:    if row.get("state") in ADMISSION_SET_ASIDE_STATES and isinstance(row.get("admission_verdict"), dict):
.\tests\test_bundle_verifier.py:260:    for r in b["verification_rows"]:
.\tests\test_bundle_verifier.py:335:    for r in b["verification_rows"]:
.\tests\test_bundle_verifier.py:450:    row = next(r for r in b["verification_rows"] if r["trial"]["id"] == "PMID 27633186")
.\tests\test_bundle_verifier.py:624:    row = next(r for r in b["verification_rows"] if r["trial"]["id"] == "PMID 27633186")
.\tests\test_bundle.py:192:    row = next(r for r in bundle["verification_rows"] if r["trial"]["id"] == "PMID 40162642")
.\tests\test_bundle.py:253:def test_verification_rows_cover_the_pool_and_carry_all_six_objects(bundle):
.\tests\test_bundle.py:256:    assert [r["trial"]["id"] for r in bundle["verification_rows"]] == [t["id"] for t in primary["trials"]]
.\tests\test_bundle.py:257:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:267:    row = next(r for r in bundle["verification_rows"] if r["trial"]["id"] == "PMID 30291013")
.\tests\test_bundle.py:274:    rows = {r["trial"]["id"]: r for r in bundle["verification_rows"]}
.\tests\test_bundle.py:306:    shared = {r["source"]["source_sha256"] for r in bundle["verification_rows"]}
.\tests\test_bundle.py:308:    assert all("container digest + deterministic selector" in r["source"]["identity"] for r in bundle["verification_rows"])
.\tests\test_bundle.py:313:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:325:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:348:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:353:    soul = next(r for r in bundle["verification_rows"] if r["trial"]["id"] == "PMID 40162642")["statistical_input"]
.\tests\test_bundle.py:382:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:431:    assert all(r["admission"]["predicates"]["P8_endpoint_bound"]["state"] == "PASS" for r in bundle["verification_rows"])
.\tests\test_bundle.py:449:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:464:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:476:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:492:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:502:    assert all("point estimate" in r["producer_label_scope"] for r in bundle["verification_rows"])
.\tests\test_bundle.py:594:    return _load(BUNDLE)["verification_rows"]
.\tests\test_bundle.py:601:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:631:    assert any(l["id"] == "L13_location_by_full_text_and_offsets" for l in bundle["limits"]) and any(l["id"] == "L14_verification_rows_source_pubmed_only" for l in bundle["limits"])
.\tests\test_bundle.py:641:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:660:    bases = [r["analysis_identity"]["analysis_set"]["basis"] for r in bundle["verification_rows"]]
.\tests\test_bundle.py:668:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:676:    assert sum(1 for r in bundle["verification_rows"] if r["statistical_input"]["ci_level"]["level_agreement"] == "MATCH") == 8   # all eight clauses state '95%'
.\tests\test_bundle.py:695:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:707:    for r in bundle["verification_rows"]:
.\tests\test_bundle.py:715:    assert all(r["admission"]["predicates"]["P2_span_located"]["typed_state"] == "LOCATED" for r in bundle["verification_rows"])
.\tests\test_bundle.py:823:    for r in bundle["verification_rows"]:
.\tests\test_admission_enforced.py:88:    assert a["admission_verdict"]["final"] == "INADMISSIBLE" and a["admission_verdict"]["failing"] == ["P5_family_eligible"]
.\tests\test_admission_enforced.py:90:    assert kept[0]["admission_verdict"]["final"] == "ADMISSIBLE"
.\tests\test_admission_enforced.py:106:    assert aside == [] and kept[0]["admission_verdict"]["final"] == "MIGRATION_STATE_UNBOUND_LEGACY"
.\tests\test_admission_enforced.py:107:    assert kept[0]["admission_verdict"]["failing"] == ["P8_endpoint_bound"]
.\tests\test_admission_enforced.py:117:    assert aside[0]["admission_verdict"]["predicates"]["P5_family_eligible"]["eligibility_state"] is None
.\tests\test_admission_enforced.py:130:    pooled = [t for t in control["trials"] if t["admission_verdict"]["final"] == "ADMISSIBLE"]
.\tests\test_admission_enforced.py:157:        out["admission_summary"] = admission.summary(out)
.\tests\test_admission_enforced.py:166:        rev["outcomes"][1]["admission_summary"] = admission.summary(rev["outcomes"][1])
.\tests\test_admission_enforced.py:253:    finals = {r["admission"]["final"] for r in b["verification_rows"]}
.\tests\test_admission_enforced.py:255:    bundle_predicates = {k for r in b["verification_rows"] for k in r["admission"]["predicates"]}
.\scripts\verify_bundle.py:750:    for br in bundle["verification_rows"]:
.\scripts\verify_bundle.py:788:    bundle_rows = {r["trial"]["id"].replace("PMID ", ""): r for r in bundle["verification_rows"]}
.\scripts\verify_bundle.py:1158:                                   for r in bundle["verification_rows"] if "statistical_input" in r}
.\scripts\admission_census.py:12:  unstamped pooled rows  a pooled row without admission_verdict (a page built before the build read the decision)
.\scripts\admission_census.py:53:                v = t.get("admission_verdict") if isinstance(t.get("admission_verdict"), dict) else None
.\scripts\admission_census.py:60:                                 "final": "INADMISSIBLE", "stamped": isinstance(a.get("admission_verdict"), dict),
.\scripts\build_bundle.py:161:    {"id": "L14_verification_rows_source_pubmed_only", "limit": "verification_rows[] bind rows whose evidence is a PubMed record in records.json; a row "
.\scripts\build_bundle.py:262:        "ASSESSED": "the row was run through the admission predicates (verification_rows) or the absence rule (absence_claims); its result stands beside it",
.\scripts\build_bundle.py:660:            "outcome_understood": {"state": "PRODUCER_ASSERTION", "basis": "the page's endpoint_binding / adjudication fields are the producer's; carried in verification_rows, not independently adjudicated"}}
.\scripts\build_bundle.py:1220:                            "(certified as review_sha256), which verification_rows[*].source binds to the container + selector + span. "
.\scripts\build_bundle.py:1276:def verification_rows(slug: str, review: dict, docs_by_id: dict, art_by_ref: dict, records: dict) -> tuple[list[dict], dict]:
.\scripts\build_bundle.py:1561:                   "in_verification_rows": bool(o.get("primary")) and t.get("id") in primary_ids,
.\scripts\build_bundle.py:1903:                st = assessment_state(t, f"verification_rows: {fin}", unresolved=(p9 == "AMBIGUOUS_ENDPOINT_BINDING"),
.\scripts\build_bundle.py:1906:                st = assessment_state(t, "rendered harms row; not a verification row (verification_rows cover the primary pool)",
.\scripts\build_bundle.py:2234:    vrows, vmeta = verification_rows(slug, review, docs_by_id, art_by_ref, records)
.\scripts\build_bundle.py:2275:            {"subject": "raw served bytes", "procedure": "sha256(bytes)", "value": _sha256(rec_raw), "appears_as": "artefacts[].sha256; verification_rows[].source.source_sha256; verified_*.json document_sha256"},
.\scripts\build_bundle.py:2366:        "verification_rows": vrows,
```

Native exit code: `0`.

### Verdict computing and call sites

Command:

```text
rg -n "P5_family_eligible.*(PASS|ELIGIBLE)|P8_endpoint_bound.*(PASS|endpoint_binding)|final =|_adm.verdict|admission_mod.admit|v = verdict" harness/admission.py harness/gate.py harness/pipeline.py scripts/build_bundle.py scripts/verify_bundle.py docs/scripts/verify_bundle.py
```

Real output:

```text
harness/pipeline.py:1320:    trials, _not_admitted = admission_mod.admit(trials, family_nodes, spec)
harness/gate.py:1335:            expect = _adm.verdict(t, fam)
harness/admission.py:14:    P5_family_eligible   the trial family's EFFECTIVE eligibility state == ELIGIBLE (trial_family.effective_eligibility:
harness/admission.py:18:    P8_endpoint_bound    endpoint_binding is a producer binding route other than unbound_legacy. NOTE the divergence
harness/admission.py:56:    "rule": "final = ADMISSIBLE if no evaluated predicate fails; MIGRATION_STATE_UNBOUND_LEGACY if P8 is the only failing "
harness/admission.py:98:    final = ("ADMISSIBLE" if not failing else
harness/admission.py:148:        v = verdict(t, fam)
docs/scripts/verify_bundle.py:899:            "P5_family_eligible": elig == "ELIGIBLE",
docs/scripts/verify_bundle.py:902:            "P8_endpoint_bound": t.get("endpoint_binding") == "named_endpoint_resolved_to_definition_span",
docs/scripts/verify_bundle.py:960:        final = ("ADMISSIBLE" if not failing else
docs/scripts/verify_bundle.py:961:                 "MIGRATION_STATE_UNBOUND_LEGACY" if failing == ["P8_endpoint_bound"] and t.get("endpoint_binding") == "unbound_legacy" else
docs/scripts/verify_bundle.py:978:                               "agrees_with_bundle": (final == recorded) if not corrupt else None,
scripts/verify_bundle.py:899:            "P5_family_eligible": elig == "ELIGIBLE",
scripts/verify_bundle.py:902:            "P8_endpoint_bound": t.get("endpoint_binding") == "named_endpoint_resolved_to_definition_span",
scripts/verify_bundle.py:960:        final = ("ADMISSIBLE" if not failing else
scripts/verify_bundle.py:961:                 "MIGRATION_STATE_UNBOUND_LEGACY" if failing == ["P8_endpoint_bound"] and t.get("endpoint_binding") == "unbound_legacy" else
scripts/verify_bundle.py:978:                               "agrees_with_bundle": (final == recorded) if not corrupt else None,
scripts/build_bundle.py:356:        "P5_family_eligible": "the trial family's eligibility state == ELIGIBLE",
scripts/build_bundle.py:359:        "P8_endpoint_bound": "endpoint_binding == named_endpoint_resolved_to_definition_span (an unbound_legacy row is a migration state, see binding_classes)",
scripts/build_bundle.py:1332:            "P5_family_eligible": {"state": "PASS" if elig == "ELIGIBLE" else "FAIL", "family_id": t.get("family_id"), "eligibility_state": elig,
scripts/build_bundle.py:1339:            "P8_endpoint_bound": {"state": "PASS" if t.get("endpoint_binding") == "named_endpoint_resolved_to_definition_span" else "FAIL",
scripts/build_bundle.py:1367:        final = ("ADMISSIBLE" if not failing else
scripts/build_bundle.py:1368:                 "MIGRATION_STATE_UNBOUND_LEGACY" if failing == ["P8_endpoint_bound"] and t.get("endpoint_binding") == "unbound_legacy" else
```

Native exit code: `0`.

### Every matched executable-source location

READ includes checking, aggregating, asserting, or rendering an existing object. Delegated calls to the canonical function do not create a new algorithm. Metadata and writes are explicitly distinguished.

| File:line | Classification |
| --- | --- |
| `docs/scripts/verify_bundle.py:750` | READS bundle verification_rows here; the enclosing run() separately RECOMPUTES verdicts at :899/:902/:960. |
| `docs/scripts/verify_bundle.py:788` | READS bundle verification_rows here; the enclosing run() separately RECOMPUTES verdicts at :899/:902/:960. |
| `docs/scripts/verify_bundle.py:1158` | READS bundle verification_rows here; the enclosing run() separately RECOMPUTES verdicts at :899/:902/:960. |
| `harness/absence.py:281` | READS the stored verdict/summary (or its presence); no independent verdict computation. |
| `harness/admission.py:14` | DOCUMENTATION; no read or computation. |
| `harness/admission.py:38` | IMPORTS the shared eligibility helper; no verdict computation here. |
| `harness/admission.py:54` | SCOPE metadata naming the bundle; not a reader. |
| `harness/admission.py:84` | COMPUTES the canonical in-build verdict in verdict(), using effective eligibility; final logic at :98. |
| `harness/admission.py:88` | Provenance text inside verdict(); same implementation, not another one. |
| `harness/admission.py:112` | READS effective eligibility to retain refusal evidence; no new verdict. |
| `harness/admission.py:124` | WRITES the verdict already supplied to set_aside_record. |
| `harness/admission.py:140` | DOCUMENTATION for admit(). |
| `harness/admission.py:149` | WRITES the result of verdict() called at :148; delegates, not another algorithm. |
| `harness/admission.py:164` | READS the stored verdict/summary (or its presence); no independent verdict computation. |
| `harness/admission.py:165` | READS the stored verdict/summary (or its presence); no independent verdict computation. |
| `harness/admission.py:166` | READS the stored verdict/summary (or its presence); no independent verdict computation. |
| `harness/admission.py:182` | READS the stored verdict/summary (or its presence); no independent verdict computation. |
| `harness/gate.py:1300` | IMPORTS shared effective eligibility for cache/page comparison; not a verdict algorithm. |
| `harness/gate.py:1336` | READS the stored verdict/summary (or its presence); no independent verdict computation. |
| `harness/gate.py:1372` | READS the stored verdict/summary (or its presence); no independent verdict computation. |
| `harness/page.py:1646` | DOCUMENTATION; rendering reads at :1649. |
| `harness/page.py:1649` | READS the stored verdict/summary (or its presence); no independent verdict computation. |
| `harness/pipeline.py:1464` | WRITES a summary derived by admission.summary; calls admission.admit at :1320 to enforce the shared verdict. |
| `harness/trial_family.py:462` | COMPUTES effective eligibility (registry-parent/source-presence overrides), not the final P5/P8 admission verdict. |
| `harness/trial_family.py:499` | CALLS that eligibility helper and writes its cell; no separate admission algorithm. |
| `scripts/admission_census.py:12` | DOCUMENTATION of unstamped rows. |
| `scripts/admission_census.py:53` | READS the stored verdict/summary (or its presence); no independent verdict computation. |
| `scripts/admission_census.py:60` | READS stamp presence, but DERIVES the set-aside final label INADMISSIBLE from a state marker (:58), not from the stamp final. No P5/P8 evaluation. |
| `scripts/build_bundle.py:161` | DOCUMENTATION / emitted schema metadata; not a verdict reader or computing site. |
| `scripts/build_bundle.py:262` | DOCUMENTATION / emitted schema metadata; not a verdict reader or computing site. |
| `scripts/build_bundle.py:660` | DOCUMENTATION / emitted schema metadata; not a verdict reader or computing site. |
| `scripts/build_bundle.py:1220` | DOCUMENTATION / emitted schema metadata; not a verdict reader or computing site. |
| `scripts/build_bundle.py:1276` | COMPUTES a separate bundle verdict; own P5/P8 at :1332/:1339 and final at :1367. |
| `scripts/build_bundle.py:1561` | DERIVES row coverage membership; no admission verdict computation. |
| `scripts/build_bundle.py:1903` | READS the bundle final fin to describe assessment state. |
| `scripts/build_bundle.py:1906` | Metadata for non-verification harms assessment; no admission computation. |
| `scripts/build_bundle.py:2234` | CALLS its own verification_rows computing implementation; does not read the build stamp. |
| `scripts/build_bundle.py:2275` | DOCUMENTATION / emitted schema metadata; not a verdict reader or computing site. |
| `scripts/build_bundle.py:2366` | WRITES the computed bundle verification rows. |
| `scripts/verify_bundle.py:750` | READS bundle verification_rows here; the enclosing run() separately RECOMPUTES verdicts at :899/:902/:960. |
| `scripts/verify_bundle.py:788` | READS bundle verification_rows here; the enclosing run() separately RECOMPUTES verdicts at :899/:902/:960. |
| `scripts/verify_bundle.py:1158` | READS bundle verification_rows here; the enclosing run() separately RECOMPUTES verdicts at :899/:902/:960. |
| `tests/test_admission_enforced.py:88` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_admission_enforced.py:90` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_admission_enforced.py:106` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_admission_enforced.py:107` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_admission_enforced.py:117` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_admission_enforced.py:130` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_admission_enforced.py:157` | FIXTURE WRITE using admission.summary; no separate verdict algorithm. |
| `tests/test_admission_enforced.py:166` | FIXTURE WRITE using admission.summary; no separate verdict algorithm. |
| `tests/test_admission_enforced.py:253` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_admission_enforced.py:255` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:192` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:253` | TEST function name; its body reads/asserts bundle rows. |
| `tests/test_bundle.py:256` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:257` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:267` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:274` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:306` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:308` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:313` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:325` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:348` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:353` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:382` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:431` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:449` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:464` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:476` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:492` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:502` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:594` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:601` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:631` | READS metadata-limit identifiers, not verdicts. |
| `tests/test_bundle.py:641` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:660` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:668` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:676` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:695` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:707` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:715` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle.py:823` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle_verifier.py:260` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle_verifier.py:335` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle_verifier.py:450` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |
| `tests/test_bundle_verifier.py:624` | READS/asserts or mutates a test fixture; does not implement the production admission policy. |

### Classified readers and physical verdict sites

Command:

```text
python .tmp/lane_part4.py
```

Real output:

```text
classified matches 86 of 86 matched executable-source lines
verdict computation: harness/admission.py:98 verdict
verdict computation: scripts/build_bundle.py:1367 verification_rows
verdict computation: scripts/verify_bundle.py:960 run
verdict computation: docs/scripts/verify_bundle.py:960 run
canonical in-build computing site 1 of 4 physical computing sites
noncanonical physical sites 3 of 4 physical computing sites
mirrored verifier byte equality: True
distinct verdict algorithms after collapsing identical mirror: 3 of 4 physical sites
```

Native exit code: `0`.

### Generated HTML token search

Command:

```text
rg -n -o verification_rows|admission_verdict|admission_summary|effective_eligibility docs/reviews docs/evidence --glob *.html
```

Real output:

```text

```

Native exit code: `1`.

### Verify supplied patch is fully applied

Command:

```text
git apply --reverse --check source.patch
```

Real output:

```text

```

Native exit code: `0`.

### Whitespace validation

Command:

```text
git diff --check
```

Real output:

```text

```

Native exit code: `0`.

### Second-implementation finding

The claim of exactly one computing site is **false across the inspected production tree**. The AST/source check identifies **4 of 4 physical combined-verdict sites**, representing **3 distinct algorithms across those 4 sites** after collapsing the byte-identical verifier mirror:

| Computing location | Actual policy source |
| --- | --- |
| `harness/admission.py:82` / final at `:98` | The shared in-build algorithm. `admit()` and `gate.check_admission_enforced()` call it rather than duplicating its policy. This is **1 of 4 physical sites**. |
| `scripts/build_bundle.py:1276` / final at `:1367` | A separate bundle algorithm computing P5, P8, other predicates, and its own final. It does not consume the build's admission_verdict. |
| `scripts/verify_bundle.py:688` / final at `:960` | A separate verifier recomputing predicates and final from bundled inputs. Its independent-verifier purpose does not turn it into a read-only consumer. |
| `docs/scripts/verify_bundle.py:688` / final at `:960` | A byte-identical shipped copy of the preceding algorithm. |

The noncanonical implementations occupy **3 of 4 physical sites**. The narrower claim that the pipeline and page gate share their in-build P5/P8 decision is supported. The wider claim that every consumer only reads that decision is not.

There is an explicit policy divergence: the in-build verdict reads `effective_eligibility` and lets any nonempty binding other than `unbound_legacy` pass P8 (`harness/admission.py:84`, `:91`). The bundle builder and independent verifier read the cached raw eligibility state and require exactly `named_endpoint_resolved_to_definition_span` (`scripts/build_bundle.py:1332`, `:1339`; `scripts/verify_bundle.py:899`, `:902`). They also evaluate additional predicates. Their verdicts cannot be assumed interchangeable. The patch's SCOPE text acknowledges this P8 difference, but acknowledgement does not eliminate the separate implementations.

`scripts/admission_census.py:60` is also not a pure verdict reader for set-aside rows: it derives an INADMISSIBLE label from the set-aside state and checks stamp presence, rather than reading the stamp's final. This is a state-to-label classification, not another P5/P8 policy algorithm; it is called out separately rather than hidden in the computing-site count. `trial_family.effective_eligibility` computes the shared eligibility input, not a combined final verdict. Test fixtures and the deliberately forged audit fixtures do not constitute production policy implementations.

The generated review/evidence HTML token search returns no matches (native `rg` exit code `1` means no matches). The executable-source inventory includes the shipped verifier mirror and tests; archived data objects containing these fields are payloads, not executable readers. The classification was cross-checked against the saved whole-tree executable grep; every matched file:line is classified.

### Completion boundaries

This is a completed reproduction/red-team audit, not a release certification or a repair of its findings. The requested admission plants passed **12 of 12 tests** after patch application; **6 of 6 requested adversarial copies** were refused, with the trial-naming and denominator limits documented above. The requested census correctly remained nonzero on untouched legacy pages. No full repository test suite, deployment, or successful forged-input rebuild is claimed. The supplied patch remains applied and uncommitted. No served page was regenerated. No source changes beyond the supplied patch were made.

Audit helper scripts and raw per-command logs remain under `.tmp`; the evidence, interpretation, commands, and full gate outputs needed for review are consolidated in `LANE_REPORT.md`. `PROGRESS.md` is an ignored checkpoint, not a committed artefact. The final preservation check below compares held files to the lane's hash snapshot and checks tracked served/cache changes against the initial HEAD.


### Served pages and cache preservation

Command:

```text
python .tmp/lane_preservation.py
```

Real output:

```text
docs/reviews/ unchanged 194 of 194 baseline files
changed or missing: []
added: []
cache/ unchanged 937 of 937 baseline files
changed or missing: []
added: []
tracked served/cache diff against initial HEAD:
(empty)
HEAD: 38c04411484dbea035a8e4c8e22c57c2794f9495
report UTF-8: True BOM: False
```

Native exit code: `0`.

Final preservation result: **194 of 194 baseline served review files** and **937 of 937 baseline cache files** are unchanged; no added, missing, or modified files in those sets. The tracked served/cache diff against initial HEAD is empty. The supplied patch reverse-check and `git diff --check` both exited with code `0`. The report is UTF-8 without BOM. No commit was made.
