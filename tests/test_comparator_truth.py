import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import comparator_truth, parity_relation  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "ad5e7c66"


def _git_json(path):
    data = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)
    return json.loads(data.decode("utf-8"))


def _json(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _prefix_review(slug):
    return _git_json(f"docs/reviews/{slug}/review.json")


def _prefix_parity_row(slug):
    rows = _git_json("docs/parity.json")
    return next(r for r in rows if r["slug"] == slug)


def _review(slug):
    return _json(f"docs/reviews/{slug}/review.json")


def _topic(slug):
    return _json(f"topics/{slug}.json")


def _text(slug, review):
    pmid = ((review.get("comparator") or {}).get("pmid"))
    return comparator_truth.load_cached_comparator_text(ROOT, slug, pmid, "")


def test_PLANT_sglt2_hfref_parity_refuted_by_participant_n():
    slug = "sglt2-hfref-hosp-cvdeath"
    old = _prefix_review(slug)
    old_rel = parity_relation.compute(_prefix_parity_row(slug), old)
    assert old_rel["relation"] == "IDENTICAL_SET"

    truth = comparator_truth.assess_review(slug, old, _topic(slug), _text(slug, old))
    nrec = truth["participant_reconciliation"]
    assert nrec["code"] == "PARITY_REFUTED_BY_N"
    assert nrec["theirs_n"] == 9199
    assert nrec["ours_n"] == 8474
    assert nrec["excess"] == 725
    assert nrec["theirs_n_span"]["status"] == "FOUND"

    current = _review(slug)
    cur = current["comparator"]["truth"]["participant_reconciliation"]
    assert cur["code"] == "PARITY_REFUTED_BY_N"
    assert current["reproduction"]["parity"]["parity_relation"]["relation"] == "PARITY_REFUTED_BY_N"


def test_pcsk9_agent_scope_class_level_and_recency_from_local_evidence():
    slug = "pcsk9-mace"
    old = _prefix_review(slug)
    assert old["comparator"]["scope"]["comparator_is_class"] is False

    agent = comparator_truth.agent_scope_from_text(_text(slug, old))
    assert agent["comparator_agent_scope"] == "class-level"
    assert "alirocumab" in agent["sentence"].lower()
    assert "evolocumab" in agent["sentence"].lower()

    recency = comparator_truth.recency_vs_named_trials(
        old["comparator"]["year"],
        comparator_truth.NAMED_TRIALS_BY_SLUG[slug],
    )
    assert recency["predates"][0]["code"] == "COMPARATOR_PREDATES_KNOWN_TRIAL(VESALIUS-CV)"

    current = _review(slug)
    scope = current["comparator"]["scope"]
    assert scope["comparator_agent_scope"] == "class-level"
    assert scope["comparator_is_class"] is True


def test_spironolactone_incomplete_and_ephesus_contradiction():
    slug = "spironolactone-hfref-mortality"
    old = _prefix_review(slug)
    truth = comparator_truth.assess_review(slug, old, _topic(slug), _text(slug, old))
    comp = truth["completeness"]
    assert comp["code"] == "COMPARATOR_INCOMPLETE"
    assert comp["missing"] == ["J-EMPHASIS-HF"]
    assert comp["contradictions"][0]["trial"] == "EPHESUS"

    current = _review(slug)
    now = current["comparator"]["truth"]["completeness"]
    assert now["detail"] == "COMPARATOR_INCOMPLETE(missing: J-EMPHASIS-HF)"
    assert now["contradictions"][0]["code"] == "COMPARATOR_SCOPE_CONTRADICTION"


def test_finerenone_identical_set_from_only_two_conforming_text():
    slug = "finerenone-ckd-t2d-renal"
    old = _prefix_review(slug)
    assert "not exactly verifiable" in old["comparator"]["overlap"]["shared_k"]

    truth = comparator_truth.assess_review(slug, old, _topic(slug), _text(slug, old))
    comp = truth["completeness"]
    assert comp["relation"] == "IDENTICAL_SET"
    assert comp["expected_count_span"]["status"] == "FOUND"

    current = _review(slug)
    assert current["comparator"]["truth"]["completeness"]["relation"] == "IDENTICAL_SET"
    assert current["comparator"]["overlap"]["shared_k"] == 2


def test_synthetic_equal_n_and_equal_named_set_allows_parity():
    nrec = comparator_truth.participant_reconciliation(100, [{"label": "A", "n1i": 50, "n2i": 50}])
    assert nrec["code"] == "N_RECONCILIATION_MATCH"

    text = "Only two of the four citations reported renal composite. FIDELIO-DKD and FIGARO-DKD were used."
    comp = comparator_truth.completeness_vs_known_eligible(
        text,
        [
            {"name": "FIDELIO-DKD", "aliases": ["FIDELIO-DKD"]},
            {"name": "FIGARO-DKD", "aliases": ["FIGARO-DKD"]},
        ],
        expected_count=2,
    )
    assert comp["relation"] == "IDENTICAL_SET"
    assert comparator_truth.span_or_not_held(text, 9199)["status"] == "NOT_IN_HELD_TEXT"
