# How the harness works now — deterministic vs model (for Mahmood; read from the code at `768c98fb`, 2026-09-16)

**Size:** 63 modules, 26,035 lines in `harness/`. Every claim below is MEASURED in the code unless marked INFERRED.

## 1. Proportion: the build is deterministic end to end
- **Zero language-model API calls anywhere in `harness/` or `scripts/`** — no OpenAI/Anthropic client, no completions call, no codex subprocess inside the build (MEASURED by grep).
- Search: boolean queries to PubMed, ClinicalTrials.gov, Europe PMC, ISRCTN (`search_v2`, `acquisition`, `registry_first`, `fetch`).
- Screening: per-topic keyword lexicon (`population_any` / `population_none` / `intervention_any` / `comparator_any`) plus regexes for "randomised" and publication type (`screen.py::screen_record`).
- Extraction: regex over abstracts and structured CT.gov fields (`extract.py` holds 32 of the harness's 218 regex calls; `protocol_compiler` 16).
- Estimand classes, compatibility keys, RoB domains (registry fields), GRADE, invalidation/STALE, the claim graph, and every sentence rendered on a page: rule tables and templates (`estmeasure`, `compat*`, `rob2`, `grade`, `invalidation`, `claimgraph`, `page`, `limitations`). Pooling: arithmetic in `synth.py`.
- Consequence: a fresh clone replays every page from the committed cache with no model — that is why byte-reproduction is possible and why CI can refuse a page.

## 2. Where a model is used today — three places; none supplies a number
| Site | What the model does | Checked afterwards by |
|---|---|---|
| Codex / Gemini as **developers and auditors**, outside the pipeline | wrote every fix today in isolated clones; cross-family panels compare our numbers to theirs (`crossfamily_compare`, `fair_judge`) | integrator adjudication; the panel verdict is rendered as external agreement, never consumed by the build |
| **Outcome-identity judgments as a cached source** (`scripts/outcome_judgments.py` → `cache/<slug>/outcome_judgments.json`; gate in `ctgov_results.py`) | says whether a CT.gov outcome-measure *title* IS the review's outcome — five required fields (population, timepoint, definition, is_match, rationale) or the cache is refused; committed, so replay never re-calls | the counts still come from the structured arm table and must round-trip; the judgment only admits/refuses a title. **Live on 1 of 32 pages** (balanced-crystalloids). This is already the reproducible pattern. |
| **Pinned local embedding model** (`embed.py`, MiniLM-L6-v2, committed vectors) | synonym-robust candidate *ranking* (arm candidates, dual screen with a rule-based adjudicator, deficit scan) | docstring: "never the decider". **Exception: `rob2_build.py` uses it as the decider** — registry outcome ≡ review outcome when cosine ≥ 0.45, with no deterministic check after (MEASURED; INFERRED that some RoB/D5 joins rest on it). |
Recoveries fetched by a Codex lane (J-EMPHASIS) are recorded as `MODEL_CALL` provenance and their digits verified against the cached span — the model found the record; the parser checked the numbers.

## 3. Today's defects that originate in regex / string matching
Confirmed from your list: truncated-title exclusion (metformin 19552097); "myocardial revascularization" absent from the cardiac-surgery vocabulary (Zarpelon); `drug_present AND placebo_present` admitting MIRO-CKD and PYY1875 (`screen_record`); bare drug name with no dose (HISTORI); `population_none` diabetes keyword as a hard veto before entry-condition context (sglt2-hfref — the fix lane's sweep found a third flip, NCT04304560).
Added: RoB join by **label string** instead of trial identifier (the stale-RoB class, 5 pages); D5 rated by registered-primary **title** comparison (EXSCEL, EINSTEIN-DVT, CANVAS); the comparator-k parser reading a **nearby integer** (Zhang "3" for a table of 8); CT.gov outcome-measure **title substring** matching (the azithromycin ED-visit class); the published-HR **sentence pattern** missing DAPA-HF/EMPEROR "hazard ratio, 0.74; 95% CI", so a crude RR was reconstructed. INFERRED: RALES's Cox "relative risk" mapped to the RR class by label string.

## 4. Where the old rule was violated, both directions
- Model doing a parser's job: the embedding threshold deciding registry-outcome identity in `rob2_build` (outcome name and components are structured fields).
- Parser attempting judgement: randomised-contrast isolation, composite-endpoint identity, population axes at unstated thresholds (LVEF, severity, acuity, case confirmation), functional unblinding — all decided by keyword presence today.

## 5. Under the new decision (models anywhere, if reproducible)
The judgement tasks in §4 move to a single pinned, cached, span-verified model source (`REPRODUCIBLE_MODEL_CONTRACT.md`); identifiers, arithmetic, count reconciliation, round-trip checks, hashes and the claim graph stay deterministic. A model never supplies a number.
