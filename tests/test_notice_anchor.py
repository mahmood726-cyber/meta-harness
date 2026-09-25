"""Decision B: every notice anchor names the version judged; a detached anchor is a refusal; nothing re-points.

Plants mutate bytes in memory only; no clinical ledger or registry file is written by any test here.
"""
import builtins
import copy
import json
from pathlib import Path

import pytest

from scripts import countersign_result_change as cli
from scripts import notice_anchor as anchor
from scripts import notice_rejudge as rejudge
from scripts import sign_walk as walk

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def loaded():
    return walk.load_walk()


def _forbid_writes(monkeypatch):
    real_open = builtins.open

    def guarded(file, mode="r", *args, **kwargs):
        if any(c in mode for c in "wa+") and Path(file).resolve() in (cli.PATH.resolve(), rejudge.AUDIT.resolve()):
            raise AssertionError(f"test attempted to write {file}")
        return real_open(file, mode, *args, **kwargs)
    monkeypatch.setattr(builtins, "open", guarded)
    for name in ("write_text", "write_bytes"):
        monkeypatch.setattr(Path, name, lambda *a, **k: (_ for _ in ()).throw(AssertionError("Path write in a test")))


def _mutate_bytes(monkeypatch, target: Path, replacement: bytes = b"in-memory rebuilt page"):
    original = Path.read_bytes

    def read(path):
        return replacement if Path(path).resolve() == target.resolve() else original(path)
    monkeypatch.setattr(Path, "read_bytes", read)


# ------------------------------------------------------------------ the committed registry, as judged
def test_every_audited_notice_has_a_commit_pinned_judgement_whose_anchors_attach(loaded):
    audit = loaded[0]
    assert len(audit["notices"]) == 41  # denominator: the 41 OPEN notices audited at 9ff4c6b0
    for row in audit["notices"]:
        judgement = anchor.verify_row(ROOT, row)
        sides = [a["side"] for a in judgement["anchors"]]
        assert sides.count("served") == 2 and sides.count("proposed") == 2 and sides.count("record") == 1
        assert all(a["ref"].startswith("git:") for a in judgement["anchors"])
        assert judgement["bulk_verdict"] in rejudge.VERDICTS and judgement["lane_verdict"] in rejudge.VERDICTS
        assert (judgement["lane_verdict"] == "HOLDS_WITH_DEFECT") == bool(judgement["defects"])
        # every departing trial carries the constraint that actually failed admission (judgement B2 onward)
        assert sorted(b["trial_id"] for b in judgement["departure_binding"]) == sorted(row["left_pool"])
        assert all(b["bucket"] and b["class"] and b["basis"] for b in judgement["departure_binding"])
        assert all(v for k, v in judgement["mechanical_checks"].items()
                   if k not in ("direction_recomputed", "rendered_block_sha256"))
    assert all(ref.startswith("git:") for ref in audit["source_digests"])
    assert audit["source_digests"] == anchor.source_digest_map(audit)


def test_old_working_tree_digests_are_kept_as_history_not_as_anchors(loaded):
    audit = loaded[0]
    old = audit["superseded_anchors"]["source_digests"]
    assert len(old) == 78 and sum(not k.startswith("git:") for k in old) == 54
    assert not set(k for k in old if not k.startswith("git:")) & set(audit["source_digests"])


# ------------------------------------------------------------------ plants: each must refuse
def test_a_working_tree_anchor_refuses():
    with pytest.raises(anchor.AnchorRefused, match="working-tree anchor"):
        anchor.parse("docs/reviews/pcsk9-mace/index.html")


def _page(row):
    return ROOT / row["page_evidence"]["html_path"]


