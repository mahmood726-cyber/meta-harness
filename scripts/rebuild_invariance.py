"""Rebuild invariance: after regenerating pages, prove -- as a test, not an inspection -- that no page got quieter anywhere and
louder in exactly the expected places. Regeneration erases retractions unless something checks; this is the something.

For every docs/reviews/<slug>/index.html, against a base ref (default: merge-base with origin/main):
  - the honest-state ratchet (harness.honest_ratchet.compare / compare_blocks, the same code the gate runs) must report no problem;
  - the set of tracked honest-state blocks (harness.honest_ratchet.blocks) on the base page must be a SUBSET of the new page's;
  - the blocks ADDED are listed by class and text prefix, so "louder in exactly one place" is checkable by eye and by --expect-added;
  - the rendered text minus the added blocks must be identical to the base page's rendered text (nothing else changed), or the
    differing lines are printed.
Named pages of concern are always listed first (ARNI = sacubitril-valsartan-hfref; the two withdrawn HFpEF pages) and the primary
pooled state (k, estimate) before/after is printed for every page.

Usage: python scripts/rebuild_invariance.py [--base REF] [--expect-added N] [--json out.json]
Exit 0 iff every page passes; the report is the evidence either way."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import honest_ratchet as hr  # noqa: E402

NAMED_FIRST = ("sacubitril-valsartan-hfref", "dapagliflozin-hfpef-hosp", "empagliflozin-hfpef-hosp", "glp1-ra-mace-t2d")


def _git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, stdin=subprocess.DEVNULL)


def _show(ref, path):
    r = _git("show", f"{ref}:{path}")
    return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None


def _primary_state(review_json_text):
    try:
        r = json.loads(review_json_text)
        o = next(x for x in r.get("outcomes", []) if x.get("primary"))
        res = o.get("result") or {}
        return {"k": res.get("k"), "estimate": res.get("estimate"), "pool_refused": (res.get("pool_refused") or {}).get("code"),
                "withdrawn": bool(r.get("withdrawn")), "release_status": (r.get("release_status") or {}).get("status")}
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__}


def _strip_blocks(text_html, block_shas):
    """Rendered text of a page with the named blocks removed (by their text)."""
    out = hr._rendered_text(text_html)
    for b in block_shas:
        out = out.replace(hr._rendered_text(b["text"]) if "<" in b["text"] else b["text"], "")
    return " ".join(out.split())


def main(argv=None):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None)
    ap.add_argument("--expect-added", type=int, default=None, help="every page must add exactly this many tracked blocks")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    base, source, err = hr._resolve_base(ROOT, a.base)
    if not base:
        print(f"REFUSED: no base ref ({err})"); return 2
    acks, ack_problems = hr._load_acknowledgements(ROOT)
    pages = sorted(p for p in (ROOT / "docs" / "reviews").iterdir() if (p / "index.html").exists())
    order = sorted(pages, key=lambda p: (p.name not in NAMED_FIRST, NAMED_FIRST.index(p.name) if p.name in NAMED_FIRST else 0, p.name))
    report = {"base": base, "base_source": source, "ack_problems": ack_problems, "pages": [], "expect_added": a.expect_added}
    all_ok = True
    for p in order:
        slug = p.name
        rel_html = f"docs/reviews/{slug}/index.html"; rel_rev = f"docs/reviews/{slug}/review.json"
        base_html, new_html = _show(base, rel_html), (p / "index.html").read_text(encoding="utf-8")
        base_rev, new_rev = _show(base, rel_rev), (p / "review.json").read_text(encoding="utf-8")
        row = {"slug": slug, "named": slug in NAMED_FIRST, "base_present": base_html is not None,
               "primary_before": _primary_state(base_rev) if base_rev else None, "primary_after": _primary_state(new_rev)}
        if base_html is None:
            row["verdict"] = "NEW_PAGE"; report["pages"].append(row); continue
        bb, nb = hr.blocks(base_html), hr.blocks(new_html)
        problems = hr.compare(base_html, new_html, acks, rel_html) + hr.compare_blocks(bb, nb, acks, rel_html)   # the gate's own two checks
        key = lambda b: hashlib.sha256(" ".join(hr._rendered_text(b["text"]).split()).encode()).hexdigest()  # noqa: E731
        bset, nset = {key(b): b for b in bb}, {key(b): b for b in nb}
        lost = [bset[k] for k in bset if k not in nset]
        added = [nset[k] for k in nset if k not in bset]
        # everything except the added blocks must read the same
        base_text = " ".join(hr._rendered_text(base_html).split())
        new_text = " ".join(hr._rendered_text(new_html).split())
        for b in added:
            new_text = new_text.replace(" ".join(hr._rendered_text(b["text"]).split()), "")
        new_text = " ".join(new_text.split())
        other_changes = []
        if base_text != new_text:
            sm = difflib.SequenceMatcher(None, base_text, new_text)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag != "equal":
                    other_changes.append({"op": tag, "before": base_text[i1:i2][:160], "after": new_text[j1:j2][:160]})
        row.update({"ratchet_problems": problems, "blocks_before": len(bb), "blocks_after": len(nb),
                    "lost_blocks": [{"class": b.get("cls") or b.get("class"), "text": " ".join(hr._rendered_text(b["text"]).split())[:120]} for b in lost],
                    "added_blocks": [{"class": b.get("cls") or b.get("class"), "text": " ".join(hr._rendered_text(b["text"]).split())[:120]} for b in added],
                    "other_text_changes": other_changes[:12]})
        ok = not problems and not lost and not other_changes and (a.expect_added is None or len(added) == a.expect_added)
        if (row["primary_before"] or {}).get("k") != (row["primary_after"] or {}).get("k") or (row["primary_before"] or {}).get("estimate") != (row["primary_after"] or {}).get("estimate"):
            ok = False; row["primary_changed"] = True
        row["verdict"] = "PASS" if ok else "FAIL"
        all_ok &= ok
        report["pages"].append(row)
        flag = "  " if ok else "!!"
        print(f"{flag} {slug:<44} ratchet={len(problems)} lost={len(lost)} added={len(added)} other_changes={len(other_changes)} "
              f"primary k {row['primary_before'] and row['primary_before'].get('k')}->{row['primary_after'].get('k')} "
              f"withdrawn {row['primary_before'] and row['primary_before'].get('withdrawn')}->{row['primary_after'].get('withdrawn')}")
        for b in lost:
            print(f"      LOST   [{b.get('cls') or b.get('class')}] {' '.join(hr._rendered_text(b['text']).split())[:110]}")
        for b in added:
            print(f"      ADDED  [{b.get('cls') or b.get('class')}] {' '.join(hr._rendered_text(b['text']).split())[:110]}")
        for c in other_changes[:4]:
            print(f"      OTHER  {c['op']}: {c['before'][:70]!r} -> {c['after'][:70]!r}")
    report["all_pass"] = all_ok
    n = len([r for r in report["pages"] if r.get("verdict") in ("PASS", "FAIL")])
    print(f"REBUILD INVARIANCE vs {base[:12]} ({source}): {sum(1 for r in report['pages'] if r.get('verdict') == 'PASS')} of {n} pages PASS; "
          f"acknowledgement file problems: {len(ack_problems)}")
    if a.json:
        Path(a.json).write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
