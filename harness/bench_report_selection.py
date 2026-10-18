"""Opt-in comparator-cited report selection; identities only, never effect data."""
import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from . import trial_family

def apply(config, records, root):
    if not config.get('report_selection'):
        return config, records
    if (config.get('report_selection') != 'as_comparator_cited'
            or config.get('slug') != 'daratumumab-rrmm-pfs-bench'
            or config.get('typed_routes') != 'daratumumab_rrmm_pfs'):
        raise ValueError('REPORT_SELECTION_SCOPE_MISMATCH')
    ref = 'cache/benchmarks/v1/PMC10519573.xml'
    raw = (Path(root)/ref).read_bytes()
    doc = ET.fromstring(raw)
    if doc.findtext('.//article-meta/article-id[@pub-id-type="pmid"]') != config['comparator_pmid']:
        raise ValueError('REPORT_SELECTION_COMPARATOR_MISMATCH')
    pubs = [dict(r) for r in records['records']]
    byid = {str(r['id']):r for r in pubs}
    selected = {}
    table = doc.find('.//table-wrap[@id="T1"]')
    for tr in table.findall('.//tbody/tr'):
        cells = [''.join(c.itertext()).strip() for c in tr]
        match = re.fullmatch(r'(\w+) et al (\d{4})', cells[0])
        if match is None:
            raise ValueError('REPORT_SELECTION_CITATION_UNBOUND: '+cells[0])
        author, year = match.groups()
        nct = cells[2]
        if not re.fullmatch(r'NCT\d{8}', nct):
            raise ValueError('REPORT_SELECTION_REGISTRY_UNBOUND')
        refs = [r for r in doc.findall('.//ref') if r.findtext('.//surname') == author and r.findtext('.//year') == year]
        refs = [r for r in refs if r.findtext('.//pub-id[@pub-id-type="pmid"]') in byid]
        if len(refs) != 1:
            raise ValueError('REPORT_SELECTION_REFERENCE_AMBIGUOUS: '+cells[0])
        citation = refs[0]
        pid = citation.findtext('.//pub-id[@pub-id-type="pmid"]')
        rec = byid[pid]
        doi = citation.findtext('.//pub-id[@pub-id-type="doi"]')
        normalize = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
        title = ''.join(citation.find('.//article-title').itertext())
        if rec.get('doi','').lower() != doi.lower() or normalize(rec['title']) != normalize(title):
            raise ValueError('REPORT_SELECTION_REPORT_IDENTITY_MISMATCH: '+pid)
        own = trial_family.registry_ids(rec)
        if own and own != [nct]:
            raise ValueError('REPORT_SELECTION_REGISTRY_CONFLICT: '+pid)
        if nct in selected:
            raise ValueError('REPORT_SELECTION_MULTIPLE_REPORTS: '+nct)
        evidence = dict(source=ref, sha256=hashlib.sha256(raw).hexdigest(),
            nct_id=nct, table_row=ET.tostring(tr,encoding='unicode'),
            citation=ET.tostring(citation,encoding='unicode'), report_id=pid,
            basis='Comparator Table 1 author/year joined to reference PMID, DOI and exact normalized title; identity only')
        rec.update(nct=nct, family_parent_evidence=evidence, report_selection_evidence=evidence)
        selected[nct] = pid
    companions = [c for c in trial_family.automatic_companions(pubs, config) if c['family_id'] not in selected]
    for rec in pubs:
        ids = trial_family.registry_ids(rec)
        # A named secondary report cannot establish an independent trial without
        # registry evidence. Keep the refusal local to this declared report policy.
        if (not ids and not rec.get('report_selection_evidence')
                and re.search(r'quality.of.life|patient.reported outcomes', rec.get('title', ''), re.I)):
            companions.append(dict(pmid=str(rec['id']), parent_pmid=None, parent=None,
                kind='secondary outcome report; independent trial identity unbound',
                selection_evidence=dict(title=rec['title'], policy=config['report_selection'])))
        if len(ids) == 1 and ids[0] in selected and rec['id'] != selected[ids[0]]:
            companions.append(dict(pmid=rec['id'], parent_pmid=selected[ids[0]], parent=selected[ids[0]],
                family_id=ids[0], kind='alternate report; comparator-cited analysis selected',
                selection_evidence=byid[selected[ids[0]]]['report_selection_evidence']))
    return dict(config, companion_reports=companions), dict(records, records=pubs)
