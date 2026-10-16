"""Source selection contracts using synthetic fixtures, never production outputs."""
import json

import pytest

from scripts import grade_formal_build as builder


LABELS = ("served contextual (A3)", "contextual (A3)", "v3.1 (current replay)")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    tiers = [(label, tmp_path / f"tier-{i}") for i, label in enumerate(LABELS)]
    monkeypatch.setattr(builder, "ROOT", str(tmp_path))
    monkeypatch.setattr(builder, "OUT", str(tmp_path / "grade"))
    monkeypatch.setattr(builder, "TIERS", tiers, raising=False)
    return tmp_path, tiers


def test_priority_and_missing_trial(sandbox):
    _, tiers = sandbox
    trial_sets = [{"4": "LOW"}, {"4": "HIGH", "3": "LOW"},
                  {"3": "HIGH", "2": "LOW", "1": "LOW"}]
    for (_, directory), trials in zip(tiers, trial_sets):
        write_json(directory / "synthetic.json", {
            "outcome": "primary", "trials": {
                pmid: {"trial": f"PMID {pmid}", "outcome": "primary", "overall": {"judgement": judgement}}
                for pmid, judgement in trials.items()
            },
        })
    rob, sources = builder.rob_for("synthetic", "primary", [f"PMID {i}" for i in range(1, 6)])
    assert rob == {f"PMID {i}": {"trial": f"PMID {i}", "outcome": "primary",
                               "overall": {"judgement": "LOW"}} for i in range(1, 5)}
    assert sources == {"PMID 4": LABELS[0], "PMID 3": LABELS[1],
                       "PMID 2": LABELS[2], "PMID 1": LABELS[2]}
    assert "PMID 5" not in rob and "PMID 5" not in sources


@pytest.mark.parametrize("wrong_outcome", ["secondary", None])
def test_file_outcome_mismatch_covers_nothing(sandbox, wrong_outcome):
    _, tiers = sandbox
    wrong = {"outcome": "primary", "overall": {"judgement": "HIGH"}}
    right = {"trial": "PMID 1", "outcome": "primary", "overall": {"judgement": "LOW"}}
    write_json(tiers[0][1] / "synthetic.json", {
        "outcome": wrong_outcome, "trials": {"1": wrong, "2": wrong},
    })
    write_json(tiers[2][1] / "synthetic.json", {
        "outcome": "primary", "trials": {"1": right},
    })
    assert builder.rob_for("synthetic", "primary", [f"PMID {i}" for i in range(1, 6)]) == (
        {"PMID 1": right}, {"PMID 1": LABELS[2]},
    )


def test_missing_files_cover_nothing(sandbox):
    assert builder.rob_for("missing", "primary", ["PMID 1"]) == ({}, {})


@pytest.mark.parametrize("field", ("trial", "outcome"))
@pytest.mark.parametrize("fallback", (False, True))
def test_object_requires_own_identity(sandbox, field, fallback):
    _, tiers = sandbox
    right = {"trial": "PMID 1", "outcome": "primary", "overall": {"judgement": "LOW"}}
    wrong = {k: v for k, v in right.items() if k != field}
    write_json(tiers[0][1] / "synthetic.json", {"outcome": "primary", "trials": {"1": wrong}})
    if fallback:
        write_json(tiers[2][1] / "synthetic.json", {"outcome": "primary", "trials": {"1": right}})
    assert builder.rob_for("synthetic", "primary", ("PMID 1",)) == (
        ({"PMID 1": right}, {"PMID 1": LABELS[2]}) if fallback else ({}, {}))


@pytest.mark.parametrize("object_outcome", ["secondary", None])
def test_object_outcome_mismatch_uses_lower_tier(sandbox, object_outcome):
    _, tiers = sandbox
    wrong = {"trial": "PMID 1", "outcome": object_outcome, "overall": {"judgement": "LOW"}}
    right = {"trial": "PMID 1", "outcome": "primary", "overall": {"judgement": "HIGH"}}
    for index, obj in [(0, wrong), (2, right)]:
        write_json(tiers[index][1] / "synthetic.json", {
            "outcome": "primary", "trials": {"1": obj},
        })
    assert builder.rob_for("synthetic", "primary", [f"PMID {i}" for i in range(1, 6)]) == (
        {"PMID 1": right}, {"PMID 1": LABELS[2]},
    )


