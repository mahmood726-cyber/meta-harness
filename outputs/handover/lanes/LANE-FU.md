# LANE FU — funding recovery: the funding sentence is in the held abstract on trials the page renders as "not stated"; four confirmed failures, sweep the corpus.

Report file: `LANE-FU-REPORT.md`. Base `ad5e7c66`. Lane EX (running concurrently) covers extractor completeness broadly and names funding; you own the funding instrument end-to-end: `harness/funding.py`, its plants, its sweep, and the render. Keep it additive; name the field `funding = {status, sponsor_class, sponsors[], role[], basis_span, source_id}`.

## Confirmed failures (CLAIMED until you locate the spans in cache)
1. spironolactone-hfref-mortality: J-EMPHASIS (PMID 28824029) rendered "not stated / abstract only"; the publication states Pfizer sponsored, designed and performed the study, collected and analysed the data, wrote the first draft, with Pfizer-employee authors. EMPHASIS-HF is Pfizer-funded. So 2 of 3 known industry, not 1 known / 2 unknown. If the Pfizer statement is not in the cached abstract, the correct state is `FUNDING_IN_SOURCE_NOT_HELD(full text)`, and the render must not say "not stated".
2. esketamine-trd-madrs: 4 of 4 trials Janssen-funded (topic 7 audit) while the page renders funding unknown for some.
3. noac-vs-warfarin-af-stroke: RE-LY funded by a Boehringer Ingelheim grant (stated in the NEJM abstract's closing sentence) — rendered unknown.
4. One further instance from topics 1–12 named in the integrator's `FOLLOWUPS.md` if present in your clone root; otherwise find it by the sweep and say the fourth was found by instrument, not by brief.
Also: NEJM/JAMA/Lancet abstracts carry "(Funded by X; ClinicalTrials.gov number, NCTxxxx.)" — a regular, parseable sentence. CT.gov records carry `sponsor` and `collaborators` and `responsible_party` (see `harness/aact.py`, cached registry records) — a second source; when abstract and registry disagree, render both with spans.

## Build
1. `harness/funding.py`: parse the funding sentence (abstract; full text where held), map to `sponsor_class ∈ {industry, public, mixed, none_stated_in_held_text, in_source_not_held}` with the exact span; registry sponsor as second source; roles (design/analysis/writing) when stated. Never infer industry from author affiliations alone — that is a flag `industry_authors_present`, not a sponsor.
2. Plants (pre-fix `ad5e7c66`): `tests/test_funding.py` — J-EMPHASIS "not stated" pre-fix (quote) → Pfizer post-fix if the span is held, else `in_source_not_held`; RE-LY BI grant from the abstract sentence; a synthetic abstract with no funding sentence → `none_stated_in_held_text` (not "no funding"); registry-vs-abstract disagreement rendered as both.
3. Sweep `scripts/funding_sweep.py` → `docs/funding_sweep.json`: over every pooled trial on 32 pages, `n trials rendered funding-unknown while a funding sentence exists in a held source of N pooled trials`, named; sponsor-class distribution per page; `n pages whose "k of N industry-funded" sentence changes of 32`.
4. Rebuild affected pages; replay; list reworded blocks.

Do not touch: pooling, membership, screening, search, RoB. No network.

## Added 2026-09-16 13:58 (topic 17)
- semaglutide-obesity-weight: STEP 3 is Novo Nordisk-funded with sponsor involvement in design, analysis and manuscript → 2 of 2 known industry, not 1 known / 1 unknown. Fifth confirmed instance. Locate the span; else `in_source_not_held`.
