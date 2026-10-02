"""WHO REACT Figure 1: prepare, record, replay/gate, or census (offline by default)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import forest_gate as fg
from reproducible_ai import model_source as ms

BINDING = 'docs/recovery_figure_binding.json'


def bacc_note(root):
    """Extract the own-paper comparison; never substitute it for figure cells."""
    from harness import recovery_map
    entries = recovery_map.load_map(root)[fg.SLUG]['entries']
    entry, = [e for e in entries if fg.norm(e['trial']) == 'BACCBAY']
    source = f"cache/{fg.SLUG}/ft_{entry['pmid']}.txt"
    raw = (Path(root) / source).read_bytes()
    try:
        article = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError('BACC_PAPER_REFUSED: malformed XML: ' + source) from exc
    pmids = [n.text for n in article.findall('.//article-id') if n.get('pub-id-type') == 'pmid']
    if pmids != [entry['pmid']]:
        raise ValueError('BACC_PAPER_REFUSED: article PMID does not match recovery map: ' + source)
    text = lambda node: ''.join(node.itertext()).strip()
    tables = {t.get('id'): t for t in article.findall('.//table-wrap')}
    try:
        if 'Modified Intention-to-Treat' not in text(tables['t2'].find('caption')) or 'Safety Population' not in text(tables['t4'].find('caption')):
            raise ValueError('population captions')
        def denominators(table):
            headers = [text(h) for h in table.findall('.//thead//th')]
            return [int(next(re.fullmatch(arm + r'\(N=(\d+)\)', h) for h in headers
                             if re.fullmatch(arm + r'\(N=(\d+)\)', h)).group(1))
                    for arm in ('Tocilizumab', 'Placebo')]
        mitt_n = denominators(tables['t3'])
        safety_n = denominators(tables['t4'])
        rows = [[text(c) for c in row] for row in tables['t2'].findall('.//tbody/tr')]
        index, = [i for i, row in enumerate(rows) if row[0] == 'Tertiary outcome: death']
        arms = rows[index + 1:index + 3]
        if [a[0] for a in arms] != ['Tocilizumab', 'Placebo']:
            raise ValueError('death arm labels')
        mitt = dict(zip(fg.COUNTS, (int(arms[0][1]), mitt_n[0], int(arms[1][1]), mitt_n[1])))
        death, = [[text(c) for c in row] for row in tables['t4'].findall('.//tbody/tr') if text(row[0]) == 'Death']
        counts = [int(re.fullmatch(r'(\d+) \([\d.]+\)[†]?', cell).group(1)) for cell in death[1:3]]
        safety = dict(zip(fg.COUNTS, (counts[0], safety_n[0], counts[1], safety_n[1])))
        quote, = [text(p) for p in tables['t4'].findall('.//table-wrap-foot//p')
                  if 'One patient who died was intubated before receiving placebo' in text(p)]
        return dict(trial=entry['trial'], source=source, sha256=hashlib.sha256(raw).hexdigest(),
                    mitt_counts=mitt, safety_counts=safety, explanation=quote,
                    table_ids=['t2', 't3', 't4'])
    except (KeyError, ValueError, TypeError, AttributeError, StopIteration) as exc:
        raise ValueError('BACC_PAPER_REFUSED: ' + source + ': ' + str(exc)) from exc


def binding_artifact(root=ROOT):
    """Offline replay boundary. The build consumes its JSON, never this module."""
    root = Path(root)
    records = []
    for path in sorted((root / 'evidence/model_calls').glob('*.json')):
        rec = ms.load_record(path)
        if (rec.get('caller') or {}).get('lane') == 'REACTFIG':
            records.append(rec)
    report = fg.gate(records, root=root, replay_response=ms.replay)
    if report['problems'] or not report['rows']:
        raise ValueError('FIGURE_BINDING_REPLAY_REFUSED: ' + repr(report['problems']))
    ids = report['rows'][0]['record_ids']
    models = [r['model']['id_reported'] for r in records if r['record_id'] in ids]
    if len(ids) < 3 or len(set(models)) < 3:
        raise ValueError('FIGURE_BINDING_READERS_REFUSED: three distinct recorded model readings required')
    note = bacc_note(root)
    for row in report['rows']:
        if row['status'] == 'UNVERIFIABLE':
            row['reasons'] = [row['control_accounting']['reason']]
    entries = []
    for binding in report['bindings']:
        entry = dict(binding)
        entry['state'] = binding['state'] if binding['state'] in ('MODEL_TRANSCRIBED_CHECKED', 'CROSS_PROVIDER_VERIFIED', 'CONFLICT') else 'REFUSED'
        entry['population'] = 'outcomes recorded'
        if entry['trial'] == note['trial']:
            if entry.get('figure_counts') != note['safety_counts']:
                raise ValueError('BACC_SAFETY_FIGURE_CONFLICT: ' + entry['trial'])
            entry['own_paper'] = note
        entries.append(entry)
    return dict(schema='recovery_figure_binding/1', topic=fg.SLUG,
                figure_sha256=report['rows'][0]['figure_sha256'], record_ids=ids,
                model_ids=models, population='outcomes recorded',
                population_equivalence='NOT_ADJUDICATED', poolable=False,
                entries=entries, gate_rows=report['rows'],
                cell_resolutions=report['cell_resolutions'], excluded_records=report['excluded_records'],
                control_accounting=report['control_accounting'])


def binding_bytes(root=ROOT):
    return (json.dumps(binding_artifact(root), ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def verify_binding(root=ROOT):
    if (Path(root) / BINDING).read_bytes() != binding_bytes(root):
        raise ValueError('STALE_FIGURE_BINDING: ' + BINDING)
    return True


def output_schema():
    properties = {k: {'type': 'string'} for k in fg.ROW_KEYS - set(fg.COUNTS)}
    properties.update({k: {'type': 'integer', 'minimum': 0} for k in fg.COUNTS})
    properties['kind'] = {'type': 'string', 'enum': ['trial', 'subgroup', 'overall']}
    row = {'type': 'object', 'properties': dict(sorted(properties.items())),
           'required': sorted(properties), 'additionalProperties': False}
    return {'type': 'object', 'properties': {'rows': {'type': 'array', 'items': row, 'minItems': 1}},
            'required': ['rows'], 'additionalProperties': False}


def prompt():
    return ("Transcribe the attached WHO REACT Figure 1 (28-day all-cause mortality). "
            "This is a PROPOSAL, not data. Read EVERY row verbatim, in figure order: "
            "all trial rows in EVERY anti-IL-6 agent section, every printed subgroup total, "
            "and the overall total. Do not correct arithmetic, infer an unprinted subtotal, "
            "drop zero-event rows, or resolve shared controls. Preserve trial names; omit only "
            "superscript footnote markers. agent is the section label. kind is trial, subgroup, "
            "or overall; use the printed total label as trial for summary rows. ai/n1i are "
            "events/total ANTI-IL-6; ci/n2i are events/total USUAL CARE OR PLACEBO. Copy OR, "
            "ci_low, ci_high, and weight as strings at exactly the printed precision (without "
            "percent sign); preserve < and use NA for a printed NA or blank. "
            "registration is the printed registration identifier or empty string when absent; "
            "never infer one. Return only the output-schema JSON. Do not read other files, "
            "use tools, or consult previous proposals. If illegible, do not invent values; "
            "an incomplete or invalid proposal will be refused.").encode('utf-8')


def census(root=ROOT):
    """All topic files are the coverage denominator; no missing call is a pass."""
    root = Path(root)
    topics = sorted(p.stem for p in (root / 'topics').glob('*.json'))
    records, refused_records = [], []
    for path in sorted((root / 'evidence/model_calls').glob('*.json')):
        try:
            rec = ms.load_record(path)
            if (rec.get('caller') or {}).get('lane') == 'REACTFIG':
                records.append(rec)
        except (ValueError, OSError) as exc:
            refused_records.append({'file': path.name, 'reason': str(exc)})
    report = fg.gate(records, root=root, replay_response=ms.replay)
    rule_prefixes = {'arithmetic': ('ARITHMETIC:',), 'totals': ('TOTALS:',),
                     'table1': ('TABLE1_',), 'agreement': ('AGREEMENT:', 'INDEPENDENCE:'),
                     'weights': ('WEIGHTS:',), 'record_and_image': ('RECORD_', 'FIGURE_', 'HELD_EVIDENCE:')}
    rules = {}
    for rule, prefixes in rule_prefixes.items():
        examined = report['rows']
        flagged = [f"{r['row']['agent']}::{r['row']['trial']}" for r in examined
                   if any(p.startswith(prefixes) for p in r['reasons'])]
        rules[rule] = {'n': len(flagged), 'N': len(examined), 'n_of_N': f'{len(flagged)} of {len(examined)}',
                       'items': flagged, 'denominator': 'rows in first valid recorded proposal'}
    rows = [r['row'] for r in report['rows']]
    singleton_agents = {r['agent'] for r in rows if r['kind'] == 'trial'
                        and sum(t['kind'] == 'trial' and t['agent'] == r['agent'] for t in rows) == 1
                        and not any(t['kind'] == 'subgroup' and t['agent'] == r['agent'] for t in rows)}
    structural = {
        'overall_agent_normalized': [r for r in rows if r['kind'] == 'overall'],
        'single_trial_section_without_subtotal': [r for r in rows if r['kind'] == 'trial' and r['agent'] in singleton_agents],
        'overall_controls_unverifiable': [r for r in rows if r['kind'] == 'overall'],
        'shared_control_dedup': [r for r in rows if r['kind'] == 'overall' and any(
            c['trial'] == r['trial'] and c['code'] == 'SHARED_CONTROL_DEDUP' for c in report['control_accounting'])],
    }
    for rule, flagged in structural.items():
        rules[rule] = {'n': len(flagged), 'N': len(rows), 'n_of_N': f'{len(flagged)} of {len(rows)}',
                       'items': [f"{r['agent']}::{r['trial']}" for r in flagged],
                       'denominator': 'rows in first valid recorded proposal; structural change or caveat, not admission'}
    for status in ('RESOLVED', 'DISAGREEMENT'):
        cells = [c for c in report['cell_resolutions'] if c['status'] == status]
        n, total = len(cells), len(rows) * len(fg.ROW_KEYS)
        rules['cell_' + status.lower()] = {
            'n': n, 'N': total, 'n_of_N': f'{n} of {total}',
            'items': [f"row {c['row_index']} {c['agent']}::{c['trial']}.{c['field']}" for c in cells],
            'denominator': 'normalized cells examined in figure-order row slots'}
    excluded = report['excluded_records']
    rules['failed_calls_excluded'] = {
        'n': len(excluded), 'N': len(records), 'n_of_N': f'{len(excluded)} of {len(records)}',
        'items': [r['record_id'] for r in excluded], 'denominator': 'recorded REACTFIG calls'}
    successful = [r for r in records if r.get('state') == 'RAN_OK']
    repeated = sorted({r['model'].get('id_reported') for r in successful
                       if sum(x['model'].get('id_reported') == r['model'].get('id_reported')
                              for x in successful) > 1})
    rules['repeated_model_ids'] = {
        'n': len(repeated), 'N': len({r['model'].get('id_reported') for r in successful}),
        'items': repeated, 'denominator': 'distinct successful model ids'}
    rule = rules['repeated_model_ids']
    rule['n_of_N'] = f"{rule['n']} of {rule['N']}"
    applicable = [s for s in topics if s == fg.SLUG]
    unavailable = applicable if not records else []
    return {'topics_examined': len(topics), 'topic_names': topics,
            'applicable': {'n_of_N': f'{len(applicable)} of {len(topics)}', 'items': applicable},
            'no_recorded_proposal': {'n_of_N': f'{len(unavailable)} of {len(topics)}', 'items': unavailable},
            'rules': rules, 'record_files_refused': refused_records,
            'gate_problems': report['problems'], 'bindings': report['bindings'],
            'control_accounting': report['control_accounting'],
            'cell_resolutions': report['cell_resolutions'], 'excluded_records': excluded,
            'note': '0 of 0 means NOT EXAMINED, never a passing arithmetic census; other topics are outside WHO REACT scope.'}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--call', action='store_true')
    mode.add_argument('--gate', nargs='+', metavar='RECORD')
    mode.add_argument('--census', action='store_true')
    mode.add_argument('--write-binding', action='store_true')
    ap.add_argument('--model', help='required for live call; use a different pinned model for each reader')
    ap.add_argument('--effort', default='medium')
    args = ap.parse_args(argv)
    if args.write_binding:
        try:
            raw = binding_bytes()
        except (OSError, ValueError) as exc:
            print(json.dumps({'status': 'REFUSED', 'reason': str(exc)}))
            return 1
        (ROOT / BINDING).write_bytes(raw)
        print(BINDING)
        return 0
    if args.call:
        if not args.model:
            ap.error('--call requires --model')
        from reproducible_ai import model_call_live
        rec = model_call_live.call(prompt(), schema=output_schema(), model=args.model, effort=args.effort,
                                  caller={'file': 'scripts/react_figure_proposal.py', 'line': 'main --call',
                                          'purpose': 'Independent WHO REACT Figure 1 transcription', 'lane': 'REACTFIG'},
                                  input_digests=[], images=(fg.FIGURE,), image_root=ROOT)
        print(ms.write_record(rec, ROOT / 'evidence/model_calls').relative_to(ROOT).as_posix())
        return 0 if rec['state'] == 'RAN_OK' else 1
    if args.gate:
        try:
            report = fg.gate([ms.load_record(p) for p in args.gate], root=ROOT, replay_response=ms.replay)
        except (OSError, ValueError) as exc:
            print(json.dumps({'status': 'REFUSED', 'reason': str(exc)}))
            return 1
        print(json.dumps(report, indent=2))
        return 0 if report['rows'] and all(r['status'] == 'ADMITTED' for r in report['rows']) and not report['problems'] else 1
    if args.census:
        print(json.dumps(census(), indent=2))
    else:
        print(json.dumps({'prompt': prompt().decode('utf-8'), 'output_schema': output_schema(),
                          'image': fg.FIGURE}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
