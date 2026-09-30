"""Document plants and offline census; synthetic fixture values are not evidence."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import types

import pytest
from harness import proposal_gate as gate
import runpy
_helpers = runpy.run_path(str(Path(__file__).with_name("test_proposal_gate.py")))
install, field = _helpers["install"], _helpers["field"]


def registered(root, media='text/html'):
    p = install(root)
    raw = ('<p>Outcome: <b>Mortality</b> at 28 days.</p>' if media == 'text/html'
           else '<article><p>Outcome: <bold>Mortality</bold> at 28 days.</p></article>')
    ref = 'evidence/held.' + ('html' if media == 'text/html' else 'xml')
    (root / 'evidence').mkdir()
    (root / ref).write_text(raw, encoding='utf-8')
    p.update(document_ref=ref, document_sha256=hashlib.sha256(raw.encode()).hexdigest())
    p['pooled'] = dict.fromkeys(gate.POOLED); p['pooled']['span'] = ''
    p['trials'] = []
    row = dict(slug=p['slug'], comparator_pmid=p['comparator_pmid'], document_ref=ref,
               sha256=p['document_sha256'], media_type=media,
               normaliser=gate.NORMALISERS[media], licence='Synthetic test fixture')
    path = root / gate.DOCUMENT_REGISTRY
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(version=1, documents=[row])), encoding='utf-8')
    return p, path


def mutate(root, p, registry, kind):
    if kind == 'attribute':
        raw = '<p data-hidden="Secret">Outcome: Mortality at 28 days.</p>'
        (root / p['document_ref']).write_text(raw, encoding='utf-8')
        p['document_sha256'] = hashlib.sha256(raw.encode()).hexdigest()
        data = json.loads(registry.read_text()); data['documents'][0]['sha256'] = p['document_sha256']
        registry.write_text(json.dumps(data), encoding='utf-8')
        p['primary_scope'].update(outcome_as_printed='Secret', timepoint_as_printed=None, span='Secret')
    elif kind == 'sha':
        (root / p['document_ref']).write_text('changed', encoding='utf-8')
    elif kind == 'unregistered':
        registry.write_text('{"version":1,"documents":[]}', encoding='utf-8')
    elif kind == 'missing':
        (root / p['document_ref']).unlink()
    elif kind == 'identity':
        data=json.loads(registry.read_text());data['documents'][0]['comparator_pmid']='99999999'
        registry.write_text(json.dumps(data),encoding='utf-8')


@pytest.mark.parametrize('kind,reason', [('attribute','REFUSED_SPAN_NOT_HELD'),
    ('sha','REFUSED_SHA256_MISMATCH'), ('unregistered','REFUSED_DOCUMENT_UNREGISTERED'),
    ('missing','REFUSED_REGISTERED_DOCUMENT_MISSING'),('identity','REFUSED_REGISTERED_COMPARATOR_IDENTITY')])
def test_refusal_plants(tmp_path, kind, reason):
    p, registry = registered(tmp_path); mutate(tmp_path,p,registry,kind)
    got=gate.verify(p,tmp_path)
    assert (got['reason'] or field(got,'primary_scope.outcome_as_printed')['reason']) == reason


@pytest.mark.parametrize('media', ['text/html','application/jats+xml'])
def test_correct_document_and_markup_spans(tmp_path,media):
    p,_=registered(tmp_path,media)
    assert gate.verify(p,tmp_path)['status']=='accepted'
    p['primary_scope']['span']='<p>Outcome: <b>Mortality</b> at 28 days.</p>'
    p['primary_scope']['field_spans']={'outcome_as_printed':'<i>Mortality</i>'}
    assert gate.verify(p,tmp_path)['status']=='accepted'


@pytest.mark.parametrize('key,value,reason', [('normaliser','unknown','REFUSED_NORMALISER'),
 ('media_type','image/png','REFUSED_MEDIA_TYPE'),('licence','','REFUSED_DOCUMENT_LICENCE_MISSING'),
 ('sha256','bad','REFUSED_REGISTERED_SHA256_INVALID')])
def test_registry_metadata(tmp_path,key,value,reason):
    p,path=registered(tmp_path);data=json.loads(path.read_text());data['documents'][0][key]=value
    path.write_text(json.dumps(data),encoding='utf-8')
    assert gate.verify(p,tmp_path)['reason']==reason


def test_xml_entities_fail_closed_and_external_doctype_not_fetched():
    with pytest.raises(ValueError,match='REFUSED_XML_DECLARATION'):
        gate.normalise_document('<!DOCTYPE x [<!ENTITY x "value">]><p>&x;</p>','application/jats+xml')
    assert gate.normalise_document('<!DOCTYPE article SYSTEM "https://invalid.invalid/a"><p>A &amp; B</p>','application/jats+xml')=='A & B'
    with pytest.raises(ValueError,match='REFUSED_XML_PARSE'):
        gate.normalise_document('<p>broken','application/jats+xml')


HTML_CASES = [
    ('<p>a<!-- hidden -->b</p>', 'a b'),
    ('<template>a<b>b</b>c</template>d', 'd'),
    ('<script>secret</script><style>hidden</style><p>Visible</p>', 'Visible'),
    ('<ruby>A<rt>B<b>C</b></rt><rp>(</rp></ruby>', 'A'),
    ('<p>a<![CDATA[b]]>c</p>', 'a b c'),
    ('<p>a<?pi x?>b</p>', 'a b'),
    ('<p>a</unknown>b</p>', 'a b'),
    ('<p>a<br>b<img src="x">c</p>', 'a b c'),
    ('<p data-hidden="Secret"> A&nbsp;B &amp; &#65; <b>C</b></p>', 'A B & A C'),
]


@pytest.mark.parametrize('raw,expected', HTML_CASES)
def test_stdlib_text_semantics(raw, expected):
    assert gate.normalise_document(raw, 'text/html') == expected


@pytest.mark.parametrize('raw,expected', HTML_CASES)
def test_optional_bs4_crosscheck(raw, expected):
    bs4 = pytest.importorskip('bs4', reason='optional BeautifulSoup equivalence cross-check',
                             exc_type=ImportError)
    assert gate.normalise_document(raw, 'text/html') == gate.flat(
        bs4.BeautifulSoup(raw, 'html.parser').get_text(' ', strip=True)) == expected


def test_bs4_absence_plant():
    code = '''
import importlib.abc
import sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'bs4' or fullname.startswith('bs4.'):
            raise ImportError('PLANT_BS4_UNAVAILABLE')
sys.meta_path.insert(0, Block())
from harness import proposal_gate as gate
assert gate.normalise_document('<p>A &amp; B</p>', 'text/html') == 'A & B'
assert gate._table_rows('<table><tr><td>A</td></tr></table>', 'text/html')[0][0]['span'] == 'A'
'''
    result = subprocess.run([__import__('sys').executable, '-c', code], cwd=gate.ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def rebuild_toci():
    """Execute only the copied lane's pure builder functions; no write entrypoint."""
    path=gate.ROOT/'scripts/g1_toci_comparator.py'
    tree=ast.parse(path.read_text(encoding='utf-8'))
    names={'one','text','normalized','extract','proposal'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    ns=dict(gate=gate,re=re,hashlib=hashlib,
            SLUG='tocilizumab-covid19-mortality',HELD='evidence/acquisition_cascade/held/WHO-REACT/PMC8261689.local.html')
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
    raw=(gate.ROOT/ns['HELD']).read_bytes()
    return ns['proposal'](ns['extract'](raw),raw)


def audit():
    base=types.ModuleType('base_gate');base.__file__=str(gate.ROOT/'harness/proposal_gate.py')
    source=subprocess.check_output(['git','--no-optional-locks','show','b0ae05a7cf440048ef07338ab2cf756dccf3241a:harness/proposal_gate.py'],cwd=gate.ROOT).decode('utf-8')
    exec(compile(source,base.__file__,'exec'),base.__dict__)
    plants=[]
    for kind in ('correct','attribute','sha','unregistered','missing','identity'):
        with tempfile.TemporaryDirectory(dir=gate.ROOT/'.tmp') as temp:
            root=Path(temp);p,path=registered(root)
            mutate(root,p,path,kind)
            before=base.verify(p,root);after=gate.verify(p,root)
            plants.append(dict(plant=kind,before=before['reason'],after=after['reason'] or field(after,'primary_scope.outcome_as_printed')))
    proposal=rebuild_toci();native=gate.verify(proposal)
    documents=json.loads((gate.ROOT/gate.DOCUMENT_REGISTRY).read_text())['documents']
    topics=sorted((gate.ROOT/'topics').glob('*.json'))
    coverage=[]
    for path in topics:
        topic=json.loads(path.read_text(encoding='utf-8'))
        rows=[r for r in documents if r['slug']==path.stem]
        for row in rows:
            p=deepcopy(proposal);p.update(slug=path.stem,comparator_pmid=str(topic['comparator_pmid']),document_ref=row['document_ref'],document_sha256=row['sha256'])
            try:
                gate._source(p,gate.ROOT)
                state='accepted'
            except (ValueError,OSError) as exc: state=str(exc)
            coverage.append(dict(topic=path.stem,document_ref=row['document_ref'],state=state))
    def count(items,N):return dict(n=len(items),N=N,n_of_N=f'{len(items)} of {N}',items=items)
    return dict(plants=plants,proposal_origin='Rebuilt in memory: copied proposal.json absent',
        base_toci=base.verify(proposal)['reason'],
        native=count([f['path'] for f in native['fields'] if f['status']=='accepted'],len(native['fields'])),
        proposed_fields=sum(f['status']!='not_proposed' for f in native['fields']),
        rejections=[f for f in native['fields'] if f['status']=='rejected'],
        census=dict(field_rules={reason: count([f['path'] for f in native['fields'] if f['reason']==reason], sum(f['status']!='not_proposed' for f in native['fields'])) for reason in sorted({f['reason'] for f in native['fields'] if f['reason']})},
                    registered_topics=count(sorted({r['topic'] for r in coverage}),len(topics)),
                    document_refusals=count([r for r in coverage if r['state']!='accepted'],len(coverage)),
                    documents=coverage))


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
