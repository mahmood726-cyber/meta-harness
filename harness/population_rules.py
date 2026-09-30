"""Explicit outcome population policy and source-span consistency checks."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

from .timepoint_identity import plain, row_span

Population = Literal['INTENTION_TO_TREAT', 'MODIFIED_ITT', 'AS_TREATED',
                     'SAFETY_POPULATION', 'PER_PROTOCOL', 'UNKNOWN']


def classify(row: dict | str) -> Population:
    s = plain(row_span(row) if isinstance(row, dict) else row).lower()
    if re.search(r'\bsafety (?:population|analysis set)\b', s):
        return 'SAFETY_POPULATION'
    if re.search(r'\bas[- ]treated\b|\btreated (?:patients|population)\b'
                 r'|\breceived (?:at least|≥|>=) (?:one|1) dose\b', s):
        return 'AS_TREATED'
    if re.search(r'\bmodified (?:intention[- ]to[- ]treat|itt)\b|\bmitt\b', s):
        return 'MODIFIED_ITT'
    if re.search(r'\bper[- ]protocol\b|\bcompleters\b', s):
        return 'PER_PROTOCOL'
    if re.search(r'\bintention[- ]to[- ]treat\b|\bitt\b|\brandomi[sz]ed\b', s):
        return 'INTENTION_TO_TREAT'
    return 'UNKNOWN'


@dataclass(frozen=True)
class PopulationRule:
    efficacy: Population
    safety: Population
    selected: Population
    basis: str


def outcome_specs(config: dict):
    if config.get('primary_outcome'):
        yield config['primary_outcome'], 'efficacy'
    for spec in config.get('secondary_outcomes', []):
        yield spec, 'efficacy'
    for spec in config.get('harm_outcomes', []):
        yield spec, 'harm'


def rule_for(outcome: dict, config: dict, protocol_text: str = '') -> PopulationRule:
    spec = next((s for s, _ in outcome_specs(config) if s['name'] == outcome['name']), outcome)
    kind = next((k for s, k in outcome_specs(config) if s['name'] == outcome['name']), outcome.get('kind'))
    field = spec.get('population') or config.get('population') or ''
    if not field:
        m = re.search(r'(?im)^\s*[-*]?\s*\*{0,2}Population\*{0,2}\s*[-:–—]\s*([^\n]+)', protocol_text)
        field = m.group(1) if m else ''
    efficacy = classify(field)
    selected = 'SAFETY_POPULATION' if kind in ('harm', 'safety') else efficacy
    return PopulationRule(efficacy, 'SAFETY_POPULATION', selected,
                          'harm outcome kind' if kind in ('harm', 'safety') else field or 'POPULATION_RULE_MISSING')


def admissibility(row: dict, rule: PopulationRule) -> dict:
    pop = classify(row)
    allowed = pop == rule.selected and pop != 'UNKNOWN'
    if rule.selected == 'SAFETY_POPULATION' and pop == 'AS_TREATED':
        allowed = True
    return {'allowed': allowed, 'population': pop, 'id': row.get('id'),
            'code': None if allowed else ('POPULATION_UNKNOWN' if pop == 'UNKNOWN' else
                                         'POPULATION_RULE_MISSING' if rule.selected == 'UNKNOWN' else
                                         'POPULATION_MISMATCH')}


def consistency(review: dict, config: dict) -> list[dict]:
    """Opposite *population* decisions, not absence for unrelated reasons.

    A refusal's explicit population rationale can witness its classification;
    it is labelled as review evidence, not silently promoted to primary text.
    """
    problems = []
    for outcome in review.get('outcomes', []):
        rule = rule_for(outcome, config, review.get('protocol', {}).get('text', ''))
        accepted = {}
        for row in outcome.get('trials', []):
            pop = classify(row)
            accepted.setdefault(pop, []).append(str(row.get('id')))
        for row in outcome.get('declared_absent_trials', []):
            if row.get('reason_code') != 'POPULATION_MISMATCH':
                continue
            pop = classify(row)
            basis = 'source span'
            if pop == 'UNKNOWN':
                pop = classify(row.get('reason', ''))
                basis = 'review refusal rationale'
            if pop != 'UNKNOWN' and accepted.get(pop):
                problems.append({'code': 'POPULATION_RULE_INCONSISTENT', 'outcome': outcome['name'],
                                 'population': pop, 'rule': rule.selected, 'accepted': accepted[pop],
                                 'refused': [str(row.get('id'))], 'basis': basis})
    return problems
