"""The regex-site ratchet (regex_layer.inventory): coverage is counted against every regex site the AST finds, and in the
files the regex layer owns the list of sites without a plant can only shrink."""
from __future__ import annotations

import json
from pathlib import Path

from regex_layer.inventory import planted, sites

ROOT = Path(__file__).resolve().parents[1]
DEBT = json.loads((ROOT / "regex_layer" / "sites_without_plants.json").read_text(encoding="utf-8"))


def test_the_inventory_finds_compiled_and_inline_sites(tmp_path):
    # plant: a tree with one named compile, one unnamed compile and one inline literal -> exactly three sites
    (tmp_path / "harness").mkdir()
    (tmp_path / "harness" / "m.py").write_text(
        "import re\nA = re.compile(r'a')\nx = [re.compile('b')]\ndef f(s):\n    return re.search(r'c+', s)\n"
        "def g(s):\n    return re.search(r'c+', s)\n", encoding="utf-8")
    got = sorted(s["site"] for s in sites(tmp_path))
    assert len(got) == 4 and "m.py:A" in got and "m.py:L3" in got
    assert sum(g.startswith("m.py:search:") for g in got) == 2 and any(g.endswith("#2") for g in got)


def test_every_planted_site_exists():
    have = {s["site"] for s in sites()}
    assert planted() <= have, sorted(planted() - have)


def test_owned_sites_without_plants_only_shrink():
    owned = set(DEBT["owned_files"])
    have = planted()
    now = {s["site"] for s in sites() if s["file"] in owned and s["site"] not in have}
    debt = set(DEBT["sites"])
    assert sorted(now - debt) == [], "a new regex site without a plant in a regex-layer file: add plants (regex_layer/specs.py)"
    assert sorted(debt - now) == [], "a listed site gained a plant or no longer exists: remove it from sites_without_plants.json"
    assert DEBT["n"] == len(debt)
