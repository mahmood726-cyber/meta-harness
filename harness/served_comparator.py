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
    if str(config.get("comparator_pmid") or "") != cur or not old or not switch_signed(slug, old, cur, root):
        return None
    pr = a.get("pooled_result") or {}
    if any(pr.get(k) is None for k in ("measure", "estimate", "ci_low", "ci_high")):
        # a SIGNED adoption without its pooled result is a broken register, not 'no adoption' (which would re-enable the
        # regex over the comparator's text; codex v8-apply-r2 #2)
        raise ValueError(f"ADOPTION: {slug}: signed switch to {cur} but the adoption record has no complete pooled_result")
    rp = os.path.join(root, "registry", "comparator_selection", f"{slug}.rule.json")
    rule_outcome = (_j(rp).get("protocol_reference") or {}).get("primary_outcome") if os.path.isfile(rp) else None
    return {"estimate": pr["estimate"], "ci_low": pr["ci_low"], "ci_high": pr["ci_high"], "scale": pr["measure"],
            "rule_primary_outcome": rule_outcome,
            "k": pr.get("k"), "outcome_as_printed": pr.get("outcome"),
            "span": ((pr.get("spans") or {}).get("result") or "")[:400],
            "source": f"adoption pooled_result (registry/comparator_selection/{slug}.adoption.json; signed switch, V8)"}


def _norm(x: Any) -> str:
    """Lower-case, a trailing parenthetical qualifier removed ('3-point MACE (CV death, nonfatal MI, ...)'), spacing
    collapsed."""
    import re
    s = " ".join(str(x or "").lower().split())
    return re.sub(r"\s*\([^()]*\)\s*$", "", s).strip()


def adopted_outcome_matches(adopted: dict[str, Any], outcome_name: str) -> bool:
    """The adopted pooled result passed criterion C5 for its rule's PRIMARY outcome, so it may stand for a served
    comparator outcome only when the two NAME THE SAME ENDPOINT: equal once case, spacing and a trailing parenthetical
    qualifier are removed, where ' / ' in the served name separates alternative labels of one outcome ('Total
    cardiovascular events / major vascular events'). Containment is never enough: 'all-cause mortality' is not 'all-cause
    mortality or hospitalization' (codex v8-apply #1 and r2 #1)."""
    r = _norm((adopted or {}).get("rule_primary_outcome"))
    if not r:
        return False
    labels = {_norm(x) for x in str(outcome_name or "").split(" / ")} | {_norm(outcome_name)}
    return r in {x for x in labels if x}
