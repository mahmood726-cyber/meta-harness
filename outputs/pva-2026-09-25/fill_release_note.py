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
    fill["verdicts"] = (f"V1: four separate verdicts {('emitted' if probe('P5b').get('ok') else 'NOT emitted')} (P5b {ok('P5b')}); "
                        f"HARMONY pooled={d7.get('pooled_in_k')}, row {d7.get('row_final')} "
                        f"(failing {', '.join(d7.get('failing_predicates') or []) or 'none'}), verifier verdict {d7.get('verifier_verdict')}."
                        if P else NM("served probes not run"))
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
    if tabs:
        fill["tabs"] = (f"V1 served pages: {tabs['passed']} of {tabs['checks']} tab checks pass ({tabs['pages']} pages at "
                        f"{' and '.join(tabs['above_max'])}, every tab, three click scenarios); the tab bar starts at most "
                        + ", ".join(f"{v} px ({k})" for k, v in tabs['above_max'].items()) + " from the top of the page.")
    if f6:
        pva = f6.get("_pva") or {}
        fill["f6"] = (f"Section F.6 acceptance suite (19 cases, {pva.get('suite_source')}, sha256 {str(pva.get('suite_sha256'))[:16]}) on the V1 "
                      f"tree: rc {pva.get('rc')}, original bytes restored {f6.get('original_bytes_restored')}; per-case verdicts in f6.json.")

    # ---- apply: each marker is mapped by its own words -------------------------------------------------------------------
    rules = [("re-run on the served V1 bundle", "pool"), ("re-run on served V1", "certs"), ("V1: re-run.", "bytes"),
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
    extra = "\n".join(f"- {fill[k]}" for k in ("tabs", "f6") if k in fill)
    if extra:
        text += "\n## V1 measurements added at release\n" + extra + "\n"
    out = work / "V1_RELEASE_NOTE_final.md"
    out.write_text(text, encoding="utf-8")
    print(json.dumps({"out": str(out), "filled": filled, "unfilled": unfilled,
                      "still_marked": len(re.findall(r"\*\*V1:", text))}, indent=1))


if __name__ == "__main__":
    main()
