"""Plants for G1-ABANDON-v1 (Mahmood 7 Oct: "abandon ten"): an ABANDONED_BY_DECISION topic never counts as matched
(G1 MATCHED or K MATCHED), the page always carries BOTH lines -- n of the active topics AND n of all topics -- and lists
every abandoned topic with its reason. Nothing is deleted: an abandoned topic keeps its row on the page."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import render_g1_tracker as rg  # noqa: E402


def test_the_register_is_the_approved_ten_from_the_preregistered_rule():
    d = json.loads((ROOT / "registry" / "g1_abandoned.json").read_text(encoding="utf-8"))
    assert d["rule_sha256"].startswith("c3ee2f62") and d["rule_commit"].startswith("6f64f133")
    assert len(d["topics"]) == 10 and all(t["state"] == "ABANDONED_BY_DECISION" for t in d["topics"])
    assert all(t["decision"]["words"] == "abandon ten" and t["decision"]["date"] == "2026-10-07" for t in d["topics"])


def test_PLANT_an_abandoned_topic_never_counts_as_matched(monkeypatch):
    recs = rg.load(ROOT)
    live = rg.matched_topics(recs, ROOT)
    assert live, "control: some topic is matched on this tree"
    victim = live[0]
    real = rg.abandoned(ROOT)
    planted = dict(real, **{victim: dict(next(iter(real.values())), slug=victim, reason="planted")})
    monkeypatch.setattr(rg, "abandoned", lambda root=ROOT: planted)
    assert victim not in rg.matched_topics(recs, ROOT)
    assert victim not in rg.k_matched_topics(recs, ROOT)
    html = rg.render(ROOT)
    head = html[:html.index("<table>")]
    assert f"({victim}" not in head and f", {victim}" not in head


def test_PLANT_both_lines_always_present_and_the_all_topics_line_never_disappears(monkeypatch):
    recs = rg.load(ROOT)
    n = len(recs)
    html = rg.render(ROOT)
    assert f"of {n - 10} active topics (10 abandoned by decision" in html
    assert f"of {n} all topics" in html
    # with NO abandonment register the all-topics line is still there (it is never conditional)
    monkeypatch.setattr(rg, "abandoned", lambda root=ROOT: {})
    assert f"of {n} all topics" in rg.render(ROOT)


def test_the_abandoned_list_and_reasons_are_on_the_page():
    html = rg.render(ROOT)
    sec = html[html.index("id='abandoned'"):]
    d = json.loads((ROOT / "registry" / "g1_abandoned.json").read_text(encoding="utf-8"))
    for t in d["topics"]:
        assert t["slug"] in sec and f"U = {t['score_U']}" in sec
    assert "abandon ten" in sec and "c3ee2f62" in sec
    # nothing deleted: every abandoned topic keeps its row in the table
    table = html[html.index("<table>"):html.index("</table>")]
    assert all(f"href='#{t['slug']}'" in table for t in d["topics"])


def test_PLANT_a_register_naming_another_rule_refuses(tmp_path):
    reg = json.loads((ROOT / "registry" / "g1_abandoned.json").read_text(encoding="utf-8"))
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "g1_abandoned.json").write_text(json.dumps(dict(reg, rule_sha256="0" * 64)), encoding="utf-8")
    with pytest.raises(ValueError):
        rg.abandoned(tmp_path)


def test_PLANT_a_released_swap_rule_cannot_run_and_its_rule_file_is_kept():
    import subprocess
    d = json.loads((ROOT / "registry" / "comparator_selection" / "swap_releases.json").read_text(encoding="utf-8"))
    slugs = [r["slug"] for r in d["released"]]
    assert sorted(slugs) == sorted(["ticagrelor-vs-clopidogrel-acs", "colchicine-postop-af", "pcsk9-mace",
                                    "tocilizumab-covid19-mortality"])
    for r in d["released"]:
        assert (ROOT / r["rule"]).is_file()                       # released, never deleted
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "g1_swap.py"), "search", slugs[0]], cwd=ROOT,
                       capture_output=True, text=True)
    assert p.returncode != 0 and "REFUSED: swap rule released" in (p.stderr + p.stdout)


@pytest.mark.parametrize("mutate", [
    lambda t: t + [dict(t[0], slug="unapproved-topic")],          # an extra, unapproved topic (codex abandon-ten g1#1)
    lambda t: t[1:],                                              # one approved topic missing
    lambda t: [dict(t[0], decision=dict(t[0]["decision"], words="no approval given"))] + t[1:],   # other words
])
def test_PLANT_the_register_must_be_exactly_the_approved_ten_with_his_words(tmp_path, mutate):
    reg = json.loads((ROOT / "registry" / "g1_abandoned.json").read_text(encoding="utf-8"))
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "g1_abandoned.json").write_text(json.dumps(dict(reg, topics=mutate(reg["topics"]))),
                                                             encoding="utf-8")
    with pytest.raises(ValueError):
        rg.abandoned(tmp_path)


def test_PLANT_a_self_contradicting_ranking_refuses(monkeypatch, tmp_path):
    import g1_abandon_apply as ap
    rank = json.loads((ROOT / "outputs" / "k_gap" / "g1_abandon_rank.json").read_text(encoding="utf-8"))
    for r in rank["ranked"]:                    # the first approved topic ALSO claims rank 11 (the first kept)
        if r["rank"] == 11:
            r["rank"] = 99
    next(r for r in rank["ranked"] if r["slug"] == ap.APPROVED[0])["rank"] = 11
    real = ap.RANK
    p = tmp_path / "rank.json"
    p.write_text(json.dumps(rank), encoding="utf-8")
    monkeypatch.setattr(ap, "RANK", str(p))
    with pytest.raises(SystemExit):
        ap.build()
    monkeypatch.setattr(ap, "RANK", real)
    assert ap.build()["boundary"]["first_kept"]["slug"] == "iv-iron-hfref-hosp"     # the committed ranking is consistent


def test_PLANT_a_malformed_release_register_refuses(monkeypatch):
    import g1_swap as g
    for bad in ({"released": None}, {"released": []}, {"released": [{"no": "slug"}]}, {"released": [{"slug": 123}]}):
        monkeypatch.setattr(g, "_j", lambda p, bad=bad: bad)
        monkeypatch.setattr(g.os.path, "exists", lambda p: True)
        with pytest.raises(SystemExit):
            g.released(["pcsk9-mace"])


def test_PLANT_a_kept_topic_scoring_above_the_ten_refuses(monkeypatch, tmp_path):
    import g1_abandon_apply as ap
    rank = json.loads((ROOT / "outputs" / "k_gap" / "g1_abandon_rank.json").read_text(encoding="utf-8"))
    row = next(r for r in rank["ranked"] if r["rank"] > 11)          # a later kept topic (codex abandon-ten-r3 g1#1)
    row["U"] = max(r["U"] for r in rank["ranked"]) + 1
    p = tmp_path / "rank.json"
    p.write_text(json.dumps(rank), encoding="utf-8")
    monkeypatch.setattr(ap, "RANK", str(p))
    with pytest.raises(SystemExit):
        ap.build()
