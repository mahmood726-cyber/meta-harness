"""Rebuild invariance: after regenerating pages, prove -- as a test, not an inspection -- that no page got quieter anywhere and
louder in exactly the expected place. Regeneration erases retractions unless something checks; this is the something.

For every <docs>/reviews/<slug>/index.html, against a base ref (default: merge-base with origin/main):
  - the honest-state ratchet (harness.honest_ratchet.compare / compare_blocks, the code the gate runs) must report no problem;
  - the tracked honest-state blocks (harness.honest_ratchet.blocks) on the base page must be a SUBSET of the new page's;
  - with --expect-added N the page must add exactly N tracked blocks; with --added-text T the single added block must BEGIN with T
    and with --added-marker M the raw html must carry exactly one more occurrence of M than the base -- a count is satisfiable by the
    wrong block, an identifier is not;
  - --exception slug=N:reason declares a page allowed to add N blocks instead (printed as an exception, never a loosened threshold);
  - the rendered text minus the added blocks must equal the base page's rendered text (nothing else changed), else the differing
    spans are printed;
  - the primary outcome's k / estimate / pool_refused / withdrawn state must be unchanged.
Named pages (--name, plus the built-in list: ARNI = sacubitril-valsartan-hfref, the two withdrawn HFpEF pages, glp1) are always
printed first, whatever the total says.

Usage: python scripts/rebuild_invariance.py [--base REF] [--docs DIR] [--expect-added N] [--added-text T] [--added-marker M]
                                           [--exception slug=N:reason ...] [--name slug ...] [--json out.json]
Exit 0 iff every page passes; the report is the evidence either way."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import re
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import honest_ratchet as hr  # noqa: E402

NAMED_FIRST = ["sacubitril-valsartan-hfref", "dapagliflozin-hfpef-hosp", "empagliflozin-hfpef-hosp", "glp1-ra-mace-t2d"]


def _show(ref, path):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{path}"], capture_output=True, stdin=subprocess.DEVNULL)
    return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None


def _norm(text):
    return " ".join(text.split())


def _all_outcomes_state(review_json_text):
    """{outcome name: (k, estimate, pool_refused code)} for EVERY outcome -- a moved pool anywhere is a finding."""
    try:
        r = json.loads(review_json_text)
        return {o.get("name"): ((o.get("result") or {}).get("k"), (o.get("result") or {}).get("estimate"),
                                ((o.get("result") or {}).get("pool_refused") or {}).get("code")) for o in r.get("outcomes", [])}
    except Exception:  # noqa: BLE001
        return None


def _parity_relation(slug):
    try:
        d = json.load(open(ROOT / "docs" / "parity.json", encoding="utf-8"))
        rows = d.get("rows") or d.get("topics") or d
        if isinstance(rows, dict):
            e = rows.get(slug)
        else:
            e = next((x for x in rows if x.get("slug") == slug), None)
        return {k: e.get(k) for k in ("status", "relation", "our_k", "their_k") if isinstance(e, dict) and k in e} if e else None
    except Exception:  # noqa: BLE001
        return None


def _primary_state(review_json_text):
    try:
        r = json.loads(review_json_text)
        o = next(x for x in r.get("outcomes", []) if x.get("primary"))
        res = o.get("result") or {}
        return {"k": res.get("k"), "estimate": res.get("estimate"), "pool_refused": (res.get("pool_refused") or {}).get("code"),
                "withdrawn": bool(r.get("withdrawn")), "release_status": (r.get("release_status") or {}).get("status")}
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__}


def check_page(slug, base_html, new_html, base_rev, new_rev, acks, expect_added, added_text, added_marker, exceptions):
    rel_html = f"docs/reviews/{slug}/index.html"
    bb, nb = hr.blocks(base_html), hr.blocks(new_html)
    problems = hr.compare(base_html, new_html, acks, rel_html) + hr.compare_blocks(bb, nb, acks, rel_html)
    key = lambda b: hashlib.sha256(_norm(b["text"]).encode()).hexdigest()  # noqa: E731
    bset, nset = {key(b): b for b in bb}, {key(b): b for b in nb}
    lost = [bset[k] for k in bset if k not in nset]
    added = [nset[k] for k in nset if k not in bset]
    base_text, new_text = _norm(hr._rendered_text(base_html)), _norm(hr._rendered_text(new_html))
    for b in added:
        new_text = _norm(new_text.replace(_norm(b["text"]), ""))
    # Digests rendered on the page (review_sha256, release_sha256, html_sha256, blob ids, certificate fields) MUST move when the
    # review core changes; they are counted separately and are not content. Everything else that differs is a finding.
    hexre = re.compile(r"[0-9a-f]{12,64}")     # rendered digests and blob ids; masked before the content diff
    base_hex, new_hex = hexre.findall(base_text), hexre.findall(new_text)
    digest_tokens_changed = sum(1 for a, b in zip(base_hex, new_hex) if a != b) + abs(len(base_hex) - len(new_hex))
    base_masked, new_masked = hexre.sub("<HEX>", base_text), hexre.sub("<HEX>", new_text)
    other = []
    if base_masked != new_masked:
        sm = difflib.SequenceMatcher(None, base_masked.split(" "), new_masked.split(" "), autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                other.append({"op": tag, "before": " ".join(base_masked.split(" ")[i1:i2])[:160], "after": " ".join(new_masked.split(" ")[j1:j2])[:160]})
    pb, pa = (_primary_state(base_rev) if base_rev else None), _primary_state(new_rev)
    primary_changed = bool(pb) and any((pb or {}).get(k) != pa.get(k) for k in ("k", "estimate", "pool_refused", "withdrawn"))
    ob, oa = (_all_outcomes_state(base_rev) if base_rev else None), _all_outcomes_state(new_rev)
    moved_outcomes = sorted(n for n in set((ob or {}) | (oa or {})) if (ob or {}).get(n) != (oa or {}).get(n)) if ob is not None else []
    want = exceptions.get(slug, {}).get("n", expect_added)
    reasons = []
    if problems:
        reasons.append(f"ratchet: {len(problems)} problem(s)")
    if lost:
        reasons.append(f"{len(lost)} tracked block(s) LOST")
    if other:
        reasons.append(f"{len(other)} other text change(s)")
    if primary_changed:
        reasons.append("primary state changed")
    if moved_outcomes:
        reasons.append(f"pool moved on outcome(s): {moved_outcomes}")
    if want is not None and len(added) != want:
        reasons.append(f"added {len(added)} block(s), expected {want}")
    if added_text and want == 1 and len(added) == 1 and not _norm(added[0]["text"]).startswith(added_text):
        reasons.append(f"the single added block is not the expected one (begins {_norm(added[0]['text'])[:60]!r})")
    if added_marker and want:
        # the identified block appears exactly once more than on the base, whatever else an exception allows the page to add
        delta = new_html.count(added_marker) - base_html.count(added_marker)
        if delta != 1:
            reasons.append(f"marker {added_marker!r} occurs {delta:+d} times vs base, expected +1")
    return {"slug": slug, "named": slug in NAMED_FIRST, "exception": exceptions.get(slug), "ratchet_problems": problems,
            "blocks_before": len(bb), "blocks_after": len(nb),
            "lost_blocks": [{"class": b["cls"], "text": _norm(b["text"])[:120]} for b in lost],
            "added_blocks": [{"class": b["cls"], "text": _norm(b["text"])[:120]} for b in added],
            "other_text_changes": other[:12], "digest_tokens_changed": digest_tokens_changed, "primary_before": pb, "primary_after": pa, "primary_changed": primary_changed,
            "outcomes_moved": moved_outcomes, "parity_relation": _parity_relation(slug),
            "verdict": "PASS" if not reasons else "FAIL", "reasons": reasons}


def main(argv=None):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None)
    ap.add_argument("--docs", default=str(ROOT / "docs"), help="docs directory to read the NEW pages from (default: the repo's)")
    ap.add_argument("--expect-added", type=int, default=None)
    ap.add_argument("--added-text", default=None, help="the single added block must begin with this rendered text")
    ap.add_argument("--added-marker", default=None, help="raw-html marker that must occur exactly expect-added more times than on the base")
    ap.add_argument("--exception", action="append", default=[], help="slug=N:reason -- this page may add N blocks (declared, with a reason)")
    ap.add_argument("--name", action="append", default=[], help="always list this slug first")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    for n in a.name:
        if n not in NAMED_FIRST:
            NAMED_FIRST.append(n)
    exceptions = {}
    for e in a.exception:
        slug, rest = e.split("=", 1); n, _, reason = rest.partition(":")
        exceptions[slug] = {"n": int(n), "reason": reason or "(no reason given)"}
    base, source, err = hr._resolve_base(ROOT, a.base)
    if not base:
        print(f"REFUSED: no base ref ({err})"); return 2
    acks, ack_problems = hr._load_acknowledgements(ROOT)
    docs = Path(a.docs)
    pages = sorted(p for p in (docs / "reviews").iterdir() if (p / "index.html").exists())
    order = sorted(pages, key=lambda p: (p.name not in NAMED_FIRST, NAMED_FIRST.index(p.name) if p.name in NAMED_FIRST else 0, p.name))
    report = {"base": base, "base_source": source, "docs": str(docs), "ack_problems": ack_problems, "expect_added": a.expect_added,
              "added_text": a.added_text, "added_marker": a.added_marker, "exceptions": exceptions, "pages": []}
    for p in order:
        slug = p.name
        base_html = _show(base, f"docs/reviews/{slug}/index.html")
        base_rev = _show(base, f"docs/reviews/{slug}/review.json")
        if base_html is None:
            report["pages"].append({"slug": slug, "verdict": "NEW_PAGE"}); continue
        row = check_page(slug, base_html, (p / "index.html").read_text(encoding="utf-8"), base_rev,
                         (p / "review.json").read_text(encoding="utf-8") if (p / "review.json").exists() else "{}",
                         acks, a.expect_added, a.added_text, a.added_marker, exceptions)
        report["pages"].append(row)
        flag = "  " if row["verdict"] == "PASS" else "!!"
        exc = f" [EXCEPTION n={row['exception']['n']}: {row['exception']['reason']}]" if row["exception"] else ""
        print(f"{flag} {slug:<44} ratchet={len(row['ratchet_problems'])} lost={len(row['lost_blocks'])} added={len(row['added_blocks'])} "
              f"other={len(row['other_text_changes'])} digests={row['digest_tokens_changed']} outcomes_moved={len(row['outcomes_moved'])} primary k {(row['primary_before'] or {}).get('k')}->{row['primary_after'].get('k')} "
              f"withdrawn {(row['primary_before'] or {}).get('withdrawn')}->{row['primary_after'].get('withdrawn')}{exc}")
        for r in row["reasons"]:
            print(f"      REASON {r}")
        for b in row["lost_blocks"]:
            print(f"      LOST   [{b['class']}] {b['text'][:110]}")
        for b in row["added_blocks"]:
            print(f"      ADDED  [{b['class']}] {b['text'][:110]}")
        for c in row["other_text_changes"][:4]:
            print(f"      OTHER  {c['op']}: {c['before'][:70]!r} -> {c['after'][:70]!r}")
    judged = [r for r in report["pages"] if r.get("verdict") in ("PASS", "FAIL")]
    passed = [r["slug"] for r in judged if r["verdict"] == "PASS"]
    failed = [r["slug"] for r in judged if r["verdict"] == "FAIL"]
    report["all_pass"] = not failed and not ack_problems
    print(f"REBUILD INVARIANCE vs {base[:12]} ({source}): {len(passed)} of {len(judged)} pages PASS"
          + (f"; FAIL: {failed}" if failed else "") + f"; acknowledgement-file problems: {len(ack_problems)}")
    print("named pages: " + ", ".join(f"{r['slug']}={r['verdict']}" for r in judged if r.get("named")))
    if a.json:
        Path(a.json).write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
