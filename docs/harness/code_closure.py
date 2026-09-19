"""Static import closure of the code that decides a page: the set of in-tree Python
modules reachable, by `import` statements at any nesting depth, from named roots.

The certificate pins Git blob identities of the analysis code. A hand-written list
drifted from the code that actually computes verdicts (the endpoint binder, the
publication gate, the canonicalizer and the certificate builder itself were all
absent). This module derives the list from the source, so a module that a root
imports -- module-level or inside a function -- cannot be left unpinned by omission.

Resolution is syntactic (ast), never by executing the code. Only modules that
resolve to a file inside the repository (harness/, scripts/) are members; the
standard library and third-party packages are outside the map by construction
and are named as such in the certificate's scope statement.
"""
from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ("harness", "scripts")


def _module_path(root, dotted):
    """Repo-relative POSIX path of an in-tree module, or None."""
    parts = dotted.split(".")
    if parts[0] not in PACKAGES:
        return None
    candidate = root.joinpath(*parts).with_suffix(".py")
    if candidate.is_file():
        return candidate.relative_to(root).as_posix()
    package_init = root.joinpath(*parts, "__init__.py")
    if package_init.is_file():
        return package_init.relative_to(root).as_posix()
    return None


def _direct_imports(root, ref):
    """Repo-relative paths of in-tree modules imported anywhere in one file."""
    path = root / ref
    tree = ast.parse(path.read_bytes(), filename=ref)
    package = ref.rsplit("/", 1)[0].replace("/", ".") if "/" in ref else ""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                target = _module_path(root, alias.name)
                if target:
                    found.add(target)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = package.split(".") if package else []
                base_parts = base_parts[: len(base_parts) - (node.level - 1)]
                base = ".".join(p for p in base_parts + (node.module or "").split(".") if p)
            else:
                base = node.module or ""
            if not base:
                continue
            target = _module_path(root, base)
            if target:
                found.add(target)
            # `from .pkg import submodule` names a module, not an attribute.
            for alias in node.names:
                sub = _module_path(root, base + "." + alias.name)
                if sub:
                    found.add(sub)
    return found


def closure(roots, root=None):
    """Sorted repo-relative paths of every in-tree module reachable from `roots`.

    Roots that do not exist are skipped: the caller states them and the
    certificate marks them NOT_PRESENT so the omission is visible, not silent.
    """
    root = Path(root or ROOT)
    pending = [r for r in roots if (root / r).is_file()]
    seen = set()
    while pending:
        ref = pending.pop()
        if ref in seen:
            continue
        seen.add(ref)
        pending.extend(_direct_imports(root, ref) - seen)
    return sorted(seen)


@lru_cache(maxsize=None)
def cached_closure(roots, root=None):
    return tuple(closure(roots, root))
