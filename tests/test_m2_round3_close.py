"""M2 battery review, round 3 of 3 (codex + agy m2comb-cap-r3, 12 Oct): the two agy findings left "UNRESOLVED for the
binding lane" (commit 739f7f1a8) are closed here, each EXECUTED on its own failing input (14 Oct)."""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from harness import pipeline  # noqa: E402
from harness import verified_inputs as vi  # noqa: E402


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (agy m2comb-cap-r3 #4; review stops at three): _validate on an entry "
                                       "with NO 'kind' raises a bare KeyError, not a typed refusal; and a kind other "
                                       "than typed_refusal returns a row refusal instead of raising. Not reachable from "
                                       "a real entry: the normaliser always sets kind and allows only four kinds "
                                       "(verified_inputs.py:17-21)")
def test_known_limit_validate_on_an_unnormalised_entry(tmp_path):
    (tmp_path / "doc.txt").write_text("held text without the span", encoding="utf-8")
    refusal = vi._validate({"source_span": "10 deaths", "document_ref": "doc.txt"}, tmp_path, "trial_1")
    assert refusal and refusal["reason_code"] == "ENDPOINT_UNBOUND"


def test_a_span_refused_trial_is_typed_extraction_debt_never_unmeasured():
    """agy m2comb-cap-r3 #5 (P1) REFUTED by execution: it claimed a span-refused trial is 'disguised as absent /
    unmeasured'. Run on its own input, the trial leaves the pool and is shown as EXTRACTION_DEBT / ENDPOINT_UNBOUND /
    ABSTAIN with the reason -- the documented abstention, fail-closed. This pins that, so it cannot quietly become
    'absent'."""
    o = pipeline._build_outcome(
        {"name": "all-cause mortality"}, "arms", [{"id": "12345", "id_type": "pmid"}], {"12345": {}}, ["A"], ["B"],
        verified_arms={"12345": {"outcome": "all-cause mortality", "kind": "extracted_counts", "source_span": "bad span",
                                 "document_ref": "x.txt", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10,
                                 "span_refusal": {"reason_code": "ENDPOINT_UNBOUND",
                                                  "reason": "source_span absent from held document x.txt"}}})
    assert not [t for t in o.get("trials", []) if "12345" in str(t.get("id"))]
    a = [x for x in o.get("declared_absent_trials", []) if "12345" in str(x.get("id"))]
    assert len(a) == 1
    assert (a[0]["state"], a[0]["endpoint_admissibility"], a[0]["hand_binding_state"]) == \
        ("EXTRACTION_DEBT", "ENDPOINT_UNBOUND", "ABSTAIN")
    assert "source_span absent" in a[0]["reason"] and a[0]["span_refusals"]
