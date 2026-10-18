"""Source-derived benchmark amendments, held harm cells/debt and ledger reconciliation.

Static: endpoint locators and suppression policy. Dynamic: cells, report IDs,
hashes, debt membership and retained-record provenance. No network retrieval.
"""
import copy
import datetime
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from harness import acquisition as acq, hand_binding, verified_inputs
from harness.hcq_primary_table import read as primary_read
from build_bench_comparators import DARA,HCQ,load,save,sha


def harm_cells():
    ref='cache/'+HCQ+'/PMC7722693.xml'
    raw=(ROOT/ref).read_bytes(); text=raw.decode('utf8'); doc=ET.fromstring(raw)
    pid=doc.findtext('.//article-id[@pub-id-type="pmid"]')
    table=next(t for t in doc.iter('table-wrap') if t.get('id')=='t3')
    rows=list(table.iter('tr'))
    headers=[''.join(c.itertext()) for c in rows[0]]
    assert 'Hydroxychloroquine' in headers[1] and 'Usual-Care' in headers[2]
    ns=[int(re.search(r'N=(\d+)',s)[1]) for s in headers[1:3]]
    specs=load('topics/'+HCQ+'.json')['harm_outcomes']
    result=[]
    for label,spec in zip(('Any adverse event','Gastrointestinal disorder: diarrhea, abdominal pain, vomiting'),specs):
        tr=next(r for r in rows if ''.join(r[0].itertext())==label)
        values=[]
        for c,n in zip(list(tr)[1:3],ns):
            match=re.fullmatch(r'(\d+) \((\d+\.\d+)\)',''.join(c.itertext()))
            assert match
            event=int(match[1]); assert abs(100*event/n-float(match[2]))<.11
            values.extend((event,n))
        span=next(s for s in re.findall(r'<tr\b[^>]*>.*?</tr>',text,re.S) if label in s)
        row=dict(outcome=spec['name'],kind='extracted_counts',override=True,
                 provenance='fulltext_verified',document_ref=ref,document_sha256=sha(ref),
                 source_span=span,source=span,source_level=1,
                 **dict(zip(('ai','n1i','ci','n2i'),values)))
        assert hand_binding.bind_hand_row(spec,dict(row,id=pid))['hand_binding_state']=='BOUND'
        result.append((pid,row))
    return result


def amend(slug,cfg):
    policy=dict(date=datetime.date.today().isoformat(),kind='retrieval_and_harms',
        retrieval_consumer='harness.invalidation.assess',
        retrieval_input='/search/retrieval_class/retrieval_auditable',
        systematic_search_claim=False,
        harms_policy='Extract held arm-linked cells; refuse unbound tuples with source spans; suppress quantitative synthesis while any reporting row is not extracted.',
        harms_debt_ref='registry/benchmarks/'+slug+'_harms_debt.json')
    cfg['benchmark']['g1g2_amendment']=policy
    path=ROOT/'protocols'/f'{slug}.md'
    text=path.read_text(encoding='utf8')
    if slug==HCQ:
        primary=primary_read((ROOT/'cache'/HCQ/'PMC7665393.xml').read_bytes())
        explanation=('The bound registry counts equal the held Table 2 PRIMARY outcome `'+primary['endpoint']+
                     '`, not the narrower PCR-confirmed row. Binding rereads the primary table and abstains on any tuple mismatch; the registry title alone does not establish endpoint identity.')
        text=text.replace('This posted endpoint is explicitly confirmed infection; the benchmark permits symptoms or PCR confirmation.',explanation)
        text=text.replace('Rajasingham: randomized denominators cannot be paired with primary-analysis events excluding illness before medication. Refuse with NO_OPEN_SOURCE-for-denominator until matching primary-analysis denominators are held.',
            'Rajasingham: the earlier denominator refusal is superseded by the held posted-results/primary-table cross-check below. The primary table supports the combined dose-arm tuple; the comparator denominators are not substituted.')
        cfg['posted_results_conversion']['primary_table_crosscheck']=dict(source_ref='cache/'+HCQ+'/PMC7665393.xml',
            table='T2',endpoint=primary['endpoint'],source_sha256=sha('cache/'+HCQ+'/PMC7665393.xml'))
    heading='## G1/G2 held-source amendment'
    if heading in text: text=text.split(heading)[0].rstrip()+'\n'
    text+='\n'+heading+'\n\n'+(
        'The recorded retrieval class is consumed by `harness.invalidation.assess` through '
        '`/search/retrieval_class/retrieval_auditable`; a recorded search does not establish systematic-search completeness. '
        'The executable consumer also checks a change to unauditable retrieval. '
        'Source-bound harm cells are extracted where available. Other source-reported harms retain typed refusals and their '
        'verbatim evidence in `'+policy['harms_debt_ref']+'`; they are not evidence of harm absence. '
        'Any such row suppresses the quantitative safety panel under the existing harms gate.\n')
    path.write_text(text,encoding='utf8')
    save('topics/'+slug+'.json',cfg)


