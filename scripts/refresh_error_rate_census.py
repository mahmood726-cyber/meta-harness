"""Refresh the live pooled-row census without fabricating a new blind audit.

The historical independent checker outputs are not required for this offline
inventory refresh. New rows are explicitly NOT_INDEPENDENTLY_RECHECKED.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ep=ROOT/'docs/error_rate.json'
    sp=ROOT/'docs/error_rate_sample.json'
    d=json.loads(ep.read_text(encoding='utf-8'))
    sample=json.loads(sp.read_text(encoding='utf-8'))
    rows={r['row_id']:r for r in sample['rows']}
    current={}
    for path in sorted((ROOT/'docs/reviews').glob('*/review.json')):
        review=json.loads(path.read_text(encoding='utf-8'))
        for outcome in review['outcomes']:
            for trial in outcome.get('trials',[]):
                if not any(trial.get(k) is not None for k in ('effect','mean1','ai')):
                    continue
                rid=f"{review['slug']}::{outcome['name']}::{trial.get('label')}"
                current[rid]=dict(row_id=rid,provenance=trial.get('provenance'),
                    verdict='NOT_INDEPENDENTLY_RECHECKED',
                    build_verification=trial.get('verified'),
                    source=trial.get('source'),
                    stored={k:trial[k] for k in ('effect','ci_low','ci_high','scale','ai','n1i','ci','n2i','mean1','sd1','nc1','mean2','sd2','nc2') if k in trial})
    for rid,row in current.items():
        if rid not in rows:
            rows[rid]=row
    sample['rows']=[rows[k] for k in sorted(rows)]
    sample['n']=len(rows)
    sample['refresh_note']='New IN3 census rows are inventoried from current objects and explicitly NOT_INDEPENDENTLY_RECHECKED; no new blind verification is claimed.'
    d.update(population=len(rows),n_pooled_current_after_fixes=len(current),
             current_pooled_population=len(current),
             removed_by_census_fixes=sorted(set(rows)-set(current)),
             inventory_refreshed_utc='2026-09-17',
             inventory_method='scripts/refresh_error_rate_census.py; current review objects, no independent re-extraction',
             independent_audit_state='HISTORICAL_ONLY',
             not_independently_rechecked_current=sum(rows[k]['verdict']=='NOT_INDEPENDENTLY_RECHECKED' for k in current))
    for path,obj in ((ep,d),(sp,sample)):
        path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Inventoried {len(current)} of {len(current)} current pooled rows; historical blind audit unchanged; {d['not_independently_rechecked_current']} current rows NOT_INDEPENDENTLY_RECHECKED.")

if __name__=='__main__':
    main()
