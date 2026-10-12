"""The pre-triage's local check decides whether a model's BIND stands. It must reject a span not in the bytes shown and
any number not in the span (a reader's inferred or computed number is never a binding)."""
import os
import sys

sys.path[:0] = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")]
import m2_pretriage as t  # noqa: E402

SRC = "TITLE: X\nABSTRACT: Death at 90 days occurred in 530 of 2433 patients (21.8%) and 530 of 2413 (22.0%); HR 0.99 (95% CI, 0.89 to 1.10)."


def test_a_verbatim_span_with_its_own_numbers_binds():
    ok, _ = t.check_bind({"decision": "BIND", "span": "HR 0.99 (95% CI, 0.89 to 1.10)",
                          "numbers": {"effect": 0.99, "ci_low": 0.89, "ci_high": 1.1}}, SRC)
    assert ok


def test_a_span_not_in_the_source_shown_never_binds():
    ok, why = t.check_bind({"decision": "BIND", "span": "HR 0.98 (95% CI, 0.89 to 1.10)", "numbers": {}}, SRC)
    assert not ok and "span" in why


def test_a_number_not_in_the_span_never_binds():
    ok, why = t.check_bind({"decision": "BIND", "span": "HR 0.99 (95% CI, 0.89 to 1.10)",
                            "numbers": {"effect": 0.99, "ci_low": 0.88, "ci_high": 1.1}}, SRC)
    assert not ok and "ci_low" in why


def test_a_refuse_is_not_a_bind():
    assert not t.check_bind({"decision": "REFUSE", "span": "", "numbers": {}}, SRC)[0]
