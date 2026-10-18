"""Replay held OCR cells into comparator-only rows; never primary extraction input.

Static: named source paths, figure layouts (column coordinates), parsing rules.
Dynamic: every number, identity, source hash, table/reference join and control.
OCR observations are retained verbatim, including imperfect author spellings.
"""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import secondary_meta as sm, bench_report_selection

DARA = 'daratumumab-rrmm-pfs-bench'
HCQ = 'hcq-covid-prophylaxis-bench'
XL = '{http://www.w3.org/1999/xlink}href'


def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf8'))


def save(path, obj):
    (ROOT/path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT/path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf8')


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def lines(name):
    obj = load('.codex_logs/'+name+'.json')
    for line in obj['lines']:
        line['x'] = min(w['x'] for w in line['words'])
        line['y'] = min(w['y'] for w in line['words'])
    return obj


def build(slug):
    cfg = load('topics/'+slug+'.json')
    dara = slug == DARA
    article = 'cache/benchmarks/v1/'+('PMC10519573' if dara else 'PMC7787432')+'.xml'
    image = 'cache/benchmarks/v1/medi-102-e35319-g004.jpg' if dara else 'cache/comparators/33406138/hcq_figure2.png'
    doc = ET.fromstring((ROOT/article).read_bytes())
    pmid = doc.findtext('.//article-id[@pub-id-type="pmid"]')
    assert pmid == cfg['comparator_pmid']
    fig = next(f for f in doc.iter('fig') if any(g.get(XL,'').endswith('g004.jpg' if dara else 'g002.jpg') for g in f.iter('graphic')))
    metadata = dict(pmid=pmid,source_ref=image,sha256=sha(image),source_article=article,
                    source_article_sha256=sha(article), figure=ET.tostring(fig,encoding='unicode'),
                    license_evidence=ET.tostring(doc.find('.//permissions'),encoding='unicode'),
                    role='comparator figure; never primary extraction input')
    metadata_path=str(Path(image).with_suffix('.source.json'))
    if (ROOT/metadata_path).exists():
        prior=load(metadata_path)
        assert prior['sha256']==metadata['sha256'] and prior['source_article_sha256']==metadata['source_article_sha256']
    else:
        save(metadata_path,metadata)
    records = load('cache/'+slug+'/records.json')
    review = load('docs/reviews/'+slug+'/review.json')
    pooled_ids = {str(t['id']) for o in review['outcomes'] if o.get('primary') for t in o['trials']}
    identities = []
    if dara:
        _, selected = bench_report_selection.apply(cfg,records,ROOT)
        for r in selected['records']:
            ev=r.get('report_selection_evidence')
            if ev:
                tr=ET.fromstring(ev['table_row'])
                label=''.join(tr[0].itertext())
                identities.append(dict(label=label,pmid=str(r['id']),nct=ev['nct_id'],evidence=ev))
    else:
        table=next(t for t in doc.iter('table-wrap') if t.get('id').endswith('t001'))
        for tr in table.iter('tr'):
            text=''.join(tr[0].itertext())
            nct=re.search(r'NCT\d{8}',text)
            if not nct: continue
            author=text.split('n =')[0]
            refs=[r for r in doc.iter('ref') if (r.findtext('.//named-content') or '').startswith(author+' ')]
            assert len(refs)==1
            citation=refs[0]
            pid=next(e.get(XL) for e in citation.iter('ext-link') if e.get('ext-link-type')=='pmid')
            doi=next(e.get(XL) for e in citation.iter('ext-link') if e.get('ext-link-type')=='doi')
            rec=next(r for r in records['records'] if str(r['id'])==pid)
            assert rec['doi'].lower()==doi.lower()
            year=re.search(r'\b20\d\d\b',citation.findtext('.//named-content')).group()
            identities.append(dict(label=author+' '+year,pmid=pid,nct=nct.group(),
                 evidence=dict(source=article,sha256=sha(article),table_row=ET.tostring(tr,encoding='unicode'),
                               citation=ET.tostring(citation,encoding='unicode'))))
    identities.sort(key=lambda r:r['label'])
    ocr=lines('dara_ocr3' if dara else 'hcq_ocr')
    read_image='.codex_logs/dara_3x.png' if dara else image
    assert ocr['image_sha256']==sha(read_image)
    effects=[]
    for line in ocr['lines']:
        if not (1050 < line['x'] < 1300): continue
        text=re.sub(r'(?<=0) (?=\d{2})','.',line['text'])
        # These figures print single-digit ratios to two decimals; OCR commonly
        # reads the square bracket as '1'. Keep that glyph in the witness.
        values=re.findall(r'\d\.\d{2}',text)
        if len(values)==3: effects.append((line,values))
    effects.sort(key=lambda x:x[0]['y'])
    assert len(effects)==len(identities)+1, effects
    label_ocr=lines('dara_ocr' if dara else 'hcq_labels_ocr')
    label_lines=[l for l in label_ocr['lines'] if re.search(r'20\d{2}',l['text']) and l['x'] < (160 if dara else 1080)]
    label_lines.sort(key=lambda l:l['y'])
    assert len(label_lines)==len(identities)
    rows=[]; units=[]
    for identity,(line,values),label_line in zip(identities,effects,label_lines):
        # Alphabetical figure order is validated against independent OCR labels;
        # canonical identity comes from the held table/reference, never OCR PMID inference.
        norm=lambda s: re.sub('[^a-z0-9]','',s.lower().replace('et al',''))
        similarity=SequenceMatcher(None,norm(identity['label']),norm(label_line['text'])).ratio()
        assert similarity >= .5, (identity['label'],label_line['text'],similarity)
        cells={k:dict(value=v,kind='TYPED_IMAGE_READ',image_sha256=sha(image),
                     read_image_sha256=ocr['image_sha256'],ocr_line=line) for k,v in zip(('effect','lower','upper'),values)}
        kwargs={}
        if not dara:
            for k,(left,right) in zip(('events_t','n_t','events_c','n_c'),((370,480),(490,595),(610,710),(730,830))):
                candidates=[l for l in ocr['lines'] if left<=l['x']<=right and abs(l['y']-line['y'])<5 and l['text'].isdigit()]
                assert len(candidates)==1,(k,candidates)
                cell=candidates[0]; kwargs[k]=int(cell['text'])
                cells[k]=dict(value=kwargs[k],kind='TYPED_IMAGE_READ',image_sha256=sha(image),ocr_line=cell)
        row=sm.SecondaryRow(meta_pmid=pmid,meta_doi='',source_digest=sha(image),
             location=dict(kind='figure',id=fig.get('id'),row_label=label_line['text'],cells=cells,
                           identity=identity['evidence'],label_read=label_line,
                           label_join=dict(method='sorted table labels corroborated by OCR',similarity=similarity)),
             provenance='TYPED_IMAGE_READ:Windows.Media.Ocr',trial_label=identity['label'],
             measure='HR' if dara else 'RR',outcome_definition=''.join(fig.find('caption').itertext()),
             effect=values[0],lower=values[1],upper=values[2],family_id='PMID '+identity['pmid'],**kwargs)
        assert not sm.validate(row),sm.validate(row)
        rows.append(row)
        units.append(dict(slug=slug,label=identity['label'],pmids=[identity['pmid']],ncts=[identity['nct']],
                          comparator_pmid=pmid,status='POOLED' if row.family_id in pooled_ids else 'NOT_IN_POOL',drug='DRUG_MATCH',study={},
                          unit_source='JATS_TABLE_AND_IMAGE',gap_class='POOLED' if row.family_id in pooled_ids else 'IDENTIFICATION',
                          table=fig.get('id'),context=identity['evidence']['table_row'],
                          cited_pmids=[identity['pmid']],identity_basis=['held_table_reference_join'],
                          identity_evidence=identity['evidence']))
    pooled=dict(zip(('effect','lower','upper'),effects[-1][1]))
    pc=sm.positive_control(rows,pooled,rows[0].measure,stated_model='Random')
    if not pc['reproduced']:
        raise ValueError(pc)
    save('registry/secondary_meta/'+slug+'.json',dict(slug=slug,comparator_pmid=pmid,rows=[r.to_dict() for r in rows],
         metas={pmid:dict(usable=True,is_comparator=True,figure=fig.get('id'),pooled=pooled,measure=rows[0].measure,
                    provenance='TYPED_IMAGE_READ',positive_control=pc,identity_basis=rows[0].outcome_definition,
                    pooled_cell_provenance=dict(kind='TYPED_IMAGE_READ',image_sha256=sha(image),ocr_line=effects[-1][0]))},
         tally={'SECONDARY_UNVERIFIED':len(rows)},skipped={},registry=None))
    return units,dict(slug=slug,comparator_set_state='ENUMERATED',sources_tried=[article,image])


def main():
    results=[build(s) for s in (DARA,HCQ)]
    table=load('outputs/k_gap/k_gap_table.json')
    for units,topic in results:
        table['trials']=[t for t in table['trials'] if t['slug']!=topic['slug']]+units
        table['topics']=[t for t in table['topics'] if t['slug']!=topic['slug']]+[topic]
    save('outputs/k_gap/k_gap_table.json',table)


if __name__=='__main__': main()
