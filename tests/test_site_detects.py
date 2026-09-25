"""R2 labelling specs (regex_layer/site_detects.py): one per regex site of every harness file except extract.py (which
is specified and measured separately) -- the regex layer's own files and, read only, the other lane's; each labellable
trigger is a superset of the site's accept plants (it is used to sample misses)."""
from __future__ import annotations

import re

import pytest

from regex_layer import lanes

from regex_layer.site_detects import DETECTS
from regex_layer.specs import INLINE_SPECS

def _files_with_detects():
    # every harness file with a regex site, except extract.py (its 32 sites are specified and measured separately:
    # regex_layer/specs.py SPECS / INLINE_SPECS "extract.py:*" and regex_layer/measure.py)
    from regex_layer.inventory import sites
    return tuple(sorted({s["file"] for s in sites()} - {"extract.py"}))


FILES = _files_with_detects()
# regex-layer files 42 + other lane: batch 1 70, batch 2 69, batch 3 56, batch 4 59, batch 5 71
N_SITES = 42 + 70 + 69 + 56 + 59 + 71 + 8 - 6 + 1   # + harness/whole_numbers.py (R4); V1.1 (lane OC): the six `<[^>]+>` source-text strippers
                                                     # removed (absence/_TAG, cites/_TAG_RE, reason_audit/_TAG, registry_multi, 2x hand_binding)
                                                     # and harness/markup.py:MARKUP added, with plants that REFUSE a literal 'P<0.001'
SITE_KEYS = sorted(k for k in INLINE_SPECS if k.split(":", 1)[0] in FILES)


def test_keys_are_exactly_the_planted_sites():
    assert len(FILES) >= 50, "the inventory found too few files -- the key set would be vacuous"
    assert len(SITE_KEYS) == N_SITES == 370, "every non-extract.py site planted in this landing carries a labelling spec"
    assert sorted(DETECTS) == SITE_KEYS


def test_every_inventory_site_of_the_OWNED_files_has_a_spec():
    # strict only where this lane owns the file (regex_layer/lanes.py): a new or changed site in the OTHER lane's files is
    # reported (plants skipped as STALE, new sites listed by regex_layer.inventory), never a failure of that lane's commit
    from regex_layer.inventory import sites
    inv = sorted(s["site"] for s in sites() if s["file"] in FILES and lanes.owned(s["site"]))
    assert inv and inv == sorted(k for k in SITE_KEYS if lanes.owned(k))


def test_other_lanes_new_sites_are_reported_not_refused():
    from regex_layer.inventory import sites
    new = sorted(s["site"] for s in sites() if s["file"] in FILES and not lanes.owned(s["site"]) and s["site"] not in DETECTS)
    stale = sorted(k for k in SITE_KEYS if lanes.stale_reason(k))
    print(f"other lanes: {len(new)} new unplanted site(s), {len(stale)} stale plant(s)")      # information, not a gate


@pytest.mark.parametrize("site", SITE_KEYS)
def test_entry_is_well_formed(site):
    if lanes.stale_reason(site):
        pytest.skip(lanes.stale_reason(site))
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
    if lanes.stale_reason(site):
        pytest.skip(lanes.stale_reason(site))
    d = DETECTS[site]
    trig = re.compile(d["trigger"], re.I)
    plants = INLINE_SPECS[site]["plants"]["accept"]
    assert plants
    for plant in plants:
        text = plant[0]
        if d["lowercased"]:
            text = text.lower()
        assert trig.search(text), f"{site}: trigger {d['trigger']!r} misses accept plant {plant[0]!r}"