def reconcile(slug,records):
    path='cache/'+slug+'/retrieval_ledger.json'; ledger=load(path)
    old=copy.deepcopy(ledger['snapshot'])
    missing=[r for r in records['records'] if str(r['id']) not in ledger['records']]
    if missing:
        # A held import is recorded as such, never back-attributed to a historic query.
        now=datetime.datetime.now(datetime.timezone.utc).isoformat()
        sid=acq.add_source(ledger,'CONTROL_PMIDS','Held-record import; no network search: '+', '.join(str(r['id']) for r in missing),
            now,'RAN_OK',None,dict(hits=len(missing),fetched=len(missing),retained=len(missing),
                                  cap={'kind':'none','remainder':0}),[r['id'] for r in missing],False)
        acq.attach_records(ledger,sid,[r['id'] for r in missing])
        next(s for s in ledger['sources'] if s['source_id']==sid)['held_import_evidence']=dict(
            source_ref='cache/'+slug+'/records.json',sha256=sha('cache/'+slug+'/records.json'),
            record_ids=[r['id'] for r in missing])
    ledger['snapshot']['records_sha256']=acq.records_sha256(records['records'])
    ledger['reconciliation']=dict(prior_snapshot=old,kind='held_corpus_reconciliation',
                                   note='Historical query records and raw-call hashes preserved; no new search claimed.')
    assert not acq.validate(ledger,records['records']),acq.validate(ledger,records['records'])
    save(path,ledger)


def main():
    cells=harm_cells()
    for slug in (DARA,HCQ):
        cfg=load('topics/'+slug+'.json'); records=load('cache/'+slug+'/records.json')
        byid={str(r['id']):r for r in records['records']}
        rev=load('docs/reviews/'+slug+'/review.json')
        vpath='cache/'+slug+'/verified_arms.json'
        existing=load(vpath) if (ROOT/vpath).exists() else {}
        bykey={(pid,e['outcome']):e for pid,value in existing.items() for e in verified_inputs.entries(value)}
        if slug==HCQ:
            for pid,row in cells: bykey[(pid,row['outcome'])]=row
        debt=[]
        for outcome in rev['outcomes']:
            if outcome.get('kind')!='harm': continue
            for item in outcome['result'].get('harm_reporting_trials',[]):
                pid=str(item['id']).removeprefix('PMID '); key=(pid,outcome['name'])
                if (bykey.get(key) or {}).get('kind')=='extracted_counts' or item.get('extracted'): continue
                rec=byid[pid]; ref='cache/'+slug+'/records.json'
                span=rec.get('abstract') or ''
                assert span
                row=dict(outcome=outcome['name'],kind='typed_refusal',provenance='REFUSED_ON_EVIDENCE',
                    source_span=span,document_ref=ref,document_sha256=sha(ref),source_level=1,
                    reason='HELD_SOURCE_TUPLE_UNBOUND: no validated arm-linked tuple for the declared any-grade outcome. Source-reported harms remain in the debt ledger; quantitative safety synthesis is suppressed, not interpreted as absence.')
                bykey[key]=row
                debt.append(dict(id=pid,**row))
        out={}
        for (pid,_),row in bykey.items(): out.setdefault(pid,[]).append(row)
        save(vpath,out)
        save('registry/benchmarks/'+slug+'_harms_debt.json',dict(slug=slug,policy='SUPPRESS_NOT_ABSENCE',entries=debt))
        amend(slug,cfg); reconcile(slug,records)
    path=ROOT/'registry/benchmarks/BENCH_KNOWN_LIMITS.md'
    text=path.read_text(encoding='utf8')
    text=re.sub(r'^4\..*$', '4. RESOLVED: the registry-derived tuple is cross-checked against held PMC7665393 Table 2 PRIMARY outcome `PCR positive or probable COVID-19`. The mutation test now passes and requires ABSTAIN when the held row changes.',text,flags=re.M)
    text=text.replace('strict xfails preserve these unresolved limits. Production code remains frozen.',
                      'strict xfails preserve the remaining unresolved limits; the Table 2 cross-check is a passing regression test. extract.py remains frozen.')
    path.write_text(text,encoding='utf8')


if __name__=='__main__': main()
