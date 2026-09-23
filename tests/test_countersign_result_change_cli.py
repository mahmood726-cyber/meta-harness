"""Signing plants use a fictional ledger, never a copy of the clinical ledger."""
import json
import builtins
from collections import defaultdict
from pathlib import Path

import pytest

from scripts import countersign_result_change as cli

ROOT = Path(__file__).resolve().parents[1]
REAL_LEDGER = ROOT / "docs" / "result_changes.json"
REAL_NOTICES = json.loads(REAL_LEDGER.read_text(encoding="utf-8"))["notices"]
_groups = defaultdict(list)
for _index, _row in enumerate(REAL_NOTICES):
    _groups[(_row["slug"], _row["outcome"])].append(_index)
DUPLICATES = [(key, indices) for key, indices in _groups.items() if len(indices) > 1]


@pytest.fixture
def synthetic_ledger(tmp_path, monkeypatch):
    notice = {
        "slug": "synthetic-example", "outcome": "Synthetic outcome",
        "before": {"k": 3, "estimate": 2, "ci_low": 1, "ci_high": 3},
        "after": {"k": 2, "estimate": 3, "ci_low": 2, "ci_high": 4},
        "left_pool": ["fictional-trial-a"], "entered_pool": [],
        "reason": "Synthetic CLI test; no research finding.",
        "by": "Test author", "when_utc": "2000-01-01T00:00:00Z",
    }
    path = tmp_path / "synthetic-ledger.json"
    path.write_text(json.dumps({"notices": [notice]}), encoding="utf-8")
    monkeypatch.setattr(cli, "PATH", path)
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    return path


def sign_args(*extra):
    return ["sign", "synthetic-example", "Synthetic outcome", "--by", "Test reviewer",
            "--basis", "Synthetic test input", "--when", "2000-01-02T00:00:00Z", *extra]


def test_mutation_between_render_and_sign_refuses_with_both_digests(synthetic_ledger, tmp_path, capsys):
    output = tmp_path / "notice.html"
    cli.main(["render", "synthetic-example", "Synthetic outcome", str(output)])
    old_sha = capsys.readouterr().out.strip().split()[-1]
    data = json.loads(synthetic_ledger.read_text(encoding="utf-8"))
    data["notices"][0]["reason"] += " Changed after rendering."
    synthetic_ledger.write_text(json.dumps(data), encoding="utf-8")
    unchanged = synthetic_ledger.read_bytes()
    new_sha = cli._block_and_sha(data["notices"][0])[2]
    assert old_sha != new_sha
    with pytest.raises(SystemExit) as error:
        cli.main(sign_args("--expect-digest", old_sha))
    assert old_sha in str(error.value) and new_sha in str(error.value)
    assert "nothing written" in str(error.value)
    assert synthetic_ledger.read_bytes() == unchanged


@pytest.mark.parametrize("use_digest", [True, False])
def test_matching_digest_and_legacy_default_proceed(synthetic_ledger, use_digest):
    notice = json.loads(synthetic_ledger.read_text(encoding="utf-8"))["notices"][0]
    sha = cli._block_and_sha(notice)[2]
    assert cli.main(sign_args(*(["--expect-digest", sha] if use_digest else []))) == 0
    signed = json.loads(synthetic_ledger.read_text(encoding="utf-8"))["notices"][0]
    assert signed["reviewer_countersignature"] == {
        "state": "SEEN_AND_SIGNED", "by": "Test reviewer", "when_utc": "2000-01-02T00:00:00Z",
        "rendered_sha256": sha, "how_it_reached_the_reviewer": "Synthetic test input",
    }


@pytest.mark.parametrize("pair,indices", DUPLICATES, ids=[key[0] + "/" + key[1] for key, _ in DUPLICATES])
def test_real_duplicate_pairs_refuse_legacy_and_select_each_exact_notice(pair, indices, tmp_path, monkeypatch):
    """Real sign calls stop at a deliberately wrong digest, before any write can occur."""
    initial = REAL_LEDGER.read_bytes()
    original_open = builtins.open

    def read_only_real_ledger(path, mode="r", *args, **kwargs):
        if Path(path).resolve() == REAL_LEDGER.resolve() and any(flag in mode for flag in "wax+"):
            pytest.fail("attempted write to real ledger")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", read_only_real_ledger)
    slug, outcome = pair
    out = tmp_path / "exact-notice.html"
    for argv in (["render", slug, outcome, str(out)],
                 ["sign", slug, outcome, "--by", "Test", "--basis", "Never written"]):
        with pytest.raises(SystemExit, match="2 notices match"):
            cli.main(argv)
    assert not out.exists()
    for index in indices:
        data, selected = cli._notice(slug, outcome, index)
        assert selected is data["notices"][index]
        assert selected == REAL_NOTICES[index]
        sha = cli._block_and_sha(selected)[2]
        cli.main(["render", slug, outcome, str(out), "--notice-index", str(index)])
        assert sha in out.read_text(encoding="utf-8")
        with pytest.raises(SystemExit) as error:
            cli.main(["sign", slug, outcome, "--notice-index", str(index), "--expect-digest", "not-a-digest",
                      "--by", "Test", "--basis", "Never written"])
        assert f"actual {sha}" in str(error.value)
    assert REAL_LEDGER.read_bytes() == initial


@pytest.mark.parametrize("index,slug,outcome", [(-1, "synthetic-example", "Synthetic outcome"),
                                              (1, "synthetic-example", "Synthetic outcome"),
                                              (0, "wrong-slug", "Synthetic outcome"),
                                              (0, "synthetic-example", "wrong outcome")])
def test_invalid_exact_selector_writes_nothing(synthetic_ledger, tmp_path, index, slug, outcome):
    initial = synthetic_ledger.read_bytes()
    out = tmp_path / "must-not-exist.html"
    for argv in (["render", slug, outcome, str(out)],
                 ["sign", slug, outcome, "--by", "Test", "--basis", "Test"]):
        with pytest.raises(SystemExit, match="refused: --notice-index"):
            cli.main([*argv, "--notice-index", str(index)])
    assert not out.exists()
    assert synthetic_ledger.read_bytes() == initial


def test_matching_exact_selector_signs_only_selected_synthetic_notice(synthetic_ledger):
    data = json.loads(synthetic_ledger.read_text(encoding="utf-8"))
    second = dict(data["notices"][0], when_utc="2000-01-02T00:00:00Z", reason="Second synthetic change.")
    data["notices"].append(second)
    synthetic_ledger.write_text(json.dumps(data), encoding="utf-8")
    sha = cli._block_and_sha(second)[2]
    cli.main(sign_args("--notice-index", "1", "--expect-digest", sha))
    signed = json.loads(synthetic_ledger.read_text(encoding="utf-8"))["notices"]
    assert signed[0] == data["notices"][0]
    assert signed[1]["reviewer_countersignature"]["rendered_sha256"] == sha
