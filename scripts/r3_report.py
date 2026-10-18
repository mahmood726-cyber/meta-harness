"""Generate R3 reporting directly from execution artifacts."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.dara_contrast_measure import cohort
LOG=ROOT/'.codex_logs'
def main():
    rows={r['slug']:r for r in json.loads((LOG/'r3_rebuild_results.json').read_text(encoding='utf8'))}
    slugs=cohort(); assert len(slugs)==32 and all(s in rows for s in slugs)
    old=subprocess.check_output(['git','show','0d95190c29:harness/extract.py'],cwd=ROOT)
    current=(ROOT/'harness/extract.py').read_bytes(); assert current==old
    proof={'main':hashlib.sha256(old).hexdigest(),'worktree':hashlib.sha256(current).hexdigest(),'byte_equal':current==old}
    (LOG/'r3_extract_hash.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
    table=['| Topic | HEAD pool/membership comparison |','|---|---|']
    failures=[]
    for slug in slugs:
        r=rows[slug]
        if r['status']=='FAIL':
            result='REFUSED; diff unavailable'
            failures.append(slug+': '+r['error'])
        else:
            result='Unchanged' if not r['changes'] else str(len(r['changes']))+' changed outcomes'
        table.append('| '+slug+' | '+result+' |')
    (LOG/'r3_topic_diff_table.md').write_text('\n'.join(table)+'\n',encoding='utf8')
    tests=(LOG/'r3_tests_final.txt').read_text(encoding='utf8')
    summary=next(x for x in reversed(tests.splitlines()) if ' passed' in x)
    failed_tests=[x for x in tests.splitlines() if x.startswith('FAILED ')]
    blockers=['# R3 unresolved verification blockers','',summary,'']+failed_tests+['']+failures
    (LOG/'STUCK_FAILURES.md').write_text('\n'.join(blockers)+'\n',encoding='utf8')
    counts={'served_topics':len(slugs),'passed_replays':sum(rows[s]['status']=='PASS' for s in slugs),'refused_replays':len(failures),'changed_successful_topics':[s for s in slugs if rows[s]['status']=='PASS' and rows[s]['changes']],'test_summary':summary,'hash':proof}
    (LOG/'r3_summary.json').write_text(json.dumps(counts,indent=2),encoding='utf8')
    from harness import extract, trial_family
    slug='daratumumab-rrmm-pfs-bench'
    review=json.loads((LOG/'r3_scratch'/slug/'review.json').read_text(encoding='utf8'))
    records={r['id']:r for r in json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))['records']}
    proof=[]
    for row in review['outcomes'][0]['trials']:
        pid=row['id'].removeprefix('PMID '); record=records[pid]
        text=extract._norm(record['abstract'])
        expected=tuple(row[k] for k in ('scale','effect','ci_low','ci_high'))
        hits=[m for m in extract._EFFECT.finditer(text) if extract._effect_from_match(m,text)==expected]
        assert hits,(pid,expected)
        proof.append(dict(id=pid,title=record['title'],registry_ids=trial_family.registry_ids(record),effect=expected,matched_spans=[text[m.start():m.end()] for m in hits]))
    (LOG/'r3_source_review.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False),encoding='utf8')
    print('DARATUMUMAB',json.dumps(rows[slug]['after'],indent=2))
    print(json.dumps(counts,indent=2)); print('\n'.join(table)); print('\n'.join(failures))
if __name__=='__main__':main()
