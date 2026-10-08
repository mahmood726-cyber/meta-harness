"""Span gate for the codex rendering checks: every page_quote must occur in that topic's tabs.html (raw markup or its
visible text), every evidence quote in the named file of the job folder (raw, or for .json any decoded string value).
Whitespace normalised; '...' fragments must occur in order. A finding with any missing quote is REJECTED."""
import html
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
A = Path(__file__).resolve().parent


def ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


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


_cache = {}


def reps(path: Path):
    if path in _cache:
        return _cache[path]
    if not path.is_file():
        _cache[path] = None
        return None
    t = path.read_text(encoding="utf-8", errors="replace")
    out = [ws(t), ws(html.unescape(re.sub(r"<[^>]+>", " ", t)))]
    if path.suffix == ".json":
        try:
            acc = []
            strings(json.loads(t), acc)
            out.append(ws("\n".join(acc)))
        except ValueError:
            pass
    _cache[path] = out
    return out


def found(path: Path, quote: str) -> str:
    r = reps(path)
    if r is None:
        return "FILE_NOT_FOUND"
    q = ws(quote)
    if not q:
        return "EMPTY"
    if any(q in x for x in r) or any(ws(html.unescape(q)) in x for x in r):
        return "OK"
    parts = [ws(p) for p in re.split(r"\s*(?:\.\.\.|…)\s*", q) if ws(p)]
    for x in r:
        pos, ok = 0, len(parts) > 1
        for p in parts:
            i = x.find(p, pos)
            if i < 0:
                ok = False
                break
            pos = i + len(p)
        if ok:
            return "OK_ELLIPSIS"
    return "NOT_FOUND"


def main():
    res = []
    for f in sorted((A / "out").glob("job*.json")):
        job = A / "jobs" / f.stem
        d = json.loads(f.read_text(encoding="utf-8"))
        for i, fd in enumerate(d.get("findings", [])):
            checks = [("page", found(job / fd["slug"] / "tabs.html", fd["page_quote"]))]
            for ev in fd.get("evidence", []):
                fp = ev["file"].replace("\\", "/").lstrip("./")
                cand = [job / fp, job / fd["slug"] / fp]
                st = next((found(c, ev["quote"]) for c in cand if c.is_file()), "FILE_NOT_FOUND")
                checks.append((ev["file"], st))
            ok = all(s.startswith("OK") for _, s in checks)
            res.append({"job": f.stem, "n": i, "slug": fd["slug"], "kind": fd["kind"], "tab": fd["tab"], "title": fd["title"],
                        "spans_verified": ok, "checks": checks, "finding": fd})
    (A / "gate.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"findings {len(res)}; spans verified {sum(r['spans_verified'] for r in res)}")
    for r in res:
        if not r["spans_verified"]:
            print("  REJECT", r["slug"], r["kind"], r["title"][:70], "::", [c for c in r["checks"] if not c[1].startswith("OK")])


if __name__ == "__main__":
    main()
