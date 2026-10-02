"""Render the G1 scoreboard (docs/g1/index.html) from the topic tracker files in outputs/k_gap/g1/.

GOAL 1: match published open-access meta-analyses trial-for-trial. The tracker files are written by the k-gap lane's
scripts/g1_tracker.py (schema 1, kgap/G1_INTERFACES.md section 4); outputs/k_gap/g1/SOURCE.json records which commit
and blobs this tree's copy came from. This page is GENERATED from those files and nothing else; `--check` refuses a
committed page that differs from a fresh render.

G1 MATCHED (the tracker's own definition) = every eligible comparator trial matched AND every matched trial verified
(PRIMARY / TWO_SOURCE, never comparator-only) AND the result agrees on the same trials AND every divergence is named.
The page prints the lane's status AND recomputes each criterion here from the same file:
  ALL_ELIGIBLE_MATCHED  k_matched == N_eligible > 0
  MATCHED_ARE_VERIFIED  every trial in our pool counts: PRIMARY, or TWO_SOURCE with a recorded independent pair that
                        holds no comparator id (an unknown pair does not count: fail-closed)
  RESULT_AGREES         same_trials verdict is AGREE
  DIVERGENCES_NAMED     every eligible trial outside our pool, and every per-trial DISAGREE, is named (a named
                        difference, a comparator finding, or a stated disagreement side)
A topic counts as MATCHED on this page only when BOTH agree; a disagreement is printed, never reconciled.

Usage: python scripts/render_g1_tracker.py [--check]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("outputs") / "k_gap" / "g1"
OUT = Path("docs") / "g1" / "index.html"
# The four G1 focus topics (decision 2026-10-02); every other topic file present is shown after them.
G1_FOCUS = ("glp1-ra-mace-t2d", "semaglutide-obesity-weight", "noac-vs-warfarin-af-stroke",
            "tocilizumab-covid19-mortality")
CRITERIA = ("ALL_ELIGIBLE_MATCHED", "MATCHED_ARE_VERIFIED", "RESULT_AGREES", "DIVERGENCES_NAMED")


def _ids(value) -> set[str]:
    vals = value if isinstance(value, (list, tuple, set)) else [value]
    out = set()
    for v in vals:
        s = re.sub(r"^(pmid[:\s]*|doi[:\s]*)", "", str(v or "").strip().lower())
        if s:
            out.add(s)
    return out


def pair_of(trial: dict) -> set[str] | None:
    raw = trial.get("independent_pair_ids")
    if raw is None:
        raw = (trial.get("verification") or {}).get("independent_pair_ids")
    return _ids(raw) if raw else None


def counts(trial: dict, comparator_ids: set[str]) -> tuple[bool, str]:
    route = trial.get("route")
    if route == "PRIMARY":
        return True, "primary source"
    if route == "TWO_SOURCE":
        pair = pair_of(trial)
        if pair is None:
            return False, "TWO_SOURCE but the independent pair is not recorded: not counted (fail-closed)"
        if pair & comparator_ids:
            return False, "TWO_SOURCE pair includes the comparator: not counted (anti-circularity)"
        return True, "two independent metas, comparator excluded"
    return False, f"{route or 'no route'}: not counted"


def _verdict(st: dict):
    v = st.get("verdict") if isinstance(st, dict) else None
    return v.get("verdict") if isinstance(v, dict) else v


def _named(rec: dict) -> set[str]:
    rows = (rec.get("named_differences") or []) + (rec.get("comparator_findings") or [])
    return {str(d["trial"]).strip().lower() for d in rows if d.get("trial")}


def recompute(rec: dict) -> dict:
    """The four criteria and the per-trial counting, recomputed from the tracker file."""
    comparator_ids = _ids([rec.get("comparator_pmid"), rec.get("comparator_doi")])
    rows = []
    for t in rec.get("trials") or []:
        ok, why = counts(t, comparator_ids)
        rows.append({"trial": t, "counted": ok, "why": why})
    named = _named(rec)
    n_el, k = rec.get("N_eligible"), rec.get("k_matched")
    pooled = [r for r in rows if r["trial"].get("in_our_pool")]
    unnamed = []
    for r in rows:
        t = r["trial"]
        outside = not t.get("in_our_pool")
        disagree = str(t.get("agreement_with_comparator_row") or "").startswith("DISAGREE")
        label = str(t.get("label") or "").strip().lower()
        if (outside or disagree) and label not in named and not t.get("disagreement_side"):
            unnamed.append(t.get("label"))
    crit = {
        "ALL_ELIGIBLE_MATCHED": bool(isinstance(n_el, int) and n_el > 0 and k == n_el),
        "MATCHED_ARE_VERIFIED": bool(pooled) and all(r["counted"] for r in pooled),
        "RESULT_AGREES": _verdict(rec.get("same_trials") or {}) == "AGREE",
        "DIVERGENCES_NAMED": not unnamed,
    }
    return {"rows": rows, "criteria": crit, "matched": all(crit.values()), "unnamed": unnamed,
            "g1_count": sum(r["counted"] for r in rows)}


def _e(x) -> str:
    return html.escape("" if x is None else str(x))


def _fmt_pool(p) -> str:
    if not isinstance(p, dict) or p.get("estimate") is None:
        return "not pooled"
    lo, hi = p.get("ci_low"), p.get("ci_high")
    ci = f" ({lo:.2f} to {hi:.2f})" if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) else " (no CI)"
    return f"{p['estimate']:.2f}{ci}"


def _list(items, a, b) -> str:
    if not items:
        return "0"
    return f"{len(items)}: " + _e("; ".join(f"{d.get(a)} ({d.get(b)})" for d in items))


def load(root: Path = ROOT) -> dict[str, dict]:
    d = root / SRC
    recs = {}
    for p in sorted(d.glob("*.json")) if d.is_dir() else []:
        if p.name == "SOURCE.json":
            continue
        rec = json.loads(p.read_text(encoding="utf-8"))
        recs[rec.get("slug") or p.stem] = rec
    order = [s for s in G1_FOCUS if s in recs] + sorted(s for s in recs if s not in G1_FOCUS)
    return {s: recs[s] for s in order}


def matched_topics(recs: dict[str, dict]) -> list[str]:
    return [s for s, r in recs.items()
            if recompute(r)["matched"] and (r.get("g1_status") or {}).get("state") == "G1_MATCHED"]


def render(root: Path = ROOT) -> str:
    recs = load(root)
    src = root / SRC / "SOURCE.json"
    source = json.loads(src.read_text(encoding="utf-8")) if src.is_file() else {}
    summ = {s: recompute(r) for s, r in recs.items()}
    lane = {s: (r.get("g1_status") or {}).get("state") for s, r in recs.items()}
    both = matched_topics(recs)
    head = f"<p><strong>G1 MATCHED: {len(both)} of {len(recs)} topics</strong>"
    if both:
        head += " (" + ", ".join(_e(s) for s in both) + ")"
    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'><title>G1 scoreboard</title>",
        "<style>body{font-family:system-ui,sans-serif;max-width:1180px;margin:24px auto;padding:0 16px;color:#1d2b33}"
        "table{border-collapse:collapse;width:100%;margin:8px 0 20px}th,td{border:1px solid #dbe3e8;padding:5px 7px;"
        "font-size:13px;vertical-align:top;text-align:left}th{background:#f2f6f8}.no{color:#8a3b12}.ok{color:#1d6b3a}"
        ".muted{color:#5b6b75;font-size:13px}.focus{font-weight:600}</style></head><body>",
        "<h1>G1 scoreboard: trial-for-trial against published open-access meta-analyses</h1>",
        head + ".</p>",
        "<p class='muted'>G1 MATCHED = every eligible comparator trial matched AND every matched trial verified from a "
        "PRIMARY source (posted CT.gov results from a versioned AACT snapshot, or the trial's own open full text) or by TWO "
        "independent metas, never the comparator alone AND the result agrees on the same trials AND every divergence is "
        "named. Each criterion is recomputed on this page from the tracker file; a topic counts only when the lane's "
        "status and the recomputation agree. Generated by scripts/render_g1_tracker.py; never hand-edited.</p>",
    ]
    if source:
        parts.append(f"<p class='muted'>Tracker source: {_e(source.get('branch'))} @ {_e(source.get('commit'))}; "
                     f"G1_TRACKER.md blob {_e(source.get('tracker_blob'))}. {_e(source.get('note'))}</p>")
    parts.append("<table><tr><th>topic</th><th>G1 (recomputed)</th><th>lane status</th><th>k matched</th>"
                 "<th>verified rows (primary + two-source)</th><th>same trials: ours vs theirs</th>"
                 "<th>named divergences</th><th>comparator-side findings</th></tr>")
    for s, rec in recs.items():
        r = summ[s]
        st = rec.get("same_trials") or {}
        if st.get("ours"):
            same = (f"{_e(st.get('measure'))} {_fmt_pool(st.get('ours'))} vs {_fmt_pool(st.get('theirs'))}, "
                    f"k={_e(st.get('k'))}: <strong>{_e(_verdict(st))}</strong>")
        else:
            same = _e(st.get("state") or "not pooled")
        mine = "MATCHED" if r["matched"] else "NOT YET (" + ", ".join(c for c in CRITERIA if not r["criteria"][c]) + ")"
        flag = "" if r["matched"] == (lane[s] == "G1_MATCHED") else " <span class='no'>(lane status disagrees)</span>"
        cls = "focus" if s in G1_FOCUS else ""
        ok = "ok" if s in both else "no"
        parts.append(
            f"<tr><td class='{cls}'><a href='#{_e(s)}'>{_e(s)}</a></td><td class='{ok}'>{_e(mine)}{flag}</td>"
            f"<td>{_e(lane[s])}</td><td>{_e(rec.get('k_matched'))} of {_e(rec.get('N_eligible'))} eligible "
            f"(comparator N={_e(rec.get('N_comparator_trials'))})</td><td>{r['g1_count']} of {len(r['rows'])}</td>"
            f"<td>{same}</td><td>{_list(rec.get('named_differences') or [], 'trial', 'kind')}</td>"
            f"<td>{_list(rec.get('comparator_findings') or [], 'finding', 'trial')}</td></tr>")
    parts.append("</table>")
    for s, rec in recs.items():
        r = summ[s]
        parts.append(f"<h2 id='{_e(s)}'>{_e(s)} <span class='muted'>(comparator PMID "
                     f"{_e(rec.get('comparator_pmid'))})</span></h2>")
        crit = "; ".join(f"{c}: " + ("yes" if r["criteria"][c] else "<span class='no'>no</span>") for c in CRITERIA)
        if r["unnamed"]:
            crit += ". Not named: " + _e(", ".join(map(str, r["unnamed"])))
        parts.append(f"<p>{crit}</p>")
        parts.append("<table><tr><th>comparator trial</th><th>route</th><th>source / basis</th><th>verified (counts)</th>"
                     "<th>in our pool</th><th>vs comparator row</th></tr>")
        for row in r["rows"]:
            t = row["trial"]
            side = t.get("disagreement_side")
            cls = "ok" if row["counted"] else "no"
            parts.append(f"<tr><td>{_e(t.get('label'))}</td><td>{_e(t.get('route'))}</td><td>{_e(t.get('basis'))}</td>"
                         f"<td class='{cls}'>{'yes' if row['counted'] else 'no'}: {_e(row['why'])}</td>"
                         f"<td>{'yes' if t.get('in_our_pool') else 'no'}</td>"
                         f"<td>{_e(t.get('agreement_with_comparator_row'))}{(' (' + _e(side) + ')') if side else ''}</td></tr>")
        parts.append("</table>")
        for d in rec.get("named_differences") or []:
            parts.append(f"<p><strong>Named divergence</strong> {_e(d.get('trial'))} ({_e(d.get('kind'))}): "
                         f"{_e(d.get('reason'))}</p>")
        for f in rec.get("comparator_findings") or []:
            parts.append(f"<p><strong>Comparator-side finding</strong> {_e(f.get('finding'))}: {_e(f.get('trial'))}</p>")
    parts.append("</body></html>\n")
    return "".join(parts)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    out = ROOT / OUT
    want = render().encode("utf-8")
    if a.check:
        if not out.is_file() or out.read_bytes() != want:
            print(f"REFUSED: {OUT.as_posix()} is stale or absent; run python scripts/render_g1_tracker.py")
            return 1
        print(f"OK {OUT.as_posix()} current")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(want)
    recs = load()
    print(f"wrote {OUT.as_posix()}: G1 MATCHED {len(matched_topics(recs))} of {len(recs)} topics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
