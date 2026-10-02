"""Read-only all-topic census; run with python scripts/ticagdys_census.py."""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness.effect_definition_binding import extract_documents, plain_outcome_binding, pair_counts
from harness.trial_family import load_registry
from harness import table_binding
from scripts.make_plato_fda_dyspnea_def_excerpt import read_sources


def census_rule(items, predicate, name):
    flagged = [name(x) for x in items if predicate(x)]
    return {'n': len(flagged), 'N': len(items), 'n of N': f'{len(flagged)} of {len(items)}', 'items': flagged}


def row_name(row):
    return f'{row.trial}/{row.label}/p{row.page}/c{row.start}'


def relay_states(block, rows):
    results = []
    keymap = {'ai': 'patients_1', 'ci': 'patients_2', 'n1i': 'n_1', 'n2i': 'n_2'}
    for entry in block['entries']:
        related = [r for r in rows if r.trial == entry['trial'] and plain_outcome_binding(r, entry['outcome']) == 'BOUND']
        effect_rows = [r for r in related if r.scale == 'HR']
        values = {}
        tuple_match = [r for r in effect_rows if all(getattr(r, k) == entry['values'].get(k, {}).get('value')
                       for k in ('effect', 'ci_low', 'ci_high'))]
        for k, v in entry['values'].items():
            state = 'RELAYED_ONLY'
            if k in keymap:
                matches = [r for r in related if r.counts.get(keymap[k]) == v['value']]
                state = 'BOUND' if matches else 'DEFINITION_DIFFERS' if related else 'UNRESOLVED'
            elif k in ('effect', 'ci_low', 'ci_high', 'measure'):
                state = 'BOUND' if tuple_match else 'UNRESOLVED'
            values[k] = {'value': v['value'], 'before': v.get('binding_state'), 'binding_state': state,
                         'provenance': 'RELAYED', 'poolable': False}
        results.append({'trial': entry['trial'], 'outcome': entry['outcome'], 'values': values})
    return results


