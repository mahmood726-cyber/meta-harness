"""Explicit recorded ledgers and interpretive limits for the remaining legacy prose."""
from .remainder_prose import Builder


LIMITS = {
    'sample': ('A selected topic sample cannot establish performance across the whole field.',
               'A representative sampling frame and prespecified success criteria could support broader evaluation.'),
    'bias': ('Machine-available risk-of-bias signals are partial; unassessed domains prevent a complete assessment.',
             'A source-based human assessment may reach different domain judgements.'),
    'snapshot': ('A fixed registry snapshot cannot establish coverage of later registrations or posted results.',
                 'A dated re-search may identify additional records and change the evidence set.'),
    'enumeration': ('PMID enumeration retrieves known items and does not establish discovery completeness.',
                    'An independently executed concept search may identify eligible records outside the enumeration.'),
    'recall': ('Known-item recovery is not systematic-review recall: trials absent from the known set are absent from its denominator. Recovery measures reach, not eligibility or poolability.',
               'Recall requires an independently generated reference universe; its result may differ from known-item recovery.'),
    'ghost': ('Broad registry enumeration and incomplete publication linkage limit interpretation of records without linked publications. Posted results do not by themselves establish eligibility or poolability.',
              'Some unlinked records may have publications, and some posted results may not support the target estimand.'),
    'dual': ('Rule-screening agreement is not independent inter-rater reliability when rule sets share authorship and eligibility criteria.',
             'Independent assessors with different information or methods may disagree.'),
    'integrity': ('A historical integrity check cannot establish current retraction status for every pooled source. The earlier claim that none of the checked pooled trials is retracted applies only to that historical checked set, not to a current independent check.',
                  'A current independent check may identify changes outside the historical checked set.'),
    'extract': ('Agreement between recorded extractions does not establish that both are correct or that uncheckable values are verified.',
                'Independent full-source extraction may identify errors or resolve values absent from abstracts.'),
    'retracted': ('RETRACTED (round-2): reproducibility claim not currently supported. This page does not claim byte-for-byte reproduction from the protocol SHA alone; mutable post-registration caches and extraction state are additional inputs. Independent repeatability of a fresh search is not established.',
                  'A manifest pinning every build input plus a successful clean replay could support a narrower reproducibility claim; a fresh search may still retrieve different evidence.'),
}


def limit(name, graph=None):
    b = Builder(graph)
    return b.finish(b.interpretation(*LIMITS[name]))


def recorded(name, record, graph=None):
    b = Builder(graph)
    return b.finish(b.decision('recorded.' + name, record, 'Recorded ' + name.replace('_', ' ')))


def records(review):
    search = review.get('search') or {}
    screening = review.get('screening') or {}
    yield 'recall', search.get('recall') or {}
    yield 'ghost', search.get('ghost') or {}
    yield 'dual', screening.get('dual') or {}
    yield 'integrity', review.get('integrity') or {}
    yield 'extract', (review.get('reproduction') or {}).get('dual') or {}
    yield 'family_count_chain', review.get('family_count_chain') or {}
    yield 'grade_arithmetic', {k: (review.get('grade') or {}).get(k) for k in
        ('upgrades', 'unassessed_domains', 'imprecision_basis', 'arithmetic_rule')}
    for row in (review.get('comparator') or {}).get('reported') or []:
        yield 'comparator_estimate', row


def register(review, graph):
    for name in LIMITS:
        limit(name, graph)
    for name, record in records(review):
        recorded(name, record, graph)
