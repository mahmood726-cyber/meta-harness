"""Every recorded model call's working directory carries the lane orientation file, and the record says so."""
from __future__ import annotations

import inspect

from reproducible_ai import model_call_live as live


def test_the_workdir_holds_only_the_schema_and_the_orientation(tmp_path):
    live.prepare_workdir(tmp_path, {"type": "object"})
    assert sorted(p.name for p in tmp_path.iterdir()) == ["LANE_CONTEXT.md", "schema.json"]
    text = (tmp_path / "LANE_CONTEXT.md").read_text(encoding="utf-8")
    assert "Nothing outside this" in text and "AGENTS.md" in text


def test_the_runner_prepares_its_workdir_and_records_the_digest():
    src = inspect.getsource(live)
    assert "prepare_workdir(work, schema)" in inspect.getsource(live.codex_runner)
    assert '"LANE_CONTEXT.md": LANE_CONTEXT_SHA256' in src
    assert '"--sandbox", "read-only"' in inspect.getsource(live.codex_runner)      # never wider than read-only