def test_a_rebuild_that_only_churns_the_page_no_longer_detaches_and_is_disclosed(loaded, monkeypatch, capsys):
    # The positive control Decision B exists for: a rebuild re-renders the page (here: extra bytes at the end), the
    # notice's block, result and membership are untouched -> the walk presents, and SAYS the page was rebuilt.
    row = next(r for r in loaded[0]["notices"] if r["audit_id"] == "N20")
    _mutate_bytes(monkeypatch, _page(row), _page(row).read_bytes() + b"<!-- rebuilt -->")
    assert walk.main(["--notice", "N20"]) == 0
    out = capsys.readouterr().out
    assert "Rebuilt since judgement (disclosed" in out and row["page_evidence"]["html_path"] in out
    assert "python scripts/countersign_result_change.py sign" in out


def test_a_rebuilt_page_without_the_judged_block_is_stale_and_refuses(loaded, monkeypatch, capsys):
    row = next(r for r in loaded[0]["notices"] if r["audit_id"] == "N20")
    _mutate_bytes(monkeypatch, _page(row), b"<html>rebuilt page carrying no notice block</html>")
    assert walk.main(["--notice", "N20"]) == 1
    err = capsys.readouterr()
    assert not err.out
    assert "STALE" in err.err and "no longer carries the rendered block" in err.err
    assert "no signing command offered" in err.err


def test_a_page_that_now_serves_a_different_after_is_stale_for_every_walk(loaded, monkeypatch, capsys):
    row = next(r for r in loaded[0]["notices"] if r["audit_id"] == "N28")
    review_path = ROOT / row["page_evidence"]["review_path"]
    review = json.loads(review_path.read_bytes())
    for outcome in review["outcomes"]:
        if outcome["name"] == row["outcome"]:
            outcome["result"]["estimate"] = 0.84  # one served number moves; nothing else does
    _mutate_bytes(monkeypatch, review_path, json.dumps(review).encode("utf-8"))
    assert walk.main(["--notice", "N01"]) == 1  # another notice: the walk as a whole refuses
    err = capsys.readouterr().err
    assert "STALE" in err and "N28" in err and "not the after the notice records" in err


def test_a_changed_pooled_membership_is_stale(loaded, monkeypatch, capsys):
    row = next(r for r in loaded[0]["notices"] if r["audit_id"] == "N22")
    review_path = ROOT / row["page_evidence"]["review_path"]
    review = json.loads(review_path.read_bytes())
    for outcome in review["outcomes"]:
        if outcome["name"] == row["outcome"]:
            outcome["membership"]["pooled"] = list(reversed(outcome["membership"]["pooled"]))[:-1] + ["PMID 1"]
    _mutate_bytes(monkeypatch, review_path, json.dumps(review).encode("utf-8"))
    assert walk.main(["--notice", "N22"]) == 1
    assert "pooled membership is now" in capsys.readouterr().err


def test_the_discriminating_probe_a_corrupted_pinned_digest_is_detached(loaded, monkeypatch, capsys):
    # A walk that ignored the anchors would pass the churn control above; this one proves the pinned bytes are read.
    audit = copy.deepcopy(loaded[0])
    anchor_ = audit["notices"][0]["judgements"][-1]["anchors"][2]
    anchor_["sha256"] = "0" * 64
    audit["source_digests"][anchor_["ref"]] = "0" * 64
    original = Path.read_text
    monkeypatch.setattr(Path, "read_text", lambda p, *a, **k: json.dumps(audit) if p == walk.AUDIT else original(p, *a, **k))
    assert walk.main(["--notice", "N20"]) == 1
    assert "DETACHED" in capsys.readouterr().err


def test_refreshing_the_top_level_digests_without_a_judgement_refuses(loaded, monkeypatch, capsys):
    audit = copy.deepcopy(loaded[0])
    audit["source_digests"] = dict(audit["superseded_anchors"]["source_digests"])  # the pre-B re-point
    original = Path.read_text
    monkeypatch.setattr(Path, "read_text", lambda p, *a, **k: json.dumps(audit) if p == walk.AUDIT else original(p, *a, **k))
    assert walk.main(["--notice", "N01"]) == 1
    assert "working-tree anchor" in capsys.readouterr().err


