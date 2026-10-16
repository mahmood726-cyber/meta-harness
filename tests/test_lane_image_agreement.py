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


def test_conflicting_answers_for_one_image_fail_closed():
    import pytest
    a = answer([])
    b = answer([row('FAIR-HF', '0.49', '0.12', '1.96')])
    with pytest.raises(ValueError, match='CONFLICTING_READER_B'):
        lia.b_records([a, b], 'm-b', {})
    assert len(lia.b_records([a, dict(a)], 'm-b', {})) == 1      # an identical repeat is one reading


def test_record_id_names_the_model():
    a = answer([])
    x = lia.b_records([a], 'model-one', {})['s1']
    y = lia.b_records([a], 'model-two', {})['s1']
    assert x['record_id'] != y['record_id']


def test_same_answer_under_a_different_prompt_fails_closed():
    import pytest
    a = answer([])
    b = dict(a, prompt_sha256='other')
    with pytest.raises(ValueError, match='CONFLICTING_READER_B'):
        lia.b_records([a, b], 'm-b', {})


# second reader (claude-sonnet) findings, 16 Oct -- plants first
def _blank(**k):
    return {**row('FAIR-HF', None, None, None, et=None, nt=None, ec=None, nc=None), **k}


def test_vacuous_row_is_not_admitted():
    images, _, funnel, trials = run([item([_blank()])], [answer([_blank()])])
    assert images[0]['proposed'] == [] and trials == [] and funnel['agreed_rows'] == 0


def test_unlabelled_row_is_not_admitted():
    r = row(None, '1.0', '0.5', '2.0')
    images, _, funnel, _ = run([item([r])], [answer([dict(r)])])
    assert images[0]['proposed'] == [] and funnel['agreed_rows'] == 0


def test_sibling_row_disagreement_refuses_the_figure():
    a = [row('FAIR-HF', '0.49', '0.12', '1.96'), row('X', '1.0', '0.5', '2.0')]
    b = [row('FAIR-HF', '0.49', '0.12', '1.96'), row('X', '3.0', '0.5', '2.0')]
    images, _, _, trials = run([item(a)], [answer(b)])
    assert images[0]['proposed'] == [] and trials == []


def test_pooled_row_disagreement_refuses_the_figure():
    it = item([row('FAIR-HF', '0.49', '0.12', '1.96')])
    it['reading']['pooled'] = dict(label='overall', effect='1.0', lower='0.5', upper='2.0')
    images, *_ = run([it], [answer([row('FAIR-HF', '0.49', '0.12', '1.96')])])
    assert images[0]['proposed'] == []


def test_malformed_reader_a_is_a_refusal_not_a_crash():
    images, _, funnel, _ = run([item(['x'])], [answer([row('FAIR-HF', '0.49', '0.12', '1.96')])])
    assert images[0]['state'] == 'READER_A_SCHEMA' and funnel['agreed_rows'] == 0


def test_non_string_measure_is_a_refusal_not_a_crash():
    images, *_ = run([item([row('FAIR-HF', '0.49', '0.12', '1.96')])],
                     [answer([row('FAIR-HF', '0.49', '0.12', '1.96')], measure=5)])
    assert images[0]['state'] == 'READER_B_SCHEMA'


def test_orphan_reader_b_answer_is_counted():
    _, _, funnel, _ = run([item([])], [answer([], sha='s1'), answer([], sha='s2')])
    assert funnel['reader_b_orphans'] == 1


def test_missing_image_hash_never_matches():
    it = item([row('FAIR-HF', '0.49', '0.12', '1.96')], png=None)
    images, *_ = run([it], [answer([row('FAIR-HF', '0.49', '0.12', '1.96')], png=None)])
    assert images[0]['state'] == 'READER_B_IMAGE_MISMATCH'


# author-year identity for trials the census names by title (corticosteroid metas print 'Blum 2015')
IDENT = {'t': {'Adjunct prednisone therapy for patients': dict(pmid='25608756', surname='Blum',
                                                             years=['2015'])}}


def _titled(rows):
    it = item(rows)
    it['sources'] = [dict(topic='t', missing_trials=['Adjunct prednisone therapy for patients'])]
    return it


def test_author_year_label_matches_a_title_named_trial():
    r = row('Blum 2015', '0.49', '0.12', '1.96')
    images, _, _, trials = lia.run(dict(images=[_titled([r])]), [answer([dict(r)])], 'm-b', {}, 11, IDENT)
    c = images[0]['candidates']
    assert trials == [('t', 'Adjunct prednisone therapy for patients')]
    assert c[0]['basis'].startswith('AUTHOR_YEAR') and c[0]['pmid'] == '25608756'


def test_author_year_wrong_year_or_surname_does_not_match():
    for lab in ('Blum 2016', 'Blumberg 2015', 'Blum', '2015'):
        r = row(lab, '0.49', '0.12', '1.96')
        _, _, _, trials = lia.run(dict(images=[_titled([r])]), [answer([dict(r)])], 'm-b', {}, 11, IDENT)
        assert trials == [], lab


def test_author_year_twice_in_one_figure_is_ambiguous():
    rows = [row('Blum 2015', '0.49', '0.12', '1.96'), row('Blum 2015a', '0.5', '0.1', '2.0')]
    images, _, _, trials = lia.run(dict(images=[_titled(rows)]), [answer([dict(r) for r in rows])], 'm-b', {}, 11,
                                   IDENT)
    assert trials == []


def test_compound_surname_is_kept_whole():
    census = {'metas': [{'topic': 'T', 'missing_trials': ['Trial A']}]}
    ident = lia.build_identity(census, {'p1': {'title': 'Trial A'}},
                               {'result': {'p1': {'sortfirstauthor': 'van der Meer J', 'pubdate': '2020'}}})
    assert ident['T']['Trial A']['surname'] == 'van der Meer'
    src = [dict(topic='T', missing_trials=['Trial A'])]
    assert lia.author_year_candidates([{'label': 'Van 2020'}], src, ident) == []
    assert len(lia.author_year_candidates([{'label': 'van der Meer 2020'}], src, ident)) == 1


def test_one_row_matching_two_trials_credits_neither():
    ident = {'T': {'Trial A': dict(pmid='a', surname='Smith', years=['2020']),
                   'Trial B': dict(pmid='b', surname='Smith', years=['2020'])}}
    src = [dict(topic='T', missing_trials=['Trial A', 'Trial B'])]
    assert lia.author_year_candidates([{'label': 'Smith 2020'}], src, ident) == []
