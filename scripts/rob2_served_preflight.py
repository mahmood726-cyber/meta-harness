"""NON-MODEL preflight. All driver operations are reads or in-memory transforms.

Static: paths, planned command, expected-count comparisons (never output inputs).
Dynamic: review membership, coverage, prompt bytes, records, licences and checks.
Never invoke driver main/process/adopt_stage: even replay writes stores.

RESIDUAL: this preflight re-derives the driver's decisions. Parity is tested
for current held-success reuse and orphan adoption; stale successful and failed
readers; unreadable successful-reader quarantine and skipped adjudication;
RAN_OK entries missing record_id (absent/null, with a current prompt hash) or
both record_id and prompt_sha256; adjudicator agreement, disagreement, conflict,
unknown readers, reuse, stale records and missing records; blocked source gates;
manifest, accounting, duplicate-row and licence refusals; and CLI flag rejection.
Parity is not proven for other cases. The recommended structural fix is a
driver-level dry run: the driver's own code path with the model-call boundary
stubbed to record WOULD_CALL.
"""
import argparse
import base64
import collections
import contextlib
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
ROLES = ('codex', 'agy', 'adjudicator')
STATES = ('REUSE', 'STALE', 'CALL', 'UNKNOWN', 'NOT_NEEDED', 'BLOCKED', 'UNVERIFIED', 'CONFLICT',
          'QUARANTINE', 'SKIPPED (trial quarantined)', 'WOULD_REFUSE')
_active_guards = 0