def test_editing_a_judged_digest_in_place_refuses(loaded):
    row = copy.deepcopy(loaded[0]["notices"][0])
    row["judgements"][-1]["anchors"][2]["sha256"] = "0" * 64
    with pytest.raises(anchor.AnchorRefused, match="recorded sha256"):
        anchor.verify_row(ROOT, row)


def test_an_anchor_whose_commit_is_absent_refuses(loaded):
    row = copy.deepcopy(loaded[0]["notices"][0])
    a = row["judgements"][-1]["anchors"][0]
    a["ref"] = "git:" + "f" * 40 + ":" + anchor.parse(a["ref"])[1]
    with pytest.raises(anchor.AnchorRefused, match="not in this clone"):
        anchor.verify_row(ROOT, row)


def test_a_notice_with_no_judgement_refuses(loaded):
    row = copy.deepcopy(loaded[0]["notices"][0])
    row["judgements"] = []
    with pytest.raises(anchor.AnchorRefused, match="re-judgement required"):
        anchor.verify_row(ROOT, row)


def test_anchors_change_only_by_appending(loaded):
    old = loaded[0]
    appended = copy.deepcopy(old)
    appended["notices"][0]["judgements"].append({"judgement_id": "B2-N01"})
    assert anchor.append_only_problem(old, appended) is None
    edited = copy.deepcopy(old)
    edited["notices"][0]["judgements"][-1]["proposed_commit"] = "0" * 40
    assert "edited or removed" in anchor.append_only_problem(old, edited)
    dropped = copy.deepcopy(old)
    dropped["notices"].pop()
    assert "dropped" in anchor.append_only_problem(old, dropped)


def test_the_committed_registry_only_appended_to_the_audit_it_replaced():
    import subprocess
    base = subprocess.run(["git", "show", "1fa77f2c4852ee79e55d540083e3c35bbff0cecc:registry/notice_adjudication.json"],
                          cwd=ROOT, capture_output=True, check=True).stdout
    old, new = json.loads(base), json.loads(rejudge.AUDIT.read_text(encoding="utf-8"))
    assert anchor.append_only_problem(old, new) is None
    for o, n in zip(old["notices"], new["notices"]):
        assert {k: v for k, v in n.items() if k != "judgements"} == o  # nothing but judgements added per notice


# ------------------------------------------------------------------ signing: defence in depth
def _sign_args(row, index, sha, judgement=None, digest=True):
    args = ["sign", row["slug"], row["outcome"], "--notice-index", str(index), "--by", "Test", "--basis", "test"]
    if digest:
        args += ["--expect-digest", sha]
    if judgement:
        args += ["--judgement", judgement]
    return args


def test_sign_refuses_a_stale_notice_even_with_the_right_digest(loaded, monkeypatch):
    audit, notices, _, mapping = loaded
    row = next(r for r in audit["notices"] if r["audit_id"] == "N20")
    index = mapping["N20"]
    sha = cli._block_and_sha(notices[index])[2]
    _forbid_writes(monkeypatch)
    _mutate_bytes(monkeypatch, _page(row), b"<html>rebuilt page carrying no notice block</html>")
    with pytest.raises(SystemExit, match="STALE"):
        cli.main(_sign_args(row, index, sha, anchor.current_judgement(row)["judgement_id"]))


@pytest.mark.parametrize("digest,judgement", [(False, "B1-N20"), (True, None)])
def test_sign_on_an_audited_notice_requires_both_digest_and_judgement(loaded, monkeypatch, digest, judgement):
    audit, notices, _, mapping = loaded
    row = next(r for r in audit["notices"] if r["audit_id"] == "N20")
    sha = cli._block_and_sha(notices[mapping["N20"]])[2]
    _forbid_writes(monkeypatch)
    with pytest.raises(SystemExit, match="--expect-digest AND --judgement"):
        cli.main(_sign_args(row, mapping["N20"], sha, judgement, digest))


