import copy
import json

import pytest

from harness import claimgraph, limitations, manuscript, page


def test_structural_table_headers_do_not_hide_sentences():
    graph = claimgraph.ClaimGraph()
    scan = claimgraph.scan_rendered(
        '<table><tr><th>95% CI</th><th>7 trials were included.</th>'
        '<td>7</td></tr></table><p>Estimate 0.87.</p>', graph)
    assert scan['structural_count'] == 1
    assert scan['rendered_units'] == 3
    assert len(scan['violations']) == 3
    assert all(v['code'] == 'SENTENCE_WITHOUT_OBJECT' for v in scan['violations'])


def test_grade_missing_assessment_is_owed_and_total_ignores_stale_summary():
    grade = {'domains': {'imprecision': {'assessed': True, 'downgrade': 1, 'basis': 'wide interval'}},
             'downgrades': 99}
    graph = claimgraph.review_graph({'grade': grade})
    assert graph.recompute('grade-downgrades') == 1
    assert graph.recompute('grade-certainty') == 'provisional'
    assert 'OWED' in graph.render('grade-domain-indirectness')
    assert 'NOT ASSESSED' in graph.render('grade-domain-indirectness')
    assert not graph.check()
    grade['domains']['imprecision']['basis'] = None
    assert 'JUDGEMENT_WITHOUT_BASIS' in claimgraph.grade_render(grade, 'grade-domain-imprecision')


@pytest.mark.parametrize('downgrade', [-1, 4, True, 0.5])
def test_invalid_grade_inputs_refuse(downgrade):
    graph = claimgraph.ClaimGraph()
    graph.add('grade', 'TRANSFORMATION', operation='certainty',
              inputs={'start': 3, 'domains': [{'assessed': True, 'downgrades': downgrade}] * 5},
              value='high')
    assert 'UNRENDERABLE' in graph.render('grade')


def test_strand_summary_recomputes_and_refuses_changed_input():
    review = json.loads((claimgraph.ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))
    strand = copy.deepcopy(review['strands']['strands'][0])
    graph = claimgraph.ClaimGraph()
    cid = claimgraph.register_strand(graph, strand)
    assert graph.recompute(cid)['k'] == len(strand['members'])
    assert '[TRANSFORMATION]' in graph.render(cid)
    assert not graph.check()
    ref = graph.objects[cid]['input_refs'][0]
    graph.objects[ref]['row']['effect'] = 19.876543
    assert 'UNRENDERABLE' in graph.render(cid)


def test_unmigrated_sensitivity_is_preserved():
    strand = {'strand': 'sensitivity', 'effect_measure': 'HR',
              'members': [{'effect': 0.8, 'ci_low': 0.7, 'ci_high': 0.9}],
              'pool': {'effect': 0.8, 'ci_low': 0.7, 'ci_high': 0.9,
                       'common_effect_sensitivity': {'effect': 0.81, 'ci_low': 0.71, 'ci_high': 0.91}}}
    assert claimgraph.strand_render(strand) is None
    assert 'common-effect sensitivity' in page.render_strands_section({'strands': [strand]})


def test_grade_renderers_share_registered_domain_objects():
    review = json.loads((claimgraph.ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))
    graph = claimgraph.review_graph(review)
    domain = graph.render('grade-domain-indirectness')
    assert domain in page.render_page(review)
    assert domain in limitations._grade_block(review['grade'])
    assert graph.render('grade-downgrades') in manuscript.render(review)


def test_provenance_batch_rechecks_mutations_and_next_call(tmp_path, monkeypatch):
    from types import SimpleNamespace
    source = tmp_path / 'source.txt'
    source.write_bytes(b'original')
    calls = []

    def git_show(*args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout=b'original')

    monkeypatch.setattr(claimgraph.subprocess, 'run', git_show)
    with claimgraph._provenance_batch():
        assert claimgraph._committed(tmp_path, source)
        assert claimgraph._committed(tmp_path, source)
        assert len(calls) == 1
        source.write_bytes(b'changed')
        assert not claimgraph._committed(tmp_path, source)
        assert len(calls) == 2
    source.write_bytes(b'original')
    assert claimgraph._committed(tmp_path, source)
    assert len(calls) == 3
