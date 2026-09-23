"""The evidence-record verifier must be able to FAIL. Every plant is synthetic (tmp files), so the controls
cannot retire themselves when a real source or record changes. Each plant is paired with the clean record it
mutates, and the clean record must verify first -- otherwise a red plant proves nothing."""
import copy, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "evidence", "scripts"))
import verify_records as V

ABSTRACT = ("TRIAL-X randomized 1,000 adults with heart failure and ejection fraction below 40%. Patients were "
            "assigned to drug A 10 mg daily or placebo. The primary end point was cardiovascular death. "
            "Over a median follow-up of 2.0 years, the hazard ratio was 0.82 (95% CI, 0.70 to 0.96). "
            "All analyses were intention-to-treat.")


def _setup(tmp_path, served=0.82):
    src = tmp_path / "abs.txt"
    src.write_text(ABSTRACT, encoding="utf-8")
    ref = str(src)
    packet = {"sources": [{"ref": ref, "text": ABSTRACT}],
              "served_row": {"effect": served, "ci_low": 0.70, "ci_high": 0.96, "scale": "HR"}}
    f = lambda s: {"ref": ref, "span": s}
    rec = {"verdict": "BOUND", "fields": {
        "population": f("randomized 1,000 adults with heart failure and ejection fraction below 40%"),
        "endpoint": f("The primary end point was cardiovascular death."),
        "estimate": f("the hazard ratio was 0.82 (95% CI, 0.70 to 0.96)"),
        "ci": f("the hazard ratio was 0.82 (95% CI, 0.70 to 0.96)"),
        "analysis_set": f("All analyses were intention-to-treat."),
        "treatment_strategy": f("assigned to drug A 10 mg daily or placebo"),
        "follow_up": f("median follow-up of 2.0 years")},
        "bound_values": {"scale": "HR", "estimate": "0.82", "ci_low": "0.70", "ci_high": "0.96"}}
    return rec, packet, src


def test_clean_record_verifies_and_matches(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    r = V.verify(rec, pk)
    assert r["errors"] == [] and r["served_compare"]["state"] == "MATCH"


def test_one_character_changed_in_a_span_is_refused(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    assert V.verify(rec, pk)["errors"] == []
    rec["fields"]["population"]["span"] = rec["fields"]["population"]["span"].replace("1,000", "1,001")
    assert any("population: span not found" in e for e in V.verify(rec, pk)["errors"])


def test_ref_outside_the_packet_is_refused(tmp_path):
    rec, pk, src = _setup(tmp_path)
    other = tmp_path / "other.txt"; other.write_text(ABSTRACT, encoding="utf-8")
    rec["fields"]["endpoint"]["ref"] = str(other)
    assert any("not a source in the packet" in e for e in V.verify(rec, pk)["errors"])


def test_bound_number_not_printed_in_span_is_refused(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["bound_values"]["estimate"] = "0.80"
    assert any("bound_values.estimate" in e for e in V.verify(rec, pk)["errors"])


def test_changed_source_bytes_are_refused_against_a_pinned_sha(tmp_path):
    rec, pk, src = _setup(tmp_path)
    pinned = V.verify(rec, pk)["spans"]
    src.write_text(ABSTRACT + " ", encoding="utf-8")   # same rendered text, different bytes
    assert any("sha256 changed" in e for e in V.verify(rec, pk, pinned)["errors"])


def test_bound_verdict_without_a_ci_span_is_refused(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["fields"]["ci"] = None
    rec["bound_values"].pop("ci_low"); rec["bound_values"].pop("ci_high")
    assert any("core fields unbound" in e for e in V.verify(rec, pk)["errors"])


def test_served_value_differing_from_the_bound_span_is_reported_not_hidden(tmp_path):
    rec, pk, _ = _setup(tmp_path, served=0.68)
    r = V.verify(rec, pk)
    assert r["errors"] == [] and r["served_compare"]["state"] == "DIFFERS"


def test_a_number_on_another_scale_is_never_compared_as_the_served_number(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    pk["served_row"] = {"effect": 0.82, "ci_low": 0.70, "ci_high": 0.96, "scale": "RR"}
    r = V.verify(rec, pk)   # the span holds an HR of 0.82; the served RR of 0.82 must NOT read as a MATCH
    assert r["served_compare"]["state"] == "NOT_COMPARABLE"


def test_served_arm_counts_are_compared_count_for_count(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["bound_values"] = {"events_t": "0.82", "n_t": "0.70", "events_c": "0.96", "n_c": "0.82"}  # printed tokens
    pk["served_row"] = {"ai": 0.82, "n1i": 0.70, "ci": 0.96, "n2i": 0.82}
    assert V.verify(rec, pk)["served_compare"]["state"] == "MATCH"
    pk["served_row"]["ci"] = 0.95
    assert V.verify(rec, pk)["served_compare"]["state"] == "DIFFERS"


def test_served_arm_means_in_either_field_shape_are_compared(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["bound_values"] = {"mean_t": "0.82", "sd_t": "0.70", "n_t": "0.96", "mean_c": "0.70", "sd_c": "0.96", "n_c": "0.82"}
    pk["served_row"] = {"mean1": 0.82, "sd1": 0.70, "nc1": 0.96, "mean2": 0.70, "sd2": 0.96, "nc2": 0.82}
    assert V.verify(rec, pk)["served_compare"]["state"] == "MATCH"
    pk["served_row"]["nc2"] = 0.96          # a denominator that is not the one the span prints
    assert V.verify(rec, pk)["served_compare"]["state"] == "DIFFERS"


# ---- adjudications: a confirmation must be checkable against the served numbers
import adjudicate as A


def test_confirmation_refused_when_served_numbers_are_not_in_the_cited_spans(tmp_path):
    served = {"effect": 0.82, "ci_low": 0.70, "ci_high": 0.96}
    ok = {"evidence": {"e": {"span": "hazard ratio was 0.82 (95% CI, 0.70 to 0.96)"}}}
    assert A.confirm_check(ok, served) is None
    bad = {"evidence": {"e": {"span": "hazard ratio was 0.82 (95% CI, 0.70 to 0.97)"}}}
    assert "not printed" in A.confirm_check(bad, served)


def test_confirmation_by_derivation_must_equal_the_served_numbers():
    served = {"effect": 0.44, "ci_low": 0.27, "ci_high": 0.73}
    assert A.confirm_check({"derivation": {"result": [0.44, 0.27, 0.73]}}, served) is None
    assert "!=" in A.confirm_check({"derivation": {"result": [0.44, 0.27, 0.74]}}, served)
