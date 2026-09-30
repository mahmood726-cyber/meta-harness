"""Independent held-byte count checks for the decided odds-boundary changes."""
import json
import math
from pathlib import Path
import re
from statistics import NormalDist

ROOT = Path(__file__).resolve().parents[1]


def mortality_counts(slug, row):
    ref = row.get('document_ref', '').split('#')[0]
    if ref.endswith('.tables.txt'):
        text = (ROOT / ref).read_text(encoding='utf-8')
        header = re.search(r'Dexamethasone \(n = (\d+)\) \| Standard care \(n = (\d+)\)', text)
        events = re.search(r'^All-cause mortality No\. \(%\) \| (\d+) \([^|]+\| (\d+) \(', text, re.M)
        assert header and events, 'REFUSED: unbound mortality table header/row'
        n1, n2 = map(int, header.groups()); a, c = map(int, events.groups())
    else:
        records = json.loads((ROOT / 'cache' / slug / 'records.json').read_text(encoding='utf-8'))['records']
        record = next(r for r in records if str(r['id']) == row['id'].removeprefix('PMID '))
        text = record['abstract']
        match = re.search(r'Overall, (\d+) \(\d+%\) of the (\d+) patients allocated tocilizumab and (\d+) \(\d+%\) of the (\d+) patients allocated to usual care died within 28 days', text)
        if match:
            a, n1, c, n2 = map(int, match.groups())
        else:
            header = re.search(r'(\d+) patients were assigned to receive dexamethasone and (\d+) to receive usual care', text)
            events = re.search(r'Overall, (\d+) patients \([^)]+\) in the dexamethasone group and (\d+) patients \([^)]+\) in the usual care group died within 28 days', text)
            assert header and events, 'REFUSED: unbound mortality allocation/result sentence'
            n1, n2 = map(int, header.groups()); a, c = map(int, events.groups())
    assert 0 < a < n1 and 0 < c < n2
    return dict(ai=a, n1i=n1, ci=c, n2i=n2)


def odds(cells):
    a, c = cells['ai'], cells['ci']
    b, d = cells['n1i']-a, cells['n2i']-c
    estimate = a*d/(b*c)
    se = math.sqrt(sum(1/x for x in (a,b,c,d)))
    z = NormalDist().inv_cdf(.975)
    return estimate, math.exp(math.log(estimate)-z*se), math.exp(math.log(estimate)+z*se)
