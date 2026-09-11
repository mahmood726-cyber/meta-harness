# Blind-judge log

Every deficiency a blind judge names is fixed in the **harness**, never patched on the page.
Record per topic: what the judge said · what changed in the machinery · whether the next topic
cleared it unaided.

---

## Topic 1 — colchicine for prevention of pericarditis recurrence
- **Registration SHA:** 34023da · **Published:** 40ebe40 · **Live:** /reviews/colchicine-recurrent-pericarditis/
- **Blind pair (neutral, opaque tokens):** ours `m979b0810`, comparator `m29f6dc16` (Imazio 2012 Heart, PMID 22442198, OA)
- **Fresh-clone reproduction:** byte-identical (empty git status after rebuild); census failures 0.
- **Result read by the judge (proof of reading):** ours k=3 RR 0.469 (0.266–0.827); comparator k=5 RR 0.40 (0.30–0.54). Correct.
- **Verdict:** Page 2 (ours) higher, **27 vs 14 / 35**.

### What the judge said (deficiencies)
1. **Both pages thin on secondary efficacy outcomes** (only primary recurrence). [scored (c)=2/2 both]
2. **Our harms are thin** — one GI estimate at k=1; discontinuation declared absent. [(d) ours 2 vs comparator 3]
3. (Implicit, and confirmed by self-audit) The comparator page names **zero trials** and declares Protocol/Screening/Reproducibility **absent** — but that is because **my `build_comparator_core` renders the comparator from its abstract only**, not because the published meta is that thin. **The win is therefore not clean.**

### What must change in the MACHINERY (queued, before the win counts)
- **F1 — faithful comparator rendering (highest priority).** The comparator page must represent the published meta's *actual* content: its included-trial list, its stated methods, its harms. Either extract them from the comparator's full text, or (cleaner) prefer comparators whose full text is machine-retrievable (PMC), so the benchmark is rendered fairly. Until then, blind wins are provisional.
- **F2 — carry secondary/harms outcomes wherever the sources report them** (e.g. symptom persistence at 72 h, hospitalization, which CORP/CORP-2/ICAP report), so "their outcomes not fewer" is met on breadth, not just the primary.
- **F3 — harms pooling** should include every trial that reports a harm count, and declare (not omit) the rest.

### Round 2 — after automating the harness end-to-end (commit 7a01637)
The whole page is now produced by one command (fetch→cache→screen→extract→synth→render→publish);
**no number typed by a human**; fresh-clone rebuild is byte-identical. The comparator is now
auto-extracted from its own PubMed abstract by the SAME pipeline, so it is no longer hand-thinned.
- **Verification caught two harness bugs before they shipped** (fixed in machinery, not on the page):
  (1) COLCORONA (COVID) false-included via an incidental "pericarditis" mention → population now
  anchored on title/conditions; (2) CORP's effect taken from the symptom-persistence clause →
  stopped splitting sentences on ";". Both are general fixes, not tuned to this topic.
- **Re-judge (blind, order swapped):** ours **25** vs comparator **11 / 35** → ours higher. The
  margin now rests on traceability/data-completeness (PMIDs + arm counts + reproduction census)
  vs the comparator's abstract-only pooled summary — the legitimate auditability value, not a
  manufactured gap.
- **Residual deficiencies (still open, queued):**
  - **F2** outcome breadth — both pages show only the primary; auto-extract secondary outcomes.
  - **F3** harms — declared absent; auto-extract harm outcomes.
  - **F1-deep** comparator full-text fidelity — a meta's *abstract* lacks its trial table/methods;
    to render the comparator fully fairly, fetch its full text (or prefer PMC comparators).
  - include-list precision — 7 screened-in but only 3 pooled; the 4 extras (anakinra trial, design/
    rationale papers) are declared-absent but the drop should be explained on the page.

### Did the next topic clear these unaided?
- Pending (topic 2 not yet built). To be recorded here.

---

## Topic 2 — colchicine for postoperative atrial fibrillation
- **Registration SHA:** 1766484 · **Published:** 08f78bf · Comparator Zhao 2022 (PMID 36050741, PMC, OA), POAF RR 0.62 (0.52–0.74), k=9.
- **Fresh-clone reproduction:** byte-identical (both topics). Negative control CORP excluded (wrong population); positive controls (COPPS-2 25172965, 32720823, 29237033) recovered.
- **Blind verdict:** ours **24** vs comparator **15 / 35** — ours higher on PROCESS (trial IDs, arm counts, PM+HKSJ, reproduction census).

### Did topic 2 clear topic 1's defects UNAIDED?
- **Inherited without help:** multi-outcome extraction (F2/F3), title-anchored population (no COLCORONA-type incidental include), resistance-guard (anakinra auto-excluded), and F1-deep pulled the comparator's GI-harm RR 2.65 from Zhao's PMC **full text**. These carried over.
- **New general extractor gaps it surfaced (fixed in machinery; topic 1 regression still passes = general, not patches):** square-bracket percentages + `n=NNN` inferred per-arm denominators (COPPS-2 AF secondary 61/180 vs 75/180); the generic "primary outcome/endpoint" anchor now applies ONLY when the trial's primary outcome IS ours (COPPS-2's primary is postpericardiotomy syndrome — was being read as AF).

