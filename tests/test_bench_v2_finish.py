import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import bench_v2_finish as finish

XML = b'<article><article-meta><abstract>Pairwise randomized trials. Three trials.</abstract></article-meta><body/></article>'


def reader(design='yes', k=3, verified=True):
    return {'answer': {'pairwise_rct_meta': design, 'k_rcts': k,
                       'design_quote': 'Pairwise randomized trials.', 'k_quote': 'Three trials.'},
            'span_check': {'status': 'VERIFIED' if verified else 'UNVERIFIED'}}


class DecisionTests(unittest.TestCase):
    def test_adjudication_overrides_disagreement_and_unverified(self):
        decision = finish.combine_decisions(reader('no'), reader(verified=False),
                                           {'c2_c3_pass': True, 'k_rcts': 5})
        self.assertEqual((decision['status'], decision['k_rcts'], decision['c2c3_source']),
                         ('PASS', 5, 'adjudicated'))

    def test_adjudicated_rejection_overrides_agreed_pass(self):
        decision = finish.combine_decisions(reader(), reader(),
                                           {'c2_c3_pass': False, 'k_rcts': 3})
        self.assertEqual(decision['status'], 'EXCLUDED')
        self.assertEqual(decision['first_failure'], 'C2/C3')

    def test_agreed_pass_boundaries(self):
        for k in (3, 25):
            with self.subTest(k=k):
                decision = finish.combine_decisions(reader(k=k), reader(k=k))
                self.assertEqual(decision['status'], 'PASS')
                self.assertEqual(decision['c2c3_source'], 'agreed')

    def test_both_fail(self):
        for a, b, criterion in ((reader('no'), reader('no', 8), 'C2'),
                                (reader(k=2), reader(k=30), 'C3'),
                                (reader('no'), reader(k=30), 'C2/C3')):
            with self.subTest(criterion=criterion):
                decision = finish.combine_decisions(a, b)
                self.assertEqual(decision['status'], 'EXCLUDED')
                self.assertEqual(decision['first_failure'], criterion)

    def test_disagreement_or_unverified_is_pending(self):
        for a, b in ((reader(), reader(k=4)), (reader(), reader('no')),
                     (reader(), reader(verified=False)), (None, reader())):
            with self.subTest(a=a, b=b):
                self.assertEqual(finish.combine_decisions(a, b)['status'], 'PENDING_ADJUDICATION')

    def test_invalid_adjudication_never_falls_back(self):
        for adj in ({'c2_c3_pass': 'yes', 'k_rcts': 3},
                    {'c2_c3_pass': True, 'k_rcts': True},
                    {'c2_c3_pass': True, 'k_rcts': 26}):
            self.assertEqual(finish.combine_decisions(reader(), reader(), adj)['status'],
                             'PENDING_ADJUDICATION')


class FixtureScreenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.reads = self.root / 'reads'
        self.reads.mkdir()
        (self.root / 'input.txt').write_text('Pairwise randomized trials. Three trials.', encoding='utf-8')
        self.hit = dict(id='1', pmid='1', pmcid='PMC1', title='Fixture', license='CC BY')
        self.entry = dict(i=0, pmcid='PMC1', file='input.txt')
        for obj, attr, value in ((finish, 'ROOT', self.root), (finish.v2, 'READS', self.reads),
                                 (finish, 'cached_xml', lambda _: (self.root / 'fixture.xml', XML))):
            p = patch.object(obj, attr, value)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(finish.v2, 'call_reader', side_effect=AssertionError('No model calls in tests'))
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(finish.old, 'urlopen', side_effect=AssertionError('No network in tests'))
        p.start()
        self.addCleanup(p.stop)

    def write_read(self, who, k=3, nested=False):
        data = dict(reader(k=k)['answer'], pmcid='PMC1')
        if nested:
            data = dict(answer=reader(k=k)['answer'], pmcid='PMC1', span_check={'status': 'VERIFIED'})
        finish.old.write_json(self.reads / f'PMC1.reader{who}.json', data)

    def screen(self, previous=None):
        return finish.screen(self.hit, self.entry, object(), [], {}, previous or {}, lambda _: None)

    def test_flat_b_from_input_and_nested_a_from_xml(self):
        self.write_read('A', nested=True)
        self.write_read('B')
        a = finish.stored_read('PMC1', 'A', XML)
        b = finish.stored_read('PMC1', 'B', XML, self.root / 'input.txt')
        self.assertEqual(finish.combine_decisions(a, b)['status'], 'PASS')
        self.assertEqual(finish.stored_read('PMC1', 'B', b'<article/>')['span_check']['status'], 'UNVERIFIED')

    def test_disagreement_stops_before_inventory(self):
        self.write_read('A', nested=True)
        self.write_read('B', k=4)
        with patch.object(finish.v2, 'load_inventory', side_effect=AssertionError('C4 must not run')):
            self.assertEqual(self.screen()['status'], 'PENDING_ADJUDICATION')

    def test_missing_input_stops_before_inventory(self):
        self.entry = {'i': 0, 'pmcid': 'PMC1', 'error': 'Fixture extraction error'}
        with patch.object(finish.v2, 'load_inventory', side_effect=AssertionError('C4 must not run')):
            self.assertEqual(self.screen()['status'], 'NEEDS_INSPECTION')

    def test_adjudicated_pass_c4_resume_and_c5_exclusion(self):
        finish.old.write_json(self.reads / 'PMC1.adjudication.json', {'c2_c3_pass': True, 'k_rcts': 3})
        trials = [{'trial_id': str(i)} for i in range(3)]
        resolutions = [dict(trial_id=str(i), route='meta_text', resolved=True,
                            registry_ids=[f'NCT{i:08d}'], evidence={'quote': 'fixture'}, attempts=[])
                       for i in range(3)]
        prior = {'trial_inventory': trials, 'c4_trial_resolutions': resolutions[:1]}
        with patch.object(finish.v2, 'load_inventory', return_value=trials), \
             patch.object(finish.v2, 'resolve_trial', side_effect=resolutions[1:]) as resolve, \
             patch.object(finish.old, 'fetch_registry', return_value={'start': '2009-01', 'registered': '2008-01'}):
            result = self.screen(prior)
        self.assertEqual(resolve.call_count, 2)
        self.assertEqual(result['first_failure'], 'C5')
        self.assertEqual(result['c4_trial_resolutions'], resolutions)
        self.assertEqual(result['c2c3_source'], 'adjudicated')

    def test_incomplete_c4_retains_all_trial_attempts(self):
        finish.old.write_json(self.reads / 'PMC1.adjudication.json', {'c2_c3_pass': True, 'k_rcts': 3})
        trials = [{'trial_id': str(i)} for i in range(3)]
        good = dict(trial_id='1', route='meta_text', resolved=True,
                    registry_ids=['NCT00000001'], evidence={'quote': 'fixture'}, attempts=[])
        with patch.object(finish.v2, 'load_inventory', return_value=trials), \
             patch.object(finish.v2, 'resolve_trial', side_effect=[finish.v2.NeedsWork('fixture missing facts'), good,
                                                                 finish.old.FetchError('fixture timeout')]) as resolve:
            result = self.screen()
        self.assertEqual(resolve.call_count, 3)
        self.assertEqual(result['status'], 'SCREEN_ERROR')
        self.assertEqual(len(result['c4_trial_resolutions']), 3)
        self.assertFalse(result['c4_trial_resolutions'][0]['lookup_complete'])

    def test_c9_area_cap_is_applied_after_c5_through_c8(self):
        finish.old.write_json(self.reads / 'PMC1.adjudication.json', {'c2_c3_pass': True, 'k_rcts': 3})
        trials = [{'trial_id': str(i)} for i in range(3)]
        resolutions = [dict(trial_id=str(i), route='meta_text', resolved=True,
                            registry_ids=[f'NCT{i:08d}'], evidence={'quote': 'fixture'}, attempts=[])
                       for i in range(3)]
        with patch.object(finish.v2, 'load_inventory', return_value=trials), \
             patch.object(finish.v2, 'resolve_trial', side_effect=resolutions * 2), \
             patch.object(finish.old, 'fetch_registry', return_value={'start': '2010-01', 'registered': '2010-01'}), \
             patch.object(finish.old, 'per_trial_rows', return_value={'rows': ['fixture']}), \
             patch.object(finish.old, 'overlap', return_value=None), \
             patch.object(finish.old, 'therapeutic_area', return_value=('other', {'source': 'fixture'})):
            result = finish.screen(self.hit, self.entry, object(), [], {'other': 3}, {}, lambda _: None)
            self.assertEqual(result['first_failure'], 'C9')
            self.assertEqual(self.screen()['status'], 'QUALIFIES')

    def test_summary_does_not_count_pending_as_exclusion(self):
        report = {'screened': [dict(status='PENDING_ADJUDICATION', first_failure=None, pmcid='PMC1'),
                               dict(status='EXCLUDED', first_failure='C3', pmcid='PMC2')]}
        finish.summarise(report)
        self.assertEqual(report['n_screened'], 2)
        self.assertEqual(report['first_failure_counts'], {'C3': 1})


