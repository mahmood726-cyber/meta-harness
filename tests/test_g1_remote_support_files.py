"""Plant (7 Oct): every full-text swap-screen job sent to the worker was refused 'licence=NOT_HELD' -- the pre-call guard reads
the job's DECLARED comparator JATS (cache/comparators/<pmid>/..jats..xml, untracked) and submit() shipped only the index
files, so the worker never held the file whose <permissions> carry the CC licence. 48 refusals, 0 local: a harness
fault, not a licence verdict."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_remote_codex as rc  # noqa: E402


def test_a_declared_comparator_jats_is_shipped_with_its_job(tmp_path, monkeypatch):
    d = tmp_path / "cache" / "comparators" / "36312269"
    d.mkdir(parents=True)
    (d / "2026-10-06_kgap_jats.xml").write_text("<permissions>CC BY</permissions>", encoding="utf-8")
    monkeypatch.setattr(rc, "ROOT", str(tmp_path))
    jobs = [{"key": "a", "input_digests": [{"ref": "cache/comparators/36312269/2026-10-06_kgap_jats.xml", "sha256": "x"}]},
            {"key": "b", "input_digests": [{"ref": "rule registry/comparator_selection/x.rule.json"}]},
            {"key": "c", "input_digests": [{"ref": "cache/comparators/99999999/missing_jats.xml"}]}]
    assert rc.support_files(jobs) == ["cache/comparators/36312269/2026-10-06_kgap_jats.xml"]
