"""L11: one recorded, licence-gated Reader A per supplement image; no admission."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import copy_licence, http
from scripts import g1_forest_reader as fr
from reproducible_ai import model_call_live as live, model_source as ms
from kgap import k_gap
from PIL import Image

CENSUS = ROOT / 'outputs/k_gap/image_census/IMAGE_CENSUS.json'
OUT = ROOT / 'outputs/k_gap/image_reads'
CACHE = ROOT / '.image_cache'
REC_DIR = ROOT / 'evidence/model_calls/image_tables'
METAS = {'34484209', '40159279', '37381009', '39076869'}
API = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n', encoding='utf8')


def dedupe(rows):
    """Exact-byte dedupe first; named GIF/JPEG renditions second (not hash equality)."""
    hashes = {}
    for row in rows:
        hashes.setdefault(row['sha256'], []).append(row)
    groups = {}
    for sources in hashes.values():
        row = sources[0]
        p = Path(row['file'])
        key = (row['meta'], p.stem) if p.suffix.lower() in {'.gif', '.jpg', '.jpeg'} else row['sha256']
        groups.setdefault(key, []).extend(sources)
    result = []
    for sources in groups.values():
        chosen = sorted(sources, key=lambda r: (Path(r['file']).suffix.lower() not in {'.jpg', '.jpeg'}, r['file']))[0]
        result.append(dict(chosen, sources=sources))
    return sorted(result, key=lambda r: (r['meta'], r['file']))


def prepare_image(path):
    path = Path(path)
    original = digest(path)
    attached = path
    if path.suffix.lower() in {'.tif', '.tiff'}:
        attached = path.with_suffix('.png')
        with Image.open(path) as im:
            if getattr(im, 'n_frames', 1) != 1:
                raise ValueError('MULTIFRAME_TIFF_REFUSED')
            im.save(attached, format='PNG')
            with Image.open(attached) as check:
                if (im.mode, im.size, im.tobytes()) != (check.mode, check.size, check.tobytes()):
                    raise ValueError('LOSSLESS_CONVERSION_FAILED')
    return attached, dict(source_sha256=original, attached_sha256=digest(attached))


def image_prompt(name, reader='codex', table=False):
    # Builder sees only an image filename, never captions, trial targets or paper text.
    fig = {'caption': name, 'image_name': name}
    prompt = fr.prompt_bytes(fig, reader)
    prompt = prompt.replace(b'FIGURE CAPTION (from the article):', b'IMAGE FILE:')
    if table:
        prompt += fr.IMAGE_TABLE_INSTR.encode('utf8')
    return prompt


def checked_licence(xml, metadata_license=None):
    """The ONE licence rule is harness.copy_licence.classify_permissions (D8; owned by the D8 lane). No second reading
    here: a JATS that states CC BY only in words with no licence URL (34484209) is NOT_OPEN until that rule says
    otherwise -- the Europe PMC metadata value is recorded (metadata_license) but never grants a model read.
    (Adjudicated by the coverage lane, 15 Oct: the lane's metadata fallback was a parallel licence rule; removed.)"""
    return copy_licence.classify_permissions(xml)


def read_image(path, expected, xml, runner=None, table=False, metadata_license=None):
    licence, statement = checked_licence(xml, metadata_license)
    result = dict(licence=licence, licence_statement=statement, rows=[], candidates=[], record_id=None)
    if licence != 'CC':
        return dict(result, state='LICENCE_REFUSED')
    if digest(path) != expected:
        return dict(result, state='HASH_MISMATCH', observed_sha256=digest(path))
    attached, hashes = prepare_image(path)
    prompt = image_prompt(attached.name, table=table)
    rec = live.call(prompt, schema=fr.SCHEMA, model=fr.CODEX_MODEL, effort=fr.CODEX_EFFORT,
                    caller={'file': 'scripts/lane_image_reader.py', 'line': 'read_image',
                            'lane': 'L11/reader-a', 'purpose': 'Unadmitted supplement image transcription'},
                    input_digests=[{'ref': Path(path).name, 'sha256': expected, 'what': 'CC BY/CC0 image'},
                                   {'ref': 'acquired JATS', 'sha256': hashlib.sha256(xml.encode()).hexdigest(),
                                    'what': 'licence checked before call; not shown to model'}],
                    images=(attached,), runner=runner, timeout_s=900)
    ms.write_record(rec, REC_DIR)
    result.update(hashes, record_id=rec['record_id'], record_state=rec['state'],
                  prompt=prompt.decode(), prompt_sha256=hashlib.sha256(prompt).hexdigest(),
                  attached_file=attached.name, error=rec.get('error'))
    if rec['state'] != 'RAN_OK':
        return dict(result, state='CALL_FAILED')
    reading, error = fr.parse_reading(ms.replay(rec))
    if error:
        return dict(result, state='PARSE_FAILED', error=error)
    return dict(result, state='READER_A_ONLY', rows=reading['rows'], reading=reading)


def norm(label):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\[\d+\]', '', label or '').lower())


def candidates(item):
    matches = []
    for row in item.get('rows', []):
        label = norm(row.get('label'))
        possible = {(s['topic'], t) for s in item['sources'] for t in s['missing_trials'] if norm(t) == label and label}
        if len(possible) == 1:
            topic, trial = next(iter(possible))
            matches.append(dict(topic=topic, trial=trial, printed_label=row['label'], state='CANDIDATE_ONLY'))
    return matches


def funnel(items, trial_total):
    read = [i for i in items if i['state'] == 'READER_A_ONLY']
    rows = [i for i in read if i.get('rows')]
    matched = [i for i in rows if i.get('candidates')]
    trials = {(c['topic'], c['trial']) for i in matched for c in i['candidates']}
    return dict(distinct_images=len(items), read={'n': len(read), 'N': len(items)},
                with_rows={'n': len(rows), 'N': len(read)}, with_missing_trial={'n': len(matched), 'N': len(rows)},
                trials_with_candidate={'n': len(trials), 'N': trial_total}, secondary=0)


def fetch(url, path, params=None):
    if path.exists():
        return path.read_bytes()
    if not url.startswith(API):
        raise ValueError('EUROPE_PMC_ONLY')
    time.sleep(0.5)
    status, data = http.get_raw(url, params=params, tries=2, timeout=180)
    if status != 200:
        raise ValueError(f'HTTP {status}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def acquire(meta, rows):
    folder = CACHE / meta
    metadata = json.loads(fetch(API + 'search', folder / 'metadata.json',
                         {'query': f'EXT_ID:{meta} AND SRC:MED', 'format': 'json', 'resultType': 'core'}))
    records = metadata['resultList']['result']
    exact = [r for r in records if str(r.get('id')) == meta and r.get('source') == 'MED']
    if len(exact) != 1 or not exact[0].get('pmcid'):
        raise ValueError('PMID_PMCID_UNVERIFIED')
    pmcid = exact[0]['pmcid']
    xml = fetch(API + pmcid + '/fullTextXML', folder / 'article.xml').decode('utf8')
    lic, stmt = checked_licence(xml, exact[0].get('license'))
    audit = dict(meta=meta, pmcid=pmcid, licence=lic, statement=stmt, metadata_license=exact[0].get('license'),
                 metadata_sha256=digest(folder / 'metadata.json'), jats_sha256=digest(folder / 'article.xml'))
    if lic != 'CC':
        return xml, audit, []
    url = API + pmcid + '/supplementaryFiles'
    data = fetch(url, folder / 'supplements.zip')
    audit.update(route=url, zip_sha256=hashlib.sha256(data).hexdigest())
    wanted = {r['file'] for r in rows}
    found = set()
    for name, content in k_gap._zip_members(data):
        if name in wanted:
            if name in found:
                raise ValueError('DUPLICATE_ZIP_BASENAME')
            if Path(name).name != name:
                raise ValueError('UNSAFE_BASENAME')
            (folder / name).write_bytes(content)
            found.add(name)
    failures = []
    for row in rows:
        p = folder / row['file']
        actual = digest(p) if p.exists() else None
        if actual != row['sha256']:
            failures.append(dict(meta=meta, file=row['file'], expected=row['sha256'], observed=actual,
                                 state='HASH_MISMATCH' if actual else 'IMAGE_MISSING'))
    return xml, audit, failures


def report(data):
    save(OUT / 'READER_A.json', data)
    lines = ['# Reader A — unadmitted image readings', '', 'All successful reads are READER_A_ONLY. No secondary admissions.',
             '', 'Funnel: `' + json.dumps(data['funnel'], sort_keys=True) + '`', '',
             'Candidates use exact normalized names only; no inferred author/title identities.', '',
             '| Meta | Image | State | Rows | Record |', '|---|---|---|---:|---|']
    for i in data['images']:
        lines.append(f"| {i['meta']} | {i['file']} | {i['state']} | {len(i.get('rows', []))} | {i.get('record_id') or '-'} |")
    (OUT / 'READER_A.md').write_text('\n'.join(lines) + '\n', encoding='utf8')
    owed = ['# Reader B owed after the 17 October reset', '',
            'Use agy (Gemini), one recorded call per eligible image, with the forest SCHEMA. Independently read the image; do not show Reader A answers.',
            'Nothing is SECONDARY_PROVISIONAL until both readers agree within printed rounding. This lane admits nothing.',
            'Recheck acquired JATS licence and all hashes first. Failed acquisition/licence/hash checks remain blocked.', '']
    for i in data['images']:
        name = i.get('attached_file', Path(i['file']).with_suffix('.png').name if Path(i['file']).suffix.lower() in {'.tif', '.tiff'} else i['file'])
        owed += [f"## {i['meta']} / {i['file']}", '', f"Source SHA256: `{i['sha256']}`",
                 f"Attached SHA256: `{i.get('attached_sha256', 'NOT_ACQUIRED')}`", f"Reader A state: {i['state']}",
                 'Aliases: `' + json.dumps([{'file': s['file'], 'sha256': s['sha256']} for s in i['sources']], sort_keys=True) + '`',
                 '', '```text', image_prompt(name, 'agy', i['class'] == 'SUPPLEMENT_TABLE_IMAGE').decode(), '```', '']
    (OUT / 'READER_B_OWED.md').write_text('\n'.join(owed), encoding='utf8')


def client_preflight():
    try:
        probe = subprocess.run([live._codex_exe(), 'login', 'status'], capture_output=True, timeout=20)
        text = (probe.stderr or probe.stdout).decode('utf8', 'replace')
        return {'state': 'READY' if probe.returncode == 0 else 'AUTH_REQUIRED',
                'exit_code': probe.returncode,
                'message': 'Not logged in' if 'Not logged in' in text else 'CLI login status checked; identity omitted',
                'output_sha256': hashlib.sha256(probe.stdout + probe.stderr).hexdigest()}
    except (OSError, subprocess.SubprocessError) as exc:
        return {'state': 'CLIENT_UNAVAILABLE', 'error_type': type(exc).__name__}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    census = json.loads(CENSUS.read_text(encoding='utf8'))
    rows = []
    for meta in census['metas']:
        if meta['meta'] not in METAS or meta['licence_gate'] != 'OPEN_FOR_MODEL':
            continue
        phase = ROOT / f"outputs/k_gap/registry_fill/phase4_supplements/{meta['topic']}.json"
        if digest(phase) != census['source_sha256'][phase.relative_to(ROOT).as_posix()]:
            raise ValueError('PHASE4_SOURCE_DRIFT')
        files = json.loads(phase.read_text(encoding='utf8'))['metas'][meta['meta']]['files']
        hashes = {f['file']: f['sha256'] for f in files}
        for image in meta['images']:
            if image['class'].startswith('SUPPLEMENT_') and not image['already_read']:
                if hashes.get(image['file']) != image['sha256']:
                    raise ValueError('CENSUS_PHASE4_HASH_DISAGREEMENT')
                rows.append(dict(image, meta=meta['meta'], topic=meta['topic'], missing_trials=meta['missing_trials']))
    items = dedupe(rows)
    previous = json.loads((OUT / 'READER_A.json').read_text(encoding='utf8')) if (OUT / 'READER_A.json').exists() else {}
    existing = {i['sha256']: i for i in previous.get('images', []) if i.get('record_id')}
    audit, failures, xmls = [], [], {}
    for meta in sorted(METAS):
        try:
            xml, entry, problems = acquire(meta, [r for r in {r['file']: r for r in rows if r['meta'] == meta}.values()])
            xmls[meta] = xml
            audit.append(entry)
            failures.extend(problems)
        except Exception as exc:
            audit.append(dict(meta=meta, state='ACQUISITION_FAILED', error=str(exc)))
    for item in items:
        item.update(state='PENDING', rows=[], candidates=[], record_id=None)
        if item['meta'] not in xmls:
            item['state'] = 'ACQUISITION_FAILED'
        elif next(a for a in audit if a['meta'] == item['meta']).get('licence') != 'CC':
            item['state'] = 'LICENCE_REFUSED'
        elif any(f['meta'] == item['meta'] and f['file'] in {s['file'] for s in item['sources']} for f in failures):
            item['state'] = 'HASH_REFUSED'
        else:
            try:
                attached, hashes = prepare_image(CACHE / item['meta'] / item['file'])
                item.update(hashes, attached_file=attached.name)
                prompt = image_prompt(attached.name, table=item['class'] == 'SUPPLEMENT_TABLE_IMAGE')
                item.update(prompt=prompt.decode(), prompt_sha256=hashlib.sha256(prompt).hexdigest())
            except Exception as exc:
                item.update(state='CONVERSION_REFUSED', error=str(exc))
            if item['sha256'] in existing:
                item.update(existing[item['sha256']])
    data = dict(census_sha256=digest(CENSUS), source_files=len(rows), unique_byte_hashes=len({r['sha256'] for r in rows}),
                dedupe_rule='Exact SHA256 then named GIF/JPEG renditions; JPEG selected, both hashes retained.',
                acquisition=audit, refusals=failures, images=items)
    def checkpoint():
        data['funnel'] = funnel(items, len(census['overall']['affected_trial_labels']))
        report(data)
    checkpoint()
    if args.run:
        data['client_preflight'] = client_preflight()
        save(OUT / 'CLI_PREFLIGHT.json', data['client_preflight'])
        if data['client_preflight']['state'] != 'READY':
            for item in items:
                if item['state'] == 'PENDING':
                    item['state'] = data['client_preflight']['state']
            checkpoint()
            print(json.dumps(data['client_preflight']), flush=True)
            return
        with ThreadPoolExecutor(max_workers=3) as pool:
            pending = {pool.submit(read_image, CACHE / i['meta'] / i['file'], i['sha256'], xmls[i['meta']],
                                   table=i['class'] == 'SUPPLEMENT_TABLE_IMAGE',
                                   metadata_license=next(a for a in audit if a['meta'] == i['meta']).get('metadata_license')): i for i in items if i['state'] == 'PENDING'}
            for future in as_completed(pending):
                item = pending[future]
                try:
                    item.update(future.result())
                    item['candidates'] = candidates(item)
                except Exception as exc:
                    item.update(state='CALL_BLOCKED', error=str(exc))
                checkpoint()
                print(item['meta'], item['file'], item['state'], flush=True)
    print(json.dumps(data['funnel']), flush=True)


if __name__ == '__main__':
    main()
