"""G7 -- arm OWNERSHIP of a number inside its span.

G2/G3 prove a number is printed in the quoted span. When one span carries BOTH arms' numbers (common: "2697 (77.2%)
and 2723 (78.1%) patients in the linagliptin and placebo groups"), that proves nothing about WHOSE number it is -- the
REWIND arm swap lives exactly there. This module decides ownership from the text alone, never from the served slots,
by one of seven relations, and names which one held:

  ADJACENT_LABEL  the number's nearest arm mention (no other arm's number in between) is its own arm; a mention that
                  follows the number through 'in (the)' / 'assigned to' / 'to receive' wins over a nearer preceding one
  PARALLEL_ORDER  the span lists the arms' numbers in the same order as it names the arms ('A and B ... respectively')
  VERSUS_ORDER    'X (p%) versus Y (q%)' where the span names exactly one arm, before the pair: X is that arm's
  EACH_GROUP      'one patient in each group' -- a distributive count, valid only when every arm's value is that number
  TABLE_COLUMN    a table row: the cell holding the span's occurrence of the number sits under a header cell (nearest
                  of up to 3 header rows that names an arm at that index) naming its own arm and no other
  GROUP_ID        registry JSON: the number's groupId is defined, in the SAME outcome measure (the nearest definition
                  before the number), with a title naming its own arm and no other
  AACT_GROUP      AACT reported_events: the number's flat JSON object carries result_group_id, whose result_groups
                  object's title names its own arm and no other
Anything else is OWNERSHIP_UNVERIFIED."""
import re

CONNECT = re.compile(r"^[\s\S]{0,45}?\b(in the|in|among|assigned to|to receive|receive|randomi[sz]ed to|receiving|with)\b\s*$", re.I)
CONTROL_ALIASES = ["placebo", "controls", "control", "usual care", "standard care"]
STOP = {"group", "groups", "arm", "plus", "with", "patients", "participants", "treated", "treatment", "daily", "once", "twice"}
# not a count: a percentage ('20 percent', '20,5%'), a per-mille, a dose, a rate denominator ('per 100 patient-years')
# -- review, 2026-09-25. (A number inside a name, 'GLP-1', is excluded by the (?<![A-Za-z]-) lookbehind at the use.)
NOT_COUNT = (r"(?!\s*(?:%|‰|percent\b|per\s*cent\b|mg\b|µg\b|mcg\b|g\b|ml\b|mmol\b|IU\b|units?\b|per\s+\d|"
             r"patient-years|person-years))(?!,\d{1,2}(?!\d))")
CTRL_RE = re.compile(r"\b(placebo|control|controls|usual care|standard care|standard of care)\b|^\s*no[- ][a-z]", re.I)


def aliases(arm, arms=None):
    """The ways a text may name this arm: its label; the label without 'group'; the source-defined expansion of an
    abbreviation; each word of the label that no other arm's label contains ('esketamine' in 'Esketamine Plus AD' vs
    'AD Plus Placebo'); control vocabulary for a control arm; and, in a two-arm trial whose other arm is a control,
    'active' / 'intervention' / 'experimental' / 'treatment' group for the non-control arm."""
    lab = (arm.get("arm_label") or "").strip()
    out = {lab}
    core = re.sub(r"\b(group|arm)s?\b", "", lab, flags=re.I).strip(" ,.:")
    if len(core) >= 2:
        out.add(core)
    exp = (arm.get("abbreviation") or {}).get("expansion")
    if exp:
        out.add(exp)
    others = [a for a in (arms or []) if a is not arm]
    other_words = {w.lower() for a in others for w in re.findall(r"[A-Za-z][A-Za-z-]{3,}", a.get("arm_label") or "")}
    for w in re.findall(r"[A-Za-z][A-Za-z-]{4,}", lab):
        if w.lower() not in other_words and w.lower() not in STOP:
            out.add(w)
    if CTRL_RE.search(lab):
        out.update(CONTROL_ALIASES)
    elif len(others) == 1 and CTRL_RE.search(others[0].get("arm_label") or ""):
        out.update(["active group", "intervention group", "experimental group", "treatment group"])
    # 'balanced-crystalloids group' and 'balanced crystalloids': a hyphen and a space name the same arm
    out |= {a.replace("-", " ") for a in out if "-" in a and not a.lower().startswith("no-")}
    return sorted((a for a in out if a), key=len, reverse=True)


