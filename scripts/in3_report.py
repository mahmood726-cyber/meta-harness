"""Write the required lane artifact from measured verification output."""
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/handover/in3'

def main():
    raw=(OUT/'verify_all.txt').read_text(encoding='utf-8')
    table=[line.strip() for line in raw.splitlines() if re.match(r'\s+\[',line)]
    assert len(table)==11,table
    ds=json.loads((OUT/'decisions.json').read_text(encoding='utf-8'))
    counts=Counter(d['entry']['kind'] for d in ds)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,encoding='utf-8').strip()
    n=len(list((ROOT/'docs/reviews').glob('*/review.json')))
    lines=['# LANE IN3 report','',f'Base and final HEAD: `{head}`. No commit. No network. No push or deployment.',
        'Build date: `2026-09-11`, as instructed. Local work and checks: `2026-09-17`.',
        '', '## Measured standard results','', '| Limb | Verdict |','|---|---|']
    for row in table:
        m=re.match(r'\[\s*(.*?)\]\s*(.*?)\s+\(\d+s\)$',row)
        assert m,row
        lines.append(f'| {m[2]} | {m[1]} |')
    lines+=['',f'Denominator: {n} live `docs/reviews/*/review.json` pages, and 11 standard limbs.',
            '', 'Retraction-survival output:', '', '```text',
            (OUT/'retraction_survival.txt').read_text(encoding='utf-8').strip(),'```',
            '', '## Source repairs','',
            f'{len(ds)} of {len(ds)} explicit trial–outcome decisions validated against held sources: '
            f"{counts['extracted_counts']} count inputs, {counts['extracted_effect']} effect-plus-CI inputs, and {counts['typed_refusal']} typed refusals (including spurious signals).",
            'The denominator is adjudicated trial–outcome pairs, not unique trials or an estimate of all harms in the literature. All four formerly empty harm registries now contain the reported endpoint families. A typed refusal establishes an extraction disposition, never harm non-reporting.',
            'Raw local AACT candidate rows, their exact-NCT identities and byte hashes are retained in `outputs/handover/in3/aact/`. The snapshot-folder date is provenance, not a claim of trial data currency. No overlapping preferred-term event counts were summed.',
            'PRESERVED-HF adverse-event numerators come from its held abstract; the arm denominators are from the same NCT in the retained AACT safety totals, independently corroborated by the abstract percentages. SGLT2 harm populations explicitly denote trial-wide cohorts, not primary-prevention-only subgroups.',
            'Source-backed HRs and RRs are not mixed. An incompatible reported RR remains a cited typed refusal under a registered HR harm endpoint. The legacy override path now preserves an explicitly supplied abstract provenance instead of relabeling it full-text.',
            '', '## Harness and test decisions','',
            '- Scope identity: render the shared qualification in the common scope block, including refused-pool branches. No slug exception and no gate change.',
            '- Manuscript numerals: permit the values actually present in per-trial follow-up and endpoint-definition objects; synthetic changed-value checks prove there is no 14/30 whitelist.',
            '- Harm completeness: the compatibility consumer recognizes canonical typed refusals only after validating their held-source reference and span. The unchanged publication gate still refuses unresolved harms.',
            '- `test_real_review_harms_incomplete_refuses_full_gate`: replaced the assertion that a repaired real page must fail with an explicit synthetic HARMS_INCOMPLETE plant.',
            '- `test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews`: requirement retained. A successful eligibility-chain explanation is a note, while actual violations retain the absent/limitation block.',
            '- `test_manuscript_limb_passes_on_every_live_review`: requirement retained; fixed object-number provenance.',
            '- `test_colchicine_or_is_non_target_alternative_under_rr_outcome`: retained the OR-versus-RR source-hierarchy assertions; updated old exclusion expectations to the existing retrospective compatibility-axis admission and strict sensitivity.',
            '- `test_retained_aact_rows_match_audit_hashes`: raw-byte hash requirement retained. All six old digests matched the LF files converted to CRLF. Regenerated manifest digests for repository-required LF bytes; retained source rows unchanged.',
            '- `test_committed_integrity_is_fresh_for_every_live_topic`: checks current served membership against the immutable cached checks. Missing PMIDs now render NOT_ASSESSED (offline lane), count as unchecked, and never acquire a fabricated clean/retracted verdict. No integrity network refresh was run.',
            '', '## Census limitation and offline handling','',
            'The existing `scripts/error_rate_compare.py` and `scripts/error_rate_pass2.py` were run; both require historical `scratchpad/errorrate/frame.json`, which is absent in this checkout. Their actual failures are retained in the command logs. Search found no checked-in generator for the served sample.',
            'Added and ran `scripts/refresh_error_rate_census.py` to regenerate current row coverage from live objects. It preserves the original independent audit, dates and numerator, explicitly marks added rows NOT_INDEPENDENTLY_RECHECKED, accounts for removed rows, and labels the index error rate HISTORICAL_ONLY. This is a measured current inventory, not a new blind extraction-error measurement. The original blind census could not be rerun from missing source artifacts offline.',
            '', '## Static versus dynamic disclosure','',
            '| Component | Kind | Evidence / transformation |','|---|---|---|',
            '| Harm endpoint definitions and refusal judgments | Static, reviewed | Held abstracts and exact-NCT local AACT rows |',
            '| Transcribed values | Static source transcription | Verbatim spans, registry denominator citations and percentage checks |',
            '| Follow-up and endpoint numerals | Dynamic | Per-trial admission object fields |',
            '| Offline integrity coverage | Dynamic | Current pooled IDs minus held checked IDs; no invented checks |',
            '| Census inventory | Dynamic | Current pooled rows; independent-audit status explicitly separate |',
            '| Synthetic regression fixtures | Static test-only | Never used as research evidence |',
            '| Page counts, synthesis, gates and survival | Dynamic | Rebuild and standard command outputs |',
            '', 'MEASURED: held-source spans and identifiers, transcriptions, invariant checks, build exits, browser contracts and standard results. INFERRED: endpoint/population compatibility and typed refusal judgments, documented per item. CLAIMED: no new blind error-rate measurement, complete literature coverage, or release certification.',
            '', 'The second-pass artifact records unchanged screening records and primary numeric inputs against the lane base. `harness/gate.py`, `harness/synth.py`, search and screening code were not edited.',
            '', '## Pre-existing source-level discrepancy requiring follow-up','',
            'MEASURED: `dapagliflozin-hfpef-hosp` names the primary outcome as the composite cardiovascular-death/worsening-HF endpoint, but its selected PMID 36027570 source explicitly says cardiovascular death alone (HR 0.88). The held abstract reports composite HR 0.82. The same selected component source is present at the lane base and is unchanged here. Evidence: `outputs/handover/in3/preexisting_endpoint_discrepancy.json`, which retains both base/current source strings and the held abstract. This bounded integration repair does not establish the clinical validity of that pre-existing primary selector; it needs a separate endpoint-selection correction. Passing the standard must not be presented as clinical certification.',
            '', '## Full standard output, including the complete honest-ratchet refusal','',
            '```text',raw.rstrip(),'```','',
            'The ratchet is not acknowledged or bypassed here; the integrator owns acknowledgements. Any other refusal remains a blocker, with its verbatim output above.',
            '', 'Artifacts: `outputs/handover/in3/build_all.txt`, `build_provenance.txt`, `decisions.json`, `second_pass.json`, `command_exits.json`, renderer logs, `verify_all.txt`, and retained `aact/` source rows.']
    (ROOT/'LANE-IN3-REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    print('Wrote LANE-IN3-REPORT.md')

if __name__=='__main__':
    main()
