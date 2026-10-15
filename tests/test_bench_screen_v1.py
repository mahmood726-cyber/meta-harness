"""Offline preregistration contracts; all article/trial fixtures are synthetic."""
import importlib.util
from pathlib import Path
import random

import pytest

SPEC = importlib.util.spec_from_file_location('bench_screen_v1', Path(__file__).resolve().parents[1] / 'scripts/bench_screen_v1.py')
bench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bench)


@pytest.fixture
def screen(monkeypatch):
    def run(k=3, ids=None, start='2011-01', registered='2010-12', license='cc by', topics=(), areas=None, extra=''):
        ids = ids if ids is not None else ['NCT00000001', 'NCT00000002', 'NCT00000003']
        abstract = f'We included {k} randomized controlled trials in a pairwise meta-analysis. The primary outcome was mortality. Drugtest reduced mortality.'
        xml = f'<article><front><article-meta><abstract><p>{abstract}</p></abstract></article-meta></front><body><sec><title>Results</title><p>Included trials: {" ".join(ids)}</p>{extra}<fig><caption><p>Forest plot of mortality.</p></caption></fig></sec></body></article>'.encode()
        monkeypatch.setattr(bench, 'fetch_xml', lambda *a: xml)
        monkeypatch.setattr(bench, 'fetch_registry', lambda rid, client: {'id': rid, 'registry': 'NCT', 'start': start, 'registered': registered, 'source': 'fixture'})
        hit = {'id': '123', 'pmid': '123', 'pmcid': 'PMC123', 'title': 'Cardiovascular drugtest meta-analysis', 'license': license, 'abstractText': abstract}
        return bench.screen_candidate(hit, object(), list(topics), areas or {})
    return run


def test_order():
    hits = [{'id': str(i)} for i in [10, 2, 5, 1]]
    expected = sorted(hits, key=lambda h: int(h['id']))
    random.Random(bench.SEED).shuffle(expected)
    assert bench.order_hits(hits) == expected == bench.order_hits(hits[::-1])


def test_old_trial(screen):
    assert screen(start='2009-12')['first_failure'] == 'C5'


def test_registration_month(screen):
    assert screen(start='2011-01', registered='2011-02')['first_failure'] == 'C6'
    assert screen(start='2011-01-01', registered='2011-01-31')['verdict'] == 'QUALIFIES'


def test_missing_id(screen):
    result = screen(k=6, ids=[f'NCT{i:08}' for i in range(1, 6)])
    assert result['first_failure'] == 'C4'
    assert len(result['evidence']['ids']) == 5


def test_license(screen):
    assert screen(license='CC BY-NC')['first_failure'] == 'C1'


def test_overlap(screen):
    topic = {'slug': 'fixture', 'intervention_terms': ['drugtest'], 'primary_outcome': {'name': 'mortality', 'keywords': ['mortality']}}
    assert screen(topics=[topic])['first_failure'] == 'C8'


def test_area_cap(screen):
    assert screen(areas={'cardiovascular': 3})['verdict'] == 'EXCLUDED_AREA_CAP'


def test_reference_ids_ignored(screen):
    assert screen(extra='<ref-list><ref>NCT99999999</ref></ref-list>')['verdict'] == 'QUALIFIES'


def test_unreadable_dates(screen):
    assert screen(start=None, registered=None)['first_failure'] == 'C6'


def test_network_error(screen, monkeypatch):
    # Set up monkeypatched article first, then fail the registry fetch.
    screen()
    monkeypatch.setattr(bench, 'fetch_registry', lambda *a: (_ for _ in ()).throw(bench.FetchError('offline fixture')))
    hit = {'id': '123', 'pmid': '123', 'pmcid': 'PMC123', 'title': 'Cardiovascular meta-analysis', 'license': 'cc by'}
    assert bench.screen_candidate(hit, object(), [], {})['verdict'] == 'SCREEN_ERROR'


def test_query_is_verbatim():
    import hashlib
    assert bench.QUERY in bench.PREREG.read_text(encoding='utf-8')
    assert bench.SEED == int(hashlib.sha256(bench.QUERY.encode('utf-8')).hexdigest()[:8], 16)


