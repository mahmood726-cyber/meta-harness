"""M2: counterexamples through the REAL route to analysis and publication.

For every case:  valid control accepted -> ONE invalidating change to a committed input ->
the real route (scripts/build_topic.py, then python -m harness.gate) -> classify the observed
outcome against the expected refusal reason -> restore the exact input bytes -> the route
regenerates the control bytes.  Integrity metadata (integrity.json, protocol SHA, cache tracking,
records.json currency) is never touched, so an unrelated blocker cannot stand in for the clinical check.

Cost: one case = build_topic (~65 s) + gate (~68 s) + control rebuild + restoration check, about 3.3 min on
this machine; the full 28-case battery is ~95 min, so it does NOT run under the gate. The gate runs the same
28 cases in process on the real inputs (tests/test_m2_battery.py, seconds); this script is the end-to-end
measurement (page, certificate, gate verdict, byte-exact restoration) run on demand before a landing and
recorded in M2_RESULTS_battery.md (scripts/m2_battery_table.py renders it from the JSON reports).

Usage:  python scripts/m2_battery.py <repo_root> <out_dir> [case_id ...]
Outputs: <out_dir>/m2_report.json and m2_report.md  (every verdict MEASURED; observed.parity_cascade records a
         first build that refused the whole topic on the parity relation, when that happened)
"""
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
ONLY = set(sys.argv[3:])
SLUG = "glp1-ra-mace-t2d"
PRIMARY = "3-point major adverse cardiovascular events"
CACHE = os.path.join(ROOT, "cache", SLUG)
REVIEW_DIR = os.path.join(ROOT, "docs", "reviews", SLUG)
SERVED = ("review.json", "index.html", "CERTIFICATE.json", "REPRODUCTION.json")
INPUTS = [os.path.join(CACHE, "verified_effects.json"), os.path.join(CACHE, "verified_arms.json"),
          os.path.join(CACHE, "records.json"), os.path.join(CACHE, "retrieval_ledger.json"),
          os.path.join(CACHE, "comparators.json"), os.path.join(ROOT, "docs", "parity.json"),
          os.path.join(ROOT, "topics", SLUG + ".json")]
PY = sys.executable
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
SOUL = "40162642"
LEADER = "27295427"
SUSTAIN6 = "27633186"
EXSCEL = "28910237"
ELIXA = "26630143"


# ----------------------------------------------------------------------------- file helpers
def rb(p):
    with open(p, "rb") as f:
        return f.read()


def wb(p, b):
    with open(p, "wb") as f:
        f.write(b)


def load_json(p):
    return json.loads(rb(p).decode("utf-8"))


def dump_json(p, obj):
    # same shape as the committed files: 2-space indent, LF, trailing newline preserved if present
    raw = rb(p)
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    if raw.endswith(b"\n"):
        text += "\n"
    wb(p, text.encode("utf-8"))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def held_abstract(pid):
    rec = [r for r in load_json(os.path.join(CACHE, "records.json"))["records"] if r["id"] == pid][0]
    return rec["abstract"]


def edit_abstract(pid, old, new):
    """Change ONE held abstract, then re-finalise the retrieval ledger's corpus hash exactly as a
    re-fetch would (harness.acquisition.records_sha256), so the integrity metadata stays VALID and the
    certificate's corpus-drift check cannot stand in for the clinical check."""
    p = os.path.join(CACHE, "records.json")
    raw = rb(p).decode("utf-8")
    old_j, new_j = json.dumps(old)[1:-1], json.dumps(new)[1:-1]   # the file stores JSON-escaped (ensure_ascii) text
    assert raw.count(old_j) == 1, (pid, raw.count(old_j), old[:60])
    raw2 = raw.replace(old_j, new_j)
    wb(p, raw2.encode("utf-8"))
    data = load_json(p)
    assert [r for r in data["records"] if r["id"] == pid][0]["abstract"].count(new) == 1
    sys.path.insert(0, ROOT)
    from harness import acquisition  # noqa: E402  (the repo's own hash, not a reconstruction)
    lp = os.path.join(CACHE, "retrieval_ledger.json")
    ledger = load_json(lp)
    ledger["snapshot"]["records_sha256"] = acquisition.records_sha256(data["records"])
    dump_json(lp, ledger)
    # comparator panel: alias digests + character offsets of records.json are pinned; re-pin as a re-fetch would
    cp = os.path.join(CACHE, "comparators.json")
    if os.path.exists(cp):
        comps = load_json(cp)
        new_sha = hashlib.sha256(rb(p)).hexdigest()
        for c in comps:
            for trial in c.get("trial_set") or []:
                for alias in trial.get("aliases") or []:
                    if not str(alias.get("document_ref", "")).endswith("records.json"):
                        continue
                    q = alias["span"]["quote"].replace(old_j, new_j)
                    i = raw2.find(q)
                    assert i >= 0 and raw2.count(q) == 1, ("alias quote not unique after edit", trial.get("family_id"))
                    alias["span"] = {"start": i, "end": i + len(q), "quote": q}
                    alias["document_sha256"] = new_sha
        dump_json(cp, comps)
    # the same trial's verbatim spans in verified_* (typed refusals quote the abstract): re-anchor to the edited text
    for name in ("verified_effects.json", "verified_arms.json"):
        vp = os.path.join(CACHE, name)
        if not os.path.exists(vp):
            continue
        v = load_json(vp)
        entries = v.get(pid)
        if not entries:
            continue
        for e in (entries if isinstance(entries, list) else [entries]):
            for k in ("source_span", "verbatim_span"):
                if isinstance(e.get(k), str) and old in e[k]:
                    e[k] = e[k].replace(old, new)
        dump_json(vp, v)


