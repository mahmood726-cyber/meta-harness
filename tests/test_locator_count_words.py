"""Plant: a count printed as a WORD ('four of 119', 'seven of 44') is a printed number -- the locator gate refused it
NON_NUMERIC, so two adjudicated-correct probiotics values could not be backed by a recorded read. A word stands only when
that very word is in the quote, and only for counts (never an effect or a bound)."""
from harness.secondary_meta import gate_locator_claim

TEXT = "AAD occurred in four of 119 (3.4%) vs. 22 of 127 (17.3%) children."


def _c(**kw):
    c = {"state": "REPORTED", "quote": "four of 119 (3.4%) vs. 22 of 127", "measure": None, "point": None, "lower": None,
         "upper": None, "events_t": "four", "n_t": "119", "events_c": "22", "n_c": "127"}
    c.update(kw)
    return c


def test_a_worded_count_in_the_quote_stands():
    val, why = gate_locator_claim(_c(), TEXT, prefer="counts")
    assert why == "ACCEPTED" and val["events_t"] == 4 and val["n_t"] == 119


def test_a_word_not_in_the_quote_is_refused():
    assert gate_locator_claim(_c(events_t="five"), TEXT, prefer="counts")[1] == "NUMBER_NOT_IN_QUOTE"


def test_a_word_is_never_an_effect():
    assert gate_locator_claim(_c(point="four", lower="0.1", upper="0.9", events_t=None), TEXT)[1] == "NON_NUMERIC"
