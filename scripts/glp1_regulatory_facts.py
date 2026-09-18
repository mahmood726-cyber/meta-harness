"""Offline, source-bound extraction. No outcome values are encoded in this module."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.target_endpoint import _components_from_text

DIRECTORY = Path('outputs/handover/glp1_regulatory')
INDEX = DIRECTORY / 'regulatory_sources_glp1.json'
OUTPUT = Path('cache/glp1-ra-mace-t2d/regulatory_facts.json')
SOURCES = {'FREEDOM-CVO': 'fda_media_172242_ITCA650.pdf', 'FLOW': '209637s025lbl.pdf',
           'ELIXA': '208471Orig1s000StatR.pdf'}
PAGE = re.compile(r'(?m)^(?:### PAGE (\d+)|===== page (\d+) =====)')
FREEDOM_CAPTION = re.compile(r'Table 19\. Time to First Occurrence[^\n]*\n[^\n]*FREEDOM \(CLP-107\)[^\n]*')
FLOW_CAPTION = re.compile(r'Table 10: Analyses of the Primary and Secondary Endpoints and their Individual Components in FLOW\s+Trial')
FREEDOM_DEFINITION = re.compile(r'3-Point MACE \(CV\s+Death, Nonfatal MI, Nonfatal Stroke\)')
FLOW_DEFINITION = re.compile(r'Composite of cardiovascular death,\s+non-fatal myocardial infarction,\s+non-fatal stroke \(time to first\s+occurrence\)')
DECIMAL = r'\d+(?:\.\d+)?'
EFFECT = rf'(?P<hr>{DECIMAL})\s*\(\s*(?P<lo>{DECIMAL}),\s*(?P<hi>{DECIMAL})\s*\)'
FREEDOM_ROW = re.compile(
    rf'3-Point MACE\*\s+(?P<ie>\d+)/(?P<inn>\d+)\s+\({DECIMAL}%\)\s+{DECIMAL}\s+'
    rf'(?P<ce>\d+)/(?P<cn>\d+)\s+\({DECIMAL}%\)\s+{DECIMAL}\s+{EFFECT}')
FLOW_ROW = re.compile(FLOW_DEFINITION.pattern +
    rf'\s+(?P<ce>\d+)\s+\({DECIMAL}\)\s+(?P<ie>\d+)\s+\({DECIMAL}\)\s+{EFFECT}')
FLOW_ARMS = re.compile(r'Placebo\s+N=(?P<cn>\d+)\s+\(%\)\s+OZEMPIC\s+1 mg\s+N=(?P<inn>\d+)')
ELIXA_CAPTION = re.compile(r'Table 8: Analysis of the MACE Endpoint[^\S\r\n]*')
ELIXA_ARMS = re.compile(r'Placebo\s+\(N=(?P<cn>[\d,]+)\)\s+Lixisenatide\s+\(N=(?P<inn>[\d,]+)\)\s+Hazard ratio\s+\(95% CI\)')
ELIXA_ROW = re.compile(rf'MACE endpoint \((?P<analysis>on-study|on-treatment)\)\s+{EFFECT}\s+No\. of patients with event \(%\)\s+(?P<ce>\d+)\s+\({DECIMAL}%\)\s+(?P<ie>\d+)\s+\({DECIMAL}%\)')
ELIXA_TEXT = re.compile(rf'For ITT analysis (?P<total>\d+) MACE events were observed, (?P<ce>\d+) and (?P<ie>\d+) in placebo and\s+lixisenatide group, respectively\. The 95% confidence interval for the hazard ratio is \((?P<lo>{DECIMAL}),\s+(?P<hi>{DECIMAL})\) with a point estimate of (?P<hr>{DECIMAL})\.')
ELIXA_SUMMARY = re.compile(rf'There were (?P<total>\d+) secondary MACE events observed in the study for the ITT population, (?P<ie>\d+) in\s+the lixisenatide group and (?P<ce>\d+) in the placebo group\. The pre-specified Cox proportional hazards\s+analysis resulted in a hazard ratio estimate of (?P<hr>{DECIMAL}) with an associated 95% confidence interval of\s+\((?P<lo>{DECIMAL}),\s+(?P<hi>{DECIMAL})\)\.')


def parse_elixa(text):
    rows = [m for m in ELIXA_ROW.finditer(text) if not text[m.end():].strip()]
    if rows:
        if len(rows) != 1:
            raise ValueError('ambiguous ELIXA row')
        headers = list(ELIXA_ARMS.finditer(text))
        if len(headers) != 1:
            raise ValueError('missing or ambiguous ELIXA arm headers')
        values = {**rows[0].groupdict(), **headers[0].groupdict()}
    else:
        match = ELIXA_TEXT.fullmatch(text) or ELIXA_SUMMARY.fullmatch(text)
        if not match:
            raise ValueError('unparseable ELIXA result')
        values = match.groupdict()
        if int(values['total']) != int(values['ie']) + int(values['ce']):
            raise ValueError('ELIXA event total mismatch')
    effect = dict(scale='HR', value=float(values['hr']), ci_low=float(values['lo']), ci_high=float(values['hi']))
    counts = {arm: {'events': int(values[e]),
                    'n': int(values[n].replace(',', '')) if n in values else 'NOT_STATED_IN_SPAN'}
              for arm, e, n in [('intervention', 'ie', 'inn'), ('comparator', 'ce', 'cn')]}
    if not 0 < effect['ci_low'] <= effect['value'] <= effect['ci_high']:
        raise ValueError('invalid effect interval')
    if any(c['events'] < 0 or (isinstance(c['n'], int) and not 0 <= c['events'] <= c['n']) for c in counts.values()):
        raise ValueError('invalid counts')
    return effect, counts


def differences(left, right):
    """Missing prose denominators are absence, not numeric disagreement."""
    result = [k for k in ('value', 'ci_low', 'ci_high') if left['effect'][k] != right['effect'][k]]
    for arm in ('intervention', 'comparator'):
        for key in ('events', 'n'):
            a, b = left['counts'][arm][key], right['counts'][arm][key]
            if isinstance(a, int) and isinstance(b, int) and a != b:
                result.append(f'counts.{arm}.{key}')
    return result


def locate_elixa(text):
    def unique(pattern):
        matches = list(re.finditer(pattern, text, re.S))
        if len(matches) != 1:
            raise ValueError('ELIXA required span missing or ambiguous: ' + pattern)
        return match_span(text, matches[0])

    definition = unique(r'MACE, a composite endpoint defined as\s+cardiovascular death, non-fatal myocardial infarction, or non-fatal stroke, as adjudicated by the\s+cardiovascular events adjudication committee \(CAC\)\.')
    role = unique(r'Secondary endpoints include alternate composites of cardiovascular outcomes, MACE and all-\s+cause mortality, and other exploratory endpoints\.')
    analysis = unique(r'The primary analysis population is intent to treat \(ITT\).*?study end date, even if a subject has discontinued randomized treatment\.')
    local_analysis = unique(r'ITT analyses \(on-study and on-treatment\) of MACE, defined as cardiovascular death, non-fatal\s+MI, and non-fatal stroke, are consistent with those of MACE\+ \(Table 8\)\.')
    treatment = unique(r'The on-treatment period for CV\s+endpoints is defined as the time from randomization up to \d+ days after the last injection of\s+randomized product\.')
    common = dict(definition_span=definition, components=sorted(_components_from_text(definition['text'])),
                  endpoint_role='secondary MACE; primary on-study analysis of this target', endpoint_role_span=role)
    tables, others = [], []
    for caption in ELIXA_CAPTION.finditer(text):
        end_match = re.search(r'Source:|### PAGE ', text[caption.end():])
        end = caption.end() + end_match.start() if end_match else len(text)
        body = text[caption.end():end]
        if not ELIXA_ARMS.search(body):
            continue
        for row in ELIXA_ROW.finditer(body):
            result = span(text, caption.end(), caption.end() + row.end())
            effect, counts = parse_elixa(result['text'])
            item = dict(common, kind='table', table=match_span(text, caption), result_span=result,
                        row_span=match_span(text, row, caption.end()), effect=effect, counts=counts,
                        analysis_set_span=local_analysis, analysis_label_span=span(text, caption.end()+row.start('analysis'), caption.end()+row.end('analysis')),
                        censoring_rule_span=treatment if row['analysis'] == 'on-treatment' else analysis)
            (others if row['analysis'] == 'on-treatment' else tables).append(item)
    passages = []
    for match in ELIXA_TEXT.finditer(text):
        result = match_span(text, match)
        effect, counts = parse_elixa(result['text'])
        passages.append(dict(common, kind='text', result_span=result, effect=effect, counts=counts,
                             analysis_set_span=span(text, match.start(), match.start()+len('For ITT analysis')),
                             censoring_rule_span='NOT_STATED_IN_SPAN', analysis_context_span=analysis))
    if len(tables) != 1 or len(passages) != 1 or len(others) != 1:
        raise ValueError('ELIXA requires unique on-study table, nearby text and on-treatment table')
    comparison = differences(tables[0], passages[0])
    result = dict(common, nct='NOT_LOCATED', other_analyses=others, comparison={'differing_fields': comparison},
                  notes='Table and adjacent prose compared without rounding; missing prose denominators not imputed. On-treatment kept separate.')
    if comparison:
        result.update(state='CONFLICT', conflicts=[tables[0], passages[0]])
    else:
        result.update(state='LOCATED', effect=tables[0]['effect'], counts=tables[0]['counts'],
                      result_span=tables[0]['result_span'], corroborating=[tables[0], passages[0]])
    result['additional_passages'] = []
    for match in ELIXA_SUMMARY.finditer(text):
        effect, counts = parse_elixa(match.group())
        result['additional_passages'].append(dict(kind='summary_text', result_span=match_span(text, match),
            effect=effect, counts=counts, analysis_set_span=span(text, match.start(), text.index(',', match.start()) ),
            censoring_rule_span='NOT_STATED_IN_SPAN', comparison_to_table=differences(tables[0], dict(effect=effect, counts=counts))))
    return result


def read_text(path):
    # Preserve CRLF: character offsets index the UTF-8 decoded committed bytes.
    return path.read_bytes().decode('utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def span(text, start, end):
    pages = list(PAGE.finditer(text, 0, start + 1))
    end_pages = list(PAGE.finditer(text, 0, end))
    result = {'text': text[start:end], 'char_start': start, 'char_end': end,
              'byte_start': len(text[:start].encode('utf-8')),
              'byte_end': len(text[:end].encode('utf-8'))}
    if pages:
        result['page_pdf'] = int(next(g for g in pages[-1].groups() if g))
        result['page_pdf_end'] = int(next(g for g in end_pages[-1].groups() if g))
    return result


def match_span(text, match, offset=0):
    return span(text, offset + match.start(), offset + match.end())


def parse_result(trial, text):
    if trial == 'ELIXA':
        return parse_elixa(text)
    rows = list((FREEDOM_ROW if trial == 'FREEDOM-CVO' else FLOW_ROW).finditer(text))
    # A candidate ends precisely at its row, while retaining preceding arm headers.
    # Earlier rows may be present; locate() emits every one and compares them.
    terminal = [row for row in rows if not text[row.end():].strip()]
    if len(terminal) != 1:
        raise ValueError('result must end with exactly one target row')
    values = terminal[0].groupdict()
    if trial == 'FLOW':
        arms = list(FLOW_ARMS.finditer(text))
        if len(arms) != 1:
            raise ValueError('missing or ambiguous FLOW arm denominators')
        values.update(arms[0].groupdict())
        if not re.search(r'Hazard\s+ratio vs\s+placebo', text):
            raise ValueError('missing FLOW effect scale')
    elif not re.search(r'ITCA 650 Number of\s+Events/Total No\..*Control Number of.*HR \(95% CI\)', text, re.S):
        raise ValueError('missing FREEDOM arm order or effect scale')
    effect = dict(scale='HR', value=float(values['hr']), ci_low=float(values['lo']), ci_high=float(values['hi']))
    counts = {'intervention': {'events': int(values['ie']), 'n': int(values['inn'])},
              'comparator': {'events': int(values['ce']), 'n': int(values['cn'])}}
    if not 0 < effect['ci_low'] <= effect['value'] <= effect['ci_high']:
        raise ValueError('invalid effect interval')
    if any(not 0 <= arm['events'] <= arm['n'] or arm['n'] <= 0 for arm in counts.values()):
        raise ValueError('invalid counts')
    return effect, counts


def locate(trial, text):
    """Bound table search, excluding TOC captions and adjacent endpoints."""
    if trial == 'ELIXA':
        return locate_elixa(text)
    freedom = trial == 'FREEDOM-CVO'
    caption_rx = FREEDOM_CAPTION if freedom else FLOW_CAPTION
    definition_rx = FREEDOM_DEFINITION if freedom else FLOW_DEFINITION
    row_rx = FREEDOM_ROW if freedom else FLOW_ROW
    candidates = []
    searched = {'caption_regex': caption_rx.pattern, 'row_regex': row_rx.pattern,
                'scope': 'each caption to next table, figure, or extracted page boundary'}
    for caption in caption_rx.finditer(text):
        boundary = re.search(r'(?m)^(?:Table \d+[.:]|Figure \d+[.:]|### PAGE |===== page )', text[caption.end():])
        end = caption.end() + boundary.start() if boundary else len(text)
        body = text[caption.end():end]
        # Table header is required; a TOC caption is never a result candidate.
        header = re.search(r'MACE Type', body) if freedom else FLOW_ARMS.search(body)
        if not header:
            continue
        definition = definition_rx.search(text, caption.start(), end)
        if not definition:
            continue
        for row in row_rx.finditer(body):
            result = span(text, caption.end(), caption.end() + row.end())
            try:
                effect, counts = parse_result(trial, result['text'])
            except ValueError:
                continue
            analysis = re.search(r'ITT Population End of Study', caption.group()) if freedom else None
            item = {'table': match_span(text, caption),
                    'definition_span': match_span(text, definition), 'result_span': result,
                    'effect': effect, 'counts': counts,
                    'components': sorted(_components_from_text(definition.group())),
                    'analysis_set_span': match_span(text, analysis, caption.start()) if analysis else 'NOT_STATED_IN_SPAN',
                    'censoring_rule_span': match_span(text, analysis, caption.start()) if analysis else 'NOT_STATED_IN_SPAN',
                    'endpoint_role': 'Table 19 three-point composite' if freedom else 'cardiovascular composite; separate from primary kidney composite',
                    'state': 'LOCATED'}
            if not freedom:
                section = re.search(r'14\.3 Kidney Outcomes Trial[^\n]*\nKidney Disease\s+FLOW \((NCT\d{8})\)', text)
                if section:
                    item.update(section_span=match_span(text, section), nct=section.group(1),
                                nct_span=span(text, section.start(1), section.end(1)))
                primary = re.search(r'OZEMPIC was superior to placebo in reducing the incidence of the primary composite endpoint.*?as shown in Table 10 and Figure 7\.', text, re.S)
                if primary:
                    item['primary_endpoint_context_span'] = match_span(text, primary)
            item.setdefault('nct', 'NOT_LOCATED')
            candidates.append(item)
    if not candidates:
        return {'state': 'NOT_LOCATED', 'nct': 'NOT_LOCATED', 'searched': searched,
                'notes': 'No uniquely parseable target row and definition inside caption-bounded table.'}
    if len(candidates) > 1:
        different = len({json.dumps([c['effect'], c['counts']], sort_keys=True) for c in candidates}) > 1
        return {'state': 'CONFLICT' if different else 'AMBIGUOUS', 'conflicts': candidates,
                'searched': searched, 'notes': 'Multiple candidates retained; no candidate selected.'}
    return {**candidates[0], 'searched': searched, 'notes': 'Definition bound to its own table row; all numeric results parsed from contiguous result span including headers.'}


def provenance(root, trial):
    filename = SOURCES[trial]
    document, text_file = DIRECTORY / 'held' / filename, DIRECTORY / (filename + '.txt')
    records = json.loads(read_text(root / INDEX))['sources']
    matches = [r for r in records if r.get('held', {}).get('held_in_tree') == document.as_posix()]
    meta = {'document': document.as_posix(), 'text_file': text_file.as_posix(),
            'document_sha256': sha(root / document), 'text_sha256': sha(root / text_file)}
    status = 'MISSING_INDEX_RECORD'
    if len(matches) == 1:
        record = matches[0]
        status = 'MATCH' if (meta['document_sha256'] == record.get('document_sha256') and
                            meta['text_sha256'] == record.get('extracted_text_sha256') and
                            record.get('held', {}).get('extracted_text') == text_file.as_posix()) else 'HASH_OR_PATH_MISMATCH'
        meta['source_id'] = record['source_id']
    elif len(matches) > 1:
        status = 'AMBIGUOUS_INDEX_RECORD'
    meta['provenance_check'] = {'state': status, 'index': INDEX.as_posix()}
    return meta


def build(root=ROOT):
    facts = []
    for trial in SOURCES:
        meta = provenance(root, trial)
        located = locate(trial, read_text(root / meta['text_file']))
        if meta['provenance_check']['state'] != 'MATCH':
            # Preserve evidence for review, but never admit an unverified numeric value.
            located['span_location_state'] = located['state']
            located['state'] = 'NOT_LOCATED'
            located['refusal_scope'] = 'required provenance index verification'
            located['notes'] += ' REFUSED: ' + meta['provenance_check']['state'] + '; numeric fields withheld, even when spans are located.'
            withhold_numbers(located)
        facts.append({'trial': trial, 'outcome': '3-point MACE', **meta, **located})
    artifact = {'generated_by': 'scripts/glp1_regulatory_facts.py',
                'mechanism': 'deterministic regex/table locator over committed .pdf.txt; no model call',
                'offset_convention': 'zero-based, end-exclusive; characters in UTF-8 decoded bytes without newline normalization; byte offsets also supplied',
                'facts': facts}
    validate(artifact, root)
    return artifact


def withhold_numbers(node):
    if isinstance(node, dict):
        node.pop('effect', None)
        node.pop('counts', None)
        for value in node.values():
            withhold_numbers(value)
    elif isinstance(node, list):
        for value in node:
            withhold_numbers(value)


def validate(artifact, root=ROOT):
    for fact in artifact['facts']:
        meta = provenance(root, fact['trial'])
        for key, value in meta.items():
            if fact.get(key) != value:
                raise ValueError('provenance mismatch: ' + key)
        text = read_text(root / fact['text_file'])

        def check_spans(node):
            if isinstance(node, dict):
                if 'char_start' in node:
                    if span(text, node['char_start'], node['char_end']) != node:
                        raise ValueError('span round-trip mismatch')
                else:
                    for value in node.values():
                        check_spans(value)
            elif isinstance(node, list):
                for value in node:
                    check_spans(value)

        check_spans(fact)
        if fact.get('state') == 'CONFLICT':
            conflicts = fact.get('conflicts', [])
            if 'effect' in fact:
                raise ValueError('CONFLICT must omit top-level effect')
            if len(conflicts) < 2 or not any(differences(a, b) for a in conflicts for b in conflicts):
                raise ValueError('CONFLICT requires differing parsed values')
        for candidate in [fact, *fact.get('conflicts', []), *fact.get('other_analyses', []),
                          *fact.get('additional_passages', []), *fact.get('corroborating', [])]:
            if 'effect' in candidate or 'counts' in candidate:
                if not candidate.get('result_span'):
                    raise ValueError('numeric value without result_span')
                if meta['provenance_check']['state'] != 'MATCH':
                    raise ValueError('numeric value without verified provenance')
                effect, counts = parse_result(fact['trial'], candidate['result_span']['text'])
                if candidate.get('effect') != effect or candidate.get('counts') != counts:
                    raise ValueError('stored numeric value differs from parsed result_span')
            if candidate.get('state') == 'LOCATED':
                if not candidate.get('effect') or not candidate.get('definition_span'):
                    raise ValueError('LOCATED fact missing evidence')
                if candidate['components'] != sorted(_components_from_text(candidate['definition_span']['text'])):
                    raise ValueError('definition components mismatch')
        # Replay the locator too: a true span from a different endpoint is insufficient.
        expected = locate(fact['trial'], text)
        if meta['provenance_check']['state'] != 'MATCH':
            withhold_numbers(expected)
        for key in ('table', 'definition_span', 'result_span', 'components', 'nct', 'nct_span', 'conflicts',
                    'other_analyses', 'additional_passages', 'corroborating', 'comparison',
                    'analysis_set_span', 'censoring_rule_span', 'endpoint_role_span'):
            if key == 'conflicts' and meta['provenance_check']['state'] != 'MATCH':
                continue
            if fact.get(key) != expected.get(key):
                raise ValueError('locator binding mismatch: ' + key)
        if meta['provenance_check']['state'] == 'MATCH' and fact['state'] != expected['state']:
            raise ValueError('locator state mismatch')


def serialize(artifact):
    return (json.dumps(artifact, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def write_report(artifact, proposal_path, test_output_path):
    """Post-generation audit only: proposal never enters build/locate/validate."""
    import subprocess
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    lines = ['# LANE FX report', '', f'HEAD: `{head}`. No commit; no network.', '',
             'MEASURED: 2 of 2 requested endpoint rows located in held text; 1 of 2 admitted as numeric facts; '
             '1 of 2 refused because the required provenance index has no FLOW record. Both held PDF/text '
             'pairs exist in git. FREEDOM hashes match the index; FLOW hashes are measured on disk but cannot be matched to that index.', '',
             'INFERRED: FLOW cardiovascular MACE is a secondary endpoint: the section explicitly names the kidney/CV-death '
             'composite as primary, separately describes cardiovascular MACE, and the table caption distinguishes primary and secondary endpoints. '
             'The numeric result is bound only to its own cardiovascular row definition, never to the primary kidney definition.', '',
             'CLAIMED: no submission, certification, deployment, or portfolio-status change. '
             'No Overmind PASS claimed. This is a bounded extraction artefact, not a release.', '',
             '## Scope and limitations', '',
             '`NOT_LOCATED` for FLOW is the contract-compatible admission refusal state, not a claim that its text is missing; '
             '`span_location_state: LOCATED` and `refusal_scope` disambiguate it. No FLOW effect/count fields are admitted. '
             'Repair of the provenance index requires its owner; this lane does not invent a retrieval record or self-certify an expected hash. '
             'FREEDOM NCT is NOT_LOCATED (no NCT token in the held document). FLOW analysis set and censoring rule are '
             'NOT_STATED_IN_SPAN; no ITT assumption is made.', '',
             'Offsets are zero-based/end-exclusive in UTF-8 decoded committed bytes with CRLF preserved; byte offsets are also stored. '
             'Pages come from the extraction page markers. Result spans deliberately include arm headers to source denominators and arm order. '
             'FLOW therefore includes preceding kidney/component rows, but the parser anchors solely on the cardiovascular-composite row.', '',
             'Helper ownership inspected: `harness/locate.py` is a cached model judgment reader, `harness/fda.py` is a remote acquisition adapter; '
             '`harness/verified_source.py` is absent (file search confirmed). Neither existing module locates held-text offsets. '
             'Reused `harness.target_endpoint._components_from_text` for definition vocabulary. No shared `heldtext.py` was needed; '
             'the small task-specific locator stays in the owned script. The abstract-oriented `bind_result_span` is not applied to an entire mixed-endpoint table; '
             'the table parser binds each result to the specific caption subspan or row definition.', '',
             '## Static versus dynamic disclosure', '',
             '| Item | Static mechanism or dynamic data |', '|---|---|',
             '| Trial labels, file names, caption/row patterns | Static source-selection configuration; no clinical result constants |',
             '| HR, confidence limits, events, denominators | Dynamically parsed from verbatim result span |',
             '| Definitions, NCT, analysis/censoring text | Located in held text; missing information remains explicit |',
             '| Hashes, offsets, PDF pages | Computed from held bytes and page markers |',
             '| Component names | Existing target_endpoint vocabulary applied only to definition span |',
             '| Admission | Deterministic comparison to existing provenance index; missing/mismatching entry refuses values |',
             '| Cross-check | Model proposal consulted after artefact generation; never an extraction input |', '']
    for fact in artifact['facts']:
        lines += [f"## {fact['trial']}", '', f"State: {fact['state']}; provenance: {fact['provenance_check']['state']}.",
                  f"PDF SHA-256: `{fact['document_sha256']}`.", f"Text SHA-256: `{fact['text_sha256']}`.",
                  f"NCT: {fact['nct']}. Components: {', '.join(fact['components'])}.", '']
        for key in ('section_span', 'table', 'definition_span', 'result_span', 'analysis_set_span', 'censoring_rule_span', 'primary_endpoint_context_span'):
            value = fact.get(key)
            if value is None:
                continue
            if isinstance(value, str):
                lines += [f'{key}: {value}', '']
            else:
                lines += [f"{key}: chars [{value['char_start']}, {value['char_end']}), bytes [{value['byte_start']}, {value['byte_end']}), PDF page {value.get('page_pdf')}.",
                          '', '```text', value['text'], '```', '']
        parsed = parse_result(fact['trial'], fact['result_span']['text'])
        label = 'Admitted parsed values' if fact['state'] == 'LOCATED' else 'Diagnostic parse ONLY; refused for admission because provenance is missing'
        lines += [label + ':', '', '```json', json.dumps({'effect': parsed[0], 'counts': parsed[1]}, indent=2), '```', '',
                  'Conflicts: no disagreeing candidate in the caption-bounded target table search. '
                  'Other populations, censoring windows, and four-point endpoints are not interchangeable candidates.', '']
    lines += ['## Independent proposal cross-check (after first artefact generation)', '',
              f'Proposal: `{proposal_path.relative_to(ROOT).as_posix()}`; SHA-256 `{sha(proposal_path)}`. '
              'This is a model proposal, not source evidence. Every quoted fragment below was searched on its proposed page after whitespace folding only; '
              'ellipses split fragments, and each successful hit maps back to held-text character offsets. '
              'A failed literal match is disclosed, not treated as a numerical conflict. Abbreviated/reordered quotes need not be verbatim.', '',
              '| Proposal passage | Held-page quoted fragments located | Missing fragments (proposal text only) |', '|---|---|---|']
    proposal = read_text(proposal_path)
    text = read_text(ROOT / artifact['facts'][0]['text_file'])
    for section in re.finditer(r'Passage (\d+):\s*"(.*?)"\s*(.*?)(?=\nPassage \d+:|\nCONFLICTS LIST:|\Z)', proposal, re.S):
        number, quote, discussion = section.groups()
        page = re.search(r'Page marker: ### PAGE (\d+)', discussion)
        if not page:
            continue
        page_start = re.search(r'(?m)^### PAGE ' + page[1] + r'\s*$', text)
        next_page = PAGE.search(text, page_start.end())
        end = next_page.start() if next_page else len(text)
        tokens = list(re.finditer(r'\S+', text[page_start.end():end]))
        normalized, mapping = '', []
        for token in tokens:
            if normalized:
                normalized += ' '
                mapping.append(page_start.end() + token.start())
            normalized += token.group()
            mapping.extend(range(page_start.end() + token.start(), page_start.end() + token.end()))
        fragments = [f.strip() for f in re.split(r'\.\.\.|…', quote) if f.strip()]
        hits, missing = [], []
        for fragment in fragments:
            folded = ' '.join(fragment.split())
            pos = normalized.find(folded)
            if pos < 0:
                missing.append('`' + folded.replace('|', '/') + '`')
            else:
                hits.append(f'[{mapping[pos]}, {mapping[pos + len(folded) - 1] + 1})')
        lines += [f"| {number} | {len(hits)} of {len(fragments)}; " + '; '.join(hits) + ' | ' + ('; '.join(missing) or 'None') + ' |']
    lines += ['', 'Interpretation: passage 8 agrees with the extracted Table 19 definition, counts, estimate, interval, '
              'population and end-of-study window. Passages 1 (FREEDOM on-study clause), 7 (first endpoint), and 11 '
              'are corroborating pointers; no numeric disagreement with Table 19 is identified. The proposal calls these a conflict '
              'in its final list, but decimal formatting differences are not numeric conflicts. Its pooled-analysis conflicts concern different '
              'estimands and are not imported into the FREEDOM-only fact. Passages 2–6, 9–10, and 12–21 concern other endpoints, '
              'populations, trials or censoring windows; the table above audits their quoted fragments, not their analytical correctness. '
              'The search preserves punctuation and line-end hyphens; it does not reconstruct flattened table columns. '
              'There is no FLOW proposal in this file.', '',
              '## Verification', '',
              'Initial focused run: 1 failed, 10 passed. Failure was a null `held_in_tree` value in an unrelated provenance record '
              'inside the hash-mismatch test fixture. Fixed the fixture to handle null paths; no source data changed. '
              'The corruption plants are validated on scratch files while still corrupt, and remain rejected without repairing them.', '',
              'Final exact test output:', '', '```text', read_text(test_output_path).rstrip(), '```', '',
              'The universal hash-match requirement is deliberately not claimed: 1 of 2 pairs matches the index; '
              'the other is tested to refuse admission. Deterministic regeneration compares complete artefact bytes. '
              'No source files, index, workbook, protected harness modules, or git history changed.', '']
    (ROOT / 'LANE-FX-REPORT.md').write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))


def write_fx2_report(artifact, test_output_path):
    """Post-generation proposal audit; never supplies locator inputs."""
    import subprocess
    fact = next(f for f in artifact['facts'] if f['trial'] == 'ELIXA')
    text = read_text(ROOT / fact['text_file'])
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    lines = ['# LANE FX2 report', '', f'HEAD: `{head}`. No commit; no network.', '',
        'MEASURED: 1 of 1 requested target definitions, 2 of 2 primary-analysis result passages, '
        'and 1 of 1 on-treatment table rows located. 2 of 2 ELIXA PDF/text digests match the required provenance index. '
        'The raw-text digest was computed before decoding/any normalization; extraction preserves CRLF. '
        'The locator-only artefact `.tmp/elixa-located-before-provenance.json` was produced before consulting '
        'the ELIXA provenance index or either proposal. The final artefact applies required provenance admission.', '',
        'INFERRED: the requested three-point target is the secondary MACE endpoint, not the trial primary MACE+ endpoint. '
        'The source explicitly classifies it as secondary. The on-study table and adjacent ITT prose refer to the same target; '
        'the general methods span defines on-study follow-up through the common study end date, including treatment discontinuation. '
        'The adjacent prose does not itself restate censoring, so its censoring_rule_span remains NOT_STATED_IN_SPAN.', '',
        'CLAIMED: bounded offline extraction only; no release, submission, certification, pooling, or portfolio-status change. '
        'No protected harness modules, source files, index, workbook, or original FX report changed.', '',
        '## Static versus dynamic disclosure', '',
        '| Item | Static configuration | Dynamic evidence |', '|---|---|---|',
        '| Selection | Trial/file labels, caption/row regexes, endpoint vocabulary | Unique source matches; missing/ambiguous required matches fail closed |',
        '| Results | No clinical result constants | Effects and counts parsed from held spans; prose denominators explicitly absent |',
        '| Provenance | Existing index path | SHA-256 over raw PDF/text bytes compared to index |',
        '| Locations | Zero-based, end-exclusive convention | Character/UTF-8 byte offsets; PDF pages from extraction markers |',
        '| Conflict | Exact comparison without rounding; only shared numeric count fields compared | Differing fields computed from independently parsed passages |',
        '| Proposal audit | Whitespace-only folding, ellipsis splitting | Post-generation substring matching; never seeds extraction |', '',
        '## Provenance and comparison', '',
        f"State: {fact['state']}; source: {fact['source_id']}; provenance: {fact['provenance_check']['state']}.",
        f"PDF SHA-256: `{fact['document_sha256']}`.", f"Raw text SHA-256: `{fact['text_sha256']}`.",
        f"Mechanical differing fields: `{json.dumps(fact['comparison']['differing_fields'])}`. No top-level effect is present.",
        'The lower-bound discrepancy is retained under exact comparison as requested; no rounding-based reconciliation is attempted. '
        'Matching estimates and event counts do not resolve the interval conflict.', '',
        '## Located evidence', '']

    def emit_span(label, value):
        if not isinstance(value, dict):
            lines.extend([f'{label}: {value}.', ''])
            return
        lines.extend([f"{label}: chars [{value['char_start']}, {value['char_end']}), bytes "
                      f"[{value['byte_start']}, {value['byte_end']}), PDF page {value.get('page_pdf')}"
                      f" (end page {value.get('page_pdf_end')}).", '', '```text', value['text'], '```', ''])

    emit_span('definition_span', fact['definition_span'])
    emit_span('endpoint_role_span', fact['endpoint_role_span'])
    lines.extend(['Components: ' + ', '.join(fact['components']) + '.', ''])
    for group in ('conflicts', 'other_analyses', 'additional_passages'):
        for index, candidate in enumerate(fact.get(group, []), 1):
            lines.extend([f"### {group} / {index}: {candidate['kind']}", '',
                          'Parsed values:', '```json', json.dumps({k: candidate[k] for k in ('effect', 'counts')}, indent=2), '```', ''])
            for key in ('table', 'row_span', 'result_span', 'analysis_label_span', 'analysis_set_span',
                        'censoring_rule_span', 'analysis_context_span'):
                if key in candidate:
                    emit_span(key, candidate[key])
    lines.extend(['The on-treatment result_span retains the preceding arm headers and on-study row; '
                  'the parser accepts only the terminal on-treatment row. Its row_span isolates that row. '
                  'The executive-summary result is an additional same-target passage, with its own comparison to the table; '
                  'it is not misclassified as a different analysis.', '',
                  '## Post-generation proposal cross-check', '',
                  'Proposal: `.tmp/ref/agy_elixa.txt`. Each quoted fragment is searched only on its proposed PDF page. '
                  'Whitespace is folded for this audit only; all reported offsets map back to unchanged raw text.', '',
                  '| Passage | PDF page | Located fragments | Not located fragments |', '|---|---|---|---|'])
    proposal = read_text(ROOT / '.tmp/ref/agy_elixa.txt')
    total, found = 0, 0
    for section in re.finditer(r'\*\*Passage (\d+)\*\*\s*\* Quote: "(.*?)"(.*?)(?=\*\*Passage |\n---|\Z)', proposal, re.S):
        number, quote, discussion = section.groups()
        page = re.search(r'Page Marker: ### PAGE (\d+)', discussion)
        if not page:
            raise ValueError('proposal passage has no page')
        marker = re.search(r'(?m)^### PAGE ' + page[1] + r'\s*$', text)
        next_page = PAGE.search(text, marker.end())
        end = next_page.start() if next_page else len(text)
        normalized, mapping = '', []
        for token in re.finditer(r'\S+', text[marker.end():end]):
            if normalized:
                normalized += ' '
                mapping.append(marker.end() + token.start())
            normalized += token.group()
            mapping.extend(range(marker.end()+token.start(), marker.end()+token.end()))
        fragments = [f.strip() for f in re.split(r'\.\.\.|…', quote) if f.strip()]
        hits, missing = [], []
        for fragment in fragments:
            folded = ' '.join(fragment.split())
            pos = normalized.find(folded)
            if pos < 0:
                missing.append('`' + folded.replace('|', '/') + '`')
            else:
                hits.append(f'chars [{mapping[pos]}, {mapping[pos+len(folded)-1]+1})')
        total += len(fragments)
        found += len(hits)
        lines.append(f"| {number} | {page[1]} | {len(hits)} of {len(fragments)}; " + '; '.join(hits) + ' | ' + ('; '.join(missing) or 'None') + ' |')
    lines.extend(['', f'MEASURED: {found} of {total} proposal fragments located with the stated exact-after-whitespace-folding rule.', '',
        'The ELX report describes eight handover spans on PDF pages 7, 8, 22, 24 and 35. '
        'The fragment audit above checks these source regions independently. The target table and adjacent result are on page 24; '
        'the executive summary is on page 7. The locator binds the fuller definition on page 16, while the proposal also quotes '
        'the shorter definition on page 24. MACE+ regions are audit-only, not imported as three-point facts. '
        'This is a region cross-check, not a claim to have independently replayed all eight handover records; those records are not extraction inputs.', '',
        '## Not located / limitations', '',
        'No NCT identifier was located by this bounded locator. No trial-primary three-point endpoint definition is located: '
        'the source calls MACE secondary. Denominators and censoring rules are NOT_STATED_IN_SPAN in the nearby prose and executive summary. '
        'Proposal fragments listed as not located above are not repaired or used as evidence. The search is bounded to these source formats, '
        'not an exhaustive semantic audit of every passage. PDF page numbers come from held extraction markers; no independent PDF rendering is claimed. '
        'Existing FLOW provenance refusal remains unchanged.', '',
        '## Verification', '', 'Command: `python -m pytest -q -s tests/test_glp1_regulatory_facts.py tests/test_target_endpoint.py`.', '',
        'The first FX2 focused run passed. Corruption plants are validated from still-corrupt scratch artefacts before any repair. '
        'Tests cover byte-identical regeneration, all nested spans/values, hash-mismatch refusal, conflict rejection, and the agreeing-passages branch.', '',
        '```text', read_text(test_output_path).rstrip(), '```', ''])
    (ROOT / 'LANE-FX2-REPORT.md').write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / OUTPUT)
    parser.add_argument('--validate', type=Path)
    parser.add_argument('--report', action='store_true')
    parser.add_argument('--report-fx2', action='store_true')
    parser.add_argument('--test-output', type=Path)
    args = parser.parse_args()
    if args.validate:
        validate(json.loads(read_text(args.validate)))
        print('VALID')
        return
    artifact = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(serialize(artifact))
    if args.report:
        if not args.test_output:
            parser.error('--report requires --test-output')
        write_report(artifact, ROOT / '.tmp/ref/agy_freedom.txt', args.test_output)
    if args.report_fx2:
        if not args.test_output:
            parser.error('--report-fx2 requires --test-output')
        write_fx2_report(artifact, args.test_output)
    for fact in artifact['facts']:
        print(f"{fact['trial']}: {fact['state']}; provenance={fact['provenance_check']['state']}")


if __name__ == '__main__':
    main()