def set_entry(d, pid, entry):
    """Replace/add the entry for `entry['outcome']` on trial `pid`, keeping the trial's OTHER outcome entries."""
    cur = d.get(pid)
    if cur is None:
        d[pid] = entry
        return
    items = cur if isinstance(cur, list) else [cur]
    items = [x for x in items if x.get("outcome") != entry["outcome"]] + [entry]
    d[pid] = items if len(items) > 1 else items[0]


def edit_ve(fn):
    p = os.path.join(CACHE, "verified_effects.json")
    data = load_json(p)
    fn(data)
    dump_json(p, data)


def leader_ft():
    return rb(os.path.join(CACHE, f"ft_{LEADER}.txt")).decode("utf-8")


def leader_mi_row():
    t = leader_ft()
    i = t.find("0.86 (0.73")
    s = t.rfind("<tr>", 0, i)
    e = t.find("</tr>", i) + 5
    row = t[s:e]
    assert row.startswith('<tr><td align="left" valign="top" rowspan="1" colspan="1">Myocardial infarction')
    return row


def leader_mace_prose():
    t = leader_ft()
    j = t.find("The primary composite outcome occurred in fewer patients in the liraglutide group")
    e = t.find("for superiority)", j) + len("for superiority)")
    return t[j:e]


SOUL_RESULT = ("a primary-outcome event occurred in 579 of the 4825 participants (12.0%) in the oral semaglutide "
               "group, as compared with 668 of the 4825 participants (13.8%) in the placebo group (hazard ratio, "
               "0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006)")
SOUL_DEF = ("The primary outcome was major adverse cardiovascular events (a composite of death from cardiovascular "
            "causes, nonfatal myocardial infarction, or nonfatal stroke), assessed in a time-to-first-event analysis.")
SUSTAIN6_DEF = ("The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial "
                "infarction, or nonfatal stroke.")
ELIXA_HF = ("There were no significant between-group differences in the rate of hospitalization for heart failure "
            "(hazard ratio in the lixisenatide group, 0.96; 95% CI, 0.75 to 1.23)")
ELIXA_DEF = ("for the primary composite end point of cardiovascular death, myocardial infarction, stroke, or "
             "hospitalization for unstable angina")


# ----------------------------------------------------------------------------- the real route
def run(cmd, timeout=900):
    t0 = time.time()
    p = subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or ""), round(time.time() - t0, 1)


