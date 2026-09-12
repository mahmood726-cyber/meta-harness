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
               + check_pooled_verified(review_dir)
               + check_manuscript_numbers(review_dir)
               + check_fetch_complete(review_dir)
               + check_no_double_counted_trial(review_dir)
               + check_pivotal_present(manifest)
               + check_controls(review_dir, manifest)
               + check_cross_source(review_dir)
               + check_retraction(review_dir)
               + check_duplicate_publication(review_dir, manifest)
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
