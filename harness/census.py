"""Reproduction census.

Two-level design:

  Level A (always): fresh-clone integrity + determinism.
    From the committed review.json alone, re-derive review_sha256 (over the core)
    and re-render the page; both must byte-match the committed manifest hashes and
    the committed index.html. This catches non-determinism and ANY hand-edit of the
    served HTML or the review data after the census ran.

  Level B (attaches when a topic pipeline exists): offline replay.
    Re-run fetch(from committed cache) -> screen -> extract -> synthesise and confirm
    the regenerated review core matches the committed one. Recorded as from_cache.

build_review_dir() writes a review directory with page + manifest + REPRODUCTION.json.
verify() performs Level A against an on-disk directory (this is what a fresh clone runs).
"""
from __future__ import annotations
import json
import os
from typing import Callable, Optional

from .canonical import canonical_json, review_core, review_sha256, sha256_text
from .page import render_page
from . import page
from . import registration
from . import claim
from . import claimgraph
from . import compat
from . import membership
from . import proposition
from . import propositions
from . import parity_relation
from .synth import CI_PROVENANCE

# Provenances a RENDERED interval may legitimately carry: the canonical engine token, or a single
# trial's own reported CI printed verbatim at k=1 (not a pool). Anything else is an inference-layer
# bypass and the build refuses it.
_VALID_CI_PROVENANCE = {CI_PROVENANCE, "source-reported-CI:k=1-verbatim"}


def _interval_provenance_check(core: dict) -> list:
    """Return a list of (outcome, provenance) for every rendered CI whose provenance token is not
    engine-certified. Empty on a well-formed corpus."""
    bad = []
    for o in (core.get("outcomes") or []):
        res = o.get("result") or {}
        if res.get("suppressed_incompatible"):
            continue
        if res.get("ci_low") is None or res.get("ci_high") is None:
            continue
        if res.get("ci_provenance") not in _VALID_CI_PROVENANCE:
            bad.append({"outcome": o.get("name"), "ci_provenance": res.get("ci_provenance")})
    return bad


def _claim_check(review_core_obj: dict):
    """Cross-surface significance-contradiction scan for the canonical claim object.

    For every outcome whose canonical claim is PRESENT, the scan reads THAT outcome's own
    rendered block (the exact bytes shown for it) and checks it does not ASSERT a significance
    opposite to the object -- a card saying 'significantly reduced' over an interval that spans
    no effect (the card<->object mismatch class). The PRIMARY claim is additionally scanned
    against the overview and manuscript, the headline surfaces that make a significance claim
    about it. Scoping to each outcome's own bytes is essential: scanning the whole page for one
    outcome would attribute a (correct) 'not significant' about a harm to a significant primary
    (the 'search the same bytes you showed' rule). Pure function of the core, so census (build)
    and reproduce_review (replay) produce it identically. The build FAILS closed on any
    contradiction."""
    core = dict(review_core_obj)
    core.pop("reproduction", None)
    checked = 0
    contradictions = []
    for o in core.get("outcomes", []):
        res = o.get("result")
        if not isinstance(res, dict):
            continue
        cl = res.get("claim") or claim.derive(res)
        if not cl.get("present"):
            continue
        checked += 1
        surfaces = {}
        try:
            surfaces["outcome block"] = page.render_outcome_block(o)
        except Exception:
            pass
        if o.get("primary"):
            for name, fn in (("overview", page.render_overview), ("manuscript", page.render_manuscript)):
                try:
                    surfaces[name] = fn(core)
                except Exception:
                    pass
        for c in claim.significance_contradictions(cl, surfaces):
            contradictions.append({"outcome": o.get("name"), **c})
    scope_counts = claimgraph.scope_counts(core, checked)
    surfaces = ["outcome block", "overview", "manuscript"]
    checked_total = checked + scope_counts.get("strand_pool", 0)
    scope = {
        "counts": scope_counts,
        "surfaces_checked": surfaces,
        "not_in_scope": ["verbatim source quotations", "external comparator prose"],
    }
    return {"claims_checked": checked_total, "surfaces": surfaces,
            "scope_counts": scope_counts, "scope": scope,
            "contradictions": contradictions}


