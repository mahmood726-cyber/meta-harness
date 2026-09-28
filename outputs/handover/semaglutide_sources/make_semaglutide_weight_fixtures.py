"""Semaglutide-obesity (weight review) fixtures, 2026-09-28. Every span is asserted against held bytes first.
 (1) TIMEPOINT-AWARE COMPLETENESS: STEP 11 (PMID 40825340, NCT04998136) reports at week 44 and STEP 10 (NCT05040971) at
     week 52 -- the registries' own primary time frames. For a week-68 question they are AVAILABLE_AT_OTHER_TIMEPOINT,
     never 'missing week-68 inputs' (a gap they can never close), and never pooled as week 68.
 (2) STEP 8 (NCT04074161): a four-arm trial (semaglutide, liraglutide, and a placebo matched to each). The registration
     was excluded X2 because its TITLE names liraglutide, while its family was eligible. One decision per COMPARISON
     (docs/comparison_families.json): semaglutide vs pooled placebo is eligible; liraglutide vs placebo and semaglutide vs
     liraglutide are not. The liraglutide mention names an ineligible comparison's arm, so the registration is included.
 (3) GI AGGREGATES from the original tables, PATIENTS with any GI disorder (never the adjacent EVENTS column, never a sum
     of symptoms), each with its on-treatment safety window:
       STEP 1 969/1,306 vs 314/655 (events 4309 vs 739 are NOT patients)
       STEP 3 337/407 vs 129/204
       STEP 8 106/126 vs 47/85 (semaglutide vs POOLED placebo; the liraglutide arm, 105/127, is another comparison)
 STEP 4 (20-week run-in, then continued vs withdrawal) stays excluded for an initiation question (population_none).
  PYTHONPATH=. python outputs/handover/semaglutide_sources/make_semaglutide_weight_fixtures.py"""
import hashlib, html, json, os, re

SLUG = "semaglutide-obesity-weight"
H = "evidence/acquisition_cascade/held"
X = "evidence/acquisition_cascade/excerpts"
PRIM, GI = "Percent change in body weight", "Gastrointestinal adverse events"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
flat = lambda s: re.sub(r"\s+", " ", s).strip()
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}


def dump(path, data):
    ind = 1
    if os.path.exists(path):
        m = re.match(r"\{\n( +)\"", open(path, encoding="utf-8").read())
        ind = len(m.group(1)) if m else 1
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")


def once(text, span, where):
    n = flat(text).count(flat(span))
    assert n == 1, f"{where}: {n} occurrences of {span!r}"
    return flat(span)


def local_once(text, pattern, where):
    m = [x.group(0) for x in re.finditer(pattern, flat(text))]
    assert len(m) == 1, f"{where}: {len(m)} matches"
    return m[0]


def page_text(p):
    s = open(p, encoding="utf-8", errors="replace").read()
    return flat(html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s))))


# ------------------------------------------------------------------ (1) timepoints (registry primary time frames)
R11 = f"{H}/STEP11-registration/NCT04998136.json"
R10 = f"{H}/NCT05040971/NCT05040971.json"
T11 = "Baseline (week 0), end of treatment (week 44)"
T10 = "From randomisation (week 0) to end of treatment (week 52)"
assert T11 in open(R11, encoding="utf-8").read() and T10 in open(R10, encoding="utf-8").read()
tp = "docs/timepoint_availability.json"
tpd = json.load(open(tp, encoding="utf-8")) if os.path.exists(tp) else {
    "_doc": ("Trials whose result is AVAILABLE AT ANOTHER TIMEPOINT than the protocol's (harness/completeness.py): in the "
             "inventory, not a gap, never pooled as the protocol's timepoint. Each with a held witness of its own time frame."),
    "topics": {}}
tpd["topics"][SLUG] = [
    {"trial": "PMID 40825340 NCT04998136", "label": "STEP 11", "outcome": PRIM, "available": "week 44", "protocol": "week 68",
     "witness": W(R11, T11), "why": "its primary time frame is 44 weeks; a week-68 result will never exist"},
    {"trial": "NCT05040971", "label": "STEP 10", "outcome": PRIM, "available": "week 52", "protocol": "week 68",
     "witness": W(R10, T10), "why": "its primary time frame is 52 weeks; a week-68 result will never exist"}]
dump(tp, tpd)

# ------------------------------------------------------------------ (2) STEP 8: one decision per comparison
R8 = f"{H}/STEP8-registration/NCT04074161.json"
r8 = open(R8, encoding="utf-8").read()
for s in ("in Subjects With Overweight or Obesity", "each of the two active treatment arms will be double blinded against placebo"):
    assert s in r8, s
