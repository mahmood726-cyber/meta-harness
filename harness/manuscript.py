"""Deterministic manuscript per review (Stage PAPER, forward plan P1).

Generates a full structured manuscript FROM the review object: structured abstract, methods describing what
actually ran, results with a forest plot (SVG, object-derived), limitations (from GRADE/RoB/heterogeneity
fields), and a data-availability statement with the protocol SHA and the one command. EVERY number is
interpolated from a committed object field, so the manuscript cannot state a number the data does not carry.
A gate limb (harness.gate.check_manuscript_numbers) enforces this by extracting every risky numeral from the
rendered manuscript and refusing any that is not in object_numerals(review)."""
from __future__ import annotations
from . import grade as _grade_mod

import html as _html

from . import rob_sensitivity as _rob_sensitivity_mod
from harness import identity as _identity_mod


def _e(s):
    return _html.escape(str(s)) if s is not None else ""


def _fmt(x, nd=2):
    if x is None:
        return ""
    try:
        return f"{round(float(x), nd):g}"
    except (TypeError, ValueError):
        return str(x)


def _unit_label(unit):
    if unit == "prespecified_subgroup":
        return "pre-specified subgroup"
    if unit == "post_hoc_subgroup":
        return "post-hoc subgroup"
    return "trial"


def _evidence_unit_summary(outcome):
    trials = outcome.get("trials") or []
    if not trials or all((t.get("evidence_unit") or "trial") == "trial" for t in trials):
        return None
    counts = {}
    for t in trials:
        unit = t.get("evidence_unit") or "trial"
        counts[unit] = counts.get(unit, 0) + 1
    bits = []
    if counts.get("trial"):
        bits.append(f"{counts['trial']} trial" + ("" if counts["trial"] == 1 else "s"))
    for unit in ("prespecified_subgroup", "post_hoc_subgroup"):
        group = [t for t in trials if t.get("evidence_unit") == unit]
        if not group:
            continue
        details = sorted({t.get("evidence_unit_detail") for t in group if t.get("evidence_unit_detail")})
        if len(group) == 1 and details:
            bits.append(f"1 {_unit_label(unit)} of {details[0]}")
        else:
            bits.append(f"{len(group)} {_unit_label(unit)}" + ("" if len(group) == 1 else "s"))
    return " + ".join(bits)


def _k_phrase(outcome):
    k = (outcome.get("result") or {}).get("k")
    eu = _evidence_unit_summary(outcome)
    return f"k = {k} ({eu})" if eu and k is not None else f"{k} trials"


def _forest_k_phrase(outcome):
    k = (outcome.get("result") or {}).get("k")
    eu = _evidence_unit_summary(outcome)
    return f"k = {k} ({eu})" if eu and k is not None else f"k={k}"


def _primary(review):
    return next((o for o in review.get("outcomes", []) if o.get("primary")), None)


