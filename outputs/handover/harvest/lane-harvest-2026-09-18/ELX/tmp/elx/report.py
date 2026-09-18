import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness.honest_ratchet import blocks

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

pages = read('.tmp/elx/page_diffs.json')
review = read('docs/reviews/glp1-ra-mace-t2d/review.json')
outcome = next(o for o in review['outcomes'] if o.get('primary'))
demo = outcome['known_missing_sensitivity']['membership_demonstration']
lines = ['# LANE ELX report', '',
         'MEASURED base HEAD: `'+subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()+'`.',
         'No commit, reset, checkout, stash, push, or network retrieval performed. This is a local increment, not a release or certification.', '',
         'MEASURED: 3 of 3 original plants failed before copying inputs or changing implementation. The held-source plant identified ELIXA and FREEDOM-CVO. Contrary to the lane description, the baseline manifest did not yet list FLOW; its PDF was committed, but its trial association arrived with the incoming manifest. After repair, 5 of 5 plants pass, including two added state/admission checks. Original assertions were retained; exact page assertions were added. Evidence: `.tmp/elx/prefix_pytest.txt`, `.tmp/elx/postfix_pytest.txt`.', '',
         'MEASURED: 32 of 32 pages rebuilt using the existing build function with date 2026-09-11; all caches preflighted and the fetch runner replaced with a refusal during the corpus rebuild. GLP1 was also rebuilt with the requested CLI. Retraction survival: 32 of 32. Targeted suite: 181 passed, 798 deselected on the final targeted run; full verifier results below. `git diff --check`: PASS.', '',
         '| Item | Static input/constant | Dynamic computation/validation |',
         '|---|---|---|',
         '| State vocabulary | Named codes and display labels | State from held document, extraction, conflict and proposal records |',
         '| Regulatory evidence | Two copied handover JSON inputs, unchanged | HEAD PDF bytes and working bytes hashed; text digest checked; eight ELIXA spans located at recorded offsets |',
         '| Membership demonstration | Proposed extraction from ADJ-GLP1-005 | Production synth.pool on original rows and original rows plus proposed ELIXA; no typed research output |',
         '| Report audit | Base revision | Field-by-field JSON comparison, manifest hashes, marker inventory |', '',
         'MEASURED source custody: 3 of 4 document digests verified against `git show HEAD:<path>` binary output (Python hashlib, avoiding shell pipeline encoding). The fourth is explicitly off-tree, has no committed path, and is REFUSED as held evidence; no numeric fact is consumed from it. Zero digest mismatches among the three committed documents. The copied manifest is retained verbatim, including that off-tree disclosure.', '',
         '```json', json.dumps(read('.tmp/elx/digests.json'),indent=2), '```', '',
         '| Trial | Before | After | Deriving evidence |', '|---|---|---|---|']
for row in outcome['known_missing_sensitivity']['rows']:
    f=row['held_fact']; a=f['adjudication']
    lines.append(f"| {f['trial']} | NOT_IN_COMMITTED_SOURCE | {row['value_status']} | `{f['document_path']}`; `{f['document_sha256']}`; {len(f['spans'])} displayed spans; {a['id']} PROPOSED, not countersigned |")
lines += ['', 'ELIXA: all eight supplied spans are preserved verbatim (including line breaks) and shown with PDF page numbers: definition/text/Table 8 page 24; executive summary page 7; Table 6 page 22; 4-point text page 35; unrounded 4-point text page 8. Endpoint identity uses the 3-component definition, not the interval fingerprint. Raw text digests are checked before universal-newline normalization used by the handover character offsets.', '',
          'FLOW: Table 10 is verbatim-located on PDF page 25; reported counts 212/1767 versus 254/1766 are displayed. ADJ-GLP1-003 remains PROPOSED. FREEDOM-CVO: the held FDA briefing supports an extraction record, not an absence-of-source state. Its older pipe-separated table span is displayed explicitly as a transcription, not falsely marked verbatim-located. No proposed row is admitted to the primary pool.', '',
          'MEASURED primary result object: unchanged in full, including k=8 and estimate 0.856. The manuscript tab text is unchanged from base. No demonstration numeral was added to the headline paragraph. Demonstration numbers live in the audit panel.', '',
          '| Production pooling metric | Primary | Primary + proposed ELIXA |', '|---|---:|---:|']
for key in ('k','estimate','ci_low','ci_high','tau2','Q','i2','pi_low','pi_high'):
    lines.append(f"| {key} | {demo['primary'][key]} | {demo['proposed'][key]} |")