def route():
    """build_topic.py then harness.gate -- exactly what the hook and CI run. Returns an observation."""
    obs = {}
    rc, out, dt = run([PY, "scripts/build_topic.py", SLUG])
    obs["build_rc"] = rc
    obs["build_seconds"] = dt
    obs["build_tail"] = out.strip().splitlines()[-12:]
    if rc != 0:
        obs["gate_ok"] = None
        obs["gate_reasons"] = ["(not run: build did not complete)"]
        return obs
    obs["served"] = {n: sha(rb(os.path.join(REVIEW_DIR, n))) for n in SERVED}
    obs["review_sha256"] = load_json(os.path.join(REVIEW_DIR, "manifest.json")).get("review_sha256")
    rev = load_json(os.path.join(REVIEW_DIR, "review.json"))
    prim = [o for o in rev["outcomes"] if o["name"] == PRIMARY][0]
    obs["k"] = (prim.get("result") or {}).get("k")
    obs["estimate"] = (prim.get("result") or {}).get("estimate")
    obs["pooled"] = {t["id"].replace("PMID ", ""): {k: t.get(k) for k in (
        "effect", "ci_low", "ci_high", "scale", "provenance", "verified", "verify_basis",
        "endpoint_admissibility", "target_endpoint_class", "verified_passage_location")} for t in prim.get("trials") or []}
    obs["absent"] = {a["id"].replace("PMID ", ""): {k: a.get(k) for k in (
        "absent_kind", "state", "reason_code", "reason", "provenance", "target_endpoint_class",
        "refused_effect", "location_state")} for a in prim.get("declared_absent_trials") or []}
    html = rb(os.path.join(REVIEW_DIR, "index.html")).decode("utf-8")
    obs["html_names"] = {pid: (pid in html) for pid in (SOUL, LEADER, SUSTAIN6, EXSCEL, ELIXA)}
    rc, out, dt = run([PY, "-m", "harness.gate", os.path.relpath(REVIEW_DIR, ROOT)])
    obs["gate_seconds"] = dt
    obs["gate_ok"] = (rc == 0 and "GATE PASS" in out)
    obs["gate_reasons"] = [ln.strip()[2:] for ln in out.splitlines() if ln.strip().startswith("- ")]
    return obs


# ----------------------------------------------------------------------------- mutations
def m_ci_wrong(d):
    d[SOUL]["ci_high"] = 0.98


def m_measure_wrong(d):
    d[SOUL]["scale"] = "OR"


def m_effect_wrong_incoherent(d):
    d[SOUL]["effect"] = 0.68


def m_effect_wrong_coherent(d):
    d[SOUL]["effect"] = 0.68
    d[SOUL]["source"] = d[SOUL]["source"].replace("hazard ratio, 0.86;", "hazard ratio, 0.68;")


def m_complement(d):
    d[SOUL]["effect"] = 0.14
    d[SOUL]["source"] = d[SOUL]["source"].replace("hazard ratio, 0.86;", "hazard ratio, 0.14;")


def m_location_wrong_doc(d):
    d[SOUL].update({"kind": "extracted_effect", "source_span": SOUL_RESULT,
                    "document_ref": f"cache/{SLUG}/ft_{LEADER}.txt", "source_level": 1})


def m_location_wrong_trial(d):
    e = copy.deepcopy(d[SOUL])
    e["override"] = True
    e["verification"] = "filed under EXSCEL by mistake: the digits are SOUL's"
    set_entry(d, EXSCEL, e)


def m_mi_cell_as_mace(d):
    set_entry(d, LEADER, {"outcome": PRIMARY, "effect": 0.86, "ci_low": 0.73, "ci_high": 1.00, "scale": "HR",
                          "kind": "extracted_effect", "override": True, "source_level": 1,
                          "document_ref": f"cache/{SLUG}/ft_{LEADER}.txt", "source_span": leader_mi_row(),
                          "verification": "Table 1 row (hand-transcribed); claimed as the primary composite"})


def m_hf_as_mace(d):
    set_entry(d, ELIXA, {"outcome": PRIMARY, "effect": 0.96, "ci_low": 0.75, "ci_high": 1.23, "scale": "HR",
                         "source": "ELIXA (PMID 26630143) abstract: " + ELIXA_HF,
                         "verification": "abstract sentence (hand-transcribed); claimed as the primary composite"})


def m_exclusion_in_source_soul():
    edit_abstract(SOUL, "(a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke)",
                  "(a composite of death from cardiovascular causes or nonfatal myocardial infarction; nonfatal stroke was excluded from the primary outcome)")


def m_exclusion_in_source_sustain6():
    edit_abstract(SUSTAIN6, "The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke.",
                  "The primary composite outcome was the first occurrence of cardiovascular death or nonfatal myocardial infarction; nonfatal stroke was excluded from the primary composite outcome.")


def m_source_changed_after_approval():
    edit_abstract(SOUL, "(hazard ratio, 0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006)",
                  "(hazard ratio, 0.88; 95% confidence interval, 0.79 to 0.98; P = 0.006)")


def m_source_changed_canonical():
    m_source_changed_after_approval()
    edit_ve(lambda d: d[SOUL].update({"kind": "extracted_effect", "source_span": SOUL_RESULT,
                                      "document_ref": f"cache/{SLUG}/records.json", "source_level": 1}))


def m_middle_dot():
    edit_abstract(SOUL, "(hazard ratio, 0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006)",
                  "(hazard ratio, 0·86; 95% confidence interval, 0·77 to 0·96; P = 0.006)")


