from __future__ import annotations

import shutil
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from harness import architecture_identity


ROOT = Path(__file__).resolve().parents[1]


def _copy_identity_tree(dst: Path) -> Path:
    for rel in (
        "harness",
        "scripts",
        ".github",
        ".githooks",
        "topics",
        "protocols",
        "registry",
    ):
        src = ROOT / rel
        if src.exists():
            shutil.copytree(src, dst / rel)
    shutil.copy2(ROOT / "requirements.txt", dst / "requirements.txt")
    (dst / "docs").mkdir()
    shutil.copy2(
        ROOT / "docs" / "model_stage_inventory.json",
        dst / "docs" / "model_stage_inventory.json",
    )
    return dst


def _identity_receipt(root=ROOT):
    original = architecture_identity.components
    captured = []
    def capture(*args, **kwargs):
        inputs = original(*args, **kwargs)
        captured.append(inputs)
        return inputs
    with patch.object(architecture_identity, 'components', side_effect=capture):
        digest = architecture_identity.identity(root)
    assert len(captured) == 1, 'identity() must use one captured component map'
    return {'inputs': captured[0], 'digest': digest}


def _assert_identity_pair(first, second, *, equal, case):
    diagnostic = json.dumps({'case': case, 'first': first, 'second': second}, indent=2, sort_keys=True)
    matches = (first['digest'] == second['digest']) == equal
    if not matches:
        # Persist before asserting: a later per-file timeout must not swallow
        # the identity inputs that caused this failure. Test helper only.
        path = ROOT / '.tmp' / 'integrate4' / 'architecture-identity-failure.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(diagnostic, encoding='utf-8')
    assert matches, diagnostic


def test_identity_is_deterministic() -> None:
    _assert_identity_pair(_identity_receipt(), _identity_receipt(), equal=True, case='determinism')


def test_topic_config_byte_change_changes_identity(tmp_path: Path) -> None:
    clone = _copy_identity_tree(tmp_path / "clone")
    baseline = _identity_receipt(clone)
    topic = next((clone / "topics").glob("*.json"))
    topic.write_text(topic.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    _assert_identity_pair(baseline, _identity_receipt(clone), equal=False, case='topic-byte-change')


def test_cli_check_wrong_value_exits_one() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "harness.architecture_identity",
            "--check",
            "not-the-identity",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert "architecture identity mismatch" in proc.stderr


def test_mutable_dependencies_names_requirements_txt() -> None:
    mutable = architecture_identity.mutable_dependencies(ROOT)
    assert mutable
    assert any(item.startswith("requirements.txt:") for item in mutable)
