"""Prospective output packages are immutable run-specific directories.

These offline filesystem tests exercise runner preflight only. They do not
establish discovery, raw API custody, model immutability or external validation.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from harness import prospective
from scripts import run_prospective_topic as runner


@pytest.mark.parametrize(
    "old_artifact",
    [
        "run_record.json",
        "failure.json",
        "review/review.json",
        "unrecognised-evidence.dat",
    ],
)
def test_run_refuses_reused_package_without_modifying_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, old_artifact: str
) -> None:
    package = tmp_path / "prior-run"
    evidence = package / old_artifact
    evidence.parent.mkdir(parents=True, exist_ok=True)
    original = b"preserve prior outcome exactly\n"
    evidence.write_bytes(original)

    config = tmp_path / "topic-config.json"
    config.write_text('{"slug":"synthetic-topic"}\n', encoding="utf-8")
    monkeypatch.setattr(
        runner.prospective, "load_declaration", lambda *_args: {"synthetic": True}
    )
    monkeypatch.setattr(
        runner.prospective, "check_declaration_frozen", lambda *_args: None
    )
    monkeypatch.setattr(
        runner.acquisition,
        "refresh",
        lambda *_args, **_kwargs: pytest.fail("must refuse before acquisition"),
    )

    with pytest.raises(prospective.ProspectiveRefusal, match="out_dir already exists"):
        runner.run_topic("synthetic-batch", str(config), str(package))

    assert evidence.read_bytes() == original
    assert not (package / "topic-config.json").exists()
    assert sorted(path.relative_to(package).as_posix() for path in package.rglob("*")) == (
        [old_artifact] if "/" not in old_artifact else [
            old_artifact.split("/")[0],
            old_artifact,
        ]
    )


def test_empty_preexisting_package_is_also_refused(tmp_path: Path) -> None:
    package = tmp_path / "previously-claimed"
    package.mkdir()

    with pytest.raises(prospective.ProspectiveRefusal, match="out_dir already exists"):
        runner._claim_fresh_out_dir(package)
    assert list(package.iterdir()) == []


def test_claim_creates_new_package_once(tmp_path: Path) -> None:
    package = tmp_path / "new-parent" / "fresh-run"
    runner._claim_fresh_out_dir(package)
    assert package.is_dir()
    with pytest.raises(prospective.ProspectiveRefusal, match="out_dir already exists"):
        runner._claim_fresh_out_dir(package)


def test_symlink_to_prior_package_is_refused(tmp_path: Path) -> None:
    previous = tmp_path / "previous-run"
    previous.mkdir()
    previous_file = previous / "run_record.json"
    previous_file.write_bytes(b"old evidence")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(previous, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink not available on this test filesystem: {exc}")

    with pytest.raises(prospective.ProspectiveRefusal, match="out_dir already exists"):
        runner._claim_fresh_out_dir(alias)
    assert previous_file.read_bytes() == b"old evidence"
