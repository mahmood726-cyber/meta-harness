"""The landing hash check certified increment 2 (237e9094 -> 75cc9a46, 2026-09-18) as "32 MOVED ... PASS" while
review_sha256 was identical on 32 of 32 reviews: it read html movement (the wrapper) as content movement (the object)
-- a container property read as a contents property, the very defect the check exists to catch. Found by Dispatch on a
no-store fetch of the served page and confirmed by the parallel workshop (ws/HASHGATE).

Requirement: the verdict per review is decided by review_sha256, named old -> new. A landing that moves only the html
is WRAPPER_ONLY and refused unless declared by name (--allow-wrapper-only SLUG); a touched review whose object and html
are both unchanged is refused; --require-change SLUG refuses unless that review's OBJECT moved. Plant: on the
pre-fix script the wrapper-only landing passes.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("landing_hash_check", ROOT / "scripts" / "landing_hash_check.py")
lhc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lhc)

PREV = {"review_sha256": "98726cc125e9fcc7" + "0" * 48, "html_sha256": "fede8d293caffb87" + "0" * 48}
WRAPPER_MOVED = {"review_sha256": PREV["review_sha256"], "html_sha256": "72fadf2610a71a9e" + "0" * 48}
OBJECT_MOVED = {"review_sha256": "a0cb837ea87ffea4" + "0" * 48, "html_sha256": "1c7145bac54e2f26" + "0" * 48}


def _manifests(table):
    return lambda ref, slug: table[ref][slug]


def test_wrapper_only_landing_is_refused_and_named():
    table = {"prev": {"glp1-ra-mace-t2d": PREV}, "new": {"glp1-ra-mace-t2d": WRAPPER_MOVED}}
    ok, lines, refusals = lhc.check("prev", "new", ["glp1-ra-mace-t2d"], _manifests(table))
    assert ok is False, lines
    assert any("WRAPPER_ONLY" in line for line in lines), lines
    assert any("98726cc125e9fcc7" in r and "unchanged" in r for r in refusals), refusals


def test_wrapper_only_landing_passes_only_when_declared_by_name():
    table = {"prev": {"glp1-ra-mace-t2d": PREV}, "new": {"glp1-ra-mace-t2d": WRAPPER_MOVED}}
    ok, lines, _ = lhc.check("prev", "new", ["glp1-ra-mace-t2d"], _manifests(table), allowed=["glp1-ra-mace-t2d"])
    assert ok is True
    assert any("WRAPPER_ONLY (declared)" in line for line in lines), lines


def test_object_moved_landing_names_old_and_new_and_passes():
    table = {"prev": {"glp1-ra-mace-t2d": PREV}, "new": {"glp1-ra-mace-t2d": OBJECT_MOVED}}
    ok, lines, _ = lhc.check("prev", "new", ["glp1-ra-mace-t2d"], _manifests(table), required=["glp1-ra-mace-t2d"])
    assert ok is True
    assert any("98726cc125e9fcc7 -> a0cb837ea87ffea4" in line and "OBJECT_MOVED" in line for line in lines), lines


def test_required_review_whose_object_did_not_move_is_refused_even_if_touched():
    table = {"prev": {"glp1-ra-mace-t2d": PREV}, "new": {"glp1-ra-mace-t2d": WRAPPER_MOVED}}
    ok, _, refusals = lhc.check("prev", "new", ["glp1-ra-mace-t2d"], _manifests(table),
                                required=["glp1-ra-mace-t2d"], allowed=["glp1-ra-mace-t2d"])
    assert ok is False
    assert any("REQUIRED" in r and "98726cc125e9fcc7" in r for r in refusals), refusals


def test_touched_but_unchanged_review_is_refused():
    table = {"prev": {"omega3-cardiovascular-events": PREV}, "new": {"omega3-cardiovascular-events": PREV}}
    ok, _, refusals = lhc.check("prev", "new", ["omega3-cardiovascular-events"], _manifests(table))
    assert ok is False and refusals
