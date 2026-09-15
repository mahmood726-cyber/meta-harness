from __future__ import annotations

import collections
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
R3_FILE = ROOT / "outputs" / "search_v2" / "candidates-2026-09-15r3-all.json"
COMPARE_FILE = ROOT / "lane_r4" / "07-r2-vs-r3.txt"
REGISTER_FILE = ROOT / "lane_r4" / "06-register-r3.txt"
RECALL_FILE = ROOT / "lane_r4" / "05-recall-r3.txt"
REPORT_FILE = ROOT / "LANE-R4-REPORT.md"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def measurement_recall() -> tuple[int, int, int, int]:
    text = read_text(COMPARE_FILE)
    match = re.search(r"benchmark positives found r2 (\d+) of (\d+) -> r3 (\d+) of (\d+)", text)
    if not match:
        raise RuntimeError("could not parse r2/r3 benchmark totals")
    r2_found, r2_total, r3_found, r3_total = map(int, match.groups())
    if r2_total != r3_total:
        raise RuntimeError("r2/r3 benchmark denominators differ")
    return r2_found, r2_total, r3_found, r3_total


def register_totals() -> tuple[int, int]:
    text = read_text(REGISTER_FILE)
    whole = re.search(r"whole engine .*?(\d+) of (\d+)", text)
    within = re.search(r"within kind .*?(\d+) of (\d+)", text)
    if not whole or not within:
        raise RuntimeError("could not parse register totals")
    within_found = int(within.group(1))
    whole_found = int(whole.group(1))
    return within_found, whole_found


def isrctn_state_counts(topics: dict[str, Any]) -> collections.Counter[str]:
    counts: collections.Counter[str] = collections.Counter()
    for topic in topics.values():
        source = next(
            (source for source in topic.get("sources") or [] if source.get("kind") == "ISRCTN_CONDITION_INTERVENTION"),
            None,
        )
        counts[str((source or {}).get("state") or "NOT_RUN")] += 1
    return counts


def run_error_names(topics: dict[str, Any]) -> list[str]:
    return [slug for slug, topic in topics.items() if topic.get("state") == "RAN_ERROR"]


