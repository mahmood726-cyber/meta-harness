"""The final-5 reader gate (scripts/g1_final5_readers.gate): a reader's quote counts only when EVERY passage it joins
is verbatim in the same bytes it was shown, and every count it reports is printed in its quote.

Instance (8 Oct): both CONFIRM-HF readers quoted the Table 2 header and the 'Hospitalizations due to worsening HF' row as
two passages joined by a newline. Each passage is verbatim in the held text; the joined string is not, so a true quote
was refused as QUOTE_NOT_VERBATIM -- a refusal that reads as a finding about the reader."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_final5_readers as fr  # noqa: E402

SHOWN = ("Table 2 Hospitalizations and deaths (full-analysis set) End-point or event FCM ( n = 150) Placebo ( n = 151) "
         "Death 12 12 (8.9) 14 14 (9.9) Hospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4) 0.39")


def ans(quote, **v):
    return dict({"state": "FOUND", "quote": quote, "events_t": 10, "n_t": 150, "events_c": 25, "n_c": 151}, **v)


def test_a_quote_of_two_verbatim_passages_joined_by_a_newline_is_gated():
    q = "FCM ( n = 150) Placebo ( n = 151)\nHospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4)"
    assert fr.gate(ans(q), SHOWN) == "GATED"


def test_a_passage_that_is_not_in_the_shown_bytes_still_refuses_the_whole_quote():
    q = "FCM ( n = 150) Placebo ( n = 151)\nHospitalizations due to worsening HF 10 10 (7.6) 32 26 (19.4)"
    assert fr.gate(ans(q), SHOWN) == "QUOTE_NOT_VERBATIM"


def test_a_count_not_printed_in_the_quote_is_refused():
    q = "Hospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4)"
    assert fr.gate(ans(q), SHOWN).startswith("NUMBER_NOT_IN_QUOTE:n_t,n_c")


def test_a_trivial_fragment_is_not_a_passage():
    # a joined quote must not smuggle numbers in through a one-token 'passage' that happens to occur anywhere
    q = "Hospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4)\n150\n151"
    assert fr.gate(ans(q), SHOWN) == "QUOTE_NOT_VERBATIM"


def test_PLANT_a_percentage_in_the_quote_is_not_a_count():
    # codex final5-binding-r1a g1#2: Kaplan-Meier percentages '10%' / '20%' were gated as participant counts
    q = "FCM randomised n=100; placebo randomised n=100. Deaths at 28 days (Kaplan-Meier estimates): FCM 10%, placebo 20%."
    a = {"state": "FOUND", "quote": q, "events_t": 10, "n_t": 100, "events_c": 20, "n_c": 100}
    assert fr.gate(a, q).startswith("NUMBER_NOT_IN_QUOTE:events_t,events_c")


def test_PLANT_a_decimal_comma_percentage_is_not_a_count():
    # codex final5-binding-r2 g1#1: '0,5%' left its integer part '0' as a 'count'
    q = "FCM n=100 and placebo n=100 were randomised. Deaths: FCM 0,5% and placebo 0,7% at 28 days."
    a = {"state": "FOUND", "quote": q, "events_t": 0, "n_t": 100, "events_c": 0, "n_c": 100}
    assert fr.gate(a, q).startswith("NUMBER_NOT_IN_QUOTE:events_t,events_c")


def test_PLANT_the_word_percent_is_a_percentage_not_a_count():
    # captain codex final5-binding-captain g1#2
    q = "Mortality was 10 percent with FCM and 20 percent with placebo; each arm randomised 200 patients."
    a = {"state": "FOUND", "quote": q, "events_t": 10, "n_t": 200, "events_c": 20, "n_c": 200}
    assert fr.gate(a, q).startswith("NUMBER_NOT_IN_QUOTE:events_t,events_c")
