"""Offline filename census. Rules are ordered, case-insensitive, basename-only.

Naming table (first matching row wins):
| Pattern | Class |
| Tab/Table + number with ESM/supplement marker; Table S; eTable; marked -Tn- | SUPPLEMENT_TABLE_IMAGE |
| Fig/Figure + number with ESM/supplement marker; Figure S; eFigure | SUPPLEMENT_FIGURE_IMAGE |
| mmc*; Data_Sheet* (including page suffixes) | SUPPLEMENT_FIGURE_IMAGE |
| *_Fign_HTML; pone.*.g00n; CD*-fig-*; journal-*-f00n; *-Fn; fig1; f0015 | ARTICLE_FIGURE |
| Everything else (including unmarked tables) | UNKNOWN_IMAGE |

These classes describe names, not verified image contents or recoverable data.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re


IMAGE_FORMATS = {'jpg', 'jpeg', 'gif', 'png', 'tif', 'tiff', 'bmp', 'webp', 'svg'}
RULE_TABLE = __doc__.split('Naming table (first matching row wins):\n')[1].split('\n\n')[0]


def basename(name):
    return name.replace('\\', '/').rsplit('/', 1)[-1].lower()


def stem(name):
    return re.sub(r'\.(?:jpg|jpeg|gif|png|tif|tiff|bmp|webp|svg)$', '', basename(name))


def classify(name):
    s = stem(name)
    marked = bool(re.search(r'esm|supplement', s))
    if (re.search(r'(?:^|[ _.-])(?:etable\s*\d+|table[ _-]*s\d+)', s)
            or marked and re.search(r'(?:tab(?:le)?[ _-]*\d+|(?:^|-)t\d+(?:-|$))', s)):
        return 'SUPPLEMENT_TABLE_IMAGE', 'supplement_table'
    if (re.search(r'(?:^|[ _.-])(?:efigure\s*\d+|fig(?:ure)?[ _-]*s\d+)', s)
            or marked and re.search(r'(?:fig(?:ure)?|f)[ _-]*\d+', s)):
        return 'SUPPLEMENT_FIGURE_IMAGE', 'supplement_figure'
    if re.match(r'(?:mmc|data[ _-]*sheet)', s):
        return 'SUPPLEMENT_FIGURE_IMAGE', 'supplement_container'
    if not marked and figure_number(s) is not None:
        return 'ARTICLE_FIGURE', 'article_figure'
    return 'UNKNOWN_IMAGE', 'unmatched'


def figure_number(s):
    m = re.search(r'(?:^|[_.-])(?:fig(?:ure)?|f|g)[ _-]*0*(\d+)(?=$|[_.-])', s)
    return str(int(m[1])) if m else None


def figure_key(name):
    s = stem(name)
    kind, _ = classify(name)
    if kind == 'ARTICLE_FIGURE':
        return 'article:' + figure_number(s)
    # Never merge supplement labels with article numbers or different PDF pages.
    if kind == 'SUPPLEMENT_FIGURE_IMAGE' and not re.match(r'(?:mmc|data[ _-]*sheet)', s):
        m = re.search(r'(?:efigure|fig(?:ure)?[ _-]*s|fig(?:ure)?)[ _-]*0*(\d+)', s)
        if m:
            return 'supplement:' + str(int(m[1]))
    return 'exact:' + s


def parse_reads(markdown):
    reads = set()
    for line in markdown.splitlines():
        cells = [c.strip() for c in line.split('|')]
        if len(cells) >= 5 and re.fullmatch(r'PMID \d+', cells[2]):
            reads.add((cells[2].split()[1], figure_key(cells[3])))
    return reads


def already_read(meta, name, reads):
    return (str(meta), figure_key(name)) in reads


def licence_gate(value):
    return ('OPEN_FOR_MODEL' if isinstance(value, str) and value.strip().lower()
            in {'cc-by', 'cc0', 'cc by', 'public domain'} else 'DETERMINISTIC_ONLY')


def ratio(n, total):
    return {'n': n, 'N': total}


def summarize(metas, total_metas, missing):
    stages = [metas]
    stages.append([m for m in stages[-1] if m['supplement_images']])
    stages.append([m for m in stages[-1] if m['licence_gate'] == 'OPEN_FOR_MODEL'])
    stages.append([m for m in stages[-1] if m['missing_trials']])
    stages.append([m for m in stages[-1] if m['unread_supplement_images']])
    labels = ['with_images', 'with_supplement_images', 'open_for_model', 'citing_missing_trials', 'with_unread_supplement_images']
    funnel = {label: ratio(len(stage), total_metas if i == 0 else len(stages[i-1]))
              for i, (label, stage) in enumerate(zip(labels, stages))}
    affected = {(m['topic'], t) for m in stages[-1] for t in m['missing_trials']}
    files = [f for m in metas for f in m['images']]
    eligible = [f for m in stages[3] for f in m['images'] if f['class'].startswith('SUPPLEMENT_')]
    return {'funnel': funnel, 'images': ratio(len(files), len(files)),
            'classes': {k: ratio(sum(f['class'] == k for f in files), len(files)) for k in
                        ['ARTICLE_FIGURE', 'SUPPLEMENT_TABLE_IMAGE', 'SUPPLEMENT_FIGURE_IMAGE', 'UNKNOWN_IMAGE']},
            'already_read_images': ratio(sum(f['already_read'] for f in files), len(files)),
            'eligible_unread_supplement_images': ratio(sum(not f['already_read'] for f in eligible), len(eligible)),
            'trials_affected': ratio(len(affected), len(missing)),
            'affected_trial_labels': [{'topic': t, 'trial': v} for t, v in sorted(affected)]}


def census(topics, reads):
    metas, unknown = [], []
    missing_all, summaries = set(), {}
    total = 0
    for topic, data in sorted(topics.items()):
        by_meta = defaultdict(set)
        for a in data['attempts']:
            if not isinstance(a['trial'], str) or not a['trial'].strip():
                raise ValueError('Invalid trial label')
            by_meta[str(a['meta'])].add(a['trial'])
        missing = {(topic, t) for ts in by_meta.values() for t in ts}
        missing_all |= missing
        current = []
        total += len(data['metas'])
        for pmid, meta in sorted(data['metas'].items()):
            if not re.fullmatch(r'\d+', pmid):
                raise ValueError('Invalid source PMID')
            images = []
            for source in sorted(meta.get('files', []), key=lambda f: f['file']):
                if source.get('skipped') != 'image (no OCR)' and str(source.get('format', '')).lower() not in IMAGE_FORMATS:
                    continue
                kind, rule = classify(source['file'])
                item = dict(source, **{'class': kind, 'rule': rule,
                                      'already_read': already_read(pmid, source['file'], reads)})
                item['read_state'] = 'ALREADY_READ' if item['already_read'] else 'NOT_RECORDED_READ'
                images.append(item)
                if kind == 'UNKNOWN_IMAGE':
                    unknown.append({'topic': topic, 'meta': pmid, 'file': source['file']})
            if images:
                current.append({'topic': topic, 'meta': pmid, 'licence': meta.get('licence'),
                                'licence_gate': licence_gate(meta.get('licence')), 'images': images,
                                'missing_trials': sorted(by_meta[pmid]),
                                'supplement_images': sum(f['class'].startswith('SUPPLEMENT_') for f in images),
                                'unread_supplement_images': sum(f['class'].startswith('SUPPLEMENT_') and not f['already_read'] for f in images)})
        metas.extend(current)
        summaries[topic] = summarize(current, len(data['metas']), missing)
    return {'scope': 'Overall counts use topic-meta pairs and topic-trial labels; no cross-topic identity inference. Missing trials are distinct labels in supplied attempts, not a complete tracker universe.',
            'topics': summaries, 'overall': summarize(metas, total, missing_all), 'metas': metas,
            'unknown_files': unknown,
            'unknown_patterns': dict(sorted(Counter(re.sub(r'\d+', '<n>', basename(f['file'])) for f in unknown).items()))}


def render(result):
    lines = ['# Image census', '', result['scope'], '',
             'Filename classifications do not establish per-trial contents. No image/model/OCR reads or network calls.',
             'ALREADY_READ matches PMID and normalized figure label across topics, including refused readings; article and supplement labels stay separate.',
             'Image records count formats separately. Funnel cells are n of previous-stage N; final meta stage requires at least one unread supplement image.', '', RULE_TABLE, '',
             '| Topic | Images metas / all metas | Supplement / image metas | Open / supplement metas | Missing-trial / open metas | Unread / relevant metas | Unread images / eligible supplement images | Affected / attempts trials |',
             '|---|---|---|---|---|---|---|---|']
    fmt = lambda v: f"{v['n']} of {v['N']}"
    for topic, summary in [('OVERALL', result['overall']), *result['topics'].items()]:
        vals = [*summary['funnel'].values(), summary['eligible_unread_supplement_images'], summary['trials_affected']]
        lines.append('| ' + topic + ' | ' + ' | '.join(map(fmt, vals)) + ' |')
    lines += ['', '## Image classes and read coverage', '']
    for topic, summary in [('OVERALL', result['overall']), *result['topics'].items()]:
        lines.append(f"- {topic}: " + '; '.join(k + ': ' + fmt(v) for k, v in summary['classes'].items()) + '; ALREADY_READ: ' + fmt(summary['already_read_images']))
    lines += ['', '## Missing trials by image-bearing meta', '']
    for m in result['metas']:
        lines.append(f"- {m['topic']} / PMID {m['meta']} ({m['licence_gate']}): " + ('; '.join(m['missing_trials']) or 'No trial in attempts'))
    lines += ['', '## Unknown patterns (digit runs replaced by <n>; no inferred classification)', '']
    for pattern, count in result['unknown_patterns'].items():
        lines.append(f"- `{pattern}`: {count} of {len(result['unknown_files'])} unknown image records")
    lines += ['', '## Every unknown file', '']
    for f in result['unknown_files']:
        lines.append(f"- {f['topic']} / PMID {f['meta']}: `{f['file']}`")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=Path('outputs/k_gap/registry_fill/phase4_supplements'))
    parser.add_argument('--reader', type=Path, default=Path('outputs/k_gap/G1_FOREST_READER.md'))
    parser.add_argument('--output', type=Path, default=Path('outputs/k_gap/image_census'))
    args = parser.parse_args()
    files = sorted(args.inputs.glob('*.json'))
    if not files:
        raise ValueError('No source records')
    topics = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in files}
    result = census(topics, parse_reads(args.reader.read_text(encoding='utf-8')))
    result['source_sha256'] = {p.as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in [*files, args.reader]}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'IMAGE_CENSUS.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (args.output / 'IMAGE_CENSUS.md').write_text(render(result), encoding='utf-8')
    print(json.dumps(result['overall'], indent=2))


if __name__ == '__main__':
    main()
