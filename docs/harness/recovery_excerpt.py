"""Read held WHO REACT HTML, or its committed, explicitly attributed excerpt.

The fallback verifies the *declared* parent digest against the source pin; it
does not claim to have rehashed missing HTML. Only excerpt row bytes bind sizes.
"""
import hashlib
import re
from pathlib import Path

# Static source navigation and integrity pin, shared with make_react_excerpt.
# Keep the runtime fallback stdlib-only; the optional HTML parser is imported
# only when those HTML bytes actually exist. These are not research values.
HELD = 'evidence/acquisition_cascade/held/WHO-REACT/PMC8261689.local.html'
OUTPUT = 'evidence/acquisition_cascade/excerpts/WHO-REACT_Table1_arm_sizes.tables.txt'
SHA256 = 'bbed7fae330b3af11faa1a63191db3db3e7dea44ac33bc7df18c0201479cf94a'


def parse_excerpt(raw):
    text = raw.decode('utf-8')
    digest = hashlib.sha256(raw).hexdigest()
    headers = re.findall(r'^# held HTML: (\S+) sha256 ([0-9a-f]{64})$', text, re.M)
    if headers != [(HELD, SHA256)]:
        raise ValueError('REACT_EXCERPT_SOURCE_UNBOUND: ' + OUTPUT)
    populations = re.findall(r'^# population \(verbatim\): (.+)$', text, re.M)
    if len(populations) != 1 or not re.search(r'participants with outcomes recorded\.', populations[0]):
        raise ValueError('REACT_EXCERPT_POPULATION_UNBOUND: ' + OUTPUT)
    header = 'Trial | NCT (or printed registration) | intervention arm n | comparator arm n'
    if text.count(header) != 1:
        raise ValueError('REACT_EXCERPT_SCHEMA_UNBOUND: ' + OUTPUT)
    excluded = re.findall(r'; ([^;\n]+) is excluded per footnote k\.', text)
    if len(excluded) != 1 or '# footnote (verbatim): k These trials were not included in the meta-analysis.' not in text:
        raise ValueError('REACT_EXCERPT_EXCLUSION_UNBOUND: ' + OUTPUT)

    def span(quote):
        start = text.index(quote)
        return dict(quote=quote, start=start, end=start + len(quote),
                    source=OUTPUT, sha256=digest, parent_sha256=SHA256)

    rows = []
    for line in text.split(header, 1)[1].splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        cells = [s.strip() for s in line.split('|')]
        if len(cells) != 4 or not cells[0] or not re.fullmatch(r'NCT\d{8}|EU-CTR [\d/-]+', cells[1]):
            raise ValueError('REACT_EXCERPT_ROW_UNBOUND: ' + line)
        arms = []
        for values in cells[2:]:
            if not re.fullmatch(r'[1-9]\d*(?:; [1-9]\d*)*', values):
                raise ValueError('REACT_EXCERPT_ARM_SIZE_UNBOUND: ' + line)
            arms.append([dict(n=int(n), span=span(line)) for n in values.split('; ')])
        rows.append(dict(trial=cells[0], nct=cells[1] if cells[1].startswith('NCT') else None,
                         registration=cells[1], intervention=arms[0], comparator=arms[1],
                         group='EXCLUDED' if cells[0] == excluded[0] else 'Tocilizumab'))
    if not rows:
        raise ValueError('REACT_EXCERPT_ROWS_MISSING: ' + OUTPUT)
    return dict(sha256=SHA256, rows=rows, deaths=[],
                population=dict(state='OUTCOMES_RECORDED', span=span(populations[0])),
                evidence=dict(mode='COMMITTED_EXCERPT', document_ref=OUTPUT,
                              excerpt_sha256=digest, held_html=HELD,
                              declared_parent_sha256=SHA256, parent_bytes_verified=False))


def load(root):
    """Build input: the committed excerpt alone, independent of local acquisition."""
    return parse_excerpt((Path(root) / OUTPUT).read_bytes())


def verify_local_html(root):
    """Explicit optional verification, never called by the review build."""
    from scripts.make_react_excerpt import parse
    data = parse((Path(root) / HELD).read_bytes())
    data['evidence'] = dict(mode='HELD_HTML', document_ref=HELD,
                            sha256=data['sha256'], parent_bytes_verified=True)
    return data
