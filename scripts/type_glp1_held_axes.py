"""Rebuild curated GLP1 axis evidence from held documents only (no network).

Static: trial/endpoint selectors and source interpretations below.
Dynamic: verbatim spans, document digests, effect selectors and AACT row fields.
No effect estimate, interval, membership, or coercion is authored here.
AACT exports in outputs/handover/typg were read through harness.aact, snapshot
2026-08-30; row IDs apply only inside that named snapshot.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import glp1_sources as glp1
from harness import effect_type as ty


def read(path):
    return (ROOT / path).read_bytes().decode('utf-8')


def evidence(value, path, span, level, json_path=None, **metadata):
    basis = dict(source=path, document_path=path,
                 document_sha256=hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                 span=span, source_level=level, **metadata)
    if json_path is not None:
        basis['json_path'] = json_path
    field = {'value': value, 'basis': basis}
    assert ty.held_axis(field)['value'] == value, (path, span)
    return field


def main():
    path = 'cache/glp1-ra-mace-t2d/records.json'
    records = json.loads(read(path))['records']
    entries = glp1.entries()
    names = ['LEADER', 'SUSTAIN-6', 'EXSCEL', 'Harmony', 'REWIND', 'PIONEER 6',
             'AMPLITUDE-O', 'SOUL', 'ELIXA', 'FLOW', 'FREEDOM-CVO']
    ids = ['27295427', '27633186', '28910237', '30291013', '31189511', '31185157',
           '34215025', '40162642', '26630143', '38785209', '34873344']
    result = {'schema_version': 1, 'rows': {}}
    for pmid, name in zip(ids, names):
        effect = entries[pmid]
        axes = {a: ty.field(absence_code='NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD')
                for a in ['endpoint_components', 'censoring', 'effect_measure']}
        result['rows'][pmid] = dict(trial=name, effect_selector={
            **{k: effect[k] for k in ['effect', 'ci_low', 'ci_high', 'scale', 'document_sha256']},
            'source_sha256': hashlib.sha256(effect['source'].encode('utf-8')).hexdigest()}, axes=axes)
        if pmid in [r['id'] for r in records]:
            idx = next(i for i, r in enumerate(records) if r['id'] == pmid)
            abstract = records[idx]['abstract']
            loc = ['records', idx, 'abstract']
            if pmid not in ['26630143', '34873344', '38785209']:
                span = next(s.strip() for s in abstract.split('. ') if re.search(r'primary (?:composite )?outcome', s, re.I) and re.search('stroke', s, re.I))
                components = ty.components(span)
                if pmid == '34215025':
                    # The protocol explicitly accepts undetermined death within CV death.
                    assert 'death from cardiovascular or undetermined causes' in span
                    components = sorted(set(components) | {'CV_DEATH'})
                axes['endpoint_components'] = evidence(components, path, span, 1, loc)
                hr = next(m.group(0) for m in re.finditer(r'hazard ratio[^;)]*', abstract, re.I)
                          if str(effect['effect']) in m.group(0).replace('·', '.'))
                axes['effect_measure'] = evidence('HR', path, hr, 1, loc)
                if pmid == '30291013':
                    start = abstract.index('On Nov 8, 2017')
                    end = abstract.index('The primary composite outcome occurred', start)
                    axes['censoring'] = evidence('end-of-study', path, abstract[start:end].strip(), 1, loc,
                        interpretation='Final visit and discontinuation; ITT evaluation through trial closeout.')
        if pmid in ['26630143', '34873344', '38785209']:
            source = effect['source']
            if pmid == '34873344':
                hr = source[source.index('IR (n/100 PY) HR'):source.index('4-Point MACE 95')].strip()
            else:
                hr = source[source.lower().index('hazard ratio'):]
            axes['effect_measure'] = evidence('HR', effect['extracted_text'], hr, effect['source_level'])

    def set_abstract_censor(pmid, span):
        result['rows'][pmid]['axes']['censoring'] = evidence('end-of-study',
            f'cache/glp1-ra-mace-t2d/ft_{pmid}.txt', span, 1,
            interpretation='Randomised participants observed until last trial visit/closeout, not treatment cessation.')

    set_abstract_censor('27295427', 'All the patients who underwent randomization were included in the primary and exploratory analyses, and data from the patients who completed or discontinued the trial without having an outcome were censored from the day of their last visit; events occurring after that visit were not included.')
    set_abstract_censor('28910237', 'The planned closeout of follow-up of the patients was from December 5, 2016, to May 11, 2017, after the prespecified required minimum of 1360 patients were confirmed to have had a primary composite outcome event.')

    # These selectors refer to exact rows in the held snapshot export, not to
    # trial-name heuristics, generic durations, or another endpoint's follow-up.
    outcomes_path = 'outputs/handover/typg/outcomes.json'
    table = json.loads(read(outcomes_path))
    selections = {'27633186': ('NCT01720446', '258793862', 'time_frame'),
                  '31189511': ('NCT01394952', '258446987', 'time_frame'),
                  '31185157': ('NCT02692716', '258712707', 'description'),
                  '40162642': ('NCT03914326', '258686373', 'description')}
    for pmid, (nct, rid, column) in selections.items():
        idx, row = next((i, r) for i, r in enumerate(table['rows']) if r['id'] == rid and r['nct_id'] == nct)
        assert row['outcome_type'] == 'PRIMARY' and row['population']
        result['rows'][pmid]['axes']['censoring'] = evidence('end-of-study', outcomes_path,
            row[column], 3, ['rows', idx, column], snapshot=table['snapshot'], table='outcomes',
            row_id=rid, nct_id=nct, outcome_title=row['title'], analysis_population=row['population'],
            interpretation='End of follow-up / study completion / in-trial observation normalised to end-of-study.')

    flow_idx, flow = next((i, r) for i, r in enumerate(table['rows']) if r['id'] == '258827888' and r['nct_id'] == 'NCT03819153')
    result['rows']['38785209']['axes']['endpoint_components'] = evidence(
        ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'], outcomes_path, flow['title'], 3,
        ['rows', flow_idx, 'title'], snapshot=table['snapshot'], table='outcomes',
        row_id=flow['id'], nct_id=flow['nct_id'])
    result['rows']['38785209']['axes']['censoring'] = ty.field(absence_code='FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR')

    for pmid in ['26630143', '34873344']:
        effect = entries[pmid]
        text = read(effect['extracted_text'])
        if pmid == '26630143':
            start = text.index('MACE, defined as cardiovascular death, non-fatal')
            end = text.index(', are consistent', start)
            component_span = text[start:end]
            start = text.index('MACE endpoint (on-study) 1.02')
            end = text.index('MACE endpoint (on-treatment)', start)
            censor_span = text[start:end].strip()
        else:
            start = text.index('Table 19. Time to First Occurrence', text.index('### PAGE 58'))
            end = text.index(' and 4-Point MACE', start)
            component_span = text[start:end]
            end = text.index('MACE Type', start)
            censor_span = text[start:end].strip()
        axes = result['rows'][pmid]['axes']
        axes['endpoint_components'] = evidence(['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE'],
            effect['extracted_text'], component_span, 2)
        axes['censoring'] = evidence('end-of-study', effect['extracted_text'], censor_span, 2,
            interpretation='On-study / ITT End of Study for the selected 3-point MACE row.')

    for pmid, row in result['rows'].items():
        row['searched'] = ['Held PubMed abstract', 'AACT design_outcomes, outcomes, outcome_analyses (snapshot 2026-08-30)']
        if pmid in ['27295427', '28910237']:
            row['searched'].append('Held full text')
        if pmid in ['26630143', '34873344']:
            row['searched'].append('Held FDA regulatory text')
        if pmid == '38785209':
            row['searched'].append('ADJUDICATIONS.json: composite on-treatment versus component in-trial caveat')
    result['rows']['34215025']['refusal_note'] = 'Abstract follow-up duration and AACT maximum duration plus ITT do not explicitly state observation after treatment cessation or at study end; censoring UNKNOWN.'
    result['rows']['30291013']['refusal_note'] = 'MI and stroke fatality unspecified in abstract and held AACT composite; COERCION NEEDED if mapping these to nonfatal components is intended. No coercion authored.'
    result['rows']['38785209']['refusal_note'] = 'No held publication span links HR 0.82 to in-trial observation; registry composite explicitly says on-treatment. Component follow-up cannot type composite censoring.'
    (ROOT/'cache/glp1-ra-mace-t2d/axis_evidence.json').write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    print('Wrote held axis evidence for', len(result['rows']), 'candidate rows')


if __name__ == '__main__':
    main()
