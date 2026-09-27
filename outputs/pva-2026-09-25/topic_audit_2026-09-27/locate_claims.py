"""Identity check for accepted-looking findings: for each claim quote in a .json file, list EVERY smallest JSON object whose
string values contain the quote, with its identity fields. A claim that the finding attaches to trial X must sit in an object
that names X; a generic string found under many rows proves nothing about one of them."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
TREE = Path(__file__).resolve().parent / "tree"
ID_KEYS = ("trial_key", "trial_label", "pmid", "id", "trial", "nct", "outcome", "name", "status", "stated_reason_code",
           "verdict", "slug", "label", "short")


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def objs_containing(o, q, path, out):
    """Return True if q is inside o; record the deepest dicts that contain it."""
    if isinstance(o, str):
        return q in ws(o)
    if isinstance(o, dict):
        child = False
        for k, v in o.items():
            if objs_containing(v, q, f"{path}/{k}", out):
                child = True
        whole = q in ws(json.dumps(o, ensure_ascii=False))
        if whole and not child:
            out.append((path, o))            # q spans several fields of this dict
        elif child and not any(p.startswith(path + "/") for p, _ in out):
            out.append((path, o))
        return whole or child
    if isinstance(o, list):
        return any([objs_containing(v, q, f"{path}[{i}]", out) for i, v in enumerate(o)])
    return False


def locate(file, quote):
    p = TREE / file
    if not p.is_file() or not file.endswith(".json"):
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    q = ws(quote)
    # a quote copied from pretty-printed JSON ('"k": "v",') is matched on its values
    vals = re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', quote)
    out = []
    if vals:
        for path, o in walk_dicts(d, ""):
            if all(str(o.get(k)) == v for k, v in vals if k in o) and all(k in o for k, _ in vals):
                out.append((path, o))
    else:
        objs_containing(d, q, "", out)
    return [(path, {k: o.get(k) for k in ID_KEYS if k in o}) for path, o in out]


def walk_dicts(o, path):
    if isinstance(o, dict):
        yield path, o
        for k, v in o.items():
            yield from walk_dicts(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk_dicts(v, f"{path}[{i}]")


if __name__ == "__main__":
    slug = sys.argv[1]
    d = json.loads((Path(__file__).resolve().parent / "out" / f"{slug}.json").read_text(encoding="utf-8"))
    for i, f in enumerate(d["findings"]):
        loc = locate(f["claim"]["file"], f["claim"]["quote"])
        print(f"[{i}] {f['class']} {f['title'][:80]}")
        if loc is None:
            print("    (claim not in a .json file)")
            continue
        print(f"    claim sits in {len(loc)} object(s)")
        for path, ids in loc[:6]:
            print(f"      {path[:90]} {json.dumps(ids, ensure_ascii=False)[:230]}")
