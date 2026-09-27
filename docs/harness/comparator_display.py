"""Comparator DISPLAY vs CALCULATION (V1.0.1, melatonin review: Ferracioli-Oda 2013, PLoS One, PMID 23691095).

A comparator's forest plot is two things: what it DISPLAYS (row weights, subgroup intervals) and what it CALCULATED (the
pooled estimate). They fail separately. From the rows' own intervals the inverse-variance weights and the fixed-effect
pools are recomputed here:
  * a printed weight that disagrees with its row's reconstructed weight is a COMPARATOR_DISPLAY_ERROR (Smits 2003
    printed 3.97% vs 0.29% reconstructed, Almeida Montes 0.28% vs 3.94% -- a SWAP, detected as such);
  * a subgroup interval the figure prints differently from the text, where the reconstruction agrees with the text, is a
    COMPARATOR_DISPLAY_ERROR in the figure (objective 2.29-7.81 in the figure, 2.29-8.71 in the text and reconstruction);
  * the pooled CALCULATION is judged on its own: FE 7.0606 (4.38-9.74) reconstructed vs 7.06 (4.37-9.75) published
    reproduces within display rounding (registry/positive_controls.json holds it as a positive control).
The comparator's SCOPE is stated from its own words, so 'k = 19 vs our 1' is never read as 18 missing trials of our
question: 19 studies in adults AND children with primary sleep disorders (14 insomnia, 4 delayed sleep phase, 1 REM
sleep behaviour), 15 of them in the sleep-latency plot.

cache/<slug>/comparator_figure_rows.json holds the figure image's sha256 and the rows read from it; every quote is
located in the held comparator JATS.
"""
from __future__ import annotations

import hashlib
import html as _html
import json
import math
import re
from pathlib import Path
from typing import Optional

Z = 1.959963984540054
ROUND_TOL = 0.011          # a figure prints two decimals; a reproduced value within one unit of the last place agrees


class DisplayRefused(ValueError):
    pass


def _norm(s):
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", str(s or "")))).strip()


def load(root, slug) -> Optional[dict]:
    p = Path(root) / "cache" / slug / "comparator_figure_rows.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    fig = doc["figure"]
    if hashlib.sha256((Path(root) / fig["document_ref"]).read_bytes()).hexdigest() != fig["sha256"]:
        raise DisplayRefused(f"{slug}: figure bytes do not match the recorded sha256")
    held = {}
    quotes = [doc.get("model_stated")] + list(doc.get("text_statements") or []) + \
             [(doc.get("scope") or {}).get(k) for k in ("stated_total", "population")]
    for q in [q for q in quotes if q]:
        ref = q["document_ref"]
        held.setdefault(ref, _norm((Path(root) / ref).read_text(encoding="utf-8")))
        if _norm(q["quote"]) not in held[ref]:
            raise DisplayRefused(f"{slug}: quote not located in {ref}: {q['quote'][:60]}")
    return doc


def _validate(rows):
    """REV-R1 (codex review, verified): a reversed interval squares into a valid variance and an empty row list divides
    by zero -- both are refused before anything is computed."""
    if not rows:
        raise DisplayRefused("no figure rows: nothing to reconstruct")
    for r in rows:
        vals = (r.get("effect"), r.get("ci_low"), r.get("ci_high"))
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in vals):
            raise DisplayRefused(f"row {r.get('label')!r}: effect/interval not finite numbers")
        if not (r["ci_low"] < r["ci_high"] and r["ci_low"] <= r["effect"] <= r["ci_high"]):
            raise DisplayRefused(f"row {r.get('label')!r}: interval {r['ci_low']} to {r['ci_high']} does not order around {r['effect']}")


def _fe(rows):
    w = [1.0 / (((r["ci_high"] - r["ci_low"]) / (2 * Z)) ** 2) for r in rows]
    m = sum(wi * r["effect"] for wi, r in zip(w, rows)) / sum(w)
    se = 1.0 / math.sqrt(sum(w))
    return m, m - Z * se, m + Z * se, w


def _agree(a, b):
    return all(abs(x - y) <= ROUND_TOL for x, y in zip(a, b))