def safety(event, args):
    """While reading, reject every filesystem mutation and process/network call."""
    if not _active_guards:
        return
    mutation = event in (
        'os.remove', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.utime',
        'os.truncate', 'os.rename', 'os.link', 'os.symlink',
    )
    if event == 'open':
        _, mode, flags = args
        mutation = bool((mode and any(c in mode for c in 'wax+')) or
                        (flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
    if mutation:
        raise PermissionError('preflight forbids writes during source inspection')
    if event in ('subprocess.Popen', 'os.system', 'os.posix_spawn',
                 'os.exec', 'os.fork', 'socket.connect', 'socket.bind', 'socket.getaddrinfo'):
        raise PermissionError('preflight forbids subprocess/network/model execution')


sys.addaudithook(safety)


@contextlib.contextmanager
def never_writes():
    """Scope the audit guard so importing this module does not restrict pytest."""
    global _active_guards
    old_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    _active_guards += 1
    try:
        yield
    finally:
        _active_guards -= 1
        sys.dont_write_bytecode = old_bytecode


def read_json(path):
    p = Path(path)
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}


def load_driver():
    # Match the sibling scripts' import convention; configuration comes from the caller.
    with never_writes():
        import rob2_served as sv
    return sv


def collect_items(sv):
    pairs = sv.served_pairs()
    todo, covered = sv.work_list()
    print('Reading pinned AACT tables and current source sets (no network)...', file=sys.stderr, flush=True)
    sv.rd.prefetch_registry(sorted(pairs.items()))
    items = [it for slug, pm in sorted(pairs.items()) if pm for it in sv.rd.items(slug, pm)]
    return pairs, todo, covered, items


def outside_driver(sv):
    nct, secondary = [], []
    for slug in sorted(sv.served_pairs()):
        path = Path(sv.REVIEWS) / slug / 'review.json'
        doc = read_json(path)
        outcomes = doc['outcomes']
        primary = next((o for o in outcomes if o.get('primary')), outcomes[0])
        primary_ids = {str(t.get('id')) for t in primary.get('trials') or []}
        all_ids = {str(t.get('id')) for o in outcomes for t in o.get('trials') or []}
        for tid in sorted(all_ids):
            row = {'slug': slug, 'trial_id': tid, 'source': str(path), 'primary': tid in primary_ids}
            if re.search(r'NCT\d+', tid) and not re.search(r'PMID (\d+)', tid):
                nct.append(row)
            if tid not in primary_ids:
                secondary.append(row)
    return {'nct_only': nct, 'non_primary_only': secondary}


@contextlib.contextmanager
def stores_context(sv, stores, validate_record=None):
    old = sv.STORES
    original_read = sv._read_record
    records = {}
    def snapshot_read(path, read=lambda record: record):
        # Validate each held file once per preflight, never across invocations.
        if path not in records:
            records[path] = original_read(path)
            if validate_record is not None:
                validate_record(records[path])
        try:
            return read(records[path])
        except Exception as exc:
            raise SystemExit(f'REFUSED: unreadable record {path}: {exc}') from exc
    sv.STORES = dict(stores)
    sv._read_record = snapshot_read
    try:
        with sv.redirected():
            yield
    finally:
        sv.STORES = old
        sv._read_record = original_read


def classify(sv, entry, want, rec_dir, role):
    entry = entry or {}
    rid = entry.get('record_id')
    if entry.get('state') == 'RAN_OK' and any(
            not isinstance(entry.get(field), str) or not entry[field].strip()
            for field in ('record_id', 'prompt_sha256')):
        return {'state': 'WOULD_REFUSE', 'record_id': rid, 'held_state': None,
                'reason': 'malformed RAN_OK manifest entry (missing record_id/prompt_sha256)'}
    state = sv._record_state(rec_dir, rid)
    result = {'state': 'CALL', 'record_id': rid, 'held_state': state}
    if state is None:
        result['reason'] = 'no held record'
        # process skips a current successful manifest entry even without an ID;
        # replay then fails before the driver's quarantine check can run.
        if want is not None and entry.get('state') == 'RAN_OK' and entry.get('prompt_sha256') == want:
            result.update(state='WOULD_REFUSE', reason='RAN_OK manifest entry without a held record')
    elif want is None:
        result.update(state='UNKNOWN', reason='current adjudication depends on fresh readers')
    elif sv._record_prompt_sha256(rec_dir, rid) != want or entry.get('prompt_sha256') != want:
        result.update(state='STALE', reason='held record or manifest differs from current prompt')
    elif state == 'RAN_OK' and entry.get('state') == 'RAN_OK' and sv._record_role(rec_dir, rid) == role:
        result.update(state='REUSE', reason='held RAN_OK record for role and current prompt')
        if role in ('codex', 'agy'):
            problem = sv._reply_problem(entry, role)
            if problem:
                result.update(state='QUARANTINE', reason=problem)
    else:
        result['reason'] = 'held failed attempt or invalid manifest binding; no reusable success'
    return result


def source_configuration():
    snapshot = os.environ.get('AACT_DIR')
    ft = os.environ.get('ROBGRADE_FT_STORE')
    return {'aact_snapshot': Path(snapshot).name if snapshot else None,
            'ft_store_root': str(Path(ft).resolve()) if ft else 'unset (ROBGRADE_FT_STORE not set)'}


class Refused(Exception):
    def __init__(self, checks):
        self.checks = checks
        super().__init__(checks[-1]['detail'])


def refused_report(exc, keys=None):
    reason = str(exc)
    rows = [{'key': key, **{role: {'state': 'UNVERIFIED', 'reason': reason}
                              for role in ROLES}} for key in sorted(keys or ())]
    return {'status': 'REFUSED', 'reason': reason,
            'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'rows': rows, 'totals': {role: {state: len(rows) if state == 'UNVERIFIED' else 0
                                          for state in STATES} for role in ROLES} if keys is not None else None,
            'totals_note': 'not computed' if keys is None else 'all slots unverified',
            'preconditions': getattr(exc, 'checks', [{'check': 'source inspection', 'status': 'REFUSED', 'detail': reason}]),
            'adjudicator_max_trials': None,
            'live_command': 'python scripts/rob2_served.py --run',
            'environment_guidance': 'REFUSED: resolve the reported failure and repeat preflight.',
            **source_configuration()}


def analyze(sv, pairs, todo, covered, items, stores=None):
    keys = None
    try:
        keys = sv.served_keys(todo)
        return _analyze(sv, pairs, todo, covered, items, stores)
    except (Exception, SystemExit) as exc:
        return refused_report(exc, keys)


def cli_check(sv):
    planned = ('--run',)
    # This is the driver's own accepted-options contract, used by its main().
    bad = tuple(flag for flag in planned if flag not in sv.FLAGS)
    if bad:
        raise ValueError(f'driver rejects planned flags: {bad}; accepted: {sv.FLAGS}')
    return {'flags': planned, 'accepted': sv.FLAGS}


def audit_check(sv, directory):
    findings = sv.audit(directory)
    if findings:
        raise ValueError(f'duplicate-row audit refused {directory}: {findings}')
    return findings