def object_numerals(review):
    """The set of numeral strings the manuscript is ALLOWED to print — every one derived from a committed
    object field. The gate limb checks the rendered manuscript's risky numerals against this set."""
    out = set()

    def add(v, nd=2):
        if isinstance(v, bool) or v is None:
            return
        if isinstance(v, int):
            out.add(str(v))
        elif isinstance(v, float):
            out.add(f"{round(v, nd):g}")
            out.add(f"{round(v, 1):g}")
            out.add(f"{abs(round(v, nd)):g}")

    prim = _primary(review) or {}
    res = prim.get("result") or {}
    for k in ("k", "estimate", "ci_low", "ci_high", "tau2", "pi_low", "pi_high"):
        add(res.get(k))
    # every pooled trial's values
    for o in review.get("outcomes", []):
        for t in o.get("trials", []):
            for k in ("effect", "ci_low", "ci_high", "ai", "n1i", "ci", "n2i",
                      "mean1", "sd1", "nc1", "mean2", "sd2", "nc2"):
                add(t.get(k))
        r2 = o.get("result") or {}
        for k in ("k", "estimate", "ci_low", "ci_high"):
            add(r2.get(k))
    # counts: pooled k, declared-absent count, screening totals
    scr = review.get("screening") or {}
    add(len(scr.get("records", []) or []))
    for o in review.get("outcomes", []):
        add(len(o.get("trials", []) or []))
        add(len(o.get("declared_absent_trials", []) or []))
        if review.get("publication_units"):
            counts = _identity_mod.outcome_counts(o)
            add(counts["pooled"].get("trials"))
            add(counts["pooled"].get("publications"))
            add(counts["absent"].get("trials"))
            add(counts["absent"].get("publications"))
        units = {}
        for t in o.get("trials", []) or []:
            unit = t.get("evidence_unit") or "trial"
            units[unit] = units.get(unit, 0) + 1
        for v in units.values():
            add(v)
    # the STALE-membership sentence's count of eligible families not in the pool: the SAME derivation the sentence
    # uses (grade.missing_family_count -- distinct known-missing rows, else declared-absent rows), so the numeral
    # the manuscript prints is registered by the function that produces it, never re-derived here. Latent until
    # iv-iron's count reached 10 on 2026-09-20 (the gate scans integers >= 10) and the page was withheld.
    from . import grade as _grade_mod
    add(_grade_mod.missing_family_count(review))
    # grade downgrades, rob coverage
    g = review.get("grade") or {}
    add(g.get("downgrades"))
    s = review.get("rob_sensitivity") or {}
    add(s.get("n_trials"))
    add(s.get("n_rob_rated"))
    for stratum in ("full", "drop_high", "low_only"):
        st = s.get(stratum) or {}
        for k in ("k", "estimate", "ci_low", "ci_high"):
            add(st.get(k))
    # the confidence/prediction-interval level is a fixed statistical constant the manuscript states
    out.add("95")
    out.add("12.71")
    # numerals present in committed TEXT fields the manuscript quotes verbatim (title, question, and each
    # outcome's timepoint/population) are object-sourced, not invented (e.g. 'semaglutide 2.4 mg', 'Week 68')
    import re as _re
    texts = [review.get("title") or "", review.get("question") or ""]
    for o in review.get("outcomes", []):
        texts += [str(o.get("timepoint") or ""), str(o.get("population") or ""), str(o.get("name") or "")]
        # Follow-up values quoted by the compatibility limitation come from
        # the per-trial admission objects, including retrospective sensitivity.
        for trial in o.get("trials", []):
            for dimension in ("follow_up_window", "endpoint_definition"):
                cell = (trial.get("admission") or {}).get(dimension) or {}
                texts.append(str(cell.get("trial_value") or ""))
    for txt in texts:
        for m in _re.findall(r"\d+(?:\.\d+)?", txt):
            out.add(m)
            if "." not in m:
                continue
            out.add(f"{float(m):g}")
    return out


