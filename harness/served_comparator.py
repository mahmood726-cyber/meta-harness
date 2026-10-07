"""The comparator a SERVED page names. The binding lane adopted replacement comparators for five topics (5 Oct,
pre-registered rules; registry/comparator_selection/<slug>.adoption.json), changing topics/<slug>.json comparator_pmid
and cache/<slug>/comparators.json (the old record kept under 'replaces'). The G1 tracker works against the adopted
comparator; a SERVED page keeps naming its previous comparator until Mahmood signs that switch
(registry/comparator_switch_signatures.json, packet V8). A served comparator is a served claim: it changes only by
signature, like a served number."""
from __future__ import annotations

import copy
import json
import os
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIGS = os.path.join(ROOT, "registry", "comparator_switch_signatures.json")
ADOPT = os.path.join(ROOT, "registry", "comparator_selection", "{slug}.adoption.json")


def _j(p: str) -> dict:
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def switch_signed(slug: str, frm: str, to: str, root: str = ROOT) -> bool:
    p = os.path.join(root, "registry", "comparator_switch_signatures.json")
    sig = ((_j(p).get("switches") or {}).get(slug) or {}) if os.path.exists(p) else {}
    return sig.get("state") == "SEEN_AND_SIGNED" and str(sig.get("from")) == str(frm) and str(sig.get("to")) == str(to)


def unsigned_switch(slug: str, adopted: str, root: str = ROOT) -> str | None:
    """The RETIRED comparator PMID while the switch to `adopted` is unsigned, else None."""
    p = os.path.join(root, "registry", "comparator_selection", f"{slug}.adoption.json")
    if not slug or not os.path.exists(p):
        return None
    a = _j(p)
    old = str((a.get("retired") or {}).get("comparator_pmid") or "")
    if str(a.get("comparator_pmid")) != str(adopted) or not old:
        return None
    return None if switch_signed(slug, old, adopted, root) else old


def served_config(slug: str, config: dict[str, Any], root: str = ROOT) -> dict[str, Any]:
    old = unsigned_switch(slug, str(config.get("comparator_pmid") or ""), root)
    if not old:
        return config
    out = dict(config)
    out["comparator_pmid"] = old
    return out


def served_panel(slug: str, panel: list[dict[str, Any]], root: str = ROOT) -> list[dict[str, Any]]:
    """The panel record of the RETIRED comparator (its 'replaces' entry, as it was served) while the switch is
    unsigned; the panel unchanged otherwise. Fail closed: an unsigned switch with no 'replaces' record raises."""
    if not panel:
        return panel
    cur = str(panel[0].get("id") or "")
    old = unsigned_switch(slug, cur, root)
    if not old:
        return panel
    rep = next((r for r in panel[0].get("replaces") or [] if str(r.get("id")) == old), None)
    if rep is None:
        raise ValueError(f"COMPARATOR_PANEL: {slug}: unsigned switch {old} -> {cur} but no 'replaces' record for {old}")
    rec = copy.deepcopy(rep)
    rec.pop("retired", None)
    return [rec] + [copy.deepcopy(c) for c in panel[1:]]