class RunFixtureTests(unittest.TestCase):
    def test_order_stop_resume_and_changed_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hits = [dict(id=str(i), pmcid=f'PMC{i}', title='Fixture') for i in range(1, 23)]
            index = root / 'INDEX.json'
            prereg = root / 'prereg.md'
            prereg.write_text('Fixture preregistration', encoding='utf-8')
            finish.old.write_json(index, [dict(i=i, pmcid=h['pmcid'], file='fixture.txt') for i, h in enumerate(hits)])
            phase = [0]
            calls = []
            def key(hit, entry, sources, areas):
                return json.dumps([hit, dict(areas), phase[0] if hit['id'] == '1' else 0], sort_keys=True)
            def screen(hit, entry, client, topics, areas, previous, save):
                calls.append(hit['pmcid'])
                excluded = phase[0] and hit['id'] == '1'
                return dict(hit, status='EXCLUDED' if excluded else 'QUALIFIES',
                            verdict='EXCLUDED' if excluded else 'QUALIFIES', area='fixture',
                            first_failure='C3' if excluded else None, c4_trial_resolutions=[])
            with patch.object(finish, 'INDEX', index), \
                 patch.object(finish, 'FINISH', root / 'finish'), \
                 patch.object(finish.v2, 'OUT', root), \
                 patch.object(finish.v2, 'PREREG', prereg), \
                 patch.object(finish.v2, 'inputs', return_value=(hits, [], [], len(hits))), \
                 patch.object(finish, 'fingerprint', side_effect=key), \
                 patch.object(finish, 'screen', side_effect=screen), \
                 patch.object(finish.time, 'sleep'), patch('builtins.print'):
                first = finish.run()
                self.assertEqual(calls, [h['pmcid'] for h in hits[:20]])
                self.assertEqual(first['n_qualifies'], 20)
                calls.clear()
                finish.run()
                self.assertEqual(calls, [])
                phase[0] = 1
                final = finish.run()
                self.assertEqual(calls, [h['pmcid'] for h in hits[:21]])
                self.assertEqual(final['n_screened'], 21)
                self.assertEqual(final['n_qualifies'], 20)
                self.assertEqual(final['first_failure_counts'], {'C3': 1})
                self.assertTrue((root / 'candidates_v2.json').is_file())
                self.assertTrue((root / 'v2_finish_summary.json').is_file())


if __name__ == '__main__':
    unittest.main()
