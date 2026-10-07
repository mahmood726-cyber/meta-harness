"""Render the G1 scoreboard (docs/g1/index.html) from the topic tracker files in outputs/k_gap/g1/.

GOAL 1: match published open-access meta-analyses trial-for-trial. The tracker files are written by the k-gap lane's
scripts/g1_tracker.py (schema 1, kgap/G1_INTERFACES.md section 4); outputs/k_gap/G1_SOURCE.json (kept OUTSIDE the tracker directory, whose every file is a tracker record) records which commit
and blobs this tree's copy came from. This page is GENERATED from those files and nothing else; `--check` refuses a
committed page that differs from a fresh render.

G1 MATCHED (the tracker's own definition) = every eligible comparator trial matched AND every matched trial verified
(PRIMARY / TWO_SOURCE / SECONDARY_SINGLE from a non-comparator meta, never comparator-only) AND the result agrees on the same trials AND every divergence is named.
The page prints the lane's status AND recomputes each criterion here from the same file:
  ALL_ELIGIBLE_MATCHED  k_matched == N_eligible > 0
  MATCHED_ARE_VERIFIED  every trial in our pool is INDEPENDENTLY CONFIRMED: PRIMARY; TWO_SOURCE with two distinct
                        recorded sources stating the counts, none the comparator; or SECONDARY_SINGLE from a recorded
                        non-comparator meta row with location + digest (anything unrecorded does not count: fail-closed)
The page shows two numbers side by side (decision 2026-10-03): COVERAGE = INDEPENDENTLY CONFIRMED + COMPARATOR_SOURCED
rows (taken from the comparator meta with location, digest and read record), and INDEPENDENTLY CONFIRMED alone. A
comparator-sourced row never counts toward INDEPENDENTLY CONFIRMED or G1 MATCHED.
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
SOURCE = Path("outputs") / "k_gap" / "G1_SOURCE.json"
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


_PMID_IN = re.compile(r"(?:PMID|meta)\W{0,3}(\d{6,9})", re.I)
_NCT_IN = re.compile(r"\bNCT\d{8}\b", re.I)


def stated_by(trial: dict) -> set[str]:
    """The DISTINCT sources that themselves state the counts (readings[].counts_stated_by): a text PMID or a meta PMID.

    Two readings of the same text are one source; a source that only reproduces a pool from counts it did not print
    is not listed by the tracker and is not counted here."""
    out = set()
    for rd in trial.get("readings") or []:
        for s in rd.get("counts_stated_by") or []:
            m = _PMID_IN.search(str(s)) or _NCT_IN.search(str(s))
            if m:  # an unidentifiable source is not a source (fail-closed; codex review 2026-10-03)
                out.add((m.group(1) if m.groups() else m.group(0)).lower())
    return out


def secondary_basis(trial: dict) -> dict | None:
    """The recorded source of a SECONDARY_SINGLE row: sweep.basis (the two-source sweep) or secondary_single.provenance
    (the tracker's own route, whose 'basis' is a sentence) -- both carry meta / location / digest."""
    for key, field in (("sweep", "basis"), ("secondary_single", "basis"), ("secondary_single", "provenance")):
        sw = trial.get(key)
        if isinstance(sw, dict) and isinstance(sw.get(field), dict):
            return sw[field]
    return None


def counts(trial: dict, comparator_ids: set[str]) -> tuple[bool, str]:
    """INDEPENDENTLY CONFIRMED: true only on a route whose sources are recorded AND exclude the comparator."""
    route = trial.get("route")
    if trial.get("scope_difference"):
        return False, "named out of scope (rule + span): not part of the comparator's eligible set"
    if trial.get("coverage") == "COMPARATOR_SOURCED":
        return False, "the row is comparator-sourced: coverage only, never confirmation"
    if route == "PRIMARY":
        return True, "primary source"
    if route == "TWO_SOURCE":
        pair = pair_of(trial)
        if pair is None:
            pair = stated_by(trial) or None
        if pair is None or len(pair) < 2:
            return False, "TWO_SOURCE but two distinct recorded sources stating the counts are not found: not counted (fail-closed)"
        if pair & comparator_ids:
            return False, "TWO_SOURCE pair includes the comparator: not counted (anti-circularity)"
        return True, "two independent sources (" + ", ".join(sorted(pair)) + "), comparator excluded"
    if route in ("SECONDARY_SINGLE", "SWEEP_SECONDARY_SINGLE"):
        b = secondary_basis(trial)
        meta = _ids((b or {}).get("meta") or (b or {}).get("meta_pmid"))
        if not b or not meta or not b.get("digest") or not (b.get("where") or b.get("location")):
            return False, f"{route} without a recorded meta, location and digest: not counted (fail-closed)"
        if meta & comparator_ids:
            return False, f"{route} read from the comparator itself: not counted (anti-circularity)"
        return True, "one non-comparator meta row (PMID " + ", ".join(sorted(meta)) + "), queued for primary verification"
    if route == "SWEEP_AACT_PRIMARY":
        ok, why = aact_binding(trial)
        return ok, why
    return False, f"{route or 'no route'}: not counted"


def _numeric(v) -> bool:
    try:
        float(str(v).replace(",", ""))
        return True
    except (TypeError, ValueError):
        return False


def aact_binding(trial: dict) -> tuple[bool, str]:
    """D1-SWEEP-AACT-PRIMARY (registry/g1_decisions.json; Mahmood 2 Oct): the trial's own posted results in a versioned
    AACT snapshot are a PRIMARY source, counted only with the recorded registry binding the sweep's gates produced --
    NCT, registry outcome title, snapshot id + digest, the posted-N = randomised-N guard, and two-arm counts or a
    two-sided effect with its CI. Anything missing: not counted (fail-closed)."""
    sw = trial.get("sweep") if isinstance(trial.get("sweep"), dict) else {}
    b = sw.get("basis") if isinstance(sw.get("basis"), dict) else {}
    v = sw.get("value") if isinstance(sw.get("value"), dict) else {}
    snap = b.get("snapshot") if isinstance(b.get("snapshot"), dict) else {}
    missing = [k for k, ok in (("NCT", bool(re.fullmatch(r"NCT\d{8}", str(b.get("nct") or "")))),
                               ("registry outcome", bool(str(b.get("outcome") or "").strip())),
                               ("snapshot id", bool(snap.get("id"))),
                               ("snapshot digest", bool(re.fullmatch(r"[0-9a-f]{64}", str(snap.get("digest") or "")))),
                               ("randomised-population guard", str(b.get("guard") or "").startswith("POSTED_N_EQUALS_RANDOMISED_N")))
               if not ok]
    counts_ok = all(isinstance(v.get(k), int) and not isinstance(v.get(k), bool) for k in ("events_t", "n_t", "events_c", "n_c"))
    effect_ok = all(_numeric(v.get(k)) for k in ("effect", "lower", "upper"))
    if not (counts_ok or effect_ok):
        missing.append("two-arm counts or a two-sided effect")
    if missing:
        return False, "SWEEP_AACT_PRIMARY without " + ", ".join(missing) + ": not counted (fail-closed)"
    return True, (f"primary source: posted results, {b['nct']} '{str(b['outcome'])[:60]}' ({snap['id']}, "
                  f"{str(snap['digest'])[:12]}; {str(b['guard']).split(' ')[0]}) [D1-SWEEP-AACT-PRIMARY]")


def comparator_sourced(trial: dict, comparator_ids: set[str]) -> tuple[bool, str]:
    """COVERAGE only (never INDEPENDENTLY CONFIRMED, never G1): a row taken from the comparator meta with provenance."""
    if trial.get("coverage") != "COMPARATOR_SOURCED" or trial.get("scope_difference"):
        return False, ""
    pv = (trial.get("comparator_sourced") or {}).get("provenance") or {}
    missing = [k for k in ("meta_pmid", "location", "digest", "read") if not pv.get(k)]
    if missing:
        return False, "comparator-sourced row without " + ", ".join(missing) + ": not covered (fail-closed)"
    if not _ids(pv["meta_pmid"]) & comparator_ids:
        return False, f"labelled comparator-sourced but read from PMID {pv['meta_pmid']}, not the comparator: not covered (fail-closed)"
    loc = pv["location"] if isinstance(pv["location"], dict) else {}
    return True, f"from comparator PMID {pv['meta_pmid']} {loc.get('kind', '')} {loc.get('id', '')}".strip()


def _verdict(st: dict):
    v = st.get("verdict") if isinstance(st, dict) else None
    return v.get("verdict") if isinstance(v, dict) else v


def _named(rec: dict) -> set[str]:
    rows = (rec.get("named_differences") or []) + (rec.get("comparator_findings") or [])
    return {str(d["trial"]).strip().lower() for d in rows if d.get("trial")}


SWITCH_SIGNATURES = Path("registry") / "comparator_switch_signatures.json"


def comparator_switch(rec: dict, root: Path = ROOT) -> dict | None:
    """None when the topic is matched against its SERVED comparator (docs/reviews/<slug>/review.json comparator.pmid).
    Otherwise {from, to, signed}: a replaced comparator counts only once Mahmood has signed that switch
    (registry/comparator_switch_signatures.json, packet V8). A topic with no served page is not on the page at all
    (table() refuses a served topic with no tracker row), so it carries no switch."""
    slug = rec.get("slug")
    rp = root / "docs" / "reviews" / str(slug) / "review.json"
    served = None
    if rp.is_file():
        served = str((json.loads(rp.read_text(encoding="utf-8")).get("comparator") or {}).get("pmid") or "") or None
    cur = str(rec.get("comparator_pmid") or "")
    if not rp.is_file() or (served and served == cur):
        return None
    sp = root / SWITCH_SIGNATURES
    sigs = (json.loads(sp.read_text(encoding="utf-8")).get("switches") or {}) if sp.is_file() else {}
    sig = sigs.get(str(slug)) or {}
    ok = (sig.get("to") == cur and sig.get("from") == served and sig.get("state") in ("SEEN_AND_SIGNED",))
    return {"from": served, "to": cur, "signed": ok, "signature": sig or None}


def recompute(rec: dict, root: Path = ROOT) -> dict:
    """The criteria and the per-trial counting, recomputed from the tracker file."""
    comparator_ids = _ids([rec.get("comparator_pmid"), rec.get("comparator_doi")])
    rows = []
    for t in rec.get("trials") or []:
        ok, why = counts(t, comparator_ids)
        cs, cs_why = (False, "") if ok else comparator_sourced(t, comparator_ids)
        rows.append({"trial": t, "counted": ok, "why": why, "covered": ok or cs, "cover_why": cs_why if cs else ""})
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
        # matched against a comparator the topic does not SERVE counts only after Mahmood signs that switch (V8)
        "COMPARATOR_SIGNED": (lambda sw: sw is None or sw["signed"])(comparator_switch(rec, root)),
    }
    return {"rows": rows, "criteria": crit, "matched": all(crit.values()), "unnamed": unnamed,
            "g1_count": sum(r["counted"] for r in rows), "covered": sum(r["covered"] for r in rows),
            "comparator_sourced": sum(r["covered"] and not r["counted"] for r in rows)}


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
        rec = json.loads(p.read_text(encoding="utf-8"))
        recs[rec.get("slug") or p.stem] = rec
    order = [s for s in G1_FOCUS if s in recs] + sorted(s for s in recs if s not in G1_FOCUS)
    return {s: recs[s] for s in order}


