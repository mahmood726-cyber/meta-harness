"""DOAC-VTE review (2026-09-26): (1) a protocol-permitted HR+RR mixture is LABELLED as one, with a majority-measure sensitivity
analysis; (2) narrative rules: never infer noninferiority/equivalence, name treatment strategies, state populations literally.
Served state at the pinned candidate 3876a62d (a missing commit fails, never skips)."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import estmeasure as em, narrative_rules as nr, synth   # noqa: E402
from harness.known_missing import _study_from_trial                  # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
SLUG = "doac-vte-recurrence"


def _show(path):
    p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]}:{path} not in history (never a skip)", pytrace=False)
    return p.stdout.decode("utf-8")


def _primary():
    return next(o for o in json.loads(_show(f"docs/reviews/{SLUG}/review.json"))["outcomes"] if o.get("primary"))


def _records():
    return {str(r["id"]): r for r in json.loads(_show(f"cache/{SLUG}/records.json"))["records"]}


# ------------------------------------------------------------------ (1) the mixture label
def test_plant_served_pool_mixes_five_hrs_and_amplifys_rr_under_an_hr_label():
    res = _primary()["result"]
    assert res["scale"] == "HR" and res["scale_mixed"] == ["HR", "RR"]


def test_the_protocol_permitted_mixture_is_labelled_as_an_approximation_per_protocol():
    topic = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    pol = em.mixture_policy(topic["primary_outcome"])
    assert pol and pol["basis"] == "protocol" and "NOT demonstrably prospective" in pol["registration"]
    labels = [t["scale"] for t in _primary()["trials"]]
    d = em.pool_measure_decision(labels, ["UNSTATED"] * len(labels), pol)
    assert d["state"] == "MIXED_BY_POLICY" and d["label"] == "mixed ratio (HR+RR, approximation per protocol)"
    assert d["sensitivity_restricted_to"] == "HR"


def test_mixed_and_hr_only_sensitivity_reproduce_the_review():
    trials = _primary()["trials"]
    st = [_study_from_trial(t, t["scale"]) for t in trials]
    m = synth.pool(st, scale="HR")
    h = synth.pool([s for s, t in zip(st, trials) if t["scale"] == "HR"], scale="HR")
    assert (round(m.estimate, 6), round(m.ci_low, 6), round(m.ci_high, 6)) == (0.909108, 0.747947, 1.104993)
    assert (round(h.estimate, 6), round(h.ci_low, 6), round(h.ci_high, 6), h.k) == (0.926524, 0.732709, 1.171606, 5)


# ------------------------------------------------------------------ (2) narrative rules
def test_the_served_page_quotes_trial_ni_conclusions_and_infers_none():
    held = [r.get("abstract", "") for r in _records().values()]
    assert nr.check_ni_inference(_show(f"docs/reviews/{SLUG}/index.html"), held) == []


@pytest.mark.parametrize("claim", [
    "The pooled hazard ratio crosses 1, so DOACs are noninferior to VKA for recurrent VTE.",
    "Across trials, DOACs showed comparable efficacy to warfarin.",
    "The pooled estimate shows the strategies are equivalent to VKA.",
])
def test_plant_a_generated_ni_or_equivalence_inference_is_refused(claim):
    held = [r.get("abstract", "") for r in _records().values()]
    page = _show(f"docs/reviews/{SLUG}/index.html").replace("</body>", f"<p>{claim}</p></body>")
    assert nr.check_ni_inference(page, held), claim


def test_the_publication_gate_refuses_a_generated_ni_inference(tmp_path):
    from harness import gate
    rd = tmp_path / "docs" / "reviews" / SLUG
    rd.mkdir(parents=True)
    (tmp_path / "cache" / SLUG).mkdir(parents=True)
    (tmp_path / "cache" / SLUG / "records.json").write_text(_show(f"cache/{SLUG}/records.json"), encoding="utf-8")
    ok_html = _show(f"docs/reviews/{SLUG}/index.html")
    assert gate.check_narrative_no_ni_inference(str(rd), ok_html) == []
    bad = ok_html.replace("</body>", "<p>So DOACs are noninferior to VKA.</p></body>")
    assert gate.check_narrative_no_ni_inference(str(rd), bad)[0].startswith("L1: generated narrative infers noninferiority")


@pytest.mark.parametrize("pmid,drug,strategy", [
    ("19966341", "dabigatran", "parenteral lead-in then dabigatran"),      # RE-COVER
    ("24344086", "dabigatran", "parenteral lead-in then dabigatran"),      # RE-COVER II
    ("23991658", "edoxaban", "parenteral lead-in then edoxaban"),          # Hokusai-VTE
    ("22449293", "rivaroxaban", "rivaroxaban alone (no parenteral lead-in)"),
    ("21128814", "rivaroxaban", "rivaroxaban alone (no parenteral lead-in)"),
    ("23808982", "apixaban", "apixaban alone (no parenteral lead-in)"),    # AMPLIFY: "apixaban alone", not "major bleeding alone"
])
def test_treatment_strategies_are_read_from_the_held_abstract(pmid, drug, strategy):
    s = nr.strategy_label(_records()[pmid]["abstract"], drug)
    assert s["strategy"] == strategy and s["basis"]


def test_a_strategy_is_never_guessed_and_populations_are_only_what_the_source_states():
    assert nr.strategy_label("Dabigatran was compared with warfarin.", "dabigatran")["strategy"] == "NOT_STATED_IN_HELD_TEXT"
    assert nr.populations_stated(_records()["23808982"]["abstract"]) == []    # AMPLIFY's abstract states none; full text not held


def test_the_ni_check_passes_every_served_page_and_lets_a_negation_through():
    """The rule must not over-refuse: all 32 served pages pass (a first version flagged 15 false positives -- 'not equivalent to',
    'Embase-equivalent', quoted titles, a truncated quotation -- fixed by matching claim constructions only)."""
    names = [n.split("/")[2] for n in subprocess.run(["git", "ls-tree", "-r", "--name-only", PINNED, "docs/reviews"], cwd=ROOT,
                                                       capture_output=True, text=True).stdout.split()
             if n.count("/") == 3 and n.endswith("index.html")]
    assert len(names) == 32
    for slug in names:
        held = []
        for path in (f"docs/cache/{slug}/records.json", f"cache/{slug}/records.json"):
            p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
            if p.returncode == 0:
                held = [(r.get("abstract", "") or "") + " " + (r.get("title", "") or "") for r in json.loads(p.stdout)["records"]]
                break
        assert nr.check_ni_inference(_show(f"docs/reviews/{slug}/index.html"), held) == [], slug
    page = _show(f"docs/reviews/{SLUG}/index.html").replace("</body>", "<p>DOACs are not noninferior on this evidence.</p></body>")
    assert nr.check_ni_inference(page, [r.get("abstract", "") for r in _records().values()]) == []
