# The RoB drift in 7 topics: root cause (7 Oct)

**What the captain saw.** A fresh `scripts/rob2_build.py` build differs from the committed `cache/<slug>/rob2.json` in 7 topics:
- colchicine-postop-af
- colchicine-secondary-cv-prevention
- doac-vte-recurrence
- esketamine-trd-madrs
- metformin-pcos-ovulation
- pcsk9-mace
- sglt2-ckd-progression

**Reproduced.** The same 7 topics drift on this branch, with the AACT 2026-08-30 snapshot and the embedding model available. The evidence is in `outputs/d11/rob_drift.json`.

**Root cause: staleness, not the model.** All 7 committed `rob2.json` files were last written on 17 Sep (04902ecf). Each topic's `review.json` has been rebuilt since, most recently on 7 Oct, and `rob2_build.py` reads the review's primary outcome (its name and its pooled trials). Nothing ties `rob2.json` to that input, so a rebuild of the review never invalidated it. Two consequences follow.

1. **Stale membership.** Three trials are still rated although they are no longer pooled in the primary outcome:
   - colchicine-postop-af 27502857
   - esketamine NCT02417064
   - pcsk9 41211925

2. **A stale D5 input.** The primary outcome was renamed in 5 topics (e.g. "Trial-defined major kidney / cardiorenal composite" became "Trial-defined primary cardiorenal composite"). The renamed labels are generic ("trial-defined ... composite"), so the D5 component parser finds no components. A fresh build therefore calls each trial's own registered primary *unregistered* ("some concerns"):
   - colchicine-secondary 31733140 and 39555823
   - sglt2-ckd 30990260, 32970396 and 36331190

   For doac, metformin and esketamine only the stored input string changes; the level stays the same.

**Which side is right.** For sglt2-ckd (an active topic), the D11 panel read the registry and abstract:
- **D5 low for CREDENCE (30990260) and DAPA-CKD (32970396).** The committed "low" is right; the fresh "some concerns" is wrong.
- **EMPA-KIDNEY (36331190): panel "some concerns".** Reader B said low; the adjudicator, which shares reader A's model family, sided with A.

Colchicine-secondary is abandoned and not in D11.

**The class, and the fix to decide.** `rob2.json` is a derived artefact with no staleness check against its inputs. A sound fix has two parts:
- Record the input-set hash (primary outcome name plus pooled trials) in `rob2.json`, and refuse to serve a `rob2.json` whose inputs changed. This is the same pattern as `rob_sensitivity.input_set_version`.
- Teach D5 that a "trial-defined" pooled composite is compared against each trial's own registered primary.

Both change served ratings, so they wait for Mahmood. Nothing was changed here; the committed files were restored after the measurement.
