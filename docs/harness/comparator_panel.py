"""Held-document comparator panels. Membership is recomputed, never imported.

Source spans use character offsets in the UTF-8 decoded document. Unknown
endpoint compatibility stays unknown; a matching family alone is insufficient.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

from .membership import canonical_trial_key

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r"independent\s+corroboration|independently\s+corroborat\w*|external\s+validation\s+confirms|\breplicat\w*", re.I)
ADJUDICATION = ("Different defensible trial-set definitions repeatedly yield a class average near {x}; "
                "heterogeneity estimates are considerably more sensitive to evidence-set definition. "
                "This is robustness to analytic membership, not independent replication.")
FACTS = ("k", "effect", "ci", "i2", "pi", "method")


def span(text, quote):
    start = text.index(quote)
    return {"start": start, "end": start + len(quote), "quote": quote}


def validate_span(text, source):
    return (isinstance(source, dict) and isinstance(source.get("start"), int)
            and isinstance(source.get("end"), int) and source["start"] >= 0
            and source["end"] > source["start"]
            and text[source["start"]:source["end"]] == source.get("quote"))


def validate(comparator, root=ROOT):
    """Refuse missing, changed, unlocated or out-of-tree evidence."""
    c = comparator
    if not c.get("held"):
        if c.get("trial_set") or any(c.get(k) is not None for k in FACTS):
            raise ValueError("COMPARATOR_PANEL: NOT HELD comparator carries facts")
        return
    path = (Path(root) / c["document_ref"]).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError("COMPARATOR_PANEL: document outside repository")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != c["document_sha256"]:
        raise ValueError("COMPARATOR_PANEL: held document hash mismatch")
    text = raw.decode("utf-8")
    for key in FACTS:
        fact = c.get(key)
        if fact is not None and (not isinstance(fact, dict) or not validate_span(text, fact.get("span"))):
            raise ValueError(f"COMPARATOR_PANEL: unlocated {key}")
        if fact is not None and key != "method":
            values = fact["value"] if isinstance(fact["value"], list) else [fact["value"]]
            for value in values:
                if not re.search(r"(?<![\d.])" + re.escape(str(value)) + r"(?![\d.])", fact["span"]["quote"]):
                    raise ValueError(f"COMPARATOR_PANEL: {key} value absent from its span")
    for trial in c.get("trial_set", []):
        if not trial.get("family_id") or not validate_span(text, trial.get("span")):
            raise ValueError("COMPARATOR_PANEL: unlocated trial family")
        if trial["family_id"].lower() not in trial["span"]["quote"].lower():
            raise ValueError("COMPARATOR_PANEL: family absent from source span")
        if trial.get("endpoint") and not validate_span(text, trial.get("endpoint_span")):
            raise ValueError("COMPARATOR_PANEL: unlocated endpoint")
        for alias in trial.get("aliases", []):
            alias_path = (Path(root) / alias["document_ref"]).resolve()
            if not alias_path.is_relative_to(Path(root).resolve()):
                raise ValueError("COMPARATOR_PANEL: alias outside repository")
            alias_raw = alias_path.read_bytes()
            if hashlib.sha256(alias_raw).hexdigest() != alias["document_sha256"]:
                raise ValueError("COMPARATOR_PANEL: alias source hash mismatch")
            if not validate_span(alias_raw.decode("utf-8"), alias.get("span")):
                raise ValueError("COMPARATOR_PANEL: alias not source backed")
            if (alias["id"] not in alias["span"]["quote"]
                    or trial["family_id"].lower() not in alias["span"]["quote"].lower()):
                raise ValueError("COMPARATOR_PANEL: alias does not bind family and identifier")


def pools(review):
    for o in review.get("outcomes", []):
        result = o.get("result") or {}
        rows = o.get("trials", [])
        if result.get("present") is False or result.get("suppressed_incompatible") or result.get("pool_refused"):
            rows = []
        yield str(o.get("name") or "primary"), rows, o.get("endpoint"), result
    for s in (review.get("strands") or {}).get("strands", []):
        members = s.get("members") or s.get("trials") or []
        rows = [dict(t, id=t.get("pmid") or t.get("nct") or t.get("id") or t.get("trial")) for t in members]
        yield "strand:" + str(s.get("strand") or s.get("name")), rows, s.get("endpoint"), s.get("pool") or {}


def overlaps(comparator, review):
    trials = comparator.get("trial_set") or []
    aliases = {}
    for t in trials:
        family = t["family_id"]
        for key in [family] + [a["id"] for a in t.get("aliases", [])]:
            canon = canonical_trial_key(key)
            if canon in aliases and aliases[canon] != family:
                raise ValueError("COMPARATOR_PANEL: ambiguous family alias")
            aliases[canon] = family
    theirs = {t["family_id"] for t in trials}
    out = []
    def _resolve(t):
        # A pooled row carries several identities (family id, report id, label); the comparator's alias list may
        # know any of them. Try each before falling back to the family id -- keying on the family id alone made
        # every glp1 row "harness only" once rows carried registry-first family ids (Jaccard 0.78 -> 0.0).
        keys = [t.get("family_id"), t.get("id"), t.get("label")]
        for k in keys:
            ck = canonical_trial_key(k) if k else ""
            if ck and ck in aliases:
                return aliases[ck]
        return canonical_trial_key(t.get("family_id") or t.get("id"))
    for name, rows, endpoint, result in pools(review):
        ours = {_resolve(t) for t in rows}
        ours.discard("")
        shared = ours & theirs
        compatible, unknown = [], []
        for t in trials:
            if t["family_id"] not in shared:
                continue
            # Curated endpoint key is bound to the declared outcome name, never guessed from a family.
            expected = (comparator.get("outcome_endpoints") or {}).get(name, endpoint)
            if not t.get("endpoint") or not expected:
                unknown.append(t["family_id"])
            elif t["endpoint"] == expected:
                compatible.append(t["family_id"])
        out.append({"pool": name, "shared": sorted(shared), "harness_only": sorted(ours - theirs),
                    "comparator_only": sorted(theirs - ours),
                    "jaccard": len(shared) / len(ours | theirs) if ours | theirs else None,
                    "contains_pool": bool(ours) and ours <= theirs,
                    "endpoint_compatible_overlap": sorted(compatible), "endpoint_unknown": sorted(unknown),
                    "harness_k": len(ours), "comparator_k": len(theirs)})
    return out


def attach(slug, review, root=ROOT):
    path = Path(root) / "cache" / slug / "comparators.json"
    if not path.exists():
        if (Path(root) / "topics" / (slug + ".json")).exists():
            raise ValueError("COMPARATOR_PANEL: registered topic source panel missing")
        return []  # Legacy test fixtures need not have a registered panel.
    panel = json.loads(path.read_text(encoding="utf-8"))
    for c in panel:
        validate(c, root)
        live = overlaps(c, review) if c.get("trial_set") else []
        if "overlaps" in c:
            raise ValueError("COMPARATOR_PANEL: stored overlap prohibited in source panel")
        c["overlaps"] = live
    return panel


def high_overlap(c, review):
    return any((o["jaccard"] or 0) > 0.5 or o["contains_pool"] for o in overlaps(c, review))


def adjudication(c):
    effect = c.get("effect")
    return ADJUDICATION.format(x=f"{effect['value']:.2f}") if effect else None


def visible_text(markup):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", markup))).strip()


def forbidden_claims(markup, panel=()):
    text = visible_text(markup)
    # Only the exact mandated negative statement is exempt, not arbitrary negations.
    for c in panel:
        sentence = adjudication(c)
        if sentence:
            text = text.replace(sentence, "")
    return [m.group(0) for m in FORBIDDEN.finditer(text)]


def gate_reasons(review, markup):
    panel = review.get("comparator_panel", [])
    reasons = []
    for c in panel:
        live = overlaps(c, review) if c.get("trial_set") else []
        if "overlaps" in c and c["overlaps"] != live:
            reasons.append("COMPARATOR_PANEL: stored overlap disagrees with live pool: " + c["id"])
        if c.get("trial_set") and high_overlap(c, review) and forbidden_claims(markup, panel):
            reasons.append("COMPARATOR_PANEL: independent corroboration claim refused: " + c["id"])
    return reasons


def render(review):
    esc = lambda x: html.escape(str(x))
    parts = ["<h3>Comparator panel</h3><p>MEASURED: overlaps use the live trial families for each outcome and strand. Unknown endpoint compatibility is not counted as compatible.</p>"]
    for c in review.get("comparator_panel", []):
        parts.append(f"<article data-comparator='{esc(c['id'])}'><h4>{esc(c['citation'])}</h4><p>{esc(c['scope_note'])}</p>")
        if not c["held"]:
            parts.append("<p><strong>NOT HELD — identity only</strong></p></article>")
            continue
        parts.append(f"<p>HELD: {esc(c['document_ref'])}{esc('#' + c['document_field']) if c.get('document_field') else ''}; SHA-256 {esc(c['document_sha256'])}</p><dl>")
        for key in FACTS:
            f = c.get(key)
            value = (f"{esc(f['value'])} (characters {f['span']['start']}–{f['span']['end']}: {esc(f['span']['quote'])})"
                     if f else "NOT EXTRACTED from held text")
            parts.append(f"<dt>{esc(key)}</dt><dd>{value}</dd>")
        parts.append("</dl>")
        if c.get("trial_set"):
            parts.append("<table><tr><th>Pool / strand</th><th>Shared</th><th>Harness-only</th><th>Comparator-only</th><th>Jaccard</th><th>Endpoint-compatible overlap</th><th>Endpoint unknown</th></tr>")
            for o in overlaps(c, review):
                values = [o[k] for k in ("pool", "shared", "harness_only", "comparator_only", "jaccard", "endpoint_compatible_overlap", "endpoint_unknown")]
                parts.append("<tr>" + "".join(f"<td>{esc(v)}</td>" for v in values) + "</tr>")
            parts.append("</table>")
            if high_overlap(c, review):
                parts.append("<p>" + esc(adjudication(c) or "Overlapping evidence sets: agreement is sensitivity to analytic membership.") + "</p>")
        else:
            parts.append("<p>Trial set NOT ENUMERATED; overlap unknown.</p>")
        parts.append("</article>")
    return "".join(parts)
