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


_SEEDED_NOTE = "Registered comparator identity; unextracted quantities and trial membership remain unknown."


def span(text, quote):
    start = text.index(quote)
    return {"start": start, "end": start + len(quote), "quote": quote}


_XREF = re.compile(r'<xref rid="([A-Za-z_-]*?)(\d+)"[^>]*>[^<]*</xref>')


def stated_k_range(fragment: str):
    """The reference ids a JATS sentence cites, when it cites them as ONE citation: a range ('<xref B10>10</xref>-
    <xref B15>15</xref>' -> B10..B15) or a comma list. None when the sentence cites nothing, or mixes prefixes."""
    xs = list(_XREF.finditer(fragment or ""))
    if not xs or len({x.group(1) for x in xs}) != 1:
        return None
    pre = xs[0].group(1)
    out = []
    for i, x in enumerate(xs):
        n = int(x.group(2))
        prev = xs[i - 1] if i else None
        if prev and re.fullmatch(r"\s*[-–—]\s*", fragment[prev.end():x.start()]):
            out += [f"{pre}{j}" for j in range(int(prev.group(2)) + 1, n + 1)]
        else:
            out.append(f"{pre}{n}")
    return out if len(out) == len(set(out)) else None


_XREF_BIBR = re.compile(r"<xref\b[^>]*>.*?</xref>", re.S)


def outcome_list_rids(fragment: str):
    """The reference ids of the citation run that ENDS a sentence fragment -- '<xref ..>2</xref>, <xref ..>3</xref>, ...'
    (each xref may wrap <sup>; ids may contain digits, e.g. 'ehf214298-bib-0002'). None unless the fragment ends in
    a run of bibr xrefs separated only by commas/whitespace, with no repeated id."""
    xs = list(_XREF_BIBR.finditer(fragment or ""))
    if not xs or fragment[xs[-1].end():].strip():
        return None
    run = [xs[-1]]
    for x in reversed(xs[:-1]):
        if fragment[x.end():run[0].start()].strip(" ,\n\t\r"):
            break
        run.insert(0, x)
    rids = []
    for x in run:
        tag = x.group(0)[:x.group(0).index(">") + 1]
        if 'ref-type="bibr"' not in tag or 'rid="' not in tag:
            return None
        rids += tag.split('rid="', 1)[1].split('"', 1)[0].split()
    return rids if len(rids) == len(set(rids)) else None


