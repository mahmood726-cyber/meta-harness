"""Offline plants for recorded identities and the two consumers."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import identity_search as ids
from scripts import provenance_census as census
from scripts import fulltext_cascade as cascade


def put(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')
    return path


class Fake:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []
    def get(self, url, params=None):
        self.requests.append({'url': url, 'when_utc': '2026-01-01T00:00:00Z', 'response_sha256': 'a'*64})
        response = next(self.responses)
        return response.encode() if isinstance(response, str) else json.dumps(response).encode()


def registry_responses(pmids):
    study = {'protocolSection': {'identificationModule': {'nctId': 'NCT00000001', 'acronym': 'TEST'}}}
    xml = '<PubmedArticleSet>' + ''.join('<PubmedArticle><MedlineCitation><PMID>'+p+'</PMID><Article><ArticleTitle>TEST trial</ArticleTitle></Article></MedlineCitation></PubmedArticle>' for p in pmids) + '</PubmedArticleSet>'
    return [{'studies': [study]}, {'esearchresult': {'idlist': pmids}}, xml]


def test_r1_single_stops():
    entries = ids.search_identity(Fake(registry_responses(['123'])), 'Test 2020', '123', ['TEST'], [], [], {})
    assert len(entries) == 1
    assert entries[0]['verdict'] == 'FOUND_SAME'


def test_r1_ambiguous_stays_hand_named(tmp_path):
    entries = ids.search_identity(Fake(registry_responses(['123', '456'])), 'Test 2020', '123', ['TEST'], [], [], {})
    assert entries[0]['verdict'] == 'AMBIGUOUS'
    put(tmp_path, 'registry/identity_searches/s.json', {'slug': 's', 'entries': entries})
    assert ids.found_pmids('s', tmp_path) == set()


def test_reference_label_match_and_citation_search():
    xml = '<article><body><ref><label>[39]</label></ref></body><back><ref-list><ref><label>[40]</label><mixed-citation><surname>Galan</surname><year>2010</year><pub-id pub-id-type="doi">10.1/test</pub-id></mixed-citation></ref></ref-list></back></article>'
    refs = ids.reference_matches(xml, 'Galan 2010 [39]')
    assert len(refs) == 1
    assert refs[0].findtext('label') == '[40]'
    http = Fake([{'resultList': {'result': [{'source': 'MED', 'id': '123'}]}}])
    entries = ids.search_identity(http, 'Galan 2010 [39]', '123', [], [], refs, {})
    assert entries[-1]['route'] == 'R2'
    assert entries[-1]['verdict'] == 'FOUND_SAME'


def entry(pmid, result=None):
    results = [result or pmid]
    return {'pmid': pmid, 'route': 'R2', 'verdict': ids.verdict(results, pmid), 'result_pmids': results,
            'requests': [{'url': 'https://example.org', 'when_utc': '2026-01-01T00:00:00Z', 'response_sha256': 'a'*64}]}


def test_found_different_never_retires(tmp_path):
    put(tmp_path, 'registry/identity_searches/s.json', {'slug': 's', 'entries': [entry('123', '456')]})
    topic = put(tmp_path, 'topics/s.json', {'extra_pmids': ['123']})
    before = topic.read_bytes()
    assert ids.retire_extras(topic, ids.found_pmids('s', tmp_path)) == []
    assert topic.read_bytes() == before


def test_census_override_and_cascade_preserve_targets(tmp_path):
    topic = put(tmp_path, 'topics/s.json', {'extra_pmids': ['123', '456'], 'positive_control_pmids': ['789']})
    trials = [{'id': 'PMID '+p, 'provenance': 'abstract', 'source': 'HR 0.8 (0.7-0.9)'} for p in ['123', '456']]
    put(tmp_path, 'docs/reviews/s/review.json', {'slug': 's', 'outcomes': [{'name': 'o', 'primary': True, 'trials': trials}]})
    put(tmp_path, 'outputs/k_gap/g1/s.json', {'slug': 's', 'trials': [{'label': p, 'family': 'PMID '+p, 'g1_countable': True, 'in_our_pool': True} for p in ['123', '456']]})
    before = set(cascade.targets('s', tmp_path))
    assert census.census(str(tmp_path))['hand_named_identity'] == {'served': 2, 'tracker': 2}
    put(tmp_path, 'registry/identity_searches/s.json', {'slug': 's', 'entries': [entry('123'), entry('456', '999')]})
    assert census.census(str(tmp_path))['hand_named_identity'] == {'served': 1, 'tracker': 1}
    assert ids.retire_extras(topic, ids.found_pmids('s', tmp_path)) == ['123']
    assert ids.read(topic)['extra_pmids'] == ['456']
    (tmp_path / 'docs/reviews/s/review.json').unlink()
    assert set(cascade.targets('s', tmp_path)) == before == {'123', '456', '789'}
    assert cascade.targets('s', tmp_path)['123'] == ['recorded identity search']
    put(tmp_path, 'topics/s.json', {'extra_pmids': []})
    assert census.census(str(tmp_path))['hand_named_identity']['tracker'] == 1


def test_r1_rejects_record_without_trial_name():
    responses = registry_responses(['123'])
    responses[-1] = responses[-1].replace('TEST trial', 'Unrelated article')
    assert ids.r1(Fake(responses), ['TEST']) == []
