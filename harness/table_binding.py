"""Fail-closed source-bound table candidates; pure, never edits served reviews.

Admission is deliberately limited to independently regenerated lane excerpts.
Other corpus tables are parsed and diagnosed but require their own byte-binding
adapter; a declared SHA alone does not prove a transcription is correct.
"""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import re
from . import table_rows, measure_identity, dose_arms

ROOT = Path(__file__).resolve().parents[1]


def select_row(table, outcome_cfg):
    name = outcome_cfg.get('name', '')
    if re.fullmatch(r'major bleeding', name, re.I):
        keys = ['Major bleeding (PLATO-defined)', 'Total Major']
    elif re.fullmatch(r'dyspn(?:ea|oea)', name, re.I):
        keys = ['Dyspnea', 'Dyspnoea']
    else:
        keys = outcome_cfg.get('keywords') or [name]
    selected, reason = table_rows.select(table, keys,
                        ['NON_CABG', 'LEADING_TO_DISCONTINUATION', 'SERIOUS'])
    if selected is None:
        raise ValueError(f'ROW_IDENTITY: {name}: {reason}')
    # Exact total endpoint: no composite major+minor or non-CABG substitute.
    if re.fullmatch(r'major bleeding', name, re.I) and selected['label'] not in keys:
        raise ValueError(f'ROW_IDENTITY: refused {selected["label"]} for {name}')
    return selected


def choose(table, row, peer_measures):
    typed = table_rows.typed(row, table)
    patients = [a for a in typed['arms'] if a['count_unit'] == 'PATIENTS']
    if len(patients) != 2 or any(not a['n_denominator'] or not 0 <= a['n_events'] <= a['n_denominator'] for a in patients):
        raise ValueError(f'COUNT_UNIT: refused {row["label"]}: need two explicit patient arms; KM percentages are not counts')
    a, c = patients
    counts = dict(ai=a['n_events'], n1i=a['n_denominator'], ci=c['n_events'], n2i=c['n_denominator'])
    candidates = []
    published = None
    for candidate in typed['candidates']:
        if candidate['derivation'] == 'PUBLISHED':
            effect = candidate['effect']
            published = dict(measure=candidate['measure'], value=effect['value'],
                             ci=[effect['ci_low'], effect['ci_high']])
            candidates.append(dict(measure=candidate['measure'], effect=effect['value'],
                                   ci_low=effect['ci_low'], ci_high=effect['ci_high'], derivation='PUBLISHED'))
        else:
            candidates.append(dict(**counts, measure='RISK_RATIO', derivation='RECONSTRUCTED'))
    selection = measure_identity.select(candidates, peer_measures)
    if not selection['admissible']:
        raise ValueError(f'MEASURE_REFUSED: {row["label"]}: {selection["problems"]}')
    return dict(**counts, count_unit='PATIENTS', published_effect=published,
                input=selection['row'], candidates=candidates,
                row_label=row['label'], variant_flags=typed['variant_flags'],
                analysis_population=typed['analysis_population'], safety_window=typed['window'],
                excluded_columns=[a for a in typed['arms'] if a['count_unit'] != 'PATIENTS'])


def _source(excerpt_path):
    from scripts import make_philo_excerpt as philo, make_plato_fda_excerpt as plato
    path = Path(excerpt_path)
    name = path.name
    if name == Path(philo.OUTPUT).name:
        expected, trial, source = philo.render(ROOT), 'PHILO', philo.PDF
    elif name in [Path(p).name for p in plato.OUTPUTS]:
        outputs = plato.render(ROOT)
        expected = next(b for p, b in outputs.items() if Path(p).name == name)
        trial, source = 'PLATO', plato.PDF
    else:
        raise ValueError(f'SOURCE_BINDING_UNSUPPORTED: {name}: no independent held-text segmentation adapter')
    if path.read_bytes() != expected:
        raise ValueError(f'SOURCE_BINDING_MISMATCH: {name}: excerpt differs from held-text regeneration')
    return trial, source


def _pmid(slug, trial):
    from .trial_family import load_registry
    records = json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf-8'))['records']
    registry = load_registry(ROOT, slug)
    ncts = {n for n, data in registry.items() if any(str(s.get('acronym','')).upper() == trial.upper()
             for s in data.get('raw',{}).get('studies',[]))}
    # Review membership anchors the report; the held record must itself name the trial.
    review = json.loads((ROOT/'docs/reviews'/slug/'review.json').read_text(encoding='utf-8'))
    members = {v for o in review['outcomes'] for key in ('trials','declared_absent_trials')
               for r in o.get(key,[]) for v in re.findall(r'\b\d{6,9}\b',str(r.get('id','')))}
    hits = [str(r['id']) for r in records if str(r['id']) in members
            and (r.get('nct') in ncts or re.search(r'\b'+re.escape(trial)+r'\b',str(r.get('title',''))+' '+str(r.get('abstract','')),re.I))]
    if len(hits) != 1:
        raise ValueError(f'TRIAL_IDENTITY: {slug}/{trial}: refused nonunique source-backed PMID {hits}')
    return hits[0]


