# Topic 12 audit: melatonin for sleep-onset latency

Audit date: 9 October 2026. Repository: `mahmood726-cyber/meta-harness`.
Pinned reference: `0730234d0b4f`.
Review identity declared in the pinned certificate and page:
`17d2b1984f234c37805170333b7ed3b86fb98f19fd0129276877657d0dd71bd8`.

## Verdict
The displayed unadjusted three-week subgroup calculation is numerically correct.
Do not sign off the broader review: screening paths disagree, a paediatric trial
is included in the adult eligible-family count, and analysis-population metadata
and manuscript scope are inconsistent.

## What was executed
Run `python checks.py` with Python 3.10 or later. No third-party packages are needed.
This regenerates `results.json` and asserts:
- MD and normal-theory 95% CI agree with the displayed rounded values.
- The exact extraction-passage string hashes to the supplied digest.
- An isolated transcription of the pinned contrast fallback labels the recorded
  `placebo Circadin; Circadin` intervention pair background-only, while the
  otherwise comparable `placebo; Circadin` pair is not so labelled.
- A transcribed caller falls through to this erroneous fallback when its
  structural-check dependency returns False.

The last two are **isolated excerpt tests**, not execution of the complete original
module or production build. The file contains explicit fixture adapters for ASCII
case folding, NCT identifier resolution and a False structural result. No claim
is made about untested Unicode normalization, cache acquisition or other inputs.

## Pinned source provenance
All paths below are relative to the repository at the pinned reference.
- `harness/screen.py`: Git blob `87fb6fdbdd1263c4457e5397aad4c3f13a7df6b0`.
  Relevant functions: `_record_arm_interventions_background_only` and
  `_background_only_randomised_contrast` (read in original lines 380-530).
- `harness/armcontrast.py`: Git blob `1430e6b1e9e1cde37b5175b24f308d99110070e4`.
  Relevant regex: `_PLACEBO`; the main normalizer uses search, whereas the
  record-list fallback uses fullmatch.
- `topics/melatonin-primary-insomnia-sol.json`: Git blob
  `3478847b5253450e3b4e5578298b55862fcad2a3`.
- `protocols/melatonin-primary-insomnia-sol.md`: Git blob
  `39741f48c7275e19a9c496edcf0909def23af523`.
- `docs/reviews/melatonin-primary-insomnia-sol/index.html`: Git blob
  `c2ff91a31ee6a26b1ace042ac0a66a6b9aab01aa`.
- Certificate Git blob: `5054960b09687be6efc8bfca41cbaab1b2b4016d`.
These are GitHub-returned object identifiers, not independently recomputed hashes
of complete local source files. Source bodies/excerpts were read via the connected
GitHub service. The complete repository was not downloaded or executed.

## Primary sources examined
1. Wade et al. 2010, PMID 20712869, original article PDF:
   https://eprints.gla.ac.uk/53469/1/53469.pdf
   Table 3, printed article page 9 (zero-indexed PDF page 9), was visually checked.
   Its 65-80-year subgroup row supplies the means, SDs and participant counts.
   The adjusted effect is a different estimand from the reconstructed raw MD.
2. MYNAP protocol, PMID 27473269:
   https://pmc.ncbi.nlm.nih.gov/articles/PMC4966772/
   The Study participants section specifies ages 6-17 and ADHD.
3. Screening samples independently supported from PubMed primary records:
   https://pubmed.ncbi.nlm.nih.gov/22616853/
   https://pubmed.ncbi.nlm.nih.gov/40418260/
   https://pubmed.ncbi.nlm.nih.gov/42453571/
   https://pubmed.ncbi.nlm.nih.gov/15766306/

The current ClinicalTrials.gov response bodies for NCT00816673 and NCT05454683
were not successfully obtained. The NCT00816673 contradiction is demonstrated
against the pinned page's own trial-family and record-level displays and its code.
NCT05454683 is not marked independently source-verified.

## Recommended regression obligations
A correction must recognize drug-matched placebo without erasing genuine active
background therapy in combination arms. Do not mechanically drop every string
containing 'placebo'. A confirmed structured randomized contrast must not be
silently overridden by a weaker list-of-interventions heuristic.

Test both `placebo Circadin` versus `Circadin` and a genuine background-drug
combination trial with placebo for the add-on. Separately test adult age eligibility
against the MYNAP source and first-randomization versus extension-phase analysis
population scoping. These are requirements, not tests claimed to have been run here.

## Limits
- Review/core, complete HTML and release hashes were NOT independently recomputed.
- The pinned page/certificate identity agreement was checked, not full replay.
- The live-page retrieval exposed another identity; cached retrieval cannot prove
  the current deployment differs. Findings are pinned-version findings.
- Four of the five requested screening samples were externally verified; the
  fifth remains an external-source verification limitation.
- All 126 screening records were not independently re-adjudicated.
- No corrected full trial census, pooled adult effect or class-level safety result
  is supplied. No repository or website was modified.
