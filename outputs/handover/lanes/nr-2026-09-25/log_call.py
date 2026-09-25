import sys,json,hashlib,os
from pathlib import Path
j,cid,s,e,rc,prompt=sys.argv[1:7]
note=sys.argv[7] if len(sys.argv)>7 else ""
def h(p):
    p=os.path.join(j,p); return hashlib.sha256(open(p,'rb').read()).hexdigest() if os.path.exists(p) else None
lm=os.path.join(j,"last_message.txt")
files=sorted(Path(os.path.relpath(os.path.join(r,f),j)).as_posix() for r,_,fs in os.walk(j) for f in fs)
tok=None
try:
    t=open(os.path.join(j,"stderr.txt"),encoding="utf-8",errors="replace").read().rsplit("tokens used",1)[1].split()[0]; tok=int(t.replace(",",""))
except Exception: pass
rec={"call_id":cid,"job_dir":j,"started_utc":s,"ended_utc":e,"rc":int(rc),"stdin":"/dev/null","sandbox":"read-only",
 "prompt":prompt,"lane_context_sha256":h("LANE_CONTEXT.md"),"brief_sha256":h("BRIEF.md"),"files":files,
 "last_message_sha256":h("last_message.txt"),"last_message_bytes":os.path.getsize(lm) if os.path.exists(lm) else None,
 "tokens_used":tok,"note":note}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"CALL_LOG.jsonl"),"a",encoding="utf-8") as f:
    f.write(json.dumps(rec)+"\n")
print("logged",cid)
