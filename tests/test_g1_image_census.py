import pytest

from scripts.g1_image_census import classify, licence_gate, parse_reads, already_read, census, render


@pytest.mark.parametrize('name,kind', [
    ('x_Fig1_HTML.jpg', 'ARTICLE_FIGURE'),
    ('pone.123.g003.tif', 'ARTICLE_FIGURE'),
    ('CD012-fig-002.jpg', 'ARTICLE_FIGURE'),
    ('jcm-12-123-f001.png', 'ARTICLE_FIGURE'),
    ('abc-F2.jpg', 'ARTICLE_FIGURE'),
    ('fig1.gif', 'ARTICLE_FIGURE'),
    ('f0015.jpg', 'ARTICLE_FIGURE'),
    ('Fig2.jpg', 'ARTICLE_FIGURE'),
    ('x_Tab4_ESM.jpg', 'SUPPLEMENT_TABLE_IMAGE'),
    ('Table S2.png', 'SUPPLEMENT_TABLE_IMAGE'),
    ('eTable3.png', 'SUPPLEMENT_TABLE_IMAGE'),
    ('supplement-T1-page.png', 'SUPPLEMENT_TABLE_IMAGE'),
    ('article-T1-page.png', 'UNKNOWN_IMAGE'),
    ('x_Fig8_ESM.jpg', 'SUPPLEMENT_FIGURE_IMAGE'),
    ('eFigure2.png', 'SUPPLEMENT_FIGURE_IMAGE'),
    ('Figure S2.png', 'SUPPLEMENT_FIGURE_IMAGE'),
    ('mmc1.png', 'SUPPLEMENT_FIGURE_IMAGE'),
    ('Data_Sheet_1.PDF#p7.png', 'SUPPLEMENT_FIGURE_IMAGE'),
    ('mystery123.png', 'UNKNOWN_IMAGE'),
    ('supplement-F2.png', 'SUPPLEMENT_FIGURE_IMAGE'),
])
def test_names(name, kind):
    assert classify(name)[0] == kind


@pytest.mark.parametrize('value', ['cc-by', 'cc0', 'cc by', 'public domain', 'CC-BY'])
def test_open(value):
    assert licence_gate(value) == 'OPEN_FOR_MODEL'


@pytest.mark.parametrize('value', ['cc-by-nc', 'cc-by-nd', 'cc-by-sa', 'CC_RESTRICTED', 'NOT_OPEN', '', None, 'other'])
def test_closed(value):
    assert licence_gate(value) == 'DETERMINISTIC_ONLY'


def test_reads():
    reads = parse_reads('| topic | PMID 123 | Fig2 | **REFUSED** |\n'
                        '| other | PMID 456 | mmc1.pdf#p7 | **ACCEPTED** |')
    assert already_read('123', 'x_Fig2_HTML.jpg', reads)
    assert already_read('123', 'F002.gif', reads)
    assert not already_read('123', 'x_Fig2_ESM.jpg', reads)
    assert not already_read('124', 'Fig2.jpg', reads)
    assert already_read('456', 'mmc1.pdf#p7.png', reads)
    assert not already_read('456', 'mmc1.pdf#p8.png', reads)
    assert not already_read('456', 'mmc1.png', reads)


def test_funnel_unknown_and_no_missing():
    def meta(names, licence='cc-by'):
        return {'licence': licence, 'files': [{'file': n, 'format': 'png'} for n in names]}
    data = {'topic': {'metas': {'1': meta(['eTable1.png', 'odd.png']),
                              '2': meta(['eFigure1.png']),
                              '3': meta(['eFigure2.png'], 'cc-by-nc'),
                              '4': meta(['Fig1.png'])},
                      'attempts': [{'meta': '1', 'trial': 'missing A'},
                                   {'meta': '3', 'trial': 'missing B'}]}}
    result = census(data, set())
    f = result['overall']['funnel']
    assert [v['n'] for v in f.values()] == [4, 3, 2, 1, 1]
    assert all(v['n'] <= v['N'] for v in f.values())
    assert result['overall']['trials_affected'] == {'n': 1, 'N': 2}
    assert result['metas'][1]['missing_trials'] == []
    assert result['unknown_files'][0]['file'] == 'odd.png'
    assert 'odd.png' in render(result)


def test_empty_and_repeat_deterministic():
    assert census({}, set()) == census({}, set())
    assert census({}, set())['overall']['trials_affected'] == {'n': 0, 'N': 0}
