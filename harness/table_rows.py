"""Deterministic JATS row reader: explicit column, endpoint and denominator bindings.

Selectors describe locations, never values. Unknown/ambiguous layouts fail closed.
Returned spans are slices of the original XML, not re-serialized elements.
"""
import html
import re
import xml.etree.ElementTree as ET


def plain(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def cells(row):
    root = ET.fromstring(re.sub(r"<sup\b.*?</sup>", "", row, flags=re.S))
    out = []
    for c in root:
        out.extend([" ".join("".join(c.itertext()).split())] * int(c.get("colspan", "1")))
    return out


def read_row(text, *, table_label, row_label, intervention, comparator,
             group=None, period=None, proportions=False, effect=False):
    tables = [t for t in re.findall(r"<table-wrap\b.*?</table-wrap>", text, re.S)
              if re.search(r"<label>" + re.escape(table_label) + r"</label>", t)]
    if len(tables) != 1:
        raise ValueError("TABLE_UNBOUND")
    table = tables[0]
    header = re.search(r"<thead>.*?</thead>", table, re.S).group()
    hrows = [cells(r) for r in re.findall(r"<tr\b.*?</tr>", header, re.S)]
    rows = re.findall(r"<tr\b.*?</tr>", re.search(r"<tbody>.*?</tbody>", table, re.S).group(), re.S)
    # Flattened text still preserves table columns: colspan expands a group header
    # across its event-count, percentage and rate columns.
    armrow = next((r for r in hrows if any(intervention.lower() in c.lower() for c in r)
                   and any(comparator.lower() in c.lower() for c in r)), None)
    if armrow is None:
        raise ValueError("ARM_HEADER_UNBOUND")
    allowed = set(range(len(armrow)))
    if period:
        prow = next((r for r in hrows if period in r), None)
        if prow is None:
            raise ValueError("PERIOD_UNBOUND")
        allowed = {i for i, c in enumerate(prow) if c == period}
    def column(term):
        hits = [i for i, c in enumerate(armrow) if i in allowed and term.lower() in c.lower()]
        if not hits or hits != list(range(min(hits), max(hits) + 1)):
            raise ValueError("ARM_COLUMN_AMBIGUOUS")
        return hits[0]
    ii, ci = column(intervention), column(comparator)
    if ii == ci:
        raise ValueError("ARM_COLUMN_AMBIGUOUS")
    denom_span = ""
    def denominator(i):
        nonlocal denom_span
        m = re.search(r"\b[Nn]\s*=\s*(\d+)", armrow[i])
        if m:
            return int(m[1])
        nr = [r for r in rows if cells(r)[0].lower() == "no. of patients"]
        if len(nr) != 1:
            raise ValueError("DENOMINATOR_UNBOUND")
        denom_span = nr[0]
        return int(cells(nr[0])[i])
    ni, nc = denominator(ii), denominator(ci)
    selected, group_span = [], ""
    for row in rows:
        cs = cells(row)
        if group and cs[0] == group:
            group_span = row
            continue
        # A new label-only heading ends the preceding group.
        if group and cs[0] and cs[0] != row_label and not any(re.search(r"\d", c) for c in cs[1:]):
            group_span = ""
        if cs[0] == row_label and (not group or group_span):
            selected.append((row, cs, group_span))
    if len(selected) != 1:
        raise ValueError("ENDPOINT_ROW_AMBIGUOUS")
    row, cs, gs = selected[0]
    foot = re.search(r"<table-wrap-foot>.*?</table-wrap-foot>", table, re.S)
    spans = [("row", row), ("header", header)]
    if denom_span:
        spans.append(("denominator", denom_span))
    if gs:
        spans.append(("outcome_group", gs))
    effect_value = None
    if effect:
        hi = [i for i, c in enumerate(armrow) if "hazard ratio" in c.lower() and "95% CI" in c]
        if len(hi) != 1:
            raise ValueError("EFFECT_HEADER_UNBOUND")
        m = re.fullmatch(r"([\d.]+)\s*\(([\d.]+)[-ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“]([\d.]+)\)", cs[hi[0]])
        if not m:
            raise ValueError("EFFECT_UNBOUND")
        pt, lo, high = map(float, m.groups())
        if not 0 < lo <= pt <= high:
            raise ValueError("EFFECT_INVALID")
        effect_value = dict(effect=pt, ci_low=lo, ci_high=high, scale="HR")
    props = None
    if proportions:
        f = plain(foot.group()) if foot else ""
        m = re.search(re.escape(row_label) + r" was ([\d.]+) vs\. ([\d.]+).*in the "
                      + re.escape(intervention) + r" vs\. " + re.escape(comparator) + r" groups", f, re.I)
        if not m:
            raise ValueError("PROPORTION_UNBOUND")
        props = tuple(map(float, m.groups()))
        spans.append(("proportion", foot.group()))
    def count(i, n, prop):
        if props:
            ev = int(cs[i])
            if not 0 <= ev <= n or abs(ev / n - prop) > .005:
                raise ValueError("PROPORTION_DISAGREES")
            return ev
        # Some JATS tables put N and (%) in separate adjacent cells.
        value = cs[i] if "(" in cs[i] else " ".join(cs[i:i + 2])
        m = re.fullmatch(r"(\d+)\s*\(([\d.]+)%?\)", value)
        if not m:
            raise ValueError("COUNT_PERCENT_UNBOUND")
        ev, pct = int(m[1]), float(m[2])
        if not 0 <= ev <= n or abs(100 * ev / n - pct) > .051:
            raise ValueError("PERCENT_DISAGREES")
        return ev
    counts = dict(ai=count(ii, ni, props[0] if props else None), n1i=ni,
                  ci=count(ci, nc, props[1] if props else None), n2i=nc)
    return effect_value or counts, spans