lines += ['', 'DEMONSTRATION: HETEROGENEITY_MEMBERSHIP_SENSITIVE, under the PROPOSED adjudication—not a result. Paule-Mandel tau², HKSJ t with k-1 df, log scale, same production function as primary. I² is percent. INFERRED from these computations: the near-zero primary heterogeneity is membership-sensitive and the proposed prediction interval crosses the null.', '',
          'Implementation ownership: existing invalidation.py owns state codes/reasons; claimgraph.py now owns regulatory_fact and digest/span validation; page.py renders evidence and demonstration; synth.py computes both demonstration pools. This base has no harness/envelope.py and had no regulatory_fact function. Existing known_missing.py already assembles this panel, so it was extended as the actual owner; no new production module/framework was added.', '',
          'MEASURED page movement: 1 of 32 canonical review_sha256 values changed (GLP1); 32 of 32 html_sha256 values changed. In the other 31 review files, exactly three field values changed, all under reproduction/certificate: synth.py blob hash, analysis_code_sha256, release_sha256. Their clinical/review cores are unchanged; rendered certificate hashes explain their HTML changes. Dictionary key-order-only changes in serialized JSON do not alter canonical review hashes. Full before/after field diffs follow. GLP1 additionally changes held evidence, missing states, dependent limitation/gate text and its audit panel; the primary pool and manuscript are unchanged. The index reflects revised invalidation reason counts; the GLP1 neutral page reflects the audit panel; blind_map.json points to the last GLP1 CLI build.', '',
          '| Page | review_sha256 before → after | html_sha256 before → after |', '|---|---|---|']
for p in pages:
    r=p['hashes']['review_sha256']; h=p['hashes']['html_sha256']
    lines.append(f"| {p['slug']} | `{r[0]}` → `{r[1]}` | `{h[0]}` → `{h[1]}` |")
lines += ['', 'MEASURED ratchet: zero marker-count decreases across the 32 review pages. No marker-count acknowledgement is proposed. Three exact-text warning-block replacements require unsigned acknowledgements. They retain STALE and replace the false missing-source explanation with held extraction/adjudication debt (index aggregates these reasons). These are proposals only; docs/ratchet_acknowledgements.json was not changed.', '']
for rel in ('docs/index.html','docs/reviews/glp1-ra-mace-t2d/index.html'):
    before=blocks(subprocess.check_output(['git','show','237e9094:'+rel],cwd=ROOT).decode('utf-8'))
    after=blocks((ROOT/rel).read_text(encoding='utf-8'))
    shas={b['sha256'] for b in after}
    for b in before:
        if b['sha256'] in shas:
            continue
        if not (b['text'].startswith('STALE') or b['text'].startswith('Corpus currency')):
            continue
        replacements=[x['sha256'] for x in after if x['cls']==b['cls'] and x['text'].startswith(b['text'].split(' — ')[0][:20])]
        lines.append(f"- PROPOSED/UNSIGNED `{rel}`, {b['cls']} `{b['sha256']}` → `{', '.join(replacements)}`. Reason: held-source state correction; completeness remains stale, no primary numerical change.")
historical = '74ef9f624c5845659feef24079fb873482531098515959d4a9a1c20473b27570'
current_stale = next(b['sha256'] for b in blocks((ROOT/'docs/reviews/glp1-ra-mace-t2d/index.html').read_text(encoding='utf-8')) if b['text'].startswith('STALE'))
lines.append(f'- PROPOSED/UNSIGNED `docs/reviews/glp1-ra-mace-t2d/index.html`, historical-floor absent `{historical}` → `{current_stale}`. Reason: the prior acknowledgement points to an obsolete replacement; the current warning preserves STALE and the search failure, while replacing missing-source wording with held extraction/adjudication debt. This historical floor is checked in addition to base 237e9094.')
lines += ['', 'CLAIMED by handover, not established here: Mahmood acceptance/countersignature; prospective exact-outcome provenance resolution; admission to a conventional strand. This increment does NOT establish countersignatures, FACT binding of the eight pooled rows, CENTRAL search coverage, source completeness, or a release/Overmind PASS. Off-tree medical-review custody and FREEDOM transcription verification remain limitations.', '',
          'Full verifier ledger:', '```text']
verify=ROOT/'.tmp/elx/verify_all.txt'
lines += [verify.read_text(encoding='utf-8',errors='replace') if verify.exists() else 'RUNNING — report will be refreshed before completion.', '```', '',
          'Full-field diffs for every non-GLP1 review object (JSON values, not line diffs):', '```json',
          json.dumps([{ 'slug':p['slug'], 'changes':p['review_fields_changed']} for p in pages if p['slug']!='glp1-ra-mace-t2d'],indent=2), '```', '']
(ROOT/'LANE-ELX-REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
print('Wrote LANE-ELX-REPORT.md')
