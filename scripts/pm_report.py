"""Assemble the PM report from measured local evidence; no network or commits."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.tmp' / 'pm'


def read(name):
    return (OUT / name).read_text(encoding='utf-8')


def summary(name):
    text = read(name)
    marker = '=========================== short test summary info'
    if marker in text:
        return text[text.index(marker):].strip()
    return '\n'.join(text.strip().splitlines()[-8:])


def main():
    evidence = json.loads(read('measurement.json'))
    scan = evidence['served']
    gate = json.loads(read('gate.json'))
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    state = ('Verification run finished; results below.' if (OUT / 'full-exit-code.txt').exists()
             else 'IN PROGRESS: the full suite is still running; this is an interim report.')
    total = scan['rendered_units']
    visible = scan['visible_units_before_structural_rules']
    parts = [f'''# LANE PM report

{state}

**MEASURED: {scan['with_object']} registered of {total} whole-page nonstructural visible text units. {len(scan['violations'])} remain unregistered. Gate: {gate[0]}.**

The three prose-migration lanes are combined, GLP1 is rebuilt, and the requested measurement/verification evidence is recorded below. This is not a claim of full prose coverage, a green release gate, or submission readiness. No commit, push, deployment or network acquisition was performed.

## Base and scope

`git rev-parse HEAD`: `{head}`. Base `refs/lanes/landing4-wip-str`: `bf99a91652e74347e4e10cf6b9f1962aee4e596d`. Initial tracked worktree was clean; existing lane prompt/log/PID files were preserved. Session index/workbook context was checked without edits. The workbook and portfolio status were not changed.

Each lane's report was read first. Files were enumerated with `git status --short --untracked-files=all`, excluding lane logs/PIDs/prompts, `.tmp`, and `LANE-*`. Non-shared files were copied in A, B, C order. Shared source files were merged against `git show bf99a916:<path>`; generated GLP1 files were then rebuilt. The copy manifest is `.tmp/pm/copy-manifest.json`.

`harness/synth.py`, `harness/gate.py`, source identifiers/dates/effects, membership, search and screening engines, and other served pages were not edited. Search/screening *renderer bindings* from C were integrated as explicitly requested. Incidental test-generated changes outside the task were restored from the initially clean base.

## Every conflict resolution

The prompt's **CLAIMED** conflict count was 3 + 7. The initial raw Windows merge exposed six page hunks and a subsequent whole-file line-ending conflict. A and B page inputs had CRLF while the Git base and C had LF. **MEASURED after LF normalization:** A+B has one claimgraph conflict and zero page conflicts; AB+C has two claimgraph conflicts and zero page conflicts. Normalization changes line separators only; this was still a real base-relative `git merge-file` merge, not an overwrite with one lane's version.

The three semantic claimgraph resolutions:

1. A+B `review_graph`: retain A's `page_claims.register(review, graph)` and B's conditional `risk_prose.register` plus `manuscript.register`. Preserve B's `include_sections=False` recursion boundary and A's provenance-batch decorator.
2. AB+C `ClaimGraph.recompute`: retain B's `section_effect_display` and `section_text` dispatch and C's `ledger_field`, `selection_flow`, `harms_states`, `parity_consistency`, `retrieval_cell`, and `query_item` dispatch. These operations own different objects.
3. AB+C `review_graph`: retain all A/B registration above and add C's `register_sections(graph, review)`.

The seven raw page conflict resolutions/line-ending cases:

1. `_known_missing_sensitivity_panel`: retain A's typed `known_missing` dispatch; B's side is the old renderer.
2. `_overview` entry: retain A's typed overview branch; B has no replacement there.
3. `_trial_inputs`: retain A's `provenance_trial` branch and fallback; B has no replacement there.
4. `_outcome_block`: retain A's typed summary/details/harms dispatch and fallback; B has no replacement there.
5. `_riskofbias`: retain B's `risk_prose.render` replacement; A's side is the old renderer.
6. `render_page`: retain A's provenance-batch decorator and the function shared by both sides.
7. The AB+C whole-file CRLF/LF artifact: normalize merge inputs to LF and re-run the three-way merge, retaining C's limitation, retrieval, selection, family, harms, comparator and parity renderer bindings alongside A/B. There was no remaining semantic page conflict after normalization.

Source-level integration review found an additional conflict that Git did not flag: A's early overview return made C's limitations block unreachable. The existing C block was extracted to `_stated_limitations` and called by both overview paths (except neutral rendering), preserving C's three registered interpretations **and** its four unregistered limitations. The merge integration test checks their visibility and existing debt. The A-only census excludes `ul.limits` by its semantic ownership boundary; the whole-page and C censuses still count every limitation. No scanner exemption or prose whitelist was introduced.

Initial test authoring encountered BeautifulSoup's attribute reordering; the integration assertion now compares parsed span nodes, not raw attribute order. This correction did not change rendering. Raw and normalized merge evidence is under `.tmp/pm/`.

The first focused merged run reported `2 failed, 129 passed in 403.23s (0:06:43)`. Both failures were integration assumptions in A's tests: an apostrophe entity spelling superseded by B's text-node escaping, and an expectation for A's unused harms summary after C takes ownership of complete unpooled harms. The assertions now compare decoded text and the actual C harms renderer respectively; source tamper/refusal assertions remain. The final rerun is pasted below. An AST comparison (`.tmp/pm/merge-node-audit.json`) confirms every lane-modified page function matches its lane implementation except the deliberately combined Overview.

## Whole-page measurement

**N = {total} nonstructural conservative visible prose/table text runs**, across the entire served GLP1 HTML, not just the three lanes' owned sections. These are not linguistic sentences or independent empirical claims. **V = {visible} visible text runs before the existing short-semantic-table-header rule.** Existing semantic headings/navigation are excluded by the scanner. No denominator is filtered according to whether a unit passes.

| Class | Registered units of N (N={total}) | Meaning |
|---|---:|---|
''']
    for cls in ('FACT', 'TRANSFORMATION', 'JUDGEMENT', 'INTERPRETATION'):
        parts.append(f"| {cls} | {scan['with_object_by_class'].get(cls, 0)} of {total} | Matched registered renderings |\n")
    parts.append(f'''| STRUCTURAL | {scan['structural_count']} of {visible} (V) | Existing semantic table-header rule; not registered claims |
| All nonstructural classes | {scan['with_object']} of {total} | Registered whole-page coverage |
| Unregistered | {len(scan['violations'])} of {total} | SENTENCE_WITHOUT_OBJECT; no class inferred |

Registered plus structural: **{scan['with_object'] + scan['structural_count']} of {visible} visible units**. Unregistered units cannot honestly be assigned FACT/JUDGEMENT/etc. without objects, so the class rows use the named common denominator N rather than invented per-class totals. Registry object counts (different from repeated rendered occurrences): `{json.dumps(evidence['object_classes'], sort_keys=True)}`.

Served and fresh-renderer census agree: **{scan == evidence['fresh']}**. The separate CGX3C census retains **451 registered of 488 nonstructural units**, with **37 unregistered of 488**; its numeric plant adds one deliberately unsupported unit. The other **{len(scan['violations']) - 37} unregistered units** are outside that C boundary. Whole-page debt includes strand membership/status tables, typed-effects disclosures, protocol/reporting/reproduction material and chrome as well as the C debt. The task's whole-page result is not 37 remaining.

`python scripts/claim_scope_sweep.py` ran as requested against the complete stored corpus. Its command output:

```text
{read('sweep.txt').strip()}
```

The corpus sweep is a measurement, not a page rebuild or portfolio certification. `.tmp/pm/measurement.json` retains complete served/fresh scans, the plant, source audit and fresh strand calculations. `docs/claim_scope_sweep.json` is the requested broader census.

## Static-versus-dynamic hardcode disclosure

| Static/authored | Dynamic/source-derived | Limit |
|---|---|---|
| Renderer labels, operation dispatch, class rules and section boundaries | Registered inputs, provenance digests/spans, recomputed pools | No topic-result constants introduced |
| Editorial interpretations and explicit alternatives | Recorded decision fields and per-item states | Registration does not mean human adjudication |
| Display precision and existing estimator policy | Source FACT dependencies, HKSJ/PM pool and leave-one-out calculations | Uses unchanged statistical engine |
| Ledger formatting selectors | Stored retrieval fields and per-item selection/harms counts | A field projection is not an independent retrieval recount |
| Report layout and test selection | Measured counts, exact scanner violations, test/gate output | No simulated research data |

## Source/identifier/date/statistics second pass

**MEASURED:** all seven primary source IDs were found in held records; all seven FACT checks pass document digest, retrieval timestamp and located numeric-span validation. Typed-object violations: `{evidence['source_audit']['typed_object_violations']}`. Fresh primary: `{evidence['source_audit']['primary_recomputed']}`. The source audit records the exact held document paths, metadata and verification results in `.tmp/pm/measurement.json`. Retrieval timestamps are evidence metadata, not inferred study dates. Input identifiers, study/source dates, effect values and membership were not edited.

Both strands were recomputed from registered FACT dependencies, not set to expected results:

| Strand | k | HR | 95% CI |
|---|---:|---:|---|
''')
    for strand in evidence['strands']:
        pool = strand['recomputed']
        parts.append(f"| {strand['id']} | {pool['k']} | {pool['estimate']:.4f} | {pool['ci_low']:.4f}–{pool['ci_high']:.4f} |\n")
    parts.append(f'''
## Build and reproduction — verbatim

`python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11`

```text
{read('build.txt').strip()}
```

`python scripts/reproduce_review.py glp1-ra-mace-t2d`

```text
{read('reproduce.txt').strip()}
```

## Numeric plant — verbatim

One unsupported number was inserted inside the served page's main element in memory. It was never written to the source or served page. The scanner must refuse it; the assertion verifies that exact plant and code.

```text
PLANT: REFUSED (expected)
{json.dumps(evidence['plant'], indent=2, ensure_ascii=False)}
```

C's separate limitations plant also fires:

```text
{read('cgx3c.txt').strip()}
```

## Focused tests — verbatim summary

The three lanes' tests, `tests/test_claimgraph*.py`, `tests/test_fact_provenance.py`, `tests/test_page.py`, lane-related regressions and the browser E2E contract were run together. Exact command:

```text
{read('focused-command.txt').strip()}
```

```text
{summary('focused.txt')}
```

## Full suite — verbatim summary

`python -m pytest -q --import-mode=importlib --tb=short`

Importlib mode permits collecting both the archived search-lane test and its canonical same-named test; no test directory is excluded. Python subprocesses use the copied lane offline socket guard, allowing only loopback for E2E.

```text
{summary('full.txt')}
```

Complete outputs are `.tmp/pm/focused.txt` and `.tmp/pm/full.txt`. Failures are disclosed, not bypassed. No full-suite PASS is claimed unless the pasted result is green. Existing lane reports described repository-wide failures before this merge; that historical report is **CLAIMED context**, not a substitute for the current run or an isolated baseline reproduction. Unresolved blockers are recorded in `STUCK_FAILURES.md`.

**MEASURED current failure details:** stale fix-ledger/fix-state documents; a gate fixture with unregistered prose; missing scorecard entries for `gate.check_effect_types` and `gate.check_typed_renderings`; GLP1 integrity recording ten pooled trials against a union of seven; a balanced-crystalloids legacy test that assumes no claimgraph; missing override-audit entries for esketamine and SGLT2 reviews; and an error-rate sample missing GLP1 input 26630143. **INFERRED:** these are the persisting blockers described in the source lanes, based on matching failure identities/details and unchanged underlying out-of-scope inputs. No isolated full-base replay was performed by PM, and no broader repair or certification is claimed.

Final cleanup restored the four test/build-written `effect_types.json` caches (GLP1, NOAC, PCSK9 and probiotics) and `docs/compat_direction_sweep.json` to their clean session-start base bytes. The final GLP1 artifacts and requested scope census stayed byte-identical to their measured outputs throughout the tests. Protected engines remain unchanged; final `git diff --check` passes. HEAD is still the recorded base, and nothing is staged or committed.

## Exact gate verdict — verbatim

Called `scripts.verify_all.limb_gate_every_page('glp1-ra-mace-t2d')` on the merged output. It gates **1 of 1 requested pages**. Gate refusal is distinct from deterministic numerical reproduction.

```text
{gate[0]}
{gate[1]}
```

## Every remaining unregistered unit, verbatim

The following is the complete served-page list, preserving repeated text units, scanner order, unit IDs and contexts. None is silently relabelled structural or source-validated. These are quotations of audit debt, **not endorsed research claims**. Every entry is `SENTENCE_WITHOUT_OBJECT`.

''')
    for i, violation in enumerate(scan['violations'], 1):
        assert violation['code'] == 'SENTENCE_WITHOUT_OBJECT'
        parts.append(f"### {i}. `{violation['unit_id']}` — `{violation['context']}`\n\n```text\n{violation['detail']}\n```\n\n")
    (ROOT / 'LANE-PM-REPORT.md').write_text(''.join(parts), encoding='utf-8')
    print(f'Wrote LANE-PM-REPORT.md with {len(scan["violations"])} verbatim unregistered units.')


if __name__ == '__main__':
    main()
