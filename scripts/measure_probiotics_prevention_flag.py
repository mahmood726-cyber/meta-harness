"""Measure (never apply) what the probiotics topic's `prevention` flag would change in its screen: every served
record re-screened by harness.screen.screen_record with and without the flag. Read-only; prints; writes nothing."""
import json, sys, copy, collections
sys.path.insert(0, '.')
from harness import screen
slug = 'probiotics-aad-prevention'
cfg = json.load(open(f'topics/{slug}.json', encoding='utf8'))
recs = json.load(open(f'cache/{slug}/records.json', encoding='utf8'))
review = json.load(open(f'docs/reviews/{slug}/review.json', encoding='utf8'))
served = {str(r['id']): r['decision'] for r in review['screening']['records']}
allr = {str(r.get('id')): r for r in list(recs['records']) + list(recs.get('ctgov') or [])}
neg = set(map(str, cfg.get('negative_control_pmids') or []))
inc0 = cfg['include']; inc1 = dict(inc0, prevention=True)
flips = collections.Counter(); newly = []
for rid, dec in served.items():
    r = allr.get(rid)
    if r is None: continue
    a = screen.screen_record(r, inc0, neg); b = screen.screen_record(r, inc1, neg)
    if a[0] != b[0] or a[1] != b[1]:
        flips[(a[1], b[1])] += 1
        if b[0] == 'include': newly.append((rid, (r.get('title') or r.get('acronym') or '')[:90]))
print('served decisions', collections.Counter(served.values()))
print('rule outcome changes with prevention=True:', dict(flips))
print('records that would become INCLUDE:', len(newly))
for x in newly[:25]: print('  ', x)
print('records that would DROP from include:')
for rid, dec in served.items():
    r = allr.get(rid)
    if r is None or dec != 'include': continue
    b = screen.screen_record(r, inc1, neg)
    if b[0] != 'include': print('  ', rid, b[1], '|', b[2][:110])