def run(root=ROOT):
    root = Path(root)
    documents = read_sources(root)
    rows, audit = extract_documents(documents)
    topics = []
    for path in sorted((root/'topics').glob('*.json')):
        cfg = json.loads(path.read_text(encoding='utf-8'))
        topics.append((path.stem, cfg))
    applicable = [(slug, cfg) for slug, cfg in topics if
                  'ticagrelor' in [str(x).lower() for x in cfg.get('intervention_terms', [])]
                  and 'clopidogrel' in [str(x).lower() for x in cfg.get('comparator_terms', [])]]
    slots, relays, baseline_errors = [], [], []
    for slug, cfg in applicable:
        registry = load_registry(root, slug)
        if not registry:
            raise ValueError('REFUSED EMPTY_FAMILY_REGISTRY: ' + slug)
        # Existing helper joins held abstracts and review membership, never a hardcoded PMID.
        identities = {table_binding._pmid(slug, trial): trial for trial in ('PLATO', 'PHILO')}
        review = json.loads((root/'docs/reviews'/slug/'review.json').read_text(encoding='utf-8'))
        block = json.loads((root/'docs/recovery_maps.json').read_text(encoding='utf-8'))['topics'][slug]
        relays.extend(relay_states(block, rows))
        for outcome in review['outcomes']:
            if outcome['name'] not in ('Major bleeding', 'Dyspnea'):
                continue
            spec = next(x for x in cfg['harm_outcomes'] if x['name'] == outcome['name'])
            for candidate in outcome.get('trials', []) + outcome.get('declared_absent_trials', []):
                identifiers = re.findall(r'\b\d{6,9}\b', candidate.get('id', ''))
                trial = identities.get(identifiers[0], candidate.get('label', 'UNKNOWN')) if identifiers else candidate.get('label', 'UNKNOWN')
                matches = [r for r in rows if r.trial == trial and r.scale == 'HR' and
                           plain_outcome_binding(r, outcome['name']) == 'BOUND']
                unique = {(r.definition, r.effect, r.ci_low, r.ci_high) for r in matches}
                before = candidate.get('scale') == 'HR' and candidate.get('effect') is not None
                baseline_held = False
                for path in sorted((root/'evidence/acquisition_cascade/excerpts').glob('*.tables.txt')):
                    if not path.name.startswith(trial+'_'):
                        continue
                    try:
                        bound = table_binding.bind(slug, spec, path)
                        baseline_held |= bool(bound.get('published_effect') and bound['published_effect']['measure'] == 'HAZARD_RATIO')
                    except ValueError as exc:
                        baseline_errors.append({'item': slug+'/'+trial+'/'+outcome['name']+'/'+path.name, 'refusal': str(exc)})
                slots.append({'name': slug+'/'+outcome['name']+'/'+trial,
                              'id': candidate.get('id'), 'served_before_hr': before,
                              'base_held_adapter_hr': baseline_held,
                              'after_bound_hr': len(unique) == 1,
                              'after_state': 'BOUND' if len(unique) == 1 else
                                'NOT_PRINTED_IN_HELD_TEXT' if trial == 'PHILO' and outcome['name'] == 'Dyspnea' else 'UNRESOLVED',
                              'evidence': [row_name(r) for r in matches], 'poolable': False})
    hrs = [r for r in rows if r.scale == 'HR']
    counted = [r for r in rows if r.counts]
    pairs = []
    for effect in hrs:
        # One actual same-trial count row per effect, preferentially its own row.
        choices = [r for r in counted if r.trial == effect.trial]
        if not choices:
            continue
        chosen = effect if effect.counts else choices[0]
        try:
            pair_counts(effect, chosen)
            refusal = None
        except ValueError as exc:
            refusal = str(exc)
        pairs.append({'name': row_name(effect)+' -> '+row_name(chosen), 'refusal': refusal})
    return {
        'scope': 'All topic configurations scanned; effect denominator is ticagrelor harm-outcome x trial slots in held review, including declared-absent slots. Source-row denominators retain repeat FDA revisions and covariates; they are not independent trials.',
        'topics': census_rule(topics, lambda x: x in applicable, lambda x: x[0]),
        'candidate_slots': slots,
        'served_before_hr': census_rule(slots, lambda x: x['served_before_hr'], lambda x: x['name']),
        'base_held_adapter_hr': census_rule(slots, lambda x: x['base_held_adapter_hr'], lambda x: x['name']),
        'after_bound_hr': census_rule(slots, lambda x: x['after_bound_hr'], lambda x: x['name']),
        'new_relative_to_served': census_rule(slots, lambda x: x['after_bound_hr'] and not x['served_before_hr'], lambda x: x['name']),
        'rules': {
            'variant_refusal': census_rule(rows, lambda r: bool(r.variant_flags), row_name),
            'unresolved_definition': census_rule(hrs, lambda r: r.binding_state != 'BOUND', row_name),
            'wrong_trial': census_rule(rows, lambda r: r.trial not in ('PLATO','PHILO'), row_name),
            'count_pair_refusal': census_rule(pairs, lambda p: p['refusal'] is not None, lambda p: p['name']),
            'nonpatient_count_unit': census_rule(counted, lambda r: r.unit not in ('PATIENTS','EVENTS_AND_PATIENTS'), row_name),
            'invalid_hr_ci': census_rule(hrs, lambda r: not 0 < r.ci_low <= r.effect <= r.ci_high, row_name),
            'empty_source_span': census_rule(rows, lambda r: not r.quote, row_name),
            'ledger_pool_refusal': census_rule(rows, lambda r: not r.poolable, row_name),
            'source_hash_failure': {'n': 0, 'N': 2*len(documents), 'n of N': f'0 of {2*len(documents)}', 'items': []},
        },
        'source_rows_by_trial': dict(Counter(r.trial for r in rows)),
        'audit_mentions_by_source': dict(Counter(a['source'] for a in audit)),
        'relayed_values_after': relays,
        'base_adapter_refusals': baseline_errors,
    }


