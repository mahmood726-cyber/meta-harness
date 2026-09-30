"""Offline lexical verification of recorded model proposals; never pool admission.

Accepted means printed and typed, NOT that a model's clinical scope mapping is
correct. Null fields are unproposed. Provenance is checked against the held panel,
not against a hash supplied solely by the proposer. Optional field_spans narrow
a field to its own evidence inside the item's contiguous span.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ("outcome_as_printed", "timepoint_as_printed", "measure_as_printed")
POOLED = ("k", "effect", "ci_low", "ci_high", "measure")
TRIAL = ("label", "registration", "pmid", "events_1", "n_1", "events_2", "n_2",
         "effect", "ci_low", "ci_high", "measure")
NUM = r"[+−‐-]?(?:\d+(?:[.·]\d+)?|\.\d+)"
MEASURE = r"(?:HR|ORs|OR|RR|IRR|MD|SMD|WMD|mean difference|Mean difference|Odds Ratio)"
CI = rf"(?:95\s*%\s*(?:confidence interval\s*)?(?:\[?CI\]?|C\.I\.)\s*[:,=]?\s*[\[(]?\s*)?({NUM})\s*(?:to|[–−,-])\s*({NUM})"
EFFECT = re.compile(
    rf"(?<!\w)({MEASURE})(?:\s+were)?[\])]?[\s,:=¼]*(?:of\s+)?({NUM})"
    rf"(?:\s*(?:minutes|points|%)\s*)?[\s,;\[(]*{CI}")
BARE_EFFECT = re.compile(rf"(?<![\w.·])({NUM})\s*[\[(]\s*{CI}\s*[\])]")
K = re.compile(r"(?<![\w.+−‐-])([1-9]\d*)\s+(?:(?:randomized|randomised|controlled|clinical|relevant|remaining|pivotal|phase\s+\d+)\s+)*(?:trials|studies|RCTs|CVOTs)\b", re.I)
RELAYED = re.compile(r"\b(?:relayed|investigator[- ]supplied|personal communication|unpublished data supplied)\b", re.I)


def flat(text):
    return re.sub(r"\s+", " ", text).strip()


def number(token):
    return float(token.replace("−", "-").replace("‐", "-").replace("·", "."))


def parse_estimate(span):
    """A unique labelled estimate; or one bare estimate/CI with no invented measure."""
    hits = list(EFFECT.finditer(span))
    if len(hits) == 1:
        m = hits[0]
        return dict(zip(("measure", "effect", "ci_low", "ci_high"),
                        [m[1], *map(number, m.group(2, 3, 4))]))
    if hits:
        return {}
    hits = list(BARE_EFFECT.finditer(span))
    if len(hits) == 1:
        return dict(zip(("effect", "ci_low", "ci_high"), map(number, hits[0].group(1, 2, 3))))
    return {}


# Kept below the proposal glob so legacy replay treats only proposals as proposals.
DOCUMENT_REGISTRY = "evidence/g1_proposals/registry/documents.json"
NORMALISERS = {"text/plain": "plain-whitespace-v1",
               "text/html": "html-text-v1",
               "application/jats+xml": "jats-text-v1"}


class _Element:
    """Minimal ordered HTML tree; text nodes preserve markup boundaries."""

    def __init__(self, name='', attrs=(), parent=None):
        self.name = name
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []

    def get(self, key, default=None):
        return self.attrs.get(key, default)

    def __getitem__(self, key):
        return self.attrs[key]

    def find_all(self, names, recursive=True):
        names = {names} if isinstance(names, str) else set(names)
        result = []
        for child in self.children:
            if isinstance(child, _Element):
                if child.name in names:
                    result.append(child)
                if recursive:
                    result.extend(child.find_all(names))
        return result

    def find_parent(self, names):
        names = {names} if isinstance(names, str) else set(names)
        parent = self.parent
        while parent is not None:
            if parent.name in names:
                return parent
            parent = parent.parent
        return None

    def get_text(self, separator=' ', strip=True, exclude=()):
        parts = []
        excluded = set(exclude) | {'script', 'style', 'template', 'rt', 'rp'}
        def visit(node):
            for child in node.children:
                if isinstance(child, _Element):
                    if child.name not in excluded:
                        visit(child)
                elif child is not None and node.name not in {'script', 'style', 'template', 'rt', 'rp'}:
                    value = child.strip() if strip else child
                    if value:
                        parts.append(value)
        visit(self)
        return separator.join(parts)


class _HTMLTree(HTMLParser):
    VOID = frozenset('area base basefont bgsound br col command embed frame hr img input keygen link meta param source spacer track wbr'.split())

    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.root = _Element()
        self.current = self.root
        self.feed(raw.decode('utf-8') if isinstance(raw, bytes) else raw)
        self.close()

    def handle_starttag(self, tag, attrs):
        child = _Element(tag, attrs, self.current)
        self.current.children.append(child)
        if tag not in self.VOID:
            self.current = child

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        # Even an unmatched closing tag terminates the preceding text node.
        self.current.children.append(None)
        node = self.current
        while node.parent is not None:
            if node.name == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        children = self.current.children
        if children and isinstance(children[-1], str):
            children[-1] += data
        else:
            children.append(data)

    def handle_comment(self, data):
        self.current.children.append(None)

    handle_decl = handle_comment
    handle_pi = handle_comment

    def unknown_decl(self, data):
        if data.startswith('CDATA['):
            self.current.children.extend([None, data[6:], None])


def parse_html(raw):
    return _HTMLTree(raw).root


def normalise_document(text, media_type):
    """Use exactly the same versioned transform for source and span fragments."""
    if media_type == "text/plain":
        return flat(text)
    if media_type == "text/html":
        return flat(parse_html(text).get_text(" ", strip=True))
    if media_type == "application/jats+xml":
        from xml.etree import ElementTree as ET
        # Do not expand document-defined entities or accept external declarations.
        if re.search(r"<!\s*ENTITY\b|<!DOCTYPE[^>]*\[", text, re.I):
            raise ValueError("REFUSED_XML_DECLARATION")
        text = re.sub(r"<!DOCTYPE[^>]*>", "", text, flags=re.I)
        text = re.sub(r"^\s*<\?xml[^?]*\?>", "", text)
        try:
            tree = ET.fromstring("<g1-fragment>" + text + "</g1-fragment>")
        except ET.ParseError as exc:
            raise ValueError("REFUSED_XML_PARSE") from exc
        return flat(" ".join(tree.itertext()))
    raise ValueError("REFUSED_MEDIA_TYPE")


def _registered_source(proposal, root, topic):
    registry = root / DOCUMENT_REGISTRY
    if not registry.is_file():
        raise ValueError("REFUSED_DOCUMENT_UNREGISTERED")
    data = json.loads(registry.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("documents"), list):
        raise ValueError("REFUSED_DOCUMENT_REGISTRY_SCHEMA")
    if not all(isinstance(row, dict) for row in data["documents"]):
        raise ValueError("REFUSED_DOCUMENT_REGISTRY_SCHEMA")
    rows = [row for row in data["documents"] if row.get("document_ref") == proposal.get("document_ref")]
    if not rows:
        raise ValueError("REFUSED_DOCUMENT_UNREGISTERED")
    if len(rows) != 1:
        raise ValueError("REFUSED_DOCUMENT_REGISTRY_AMBIGUOUS")
    row = rows[0]
    if row.get("slug") != proposal["slug"] or row.get("comparator_pmid") != proposal["comparator_pmid"]:
        raise ValueError("REFUSED_REGISTERED_COMPARATOR_IDENTITY")
    media = row.get("media_type")
    if not isinstance(media, str) or media not in NORMALISERS:
        raise ValueError("REFUSED_MEDIA_TYPE")
    if row.get("normaliser") != NORMALISERS[media]:
        raise ValueError("REFUSED_NORMALISER")
    if not isinstance(row.get("licence"), str) or not row["licence"].strip():
        raise ValueError("REFUSED_DOCUMENT_LICENCE_MISSING")
    for key in ("media_type", "normaliser"):
        if key in proposal and proposal[key] != row[key]:
            raise ValueError("REFUSED_" + key.upper() + "_MISMATCH")
    sha = row.get("sha256")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ValueError("REFUSED_REGISTERED_SHA256_INVALID")
    if proposal.get("document_sha256") != sha:
        raise ValueError("REFUSED_DOCUMENT_SHA256_MISMATCH")
    ref = row["document_ref"]
    path = (root / ref).resolve()
    if Path(ref).is_absolute() or ".." in Path(ref).parts or not path.is_relative_to(root):
        raise ValueError("REFUSED_DOCUMENT_PATH")
    if not path.is_file():
        raise ValueError("REFUSED_REGISTERED_DOCUMENT_MISSING")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError("REFUSED_SHA256_MISMATCH")
    normalise = lambda value: normalise_document(value, media)
    text = normalise(raw.decode("utf-8"))
    # Carry only hash-verified bytes, without changing the existing source API.
    if media in {"text/html", "application/jats+xml"}:
        normalise.table_source = (raw.decode("utf-8"), media)
    return text, text, topic, normalise


def _source(proposal, root):
    slug = proposal.get("slug")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ValueError("REFUSED_INVALID_SLUG")
    topic = json.loads((root / "topics" / (slug + ".json")).read_text(encoding="utf-8"))
    panels = json.loads((root / "cache" / slug / "comparators.json").read_text(encoding="utf-8"))
    pmid = str(proposal.get("comparator_pmid", ""))
    panels = [p for p in panels if str(p.get("id")) == pmid or
              re.search(r"\bPMID\s+" + re.escape(pmid) + r"\b", p.get("citation", ""))]
    if not re.fullmatch(r"\d{6,9}", pmid) or len(panels) != 1 or pmid != str(topic.get("comparator_pmid")):
        raise ValueError("REFUSED_COMPARATOR_IDENTITY")
    panel = panels[0]
    if panel.get("held") is not True:
        raise ValueError("REFUSED_DOCUMENT_NOT_HELD")
    if proposal.get("document_ref") != panel.get("document_ref"):
        return _registered_source(proposal, root, topic)
    for key in ("document_ref", "document_sha256"):
        if not isinstance(proposal.get(key), str) or proposal[key] != panel.get(key):
            raise ValueError("REFUSED_" + key.upper() + "_MISMATCH")
    path = (root / panel["document_ref"]).resolve()
    if not path.is_relative_to((root / "cache").resolve()) or not path.is_file():
        raise ValueError("REFUSED_DOCUMENT_PATH")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != panel["document_sha256"]:
        raise ValueError("REFUSED_SHA256_MISMATCH")
    text = flat(raw.decode("utf-8"))
    allowed = text
    if path.suffix == ".json":
        records = json.loads(raw).get("records", [])
        rows = [r for r in records if str(r.get("id")) == pmid and r.get("id_type") == "pmid"]
        if len(rows) != 1:
            raise ValueError("REFUSED_COMPARATOR_RECORD_AMBIGUOUS")
        # Both raw-byte text containment and the selected record are required.
        allowed = flat(rows[0].get("abstract", ""))
    return text, allowed, topic, flat


def _schema(p):
    if not isinstance(p, dict):
        return "REFUSED_PROPOSAL_TYPE"
    required = {"slug", "comparator_pmid", "document_ref", "document_sha256", "proposed_by",
                "scope_note", "primary_scope", "pooled", "trials", "not_found"}
    if not required.issubset(p):
        return "REFUSED_MISSING_KEYS:" + ",".join(sorted(required - p.keys()))
    if not all(isinstance(p[k], str) and p[k].strip() for k in
               ("proposed_by", "scope_note", "comparator_pmid")):
        return "REFUSED_METADATA_TYPE"
    if not isinstance(p["not_found"], list) or not all(isinstance(x, str) for x in p["not_found"]):
        return "REFUSED_NOT_FOUND_TYPE"
    if not isinstance(p["trials"], list):
        return "REFUSED_TRIALS_TYPE"
    if p.get("trial_set_scope", "included_studies_only") not in {"selected_outcome", "included_studies_only"}:
        return "REFUSED_TRIAL_SET_SCOPE"
    if type(p.get("trial_set_complete", False)) is not bool:
        return "REFUSED_COMPLETENESS_TYPE"
    for item, fields in [(p["primary_scope"], SCOPE), (p["pooled"], POOLED)] + [(r, TRIAL) for r in p["trials"]]:
        if not isinstance(item, dict) or not set(fields).issubset(item) or not isinstance(item.get("span"), str):
            return "REFUSED_ITEM_SCHEMA"
        allowed = set(fields) | {"span", "field_spans"}
        if set(item) - allowed:
            return "REFUSED_UNKNOWN_ITEM_FIELDS:" + ",".join(sorted(set(item) - allowed))
        fs = item.get("field_spans", {})
        if not isinstance(fs, dict) or set(fs) - set(fields) or not all(isinstance(s, str) for s in fs.values()):
            return "REFUSED_FIELD_SPANS_SCHEMA"
    return None


def _reparse(key, value, span):
    if key in {"effect", "ci_low", "ci_high", "k", "events_1", "n_1", "events_2", "n_2"}:
        if type(value) not in (int, float) or not math.isfinite(value):
            return "REFUSED_NONFINITE_OR_NONNUMERIC"
    if key in {"k", "events_1", "n_1", "events_2", "n_2"}:
        if type(value) is not int or value < (1 if key in {"k", "n_1", "n_2"} else 0):
            return "REFUSED_COUNT_TYPE_OR_RANGE"
        if key == "k":
            hits = [int(m[1]) for m in K.finditer(span)]
        else:
            hits = [int(m[1].replace(",", "")) for m in re.finditer(
                rf"\b{re.escape(key)}\s*[:=]\s*(\d[\d,]*)\b", span)]
            pairs = list(re.finditer(r"\b(\d+)/(\d+)\s+(?:vs\.?|versus)\s+(\d+)/(\d+)\b", span))
            if len(pairs) == 1 and not hits:
                hits = [int(pairs[0][{"events_1": 1, "n_1": 2, "events_2": 3, "n_2": 4}[key]])]
        return None if len(hits) == 1 and hits[0] == value else "REFUSED_NUMBER_ROLE_NOT_IN_OWN_SPAN"
    if key in {"effect", "ci_low", "ci_high"}:
        parsed = parse_estimate(span)
        if parsed.get(key) != value:
            return "REFUSED_NUMBER_ROLE_NOT_IN_OWN_SPAN"
        if not parsed["ci_low"] <= parsed["effect"] <= parsed["ci_high"]:
            return "REFUSED_INTERVAL_ORDER"
        if parsed.get("measure") in {"RR", "OR", "ORs", "HR", "IRR"} and parsed["ci_low"] <= 0:
            return "REFUSED_RATIO_RANGE"
        return None
    if not isinstance(value, str) or not value.strip():
        return "REFUSED_STRING_TYPE"
    # PDF's quarter glyph is a printed equals-sign artifact, not a word suffix.
    boundary_span = span.replace("¼", "=")
    if not re.search(r"(?<!\w)" + re.escape(flat(value)) + r"(?!\w)", boundary_span):
        return "REFUSED_LITERAL_NOT_IN_OWN_SPAN"
    if key == "registration" and not re.fullmatch(r"NCT\d{8}", value):
        return "REFUSED_REGISTRATION_TYPE"
    if key == "pmid" and not re.search(r"\bPMID\s*[:=]?\s*" + re.escape(value) + r"\b", span):
        return "REFUSED_PMID_ROLE"
    if key in {"measure", "measure_as_printed"} and not re.fullmatch(MEASURE, value):
        return "REFUSED_MEASURE_TYPE"
    return None


def _table_rows(raw, media):
    """Resolve physical cells into a grid; retain header tiers and cell origins.

    Unsupported/malformed tables are reported, never guessed. Positions are
    zero-based indexes in the held document, including header and section rows.
    """
    if media == "application/jats+xml":
        from xml.etree import ElementTree as ET
        normalise_document(raw, media)  # entity/parse policy also applies here
        xml = re.sub(r"<!DOCTYPE[^>]*>", "", raw, flags=re.I)
        xml = re.sub(r"^\s*<\?xml[^?]*\?>", "", xml)
        tree = ET.fromstring("<g1-fragment>" + xml + "</g1-fragment>")
        for node in tree.iter():
            node.tag = node.tag.rsplit("}", 1)[-1]
        raw = ET.tostring(tree, encoding="unicode")
    soup = parse_html(raw)
    rows, errors = [], []
    for ti, table in enumerate(soup.find_all("table")):
        grid, headers, section, built = {}, {}, "", []
        trs = [r for r in table.find_all("tr") if r.find_parent("table") is table]
        try:
            for ri, tr in enumerate(trs):
                cells = tr.find_all(["td", "th"], recursive=False)
                if not cells:
                    continue
                col = 0
                for cell in cells:
                    while (ri, col) in grid:
                        col += 1
                    rs, cs = cell.get("rowspan", "1"), cell.get("colspan", "1")
                    if not re.fullmatch(r"[1-9]\d*", str(rs)) or not re.fullmatch(r"[1-9]\d*", str(cs)):
                        raise ValueError("REFUSED_TABLE_SPAN_SCHEMA")
                    rs, cs = int(rs), int(cs)
                    if ri + rs > len(trs) or cs > 256:
                        raise ValueError("REFUSED_TABLE_SPAN_RANGE")
                    entry = dict(text=flat(cell.get_text(" ", strip=True)), origin=[ri, col])
                    for r in range(ri, ri + rs):
                        for c in range(col, col + cs):
                            if (r, c) in grid:
                                raise ValueError("REFUSED_TABLE_OVERLAPPING_CELLS")
                            grid[r, c] = entry
                    if cell.name == "th" and cell.get("scope") != "row":
                        # Footnote markers are not part of the column's role.
                        label = flat(cell.get_text(" ", strip=True, exclude={"sup", "xref"}))
                        for c in range(col, col + cs):
                            headers.setdefault(c, []).append(label)
                    col += cs
                if all(c.name == "th" and c.get("scope") != "row" for c in cells):
                    continue
                if len(cells) == 1 and int(cells[0].get("colspan", 1)) > 1:
                    section = flat(cells[0].get_text(" ", strip=True))
                    continue
                built.append(dict(table=ti, row=ri, section=section,
                                  cells={c: v for (r, c), v in grid.items() if r == ri},
                                  headers={c: list(v) for c, v in headers.items()},
                                  span=flat(tr.get_text(" ", strip=True))))
            rows.extend(built)
        except ValueError as exc:
            errors.append(dict(table=ti, reason=str(exc)))
    return rows, errors


def _table_count(item, key, value, span, parent, rows, errors, topic):
    """Bind n_1/n_2 to a trial, drug section, arm and patient-count column.

    Tall arm tables only; no aggregation of dose arms and no event inference.
    """
    def column(row, pattern):
        found = [c for c, tiers in row['headers'].items()
                 if tiers and re.fullmatch(pattern, tiers[-1], re.I)]
        return found[0] if len(found) == 1 else None

    drug = topic.get('registry_first', {}).get('intr')
    if not isinstance(drug, str) or not drug.strip():
        return 'REFUSED_TABLE_DRUG_SCOPE_UNBOUND', None
    hits = []
    for row in rows:
        lc = column(row, r'Trial|Study')
        nc = column(row, r'No\. of patients|Number of patients')
        ac = column(row, r'Treatment group|Treatment arm')
        rc = column(row, r'Trial registration No\.?|Registration')
        if None in (lc, nc, ac) or any(c not in row['cells'] for c in (lc, nc, ac)):
            continue
        cells = row['cells']
        if cells[lc]['text'] != item.get('label'):
            continue
        if item.get('registration') is not None and (rc not in cells or cells[rc]['text'] != item['registration']):
            continue
        if RELAYED.search(row['section'] + ' ' + row['span']):
            return 'REFUSED_TABLE_RELAYED_NOT_DATA', None
        if row['section'].casefold() != drug.strip().casefold():
            continue
        arm = cells[ac]['text']
        pattern = (r'Anti[–-]IL-6(?: \([^)]*\))?' if key == 'n_1'
                   else r'(?:Placebo \+ usual care|Usual care)(?: [a-z])?')
        if not re.fullmatch(pattern, arm, re.I):
            continue
        # The complete physical row must be in the held parent. A field span
        # may be a cell or row, but never evidence from another physical row.
        if row['span'] not in parent or not span or span not in row['span']:
            continue
        token = cells[nc]['text']
        if not re.fullmatch(r'[1-9]\d*', token) or int(token) != value:
            continue
        if not re.search(r'(?<!\d)' + re.escape(token) + r'(?!\d)', span):
            continue
        hits.append(dict(table=row['table'], row=row['row'], column=nc,
                         headers=row['headers'][nc], label_origin=cells[lc]['origin'],
                         value_origin=cells[nc]['origin'], section=row['section'], arm=arm))
    if len(hits) == 1:
        return None, hits[0]
    if hits:
        return 'REFUSED_TABLE_AMBIGUOUS_BINDING:' + key, None
    return (errors[0]['reason'] if errors else 'REFUSED_TABLE_ROW_HEADER_ARM_BINDING:' + key), None


def verify(proposal, root=ROOT):
    """Return accepted/rejected/non-proposed fields and a sanitized value tree.

    Any document or schema failure rejects the entire proposal. A field failure
    rejects only that field. No unverified value is returned in accepted.
    """
    result = {"status": "rejected", "reason": None, "fields": [], "accepted": None}
    reason = _schema(proposal)
    if reason:
        result["reason"] = reason
        return result
    groups = [("primary_scope", proposal["primary_scope"], SCOPE), ("pooled", proposal["pooled"], POOLED)]
    groups += [(f"trials.{i}", row, TRIAL) for i, row in enumerate(proposal["trials"])]
    try:
        text, allowed, topic, normalise = _source(proposal, Path(root).resolve())
    except (ValueError, OSError, UnicodeError, TypeError, KeyError) as exc:
        reason = str(exc)
        if not reason.startswith("REFUSED_"):
            reason = "REFUSED_SOURCE_READ:" + type(exc).__name__
        result["reason"] = reason
        for prefix, item, keys in groups:
            for key in keys:
                if item[key] is not None:
                    result["fields"].append({"path": prefix + "." + key, "status": "rejected", "reason": reason})
        return result
    clean = {"primary_scope": {}, "pooled": {}, "trials": []}
    table_data = None
    for prefix, item, keys in groups:
        target = {} if prefix.startswith("trials.") else clean[prefix]
        if prefix.startswith("trials."):
            clean["trials"].append(target)
        for key in keys:
            path = prefix + "." + key
            value = item[key]
            try:
                span = normalise(item.get("field_spans", {}).get(key, item["span"]))
                parent = normalise(item["span"])
                span_error = None
            except ValueError as exc:
                span, parent, span_error = "", "", str(exc)
            reason, table_path = None, None
            if value is None:
                status = "not_proposed"
            else:
                if span_error:
                    reason = span_error
                elif not parent or parent not in text or not span or span not in parent:
                    reason = "REFUSED_SPAN_NOT_HELD"
                elif parent not in allowed:
                    reason = "REFUSED_SPAN_OUTSIDE_COMPARATOR_RECORD"
                elif RELAYED.search(parent):
                    reason = "REFUSED_RELAYED_NOT_DATA"
                else:
                    reason = _reparse(key, value, span)
                    if (reason == 'REFUSED_NUMBER_ROLE_NOT_IN_OWN_SPAN'
                            and prefix.startswith('trials.') and key in {'n_1', 'n_2'}
                            and hasattr(normalise, 'table_source')):
                        if table_data is None:
                            table_data = _table_rows(*normalise.table_source)
                        reason, table_path = _table_count(
                            item, key, value, span, parent, *table_data, topic)
                status = "rejected" if reason else "accepted"
            result["fields"].append({"path": path, "status": status, "reason": reason})
            if table_path is not None:
                result['fields'][-1]['table_path'] = table_path
            target[key] = value if status == "accepted" else None
        # Do not assemble one estimate from independently valid but different rows.
        bound = set()
        for key in ("effect", "ci_low", "ci_high"):
            if target.get(key) is not None:
                parsed = parse_estimate(normalise(item.get("field_spans", {}).get(key, item["span"])))
                bound.add(tuple(parsed.get(x) for x in ("effect", "ci_low", "ci_high")))
        if len(bound) > 1:
            for key in ("effect", "ci_low", "ci_high"):
                if target.get(key) is not None:
                    target[key] = None
                    field = next(f for f in result["fields"] if f["path"] == prefix + "." + key)
                    field.update(status="rejected", reason="REFUSED_MIXED_ESTIMATE_BINDINGS")
        # Field support alone cannot authorize an impossible arm count.
        if prefix.startswith("trials."):
            for arm in ("1", "2"):
                e, n = target.get("events_" + arm), target.get("n_" + arm)
                if e is not None and n is not None and e > n:
                    for key in ("events_" + arm, "n_" + arm):
                        target[key] = None
                        field = next(f for f in result["fields"] if f["path"] == prefix + "." + key)
                        field.update(status="rejected", reason="REFUSED_EVENTS_EXCEED_N")
    result["accepted"] = clean
    result["status"] = "partial" if any(f["status"] == "rejected" for f in result["fields"]) else "accepted"
    return result


def to_comparator(proposal, root=ROOT):
    """Adapt printed fields and the recorded model's selected-outcome mapping.

    This is an audit of the PROPOSED closest scope, never equivalence certification.
    General included-study inventories keep OUTCOME_UNPARSED. Completeness needs
    a recorded model declaration AND accepted k, all labels and unique identities.
    That remains a proposed set, not a certification of clinical equivalence.
    """
    from .comparator_extract import fact, norm
    from .meta_match import _join
    checked = verify(proposal, root)
    if checked["accepted"] is None:
        raise ValueError(checked["reason"])
    topic = json.loads((Path(root) / "topics" / (proposal["slug"] + ".json")).read_text(encoding="utf-8"))
    clean = checked["accepted"]
    rows = []
    for r in clean["trials"]:
        if r["label"] is None:
            continue
        primary = topic["primary_outcome"]["name"]
        selected = proposal.get("trial_set_scope") == "selected_outcome" and clean["primary_scope"]["outcome_as_printed"] is not None
        row = {"label": r["label"], "outcome": fact(primary if selected else None),
               "timepoint": fact(), "population": fact()}
        for key in TRIAL[1:]:
            row[{"events_1": "events1", "events_2": "events2", "n_1": "n1", "n_2": "n2"}.get(key, key)] = fact(r[key])
        rows.append(row)
    k = clean["pooled"]["k"]
    complete = (proposal.get("trial_set_complete") is True
                and proposal.get("trial_set_scope") == "selected_outcome"
                and clean["primary_scope"]["outcome_as_printed"] is not None
                and k is not None and len(rows) == len(proposal["trials"]) == k
                and len({norm(r["label"]) for r in rows}) == k
                and not any(_join(a, b) for i, a in enumerate(rows) for b in rows[i + 1:]))
    return {"slug": proposal["slug"], "primary_outcome": topic["primary_outcome"]["name"],
            "status": "LEXICALLY_VERIFIED_PROPOSAL", "trial_set": rows,
            "pooled": {k: fact(v) for k, v in clean["pooled"].items()},
            "membership_complete": complete, "scope_note": proposal["scope_note"]}
