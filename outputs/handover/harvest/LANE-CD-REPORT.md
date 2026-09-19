# Lane CD report

Base/finish HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit, checkout, reset, stash or push. Replay and browser checks blocked external network; the final broad test run uses a network guard. Generated corpus is confined to `.tmp/cd/docs/`; tracked `docs/` is unchanged.

## MEASURED

- Pre-fix plants: **2 failed**, before implementation. Both named failures were reproduced verbatim from the committed GLP-1 review rendered with base code.
- Post-fix focused suite: **24 passed**. Command (PowerShell wildcards expanded to the matching test files): `python -X utf8 -m pytest tests/test_declared_enforced_not_established.py tests/test_propositions*.py tests/test_protocol_compiler*.py -q`.
- Offline replay: **32/32 PASS** from each committed topic config and `cache/<slug>/records.json`, through `build_review_core` and `build_review_dir`, with `AACT_DIR=.tmp/empty_aact` (exists and verified empty). Network socket calls were blocked in the replay. Output: `.tmp/cd/docs/reviews/<slug>/`. `certify=False`: this is a lane replay, not a release certification.
- Browser E2E: **PASS** at `http://127.0.0.1:8000/`, Chrome/Playwright, external requests aborted. Served baseline reproduces the vacuous sentence and tick. Served legacy post-fix shows NOT ESTABLISHED with no tick. Rebuilt post-fix names real checked dimensions, shows ESTABLISHED only for those dimensions, no tick. No page errors. Evidence: `.tmp/cd/browser.json`; runner `.tmp/cd/e2e.py`.
- Changed item-5/proposition surfaces: **32 pages**. Rebuilt state distribution: `{'ESTABLISHED': 14, 'DIVERGENT': 18}`. Complete old/new text follows below.
- Full-suite initial command: `python -X utf8 -m pytest -q` → **collection ERROR**, duplicate `test_search_v2_isrctn` module in `outputs/search_v2/lanes/R2/` and `tests/`. No production fix attempted for this unrelated collection layout.

## Implementation and scope

`harness/protocol_compiler.py::comparison` records dimensions that can actually be compared, divergence codes and unchecked eligibility axes; its call site is `propositions.attach`, because `pipeline.py` is outside this lane. It reads repository-relative topic configuration at build time only and preserves recorded comparison evidence on subsequent attachment. Renderers do not read configuration from disk.

`propositions.declared_equals_enforced` derives the explicit state and basis. An empty check set is NOT_ESTABLISHED, retaining any recorded divergences for disclosure; a nonempty set with divergences is DIVERGENT; a nonempty divergence-free set is ESTABLISHED for the named dimensions only. The generated assertion boolean uses that state, and the checker rejects a claimed equality without supporting checks. Both page sentences and the item-5 status cell use the same state. Legacy review objects with no checked-dimension evidence fail closed.

GLP-1 has comparable estimand, analysis-set, intervention declaration and intervention PICO-line evidence. The committed include object has no explicit ascertainment-axis or result-availability boolean, so neither is advertised as checked. Their absence is reported alongside the comparison. An ESTABLISHED state is not a claim that these missing axes, every eligibility rule, or actual trial-level enforcement has been validated.

Renderer diff: `.tmp/patches/page.py.diff`; supporting diffs: `.tmp/patches/propositions.py.diff` and `.tmp/patches/protocol_compiler.py.diff`. No manuscript edit is necessary: the PRISMA row and proposition block both live in page.py.

## Static versus dynamic disclosure

| Component | Static | Dynamic evidence |
|---|---|---|
| State machine | Three state labels and decision rules | Checked dimensions and divergences in the review object |
| Compiler | Supported field names and normalization rules | Local committed prose/config values; no hardcoded research outputs |
| Renderers | Sentence templates | State, basis, checked/unchecked dimensions, divergence codes |
| Plants | Explicitly synthetic zero-check/mismatch fixtures | Committed GLP-1 review rendered by actual page code |
| Corpus/report | Destination and extraction logic | Rebuilt pages, browser DOM text, test logs and git HEAD |

## INFERRED

