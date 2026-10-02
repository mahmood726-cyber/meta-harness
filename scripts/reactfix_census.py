"""Offline all-topic census of REACTFIX states and deterministic checks."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import forest_gate as fg, disperse2_gate as dg
from reproducible_ai import model_source as ms


def census(root=ROOT):
    root = Path(root)
    topics = []
    for path in sorted((root / 'topics').glob('*.json')):
        json.loads(path.read_text(encoding='utf-8'))  # malformed topics fail closed
        topics.append(path.stem)
    records = [ms.load_record(p) for p in sorted((root / 'evidence/model_calls').glob('*.json'))]
    forest, tables = None, None
    rules = {}
    def rule(name, examined, flagged, unit):
        rules[name] = {'n': len(flagged), 'N': len(examined), 'n_of_N': f'{len(flagged)} of {len(examined)}',
                       'items': flagged, 'unit': unit}
    applicable = []
    for slug in topics:
        if slug == fg.SLUG:
            applicable.append(slug)
            forest = fg.gate([r for r in records if r.get('caller', {}).get('lane') == 'REACTFIG'],
                             root=root, replay_response=ms.replay)
        elif slug == 'ticagrelor-vs-clopidogrel-acs':
            applicable.append(slug)
            text, images = dg.held_inputs(root)
            tables = dg.gate_batches([r for r in records if r.get('caller', {}).get('lane') == 'DISP2CALL'],
                text, images, replay_response=ms.replay, record_problems=ms.record_problems)
    if forest is None or tables is None:
        raise ValueError('CENSUS_REFUSED: missing required topic')
    if forest['problems'] or tables['status'] != 'ADMIT':
        raise ValueError('CENSUS_REFUSED: ' + json.dumps({'forest': forest['problems'], 'tables': tables.get('reason')}))
    rule('topic_coverage', topics, applicable, 'all topics; other topics outside these two transcription gates')
    frows = [(fg.SLUG + '/' + r['row']['kind'] + '/' + r['row']['agent'] + '/' + r['row']['trial'], r) for r in forest['rows']]
    drows = [('ticagrelor-vs-clopidogrel-acs/' + '/'.join((r['table_id'],r['outcome_label_verbatim'],r['window'],r['arm'])), r) for r in tables['rows']]
    rows = frows + drows
    for state in (fg.MODEL_TRANSCRIBED_CHECKED, fg.CROSS_PROVIDER_VERIFIED):
        rule(state, rows, [name for name, row in rows if row['transcription_state'] == state], 'gated forest/table rows; refused/unverifiable rows included in denominator')
    rule('DOSE_COLUMN_UNVERIFIED', drows, [name for name, row in drows if 'DOSE_COLUMN_UNVERIFIED' in row['flags']], 'DISPERSE-2 rows')
    trials = [(name, row) for name, row in frows if row['row']['kind'] == 'trial']
    rule('NO_TABLE1_IDENTITY_WITNESS', trials, [name for name,row in trials if row['identity_witness'] == 'NO_TABLE1_IDENTITY_WITNESS'], 'forest trial rows, including refused Table 1 mismatches')
    summary = [(name, row) for name,row in frows if row['row']['kind'] != 'trial']
    rule('INTERVAL_ORDER', summary, [name for name,row in summary if any('INTERVAL_ORDER' in e for e in row['reasons'])], 'resolved subgroup/overall rows')
    context_checks = [(g, c) for g in tables['groups'] for c in g['agreement_audit']['contexts']]
    for name in ('TABLE_ID', 'TIMEPOINT', 'CONTEXT_CONTRADICTION'):
        rule(name, context_checks, [], 'recorded table proposals; every source-semantic check passed')
    rule('MODEL_CONTEXT_ECHO_SEPARATED', context_checks,
         [c['table_id'] + '/' + c['record_id'] for _,c in context_checks], 'recorded table proposals with retained echo and held context')
    rule('CROSS_PROVIDER_DISAGREEMENT', rows,
         [name for name,row in rows if any(w['disagreeing_cells'] for w in row['cross_provider_witnesses'])], 'gated rows; zero witnesses is not verification')
    rule('FOREST_EXISTING_REFUSAL', frows, [name for name,row in frows if row['status'] != 'ADMITTED'], 'forest rows; existing refusals and unverifiable overall retained')
    return {'topics_examined': len(topics), 'rules': rules,
            'real_cross_provider_records': [r['record_id'] for r in records if r.get('caller', {}).get('lane') in ('REACTFIG','DISP2CALL') and r['model']['provider'].casefold() != 'openai'],
            'poolable_rows': sum(bool(r.get('poolable')) for _,r in rows),
            'note': 'All values derived from held bytes. Synthetic regression plants excluded. No cross-provider reading was invented.'}


if __name__ == '__main__':
    print(json.dumps(census(), ensure_ascii=False, indent=2))
