from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path

from harness import limitations, page, rob_sensitivity as rs

ROOT = Path(__file__).resolve().parents[1]
BASE_REF = "aa8ed28a"

EXPECTED_IDENTICAL_SLUGS = [
    "balanced-crystalloids-vs-saline-mortality",
    "colchicine-postop-af",
    "colchicine-recurrent-pericarditis",
    "dapagliflozin-hfpef-hosp",
    "denosumab-vertebral-fracture",
    "dpp4-mace-t2d",
    "empagliflozin-hfpef-hosp",
    "finerenone-ckd-t2d-renal",
    "melatonin-primary-insomnia-sol",
    "noac-vs-warfarin-af-stroke",
    "pcsk9-mace",
    "probiotics-aad-prevention",
    "sacubitril-valsartan-hfref",
    "semaglutide-obesity-weight",
    "sglt2-ckd-progression",
    "sglt2-hfref-hosp-cvdeath",
    "statins-primary-prevention-elderly",
]
EXPECTED_FEWER_SLUGS = [
    "colchicine-secondary-cv-prevention",
    "corticosteroids-cap-mortality",
    "doac-vte-recurrence",
    "glp1-ra-mace-t2d",
    "metformin-pcos-ovulation",
    "omega3-cardiovascular-events",
    "sglt2-primary-prevention-hf",
    "spironolactone-hfref-mortality",
    "ticagrelor-vs-clopidogrel-acs",
]


def _git_text(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{BASE_REF}:{path}"],
        cwd=ROOT,
        encoding="utf-8",
    )


def _refused_pool_slugs() -> list[str]:
    """Pages whose primary pooled ROW is refused (k=2 direction conflict): no RoB re-pool exists."""
    out = []
    for path in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        prim = next((o for o in review.get("outcomes", []) if o.get("primary")), {}) or {}
        if (prim.get("result") or {}).get("pool_refused") and not review.get("rob_sensitivity"):
            out.append(path.parent.name)
    return out


def _current_rob_slugs() -> list[str]:
    slugs = []
    for path in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        if review.get("rob_sensitivity"):
            slugs.append(path.parent.name)
    return slugs


def _base_review(slug: str) -> dict:
    return json.loads(_git_text(f"docs/reviews/{slug}/review.json"))


def _base_html(slug: str) -> str:
    return _git_text(f"docs/reviews/{slug}/index.html")


def _current_review(slug: str) -> dict:
    path = ROOT / "docs" / "reviews" / slug / "review.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _current_html(slug: str) -> str:
    path = ROOT / "docs" / "reviews" / slug / "index.html"
    return path.read_text(encoding="utf-8")


def _low_only_cell(rendered_html: str) -> str:
    match = re.search(
        r"<tr><t[dh](?: scope=\"row\")?>Low risk of bias only</t[dh]><td>(.*?)</td></tr>",
        rendered_html,
        flags=re.DOTALL,
    )
    assert match, "low-risk-only row missing from rendered RoB sensitivity table"
    return html.unescape(re.sub(r"<[^>]+>", "", match.group(1)))


def predicate_is_true(sens: dict, rendered_html: str) -> bool:
    cell = _low_only_cell(rendered_html)
    relation = rs.relation_from_sensitivity(sens)
    if relation == rs.LOW_ONLY_IDENTICAL_TO_FULL:
        return (
            "fewer trials than the full pool" not in cell
            and "NOT ESTIMABLE" not in cell
        )
    if relation == rs.LOW_ONLY_FEWER_TRIALS:
        return (
            "all pooled trials are low risk; the re-pool is the full pool" not in cell
            and "NOT ESTIMABLE" not in cell
        )
    if relation == rs.LOW_ONLY_EMPTY:
        return "NOT ESTIMABLE" in cell and "fewer trials than the full pool" not in cell
    return "fewer trials than the full pool" not in cell


def relation_sentence_is_rendered(sens: dict, rendered_html: str) -> bool:
    cell = _low_only_cell(rendered_html)
    typed_state = re.search(r'<span data-claim-id="risk-sensitivity-state".*?</span>',
                           rendered_html, flags=re.DOTALL)
    if typed_state:
        cell = html.unescape(re.sub(r'<[^>]+>', '', typed_state.group(0))).lower()
    relation = rs.relation_from_sensitivity(sens)
    if relation == rs.LOW_ONLY_IDENTICAL_TO_FULL:
        return ("all pooled trials are low risk; the re-pool is the full pool" in cell
                or "all pooled trials are low risk on assessed domains; the re-pool is the full pool" in cell)
    if relation == rs.LOW_ONLY_FEWER_TRIALS:
        return "fewer trials than the full pool" in cell
    if relation == rs.LOW_ONLY_EMPTY:
        return "NOT ESTIMABLE" in cell
    return True


