"""Match a locator's verbatim quotes to the lane's held renders. For each trial / domain / quote, find_span.locate
returns the EXACT render substring (tolerating whitespace/dash/quote differences) or None. Output: a JSON of matched
spans with their held ref, for the lane to review before any enters SPEC.json. Nothing here judges anything.
  python match_quotes.py <located.json> <srcmap.json> <out.json>
srcmap.json: {"<trial>": {"<source id>": "<held ref>"}}"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evidence", "scripts"))
os.chdir(ROOT)
import find_span  # noqa: E402

KEYS = ("D1", "D2", "D2_treatment_discontinuation", "D3", "D4", "D5")


def bracket(ref, quote, head=40, tail=24, maxlen=1400):
    """Fallback for PDF text layers with margin line numbers or hyphen breaks inside a sentence: locate the quote's
    first `head` and last `tail` characters (normalised) and return the render substring between them, if short."""
    from textrep import render
    t = render(ref)
    nt, idx = find_span._norm(t)
    nq = find_span._norm(quote)[0].strip()
    if len(nq) < head + tail:
        return None
    i = nt.find(nq[:head])
    if i < 0:
        return None
    j = nt.find(nq[-tail:], i)
    if j < 0 or j - i > maxlen:
        return None
    s, e = idx[i], idx[j + tail - 1] + 1
    return t[s:e]


def main(located, srcmap, out):
    L = json.load(open(located, encoding="utf-8"))["trials"]
    M = json.load(open(srcmap, encoding="utf-8"))
    res, miss, n = {}, [], 0
    for trial, v in L.items():
        for k in KEYS:
            for q in v.get(k) or []:
                n += 1
                ref = M.get(trial, {}).get(q.get("source"))
                sp = None
                if ref:
                    try:
                        sp = find_span.locate(ref, q["quote"])
                    except Exception:
                        sp = None
                how = "verbatim"
                if not sp and ref:
                    sp = bracket(ref, q["quote"]); how = "bracketed (render has line numbers / hyphen breaks inside; REVIEW)"
                if sp:
                    res.setdefault(trial, {}).setdefault(k, []).append({"ref": ref, "span": sp, "note": q.get("note", ""), "match": how})
                else:
                    miss.append((trial, k, q.get("source"), ref, q["quote"][:90]))
    json.dump({"matched": res, "unmatched": miss}, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"quotes {n}; matched {n - len(miss)}; unmatched {len(miss)}")
    for m in miss:
        print("  UNMATCHED", m)


if __name__ == "__main__":
    main(*sys.argv[1:4])