def test_cursor_paging():
    from urllib.parse import urlparse, parse_qs
    class Client:
        def get(self, url, kind):
            query = parse_qs(urlparse(url).query)
            assert query['query'] == [bench.QUERY]
            assert query['pageSize'] == ['1000']
            assert query['resultType'] == ['core']
            assert query['format'] == ['json']
            if query['cursorMark'] == ['*']:
                return {'hitCount': 2, 'resultList': {'result': [{'id': '8'}]}, 'nextCursorMark': 'next'}
            assert query['cursorMark'] == ['next']
            return {'hitCount': 2, 'resultList': {'result': [{'id': '2'}]}}
    assert bench.search_hits(Client()) == [{'id': '8'}, {'id': '2'}]


def test_registry_date_source():
    class Client:
        def get(self, url, kind):
            assert url == 'https://clinicaltrials.gov/api/v2/studies/NCT00000001?fields=protocolSection.statusModule'
            return {'protocolSection': {'statusModule': {'startDateStruct': {'date': '2010-01'}, 'studyFirstSubmitDate': '2010-01-31'}}}
    result = bench.fetch_registry('NCT00000001', Client())
    assert result['start'] == '2010-01'
    assert result['registered'] == '2010-01-31'
    assert bench.fetch_registry('2020-123456-12', object())['start'] is None


def test_mesh_major_priority():
    area, evidence = bench.therapeutic_area({'title': 'Cardiovascular disease', 'meshHeadingList': {'meshHeading': [{'descriptorName': 'Diabetes Mellitus', 'majorTopic_YN': 'Y'}]}})
    assert area == 'endocrine/metabolic'
    assert evidence['source'] == 'MeSH major headings'


def test_table_row_threshold():
    ids = [f'NCT{i:08}' for i in range(1, 6)]
    def table(n):
        rows = ''.join(f'<tr><td>{rid}</td><td>2</td></tr>' for rid in ids[:n])
        return bench.parse_xml(f'<article><body><table-wrap><caption>Pooled mortality</caption><table>{rows}</table></table-wrap></body></article>'.encode())
    assert bench.per_trial_rows(table(4), ids, 5, 'The primary outcome was mortality.')['kind'] == 'table'
    assert bench.per_trial_rows(table(3), ids, 5, 'The primary outcome was mortality.') is None


def test_html_is_not_xml_data():
    with pytest.raises(bench.FetchError):
        bench.parse_xml(b'<html><body>Unavailable</body></html>')


def test_registry_patterns_and_ctis_not_double_counted():
    values = ['NCT00000001', 'EudraCT 2020-123456-12', 'ISRCTN12345678', 'ACTRN12345678901234', 'ChiCTR-ABC123', 'CTRI/2020/01/123456', 'UMIN123456789', 'jRCT123', 'DRKS12345678', 'IRCT123', 'NTR123', 'PACTR123', 'KCT1234567', '2020-123456-12-34']
    root = bench.parse_xml(('<article><body><p>Included trials: ' + ' '.join(values) + '</p></body><back><ref-list><ref>NCT99999999</ref></ref-list></back></article>').encode())
    ids, _ = bench.included_ids(root)
    assert len(ids) == len(values)
    assert 'NCT99999999' not in ids


def test_forest_caption_names_outcome_without_outcome_statement():
    root = bench.parse_xml(b'<article><body><fig><caption>Forest plots of HRs for progression-free survival in the treatment and control groups.</caption></fig></body></article>')
    result = bench.per_trial_rows(root, ['NCT00000001'], 1, 'Pooling trials improved progression-free survival.')
    assert result is not None
    assert result['outcome'] == 'progression-free survival'


def test_supplementary_forest_is_article_xml():
    root = bench.parse_xml(b'<article><body/><back><supplementary-material><fig><caption>Forest plot of mortality.</caption></fig></supplementary-material></back></article>')
    assert bench.per_trial_rows(root, [], 3, 'The primary outcome was mortality.') is not None


def test_myeloma_area():
    assert bench.therapeutic_area({'title': 'Multiple myeloma meta-analysis'})[0] == 'oncology'