def test_sign_refuses_a_judgement_that_is_not_the_current_one(loaded, monkeypatch):
    audit, notices, _, mapping = loaded
    row = next(r for r in audit["notices"] if r["audit_id"] == "N20")
    sha = cli._block_and_sha(notices[mapping["N20"]])[2]
    _forbid_writes(monkeypatch)
    with pytest.raises(SystemExit, match="not this notice's current judgement"):
        cli.main(_sign_args(row, mapping["N20"], sha, "B0-N20"))


def test_walker_offers_the_judgement_it_verified(loaded):
    audit, notices, chains, mapping = loaded
    for position, row in enumerate(walk.ordered_notices(audit), 1):
        out = walk.present(audit, notices, chains, mapping, position)
        j = anchor.current_judgement(row)
        assert f"--judgement {j['judgement_id']}" in out
        assert f"judgement {j['judgement_id']} on {j['judged_utc']}" in out and j["before_after"] in out
        command_at = out.index("python scripts/countersign_result_change.py sign")
        for text in j["defects"] + ([j["lane_notes"]] if j["lane_notes"] else []) + j["bulk_concerns"]:
            assert out.index(text) < command_at  # every finding is read before the command is offered
        if j["departure_binding"]:
            assert out.index("WHY EACH TRIAL LEFT") < command_at


# ------------------------------------------------------------------ the re-judgement's own direction rule, planted
@pytest.mark.parametrize("before,after,scale,hi,changed,expected", [
    ({"estimate": 0.8, "ci_low": 0.7, "ci_high": 0.9}, {"estimate": None}, "HR", False, True, "RESULT_REMOVED"),
    ({"estimate": None}, {"estimate": 1.2, "ci_low": 1.0, "ci_high": 1.4}, "RR", False, True, "RESULT_ADDED"),
    ({"estimate": None}, {"estimate": None}, "RR", False, True, "NO_DIRECTION"),
    ({"estimate": -3.1, "ci_low": -7.3, "ci_high": 1.1}, {"estimate": -4.4, "ci_low": -8.0, "ci_high": -0.8},
     "MD", False, True, "AWAY_FROM_NULL"),
    ({"estimate": 0.80, "ci_low": 0.70, "ci_high": 0.90}, {"estimate": 0.90, "ci_low": 0.75, "ci_high": 1.08},
     "RR", False, True, "TOWARD_NULL"),
    ({"estimate": 1.5, "ci_low": 1.1, "ci_high": 2.0}, {"estimate": 1.8, "ci_low": 1.2, "ci_high": 2.4},
     "OR", True, True, "AWAY_FROM_NULL"),
])
def test_direction_rule(before, after, scale, hi, changed, expected):
    assert rejudge.direction(before, after, scale, hi, changed) == expected


def test_append_refuses_a_verdict_that_names_other_bytes(monkeypatch, tmp_path, capsys):
    verdicts = tmp_path / "v.json"
    audit = json.loads(rejudge.AUDIT.read_text(encoding="utf-8"))
    verdicts.write_bytes(json.dumps({"verdicts": [
        {"audit_id": r["audit_id"], "anchors": {"git:0000000:x": "0" * 64}, "bulk_verdict": "HOLDS",
         "lane_verdict": "HOLDS", "before_after": "x", "rendered_block_sha256": "x"} for r in audit["notices"]]}).encode())
    _forbid_writes(monkeypatch)
    registry_before = rejudge.AUDIT.read_bytes()
    code = rejudge.main(["append", "--served", "HEAD", "--proposed", "HEAD", "--verdicts", str(verdicts),
                         "--judged-by", "test", "--judgement-prefix", "T"])
    assert code == 1
    assert "names different bytes" in capsys.readouterr().err
    assert rejudge.AUDIT.read_bytes() == registry_before