def assess(doc: Optional[dict]) -> Optional[dict]:
    if not doc:
        return None
    rows = doc["rows"]
    _validate(rows)
    m, lo, hi, w = _fe(rows)
    tw = sum(w)
    recon = [100 * wi / tw for wi in w]
    bad = [i for i, (r, rp) in enumerate(zip(rows, recon)) if abs(r["printed_weight_pct"] - rp) > max(0.5, 0.25 * rp)]
    errors = []
    swapped = set()
    for i in bad:
        for j in bad:
            if i < j and abs(rows[i]["printed_weight_pct"] - recon[j]) <= 0.1 and abs(rows[j]["printed_weight_pct"] - recon[i]) <= 0.1:
                swapped |= {i, j}
                errors.append({"kind": "ROW_WEIGHTS_SWAPPED", "rows": [rows[i]["label"], rows[j]["label"]],
                               "printed": [rows[i]["printed_weight_pct"], rows[j]["printed_weight_pct"]],
                               "reconstructed": [round(recon[i], 2), round(recon[j], 2)]})
    for i in bad:
        if i not in swapped:
            errors.append({"kind": "ROW_WEIGHT_MISPRINTED", "rows": [rows[i]["label"]], "printed": [rows[i]["printed_weight_pct"]],
                           "reconstructed": [round(recon[i], 2)]})
    pools = {"Overall": (m, lo, hi)}
    for g in sorted({r.get("subgroup") for r in rows if r.get("subgroup")}):
        gm, gl, gh, _ = _fe([r for r in rows if r.get("subgroup") == g])
        pools[g] = (gm, gl, gh)
    text = {s["pool"]: s for s in doc.get("text_statements") or []}
    for name, pr in sorted((doc.get("printed_pools") or {}).items()):
        fig = (pr["effect"], pr["ci_low"], pr["ci_high"])
        rec = pools.get(name)
        tx = text.get(name)
        if rec and not _agree(fig, rec):
            txv = (tx["effect"], tx["ci_low"], tx["ci_high"]) if tx else None
            errors.append({"kind": "FIGURE_POOL_DISAGREES", "pool": name, "figure": list(fig),
                           "text": list(txv) if txv else None, "reconstructed": [round(x, 4) for x in rec],
                           "text_agrees_with_reconstruction": bool(txv and _agree(txv, rec)),
                           "text_quote": tx["quote"] if tx else None})
    pub = doc["printed_pools"]["Overall"]
    calc = {"published": [pub["effect"], pub["ci_low"], pub["ci_high"]], "reconstructed": [round(m, 4), round(lo, 4), round(hi, 4)],
            "state": "CALCULATION_REPRODUCED" if _agree((pub["effect"], pub["ci_low"], pub["ci_high"]), (m, lo, hi)) else "CALCULATION_NOT_REPRODUCED",
            "tolerance": f"{ROUND_TOL} (two-decimal display rounding)", "model": "fixed effect, inverse variance, from the rows' printed intervals"}
    sc = doc.get("scope") or {}
    return {"state": "COMPARATOR_DISPLAY_ERROR" if errors else "DISPLAY_CONSISTENT", "display_errors": errors,
            "calculation": calc, "reconstructed_weights": [{"row": r["label"], "printed": r["printed_weight_pct"],
                                                              "reconstructed": round(x, 2)} for r, x in zip(rows, recon)],
            "figure": {k: doc["figure"][k] for k in ("label", "document_ref", "sha256", "read_by", "licence")},
            "scope": {"stated_total": sc.get("stated_total"), "population": sc.get("population"),
                      "outcome_rows": sc.get("outcome_rows"),
                      "reading": ("the comparator's set is not a list of trials missing from ours: its scope is its own "
                                  "(quoted above); only trials inside our question could be missing")}}


def render(a: Optional[dict]) -> str:
    if not a:
        return ""
    e = lambda s: _html.escape(str(s), quote=True)  # noqa: E731
    items = []
    for x in a["display_errors"]:
        if x["kind"] == "ROW_WEIGHTS_SWAPPED":
            items.append(f"<li><code>COMPARATOR_DISPLAY_ERROR</code> weights swapped: {e(x['rows'][0])} printed {e(x['printed'][0])}% "
                         f"(reconstructed {e(x['reconstructed'][0])}%), {e(x['rows'][1])} printed {e(x['printed'][1])}% "
                         f"(reconstructed {e(x['reconstructed'][1])}%)</li>")
        elif x["kind"] == "ROW_WEIGHT_MISPRINTED":
            items.append(f"<li><code>COMPARATOR_DISPLAY_ERROR</code> {e(x['rows'][0])}: printed {e(x['printed'][0])}%, "
                         f"reconstructed {e(x['reconstructed'][0])}%</li>")
        else:
            items.append(f"<li><code>COMPARATOR_DISPLAY_ERROR</code> {e(x['pool'])} pool: figure {e(x['figure'])}, text "
                         f"{e(x['text'])}, reconstructed {e(x['reconstructed'])}"
                         + (" (the text and the reconstruction agree: the figure is wrong)" if x["text_agrees_with_reconstruction"] else "")
                         + "</li>")
    c = a["calculation"]
    sc = a["scope"]
    scope = ""
    if sc.get("stated_total"):
        scope = (f"<p><strong>Scope, in the comparator's words:</strong> &ldquo;{e(sc['stated_total']['quote'])}&rdquo; "
                 f"Population: &ldquo;{e((sc.get('population') or {}).get('quote'))}&rdquo; "
                 f"{e((sc.get('outcome_rows') or {}).get('k'))} studies are in its sleep-latency plot. {e(sc['reading'])}.</p>")
    return ("<div class='comparator-display'><h5>Comparator display vs calculation (forest plot re-derived from its own rows)</h5>"
            + scope + (f"<ul>{''.join(items)}</ul>" if items else "<p>No display error found.</p>")
            + f"<p>Calculation: <code>{e(c['state'])}</code> &mdash; published {e(c['published'])}, reconstructed "
            f"{e(c['reconstructed'])} ({e(c['model'])}; tolerance {e(c['tolerance'])}). A display error is not a calculation "
            f"error; each is judged on its own.</p><p class='small'>Rows read from {e(a['figure']['label'])} "
            f"({e(a['figure']['document_ref'])}, sha256 {e(a['figure']['sha256'][:16])}&hellip;; {e(a['figure']['licence'])}) by "
            f"{e(a['figure']['read_by'])}.</p></div>")
