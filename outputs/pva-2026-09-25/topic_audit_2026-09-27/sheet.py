import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
ident = json.load(open("identity.json", encoding="utf-8"))
for slug in sys.argv[1:]:
    fs = json.load(open(f"out/{slug}.json", encoding="utf-8"))["findings"]
    print(f"\n######## {slug} ({len(fs)})")
    for i, f in enumerate(fs):
        idn = ident.get(f"{slug}#{i}", {})
        print(f"[{i}] {f['class']} {f['confidence']} | {f['title']}")
        print(f"   CLAIM {f['claim']['file'].split('/')[-1]} objs={idn.get('objects')} ids={json.dumps(idn.get('ids'), ensure_ascii=False)[:200]}")
        print(f"         {f['claim']['quote'][:260]}")
        for e in f["evidence"][:3]:
            print(f"   EVID  {e['file'].split('/')[-1]}: {e['quote'][:260]}")
        print(f"   WHY   {f['why_wrong'][:420]}")