def ref_author_year(ref: str):
    """('Surname', 'YYYY') of a JATS <ref>: its FIRST <surname> and its <year>; apostrophes normalised. None if absent."""
    s = re.search(r"<surname>(.*?)</surname>", ref or "", re.S)
    y = re.search(r"<year>(\d{4})", ref or "")
    if not s or not y:
        return None
    return (visible_text(s.group(1)).replace("’", "'"), y.group(1))


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
            if alias.get("author_year_row"):
                # V1.0.1 (semaglutide-weight review; scripts/comparator_author_year_rows.py): an included-trial table
                # row that prints only "Surname, year" (no reference link) binds to the ONE <ref> in the same held JATS
                # whose first author and year are those -- re-proved here, uniqueness over the whole reference list
                alias_text = alias_raw.decode("utf-8")
                row = alias["author_year_row"]
                key = ref_author_year(alias["span"]["quote"])
                cell = visible_text((re.search(r"<t[dh][^>]*>(.*?)</t[dh]>", row.get("quote") or "", re.S) or [None, ""])[1])
                if (not validate_span(alias_text, row) or not key or cell.replace("’", "'") != f"{key[0]}, {key[1]}"
                        or sum(1 for rm in re.finditer(r"<ref id=\"[^\"]+\">.*?</ref>", alias_text, re.S)
                               if ref_author_year(rm.group(0)) == key) != 1):
                    raise ValueError("COMPARATOR_PANEL: author-year row does not name exactly one reference")
                continue
            if alias.get("outcome_list_span"):
                # V1.0.1 (sacubitril review; scripts/comparator_outcome_list_members.py): a member of the comparator's
                # OUTCOME-LEVEL trial list -- the located span prints "<k> trials" and then cites exactly k references
                # (a comma list of <xref>s), rid among them; the alias span IS <ref id=rid>
                ol = alias["outcome_list_span"]
                k_pr = alias.get("stated_k")
                cited = outcome_list_rids(ol.get("quote") or "")
                if (not rid or not validate_span(alias_raw.decode("utf-8"), ol) or not isinstance(k_pr, int)
                        or f"{k_pr} trials" not in visible_text(ol.get("quote") or "") or cited is None
                        or len(cited) != k_pr or rid not in cited
                        or not re.match(r'<ref id="%s"' % re.escape(rid), alias["span"]["quote"])
                        or name not in re.sub(r"<[^>]+>", " ", alias["span"]["quote"]).lower()):
                    raise ValueError("COMPARATOR_PANEL: outcome-list member not in the comparator's cited list")
                continue
            if alias.get("stated_k_span"):
                # V1.0.1 (DPP-4 review; scripts/comparator_stated_k_members.py): a member of the comparator's OWN stated
                # trial list -- the located sentence states k and cites one reference range containing rid, and the
                # alias span IS <ref id=rid> (it carries the PMID and the member's printed name)
                sk = alias["stated_k_span"]
                from .extract import stated_trial_count
                k_st, _q = stated_trial_count(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", sk.get("quote") or "")))
                rng = stated_k_range(sk.get("quote")) or []
                if (not rid or not validate_span(alias_raw.decode("utf-8"), sk) or not k_st or rid not in rng
                        or len(rng) != k_st or not re.match(r'<ref id="%s"' % re.escape(rid), alias["span"]["quote"])
                        or name not in re.sub(r"<[^>]+>", " ", alias["span"]["quote"]).lower()):
                    raise ValueError("COMPARATOR_PANEL: stated-k member not in the comparator's cited range")
                continue
            if alias.get("cited_name_span"):
                # V1.0.1 (MRA-HFrEF review; scripts/comparator_trial_tables.py text route): a transcription row bound
                # through the comparator's OWN prose citation -- the located span begins with the row's printed name
                # and ends with the first citation after it, which links rid; the alias span IS <ref id=rid>
                cn = alias["cited_name_span"]
                q = cn.get("quote") or ""
                xs = re.findall(r"<xref\b[^>]*>", q)
                if (not rid or not validate_span(alias_raw.decode("utf-8"), cn) or not q.lower().startswith(name)
                        or len(xs) != 1 or not q.endswith(xs[0]) or 'ref-type="bibr"' not in xs[0]
                        or rid not in (re.search(r'rid="([^"]+)"', xs[0]) or [None, ""])[1].split()
                        or not re.match(r'<ref id="%s"' % re.escape(rid), alias["span"]["quote"])):
                    raise ValueError("COMPARATOR_PANEL: cited-name alias not located as the comparator's own citation")
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


def _fold(s) -> str:
    import unicodedata
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower())


