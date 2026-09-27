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
    # V1.0.1: a trial set may be located in its own held document (e.g. the comparator's PMC JATS, whose table rows
    # link each included study to a reference with its PMID/DOI) instead of the panel's text; and a row may name its
    # trial by the surname printed in the source (`name_in_source`) while `family_id` stays the unique key (two
    # "Imazio" rows are two trials).
    ts_doc = c.get("trial_set_document")
    if ts_doc:
        ts_path = (Path(root) / ts_doc["document_ref"]).resolve()
        if not ts_path.is_relative_to(Path(root).resolve()):
            raise ValueError("COMPARATOR_PANEL: trial-set document outside repository")
        ts_raw = ts_path.read_bytes()
        if hashlib.sha256(ts_raw).hexdigest() != ts_doc["document_sha256"]:
            raise ValueError("COMPARATOR_PANEL: trial-set document hash mismatch")
        ts_text = ts_raw.decode("utf-8")
    else:
        ts_text = text
    for trial in c.get("trial_set", []):
        name = (trial.get("name_in_source") or trial.get("family_id") or "").lower()
        if not trial.get("family_id") or not validate_span(ts_text, trial.get("span")):
            raise ValueError("COMPARATOR_PANEL: unlocated trial family")
        if not name or name not in trial["span"]["quote"].lower():
            raise ValueError("COMPARATOR_PANEL: family absent from source span")
        if trial.get("endpoint") and not validate_span(ts_text, trial.get("endpoint_span")):
            raise ValueError("COMPARATOR_PANEL: unlocated endpoint")
        if trial.get("bib_key"):
            # a reference with no PMID/DOI is identified by journal/year/volume/first page, each printed in its
            # own located reference span
            ref = trial.get("bib_key_span") or {}
            if not validate_span(ts_text, ref):
                raise ValueError("COMPARATOR_PANEL: unlocated bibliographic key")
            _, _journal, year, volume, fpage = trial["bib_key"].split(":")
            if not all(v and v in ref["quote"] for v in (year, volume, fpage)):
                raise ValueError("COMPARATOR_PANEL: bibliographic key not printed in its reference")
        for alias in trial.get("aliases", []):
            alias_path = (Path(root) / alias["document_ref"]).resolve()
            if not alias_path.is_relative_to(Path(root).resolve()):
                raise ValueError("COMPARATOR_PANEL: alias outside repository")
            alias_raw = alias_path.read_bytes()
            if hashlib.sha256(alias_raw).hexdigest() != alias["document_sha256"]:
                raise ValueError("COMPARATOR_PANEL: alias source hash mismatch")
            if not validate_span(alias_raw.decode("utf-8"), alias.get("span")):
                raise ValueError("COMPARATOR_PANEL: alias not source backed")
            if alias["id"] not in alias["span"]["quote"]:
                raise ValueError("COMPARATOR_PANEL: alias does not bind family and identifier")
            rid = alias.get("linked_rid")
            if alias.get("table_row_span"):
                # V1.0.1 (scripts/comparator_row_citations.py jats): a name-only row bound through the comparator's own
                # JATS table -- the located table row names the row's SURNAME and cites rid; the <ref id=rid> carries
                # the identifier AND the row's YEAR (two 'Young' rows are told apart by their references' years)
                alias_text = alias_raw.decode("utf-8")
                row = alias["table_row_span"]
                surname = name.split()[0]
                year = (re.search(r"\b(19|20)\d{2}\b", trial["family_id"]) or [None])[0]
                row_plain = re.sub(r"<[^>]+>", " ", row.get("quote") or "").lower()
                if (not rid or not validate_span(alias_text, row) or surname not in row_plain.split()
                        or not any(rid in m.split() for m in re.findall(r'rid="([^"]+)"', row["quote"]))
                        or not re.match(r'<ref id="%s"' % re.escape(rid), alias["span"]["quote"])
                        or (year and year not in alias["span"]["quote"])):
                    raise ValueError("COMPARATOR_PANEL: alias table row / reference / year not located")
                continue
            if rid:
                # bound by the row's own reference link: the located row cites rid, and the alias span IS <ref id=rid>
                cites = any(rid in m.split() for m in re.findall(r'rid="([^"]+)"', trial["span"]["quote"]))
                if not cites or not re.match(r'<ref id="%s"' % re.escape(rid), alias["span"]["quote"]):
                    raise ValueError("COMPARATOR_PANEL: alias reference link not located in the row and its reference")
            elif name not in alias["span"]["quote"].lower():
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
    from . import comparator_models
    figures = comparator_models.load(root, slug)
    primary = next((o.get("name") for o in review.get("outcomes") or [] if o.get("primary")), None)
    for c in panel:
        validate(c, root)
        # V1.0.1 (DOAC-VTE review): a panel may name records.json#comparator_fulltext as its held document only when
        # that text is proved to be the comparator's own (harness/held_text_identity.py)
        if c.get("held") and c.get("document_field") == "comparator_fulltext":
            from . import held_text_identity
            st = held_text_identity.comparator_text_state(
                str(root), slug, json.loads((Path(root) / c["document_ref"]).read_text(encoding="utf-8")))
            if st["state"] != "OWN_TEXT":
                raise ValueError("COMPARATOR_PANEL: held document is not the comparator's own text: " + st.get("why", ""))
        if figures and (str(figures.get("comparator_pmid")) in str(c.get("citation") or "")
                        or str(figures.get("comparator_pmid")) == str(c.get("id") or "")):
            # V1.0.1: model-specific tuples from the comparator's own figure, its internal mismatches, and the
            # figure panel's outcome-level membership (harness/comparator_models.py) -- applied after validation
            comparator_models.apply_to_panel(c, figures, primary, root)
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
    # THE relation word (V1.0.1): one computed object, the same one the index, parity row and manuscript read.
    from .overlap_relation import render_block
    parts.append(render_block((review.get("comparator") or {}).get("overlap_relation")))
    from .comparator_models import render_block as _models_block
    from .overlap_relation import _panel_entry
    parts.append(_models_block(_panel_entry(review) or {}))
    from .comparator_models import render_reported as _reported_block
    from .comparator_identity import render_block as _identity_block
    parts.append(_reported_block(review.get("comparator") or {}))
    parts.append(_identity_block((review.get("comparator") or {}).get("identity") or {}))
    from .outcome_match import render as _outcome_match_block
    parts.append(_outcome_match_block((review.get("comparator") or {}).get("shared_trial_inputs")))
    from .held_text_identity import render as _held_identity_block
    parts.append(_held_identity_block((review.get("comparator") or {}).get("fulltext_identity") or {}))
    from .comparator_network import render as _network_block
    parts.append(_network_block((review.get("comparator") or {}).get("overlap") or {}))
    mp = (review.get("comparator") or {}).get("member_populations") or []
    if mp:
        e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
        parts.append("<div class='comparator-members'><h5>Comparator rows: population read from the trial's own report</h5><ul>"
                     + "".join(f"<li><strong>{e(m['member'])}</strong>: comparator prints &ldquo;{e(m['comparator_prints'])}&rdquo;; "
                               f"<code>{e(m['ef_state'])}</code> from PMID {e(m['report_pmid'])}: &ldquo;{e(m['report_quote'])}&rdquo; "
                               f"&mdash; {e(m['note'])}.</li>" for m in mp) + "</ul></div>")
    for c in review.get("comparator_panel", []):
        parts.append(f"<article data-comparator='{esc(c['id'])}'><h4>{esc(c['citation'])}</h4><p>{esc(c['scope_note'])}</p>")
        if not c["held"]:
            parts.append("<p><strong>NOT HELD — identity only</strong>"
                         + (f" (held text refused: {esc(c['held_refused']['why'])})" if c.get("held_refused") else "")
                         + "</p></article>")
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