def test_prefix_rendered_predicate_fires_on_identical_low_only_pages():
    failures = []
    fewer_true = []
    rows = []
    for slug in _current_rob_slugs():
        review = _base_review(slug)
        sens = review.get("rob_sensitivity")
        if not sens:
            continue
        relation = rs.relation_from_sensitivity(sens)
        ok = predicate_is_true(sens, _base_html(slug))
        rows.append((slug, relation, ok))
        if not ok:
            failures.append(slug)
        if relation == rs.LOW_ONLY_FEWER_TRIALS and ok:
            fewer_true.append(slug)

    count_line = f"{len(failures)} of {len(rows)}"
    print(f"pre-fix predicate failures: {count_line}")
    # N is the pre-fix population: every committed page whose object carried a RoB sensitivity (31 at
    # aa8ed28a). Integration 2026-09-16: ticagrelor's pooled row is now REFUSED (direction conflict), so
    # its rebuilt object has no re-pool and _current_rob_slugs() drops it -- the pre-fix row is added back
    # from the committed object so the pre-fix count stays a statement about aa8ed28a.
    assert len(rows) + len(_refused_pool_slugs()) == 31, (len(rows), _refused_pool_slugs())
    assert len(failures) == 17 - sum(1 for s in _refused_pool_slugs() if s in EXPECTED_IDENTICAL_SLUGS)
    assert failures == [s for s in EXPECTED_IDENTICAL_SLUGS if s not in _refused_pool_slugs()]
    assert fewer_true == [s for s in EXPECTED_FEWER_SLUGS if s not in _refused_pool_slugs()]


def test_postfix_rebuilt_pages_satisfy_relation_predicate():
    failures = []
    rows = []
    for slug in _current_rob_slugs():
        review = _current_review(slug)
        sens = review["rob_sensitivity"]
        expected_relation = rs.low_only_relation(sens.get("full"), sens.get("low_only"))
        rows.append(slug)
        if sens.get("low_only_relation") != expected_relation:
            failures.append((slug, "object", sens.get("low_only_relation"), expected_relation))
            continue
        if not predicate_is_true(sens, _current_html(slug)):
            failures.append((slug, "html", sens.get("low_only_relation")))
        if not relation_sentence_is_rendered(sens, _current_html(slug)):
            failures.append((slug, "sentence", sens.get("low_only_relation")))

    count_line = f"{len(rows) - len(failures)} of {len(rows)}"
    print(f"post-fix predicate passes: {count_line}")
    # Post-fix population: pages that still have a re-pool. A refused pooled row has none by design and
    # renders the refusal statement instead (asserted by name, not silently dropped).
    assert len(rows) + len(_refused_pool_slugs()) == 31, (len(rows), _refused_pool_slugs())
    assert count_line == f"{len(rows)} of {len(rows)}"
    assert failures == []


def _point(k: int, estimate: float = 0.8) -> dict:
    return {"k": k, "estimate": estimate, "scale": "RR", "ci_low": estimate - 0.1, "ci_high": estimate + 0.1}


def _sens(full_k: int, low_k: int | None) -> dict:
    full = _point(full_k)
    low_only = _point(low_k, 0.82) if low_k is not None else None
    relation = rs.low_only_relation(full, low_only)
    return {
        "n_rob_rated": full_k,
        "n_trials": full_k,
        "any_high": False,
        "full": full,
        "drop_high": full,
        "low_only": low_only,
        "low_only_relation": relation,
        "low_only_informative": relation == rs.LOW_ONLY_FEWER_TRIALS,
    }


def _review_with_sens(sens: dict) -> dict:
    domains = {
        "D1_randomisation": {"basis": "synthetic", "level": "low"},
        "D2_deviations": {"basis": "synthetic", "level": "low"},
        "D3_missing_outcome_data": {"basis": "synthetic", "level": "not assessed"},
        "D4_outcome_measurement": {"basis": "synthetic", "level": "low"},
        "D5_selective_reporting": {"basis": "synthetic", "level": "low"},
    }
    return {
        "outcomes": [{"primary": True, "trials": [{"id": "PMID 1", "label": "1"}]}],
        "rob2": {"source": "synthetic", "trials": {"1": {"overall": "low", "domains": domains}}},
        "rob_sensitivity": sens,
    }


def test_page_uses_per_item_states_instead_of_stale_sensitivity_totals():
    cases = [
        (_sens(3, 2), "fewer trials than the full pool"),
        (_sens(2, 2), "all pooled trials are low risk; the re-pool is the full pool"),
    ]
    for sens, expected_phrase in cases:
        rendered = page._riskofbias(_review_with_sens(sens), neutral=False)
        limitations_cell = _low_only_cell(limitations._rob_sensitivity_block(sens))
        # This fixture holds only one low-rated trial, regardless of the stale
        # synthetic full_k/low_k summaries. The migrated page uses that row.
        assert '1 of 1 rows retained' in rendered
        assert 'All pooled trials are low risk on assessed domains' in rendered
        assert 'UNRENDERABLE' in rendered  # no source effect exists in this fixture
        assert expected_phrase in limitations_cell