def adopted_pooled(slug: str, config: dict[str, Any], root: str = ROOT) -> dict[str, Any] | None:
    """The signed replacement comparator's gated pooled result (its adoption record: numbers verbatim in a quoted span of
    the comparator's own text), or None. Only for the comparator the page is configured with, and only once the switch
    is SIGNED. This, not a regex over the comparator's text, is the 'reported' result a served page shows for it: the
    regex misattributed on two of the five V8 switches (dpp4 0.88 = the SGLT-2 OR in the same sentence; statins 0.72)."""
    p = os.path.join(root, "registry", "comparator_selection", f"{slug}.adoption.json")
    if not slug or not os.path.lexists(p):
        return None
    if not os.path.isfile(p):        # a dangling link / directory is a broken register, never 'no adoption' (codex v8-apply #3)
        raise ValueError(f"ADOPTION: {p} exists but is not a readable file")
    a = _j(p)
    cur, old = str(a.get("comparator_pmid") or ""), str((a.get("retired") or {}).get("comparator_pmid") or "")
    if str(config.get("comparator_pmid") or "") != cur:
        return None
    if not old:
        # an adoption for the configured comparator with no retired identity cannot be tied to a signature: broken,
        # never 'absent' (which would re-enable the regex; codex v8-apply-r5 #3)
        raise ValueError(f"ADOPTION: {slug}: adoption of {cur} names no retired comparator")
    if not switch_signed(slug, old, cur, root):
        return None
    pr = a.get("pooled_result") or {}
    if any(pr.get(k) is None for k in ("measure", "estimate", "ci_low", "ci_high")):
        # a SIGNED adoption without its pooled result is a broken register, not 'no adoption' (which would re-enable the
        # regex over the comparator's text; codex v8-apply-r2 #2)
        raise ValueError(f"ADOPTION: {slug}: signed switch to {cur} but the adoption record has no complete pooled_result")
    # the numbers must be the span's own: estimate and both bounds verbatim in the quoted result span (Unicode minus read
    # as '-'). A record whose numbers contradict its span is broken, never served (codex v8-apply-r8 #1)
    span = ((pr.get("spans") or {}).get("result") or "").replace("−", "-")
    if not _span_states(span, pr["estimate"], pr["ci_low"], pr["ci_high"]):
        raise ValueError(f"ADOPTION: {slug}: pooled_result is not stated in its quoted result span as estimate, then "
                         f"lower, then upper bound")
    rp = os.path.join(root, "registry", "comparator_selection", f"{slug}.rule.json")
    rule_outcome = (_j(rp).get("protocol_reference") or {}).get("primary_outcome") if os.path.isfile(rp) else None
    if not rule_outcome:
        # without its rule the adopted value cannot be tied to an endpoint: broken, never silently empty (codex r3 #3)
        raise ValueError(f"ADOPTION: {slug}: signed switch to {cur} but its rule (primary outcome) is missing")
    return {"estimate": pr["estimate"], "ci_low": pr["ci_low"], "ci_high": pr["ci_high"], "scale": pr["measure"],
            "rule_primary_outcome": rule_outcome,
            "k": pr.get("k"), "outcome_as_printed": pr.get("outcome"),
            "span": ((pr.get("spans") or {}).get("result") or "")[:400],
            "source": f"adoption pooled_result (registry/comparator_selection/{slug}.adoption.json; signed switch, V8)"}


def _norm(x: Any) -> str:
    """Lower-case, spacing collapsed. Nothing else: every looser rule tried merged distinct endpoints -- containment
    ('mortality' in 'mortality or hospitalization'), dropping a parenthetical ('(30 days)' vs '(1 year)'), dropping a
    digit-free one ('(fatal)' vs '(nonfatal)') -- codex v8-apply rounds 1, 2, 3, 4."""
    return " ".join(str(x or "").lower().split())


def adopted_outcome_matches(adopted: dict[str, Any], outcome_name: str) -> bool:
    """The adopted pooled result passed criterion C5 for its rule's PRIMARY outcome, so it may stand for a served
    comparator outcome only when the two names are EQUAL (case and spacing ignored), where ' / ' in the served name
    separates alternative labels of one outcome ('Total cardiovascular events / major vascular events'). Where the names
    differ in any other way the comparator's reported result is left ABSENT -- never matched by a heuristic and never
    mapped by hand (Mahmood's rule: nothing hand-entered)."""
    r = _norm((adopted or {}).get("rule_primary_outcome"))
    if not r:
        return False
    labels = {_norm(x) for x in str(outcome_name or "").split(" / ")} | {_norm(outcome_name)}
    return r in {x for x in labels if x}


_NUM_TOKEN = None


def _tokens(text: str) -> list[float]:
    """The span's numbers as WHOLE tokens, in order. A '-' is a sign only where no letter, digit or '.' stands before it
    ('MD=-4.09', '[-8.45'), so '0.7-0.9' is a range and 'DPP-4' is 4. A token followed by '%' (a CI level, a rate) is
    not a result number and is dropped."""
    import re
    global _NUM_TOKEN
    if _NUM_TOKEN is None:
        _NUM_TOKEN = re.compile(r"(?<![\w.])(-?)(\d+(?:\.\d+)?|\.\d+)(?![\d.])")
    out = []
    for m in _NUM_TOKEN.finditer(text):
        if m.end() < len(text) and text[m.end()] == "%":
            continue
        body = m.group(2) if not m.group(2).startswith(".") else "0" + m.group(2)
        out.append(float(m.group(1) + body))
    return out


def _span_states(span: str, est: Any, lo: Any, hi: Any) -> bool:
    """The span STATES this result: three CONSECUTIVE number tokens equal to the estimate, the lower bound and the upper
    bound, exactly (never a rounding: 0.876 is not a printed 0.88; never a fragment of another token; never an estimate
    from one result beside another result's interval), and lower <= estimate <= upper. Four hand-built matchers each
    failed review (codex v8-apply r8, r9, r10); this one only compares whole tokens."""
    try:
        trip = (float(est), float(lo), float(hi))
    except (TypeError, ValueError):
        return False
    if not (trip[1] <= trip[0] <= trip[2]):
        return False
    t = _tokens(span)
    return any(tuple(t[i:i + 3]) == trip for i in range(len(t) - 2))