def _raw_mentions(text, arm, arms=None):
    spans = []
    for a in aliases(arm, arms):
        for m in re.finditer(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", text, re.I):
            if not any(s <= m.start() < e for s, e in spans):
                spans.append((m.start(), m.end()))
    return sorted(spans)


def mentions(text, arm, arms=None):
    """Non-overlapping [start, end) of every mention of this arm (longest alias first). A mention lying INSIDE a
    longer mention of another arm is that other arm's ('Omega-3' inside 'Placebo Omega-3' names the placebo arm)."""
    own = _raw_mentions(text, arm, arms)
    longer = [(s, e) for a in (arms or []) if a is not arm for s, e in _raw_mentions(text, a, arms)]
    return [(s, e) for s, e in own
            if not any(ls <= s and e <= le and (le - ls) > (e - s) for ls, le in longer)]


# 'Compared with placebo, ... 20 vs 10': the arm after 'compared with / versus / than' is the REFERENCE of the
# comparison, not the owner of the nearest or first-listed number (review, 2026-09-25: the swapped claim bound here).
GOVERNOR = re.compile(r"(?:compared\s+(?:with|to)|versus|vs\.?|than|relative\s+to|in\s+comparison\s+(?:with|to))\s+(?:the\s+|a\s+)?$", re.I)


def free_mentions(text, arm, arms=None):
    """Mentions that are not the object of a comparison ('compared with X', 'versus X', 'than X')."""
    return [(s, e) for s, e in mentions(text, arm, arms) if not GOVERNOR.search(text[max(0, s - 40):s])]


_SPANS = {}


def object_spans(doc):
    """[start, end) of every JSON object in doc, by a brace scanner that skips string contents (cached per text)."""
    key = (id(doc), len(doc))
    if key not in _SPANS:
        out, stack, i, n, in_str = [], [], 0, len(doc), False
        while i < n:
            c = doc[i]
            if in_str:
                if c == "\\":
                    i += 1
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "{":
                stack.append(i)
            elif c == "}" and stack:
                out.append((stack.pop(), i + 1))
            i += 1
        _SPANS.clear()
        _SPANS[key] = out
    return _SPANS[key]


def flat_object_at(doc, pos):
    """(span, parsed object) of the innermost JSON object containing pos (object None when it is not valid JSON)."""
    import json
    spans = sorted((sp for sp in object_spans(doc) if sp[0] <= pos < sp[1]), key=lambda sp: sp[1] - sp[0])
    if not spans:
        return None, None
    try:
        return spans[0], json.loads(doc[spans[0][0]:spans[0][1]])
    except ValueError:
        return spans[0], None


def number_positions(text, value, partner=None):
    """Positions of `value` printed as a count; prefer 'v/partner' or 'v of partner' when a partner number is given."""
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
             10: "ten", 11: "eleven", 12: "twelve"}
    pats = []
    if partner is not None:
        pats.append(r"(?<![\d.,·])(?<![A-Za-z]-)%d\s*(?:/|of)\s*%d(?![\d.,·])" % (value, partner))
    shown = f"{value:,}" if value >= 1000 and f"{value:,}" in text else str(value)
    pats.append(r"(?<![\d.,·])(?<![A-Za-z]-)%s(?![\d]|[.·]\d)%s" % (re.escape(shown), NOT_COUNT))
    if value in words:
        pats.append(r"(?<!at least )(?<!more than )(?<!fewer than )\b%s\b(?!-[a-z])" % words[value])
    for p in pats:
        hits = [(m.start(), m.end()) for m in re.finditer(p, text, re.I)]
        if hits:
            return hits
    return []


