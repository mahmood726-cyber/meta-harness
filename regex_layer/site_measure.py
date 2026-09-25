"""R2 for the regex sites outside extract.py (regex_layer/site_detects.py): precision and sampled recall of each site
against recorded, replayable labels, on the held text the site actually reads -- abstract sentences or protocol
markdown lines. A site whose text source is not a held population here (a registry paramType string, a trial id, a
derived value) is reported as NOT MEASURED with its reason, never dropped.

Classifier semantics per text: TP fires & states, FP fires & not, FN states & not fired.
"""
from __future__ import annotations

import ast
import functools
import hashlib
import importlib
import re
from pathlib import Path

from regex_layer.inventory import sites
from regex_layer.measure import held_sentences
from regex_layer.site_detects import DETECTS

ROOT = Path(__file__).resolve().parents[1]


def population_of(site: str) -> str | None:
    d = DETECTS.get(site) or {}
    if not d.get("detects"):
        return None
    src = (d.get("text_source") or "").lower()
    if src.startswith("comparator"):       # one comparator description per topic, not a population of sentences
        return None
    if "protocol markdown" in src:
        return "protocol"
    if "abstract" in src:
        return "abstract"
    return None


def not_measured_reason(site: str) -> str | None:
    d = DETECTS.get(site) or {}
    if not d.get("detects"):
        return f"NOT_LABELLABLE: {d.get('why_not_labellable')}"
    if population_of(site) is None:
        return f"TEXT_SOURCE_NOT_HELD_HERE: {d.get('text_source')}"
    return None


@functools.lru_cache(maxsize=None)
def _by_site():
    return {s["site"]: s for s in sites()}


@functools.lru_cache(maxsize=None)
def site_regex(site: str) -> re.Pattern:
    """The site's pattern exactly as the harness compiles it (a named compiled pattern from its module; an inline
    literal from the AST call at the recorded line whose first argument IS the site's literal)."""
    s = _by_site()[site]
    if s["kind"] == "compiled" and s["name"]:
        mod = importlib.import_module(f"harness.{s['file'][:-3]}")
        if isinstance(getattr(mod, s["name"], None), re.Pattern):
            return getattr(mod, s["name"])
        # a name local to a function (start_re, pattern): not a module attribute -- read the call from the AST
    # an unnamed / function-local compile or an inline literal: the re.<method> call at the recorded line
    method = "compile" if s["kind"] == "compiled" else s["kind"].split(":")[1]
    tree = ast.parse((ROOT / "harness" / s["file"]).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and getattr(node, "lineno", None) == s["line"]
                and isinstance(node.func, ast.Attribute) and node.func.attr == method
                and getattr(node.func.value, "id", "") == "re" and node.args
                and (method == "compile" or ast.unparse(node.args[0]) == s["pattern"])):
            return re.compile(_pattern_text(site, node.args[0]), call_flags(node))
    raise KeyError(site)


# where each re.<method> takes its flags positionally (pattern first); the keyword `flags=` works for all of them
_FLAGS_POS = {"compile": 1, "search": 2, "match": 2, "fullmatch": 2, "findall": 2, "finditer": 2, "split": 3,
              "sub": 4, "subn": 4}


def call_flags(node: ast.Call) -> int:
    """The flags of one re.<method>(...) call, read ONLY from its flags slot (positional or keyword): the other
    arguments can hold a nested re.<call> (hand_binding._plain nests re.sub in re.sub) whose re.<name> is not a flag
    of this pattern -- and an attribute that is not a RegexFlag is never OR-ed in."""
    pos = _FLAGS_POS[node.func.attr]
    slots = ([node.args[pos]] if len(node.args) > pos else []) + [k.value for k in node.keywords if k.arg == "flags"]
    flags = 0
    for extra in slots:
        for a in ast.walk(extra):
            if isinstance(a, ast.Attribute) and getattr(a.value, "id", "") == "re":
                v = getattr(re, a.attr, None)
                if not isinstance(v, re.RegexFlag):
                    raise ValueError(f"line {node.lineno}: re.{a.attr} in the flags slot is not a regex flag")
                flags |= v
    return flags


def _pattern_text(site: str, arg: ast.expr) -> str:
    """A literal pattern; or an f-string pattern / re.escape(<name>) compiled with the values its spec names in
    "bind" (the loop value the harness formats in). A dynamic pattern with no bind, or an unsupported placeholder, is
    refused rather than guessed."""
    is_escape = (isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == "escape"
                 and getattr(arg.func.value, "id", "") == "re" and len(arg.args) == 1 and not arg.keywords
                 and isinstance(arg.args[0], ast.Name))
    if not isinstance(arg, ast.JoinedStr) and not is_escape:
        return ast.literal_eval(arg)
    from regex_layer.specs import INLINE_SPECS
    bind = (INLINE_SPECS.get(site) or {}).get("bind")
    if not bind:
        raise KeyError(f"{site}: a dynamic pattern needs a 'bind' in its spec")
    if is_escape:
        if arg.args[0].id not in bind:
            raise KeyError(f"{site}: bind has no value for {arg.args[0].id}")
        return re.escape(str(bind[arg.args[0].id]))
    out = []
    for v in arg.values:
        if isinstance(v, ast.Constant):
            out.append(v.value)
        elif (isinstance(v, ast.FormattedValue) and isinstance(v.value, ast.Name) and v.conversion == -1
              and v.format_spec is None and v.value.id in bind):
            out.append(str(bind[v.value.id]))
        else:
            raise KeyError(f"{site}: unsupported f-string placeholder {ast.unparse(v)}")
    return "".join(out)