def m_fulltext_prose_override(d):
    set_entry(d, LEADER, {"outcome": PRIMARY, "effect": 0.87, "ci_low": 0.78, "ci_high": 0.97, "scale": "HR",
                          "kind": "extracted_effect", "override": True, "source_level": 1,
                          "document_ref": f"cache/{SLUG}/ft_{LEADER}.txt", "source_span": leader_mace_prose(),
                          "verification": "full-text results prose, primary composite (hand-transcribed)"})


def m_adjudicated_unresolved(d):
    set_entry(d, ELIXA, {"outcome": PRIMARY, "kind": "typed_refusal", "provenance": "REFUSED_ON_EVIDENCE",
                "document_ref": f"cache/{SLUG}/records.json", "source_span": ELIXA_DEF, "source_level": 1,
                "reason": "ELIXA's primary composite is 4-point (adds hospitalization for unstable angina); "
                          "the 3-point MACE is not reported in the held abstract -- documented decision, "
                          "reviewer M.A., 2026-09-20"})


def m_soul_canonical_valid(d):
    d[SOUL].update({"kind": "extracted_effect", "source_span": SOUL_RESULT,
                    "document_ref": f"cache/{SLUG}/records.json", "source_level": 1})


CASES = [
    # id, class, description, mutation, expect
    ("W1a", "wrong interval", "SOUL hand entry: ci_high 0.96 -> 0.98 (source unchanged)", ("ve", m_ci_wrong),
     {"trial": SOUL, "outcome": "refuse", "reason": r"interval|ci_high|0\.98|not (located|present|found)|verified"}),
    ("W1b", "wrong effect measure", "SOUL hand entry: scale HR -> OR (source says hazard ratio)", ("ve", m_measure_wrong),
     {"trial": SOUL, "outcome": "refuse", "reason": r"measure|scale|hazard|odds|OR\b"}),
    ("W1c", "wrong effect (incoherent)", "SOUL hand entry: effect 0.86 -> 0.68 (source string unchanged)", ("ve", m_effect_wrong_incoherent),
     {"trial": SOUL, "outcome": "refuse", "reason": r"not (located|present|found)|verified|0\.68"}),
    ("W1d", "wrong effect (coherent lie)", "SOUL hand entry: effect AND source string say 0.68; held abstract says 0.86", ("ve", m_effect_wrong_coherent),
     {"trial": SOUL, "outcome": "refuse", "reason": r"not (located|present|found)|verified|held|abstract|0\.68"}),
    ("W1e", "wrong effect (RR complement)", "SOUL hand entry: effect 0.14 = 1-0.86 (source string says 0.14)", ("ve", m_complement),
     {"trial": SOUL, "outcome": "refuse", "reason": r"not (located|present|found)|verified|complement|0\.14"}),
    ("W2a", "wrong source location (document)", "SOUL canonical entry cites LEADER's full text as the document holding its span", ("ve", m_location_wrong_doc),
     {"trial": SOUL, "outcome": "refuse", "reason": r"span|document|location|absent from"}),
    ("W2b", "wrong source location (trial)", "SOUL's digits filed as an override under EXSCEL (28910237)", ("ve", m_location_wrong_trial),
     {"trial": EXSCEL, "outcome": "refuse", "reason": r"not (located|present|found)|verified|held|abstract|document"}),
    ("W3a", "wrong endpoint ownership", "LEADER override: MI-only table row 0.86 (0.73-1.00) claimed as 3-point MACE", ("ve", m_mi_cell_as_mace),
     {"trial": LEADER, "outcome": "refuse", "reason": r"endpoint|component|myocardial|ownership|DIFFERENT|COMPONENT|unbound|UNBOUND"}),
    ("W3b", "wrong endpoint ownership (abstract)", "ELIXA hand entry: HF-hospitalisation HR 0.96 claimed as 3-point MACE", ("ve", m_hf_as_mace),
     {"trial": ELIXA, "outcome": "refuse", "reason": r"endpoint|component|heart failure|ownership|DIFFERENT|COMPONENT|unbound|UNBOUND"}),
    ("W4a", "excluded component treated as included", "SOUL held abstract now says nonfatal stroke was EXCLUDED; hand entry still claims 3-point MACE", ("fn", m_exclusion_in_source_soul),
     {"trial": SOUL, "outcome": "refuse", "reason": r"exclu|component|endpoint|COMPONENT|DIFFERENT"}),
    ("W4b", "excluded component treated as included (machine route)", "SUSTAIN-6 held abstract now says nonfatal stroke was EXCLUDED (abstract-extracted row)", ("fn", m_exclusion_in_source_sustain6),
     {"trial": SUSTAIN6, "outcome": "refuse", "reason": r"exclu|component|endpoint|COMPONENT|DIFFERENT"}),
    ("W5a", "stale approval", "SOUL held abstract corrected to HR 0.88 (0.79-0.98); the 2026-09-13 approval still says 0.86", ("fn", m_source_changed_after_approval),
     {"trial": SOUL, "outcome": "refuse", "reason": r"not (located|present|found)|verified|stale|approv|held|abstract|document"}),
    ("W5b", "stale approval (canonical span)", "same erratum; SOUL entry carries a verbatim source_span that the held abstract no longer contains", ("fn", m_source_changed_canonical),
     {"trial": SOUL, "outcome": "refuse", "reason": r"span|stale|approv|absent from|document"}),
    ("P1", "control", "served inputs, no change", None,
     {"trial": SOUL, "outcome": "admit", "k": 8}),
    ("P2", "representation variant", "SOUL held abstract uses Lancet middle-dot decimals (0·86; 0·77 to 0·96)", ("fn", m_middle_dot),
     {"trial": SOUL, "outcome": "admit", "k": 8}),
    ("P3", "legitimate full-text prose override", "LEADER override: primary composite 0.87 (0.78-0.97) quoted verbatim from the held full text", ("ve", m_fulltext_prose_override),
     {"trial": LEADER, "outcome": "admit", "k": 8}),
    ("P4", "canonical hand entry", "SOUL entry carries its verbatim source_span + document_ref (records.json)", ("ve", m_soul_canonical_valid),
     {"trial": SOUL, "outcome": "admit", "k": 8}),
    ("P5", "documented decision on unresolved evidence", "ELIXA typed refusal: 4-point composite, reviewer-signed, span held", ("ve", m_adjudicated_unresolved),
     {"trial": ELIXA, "outcome": "documented_absent", "k": 8}),
]


