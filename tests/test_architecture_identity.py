from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

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


def test_identity_is_deterministic() -> None:
    assert architecture_identity.identity(ROOT) == architecture_identity.identity(ROOT)


def test_topic_config_byte_change_changes_identity(tmp_path: Path) -> None:
    clone = _copy_identity_tree(tmp_path / "clone")
    baseline = architecture_identity.identity(clone)
    topic = next((clone / "topics").glob("*.json"))
    topic.write_text(topic.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert architecture_identity.identity(clone) != baseline


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