def trial_totals(recs: dict[str, dict]) -> dict:
    """Both denominators, summed from the topic files: matched / eligible and matched / the comparators' own N."""
    def n(v):
        return v if isinstance(v, int) and not isinstance(v, bool) else 0
    return {"matched": sum(n(r.get("k_matched")) for r in recs.values()),
            "eligible": sum(n(r.get("N_eligible")) for r in recs.values()),
            "comparator_n": sum(n(r.get("N_comparator_trials")) for r in recs.values())}


ABANDONED = Path("registry") / "g1_abandoned.json"
ABANDON_RULE_SHA = "c3ee2f6224b62b0aa50312ace3ae1e634332efeb8e59684176aefce7fed28f1d"
# THE DECISION ITSELF, pinned here: the ten Mahmood approved and his words (7 Oct, 'abandon ten'). The register must equal
# this exactly -- the rule hash is public, so it alone never establishes approval (codex abandon-ten g1#1, reproduced).
ABANDON_APPROVED = ("balanced-crystalloids-vs-saline-mortality", "ticagrelor-vs-clopidogrel-acs", "metformin-pcos-ovulation",
                    "colchicine-secondary-cv-prevention", "probiotics-aad-prevention", "colchicine-postop-af",
                    "pcsk9-mace", "corticosteroids-cap-mortality", "tocilizumab-covid19-mortality",
                    "omega3-cardiovascular-events")
