"""Reader A x reader B on supplement images: only agreed rows become SECONDARY_PROVISIONAL; nothing is PRIMARY."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import lane_image_agreement as lia  # noqa: E402


def reading(rows, measure='RR', legible=True, kind='study'):
    return dict(legible=legible, row_kind=kind, measure=measure, model_printed=None, notes='',
                pooled=dict(label=None, effect=None, lower=None, upper=None), rows=rows)


def row(label, e, lo, up, et='4', nt='305', ec='4', nc='154'):
    return dict(label=label, effect=e, lower=lo, upper=up, weight_pct=None,
                events_t=et, n_t=nt, events_c=ec, n_c=nc)


def item(rows, sha='s1', png='p1'):
    return dict(sha256=sha, attached_sha256=png, file='Fig6.jpg', meta='m', state='READER_A_ONLY',
                record_id='mc-a', reading=reading(rows), candidates=[],
                sources=[dict(topic='t', missing_trials=['FAIR-HF [20]'])])


def answer(rows, sha='s1', png='p1', **kw):
    return dict(key=sha, image_sha256=png, prompt_sha256='ph', answer=reading(rows, **kw))


def run(items, answers):
    return lia.run(dict(images=items), answers, 'm-b', {}, 11)


def test_agreed_row_is_secondary_and_never_primary():
    images, recs, funnel, trials = run([item([row('FAIR-HF', '0.49', '0.12', '1.96')])],
                                       [answer([row('FAIR-HF', '0.49', '0.12', '1.96')])])
    assert images[0]['proposed'][0]['state'] == 'SECONDARY_PROVISIONAL'
    assert trials == [('t', 'FAIR-HF [20]')] and funnel['primary_verified'] == 0
    assert all(r['attested'] is False for r in recs.values())


def test_value_disagreement_refused_with_both_readings():
    images, _, funnel, trials = run([item([row('FAIR-HF', '0.49', '0.12', '1.96')])],
                                    [answer([row('FAIR-HF', '0.94', '0.12', '1.96')])])
    assert images[0]['proposed'] == [] and trials == []
    ref = images[0]['refused'][0]
    assert 'EFFECT_DISAGREES' in ref['why'] and ref['a'] and ref['b']


def test_count_disagreement_refused():
    images, *_ = run([item([row('FAIR-HF', '0.49', '0.12', '1.96')])],
                     [answer([row('FAIR-HF', '0.49', '0.12', '1.96', et='5')])])
    assert images[0]['proposed'] == []


def test_reader_b_saw_a_different_image_is_not_compared():
    images, _, funnel, _ = run([item([row('FAIR-HF', '0.49', '0.12', '1.96')])],
                               [answer([row('FAIR-HF', '0.49', '0.12', '1.96')], png='OTHER')])
    assert images[0]['state'] == 'READER_B_IMAGE_MISMATCH' and funnel['agreed_rows'] == 0


def test_missing_reader_b_admits_nothing():
    images, _, funnel, _ = run([item([row('FAIR-HF', '0.49', '0.12', '1.96')])], [])
    assert images[0]['state'] == 'READER_B_MISSING' and funnel['agreed_rows'] == 0


def test_measure_disagreement_blocks_every_row():
    images, *_ = run([item([row('FAIR-HF', '0.49', '0.12', '1.96')])],
                     [answer([row('FAIR-HF', '0.49', '0.12', '1.96')], measure='MD')])
    assert images[0]['proposed'] == [] and images[0]['refused'][0]['why'].startswith('FIGURE_MEASURE')


def test_reader_b_schema_failure_admits_nothing():
    a = answer([row('FAIR-HF', '0.49', '0.12', '1.96')])
    del a['answer']['pooled']
    images, *_ = run([item([row('FAIR-HF', '0.49', '0.12', '1.96')])], [a])
    assert images[0]['state'] == 'READER_B_SCHEMA'
