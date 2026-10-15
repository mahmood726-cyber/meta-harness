"""Read-only A4 audit: regenerate prompts, validate records, count reply defects.

No calls, record writes, output saves, or production patches. Missing ingredients
and invalid records abort rather than becoming zero-impact observations.

Uses the caller's environment, without setting source-selection defaults. Set
ROBGRADE_LOCAL_FT and ROBGRADE_DEV_OPEN_CC only to exactly 1 (enabled), or leave
them unset (disabled), and set AACT_DIR to the source snapshot. Reproducing the
held DEV reads needs BOTH flags set to 1.
"""
import sys
sys.dont_write_bytecode = True
import base64
import hashlib
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import rob2_dual as rd


def old_parse(raw):
    """Pre-A2 parser, for read-only causal comparison (e83be9e07 parent)."""
    t = raw.decode('utf-8', 'replace').strip()
    m = re.fullmatch(r'```(?:json)?\s*(.*?)\s*```', t, re.S)
    t = m.group(1) if m else t
    try:
        d = json.loads(t)
    except ValueError:
        return None
    return d if isinstance(d, dict) and isinstance(d.get('answers'), list) else None


def shown(prompt):
    return json.loads(prompt.decode('utf-8').split('\nTHE TWO READINGS:\n', 1)[1]
                      .split('\n=== EVIDENCE ===\n', 1)[0])


def pair(readings):
    return '/'.join(readings[r]['answer'] for r in ('reader 1', 'reader 2'))


def conflicts(parsed):
    seen = defaultdict(set)
    for row in parsed.get('answers') or []:
        if row.get('qid') in rd.QIDS:
            seen[row['qid']].add(row.get('answer'))
    return any(len(values) > 1 for values in seen.values())


