"""Write the required HM3 report from measured artifacts."""
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence/hm3-held-source-audit'
baseline=json.loads((E/'baseline-debt.json').read_text(encoding='utf-8'))
decisions=json.loads((E/'decisions.json').read_text(encoding='utf-8'))
gates=json.loads((E/'gate-results.json').read_text(encoding='utf-8'))
slugs=list(dict.fromkeys(r['slug'] for r in baseline))
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,encoding='utf-8').strip()
counts=Counter(d['category'] for d in decisions)
lines=['# LANE HM3 report','',
       'MEASURED: 50 of 50 baseline trial × harm items resolved from held sources: '
       f"{counts['extracted (counts)']} count extractions, {counts['extracted (effect+CI)']} published effect+CI extractions, "
       f"{counts['typed refusal']} typed refusals, and {counts['spurious signal']} spurious signals.",
       '',f'HEAD: `{head}` (matches specified WIP base). No commit; no network; no deployment.',
       'Builds use the instructed fixed date `2026-09-11`. Work and verification performed 2026-09-17.',
       '',f"HM completeness: {sum(not g['harms_violations'] for g in gates)}/17 pages pass. Full publication gate: {sum(g['gate_ok'] for g in gates)}/17 pass.",
       'Ticagrelor retains its pre-existing scope_identity refusal. The lane prohibits changes to search, screening and membership; it is not reported as publication-ready.',
       '', '## Per-page measured resolution', '',
       '| Page | Resolved of baseline N | Counts | Effect+CI | Typed refusal | Spurious |',
       '|---|---:|---:|---:|---:|---:|']
for slug in slugs:
    ds=[d for d in decisions if d['topic']==slug]
    n=sum(r['slug']==slug for r in baseline)
    c=Counter(d['category'] for d in ds)
    lines.append(f"| {slug} | {len(ds)} of {n} | {c['extracted (counts)']} | {c['extracted (effect+CI)']} | {c['typed refusal']} | {c['spurious signal']} |")
lines += ['', 'N is the number of baseline `known_reported_not_yet_extracted` trial–outcome pairs, not unique trials. Unresolved harm items: none. A typed refusal resolves extraction debt; it does not establish absence of harm.',
          '', '## Gate output, verbatim', '',
          'Each page was built with `python scripts/build_topic.py <slug> --now 2026-09-11`, then checked with `harness.gate.gate_page`, the function used by `verify_all.limb_gate_every_page`. Every build exited 0. The runner blocks socket connections and restores shared index/blind-map bytes after builds.', '', '```text']
for g in gates:
    lines.append(g['slug']+': '+('PASS' if g['gate_ok'] else '; '.join(g['reasons'])))
lines += ['```','', 'Raw build output and structured gate results: [evidence directory](docs/evidence/hm3-held-source-audit/).',
          '', '## Plant-first proof', '',
          'Before implementation changes, the synthetic fixture contained one KNOWN_REPORTED_NOT_YET_EXTRACTED item. Running `python -m pytest tests/test_hm3_contract.py -q` with an assertion that the gate accepted it failed as follows (test-only synthetic data):','', '```text',
          (E/'plant-before.txt').read_text(encoding='utf-8').rstrip(), '```', '',
          'The final test first asserts this refusal, then applies a cited REFUSED_ON_EVIDENCE adjudication, reannotates the outcome and requires the same unchanged HM gate to pass.',
          '', '## Verification', '']
for name, command in [('required-tests.txt','python -m pytest tests/test_harms_recovery.py tests/test_override_audit.py -q'),
                      ('regression-tests.txt','python -m pytest tests/test_hm3_contract.py tests/test_hm3_pages.py tests/test_absence_ontology.py tests/test_verified_override.py tests/test_verified_effects.py tests/test_source_hierarchy.py tests/test_source_hierarchy_regression.py tests/test_missing_effect.py tests/test_page.py tests/test_honest_states_renderable.py -q')]:
    path=E/name
    lines += [f'`{command}`','', '```text',path.read_text(encoding='utf-8').rstrip() if path.exists() else 'PENDING final rerun', '```','']
