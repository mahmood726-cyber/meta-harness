"""Harms and secondary outcomes not preregistered in the protocol are EXPLORATORY, or cite a dated amendment (dapagliflozin HFpEF
review, 2026-09-26). Served state and protocols at the pinned candidate 3876a62d (a missing commit fails, never skips)."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import outcome_tiers as ot   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"


def _show(path):
    p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]}:{path} not in history (never a skip)", pytrace=False)
    return p.stdout.decode("utf-8")


def _outcome(slug, name):
    return next(o for o in json.loads(_show(f"docs/reviews/{slug}/review.json"))["outcomes"] if o["name"] == name)


def test_plant_dapagliflozin_serves_an_adverse_events_pool_the_protocol_says_is_not_preregistered():
    md = _show("protocols/dapagliflozin-hfpef-hosp.md")
    assert "**Harms** - none preregistered for this topic." in md
    o = _outcome("dapagliflozin-hfpef-hosp", "Adverse events")
    assert o["result"]["estimate"] is not None and "served_tier" not in o and "outcome_tiers" not in o     # served, unlabelled
    p = ot.preregistration(o, md)
    assert p["state"] == "NOT_PREREGISTERED" and p["served_as"] == "EXPLORATORY" and "none preregistered" in p["basis"]


@pytest.mark.parametrize("slug,name,basis", [
    ("ticagrelor-vs-clopidogrel-acs", "Major bleeding", "harm outcomes"),        # '- **Harm outcomes** - major bleeding and dyspnea'
    ("ticagrelor-vs-clopidogrel-acs", "Dyspnea", "harm outcomes"),
    ("denosumab-vertebral-fracture", "Serious adverse events", "harm outcomes"),  # 'Harm outcomes:' + bullet list
    ("corticosteroids-cap-mortality", "Hyperglycaemia", "o (harms)"),            # British spelling vs the protocol's
])
def test_every_protocol_style_is_read(slug, name, basis):
    p = ot.preregistration(_outcome(slug, name), _show(f"protocols/{slug}.md"))
    assert p["state"] == "PREREGISTERED" and basis in p["basis"].lower(), p


def test_a_general_harms_clause_preregisters_harms():
    md = "- **O (primary)** - x.\n- **O (harms / secondary)** - gastrointestinal adverse events, and any further harm outcome the comparator reports.\n"
    assert ot.preregistration({"name": "Acute pancreatitis", "kind": "harm"}, md)["state"] == "PREREGISTERED"


def test_a_dated_amendment_that_names_the_outcome_counts_and_its_date_is_kept():
    md = ("- **O (primary)** - x.\n- **Harms** - none preregistered for this topic.\n\n"
          "## Amendment 2026-09-20 (harms)\nAdverse events are added as a harm outcome.\n")
    p = ot.preregistration({"name": "Adverse events", "kind": "harm"}, md)
    assert p["state"] == "AMENDED" and p["amendment_date"] == "2026-09-20"


def test_no_protocol_text_shows_nothing_preregistered_except_the_primary():
    assert ot.preregistration({"name": "Adverse events", "kind": "harm"}, "")["state"] == "NOT_PREREGISTERED"
    assert ot.preregistration({"name": "x", "primary": True}, "")["state"] == "PREREGISTERED"
