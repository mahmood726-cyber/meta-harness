"""Inventory of the RapidMeta-style transparent tabs on every served review page (presentation only; reads committed files).

For each served topic (docs/reviews/<slug>/index.html) and each REQUIRED tab, report
  COMPLETE  the page has a tab of that name and every required element is found in it,
  PRESENT   the content is found on the page but not as its own tab, or some elements are missing (named),
  MISSING   none of the elements is found anywhere on the page,
  REASONED  the tab exists and every missing element carries a stated reason on the page (class="tab-reason").

Checks are deterministic: regex over the RENDERED text (tags stripped, entities unescaped, whitespace collapsed), plus
data checks against the review's own committed objects (every screening record id, every pooled trial id and PMID/NCT,
every committed notice for the slug). A marker check finds that an element is shown, not that it is correct.

usage: python scripts/review_tab_inventory.py [--json out.json] [--md out.md] [--root .]
"""
from __future__ import annotations

import argparse
import os
import html as H
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUIRED = [  # (id, label) -- the order and names of the required tabs
    ("protocol", "Protocol"), ("search", "Search"), ("screening", "Screening"), ("included", "Included studies"),
    ("extraction", "Data extraction"), ("riskofbias", "Risk of bias & GRADE"), ("analysis", "Analysis"),
    ("results", "Results & conclusions"), ("comparator", "Comparison with published meta-analysis"),
    ("changes", "Changes & signatures"), ("reproduce", "Reproduce"),
]
# where each required tab's content lives on the legacy (pre-restructure) page; used only when no dedicated tab exists
LEGACY = {"protocol": ["protocol"], "search": ["search", "screening"], "screening": ["screening"],
          "included": ["screening", "outcomes"], "extraction": ["outcomes", "harms"], "riskofbias": ["riskofbias"],
          "analysis": ["outcomes", "manuscript"], "results": ["outcomes", "manuscript"], "comparator": ["comparator"],
          "changes": ["reproduction", "overview"], "reproduce": ["reproduction", "verify"]}
# the page's own tab id for each required tab (the page kept its legacy ids where a tab only gained content)
PAGE_ID = {"results": "outcomes", "reproduce": "reproduction"}
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")


def flat(s: str) -> str:
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def tabs_of(page: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r'<section class="tab"[^>]*id="tab-([a-z0-9-]+)"[^>]*>(.*?)(?=<section class="tab"|</main>)', page, re.S):
        out[m.group(1)] = m.group(2)
    return out


def g1_decision_ids(root: Path) -> list[str]:
    d = json.loads((root / "registry" / "g1_decisions.json").read_text(encoding="utf-8"))
    return [x["id"] for x in d["decisions"]]


def pooled_trials(review: dict, shown_only: bool = False) -> list[dict]:
    """Every pooled trial row; with shown_only, only rows of outcomes the publication gate lets carry a numerical
    surface (an incomplete harm ledger or a suppressed pool is served only through its gated block)."""
    rows = []
    for o in review.get("outcomes") or []:
        if shown_only and withheld(o):
            continue
        for t in o.get("trials") or []:
            rows.append(t)
    return rows


def withheld(o: dict) -> bool:
    from harness import harms   # the gate's own rule (harness/gate.py check_harms_synthesis_gated)
    res = o.get("result") or {}
    return bool(harms.synthesis_incomplete(o) or res.get("suppressed_incompatible") or res.get("harms_synthesis_suppressed"))


def ids_of(t: dict) -> tuple[str | None, str | None]:
    s = json.dumps({k: t.get(k) for k in ("id", "label", "pmid", "nct", "trial_family_id")})
    pm = re.search(r"PMID[ :]*(\d{6,9})|\"pmid\": \"?(\d{6,9})", s)
    nct = re.search(r"NCT\d{8}", s)
    return (next(g for g in pm.groups() if g) if pm else None), (nct.group(0) if nct else None)