The former agreement arose from treating an empty divergence list as positive evidence and a missing agreed-dimensions list as “none”. The pre-fix assertions and browser observation establish that failure on this base. Absence of a corresponding include field cannot establish agreement for that axis.

## CLAIMED (bounded)

The lane removes vacuous agreement from the two owned surfaces and records a nonempty comparison where the local sources permit it. No claim is made of complete protocol enforcement, clinical validation, new evidence acquisition, Overmind PASS, release readiness, or deployment.

## Plants, verbatim

```python
import copy
import json
import re
from html import unescape
from pathlib import Path

from harness import page

ROOT = Path(__file__).resolve().parents[1]


def text(html):
    return ' '.join(unescape(re.sub(r'<[^>]+>', ' ', html)).split())


def review():
    return json.loads((ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))


def item5(html):
    return next(text(row) for row in re.findall(r'<tr\b[^>]*>.*?</tr>', html, re.S)
                if '5 Eligibility criteria' in row)


def test_PLANT_committed_glp1_no_vacuous_agreement():
    html = page.render_page(review())
    rendered = text(html)
    row = item5(html)
    vacuous = 'agree on these checked dimensions: none' in rendered
    backed = 'declared == enforced is backed' in row or '✓' in row
    assert not (vacuous and backed and 'NOT ESTABLISHED' not in rendered), row


def test_PLANT_zero_dimension_proposition_never_tick():
    r = copy.deepcopy(review())
    r['protocol_config'] = {'checked_dimensions': [], 'divergences': []}
    state = {'state': 'NOT_ESTABLISHED', 'checked_dimensions': [],
             'divergences': [], 'basis': 'no dimension was checked'}
    r.setdefault('propositions', {})['declared_equals_enforced'] = state
    r['propositions']['objects'] = [dict(kind='declared_equals_enforced', **state)]
    html = page.render_page(r)
    assert 'NOT ESTABLISHED' in text(html)
    assert 'declared == enforced: NOT ESTABLISHED' in item5(html)
    assert '✓' not in item5(html)
```

### Pre-fix output

```text
FF                                                                       [100%]
================================== FAILURES ===================================
_______________ test_PLANT_committed_glp1_no_vacuous_agreement ________________

    def test_PLANT_committed_glp1_no_vacuous_agreement():
        html = page.render_page(review())
        rendered = text(html)
        row = item5(html)
        vacuous = 'agree on these checked dimensions: none' in rendered
        backed = 'declared == enforced is backed' in row or '✓' in row
>       assert not (vacuous and backed and 'NOT ESTABLISHED' not in rendered), row
E       AssertionError: 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.
E       assert not (True and True and 'NOT ESTABLISHED' not in 'GLP-1 recep...set.t);})();'
E         
E         'NOT ESTABLISHED' is contained here:
E           et.t);})();)

tests\test_declared_enforced_not_established.py:31: AssertionError
______________ test_PLANT_zero_dimension_proposition_never_tick _______________

    def test_PLANT_zero_dimension_proposition_never_tick():
        r = copy.deepcopy(review())
        r['protocol_config'] = {'checked_dimensions': [], 'divergences': []}
        state = {'state': 'NOT_ESTABLISHED', 'checked_dimensions': [],
                 'divergences': [], 'basis': 'no dimension was checked'}
        r.setdefault('propositions', {})['declared_equals_enforced'] = state
        r['propositions']['objects'] = [dict(kind='declared_equals_enforced', **state)]
        html = page.render_page(r)
>       assert 'NOT ESTABLISHED' in text(html)
E       assert 'NOT ESTABLISHED' in "GLP-1 receptor agonists vs placebo for 3-point MACE in type 2 diabetes *{box-sizing:border-box}body{font:15px/1.55 sy...gle('active',b.dataset.t===id)});} (function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);})();"
E        +  where "GLP-1 receptor agonists vs placebo for 3-point MACE in type 2 diabetes *{box-sizing:border-box}body{font:15px/1.55 sy...gle('active',b.dataset.t===id)});} (function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);})();" = text("<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=...===id)});}\n(function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);})();</script></body></html>")

tests\test_declared_enforced_not_established.py:42: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_declared_enforced_not_established.py::test_PLANT_committed_glp1_no_vacuous_agreement
FAILED tests/test_declared_enforced_not_established.py::test_PLANT_zero_dimension_proposition_never_tick
2 failed in 29.90s
```

