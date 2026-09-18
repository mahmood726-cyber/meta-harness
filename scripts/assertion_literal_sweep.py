"""Conservative AST audit of literal assertions and temporal provenance.

Findings are review candidates, not proof that a claim is false. No comment-based
suppression is supported. Branch dependencies are followed through local aliases.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

WORDS = re.compile(r'\b(?:assessed|verified|checked|searched|retrieved|measured|replayed|reproduced|confirmed|located|no evidence of|was not|were not|passed|retracted|traces to|committed search|AACT dates)\b', re.I)
DATE = re.compile(r'\b\d{4}-\d{2}-\d{2}\b|T\d{2}:\d{2}:\d{2}Z')
TIME_NAME = re.compile(r'(?:^|_)(?:now|generated|run|retrieved|measured|snapshot)(?:_|$)', re.I)
STATE = re.compile(r'(?:^|_)(?:state|assessed|status|verified|decision)$')
STATUS_KEY = re.compile(r'^(?:checked|verified|assessed|state|status|replayed|reproduced|pass|passed|ok|success)$', re.I)
VERDICTS = {'TRUE-DEFECT', 'DEFENSIBLE-CONDITIONED', 'DESCRIPTIVE-METHOD', 'RETRACTION-MARKER', 'FALSE-POSITIVE'}


def finding_key(f):
    return '::'.join(f[k] for k in ('file', 'function', 'literal_sha256'))


def adjudicate(findings, entries):
    for key, entry in entries.items():
        if (key != finding_key(entry) or entry.get('verdict') not in VERDICTS
                or any(not isinstance(entry.get(k), str) or not entry[k].strip()
                       for k in ('reason', 'by', 'when_utc'))):
            raise ValueError('INVALID_ADJUDICATION: ' + key)
    for f in findings:
        if f['kind'] == 'INFO_CLOCK':
            f['verdict'] = 'INVENTORY-ONLY'
            continue
        entry = entries.get(finding_key(f))
        if f['kind'] == 'UNSUPPORTED_TEMPLATE' and entry and entry['verdict'] != 'TRUE-DEFECT':
            raise ValueError('UNSUPPORTED_TEMPLATE cannot be cleared without language-aware analysis')
        f['verdict'] = entry['verdict'] if entry else 'UNADJUDICATED'
        if entry:
            f['adjudication'] = entry
    return findings


def blockers(report):
    return [f for f in report['findings'] if f.get('verdict', 'UNADJUDICATED')
            in {'UNADJUDICATED', 'TRUE-DEFECT'} and f['kind'] != 'INFO_CLOCK']


def scan_source(source: str, filename: str) -> list[dict]:
    tree = ast.parse(source, filename=filename)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    def ancestors(node):
        while node in parents:
            node = parents[node]
            yield node
    def scope(node):
        return next((p for p in ancestors(node) if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef))), tree)
    assignments = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    assignments.setdefault((scope(node), target.id), []).append(node.value)
    surface_names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Return):
            surface_names.setdefault(scope(node), set()).update(
                p.id for p in ast.walk(node) if isinstance(p, ast.Name))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {'dump', 'dumps', 'write', 'write_text', 'render'}:
            surface_names.setdefault(scope(node), set()).update(
                p.id for arg in node.args for p in ast.walk(arg) if isinstance(p, ast.Name))
    for owner, names in surface_names.items():
        changed = True
        while changed:
            previous = set(names)
            for name in previous:
                for value in assignments.get((owner, name), []):
                    if value:
                        names.update(p.id for p in ast.walk(value) if isinstance(p, ast.Name))
            changed = names != previous
    def reads_state(node, owner, seen=None):
        seen = set() if seen is None else seen
        for part in ast.walk(node):
            if isinstance(part, ast.Constant) and isinstance(part.value, str) and STATE.search(part.value):
                parent = parents.get(part)
                if isinstance(parent, ast.Subscript) and parent.slice is part:
                    return True
                if (isinstance(parent, ast.Call) and isinstance(parent.func, ast.Attribute)
                        and parent.func.attr in {'get', 'pop'} and parent.args and parent.args[0] is part):
                    return True
            if isinstance(part, ast.Attribute) and STATE.search(part.attr):
                return True
            if isinstance(part, ast.Name) and part.id not in seen:
                seen.add(part.id)
                if any(reads_state(v, owner, seen) for v in assignments.get((owner, part.id), []) if v):
                    return True
        return False
    html_scopes = {scope(n) for n in ast.walk(tree)
                   if isinstance(n, ast.Constant) and isinstance(n.value, str) and '<' in n.value}
    findings = []
    # Coverage counters are execution assertions even when their keys are labels.
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if not (isinstance(key, ast.Constant) and key.value in {'surfaces_checked', 'claims_checked'}):
                continue
            literal = ast.unparse(key) + ': ' + ast.unparse(value)
            findings.append(dict(file=filename, line=key.lineno,
                function=getattr(scope(node), 'name', '<module>'), literal=literal,
                literal_sha256=hashlib.sha256(literal.encode()).hexdigest(),
                kind='COVERAGE_ASSERTION', reason='reported scan coverage requires successful surface execution'))
    for node in ast.walk(tree):
        chain = list(ancestors(node))
        owner = scope(node)
        function = getattr(owner, 'name', '<module>')
        status_target = None
        parent = parents.get(node)
        if isinstance(node, ast.Constant) and (node.value is True or isinstance(node.value, str)):
            if isinstance(parent, ast.Dict):
                status_target = next((key.value for key, value in zip(parent.keys, parent.values)
                                      if value is node and isinstance(key, ast.Constant)
                                      and isinstance(key.value, str) and STATUS_KEY.fullmatch(key.value)), None)
            if isinstance(parent, (ast.Assign, ast.AnnAssign)) and parent.value is node:
                for target in (parent.targets if isinstance(parent, ast.Assign) else [parent.target]):
                    key = target.attr if isinstance(target, ast.Attribute) else (
                        target.slice.value if isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant) else '')
                    if isinstance(key, str) and STATUS_KEY.fullmatch(key):
                        status_target = key
        status_surface = any(isinstance(p, ast.Return) for p in chain)
        status_surface |= any(isinstance(p, ast.Call) and isinstance(p.func, ast.Attribute)
                              and p.func.attr in {'dump', 'dumps', 'write', 'write_text', 'render'} for p in chain)
        for statement in chain:
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                status_surface |= any(part.id in surface_names.get(owner, set())
                                      for target in targets for part in ast.walk(target) if isinstance(part, ast.Name))
        if status_target and status_surface:
            literal = str(node.value)
            conditioned = any(reads_state(p.test, owner) for p in chain if isinstance(p, (ast.If, ast.IfExp)))
            kind = 'CONDITIONED' if conditioned else 'STATUS_CONSTANT'
            reason = f'constant status target {status_target!r} reaches a return/serialization surface; ' + (
                'enclosing branch reads a state field (review relevance to this claim)' if conditioned else 'no enclosing branch reads a state field')
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            literal = node.value
            # Docstrings, dictionary keys, field lookups, labels and regexes are not assertions.
            if isinstance(parents.get(node), ast.Expr):
                continue
            parent = parents.get(node)
            if isinstance(parent, ast.Dict) and node in parent.keys:
                continue
            if isinstance(parent, ast.Subscript) or (isinstance(parent, ast.Call) and isinstance(parent.func, ast.Attribute) and ((parent.func.attr in {'get', 'pop'} and parent.args and node is parent.args[0]) or parent.func.attr in {'search', 'compile', 'findall'})):
                continue
            targets = []
            for p in chain:
                if isinstance(p, ast.Dict):
                    for key, value in zip(p.keys, p.values):
                        if key and (value is node or value in chain):
                            targets.append(ast.unparse(key))
                if isinstance(p, (ast.Assign, ast.AnnAssign)):
                    targets.extend(ast.unparse(t) for t in (p.targets if isinstance(p, ast.Assign) else [p.target]))
                    break
            if DATE.match(literal) and any(TIME_NAME.search(t.strip("'\"")) for t in targets):
                kind, reason = 'FIXED_TIME', 'date literal assigned to temporal provenance target: ' + ', '.join(targets)
            elif WORDS.search(literal) and (len(literal.split()) >= 4 or '<' in literal):
                if any(isinstance(p, (ast.Raise, ast.Assert)) for p in chain):
                    continue
                if any(isinstance(p, ast.Call) and isinstance(p.func, ast.Name) and p.func.id == 'print' for p in chain):
                    continue
                # Surface candidates: HTML, returned prose, or prose carried in objects.
                surface = '<' in literal or any(isinstance(p, (ast.Return, ast.Dict, ast.JoinedStr)) for p in chain)
                surface |= any(isinstance(p, ast.Call) and isinstance(p.func, ast.Attribute) and p.func.attr in {'append', 'write', 'write_text'} for p in chain)
                surface |= function.startswith(('render', '_render'))
                # Table descriptors carried through tuple-unpacking loops into HTML.
                surface |= (any(isinstance(p, (ast.List, ast.Tuple)) for p in chain)
                            and owner in html_scopes)
                surface |= any(t in surface_names.get(owner, set()) for t in targets)
                if not surface:
                    continue
                guards = [p.test for p in chain if isinstance(p, (ast.If, ast.IfExp))]
                conditioned = any(reads_state(g, owner) for g in guards)
                kind = 'CONDITIONED' if conditioned else 'ASSERTION'
                reason = ('enclosing branch reads a state field (review relevance to this claim)' if conditioned else 'no enclosing branch reads a state field; surface-bound prose candidate')
            else:
                continue
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {'now', 'utcnow'} and 'datetime' in ast.unparse(node.func):
            literal = ast.unparse(node)
            kind = 'INFO_CLOCK'
            reason = ('live clock candidate in a file exposing --now; check pinned-build reachability'
                      if '--now' in source else
                      'live clock candidate; no file-local --now contract established')
        else:
            continue
        findings.append(dict(file=filename, line=node.lineno, function=function, literal=literal,
                             literal_sha256=hashlib.sha256(literal.encode()).hexdigest(),
                             kind=kind, reason=reason))
    return sorted(findings, key=lambda f: (f['file'], f['line'], f['literal']))


def sweep(root: Path) -> dict:
    files = sorted(p for folder in ('harness', 'scripts') for p in (root / folder).rglob('*.py'))
    findings = [f for p in files for f in scan_source(p.read_text(encoding='utf-8-sig'), p.relative_to(root).as_posix())]
    templates = sorted(p for folder in ('harness', 'scripts', 'templates')
                       for p in (root / folder).rglob('*') if p.suffix in {'.html', '.j2', '.jinja', '.jinja2'})
    # This repository uses inline Python templates. A newly added external template
    # must not silently escape the audit: refuse until its language is supported.
    for p in templates:
        literal = p.read_text(encoding='utf-8-sig')
        findings.append(dict(file=p.relative_to(root).as_posix(), line=1, function='<template>',
                             literal=literal, literal_sha256=hashlib.sha256(literal.encode()).hexdigest(),
                             kind='UNSUPPORTED_TEMPLATE', reason='external template requires language-aware condition analysis'))
    registry = root / 'registry/assertion_literal_adjudications.json'
    raw = registry.read_text(encoding='utf-8') if registry.exists() else '{}'
    entries = json.loads(raw).get('adjudications', {})
    adjudicate(findings, entries)
    present = {finding_key(f) for f in findings}
    return {'schema_version': 2, 'files_scanned': len(files), 'external_templates': len(templates),
            'adjudications_sha256': hashlib.sha256(raw.encode()).hexdigest(),
            'counts_by_class': dict(sorted(Counter(f['kind'] for f in findings).items())),
            'counts_by_verdict': dict(sorted(Counter(f['verdict'] for f in findings if f['kind'] != 'INFO_CLOCK').items())),
            'resolved_adjudications': [dict(e, current_presence=False) for key, e in sorted(entries.items()) if key not in present],
            'source_sha256': {p.relative_to(root).as_posix(): hashlib.sha256(p.read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest()
                              for p in files + templates}, 'findings': findings}


def describe(f):
    return f"{f['file']}:{f['line']} [{f['kind']}] {f['function']}: {f['literal']!r} — {f['reason']}"


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = {'findings': scan_source(args.source.read_text(encoding='utf-8-sig'), args.source.as_posix())} if args.source else sweep(args.root)
    if args.write:
        target = args.root / 'docs/assertion_literal_sweep.json'
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        target.with_suffix('.json.html').write_text('<!doctype html><meta charset="utf-8"><title>Assertion literal sweep</title><h1>Assertion literal sweep</h1><p>AST candidates require source review. CONDITIONED does not establish truth.</p><pre>' + html.escape(json.dumps(report, indent=2, ensure_ascii=False)) + '</pre>\n', encoding='utf-8')
    for finding in report['findings']:
        print(describe(finding))
    return int(bool(blockers(report)))


if __name__ == '__main__':
    raise SystemExit(main())
