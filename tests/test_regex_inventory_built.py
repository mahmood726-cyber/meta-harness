"""The inventory must count a regex whose pattern is BUILT at run time (concatenation, re.escape, a variable), not only
literal ones. Before this, `regex_layer.inventory.sites` skipped them silently, so "407 of 407 sites planted" was true of
the literal sites only while 19 built sites in harness/ were neither counted nor planted (pva, RAI-C13 / PVA-D12).
Plant: fired on the old inventory (the built sites were absent)."""
from pathlib import Path

from regex_layer.inventory import sites

SRC = '''import re
def present(text, x):
    return re.search(r"(?<![\\d.])" + re.escape(x) + r"(?![\\d])", text)
def escaped(text, term):
    return re.search(re.escape(term), text)
def via_variable(text, pat):
    return re.search(pat, text)
def literal(text):
    return re.search(r"\\d+", text)
'''


def _tree(tmp_path: Path) -> Path:
    (tmp_path / "harness").mkdir()
    (tmp_path / "harness" / "m.py").write_text(SRC, encoding="utf-8")
    return tmp_path


def test_built_patterns_are_counted_as_sites(tmp_path):
    got = sites(_tree(tmp_path))
    kinds = sorted(s["kind"] for s in got)
    assert kinds == ["built:search", "built:search", "built:search", "inline:search"], kinds


def test_a_built_site_is_keyed_by_its_expression_and_names_its_function(tmp_path):
    got = {s["name"]: s for s in sites(_tree(tmp_path)) if s["kind"].startswith("built:")}
    assert set(got) == {"present", "escaped", "via_variable"}
    assert all(s["site"].startswith("m.py:search:built:") for s in got.values())
    assert "re.escape(x)" in got["present"]["pattern"]


def test_the_literal_site_key_is_unchanged(tmp_path):
    lit = [s for s in sites(_tree(tmp_path)) if s["kind"] == "inline:search"]
    assert len(lit) == 1 and lit[0]["site"].startswith("m.py:search:") and ":built:" not in lit[0]["site"]
