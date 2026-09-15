"""Two-limb publication gate.

A page is publishable ONLY IF BOTH limbs pass. The gate is enforced at commit
time by .githooks/pre-commit against every staged docs/reviews/<slug>/ page, and
it is designed to REFUSE — see tests/test_gate.py, which proves refusal on each
failure mode. The old corpus reached 1,427 pages because nothing ever stopped a
page appearing; this is that stop.

Limb 1 - reproducibility & integrity:
  * manifest complete; served_method == declared_method
  * generator is the harness, not hand; no hand-made marker in the page
  * a reproduction census is committed with 0 failures, pinned to the exact
    served bytes (its html_sha256 == sha256(index.html) == manifest.html_sha256)
  * the census re-runs live here and reproduces (failures == 0)

Limb 2 - named published OPEN-ACCESS comparator:
  * manifest.comparator has name, PMID or DOI, url, open_access == True,
    and a trial-set overlap {ours_k, theirs_k, shared_k, method}
  * the SERVED page actually contains the comparator identifier and the three
    overlap counts (stated on the page, not merely in metadata)
"""
from __future__ import annotations
import json
import os
import re
import sys

from .canonical import sha256_text
from .census import verify
from . import manuscript as _manuscript_mod
from .registration import protocol_sha as _registration_sha
from . import registration as _registration
from .synth import method_text as _method_text
from .limitations import publication_gate_refusals

REQUIRED_MANIFEST = ("slug", "declared_method", "served_method", "protocol_sha",
                     "generator", "review_sha256", "html_sha256")