### Post-fix focused output

```text
........................                                                 [100%]
24 passed in 27.38s
```

## Every changed page: old/new rendered text

### balanced-crystalloids-vs-saline-mortality

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### colchicine-postop-af

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: analysis_set, comparator, design_masking, follow_up_window . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: design, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: design, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### colchicine-recurrent-pericarditis

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: design, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: design, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.

### colchicine-secondary-cv-prevention

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.

### corticosteroids-cap-mortality

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 5 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care. , config enforces dexamethasone INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care. , config enforces hydrocortisone INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care. , config enforces methylprednisolone INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care. , config enforces prednisolone INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care. , config enforces prednisone

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care., config enforces dexamethasone INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care., config enforces hydrocortisone INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care., config enforces methylprednisolone INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care., config enforces prednisolone INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says systemic corticosteroids added to standard antimicrobial/supportive care., config enforces prednisone

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE.

### corticosteroids-covid19-mortality

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### dapagliflozin-hfpef-hosp

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.

### denosumab-vertebral-fracture

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: design, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: design, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### doac-vte-recurrence

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: analysis_set, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### dpp4-mace-t2d

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.

### empagliflozin-hfpef-hosp

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.

### esketamine-trd-madrs

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: design, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: design, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### finerenone-ckd-t2d-renal

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.

### glp1-ra-mace-t2d

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### iv-iron-hfref-hosp

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### melatonin-primary-insomnia-sol

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: design, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: design, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### metformin-pcos-ovulation

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: POPULATION_CONTEXT_DIVERGENCE (population): prose says PCOS in an ovulation-induction/subfertility context , config enforces polycystic ovary syndrome, polycystic ovarian syndrome, pcos, polycystic ovaries

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: estimand, intervention_declaration, intervention_i_line, population -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: POPULATION_CONTEXT_DIVERGENCE. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. POPULATION_CONTEXT_DIVERGENCE (population): prose says PCOS in an ovulation-induction/subfertility context, config enforces polycystic ovary syndrome, polycystic ovarian syndrome, pcos, polycystic ovaries

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: estimand, intervention_declaration, intervention_i_line, population. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: POPULATION_CONTEXT_DIVERGENCE.

### noac-vs-warfarin-af-stroke

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: ESTIMAND_PREFERENCE_UNDECLARED (estimand_preference): prose says protocol permits crude count reconstruction and published time-to-event effects , config enforces no explicit preference

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, estimand, estimand_preference, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: ESTIMAND_PREFERENCE_UNDECLARED. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. ESTIMAND_PREFERENCE_UNDECLARED (estimand_preference): prose says protocol permits crude count reconstruction and published time-to-event effects, config enforces no explicit preference

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, estimand, estimand_preference, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: ESTIMAND_PREFERENCE_UNDECLARED.

### omega3-cardiovascular-events

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.

### pcsk9-mace

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.

### probiotics-aad-prevention

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 8 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics. , config enforces BIO-K INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics. , config enforces Florajen INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics. , config enforces LcS INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics. , config enforces bacillus INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics. , config enforces bifidobacter INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics. , config enforces lactobacillus INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics. , config enforces saccharomyces INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics. , config enforces streptococcus thermophilus

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics., config enforces BIO-K INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics., config enforces Florajen INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics., config enforces LcS INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics., config enforces bacillus INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics., config enforces bifidobacter INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics., config enforces lactobacillus INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics., config enforces saccharomyces INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says probiotics, including named probiotic genera, strains, fermented probiotic products, probiotic yogurt/yoghurt, kefir, or synbiotics., config enforces streptococcus thermophilus

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE.

### sacubitril-valsartan-hfref

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### semaglutide-obesity-mace

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.

### semaglutide-obesity-weight

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: design, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: design, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### sglt2-ckd-progression

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 2 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says an sglt2 inhibitor, specifically dapagliflozin, canagliflozin, or empagliflozin, added to background standard care. , config enforces ertugliflozin

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR, INTERVENTION_AGENT_PROSE_DIVERGENCE. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says an sglt2 inhibitor, specifically dapagliflozin, canagliflozin, or empagliflozin, added to background standard care., config enforces ertugliflozin

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR, INTERVENTION_AGENT_PROSE_DIVERGENCE.