def check(slug: str, page: str, review: dict, notices: list, decisions: list[str]) -> dict:
    tabs = tabs_of(page)
    res = {}
    for tid, label in REQUIRED:
        pid = PAGE_ID.get(tid, tid)
        dedicated = pid in tabs and _is_new(page)
        full = tabs[pid] if dedicated else "".join(tabs.get(x, "") for x in LEGACY[tid])
        # markers are checked on the tab's CONTENT, with its stated-reason blocks removed: a reason's own words never
        # satisfy a marker, and a reason for one outcome does not hide content shown for another
        src = _REASON_BLOCK.sub(" ", full)
        txt = flat(src)
        el = {}
        if tid == "protocol":
            el["PICO"] = all(re.search(w, txt, re.I) for w in (r"\bpopulation\b", r"\bintervention\b", r"\bcompar", r"\boutcome"))
            # structural: the dated-amendments table, or (legacy page) an Amendment heading with a date
            el["amendments with dates"] = (bool(re.search(r"id='protocol-amendments'>[^<]*</h4><table", src)) if dedicated
                                           else bool(re.search(r"amendment[^.]{0,80}20\d\d-\d\d-\d\d", txt, re.I)))
            el["decisions D1-D12"] = all(d in txt for d in decisions)
        elif tid == "search":
            el["databases"] = "PubMed" in txt and "ClinicalTrials.gov" in txt
            qs = [q for src in (review.get("search") or {}).get("sources") or [] if isinstance(src, dict)
                  for q in src.get("queries") or []]
            qshown = sum(1 for q in qs if flat(str(q))[:60] in txt)
            el[f"queries ({qshown}/{len(qs)})"] = bool(qs) and qshown == len(qs)
            el["dates"] = bool(DATE.search(txt))
            # data check: the search's recorded identification count is shown on the tab
            n_rec = (review.get("search") or {}).get("n_records")
            el["counts"] = (n_rec is not None and bool(re.search(r"(?<![\d.])" + re.escape(str(n_rec)) + r"(?![\d.])", txt)))
            # dedicated tab: identification count + a link to the one PRISMA flow (Screening); legacy page: the words
            el["PRISMA flow"] = (bool(re.search(r"id='search-prisma'.*?href='#tab-screening'", src, re.S)) if dedicated
                                 else ("PRISMA" in txt and bool(re.search(r"identified", txt, re.I))))
        elif tid == "screening":
            recs = ((review.get("screening") or {}).get("records") or [])
            ids = [str(r.get("id")) for r in recs if r.get("id")]
            shown = sum(1 for i in ids if i in txt)
            el[f"every record ({shown}/{len(ids)})"] = bool(ids) and shown == len(ids)
            el["decision + rule"] = bool(re.search(r"\b(INCLUDE|X\d+|I\d+)\b", txt))
            el["span"] = bool(re.search(r"span|verbatim|“|\"", txt, re.I))
            el["dual-reviewer agreement"] = bool(re.search(r"dual|second reviewer|independent screen", txt, re.I)) and bool(
                re.search(r"kappa|κ|agree", txt, re.I))
        elif tid == "included":
            tr = pooled_trials(review)
            pairs = [ids_of(t) for t in tr]
            uniq = {(p, n) for p, n in pairs}
            shown = sum(1 for p, n in uniq if (p is None or p in txt) and (n is None or n in txt))
            el[f"every pooled trial with PMID/NCT ({shown}/{len(uniq)})"] = bool(uniq) and shown == len(uniq)
        elif tid == "extraction":
            tr = pooled_trials(review, shown_only=True)   # every pooled row shown: effect, arm counts or means
            held = [o.get("name") for o in review.get("outcomes") or [] if withheld(o)]
            el[f"withheld outcomes stated ({sum(1 for n in held if flat(str(n)) in flat(full))}/{len(held)})"] = all(
                flat(str(n)) in flat(full) for n in held)
            spans = sum(1 for t in tr if _span(t) and flat(_span(t))[:30] in txt)
            el[f"source span per pooled number ({spans}/{len(tr)})"] = bool(tr) and spans == len(tr)
            el["digest"] = bool(HEX64.search(txt))
            el["extractor or recorded call"] = bool(re.search(r"\b(extractor|regex|model call|recorded call|mc-[0-9a-f]{8})", txt, re.I))
        elif tid == "riskofbias":
            el["RoB 2 per trial"] = bool(re.search(r"randomi[sz]ation process|deviations from intended|D1\b.*D5\b", txt, re.I))
            el["GRADE"] = "GRADE" in txt
            # structural: only a RECORDED sign-off counts (the renderer marks it); naming D11 is not a sign-off
            el["D11 reproducible-AI sign-off"] = bool(re.search(r"data-d11-signoff=['\"]RECORDED", src))
        elif tid == "analysis":
            el["forest plot"] = "<svg" in src and bool(re.search(r"forest", src, re.I))
            el["model"] = bool(re.search(r"REML|Paule|DerSimonian|random[- ]effects", txt, re.I))
            el["heterogeneity"] = bool(re.search(r"τ²|tau|I²|I2\b", txt))
            el["sensitivity"] = bool(re.search(r"sensitivity|leave-one-out", txt, re.I))
            el["HKSJ rule"] = bool(re.search(r"HKSJ|Hartung|Knapp", txt))
        elif tid == "results":
            el["pooled estimate with CI"] = bool(re.search(r"95% CI|\(\d\.\d+[–-]\d\.\d+\)|\d\.\d+ to \d\.\d+", txt))
            el["conclusions"] = bool(re.search(r"conclusion|interpretation", txt, re.I))
        elif tid == "comparator":
            el["published meta-analysis named"] = bool(re.search(r"comparator|published meta", txt, re.I))
            el["G1 panel"] = bool(re.search(r"comparator panel|\bG1\b", txt, re.I))
        elif tid == "changes":
            mine = [n for n in notices if n.get("slug") == slug]
            shown = sum(1 for n in mine if (n.get("outcome") or "") in txt and (n.get("when_utc") or "")[:10] in txt)
            el[f"every committed notice ({shown}/{len(mine)})"] = shown == len(mine)
            el["signatures"] = (not mine) or bool(re.search(r"SEEN_AND_SIGNED|signed", txt, re.I))
            el["withdrawals/reinstatements stated"] = bool(re.search(r"withdraw|reinstat|no withdrawals", txt, re.I))
        elif tid == "reproduce":
            el["one-command replay"] = bool(re.search(r"python [\w./-]+\.py", txt))
            el["certificate hashes"] = bool(HEX64.search(txt))
            el["bundle download"] = bool(re.search(r"""href=["'][^"']*(\.zip|BUNDLE\.json)["']""", src))
        # an element the tab answers with a stated reason is REASONED, never COMPLETE -- the reason's own words must not
        # satisfy the element's marker (a D11 reason says "D11 ... sign-off"; that is not a sign-off)
        reasons = {k for k in el if dedicated and not el[k] and _has_reason(full, k)}
        found = sum(el.values())
        if dedicated and found == len(el):
            st = "COMPLETE"
        elif dedicated and all(v or k in reasons for k, v in el.items()):
            st = "REASONED"
        elif found == 0:
            st = "MISSING"
        else:
            st = "PRESENT"
        res[tid] = {"status": st, "dedicated_tab": bool(dedicated), "elements": el, "reasoned": sorted(reasons)}
    return res


