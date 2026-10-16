"""Finish the frozen v2 screen using stored C2/C3 reads only.

Run from the captain's shell: python scripts/bench_v2_finish.py
Re-run the same command to resume; pending/error records are reconsidered.

Hardcode disclosure:
| Static | preregistered 800 budget, 20 stop, 3..25 k, criterion order |
| Dynamic | frozen inputs, stored reads/adjudications, XML, registry evidence |
| Synthetic | isolated test fixtures only |
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import time

import bench_screen_v2 as v2

old = v2.old
ROOT = v2.ROOT
FINISH = v2.OUT / 'v2_finish'
INDEX = v2.OUT / 'v2_inputs/INDEX.json'


def combine_decisions(a, b, adjudication=None):
    """Inputs A/B contain answer and a freshly checked span_check."""
    pending = dict(status='PENDING_ADJUDICATION', c2c3_source=None,
                   k_rcts=None, first_failure=None)
    if adjudication is not None:
        passed = adjudication.get('c2_c3_pass')
        k = adjudication.get('k_rcts')
        if type(passed) is not bool or (passed and (type(k) is not int or not 3 <= k <= 25)):
            return dict(pending, c2c3_source='adjudicated', reason='Invalid adjudication schema')
        criterion = adjudication.get('first_failure')
        if criterion not in ('C2', 'C3'):
            # A combined rejection alone cannot establish which criterion failed.
            criterion = 'C2/C3'
        return dict(status='PASS' if passed else 'EXCLUDED', c2c3_source='adjudicated',
                    k_rcts=k, first_failure=None if passed else criterion)
    if not all(r and r.get('span_check', {}).get('status') == 'VERIFIED' for r in (a, b)):
        return dict(pending, reason='Missing or unverified reader')
    aa, bb = a['answer'], b['answer']
    def failure(answer):
        if answer.get('pairwise_rct_meta') == 'no':
            return 'C2'
        k = answer.get('k_rcts')
        if answer.get('pairwise_rct_meta') != 'yes':
            return None
        return 'C3' if k is None or (type(k) is int and not 3 <= k <= 25) else None
    fa, fb = failure(aa), failure(bb)
    if fa and fb:
        return dict(status='EXCLUDED', c2c3_source='agreed',
                    k_rcts=aa.get('k_rcts') if aa.get('k_rcts') == bb.get('k_rcts') else None,
                    first_failure=fa if fa == fb else 'C2/C3')
    k = aa.get('k_rcts')
    if (aa.get('pairwise_rct_meta') == bb.get('pairwise_rct_meta') == 'yes'
            and type(k) is int and k == bb.get('k_rcts') and type(bb.get('k_rcts')) is int
            and 3 <= k <= 25):
        return dict(status='PASS', c2c3_source='agreed', k_rcts=k, first_failure=None)
    return dict(pending, reason='Reader disagreement')


def cached_xml(pmcid):
    for path in (ROOT / 'cache/benchmarks/v1' / (pmcid + '.xml'),
                 v2.LOGS / 'bench_v2_sources' / (pmcid + '.xml')):
        if path.is_file():
            return path, path.read_bytes()
    raise v2.NeedsWork('Cached XML is missing')


def stored_read(pmcid, reader, raw, input_path=None):
    path = v2.READS / f'{pmcid}.reader{reader}.json'
    if not path.exists():
        return None
    item = v2.load(path)
    answer = item.get('answer', item)
    check = v2.verify_answer(raw, answer)
    # Resolve only the named prepared input; old absolute roots are not portable.
    if input_path is None and item.get('input_file'):
        name = Path(item['input_file'].replace('\\', '/')).name
        if name.endswith('_' + pmcid + '.txt'):
            input_path = ROOT / 'registry/benchmarks/v2_inputs' / name
    if input_path is None and INDEX.is_file():
        entry = next((e for e in v2.load(INDEX) if e['pmcid'] == pmcid), {})
        if entry.get('file'):
            input_path = ROOT / entry['file']
    source = (v2.normalise(Path(input_path).read_text(encoding='utf-8'))
              if input_path is not None and Path(input_path).is_file() else '')
    spans = {}
    for field in ('design_quote', 'k_quote'):
        value = answer.get(field, '')
        quote = v2.normalise(value) if isinstance(value, str) else ''
        start = source.find(quote) if quote else -1
        xml_span = check['spans'][field]
        found = isinstance(value, str) and (not quote or start >= 0
                                            or (reader == 'A' and xml_span['found']))
        spans[field] = dict(quote=quote, found=found,
                            source='input' if start >= 0 else 'xml' if quote and found else None,
                            start=start if start >= 0 else None,
                            end=start + len(quote) if start >= 0 else None)
    check = dict(check, spans=spans, normalised_input_sha256=v2.sha(source),
                 status='VERIFIED' if check['schema_ok'] and all(s['found'] for s in spans.values())
                 else 'UNVERIFIED')
    errors = []
    if item.get('pmcid') != pmcid:
        errors.append('PMCID mismatch')
    if item.get('xml_sha256') and item['xml_sha256'] != v2.sha(raw):
        errors.append('XML hash mismatch')
    for field in ('prompt', 'response'):
        if field + '_sha256' in item and v2.sha(item.get(field, '')) != item[field + '_sha256']:
            errors.append(field + ' hash mismatch')
    if 'response' in item and v2.parse_response(item['response']) != answer:
        errors.append('Response differs from answer')
    if item.get('span_check', {}).get('status', 'VERIFIED') != 'VERIFIED':
        errors.append('Stored verification failed')
    if errors:
        check = dict(check, status='UNVERIFIED', errors=errors)
    return dict(answer=answer, span_check=check, read_id=item.get('read_id', path.stem),
                file=path.relative_to(ROOT).as_posix(), sha256=v2.sha(path.read_bytes()))


def screen(hit, entry, client, topics, areas, previous, save):
    pmcid = hit['pmcid']
    result = {key: hit.get(key) for key in ('id', 'pmid', 'pmcid', 'title', 'license')}
    result.update(status='IN_PROGRESS', verdict='IN_PROGRESS', first_failure=None,
                  evidence={}, checks={}, c2c3_source=None, c4_trial_resolutions=[])
    def fail(criterion, evidence, status='EXCLUDED'):
        result.update(first_failure=criterion, evidence=evidence, status=status, verdict=status)
        return result
    criterion = 'C1'
    try:
        if not entry or 'error' in entry or not entry.get('file') or not (ROOT / entry['file']).is_file():
            return fail(None, {'reason': 'Missing prepared input', 'index_entry': entry}, 'NEEDS_INSPECTION')
        if not old.accepted_license(hit.get('license')):
            return fail('C1', {'license': hit.get('license')})
        path, raw = cached_xml(pmcid)
        if hit.get('baseline_xml_sha256') and hit['baseline_xml_sha256'] != v2.sha(raw):
            raise ValueError('Baseline XML hash mismatch')
        root = old.parse_xml(raw, 'article')
        result.update(xml_sha256=v2.sha(raw), xml_cache=path.relative_to(ROOT).as_posix())
        result['checks']['C1'] = {'license': hit['license'], 'xml_sha256': v2.sha(raw)}
        criterion = 'C2/C3'
        adj_path = v2.READS / (pmcid + '.adjudication.json')
        if adj_path.exists():
            adjudication = v2.load(adj_path)
            if adjudication.get('pmcid', pmcid) != pmcid:
                raise ValueError('Adjudication PMCID mismatch')
            decision = combine_decisions(None, None, adjudication)
            result['c2c3_evidence'] = {'adjudication': adjudication, 'sha256': v2.sha(adj_path.read_bytes())}
        else:
            reads = []
            for reader in ('A', 'B'):
                try:
                    reads.append(stored_read(pmcid, reader, raw, ROOT / entry['file']))
                except (ValueError, TypeError, KeyError) as exc:
                    reads.append({'span_check': {'status': 'UNVERIFIED'}, 'error': str(exc)})
            a, b = reads
            decision = combine_decisions(a, b)
            result['c2c3_evidence'] = {'A': a, 'B': b}
        result.update(c2c3_source=decision['c2c3_source'], k=decision['k_rcts'])
        result['checks']['C2/C3'] = decision
        if decision['status'] != 'PASS':
            return fail(decision['first_failure'], decision, decision['status'])
        k = decision['k_rcts']
        criterion = 'C4'
        trials = v2.load_inventory(hit, raw, k)
        result['trial_inventory'] = trials
        prior_rows = previous.get('c4_trial_resolutions', []) if previous.get('trial_inventory') == trials else []
        unfinished = []
        for trial in trials:
            saved = next((r for r in prior_rows if r['trial_id'] == trial['trial_id']
                          and r.get('lookup_complete', True)), None)
            try:
                resolution = saved or v2.resolve_trial(trial, client)
            except (v2.NeedsWork, old.FetchError) as exc:
                resolution = dict(trial_id=trial['trial_id'], pmid=trial.get('pmid'),
                                  resolved=False, lookup_complete=False, route=None, registry_ids=[],
                                  evidence={'reason': str(exc)}, attempts=getattr(exc, 'trial_attempts', []))
                unfinished.append(exc)
            result['c4_trial_resolutions'].append(resolution)
            save(result)
        resolutions = result['c4_trial_resolutions']
        result['checks']['C4'] = resolutions
        if unfinished:
            status = 'SCREEN_ERROR' if any(isinstance(e, old.FetchError) for e in unfinished) else 'NEEDS_INSPECTION'
            return fail('C4' if status == 'SCREEN_ERROR' else None,
                        {'criterion': 'C4', 'unfinished_trials': [str(e) for e in unfinished]}, status)
        if not v2.c4_passes(resolutions, k):
            return fail('C4', {'reason': 'Every included trial must resolve to exactly one distinct record', 'trials': resolutions})
        ids = [r['registry_ids'][0] for r in resolutions]
        result['registry_ids'] = ids
        criterion = 'C5'
        dates = []
        result['registry_dates'] = dates
        for rid in ids:
            record = old.fetch_registry(rid, client)
            dates.append(record)
            if old.month(record.get('start')) is not None and old.month(record['start']) < (2010, 1):
                return fail('C5', {'reason': 'Trial started before 2010-01', 'trials': [record]})
        result['checks']['C5'] = {'known_starts': [d.get('start') for d in dates]}
        criterion = 'C6'
        unreadable = [d for d in dates if old.month(d.get('start')) is None or old.month(d.get('registered')) is None]
        if unreadable:
            return fail('C6', {'reason': 'UNREADABLE registry dates', 'trials': unreadable})
        late = [d for d in dates if old.month(d['registered']) > old.month(d['start'])]
        if late:
            return fail('C6', {'reason': 'Registered after start month', 'trials': late})
        result['checks']['C6'] = dates
        criterion = 'C7'
        abstract = v2.re.sub(r'<[^>]+>', ' ', old.html.unescape(hit.get('abstractText') or '')) or ' '.join(old.text(a) for a in root.findall('.//article-meta/abstract'))
        rows = old.per_trial_rows(root, ids, k, abstract)
        if rows is None:
            return fail('C7', {'reason': 'No qualifying per-trial outcome table or forest caption naming a pooled outcome', 'outcome_terms': old.outcome_terms(abstract, root)[0]})
        result['checks']['C7'] = rows
        criterion = 'C8'
        matched = old.overlap(topics, hit.get('title', '') + ' ' + abstract)
        if matched:
            return fail('C8', matched)
        result['checks']['C8'] = {'overlap': False}
        criterion = 'C9'
        area, evidence = old.therapeutic_area(hit)
        result['area'] = area
        result['checks']['C9'] = evidence
        if areas.get(area, 0) >= 3:
            return fail('C9', {**evidence, 'area': area, 'already_qualified': areas[area], 'reason': 'EXCLUDED_AREA_CAP'})
        result.update(verdict='QUALIFIES', status='QUALIFIES', evidence={'reason': 'Passed C1..C9'})
        return result
    except v2.NeedsWork as exc:
        return fail(None, {'reason': str(exc), 'criterion': criterion}, 'NEEDS_INSPECTION')
    except Exception as exc:
        return fail(criterion, {'reason': str(exc), 'error_type': type(exc).__name__}, 'SCREEN_ERROR')


def fingerprint(hit, entry, sources, areas):
    files = [Path(__file__), Path(v2.__file__), Path(old.__file__), v2.PREREG]
    pmcid = hit['pmcid']
    files += [v2.READS / (pmcid + suffix) for suffix in
              ('.readerA.json', '.readerB.json', '.adjudication.json', '.trials.readerA.json')]
    files += [ROOT / 'cache/benchmarks/v1' / (pmcid + '.xml'),
              v2.LOGS / 'bench_v2_sources' / (pmcid + '.xml')]
    if entry and entry.get('file'):
        files.append(ROOT / entry['file'])
    hashes = {p.relative_to(ROOT).as_posix(): v2.sha(p.read_bytes()) if p.exists() else None for p in files}
    return v2.sha(json.dumps([hit, entry, sources, dict(areas), hashes], sort_keys=True))


def summarise(report):
    rows = report['screened']
    counts = Counter(r['status'] for r in rows)
    report.update(n_screened=len(rows), n_qualifies=counts['QUALIFIES'],
                  n_screen_errors=counts['SCREEN_ERROR'], status_counts=dict(counts))
    report['first_failure_counts'] = dict(Counter(r['first_failure'] for r in rows if r['status'] == 'EXCLUDED'))
    report['screen_error_counts'] = dict(Counter(r['first_failure'] for r in rows if r['status'] == 'SCREEN_ERROR'))
    report['qualifies'] = [{k: r.get(k) for k in ('pmcid', 'pmid', 'title', 'area', 'k')} for r in rows if r['status'] == 'QUALIFIES']
    report['pending_adjudication'] = [r['pmcid'] for r in rows if r['status'] == 'PENDING_ADJUDICATION']
    report['needs_inspection'] = [r['pmcid'] for r in rows if r['status'] == 'NEEDS_INSPECTION']


def run(attempts=3, pause=1.0):
    hits, topics, sources, n_hits = v2.inputs()
    entries = v2.load(INDEX)
    indexed = {e['pmcid']: e for e in entries}
    if len(indexed) != len(entries):
        raise ValueError('Duplicate INDEX PMCID')
    report = dict(prereg_commit=v2.PREREG_COMMIT, prereg_sha256=v2.sha(v2.PREREG.read_bytes()),
                  query=old.QUERY, query_sha256=old.QUERY_SHA256, seed=v2.SEED, scope=v2.SCOPE,
                  run_utc=old.utc_now(), instrument_version='2-finish', topic_sources=sources,
                  screening_script_sha256=v2.sha(Path(__file__).read_bytes()), n_hits=n_hits,
                  complete=False, independent_validation_complete=False, screened=[])
    areas, client = Counter(), v2.Client()
    summarise(report)
    def publish():
        summarise(report)
        old.write_json(v2.OUT / 'candidates_v2.json', report)
        old.write_json(v2.OUT / 'v2_finish_summary.json', {k: v for k, v in report.items() if k not in ('screened', 'topic_sources')})
    for position, hit in enumerate(hits[:800]):
        pmcid = hit['pmcid']
        if not v2.re.fullmatch(r'PMC\d+', pmcid):
            raise ValueError('Invalid frozen PMCID')
        entry = indexed.get(pmcid)
        if entry and entry.get('i') != position:
            raise ValueError('INDEX differs from frozen v1 order: ' + pmcid)
        path = FINISH / (pmcid + '.json')
        key = fingerprint(hit, entry, sources, areas)
        previous = v2.load(path) if path.exists() else {}
        if previous.get('resume_key') != key:
            previous = {}
        def save(result):
            result.update(resume_key=fingerprint(hit, entry, sources, areas), recorded_utc=old.utc_now())
            old.write_json(path, result)
        if previous.get('status') in ('QUALIFIES', 'EXCLUDED', 'NEEDS_INSPECTION'):
            result = previous
        else:
            for attempt in range(attempts):
                result = screen(hit, entry, client, topics, areas, previous, save)
                save(result)
                if result['status'] != 'SCREEN_ERROR':
                    break
                previous = result
                if attempt + 1 < attempts:
                    time.sleep(max(pause, 2 ** attempt))
            time.sleep(pause)
        report['screened'].append(result)
        if result['status'] == 'QUALIFIES':
            areas[result['area']] += 1
        publish()
        print(json.dumps({'pmcid': pmcid, 'status': result['status'], 'n_screened': report['n_screened'], 'n_qualifies': report['n_qualifies']}), flush=True)
        if report['n_qualifies'] >= 20:
            break
    report['stop_reason'] = '20 qualifiers' if report['n_qualifies'] >= 20 else '800 screened' if len(report['screened']) == 800 else 'hit list exhausted'
    report['complete'] = not any(r['status'] in ('SCREEN_ERROR', 'NEEDS_INSPECTION', 'PENDING_ADJUDICATION') for r in report['screened'])
    report['screening_finished_utc'] = old.utc_now()
    publish()
    print(json.dumps({k: v for k, v in report.items() if k not in ('screened', 'topic_sources')}, ensure_ascii=False, indent=2), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempts', type=int, default=3)
    parser.add_argument('--pause', type=float, default=1.0)
    args = parser.parse_args()
    if not 1 <= args.attempts <= 5 or args.pause < 0.35:
        parser.error('Use 1..5 attempts and pause >= 0.35 seconds')
    run(args.attempts, args.pause)


if __name__ == '__main__':
    main()
