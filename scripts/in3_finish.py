"""Run the required ordered renderer, survival, and full-standard sequence."""
import os
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/handover/in3'

def run(name,args):
    with (OUT/name).open('w',encoding='utf-8',newline='\n') as f:
        env=dict(os.environ,PYTHONIOENCODING='utf-8')
        guard=ROOT/'scripts/in3_offline'
        assert (guard/'sitecustomize.py').is_file(), 'Offline guard missing'
        env['PYTHONPATH']=str(guard)+os.pathsep+env.get('PYTHONPATH','')
        p=subprocess.run([sys.executable,*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,
                         env=env)
    print(name,'exit',p.returncode,flush=True)
    status_path=OUT/'command_exits.json'
    statuses=json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {}
    statuses[name]=dict(command=[sys.executable,*args],exit_code=p.returncode)
    status_path.write_text(json.dumps(statuses,indent=2)+'\n',encoding='utf-8',newline='\n')
    return p.returncode

def main():
    for script in ('error_rate_compare.py','error_rate_pass2.py'):
        run(script+'.txt',['scripts/in3_run.py','scripts/'+script])
    if run('census.txt',['scripts/refresh_error_rate_census.py']):
        return 1
    for script in ('render_fix_ledger.py','rewrite_fixstate_lines.py','build_evidence_index.py',
                   'render_gate_gaps.py','render_gate_scorecard.py','external_agreement.py'):
        if run(script+'.txt',['scripts/in3_run.py','scripts/'+script]):
            return 1
    if run('index.txt',['-m','harness.index','docs']):
        return 1
    run('retraction_survival.txt',['scripts/retraction_survival.py','f6f7b14c'])
    return run('verify_all.txt',['-u','scripts/verify_all.py'])

if __name__=='__main__':
    sys.exit(main())