def bind(slug, outcome_cfg, excerpt_path):
    path = Path(excerpt_path)
    tables = table_rows.parse(path)
    matches, reasons = [], []
    for table in tables:
        try:
            row = select_row(table, outcome_cfg)
            peers = outcome_cfg.get('peer_measures') or [outcome_cfg.get('estimand')]
            matches.append((table, choose(table, row, peers)))
        except ValueError as exc:
            reasons.append(str(exc))
    if len(matches) != 1:
        raise ValueError(f'BIND_REFUSED: {path.name}/{outcome_cfg.get("name")}: {reasons}; matches={len(matches)}')
    trial, source = _source(path)
    pmid = _pmid(slug, trial)
    table, result = matches[0]
    spans=[line for line in path.read_text(encoding='utf-8').splitlines()
           if '|' in line and line.split('|',1)[0].strip()==result['row_label']]
    if len(spans)!=1:
        raise ValueError(f'SOURCE_SPAN_REFUSED: {path.name}: row span not unique')
    result.update(trial=trial, pmid=pmid, state='TABLE_BOUND', provenance='HELD_TABLE',
                  excerpt_sha=hashlib.sha256(path.read_bytes()).hexdigest(), source_sha=table['source_sha'],
                  document_ref=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                  source_document=source, target_measure=measure_identity.normalize(outcome_cfg.get('estimand')).value,
                  source_span=spans[0],
                  selected_measure=measure_identity.measure_of(result['input']).value)
    result['protocol_change_required'] = result['target_measure'] != result['selected_measure']
    result['definition'] = ('FDA_GROUPED_SEVEN_PREFERRED_TERMS' if trial == 'PLATO' and 'Dyspnea' in result['row_label']
                            else 'STUDY_DEFINED_TOTAL_MAJOR_BLEEDING' if re.search('major',result['row_label'],re.I)
                            else 'STUDY_REPORTED_DYSPNEA')
    return result


def supersede_absence(previous, bound):
    if bound.get('state') != 'TABLE_BOUND' or bound.get('provenance') != 'HELD_TABLE':
        raise ValueError('ABSENCE_SUPERSEDED refused: input is not a held table binding')
    if bound['pmid'] not in re.findall(r'\b\d+\b', str(previous.get('id',''))):
        raise ValueError('ABSENCE_SUPERSEDED refused: trial identity differs')
    status = previous.get('result_status',{})
    text = ' '.join(str(previous.get(k,'')) for k in ('reason','state','reason_code'))+' '+json.dumps(status)
    if not re.search(r'inspected abstract|found in the abstract',text,re.I):
        raise ValueError('ABSENCE_SUPERSEDED refused: not an abstract-scoped absence')
    result = deepcopy(previous)
    for key in ('reason','reason_code','absent','override','typed_refusal','absent_kind'):
        result.pop(key,None)
    result.update(state='TABLE_BOUND', result_status={'state':'TABLE_BOUND','basis':bound['document_ref']},
                  table_binding=deepcopy(bound), previous_result_status=deepcopy(status))
    return result


def require_pool(rows):
    for row in rows:
        if row.get('state') == 'REFUSED' or row.get('provenance') == 'RELAYED' or row.get('derivation') == 'RELAYED':
            raise ValueError(f'POOL_REFUSED: {row.get("trial",row.get("id"))}: refused or relayed')
    problems = measure_identity.check_pool(rows)
    if problems:
        raise ValueError(f'POOL_REFUSED: {problems}')
    return rows


def disperse():
    path = ROOT/'evidence/acquisition_cascade/held/DISPERSE-2'
    files = sorted(path.glob('europepmc_record_*.json'))
    if len(files) != 1:
        raise ValueError('DISPERSE-2 held record missing or ambiguous')
    record = json.loads(files[0].read_text(encoding='utf-8'))['resultList']['result'][0]
    record = dict(record, abstract=re.sub(r'<[^>]+>', ' ', record['abstractText']))
    result = dose_arms.assess(record)
    if len(result['arms']) != 3 or result['status'] != 'REFUSED':
        raise ValueError('DISPERSE-2 dose/held-table contract unresolved')
    return dict(result, pmid=record['pmid'], trial='DISPERSE-2',
                reason='full table not held; recovery active', record=record)
