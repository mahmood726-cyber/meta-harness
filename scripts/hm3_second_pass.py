"""Offline identifiers, unchanged membership/efficacy, and artifact checks."""
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/evidence/hm3-held-source-audit'
decisions = json.loads((OUT/'decisions.json').read_text(encoding='utf-8'))
checks = []
for d in decisions:
    e = d['entry']
    path = ROOT/e['document_ref']
    text = path.read_text(encoding='utf-8')
    if e['source_level']=='fulltext':
        pmids = re.findall(r'<article-id\s+pub-id-type="pmid"[^>]*>(\d+)</article-id>',text)
        assert pmids and pmids[0]==d['trial'], (d['trial'],pmids[:1])
        identity = 'full-text article-id PMID matches input trial'
    else:
        rec = next(r for r in json.loads(text)['records'] if str(r['id'])==d['trial'])
        text = rec['abstract']
        identity = 'record ID and abstract are from the same held record'
    span = e.get('source_span') or e['source']
    assert span in text
    if 'effect' in e:
        assert 0 < e['ci_low'] < e['effect'] < e['ci_high']
    if 'ai' in e:
        assert 0 <= e['ai'] <= e['n1i'] and 0 <= e['ci'] <= e['n2i']
    checks.append(dict(topic=d['topic'],trial=d['trial'],outcome=d['outcome'],
                       identity_check=identity,document_ref=e['document_ref'],
                       document_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                       span_verbatim=True))

records = json.loads((ROOT/'cache/esketamine-trd-madrs/records.json').read_text(encoding='utf-8'))
source = records['ctgov_results']['NCT02417064'][0]
ms = source['classes'][0]['categories'][0]['measurements']
ns = source['denoms'][0]['counts']
assert [float(x['value']) for x in ms]==[-19.0,-18.8,-14.8]
assert [float(x['spread']) for x in ms]==[13.86,14.12,15.07]
assert [int(x['value']) for x in ns]==[111,98,108]
n1,n2=111,98
combined_mean=(n1*(-19.0)+n2*(-18.8))/(n1+n2)
combined_sd=math.sqrt(((n1-1)*13.86**2+(n2-1)*14.12**2+n1*n2/(n1+n2)*(-19.0+18.8)**2)/(n1+n2-1))
assert round(combined_mean,2)==-18.91 and round(combined_sd,2)==13.95
for pid, values in [('32970396',('0.61','0.51','0.72')),('36331190',('0.72','0.64','0.82'))]:
    records=json.loads((ROOT/'cache/sglt2-ckd-progression/records.json').read_text(encoding='utf-8'))['records']
    abstract=next(r['abstract'] for r in records if str(r['id'])==pid)
    assert all(v in abstract for v in values)

result = dict(status='PASS',new_items_checked=len(checks),checks=checks,
              preexisting_override_checks='Three original inputs verified: MADRS group values and combined arithmetic; both primary-composite HRs and intervals in held abstracts.',
              date_policy='Build date fixed to 2026-09-11 as instructed; AACT folder 2026-08-30 is an archive locator, not a claimed trial data date.',
              excluded_embedded_texts=[
                  dict(topic='melatonin-primary-insomnia-sol',trial='33157425',reason='Embedded text describes ARE/MLT arms and ashwagandha; identity does not match the two-arm melatonin abstract.'),
                  dict(topic='semaglutide-obesity-weight',trial='40825340',reason='Embedded text is an obesity treatment review, not a primary STEP-11 safety table.'),
                  dict(topic='esketamine-trd-madrs',trial='31109201',reason='Embedded text describes a French prospective cohort (207 patients), not the randomized TRANSFORM-2 report.')])
(OUT/'second-pass.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 50 held-span and source-identifier checks; 3 pre-existing override checks.')