@pytest.mark.parametrize("fallback", [False, True])
def test_object_trial_mismatch_is_rejected(sandbox, fallback):
    _, tiers = sandbox
    wrong = {"trial": "PMID 2", "outcome": "primary", "overall": {"judgement": "LOW"}}
    right = {"trial": "PMID 1", "outcome": "primary", "overall": {"judgement": "HIGH"}}
    write_json(tiers[0][1] / "synthetic.json", {
        "outcome": "primary", "trials": {"1": wrong},
    })
    if fallback:
        write_json(tiers[2][1] / "synthetic.json", {
            "outcome": "primary", "trials": {"1": right},
        })
    assert builder.rob_for("synthetic", "primary", [f"PMID {i}" for i in range(1, 6)]) == (
        ({"PMID 1": right}, {"PMID 1": LABELS[2]}) if fallback else ({}, {})
    )


def test_only_pooled_trials_have_objects_and_sources(sandbox):
    _, tiers = sandbox
    obj = {"trial": "PMID 1", "outcome": "primary", "overall": {"judgement": "LOW"}}
    write_json(tiers[0][1] / "synthetic.json", {
        "outcome": "primary", "trials": {"1": obj, "2": obj},
    })
    assert builder.rob_for("synthetic", "primary", ["PMID 1"]) == (
        {"PMID 1": obj}, {"PMID 1": LABELS[0]},
    )
    assert builder.rob_for("synthetic", "primary", []) == ({}, {})


def test_production_tier_order():
    from pathlib import Path

    base = Path(builder.ROOT) / "outputs" / "robgrade"
    assert [(label, Path(directory)) for label, directory in builder.TIERS] == [
        ("served contextual (A3)", base / "served" / "rob2_ctx"),
        ("contextual (A3)", base / "rob2_ctx"),
        ("v3.1 (current replay)", base / "rob2_current"),
    ]


def test_build_records_sorted_sources_and_missing_assessment(sandbox):
    root, tiers = sandbox
    primary = {
        "name": "primary", "primary": True,
        "result": {"k": 3, "scale": "RR", "tau2": 0},
        "trials": [{"id": f"PMID {i}", "effect": 0.8,
                    "study_effect": {"standard_error": 0.1}} for i in range(1, 4)],
    }
    write_json(root / "docs/reviews/synthetic/review.json", {
        "outcomes": [{"name": "secondary"}, primary],
    })
    write_json(tiers[0][1] / "synthetic.json", {
        "outcome": "primary", "trials": {
            "2": {"trial": "PMID 2", "outcome": "primary", "overall": {"judgement": "LOW"}},
            "99": {"trial": "PMID 99", "outcome": "primary", "overall": {"judgement": "LOW"}},
        },
    })
    write_json(tiers[1][1] / "synthetic.json", {
        "outcome": "primary", "trials": {"1": {
            "trial": "PMID 1", "outcome": "primary", "overall": {"judgement": "HIGH"}}},
    })
    result = builder.build("synthetic")
    written = json.loads((root / "grade/synthetic.json").read_text(encoding="utf-8"))
    assert result == written
    assert result["rob_sources"] == {"PMID 1": LABELS[1], "PMID 2": LABELS[0]}
    assert list(result["rob_sources"]) == list(written["rob_sources"]) == ["PMID 1", "PMID 2"]
    inputs = written["domains"]["risk_of_bias"]["inputs"]
    assert inputs["no_formal_assessment"] == ["PMID 3"]
    assert inputs["per_trial"]["PMID 1"]["overall"] == "HIGH"
    assert inputs["per_trial"]["PMID 2"]["overall"] == "LOW"


