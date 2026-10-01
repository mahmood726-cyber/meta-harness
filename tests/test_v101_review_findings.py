"""V1.0.1 hostile review (codex slot B, lane-logged record mc-210b69f4c54c49284c88c29a4634734f), findings reproduced by execution
before any fix. Plants fired on the pre-fix code.

F2: the backward endpoint-label search stopped at the first cell matching `mace|point|composite`, so the regulatory phrasing
    "... with a point estimate of 0.87" (held GLP-1 regulatory sources use it) stopped the search on the NUMERIC cell and the label
    came back UNSTATED -- in the verifier and in both producer copies. The cue is an endpoint name, not the word "point".
F3: _finite_number(10**400) raised OverflowError (math.isfinite converts to float), turning a malformed input into a crash.
F1 (a linkage refusal does not stop the certified pool being computed) reproduced and is BY DESIGN: the five-verdict split
    reports state reproduction independently of linkage, and publication is refused on linkage
    (tests/test_pool_binding.py::test_rotated_ids_fail_linkage_while_state_reproduction_passes guards exactly that)."""
import re
from pathlib import Path

from scripts import verify_bundle as verifier

ROOT = Path(__file__).resolve().parents[1]
EFFECT = {"estimate": 0.87, "ci_low": 0.80, "ci_high": 0.95}


def test_point_estimate_prose_does_not_hide_the_endpoint_label():
    txt = ("On-treatment | 3-point MACE | (0.80, 0.95) with a point estimate of 0.87 | 4-point MACE+ | (0.82, 0.97) "
           "with a point estimate of 0.89")
    assert verifier.regulatory_holder_endpoint({"text": txt}, EFFECT) == {"3-point MACE"}


def test_the_same_row_without_the_prose_is_unchanged():
    txt = "On-treatment | 3-point MACE | 0.87 (0.80, 0.95) | 4-point MACE+ | 0.89 (0.82, 0.97)"
    assert verifier.regulatory_holder_endpoint({"text": txt}, EFFECT) == {"3-point MACE"}


def test_the_producer_uses_the_same_label_cue_as_the_verifier():
    # three copies of one rule (verifier + two producer sites): they must stay one rule
    cue_v = re.findall(r're\.search\(r"([^"]+)", pieces\[j\]', (ROOT / "scripts" / "verify_bundle.py").read_text(encoding="utf-8"))
    cue_p = re.findall(r're\.search\(r"([^"]+)", pieces\[j\]', (ROOT / "scripts" / "build_bundle.py").read_text(encoding="utf-8"))
    assert len(cue_v) == 1 and len(cue_p) == 2 and set(cue_p) == set(cue_v), (cue_v, cue_p)
    assert not re.search(cue_v[0], "(0.80, 0.95) with a point estimate of 0.87", re.I)
    assert all(re.search(cue_v[0], s, re.I) for s in ("3-point MACE", "4-point MACE+", "composite endpoint", "MACE"))


def test_a_huge_integer_is_not_finite_and_does_not_crash():
    assert verifier._finite_number(10 ** 400) is False
    assert verifier._finite_number(0.87) is True and verifier._finite_number(True) is False