cp = "docs/comparison_families.json"
cfd = json.load(open(cp, encoding="utf-8"))
POPW = W(R8, "in Subjects With Overweight or Obesity")
DES = W(R8, "each of the two active treatment arms will be double blinded against placebo")


def comp(cid, ex, cm, **extra):
    return {"comparison_id": cid, "kind": "ARM_PAIR", "reports": ["NCT04074161", "PMID 35015037"],
            "population": {"witness": POPW}, "design": {"witness": DES},
            "arm_pair": {"experimental": {"witness": W(R8, ex)}, "comparator": {"witness": W(R8, cm)}},
            "comparator": {"witness": W(R8, cm)}, **extra}


cfd["families"] = [f for f in cfd["families"] if f.get("family_id") != "NCT04074161"] + [{
    "family_id": "NCT04074161", "registration": "NCT04074161", "label": "STEP 8", "kind": "ARM_PAIRS",
    "registration_conditions_note": ("four arms (semaglutide, liraglutide, a placebo matched to each); the title names "
                                     "liraglutide because one comparison is semaglutide vs liraglutide"),
    "comparisons": [
        comp("STEP8:semaglutide-vs-pooled-placebo", "Semaglutide", "Placebo (semaglutide)",
             pooled_comparator_note="the report's comparison is semaglutide vs POOLED placebo (both placebo arms, n=85)"),
        comp("STEP8:liraglutide-vs-placebo", "Liraglutide", "Placebo (liraglutide)"),
        comp("STEP8:semaglutide-vs-liraglutide", "Semaglutide", "Liraglutide")]}]
dump(cp, cfd)

# ------------------------------------------------------------------ (3) GI aggregates (patients) with safety windows
S1_TXT, S1_PDF = f"{H}/STEP1/repository.local.txt", f"{H}/STEP1/unpaywall.pdf"
S1 = open(S1_TXT, encoding="utf-8").read()
once(S1, "Safety focus areas¶ Gastrointestinal disorders‖ 969 (74.2) 4309 252.6 314 (47.9) 739 89.1", "STEP 1 GI row")
S1_WIN = local_once(S1, r"on-treatment period \(the time during which participants received any dose of semaglutide or "
                        r"placebo within the previous 49 days, with any period of temporary interrup- ?tion of the regimen excluded\)",
                    "STEP 1 window")
S1_HDR = local_once(S1, r"No\. of patients \(%\) No\. of events Events/100 person-yr", "STEP 1 column header") \
    if re.search(r"No\. of patients \(%\) No\. of events Events/100 person-yr", flat(S1)) else None
S3_HTML = f"{H}/STEP3/pmc_article.html"
S3 = page_text(S3_HTML)
once(S3, "Adverse events of interest e Gastrointestinal disorders 337 (82.8) 1760 334.5 129 (63.2) 333 127.4", "STEP 3 GI row")
S3_WIN = once(S3, "within the previous 49 days for adverse event analyses", "STEP 3 window")
S8_HTML = f"{H}/STEP8/pmc_article.html"
S8 = page_text(S8_HTML)
once(S8, "GI disorders 106 (84.1) 440 105 (82.7) 313 47 (55.3) 130", "STEP 8 GI row")
S8_WIN = once(S8, "(receipt of any dose of treatment within the previous 2 weeks [49 days for safety-related analyses])", "STEP 8 window")


def tab(name, source, held, rows, notes):
    p = f"{X}/{name}"
    open(p, "w", encoding="utf-8", newline="\n").write(
        f"# EXCERPT of {source}; held locally, not redistributed. Every value is verbatim from our text of the held document; "
        "the CELL BOUNDARIES are this excerpt's segmentation. PATIENTS column only is data; the EVENTS column is shown so it "
        f"can never be mistaken for patients.\n# held: {held} sha256 {sha(held)}\n" + "".join(f"# {n}\n" for n in notes)
        + "\n=== TABLES (excerpt) ===\n" + "\n".join(rows) + "\n")
    return p


T1 = tab("STEP1_Table_safety_GI.tables.txt", "STEP 1 (Wilding et al., NEJM 2021) safety table, UCL repository copy", S1_PDF,
         ["TABLE Adverse events: safety focus areas (safety analysis set)",
          "Event | Semaglutide (N=1306) patients no. (%) | Semaglutide events | Placebo (N=655) patients no. (%) | Placebo events",
          "Gastrointestinal disorders‖ | 969 (74.2) | 4309 | 314 (47.9) | 739"],
         [f"safety window (verbatim): {S1_WIN}"])