def _span(t: dict) -> str:   # the passage a pooled number was read from: the bound result span, else the row's source text
    return str(t.get("endpoint_result_span") or t.get("source") or "")


def _is_new(page: str) -> bool:   # the restructured page declares its tab contract
    return "<meta name='tab-contract' content='rapidmeta-v1'>" in page


_REASON_BLOCK = re.compile(r'<(p|span) class="tab-reason"[^>]*>.*?</\1>', re.S)


def _has_reason(src: str, element: str) -> bool:
    key = re.sub(r" \(.*\)$", "", element)
    return bool(re.search(r'class="tab-reason"[^>]*data-element="' + re.escape(key) + '"', src))


def run(root: Path) -> dict:
    decisions = g1_decision_ids(root)
    notices = json.loads((root / "docs" / "result_changes.json").read_text(encoding="utf-8"))["notices"]
    out = {}
    for d in sorted((root / "docs" / "reviews").iterdir()):
        if not (d / "index.html").is_file():
            continue
        page = (d / "index.html").read_text(encoding="utf-8")
        review = json.loads((d / "review.json").read_text(encoding="utf-8"))
        out[d.name] = check(d.name, page, review, notices, decisions)
    return out


def to_md(inv: dict) -> str:
    sym = {"COMPLETE": "✅ complete", "REASONED": "☑️ reasoned", "PRESENT": "🟡 present", "MISSING": "❌ missing"}
    head = "| topic | " + " | ".join(l for _, l in REQUIRED) + " |\n|---|" + "---|" * len(REQUIRED) + "\n"
    rows = "".join(f"| {s} | " + " | ".join(sym[v[t]['status']] for t, _ in REQUIRED) + " |\n" for s, v in inv.items())
    tot = {t: {k: sum(1 for v in inv.values() if v[t]["status"] == k) for k in sym} for t, _ in REQUIRED}
    summ = "| tab | complete | reasoned | present | missing |\n|---|---|---|---|---|\n" + "".join(
        f"| {l} | {tot[t]['COMPLETE']} | {tot[t]['REASONED']} | {tot[t]['PRESENT']} | {tot[t]['MISSING']} |\n" for t, l in REQUIRED)
    miss = {}
    for s, v in inv.items():
        for t, l in REQUIRED:
            for k, ok in v[t]["elements"].items():
                if not ok:
                    miss.setdefault((l, re.sub(r" \(.*\)$", "", k)), []).append(s)
    gaps = "| tab | element not shown | topics |\n|---|---|---|\n" + "".join(
        f"| {l} | {k} | {len(ss)}{'' if len(ss) > 6 else ': ' + ', '.join(ss)} |\n" for (l, k), ss in sorted(miss.items()))
    return summ + "\n" + gaps + "\n" + head + rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--json")
    ap.add_argument("--md")
    a = ap.parse_args()
    inv = run(Path(a.root))
    if a.json:
        Path(a.json).write_text(json.dumps(inv, indent=1, ensure_ascii=False), encoding="utf-8")
    md = to_md(inv)
    if a.md:
        Path(a.md).write_text(md, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(md.split("\n\n")[0])
    print(f"topics: {len(inv)}")


if __name__ == "__main__":
    main()