def _forest(review):
    """A minimal object-derived forest plot (SVG) of the primary outcome: one row per pooled trial with its
    effect and CI, and a diamond for the pooled estimate. Ratio scales use a log x-axis with null at 1."""
    prim = _primary(review)
    if not prim or not prim.get("trials"):
        return ""
    res = prim.get("result") or {}
    if res.get("suppressed_incompatible"):
        return ""  # FAIL CLOSED (audit 23): no forest for an incompatible (suppressed) pool
    import math
    scale = (res.get("scale") or prim.get("estimand") or "").upper()
    is_ratio = scale in ("HR", "RR", "OR", "IRR") or scale.startswith("MIXED")
    rows = []
    for t in prim["trials"]:
        e, lo, hi = t.get("effect"), t.get("ci_low"), t.get("ci_high")
        if e is None and t.get("ai") is not None:
            # 2x2 -> RR for display only (not a stored number; skip if incomputable)
            try:
                a, n1, c, n2 = t["ai"], t["n1i"], t["ci"], t["n2i"]
                e = (a / n1) / (c / n2) if c and n2 and n1 else None
            except (TypeError, ZeroDivisionError):
                e = None
        if e is None and t.get("mean1") is not None:
            e = t["mean1"] - t["mean2"]
            lo = hi = None
        if e is not None:
            rows.append((str(t.get("label")), e, lo, hi))
    if not rows:
        return ""
    pooled = (res.get("estimate"), res.get("ci_low"), res.get("ci_high"))
    xs = [v for _, e, lo, hi in rows for v in (e, lo, hi) if v is not None]
    if pooled[0] is not None:
        xs += [v for v in pooled if v is not None]
    if is_ratio:
        xs = [x for x in xs if x and x > 0]
        if not xs:
            return ""
        tx = [math.log(x) for x in xs]
    else:
        tx = xs
    lo_x, hi_x = min(tx), max(tx)
    span = (hi_x - lo_x) or 1.0
    W, rowh, padL, padR, padT = 640, 22, 190, 60, 30
    H = padT + rowh * (len(rows) + 2) + 20

    def xpix(v):
        if v is None:
            return None
        vv = math.log(v) if is_ratio else v
        return padL + (vv - lo_x) / span * (W - padL - padR)

    null = 1.0 if is_ratio else 0.0
    parts = [f"<svg viewBox='0 0 {W} {H}' role='img' aria-label='Forest plot of the primary outcome' "
             f"style='max-width:100%;height:auto;font:12px system-ui'>"]
    nx = xpix(null)
    if nx is not None and lo_x <= (math.log(null) if is_ratio else null) <= hi_x:
        parts.append(f"<line x1='{nx:.1f}' y1='{padT-6}' x2='{nx:.1f}' y2='{H-24}' stroke='#b0bec5' stroke-dasharray='3 3'/>")
    y = padT
    for lab, e, lo, hi in rows:
        cx = xpix(e)
        if lo is not None and hi is not None:
            xl, xh = xpix(lo), xpix(hi)
            parts.append(f"<line x1='{xl:.1f}' y1='{y:.1f}' x2='{xh:.1f}' y2='{y:.1f}' stroke='#37474f'/>")
        parts.append(f"<rect x='{cx-3:.1f}' y='{y-3:.1f}' width='6' height='6' fill='#1d3b4d'/>")
        parts.append(f"<text x='6' y='{y+4:.1f}' fill='#12232e'>{_e(lab)}</text>")
        val = f"{_fmt(e)}" + (f" [{_fmt(lo)}, {_fmt(hi)}]" if lo is not None else "")
        parts.append(f"<text x='{W-padR+6}' y='{y+4:.1f}' fill='#37474f'>{_e(val)}</text>")
        y += rowh
    # pooled diamond
    if pooled[0] is not None and pooled[1] is not None:
        y += rowh // 2
        xc, xl, xh = xpix(pooled[0]), xpix(pooled[1]), xpix(pooled[2])
        parts.append(f"<polygon points='{xl:.1f},{y:.1f} {xc:.1f},{y-6:.1f} {xh:.1f},{y:.1f} {xc:.1f},{y+6:.1f}' fill='#b31412'/>")
        parts.append(f"<text x='6' y='{y+4:.1f}' fill='#b31412' font-weight='600'>Pooled ({_e(_forest_k_phrase(prim))})</text>")
        pv = f"{_fmt(pooled[0])} [{_fmt(pooled[1])}, {_fmt(pooled[2])}]"
        parts.append(f"<text x='{W-padR+6}' y='{y+4:.1f}' fill='#b31412' font-weight='600'>{_e(pv)}</text>")
    parts.append(f"<text x='{padL}' y='{H-6}' fill='#78909c'>{_e(scale or 'effect')} ({'log scale, null=1' if is_ratio else 'null=0'})</text></svg>")
    return "".join(parts)



def _eligibility_rule_sentence(review):
    """The eligibility rule as REGISTERED, derived from the committed protocol prose (harness.protocol_compiler
    .eligibility_clause) -- never a literal. glp1's B-prime clause makes prospective, systematic outcome ascertainment an
    eligibility axis and result availability explicitly not one; a topic whose registered rule is P/I/C/design says so;
    a protocol with no parsable clause gets a stated refusal, not a sentence."""
    from . import protocol_compiler as _pc
    text = ((review.get("protocol") or {}).get("text")) if isinstance(review.get("protocol"), dict) else None
    sentence = _pc.eligibility_rule_sentence(text or "")
    if sentence is None:
        return ("Eligibility rule: NOT PARSABLE from the registered protocol text (no eligibility clause located); "
                "no rule sentence is asserted.")
    return _e(sentence).replace("**", "")

