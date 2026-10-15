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


def header_grid(header):
    """Expand both spans, reserving occupied columns on subsequent rows."""
    rows = ET.fromstring(re.sub(r"<sup\b.*?</sup>", "", header, flags=re.S))
    occupied = {}
    for ri, row in enumerate(rows):
        col = 0
        for cell in row:
            while (ri, col) in occupied:
                col += 1
            width, height = int(cell.get("colspan", "1")), int(cell.get("rowspan", "1"))
            if width < 1 or height < 1 or ri + height > len(rows):
                raise ValueError("HEADER_SPAN_INVALID")
            value = " ".join("".join(cell.itertext()).split())
            for r in range(ri, ri + height):
                for c in range(col, col + width):
                    if (r, c) in occupied:
                        raise ValueError("HEADER_SPAN_OVERLAP")
                    occupied[r, c] = value
            col += width
    width = max((c for r, c in occupied), default=-1) + 1
    return [[occupied.get((r, c), "") for c in range(width)] for r in range(len(rows))]


def read_row(text, *, table_label, row_label, intervention, comparator,
             group=None, period=None, proportions=False, effect=False, analysis_set=None):
    tables = [t for t in re.findall(r"<table-wrap\b.*?</table-wrap>", text, re.S)
              if re.search(r"<label>" + re.escape(table_label) + r"</label>", t)]
    if len(tables) != 1:
        raise ValueError("TABLE_UNBOUND")
    table = tables[0]
    header = re.search(r"<thead>.*?</thead>", table, re.S).group()
    hrows = header_grid(header)
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
    caption = re.search(r"<caption>.*?</caption>", table, re.S)
    foot = re.search(r"<table-wrap-foot>.*?</table-wrap-foot>", table, re.S)
    count_type = re.compile(r"\b(?:n|no\.|number)(?:\s+of\s+patients)?\s*\(\s*%\s*\)|\bn\s*/\s*n\b|\bevents\b|\bpatients with\b|\bnumber of people with", re.I)
    not_count = re.compile(r"\bKM\b|Kaplan|estimate|\bSE\b|\bmean\b|\bmedian\b|per\s+100|person[- ]years", re.I)
    # A table-wide declaration is usable only when explicitly scoped by its
    # caption or notes. The row's number-of-people label types raw counts too.
    table_count_type = re.compile(r"\b(?:n|no\.|number)(?:\s+of\s+patients)?\s*\(\s*%\s*\)|\bnumber of (?:patients|people) (?:with|who)", re.I)
    declarations = [m.group() for m in (caption, foot) if m and table_count_type.search(plain(m.group()))]
    if proportions and count_type.search(row_label):
        declarations.append(row_label)
    def is_count(i):
        labels = " ".join(r[i] for r in hrows)
        if not_count.search(labels):
            return False
        if count_type.search(labels):
            return True
        if "%" in labels:
            return False
        return bool(declarations)
    def column(term):
        hits = [i for i, c in enumerate(armrow) if i in allowed and term.lower() in c.lower()]
        hits = [i for i in hits if is_count(i)]
        if not hits or hits != list(range(min(hits), max(hits) + 1)):
            raise ValueError("ARM_COLUMN_AMBIGUOUS")
        return hits[0]
    ii, ci = column(intervention), column(comparator)
    if ii == ci:
        raise ValueError("ARM_COLUMN_AMBIGUOUS")
    denom_span = ""
    def denominator(i):
        nonlocal denom_span
        matches = list(re.finditer(r"\b[Nn]\s*=\s*(\d+)", armrow[i]))
        if len(matches) == 1:
            return int(matches[0][1])
        if matches:
            ae = re.search(r"adverse|\bAEs?\b|TEAEs?", row_label + " " + (group or ""), re.I)
            wanted = analysis_set or ("safety" if ae else "randomised")
            if "safety" in wanted.lower():
                pattern = r"safety"
            elif re.search(r"randomi[sz]ed|\bITT\b|intention.to.treat", wanted, re.I):
                pattern = r"randomi[sz]ed|\bITT\b|intention.to.treat"
            else:
                raise ValueError("ANALYSIS_DENOMINATOR_AMBIGUOUS")
            selected_n = []
            for j, m in enumerate(matches):
                label = armrow[i][matches[j-1].end() if j else 0:m.start()]
                if re.search(pattern, label, re.I):
                    selected_n.append(int(m[1]))
            if len(selected_n) != 1:
                raise ValueError("ANALYSIS_DENOMINATOR_AMBIGUOUS")
            return selected_n[0]
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
    spans.extend(("count_type", s) for s in declarations)
    if denom_span:
        spans.append(("denominator", denom_span))
    if gs:
        spans.append(("outcome_group", gs))
    effect_value = None
    if effect:
        hi = [i for i in allowed if re.search(r"hazard ratio|risk ratio|odds ratio|\bHR\b|\bRR\b|\bOR\b", " ".join(r[i] for r in hrows), re.I)
              and "95% CI" in " ".join(r[i] for r in hrows)]
        if len(hi) != 1:
            raise ValueError("EFFECT_HEADER_UNBOUND")
        m = re.fullmatch(r'([\d.]+)\s*\(([\d.]+)\s*[-\u2013\u2014]\s*([\d.]+)\)', cs[hi[0]])
        if not m:
            raise ValueError("EFFECT_UNBOUND")
        pt, lo, high = map(float, m.groups())
        if not 0 < lo <= pt <= high:
            raise ValueError("EFFECT_INVALID")
        label = " ".join(r[hi[0]] for r in hrows)
        scale = "HR" if re.search(r"hazard|\bHR\b", label, re.I) else "OR" if re.search(r"odds|\bOR\b", label, re.I) else "RR"
        effect_value = dict(effect=pt, ci_low=lo, ci_high=high, scale=scale)
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
