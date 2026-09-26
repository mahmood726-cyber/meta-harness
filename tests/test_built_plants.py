"""Plants for regex sites whose pattern is built at run time (regex_layer/specs_built.py): each calls the harness
function that builds and uses the pattern and asserts its result. A plant in a site's "defects" is a located defect and
runs as a strict xfail. A site whose code moved away (a lane's edit re-keyed it) is skipped as STALE, as for literal
sites (regex_layer.lanes)."""
from __future__ import annotations

import importlib
import re

import pytest

from regex_layer.inventory import sites
from regex_layer.specs_built import BUILT_SPECS

SITES = {s["site"]: s for s in sites()}


def _call(dotted):
    mod, fn = dotted.rsplit(".", 1)
    return getattr(importlib.import_module(mod), fn)


def _normal(v):
    return "MATCH" if isinstance(v, re.Match) else v


def _cases():
    for site, spec in BUILT_SPECS.items():
        for kind in ("accept", "refuse"):
            for i, (args, expected) in enumerate(spec["plants"][kind]):
                yield pytest.param(site, kind, i, args, expected, id=f"{site}-{kind}-{i}")


@pytest.mark.parametrize("site,kind,i,args,expected", list(_cases()))
def test_built_plant(site, kind, i, args, expected, request):
    if site not in SITES:
        pytest.skip(f"STALE: {site} is no longer in the inventory (its expression changed)")
    spec = BUILT_SPECS[site]
    reason = spec.get("defects", {}).get(f"{kind}-{i}")
    if reason:
        request.applymarker(pytest.mark.xfail(reason=reason, strict=True))
    got = _normal(_call(spec["call"])(*args))
    assert got == expected, f"{spec['call']}{args!r} -> {got!r}, expected {expected!r}"


@pytest.mark.parametrize("site", sorted(BUILT_SPECS))
def test_each_built_site_has_a_discriminating_plant_pair(site):
    """At least one accept and one refuse, with different expected results -- a plant set that cannot tell the site
    working from the site broken is not a plant."""
    p = BUILT_SPECS[site]["plants"]
    assert p["accept"] and p["refuse"]
    assert {repr(e) for _, e in p["accept"]}.isdisjoint({repr(e) for _, e in p["refuse"]})


@pytest.mark.parametrize("site", sorted(BUILT_SPECS))
def test_each_built_spec_names_the_function_the_inventory_found(site):
    if site not in SITES:
        pytest.skip(f"STALE: {site}")
    assert BUILT_SPECS[site]["call"].rsplit(".", 1)[1] == SITES[site]["name"], (BUILT_SPECS[site]["call"], SITES[site])