def clauses(text):
    """[start, end) of each clause: split at ';' and at a sentence end ('. ' followed by a capital)."""
    cuts = [0] + [m.end() for m in re.finditer(r";|\.\s+(?=[A-Z])", text)] + [len(text)]
    return [(a, b) for a, b in zip(cuts, cuts[1:]) if b > a]


def adjacent(text, pos, own, others, other_numbers):
    s, e = pos
    best = None
    for owner, spans in [("own", own)] + [("other", o) for o in others]:
        for ms, me in spans:
            if ms >= e:  # mention follows the number
                gap = text[e:ms]
                if any(e <= a < ms for a, _ in other_numbers):
                    continue
                d = len(gap) - (1000 if CONNECT.match(gap) else 0)
            elif me <= s:
                gap = text[me:s]
                if any(me <= a < s for a, _ in other_numbers):
                    continue
                d = len(gap)
            else:
                continue
            if d <= 120 and (best is None or d < best[0]):
                best = (d, owner)
    return best[1] if best else None


def cells(fragment):
    """Cell texts of a row, each repeated by its colspan, so a column index is a grid index (review, 2026-09-25)."""
    out = []
    for m in re.finditer(r"<t[dh]\b([^>]*)>(.*?)</t[dh]>", fragment, re.S):
        span = re.search(r'colspan="?(\d+)', m.group(1))
        out += [m.group(2)] * (int(span.group(1)) if span else 1)
    return out


def cell_bounds(fragment, base):
    """[start, end) of each GRID cell of a row (a cell with colspan=n occupies n grid slots)."""
    out = []
    for m in re.finditer(r"<t[dh]\b([^>]*)>.*?</t[dh]>", fragment, re.S):
        span = re.search(r'colspan="?(\d+)', m.group(1))
        out += [(m.start() + base, m.end() + base)] * (int(span.group(1)) if span else 1)
    return out


def table_column(doc, span_start, span_text, value, own_arm, arms):
    """The row containing the span; the cell holding THE SPAN'S occurrence of `value` (located by position, so a value
    repeated elsewhere in the row cannot be confused with it); the header rows above, nearest first (up to 3), until
    one names an arm at that column index. Own arm named there and no other arm -> owned."""
    row_start = doc.rfind("<tr", 0, span_start + 3)   # +3: a "<tr" starting AT the span start must be found
    row_end = doc.find("</tr>", span_start)
    if row_start < 0 or row_end < 0:
        return False
    pos = [span_start + p for p, _ in number_positions(span_text, value)]
    bounds = cell_bounds(doc[row_start:row_end], row_start)
    ks = sorted({i for i, (a, b) in enumerate(bounds) if any(a <= p < b for p in pos)})
    if len(ks) != 1:
        return False
    k, nrow = ks[0], len(bounds)
    cursor = row_start
    for _ in range(3):
        hm = [m.start() for m in re.finditer(r"<th\b", doc[:cursor])]   # '<th\b': never '<thead'
        if not hm:
            return False
        head_end = hm[-1]
        hrow_start = doc.rfind("<tr", 0, head_end + 1)
        header = cells(doc[hrow_start:doc.find("</tr>", head_end)])
        offset = nrow - len(header)
        # a header shorter than the row is only trusted when the missing cell is the row's stub (offset 1) and the row
        # has no trailing extra cell -- equal lengths otherwise (review, 2026-09-25)
        # offset 1 is ambiguous: the header lacks the row's stub cell (shift by one) or a trailing cell (no shift).
        # An empty first header cell IS a stub, so then the missing cell is trailing.
        stub_present = bool(header) and not re.sub(r"<[^>]+>|&nbsp;|\s", "", header[0])
        shift = 0 if offset == 0 or (offset == 1 and stub_present) else (1 if offset == 1 else None)
        if shift is not None and 0 <= k - shift < len(header):
            h = re.sub(r"<[^>]+>", " ", header[k - shift])
            own = bool(mentions(h, own_arm, arms))
            other = any(mentions(h, a, arms) for a in arms if a is not own_arm)
            if own or other:
                return own and not other
        cursor = hrow_start
    return False


