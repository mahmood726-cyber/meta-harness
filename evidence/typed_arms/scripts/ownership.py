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


def number_positions(text, value, partner=None):
    """Positions of `value` printed as a count; prefer 'v/partner' or 'v of partner' when a partner number is given."""
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
             10: "ten", 11: "eleven", 12: "twelve"}
    pats = []
    if partner is not None:
        pats.append(r"(?<![\d.,·])%d\s*(?:/|of)\s*%d(?![\d.,·])" % (value, partner))
    shown = f"{value:,}" if value >= 1000 and f"{value:,}" in text else str(value)
    pats.append(r"(?<![\d.,·])%s(?![\d]|[.·]\d|\s*%%)" % re.escape(shown))
    if value in words:
        pats.append(r"\b%s\b" % words[value])
    for p in pats:
        hits = [(m.start(), m.end()) for m in re.finditer(p, text, re.I)]
        if hits:
            return hits
    return []


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
    return re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", fragment, re.S)


def table_column(doc, span_start, span_text, value, own_arm, arms):
    """The row containing the span; the cell holding THE SPAN'S occurrence of `value` (located by position, so a value
    repeated elsewhere in the row cannot be confused with it); the header rows above, nearest first (up to 3), until
    one names an arm at that column index. Own arm named there and no other arm -> owned."""
    row_start = doc.rfind("<tr", 0, span_start + 1)
    row_end = doc.find("</tr>", span_start)
    if row_start < 0 or row_end < 0:
        return False
    pos = [span_start + p for p, _ in number_positions(span_text, value)]
    bounds = [(m.start() + row_start, m.end() + row_start)
              for m in re.finditer(r"<t[dh]\b[^>]*>.*?</t[dh]>", doc[row_start:row_end], re.S)]
    ks = [i for i, (a, b) in enumerate(bounds) if any(a <= p < b for p in pos)]
    if len(ks) != 1:
        return False
    k, nrow = ks[0], len(bounds)
    cursor = row_start
    for _ in range(3):
        head_end = doc.rfind("<th", 0, cursor)
        if head_end < 0:
            return False
        hrow_start = doc.rfind("<tr", 0, head_end + 1)
        header = cells(doc[hrow_start:doc.find("</tr>", head_end)])
        offset = nrow - len(header)
        if offset in (0, 1) and 0 <= k - offset < len(header):
            h = re.sub(r"<[^>]+>", " ", header[k - offset])
            own = bool(mentions(h, own_arm, arms))
            other = any(mentions(h, a, arms) for a in arms if a is not own_arm)
            if own or other:
                return own and not other
        cursor = hrow_start
    return False


def group_def(doc, span):
    """Offset and title of the nearest '"id": "<groupId>", "title": ...' definition before this span -- the group's
    definition in the same outcome measure."""
    g = re.search(r'"groupId":\s*"(\w+)"', span["text"])
    if not g:
        return None, None
    defs = list(re.finditer(r'"id":\s*"%s",\s*"title":\s*"([^"]*)"' % re.escape(g.group(1)), doc[:span["start"]]))
    return (defs[-1].start(), defs[-1].group(1)) if defs else (None, None)


def group_id(doc, span, own_arm, arms):
    at, title = group_def(doc, span)
    if at is None:
        return False
    return bool(mentions(title, own_arm, arms)) and not any(mentions(title, a, arms) for a in arms if a is not own_arm)


def owns(doc, span, value, partner, arm_i, arms, values):
    """-> relation name or None. `values` = {arm index: value of the same kind (events or totals)} for every arm."""
    text = span["text"]
    own = mentions(text, arms[arm_i], arms)
    others = [mentions(text, a, arms) for j, a in enumerate(arms) if j != arm_i]
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
    firsts = []
    for j, a in enumerate(arms):
        v = values.get(j)
        ps = number_positions(text, v, None) if v is not None else []
        ms = mentions(text, a, arms)
        if not ps or not ms:
            firsts = None
            break
        firsts.append((ps[-1][0], ms[0][0], j))
    if firsts and len({v for v in values.values()}) == len(values):
        by_num = [j for _, _, j in sorted(firsts, key=lambda x: x[0])]
        by_lab = [j for _, _, j in sorted(firsts, key=lambda x: x[1])]
        if by_num == by_lab:
            return "PARALLEL_ORDER"
    named = [j for j, a in enumerate(arms) if mentions(text, a, arms)]
    if len(named) == 1 and len(arms) == 2:
        j0 = named[0]
        v0, v1 = values.get(j0), values.get(1 - j0)
        m = re.search(r"(?<![\d.])%s\s*(?:\([^)]*\))?\s*(?:versus|vs\.?|compared with)\s*%s(?![\d.])" % (v0, v1), text)
        if m and mentions(text[:m.start()], arms[j0], arms):
            return "VERSUS_ORDER"
    # EACH_GROUP: 'one patient in each group' -- a distributive count belongs to every arm, and is only a valid owner
    # when every arm's value IS that number
    if len({v for v in values.values()}) == 1 and any(
            re.match(r"[^.;]{0,60}?\b(in|of) (each|both) (group|arm)s?\b|[^.;]{0,30}?\bper (group|arm)\b", text[e:], re.I)
            for _, e in positions):
        return "EACH_GROUP"
    if doc is not None and "<t" in text and table_column(doc, span["start"], text, value, arms[arm_i], arms):
        return "TABLE_COLUMN"
    if doc is not None and '"groupId"' in text and group_id(doc, span, arms[arm_i], arms):
        return "GROUP_ID"
    if doc is not None and re.search(r'"subjects_(affected|at_risk)"', text) and aact_group(doc, span, arms[arm_i], arms):
        return "AACT_GROUP"
    return None


def aact_group(doc, span, own_arm, arms):
    """AACT reported_events: the flat JSON object enclosing the number carries result_group_id; the result_groups
    object with that id carries the arm's title. Own arm named in that title and no other arm -> owned."""
    start, end = doc.rfind("{", 0, span["start"]), doc.find("}", span["end"])
    if start < 0 or end < 0 or "}" in doc[start:span["start"]]:
        return False
    rid = re.search(r'"result_group_id":\s*"(\w+)"', doc[start:end])
    if not rid:
        return False
    g = re.search(r'\{\s*"id":\s*"%s"[^{}]*?"title":\s*"([^"]*)"' % re.escape(rid.group(1)), doc)
    if not g:
        return False
    title = g.group(1)
    return bool(mentions(title, own_arm, arms)) and not any(mentions(title, a, arms) for a in arms if a is not own_arm)