def _parity_row(root: str, slug: str, review_core_obj: Optional[dict] = None):
    """This topic's row from the committed docs/parity.json (a measurement snapshot), or None.
    Shared by census (build) and reproduce_review (replay) so the reproduction block byte-matches."""
    if not slug:
        return None
    row = parity_relation.load_parity_row(root, slug)
    if row:
        return parity_relation.enrich(row, review_core_obj)
    return None


def _dual_row(root: str, slug: str):
    """This topic's independent-second-extraction tally from committed docs/dual_extract.json, or
    None. A blind second extractor located each pooled number's digits from the abstract; agree =
    same 2x2, reconcile = same result via a different statistic (effect vs counts / RRR), conflict =
    a genuine numeric disagreement, not_checkable = the number is not in the abstract. Two independent
    extractions agreeing is a claim no published meta makes about its own numbers. Outside the core
    hash; shared by census + reproduce_review so replay byte-matches."""
    p = os.path.join(root, "docs", "dual_extract.json")
    if not slug or not os.path.exists(p):
        return None
    try:
        return (json.load(open(p, encoding="utf-8")) or {}).get(slug)
    except (ValueError, OSError):
        return None


def _refusals_rows(root: str, slug: str):
    """This topic's notable VERIFIED-BUT-NOT-POOLED refusals from committed docs/refusals.json, or
    None. Makes the honest 'we found this trial, verified its numbers, and still did not pool it,
    because ...' visible on the page — a stronger statement than a larger k. Outside the core hash;
    shared by census + reproduce_review so replay byte-matches."""
    p = os.path.join(root, "docs", "refusals.json")
    if not slug or not os.path.exists(p):
        return None
    try:
        return (json.load(open(p, encoding="utf-8")) or {}).get(slug)
    except (ValueError, OSError):
        return None