def plant_observations(rows):
    """Run base helper functions on the same planted inputs; no pipeline claims."""
    from dataclasses import replace
    from unittest.mock import patch
    from harness import source_hierarchy, target_endpoint, hand_binding, recovery_map
    from harness.effect_definition_binding import parse_passage, require_poolable, make_row, medical_rows, statistical_rows
    from scripts.make_philo_excerpt import held
    from scripts.make_plato_fda_dyspnea_def_excerpt import SOURCES
    observations = []

    def attempt(fn):
        try:
            value = fn()
            return value.to_dict() if hasattr(value, 'to_dict') else value
        except ValueError as exc:
            return str(exc)

    for label, outcome in [
        ('PLATO-defined non-CABG major bleeding', 'Major bleeding'),
        ('Dyspnea single preferred term leading to discontinuation', 'Dyspnea'),
        ('Serious dyspnea single preferred term', 'Dyspnea'),
        ('TIMI major bleeding', 'Major bleeding'),
        ('Time to first dyspnea event', 'Dyspnea'),
        ('Time to first dyspnea event (single preferred term only)', 'Dyspnea'),
        ('PLATO-defined total major bleeding', 'Major bleeding'),
    ]:
        passage = label + ' HR 1.25 (95% CI 1.10, 1.42).'
        spec = {'name': outcome, 'keywords': [outcome.lower()]}
        row = parse_passage(passage, trial='PLATO')[0]
        observations.append({'plant': passage, 'base_function': 'target_endpoint._classify / source_hierarchy.source_effect_candidates',
            'pre_fix_output': {'classification': target_endpoint._classify(spec, passage),
                               'candidates': source_hierarchy.source_effect_candidates(spec, abstract=passage)},
            'post_fix': plain_outcome_binding(row, outcome)})
    major = next(r for r in rows if r.trial == 'PHILO' and r.label == 'Major bleeding (PLATO-defined)')
    other = next(r for r in rows if r.trial == 'PHILO' and 'Non-CABG' in r.label)
    for label, countrow in [('cross-definition counts', other), ('same-row counts (negative plant)', major),
                            ('event unit', replace(major, unit='EVENTS'))]:
        effectrow = countrow if label == 'event unit' else major
        planted = {'effect': effectrow.effect, 'ci_low': effectrow.ci_low, 'ci_high': effectrow.ci_high, 'scale': 'HR',
                   'ai': countrow.counts['patients_1'], 'ci': countrow.counts['patients_2'],
                   'n1i': countrow.counts['n_1'], 'n2i': countrow.counts['n_2']}
        tup = hand_binding._tuple_of(planted)
        observations.append({'plant': label, 'input': planted, 'base_function': 'hand_binding._tuple_of / _tuple_in',
            'pre_fix_output': {'tuple': tup, 'tuple_in_effect_row': hand_binding._tuple_in(effectrow.quote, tup)},
            'post_fix': attempt(lambda: pair_counts(effectrow, countrow))})
    relay = {'trial': major.trial, 'provenance': 'RELAYED', 'poolable': False}
    observations.append({'plant': 'relayed ledger admission', 'input': relay,
        'base_function': 'recovery_map.require_poolable', 'pre_fix_output': attempt(lambda: recovery_map.require_poolable(relay)),
        'post_fix': attempt(lambda: require_poolable(major)), 'note': 'Base relay protection already refuses; preserved, not a newly discovered defect.'})
    triton = next(r for r in rows if r.trial == 'TRITON')
    observations.append({'plant': 'TRITON row offered as PLATO major bleeding', 'input': triton.quote,
        'base_function': 'target_endpoint._classify',
        'pre_fix_output': target_endpoint._classify({'name':'Major bleeding','keywords':['major bleeding']}, triton.label),
        'post_fix': plain_outcome_binding(triton, 'Major bleeding')})
    invalid = 'PLATO-defined total major bleeding HR 1.25 (95% CI 1.50, 1.60).'
    observations.append({'plant': invalid, 'base_function': 'source_hierarchy.source_effect_candidates',
        'pre_fix_output': source_hierarchy.source_effect_candidates({'keywords':['major bleeding']}, abstract=invalid),
        'post_fix': attempt(lambda: parse_passage(invalid, trial='PLATO'))})
    documents = read_sources(ROOT)
    stem, sha, _ = SOURCES['medical']
    original_bytes, original_text = Path.read_bytes, Path.read_text
    def corrupted_bytes(path):
        content = original_bytes(path)
        return content + b'\nSYNTHETIC DEFECT' if path.name.endswith('.local.txt') else content
    def corrupted_text(path, *args, **kwargs):
        content = original_text(path, *args, **kwargs)
        return content + '\nSYNTHETIC DEFECT' if path.name.endswith('.local.txt') else content
    with patch.object(Path, 'read_bytes', corrupted_bytes), patch.object(Path, 'read_text', corrupted_text):
        before = held(ROOT, 'evidence/acquisition_cascade/held/'+stem+'.pdf', sha)
        after = attempt(lambda: read_sources(ROOT))
    observations.append({'plant': 'modified local sidecar; unchanged PDF (in-memory patch only)',
        'base_function': 'scripts.make_philo_excerpt.held', 'pre_fix_output': {'returned_tampered_text': before.endswith('SYNTHETIC DEFECT')}, 'post_fix': after})
    observations.append({'plant': 'empty passage', 'base_function': 'source_hierarchy.source_effect_candidates',
        'pre_fix_output': source_hierarchy.source_effect_candidates({'keywords':['dyspnea']}, abstract=''),
        'post_fix': attempt(lambda: make_row('', 'missing', 'PLATO', 0, 0, 'Dyspnea'))})
    # Existing generator only extracts total major; a malformed sibling was ignored.
    from scripts.make_plato_fda_excerpt import render as base_render
    damaged = documents['medical']['text'].replace('Major Fatal/ Life-threatening    ', 'Major Fatal/ UNKNOWN    ', 1)
    with patch('scripts.make_plato_fda_excerpt.held', return_value=damaged):
        old = base_render(ROOT)
    observations.append({'plant': 'malformed fatal/life-threatening sibling row',
        'base_function': 'scripts.make_plato_fda_excerpt.render',
        'pre_fix_output': {'excerpts_returned': list(old)},
        'post_fix': attempt(lambda: medical_rows(damaged, 'synthetic-defect'))})
    return observations