ABANDON_WORDS = "abandon ten"


def abandoned(root: Path = ROOT) -> dict[str, dict]:
    """{slug: entry} of the topics ABANDONED_BY_DECISION (G1-ABANDON-v1; Mahmood 7 Oct, 'abandon ten'), from
    registry/g1_abandoned.json (scripts/g1_abandon_apply.py). {} when no register is committed. A register naming any
    other rule, or an entry in any other state, refuses: the page never counts against an unapproved list."""
    p = root / ABANDONED
    if not p.exists():
        return {}
    if not p.is_file():          # a path that exists but is not a file is a broken register, never 'none' (codex r4 g1#2)
        raise ValueError(f"ABANDONED: {p} exists but is not a file")
    d = json.loads(p.read_text(encoding="utf-8"))
    if d.get("rule_sha256") != ABANDON_RULE_SHA:
        raise ValueError(f"ABANDONED: {p} names rule sha256 {str(d.get('rule_sha256'))[:12]}, not G1-ABANDON-v1")
    out = {}
    for t in d.get("topics") or []:
        if t.get("state") != "ABANDONED_BY_DECISION" or (t.get("decision") or {}).get("words") != ABANDON_WORDS:
            raise ValueError(f"ABANDONED: {t.get('slug')} is not ABANDONED_BY_DECISION with the decision's words")
        out[t["slug"]] = dict(t, _register=d)
    if sorted(out) != sorted(ABANDON_APPROVED) or len(d.get("topics") or []) != len(ABANDON_APPROVED):
        raise ValueError(f"ABANDONED: the register is not exactly the approved ten (extra "
                         f"{sorted(set(out) - set(ABANDON_APPROVED))}, missing {sorted(set(ABANDON_APPROVED) - set(out))})")
    return out


