"""Grade checks on extracted result clauses, enabled by the outcome declaration."""
import re

HIGH = re.compile(r'\bserious\b|\bsevere\b|\bSAEs?\b|\bgrade\s*(?:>=|≥)?\s*(?:[3-5]|III|IV|V)\b', re.I)

def mismatch(spec, row):
    if spec.get('grade') != 'any grade':
        return False
    cell = row.get('extracted_cell_span')
    if cell:
        return bool(HIGH.search(cell))
    span = row.get('source_span') or row.get('source') or ''
    # Extractors may retain a trailing negative safety sentence. A grade on a
    # different clause with no extracted result does not qualify this cell.
    clauses = re.split(r';|(?<=[.!?])\s+', span)
    numeric = [c for c in clauses if re.search(r'\d', c)]
    for clause in numeric:
        for hit in HIGH.finditer(clause):
            # Explicit absence of serious events is not the grade of the
            # preceding all-event result in the same sentence.
            prefix = clause[max(0, hit.start()-30):hit.start()]
            if re.search(r'\b(?:no|without)\s+(?:\w+\s+){0,2}$', prefix, re.I):
                continue
            if re.search(r'\b(?:any|all)[ -]grade\b', clause[:hit.start()], re.I):
                continue
            return True
    return False