def _view(site: str, text: str) -> str:
    """The text as the site sees it (lowercased when the harness lowercases first)."""
    return text.lower() if DETECTS[site].get("lowercased") else text


def fires(site: str, text: str) -> bool:
    return site_regex(site).search(_view(site, text)) is not None


@functools.lru_cache(maxsize=1)
def protocol_lines() -> tuple:
    out, seen = [], set()
    for p in sorted((ROOT / "protocols").glob("*.md")):
        for k, line in enumerate(p.read_text(encoding="utf-8").splitlines()):
            line = line.strip()
            if 12 <= len(line) <= 1200 and line not in seen:   # boilerplate recurs across protocols: one item per text
                seen.add(line)
                out.append((p.name, k, line))
    return tuple(out)


@functools.lru_cache(maxsize=1)
def _abstract_sentences() -> tuple:
    seen = {}
    for slug, rid, k, s in held_sentences():
        seen.setdefault(s, (slug, rid, k))
    return tuple((s, v) for s, v in seen.items())


def candidates(per_kind: int = 15) -> list[dict]:
    out = []
    for site in sorted(DETECTS):
        pop = population_of(site)
        if pop is None:
            continue
        trig = re.compile(DETECTS[site]["trigger"], re.I)
        texts = ([(s, f"cache/{slug}/records.json#{rid} abstract sentence {k}") for s, (slug, rid, k) in _abstract_sentences()]
                 if pop == "abstract" else [(line, f"protocols/{name} line {k + 1}") for name, k, line in protocol_lines()])
        hit, near = [], []
        for t, ref in texts:
            key = hashlib.sha256(f"{site}\0{t}".encode("utf-8")).hexdigest()
            if fires(site, t):
                hit.append((key, t, ref))
            elif trig.search(t):
                near.append((key, t, ref))
        for kind, pool in (("FIRES", hit), ("TRIGGER_ONLY", near)):
            for key, t, ref in sorted(pool)[:per_kind]:
                out.append({"site": site, "sample": kind, "text": t, "held_ref": ref,
                            "held_sha256": hashlib.sha256(t.encode("utf-8")).hexdigest(),
                            "pool_sizes": {"FIRES": len(hit), "TRIGGER_ONLY": len(near)}})
    return out


def verify_site_label(claim, held_text: str, site: str) -> dict:
    out = {"task": "site_label", "site": site}
    if site not in DETECTS or not DETECTS[site].get("detects"):
        return {**out, "state": "VERIFIER_REFUSED", "problems": [f"SITE_NOT_LABELLABLE: {site!r}"]}
    if not isinstance(claim, dict) or not isinstance(claim.get("states"), bool):
        return {**out, "state": "VERIFIER_REFUSED", "problems": ["NOT_TYPED: states must be a bool"]}
    q = claim.get("quote")
    problems = []
    if claim["states"] and (not isinstance(q, str) or not q or q not in held_text):
        problems.append("SPAN_NOT_IN_SOURCE: the quote is not in the text")
    if not claim["states"] and q not in (None, ""):
        problems.append("NOT_STATED_WITH_SPAN")
    out["problems"] = problems
    out["state"] = "VERIFIER_REFUSED" if problems else "VERIFIER_PASS"
    if not problems:
        f = fires(site, held_text)
        out["regex"], out["label"] = f, claim["states"]
        out["agreement"] = "RULE_MODEL_AGREE" if f == claim["states"] else \
            f"RULE_MODEL_DISAGREE(regex={'fires' if f else 'silent'}, label={'states' if claim['states'] else 'not'}, adjudication=OWED)"
    return out


def measure(labelled: list[tuple[str, str, bool]]) -> dict:
    per = {}
    for site, text, states in labelled:
        f = fires(site, text)
        c = per.setdefault(site, {"texts": 0, "tp": 0, "fp": 0, "fn": 0, "fp_examples": [], "fn_examples": []})
        c["texts"] += 1
        c["tp"] += f and states
        c["fp"] += f and not states
        c["fn"] += states and not f
        if f and not states and len(c["fp_examples"]) < 5:
            c["fp_examples"].append(text[:300])
        if states and not f and len(c["fn_examples"]) < 5:
            c["fn_examples"].append(text[:300])
    for c in per.values():
        c["precision"] = f"{c['tp']} of {c['tp'] + c['fp']}"
        c["recall"] = f"{c['tp']} of {c['tp'] + c['fn']}"
    return per
