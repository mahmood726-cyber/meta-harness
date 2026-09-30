"""Conservative, span-bound time and count identity. No inferred source values."""
from __future__ import annotations

from dataclasses import dataclass
from html import unescape
import re
from typing import Literal

Origin = Literal['DAY1_IS_BASELINE', 'DAY0_IS_BASELINE', 'UNSTATED']
Decision = Literal['MATCH', 'MISMATCH', 'TARGET_MISSING']
CountUnit = Literal['PATIENTS', 'EVENTS', 'UNKNOWN']


def plain(span: str) -> str:
    return ' '.join(unescape(re.sub(r'<[^>]*>', ' ', span or '')).split())


_ORIGIN = re.compile(
    r'\bday\s*([01])\s*(?:\(\s*|=\s*|is\s+|was\s+|defined as\s+)'
    r'(?:the\s+)?(?:day of\s+)?(?:inclusion|randomi[sz]ation|enrol[l]?ment|baseline)\b', re.I)
_TIME = re.compile(r'\b(?:(day|week)s?\s*[- ]?\s*(\d+(?:\.\d+)?)'
                   r'|(\d+(?:\.\d+)?)\s*[- ]?\s*(days?|weeks?))\b', re.I)


@dataclass(frozen=True)
class Timepoint:
    value: float | None
    unit: str | None
    origin: Origin
    elapsed_days: float | None
    refusal: str | None = None


def origin_spans(span: str) -> list[str]:
    return [m.group(0) for m in _ORIGIN.finditer(plain(span))]


def parse(span: str, origin_span: str = '') -> Timepoint:
    """Parse one bound result, never an entire multi-endpoint article.

    Unstated day labels retain their numeric convention; only an explicit day-1
    baseline subtracts one, and only for ordinal day labels (not durations/weeks).
    Ambiguous/ranged/unsupported windows refuse instead of selecting a number.
    """
    text = plain(span)
    origins = {m.group(1) for m in _ORIGIN.finditer(text + ' ' + plain(origin_span))}
    origin: Origin = 'UNSTATED'
    if len(origins) > 1:
        return Timepoint(None, None, origin, None, 'TIME_ORIGIN_CONFLICT')
    if origins:
        origin = 'DAY1_IS_BASELINE' if '1' in origins else 'DAY0_IS_BASELINE'
    text = _ORIGIN.sub('', text)
    if re.search(r'\b(?:days?|weeks?)\s*\d+\s*[-–—/]\s*\d+|\b\d+\s*[-–—/]\s*\d+\s*(?:days?|weeks?)', text, re.I):
        return Timepoint(None, None, origin, None, 'TIMEPOINT_RANGE_UNRESOLVED')
    candidates = set()
    for m in _TIME.finditer(text):
        unit = (m.group(1) or m.group(4)).lower().rstrip('s')
        value = float(m.group(2) or m.group(3))
        elapsed = value * (7 if unit == 'week' else 1)
        if m.group(1) and unit == 'day' and origin == 'DAY1_IS_BASELINE':
            elapsed -= 1
        candidates.add((value, unit, elapsed))
    if len(candidates) != 1:
        return Timepoint(None, None, origin, None,
                         'TIMEPOINT_AMBIGUOUS' if candidates else 'TIMEPOINT_UNSTATED')
    value, unit, elapsed = candidates.pop()
    if elapsed < 0:
        return Timepoint(value, unit, origin, None, 'TIMEPOINT_BEFORE_BASELINE')
    return Timepoint(value, unit, origin, elapsed)


def compare(target: str | Timepoint | None, result: str | Timepoint) -> Decision:
    if target is None or (isinstance(target, str) and not target.strip()):
        return 'TARGET_MISSING'
    t = parse(target) if isinstance(target, str) else target
    r = parse(result) if isinstance(result, str) else result
    if t.elapsed_days is None or r.elapsed_days is None or t.refusal or r.refusal:
        return 'MISMATCH'
    return 'MATCH' if t.elapsed_days == r.elapsed_days else 'MISMATCH'


def row_span(row: dict) -> str:
    return next((row[k] for k in ('source', 'source_span', 'verbatim_span', 'span')
                 if isinstance(row.get(k), str) and row[k]), '')


def count_unit(span: str) -> CountUnit:
    """Requires a result-bound span. Mixed table rows remain UNKNOWN."""
    s = plain(span).lower()
    patient = bool(re.search(r'\b(?:patients|participants)\s+(?:with|who|had|experienced)\b'
                             r'|\bn\s*\(%\)\s*of\s+(?:patients|participants)\b'
                             r'|\b(?:occurred|reported|observed) in\s+\d+(?:\.\d+)?(?:% of|\s+of\s+\d+)?\s+(?:patients|participants)\b', s))
    explicit_events = bool(re.search(r'\b(?:\d+(?:\.\d+)?|number of|total|recurrent)\s+(?:(?:serious|adverse|major)\s+){0,2}(?:events|episodes)\b'
                                    r'|\b(?:events|episodes)\s*,?\s*n\b', s))
    if patient:
        return 'UNKNOWN' if explicit_events else 'PATIENTS'
    if explicit_events or re.fullmatch(r'(?:events|episodes)', s):
        return 'EVENTS'
    return 'UNKNOWN'


def pool_problems(rows: list[dict]) -> list[dict]:
    units = [(str(r.get('id', i)), count_unit(row_span(r))) for i, r in enumerate(rows)]
    problems = []
    if {'PATIENTS', 'EVENTS'} <= {u for _, u in units}:
        problems.append({'code': 'UNIT_MIX_POOLED', 'refused': [i for i, _ in units],
                         'units': dict(units)})
    unknown = [i for i, u in units if u == 'UNKNOWN']
    if unknown:
        problems.append({'code': 'COUNT_UNIT_UNKNOWN', 'refused': unknown})
    return problems
