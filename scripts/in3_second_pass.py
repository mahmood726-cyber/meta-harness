"""Source spans, numerical transcriptions, registry links and unchanged membership."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from harness.verified_inputs import load

def main():
    out=ROOT/'outputs/handover/in3'
    ds=json.loads((out/'decisions.json').read_text(encoding='utf-8'))
    checks=[]
    for d in ds:
        e=d['entry']
        recs=json.loads((ROOT/f"cache/{d['slug']}/records.json").read_text(encoding='utf-8'))['records']
        rec=next(r for r in recs if str(r['id'])==d['pmid'])
        if e['document_ref'].endswith('records.json'):
            assert e['source_span'] in rec['abstract'],d
        else:
            assert e['source_span'] in (ROOT/e['document_ref']).read_text(encoding='utf-8'),d
            assert any(n in e['source_span'] and n in json.dumps(rec) for n in e['registry_ncts']),d
        for key in ('ai','ci','effect','ci_low','ci_high'):
            if key in e:
                numbers=[float(x) for x in re.findall(r'\d+(?:\.\d+)?',e['source_span'])]
                assert e[key] in numbers,(d['pmid'],key)
        if e.get('denominator_source'):
            denom=e['denominator_source']
            assert denom['nct'] in json.dumps(rec)
            text=(ROOT/denom['document_ref']).read_text(encoding='utf-8')
            for row in denom['rows']:
                assert row['id']+'|'+row['nct_id']+'|' in text
            assert round(100*e['ai']/e['n1i'],1)==27.2
            assert round(100*e['ci']/e['n2i'],1)==23.5
        if e.get('effect') is not None:
            assert 0<e['ci_low']<e['effect']<e['ci_high']
        checks.append(dict(slug=d['slug'],pmid=d['pmid'],outcome=d['outcome'],kind=e['kind'],span_verbatim=True))
    for slug in sorted({d['slug'] for d in ds}):
        load(slug)
    fields=('id','ai','n1i','ci','n2i','effect','ci_low','ci_high','scale','mean1','mean2','sd1','sd2','nc1','nc2')
    pages=[]
    for p in sorted((ROOT/'docs/reviews').glob('*/review.json')):
        rel=p.relative_to(ROOT).as_posix()
        before=json.loads(subprocess.check_output(['git','show',f'f5f8180076873a48e0d2d83b7bb7c1a46ddb87df:{rel}'],cwd=ROOT))
        after=json.loads(p.read_text(encoding='utf-8'))
        assert before['screening']['records']==after['screening']['records'],p
        a=next(o for o in before['outcomes'] if o.get('primary'))
        b=next(o for o in after['outcomes'] if o.get('primary'))
        vals=lambda o:[{k:t.get(k) for k in fields} for t in o.get('trials',[])]
        assert vals(a)==vals(b),p
        pages.append(p.parent.name)
    result=dict(source_checks=checks,membership_and_primary_unchanged=pages)
    (out/'second_pass.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'{len(checks)} of {len(ds)} decisions validated; {len(pages)} of {len(pages)} live pages retain screening and primary values.')

if __name__=='__main__':
    main()
