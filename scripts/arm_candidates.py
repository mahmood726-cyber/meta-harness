"""For topics with results-only trials (AACT results posted, no publication — poolable data no meta
has), dump their AACT structured arm-level outcomes ranked to the declared outcome. CANDIDATES for
hand-verification + pooling as registry-only entries; never auto-pooled."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import aact, embed
TOPICS = sys.argv[1:] or ["colchicine-postop-af","sglt2-hfref-hosp-cvdeath","pcsk9-mace","dapagliflozin-hfpef-hosp"]
want={}; declared={}
for slug in TOPICS:
    gp=f"{ROOT}/cache/{slug}/ghost.json"
    if not os.path.exists(gp): continue
    g=json.load(open(gp,encoding="utf-8"))
    cfg=json.load(open(f"{ROOT}/topics/{slug}.json",encoding="utf-8"))
    declared[slug]=cfg["primary_outcome"]["name"]
    for nct in g.get("results_only_ncts",[])[:8]:
        want.setdefault(slug,[]).append(nct)
alln=set(n for v in want.values() for n in v)
print("results-only NCTs to extract:",{s:v for s,v in want.items()})
arms=aact.outcome_arms(alln) if alln else {}
for slug,ncts in want.items():
    for nct in ncts:
        outs=arms.get(nct,[]); titles=[o["title"] for o in outs if o.get("title")]
        ranked=embed.rank(declared[slug],titles) if titles else []
        top=ranked[:2]
        if top and top[0][1]>=0.35:
            print(f"\n== {slug} {nct} | declared {declared[slug]} ==")
            for title,score in top:
                o=next(x for x in outs if x["title"]==title)
                print(f"  [{score:.2f}] {title[:55]} ({o.get('type')}) "+str([(a['group'][:22],a.get('events'),a.get('denom')) for a in o['arms']]))