def _load(review_dir):
    with open(os.path.join(review_dir, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    with open(os.path.join(review_dir, "index.html"), encoding="utf-8") as f:
        html = f.read()
    rep_path = os.path.join(review_dir, "REPRODUCTION.json")
    rep = None
    if os.path.exists(rep_path):
        with open(rep_path, encoding="utf-8") as f:
            rep = json.load(f)
    return manifest, html, rep


def check_limb1(review_dir, manifest, html, rep):
    reasons = []
    for k in REQUIRED_MANIFEST:
        if not manifest.get(k):
            reasons.append(f"L1: manifest missing '{k}'")
    if manifest.get("declared_method") != manifest.get("served_method"):
        reasons.append(
            f"L1: served method != declared method "
            f"({manifest.get('served_method')!r} vs {manifest.get('declared_method')!r})")
    if str(manifest.get("generator", "")).lower() == "hand":
        reasons.append("L1: generator is 'hand' (nothing hand-made may publish)")
    if "data-handmade" in html or "<!-- handmade -->" in html:
        reasons.append("L1: page carries a hand-made marker")

    if rep is None:
        reasons.append("L1: no committed reproduction census (REPRODUCTION.json)")
    else:
        if rep.get("failures") != 0:
            reasons.append(f"L1: committed census has {rep.get('failures')} failures")
        served_sha = sha256_text(html)
        if rep.get("html_sha256") != served_sha:
            reasons.append("L1: census html_sha256 != sha256(served index.html) "
                           "(page edited after census)")
        if manifest.get("html_sha256") != served_sha:
            reasons.append("L1: manifest html_sha256 != sha256(served index.html)")

    # Live fresh-clone-style reproduction.
    live = verify(review_dir)
    if live["failures"] != 0:
        reasons.append(f"L1: live census reproduced {live['failures']} failure(s): "
                       + "; ".join(c["check"] for c in live["checks"] if not c["ok"]))
    return reasons


def check_limb2(manifest, html):
    reasons = []
    c = manifest.get("comparator")
    if not c:
        reasons.append("L2: no named published comparator")
        return reasons
    if not c.get("name"):
        reasons.append("L2: comparator has no name")
    ident = c.get("pmid") or c.get("doi")
    if not ident:
        reasons.append("L2: comparator has no PMID or DOI")
    if not c.get("url"):
        reasons.append("L2: comparator has no URL")
    if c.get("open_access") is not True:
        reasons.append("L2: comparator is not marked open_access=true")
    ov = c.get("overlap") or {}
    for k in ("ours_k", "theirs_k", "shared_k", "method"):
        if ov.get(k) in (None, ""):
            reasons.append(f"L2: overlap missing '{k}'")
    # Served page must actually state the identifier and the three counts.
    if ident and str(ident) not in html:
        reasons.append("L2: comparator identifier not present on the served page")
    for k in ("ours_k", "theirs_k", "shared_k"):
        v = ov.get(k)
        if v is not None and str(v) not in html:
            reasons.append(f"L2: overlap {k}={v} not stated on the served page")
    return reasons


def check_primary_result(review_dir):
    """A page whose PRIMARY outcome has no pooled result cannot make its central claim and
    must not publish (this is what a k=0 decline looks like — the gate refuses it here rather
    than relying on a human to notice and not commit it)."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return ["L1: no review.json to verify the primary outcome has a result"]
    try:
        with open(p, encoding="utf-8") as f:
            rev = json.load(f)
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read review.json: {exc}"]
    outs = rev.get("outcomes") or []
    prim = next((o for o in outs if o.get("primary")), outs[0] if outs else None)
    if not prim:
        return ["L1: review has no primary outcome"]
    res = prim.get("result") or {}
    if res.get("present") is False or not res.get("k"):
        return [f"L1: primary outcome {prim.get('name')!r} has no pooled result "
                f"(k={res.get('k')}) — a page whose primary claim is absent must not publish"]
    return []


def check_limitation_decision_links(review_dir):
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return ["L1: no review.json to check limitation decision links"]
    try:
        with open(p, encoding="utf-8") as f:
            rev = json.load(f)
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read review.json for limitation decision links: {exc}"]
    bad = publication_gate_refusals(rev.get("limitations") or [])
    return [
        "L1: validity-threatening limitation lacks a linked analytic decision or executable consumer -- "
        + "; ".join(bad[:6])
    ] if bad else []


def check_manuscript_numbers(review_dir):
    """PAPER limb: the generated manuscript must not state a number the object does not carry. Render the
    manuscript from review.json, strip layout (the forest SVG's pixel coordinates) and the registration
    SHA, then refuse any RISKY numeral (decimal, 'N of M', integer >= 10) that is not in
    manuscript.object_numerals(review). This makes 'no prose number without a matching object field'
    structural, not aspirational."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return []  # no review to check (other limbs catch a missing review.json)
    try:
        with open(p, encoding="utf-8") as f:
            rev = json.load(f)
    except (OSError, ValueError) as exc:
        return [f"PAPER: cannot read review.json: {exc}"]
    html = _manuscript_mod.render(rev)
    html = re.sub(r"<svg\b.*?</svg>", " ", html, flags=re.DOTALL)   # layout coordinates, not claims
    html = re.sub(r"<pre\b.*?</pre>", " ", html, flags=re.DOTALL)   # the one-command block
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\b[0-9a-f]{7,}\b", " ", text)                   # registration SHA fragment (hex)
    text = re.sub(r"\b(?:19|20)\d\d\b", " ", text)                  # publication years are inherent
    text = re.sub(r"\bk\s*&minus;\s*1\b", " ", text)                # 'k-1 df' is a formula, not a value
    allowed = _manuscript_mod.object_numerals(rev)
    risky = set(re.findall(r"\d+\.\d+", text))
    ints_text = re.sub(r"\d+\.\d+", " ", text)
    risky |= {n for pair in re.findall(r"(\d+)\s+of\s+(\d+)", ints_text) for n in pair}
    risky |= {n for n in re.findall(r"\d+", ints_text) if int(n) >= 10}
    unaccounted = sorted(n for n in risky if n not in allowed)
    if unaccounted:
        return [f"PAPER: manuscript prose contains numerals not derived from the review object: "
                f"{unaccounted} (every manuscript number must be object-derived — see manuscript.object_numerals)"]
    return []


def check_pooled_verified(review_dir):
    """THE BAR, made structural: every pooled number's digits must appear in its committed source span
    (verify.verify_pooled marks 'verified'/'verified_handchecked'/'not-yet'). A page that pools a
    'not-yet' number — a number not located in the source — must not publish. This converts the
    'a wrong number that gate-passes is the only failure that matters' rule from a rendered badge +
    a survey into a REFUSAL, so an unverified pooled number cannot ship even if a human misses it."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return ["L1: no review.json to verify pooled numbers"]
    try:
        with open(p, encoding="utf-8") as f:
            rev = json.load(f)
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read review.json: {exc}"]
    bad = []
    for o in rev.get("outcomes", []) or []:
        for t in o.get("trials", []) or []:
            if t.get("verified") not in ("verified", "verified_handchecked"):
                bad.append(f"{t.get('id')} in {o.get('name')!r} (status={t.get('verified')!r})")
    if bad:
        return [f"L1: pooled number(s) not verified against the committed source span — a page must not "
                f"pool a number whose digits are not located in its source: {'; '.join(bad[:6])}"]
    return []


_CORE_SOURCES = ("PubMed", "Europe PMC (OA + metadata)", "ClinicalTrials.gov")


def check_fetch_complete(review_dir):
    """A THROTTLED FETCH IS A PARTIAL FETCH, and a partial cache looks exactly like a complete one.
    If a CORE acquisition source (PubMed / Europe PMC / ClinicalTrials.gov) reported RAN_ERROR, the
    committed cache is silently incomplete — a rate-limit (HTTP 429) can drop a pivotal trial and the
    build then pools an over-broad or under-complete set that looks fine. REFUSE on a core-source
    RAN_ERROR (auxiliary reach sources — citation chase / registry-first / full text — may error without
    degrading the core pool, and are rendered as reach limitations rather than blocking). Complements the
    pivotal-present limb: that catches a KNOWN missing landmark; this catches the degraded fetch itself."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return ["L1: no review.json to check fetch completeness"]
    try:
        with open(p, encoding="utf-8") as f:
            rev = json.load(f)
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read review.json: {exc}"]
    ss = (rev.get("search") or {}).get("source_status") or {}
    bad = [k for k in _CORE_SOURCES if ss.get(k) == "RAN_ERROR"]
    if bad:
        return [f"L1: core acquisition source(s) {bad} reported RAN_ERROR — a throttled/failed fetch means "
                f"the committed cache is silently incomplete (a rate-limit can drop a pivotal trial); "
                f"re-fetch (serialised, no 429) before building rather than pool a degraded cache"]
    return []


_ACCESS_OUTCOME_PHRASES = (
    "re-tested at full text", "retested at full text",
    "confirmed at full-text level", "confirmed at full text",
    "publisher-blocked", "publisher blocked",
    "access-blocked", "access blocked",
    "paywalled",
    "pmc disallows xml",
)


def _all_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _all_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _all_strings(v)


def check_access_claim_supported(review_dir):
    """NOT_RUN-as-paywalled (audit 22): a review must not assert a full-text ACCESS OUTCOME — that full text
    was re-tested/confirmed, or is publisher-blocked / access-blocked / paywalled — when the PMC full-text
    adapter did not run. An adapter with source_status 'NOT_RUN' established nothing about access, so any such
    claim is manufactured, and (worse) it is used to justify excluding poolable trials (corticosteroids-covid,
    sglt2-ckd). Stating that the adapter DID NOT RUN and that a count is absent from the committed abstract is
    honest and passes; asserting a tested access barrier we never tested does not."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return ["L1: no review.json to check access claims"]
    try:
        with open(p, encoding="utf-8") as f:
            rev = json.load(f)
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read review.json: {exc}"]
    ss = (rev.get("search") or {}).get("source_status") or {}
    if ss.get("PMC full text") != "NOT_RUN":
        return []  # the full-text adapter ran (or its state is unknown) — access claims are not manufactured here
    hay = " \n ".join(_all_strings(rev)).lower()
    hit = [ph for ph in _ACCESS_OUTCOME_PHRASES if ph in hay]
    if hit:
        return [f"L1: review asserts a full-text access outcome {hit} while source_status['PMC full text'] "
                f"== NOT_RUN — the adapter never ran, so 're-tested at full text' / 'publisher-blocked' / "
                f"'paywalled' is unsupported; state that the adapter did not run and the count is absent from "
                f"the committed abstract instead of a tested access barrier"]
    return []


_PARITY_EXCL_CUE = re.compile(r"excluded|design-excluded|scope-excluded|open-label|binding trap|we caught|"
                              r"declined|not pooled", re.I)
_PARITY_ACRONYM = re.compile(r"\b([A-Z][A-Za-z0-9]*(?:[.\-][A-Za-z0-9]+){1,4}|[A-Z]{3,}[0-9]*)\b")


def check_parity_our_k(review_dir):
    """Derived-narrative / stale-panel guard (audit 28): the parity block is a STORED narrative that can
    survive after the review object changed (omega3 parity claimed we pool OMEMI + OMEGA-REMODEL, which are
    declared-absent; colchicine-postop named Bessissow as pooled when it is not). You cannot pool MORE than
    you pooled, so parity.our_k must not EXCEED the primary result's k. (our_k < k is allowed — a legitimate
    same-scope subset, e.g. we pool 4 but only 2 match the comparator's exact scope.) A suppressed primary
    has no k and is skipped."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return []
    try:
        rev = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return []
    prim = next((o for o in rev.get("outcomes", []) if o.get("primary")), None)
    res = (prim or {}).get("result") or {}
    if res.get("suppressed_incompatible"):
        return []
    k = res.get("k")
    par = (rev.get("reproduction") or {}).get("parity") or {}
    our_k = par.get("our_k")
    reasons = []
    # (1) COUNT: equality, not <=. A same-scope subset is a different quantity that belongs in its own field,
    # never smuggled into our_k (relaxing the comparison would be a loosened test).
    if isinstance(k, int) and isinstance(our_k, int) and our_k != k:
        reasons.append(f"L1: parity.our_k ({our_k}) != the primary pooled k ({k}) — a stored parity count out "
                       f"of sync with the live pool. Derive our_k from the object; a same-scope subset belongs "
                       f"in its own field, not our_k.")
    # (2) SET MEMBERSHIP: a trial the reason names as EXCLUDED must NOT be in the pool (omega3 named the pooled
    # SU.FOL.OM3 as 'excluded'). Matched by PMID and by acronym taken from each pooled trial's own source span.
    pooled = {str(t.get("id", "")).replace("PMID ", "").strip() for t in prim.get("trials", [])}
    for t in prim.get("trials", []):
        pooled.add(str(t.get("label", "")).upper())
        # a trial ACRONYM only where it sits in a trial-name position: immediately before "(PMID/PMC/NCT".
        # This excludes outcome/method abbreviations (POAF, AAD, MACE) that appear elsewhere in the source.
        for a in re.findall(r"\b([A-Z][A-Za-z0-9.\-]{2,})\s*\((?:PMID|PMC|NCT)", t.get("source", "") or ""):
            if not a.isdigit():
                pooled.add(a.upper())
    pooled.discard("")
    txt = par.get("reason", "") or ""
    for m in _PARITY_EXCL_CUE.finditer(txt):
        seg = txt[m.end():m.end() + 90]
        named = set(re.findall(r"\b\d{7,8}\b", seg)) | {a.upper() for a in _PARITY_ACRONYM.findall(seg)
                                                        if not a.isdigit() and len(a) >= 3}
        for nm in named:
            if nm in pooled:
                reasons.append(f"L1: parity reason names '{nm}' as EXCLUDED but it IS in the pooled set — a "
                               f"stale narrative describing a review that no longer exists (audit 28).")
    return reasons


def check_no_double_counted_trial(review_dir):
    """Unit-of-analysis: no trial may be pooled more than once WITHIN an outcome (multi-arm shared-control
    double-counting, ME-25). The harness contributes one effect per trial and the multi-arm guard refuses
    un-ruled dose selection, so a trial never enters an outcome's pool twice — this asserts that structural
    guarantee: if the same trial id appears twice in one outcome's pooled set (e.g. two arms of a 3-arm trial
    both pooled against the shared control), REFUSE (the control would be counted twice, inflating weight)."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return ["L1: no review.json to check unit-of-analysis double-counting"]
    try:
        with open(p, encoding="utf-8") as f:
            rev = json.load(f)
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read review.json: {exc}"]
    bad = []
    for o in rev.get("outcomes", []) or []:
        seen = {}
        for t in o.get("trials", []) or []:
            tid = str(t.get("id", "")).strip()
            seen[tid] = seen.get(tid, 0) + 1
        for tid, n in seen.items():
            if n > 1:
                bad.append(f"{tid} pooled {n}x in {o.get('name')!r} (shared-control double-count)")
    if bad:
        return [f"L1: a trial is pooled more than once within an outcome — a unit-of-analysis "
                f"(shared-control) double-count that inflates its weight: {'; '.join(bad[:6])}"]
    return []


def check_cache_tracked(manifest):
    """A page replays from its committed cache, so that cache MUST be git-tracked — an untracked
    cache means a fresh clone cannot reproduce the page (this silently broke empagliflozin: the
    page looked fine, but its cache/<slug>/records.json was never committed). Refuse if untracked."""
    import subprocess
    slug = manifest.get("slug")
    if not slug:
        return ["L1: manifest has no slug to check cache tracking"]
    rel = f"cache/{slug}/records.json"
    try:
        out = subprocess.check_output(["git", "-C", ROOT, "ls-files", "--", rel], text=True).strip()
    except Exception as exc:  # noqa: BLE001
        return [f"L1: cannot check cache tracking ({exc})"]
    if not out:
        return [f"L1: committed cache {rel} is NOT git-tracked — a fresh clone could not reproduce "
                "this page; commit the cache"]
    return []


def check_reproduction(review_dir, manifest):
    """Level B: re-run the pipeline from the COMMITTED cache + protocol SHA and confirm it
    regenerates the committed review core (the numbers), not just that the HTML matches the
    JSON. This is what makes 'reproducible from the protocol SHA on a fresh clone' an enforced
    property rather than a claim — every extraction/screening/dedup change must survive it."""
    import json as _json
    slug = manifest.get("slug")
    if not slug:
        return ["L1: manifest has no slug to replay"]
    try:
        from . import fetch
        from .canonical import review_sha256
        from .pipeline import build_review_core
        cfg = _json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        sha = _registration_sha(slug)
        if not sha:
            return [f"L1: no registration SHA for {slug!r}"]
        records = fetch.ensure(cfg, "")  # committed cache present -> offline
        regen = review_sha256(build_review_core(slug, cfg, records, sha))
    except Exception as exc:  # noqa: BLE001 - a replay that cannot run is a refusal, not a pass
        return [f"L1: offline replay could not execute ({exc}) — cannot confirm reproduction"]
    if regen != manifest.get("review_sha256"):
        return [f"L1: offline replay does NOT regenerate the committed numbers "
                f"(replay {regen} vs committed {manifest.get('review_sha256')})"]
    return []


def check_controls(review_dir, manifest):
    """Screening controls must be ENFORCED, not just reported. Every topic must declare >=1 positive
    and >=1 negative control (a control that never runs is decoration); every POSITIVE control (a
    canonical trial a comparator includes) must be screened IN, and every NEGATIVE control (a
    same-drug/design trial of the wrong topic) must be screened OUT. A positive control screened out,
    or a negative control screened in, is a screening regression and REFUSES here rather than sitting
    as a 'MISSED' string on the page."""
    slug = manifest.get("slug")
    if not slug:
        return ["L1: manifest has no slug to check controls"]
    try:
        cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        rev = json.load(open(os.path.join(review_dir, "review.json"), encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"L1: cannot load config/review to check controls ({exc})"]
    pos = [str(p) for p in cfg.get("positive_control_pmids", [])]
    neg = [str(p) for p in cfg.get("negative_control_pmids", [])]
    reasons = []
    if not pos:
        reasons.append("L1: no positive control declared (every topic needs >=1 canonical-trial control)")
    if not neg:
        reasons.append("L1: no negative control declared (every topic needs >=1 wrong-topic control)")
    dec = {}
    for x in (rev.get("screening") or {}).get("records", []):
        rid = str(x.get("id", "")).split("·")[-1].strip()
        dec[rid] = x.get("decision")
    pos_miss = [p for p in pos if dec.get(p) != "include"]
    neg_in = [p for p in neg if dec.get(p) == "include"]
    if pos_miss:
        reasons.append(f"L1: positive control(s) {pos_miss} were NOT screened in "
                       "(a canonical trial the comparator includes must pass our screen)")
    if neg_in:
        reasons.append(f"L1: negative control(s) {neg_in} were wrongly screened in "
                       "(a wrong-topic trial must be excluded by rule)")
    return reasons


def check_cross_source(review_dir):
    """The second independent extractor (CT.gov structured vs abstract) may only flag a DIRECTION
    FLIP as agree=False -- one source says the intervention helps, the other that it harms, on the
    same outcome family. That is almost never a benign timepoint/definition difference (unlike a mere
    magnitude gap, which is NOT flagged), so it is a real integrity signal and REFUSES here. A wrong
    number that two independent primary sources contradict on direction must not publish."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return []
    try:
        rev = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read review.json for cross-source check ({exc})"]
    bad = []
    for o in rev.get("outcomes", []) or []:
        for t in o.get("trials", []) or []:
            cs = t.get("cross_source") or {}
            if cs.get("agree") is False:
                bad.append(f"{t.get('id')} (abstract RR {cs.get('abstract_rr')} vs CT.gov RR {cs.get('ctgov_rr')})")
    if bad:
        return ["L1: cross-source DIRECTION-FLIP discrepancy on " + "; ".join(bad)
                + " — two independent sources disagree on direction; do not publish until resolved"]
    return []


def check_duplicate_publication(review_dir, manifest):
    """Unit-of-analysis guard: the SAME trial reported in two papers must not be pooled twice. If two
    pooled trials in one outcome share an NCT, that is double-counting — refuse. Reads the committed
    cache for the pmid->nct map (the review does not carry it)."""
    slug = manifest.get("slug")
    if not slug:
        return []
    cp = os.path.join(ROOT, "cache", slug, "records.json")
    rp = os.path.join(review_dir, "review.json")
    if not (os.path.exists(cp) and os.path.exists(rp)):
        return []
    try:
        nct_of = {str(r.get("id")): r.get("nct") for r in json.load(open(cp, encoding="utf-8")).get("records", [])}
        rev = json.load(open(rp, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read for duplicate-publication check ({exc})"]
    reasons = []
    for o in rev.get("outcomes", []) or []:
        seen = {}
        for t in o.get("trials", []) or []:
            pid = str(t.get("id", "")).replace("PMID ", "")
            nct = nct_of.get(pid)
            if nct:
                seen.setdefault(nct, []).append(pid)
        dups = {n: ps for n, ps in seen.items() if len(ps) > 1}
        if dups:
            reasons.append(f"L1: outcome {o.get('name')!r} pools the same trial twice (shared NCT {dups}) "
                           "— duplicate-publication double-counting; pool one report per trial")
    return reasons


def check_retraction(review_dir):
    """A pooled RETRACTED trial is a catastrophic defect; refuse the page. Reads the committed
    integrity snapshot (cache/<slug>/integrity.json via review.json's integrity block). If the check
    has not been run for a topic, this does NOT refuse (absence != clean) — but a topic that HAS an
    integrity block with a retracted PMID is blocked. Expression-of-concern is surfaced, not blocked."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return []
    try:
        rev = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read review.json for retraction check ({exc})"]
    integ = rev.get("integrity") or {}
    retracted = integ.get("retracted") or []
    if retracted:
        return [f"L1: pooled trial(s) {retracted} are RETRACTED (integrity check) — a retracted trial "
                "must never be pooled; withdraw or replace before publishing"]
    return []


def _pivotal_missing(piv, records):
    """Pure: which of the declared pivotal ids (PMIDs/NCTs) are absent from the records. A record
    matches by its id or its nct."""
    ids = set()
    for r in records:
        ids.add(str(r.get("id")))
        if r.get("nct"):
            ids.add(str(r.get("nct")))
    return [str(p) for p in piv if str(p) not in ids]


def check_pivotal_present(manifest):
    """A generated/fetched cache that omits the topic's PIVOTAL/landmark trial produces a silently
    empty or wrong result (sacubitril: PARADIGM-HF was absent from Codex's fetch -> k=None). A topic
    may declare `pivotal_trials` (PMIDs/NCTs named in its preregistration); each MUST be present in
    the committed cache/<slug>/records.json, else REFUSE — converting a silent search failure into a
    build-time refusal, and generalising to every generated-config topic. Opt-in: topics without
    `pivotal_trials` are unaffected (absence != enforcement)."""
    slug = manifest.get("slug")
    if not slug:
        return []
    try:
        cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    except (OSError, ValueError):
        return []
    piv = [str(p) for p in cfg.get("pivotal_trials", [])]
    if not piv:
        return []
    cp = os.path.join(ROOT, "cache", slug, "records.json")
    try:
        recs = json.load(open(cp, encoding="utf-8")).get("records", [])
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read cache to check pivotal trials ({exc})"]
    missing = _pivotal_missing(piv, recs)
    if missing:
        return [f"L1: pivotal/landmark trial(s) {missing} declared in the preregistration are ABSENT "
                "from the committed cache — the search did not retrieve the topic's defining trial, so "
                "any pooled result would be silently incomplete; fix the query/fetch before building"]
    return []


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_prespecification_in_protocol(review_dir):
    """A selection rule cited on the page as 'pre-specified' MUST exist in the protocol at its SHA
    (external audit #9: noac claimed a 'pre-specified approved-dose rule' that was not in the registered
    protocol). Two checks: (1) a 'pre-specified' claim on the page requires the same in the protocol,
    unless the page frames it as post-hoc/amendment/not-pre-specified; (2) a dose_selection override in
    the cache requires the protocol to document a dose rule or a dated amendment."""
    slug = os.path.basename(os.path.normpath(review_dir))
    # Scope the check to a SELECTION RULE we actually apply: a committed dose_selection override. (A
    # trial's own "pre-specified primary endpoint" is the trial's prespecification, not ours, and must
    # not trip this — that over-broad reading false-fired on 4 pages.)
    ds_p = os.path.join(ROOT, "cache", slug, "dose_selection.json")
    if not os.path.exists(ds_p):
        return []
    reasons = []
    proto_p = os.path.join(ROOT, "protocols", f"{slug}.md")
    proto = open(proto_p, encoding="utf-8").read().lower() if os.path.exists(proto_p) else ""
    # (1) the applied dose rule must be documented in the protocol (a dose rule or a dated amendment).
    if not re.search(r"dose|amendment|approved", proto):
        reasons.append(f"prespecification: a dose_selection override is applied but "
                       f"protocols/{slug}.md documents no dose-selection rule or amendment.")
    # (2) if the dose_selection source-text claims the rule is 'pre-specified', the protocol must
    #     actually prespecify it; otherwise it must be framed as a post-hoc amendment.
    try:
        ds = json.load(open(ds_p, encoding="utf-8"))
    except (OSError, ValueError):
        ds = {}
    src_text = " ".join(str((v or {}).get("source", "")) for v in ds.values()).lower()
    claims_prespec = ("pre-specified" in src_text or "prespecified" in src_text) and \
                     not any(w in src_text for w in ("post-hoc", "post hoc", "amendment", "not pre"))
    proto_prespec = ("pre-specified" in proto) or ("prespecified" in proto)
    if claims_prespec and not proto_prespec:
        reasons.append(f"prespecification: dose_selection for {slug} claims a 'pre-specified' rule but "
                       f"protocols/{slug}.md does not prespecify it — relabel it a dated post-hoc "
                       f"amendment or add the rule to the protocol.")
    return reasons


def check_population_identity(review_dir):
    """No POOLED trial may match the topic's population_none (external audit: colchicine-postop pooled
    non-cardiac COP-AF/Bessissow though I2 was cardiac surgery). If a pooled trial's own record matches
    an exclusion term, it leaked past screening into the pool — refuse. Deterministic; uses the same
    matcher as the screen so it stays in lock-step."""
    slug = os.path.basename(os.path.normpath(review_dir))
    cfg_p = os.path.join(ROOT, "topics", f"{slug}.json")
    rec_p = os.path.join(ROOT, "cache", slug, "records.json")
    rev_p = os.path.join(review_dir, "review.json")
    if not (os.path.exists(cfg_p) and os.path.exists(rec_p) and os.path.exists(rev_p)):
        return []
    try:
        from harness.screen import _has, _poptext
        cfg = json.load(open(cfg_p, encoding="utf-8"))
        recs = {str(r.get("id")): r for r in json.load(open(rec_p, encoding="utf-8")).get("records", [])}
        rev = json.load(open(rev_p, encoding="utf-8"))
    except (OSError, ValueError, ImportError):
        return []
    pop_none = (cfg.get("include") or {}).get("population_none") or []
    if not pop_none:
        return []
    reasons = []
    seen = set()
    for o in rev.get("outcomes", []):
        for t in o.get("trials", []):
            lab = str(t.get("label"))
            if lab in seen:
                continue
            seen.add(lab)
            rec = recs.get(lab)
            if not rec:
                continue
            bad = _has(_poptext(rec), pop_none)
            if bad:
                reasons.append(f"population identity: pooled trial {lab} matches the exclusion term "
                               f"'{bad}' (population_none) — it leaked past screening into the pool.")
    return reasons


def check_preregistration_not_build(review_dir):
    """A page that CLAIMS prospective registration (reproduction.preregistration.prospective) must cite a
    PROTOCOL-ONLY commit — one that contains no fetched cache, extracted review, blind pages or index. A
    commit that added the protocol ALONGSIDE the build cannot show the protocol preceded synthesis (audit
    20: the displayed SHA was a build commit). If prospective is claimed but the cited SHA is a build
    commit (or missing), REFUSE. A page that honestly records prospective=False makes no claim and passes."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return []
    try:
        rev = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return []
    pre = (rev.get("reproduction") or {}).get("preregistration") or {}
    if not pre.get("prospective"):
        return []  # no prospective claim -> nothing to enforce (honestly labelled not-demonstrated)
    sha = pre.get("sha")
    if not sha:
        return ["L1(prereg): prospective registration claimed but no SHA cited"]
    if _registration.is_build_commit(sha):
        return [f"L1(prereg): prospective registration cites {sha[:8]} but that commit contains build "
                "artifacts (cache/review/pages) — a build commit cannot demonstrate the protocol preceded "
                "synthesis; cite a protocol-only commit or record prospective=False"]
    return []


def check_method_matches_scale(review_dir):
    """The declared analysis-method string must match the scale ACTUALLY pooled — recomputed here
    independently via synth.method_text so the check cannot be a constant compared to itself (the
    melatonin cold-audit class: a mean-difference outcome was labelled with the log-ratio method, and
    the old declared==served limb compared one METHOD constant to itself and could never fire). For
    every POOLED outcome (k>=2), the stored method must equal method_text(result.scale); and the
    manifest served_method must equal method_text(the primary outcome's result.scale). Single-trial
    (k==1) outcomes carry the honest 'trial's own effect' text and are exempt."""
    rev_p = os.path.join(review_dir, "review.json")
    man_p = os.path.join(review_dir, "manifest.json")
    if not os.path.exists(rev_p):
        return []
    try:
        rev = json.load(open(rev_p, encoding="utf-8"))
    except (OSError, ValueError):
        return []
    reasons = []
    primary_scale = None
    for o in rev.get("outcomes", []):
        res = o.get("result") or {}
        scale = res.get("scale")
        k = res.get("k")
        if o.get("primary"):
            primary_scale = scale
        if isinstance(k, int) and k >= 2 and scale:
            want = _method_text(scale)
            got = o.get("method") or ""
            if got != want:
                fam = "mean-difference" if want.startswith("Random-effects inverse-variance on the mean") else "log-ratio"
                reasons.append(f"L1(method): outcome '{o.get('name')}' pooled on scale {scale!r} "
                               f"but its declared method is not the {fam} method "
                               f"(method-string does not match the pooled scale).")
    # manifest served_method must match the primary outcome's actual scale
    if primary_scale and os.path.exists(man_p):
        try:
            man = json.load(open(man_p, encoding="utf-8"))
            if man.get("served_method") and man.get("served_method") != _method_text(primary_scale):
                reasons.append(f"L1(method): manifest served_method does not match the method for the "
                               f"primary pooled scale {primary_scale!r}.")
        except (OSError, ValueError):
            pass
    return reasons


def gate_page(review_dir):
    """Return (ok: bool, reasons: list[str]). ok == True only if both limbs pass."""
    try:
        manifest, html, rep = _load(review_dir)
    except (OSError, ValueError) as exc:
        return False, [f"gate: cannot load review dir: {exc}"]
    reasons = (check_limb1(review_dir, manifest, html, rep)
               + check_cache_tracked(manifest)
               + check_reproduction(review_dir, manifest)
               + check_primary_result(review_dir)
               + check_limitation_decision_links(review_dir)
               + check_pooled_verified(review_dir)
               + check_manuscript_numbers(review_dir)
               + check_fetch_complete(review_dir)
               + check_access_claim_supported(review_dir)
               + check_parity_our_k(review_dir)
               + check_no_double_counted_trial(review_dir)
               + check_pivotal_present(manifest)
               + check_controls(review_dir, manifest)
               + check_cross_source(review_dir)
               + check_retraction(review_dir)
               + check_duplicate_publication(review_dir, manifest)
               + check_prespecification_in_protocol(review_dir)
               + check_population_identity(review_dir)
               + check_method_matches_scale(review_dir)
               + check_preregistration_not_build(review_dir)
               + check_limb2(manifest, html))
    return (len(reasons) == 0), reasons


def main(argv):
    if not argv:
        print("usage: python -m harness.gate <review_dir> [<review_dir> ...]")
        return 2
    any_refused = False
    for d in argv:
        ok, reasons = gate_page(d)
        if ok:
            print(f"GATE PASS  {d}")
        else:
            any_refused = True
            print(f"GATE REFUSE {d}")
            for r in reasons:
                print(f"    - {r}")
    return 1 if any_refused else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
