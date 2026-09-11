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
