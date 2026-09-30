"""Sequential, bounded per-file regression runner with offline/write guards."""
from pathlib import Path
import json, os, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]
SCRATCH=ROOT/'.tmp'/'integrate3'
GUARD=r'''import os, sys, re
from pathlib import Path
ROOT=Path(os.environ['LANE_ROOT']).resolve()
def protected(p):
    if isinstance(p, int) or not isinstance(p, (str, bytes, os.PathLike)): return False
    p=Path(os.fsdecode(p)).resolve()
    return p.is_relative_to(ROOT) and not p.is_relative_to(ROOT/'.tmp')
def audit(event,args):
    if event=='open':
        p,mode,flags=args
        if ((mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)) and protected(p):
            raise PermissionError('LANE_PROTECTED_WRITE: '+str(p))
    if event in ('os.remove','os.rmdir','os.mkdir','os.rename','os.replace'):
        for p in args[:2] if event in ('os.rename','os.replace') else args[:1]:
            if protected(p): raise PermissionError('LANE_PROTECTED_WRITE: '+str(p))
    if event=='socket.connect' and args[1][0] not in ('127.0.0.1','::1','localhost'):
        raise PermissionError('LANE_NETWORK_FORBIDDEN')
    if event=='subprocess.Popen':
        exe,argv,cwd,env=args
        # On Windows executable can be None even for a direct argv-list call.
        words=list(argv) if isinstance(argv,(list,tuple)) else re.findall(r'"[^"\n]*"|[^\s"]+',str(argv))
        executable=os.fsdecode(exe) if exe is not None else (str(words[0]).strip('"') if words else '')
        if Path(executable).stem.lower()=='git':
            forbidden={'add','commit','push','checkout','reset','switch','restore','update-index','update-ref','symbolic-ref','init','clean','merge','rebase','fetch','pull','tag','config','branch','rm','mv','stash','gc','prune','repack','worktree','maintenance','reflog','clone','submodule','am','apply','cherry-pick','revert','bisect','notes','replace','-w','--write'}
            normalized=[str(w).strip('"') for w in words]
            # This exact query is read-only and used by fixstate validation.
            if 'branch' in normalized and normalized[normalized.index('branch')+1:] == ['--show-current']:
                forbidden=forbidden-{'branch'}
            if forbidden.intersection(normalized):
                raise PermissionError('LANE_GIT_MUTATION_FORBIDDEN')
sys.addaudithook(audit)
# Old fixture helpers request scratch directly under cwd; relocate only that
# temporary directory request, preserving the test's fixture content and assertions.
import tempfile
_original_mkdtemp = tempfile.mkdtemp
def _lane_mkdtemp(suffix=None, prefix=None, dir=None):
    if dir is not None and Path(dir).resolve() == ROOT:
        dir = ROOT / '.tmp' / 'integrate3'
    return _original_mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
tempfile.mkdtemp = _lane_mkdtemp
'''

def environment():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    guard=SCRATCH/'guard'; guard.mkdir(exist_ok=True)
    (guard/'sitecustomize.py').write_text(GUARD, encoding='utf-8')
    env=dict(os.environ, PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0',
             LANE_ROOT=str(ROOT),PYTHONPATH=os.pathsep.join([str(guard),str(ROOT),str(ROOT/'tests')]),
             TEMP=str(SCRATCH),TMP=str(SCRATCH))
    return env

if __name__=='__main__':
    env=environment()
    files=sorted((ROOT/'tests').glob('test_*.py'))
    if '--files' in sys.argv: files=[ROOT/x for x in sys.argv[sys.argv.index('--files')+1:]]
    baseline='--baseline' in sys.argv
    results=json.loads((SCRATCH/'suite.json').read_text(encoding='utf-8')) if '--resume' in sys.argv else []
    done={r['file'] for r in results}
    files=[f for f in files if f.relative_to(ROOT).as_posix() not in done]
    for file in files:
        name=file.stem+('-base' if baseline else '')
        log=SCRATCH/(name+'.log'); started=time.monotonic()
        args=['-q' if '--quiet' in sys.argv else '-vv','--tb=short','-p','no:cacheprovider',str(file),'--basetemp',str(SCRATCH/('tmp-'+name+'-guarded'))]
        if '--fail-fast' in sys.argv: args.append('-x')
        if baseline:
            command=[sys.executable,'-c','from integrate2_helper import enable_baseline; enable_baseline(); import pytest,sys; sys.exit(pytest.main(sys.argv[1:]))',*args]
        else: command=[sys.executable,'-m','pytest',*args]
        with log.open('w',encoding='utf-8') as output:
            try:
                process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT)
                status=process.wait(timeout=600)
            except subprocess.TimeoutExpired:
                # Only this owned test process tree; never global browser cleanup.
                import psutil
                try:
                    children=psutil.Process(process.pid).children(recursive=True)
                    for child in reversed(children):
                        try: child.kill()
                        except psutil.NoSuchProcess: pass
                except psutil.NoSuchProcess: pass
                process.kill(); process.wait()
                status='TIMEOUT_600S'
        entry=dict(file=file.relative_to(ROOT).as_posix(),status=status,seconds=round(time.monotonic()-started,2),log=str(log.relative_to(ROOT)))
        results.append(entry)
        if '--files' in sys.argv:
            history_path=SCRATCH/'reruns.json'
            history=json.loads(history_path.read_text(encoding='utf-8')) if history_path.exists() else []
            history.append(entry)
            history_path.write_text(json.dumps(history,indent=2),encoding='utf-8')
        (SCRATCH/('suite-baseline.json' if baseline else 'suite-rerun.json' if '--files' in sys.argv else 'suite.json')).write_text(json.dumps(results,indent=2),encoding='utf-8')
        print(json.dumps(entry),flush=True)