T3 = tab("STEP3_Table3_GI.tables.txt", "STEP 3 (Wadden et al., JAMA 2021) Table 3, PMC7905697 page", S3_HTML,
         ["TABLE Table 3. Adverse events: adverse events of interest",
          "Event | Semaglutide (n=407) participants no. (%) | Semaglutide events | Placebo (n=204) participants no. (%) | Placebo events",
          "Gastrointestinal disorders | 337 (82.8) | 1760 | 129 (63.2) | 333"],
         [f"safety window (verbatim): {S3_WIN}"])
T8 = tab("STEP8_Table3_GI.tables.txt", "STEP 8 (Rubino et al., JAMA 2022) Table 3, PMC8753508 page", S8_HTML,
         ["TABLE Table 3. Adverse events: safety areas of interest",
          "Event | Semaglutide (n=126) participants no. (%) | Semaglutide events | Liraglutide (n=127) participants no. (%) | "
          "Liraglutide events | Pooled placebo (n=85) participants no. (%) | Pooled placebo events",
          "GI disorders | 106 (84.1) | 440 | 105 (82.7) | 313 | 47 (55.3) | 130"],
         [f"safety window (verbatim): {S8_WIN}", "comparison: semaglutide vs POOLED placebo; the liraglutide columns are another comparison"])
va_p = f"cache/{SLUG}/verified_arms.json"
va = json.load(open(va_p, encoding="utf-8")) if os.path.exists(va_p) else {}
as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])


def put(store, pid, entry):
    rows = [r for r in as_list(store.get(pid)) if r.get("outcome") != entry["outcome"]] + [entry]
    store[pid] = rows if len(rows) > 1 else rows[0]


WIN = "on-treatment (any dose within the previous 49 days)"
DEF = "patients with any gastrointestinal disorder (MedDRA system organ class), not events, not a sum of symptoms"
ve_p = f"cache/{SLUG}/verified_effects.json"
ve = json.load(open(ve_p, encoding="utf-8"))


def superseded(pid, outcome):
    """remove the decision a new row replaces (HM3-pinned refusals: declared in scripts/hm3_screening_supersession.py) and
    return what it was -- or, on a rerun, what the arms entry already says it superseded"""
    rows = as_list(ve.get(pid))
    old = next((r for r in rows if r.get("outcome") == outcome), None)
    rest = [r for r in rows if r.get("outcome") != outcome]
    if old:
        if rest:
            ve[pid] = rest if len(rest) > 1 else rest[0]
        else:
            ve.pop(pid, None)
        return {k: old.get(k) for k in ("provenance", "reason") if old.get(k)}
    prev = next((r for r in as_list(va.get(pid)) if r.get("outcome") == outcome), None)
    return (prev or {}).get("supersedes")


for pid, a, n1, c, n2, t, span, extra in (
        ("33567185", 969, 1306, 314, 655, T1, "Gastrointestinal disorders‖ | 969 (74.2) | 4309 | 314 (47.9) | 739", {}),
        ("33625476", 337, 407, 129, 204, T3, "Gastrointestinal disorders | 337 (82.8) | 1760 | 129 (63.2) | 333", {}),
        ("NCT04074161", 106, 126, 47, 85, T8, "GI disorders | 106 (84.1) | 440 | 105 (82.7) | 313 | 47 (55.3) | 130",
         {"comparison_id": "STEP8:semaglutide-vs-pooled-placebo"})):
    sup = superseded(pid, GI)
    if sup:
        extra = {**extra, "supersedes": sup}
    put(va, pid, {"outcome": GI, "ai": a, "n1i": n1, "ci": c, "n2i": n2, "kind": "extracted_counts",
                  "provenance": "fulltext_verified_arms", "source_level": 1, "override": True,
                  "document_ref": t, "document_sha256": sha(t), "source_span": span,
                  "safety_population": "safety analysis set (participants exposed to at least one dose)",
                  "safety_window": WIN, "harm_definition": DEF, **extra,
                  "reason": (f"patients with any GI disorder {a}/{n1} vs {c}/{n2} from the trial's own table (the PATIENTS "
                             "column; the adjacent EVENTS column is not patients), on-treatment safety window")})
dump(va_p, va)
dump(ve_p, ve)
print("semaglutide-weight fixtures written")