def adjudicator_state(sv, it, held, row):
    if (any(row[w]['state'] == 'QUARANTINE' for w in ('codex', 'agy'))
            and not any(row[w]['state'] == 'WOULD_REFUSE' for w in ('codex', 'agy'))):
        return {'state': 'SKIPPED (trial quarantined)', 'reason': 'reader check quarantines trial before adjudication'}
    if not all(row[w]['state'] == 'REUSE' for w in ('codex', 'agy')):
        return {'state': 'UNKNOWN', 'reason': 'needed-ness depends on readers still to be called'}
    a, b = (sv.rd.verify_answers(sv.rd.replay(held[w]), it) for w in ('codex', 'agy'))
    dis = sv.rd.agree(a, b)[1]
    typed, _ = sv.rt.typed_answers(it['sources'], it.get('machine_d5'), outcome=it['outcome'])
    dis = {q: {'reader 1': a, 'reader 2': b} for q, (a, b) in dis.items() if q not in typed}
    if not dis:
        adj = held.get('adjudicator')
        if adj and adj.get('state') != 'DEFERRED':
            return {'state': 'CONFLICT',
                    'reason': 'an adjudication is recorded but the fresh readers agree'}
        return {'state': 'NOT_NEEDED', 'reason': 'readers agree after driver typed answers'}
    want = sv._sha(sv.rd.prompt_bytes(it, 'adjudicator', dis))
    return classify(sv, held.get('adjudicator'), want, sv.rd.REC_DIR, 'adjudicator')


