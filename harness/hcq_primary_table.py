"""Read the declared Rajasingham primary endpoint and arm sizes from held JATS.

Static: endpoint/table locators. Dynamic: identities, counts, denominators, spans.
"""
import re
import xml.etree.ElementTree as ET

ENDPOINT = 'PCR positive or probable COVID-19'


def read(raw):
    doc = ET.fromstring(raw)
    def table(key):
        found = [t for t in doc.iter('table-wrap') if t.get('id') == key]
        if len(found) != 1:
            raise ValueError('HCQ_PRIMARY_TABLE_NONUNIQUE')
        return [[''.join(c.itertext()).strip() for c in r] for r in found[0].iter('tr')]
    def one(rows, label):
        found = [r for r in rows if r and r[0] == label]
        if len(found) != 1:
            raise ValueError('HCQ_PRIMARY_ROW_NONUNIQUE')
        return found[0]
    baseline, outcomes = table('T1'), table('T2')
    ns = one(baseline, 'Number randomized')
    target = one(outcomes, ENDPOINT)
    arms = {}
    for title, n in zip(baseline[0][1:], ns[1:]):
        indices = [i for i, value in enumerate(outcomes[0]) if value == title]
        if len(indices) != 1:
            raise ValueError('HCQ_PRIMARY_ARM_NONUNIQUE')
        cell = target[indices[0]]
        match = re.fullmatch(r'(\d+) \((\d+(?:\.\d+)?)\)', cell)
        if not match:
            raise ValueError('HCQ_PRIMARY_CELL_INVALID')
        e, total = int(match[1]), int(n)
        if not 0 <= e <= total or total <= 0 or abs(100*e/total-float(match[2])) > .11:
            raise ValueError('HCQ_PRIMARY_CELL_CORROBORATION')
        arms[title] = [e, total]
    treated = [v for k, v in arms.items() if k.startswith('Hydroxychloroquine ')]
    control = [v for k, v in arms.items() if k == 'Placebo']
    if len(treated) != 2 or len(control) != 1 or len(arms) != 3:
        raise ValueError('HCQ_PRIMARY_ARM_PARTITION')
    return dict(arms=arms, ai=sum(v[0] for v in treated), n1i=sum(v[1] for v in treated),
                ci=control[0][0], n2i=control[0][1], endpoint=ENDPOINT,
                report_id=doc.findtext('.//article-id[@pub-id-type="pmid"]'),
                span=' | '.join(target), denominators=' | '.join(ns))
