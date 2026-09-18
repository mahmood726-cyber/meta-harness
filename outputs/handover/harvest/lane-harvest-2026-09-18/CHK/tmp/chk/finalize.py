from pathlib import Path
import json

root = Path(__file__).resolve().parents[2]
log = (root / '.tmp/chk/verify_all.txt').read_text(encoding='utf-8')
lines = log.splitlines()
ledger = next(s for s in lines if s.startswith('CHECK_RECEIPTS '))
receipts = json.loads(ledger.removeprefix('CHECK_RECEIPTS '))
verdict = [s for s in lines if s.startswith('VERIFY-ALL:')][-1]
completed = sum(r['state'] == 'COMPLETED' for r in receipts)
report = root / 'LANE-CHK-REPORT.md'
text = report.read_text(encoding='utf-8').replace('Full verification is still running; no PASS is claimed.', '')
text += f'\n## Full verification: MEASURED\n\n{verdict}\n\n{completed} of {len(receipts)} limbs COMPLETED. Full output: [.tmp/chk/verify_all.txt](.tmp/chk/verify_all.txt).\n\nLimb receipts pasted verbatim:\n\n```text\n{ledger}\n```\n'
if completed != len(receipts):
    bad = [r for r in receipts if r['state'] != 'COMPLETED']
    text += '\nFull verification is not a PASS. The refusals above are retained; no limb was bypassed. See [STUCK_FAILURES.md](STUCK_FAILURES.md).\n'
    findings = '# CHK full-verifier refusals\n\nNo release claim. Lane-specific tests pass; full verifier refuses.\n\n'
    for r in bad:
        findings += '## ' + r['check_id'] + '\n\n```text\n' + r['reason'] + '\n```\n\n'
    (root / 'STUCK_FAILURES.md').write_text(findings, encoding='utf-8')
report.write_text(text, encoding='utf-8')
progress = root / 'PROGRESS.md'
progress.write_text(progress.read_text(encoding='utf-8') + '\nFinal: report complete; ' + verdict + '. No commit.\n', encoding='utf-8')
print(verdict)
for r in receipts:
    print(r['check_id'], r['state'])
    if r['state'] != 'COMPLETED':
        print(r['reason'])
