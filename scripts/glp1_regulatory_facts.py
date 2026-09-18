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
SOURCES = {'FREEDOM-CVO': 'fda_media_172242_ITCA650.pdf', 'FLOW': '209637s025lbl.pdf'}
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
            located.pop('effect', None)
            located.pop('counts', None)
            for candidate in located.get('conflicts', []):
                candidate.pop('effect', None)
                candidate.pop('counts', None)
        facts.append({'trial': trial, 'outcome': '3-point MACE', **meta, **located})
    artifact = {'generated_by': 'scripts/glp1_regulatory_facts.py',
                'mechanism': 'deterministic regex/table locator over committed .pdf.txt; no model call',
                'offset_convention': 'zero-based, end-exclusive; characters in UTF-8 decoded bytes without newline normalization; byte offsets also supplied',
                'facts': facts}
    validate(artifact, root)
    return artifact


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
        for candidate in [fact, *fact.get('conflicts', [])]:
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
        for key in ('table', 'definition_span', 'result_span', 'components', 'nct', 'nct_span', 'conflicts'):
            if key == 'conflicts' and meta['provenance_check']['state'] != 'MATCH':
                continue
            if fact.get(key) != expected.get(key):
                raise ValueError('locator binding mismatch: ' + key)


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / OUTPUT)
    parser.add_argument('--validate', type=Path)
    parser.add_argument('--report', action='store_true')
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
    for fact in artifact['facts']:
        print(f"{fact['trial']}: {fact['state']}; provenance={fact['provenance_check']['state']}")


if __name__ == '__main__':
    main()