def write_report(census_stdout, test_stdout, root=ROOT):
    """Embed actual census stdout and individually hashed excerpts in allowed report."""
    from scripts.make_plato_fda_dyspnea_def_excerpt import render, SOURCES
    root = Path(root)
    documents = read_sources(root)
    rows, audit = extract_documents(documents)
    plants = plant_observations(rows)
    census = json.loads(census_stdout)
    lines = ['# TICAGDYS lane report', '', '## FILES', '',
        '- `harness/effect_definition_binding.py`: pure typed row ledger, source spans, strict definition/count pairing and pool quarantine.',
        '- `scripts/make_plato_fda_dyspnea_def_excerpt.py`: checks both PDF and text SHA-256; emits one deterministic excerpt per source row to stdout.',
        '- `tests/test_effect_definition_binding.py`: constructed defects and correct-input negative plants.',
        '- `scripts/ticagdys_census.py`: scans every topic configuration, calls the family registry loader, joins report identifiers through held abstracts, compares base adapters with the new ledger.',
        '- `LANE_REPORT.md`: this report, actual census output, typed inventory and embeddable excerpts.', '',
        'Only these new files were authored. No commit, push, checkout, staging or other git-state operation was performed. No network calls. No served files, cache files, topic configuration or shared project-status files were changed.', '',
        '## RULES', '',
        '| Component | Static parsing contract | Dynamic evidence |',
        '|---|---|---|',
        '| Sources | Relative source filenames and SHA-256 pins | PDF and sidecar bytes verified on every read |',
        '| FDA tables | Caption/row-label regex and explicit column layout | Every count, HR and CI parsed from matched bytes |',
        '| PHILO | Table 3 boundaries and inherited parent labels | Each row, its printed HR/CI or its absence, and safety denominators |',
        '| Definition gate | Variant regex; plain major requires study-defined total major | Definition text and exact same-row provenance |',
        '| Trial census | Target drug terms and harm names; no PMID lookup constants | All topic JSON; load_registry; held records and review trial membership |',
        '| PLANTS | Deliberately synthetic defect numbers inside tests/observations | Never treated as study data |', '',
        '1. **Variants.** `variants()` recognizes non-CABG, CABG, procedural/nonprocedural, noncoronary, discontinuation, serious, fatal/life-threatening, other-major, minor/minimal, TIMI and subgroup labels. Adjusted Cox coefficients carry a separate flag. `plain_outcome_binding()` refuses every flagged row for a plain outcome, naming the flags.',
        '2. **Definitions.** A plain Major bleeding HR requires `STUDY_DEFINED_TOTAL_MAJOR_BLEEDING`; a dyspnea HR needs its own explicit preferred-term definition. Onset paragraphs do not inherit the preceding table footnote. Missing or conflicting definitions remain UNRESOLVED. Counts-only PHILO dyspnea is a reported AE label, not evidence of a printed HR.',
        '3. **Count pairing and units.** Trial, source, hash, character offsets, definition, variants, population and window must match. Events are distinct from patients. FDA event columns are excluded by `pair_counts`; Table 13 corroborates total-major patient counts. No cross-row join on matching HR digits is allowed.',
        '4. **Trial identity.** StatR Table 11 says TRITON and describes prasugrel versus clopidogrel. These HRs remain TRITON rows and are refused for PLATO/PHILO.',
        '5. **Numeric/layout validity.** HR bounds must be finite, positive and contain the estimate. Missing/duplicate FDA rows and unparsed StatR low/high rows fail closed. Point-only estimates retain no fabricated CI. A missing PHILO dyspnea HR is never reconstructed or borrowed.',
        '6. **Provenance.** SHA-256 pins cover both PDF and local text. Every row stores its source quote, decoded-text character offsets, PDF page marker and sidecar hash. Offsets refer to read_text newline-normalized text; they are not byte offsets.',
        '7. **Admission.** Every ledger row has `poolable=false`; `require_poolable()` always refuses. RELAYED values remain RELAYED even if individual fields bind. No estimator or protocol change is authorized by this ledger.', '',
        '### Findings and coverage', '',
        'PLATO dyspnea onset HR remains **UNRESOLVED** in both Medical Review revisions. The passage establishes time to first event, but does not explicitly bind the HR to a single PT, the seven-term group, its analysis population or censoring window. A Cox model is not stated in that onset passage. The Statistical Review contains no dyspnea text. Resolving this requires the exact dyspnea analysis definition/footnote or SAP/CSR table that links the HR, PT list, population, time origin and censoring window in the same evidence chain.',
        'The relayed NEJM dyspnea numerators do not match the held grouped Table 23 counts. The Medical Review also reports a one-patient difference between its grouped table and grouped prose elsewhere; these are retained as separate evidence, not silently reconciled. No proof that the relay is a single-PT result was found. The relay window remains relayed. The explicit seven-day post-dose window in the Medical Review is in the death-analysis table; it cannot establish the dyspnea HR window.',
        'PHILO dyspnea HR: **NOT_PRINTED_IN_HELD_TEXT**. Table 3 prints counts only. This is not a claim that an unheld supplement or inaccessible image cannot contain another analysis. PHILO major, minor and composite bleeding table rows are inventoried separately, including CABG/non-CABG/procedural children and the Japanese subgroup statement.',
        'The Medical Review total-major table explicitly leaves Life-threatening and Major Other HR cells blank; those rows have counts and no HR. Adjusted Cox tables are retained coefficient by coefficient, with raw variable/context evidence; their coefficients are not interchangeable with the unadjusted primary safety HR.', '',
        '### Relevant held passages', '']
    # Whole bounded onset/table blocks retain definition proximity without conferring a join.
    for key, patterns in {
        'medical': [r'vi\) Onset of Dyspnea\s+.*?(?=vii\)|=== PAGE)',
                    r'In PLATO, most cases of dyspnea.*?while on treatment\.',
                    r'Deaths in safety on-treatment analysis.*?study drug\)',
                    r'5\.3\.1\.14 Primary Safety Objective.*?(?=5\.3\.1\.15)'],
        'philo': [r'Safety data were analyzed.*?2-sided 95% confidence intervals\s*\(CI\)',
                  r'In patients\s+recruited from Japan,.*?\(HR,.*?\)\.'],
        'statistical': [r'Similar analyses were also performed on Non CABG TIMI major bleeding.*?\(Table 11\)\.',
                        r'3\.3 Evaluation of Safety\s+.*?clinical review for safety evaluation\.'],
    }.items():
        text = documents[key]['text']
        for pattern in patterns:
            for m in re.finditer(pattern, text, re.S):
                page = re.findall(r'=== PAGE (\d+) ===', text[:m.start()])[-1]
                lines += [f"Source: `{documents[key]['source']}`, PDF page {page}, characters {m.start()}:{m.end()}.", '', '```text', m[0], '```', '']
    lines += ['## PLANTS', '',
        'Pre-fix results below were actually run against the unchanged base helper functions on the same inputs. Keyword classification and tuple location are lower-level functions, not claims that the entire base pipeline admitted these rows. Existing table selection and relay quarantine already contain protections; this lane preserves them.', '',
        '```json', json.dumps(plants, ensure_ascii=False, indent=2), '```', '',
        'Test command: `PYTHONIOENCODING=utf-8 python -m pytest -q -p no:cacheprovider tests/test_effect_definition_binding.py` (PowerShell environment equivalent; bytecode disabled).',
        '', '```text', test_stdout.strip(), '```', '',
        '## CENSUS', '',
        'Command: `python scripts/ticagdys_census.py`. The following is its captured stdout, pasted without recomputing the JSON. Before/after distinguishes served review state from the base held-table adapter. Repeated FDA revisions and adjusted coefficients are source rows, not additional independent trials.', '',
        '```json', census_stdout.rstrip(), '```', '', '## HOOKS', '']
    hooks = [('harness/pipeline.py', 'def _source_effect_candidates',
              'After candidate surfacing, before preference/selection, attach this ledger to the held candidate; call plain_outcome_binding before allowing a candidate to stand for the plain harm. Do not change RR protocol to HR automatically.'),
             ('harness/pipeline.py', 'trials, _inadmissible = target_endpoint_mod.admit_rows',
              'Before this admission call, retain definition, variant flags, source/row identity and the named refusal; never synthesize a ledger row or relay.'),
             ('harness/hand_binding.py', 'def _tuple_of',
              'When a supplied effect also has counts, validate both together through same-row evidence; the base effect-first tuple omits count validation.'),
             ('harness/table_binding.py', 'def bind(',
              'After source regeneration and row selection, annotate the exact definition and variant flags. Existing select_row protections must remain. Hash both sidecar and PDF using read_sources.'),
             ('harness/recovery_binding.py', 'def require_poolable',
              'Keep relay quarantine. relay_states is an annotation-only comparison, not pool construction.')]
    for file, needle, note in hooks:
        source_lines = (root/file).read_text(encoding='utf-8').splitlines()
        number = next(i for i, line in enumerate(source_lines, 1) if needle in line)
        lines.append(f'- `{file}:{number}`, context `{needle}`: {note}')
    lines += ['', '## OPEN', '',
        '- **Raster-only bleeding results remain unextracted.** The Medical Review nonprocedural HR plots (caption-derived page list below) have image content but no numeric text layer. PDF page 243 was rendered in memory and visually checked: printed estimates exist in the image. PyMuPDF confirms its text layer contains only the caption/source. No local Tesseract executable was found on PATH or in the two standard installation locations. Values were not hand-transcribed because the lane requires regex/typed derivation. A deterministic, hash-verified OCR/table adapter with image QA is required before claiming every published bleeding HR is captured. Other image-only pages may also contain results; text-layer absence is not proof of publication absence.',
        '- **Excerpts destination conflict.** The brief asks for committed excerpts but explicitly allows only the five named new files (plus further generators), and the user prohibits commits/git-state changes. Therefore independently hashed one-row excerpts are embedded below in this allowed report and emitted by render(); no extra evidence file or commit was created. The integrator can materialize them after authorizing a destination. Existing excerpt files are untouched.',
        '- **Conservative unresolved rows.** Prose-only bleeding HR clauses lacking explicit definition binding and adjusted coefficients remain unresolved. Narrative outcome mentions are audit leads, not newly invented effect tuples. Full numeric extraction of every narrative count and raster table is not claimed.',
        '- **No release claim.** This is a lane module/report only; no pipeline integration, pool change, UI build, Overmind certification, portfolio-status edit, push or deploy was performed.', '',
        '### Raster plot caption locators', '']
    for a in audit:
        if re.search(r'^Figure \d+:.*Hazard Ratio.*(?:bleed|Bleed)', a['quote']) and '...' not in a['quote']:
            lines.append(f"- PDF page {a['page']}: {a['quote'].strip()}")
    lines += ['', '### Typed source-row inventory', '',
              '| Trial | PDF page / character | Row definition / label | Variants | HR or other printed measure | Counts/unit | State |',
              '|---|---|---|---|---|---|---|']
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    for r in rows:
        effect = f'{r.scale}: {r.effect}; CI {r.ci_low}, {r.ci_high}' if r.effect is not None else 'NOT_PRINTED in row'
        lines.append('| '+' | '.join(map(cell, [r.trial, f'{r.page} / {r.start}', str(r.definition)+' / '+r.label,
                     ','.join(r.variant_flags), effect, str(r.counts)+' / '+r.unit, r.binding_state]))+' |')
    lines += ['', '### Individually hashed source excerpts', '',
              'Each block is one result-row excerpt. PHILO blocks contain one result row each. Source hashes refer to the sidecar; the paired PDF hashes are listed below. These excerpts are audit artifacts and do not authorize pooling.', '']
    for key, (stem, pdf_sha, text_sha) in SOURCES.items():
        lines.append(f'- `{stem}`: PDF `{pdf_sha}`; text `{text_sha}`.')
    for key, excerpt in render(root).items():
        lines += ['', f"#### {key}", '', f"SHA-256 of UTF-8 excerpt bytes: `{excerpt['sha256']}`", '',
                  '```text', excerpt['text'].rstrip('\n'), '```']
    lines += ['', '### Complete PHILO outcome-mention audit and FDA dyspnea analysis leads', '',
              'Every matching source line is listed; surrounding context is preserved for PHILO because PDF columns split sentences. These leads include history, methods, prior-trial references, percentages and count statements; they are not all treatment-effect candidates.', '']
    for a in audit:
        if 'PHILO/' in a['source'] or re.search(r'dyspn(?:ea|oea)', a['quote'], re.I):
            lines += [f"- `{a['source']}` PDF page {a['page']}, characters {a['start']}:{a['end']}: {norm_for_report(a['quote'])}"]
            if 'PHILO/' in a['source']:
                lines += ['', '```text', a['context'], '```', '']
    content = '\n'.join(lines) + '\n'
    (root/'LANE_REPORT.md').write_bytes(content.encode('utf-8'))
    return {'report': 'LANE_REPORT.md', 'bytes': len(content.encode('utf-8')), 'rows':len(rows),
            'before': census['base_held_adapter_hr']['n of N'], 'after':census['after_bound_hr']['n of N']}


def norm_for_report(text):
    return re.sub(r'\s+', ' ', text).strip()


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True, indent=2))
