"""Prepare image transcription requests; replay three distinct model records offline; census all topics."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import disperse2_gate as gate
from harness.trial_family import load_registry
from reproducible_ai import model_source as ms


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


STRING = {'type': 'string'}
ROW_SCHEMA = obj({
    'outcome_definition': STRING, 'printed_cell': STRING, 'footnote_markers': STRING, 'arm': {'enum': list(gate.ARMS)},
    'n': {'type': ['integer', 'null']}, 'N': {'type': ['integer', 'null']},
    'percent': {'type': ['string', 'null']}, 'timepoint': {'enum': ['4 weeks', '12 weeks', 'overall', 'overall study', 'UNKNOWN']},
    'percent_kind': {'enum': ['CRUDE', 'KM', 'UNKNOWN']},
    'count_basis': {'enum': ['PRINTED_PATIENTS', 'NOT_PRINTED', 'UNKNOWN']}})
TABLE_SCHEMA = obj({'table_id': STRING, 'image_sha256': STRING, 'caption': STRING, 'footnotes': STRING, 'printed_footnotes': STRING,
                    'arm_headers': obj({a: STRING for a in gate.ARMS}),
                    'arm_sizes': obj({a: {'type': ['integer', 'null']} for a in gate.ARMS}),
                    'rows': {'type': 'array', 'items': ROW_SCHEMA}})
SCHEMA = obj({'trial': {'enum': ['DISPERSE-2', 'OTHER', 'UNKNOWN']},
              'provenance': {'enum': ['IMAGE_TRANSCRIPTION', 'RELAYED']},
              'tables': {'type': 'array', 'items': TABLE_SCHEMA}})
PROMPT = '''Independently transcribe only the attached table image. Never consult another proposal.
Do not calculate, infer, repair, combine, or round any printed value. Keep percent as a string
with exactly its printed precision. Use null/UNKNOWN for illegible or missing cells. Distinguish
DISPERSE from DISPERSE-2; use OTHER/UNKNOWN if this is not DISPERSE-2. Preserve outcome
definitions, bleeding definitions, composite components, counts versus rates, and timepoints.
Never convert KM percentages to patient counts. Overall is not a fixed 12-week timepoint.
Copy all three dose arms; include clopidogrel once per outcome/timepoint. Never infer N from a
percentage. Copy the supplied full page context verbatim to footnotes and the caption verbatim.
Read EVERY row in printed order, including every outcome and window. Preserve every row label,
arm header verbatim (including drug, dose and n), printed n (percent) cell, caption, and footnote
marker. arm_headers maps the canonical arms to their verbatim printed headers. printed_cell
keeps the full cell; footnote_markers contains its trailing markers, or empty string.
printed_footnotes contains the verbatim printed image footnotes (empty when none).
Use overall study for that printed window. Do not use tools, read files, or consult prior answers.
Return only the supplied JSON schema. These are proposals, never research evidence by themselves.
'''


def census(root=ROOT):
    """Per-rule denominators are recorded proposal pairs, NOT unrelated topic counts."""
    root = Path(root)
    topics, matched, items, errors = [], [], [], []
    for topic in sorted((root / 'topics').glob('*.json')):
        slug = topic.stem
        topics.append(slug)
        paths = [topic, root / 'cache' / slug / 'records.json', root / 'docs/reviews' / slug / 'review.json']
        try:
            registry = load_registry(root, slug)
            if gate.MENTION.search(json.dumps(registry)):
                items.append(f'{slug}:family-registry')
                matched.append(slug)
            for path in paths:
                if not path.exists():
                    errors.append({'item': path.relative_to(root).as_posix(), 'reason': 'MISSING_HELD_INPUT'})
                    continue
                data = json.loads(path.read_text(encoding='utf-8'))
                if gate.MENTION.search(json.dumps(data)):
                    items.append(path.relative_to(root).as_posix())
                    matched.append(slug)
        except (ValueError, OSError) as exc:
            errors.append({'item': slug, 'reason': str(exc)})
    text, images = gate.held_inputs(root)
    manifest = json.loads((root / gate.IMAGE_DIR / 'manifest.json').read_text(encoding='utf-8'))
    groups = {}
    for path in sorted((root / 'evidence/model_calls').glob('*.json')):
        try:
            record = ms.load_record(path)
            if record.get('caller', {}).get('lane') != 'DISP2CALL':
                continue
            image_shas = tuple(sorted(d['sha256'] for d in record.get('input_digests', [])
                                      if d.get('media_type') == 'image/png'))
            groups.setdefault(image_shas, []).append(record)
        except (ValueError, OSError) as exc:
            errors.append({'item': path.relative_to(root).as_posix(), 'reason': str(exc)})
    results = []
    for key, records in sorted(groups.items()):
        result = gate.gate_records(records, text, images, replay_response=ms.replay,
                                   record_problems=ms.record_problems, target=gate.target_from_topic(root))
        results.append({'item': ','.join(key) or 'MISSING_IMAGE_DIGEST', **result})
    rules = {}
    for rule in gate.RULES:
        flagged = [r['item'] for r in results if r.get('reason', '').startswith(rule + ':')]
        rules[rule] = {'n': len(flagged), 'N': len(results), 'n_of_N': f'{len(flagged)} of {len(results)}',
                       'items': flagged, 'unit': 'held image proposal group; first refusal, not all defects'}
    admitted = [(r['item'], row) for r in results for row in r['rows']]
    for flag in ('RANDOMIZED_TREATED_DENOMINATOR_CONFLICT', 'POST_LOCK_EVENTS_EXCLUDED', 'MACE_CANDIDATE'):
        flagged = [f"{item}/{row['table']}/{row['outcome_label_verbatim']}/{row['window']}/{row['arm']}"
                   for item, row in admitted if (row.get('mace_candidate') if flag == 'MACE_CANDIDATE' else flag in row['flags'])]
        rules[flag] = {'n': len(flagged), 'N': len(admitted), 'n_of_N': f'{len(flagged)} of {len(admitted)}',
                       'items': flagged, 'unit': 'admitted transcription row; never a pooled row'}
    # Census format changes separately from refusals; no unrelated topic denominator.
    observed = [(result['item'], entry, reading) for result in results
                for entry in result.get('agreement_audit', {}).get('keys', [])
                for reading in entry['readings']]
    for rule, field in (('PERCENT_NORMALIZATION', 'percent'), ('HEADER_N_FALLBACK', 'N')):
        changed = [f"{item}/{'/'.join(entry['key'])}/{reading['model']}"
                   for item, entry, reading in observed
                   if reading['raw'].get(field) != reading['effective'].get(field)]
        rules[rule] = {'n': len(changed), 'N': len(observed),
            'n_of_N': f'{len(changed)} of {len(observed)}', 'items': changed,
            'unit': 'reader row with resolved key; raw vs effective value'}
    order_items, order_changed = [], []
    for image_key, records in sorted(groups.items()):
        seen_models = set()
        for record in records:
            if record.get('state') != 'RAN_OK' or ms.record_problems(record):
                continue
            mid = record['model']['id_reported']
            if mid in seen_models:
                continue
            seen_models.add(mid)
            for table in json.loads(ms.replay(record))['tables']:
                item = '/'.join(image_key) + '/' + table['table_id'] + '/' + mid
                order_items.append(item)
                keys = [gate.row_key(table['table_id'], row) for row in table['rows']]
                canonical = sorted(keys, key=lambda k: (k[0], k[1], k[3], gate.ARMS.index(k[2])))
                if keys != canonical:
                    order_changed.append(item)
    rules['KEY_ALIGNMENT'] = {'n': len(order_changed), 'N': len(order_items),
        'n_of_N': f'{len(order_changed)} of {len(order_items)}', 'items': order_changed,
        'unit': 'distinct-model table reordered into deterministic key order'}
    batch = gate.gate_batches([record for records in groups.values() for record in records], text, images,
            replay_response=ms.replay, record_problems=ms.record_problems, target=gate.target_from_topic(root)) if groups else None
    cross_flagged = ['DISPERSE-2 recorded table batch'] if batch and 'across recorded tables' in batch.get('reason', '') else []
    rules['ACROSS_TABLE_ARM_N'] = {'n': len(cross_flagged), 'N': int(bool(groups)),
        'n_of_N': f'{len(cross_flagged)} of {int(bool(groups))}', 'items': cross_flagged,
        'unit': 'recorded table batch; cross-table check requires passing individual image gates'}
    return {'topics_examined': len(topics), 'topic_names': topics, 'topic_coverage': {'n': len(set(matched)), 'N': len(topics),
            'n_of_N': f'{len(set(matched))} of {len(topics)}', 'items': sorted(set(matched))},
            'batch_result': batch, 'no_recorded_proposal': {'n': len(set(matched)) if not groups else 0,
                'N': len(topics), 'n_of_N': f'{len(set(matched)) if not groups else 0} of {len(topics)}',
                'items': sorted(set(matched)) if not groups else []}, 'mention_sources': sorted(items), 'input_errors': errors, 'rules': rules,
            'total_treated_evidence': gate.text_evidence(text),
            'pdf_pages': manifest['pages_examined'], 'mention_pages': len(manifest['mention_pages']),
            'images': [{'page': i['page'], 'image_index': i['image_index'], 'sha256': i['sha256'],
                        'rendered_sha256': i['rendered_sha256'], 'dimensions': [i['width'], i['height']],
                        'captions': i['captions']} for i in manifest['images']],
            'proposal_results': results,
            'interpretation': '0 of 0 means NOT EXAMINED. No recorded DISP2CALL proposals exist unless listed; no empirical rows inferred.'}


def prepare(image_sha, images):
    context = images[image_sha]
    return {'prompt': PROMPT + '\nIMAGE SHA256: ' + image_sha +
            '\nHELD STUDY SECTION: ' + context['study'] + '\nHELD PAGE CONTEXT:\n' + context['text'] +
            '\nCAPTIONS:\n' + json.dumps(context['captions']), 'schema': SCHEMA,
            'image': {'ref': context['path'], 'sha256': image_sha}, 'status': 'PREPARED_NOT_CALLED'}


BINDING = Path('docs/disperse2_table_binding.json')


def binding_bytes(root=ROOT):
    """Offline replay only; the build consumes the resulting data artifact."""
    root = Path(root)
    paths = sorted((root / 'evidence/model_calls/disperse2_table_records.txt').read_text(encoding='utf-8').split())
    records = [ms.load_record(root / p) for p in paths]
    ids = {r['record_id'] for r in records}
    for path in sorted((root / 'evidence/model_calls').glob('*.json')):
        record = ms.load_record(path)
        if record.get('caller', {}).get('lane') == 'DISP2CALL' and record['record_id'] not in ids:
            records.append(record)
            ids.add(record['record_id'])
    text, images = gate.held_inputs(root)
    result = gate.gate_batches(records, text, images, replay_response=ms.replay,
        record_problems=ms.record_problems, target=gate.target_from_topic(root))
    if result['status'] != 'ADMIT':
        raise ValueError('DISPERSE_BINDING_REFUSED: ' + result.get('reason', 'gate failed'))
    if any(len(g['model_ids']) < 3 or len(set(g['record_ids'])) < 3 for g in result['groups']):
        raise ValueError('DISPERSE_BINDING_REFUSED: three distinct recorded readings required per image')
    from harness import table_binding
    old_root = table_binding.ROOT
    try:
        table_binding.ROOT = root
        pmid = table_binding._pmid('ticagrelor-vs-clopidogrel-acs', 'DISPERSE-2')
    finally:
        table_binding.ROOT = old_root
    payload = dict(schema='disperse2-table-binding-v1', trial='DISPERSE-2', pmid=pmid,
        topic='ticagrelor-vs-clopidogrel-acs', status='REFUSED', POOLABLE=False, poolable=False,
        state='MODEL_TRANSCRIBED_CHECKED', gate=result,
        record_ids=sorted(r['record_id'] for r in records),
        image_sha256s=sorted({r['image_sha256'] for r in result['rows']}))
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def verify_binding(root=ROOT):
    expected = binding_bytes(root)
    if (Path(root) / BINDING).read_bytes() != expected:
        raise ValueError('STALE_DISPERSE_BINDING: ' + BINDING.as_posix())
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', metavar='RENDERED_SHA256')
    mode.add_argument('--gate', nargs='+', metavar='RECORD')
    mode.add_argument('--call', action='store_true')
    mode.add_argument('--census', action='store_true')
    mode.add_argument('--write-binding', action='store_true')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--image', type=Path)
    parser.add_argument('--model')
    parser.add_argument('--effort', default='medium')
    args = parser.parse_args(argv)
    if args.call and (not args.image or not args.model):
        parser.error('--call requires --image and --model')
    try:
        if args.write_binding:
            raw = binding_bytes(args.root)
            (args.root / BINDING).write_bytes(raw)
            result = {'status': 'ADMIT', 'binding': BINDING.as_posix(), 'poolable': False}
        elif args.census:
            result = census(args.root)
        else:
            text, images = gate.held_inputs(args.root)
            if args.call:
                from reproducible_ai import model_call_live
                path = args.image if args.image.is_absolute() else args.root / args.image
                path = path.resolve()
                matches = [digest for digest, context in images.items()
                           if (args.root / context['path']).resolve() == path]
                if len(matches) != 1:
                    raise ValueError('IMAGE_SOURCE: --image is not a verified held render')
                if images[matches[0]]['study'] != 'DISPERSE-2':
                    raise ValueError('STUDY_IDENTITY: refused image outside DISPERSE-2')
                request = prepare(matches[0], images)
                rec = model_call_live.call(request['prompt'].encode('utf-8'), schema=SCHEMA,
                    model=args.model, effort=args.effort,
                    caller={'file': 'scripts/disperse2_figure_proposal.py', 'line': 'main --call',
                            'purpose': 'Independent DISPERSE-2 table transcription', 'lane': 'DISP2CALL'},
                    input_digests=[], images=(path,), image_root=args.root)
                print(ms.write_record(rec, args.root / 'evidence/model_calls').relative_to(args.root).as_posix())
                return 0 if rec['state'] == 'RAN_OK' else 1
            elif args.prepare:
                result = prepare(args.prepare, images)
            else:
                records = [ms.load_record(p) for p in args.gate]
                result = gate.gate_batches(records, text, images, replay_response=ms.replay,
                    record_problems=ms.record_problems, target=gate.target_from_topic(args.root))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get('status') == 'REFUSED' else 0
    except (ValueError, OSError, KeyError) as exc:
        print(json.dumps({'status': 'REFUSED', 'reason': str(exc), 'rows': []}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