# ----------------------------------------------------------------------------- the LEADER semantic suite
# One authentic held document (ft_27295427.txt, sha256 ded4c69e...): the real target definition, the real target
# estimate, and four REAL wrong-endpoint estimates from the same Table 1. Same digest, representation, population,
# comparator, route; every integrity check valid. Ambiguity must ABSTAIN, not choose.
def leader_row(prefix):
    t = leader_ft()
    i = t.find(prefix)
    assert i > 0, prefix
    s = t.rfind("<tr>", 0, i)
    e = t.find("</tr>", i) + 5
    return t[s:e]


def _leader_entry(effect, lo, hi, span, **extra):
    d = {"outcome": PRIMARY, "effect": effect, "ci_low": lo, "ci_high": hi, "scale": "HR",
         "kind": "extracted_effect", "override": True, "source_level": 1,
         "document_ref": f"cache/{SLUG}/ft_{LEADER}.txt", "source_span": span,
         "verification": "LEADER Table 1 / results prose, hand-transcribed (M2 LEADER suite)"}
    d.update(extra)
    return d


def m_L_control_table(d):
    set_entry(d, LEADER, _leader_entry(0.87, 0.78, 0.97, leader_row("0.87 (0.78")))


def m_L_stroke(d):
    set_entry(d, LEADER, _leader_entry(0.86, 0.71, 1.06, leader_row("0.86 (0.71")))


def m_L_expanded(d):
    set_entry(d, LEADER, _leader_entry(0.88, 0.81, 0.96, leader_row("0.88 (0.81")))


def m_L_cvdeath(d):
    set_entry(d, LEADER, _leader_entry(0.78, 0.66, 0.93, leader_row("0.78 (0.66")))


def m_L_direction_numbers(d):
    # placebo vs liraglutide: the inverted tuple is NOT in the held document
    set_entry(d, LEADER, _leader_entry(1.15, 1.03, 1.28, leader_mace_prose(), comparator_direction="placebo vs liraglutide"))


def m_L_direction_declared(d):
    # the held tuple, but the entry DECLARES the reversed direction: contradicts the column headers
    set_entry(d, LEADER, _leader_entry(0.87, 0.78, 0.97, leader_row("0.87 (0.78"), comparator_direction="placebo vs liraglutide"))


def m_L_analysis_set(d):
    # the held 0.87 is the time-to-event primary analysis; the entry claims it is the per-protocol analysis,
    # whose number is in a supplement we do not hold
    set_entry(d, LEADER, _leader_entry(0.87, 0.78, 0.97, leader_mace_prose(), analysis_set="per-protocol"))