def measure(name, manifest_name):
    directory = ROOT / 'evidence/model_calls' / name
    runs = json.loads((ROOT / 'registry/model_proposals' / manifest_name).read_text(encoding='utf-8'))
    records = {}
    parsed = {}
    for path in sorted(directory.glob('*.json')):
        rec = rd.ms.load_record(path)
        problems = rd.ms.record_problems(rec)
        if problems:
            raise ValueError(f'{path.name}: {problems}')
        if path.stem != rec['record_id']:
            raise ValueError(f'{path.name}: record ID mismatch')
        records[path.stem] = rec
        if rec['state'] == 'RAN_OK':
            parsed[path.stem] = rd.parse(rd.ms.replay(rec))
    grouped = defaultdict(set)
    for key in runs:
        slug, pmid, _ = key.split('::', 2)
        grouped[slug].add(pmid)
    rd.prefetch_registry([(slug, sorted(pmids)) for slug, pmids in sorted(grouped.items())])
    items = {item['key']: item for slug, pmids in sorted(grouped.items()) for item in rd.items(slug, sorted(pmids))}
    total = sum(len(roles) for roles in runs.values())
    counts = defaultdict(int)
    mismatches = []
    original_prompt = rd.prompt_bytes
    for key, roles in sorted(runs.items()):
        item = items[key]  # fail closed if the current outcome/key changed
        prompts = {}
        consumed = []
        original_replay = rd.ms.replay
        def replay_record(rec):
            consumed.append(rec['record_id'])
            return original_replay(rec)
        def capture(item, kind='reader', disagreements=None):
            p = original_prompt(item, kind, disagreements)
            prompts[kind] = p
            return p
        with patch.object(rd, 'REC_DIR', str(directory)), patch.object(rd, 'prompt_bytes', capture), patch.object(rd.ms, 'replay', replay_record):
            rd.process(item, runs, False, {})
        for who, run in sorted(roles.items()):
            if who not in ('codex', 'agy', 'adjudicator'):
                raise ValueError(f'unknown manifest role {who}')
            rec = records[run['record_id']]
            held = base64.b64decode(rec['prompt']['b64'], validate=True)
            counts['manifest_vs_held'] += run['prompt_sha256'] != hashlib.sha256(held).hexdigest()
            kind = 'adjudicator' if who == 'adjudicator' else 'reader'
            if kind not in prompts:
                counts['not_consumed'] += 1
                print(f'{name}: no current {kind} prompt (not consumed): {key} / {who}')
                continue
            current = prompts[kind]
            counts['regenerated'] += 1
            counts['manifest_vs_current'] += run['prompt_sha256'] != hashlib.sha256(current).hexdigest()
            counts['held_vs_current'] += held != current
            counts[f'{kind}_compared'] += 1
            counts[f'{kind}_mismatched'] += held != current
            if held != current or run['prompt_sha256'] != hashlib.sha256(current).hexdigest():
                detail = [f'{key} | {who} | {rec["record_id"]}']
                detail.append(f'  response read by frozen replay: {rec["record_id"] in consumed}')
                if kind == 'adjudicator':
                    before, after = shown(held), shown(current)
                    typed, _ = rd.rt.typed_answers(item['sources'], item.get('machine_d5'), outcome=item.get('outcome'))
                    detail.append('  evidence bytes unchanged: ' + str(held.split(b'\n=== EVIDENCE ===\n', 1)[1] == current.split(b'\n=== EVIDENCE ===\n', 1)[1]))
                    verified = [rd.verify_answers(parsed.get(roles[r]['record_id']), item)
                                for r in ('codex', 'agy')]
                    detail.append('  held questions: ' + ', '.join(sorted(before)))
                    detail.append('  current questions: ' + ', '.join(sorted(after)))
                    for q in sorted(set(before) | set(after)):
                        now = {f'reader {i + 1}': v.get(q, {'answer': 'NI'})
                               for i, v in enumerate(verified)}
                        if before.get(q) != after.get(q):
                            changed = sorted({k for r in now for k in set((before.get(q) or {}).get(r, {})) | set(now[r])
                                              if (before.get(q) or {}).get(r, {}).get(k) != now[r].get(k)})
                            detail.append(f'  {q}: held {pair(before[q]) if q in before else "not shown"}; '
                                          f'current verified {pair(now)}; current shown {q in after}; '
                                          f'changed fields {",".join(changed) or "none"}')
                            if q in typed:
                                detail.append(f'    typed precedence: {typed[q]["answer"]} ({typed[q].get("rule_id")})')
                    with patch.object(rd, 'REC_DIR', str(directory)), patch.object(rd, 'parse', old_parse), patch.object(rd, 'prompt_bytes', capture):
                        prompts.pop('adjudicator', None)
                        rd.process(item, runs, False, {})
                    detail.append(f'  pre-A2 parser reproduces held prompt: {prompts.get("adjudicator") == held}')
                    for r in ('codex', 'agy'):
                        raw = rd.ms.replay(records[roles[r]['record_id']])
                        detail.append(f'  {r} reply parseable pre-A2/current: {old_parse(raw) is not None}/{rd.parse(raw) is not None}')
                mismatches.append('\n'.join(detail))
    readable = {rid: obj for rid, obj in parsed.items() if obj is not None}
    unreadable = sorted(set(parsed) - set(readable))
    print(f'[{name}]')
    print(f'manifest entries with regenerated current prompts: {counts["regenerated"]}/{total}')
    print(f'manifest entries not consumed (no current prompt): {counts["not_consumed"]}/{total}')
    print(f'manifest/current prompt hash mismatches: {counts["manifest_vs_current"]}/{counts["regenerated"]}')
    print(f'held/current prompt byte mismatches: {counts["held_vs_current"]}/{counts["regenerated"]}')
    print(f'manifest/held prompt hash mismatches: {counts["manifest_vs_held"]}/{total}')
    for kind in ('reader', 'adjudicator'):
        print(f'{kind} held/current prompt byte mismatches: {counts[f"{kind}_mismatched"]}/{counts[f"{kind}_compared"]}')
    print(f'successful held records: {len(parsed)}/{len(records)}')
    print(f'unparseable successful replies: {len(unreadable)}/{len(parsed)}')
    print('unparseable record IDs: ' + (', '.join(unreadable) or 'none'))
    print(f'parseable successful replies: {len(readable)}/{len(parsed)}')
    print(f'replies with conflicting duplicate rows: {sum(conflicts(x) for x in readable.values())}/{len(readable)} parseable successful replies')
    print('mismatching entries (key | role | record id):')
    print('\n'.join(mismatches) or 'none')


if __name__ == '__main__':
    for flag in ('ROBGRADE_LOCAL_FT', 'ROBGRADE_DEV_OPEN_CC'):
        value = os.environ.get(flag)
        if value not in (None, '1'):
            raise SystemExit(
                f'{flag}={value!r} is invalid: leave unset (disabled) or set exactly "1" '
                '(enabled); the frozen driver enables any non-empty value, including "0"'
            )
    if not os.environ.get('AACT_DIR') or not Path(os.environ['AACT_DIR']).is_dir():
        raise SystemExit('AACT_DIR must explicitly name an existing source snapshot directory')
    print('environment: ' + ' '.join(
        f'{flag}={os.environ.get(flag, "UNSET")} '
        f'(effective: {"enabled" if bool(os.environ.get(flag)) else "disabled"})'
        for flag in ('ROBGRADE_LOCAL_FT', 'ROBGRADE_DEV_OPEN_CC')
    ) + f' AACT_DIR={os.environ["AACT_DIR"]}')
    measure('rob2', 'rob2_dual_runs.json')
    measure('rob2_served', 'rob2_served_runs.json')