def matched_topics(recs: dict[str, dict], root: Path = ROOT) -> list[str]:
    """Strictly matched topics. An ABANDONED_BY_DECISION topic never counts, whatever its tracker says."""
    gone = abandoned(root)
    return [s for s, r in recs.items() if s not in gone
            and recompute(r)["matched"] and (r.get("g1_status") or {}).get("state") == "G1_MATCHED"]


def k_matched(rec: dict) -> dict | None:
    """K MATCHED (Mahmood 5 Oct, 'not inferior k-wise'): EVERY eligible comparator trial (not named out of scope) has a
    typed row from ANY admitted source -- independent or taken from the comparator meta itself (comparator-sourced,
    labelled). None when the topic has no eligible trial. A k-wise claim only: it never implies G1 MATCHED (strict), which
    stays the first line. Recomputed from the tracker file, fail-closed like every other count on this page."""
    r = recompute(rec)
    elig = [x for x in r["rows"] if not x["trial"].get("scope_difference")]
    if not elig or not r["criteria"]["COMPARATOR_SIGNED"]:
        return None                     # k-wise against an unsigned comparator switch is not claimed either
    return {"matched": all(x["covered"] for x in elig), "eligible": len(elig),
            "comparator_sourced": sum(1 for x in elig if x["covered"] and not x["counted"]),
            "uncovered": [x["trial"].get("label") for x in elig if not x["covered"]]}


def k_matched_topics(recs: dict[str, dict], root: Path = ROOT) -> list[str]:
    gone = abandoned(root)
    return [s for s, rec in recs.items() if s not in gone and (k_matched(rec) or {}).get("matched")]


