"""R3 -- a named plant per pattern in harness/extract.py, and proof that each plant can fire.

For every compiled pattern (enumerated from the source by AST, so a pattern added without a spec fails here):
  accept plants   the pattern must match and yield exactly the stated groups;
  refuse plants   the pattern must NOT match;
  mutation        a permissive mutant (matches anything) and a dead mutant (matches nothing) are run through the SAME
                  assertions -- at least one assertion must fail for each, or the plants prove nothing.
A plant the CURRENT pattern gets wrong is a located defect: it is listed in KNOWN_DEFECTS with its reason and runs as
a strict xfail, so a fix flips it to a pass (and must remove the entry) and a regression cannot hide.
"""
from __future__ import annotations

import ast
import functools
import re
from pathlib import Path

import pytest

from harness import extract
from regex_layer.specs import SPECS

ROOT = Path(__file__).resolve().parents[1]

from regex_layer.defects import KNOWN_DEFECTS  # noqa: E402  (located defects: strict xfails)


def compiled_names(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            f = node.value.func
            if isinstance(f, ast.Attribute) and f.attr == "compile" and getattr(f.value, "id", "") == "re":
                out += [t.id for t in node.targets if isinstance(t, ast.Name)]
    return out


def test_every_compiled_pattern_has_a_spec_and_plants():
    names = compiled_names(ROOT / "harness" / "extract.py")
    assert len(names) >= 20, "the AST walk found too few patterns -- it would pass vacuously"
    assert sorted(set(names) - set(SPECS)) == [], "a compiled pattern with no spec/plant: add one to regex_layer/specs.py"
    assert sorted(set(SPECS) - set(names)) == [], "a spec for a pattern that no longer exists: remove it"
    for n in names:
        p = SPECS[n]["plants"]
        assert p.get("accept") and p.get("refuse"), f"{n} needs at least one accept AND one refuse plant"


def _cases():
    for name, spec in SPECS.items():
        for i, acc in enumerate(spec["plants"]["accept"]):
            yield pytest.param(name, "accept", acc, id=f"{name}-accept-{i}")
        for i, ref in enumerate(spec["plants"]["refuse"]):
            yield pytest.param(name, "refuse", ref, id=f"{name}-refuse-{i}")


def check(rx, kind, spec_kind, plant) -> None:
    """The assertion every plant is held to (shared with the mutation test)."""
    if kind == "accept":
        text, groups = (plant if spec_kind == "extractor" else (plant, None))
        m = rx.search(extract._norm(text))
        assert m is not None, f"did not match {text!r}"
        if groups is not None:
            assert m.groups() == tuple(groups), f"{text!r}: groups {m.groups()} != {tuple(groups)}"
    else:
        assert rx.search(extract._norm(plant)) is None, f"matched {plant!r}"


@pytest.mark.parametrize("name,kind,plant", list(_cases()))
def test_plant(name, kind, plant, request):
    pid = request.node.callspec.id
    if pid in KNOWN_DEFECTS:
        request.applymarker(pytest.mark.xfail(reason=KNOWN_DEFECTS[pid], strict=True))
    check(getattr(extract, name), kind, SPECS[name]["kind"], plant)


@pytest.mark.parametrize("name", sorted(SPECS))
def test_each_patterns_plants_can_fire(name):
    """A permissive mutant and a dead mutant must each FAIL at least one of this pattern's plants."""
    spec = SPECS[name]
    groups_n = max((len(g) for _, g in spec["plants"]["accept"]), default=0) if spec["kind"] == "extractor" else 0
    permissive = re.compile("(.?)" * groups_n + r"[\s\S]*")
    dead = re.compile(r"(?!)")
    for mutant in (permissive, dead):
        failed = 0
        for kind in ("accept", "refuse"):
            for plant in spec["plants"][kind]:
                try:
                    check(mutant, kind, spec["kind"], plant)
                except AssertionError:
                    failed += 1
        assert failed > 0, f"{name}: the plants did not catch the {'permissive' if mutant is permissive else 'dead'} mutant"


def _readers(name: str) -> list[str]:
    """Lines in harness/*.py that use `name` from extract.py (its own definition and same-named private copies in other
    modules excluded)."""
    out = []
    for p in sorted((ROOT / "harness").glob("*.py")):
        src = p.read_text(encoding="utf-8")
        local = re.search(rf"^{re.escape(name)}\s*=", src, re.M) is not None
        for k, line in enumerate(src.splitlines(), 1):
            if re.search(rf"\b{re.escape(name)}\b", line) and not re.match(rf"\s*{re.escape(name)}\s*=", line) \
                    and not line.lstrip().startswith("#"):
                if p.name == "extract.py" or (not local and ("extract" in src)):
                    out.append(f"{p.name}:{k}")
    return out


@pytest.mark.parametrize("name", sorted(SPECS))
def test_role_matches_the_source(name):
    from regex_layer.specs import ROLES
    readers = _readers(name)
    role = ROLES[name]
    if role == "dead":
        assert readers == [], f"{name} is marked dead but is read at {readers}"
    else:
        assert readers, f"{name} is marked {role} but nothing in harness/ reads it"
    if role.startswith("conjunct:"):
        other = role.split(":", 1)[1]
        lines = (ROOT / "harness" / "extract.py").read_text(encoding="utf-8").splitlines()
        uses = [lines[int(r.split(":")[1]) - 1] for r in readers if r.startswith("extract.py")]
        assert uses and all(other in u for u in uses), f"{name} is read without {other}: {uses}"


@functools.lru_cache(maxsize=None)
def _sites_and_tree(fname: str):
    from regex_layer.inventory import sites
    return ({x["site"]: x for x in sites() if x["file"] == fname},
            ast.parse((ROOT / "harness" / fname).read_text(encoding="utf-8")))


def _inline_pattern(site: str):
    """The compiled pattern (with its flags) of a site, read from its harness file: a named compiled pattern from the
    module itself, an inline literal from the AST at the recorded line."""
    import importlib
    fname = site.split(":", 1)[0]
    by_site, tree = _sites_and_tree(fname)
    s = by_site[site]
    if s["kind"] == "compiled":
        return getattr(importlib.import_module(f"harness.{fname[:-3]}"), s["name"])
    for node in ast.walk(tree):
        # same predicate as regex_layer.inventory (a re.<method> call whose first arg IS this site's literal): a line can
        # carry a compiled pattern's .search(x) or a second inline re.search, and ast.walk order would pick the wrong one
        if (isinstance(node, ast.Call) and getattr(node, "lineno", None) == s["line"]
                and isinstance(node.func, ast.Attribute) and node.func.attr == s["kind"].split(":")[1]
                and getattr(node.func.value, "id", "") == "re" and node.args
                and ast.unparse(node.args[0]) == s["pattern"]):
            pat = ast.literal_eval(node.args[0])
            flags = 0
            for extra in list(node.args[2:]) + [k.value for k in node.keywords if k.arg == "flags"]:
                for a in ast.walk(extra):
                    if isinstance(a, ast.Attribute) and getattr(a.value, "id", "") == "re":
                        flags |= getattr(re, a.attr)
            return re.compile(pat, flags)
    raise AssertionError(f"{site}: not found at line {s['line']}")


def _inline_cases():
    from regex_layer.specs import INLINE_SPECS
    for site, spec in INLINE_SPECS.items():
        for i, acc in enumerate(spec["plants"]["accept"]):
            yield pytest.param(site, "accept", acc, id=f"{site}-accept-{i}")
        for i, ref in enumerate(spec["plants"]["refuse"]):
            yield pytest.param(site, "refuse", ref, id=f"{site}-refuse-{i}")


@pytest.mark.parametrize("site,kind,plant", list(_inline_cases()))
def test_inline_plant(site, kind, plant, request):
    from regex_layer.specs import INLINE_SPECS
    pid = request.node.callspec.id
    if pid in KNOWN_DEFECTS:
        request.applymarker(pytest.mark.xfail(reason=KNOWN_DEFECTS[pid], strict=True))
    rx, spec = _inline_pattern(site), INLINE_SPECS[site]
    if spec["kind"] == "split":
        if kind == "accept":
            text, parts = plant
            assert rx.split(text) == parts, rx.split(text)
        else:
            assert rx.split(plant) == [plant], f"split {plant!r}"
    else:
        if kind == "accept":
            text, groups = plant
            m = rx.search(text)
            assert m is not None, f"did not match {text!r}"
            if groups is not None:
                assert m.groups() == tuple(groups), m.groups()
        else:
            assert rx.search(plant) is None, f"matched {plant!r}"


@pytest.mark.parametrize("site", sorted(__import__("regex_layer.specs", fromlist=["x"]).INLINE_SPECS))
def test_each_inline_sites_plants_can_fire(site):
    """A dead mutant (never matches / never splits) and a permissive one (matches anything / splits everywhere) must
    each fail at least one plant of the site."""
    from regex_layer.specs import INLINE_SPECS
    spec = INLINE_SPECS[site]
    groups_n = max((len(g) for _, g in spec["plants"]["accept"] if isinstance(g, tuple)), default=0)
    mutants = {"dead": re.compile(r"(?!)"), "permissive": re.compile("(.?)" * groups_n + r"[\s\S]*" if spec["kind"] == "search"
                                                                      else r"\s*")}
    for label, mutant in mutants.items():
        failed = 0
        for kind in ("accept", "refuse"):
            for plant in spec["plants"][kind]:
                try:
                    if spec["kind"] == "split":
                        if kind == "accept":
                            assert mutant.split(plant[0]) == plant[1]
                        else:
                            assert mutant.split(plant) == [plant]
                    else:
                        if kind == "accept":
                            m = mutant.search(plant[0])
                            assert m is not None and (plant[1] is None or m.groups() == tuple(plant[1]))
                        else:
                            assert mutant.search(plant) is None
                except AssertionError:
                    failed += 1
        assert failed > 0, f"{site}: the plants did not catch the {label} mutant"