### The defect topic 2 EXPOSED — and it is a DATA-LIMB loss, not a win
- The blind judge ranked ours higher on process **but explicitly judged the comparator better on completeness and point-estimate correctness**: we pooled **3 of ~9** trials → **underpowered null RR 0.82 (0.48–1.40)** vs the established RR 0.62 (0.52–0.74). Per "equal has both limbs," **topic 2 does NOT match k and is NOT equal on data.**
- **Next harness priority (F4 — search recall):** our search/screen recover far fewer trials than the comparator (retmax caps, query breadth, and NCT-registration-only records with no results). Raising recall so k approaches the comparator's is the top fix before more topics — a data-limb fix, which is what actually decides "equal."
- Also flagged: page shows k=3 pooled but 6 screened-in (reconcile the overview count); minor blinding leak (our Screening tab lists the comparator's PMID as an excluded meta — not mappable since the comparator page shows no PMID).

---

## Topic 1 — re-judge after F2/F3/F4 (pages improved)
- Blind verdict (order swapped): ours **25** vs comparator **17 / 35** — ours higher (was 25 vs 11 pre-F2/F3; comparator rose to 17 because it now shows 3 outcomes incl 2 harms via full-text).
- **Two persistent cross-topic limbs the judge named (track across all topics):**
  1. **Harms depth** — our GI harm in CORP-2 is reported word-form ("nine ... vs nine", no %), so the conservative extractor declares it absent; the comparator pools 2 harms. Ours loses the harms limb until harms extraction is deepened (word-form counts / count-only pairs). Weigh against fabrication risk.
  2. **Include-list precision** — 6 screened-in, 3 pooled; the 3 extras are design/rationale/duplicate reports of already-included trials. Pool stays correct (they're declared-absent), but the include count reads high. Fix generally only if it recurs on the lane topics.
- Data-completeness/provenance win is stable and is the genuine value proposition.

---

## Topic 4 — azithromycin for COPD exacerbations — DECLINED (honest non-production)
- Registered (protocol+config+cache committed, Codex lane 2) and comparator resolved well
  (PMID 30538443, OA; patients-with-exacerbation OR 0.40). But **k=0**: the 5 included trials
  report the exacerbation outcome as **time-to-first (HR), rate ratio per patient-year, or median
  time** (e.g. Albert 2011: "median time to first exacerbation 266 vs 174 days"), not a poolable
  proportion, and the abstracts give no clean effect+CI to extract. The comparator harmonised these
  from full trial data; the harness cannot from abstracts.
- **Decision:** do NOT publish a hollow k=0 page. Declared not-yet-produced. To produce honestly
  would need rate-ratio/HR-of-time-to-first pooling as the primary AND per-trial full-text data —
  a real harness extension (deferred; noted as a general capability gap, not a topic patch).
- The registration stays committed; no page is claimed live. This is a result (a named refusal), not a gap in n.

## Topic 5 — corticosteroids for CAP mortality — DECLINED (honest non-production)
- k=0: included trials report mortality as P-values or "did not differ" with no counts/CI in the
  abstract (Confalonieri 2005 "mortality (p=0.009)"; another "30-day mortality did not differ").
  Not conservatively extractable from abstracts. Comparator resolved OA. Declared not-produced, no hollow page.

## Topic 6 — statins for primary prevention in the elderly — LIVE (honest k=1)
- k=1: JUPITER older-persons subgroup (PMID 20404379, HR 0.61, 0.46-0.81, verified TRUE against source
  "1.22 vs 1.99 per 100 person-years"). Comparator PMID 39076238 (OA), total CV HR 0.75. Neg control excluded.
  Thin (one post-hoc subgroup) and declared as such; a legitimate honest k=1, not inflated.

---

## Blind-judge sweep — 8 live topics, all URL-only, verdicts
| Topic | ours | comparator | winner | ours k / comp |
|---|---|---|---|---|
| colchicine-recurrent-pericarditis | 25 | 11 | OURS | 3 / 5 |
| colchicine-postop-af | 24 | 15 | OURS | 3 / 9 |
| tranexamic-acid-pph | 21 | 12 | OURS | 1 / (IPD) |
| statins-primary-prevention-elderly | 24 | 11 | OURS | 1 / many |
| balanced-crystalloids-vs-saline | 27 | 12 | OURS | 2 / 6 |
| sglt2-hfref | 22 | 13 | OURS | 1 / 2 |
| finerenone-ckd | 22 | 18 | OURS | 1 / 2 |
| probiotics-aad | 30 | 9 | OURS | 13 / (large) |
**Result so far: 8 live, 8/8 blind wins.**

### The honest pattern (both limbs)
- **Ours wins the AUDITABILITY limb decisively every time** — named trials + PMIDs, arm counts, declared method, protocol SHA, content hash, offline-replay census. The comparator is repeatedly "an unauditable transcription."
- **Ours consistently LOSES the DATA-COMPLETENESS limb** — we pool fewer trials (k=1-3) than the comparator's larger pools, and judges repeatedly note the comparator's estimate is "the more clinically complete/plausible answer." probiotics (k=13, RR 0.62 vs comparator 0.63) is the exception and the model to reach.
- Judges win on quality *because the rubric rewards verifiability*; a reader wanting the best effect estimate would often still prefer the comparator. So the wins are real but the data limb is the standing gap.

### Fix applied this round (judge-flagged, general): F5 k=1 honest presentation
- Showing Paule-Mandel/HKSJ/tau2/PI on a single pooled trial is incoherent (flagged on TXA, statins, sglt2). k=1 outcomes now state "single included trial — the trial's own effect; no random-effects pooling" and omit tau2. Applied to all 4 k=1 live topics; multi-k unchanged; tests green.
- **Standing priority remains raising k** (search recall + extraction depth) so the data limb catches up — that is what "equal" actually needs.

## Topic — prone positioning in ARDS — DECLINED (uninformative at k=2)
- k=2 (PROSEVA HR 0.44 severe ARDS; an older mixed-severity trial RR 0.97) — genuine clinical
  heterogeneity by ARDS severity. Naive RE pool: RR 0.67 but tau2=0.29 with t_{k-1}=t_1 gives a CI of
  0.005-100 — correct under the declared method but uninformative and reader-hostile. Declining rather
  than publishing a nonsense-CI page; an honest synthesis needs severity stratification (harness gap).
## Topic — omega-3 for CV events — LIVE (honest k=3)
- k=3 (VITAL 785/6539 vs 795/6539; REDUCE-IT HR 0.75; a null trial HR 1.01) RR 0.91 (0.60-1.37);
  comparator PMID 35905212 (OA) major CV 0.94. Neg control excluded. Direction matches; honest wide CI.

## Topic — IV iron in HFrEF — DECLINED (k=0)
- HF-hospitalisation reported as composites ("CV death or first HF hospitalisation") or recurrent-event
  rate ratios across trials; not uniformly extractable from abstracts to a common RR. Comparator PMID
  39727669 (OA) total HF hosp RR 0.59. Declared not-produced. (Deferred general gap: 'rate ratio' /
  recurrent-event support in the effect parser + rate-ratio pooling.)

## Topic — GLP-1 RA for MACE in T2D — LIVE (strong k=7)
- k=7 (LEADER/SUSTAIN-6/REWIND/PIONEER-6/HARMONY/AMPLITUDE-O/ELIXA HRs) RR 0.85 (0.79-0.91) ~ comparator
  PMID 34526024 (OA) MACE 0.86. Second large-k match after probiotics; neg control excluded. Verified.
## Topic — metformin for ovulation in PCOS — DECLINED (k=0)
- Ovulation reported as rates/proportions not conservatively extractable from abstracts; comparator PMID
  31845767 (OA) OR 2.64. Extraction-recall gap (same family as CAP/COPD).

## Wave-4: 4 published, 2 declined
- pcsk9-mace: k=2 (FOURIER+ODYSSEY HR 0.85) ~ comparator 0.83. sglt2-ckd-progression: k=3 (DAPA-CKD 197/2152,
  CREDENCE HR 0.70, EMPA-KIDNEY 432/3304) HR 0.71 vs comparator 0.62. noac-vs-warfarin-af: k=3 DOAC HRs, pooled
  0.86 vs comparator 0.81 (pairwise subset of an NMA, declared). tocilizumab-covid19: k=1 (RECOVERY 0.85) vs WHO-REACT 0.86.
- DECLINED hfnc-reintubation: k=1 outlier (a VenturiMask trial, 13% vs 11%, HFNC worse) contradicts the evidence base; unrepresentative.
- DECLINED antibiotics-vs-appendectomy: WRONG-OUTCOME — CT.gov substring match grabbed "Resolution of Appendicitis
  Symptoms" (success) for our "treatment failure" outcome. Caught by hand-verification. Flags a CT.gov-substring risk
  when config keywords are disease-broad rather than outcome-specific (do not publish a wrong-outcome number).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Wave-4 BLIND VERDICTS (4 of 4 wins) — recorded 2026-09-11
Neutral opaque-token pair per topic; subagent judge, /35 on 7 criteria, ours = the reproducible page.
- **pcsk9-mace**: OURS 27 vs comparator 8. Named FOURIER(28304224)+ODYSSEY(30403574), arm counts, PM+HKSJ, SHA/census. Judge caveats (against us, both visible): k=2 HKSJ t_1 CI 0.585-1.23 crosses null (known small-k pathology); flagged a likely trial-label mixup (30403574 = ODYSSEY/alirocumab). Comparator = unauditable transcription.
- **sglt2-ckd-progression**: OURS 28 vs 8. Named DAPA-CKD(32970396)+CREDENCE(30990260)+EMPA-KIDNEY(36331190), PM tau2=0.00509, PI, SHA/hash/census; distinguished 3 data-bearing from 7 ongoing NCTs. Comparator claimed k=10 with zero identifiers.
- **noac-vs-warfarin-af-stroke**: OURS 24 vs 10. Named RE-LY/ROCKET/ARISTOTLE by PMID; declared pairwise-subset-of-NMA honestly. Judge caveat: our HKSJ CI 0.681-1.08 crosses null (omits ENGAGE from primary) — visible/auditable vs comparator's unverifiable HR 0.81.
- **tocilizumab-covid19-mortality**: OURS 25 vs 9. RECOVERY(33933206) 621/2022 vs 729/2094; SAE pooled k=2; SHA/hash/census. **Judge-flagged real defect (extraction-coverage): 13 trials screened in but primary rests on k=1 — REMAP-CAP/EMPACTA reported 28-day mortality yet were "declared absent". This is the keyword-brittleness class; the class fix should recover them and raise k.**

### Blind record to date: 16 of 16 topics judged, ours higher on all 16.
### Standing gap unchanged: we win the AUDITABILITY limb every time; DATA-completeness (k) is the limb to close — tocilizumab is the sharpest live example (k=1 where k could be ~5+).

## Tocilizumab k=1 investigated (2026-09-11) — judge's "coverage gap" is mostly CORRECT behavior
The tocilizumab-covid19-mortality judge flagged "13 screened, k=1 primary; REMAP-CAP/EMPACTA
reported 28-day mortality yet declared absent." Investigated the 12 declared-absent: sampled 5,
ALL report a DIFFERENT primary than our strict "28-day all-cause mortality":
 - 34609549 REMDACTA: primary = time to hospital discharge.
 - 33631066: primary = clinical status on a day-28 ordinal scale (1-7).
 - 33332779 EMPACTA: primary = COMPOSITE "mechanical ventilation OR death by day 28" (12.0% vs 19.x%).
 - 40232661: is itself a META-ANALYSIS ("death or IMV" RR 0.83), not a primary RCT.
RECOVERY is the one trial reporting 28-day ALL-CAUSE mortality as a clean per-arm count (621/2022 vs
729/2094). Reading a composite (MV-or-death), ordinal, or discharge outcome as "all-cause mortality"
would be a WRONG-OUTCOME error — the only failure mode that matters. So k=1 is DEFENSIBLE for the
strict estimand; the page's declared-absent list is honest. Legitimate lever to raise k = CT.gov
SECONDARY outcome-measure "all-cause mortality (day 28)" tables (structured, arm-level, TRUE) — a
careful reach pass, NOT a keyword change. Deferred; must never substitute a composite for the estimand.
No code changed (no wrong-number risk taken). Discipline: I was inclined to ACCEPT the judge's
coverage-gap framing and "fix" it; the data showed it was largely correct — test the finding you accept.

## Wave-5 integrated (2026-09-11): 3 published, 1 declined — all numbers verified TRUE vs source
Codex lanes authored config+protocol+cache+VERIFY (source-quoted); I verified every number, gated, published.
- **ticagrelor-vs-clopidogrel-acs**: k=1 PLATO (PMID 19717846) HR 0.84 (9.8% vs 11.7%); comparator PMID 28545073 (OA). Neg control (a stroke trial) excluded; DISPERSE-2 declared-absent (reports bleeding/MI/pauses, not MACE composite). Lane's earlier HR 1.25 was an intermediate state; final = correct 0.84.
- **semaglutide-obesity-mace**: k=1 SELECT (PMID 37952131) HR 0.80 (569/8803=6.5% vs 701/8801=8.0%); comparator PMID 39345822 (OA, GLP-1/tirzepatide MACE OR 0.79). The surrogate-warning worked: it extracted the MACE HR, NOT the body-weight MD that corrupted the earlier exploration.
- **denosumab-vertebral-fracture**: k=1 FREEDOM (PMID 19671655) RR 0.32 (2.3% vs 7.2%); comparator PMID 36852077 (OA) RR 0.33. DIRECT (24646104) excluded per PRE-SPECIFIED protocol rule (excludes mixed women-and-men trials) — protocol-consistent, not a bug.
- **sacubitril-valsartan-hfref DECLINED (k=0 on the honest pipeline)**: PARADIGM-HF's abstract HR "hazard ratio in the LCZ696 group, 0.80" is UNPARSEABLE because the drug code LCZ696 carries DIGITS inside the effect-parser gap (`[^0-9]` cannot cross "696"); per-arm denominators are not in the abstract (only total 8442 + rounded %); and pooling a count-derived RR against an HR-estimand topic is not clean. The lane's claimed k=1 did NOT reproduce on the committed pipeline. No page (decline).
  - **GATE HARDENED as a result**: check_primary_result now REFUSES any page whose primary outcome has no pooled result (k=0/None) — a hollow page is refused automatically, not by a human noticing. Regression test added; sacubitril now refuses, all live pages pass.
  - **Documented extraction defect (deferred, general): drug codes containing digits (LCZ696, AZD6140, ...) between an effect-kind token and its value break _EFFECT.** A safe fix must not let the digits be read as the value. Until fixed, such trials fall back to counts (if per-arm denominators exist) or decline.

### After wave-5: 19 live, 9 declined.

## PUB-UNEXT classification (Codex first-pass + my adjudication, 2026-09-11) — most "unextractable" is CORRECT absence
Verdicts: A=real extraction miss (recoverable), B=reach (bare %/full-text only), C=different outcome (correct absent), D=not eligible (screening should exclude).
- **colchicine-secondary-cv (15 pub-unext): A=2, B=1, C=9, D=3.** 9 report imaging/biomarker/mechanistic outcomes (plaque, LVMI, OCT, CK-MB, restenosis) — correctly absent for MACE. 3 ineligible (cost-effectiveness model, LoDoCo2 subgroup, cytokine sub-study). Genuine misses: 34876021 ("8 events colchicine vs 28 placebo", no inline denom), 32862667 ("24 vs 38 events", no inline denom).
- **probiotics-aad (≈19 pub-unext): A=5, B=12, C=1, D=6.** 12 report AAD as bare % (reach), 6 ineligible (2 protocols, treatment-not-prevention, observational). Genuine misses with explicit per-arm N/M: 22472744 (13/98 vs 16/106), 18949181 (4/41 vs 5/45), 16572062 (7/78 vs 1/73). 30149135 reports diarrhoea under MULTIPLE definitions (ambiguous — do NOT auto-extract, wrong-number risk). 24044687 needs effect inversion (risky).
- **Conclusion: our pooled k is largely CORRECT for the strict outcome** — PUB-UNEXT is dominated by different-outcome/surrogate studies and bare-% reporting, not extraction defects. The real, safe misses are few (~2 colchicine + ~3 probiotics with explicit N/M).
- **Extraction-pattern gaps identified (front-four #3):** (1) "P% (N/M)" percentage-FIRST order (e.g. "9% (7/78) ... 1.4% (1/73)"); (2) generic arm labels "study group"/"treatment group"/"intervention group" not assigned to intervention; (3) counts without inline denominators ("8 events ... 28 events"); (4) multi-definition outcomes (must pick the right definition or skip). To be fixed carefully with per-trial verification; probiotics stays k=13 (verified flagship) until then.

## Wave-5 BLIND VERDICTS (3 of 3 wins) — 2026-09-11
Neutral opaque-token pairs, URL-only subagent judges, /35.
- ticagrelor-vs-clopidogrel-acs: OURS 28 vs comparator 9. Named PLATO (19717846) HR 0.84 + major-bleeding arm counts (961/9235 vs 929/9186); 31-record screening log; SHA/hash/census. Comparator = unnamed 2017 transcription (OR 0.83, no trials).
- semaglutide-obesity-mace: OURS 23 vs 9. SELECT (37952131) 569/8803 vs 701/8801, HR 0.80; SHA/hash/census. Comparator claimed k=16 with zero identifiers, OR 0.79 (implausibly near SELECT alone). Judge nit: our k=1 method boilerplate says log(RR) while estimand is HR — label precision.
- denosumab-vertebral-fracture: OURS 27 vs 9. FREEDOM (19671655) RR 0.32 (2.3% vs 7.2%); SHA/hash/census. Judge nit: at k=1 "Pooled effect" oversells (single-trial); rendered % not n/N.

### BLIND RECORD: 19 of 19 topics judged, ours higher on all 19 (all auditability wins).
### k=1-labeling polish queued: label single-trial result as "Single-trial effect", generalise method string beyond log(RR).

## omega3 recall audit integrated (2026-09-11) — k6->7, one verified add, one wrong-number caught
Codex recall audit (Europe PMC + CT.gov, free) named 14 PMID-backed missed RCTs. Integrated reproducibly:
audit PMIDs added to committed extra_pmids (re-fetchable, documented); cite_chase enabled; every candidate
went through screening + extraction + round-trip, then hand-verified against the audit's source quotes.
- ADDED (verified): OMEGA-REMODEL PMID 38184150 — O3-FA MACE HR 1.014 (0.716-1.436), double-blind. k6->7, RR 0.9316.
- CAUGHT + EXCLUDED (wrong number): SU.FOL.OM3 PMID 21115589 is a 2x2 factorial; the effect-only extractor
  bound the B-vitamin/homocysteine HR (0.9) NOT the omega-3 vascular-events HR (1.08 per source). Round-trip
  could not fire (no counts). Hand-verification caught it; excluded. FACTORIAL-EXTRACTION LIMITATION documented.
- Correctly declared-absent: open-label (JELIS, RESPECT-EPA, DART, dietary) design-excluded; OMEGA/DART bare-%.
- Registry-first/citation-chasing (cite_chase adapter) proven reproducible on the flagship not-found topic:
  the gap to comparator's ~28 is mostly our double-blind design strictness + extraction limits, not missing search.
- NOTE: SU.FOL.OM3 shows round-trip's blind spot (effect-only, no counts). Extending round-trip to effect-only
  factorial trials (or refusing effect-only when the abstract has multiple factors) is a deferred hardening.

## sglt2-ckd recall NOT integrated (2026-09-11) — estimand heterogeneity, declined (k stays 3)
Recall audit named 6 double-blind SGLT2 CV/HF trials reporting a kidney composite as a SECONDARY (EMPA-REG,
CANVAS, DECLARE, DELIVER, VERTIS, SCORED). Attempted integration via extra_pmids + cite_chase; result rejected:
- EMPA-REG (27299675) pooled with the WRONG endpoint — our extractor grabbed "doubling of serum creatinine
  70/4645", NOT our kidney composite (sustained eGFR decline/ESKD/renal death). Estimand mismatch. Excluded.
- The other 5 correctly declared-absent (composite reported as HR the keyword-extractor couldn't safely bind).
These trials define the kidney composite DIFFERENTLY (nephropathy incl. albuminuria; ≥40% vs ≥50% eGFR; some
include CV death). Pooling them with our 3 landmark CKD trials (DAPA-CKD/CREDENCE/EMPA-KIDNEY, matching
composite) would mix estimands — the wrong-outcome class. DECLINED: k stays 3 (honest, matching-composite pool).
Deferred: an estimand-aware extractor (verify the composite DEFINITION matches, not just a kidney keyword)
would be needed to safely add secondary-outcome kidney data. This is the omega3-vs-sglt2ckd contrast: omega3's
missed trials report the SAME MACE endpoint (safely poolable, +1 verified); sglt2-ckd's report DIFFERENT composites.

## Declined-topic re-attempts with the improved harness (2026-09-11) — bar holds
Re-ran declined topics through the current harness (round-trip, factorial guard, dedup, ctgov guard, cite_chase):
- azithromycin-copd: RE-DECLINED — 6 screened-in, all declared-absent (exacerbations are recurrent-event rates, not extractable to a common RR). Gate's primary-result limb correctly refused.
- corticosteroids-cap: RE-DECLINED — no extractable pooled primary; comparator RR 0.69 but trial table not machine-exposed.
- vitamin-d-ari: now produces k=1 (PMID 20219962) but HELD not published — a k=1 abstract-extraction page misrepresents a ~25-RCT field; honest-but-unrepresentative, weak. Revisit if extraction depth improves.
- iv-iron-hfref: (in progress / recurrent-event class).
Not every decline becomes buildable; re-attempting with better machinery is correct, publishing a weak/wrong page is not.

## New-topic wave (2026-09-11): spironolactone LIVE (20th); rivaroxaban + canakinumab DECLINED
- spironolactone-hfref-mortality: LIVE k=2 — RALES RR 0.70 (0.60-0.82) + EMPHASIS-HF HR 0.76 (0.62-0.93), pooled 0.72; comparator (OA) HR 0.78. Both verified; EPHESUS negative control excluded. Required the spelled-out-CI extraction fix (RALES writes "95 percent confidence interval").
- rivaroxaban-vte-treatment: DECLINED — EINSTEIN-DVT (HR 0.68) vs EINSTEIN-PE (HR 1.12) genuinely heterogeneous (tau2=0.079); k=2 HKSJ t_1 CI 0.037-20.88 is uninformative (prone-ARDS precedent). An honest synthesis needs DVT/PE handling the harness does not do.
- canakinumab-cv-prevention: DECLINED — CANTOS is a MULTI-ARM dose-ranging trial (50/150/300 mg canakinumab vs placebo); extractor bound the 150-mg HR 0.85 by clause-binding, but selecting one of three dose arms without a pre-specified rule is multi-arm ambiguity. Needs a MULTI-ARM GUARD (generalise the factorial principle: >2 randomised arms must have the comparison specified or be refused) — deferred; declined rather than publish a luck-of-binding number.
### Live now: 20 of 31 preregistered.

## Recurrent-event/rate class status (2026-09-11)
- SYNTH half BUILT + metafor-validated: Study accepts events+person-time per arm; pool() does log-rate-ratio
  (IRR), point+tau2 match metafor measure='IRR' exactly. Rate ratios now labelled IRR (not RR). A topic that
  declares estimand IRR and whose trials report a clean incidence-rate-ratio+CI (or explicit events+person-time)
  will pool correctly today.
- EXTRACTION half DEFERRED (deliberately, not rushed): the declined recurrent-event topics report heterogeneously
  — azithromycin-COPD: Albert rates 1.48 vs 1.83 per patient-year (no events, no ratio+CI); COLUMBUS 84 vs 129
  events (no per-arm person-time); others give incidence-rate ratios. Converting rates->events needs person-time
  INFERENCE (N x follow-up) and unit disambiguation ("per patient-year" vs "per 100 person-years" vs "%/yr"),
  which is the exact place wrong numbers hide. Per the standing rule (a wrong number that gate-passes is the only
  failure that matters), this extraction must be built with explicit unit parsing + refuse-on-ambiguity and
  verified per trial, NOT rushed. azithromycin/iv-iron stay declined until then. The synth is ready to receive it.

## New-topic BLIND VERDICTS (3 of 3 wins) — 2026-09-11
- spironolactone-hfref-mortality: OURS 28 vs comparator 11. Named RALES (10471456, 284/818 vs 386/838) + EMPHASIS-HF (21073363); PM/HKSJ, SHA/hash/census; even extracted a harm (hyperkalemia RR 1.34). Comparator: unauditable HR 0.78 (9 trials, no identifiers). Judge note: k=2 CI 0.32-1.61 correctly wide (HKSJ t_1), "a verifiable wide-and-uncertain answer beats an unverifiable precise-looking one."
- dapagliflozin-hfpef-hosp: OURS 25 vs 10. DELIVER (36027570) 512/3131 vs 610/3132, count-RR 0.84; SHA/hash/census; honest k=1. Comparator: unauditable HR 0.80, no trials — "could even be an off-population pool, no way to rule out."
- empagliflozin-hfpef-hosp: OURS 23 vs 8. EMPEROR-Preserved (34449189) 415/2997 vs 511/2991, RR 0.81 (recomputable from the stated incidences); SHA/hash/census. Comparator: unauditable HR 0.74.
### BLIND RECORD: 22 of 22 topics judged, ours higher on all 22 (all auditability wins; the standing data-limb pattern holds — we pool fewer, honestly, and win on verifiability).

## Recurrent-event class WIRED end-to-end (2026-09-11); real blocker is ACQUISITION not synth/parsing
extract_rate now feeds the synth IRR path: explicit per-arm events+person-time -> log-rate-ratio pooling
(metafor-validated), rendered as events/person-time. Refuses ambiguous rates (Albert's "1.48 per
patient-year" without explicit events+PT is NOT extracted). Regression: 0 change across all topics; tests added.
KEY FINDING (verified on real abstracts): the declined recurrent-event topics are blocked at ACQUISITION, not
synth or parsing. azithromycin-COPD abstracts report rates-per-patient-year (Albert) or events-without-person-time
(COLUMBUS 84 vs 129) or bare per-year counts — none carry per-arm events+person-time (or per-arm N + follow-up)
unambiguously. A careful extractor correctly REFUSES them (missing/ambiguous components) rather than infer a
denominator or guess a unit. Recovering these needs FULL-TEXT acquisition (person-time tables), a larger deferred
change; the synth+extraction are ready to receive it. Honest state: synth IRR ready, safe extraction wired,
azithromycin/iv-iron/ENGAGE stay declined until full-text acquisition — not a wrong number substituted.

## zinc-common-cold-duration DECLINED (2026-09-11) — continuous class blocked at abstract acquisition
Continuous MD synth + extractor are built/validated, but zinc trials report cold duration as MEDIANS
WITHOUT IQR (Mossad 4.4 vs 7.6), MEANS WITHOUT SD (Prasad 4.0 vs 7.1, P-value only), or proportions —
none carry per-arm SD/IQR, so MD variance cannot be computed. extract_continuous correctly REFUSES all
21 screened-in trials; gate's primary-result limb refuses the k=0 page. No wrong number. Same acquisition
limit as the recurrent-event class: **abstracts lack the per-arm variance (SD/IQR) and person-time the
pooling needs; that data lives in FULL TEXT.** UNIFYING NEXT LEVER = per-trial PMC OA full-text extraction
(free, already in the adapter set as _pmc_fulltext) — it unblocks BOTH the continuous (zinc/melatonin) and
rate (azithromycin/iv-iron/ENGAGE) classes. Synth+extractors are ready to receive full-text numbers.

## azithromycin full-text re-attempt DECLINED again (2026-09-11) — full-text lever real, but noisy-source extraction produced wrong numbers
Enabled estimand IRR + full-text on azithromycin. Result k=2 but BOTH extractions WRONG:
- Albert (21864166) pooled via CT.gov "Number of Emergency Department Visits" OM — WRONG outcome (my
  broadened keywords let ctgov title-match an ED-visits measure); the correct full-text IRR 0.73
  (0.63-0.84) was never reached because ctgov is tried before full text and matched wrong.
- 28558695 gave a SUBGROUP hazard ratio ("lowest in the HP+/AZ group"), not the main comparison.
DECLINED (reverted). The full-text lever is REAL (Albert's IRR 0.73 IS in the PMC full text), but
recovering these topics safely needs: (a) CT.gov OM outcome-IDENTITY tightening (ED-visits != our
exacerbation outcome), (b) subgroup detection in full-text/abstract extraction, (c) full-text tried
with the same outcome-scoping care. These are careful hardening steps, not a turn-tail rush. The
full-text acquisition adapter + rate/continuous extractors are committed (tested, opt-in via
fulltext:true, 0 regression) and ready once that hardening lands. Bar held: no wrong number published.

## Registry-first enumeration spike (2026-09-11) — adapter built; broad enumeration FLOODS, needs tight scoping
Codex spike built harness/registry_first.py (enumerate_nct via CT.gov v2 query.cond/query.intr; nct_to_pmids
via CT.gov referencesModule + PubMed "<NCT>[si]" secondary-source-id; four-state RAN_OK/ZERO/ERROR). Harvested
to scratch (lane-hygiene rule). Demo on omega3 (cond='cardiovascular', intr='omega-3/fish oil/icosapent'):
enumerated ~312 NCTs, resolved to ~1,114 uncached candidate PMIDs. That FLOOD is the finding: registry-first
by broad condition x intervention over-returns; to be useful it needs (a) tight PICO-scoped enumeration
(specific condition + intervention, not 'cardiovascular'), (b) screening every candidate by P/I/C/design,
(c) the extraction hardening (rate/continuous/full-text outcome-identity) that is still pending. Not a clean
turn-tail integration; the adapter is ready for a careful scoped pass. Reproducibility unaffected (unwired).

## Registry-first RECALL measured (2026-09-11) — 9/13 known omega3 trials recovered (the 7-vs-28 answer)
registry_first_pmids('cardiovascular','omega-3 fatty acids') = RAN_OK, 925 PMIDs enumerated. Of 13 known
omega3 CV-outcome trials (our pooled + recall-audit poolable), enumeration RECOVERS 9/13 — crucially
GISSI-P (10465168), SOFA (16772624), OMEGA (21060071), which our brittle title-AND queries MISSED entirely.
This is hard evidence registry-first materially lifts recall (the omega3 7-vs-28 gap). MISSED 4: OMEGA-REMODEL
(38184150), SU.FOL.OM3 (21115589 = ISRCTN not CT.gov), AREDS2 (24638908 = eye-disease condition), DO-HEALTH
(38199870) — confirms multi-registry need (ICTRP/EU CTR/ISRCTN) + that CT.gov condition tags miss off-condition
trials. INTEGRATION (make it the default search path): union enumerated PMIDs into fetch, SCREEN the ~925-flood
by P/I/C/design (precision handled by screening, recall proven here), re-pool. That re-pool needs per-trial
extraction + estimand verification (GISSI relative-risk, SOFA HR, OMEGA) and touches every cache -> a careful
scoped pass, not turn-tail. The adapter + measurement are committed; the recall metric is the run's compass.

## Registry-first RECALL per topic (2026-09-11) — the run's primary metric (harness output via scripts/recall.py)
Clean RAN_OK enumeration runs (committed registry_first:{cond,intr} queries):
- omega3-cardiovascular-events: 9/13 (0.69) — enum ~925; recovers GISSI-P/SOFA/OMEGA the title-AND queries missed.
- balanced-crystalloids-vs-saline-mortality: 3/4 (0.75) — enum 77; recovers SMART (29485925); missed SALT (27749094, registered/linked differently).
- colchicine-postop-af: 3/4 (0.75) — enum 27.
Registry-first recovers ~70-75% of known trials — substantial reach vs brittle title-AND queries. OPERATIONAL:
(a) CT.gov RATE-LIMITS concurrent enumerations -> RAN_ERROR (not RAN_ZERO; four-state working); space runs, don't
fan too many at once. (b) untracked RECALL-*.md from prior lane uses survive git reset --hard -> clean untracked
before clone reuse (never clean a tree another lane holds). recall.py is the regenerable metric; numbers above are
from clean runs. Missed trials (SALT, the omega3 4) confirm multi-registry need (ISRCTN/EU CTR/ICTRP) + NCT-link gaps.

## omega3 re-pool (priority-1): registry-first REACH validated, inclusion HELD — k=7 stands (2026-09-11)
Re-fetch with max_records=1200/max_fulltext=0 STALLED (992 records, OMEGA extra_pmid dropped from screening) → k=4 working-tree artefact of a TRUNCATED download. Per fail-closed rule, not valid data. RESTORED committed k=7 (RR 0.9316, 0.843–1.030, 86 records, reproduces).
Priority-1 verification done on committed cache (no fetch needed — all three classics already present + screened):
- **GISSI-P 10465168 → X-DESIGN CORRECT.** Abstract: "n-3 PUFA, vitamin E, both, or none (control)" — open-label, no placebo, masking=None. Protocol pre-declares design_double_blind:true. Comparator metas include it only because they don't restrict to double-blind.
- **SOFA 16772624 → X2 DEFENSIBLE.** Title population = ICD patients w/ ventricular arrhythmia; endpoint = ventricular tachyarrhythmia/death. No CV/MACE umbrella term in title. Arrhythmia trial, not MACE trial.
- **OMEGA 21060071 → INCLUDE, honestly unpooled.** Screened in (MI+omega-3+placebo+double-blind), but primary = sudden cardiac death, not MACE → no extractable per-arm MACE composite → outcome-identity keeps it out of the MACE pool correctly.
FINDING: registry-first/citation-chasing REACHED all three; harness declined each on a fact true against source (design/population/outcome-identity). "Recall is reach, not inclusion" demonstrated on a live page. 7↛13 gap = harness MORE rigorous than comparator, transparently — NOT a search miss. Declined to relax design_double_blind (would be tuning-to-pass). No number changed.

## #4 multi-registry: ISRCTN adapter added; recall data says the dominant miss is NCT->PMID, not coverage (2026-09-11)
Built ISRCTN adapter in registry_first.py: enumerate_isrctn (free-text q, intervention-alone since ISRCTN q needs whole-string co-occurrence — 'colchicine pericarditis'->0 but 'colchicine'->31; screen enforces condition downstream), _parse_isrctn_ids (pure, namespace-tolerant, offline-tested vs fixture), registry_id_to_pmids (generalises PubMed [si] across NCT/ISRCTN/EudraCT; CT.gov refs only for NCT). registry_first_pmids(include_isrctn=) unions registries with per-registry four-state + fail-closed (any registry RAN_ERROR => whole run RAN_ERROR, pmids=[]). fetch.py knob registry_first.isrctn (default off). +6 tests (63 total). Live smoke: 31 ISRCTN ids for colchicine, resolver works (first id is an unpublished 2026 trial -> 0 PMIDs, correct).
RECALL LANE ANALYSIS (serial spaced + parallel lanes): recall misses have MIXED causes. I first
asserted "dominant miss = NCT->PMID resolution" from the marginal miss table, then ROOT-CAUSED two
cases and BOTH contradicted it:
- balanced-crystalloids missed 27749094: NCT02444988/NCT02547779 references ALL carry pmids (resolution
  works fine, incl. SMART's 29485925) but not this one; the query 'critically ill'x'balanced crystalloid'
  enumerated only 19 NCTs and NCT02444951 (a guessed NCT for it) is a 404. So it is an
  ENUMERATION/LINKAGE-COVERAGE gap, NOT a citation-string resolution gap. (27749094 still pools via
  ctgov_results on an enumerated NCT, so the page is complete; only the recall metric under-counts.)
- serial lane got RAN_ZERO where parallel lanes got RAN_OK for the same topic (noac 0/4 vs 4/4, pcsk9
  0/2 vs 2/2): query-derivation/rate-limit inconsistency (serial derived cond/intr from PICO; committed
  registry_first queries differ) — an OPERATIONAL cause, not resolution.
CORRECTED IMPLICATION: did NOT build a resolution-robustness (citation->PMID) fix — the two verified
misses are not resolution gaps, and building it would have been the "test the finding you assert" trap.
Evidenced levers instead: (a) one committed query per topic + query/rate-limit consistency (the
serial-vs-parallel RAN split is a query+contention artefact, not found-nothing), (b) multi-registry reach
(banked: ISRCTN). Naming a single dominant lever needs more per-case root-causing first.

## Fast-build of the 11 unbuilt preregistered topics: ALL decline; 4 were wrong-endpoint that PASSED the gate (2026-09-11)
Attempted all 11 unbuilt topics offline from committed caches (they inherit every guard/gate/control). Result: 0 honest new pages — the harder tier, as preregistered. Bar held. Detail:
- **iv-iron-hfref-hosp** k=1 RR 0.79 (FAIR-HF2 40159390): the 0.79 is the COMPOSITE "cardiovascular death or first heart failure hospitalization" (a co-primary), NOT the declared "Heart-failure hospitalization" alone. WRONG ENDPOINT. DECLINE. (Also only 1 trial; field is missing AFFIRM-AHF/IRONMAN.)
- **vitamin-d-acute-respiratory-infection** k=1 (Urashima 2010, 20219962): 18/167 is INFLUENZA A (the trial's actual primary), not "at least one acute respiratory infection." WRONG ENDPOINT. DECLINE.
- **antibiotics-vs-appendectomy-appendicitis** k=2 (CODA 33017106 / APPAC 26080338): pooled CT.gov OMs "resolution at 30 days" / "success", not declared "treatment failure or complication at 1 year". CODA's true primary is a 30-day EQ-5D score; APPAC is 1-year but the two don't harmonize. WRONG ENDPOINT+TIMEPOINT. DECLINE.
- **prone-positioning-ards-mortality** k=3 RR 0.70: mixes PROSEVA HR 0.44 (90-day) with RRs at 28-day/ICU across two scales and three timepoints — not a clean poolable set. DECLINE.
- **hfnc-vs-conventional-o2-reintubation** k=1: endpoint correct (reintubation 72h) but 1.26 is the ODDS RATIO mislabeled RR, and k=1 (VenturiMask trial only) likely misses Hernández-2016; scale+recall issue. DECLINE for now.
- corticosteroids-cap / azithromycin-copd / zinc-cold / metformin-pcos / sacubitril-hfref: k=None (no extractable primary matching PICO). Gate auto-refuses k=0. DECLINE.
GATE-HOLE (the important part): the 4 wrong-endpoint pages ALL PASSED the full gate — the gate enforces reproducibility/controls/cross-source/primary-present but NOT that an ABSTRACT-extracted number's endpoint IS the declared outcome. Only hand-verification caught them. Per the mandate ("the harness must reach that conclusion on its own"), this must be encoded: the outcome-identity discipline (built for CT.gov OMs) needs extending to abstract extraction. Nothing shipped; working tree cleaned to the committed 22.

## Embedding-as-second-screener: FAILED (honest negative) — embedding is candidate-gen, not a screener (2026-09-11)
Tried the PRISMA/AMSTAR-2 dual-screening item via an embedding second reader (cosine(title, PICO)>=0.30 vs the rule screener). Disagreement rate 48-93% across topics — a THRESHOLD ARTIFACT, not real reviewer disagreement: embedding measures topical similarity, not ELIGIBILITY (RCT design, exact population, intervention identity), so it includes many off-topic-but-related titles the rule screener correctly excludes. Shipping an 80% "disagreement rate" would be misleading and worse than none (same principle as the appendicitis-mismatch negative). NOT shipped (dry run, nothing committed). The embedding layer stays where the 9-case test validated it: candidate GENERATION/ranking for outcome-identity, never a decider. The dual-screening PRISMA gap therefore remains OPEN; the correct fix is a capable-MODEL eligibility screener on the embedding-generated shortlist (layer 3), a larger careful build — not naive similarity.

## Prior-meta TABLE-data adapter: BLOCKED by format (0/15 OA metas parseable) — honest feasibility negative (2026-09-11)
Mahmood's k>=comparator lever = extract per-trial data from a prior meta's forest plot / characteristics table (attach at bottom of source hierarchy, provenance-rendered, non-comparator meta). INGREDIENT-PROOF before building the parser: probed 15 OA meta-analyses across 5 gap topics (colchicine-postop, spironolactone, sglt2-ckd, tranexamic, omega3) for a table with a machine-parseable per-arm 2x2 (events/total) pattern. RESULT: 0/15 had one (max n/N-cells in any table was 5, once). Recent OA metas tabulate DESIGN/total-N/follow-up in their "characteristics" tables; the per-arm event counts live in the FOREST-PLOT IMAGE, which is not machine-readable from the OA XML. So the premise "the numbers exist in the table" is false for the table — they exist in the figure. The prior-meta data path is therefore forest-plot VISION/OCR (larger, unreliable — cf. memory "vision REAL but 0-fabricated-rate unmeasured"), NOT table parsing. Did NOT build the table parser (it would find nothing). The k>=comparator gap cannot be closed by prior-meta tables; the viable structured lever remains AACT outcome_measurements (local, per-arm counts) gated by outcome-identity + per-trial verified — the composite trap (AFFIRM-AHF 'HF Hospitalizations and CV Death') means it is careful number-changing work, not a sweep.

## recall->k repetition, verified triage (2026-09-11 night)
The lever raises k ONLY when the exact per-arm number is verifiably accessible; it declines cleanly otherwise. Applied in order:
- **crystalloids 3->5 (CLEAN):** SMART (818/7942 vs 875/7860, AACT summed across 2 registrations, verified to published 10.3%/11.1%) + BaSICS (1381/5230 vs 1439/5290, abstract counts once the title-RCT screening fix corrected its wrongful X1, verified to 26.4%/27.2%). Now 5/6; SALT-ED is a search-reach gap.
- **pericarditis 3/5 (HOLD):** the 3 declared-absent are DESIGN/RATIONALE/commentary papers of the already-pooled CORP/CORP-2/ICAP trials (duplicate publications), not missed RCTs. Correctly not pooled.
- **colchicine-postop 4/9 (HOLD):** COPPS (22090167) is a genuine missed RCT (POAF substudy, 12.0% vs 22.0%, P=0.021, n=336) BUT abstract gives PERCENTAGES ONLY (no per-arm denominators, no CI), AACT NCT00128427 has no posted AF outcome, and the full text is NOT open-access (isOA=N). Exact per-arm counts are not machine-accessible, so it is NOT pooled — deriving ~20/169 from a rounded 12.0% is not exact-verified. COPPS is the canonical illustration of the field's wall: the number exists, but only in paywalled full text / the forest-plot image, not in any machine-verifiable source we can reach.
GENERAL: title-declared-RCT screening fix recovered 10 genuine RCTs from wrongful X1 across 3 topics (crystalloids +1 BaSICS [pooled], colchicine-secondary +1 LoDoCo-MI [declared-absent], probiotics +8 [declared-absent]); off-topic title-flips correctly excluded downstream.

## Screen-rule audit: field-present-required shape (RAN_ERROR != RAN_ZERO for record fields) (2026-09-11)
Triggered by the pubtype bug (title-RCT fix recovered 10 real RCTs across 3 topics). Audited every screen rule for "requires a metadata field to be POPULATED" vs "requires evidence to be ABSENT":
- **_is_rct pubtype (X1): WAS the bug** — required PublicationType to contain "randomized controlled trial"; PubMed omits it for some definitive RCTs (BaSICS). FIXED with a positive title-declared-RCT fallback. This is the true sibling of the pattern: metadata OMISSION + strong positive evidence (title) available.
- **_double_blind / X-DESIGN: NOT a bug, correctly conservative.** "Exclude unless blinding is shown" is right for a DESIGN criterion — flipping to "exclude only if non-blinding shown" would wrongly INCLUDE open-label trials whose abstract never says 'open-label' (GISSI-P: control arm, no placebo, no 'open-label' token) and corrupt the pool. Absence of design evidence must not admit a trial. Distinct from pubtype: no positive blinding evidence exists to recover.
- **_is_rct NCT branch / X2 population: same shape, low-risk + correctly conservative.** CT.gov study_type and title/conditions are near-always populated; admitting on absent population evidence would flood the pool. Left as-is (precision-conservative), documented.
CONCLUSION: the general lesson holds — a missing metadata field is "unknown", and when strong positive evidence exists elsewhere (title) the screen must use it (fixed). But where the criterion is design/population membership and NO positive evidence exists, conservative exclusion is correct, not the same defect. One instance was a real bug; the others are correct-by-purpose.