def m_L_normalisation(d):
    # declared harmless normalisation: en dash in the cell, scale named only by the column header, ci_pct explicit
    set_entry(d, LEADER, _leader_entry(0.87, 0.78, 0.97, leader_row("0.87 (0.78"), ci_pct=95, scale="HR",
                                       normalisation="en dash -> hyphen; 'Hazard Ratio (95% CI)' column header -> HR"))


def m_L_ambiguous(d):
    # point estimate only, span = the whole Table 1: 0.86 sits in TWO rows (MI 0.73-1.00, stroke 0.71-1.06)
    t = leader_ft()
    i = t.find("0.87 (0.78")
    s = t.rfind("<table-wrap", 0, i)
    e = t.find("</table-wrap>", i) + len("</table-wrap>")
    set_entry(d, LEADER, _leader_entry(0.86, None, None, t[s:e]))


LEADER_CASES = [
    ("L0", "control (table row)", "LEADER override: Table 1 'Primary composite outcome' row 0.87 (0.78-0.97)", ("ve", m_L_control_table),
     {"trial": LEADER, "outcome": "admit", "k": 8}),
    ("L1", "wrong endpoint: MI row", "LEADER override: 'Myocardial infarction' row 0.86 (0.73-1.00) as 3-point MACE", ("ve", m_mi_cell_as_mace),
     {"trial": LEADER, "outcome": "refuse", "reason": r"INCOMPATIBLE|component|endpoint|myocardial|UNBOUND|unbound"}),
    ("L2", "wrong endpoint: stroke row", "LEADER override: 'Stroke' row 0.86 (0.71-1.06) as 3-point MACE", ("ve", m_L_stroke),
     {"trial": LEADER, "outcome": "refuse", "reason": r"INCOMPATIBLE|component|endpoint|stroke|UNBOUND|unbound"}),
    ("L3", "wrong endpoint: expanded composite", "LEADER override: 'Expanded composite outcome' row 0.88 (0.81-0.96) as 3-point MACE", ("ve", m_L_expanded),
     {"trial": LEADER, "outcome": "refuse", "reason": r"INCOMPATIBLE|component|endpoint|expanded|superset|near|UNBOUND|unbound"}),
    ("L4", "wrong endpoint: CV death", "LEADER override: 'Death from cardiovascular causes' row 0.78 (0.66-0.93) as 3-point MACE", ("ve", m_L_cvdeath),
     {"trial": LEADER, "outcome": "refuse", "reason": r"INCOMPATIBLE|component|endpoint|cardiovascular|UNBOUND|unbound"}),
    ("L5", "comparator direction (numbers)", "LEADER override: inverted tuple 1.15 (1.03-1.28), declared placebo vs liraglutide", ("ve", m_L_direction_numbers),
     {"trial": LEADER, "outcome": "refuse", "reason": r"not (located|present|found)|verified|direction|held|document"}),
    ("L6", "comparator direction (declared)", "LEADER override: held 0.87 tuple with comparator_direction 'placebo vs liraglutide'", ("ve", m_L_direction_declared),
     {"trial": LEADER, "outcome": "refuse", "reason": r"direction|comparator|arm|contradict"}),
    ("L7", "analysis set", "LEADER override: held 0.87 tuple declared as the per-protocol analysis", ("ve", m_L_analysis_set),
     {"trial": LEADER, "outcome": "refuse", "reason": r"analysis|per-protocol|population|identity|ABSTAIN|unresolved"}),
    ("L8", "declared harmless normalisation", "LEADER override: Table 1 primary row, en dash, header-declared scale, ci_pct 95", ("ve", m_L_normalisation),
     {"trial": LEADER, "outcome": "admit", "k": 8}),
    ("L9", "ambiguity must ABSTAIN", "LEADER override: point 0.86 only, span = whole Table 1 (0.86 sits in the MI row AND the stroke row)", ("ve", m_L_ambiguous),
     {"trial": LEADER, "outcome": "refuse", "reason": r"ambig|ABSTAIN|MULTIPLE|several|two|unresolved|UNBOUND|unbound|not (located|present|found)"}),
]
if ONLY and any(c in {x[0] for x in LEADER_CASES} for c in ONLY):
    CASES = CASES + LEADER_CASES