def group_def(doc, span, value=None):
    """(identity of the enclosing outcome measure, title of the number's OWN group) -- the groupId is read from the
    flat JSON object that holds the number (not the span's first groupId), and its title from the 'groups' list of the
    innermost measure containing it. A span crossing an object boundary has no single object: (None, None).
    (Review, 2026-09-25: a span beginning in OG000's object and ending at OG001's number bound a full swap.)"""
    import json
    if "{" in span["text"] or "}" in span["text"]:
        return None, None
    if value is None:
        m = re.search(r'"value":\s*"(\d+)"', span["text"])
        pos = span["start"] + m.start(1) if m else span["start"]
    else:
        ps = [span["start"] + p for p, _ in number_positions(span["text"], value)]
        if len(ps) != 1:
            return None, None
        pos = ps[0]
    _, flat = flat_object_at(doc, pos)
    gid = (flat or {}).get("groupId") if isinstance(flat, dict) else None
    if not gid:
        return None, None
    for a, b in sorted((sp for sp in object_spans(doc) if sp[0] <= pos < sp[1]), key=lambda sp: sp[1] - sp[0]):
        body = doc[a:b]
        if '"groups":' in body or '"eventGroups":' in body:
            try:
                obj = json.loads(body)
            except ValueError:
                return None, None
            groups = obj.get("groups") or obj.get("eventGroups") or []
            title = next((g.get("title") for g in groups if g.get("id") == gid), None)
            return (a, title) if title is not None else (None, None)
    return None, None


def group_id(doc, span, own_arm, arms, value=None):
    at, title = group_def(doc, span, value)
    if at is None:
        return False
    return bool(mentions(title, own_arm, arms)) and not any(mentions(title, a, arms) for a in arms if a is not own_arm)