def _analyze(sv, pairs, todo, covered, items, stores=None):
    from reproducible_ai import record_licence
    from harness import aact
    licences = record_licence.licences()
    stores = stores or sv.STORES
    checks, rows, d8_all = [], [], []
    would_refuse, quarantined_trials = [], []
    will_recall = {role: 0 for role in ROLES}
    def check(name, fn):
        try:
            value = fn()
            checks.append({'check': name, 'status': 'PASS', 'detail': value})
            return value
        except (Exception, SystemExit) as exc:
            checks.append({'check': name, 'status': 'REFUSED', 'detail': str(exc)})
            raise Refused(checks) from exc
    todo_keys = sv.served_keys(todo)
    selected = [it for it in items if it['key'] in todo_keys]
    def environment_check():
        for name in ('ROBGRADE_LOCAL_FT', 'ROBGRADE_DEV_OPEN_CC'):
            if os.environ.get(name) != '1':
                raise ValueError(f'{name} must be 1 for this recorded-run configuration')
        if not Path(os.environ['AACT_DIR']).is_dir():
            raise ValueError('AACT_DIR is absent; fallback would change prompts')
        tables = {t: aact._table(t) for t in ('study_references', 'designs', 'brief_summaries', 'detailed_descriptions')}
        if not all(tables.values()):
            raise ValueError(f'missing AACT tables: {tables}')
        return tables
    check('source environment (additional preflight guard)', environment_check)
    check('CLI flags', lambda: cli_check(sv))
    def validate_record(record):
        problems = record_licence.record_problems(record, lic=licences)
        if problems:
            raise ValueError('D8 licence violation: ' + '; '.join(problems))
    with stores_context(sv, stores, validate_record):
        runs = read_json(sv.rd.RUNS)
        adopted = check('orphan adoption (in memory; no save)', lambda: sv.adopt_orphans(selected, runs, sv.rd.REC_DIR))
        check('dual manifest validation', lambda: sv.check_manifest_records(runs, sv.rd.REC_DIR))
        check('dual accounting', lambda: sv.check_accounted(runs, sv.rd.REC_DIR, keys=sv.served_keys(pairs)))
        ctx = read_json(sv.rc.RUNS)
        check('contextual manifest validation (before contextual stage)', lambda: sv.check_manifest_records(ctx, sv.rc.REC_DIR, contextual=True))
        check('contextual consumed accounting (before contextual stage)', lambda: sv.check_accounted(ctx, sv.rc.REC_DIR, consumed=True, keys=sv.served_keys(pairs)))
        for name, directory in [('dual', sv.rd.REC_DIR), ('contextual', sv.rc.REC_DIR)]:
            check(name + ' duplicate-row audit (driver reports after stages)', lambda d=directory: audit_check(sv, d))
        for it in items:
            problems = []
            prompt = None
            open_sources = sv.rd.open_sources(it)
            try:
                ev = sv.rd.evidence_block(it)
            except sv.rd.D8Refused as exc:
                # Only the source gate's documented refusal is a blocked trial.
                # Licence validation and all other failures refuse the preflight.
                gate, problems = 'blocked', [str(exc)]
            else:
                gate = ('blocked' if not open_sources else
                        'CC full text' if any(s['kind'] == 'fulltext' for s in ev) else 'abstract only')
                if gate != 'blocked':
                    prompt = sv.rd.prompt_bytes(it)
                    check('D8 prompt licence ' + it['key'], lambda: validate_record({
                        'record_id': 'pre-call', 'input_digests': sv.rd.digests(it),
                        'prompt': {'b64': base64.b64encode(prompt).decode('ascii')}}))
            d8 = {'key': it['key'], 'gate': gate, 'problems': problems,
                  'open_source_kinds': sorted({s['kind'] for s in open_sources}),
                  'todo': it['key'] in todo_keys}
            d8_all.append(d8)
            if it['key'] not in todo_keys:
                continue
            row = {'key': it['key'], 'd8': gate, 'prompt_sha256': sv._sha(prompt) if prompt else None}
            if gate == 'blocked':
                row.update({role: {'state': 'BLOCKED', 'reason': 'source gate blocked reading'} for role in ROLES})
                rows.append(row)
                continue
            held = runs.get(it['key']) or {}
            for role in ('codex', 'agy'):
                row[role] = classify(sv, held.get(role), row['prompt_sha256'], sv.rd.REC_DIR, role)
            row['adjudicator'] = adjudicator_state(sv, it, held, row)
            if row['adjudicator']['state'] == 'SKIPPED (trial quarantined)':
                reason = next(row[w]['reason'] for w in ('codex', 'agy') if row[w]['state'] == 'QUARANTINE')
                row['state'] = 'QUARANTINE'
                quarantined_trials.append({'key': it['key'], 'reason': reason})
            for role in ROLES:
                slot = row[role]
                if slot['state'] == 'STALE':
                    will_recall[role] += 1
                    slot['live_action'] = 're-call'
                    if slot['held_state'] == 'RAN_OK':
                        reason = ('live process re-calls this stale successful slot; its old RAN_OK record '
                                  'becomes unaccounted and the post-stage accounting check refuses')
                        slot['live_result'] = 'WOULD_REFUSE'
                        would_refuse.append({'key': it['key'], 'role': role, 'reason': reason})
                elif slot['state'] in ('CONFLICT', 'WOULD_REFUSE'):
                    would_refuse.append({'key': it['key'], 'role': role, 'reason': slot['reason']})
            def reader_now():
                try:
                    return sv.reader_verdict(it, held, sv.rd.REC_DIR)
                except SystemExit as exc:
                    # A current-prompt mismatch is expected before live process re-calls.
                    # All held-record/manifest/licence integrity checks ran above.
                    if (str(exc).endswith('does not answer the current prompt (stale)')
                            and any(row[w]['state'] == 'STALE' for w in ('codex', 'agy'))):
                        return str(exc)
                    raise
            row['reader_verdict_now'] = check('reader verdict ' + it['key'], reader_now)
            rows.append(row)
    totals = {role: {state: sum(r[role]['state'] == state for r in rows) for state in STATES}
              for role in sv.ROLES}
    outside = outside_driver(sv)
    counts = {'topics': len(pairs), 'primary_pmid_pairs': sum(map(len, pairs.values())),
              'covered': sum(map(len, covered.values())), 'todo': len(rows), 'todo_topics': len(todo),
              'nct_only_outside_driver': len(outside['nct_only']), 'non_primary_only_outside_driver': len(outside['non_primary_only'])}
    expected = {'topics': 32, 'primary_pmid_pairs': 91, 'todo': 65, 'nct_only_outside_driver': 5, 'non_primary_only_outside_driver': 11}
    checks.append({'check': 'expected scope comparisons (not computation inputs)',
                   'status': 'PASS' if all(counts[k] == v for k, v in expected.items()) else 'MISMATCH', 'detail': expected})
    if checks[-1]['status'] != 'PASS':
        raise Refused(checks)
    env = {k: os.environ.get(k) for k in ('PYTHONDONTWRITEBYTECODE', 'TMPDIR', 'TMP', 'TEMP', 'MODEL_CALL_WORKDIR', 'AACT_DIR', 'ROBGRADE_LOCAL_FT', 'ROBGRADE_DEV_OPEN_CC', 'ROBGRADE_FT_STORE')}
    return {'status': 'WOULD_REFUSE' if would_refuse else 'PASS',
            'would_refuse': would_refuse, 'will_recall': will_recall,
            'quarantined_trials': quarantined_trials,
            'warnings': ([f"STALE records with AACT snapshot {source_configuration()['aact_snapshot']}; "
                          'a different AACT snapshot than the records were made with changes prompts.']
                         if any(t['STALE'] for t in totals.values()) else []), **source_configuration(), 'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'driver': str(ROOT / 'scripts/rob2_served.py'),
            'driver_sha256': hashlib.sha256((ROOT / 'scripts/rob2_served.py').read_bytes()).hexdigest(),
            'counts': counts, 'pairs': pairs, 'todo': todo, 'covered': covered, 'outside_driver': outside,
            'totals': totals, 'adjudicator_max_trials': len(rows), 'rows': rows, 'd8_per_trial': d8_all,
            'd8_todo_split': dict(collections.Counter(r['d8'] for r in rows)),
            'd8_all_primary_split': dict(collections.Counter(r['gate'] for r in d8_all)),
            'd8_note': 'abstract only means no prompt-open full text; permitted registry sources may also be present',
            'preconditions': checks, 'adopted_in_memory': adopted,
            'live_command': 'python scripts/rob2_served.py --run',
            'environment': env, 'environment_guidance': (
                'Run from the repo root. Supply AACT_DIR and ROBGRADE_FT_STORE from the pinned source configuration; '
                'ROBGRADE_LOCAL_FT and ROBGRADE_DEV_OPEN_CC from the held reader configuration; '
                'MODEL_CALL_WORKDIR, TMPDIR, TMP and TEMP from the operator temporary workspace; '
                'set PYTHONDONTWRITEBYTECODE=1. No machine paths are embedded in the command.'), 'cli_on_path': {n: shutil.which(n) for n in ('codex', 'agy')},
            'limitations': ['No model availability/quota/authentication probe performed.',
                'Post-stage checks cannot be predicted before model results exist.',
                'Contextual calls are additional to the dual-reader/adjudicator counts.',
                'Live process re-calls stale readers; replacing held successes causes post-stage accounting refusal.',
                'Repeat immediately before the live run; worktree and stores can change.'],
            'hardcode_disclosure': {'static': ['repo-relative layout', 'expected-count comparisons'],
                                   'dynamic': ['all counts', 'trial keys', 'prompt hashes', 'record states', 'licence gates', 'preconditions']}}


