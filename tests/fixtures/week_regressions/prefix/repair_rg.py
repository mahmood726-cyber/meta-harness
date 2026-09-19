from pathlib import Path
import subprocess

ROOT = Path.cwd()
OUT = ROOT / '.tmp/prefix'
paths = ['scripts/search_v2_run.py', 'scripts/measure_search_v2_measurement.py', 'scripts/search_v2_run_evidence.py', 'harness/gate_scorecard.py']
for rel in paths:
    p = OUT / 'base' / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(subprocess.check_output(['git', 'show', 'HEAD:' + rel]))
r = subprocess.run(['python', '-X', 'utf8', '-m', 'pytest', 'tests/test_week_regressions_dates.py', 'tests/test_week_regressions_scorecard.py', '-q', '-p', 'no:cacheprovider'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(OUT / 'dates-scorecard-before.txt').write_bytes(r.stdout)

def edit(rel, transform):
    p = ROOT / rel
    s = p.read_text(encoding='utf-8')
    p.write_text(transform(s), encoding='utf-8', newline=chr(10))

def live(s):
    s = s.replace('RUN_DATE = "2026-09-15"', 'FIRST_RUN_DATE = "2026-09-15"')
    start = s.index('def _snapshot_name(')
    end = s.index('def _previous_row(', start)
    s = s[:start] + '''def _dated_label(label: str) -> str:
    if len(label) > 10:
        try:
            datetime.date.fromisoformat(label[:10])
            return label
        except ValueError:
            pass
    return FIRST_RUN_DATE + label


def _snapshot_name(label: str) -> str:
    return f"{_dated_label(label)}-{search_v2.SNAPSHOT_SUFFIX}"


def _candidate_path(label: str, scope: str) -> str:
    return os.path.join(ROOT, "outputs", "search_v2", f"candidates-{_dated_label(label)}-{scope}.json")


''' + s[end:]
    s = s.replace('    tar_only: bool = False,\n) -> int:\n    split = _split()', '''    tar_only: bool = False,
    run_date: str | None = None,
) -> int:
    today = datetime.datetime.now(datetime.UTC).date().isoformat()
    if run_date != today:
        raise SystemExit(f"REFUSED: --run-date must equal today's UTC date {today}")
    dated = _dated_label(label)
    if dated != FIRST_RUN_DATE + label and dated[:10] != run_date:
        raise SystemExit("REFUSED: date-prefixed label disagrees with UTC run date")
    label = label if dated != FIRST_RUN_DATE + label else run_date + label
    split = _split()''')
    start = s.index('def refresh(')
    end = s.index('def status(', start)
    body = s[start:end].replace('"snapshot_date": RUN_DATE', '"snapshot_date": run_date').replace('{RUN_DATE}{label}', '{label}').replace('RUN_DATE + label', 'label').replace('slug, RUN_DATE,', 'slug, run_date,')
    # Keep historical-label recognition comparisons intact.
    body = body.replace('FIRST_label', 'FIRST_RUN_DATE + label')
    s = s[:start] + body + s[end:]
    s = s.replace('r.add_argument("--label", required=True)', 'r.add_argument("--label", required=True)\n    r.add_argument("--run-date", required=True, help="must equal today in UTC")')
    return s.replace('            tar_only=args.tar_only,', '            tar_only=args.tar_only,\n            run_date=args.run_date,')

edit(paths[0], live)
edit(paths[1], lambda s: s.replace('RUN_DATE', 'FIRST_RUN_DATE').replace('def refresh_measurement() -> int:\n', '''def refresh_measurement() -> int:
    if dt.datetime.now(dt.timezone.utc).date().isoformat() != FIRST_RUN_DATE:
        raise SystemExit("REFUSED: sealed first-run measurement may only run on " + FIRST_RUN_DATE)
'''))
def evidence(s):
    s = s.replace('RUN_DATE = m1.RUN_DATE', 'RUN_DATE = m1.FIRST_RUN_DATE\nfrom scripts.search_v2_run import _dated_label')
    s = s.replace('{RUN_DATE}{label}', '{_dated_label(label)}')
    return s
edit(paths[2], evidence)
