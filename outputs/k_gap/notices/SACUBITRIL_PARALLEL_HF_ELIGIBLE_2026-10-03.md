# Notice for Mahmood: the served sacubitril/valsartan review excludes PARALLEL-HF on its abstract alone

Lane G1 (g1/sglt2-primary-prevention-hf), 2026-10-03. **A notice only.** No served page or pool was changed (MAIN is
frozen), and nothing here is signed; a lane never signs for you.

**What.** PARALLEL-HF (Tsutsui 2021, Circ J 85:584-594, PMID 33731544, DOI 10.1253/circj.CJ-20-0854) is excluded by the
served screen under X-DESIGN ("not double-blind/placebo-controlled"). The abstract never mentions blinding. The open full
text (J-STAGE PDF via Unpaywall, CC BY-NC-ND, text sha256 fd798579...) states:
"the study was a multicenter, randomized, double-blind study to assess the effect of sacubitril/valsartan 200 mg twice
daily (bid) vs. enalapril 10 mg bid", with 225 patients randomized "during the double-blind treatment period".
The protocol asks for a double-blind active-controlled design against enalapril, ACEi, ARB or RAS inhibitor, so the
trial meets it.

**Classified (harness, deterministic):** outputs/k_gap/exclusion_fulltext.json, SCREENER_ERROR:ELIGIBLE_ON_FULL_TEXT,
using that full-text span. In G1 the trial stays an eligible open gap (1 / 2 matched). It can only be matched once the
served pool includes it.

**What a served change would do (not done):** include PARALLEL-HF in the primary pool. Its abstract reports the primary
composite of CV death and HF hospitalization as HR 1.09 (0.65-1.82). Served k would go from 1 to 2. This needs your
decision and re-certification, and it should also settle whether the served screen may read held full texts to decide
design.