def render(review, neutral: bool = False) -> str:
    prim = _primary(review)
    if not prim:
        return "<p>No primary outcome to report.</p>"
    res = prim.get("result") or {}
    title = review.get("title") or review.get("slug")
    q = review.get("question") or ""
    scr = review.get("screening") or {}
    n_screened = len(scr.get("records", []) or [])
    k = res.get("k")
    scale = res.get("scale") or prim.get("estimand") or "effect"
    est = _fmt(res.get("estimate"))
    lo, hi = _fmt(res.get("ci_low")), _fmt(res.get("ci_high"))
    g = review.get("grade") or {}
    cert = _grade_mod.render_certainty(g) if g else ""
    _grade_not_rateable = bool(g.get("not_rateable_reason"))
    sens = review.get("rob_sensitivity") or {}
    prot = review.get("protocol") or {}
    sha = str(prot.get("sha") or "")[:12]
    # PREREGISTRATION vs BUILD (audit 20): only claim "committed before synthesis" when a protocol-ONLY
    # prospective commit actually exists; otherwise state honestly that precedence is not demonstrated.
    _pre = (review.get("reproduction") or {}).get("preregistration") or {}
    # RETRACTION #2: a protocol that already contains PMIDs/NCTs/results is a timestamped record, not a
    # prospective registration (fails PRISMA 24a regardless of a protocol-only SHA).
    import re as _re
    _proto_has_results = bool(_re.search(r"\bNCT\d{8}\b|\bPMID[:\s]|\b\d{7,8}\b|hazard ratio|95%\s*CI|"
                                         r"odds ratio|rate ratio", (prot.get("text", "") or "")))
    _prospective = bool(_pre.get("prospective")) and not _proto_has_results
    _pre_sha = str(_pre.get("sha") or "")[:12]
    _build_sha = str(_pre.get("build_sha") or prot.get("sha") or "")[:12]
    if _prospective:
        reg_phrase = (f"prospectively registered: the protocol was committed in a protocol-only commit "
                      f"(registration SHA {_e(_pre_sha)}) before synthesis")
        reg_methods = (f"The protocol (protocol-only commit {_e(_pre_sha)}) was committed before any "
                       f"synthesis ran; deterministic replay is from the committed cache, and "
                       f"protocol-SHA byte-for-byte replay is not currently claimed.")
    else:
        reg_phrase = (f"NOT prospectively registered in this repository: the protocol first "
                      f"entered the repository inside a build commit (SHA {_e(_build_sha)}), so precedence of "
                      f"protocol over synthesis is not demonstrated here")
        reg_methods = (f"The protocol first entered the repository inside a build commit (SHA {_e(_build_sha)}); "
                       f"the PICO is fixed, but this repository's history does not demonstrate that the protocol "
                       f"preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed.")
    # RETRACTION propagation: the search claim in Methods must derive from source_status, not be authored.
    _ss = (review.get("search") or {}).get("source_status") or {}
    _aact = _ss.get("Registry-first (AACT)")
    if _aact == "RAN_OK":
        _search_phrase = "The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval."
    else:
        _search_phrase = (f"The registry-first (AACT) adapter did NOT complete for this topic (status "
                          f"{_e(_aact)}); the evidence set was assembled by known-item retrieval, NOT a completed "
                          f"registry-first or systematic search (retracted claim).")
    if review.get("publication_units"):
        absent_counts = _identity_mod.outcome_counts(prim)["absent"]
        n_absent = absent_counts.get("trials", 0)
        absent_phrase = _identity_mod.count_phrase(absent_counts, "trial family")
    else:
        n_absent = len(prim.get("declared_absent_trials", []) or [])
        absent_phrase = f"{n_absent} eligible trial(s)"

    # ---- structured abstract ----
    if res.get("pool_refused"):
        ref = res.get("pool_refused") or {}
        anchor = ref.get("honest_k1_anchor") or {}
        if anchor:
            rem = ", ".join(str(x.get("label")) for x in (ref.get("named_remainders") or []))
            result_sentence = (
                f"The two eligible trials conflict in direction, so no pooled effect is reported. "
                f"The pre-named k=1 anchor is {_e(anchor.get('name') or anchor.get('label'))}: "
                f"{_e(anchor.get('scale') or scale)} {_fmt(anchor.get('effect'))} "
                f"(95% CI {_fmt(anchor.get('ci_low'))} to {_fmt(anchor.get('ci_high'))}); "
                f"the named remainder is {_e(rem)}."
            )
        else:
            result_sentence = (
                "The two eligible trials conflict in direction or interval support, so no pooled effect is "
                "reported; both trial estimates are reported individually."
            )
    elif res.get("suppressed_incompatible"):
        # FAIL CLOSED (audit 23): no pooled result sentence when the estimand pool is incompatible.
        result_sentence = ("The eligible trials report the primary outcome on INCOMPATIBLE estimand classes ("
                           + _e(" + ".join((res.get("estmeasure") or {}).get("canonicals", [])))
                           + "), so no pooled effect is reported: these effect measures are not one "
                           "quantity without an explicit, source-backed conversion. The per-trial estimates "
                           "are reported and each coherent strand must be pooled separately.")
    elif res.get("present") is False or k is None:
        result_sentence = ("No eligible trial reported the primary outcome with an extractable, "
                           "source-verified estimate, so it is declared absent rather than pooled.")
    elif k == 1:
        result_sentence = (f"A single eligible trial contributed an extractable estimate: {scale} "
                           f"{est} (95% CI {lo} to {hi}); with k=1 no between-trial heterogeneity or "
                           f"prediction interval is estimable.")
    elif res.get("pooled_ci_refused"):
        result_sentence = (
            f"Pooling {k} trials retained the point estimate ({scale} {est}), but the registered PM/HKSJ "
            "confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled "
            "significance or null-crossing claim is made."
        )
    else:
        pi = ""
        if res.get("pi_low") is not None:
            pi = f" The 95% prediction interval was {_fmt(res.get('pi_low'))} to {_fmt(res.get('pi_high'))}."
        result_sentence = (f"Pooling {_k_phrase(prim)} gave {scale} {est} (95% CI {lo} to {hi}), "
                           f"random-effects (Paule-Mandel with a Hartung-Knapp interval).{pi}")

    if _grade_mod.membership_incomplete(review):
        result_sentence += " " + _e(_grade_mod.stale_heterogeneity(review))

    _pub = (g.get("domains") or {}).get("publication_bias") or {}
    _pub_certainty_phrase = (
        "publication bias not assessed automatically; any registry ghost census is descriptive until "
        "PICO-scoped"
        if not _pub.get("assessed", False) else
        "publication bias assessed from the trial registry"
    )
    abstract = (
        "<h4>Abstract</h4>"
        f"<p><strong>Question.</strong> {_e(q)}</p>"
        f"<p><strong>Methods.</strong> This review is {reg_phrase}. {_search_phrase} "
        f"Records were screened by two independent rule screeners with adjudication ({n_screened} records "
        f"assessed); every pooled number was extracted down a source ladder and verified against its "
        f"committed source. (Deterministic replay establishes that the same committed cache produces the same "
        f"page; it does not validate search completeness or extraction, and byte-for-byte reproduction from "
        f"the protocol SHA is not currently claimed — see Data availability.)</p>"
        f"<p><strong>Results.</strong> {result_sentence} "
        + (f"{absent_phrase} were declared absent for this outcome (reported reason on each)."
           if n_absent else "")
        + "</p>"
        f"<p><strong>Certainty.</strong> "
        + (f"<strong data-grade-certainty='true'>{_e(cert)}</strong> "
           + (f"(from {g.get('downgrades', 0)} downgrade(s); " if not _grade_not_rateable and not (g.get('unassessed_domains') or []) else "(")
           + f"{_pub_certainty_phrase}; "
           f"unassessed domains: {_e(', '.join(g.get('unassessed_domains') or []))}). "
           + (_e(g.get('not_rateable_reason')) if _grade_not_rateable else ""))
        + "</p>"
    )

    # ---- methods ----
    methods = (
        "<h4>Methods</h4>"
        "<p>This manuscript is generated deterministically from the review object; every number below is "
        "interpolated from a committed field. Deterministic replay is from the committed cache; "
        "protocol-commit byte reproduction is not claimed. "
        f"{reg_methods} {_eligibility_rule_sentence(review)} Two independently implemented rule screeners ran with "
        "adjudication. Each pooled value was located in a committed source, its arms checked for correct "
        "assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value "
        "failing that reconciliation is declared absent, never guessed. Pooling used random effects "
        "(Paule-Mandel &tau;&sup2; with a Hartung-Knapp interval on t with k&minus;1 df; log scale for ratios).</p>"
    )

    # ---- results ----
    forest = _forest(review)
    forest_caption = ("Forest plot of the primary outcome, rendered from the committed per-trial estimates."
                      if res.get("pool_refused") or res.get("pooled_ci_refused") else
                      "Forest plot of the primary outcome, rendered from the committed per-trial estimates "
                      "and the pooled result.")
    results = (
        "<h4>Results</h4>"
        f"<p>{result_sentence}</p>"
        + (f"<figure>{forest}<figcaption class='note'>{forest_caption}</figcaption></figure>" if forest else "")
    )
    suppressed = _rob_sensitivity_mod.suppression_reason(sens, review)
    if not sens.get("full") and (_omit := review.get("rob_sensitivity_omitted")):
        results += (f"<p><strong>Risk-of-bias sensitivity.</strong> Not computed ({_e(_omit.get('reason_code'))}): "
                    f"{_e(_omit.get('reason'))}.</p>")
    elif sens.get("full") and suppressed:
        results += f"<p>{_e(suppressed)}</p>"
    elif sens.get("full"):
        n_rated, n_tr = sens.get("n_rob_rated"), sens.get("n_trials")
        lo_s = sens.get("low_only") or {}
        results += (f"<p><strong>Risk-of-bias sensitivity.</strong> {n_rated} of {n_tr} pooled trials carry a "
                    f"risk-of-bias rating"
                    + ("; no trial is rated high risk. " if not sens.get("any_high") else ". ")
                    + (f"Restricted to low-risk trials the estimate was {scale} {_fmt(lo_s.get('estimate'))} "
                       f"(95% CI {_fmt(lo_s.get('ci_low'))} to {_fmt(lo_s.get('ci_high'))}, k={lo_s.get('k')}); "
                       f"{_rob_sensitivity_mod.low_only_relation_context_text(sens)}" if lo_s.get("estimate") is not None
                       else "a low-risk-only subpool was not estimable.") + "</p>")

    # ---- limitations ----
    lim_bits = []
    imp = g.get("domains", {}).get("imprecision", {})
    if not imp.get("assessed", True):
        lim_bits.append(imp.get("state", "NOT_ASSESSABLE") + ": missing/insufficient "
                        + "; ".join(imp.get("missing_inputs") or ["imprecision support"]))
    elif imp.get("downgrade"):
        lim_bits.append("the confidence interval spans clinical decisions under a registered or GRADE default threshold, or information size is inadequate (imprecision)")
    if g.get("domains", {}).get("inconsistency", {}).get("stale"):
        lim_bits.append(_grade_mod.stale_heterogeneity(review))
    elif g.get("domains", {}).get("inconsistency", {}).get("downgrade"):
        lim_bits.append("between-trial heterogeneity was detected (inconsistency)")
    elif not g.get("domains", {}).get("inconsistency", {}).get("assessed", True):
        lim_bits.append(g["domains"]["inconsistency"].get("basis", "inconsistency is not assessed"))
    if not sens.get("rob_covered", True):
        lim_bits.append("risk of bias is not assessed for every pooled trial (registry-derived coverage)")
    if g.get("domains", {}).get("publication_bias", {}).get("downgrade"):
        lim_bits.append("the trial registry shows unpublished completed trials (possible publication bias)")
    ck = prim.get("compat_key") or {}
    for lim in ck.get("limitations") or []:
        if lim.get("code") == "COMPAT_DIMENSION_HETEROGENEOUS":
            lim_bits.append(lim.get("detail"))
    limitations = (
        "<h4>Limitations</h4>"
        "<p>" + ((_e(_grade_mod.render_certainty(g)) + ": the primary pool mixes ") +
                 "incompatible estimand classes, so no certainty conclusion (and no 'no domain downgraded' "
                 "claim) is made. " if _grade_not_rateable else
                 ("This synthesis is limited in that " + "; ".join(lim_bits) + ". " if lim_bits else
                  "No GRADE domain was downgraded from the machine-computable signals. "))
        + "The comparison with published meta-analyses is one of auditability, not of a claim to more "
        "evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. "
        "Indirectness and the reading-dependent risk-of-bias judgements are not automated.</p>"
    )

    # ---- data availability ----
    data = (
        "<h4>Data availability & reproduction</h4>"
        f"<p>The committed cache and code regenerate this review from the committed cache as-is "
        f"(<code>python scripts/build_topic.py {_e(review.get('slug'))}</code>). "
        "<strong>RETRACTED (round-2): we do NOT currently claim byte-for-byte reproduction from the protocol "
        f"SHA {_e(sha)}.</strong> Direct testing showed the build consumes mutable post-registration state not "
        "pinned in any committed manifest, so re-running at the protocol SHA does not regenerate this page. "
        "'Deterministic replay establishes that the same cache produces the same page; it does not validate "
        "search completeness or extraction.' A pinned build manifest is required before any byte-for-byte or "
        "single-command reproduction claim can be restored.</p>"
    )

    banner = ("<div class='banner'>This manuscript is <strong>generated from the review object</strong> — "
              "every number is interpolated from a committed field, and a gate limb refuses any manuscript "
              "numeral that is not object-derived. It is a machine artefact, not a hand-written paper.</div>")
    return banner + abstract + methods + results + limitations + data
