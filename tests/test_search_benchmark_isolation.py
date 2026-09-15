from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

QUERY_BUILDER_NEEDLES = ("concept_query", "search_v2", "query_builder")
FORBIDDEN_TARGETS = (
    "registry/search_benchmark.json",
    "docs/known_eligible_missing.json",
    "docs/never_considered.json",
    "docs/evidence/probiotics-search-diagnostic-2026-09-15",
    "registry/heldout_sealed.json",
    # bare basenames: os.path.join(ROOT, "registry", "search_benchmark.json") names the target without the slash form
    # (2026-09-15: a collision check inside the v2 engine did exactly that and this detector did not fire)
    "search_benchmark.json",
    "known_eligible_missing.json",
    "never_considered.json",
    "heldout_sealed.json",
)


def _posix(path: Path) -> str:
    return str(path).replace("\\", "/")


def _query_builder_modules(harness_dir: Path) -> list[Path]:
    modules = []
    for path in sorted(harness_dir.glob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(needle in text for needle in QUERY_BUILDER_NEEDLES):
            modules.append(path)
    return modules


def _isolation_violations(harness_dir: Path) -> list[str]:
    violations = []
    for path in _query_builder_modules(harness_dir):
        text = path.read_text(encoding="utf-8", errors="replace").replace("\\", "/")
        for target in FORBIDDEN_TARGETS:
            if target in text:
                violations.append(f"{_posix(path)} opens or names isolated target {target}")
    return violations


def test_query_builders_do_not_read_search_benchmark_targets() -> None:
    violations = _isolation_violations(ROOT / "harness")

    assert violations == []


def test_isolation_plant_catches_temp_query_builder_open(tmp_path: Path) -> None:
    harness_dir = tmp_path / "harness"
    harness_dir.mkdir()
    (harness_dir / "query_builder_plant.py").write_text(
        "def concept_query(config):\n"
        "    return open('registry/search_benchmark.json', encoding='utf-8').read()\n",
        encoding="utf-8",
        newline="\n",
    )

    violations = _isolation_violations(harness_dir)

    assert violations[0] == (
        f"{_posix(harness_dir / 'query_builder_plant.py')} opens or names isolated target registry/search_benchmark.json"
    )
    assert violations[1:] == [
        f"{_posix(harness_dir / 'query_builder_plant.py')} opens or names isolated target search_benchmark.json"
    ]


def test_isolation_plant_catches_os_path_join_form(tmp_path: Path) -> None:
    """The form that slipped past the slash-only needles on 2026-09-15: a v2-engine module built the target path
    with os.path.join, so no 'registry/search_benchmark.json' substring existed. The bare basename must fire."""
    harness_dir = tmp_path / "harness"
    harness_dir.mkdir()
    (harness_dir / "search_v2_plant.py").write_text(
        "import os\n"
        "# search_v2 collision check (the real one lived in the engine module for one uncommitted hour)\n"
        "def benchmark_acronyms(root):\n"
        "    return open(os.path.join(root, 'registry', 'search_benchmark.json'), encoding='utf-8').read()\n",
        encoding="utf-8",
        newline="\n",
    )

    violations = _isolation_violations(harness_dir)

    assert violations == [
        f"{_posix(harness_dir / 'search_v2_plant.py')} opens or names isolated target search_benchmark.json"
    ]