### sglt2-hfref-hosp-cvdeath

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 4 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: ESTIMAND_PREFERENCE_UNDECLARED (estimand_preference): prose says protocol permits crude count reconstruction and published time-to-event effects , config enforces no explicit preference DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says an sglt2 inhibitor, specifically dapagliflozin or empagliflozin, added to recommended therapy. , config enforces canagliflozin INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says an sglt2 inhibitor, specifically dapagliflozin or empagliflozin, added to recommended therapy. , config enforces ertugliflozin

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, estimand_preference, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: ESTIMAND_PREFERENCE_UNDECLARED, DESIGN_MASKING_ANDOR, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. ESTIMAND_PREFERENCE_UNDECLARED (estimand_preference): prose says protocol permits crude count reconstruction and published time-to-event effects, config enforces no explicit preference DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says an sglt2 inhibitor, specifically dapagliflozin or empagliflozin, added to recommended therapy., config enforces canagliflozin INTERVENTION_AGENT_PROSE_DIVERGENCE (intervention_i_line): prose says an sglt2 inhibitor, specifically dapagliflozin or empagliflozin, added to recommended therapy., config enforces ertugliflozin

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, estimand_preference, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: ESTIMAND_PREFERENCE_UNDECLARED, DESIGN_MASKING_ANDOR, INTERVENTION_AGENT_PROSE_DIVERGENCE, INTERVENTION_AGENT_PROSE_DIVERGENCE.

### sglt2-primary-prevention-hf

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 2 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled POPULATION_SCOPE_DIVERGENCE (population): prose says broad cardiovascular outcome trials , config enforces type 2 diabetes, type 2 diabetes mellitus, type 2 diabetic, cardiovascular risk, cardiovascular disease, atherosclerotic cardiovascular disease

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line, population -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR, POPULATION_SCOPE_DIVERGENCE. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled POPULATION_SCOPE_DIVERGENCE (population): prose says broad cardiovascular outcome trials, config enforces type 2 diabetes, type 2 diabetes mellitus, type 2 diabetic, cardiovascular risk, cardiovascular disease, atherosclerotic cardiovascular disease

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line, population. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR, POPULATION_SCOPE_DIVERGENCE.

### spironolactone-hfref-mortality

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 2 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: ESTIMAND_DIVERGENCE (estimand): prose says RR , config enforces RR/HR DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: ESTIMAND_DIVERGENCE, DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. ESTIMAND_DIVERGENCE (estimand): prose says RR, config enforces RR/HR DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: ESTIMAND_DIVERGENCE, DESIGN_MASKING_ANDOR.

### statins-primary-prevention-elderly

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### ticagrelor-vs-clopidogrel-acs

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### tocilizumab-covid19-mortality