# ----------------------------------------------------------------------------- classification
def classify(case, obs, control):
    exp = case[4]
    tid = exp["trial"]
    pooled = obs.get("pooled") or {}
    absent = obs.get("absent") or {}
    gate_reasons = obs.get("gate_reasons") or []
    out = {"trial_visible": (tid in pooled) or (tid in absent) or bool((obs.get("html_names") or {}).get(tid))}
    if obs["build_rc"] != 0:
        out["verdict"] = "REFUSED_WHOLE_BUILD"
        out["scope"] = "topic (every trial, every outcome)"
        out["detail"] = " | ".join(obs["build_tail"][-3:])
        out["trial_visible"] = False
        return out
    named_in_gate = [r for r in gate_reasons if tid in r]
    if exp["outcome"] == "admit":
        if tid in pooled and obs["gate_ok"] and obs["k"] == exp["k"]:
            row = pooled[tid]
            unbound = (row.get("endpoint_admissibility") or "").startswith("UNBOUND") or row.get("target_endpoint_class") in (None, "UNBOUND_LEGACY")
            out["verdict"] = "ADMITTED_UNCHECKED" if unbound else "ADMITTED"
            out["detail"] = f"{row.get('effect')} ({row.get('ci_low')}-{row.get('ci_high')}) {row.get('scale')} prov={row.get('provenance')} class={row.get('target_endpoint_class')} verified={row.get('verified')}"
        elif tid in pooled and not obs["gate_ok"]:
            out["verdict"] = "UNNECESSARY_REFUSAL"
            out["scope"] = "page (gate)"
            out["detail"] = " | ".join(gate_reasons[:3])
        else:
            out["verdict"] = "UNNECESSARY_REFUSAL"
            out["scope"] = "row"
            out["detail"] = json.dumps(absent.get(tid))
        return out
    if exp["outcome"] == "documented_absent":
        a = absent.get(tid) or {}
        ok = (tid not in pooled and a.get("absent_kind") == "adjudicated_absent" and obs["gate_ok"] and obs["k"] == exp["k"])
        out["verdict"] = "DOCUMENTED_DECISION_RECORDED" if ok else "DOCUMENTED_DECISION_NOT_RECORDED"
        out["detail"] = json.dumps(a) if a else " | ".join(gate_reasons[:3])
        return out
    # expected refusal
    pat = re.compile(exp["reason"], re.I)
    if tid in pooled:
        row = pooled[tid]
        if obs["gate_ok"]:
            out["verdict"] = "WRONG_ADMISSION"
            out["detail"] = f"pooled {row.get('effect')} ({row.get('ci_low')}-{row.get('ci_high')}) {row.get('scale')} prov={row.get('provenance')} class={row.get('target_endpoint_class')} verified={row.get('verified')} basis={row.get('verify_basis')}; k={obs['k']} est={obs['estimate']}; GATE PASS"
        elif named_in_gate and any(pat.search(r) for r in named_in_gate):
            out["verdict"] = "GATE_REFUSED_CORRECT_REASON"
            out["scope"] = "page (the whole page is withheld; the row stays in the pool with a not-yet label)"
            out["detail"] = named_in_gate[0]
        else:
            out["verdict"] = "GATE_REFUSED_OTHER_REASON"
            out["scope"] = "page"
            out["detail"] = " | ".join(gate_reasons[:3])
        return out
    a = absent.get(tid)
    if a is None:
        out["verdict"] = "TRIAL_DROPPED"
        out["detail"] = "neither pooled nor declared absent"
        return out
    text = " ".join(str(v) for v in a.values() if v)
    if pat.search(text) and obs["gate_ok"]:
        out["verdict"] = "REFUSED_CORRECT_REASON"
        out["scope"] = "row (candidate extraction); page publishes"
    elif obs["gate_ok"]:
        out["verdict"] = "REFUSED_OTHER_REASON"
        out["scope"] = "row"
    else:
        out["verdict"] = "REFUSED_ROW_AND_GATE"
        out["scope"] = "row + page"
    out["detail"] = json.dumps(a) + ("" if obs["gate_ok"] else " || GATE: " + " | ".join(gate_reasons[:2]))
    out["k"] = obs["k"]
    return out


def workload(obs):
    """Rows a human must act on: unresolved eligible evidence (declared-absent without a documented
    decision), refused candidate extractions awaiting re-adjudication, and pooled rows admitted UNBOUND
    (no check ran, so a human is the check)."""
    pooled = obs.get("pooled") or {}
    absent = obs.get("absent") or {}
    unresolved = [pid for pid, a in absent.items() if a.get("absent_kind") in ("machine_absent",)]
    refused = [pid for pid, a in absent.items() if a.get("absent_kind") in ("refused_on_evidence",)]
    documented = [pid for pid, a in absent.items() if a.get("absent_kind") in ("adjudicated_absent",)]
    unbound = [pid for pid, r in pooled.items()
               if (r.get("endpoint_admissibility") or "").startswith("UNBOUND") or r.get("target_endpoint_class") in (None, "UNBOUND_LEGACY")]
    return {"pooled": len(pooled), "unresolved_eligible": unresolved, "refused_awaiting": refused,
            "documented_decisions": documented, "admitted_unbound": unbound,
            "reviewer_rows": len(unresolved) + len(refused) + len(unbound)}


