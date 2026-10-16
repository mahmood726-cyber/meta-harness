"""Reader A (codex, recorded) x reader B (second family) on the supplement images -> SECONDARY_PROVISIONAL rows.

Rows are admitted only where BOTH readings agree within the printed rounding (g1_forest_reader.agree). A row
matched to a missing trial by name is a candidate; nothing here is PRIMARY_VERIFIED (that needs verify_typed
against the source). Every refusal keeps both readings.

  python scripts/lane_image_agreement.py --reader-b <readerB_out*.json ...> --reader-b-model <alias>
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
import g1_forest_reader as fr  # noqa: E402
from lane_image_reader import candidates  # noqa: E402

OUT = ROOT / 'outputs/k_gap/image_reads'
REC_DIR = ROOT / 'evidence/model_calls/image_tables_reader_b'
LANE_LOG = ROOT / 'registry/model_calls/lane_log/coverage__reader-b.jsonl'


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def b_records(answers, model, batches):
    """One record per reader-B answer: the image and prompt it saw (by sha256), its answer, and the model alias.
    The second family ran as a subagent, so its client is NOT attested -- the record says so."""
    out = {}
    for a in answers:
        rec = dict(record_id='mcb-' + digest([a['key'], a['image_sha256'], a['prompt_sha256'], a['answer']])[:32],
                   caller=dict(file='scripts/lane_image_agreement.py', lane='coverage/reader-b',
                               purpose='Unadmitted supplement image transcription, second reader'),
                   model=model, client='subagent (Agent tool)', attested=False,
                   input_digests=dict(source_sha256=a['key'], image_sha256=a['image_sha256'],
                                      prompt_sha256=a['prompt_sha256']),
                   batch_sha256=batches.get(a['key']), response=a['answer'],
                   state='RECORDED_UNATTESTED')
        out[a['key']] = rec
    return out


def compare(item, rb):
    """One image: reader A's reading x reader B's -> state + rows."""
    ra = item.get('reading')
    if item.get('state') != 'READER_A_ONLY' or not isinstance(ra, dict):
        return dict(state='NOT_READ_BY_A', proposed=[], refused=[], problems=[])
    if rb is None:
        return dict(state='READER_B_MISSING', proposed=[], refused=[], problems=[])
    probs = fr.shape_problems(rb)
    if probs:
        return dict(state='READER_B_SCHEMA', proposed=[], refused=[], problems=probs)
    if not ra.get('rows') and not rb.get('rows'):
        return dict(state='NO_ROWS_IN_EITHER', proposed=[], refused=[], problems=[])
    proposed, refused, pooled, problems, not_est = fr.agree(ra, rb)
    blocking = [p for p in problems if p.startswith(('NOT_LEGIBLE', 'ROWS_ARE_NOT_STUDIES', 'MEASURE_DISAGREES'))]
    if blocking:
        # a figure both readers cannot read as study rows, or read under different measures: no row is admitted
        refused = refused + [dict(label=r['label'], why='FIGURE_' + blocking[0].split(':')[0], a=r, b=None)
                             for r in proposed]
        proposed = []
    for r in proposed:
        r['state'] = 'SECONDARY_PROVISIONAL'
    return dict(state='COMPARED', proposed=proposed, refused=refused, pooled=pooled, problems=problems,
                not_estimable=not_est)


def run(reader_a, answers, model, batches, trial_total):
    recs = b_records(answers, model, batches)
    images, trials_secondary, trials_a = [], set(), set()
    for item in reader_a['images']:
        rec = recs.get(item['sha256'])
        if rec and rec['input_digests']['image_sha256'] != item.get('attached_sha256'):
            res = dict(state='READER_B_IMAGE_MISMATCH', proposed=[], refused=[], problems=[])
        else:
            res = compare(item, rec['response'] if rec else None)
        cands = candidates(dict(rows=res['proposed'], sources=item['sources']))
        for c in cands:
            c['state'] = 'SECONDARY_PROVISIONAL_CANDIDATE'
            trials_secondary.add((c['topic'], c['trial']))
        trials_a |= {(c['topic'], c['trial']) for c in item.get('candidates', [])}
        images.append(dict(sha256=item['sha256'], file=item['file'], meta=item['meta'],
                           reader_a_record=item.get('record_id'), reader_b_record=rec and rec['record_id'],
                           candidates=cands, **res))
    compared = [i for i in images if i['state'] == 'COMPARED']
    with_rows = [i for i in compared if i['proposed']]
    funnel = dict(distinct_images=len(images), compared={'n': len(compared), 'N': len(images)},
                  with_agreed_rows={'n': len(with_rows), 'N': len(compared)},
                  agreed_rows=sum(len(i['proposed']) for i in images),
                  refused_rows=sum(len(i['refused']) for i in images),
                  trials_reader_a_candidate={'n': len(trials_a), 'N': trial_total},
                  trials_secondary_provisional={'n': len(trials_secondary), 'N': trial_total},
                  primary_verified=0)
    return images, recs, funnel, sorted(trials_secondary)


def report(data):
    f = data['funnel']
    lines = ['# Image reads: reader A x reader B', '',
             f"Reader A: codex (recorded). Reader B: {data['reader_b_model']} (recorded, client NOT attested).",
             'A row is SECONDARY_PROVISIONAL only when both readings agree within the printed rounding; '
             'PRIMARY_VERIFIED needs verify_typed against the source and is 0 here.', '',
             '| step | n | N |', '|---|---|---|',
             f"| images compared | {f['compared']['n']} | {f['compared']['N']} |",
             f"| with >=1 agreed row | {f['with_agreed_rows']['n']} | {f['with_agreed_rows']['N']} |",
             f"| missing trials, reader-A candidate | {f['trials_reader_a_candidate']['n']} | "
             f"{f['trials_reader_a_candidate']['N']} |",
             f"| missing trials, SECONDARY_PROVISIONAL candidate | {f['trials_secondary_provisional']['n']} | "
             f"{f['trials_secondary_provisional']['N']} |", '',
             f"Agreed rows {f['agreed_rows']}, refused rows {f['refused_rows']}, PRIMARY_VERIFIED {f['primary_verified']}.",
             '', '## Missing-trial candidates', '']
    for i in data['images']:
        for c in i['candidates']:
            lines.append(f"- {c['topic']}: `{c['trial']}` <- '{c['printed_label']}' ({i['file']}, {c['state']})")
    lines += ['', '## Per image', '', '| meta | file | state | agreed | refused | problems |', '|---|---|---|---|---|---|']
    for i in data['images']:
        lines.append(f"| {i['meta']} | {i['file']} | {i['state']} | {len(i['proposed'])} | {len(i['refused'])} | "
                     f"{'; '.join(i['problems'][:3])} |")
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reader-b', nargs='+', required=True)
    ap.add_argument('--batches', nargs='*', default=[])
    ap.add_argument('--reader-b-model', required=True)
    ap.add_argument('--trial-total', type=int, default=11)
    a = ap.parse_args()
    reader_a = json.loads((OUT / 'READER_A.json').read_text(encoding='utf8'))
    answers = [x for p in a.reader_b for x in json.loads(Path(p).read_text(encoding='utf8'))['answers']]
    batches = {}
    for p in a.batches:
        raw = Path(p).read_bytes()
        for x in json.loads(raw)['items']:
            batches[x['key']] = hashlib.sha256(raw).hexdigest()
    images, recs, funnel, trials = run(reader_a, answers, a.reader_b_model, batches, a.trial_total)
    REC_DIR.mkdir(parents=True, exist_ok=True)
    log = []
    for r in recs.values():
        path = REC_DIR / f"{r['record_id']}.json"
        # LF bytes: the ledger hash must be the hash of the blob git stores
        path.write_bytes((json.dumps(r, indent=1, ensure_ascii=False) + '\n').encode('utf8'))
        log.append(json.dumps(dict(record_id=r['record_id'], model=r['model'], attested=False,
                                   record=path.relative_to(ROOT).as_posix(),
                                   record_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                   **r['input_digests']), sort_keys=True))
    LANE_LOG.write_bytes(('\n'.join(sorted(log)) + '\n').encode('utf8'))
    data = dict(created_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                reader_a_sha256=hashlib.sha256((OUT / 'READER_A.json').read_bytes()).hexdigest(),
                reader_b_model=a.reader_b_model, funnel=funnel, secondary_trials=trials, images=images)
    (OUT / 'READER_AB.json').write_bytes((json.dumps(data, indent=1, ensure_ascii=False) + '\n').encode('utf8'))
    (OUT / 'READER_AB.md').write_bytes(report(data).encode('utf8'))
    print(json.dumps(funnel))


if __name__ == '__main__':
    main()
