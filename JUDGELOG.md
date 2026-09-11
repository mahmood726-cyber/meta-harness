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
