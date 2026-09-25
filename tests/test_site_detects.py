"""R2 labelling specs (regex_layer/site_detects.py): one per regex site of target_endpoint.py, eligibility_chain.py,
compat_check.py and the other lane's files (read only: rob2.py, funding.py, hand_binding.py; gate.py,
protocol_compiler.py, absence.py, registry_multi.py, pipeline.py); each labellable trigger is a superset of the site's
accept plants (it is used to sample misses)."""
from __future__ import annotations

import re

import pytest

from regex_layer.site_detects import DETECTS
from regex_layer.specs import INLINE_SPECS

FILES = ("target_endpoint.py", "eligibility_chain.py", "compat_check.py",   # regex-layer files: 42 sites
         "rob2.py", "funding.py", "hand_binding.py",                          # other lane, batch 1: 70 sites
         "gate.py", "protocol_compiler.py", "absence.py", "registry_multi.py", "pipeline.py")  # batch 2: 69 sites
N_SITES = 42 + 70 + 69
SITE_KEYS = sorted(k for k in INLINE_SPECS if k.split(":", 1)[0] in FILES)


def test_keys_are_exactly_the_planted_sites():
    assert len(SITE_KEYS) == N_SITES == 181, "the eleven files should carry 42 + 70 + 69 planted sites"
    assert sorted(DETECTS) == SITE_KEYS


def test_every_inventory_site_of_the_eleven_files_has_a_spec():
    # against the AST inventory, not against INLINE_SPECS itself: a site with no plant cannot drop out of both sides
    from regex_layer.inventory import sites
    inv = sorted(s["site"] for s in sites() if s["file"] in FILES)
    assert len(inv) == N_SITES and inv == SITE_KEYS


@pytest.mark.parametrize("site", SITE_KEYS)
def test_entry_is_well_formed(site):
    d = DETECTS[site]
    assert isinstance(d.get("text_source"), str) and d["text_source"]
    assert isinstance(d.get("lowercased"), bool)
    if d.get("detects") is None:
        assert isinstance(d.get("why_not_labellable"), str) and d["why_not_labellable"], site
        assert "trigger" not in d
    else:
        assert isinstance(d["detects"], str) and d["detects"]
        assert isinstance(d.get("trigger"), str) and d["trigger"]


@pytest.mark.parametrize("site", [k for k in SITE_KEYS if DETECTS[k].get("detects") is not None])
def test_trigger_is_a_superset_of_the_accept_plants(site):
    d = DETECTS[site]
    trig = re.compile(d["trigger"], re.I)
    plants = INLINE_SPECS[site]["plants"]["accept"]
    assert plants
    for plant in plants:
        text = plant[0]
        if d["lowercased"]:
            text = text.lower()
        assert trig.search(text), f"{site}: trigger {d['trigger']!r} misses accept plant {plant[0]!r}"