# ----------------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    baseline = {p: rb(p) for p in INPUTS}
    served_before = {n: sha(rb(os.path.join(REVIEW_DIR, n))) for n in SERVED}
    print(f"repo {ROOT}; served review.json {served_before['review.json'][:12]}", flush=True)
    control = route()
    assert control["build_rc"] == 0 and control["gate_ok"], control
    print(f"control: k={control['k']} est={control['estimate']} gate={control['gate_ok']} "
          f"review.json {control['served']['review.json'][:12]} (served {served_before['review.json'][:12]})", flush=True)
    report = {"repo": ROOT, "head": subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip(),
              "control": {"k": control["k"], "estimate": control["estimate"], "served": control["served"],
                          "served_equals_committed": control["served"] == served_before,
                          "workload": workload(control)}, "cases": []}
    for case in CASES:
        cid, cls, desc, mut, exp = case
        if ONLY and cid not in ONLY:
            continue
        print(f"\n=== {cid} [{cls}] {desc}", flush=True)
        try:
            if mut is not None:
                kind, fn = mut
                if kind == "ve":
                    edit_ve(fn)
                else:
                    fn()
            changed = [os.path.relpath(p, ROOT) for p in INPUTS if rb(p) != baseline[p]]
            obs = route()
            verdict = classify(case, obs, control)
            wl = workload(obs) if obs["build_rc"] == 0 else None
        finally:
            for p, b in baseline.items():
                wb(p, b)
        restored = route()
        exact = restored.get("served") == control["served"]
        rec = {"id": cid, "class": cls, "description": desc, "inputs_changed": changed,
               "expected": exp, "observed": {k: v for k, v in obs.items() if k not in ("pooled", "absent")},
               "row": (obs.get("pooled") or {}).get(exp["trial"]) or (obs.get("absent") or {}).get(exp["trial"]),
               "verdict": verdict, "workload": wl,
               "restoration": {"build_rc": restored["build_rc"], "gate_ok": restored.get("gate_ok"),
                               "served_bytes_equal_control": exact,
                               "review_json": (restored.get("served") or {}).get("review.json")}}
        report["cases"].append(rec)
        print(f"  -> {verdict['verdict']}  {verdict.get('detail', '')[:220]}", flush=True)
        print(f"  restoration: build_rc={restored['build_rc']} gate={restored.get('gate_ok')} exact={exact}", flush=True)
        with open(os.path.join(OUT, "m2_report.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    write_md(report)


def write_md(report):
    lines = [f"# M2 counterexamples through the real route -- {SLUG} at {report['head'][:12]}", "",
             f"control: k={report['control']['k']} estimate={report['control']['estimate']}; rebuilt served bytes equal committed: "
             f"{report['control']['served_equals_committed']}; workload {json.dumps(report['control']['workload'])}", "",
             "| id | class | one change | expected | observed | scope | restoration exact |", "|---|---|---|---|---|---|---|"]
    tally = {}
    for c in report["cases"]:
        v = c["verdict"]
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1
        lines.append(f"| {c['id']} | {c['class']} | {c['description']} | {c['expected']['outcome']} | **{v['verdict']}** | {v.get('scope', '')} | {c['restoration']['served_bytes_equal_control']} |")
    lines += ["", "## Tally", ""] + [f"- {k}: {n}" for k, n in sorted(tally.items())]
    lines += ["", "## Detail", ""]
    for c in report["cases"]:
        lines.append(f"### {c['id']} -- {c['class']}")
        lines.append(f"- change: {c['description']} (files: {', '.join(c['inputs_changed']) or 'none'})")
        lines.append(f"- verdict: {c['verdict']['verdict']}; trial visible: {c['verdict'].get('trial_visible')}")
        lines.append(f"- detail: {c['verdict'].get('detail', '')}")
        if c["workload"]:
            lines.append(f"- workload after change: {json.dumps(c['workload'])}")
        lines.append(f"- restoration: build_rc={c['restoration']['build_rc']} gate={c['restoration']['gate_ok']} exact bytes={c['restoration']['served_bytes_equal_control']}")
        lines.append("")
    with open(os.path.join(OUT, "m2_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