def build_review_dir(
    review_core_obj: dict,
    manifest_meta: dict,
    out_dir: str,
    protocol_sha: str,
    from_cache: bool = False,
    certify: bool = False,
) -> dict:
    """Assemble a publishable review directory. Returns the manifest dict."""
    os.makedirs(out_dir, exist_ok=True)
    review_core_obj = propositions.attach(review_core_obj)
    core_sha = review_sha256(review_core_obj)  # excludes 'reproduction' by construction

    # Level A self-check while building: rendering the core twice is byte-stable.
    core_review = dict(review_core_obj)
    core_review.pop("reproduction", None)
    h1 = render_page(core_review)
    h2 = render_page(json.loads(canonical_json(core_review)))
    failures = 0
    checks = []
    det_ok = (h1 == h2)
    checks.append({"check": "render is deterministic", "ok": det_ok})
    if not det_ok:
        failures += 1

    reproduction = {
        "failures": failures,
        "protocol_sha": protocol_sha,
        "review_sha256": core_sha,
        "from_cache": from_cache,
    }
    # PREREGISTRATION vs BUILD (P0, audit 20): the displayed protocol SHA is usually a BUILD commit
    # (protocol + cache + synthesis + page together), which cannot demonstrate the protocol PRECEDED
    # synthesis. Resolve a genuine protocol-only prospective-registration commit if one exists, else
    # record prospective=False honestly. Lives in the reproduction block (outside the core hash).
    _slug = manifest_meta.get("slug")
    if _slug:
        reproduction["preregistration"] = registration.preregistration_sha(_slug)
    # Re-search diff (item 1): committed, outside the core hash by living in 'reproduction', so it can
    # never affect the analysis sha or replay. Present only where scripts/research_diff.py has run.
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _rd = os.path.join(_root, "cache", manifest_meta.get("slug", ""), "research_diff.json")
    if os.path.exists(_rd):
        try:
            reproduction["research_diff"] = json.load(open(_rd, encoding="utf-8"))
        except (ValueError, OSError):
            pass
    # Parity snapshot (docs/parity.json): this topic's row, outside the core hash. Rendered so a
    # reader sees our k vs the comparable comparator k on the page itself, not only on the index.
    _pa = membership.annotate_parity(_parity_row(_root, manifest_meta.get("slug", ""), review_core_obj), review_core_obj)
    if _pa:
        reproduction["parity"] = _pa
    _rf = _refusals_rows(_root, manifest_meta.get("slug", ""))
    if _rf:
        reproduction["refusals"] = _rf
    _du = _dual_row(_root, manifest_meta.get("slug", ""))
    if _du:
        reproduction["dual"] = _du
    # CANONICAL-CLAIM cross-surface contradiction gate: every surface must derive its significance
    # wording from the one claim object. Fail closed if any rendered surface asserts the opposite.
    _cc = _claim_check(review_core_obj)
    reproduction["claim_check"] = _cc
    if _cc["contradictions"]:
        raise ValueError(
            "CLAIM-OBJECT CONTRADICTION (build refused): a rendered surface asserts a significance "
            "opposite to the canonical claim object -> " + json.dumps(_cc["contradictions"]))
    # SEVENTH GATE — categorical/membership + methodological proposition contradictions (the two families
    # a significance check cannot see: a trial BOTH pooled and declared-absent, a suppressed pool that
    # still renders an estimate, a record BOTH eligible and excluded, a current-headline claim on an
    # invalidated topic, a preregistration-precedence claim it cannot support). Object-derived; fail closed.
    _pbad = proposition.contradictions(review_core_obj)
    _prop_doc = propositions.check_document(review_core_obj)
    _pbad = _pbad + (_prop_doc.get("contradictions") or [])
    reproduction["proposition_check"] = {
        "checked": True,
        "contradictions": _pbad,
        "legacy_contradictions": proposition.contradictions(review_core_obj),
        "scope_counts": _prop_doc.get("scope_counts") or {},
        "scope": _prop_doc.get("scope") or {},
    }
    if _pbad:
        raise ValueError("PROPOSITION CONTRADICTION (build refused): a categorical/membership or "
                         "methodological proposition and its negation are asserted at once -> " + json.dumps(_pbad))
    reproduction = claimgraph.prepare_reproduction(review_core_obj, reproduction)
    _cgbad = claimgraph.check({**review_core_obj, "reproduction": reproduction})
    reproduction["claimgraph_check"] = {"violations": _cgbad,
                                        "disputes": claimgraph.disputes({**review_core_obj, "reproduction": reproduction})}
    if _cgbad:
        raise ValueError("CLAIMGRAPH CONTRADICTION (build refused): " + json.dumps(_cgbad))
    # COMPATIBILITY-KEY backstop: refuse a rendered pool whose trials do not share the hard
    # dimensions (an incompatible effect-measure class inside a pool). Defense in depth -- the
    # upstream guards already suppress these, so this passes on a well-formed corpus and fires
    # only on a regression that bypassed a guard.
    _cbad = compat.check(review_core_obj)
    if _cbad:
        raise ValueError("COMPATIBILITY-KEY MISMATCH (build refused): a pooled outcome mixes "
                         "incompatible quantities -> " + json.dumps(_cbad))
    # INTERVAL-PROVENANCE gate (INFERENCE_LAYER_BYPASS): every RENDERED confidence interval must carry
    # a token proving it came from the canonical PM/HKSJ engine (synth.pool) or is a single trial's own
    # reported CI (k=1 verbatim). A hand-rolled interval -- the iv-iron strand builder's z-interval,
    # right number, wrong origin -- has no valid token and is refused here. A check on the NUMBER cannot
    # catch this; only a check on the interval's PROVENANCE can.
    _ipbad = _interval_provenance_check(review_core_obj)
    if _ipbad:
        raise ValueError("INTERVAL-PROVENANCE (build refused): a rendered CI is not stamped by the "
                         "canonical engine (INFERENCE_LAYER_BYPASS) -> " + json.dumps(_ipbad))
    final_review = dict(review_core_obj)
    final_review["reproduction"] = reproduction
    if certify:
        from . import certificate
        cert = certificate.compute(manifest_meta["slug"], final_review, protocol_sha)
        reproduction["certificate"] = cert
        with open(os.path.join(out_dir, "CERTIFICATE.json"), "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(cert, ensure_ascii=False, indent=2) + "\n")
    html = render_page(final_review)
    html_sha = sha256_text(html)

    manifest = {
        "slug": manifest_meta["slug"],
        "title": review_core_obj.get("title"),
        "declared_method": manifest_meta["declared_method"],
        "served_method": manifest_meta["served_method"],
        "protocol_sha": protocol_sha,
        "generator": manifest_meta.get("generator", "harness"),
        "review_sha256": core_sha,
        "html_sha256": html_sha,
        "comparator": manifest_meta.get("comparator"),
        "build_utc": manifest_meta.get("build_utc"),
    }

    # RoB gate: every rendered verdict must resolve to the canonical object (a bare judgement word in a verdict
    # position, or a cell with no binding, refuses the page -- the served page carried 48 unresolved cells)
    from . import rob2 as _rob2
    _rob_violations = _rob2.verify_rendered_verdicts(html, review_core_obj.get("rob2") or {})
    if _rob_violations:
        raise ValueError("ROB_VERDICT_UNRESOLVED: " + "; ".join(
            f"{v['trial']}#{v['cell']} {v['code']}: {v['detail']}" for v in _rob_violations[:5]) + f" ({len(_rob_violations)} total)")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="") as f:
        f.write(html)
    with open(os.path.join(out_dir, "review.json"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(final_review, ensure_ascii=False, indent=2))
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=2))
    with open(os.path.join(out_dir, "REPRODUCTION.json"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps({**reproduction, "html_sha256": html_sha, "checks": checks},
                           ensure_ascii=False, indent=2))
    return manifest


def verify(review_dir: str, replay: Optional[Callable[[dict], dict]] = None) -> dict:
    """Fresh-clone census. Returns {'failures': int, 'checks': [...]}.

    replay: optional Level-B fn taking the manifest and returning a regenerated
    review core (from committed cache, offline). If given, its output must match
    the committed review core.
    """
    checks = []
    failures = 0

    def _fail(name, ok, detail=""):
        nonlocal failures
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        if not ok:
            failures += 1

    try:
        with open(os.path.join(review_dir, "manifest.json"), encoding="utf-8") as f:
            manifest = json.load(f)
        with open(os.path.join(review_dir, "review.json"), encoding="utf-8") as f:
            review = json.load(f)
        with open(os.path.join(review_dir, "index.html"), encoding="utf-8") as f:
            served_html = f.read()
    except (OSError, ValueError) as exc:
        return {"failures": 1, "checks": [{"check": "load artifacts", "ok": False, "detail": str(exc)}]}

    # 1. review core hash reproduces
    core_sha = review_sha256(review)
    _fail("review_sha256 reproduces from committed review.json",
          core_sha == manifest.get("review_sha256"),
          f"{core_sha} vs {manifest.get('review_sha256')}")

    # 2. served HTML byte-matches a re-render of the committed review (catches hand-edits)
    rerender = render_page(review)
    _fail("served index.html byte-matches re-render of review.json",
          sha256_text(rerender) == sha256_text(served_html))
    _fail("served index.html sha matches manifest.html_sha256",
          sha256_text(served_html) == manifest.get("html_sha256"))

    # 3. Level B replay if provided
    if replay is not None:
        try:
            regen = replay(manifest)
            _fail("offline replay reproduces review core",
                  review_sha256(regen) == manifest.get("review_sha256"))
        except Exception as exc:  # noqa: BLE001 - report, do not mask
            _fail("offline replay executed", False, str(exc))

    return {"failures": failures, "checks": checks}
