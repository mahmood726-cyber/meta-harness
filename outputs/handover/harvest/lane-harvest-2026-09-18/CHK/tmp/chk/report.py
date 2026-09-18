from pathlib import Path
import json
import subprocess

root = Path(__file__).resolve().parents[2]
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
table = (root / '.tmp/chk/count-table.md').read_text(encoding='utf-8')
text = f'''# LANE CHK — counts from execution receipts

HEAD: `{head}`. No commit, reset, checkout, stash, push or deployment.
The F: index/workbook session context was accessed; neither was edited because this
lane does not change project/submission status. AUD2's report and relevant diffs
were read as design context; its measurements were not treated as this base's evidence.

## MEASURED: pre-fix and post-fix plants

The production tree was untouched when the four original plants ran. Evidence:
[prefix_pytest.txt](.tmp/chk/prefix_pytest.txt). The four assertions were retained
unchanged after implementation and re-read: passing them now is correction of
the demonstrated failures, not deletion or loosening of a plant.

| Plant | Before | After |
|---|---|---|
| IV-iron rendered count equals completed actual checker calls | FIRED: 4 reported / 0 calls | HELD: 4 / 4 |
| Renderer raises: count falls by one, failed: 1 visible | FIRED: stayed 1 rather than falling to 0 | HELD: 3 to 2; one failed receipt and exception text |
| GLP-1 k=8 given k=1-verbatim provenance | FIRED: accepted | HELD: rejected |
| Zero completed checks visibly failing | HELD | HELD |

Pre-fix: 3 of 4 plants fired, 1 of 4 held. Post-fix: 4 of 4 held.
Additional plants cover a checker exception, an inflated legacy count, limb
exceptions and unattended PLANNED limbs. The combined targeted command in
[postfix_pytest.txt](.tmp/chk/postfix_pytest.txt) passed **38 of 38 tests**.
The pre-existing contradiction integration test now expects two completed
surface checks and one FAILED receipt; its original contradiction count and
build-refusal assertions remain. Its output directory now uses pytest's temporary path.

## MEASURED: rebuilds and hashes

Both named topics were built first, then the remaining topics, with
`scripts.build_topic.main(slug, '2026-09-11')`, the same entry point as
`python scripts/build_topic.py <slug> --now 2026-09-11`.
All 32 of 32 cache files were checked before building; the runner blocked socket
connections and used committed caches. [Rebuild log](.tmp/chk/rebuild.txt).

All 32 of 32 HTML hashes moved; 0 of 32 review-core hashes moved.
The table's unit is a completed significance checker invocation on one surface,
so a primary outcome can contribute three receipts. Counts are no longer sums
of outcome and strand inventory. There are 79 completed significance receipts
across the 32 pages, with zero failed/planned receipts in these successful builds.
Zero-check pages retain their failing limitation state.

{table}

Exact old/new hashes are retained in [after.json](.tmp/chk/after.json), with the
pre-edit snapshot in [before.json](.tmp/chk/before.json).
`python scripts/retraction_survival.py 237e9094`: **32 of 32**, exit 0;
[log](.tmp/chk/retraction_survival.txt). Browser E2E
`python -m pytest -q tests/test_certificate_ui.py`: **1 of 1 passed**, exercising
certificate rendering/downloads on all 32 pages using the installed browser.
The existing browser test uses a loopback ephemeral port for lane isolation;
all nonlocal browser requests are aborted. `git diff --check`: PASS.

## Diff summary

- `harness/census.py`: receipt schema with PLANNED, ATTEMPTED, COMPLETED, FAILED,
  reason and canonical inputs digest; actual outcome-surface and strand checker
  calls; renderer/checker exceptions become FAILED and refuse builds; counts and
  checked surfaces derive from completed receipts. Determinism, reproduction,
  proposition and claimgraph records also carry receipts. k=1-verbatim requires k=1.
- `harness/page.py`: computes visible counts from receipts, ignores legacy
  scalar counts, shows failed/not-attempted tallies and retains zero-check warning.
- `scripts/verify_all.py`: plans every limb before execution, emits receipts,
  refuses every state other than COMPLETED; no limb implementation removed or weakened.
- `scripts/reproduce_review.py`: reconstructs the added proposition/claimgraph
  receipts so the existing replay path agrees with the build path. This small
  dependent change is necessary for receipt metadata outside the scientific core.
- Tests and 32 regenerated review bundles. No research inputs or estimates edited.

## Static versus dynamic disclosure

| Item | Kind | Meaning |
|---|---|---|
| State names / check IDs | Static | Execution contract |
| Counts / exceptions / digests | Dynamic | Executed checks and canonical input objects |
| Limb digest | Dynamic target descriptor + limb identity | Local execution context; not a cryptographic attestation of all dependency bytes |
| k=1 token constraint | Static validation | Single-study label cannot certify a multi-study outcome |
| 999 / injected exceptions | Synthetic tests only | Never emitted as scientific findings |
| Trial IDs, dates and statistics | Existing data | All 32 scientific core hashes unchanged |

## Boundaries: INFERRED / CLAIMED

MEASURED: the four plants, cached rebuilds, receipt counts, core/HTML hash comparisons
and retraction survival above. The unchanged core hashes support the inference
that this increment did not alter scientific IDs, dates or statistical outputs;
this is not a new independent bibliographic revalidation of every source.

CLAIMED scope is local execution accounting for these existing checks. A completed
receipt means the named check returned successfully with no detected contradiction,
not that all scientific claims are true. The significance scanner's existing
recognition limits remain. No independent execution attestation is established.
GRADE NOT_ASSESSABLE is a separate increment; certificate binding is a separate
increment. The existing certificate has no checks-passed numerical tally, and
was not expanded to bind these new receipts. This work does not establish complete
interval provenance from a label, exhaustive nested sensitivity checking, or
portfolio certification. No Overmind PASS, submission-ready or shipped claim.
'''
verify = root / '.tmp/chk/verify_all.txt'
if verify.exists():
    output = verify.read_text(encoding='utf-8')
    lines = output.splitlines()
    verdict = [s for s in lines if s.startswith('VERIFY-ALL:')][-1]
    receipts = next(s for s in lines if s.startswith('CHECK_RECEIPTS '))
    text += '\n## MEASURED: full verifier\n\n' + verdict + '\n\n[Full log](.tmp/chk/verify_all.txt). Limb receipts pasted verbatim:\n\n```text\n' + receipts + '\n```\n'
else:
    text += '\nFull verification is still running; no PASS is claimed.\n'
(root / 'LANE-CHK-REPORT.md').write_text(text, encoding='utf-8')
