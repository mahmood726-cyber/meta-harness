"""Conservative parser of held, segmented table excerpts; no pool admission.

``select`` returns (row_or_None, reason). ``typed`` includes separate candidates
and explicit refusals. Counts are never denominators inferred from percentages.
Source SHA is the declaration in the excerpt, not a claim of source verification.
"""
from pathlib import Path
import re


def _norm(s):
    for old, new in (("â€“", "-"), ("â€”", "-"), ("–", "-"), ("—", "-"),
                     ("â€ ", "†"), ("â€¡", "‡")):
        s = s.replace(old, new)
    return s


_MEASURES = {
    "HAZARD_RATIO": r"\bhazard ratios?\b|\bHR\b",
    "ODDS_RATIO": r"\bodds ratios?\b|\bOR\b",
    "RISK_RATIO": r"\b(?:risk ratios?|relative risks?)\b|\bRR\b",
    "RATE_RATIO": r"\b(?:incidence )?rate ratios?\b|\bIRR\b",
}


def _measures(s):
    # Abbreviations are case sensitive: the conjunction 'or' is not OR.
    return {key for key, pattern in _MEASURES.items()
            if re.search(pattern.rsplit("|", 1)[0], s, re.I)
            or re.search(pattern.rsplit("|", 1)[1], s)}


def variants(row):
    s = _norm(row["label"] + " " + row.get("parent_label", "")).lower()
    flags = []
    for flag, pattern in (
        ("NON_CABG", r"\bnon[- ]CABG\b|\bnot related to CABG\b"),
        ("LEADING_TO_DISCONTINUATION", r"\b(?:leading to|causing|led to) (?:permanent )?discontinuation\b"),
        ("SERIOUS", r"(?<!non-)\bserious\b"),
    ):
        if re.search(pattern, s, re.I):
            flags.append(flag)
    return flags