**proposition — old:** Protocol ↔ config (two independent sources) The prose protocol and executable config agree on these checked dimensions: none . Compared as separate sources.

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line -- declared == enforced ESTABLISHED (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: none. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean.

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.

**item5 — new:** 5 Eligibility criteria ESTABLISHED Protocol tab - eligibility is rendered from the structured include object; declared == enforced: ESTABLISHED. Checked dimensions: analysis_set, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: none.

### tranexamic-acid-pph

**proposition — old:** Protocol ↔ config divergences (two independent sources) The prose protocol and the executable config are compared as SEPARATE sources (a conformance check derived from the config it certifies cannot fail). 1 divergence(s) — each is a defect to resolve or a dated amendment to declare, never a silent widening: DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled , config enforces double-blind OR placebo-controlled

**proposition — new:** Protocol/config (two independent sources) Protocol/config checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line -- declared == enforced DIVERGENT (Committed protocol prose compared with executable topic fields; only listed dimensions are checked.). Divergences: DESIGN_MASKING_ANDOR. Unchecked dimensions: ascertainment_axis: no comparable explicit protocol/include boolean; result_availability_not_axis: no comparable explicit protocol/include boolean. DESIGN_MASKING_ANDOR (design): prose says double-blind AND placebo-controlled, config enforces double-blind OR placebo-controlled

**item5 — old:** 5 Eligibility criteria ✓ present Protocol tab - eligibility is rendered from the structured include object, but protocol/config divergences are disclosed in Reproducibility, so declared == enforced is not asserted.

**item5 — new:** 5 Eligibility criteria DIVERGENT Protocol tab - eligibility is rendered from the structured include object; declared == enforced: DIVERGENT. Checked dimensions: analysis_set, design, estimand, intervention_declaration, intervention_i_line. Committed protocol prose compared with executable topic fields; only listed dimensions are checked.. Divergences: DESIGN_MASKING_ANDOR.


## Second-pass review and verification limits

Reviewed the scoped source diff for identifiers, dates and statistical claims: no trial identifiers, study dates, research estimates or clinical input files were edited. `git diff --exit-code -- docs topics protocols cache` passed. The final state function agrees with every one of the 32 rebuilt state objects. `git diff --check` passed. The report is UTF-8 without BOM.

The first `tests/` run was interrupted after source inspection found an acquisition test that does not stub every potential network call. No external acquisition was requested; that initial test process was not guarded, so absence of all test-originated network traffic is not established. Subsequent checks use `.tmp/cd/guard/sitecustomize.py` to reject external HTTP, DNS and socket connections while allowing loopback.

The first broader-suite failure was independently reproduced: `tests/test_aact_cache.py::test_replay_with_snapshot_access_forbidden` compares the changed replay against unchanged committed review hashes and HTML. It fails on review/hash/served-byte mismatch, as expected when the lane changes object/rendering output but explicitly forbids updating `docs/`. Full output is `.tmp/cd/first-failure.txt`. This is a verification failure, not a green full-suite result.

Final empty-declaration regression: empty intervention lists/maps do not contribute checked dimensions. The final compiler comparison was recomputed against all 32 rebuilt objects; checked-dimension differences were zero.

## Final full-suite stop-first check

Command: `AACT_DIR=.tmp/empty_aact python -X utf8 -m pytest tests -q -x --tb=short`, with the network guard on PYTHONPATH. This is a full-suite selection stopped at its first failure, not a completed passing suite.

```text
F
================================== FAILURES ===================================
_________________ test_replay_with_snapshot_access_forbidden __________________
tests\test_aact_cache.py:22: in test_replay_with_snapshot_access_forbidden
    assert ok, reasons
E   AssertionError: ['review_sha256 mismatch: replay 8783526857b75f8c28e368ec6d8f9a8f1122b6ab1605c6d88abc28e8c46f1201 vs committed bc9c2fc...0b77e4ee7423b6c23b5ed2756cf261cc1bf272049', 'served index.html does not byte-match a re-render from the replayed core']
E   assert False
=========================== short test summary info ===========================
FAILED tests/test_aact_cache.py::test_replay_with_snapshot_access_forbidden
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed in 45.47s
```

## Bounded broader-suite diagnostic outcome

Command: `AACT_DIR=.tmp/empty_aact python -X utf8 -m pytest tests -q --tb=short`, with external network blocked by `.tmp/cd/guard/sitecustomize.py`. Outcome: **TIMEOUT after 600 seconds; bounded verification cap**. The run did not complete; no passing full-suite claim is made. This diagnostic started before the last empty-declaration edge-case adjustment; final code was subsequently checked by the 24-test focused suite and the full-suite stop-first command above.

```text
F....................................................................... [  7%]
........................................................................ [ 14%]
........................................................................ [ 22%]
........................................................................ [ 29%]
..................................
```

The broader tests regenerated `docs/compat_direction_sweep.json` as a side effect. Its initially clean committed bytes were restored directly from `git show HEAD:<path>`; no reset/checkout/stash was used. Final scoped diff confirms no retained changes under docs/, topics/, protocols/ or cache/. Blockers are also logged in `.tmp/cd/STUCK_FAILURES.md`.

Final artifacts: `LANE-CD-REPORT.md`, the four owned source/test files, `.tmp/patches/*.diff`, and `.tmp/cd/` evidence/rebuilt corpus. HEAD remains `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit.
