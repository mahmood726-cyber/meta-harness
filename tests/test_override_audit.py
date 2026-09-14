import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "evidence" / "override-audit-2026-09-14" / "overrides.json"


def _override_rows_in_cache():
    rows = []
    for path in sorted((ROOT / "cache").glob("*/verified_effects.json")) + sorted((ROOT / "cache").glob("*/verified_arms.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for trial, entry in data.items():
            if isinstance(entry, dict) and entry.get("override") is True:
                rows.append({
                    "topic": path.parent.name,
                    "file": path.name,
                    "trial": str(trial),
                    "outcome": entry.get("outcome", ""),
                })
    return rows


def _key(row):
    return (row["topic"], row["file"], str(row["trial"]), row.get("outcome", ""))


def test_override_audit_covers_every_committed_override():
    audited = json.loads(AUDIT.read_text(encoding="utf-8"))
    audited_by_key = {_key(row): row for row in audited}
    required = {_key(row) for row in _override_rows_in_cache()}

    missing = sorted(required - set(audited_by_key))
    extra = sorted(set(audited_by_key) - required)
    assert not missing, "override(s) missing from audit: " + repr(missing)
    assert not extra, "audit row(s) without matching committed override: " + repr(extra)

    empty = [key for key in required if not str(audited_by_key[key].get("judgement", "")).strip()]
    assert not empty, "audited override(s) lack judgement: " + repr(sorted(empty))