@pytest.mark.parametrize("argv, expected", [([], ["alpha", "zeta"]), (["zeta"], ["zeta"])])
def test_main_topic_selection(sandbox, monkeypatch, capsys, argv, expected):
    root, _ = sandbox
    for slug in ("zeta", "alpha"):
        write_json(root / "docs/reviews" / slug / "review.json", {})
    (root / "docs/reviews/no-review").mkdir()
    calls = []

    def fake_build(slug):
        calls.append(slug)
        return {"certainty": "provisional", "certainty_from_assessed_domains_only": "high",
                "domains": {}, "served_partial_grade": {"certainty": None}}

    monkeypatch.setattr(builder, "build", fake_build)
    builder.main(argv)
    assert calls == expected
    assert capsys.readouterr().out.splitlines() == [
        f"{slug} certainty provisional (assessed domains only: high ) {{}} served: None"
        for slug in expected
    ]


def test_production_never_reads_frozen_objects(tmp_path, monkeypatch):
    from pathlib import Path
    import builtins

    root = Path(builder.ROOT)
    tiers = [(label, tmp_path / Path(directory).relative_to(root))
             for label, directory in builder.TIERS]
    monkeypatch.setattr(builder, "TIERS", tiers)
    frozen = tmp_path / "outputs/robgrade/rob2"
    for directory in (frozen, frozen / "dev"):
        write_json(directory / "synthetic.json", {
            "outcome": "primary", "trials": {"1": {"overall": {"judgement": "LOW"}}},
        })
    original = builtins.open

    def guarded_open(path, *args, **kwargs):
        assert not Path(path).is_relative_to(frozen), "GRADE read a frozen object"
        return original(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded_open)
    assert builder.rob_for("synthetic", "primary", ["PMID 1"]) == ({}, {})


@pytest.mark.parametrize("provenance, state", [("abstract", "ASSESSED"), ("UNTRACED", "PARTIAL")])
def test_build_wires_only_provenanced_counts(sandbox, provenance, state):
    root, _ = sandbox
    write_json(root / "docs/reviews/synthetic/review.json", {"outcomes": [{
        "primary": True, "name": "primary", "result": {"k": 1, "scale": "RR", "ci_low": 0.7, "ci_high": 0.9},
        "trials": [{"id": "synthetic", "ai": 15, "n1i": 100, "ci": 20, "n2i": 100,
                    "source": "synthetic extractor fixture", "provenance": provenance}]}]})
    d = builder.build("synthetic")["domains"]["imprecision"]
    assert d["state"] == state
    if state == "ASSESSED":
        assert d["inputs"]["ois"] == 1806 and d["inputs"]["total_n"] == 200


@pytest.mark.parametrize("record_state, held, changed, expected", [
    ("AGREES", True, False, "RECORDED_MODEL_CALL"),
    ("GATE_REFUSED", True, False, "HAND_ENTERED"),
    ("AGREES", False, False, "HAND_ENTERED"),
    ("AGREES", True, True, "HAND_ENTERED"),
])
def test_arm_counts_recorded_read_must_match_counts(sandbox, record_state, held, changed, expected):
    root, _ = sandbox
    rid = "mc-" + "a" * 32
    trial = {"id": "synthetic", "ai": 15, "n1i": 100, "ci": 20, "n2i": 100,
             "provenance": "aact_verified", "source": "synthetic held span"}
    snapshot = dict(trial, ai=14) if changed else trial
    write_json(root / "registry/provenance_recorded_reads.json", {"reads": {
        "synthetic|synthetic|primary": {"state": record_state, "record_id": rid, "served": snapshot}}})
    if held:
        write_json(root / "registry/model_calls" / (rid + ".json"), {"synthetic_fixture": True})
    outcome = {"name": "primary", "result": {"scale": "RR"}, "trials": [trial]}
    row = builder.arm_counts("synthetic", outcome)[0]
    assert row["provenance_class"] == expected
    assert row["events_t"] == 15


def test_arm_counts_does_not_read_secondary_sibling_or_source_prose(sandbox):
    root, _ = sandbox
    write_json(root / "cache/synthetic/verified_arms.json", {"synthetic": {
        "ai": 15, "ci": 20, "n1i": 100, "n2i": 100, "outcome": "secondary"}})
    outcome = {"name": "primary", "result": {"scale": "RR"}, "trials": [{
        "id": "synthetic", "source": "15/100 versus 20/100", "provenance": "abstract"}]}
    row = builder.arm_counts("synthetic", outcome)[0]
    assert row["events_t"] is None and row["n_t"] is None
