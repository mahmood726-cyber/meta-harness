"""Offline R3 core/page replay into scratch; compare membership and pool against HEAD."""
import os
os.environ['CAPTAIN_NO_WORKTREE_SCAN']='1'
import hashlib, json, socket, subprocess, sys, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.dara_contrast_measure import cohort
from scripts.dara_contrast_rebuild import state
from harness import pipeline, served_comparator, registration
from harness.page import render_page
LOG=ROOT/'.codex_logs'
def no_network(*args,**kwargs):
    raise RuntimeError('R3 offline replay: network prohibited')
socket.socket.connect=no_network

def main():
    slugs=cohort(); assert len(slugs)==32
    rows=[]
    if '--resume' in sys.argv:
        prior=json.loads((LOG/'r3_rebuild_results.json').read_text(encoding='utf8'))
        rows=[r for r in prior if r['status']=='PASS']
    done={r['slug'] for r in rows}
    for slug in ['daratumumab-rrmm-pfs-bench']+slugs:
        if slug in done:
            continue
        print('BUILD',slug,flush=True)
        row={'slug':slug}
        try:
            cfg=json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8'))
            cfg=served_comparator.served_config(slug,cfg)
            if slug in slugs:
                assert not cfg.get('typed_routes')
            records=json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))
            sha=registration.protocol_sha(slug)
            core=pipeline.build_review_core(slug,cfg,records,sha)
            if str(cfg.get('benchmark',{}).get('status','')).startswith('protocol_draft'):
                core['status']='DRAFT_BOOTSTRAP'
            dest=LOG/'r3_scratch'/slug; dest.mkdir(parents=True,exist_ok=True)
            (dest/'review.json').write_text(json.dumps(core,ensure_ascii=False,indent=2),encoding='utf8')
            (dest/'index.html').write_text(render_page(core),encoding='utf8')
            baseline=subprocess.run(['git','show',f'HEAD:docs/reviews/{slug}/review.json'],capture_output=True)
            before=state(json.loads(baseline.stdout)) if baseline.returncode==0 else {}
            after=state(core)
            changes={k:{'before':before.get(k),'after':after.get(k)} for k in sorted(before.keys()|after.keys()) if before.get(k)!=after.get(k)}
            row.update(status='PASS',changes=changes,after=after,baseline='HEAD' if baseline.returncode==0 else 'HEAD_ABSENT')
        except Exception as e:
            traceback.print_exc(); row.update(status='FAIL',error=str(e))
        rows.append(row)
        (LOG/'r3_rebuild_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
        print('DONE',slug,row['status'],len(row.get('changes',{})),flush=True)
if __name__=='__main__': main()