def owns(doc, span, value, partner, arm_i, arms, values):
    """-> relation name or None. `values` = {arm index: value of the same kind (events or totals)} for every arm."""
    text = span["text"]
    own = free_mentions(text, arms[arm_i], arms)
    others = [free_mentions(text, a, arms) for j, a in enumerate(arms) if j != arm_i]
    other_numbers = [p for j, v in values.items() if j != arm_i and v is not None and v != value
                     for p in number_positions(text, v)]
    positions = number_positions(text, value, partner)
    if not positions:
        return None
    # "... 20 (x%) and 10 (y%) participants in the A and B groups": a COORDINATED list of arm names makes nearness
    # meaningless (10 sits next to 'A'), so adjacency is not used in such a span -- only the order relations are.
    coordinated = any(re.fullmatch(r"\s*(,|and|or|vs\.?|versus|/|&)\s*(the\s+)?", text[e1:s2] if e1 <= s2 else text[e2:s1], re.I)
                      for s1, e1 in own for o in others for s2, e2 in o)
    for pos in ([] if coordinated else positions):
        if adjacent(text, pos, own, others, other_numbers) == "own":
            return "ADJACENT_LABEL"
    # PARALLEL_ORDER, anchored to ONE clause (review, 2026-09-25: first-mention/last-number over the whole span let an
    # earlier 'drugx or placebo' or a later '20 mg' decide): a clause (split at ';' and sentence ends) in which every
    # arm's value occurs exactly once and every arm is named by a free (non-reference) mention; values in the order
    # the arms are named. Every such clause must agree.
    verdicts = set()
    if len({v for v in values.values()}) == len(values):
        carried, prev = None, ""
        for cl_s, cl_e in clauses(text):
            clause = text[cl_s:cl_e]
            if re.search(r"\.\s*$", prev):
                carried = None                     # a carried arm order never crosses a sentence break
            prev = clause
            named = [free_mentions(clause, a, arms) for a in arms]
            nums = [number_positions(clause, values.get(j), None) if values.get(j) is not None else [] for j in range(len(arms))]
            if all(named):
                # an ORDER clause: every arm named freely next to a list of numbers ('2697 and 2723 patients in the
                # linagliptin and placebo groups') fixes the order a later clause of the same sentence may reuse
                if len(re.findall(r"(?<![\d.])\d[\d,]*(?![\d.]|\s*%)", clause)) >= len(arms):
                    carried = [j for _, j in sorted((m[0][0], j) for j, m in enumerate(named))]
                if all(len(n) == 1 for n in nums):
                    by_num = [j for _, j in sorted((n[0][0], j) for j, n in enumerate(nums))]
                    verdicts.add(by_num == [j for _, j in sorted((m[0][0], j) for j, m in enumerate(named))])
            elif not any(named) and carried and all(len(n) == 1 for n in nums):
                # '...; 1036 (29.7%) and 1024 (29.4%) had hypoglycaemia': no arm named, the sentence's order applies
                verdicts.add([j for _, j in sorted((n[0][0], j) for j, n in enumerate(nums))] == carried)
    if verdicts == {True}:
        return "PARALLEL_ORDER"
    named = [j for j, a in enumerate(arms) if free_mentions(text, a, arms)]
    if len(named) == 1 and len(arms) == 2:
        j0 = named[0]
        v0, v1 = values.get(j0), values.get(1 - j0)
        # the named arm is the SUBJECT: its free mention precedes 'v0 versus v1' in the same clause
        def num(v):   # the value as printed: digits (with thousands commas) or a spelled number
            w = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
                 10: "ten", 11: "eleven", 12: "twelve"}.get(v)
            return r"(?:%s|%s%s)" % (re.escape(f"{v:,}"), v, "|" + w if w else "")
        lead = r"(?:\d[\d,]*\s*(?:of|/)\s*)?"                       # 'four of 119 ... vs. 22 of 127' for totals
        m = re.search(r"(?<![\d.\w])%s%s(?:\s*(?:of|/)\s*\d[\d,]*)?\s*(?:\([^)]*\))?\s*(?:versus|vs\.?|compared with)\s*%s%s(?![\d.])"
                      % (lead, num(v0), lead, num(v1)), text, re.I)
        # the named arm is the SUBJECT: its free mention precedes the pair with no sentence break in between
        if m and any(e <= m.start() and not re.search(r"\.\s+(?=[A-Z(])", text[e:m.start()])
                     for _, e in free_mentions(text, arms[j0], arms)):
            return "VERSUS_ORDER"
    # EACH_GROUP: 'one patient in each group' -- a distributive count belongs to every arm, and is only a valid owner
    # when every arm's value IS that number
    if len({v for v in values.values()}) == 1 and any(
            re.match(r"[^.;]{0,60}?\b(in|of) (each|both) (group|arm)s?\b|[^.;]{0,30}?\bper (group|arm)\b", text[e:], re.I)
            for _, e in positions):
        return "EACH_GROUP"
    if doc is not None and "<t" in text and table_column(doc, span["start"], text, value, arms[arm_i], arms):
        return "TABLE_COLUMN"
    if doc is not None and '"groupId"' in text and group_id(doc, span, arms[arm_i], arms, value):
        return "GROUP_ID"
    if doc is not None and re.search(r'"subjects_(affected|at_risk)"', text) and aact_group(doc, span, arms[arm_i], arms, value):
        return "AACT_GROUP"
    return None


def aact_group(doc, span, own_arm, arms, value=None):
    """AACT reported_events: the flat JSON object holding THE NUMBER carries result_group_id; the result_groups
    object with that id carries the arm's title. Own arm named in that title and no other arm -> owned. A span that
    crosses an object boundary has no single object (review, 2026-09-25)."""
    if "{" in span["text"] or "}" in span["text"]:
        return False
    ps = [span["start"] + p for p, _ in number_positions(span["text"], value)] if value is not None else [span["start"]]
    if len(ps) != 1:
        return False
    _, flat = flat_object_at(doc, ps[0])
    rid_v = (flat or {}).get("result_group_id") if isinstance(flat, dict) else None
    if not rid_v:
        return False
    g = re.search(r'\{\s*"id":\s*"%s"[^{}]*?"title":\s*"([^"]*)"' % re.escape(str(rid_v)), doc)
    if not g:
        return False
    title = g.group(1)
    return bool(mentions(title, own_arm, arms)) and not any(mentions(title, a, arms) for a in arms if a is not own_arm)