def render(root: Path = ROOT) -> str:
    recs = load(root)
    src = root / SOURCE
    source = json.loads(src.read_text(encoding="utf-8")) if src.is_file() else {}
    summ = {s: recompute(r) for s, r in recs.items()}
    lane = {s: (r.get("g1_status") or {}).get("state") for s, r in recs.items()}
    both = matched_topics(recs, root)
    gone = {s: g for s, g in abandoned(root).items() if s in recs}
    active = [s for s in recs if s not in gone]
    # BOTH LINES (G1-ABANDON-v1, Mahmood 7 Oct): n of the active topics AND n of all topics. The all-topics line is
    # never conditional -- abandonment narrows what is being attempted, it never shrinks the denominator out of sight.
    if gone:
        head = (f"<p><strong>G1 MATCHED: {len(both)} of {len(active)} active topics ({len(gone)} abandoned by decision, "
                f"listed <a href='#abandoned'>below</a>)</strong>")
        if both:
            head += " (" + ", ".join(_e(s) for s in both) + ")"
        head += f".</p><p class='hl'><strong>G1 MATCHED: {len(both)} of {len(recs)} all topics</strong>"
    else:
        head = f"<p><strong>G1 MATCHED: {len(both)} of {len(recs)} all topics</strong>"
        if both:
            head += " (" + ", ".join(_e(s) for s in both) + ")"
    # K MATCHED beside the strict count, never replacing it (Mahmood 5 Oct): k-wise only, comparator rows labelled
    km = k_matched_topics(recs, root)
    km_lab = [f"{_e(s)} {k_matched(recs[s])['eligible']} of comparator N {_e(recs[s].get('N_comparator_trials'))}"
              + (f" [{k_matched(recs[s])['comparator_sourced']} comparator-sourced]"
                 if k_matched(recs[s])["comparator_sourced"] else "") for s in km]
    head += (f".</p><p class='hl' id='k-matched'><strong>K MATCHED:</strong> {len(km)} of {len(recs)} topics -- every eligible "
             f"comparator trial has a typed row from an admitted source, comparator-sourced rows included and labelled; "
             f"a k-wise count only, not G1 MATCHED" + (" (" + ", ".join(km_lab) + ")" if km else ""))
    tot = trial_totals(recs)
    conf = sum(x["g1_count"] for x in summ.values())
    cov = sum(x["covered"] for x in summ.values())
    csrc = sum(x["comparator_sourced"] for x in summ.values())
    n = tot["comparator_n"]
    pct = (lambda a: f" ({100 * a / n:.0f}%)") if n else (lambda a: "")
    led_p = root / "outputs" / "k_gap" / "G1_DENOMINATOR.json"
    led = json.loads(led_p.read_text(encoding="utf-8")) if led_p.is_file() else None
    led_bad = None
    if led is not None:
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location("g1_denominator_ledger", root / "scripts" / "g1_denominator_ledger.py")
        if _sp and (root / "scripts" / "g1_denominator_ledger.py").is_file():
            _m = _ilu.module_from_spec(_sp)
            _sp.loader.exec_module(_m)
            led_bad = _m.problems(led)
    # TWO SEPARATE, LABELLED LINES (dispatch 2026-10-04: the side-by-side table read as one run-on label)
    head += (f".</p><p class='hl'><strong>COVERAGE:</strong> {cov} of {n} comparator rows{pct(cov)} -- a typed row "
             f"for the trial from any admitted source, INCLUDING {csrc} taken from the comparator meta itself (figure/"
             f"table location, digest and read record on each row). Coverage only; never counted as confirmation.</p>"
             f"<p class='hl'><strong>INDEPENDENTLY CONFIRMED:</strong> {conf} of {n} comparator rows{pct(conf)} -- a "
             f"primary source, two independent sources, or one non-comparator meta row queued for primary verification; "
             f"the comparator is never one of the sources (recomputed here, fail-closed on an unrecorded source).</p>")
    if led is not None and not led_bad and led.get("current", {}).get("N") == n:
        kinds = {}
        for r in led.get("removed") or []:
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
        rem = ", ".join(f"{v} {k.replace('_', ' ').lower()}" for k, v in sorted(kinds.items()) if k != "RELABELLED")
        head += (f"<p class='hl'><strong>DENOMINATOR:</strong> {n} comparator rows; {led['removed_n']} removed "
                 f"({rem}), {led['relabelled_n']} relabelled and {led['added_n']} added since the "
                 f"{led['baseline']['N']}-row baseline (main {str(led['baseline']['commit'])[:8]}) -- every change is "
                 f"listed <a href='#denominator'>below</a> with its rule ID and a span quoted from a held source.</p><p>")
    else:
        b0 = (led or {}).get("baseline", {}).get("N", 367)
        head += (f"<p class='hl no'><strong>DENOMINATOR:</strong> {n} comparator rows -- denominator reduced "
                 f"{b0}&rarr;{n}; per-trial justification pending.</p><p>")
    head += (f"Trials matched: <strong>{tot['matched']} of {tot['eligible']} eligible</strong> and "
             f"<strong>{tot['matched']} of {tot['comparator_n']} comparator trials</strong> (the comparators' own N; the "
             f"difference, {tot['comparator_n'] - tot['eligible']}, is comparator trials outside our registered scope or "
             f"estimand, each named per topic)")
    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'><title>G1 scoreboard</title>",
        "<style>body{font-family:system-ui,sans-serif;max-width:1180px;margin:24px auto;padding:0 16px;color:#1d2b33}"
        "table{border-collapse:collapse;width:100%;margin:8px 0 20px}th,td{border:1px solid #dbe3e8;padding:5px 7px;"
        "font-size:13px;vertical-align:top;text-align:left}th{background:#f2f6f8}.no{color:#8a3b12}.ok{color:#1d6b3a}"
        ".muted{color:#5b6b75;font-size:13px}.focus{font-weight:600}.hl{font-size:15px;margin:6px 0}</style></head><body>",
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
                 "<th>COVERAGE (comparator-sourced)</th><th>INDEPENDENTLY CONFIRMED</th><th>same trials: ours vs theirs</th>"
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
        if s in gone:
            mine = "ABANDONED_BY_DECISION (never counted; " + mine + ")"
        flag = "" if r["matched"] == (lane[s] == "G1_MATCHED") else " <span class='no'>(lane status disagrees)</span>"
        cls = "focus" if s in G1_FOCUS else ""
        ok = "ok" if s in both else "no"
        parts.append(
            f"<tr><td class='{cls}'><a href='#{_e(s)}'>{_e(s)}</a></td><td class='{ok}'>{_e(mine)}{flag}</td>"
            f"<td>{_e(lane[s])}</td><td>{_e(rec.get('k_matched'))} of {_e(rec.get('N_eligible'))} eligible "
            f"(comparator N={_e(rec.get('N_comparator_trials'))})</td>"
            f"<td>{r['covered']} of {len(r['rows'])} ({r['comparator_sourced']})</td><td>{r['g1_count']} of {len(r['rows'])}</td>"
            f"<td>{same}</td><td>{_list(rec.get('named_differences') or [], 'trial', 'kind')}</td>"
            f"<td>{_list(rec.get('comparator_findings') or [], 'finding', 'trial')}</td></tr>")
    parts.append("</table>")
    # D3-COMPARATOR-POOLS-NO-RCT: still in the denominator, listed here with the comparator's own words
    noatt = [(s, rec.get("g1_status") or {}) for s, rec in recs.items()
             if (rec.get("g1_status") or {}).get("state") == "COMPARATOR_POOLS_NO_RCT"]
    if noatt:
        parts.append(f"<h2 id='not-attainable'>Not attainable against this comparator ({len(noatt)} of {len(recs)} "
                     f"topics; still counted in the {len(recs)})</h2><ul>")
        for s, g in noatt:
            sp = g.get("span") or {}
            parts.append(f"<li><a href='#{_e(s)}'>{_e(s)}</a>: the comparator pools no randomised trials -- "
                         f"&ldquo;{_e(sp.get('text'))}&rdquo; ({_e(sp.get('source'))}, {_e(sp.get('field'))}). "
                         f"{_e(g.get('flag'))} [{_e(g.get('decision'))}]</li>")
        parts.append("</ul>")
    pend = [(s, comparator_switch(rec, root)) for s, rec in recs.items()]
    pend = [(s, sw) for s, sw in pend if sw and not sw["signed"]]
    if pend:
        parts.append(f"<h2 id='comparator-switch-pending'>Comparator switch pending signature ({len(pend)} of {len(recs)} "
                     f"topics; not counted in G1 MATCHED or K MATCHED until signed)</h2><ul>")
        for s, sw in pend:
            parts.append(f"<li><a href='#{_e(s)}'>{_e(s)}</a>: served comparator PMID {_e(sw['from'])}; the tracker is "
                         f"matched against PMID {_e(sw['to'])} (pre-registered replacement), which counts once Mahmood "
                         f"signs the switch (packet V8)</li>")
        parts.append("</ul>")
    if gone:
        reg = next(iter(gone.values()))["_register"]
        dc = reg.get("decision") or {}
        parts.append(f"<h2 id='abandoned'>Abandoned by decision ({len(gone)} of {len(recs)} topics; still on this page, "
                     f"never counted as matched)</h2><p class='muted'>{_e(dc.get('by'))}, {_e(dc.get('date'))}, verbatim: "
                     f"&ldquo;{_e(dc.get('words'))}&rdquo; ({_e(dc.get('relayed'))}). Rule {_e(reg.get('rule_id'))} "
                     f"(<code>{_e(reg.get('rule_path'))}</code>, sha256 <code>{_e(reg.get('rule_sha256'))}</code>, committed "
                     f"at <code>{_e(str(reg.get('rule_commit'))[:8])}</code> before any score was computed): score "
                     f"{_e(reg.get('score'))}; the ten highest are abandoned. Boundary: #10 "
                     f"{_e(reg['boundary']['last_abandoned']['slug'])} U = {_e(reg['boundary']['last_abandoned']['U'])}, "
                     f"#11 {_e(reg['boundary']['first_kept']['slug'])} U = {_e(reg['boundary']['first_kept']['U'])} (kept). "
                     f"Nothing is deleted: pages, rows, findings and signed results stay served.</p><ul>")
        for s, g in sorted(gone.items(), key=lambda kv: kv[1].get("rank") or 0):
            parts.append(f"<li><a href='#{_e(s)}'>{_e(s)}</a>: {_e(g.get('reason'))}; closed: "
                         f"{_e('; '.join(g.get('closed_trials') or []) or 'none')}</li>")
        parts.append("</ul>")
    dec_p = root / "registry" / "g1_decisions.json"
    decs = (json.loads(dec_p.read_text(encoding="utf-8")).get("decisions") or []) if dec_p.is_file() else []
    if decs:
        parts.append("<h2 id='decisions'>Decisions applied</h2><ul>")
        for d in decs:
            parts.append(f"<li><strong>{_e(d.get('id'))}</strong> ({_e(d.get('decided'))}, {_e(d.get('by'))}): "
                         f"{_e(d.get('rule'))}</li>")
        parts.append("</ul>")
    for s, rec in recs.items():
        r = summ[s]
        parts.append(f"<h2 id='{_e(s)}'>{_e(s)} <span class='muted'>(comparator PMID "
                     f"{_e(rec.get('comparator_pmid'))})</span></h2>")
        crit = "; ".join(f"{c}: " + ("yes" if r["criteria"][c] else "<span class='no'>no</span>") for c in CRITERIA)
        if r["unnamed"]:
            crit += ". Not named: " + _e(", ".join(map(str, r["unnamed"])))
        parts.append(f"<p>{crit}</p>")
        parts.append("<table><tr><th>comparator trial</th><th>route</th><th>source / basis</th><th>independently confirmed</th><th>coverage</th>"
                     "<th>in our pool</th><th>vs comparator row</th></tr>")
        for row in r["rows"]:
            t = row["trial"]
            side = t.get("disagreement_side")
            cls = "ok" if row["counted"] else "no"
            parts.append(f"<tr><td>{_e(t.get('label'))}</td><td>{_e(t.get('route'))}</td><td>{_e(t.get('basis'))}</td>"
                         f"<td class='{cls}'>{'yes' if row['counted'] else 'no'}: {_e(row['why'])}</td>"
                         f"<td>{'yes' if row['covered'] else 'no'}{(': ' + _e(row['cover_why'])) if row['cover_why'] else ''}</td>"
                         f"<td>{'yes' if t.get('in_our_pool') else 'no'}</td>"
                         f"<td>{_e(t.get('agreement_with_comparator_row'))}{(' (' + _e(side) + ')') if side else ''}</td></tr>")
        parts.append("</table>")
        for d in rec.get("named_differences") or []:
            parts.append(f"<p><strong>Named divergence</strong> {_e(d.get('trial'))} ({_e(d.get('kind'))}): "
                         f"{_e(d.get('reason'))}</p>")
        for f in rec.get("comparator_findings") or []:
            parts.append(f"<p><strong>Comparator-side finding</strong> {_e(f.get('finding'))}: {_e(f.get('trial'))}</p>")
    if led is not None and not led_bad:
        parts.append(f"<h2 id='denominator'>Denominator ledger: {led['baseline']['N']} -> {led['current']['N']} "
                     f"comparator rows</h2><p class='muted'>Every row that left the pinned baseline "
                     f"({_e(led['baseline']['fixture'])}) and every row that joined, from outputs/k_gap/G1_DENOMINATOR.json "
                     f"(scripts/g1_denominator_ledger.py --check refuses a removal without rule + verbatim span).</p>")
        parts.append("<table><tr><th>topic</th><th>comparator row</th><th>change</th><th>rule</th><th>quoted source span"
                     "</th><th>source</th></tr>")
        for r in led.get("removed") or []:
            sp = r.get("span") or {}
            rows = sp.get("rows") if "rows" in sp else [sp]
            txt = " | ".join((x or {}).get("text", "") for x in rows)
            if r["kind"] == "DUPLICATE_UNIT":
                txt += " | duplicate of: " + ((r.get("span_duplicate_of") or {}).get("text") or "")
            if r["kind"] == "RELABELLED":
                txt = f"now '{r.get('now_label')}': " + txt
            ctx = sp.get("context_before") if isinstance(sp, dict) else None
            parts.append(f"<tr><td>{_e(r['slug'])}</td><td>{_e(r['label'])}</td><td>{_e(r['kind'])}</td>"
                         f"<td>{_e(r['rule_id'])}</td><td>{_e(txt)}"
                         + (f"<br><span class='muted'>preceded by: ...{_e(ctx[-160:])}</span>" if ctx else "")
                         + f"</td><td class='muted'>{_e((rows[0] or {}).get('source'))}</td></tr>")
        for a_ in led.get("added") or []:
            parts.append(f"<tr><td>{_e(a_['slug'])}</td><td>{_e(a_['label'])}</td><td>ADDED</td><td>{_e(a_['basis'])}"
                         f"</td><td>{_e((a_.get('span') or {}).get('text'))}</td><td class='muted'>"
                         f"{_e((a_.get('span') or {}).get('source'))}</td></tr>")
        parts.append("</table>")
    parts.append("</body></html>\n")
    return "".join(parts)


def record_tracker_blob(root: Path = ROOT) -> str | None:
    """G1_SOURCE.json names the G1_TRACKER.md the page is rendered from (its git blob, LF bytes). It was set by hand, so a
    regenerated tracker left the page declaring a blob that no longer exists (PR #13 CI). Recorded at render time now."""
    md, src = root / "outputs" / "k_gap" / "G1_TRACKER.md", root / SOURCE
    if not (md.is_file() and src.is_file()):
        return None
    import hashlib
    data = md.read_bytes().replace(b"\r\n", b"\n")
    blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
    source = json.loads(src.read_text(encoding="utf-8"))
    if source.get("tracker_blob") != blob:
        source["tracker_blob"] = blob
        src.write_text(json.dumps(source, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return blob


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    out = ROOT / OUT
    if not a.check:
        record_tracker_blob(ROOT)
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
    _gone = abandoned()
    print(f"wrote {OUT.as_posix()}: G1 MATCHED {len(matched_topics(recs))} of {len([s for s in recs if s not in _gone])} "
          f"active topics; of {len(recs)} all topics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