def command_ledger() -> list[str]:
    return [
        "Get-Content -Raw -LiteralPath 'F:\\ProjectIndex\\INDEX.md'",
        "Get-Content -Raw -LiteralPath 'F:\\E156\\rewrite-workbook.txt'",
        "Get-Content -Raw -LiteralPath '.\\LANE_PROMPT.md'",
        "git status --short",
        "Get-Content -Raw -LiteralPath '.\\LANE-R4-REPORT.md'",
        "Get-Content -Raw -LiteralPath '.\\lane_r4\\01-integrate.txt'",
        "Get-Content -Raw -LiteralPath '.\\lane_r4\\02-driver.txt'",
        "python -c \"import shutil;print(shutil.disk_usage('C:/').free)\"",
        "python scripts/search_v2_run.py refresh --help",
        "Get-ChildItem -LiteralPath '.\\lane_r4'",
        "python - <<'PY' ... PY  # failed in PowerShell before any repo change",
        "python scripts/search_v2_run.py refresh --label r3 --topics all --scope all --registries ctgov,isrctn --tar-only --archive-root .tmp/arch-r3 > lane_r4/03-run-r3.stdout 2>&1",
        "write_stdin/poll session 9707 until process exit",
        "Get-Content -Tail 80/100/120 -LiteralPath '.\\lane_r4\\03-run-r3.stdout'  # repeated progress inspection",
        "python -c \"import json,os,collections; p='outputs/search_v2/candidates-2026-09-15r3-all.json'; ...\"  # repeated candidate-count inspection",
        "python -c \"import shutil;print(shutil.disk_usage('C:/').free)\"  # repeated disk-gate inspection",
        "python scripts/search_v2_run.py status --label r3 --scope all > lane_r4/04-status-r3.txt",
        "python scripts/measure_search_recall.py outputs/search_v2/candidates-2026-09-15r3-all.json --include-development > lane_r4/05-recall-r3.txt",
        "python scripts/measure_regression_corpus_recall_search_v2.py --snapshot 2026-09-15r3-search_v2 > lane_r4/06-register-r3.txt",
        "Get-Content -Raw -LiteralPath '.\\lane_r4\\04-status-r3.txt'",
        "Get-Content -Raw -LiteralPath '.\\lane_r4\\05-recall-r3.txt'",
        "Get-Content -Raw -LiteralPath '.\\lane_r4\\06-register-r3.txt'",
        "python -c \"import json,pprint; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ...\"",
        "rg \"def _|MEASUREMENT|TOTAL|found\" scripts/measure_search_recall.py",
        "Get-Content -TotalCount 220 -LiteralPath '.\\scripts\\measure_search_recall.py'",
        "python -c \"import json,pprint; d=json.load(open('outputs/search_v2/candidates-2026-09-15r2-all.json',encoding='utf-8')); ...\"",
        "python -c \"import json; d=json.load(open('registry/search_benchmark_split.json',encoding='utf-8')); ...\"",
        "Get-Content -LiteralPath '.\\scripts\\measure_search_recall.py' -TotalCount 340 | Select-Object -Skip 220",
        "python -c \"import json,pprint; d=json.load(open('registry/search_benchmark.json',encoding='utf-8')); ...\"",
        "python -c \"import json; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ... ISRCTN ...\"",
        "Get-ChildItem -Recurse -Filter 'retrieval_ledger.json' -Path '.\\cache\\balanced-crystalloids-vs-saline-mortality\\snapshots\\2026-09-15r3-search_v2' | Select-Object -First 5 -ExpandProperty FullName",
        "python -c \"import json; p='cache/balanced-crystalloids-vs-saline-mortality/snapshots/2026-09-15r3-search_v2/retrieval_ledger.json'; ...\"",
        "python -c \"import json; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); c=d['candidates']['balanced-crystalloids-vs-saline-mortality']; ...\"",
        "python -c \"import json,collections; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ...\"",
        "apply_patch Add File: lane_r4/compare_r2_r3.py",
        "python lane_r4/compare_r2_r3.py > lane_r4/07-r2-vs-r3.txt",
        "Get-Content -Raw -LiteralPath '.\\lane_r4\\07-r2-vs-r3.txt'",
        "python -c \"from pathlib import Path; ... lane_r4/03..07 file sizes ...\"",
        "python -c \"import json; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); print(len(d.get('topics',{}))); ...\"",
        "python -c \"import json; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ... ISRCTN state counts ...\"",
        "Select-String -Path '.\\lane_r4\\05-recall-r3.txt' -Pattern '^TOTAL: found'",
        "Select-String -Path '.\\lane_r4\\06-register-r3.txt' -Pattern 'within kind|whole engine'",
        "Select-String -Path '.\\lane_r4\\03-run-r3.stdout' -Pattern 'RUN r3 scope=all|done .*: RAN|refresh ' | Select-Object -Last 10",
        "apply_patch Add File: lane_r4/make_r4_report.py",
        "python lane_r4/make_r4_report.py  # first attempt failed before report write due UTF-16 redirected input",
        "python -c \"import re; from pathlib import Path; text=Path('lane_r4/07-r2-vs-r3.txt').read_text(encoding='utf-8'); ...\"  # confirmed UTF-16 decode issue",
        "Format-Hex -Path '.\\lane_r4\\04-status-r3.txt' -Count 8  # failed: this PowerShell lacks -Count",
        "Format-Hex -Path '.\\lane_r4\\05-recall-r3.txt' -Count 8  # failed: this PowerShell lacks -Count",
        "Format-Hex -Path '.\\lane_r4\\06-register-r3.txt' -Count 8  # failed: this PowerShell lacks -Count",
        "Format-Hex -Path '.\\lane_r4\\07-r2-vs-r3.txt' -Count 8  # failed: this PowerShell lacks -Count",
        "python -c \"from pathlib import Path; ... read first bytes of lane_r4/03..07 ...\"",
        "python -c \"from pathlib import Path; ... detect UTF-16LE BOM in lane_r4/04..07 ...\"",
        "python -c \"from pathlib import Path; ... rewrite lane_r4/03..07 from utf-16 to utf-8 ...\"",
        "apply_patch Update File: lane_r4/make_r4_report.py",
        "python lane_r4/make_r4_report.py",
        "Get-Content -TotalCount 1 -LiteralPath '.\\LANE-R4-REPORT.md'",
        "python -c \"from pathlib import Path; ... verify LANE-R4-REPORT.md and lane_r4/03..07 existence, size, first bytes ...\"",
        "python -c \"import json,collections; d=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json',encoding='utf-8')); ... verify topics/candidates ...\"",
        "git status --short",
        "apply_patch Update File: lane_r4/make_r4_report.py",
        "python lane_r4/make_r4_report.py",
    ]