def refuse_misbound_rows(c) -> None:
    """V1.0.1 (esketamine/omega-3 reviews): a row bound to a trial through its OWN citation (linked_rid) is refused when
    the row prints a SURNAME that is not in the cited reference. The omega-3 comparator's table cites every study one
    reference early ('Burr 1989 [23]' -> reference 23 is Begg & Mazumdar; Burr is 24), so all 28 bindings named the
    wrong trial. Acronym rows (HEART-FID) and generic labels ('Trial A') are not surnames; accents are folded
    (Garzon/Garzon). The alias is moved to binding_refused -- never re-guessed -- and the row stays unbound."""
    from .overlap_relation import generic_label
    checked = refused_n = 0
    for m in c.get("trial_set") or []:
        name = (m.get("name_in_source") or m.get("family_id") or "").split()
        first = name[0] if name else ""
        surname = (not generic_label(" ".join(name)) and re.search(r"[a-z]", first) and not re.fullmatch(r"[A-Z0-9-]+", first))
        if not surname:
            continue
        keep, refused = [], []
        for a in m.get("aliases") or []:
            if a.get("linked_rid") and not a.get("table_row_span") and not a.get("stated_k_span"):
                ref = re.sub(r"<[^>]+>", " ", (a.get("span") or {}).get("quote") or "")
                checked += 1
                if _fold(first) and _fold(first) not in _fold(ref):
                    refused_n += 1
                    refused.append({"id": a["id"], "linked_rid": a["linked_rid"],
                                    "why": f"the row prints '{first}' but its cited reference {a['linked_rid']} does not "
                                           f"name that author: '{re.sub(chr(92) + 's+', ' ', ref).strip()[:90]}'"})
                    continue
            keep.append(a)
        if refused:
            m["aliases"] = keep
            m["binding_refused"] = refused
    # a panel whose checkable surname rows MOSTLY cite another author has an unreliable citation column: every
    # citation-bound row in it is refused, acronym rows included (omega-3: 'GISSI-P [25]' -> reference 25 is Eritsland)
    if checked >= 3 and refused_n * 2 >= checked:
        c["citation_column"] = {"state": "UNRELIABLE", "surname_rows_checked": checked, "citing_another_author": refused_n}
        for m in c.get("trial_set") or []:
            keep = []
            for a in m.get("aliases") or []:
                if a.get("linked_rid") and not a.get("table_row_span") and not a.get("stated_k_span"):
                    m.setdefault("binding_refused", []).append(
                        {"id": a["id"], "linked_rid": a["linked_rid"],
                         "why": f"the comparator's table citations are unreliable: {refused_n} of {checked} surname rows "
                                "cite a reference by another author"})
                    continue
                keep.append(a)
            m["aliases"] = keep


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
        refuse_misbound_rows(c)
        from . import comparator_rows
        _rows = comparator_rows.assess(comparator_rows.load(root, slug))
        if _rows and str(c.get("id")) == str(json.loads((Path(root) / "cache" / slug / "comparator_row_checks.json")
                                                          .read_text(encoding="utf-8")).get("comparator_pmid")):
            # V1.0.1 (esketamine review): the comparator's result for OUR outcome pools only some of its rows
            comparator_rows.apply_to_panel(c, _rows, primary)
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
    from .external_checkpoints import render as _checkpoints_block
    parts.append(_checkpoints_block(review.get("external_checkpoints")))
    from .comparator_rows import render as _rows_block
    parts.append(_rows_block((review.get("comparator") or {}).get("row_checks")))
    from .comparator_analysis import render as _analysis_block
    parts.append(_analysis_block((review.get("comparator") or {}).get("analysis")))
    from .comparator_display import render as _display_block
    parts.append(_display_block((review.get("comparator") or {}).get("display_check")))
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
    from .comparator_named import render as _named_block
    parts.append(_named_block(review.get("comparator_named")))
    for c in review.get("comparator_panel", []):
        note = c["scope_note"]
        if c.get("trial_set") and note == _SEEDED_NOTE:
            # V1.0.1 (PCSK9 review): the seeded note said membership was unknown on pages whose trial set IS
            # enumerated from a located table -- the note must not contradict the overlap rendered above it
            note = (f"Registered comparator identity; trial membership enumerated ({len(c['trial_set'])} rows, located "
                    f"spans); unextracted quantities remain unknown.")
        parts.append(f"<article data-comparator='{esc(c['id'])}'><h4>{esc(c['citation'])}</h4><p>{esc(note)}</p>")
        cc = c.get("citation_column") or {}
        refused = [m for m in c.get("trial_set") or [] if m.get("binding_refused")]
        if cc.get("state") == "UNRELIABLE":
            parts.append(f"<p><strong>Citation column UNRELIABLE</strong>: {esc(cc['citing_another_author'])} of "
                         f"{esc(cc['surname_rows_checked'])} rows that print an author cite a reference by another author; "
                         f"no row of this comparator is bound to a trial through its citation ({esc(len(refused))} refused).</p>")
        elif refused:
            parts.append("<p>Row bindings refused (the row's printed author is not in its cited reference): "
                         + esc("; ".join(m["family_id"] for m in refused)) + ".</p>")
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
            withheld = (((review.get("comparator") or {}).get("row_checks") or {}).get("numerical_validation")
                        or {}).get("state") == "WITHHELD"
            if high_overlap(c, review) and not withheld:
                parts.append("<p>" + esc(adjudication(c) or "Overlapping evidence sets: agreement is sensitivity to analytic membership.") + "</p>")
        else:
            parts.append("<p>Trial set NOT ENUMERATED; overlap unknown.</p>")
        parts.append("</article>")
    return "".join(parts)
