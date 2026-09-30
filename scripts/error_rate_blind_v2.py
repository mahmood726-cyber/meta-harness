"""Offline, value-blind incremental census. Run --write to append audited rows.

Only row identity, requested endpoint/type and source locator cross the checker
boundary. No review result text, stored numbers, or verification flags do.
The read-only default is the lane census (this lane permits this script name).
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = 'BLIND_V2_2026-09-29'
FIELDS = ('effect', 'ci_low', 'ci_high', 'ai', 'n1i', 'ci', 'n2i',
          'mean1', 'sd1', 'nc1', 'mean2', 'sd2', 'nc2')
INPUT_KEYS = {'row_id', 'endpoint', 'rowtype', 'document_ref', 'record_id', 'kind'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def classify(topic, trial):
    if any(topic.get(k) is True or trial.get(k) is True
           for k in ('is_control', 'is_fixture', 'synthetic', 'control', 'fixture')):
        return 'control'
    if str(topic.get('kind', '')).lower() in ('control', 'fixture'):
        return 'control'
    return 'real pooled number'


def population(root=ROOT):
    """Same path-derived slug and numeric predicate as _pooled_population()."""
    rows = {}
    topics = {p.stem: read(p) for p in sorted((root / 'topics').glob('*.json'))}
    for path in sorted((root / 'docs/reviews').glob('*/review.json')):
        review = read(path)
        for outcome in review.get('outcomes', []):
            for trial in outcome.get('trials', []):
                if any(trial.get(k) is not None for k in ('effect', 'mean1', 'ai')):
                    rid = f"{path.parent.name}::{outcome['name']}::{trial.get('label')}"
                    if rid in rows:
                        raise ValueError(f'refused duplicate population identity: {rid}')
                    rows[rid] = (outcome, trial, classify(topics.get(path.parent.name, {}), trial))
    return rows, topics


def checker_input(rid, outcome, trial, kind):
    # Explicit whitelist: never pass source_span, source, stored, effect_object,
    # study_effect, handed_abstract, or any numeric extraction from the review.
    return dict(row_id=rid, endpoint=outcome['name'], kind=kind,
                rowtype='effect' if trial.get('effect') is not None else
                'count2x2' if trial.get('ai') is not None else 'continuous',
                document_ref=trial.get('document_ref') or
                f"cache/{rid.split('::')[0]}/records.json",
                record_id=str(trial.get('id', trial.get('label', ''))))


def norm(text):
    return re.sub(r'\s+', ' ', text).strip()


def endpoint_matches(endpoint, label):
    """Explicit lexical endpoint aliases, never numeric or row-ID selectors."""
    e, s = endpoint.lower(), label.lower().strip(' †‡*‖')
    if e == 'hyperkalemia':
        return s == 'hyperkalemia' or s.startswith('elevated serum potassium') or s == 'number of patients with incidences of hyperkalemia'
    if 'hyperkalemia' in e and 'discontinuation' in e:
        return 'hyperkalemia' in s and 'discontinuation' in s
    if 'gastrointestinal' in e:
        gi = 'gastrointestinal' in s or s.startswith('gi disorders')
        return gi and ('serious' in e) == ('serious' in s) and ('discontinuation' in e) == ('discontinuation' in s)
    if e == 'serious adverse events':
        return s == e or s.startswith('serious adverse events, participants affected')
    if e == 'serious infection':
        return s == 'serious adverse events of infection'
    if 'discontinuation' in e:
        return ('adverse event' in s or ' ae ' in s) and ('discontinuation' in s or 'discontinued' in s)
    if e == 'hospitalization for heart failure':
        return bool(re.search(r'hospitalization for heart failure|hhf outcome', s))
    if e == '3-point major adverse cardiovascular events':
        return all(x in s for x in ('cardiovascular death', 'nonfatal myocardial infarction', 'nonfatal stroke')) and 'unstable angina' not in s
    if 'muscle symptoms' in e:
        return s == 'muscle weakness, stiffness or pain'
    if e == 'new-onset diabetes':
        return s == 'newly diagnosed diabetes'
    if 'amputation' in e:
        return s.startswith('amputation')
    if e == 'diabetic ketoacidosis':
        return 'diabetic ketoacidosis' in s
    if e == 'hypotension':
        return 'hypotension' in s
    if 'all-cause mortality' in e:
        return s.startswith('all-cause mortality')
    if e == 'injection-site reactions':
        return 'injection-site reaction' in s
    return s == e


def refuse(reason):
    return {'verdict': 'NOT_RECHECKABLE', 'reason': reason}


def number(s):
    return int(s.replace(',', ''))


def count_result(a, n, b, m, spans):
    values = dict(ai=a, n1i=n, ci=b, n2i=m)
    if n <= 0 or m <= 0 or not (0 <= a <= n and 0 <= b <= m):
        return refuse('refused invalid participant counts/denominators')
    return dict(values=values, printed={k: str(v) for k, v in values.items()}, spans=spans)


def tables(text, endpoint, rowtype):
    header = None
    candidates = []
    for line in text.splitlines():
        if '|' not in line or line.startswith('#'):
            continue
        cells = [c.strip() for c in line.split('|')]
        if any(re.search(r'\b[nN]\s*=\s*[\d,]+', c) for c in cells):
            # Multi-level headers (CoDEX) omit the leading outcome-label cell.
            header = ['Outcome'] + cells if re.search(r'\b[nN]\s*=', cells[0]) else cells
        if not endpoint_matches(endpoint, cells[0]):
            continue
        if re.search(r'\b28.day\b', endpoint, re.I) and not re.search(r'28.Day results', text, re.I):
            continue
        if rowtype == 'effect':
            for c in cells[1:]:
                m = re.fullmatch(r'(\d+\.\d+)\s*\((\d+\.\d+)\s*[–−,-]\s*(\d+\.\d+)\)', c)
                if m:
                    candidates.append(effect_result(m.groups(), [line]))
            continue
        if header:
            arms = [(i, h, re.search(r'\b[nN]\s*=\s*([\d,]+)', h)) for i, h in enumerate(header)]
            arms = [(i, h, m) for i, h, m in arms if m]
            controls = [a for a in arms if re.search(r'placebo|enalapril|standard care', a[1], re.I)]
            active = [a for a in arms if a not in controls]
            # STEP 8 explicitly specifies semaglutide vs pooled placebo in held bytes.
            if len(active) > 1 and re.search(r'comparison: semaglutide vs POOLED placebo', text, re.I):
                active = [a for a in active if 'semaglutide' in a[1].lower()]
            if len(controls) == len(active) == 1:
                ai, _, an = active[0]; bi, _, bn = controls[0]
                a = re.match(r'([\d,]+)(?:/([\d,]+))?', cells[ai])
                b = re.match(r'([\d,]+)(?:/([\d,]+))?', cells[bi])
                if a and b:
                    candidates.append(count_result(number(a[1]), number(an[1]), number(b[1]), number(bn[1]), [' | '.join(header), line]))
        else:
            # Fractions with explicit active/control column labels (CREDENCE).
            fractions = [re.fullmatch(r'(\d+)/(\d+)(?:\s*\([^)]*\))?', c) for c in cells[1:3]]
            if all(fractions) and re.search(r'Outcome \| [^|]+no\./total no\. \| Placebo no\./total no\.', text):
                a, b = fractions
                candidates.append(count_result(int(a[1]), int(a[2]), int(b[1]), int(b[2]), [line]))
    return unique(candidates, endpoint)


def unique(candidates, endpoint):
    if len(candidates) != 1:
        return refuse(f'refused {len(candidates)} candidate results for {endpoint}; need one endpoint-bound result and arm denominators in cited source')
    return candidates[0]


def effect_result(tokens, spans):
    keys = ('effect', 'ci_low', 'ci_high')
    values = dict(zip(keys, map(float, tokens)))
    if not 0 < values['ci_low'] <= values['effect'] <= values['ci_high']:
        return refuse('refused invalid ratio confidence interval')
    return dict(values=values, printed=dict(zip(keys, tokens)), spans=spans)


def registry(data, record_id, endpoint):
    key = record_id.replace('NCT ', 'NCT')
    measures = data.get('ctgov_results', {}).get(key, [])
    candidates = []
    for measure in measures:
        if not endpoint_matches(endpoint, measure.get('title', '')):
            continue
        if measure.get('paramType') != 'NUMBER' or measure.get('unitOfMeasure', '').lower() != 'participants':
            return refuse('refused registry result not typed NUMBER/participants')
        groups = measure.get('groups', [])
        active = [g['id'] for g in groups if 'sacubitril' in g['title'].lower()]
        control = [g['id'] for g in groups if g['title'].lower() == 'enalapril']
        denoms = [d for d in measure.get('denoms', []) if d.get('units', '').lower() == 'participants']
        vals = [m for c in measure.get('classes', []) for cat in c.get('categories', []) for m in cat.get('measurements', [])]
        if len(active) != 1 or len(control) != 1 or len(denoms) != 1 or len(vals) != 2:
            return refuse('refused ambiguous registry arms/classes/denominators')
        ns = {c['groupId']: int(c['value']) for c in denoms[0]['counts']}
        vs = {m['groupId']: int(m['value']) for m in vals}
        a, b = active[0], control[0]
        candidates.append(count_result(vs[a], ns[a], vs[b], ns[b], [json.dumps(measure, ensure_ascii=False, sort_keys=True)]))
    return unique(candidates, endpoint)


def extract(request, root=ROOT):
    extra = set(request) - INPUT_KEYS
    if extra or set(request) != INPUT_KEYS:
        raise ValueError(f'refused checker input keys: {sorted(extra or (INPUT_KEYS-set(request)))}; stored values/result spans forbidden')
    if request['kind'] != 'real pooled number':
        return dict(verdict='EXCLUDED', reason=f"refused {request['kind']}: {request['row_id']}")
    path = (root / request['document_ref'].split('#')[0]).resolve()
    if not path.is_relative_to(root.resolve()):
        return refuse(f"refused out-of-root source {request['document_ref']}")
    if not path.is_file():
        return refuse(f"need missing cited source {request['document_ref']}")
    raw = path.read_bytes()
    text = raw.decode('utf-8')
    endpoint = request['endpoint']
    if path.suffix == '.json':
        data = json.loads(text)
        if request['record_id'].startswith('NCT'):
            result = registry(data, request['record_id'], endpoint)
        else:
            records = [r for r in data.get('records', []) if str(r.get('id')) == request['record_id'].replace('PMID ', '')]
            result = prose(records[0].get('abstract', ''), endpoint, request['rowtype']) if len(records) == 1 else refuse('need uniquely identified committed abstract')
    elif path.suffix == '.xml':
        tree = ET.fromstring(text)
        candidates = []
        if request['rowtype'] == 'count2x2':
            for table in tree.iter('table'):
                lines = [' | '.join(norm(''.join(c.itertext())) for c in tr if c.tag in ('td', 'th')) for tr in table.iter('tr')]
                r = tables('\n'.join(lines), endpoint, request['rowtype'])
                if 'values' in r:
                    candidates.append(r)
            result = unique(candidates, endpoint)
        else:
            # Paragraph scope prevents adjacent table/subgroup estimates from leaking.
            for p in tree.iter('p'):
                r = prose(norm(''.join(p.itertext())), endpoint, request['rowtype'])
                if 'values' in r:
                    candidates.append(r)
            result = unique(candidates, endpoint)
    elif '=== TABLES' in text:
        result = tables(text, endpoint, request['rowtype'])
    else:
        result = prose(text, endpoint, request['rowtype'])
    result.update(document_ref=request['document_ref'], document_sha256=hashlib.sha256(raw).hexdigest())
    return result


def prose(text, endpoint, rowtype):
    text = '\n'.join(x for x in text.splitlines() if not x.startswith('#'))
    if rowtype == 'effect':
        if not endpoint_matches(endpoint, norm(text)):
            return refuse(f'need endpoint-bound source sentence for {endpoint}')
        pattern = r'(?:\bHR\b|hazard ratio)\s*(?:of\s*)?[,=:]?\s*(\d+\.\d+)\s*[;(]\s*95%\s*CI\s*[,=:]?\s*(\d+\.\d+)\s*(?:to|[–−,-])\s*(\d+\.\d+)'
        matches = list(re.finditer(pattern, text, re.I))
        return unique([effect_result(m.groups(), [norm(text)]) for m in matches], endpoint)
    if rowtype == 'count2x2':
        candidates = []
        for line in text.splitlines():
            if not endpoint_matches(endpoint, line):
                continue
            arms = re.findall(r'([A-Za-z][A-Za-z0-9 .]*?)\s+(\d+)\s*/\s*(\d+)(?:[;.]|$)', line)
            controls = [a for a in arms if a[0].strip().lower() == 'placebo']
            active = [a for a in arms if a not in controls]
            if len(active) == len(controls) == 1:
                a, b = active[0], controls[0]
                candidates.append(count_result(int(a[1]), int(a[2]), int(b[1]), int(b[2]), [line]))
        return unique(candidates, endpoint)
    return refuse(f'need supported source schema for {rowtype}: {endpoint}')


def compare(stored, extraction, rowtype):
    if 'values' not in extraction:
        return extraction
    keys = ('effect', 'ci_low', 'ci_high') if rowtype == 'effect' else ('ai', 'n1i', 'ci', 'n2i')
    diffs = []
    for key in keys:
        token = extraction['printed'][key]
        # Half a printed unit is the rounding cell; integer counts are exact.
        tol = Decimal(0) if rowtype == 'count2x2' else Decimal(10) ** Decimal(Decimal(token).as_tuple().exponent) / 2
        if stored.get(key) is None or abs(Decimal(str(stored[key])) - Decimal(token)) > tol:
            diffs.append(dict(field=key, stored=stored.get(key), extracted=extraction['values'][key], tolerance=float(tol)))
    return dict(extraction, verdict='DISAGREE' if diffs else 'EXACT_MATCH', differences=diffs,
                **({'adjudication': 'UNRESOLVED', 'adjudication_note': 'Source review required; no automatic OUR_ERROR attribution.'} if diffs else {}))


def wilson(k, n):
    if not n:
        return None
    z = 1.96; p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0, c-h), min(1, c+h)]


def census(root=ROOT, *, new_only=False):
    pop, topics = population(root)
    sample = read(root / 'docs/error_rate_sample.json')
    old = {r['row_id']: r for r in sample['rows']}
    audit = read(root / 'docs/error_rate.json')
    # Reproducible reruns re-extract this wave as well as newly missing rows.
    targets = sorted(set(pop)-set(old) | (set() if new_only else {rid for rid in pop if old.get(rid, {}).get('provenance') == PROVENANCE}))
    results = []
    for rid in targets:
        outcome, trial, kind = pop[rid]
        request = checker_input(rid, outcome, trial, kind)
        ext = extract(request, root)
        result = compare(trial, ext, request['rowtype'])
        results.append(dict(row_id=rid, kind=kind, provenance=PROVENANCE,
                            stored={k: trial[k] for k in FIELDS if k in trial},
                            checker_input=request, **result))
    counts = Counter(r['verdict'] for r in results)
    comparable = counts['EXACT_MATCH'] + counts['DISAGREE']
    live = {rid for rid, (_, _, kind) in pop.items() if kind == 'real pooled number'}
    exclusions = [{'row_id': rid, 'kind': kind} for rid, (_, _, kind) in pop.items() if kind != 'real pooled number']
    summary = dict(topics_examined=len(topics), topics_without_review=sorted(s for s in topics if not (root/'docs/reviews'/s/'review.json').exists()),
                   live_population=len(pop), data_denominator=len(live), excluded=exclusions,
                   n_rechecked=comparable, N_uncensused=len(results), counts=dict(counts),
                   disagreement_rate=counts['DISAGREE']/comparable if comparable else None,
                   disagreement_wilson95=wilson(counts['DISAGREE'], comparable),
                   unaccounted_removals=sorted(set(old)-set(pop)-set(audit.get('removed_by_census_fixes', []))),
                   rules={v: {'n': counts[v], 'N': len(results), 'n_of_N': f'{counts[v]} of {len(results)}',
                              'items': [r['row_id'] for r in results if r['verdict']==v]}
                          for v in ('EXACT_MATCH', 'DISAGREE', 'NOT_RECHECKABLE', 'EXCLUDED')})
    return summary, results, pop


def row_byte_spans(raw):
    """Offsets of original JSON row objects; preserve their literal bytes on append."""
    start = re.search(rb'"rows"\s*:\s*\[', raw).end()
    decoder = json.JSONDecoder(); text = raw[start:].decode('utf-8'); i = 0; spans = []
    while True:
        while i < len(text) and text[i] in ' \t\r\n,': i += 1
        if text[i] == ']':
            return spans, start + len(text[:i].encode('utf-8'))
        _, end = decoder.raw_decode(text, i)
        spans.append(text[i:end].encode('utf-8')); i = end


def write(summary, results, pop, root=ROOT):
    sp = root/'docs/error_rate_sample.json'; ep = root/'docs/error_rate.json'
    raw = sp.read_bytes(); sample = json.loads(raw); existing = {r['row_id'] for r in sample['rows']}
    additions = [r for r in results if r['row_id'] not in existing]
    spans, end = row_byte_spans(raw)
    if additions:
        insertion = (',\n' if spans else '') + ',\n'.join(json.dumps(r, ensure_ascii=False, indent=2) for r in additions) + '\n'
        updated = raw[:end] + insertion.encode('utf-8') + raw[end:]
        updated = re.sub(rb'("n"\s*:\s*)\d+', lambda m: m[1]+str(len(existing)+len(additions)).encode(), updated, count=1)
        note = json.dumps('BLIND_V2 additions independently re-extracted from committed source bytes; every pre-existing row object retained byte-for-byte. Legacy verdicts are historical, not newly reverified.').encode('utf-8')
        updated = re.sub(rb'("refresh_note"\s*:\s*)"(?:[^"\\]|\\.)*"', lambda m: m[1]+note, updated, count=1)
        assert row_byte_spans(updated)[0][:len(spans)] == spans
        sp.write_bytes(updated)
    data = read(ep)
    if 'HISTORICAL_before_blind_v2' not in data:
        data['HISTORICAL_before_blind_v2'] = dict(data)
    # Historical cycle-76 numbers remain untouched in the complete snapshot.
    all_ids = existing | {r['row_id'] for r in additions}
    data.update(measured_utc=datetime.now(timezone.utc).date().isoformat(), population=len(all_ids),
                census_population=summary['N_uncensused'],
                n_pooled_at_measurement=len(pop), n_pooled_current_after_fixes=len(pop),
                current_pooled_population=len(pop), removed_by_census_fixes=sorted(all_ids-set(pop)),
                independently_reverified=summary['n_rechecked'], exact_match=summary['counts'].get('EXACT_MATCH', 0),
                disagreements_pre_adjudication=summary['counts'].get('DISAGREE', 0),
                disagreement_rate=summary['disagreement_rate'], disagreement_wilson95=summary['disagreement_wilson95'],
                independent_audit_state='INCREMENTAL_BLIND_V2',
                inventory_refreshed_utc=datetime.now(timezone.utc).date().isoformat(),
                inventory_method='scripts/error_rate_blind_v2.py; exact live predicate plus independent extraction of additions',
                measurement_scope='BLIND_V2 additions only; legacy sample rows retain historical verdicts and are not newly reverified',
                blind_v2=summary,
                _doc='Incremental blind source re-extraction. Current rate describes BLIND_V2 additions only, not all live rows. Original cycle-76 figures and notes are preserved verbatim as JSON values under HISTORICAL_before_blind_v2.')
    data['confirmed_our_errors_after_adjudication'] = sum(r.get('adjudication') == 'OUR_ERROR' for r in results)
    data['confirmed_our_errors_note'] = 'BLIND_V2 only; no previously identified defect is erased. See HISTORICAL_before_blind_v2.'
    data['not_recheckable_from_abstract'] = summary['counts'].get('NOT_RECHECKABLE', 0)
    data['not_recheckable_note'] = 'BLIND_V2 checks held tables, registry results and abstracts, not abstracts alone.'
    data['adjudication'] = [r for r in results if r['verdict'] == 'DISAGREE']
    data['not_independently_rechecked_current'] = sum(r['verdict']=='NOT_INDEPENDENTLY_RECHECKED' for r in read(sp)['rows'] if r['row_id'] in pop)
    ep.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--write', action='store_true')
    parser.add_argument('--new-only', action='store_true', help='Audit only row IDs absent from the append-only sample')
    args = parser.parse_args()
    if args.write and args.new_only:
        parser.error('--new-only is read-only: do not replace the saved wave rate with a subset')
    summary, results, pop = census(new_only=args.new_only)
    if args.write:
        write(summary, results, pop)
    print(json.dumps(dict(summary=summary, rows=results), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