def output_path(value):
    """Reject repository/source destinations, including symlink aliases."""
    out = Path(value).resolve()
    protected = [ROOT]
    for name in ('AACT_DIR', 'ROBGRADE_FT_STORE'):
        if os.environ.get(name):
            protected.append(Path(os.environ[name]).resolve())
    if any(out.is_relative_to(p) for p in protected):
        raise ValueError('--out must be outside the repository and source stores')
    if any((parent / '.git').exists() for parent in out.parents):
        raise ValueError('--out must be outside every git work tree')
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path,
                        default=Path(tempfile.gettempdir()) / 'served_preflight' / 'preflight.json',
                        help='Report file outside the repository (default: system temp/served_preflight/preflight.json)')
    args = parser.parse_args(argv)
    out = output_path(args.out)
    try:
        with never_writes():
            sv = load_driver()
            report = analyze(sv, *collect_items(sv))
    except (Exception, SystemExit) as exc:
        report = refused_report(exc)
    content = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=out.parent, prefix='.preflight-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, out)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    if any(t.get('STALE', 0) for t in (report['totals'] or {}).values()):
        print(f"WARNING: STALE records with AACT snapshot {report.get('aact_snapshot')}; "
              'a different AACT snapshot than the records were made with changes prompts.', file=sys.stderr)
    print('Status:', report.get('status', 'PASS'))
    print('Totals: not computed' if report['totals'] is None else json.dumps(report['totals'], sort_keys=True))
    print('Will re-call:', report.get('will_recall'))
    for refusal in report.get('would_refuse', ()):
        print('WOULD_REFUSE:', refusal['key'], refusal['role'], refusal['reason'])
    print('Adjudicator maximum:', report['adjudicator_max_trials'])
    print('Live command:', report['live_command'])
    print(report['environment_guidance'])
    print('Report:', out)
    return int(report.get('status') == 'WOULD_REFUSE' or any(c['status'] in ('REFUSED', 'MISMATCH') for c in report['preconditions']))


if __name__ == '__main__':
    raise SystemExit(main())
