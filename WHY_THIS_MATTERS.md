# Why this matters — and exactly how far the claim goes

_Every claim below points at a committed artefact you can open and check. Live counts (verified numbers,
error-library coverage, the error rate) are **self-counted on the published index** and in the JSON named
here — read them there, not from prose, so this document cannot drift. Structural counts (33 error classes,
14 gate limbs) come from the code._

## The claim, stated precisely

This harness does **not** produce a guaranteed-correct meta-analysis. The same audit that motivates it found
**13 wrong numbers on pages that had passed every gate** (12 in the cycle-75 source re-audit; 1 more — a
gastrointestinal-harms row that had pooled the trial's *overall* adverse-event count — surfaced by the
cycle-76 blind accuracy census and fixed). A machine that can ship a wrong number is not a machine that
replaces the reviewer.

What it does instead is the thing published meta-analysis does not: **it produces a fully auditable draft
and makes human checking tractable.** Every pooled number carries a verbatim source span; every
include/exclude carries a rule id and a span; every refusal is rendered with its reason; and the entire
review regenerates byte-for-byte from a committed protocol commit. A human checking one of our pages can
verify a number against its source in seconds. A human checking a published meta-analysis usually cannot
verify it at all — the extraction, the search, and the discarded candidates are not in the paper.

So the honest framing is a **reframe of the human role, not its removal**: from *doing* the extraction to
*adjudicating* it.

## What is genuinely new here — each backed by a measured artefact

1. **Byte-reproducible from a protocol SHA.** The protocol is committed before synthesis; a fresh clone
   regenerates every page's exact bytes offline from the committed queries and cache.
   → `scripts/reproduce_review.py` (and `--fresh-clone`); the gate limb `check_reproduction`.
2. **Every pooled number verified to a verbatim span, gate-enforced.** A page that pools a number not
   located in its committed source is refused — so the property cannot silently stop being true.
   → gate limb `check_pooled_verified`; each `docs/reviews/<slug>/review.json` trial carries its `source`
   span and `verified` flag (live count self-counted on the index).
3. **A documented meta-analysis error library, mechanically checked per review.** 33 classes, each realised
   as a gate limb, a regression test with a plant, or a rendered disclosure — a claim no published review
   makes about itself. → `harness/error_library.py`, `docs/error_coverage.json`.
4. **Publication bias measured by registry census, not funnel asymmetry.** Registered-but-unpublished
   completed trials are counted directly from the trial registry (far more reliable than funnel plots at
   small k) and feed the GRADE publication-bias domain. → `cache/<slug>/ghost.json`; `harness/grade.py`.
5. **Refusals are rendered, not discarded.** "We found it, verified it, did not pool it, because…" — the
   declared-absent trials with reasons are information a published review throws away.
   → `declared_absent_trials` in every `review.json`; the absent-override tier in `harness/pipeline.py`.
6. **Parity decomposed trial by trial.** Where our `k` is below a comparator's, the difference is explained
   trial by trial (open-label excluded, prophylaxis vs treatment, drug-class vs single agent, imputed
   variance declined) rather than asserted. → `docs/parity.json`; the per-page comparator tab.
7. **Speed with reproducibility.** 29 reviews, each regenerable from one command, built in days.
   → `docs/reviews/` (29 topics); `python scripts/build_topic.py <slug>`.

## The measured accuracy — and why it is the deliverable that unlocks the rest

The blind accuracy census re-extracted every pooled number from committed source with a checker **blind to
the stored value**, then compared deterministically and adjudicated the disagreements against source.
→ `scripts/error_rate_compare.py` + `scripts/error_rate_pass2.py`; the committed sample and result live in
`docs/error_rate_sample.json` and `docs/error_rate.json`, and the headline is rendered on the index.

This number is what gives "human-checked" a **budget**. A reviewer adjudicating a machine draft needs to
know whether they are checking one error in a hundred or one in ten; without a measured residual error rate
the phrase is empty. Because the figure is measured once against a committed sample, `error_rate.json`
records the measurement date and the sample it was measured against, and a **freshness invariant refuses a
stale figure if the pooled population changes** — a measured-once number that looks live is the stale-number
class in a new costume, and it is guarded exactly like the retraction/integrity snapshot.

## What still requires a human — stated plainly

- **Risk-of-bias judgement.** Our RoB2 is computed from registry fields for a subset of trials and reaches
  "some concerns" at most; the reading-dependent domains and the overall clinical judgement are a human's.
- **PICO framing and clinical relevance.** Whether the question, population, and comparator are the right
  ones is not a machine decision.
- **Interpretation and discussion.** What the pooled estimate *means* for practice.
- **Final adjudication of any refusal.** A declared-absent trial or a mixed-scale label is a flag for a
  human to resolve, not a conclusion.

## The research agenda this sets

The reframe — *auditable draft + tractable human checking* — makes the priorities obvious, and they are the
open items in `CODEX_QUEUE.md`:

- **Tighten the residual-error interval** (more sampling) until it is a usefully narrow bound, not a point.
- **Raise risk-of-bias coverage** from registry fields toward model-assisted RoB2 from methods text with a
  verbatim span per domain — the weakest measured dimension.
- **A screening gold set** with sensitivity/specificity/κ against human labels (a model second screener is a
  reproducibility check, not a gold standard).
- **An independent search seed set** to measure absolute recall rather than agreement with one comparator.
- **External human review** of a handful of pages — the one thing the project has never had.

The destination is not "the machine writes the meta-analysis." It is: **the machine writes the draft and
shows its work so completely that one human can check it in an afternoon** — which, for a task that today
takes a team a year and still ships unverifiable numbers, would change a great deal of work.