def main() -> int:
    data = load_json(R3_FILE)
    topics = data.get("topics") or {}
    topic_states = collections.Counter(str(topic.get("state") or "NOT_RUN") for topic in topics.values())
    topic_count = len(topics)
    not_run = max(0, 32 - topic_count)
    errors = run_error_names(topics)
    error_label = ", ".join(errors) if errors else "none"
    isrctn_counts = isrctn_state_counts(topics)
    r2_found, total, r3_found, _ = measurement_recall()
    register_within_found, register_whole_found = register_totals()

    first_line = (
        f"R4 VERDICT: RUN r3 COMPLETE {topic_count} of 32 topics ran "
        f"(states: RAN_OK {topic_states.get('RAN_OK', 0)}; "
        f"RAN_OK_WITH_SOURCE_ERRORS {topic_states.get('RAN_OK_WITH_SOURCE_ERRORS', 0)}; "
        f"RAN_ZERO {topic_states.get('RAN_ZERO', 0)}; "
        f"RAN_ERROR {topic_states.get('RAN_ERROR', 0)} ({error_label}); "
        f"NOT_RUN {not_run}); "
        f"ISRCTN source RAN_OK on {isrctn_counts.get('RAN_OK', 0)} of 32, "
        f"RAN_ZERO on {isrctn_counts.get('RAN_ZERO', 0)} of 32, "
        f"RAN_ERROR on {isrctn_counts.get('RAN_ERROR', 0)} of 32; "
        f"benchmark positives r2 {r2_found} of {total} -> r3 {r3_found} of {total}; "
        f"register within kind {register_within_found} of 20, whole engine {register_whole_found} of 20"
    )

    lines: list[str] = [first_line, ""]
    lines += [
        "## Notes",
        "- No commit was made.",
        "- The r3 refresh log completed with `RUN r3 scope=all: states={'RAN_OK_WITH_SOURCE_ERRORS': 32} NOT_RUN=0 of 32`.",
        "- The candidate JSON top-level `stop_reason` still contains the previous low-disk stop message, but `updated_utc`, topic rows, status output, and run log reflect the completed continuation run.",
        "- `lane_r4/05-recall-r3.txt` includes both sections: MEASUREMENT `136 of 147`; DEVELOPMENT fit statistic `122 of 131`.",
        "- Register tool raw within-kind line is `15 of 16 over 4 of 5 topics; not scored: ['statins-primary-prevention-elderly']`; the verdict line uses the requested denominator of 20.",
        "",
        "## Disk Gate",
        "- Before r3 start: 8483598336 bytes free.",
        "- After topic 8: 7574974464 bytes free.",
        "- After topic 16: 6745915392 bytes free.",
        "- During topic 21: 6201765888 bytes free.",
        "- After topic 24: 5943767040 bytes free.",
        "- During topic 28: 5141327872 bytes free.",
        "- After r3 completion: 4789813248 bytes free.",
        "",
        "## Required Artefacts",
    ]
    for rel in [
        "lane_r4/03-run-r3.stdout",
        "lane_r4/04-status-r3.txt",
        "lane_r4/05-recall-r3.txt",
        "lane_r4/06-register-r3.txt",
        "lane_r4/07-r2-vs-r3.txt",
        "outputs/search_v2/candidates-2026-09-15r3-all.json",
    ]:
        path = ROOT / rel
        lines.append(f"- `{rel}`: exists {path.exists()} size {path.stat().st_size if path.exists() else 0} bytes")

    lines += ["", "## Tar-Only Ledger", "| Topic | Asset | Bytes | SHA256 |", "|---|---|---:|---|"]
    for slug, topic in topics.items():
        archive = topic.get("raw_archive") or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    slug,
                    str(archive.get("asset") or ""),
                    str(archive.get("tar_bytes") or 0),
                    str(archive.get("tar_sha256") or ""),
                ]
            )
            + " |"
        )

    lines += ["", "## ISRCTN Source States"]
    for slug, topic in topics.items():
        source = next(
            (source for source in topic.get("sources") or [] if source.get("kind") == "ISRCTN_CONDITION_INTERVENTION"),
            None,
        )
        if source:
            lines.append(f"- {slug}: {source.get('state')} records {source.get('record_count', 0)}")
        else:
            lines.append(f"- {slug}: NOT_RUN records 0")

    lines += ["", "## Command Ledger"]
    for command in command_ledger():
        lines.append(f"- `{command}`")

    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(first_line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
