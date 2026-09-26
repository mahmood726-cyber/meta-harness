"""Fill the independent release-note section's **V1:** markers from MEASURED artefacts of the V1 run (v1_final.py), never from
rehearsals. A marker whose artefact is missing is NOT filled: it becomes '[NOT MEASURED ON V1: <why>]' so a gap can never
read as a result. Writes <work>/V1_RELEASE_NOTE_final.md and prints the list of filled / unfilled markers.

  python fill_release_note.py --results <work>/RESULTS.json --work <work> [--draft <path>]"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

REPO = "C:/mh-lanes/pva"
DRAFT = Path(REPO) / "outputs" / "pva-2026-09-25" / "V1_RELEASE_NOTE_independent_section.md"


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8", errors="replace",
                          stdin=subprocess.DEVNULL).stdout


def load(p):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--draft", default=str(DRAFT))
    a = ap.parse_args()
    work = Path(a.work)
    R = load(a.results) or {}
    v1 = R.get("v1") or ""
    sc = load(work / "served" / "scorecard.json")
    P = (sc or {}).get("probes", {})
    tabs = (load(work / "tabs.json") or {}).get("summary")
    producer = (work / "producer.txt").read_text(encoding="utf-8") if (work / "producer.txt").is_file() else None
    f6 = load(work / "f6.json")
    arch = R.get("archive")
    NM = lambda why: f"**[NOT MEASURED ON V1: {why}]**"  # noqa: E731

    def probe(pid):
        return P.get(pid) or {}

    def ok(pid):
        return {True: "PASS", False: "FAIL", None: "n/a"}.get(probe(pid).get("ok"), "absent")

    # ---- measurements -------------------------------------------------------------------------------------------------
    fill = {}
    # served pool numbers from the served glp1 review.json the audit fetched
    rv = load(work / "served" / "site" / "reviews" / "glp1-ra-mace-t2d" / "review.json")
    if rv:
        prim = next((o for o in rv.get("outcomes", []) if o.get("primary")), None)
        r = (prim or {}).get("result") or {}
        fill["pool"] = (f"V1 serves k = {r.get('k')}, HR {r.get('estimate')} ({r.get('ci_low')}-{r.get('ci_high')}) "
                        f"[bundle verifier baseline {ok('P5')}].")
    else:
        fill["pool"] = NM("served glp1 review.json not fetched")
    d2 = probe("P2").get("detail") or {}
    fill["certs"] = (f"V1: {d2.get('reproduced_full_scope')} of {d2.get('pages')} pages RESULT REPRODUCED at full scope (P2 {ok('P2')})."
                     if d2 else NM("P2 not run"))
    d1, d0 = probe("P1").get("detail") or {}, probe("P0").get("detail") or {}
    fill["bytes"] = (f"V1: {d1.get('files', 0) - d1.get('n_mismatch', 0) - d1.get('n_missing', 0)} of {d1.get('files')} fetched files equal the "
                     f"committed bytes (P1 {ok('P1')}); {d0.get('record') or 'no production record'} (P0 {ok('P0')})."
                     if d1 else NM("P1 not run"))
    absence = git("show", f"{v1}:harness/absence.py") if v1 else ""
    fill["tagstrip"] = ("V1: NOT fixed -- harness/absence.py at V1 still strips with `<[^>]+>`." if "_TAG = re.compile(r\"<[^>]+>\")" in absence
                        else ("V1: fixed -- harness/absence.py at V1 no longer uses the `<[^>]+>` strip." if absence else NM("V1 commit unreadable")))
    proto = git("show", f"{v1}:protocols/dapagliflozin-hfpef-hosp.md") if v1 else ""
    fill["ruling"] = ("V1: the protocol at V1 contains 'preserved systolic function' -- the clarification was applied; it is a retrospective "
                      "clarification, not a pre-registered rule." if "preserved systolic function" in proto.lower()
                      else "V1: not applied -- the dapagliflozin-HFpEF protocol at V1 does not add 'preserved systolic function'.")
    d7 = probe("P7").get("detail") or {}
    fill["verdicts"] = (f"V1: the verifier reports {'separate verdicts' if probe('P5b').get('ok') else 'one PASS/FAIL, not separate verdicts'} "
                        f"(P5b {ok('P5b')}). HARMONY Outcomes is "
                        + (f"in the pooled k and its row is {d7.get('row_final')} (failing {', '.join(d7.get('failing_predicates') or []) or 'none'}), "
                           f"while the verifier's verdict is {d7.get('verifier_verdict')}." if d7.get('pooled_in_k') else
                           f"not in the pooled k (row {d7.get('row_final')}).")
                        if P else NM("served probes not run"))
    # ---- final V1 scope (26 Sep): frozen main + P5 + D3; GLP-1 k = 8 with a pending FLOW+ELIXA block
    if v1:
        tf = git("show", f"{v1}:harness/trial_family.py")
        p5_fixed = bool(tf) and "if bool(aa) == bool(bb) or av-aa != bv-bb:" not in tf
        on_frozen = subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", "6260e70c", v1], capture_output=True,
                                   stdin=subprocess.DEVNULL).returncode == 0
        d3 = "preserved systolic function" in proto.lower()
        fill["scope"] = (f"V1: `{v1[:12]}` {'contains' if on_frozen else '**does NOT contain**'} frozen main 6260e70c; the P5 fix is "
                         f"{'present' if p5_fixed else '**absent**'} (the active-comparator line in harness/trial_family.py "
                         f"{'is gone' if p5_fixed else 'is still there'}); D3 is {'applied' if d3 else '**not applied**'} in the "
                         "dapagliflozin-HFpEF protocol.")
    else:
        fill["scope"] = NM("no V1 commit")
    idx = work / "served" / "site" / "reviews" / "glp1-ra-mace-t2d" / "index.html"
    page = idx.read_text(encoding="utf-8", errors="replace") if idx.is_file() else ""
    if rv or page:
        prim = next((o for o in (rv or {}).get("outcomes", []) if o.get("primary")), {}) or {}
        r = prim.get("result") or {}
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page))
        # a pending block, not scattered words: 'pending' with FLOW, ELIXA and k = 10 in the same 700-character window
        has_block = any(re.search(r"\bFLOW\b", w) and "ELIXA" in w and re.search(r"k\s*=\s*10\b", w)
                        for w in (txt[max(0, m.start() - 350): m.start() + 350] for m in re.finditer(r"(?i)pending", txt)))
        fill["pending"] = (f"V1 serves k = {r.get('k')}, HR {r.get('estimate')} ({r.get('ci_low')}-{r.get('ci_high')}); the served GLP-1 page "
                           + ("shows a pending result-change block naming FLOW and ELIXA." if has_block else
                              "**does not show a pending block naming FLOW and ELIXA**" + ("" if page else " (page not fetched)") + "."))
    else:
        fill["pending"] = NM("served GLP-1 page not fetched")
    if producer:
        pooled_refused = len(re.findall(r"final=INADMISSIBLE in_pool=True", producer))
        fill["producer"] = (f"V1: on planted inputs the producer left {pooled_refused} refused (INADMISSIBLE) row(s) in the pool "
                            "(producer_probe.py on the V1 commit)." if pooled_refused else
                            "V1: no refused row stayed in the pool under the planted inputs (producer_probe.py on the V1 commit).")
    else:
        fill["producer"] = NM("producer probe not run")
    d6 = probe("P6").get("detail") or {}
    muts = [m for v in d6.values() if isinstance(v, dict) for m in v.get("mutations", [])]
    st = next((m for m in muts if m.get("id", "").startswith("span_text_replaced")), None)
    missed = [m.get("id", "?").split(":")[0] for m in muts if not (m.get("fails_as_expected") and m.get("intended_reason_named"))]
    fill["spantext"] = (f"V1: span.text replacement is {'CAUGHT' if st and st.get('fails_as_expected') else 'NOT caught'} "
                        f"(P6: {len(muts) - len(missed)} of {len(muts)} named mutations caught for their intended reason"
                        + (f"; not caught: {', '.join(missed)}" if missed else "") + ")." if muts else NM("P6 not run"))
    # not-merged list, recomputed at V1
    def anc(c):
        return subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", c, v1], capture_output=True,
                              stdin=subprocess.DEVNULL).returncode == 0
    rc = load(work / "served" / "site" / "result_changes.json") or {}
    notices = rc.get("notices", []) if isinstance(rc, dict) else []
    signed = sum(1 for n in notices if (n.get("reviewer_countersignature") or {}).get("state") in ("SEEN_AND_SIGNED", "BATCH_SEEN_AND_SIGNED"))
    k = None
    if rv:
        k = ((next((o for o in rv.get("outcomes", []) if o.get("primary")), {}) or {}).get("result") or {}).get("k")
    fill["notmerged"] = ("V1: oc P10/P11 + pool guard " + ("IN V1" if v1 and anc("4cc42b86") else "not in V1")
                         + f"; the served result_changes.json lists {len(notices)} notices, {signed} signed"
                         + " (notices queued on lane branches are not in it)"
                         + f"; GLP-1 primary k = {k} ({'FLOW+ELIXA admitted' if k == 10 else 'FLOW+ELIXA not admitted' if k == 8 else 'check'})"
                         + f"; four verdicts {'present' if probe('P5b').get('ok') else 'absent'}.")
    lin = R.get("lineage")
    if lin:
        fill["lineage"] = ("V1 descends from every fix landed and proved live before the freeze (" if lin["ok"] else
                           "**V1 does NOT descend from: ") + ", ".join(
            f"{c} {v['what']}" for c, v in lin["commits"].items() if v["in_v1"] == lin["ok"]) + (")." if lin["ok"] else "**.")
    if tabs:
        fill["tabs"] = (f"V1 served pages: {tabs['passed']} of {tabs['checks']} tab checks pass ({tabs['pages']} pages at "
                        f"{' and '.join(tabs['above_max'])}, every tab, three click scenarios); the tab bar starts at most "
                        + ", ".join(f"{v} px ({k})" for k, v in tabs['above_max'].items()) + " from the top of the page.")
    if f6:
        pva = f6.get("_pva") or {}
        fill["f6"] = (f"Section F.6 acceptance suite (19 cases, {pva.get('suite_source')}, sha256 {str(pva.get('suite_sha256'))[:16]}) on the V1 "
                      f"tree: rc {pva.get('rc')}, original bytes restored {f6.get('original_bytes_restored')}; per-case verdicts in f6.json.")

    # ---- the 26 Sep auditor pass: AUD-1..4 from P6 on V1, AUD-5 read from the served key; fix branch from P6 on each branch
    def aud_rows(p6detail):
        ms = [m for v in (p6detail or {}).values() if isinstance(v, dict) for m in v.get("mutations", [])]
        return {m["id"].split("_")[0]: m for m in ms if m.get("id", "").startswith("aud")}

    def refused(m):
        # LEADER itself refused, for a named predicate. NOT 'verdict FAIL': a run with a swapped-in source verifier fails its
        # digest check on every edit, and a verdict-level test would then call every edit refused.
        if not m or not m.get("target_failing_predicates"):
            return False
        tgt = str(m.get("target"))
        row_out = (m.get("rows_final") or {}).get(tgt) not in (None, "ADMISSIBLE")
        named = any(tgt in str(c) for c in (m.get("semantic_codes") or []) + (m.get("raw_first_failures") or []))
        return row_out or named
    AUD_PLAIN = {
        "aud1": "reversing which arm a trial's result compares against (LEADER recorded as placebo vs liraglutide) is not caught",
        "aud2": "changing the recorded estimator of a pooled result (LEADER's hazard ratio relabelled a rate ratio) is not caught",
        "aud3": ("re-labelling a default analysis set as per-protocol is not caught: the check compares where a value came from, "
                 "not the value itself"),
        "aud4": "the analysis identity key of an ordinary row is stored, not recomputed, so an edited key is not caught",
        "aud5": ("the analysis identity key leaves out comparator direction, so two results that differ only in which arm they "
                 "compare against share one key"),
    }
    here = aud_rows(d6)
    fixes = []                                 # (branch label, aud rows) from --fix-branch scorecards, in the order given
    for spec in R.get("fix_branches") or []:
        fsc = load(spec["scorecard"])
        fixes.append((spec["label"], aud_rows(((fsc or {}).get("probes", {}).get("P6") or {}).get("detail")), spec.get("key_has_comparator")))
    open_aud = []
    for a_id in ("aud1", "aud2", "aud3", "aud4"):
        m = here.get(a_id)
        if not m:
            fill[a_id] = NM("P6 on V1 did not run this edit")
            continue
        is_refused = refused(m)
        codes = ", ".join((m.get("target_failing_predicates") or []) + (m.get("semantic_codes") or [])[:2]) or "no code"
        fill[a_id] = (f"REFUSED in V1 ({'verdict FAIL' if m.get('verdict_level_fail') else 'LEADER refused'}; {codes}; "
                      f"P6 `{m['id']}`)" if is_refused else "**OPEN** in V1 (LEADER stays admissible; P6 `" + m["id"] + "`)")
        if not is_refused:
            open_aud.append(a_id)
    bundle = load(work / "served" / "site" / "reviews" / "glp1-ra-mace-t2d" / "BUNDLE.json")
    if bundle:
        lr = next((r for r in bundle.get("verification_rows", []) if str(r["trial"]["id"]).endswith("27295427")), None)
        key = ((lr or {}).get("analysis_identity") or {}).get("analysis_identity_key") or ""
        has = "comparator" in key
        fill["aud5"] = ("fixed in V1: the served LEADER key names comparator direction" if has else
                        "**OPEN** in V1: the served LEADER key has no comparator direction (`" + key[:70].replace("|", "\\|") + "...`)")
        if not has:
            open_aud.append("aud5")
    else:
        fill["aud5"] = NM("served GLP-1 BUNDLE.json not fetched")
    for a_id in ("aud1", "aud2", "aud3", "aud4", "aud5"):
        if a_id not in open_aud:
            fill["fb_" + a_id] = "--" if a_id in fill and not fill[a_id].startswith("**[NOT") else NM("V1 not measured")
            continue
        hit = None
        for label, rows, key_has in fixes:
            if a_id == "aud5" and key_has:
                hit = f"{label} (its producer puts comparator direction into the key)"
            elif a_id != "aud5" and refused(rows.get(a_id)):
                m = rows[a_id]
                hit = f"{label} (refused there: {', '.join((m.get('target_failing_predicates') or [])[:2]) or 'verdict FAIL'})"
            if hit:
                break
        fill["fb_" + a_id] = hit or (("**no fix yet** (measured, does not refuse it: " + ", ".join(f[0] for f in fixes) + ")")
                                     if fixes else NM("no fix branch measured"))
    if open_aud:
        fill["audlim"] = ("In V1, " + "; ".join(AUD_PLAIN[a] for a in open_aud) + ". Each was reproduced on the live release and "
                          "measured on V1. Where a V1.1 branch was measured to refuse one, the auditor table in section 2 names it; the others "
                          "have no measured fix.")
    else:
        fill["audlim"] = "None: V1 refuses all five (see the auditor table in section 2)."

    # ---- apply: each marker is mapped by its own words -------------------------------------------------------------------
    rules = [(f"fill from P6 {a}", a) for a in ("aud1", "aud2", "aud3", "aud4")] + [("fill from key aud5", "aud5")] + \
            [(f"fill fix branch {a}", "fb_" + a) for a in ("aud1", "aud2", "aud3", "aud4", "aud5")] + \
            [("fill auditor-open limitations", "audlim"), ("fill scope", "scope"), ("fill pending block", "pending")] + [("re-run on the served V1 bundle", "pool"), ("re-run on served V1", "certs"), ("V1: re-run.", "bytes"),
             ("whether it is fixed in V1", "tagstrip"), ("unless that branch lands", "tagstrip"), ("state whether it was ruled", "ruling"),
             ("fill from P5b / P7", "verdicts"), ("fill from producer_probe", "producer"), ("fill from P6", "spantext"),
             ("re-check at the freeze", "notmerged")]
    text = Path(a.draft).read_text(encoding="utf-8")
    filled, unfilled = [], []

    def sub(m):
        body = m.group(1)
        for key_text, key in rules:
            if key_text in body:
                filled.append(key)
                return fill.get(key) or NM(key)
        unfilled.append(body[:60])
        return NM("no rule for this marker: " + body[:60])
    record = R.get("record") or (d0.get("record") if d0 else None)
    head = (f"# V1 release note -- independent section (FINAL for V1 `{v1[:12]}`)\n\n"
            f"*Measured on the SERVED V1 bytes: {record or 'production record: NOT MEASURED'}. "
            + (f"Archive: `{Path(arch['zip']).name}`, sha256 `{arch['sha256']}`, {arch['bytes']:,} B, offline check rc {arch['check_rc']}. "
               if arch else "Archive: NOT BUILT. ")
            + "Artefacts: served/scorecard.json, tabs.json, producer.txt, f6.json.*\n\n")
    # header first, so the draft header's own '**V1:**' is never taken for a marker
    text, nh = re.subn(r"\A# .*?\n\n\*.*?\*\n\n", lambda m: head, text, count=1, flags=re.S)
    if nh != 1:
        raise SystemExit("REFUSED: the draft's header block was not found; the note would still say DRAFT")
    text = re.sub(r"\*\*(V1:[^*]*)\*\*", sub, text)
    extra = "\n".join(f"- {fill[k]}" for k in ("lineage", "tabs", "f6") if k in fill)
    if extra:
        text += "\n## V1 measurements added at release\n" + extra + "\n"
    out = work / "V1_RELEASE_NOTE_final.md"
    out.write_text(text, encoding="utf-8")
    print(json.dumps({"out": str(out), "filled": filled, "unfilled": unfilled,
                      "still_marked": len(re.findall(r"\*\*V1:", text))}, indent=1))


if __name__ == "__main__":
    main()