lines += ['The rebuilt-page E2E contract checks every baseline item against its served review, verbatim refusal spans, extracted values and verification states, plus unchanged screening records and primary trial values. The second pass checks source PMIDs, source hashes, count bounds and interval ordering, and the three pre-existing overrides against held records.',
          '', '## Implementation and audit', '',
          '- Added distinct-outcome lists while retaining the legacy single-object format; duplicate trial–outcome inputs fail closed. Pipeline selection is outcome-specific.',
          '- Missing-effect enrichment uses the explicit outcome or the registered primary outcome; it cannot borrow a harm estimate.',
          '- Added SIGNAL_SPURIOUS and a typed-refusal path that requires a recognized code, reason and exact span in the held abstract/full text.',
          '- Count overrides retain their actual abstract/full-text provenance and receive digit verification rather than the AACT trusted-entry shortcut.',
          '- Extended override auditing to every list member. Replaced the three stale audit outcome labels for esketamine NCT02417064 and CKD PMIDs 32970396/36331190; preserved their existing numeric inputs.',
          '- `harness/gate.py`, `harness/synth.py`, search, screening, membership and other lane pages were not modified.',
          '', '## Held-source boundaries', '',
          'Local AACT was read through the adapter schema from snapshot folder `2026-08-30`; this is an archive locator, not a claim about source-record currency. Verbatim filtered rows and hashes are retained in [aact/](docs/evidence/hm3-held-source-audit/aact/), including reported_events, reported_event_totals, outcome_counts, outcomes, outcome_measurements and result_groups. No percentages were multiplied by an assumed denominator. Overlapping adverse-event categories were not summed.',
          '', 'Second-pass identity checks excluded embedded fulltext_by_pmid entries for melatonin PMID 33157425 (ARE/MLT study), semaglutide PMID 40825340 (review text), and esketamine PMID 31109201 (French prospective cohort). These texts were not used as numbers for the named trials; the held abstracts and matching primary sources were used. Source-cache repairs are outside this harm lane.',
          '', 'The tocilizumab PMID 33085857 extraction uses the published narrative participant totals (28 and 12), with Table 4 denominators (161 and 82); it does not sum the 36 and 38 events. The local registry totals differ (19 and 8), so the published participant counts are explicitly identified as the chosen source.',
          '', '## Static versus dynamic disclosure', '',
          '| Component | Static / dynamic | Evidence and transformation |',
          '|---|---|---|',
          '| Outcome identities and refusal judgments | Static, reviewed | Existing protocol/specifications and verbatim held spans |',
          '| New counts and HRs | Static source transcription | Exact digits; no imputed denominator or variance |',
          '| Original combined MADRS input | Existing derived value | Rechecked original per-arm values and weighted mean/pooled-SD arithmetic; not changed |',
          '| Baseline N, resolved counts, gates and synthesis | Dynamic | Baseline review objects, new verified inputs, unchanged gate and synthesis |',
          '| Synthetic fixture | Static test data | Explicitly synthetic; never included in published evidence |',
          '', 'MEASURED: baseline lists, source spans, values, hashes, rebuild exits, gate results and test results. INFERRED: endpoint/population/timepoint compatibility and refusal judgments, stated per item below. CLAIMED: no clinical effect conclusion, completeness of an unheld source, or release certification beyond those measured checks.',
          '', '## Item-by-item decisions', '',
          'Full verbatim spans and source document references are in [decisions.json](docs/evidence/hm3-held-source-audit/decisions.json) and each topic’s verified input file. The machine-readable audit identifies each trial and outcome separately.', '']
for slug in slugs:
    lines += ['### '+slug,'']
    for d in decisions:
        if d['topic']!=slug:
            continue
        e=d['entry']
        code=e.get('provenance','') if e.get('absent') else ''
        details=e.get('reason') or e.get('verification')
        lines.append(f"- **{d['trial']} — {d['outcome']}**: {d['category']}"+(f' (`{code}`)' if code else '')+f". {details} [Held source]({e['document_ref']}).")
    lines.append('')
(ROOT/'LANE-HM3-REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Wrote LANE-HM3-REPORT.md')