def parse(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    comments = [line for line in text.splitlines() if line.startswith("#")]
    hashes = set(re.findall(r"sha256[:\s]+([a-fA-F0-9]{64})\b", "\n".join(comments)))
    if len(hashes) != 1:
        raise ValueError(f"{path}: refused missing or conflicting source sha256")
    if "=== TABLES (excerpt) ===" not in text:
        raise ValueError(f"{path}: refused missing TABLES excerpt marker")
    tables, table, parent = [], None, ""
    for raw in text.split("=== TABLES (excerpt) ===", 1)[1].splitlines():
        line = _norm(raw.strip())
        if not line or line.startswith("#"):
            continue
        if line.startswith("TABLE "):
            table = dict(caption=line[6:], header=[], rows=[], footnotes=[],
                         source_sha=next(iter(hashes)), comments=comments, header_lines=[])
            tables.append(table)
            parent = ""
        elif table is None:
            raise ValueError(f"{path}: refused content before TABLE: {line}")
        elif re.match(r"^(?:[*†‡]|a\s|Footnote)", line, re.I):
            table["footnotes"].append(line)
        elif "|" in line:
            cells = [c.strip() for c in line.split("|")]
            if not table["header"] or (not table["rows"] and not any(re.match(r"^\d", c) for c in cells[1:])):
                table["header_lines"].append(cells)
                # Keep the most detailed header while preserving all tiers.
                if len(cells) >= len(table["header"]):
                    table["header"] = cells
            else:
                row = dict(label=cells[0], cells=cells[1:])
                if parent:
                    row["parent_label"] = parent
                table["rows"].append(row)
        else:
            parent = line
    for table in tables:
        table["footnotes"] += [_norm(c.lstrip("# ")) for c in comments
                               if re.match(r"#\s*footnote\b", c, re.I)]
    return tables


def _measure(row, table):
    applicable = []
    label = row["label"].lower().rstrip("*†‡ ")
    for note in table["footnotes"]:
        # Explicit 'for <row>' restricts a note; markers bind marked rows.
        targets = re.findall(r"\bfor\s+([^.;:]+)", note, re.I)
        marker = re.match(r"^([*†‡a])(?:\s|(?=[A-Z]))", note)
        scoped = any(label in target.lower() for target in targets)
        global_note = not targets or any(re.search(r"\b(?:all|column|outcomes|rows|estimates)\b", t, re.I) for t in targets)
        if (scoped or global_note) and (not marker or marker[1] in row["label"] or global_note and "column" in note.lower()):
            applicable.extend(_measures(note))
    found = set(applicable)
    if found:
        return (next(iter(found)) if len(found) == 1 else "UNKNOWN", "footnote")
    found = _measures(" ".join(" ".join(h) for h in table.get("header_lines", [table["header"]])))
    if found:
        return (next(iter(found)) if len(found) == 1 else "UNKNOWN", "header")
    found = _measures(row["label"])
    return (next(iter(found)) if len(found) == 1 else "UNKNOWN", "row label")


_NUM = r"\d+(?:\.\d+)?"
_EFFECT = re.compile(rf"^({_NUM})\s*\(\s*(?:95%\s*CI[:,]?\s*)?({_NUM})\s*(?:-|to|,)\s*({_NUM})\s*\)$", re.I)
_COUNT = re.compile(r"^(\d[\d,]*)(?:\s*/\s*(\d[\d,]*))?(?:\s*\(\s*([<>]?\d+(?:\.\d+)?)\s*%?\s*\))?[*†‡]?$" )


def typed(row, table):
    measure, basis = _measure(row, table)
    refused, arms, effects = [], [], []
    context = _norm("\n".join(table.get("comments", [])) + "\n" + table["caption"])
    header = table["header"]
    aligned = len(row["cells"]) == len(header) - 1
    if not aligned:
        refused.append(f"{row['label']}: column count does not match header; refused arm alignment")
    for i, cell in enumerate(row["cells"]):
        match = _EFFECT.fullmatch(_norm(cell))
        if match:
            value, low, high = map(float, match.groups())
            if 0 < low <= value <= high:
                effects.append(dict(value=value, ci_low=low, ci_high=high))
            else:
                refused.append(f"{row['label']}: invalid positive ratio CI {cell}")
            continue
        if not aligned:
            continue
        h = header[i + 1]
        if re.search(r"p[- ]?value|\brate\b|pt-yr|patient-years|leading to discontinuation", h, re.I) or _measures(h):
            continue
        m = _COUNT.fullmatch(cell)
        if not m:
            continue
        denom = re.search(r"\bn\s*=\s*([\d,]+)", h, re.I)
        n = int(m[2].replace(",", "")) if m[2] else int(denom[1].replace(",", "")) if denom else None
        pct = m[3]
        # Parenthetic rates in regulatory tables are not patient percentages.
        is_rate = bool(re.search(r"%/year|per 100.*years", h + " " + table["caption"], re.I))
        patients = bool(re.search(r"patients|participants|\bn\s*\(\s*%\)|no\.\s*\(\s*%\)", h, re.I))
        events = bool(re.search(r"\bevents\b", h, re.I))
        if not patients and not events:
            patients = bool(re.search(r"no\. of patients|participants|n\s*\(%\)", table["caption"] + " " + row.get("parent_label", ""), re.I))
        unit = "PATIENTS" if patients else "EVENTS" if events else "UNKNOWN"
        arms.append(dict(n_events=int(m[1].replace(",", "")), n_denominator=n,
                         percent=float(pct) if pct and not pct.startswith(("<", ">")) and not is_rate else None,
                         percent_bound=pct if pct and pct.startswith(("<", ">")) and not is_rate else None,
                         column=h, count_unit=unit))
    units = {a["count_unit"] for a in arms}
    unit = next(iter(units)) if len(units) == 1 else "UNKNOWN"
    effect = effects[0] if len(effects) == 1 else None
    if len(effects) > 1:
        refused.append(f"{row['label']}: multiple published effects; refused choosing adjustment")
    if measure == "UNKNOWN":
        refused.append(f"{row['label']}: unresolved published measure")
    candidates = []
    if effect:
        candidates.append(dict(measure=measure, derivation="PUBLISHED", effect=effect,
                               admissible=measure != "UNKNOWN"))
    patient_arms = [a for a in arms if a["count_unit"] == "PATIENTS"]
    if len(patient_arms) == 2 and all(a["n_denominator"] and 0 <= a["n_events"] <= a["n_denominator"] for a in patient_arms) and patient_arms[1]["n_events"] > 0:
        a, b = patient_arms
        rr = (a["n_events"] / a["n_denominator"]) / (b["n_events"] / b["n_denominator"])
        candidates.append(dict(measure="RISK_RATIO", derivation="RECONSTRUCTED",
                               effect=dict(value=rr, ci_low=None, ci_high=None),
                               arms=patient_arms, admissible=True))
    else:
        refused.append(f"{row['label']}: refused reconstructed risk ratio: need exactly two patient arms, explicit valid denominators, and nonzero comparator risk")
    window = [m.group(0) for m in re.finditer(r"through\s+\d+\s+days\s+after[^.;\n]*|within the previous[^.;\n)]*|on[- ]treatment(?: plus \d+ days)?", context, re.I)]
    population = [m.group(0) for m in re.finditer(r"safety population|safety analysis set|all treated patients|\btreated\b|at least one dose|on[- ]treatment", context, re.I)]
    return dict(measure=measure, measure_basis=basis, count_unit=unit, arms=arms,
                effect=effect, candidates=candidates, window=list(dict.fromkeys(window)),
                analysis_population=list(dict.fromkeys(population)),
                variant_flags=variants(row), refusals=refused)


def select(table, outcome_keywords, exclude_variants):
    if isinstance(outcome_keywords, str):
        outcome_keywords = [outcome_keywords]
    known = {"NON_CABG", "LEADING_TO_DISCONTINUATION", "SERIOUS"}
    if set(exclude_variants) - known:
        return None, "refused unknown excluded variants: " + ", ".join(sorted(set(exclude_variants) - known))
    matches, refused = [], []
    for row in table["rows"]:
        if any(re.search(r"(?<!\w)" + re.escape(_norm(k).lower()) + r"(?!\w)", row["label"].lower()) for k in outcome_keywords if k.strip()):
            flags = set(variants(row)) & set(exclude_variants)
            if flags:
                refused.append(row["label"] + ": " + ", ".join(sorted(flags)))
            else:
                matches.append(row)
    if len(matches) == 1:
        return matches[0], "selected unique outcome row"
    if len(matches) > 1:
        return None, "refused ambiguous outcome rows: " + "; ".join(r["label"] for r in matches)
    return None, "refused: " + ("; ".join(refused) or "no row label names requested outcome")
