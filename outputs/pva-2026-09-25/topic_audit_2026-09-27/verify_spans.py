"""Gate for codex findings: every quote (claim + evidence) must exist in the file it names, in the held bytes of the
read-only extract. Representations searched: raw text; for .json, every decoded string value (escapes differ); for .html,
the unescaped tag-stripped text; .gz decompressed. Whitespace normalised. A finding with ANY missing quote is REJECTED."""
import gzip
import html
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
TREE = Path(__file__).resolve().parent / "tree"
_cache = {}


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def strings(o, acc):
    if isinstance(o, str):
        acc.append(o)
    elif isinstance(o, dict):
        for k, v in o.items():
            acc.append(str(k))
            strings(v, acc)
    elif isinstance(o, list):
        for v in o:
            strings(v, acc)
    elif o is not None:
        acc.append(json.dumps(o))


def reps(rel):
    rel = rel.replace("\\", "/")
    rel = re.sub(r"^.*?/tree/", "", rel).lstrip("./")
    if rel in _cache:
        return _cache[rel]
    p = TREE / rel
    if not p.is_file():
        _cache[rel] = None
        return None
    b = p.read_bytes()
    if rel.endswith(".gz"):
        b = gzip.decompress(b)
    t = b.decode("utf-8", "replace")
    out = [ws(t)]
    if rel.endswith(".json") or rel.endswith(".json.gz"):
        try:
            acc = []
            strings(json.loads(t), acc)
            out.append(ws("\n".join(acc)))
        except ValueError:
            pass
    if rel.endswith(".html"):
        out.append(ws(html.unescape(re.sub(r"<[^>]+>", " ", t))))
    _cache[rel] = out
    return out


def found(file, quote):
    r = reps(file)
    if r is None:
        return "FILE_NOT_FOUND"
    q = ws(quote)
    if not q:
        return "EMPTY_QUOTE"
    if any(q in x for x in r):
        return "OK"
    # tolerate an ellipsis the model inserted: every fragment must be present, in order, in one representation
    parts = [ws(x) for x in re.split(r"\s*(?:\.\.\.|…)\s*", q) if ws(x)]
    if len(parts) > 1:
        for x in r:
            pos, ok = 0, True
            for part in parts:
                i = x.find(part, pos)
                if i < 0:
                    ok = False
                    break
                pos = i + len(part)
            if ok:
                return "OK_ELLIPSIS"
    return "NOT_FOUND"


def main():
    res = {}
    for f in sorted((Path(__file__).resolve().parent / "out").glob("*.json")):
        slug = f.stem
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            res[slug] = {"error": f"unparseable output: {e}"}
            continue
        rows = []
        for i, fd in enumerate(d.get("findings", [])):
            qs = [("claim", fd["claim"])] + [(f"evidence{j}", e) for j, e in enumerate(fd.get("evidence", []))]
            checks = [{"role": role, "file": q["file"], "status": found(q["file"], q["quote"]), "quote": q["quote"][:160]} for role, q in qs]
            ok = all(c["status"].startswith("OK") for c in checks)
            rows.append({"n": i, "class": fd["class"], "title": fd["title"], "spans_verified": ok, "checks": checks})
        res[slug] = {"findings": len(rows), "spans_verified": sum(r["spans_verified"] for r in rows), "rows": rows,
                     "classes_checked": {c["class"]: c["result"] for c in d.get("classes_checked", [])}}
    (Path(__file__).resolve().parent / "span_gate.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    for slug, v in res.items():
        if "error" in v:
            print(slug, v["error"])
            continue
        print(f"{slug:36} findings {v['findings']:2}  spans verified {v['spans_verified']:2}")
        for r in v["rows"]:
            if not r["spans_verified"]:
                bad = [c for c in r["checks"] if not c["status"].startswith("OK")]
                print(f"    REJECT {r['class']} {r['title'][:70]} :: {bad[0]['status']} {bad[0]['file']} :: {bad[0]['quote'][:90]}")


if __name__ == "__main__":
    main()
