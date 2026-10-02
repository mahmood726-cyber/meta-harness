"""IDENTITY_UNRESOLVED as a class (the PMID <-> NCT <-> DOI chain): every new step resolves its planted case, every
guard refuses its planted violation, and no unresolved row is ever left with an EMPTY basis (61 of 66 were)."""
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / 'scripts'))
from kgap import k_gap  # noqa: E402
import k_gap_table as kt  # noqa: E402

kt._registered_before_real = kt.registered_before


# ---------------------------------------------------------------- the tokenizer: what is a marker, a year, a name
@pytest.mark.parametrize('label,acr,author,year,marker', [
    ('Ratanarat [18]', [], 'Ratanarat', '', '18'),
    ('Helps et al52', [], 'Helps', '', '52'),
    ('5 [24]', [], '', '', '24'),
    ('RALES1999', ['RALES'], 'RALES', '1999', ''),
    ('Aldo-DHF2013', ['Aldo-DHF', 'DHF'], 'Aldo-DHF', '2013', ''),
    ('GISSI-P 1999 [25]', ['GISSI-P'], 'GISSI-P', '1999', '25'),
    ('SOLOIST‐WHF (n = 1222)', ['SOLOIST-WHF'], '', '', ''),
    # a bare trailing number is part of the NAME, never a marker
    ('PIONEER 6', ['PIONEER 6'], '', '', ''),
    ('STEP 1', ['STEP 1'], '', '', ''),
    ('DECLARE-TIMI 58', ['DECLARE-TIMI 58'], '', '', ''),
    ('Baillargeon 2004', [], 'Baillargeon', '2004', ''),
])
def test_label_tokens(label, acr, author, year, marker):
    t = k_gap.identity_tokens(label)
    assert (t['acronyms'], t['author'], t['year'], t['marker']) == (acr, author, year, marker)


# ---------------------------------------------------------------- the resolver on a planted comparator
IDX = {'pmid_nct': {'90000001': [('NCT09000001', 'RESULT')]}, 'agent_nct': {}, 'acr_nct': {}, 'acr_title_nct': {},
       'nct_pmids': {}, 'study': {}}


def parsed(*refs):
    return {'refs': {r['rid']: dict({'label': '', 'ordinal': i + 1, 'title': '', 'year': '', 'first_author': '',
                                     'text': ''}, **r) for i, r in enumerate(refs)}}


def unit(label, **kw):
    t = k_gap.identity_tokens(label)
    return dict({'cited': [], 'ncts': [], 'author': t['author'], 'year': t['year'], 'acronyms': t['acronyms'],
                 'marker': t['marker'], 'label': label}, **kw)


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    monkeypatch.setattr(kt, 'REF_PMID', {})
    monkeypatch.setattr(kt, 'PUBNCT', {})
    monkeypatch.setattr(kt, 'SELF_REG', {})
    monkeypatch.setattr(kt, 'registered_before', lambda n, y, idx: True)


def test_marker_resolves_to_the_numbered_reference():
    p = parsed({'rid': 'R7', 'label': '7', 'pmid': '90000001', 'first_author': 'Plant', 'year': '2010'})
    r = kt.resolve_unit(unit('Plant [7]'), p, IDX, None)
    assert r['pmids'] == ['90000001'] and r['ncts'] == ['NCT09000001']
    assert 'label_marker_ref:7' in r['basis']


def test_marker_in_a_distrusted_table_never_resolves():
    p = parsed({'rid': 'R7', 'label': '7', 'pmid': '90000001'})
    r = kt.resolve_unit(unit('Plant [7]', distrust_links='26/28 links in Table 1 contradict their rows'), p, IDX, None)
    assert r['pmids'] == [] and r['ncts'] == []
    assert any(b.startswith('label_marker_not_used:table_links_distrusted') for b in r['basis'])


def test_marker_matching_two_references_is_ambiguous_never_picked():
    p = parsed({'rid': 'A', 'label': '7', 'pmid': '1'}, {'rid': 'B', 'label': '7', 'pmid': '2'})
    r = kt.resolve_unit(unit('Plant [7]'), p, IDX, None)
    assert r['pmids'] == [] and 'label_marker_ref_not_unique:7:2' in r['basis']


def test_reference_without_pmid_uses_only_a_CONFIRMED_title_lookup(monkeypatch):
    ref = {'rid': 'R9', 'label': '9', 'title': 'A planted trial of things', 'first_author': 'Plant', 'year': '2011'}
    p = parsed(ref)
    key = kt._ref_key(ref)
    monkeypatch.setattr(kt, 'REF_PMID', {key: {'state': 'CONFIRMED', 'pmid': '90000001'}})
    r = kt.resolve_unit(unit('Plant [9]'), p, IDX, None)
    assert r['pmids'] == ['90000001'] and 'ref_title_pubmed_confirmed:90000001' in r['basis']
    # candidates that were NOT confirmed (title/author/year) never become an identity
    monkeypatch.setattr(kt, 'REF_PMID', {key: {'state': 'CANDIDATES_NOT_CONFIRMED', 'pmid': None}})
    r = kt.resolve_unit(unit('Plant [9]'), p, IDX, None)
    assert r['pmids'] == [] and 'ref_pubmed_lookup:CANDIDATES_NOT_CONFIRMED' in r['basis']


def test_reference_absent_from_pubmed_is_typed_not_unresolved(monkeypatch):
    ref = {'rid': 'R9', 'label': '9', 'title': 'A trial in a journal PubMed does not index', 'first_author': 'Plant'}
    monkeypatch.setattr(kt, 'REF_PMID', {kt._ref_key(ref): {'state': 'NOT_IN_PUBMED_BY_TITLE_WORDS_AND_FIRST_AUTHOR'}})
    r = kt.resolve_unit(unit('Plant [9]'), parsed(ref), IDX, None)
    assert r['pmids'] == [] and any(b.startswith('ref_not_in_pubmed:') for b in r['basis'])
    assert kt.classify('IDENTIFIED_NOT_INDEXED', None, None, None, None) == 'IDENTIFIED_NOT_INDEXED'


def test_a_doi_with_no_held_mapping_stays_unresolved_and_says_so():
    ref = {'rid': 'R4', 'label': '4', 'doi': '10.9999/plant.1', 'title': 'x', 'first_author': 'Plant'}
    r = kt.resolve_unit(unit('Plant [4]'), parsed(ref), IDX, None)
    assert r['pmids'] == [] and 'ref_has_no_pmid:doi_unmapped:not_looked_up' in r['basis']


def test_acronym_named_in_exactly_one_reference_with_the_labels_year():
    p = parsed({'rid': 'B16', 'pmid': '90000001', 'year': '2013', 'text': 'Edelmann F. ... the Aldo-DHF randomized trial. 2013'},
               {'rid': 'B17', 'pmid': '90000002', 'year': '2015', 'text': 'A post hoc analysis of Aldo-DHF. 2015'})
    r = kt.resolve_unit(unit('Aldo-DHF2013'), p, IDX, None)
    assert r['pmids'] == ['90000001'] and 'acronym_named_in_comparator_ref:Aldo-DHF:B16' in r['basis']
    # without the year, two references name it: ambiguous, recorded, never picked
    r = kt.resolve_unit(unit('Aldo-DHF'), p, IDX, None)
    assert r['pmids'] == [] and 'acronym_in_comparator_refs_ambiguous:Aldo-DHF:2' in r['basis']


def test_an_unresolved_row_never_has_an_empty_basis():
    for label, p in [('Baillargeon 2004', None), ('No statin used group in QRISK <10% (n = 3', parsed()),
                     ('COPE study', None)]:
        r = kt.resolve_unit(unit(label), p, IDX, None)
        assert r['pmids'] == [] and r['ncts'] == []
        assert r['basis'] and any(b.startswith('unresolved_at:') for b in r['basis'])
    r = kt.resolve_unit(unit('Baillargeon 2004'), None, IDX, None)
    assert 'unresolved_at:no_comparator_reference_list,no_citation_link_or_marker,no_acronym_in_label' in r['basis']


# ---------------------------------------------------------------- the committed table: the class, measured
def test_committed_table_has_no_empty_basis_on_an_unresolved_row():
    T = json.load(open(ROOT / 'outputs/k_gap/k_gap_table.json', encoding='utf-8'))
    bad = [(t['slug'], t['label']) for t in T['trials']
           if t['status'] in ('UNRESOLVED', 'IDENTIFIED_NOT_INDEXED') and not t.get('identity_basis')]
    assert bad == []


def test_ref_title_lookup_cache_records_retrieval_and_never_a_bare_zero():
    c = json.load(open(ROOT / 'outputs/k_gap/ref_title_pmid.json', encoding='utf-8'))
    assert c
    for k, v in c.items():
        assert v['retrieved_utc'] and v['query'] and v['state']
        if v['state'].startswith('NOT_IN_PUBMED'):
            # a zero is only a finding when PubMed executed the query as written
            assert not any((v.get('warnings') or {}).get(w) for w in ('quotedphrasesnotfound', 'phrasesignored'))
            assert not any((v.get('errors') or {}).get(e) for e in ('phrasesnotfound', 'fieldsnotfound'))


def test_unit_enumeration_tokens_are_unchanged():
    """_label_tokens decides which rows/columns ARE trial units; the identity reading must never change that (an
    earlier draft did, and turned empagliflozin's comparator Table 1 into its trial set)."""
    t = k_gap._label_tokens('RALES1999')
    assert t == {'acronyms': ['RALES1999'], 'author': 'RALES', 'year': '1999', 'ncts': []}
    assert 'marker' not in k_gap._label_tokens('Ratanarat [18]')


def test_acronym_never_names_a_registration_made_after_the_labels_year(monkeypatch):
    idx = dict(IDX, acr_nct={k_gap.norm_acronym('ASCEND'): ['NCT04382612']}, agent_nct={'NCT04382612': True},
               study={'NCT04382612': {'study_first_submitted_date': '2020-05-06'}})
    monkeypatch.setattr(kt, 'registered_before', kt.__dict__['_registered_before_real'])
    r = kt.resolve_unit(unit('ASCEND 2018'), None, idx, None)
    assert r['ncts'] == []                       # the 2020 HARPOON device study is not the 2018 ASCEND trial
    r = kt.resolve_unit(unit('ASCEND 2021'), None, idx, None)
    assert r['ncts'] == ['NCT04382612'] and 'acronym_aact:ASCEND' in r['basis']


def test_study_id_citation_list_parsed_from_held_review_text():
    text = ('References to studies included in this review Baillargeon 2004 {published data only} Baillargeon JP, '
            'Jakubowicz DJ, Nestler JE. Effects of metformin and rosiglitazone in nonobese women with polycystic ovary '
            'syndrome. Fertility and Sterility 2004;82:893-902. [ DOI ] [ PubMed ] Ben Ayed 2009 {published data only} '
            'Ben Ayed B, Dammak Y, Fourati S. Metformin effects on clomifene-induced ovulation in the polycystic ovary '
            'syndrome. Tunisie Medicale 2009;87:43-9. [ PubMed ] Dup 2001 {published data only} Dup A. T one. J 2001;1. '
            'Dup 2001 {unpublished data only} Dup B. T two. J 2001;2. References to studies excluded from this review X')
    r = kt.study_id_citations(text)
    assert set(r) == {'Baillargeon 2004', 'Ben Ayed 2009'}          # a study ID listed twice is not an identity
    assert r['Ben Ayed 2009']['first_author'] == 'Ben Ayed' and r['Ben Ayed 2009']['year'] == '2009'
    assert r['Baillargeon 2004']['title'].startswith('Effects of metformin and rosiglitazone')
    assert all(v['pmid'] is None for v in r.values())                # never an invented PMID


def test_study_id_ref_then_confirmed_title_gives_the_pmid(monkeypatch):
    ref = {'rid': 'SID:Tang 2006', 'label': 'Tang 2006', 'first_author': 'Tang', 'year': '2006',
           'title': 'Combined lifestyle modification and metformin in obese patients with polycystic ovary syndrome'}
    monkeypatch.setattr(kt, 'REF_PMID', {kt._ref_key(ref): {'state': 'CONFIRMED', 'pmid': '90000001'}})
    r = kt.resolve_unit(unit('Tang 2006'), parsed(ref), IDX, None)
    assert r['pmids'] == ['90000001'] and 'study_id_ref:SID:Tang 2006' in r['basis']
    # two references by the same first author in the same year, and no study-ID label: ambiguous, never picked
    a = dict(ref, rid='A', label=''); b = dict(ref, rid='B', label='', title='Another trial')
    r = kt.resolve_unit(unit('Tang 2006'), parsed(a, b), IDX, None)
    assert r['pmids'] == [] and 'author_year_ref_ambiguous:2' in r['basis']


def test_title_confirmation_rules():
    sys.path.insert(0, str(ROOT / 'scripts'))
    import ref_title_pmid_lookup as L
    t = 'Combined lifestyle modification and metformin in obese patients with polycystic ovary syndrome'
    assert L.same_title(t + '. A randomized, placebo-controlled, double-blind multicentre study.', t)   # subtitle
    assert not L.same_title(t + ' and diabetes', t)            # a longer title is a different paper
    assert not L.same_title('Metformin in PCOS. A trial.', 'Metformin in PCOS')   # short titles: exact only
    assert L.fold('Boudhrâa') == L.fold('Boudhraa')            # diacritics folded for surnames only


def test_report_family_consolidation():
    fams = [{'family_id': 'NCT00795808', 'reports': {'20435692', 'NCT00795808'}, 'acronyms': set()},
            {'family_id': 'PMID 1', 'reports': {'111'}, 'acronyms': set()}]
    # the review cites a SECONDARY report of a trial we hold: the identity becomes the trial (NCT + every report)
    r = kt.consolidate_report_family({'pmids': ['21631446'], 'ncts': ['NCT00795808'], 'basis': []}, fams)
    assert r['pmids'] == ['20435692', '21631446'] and r['ncts'] == ['NCT00795808']
    assert any(b.startswith('report_family_consolidated:NCT00795808') for b in r['basis'])
    # an identity no family claims is untouched; two families claiming it are recorded, never merged
    assert kt.consolidate_report_family({'pmids': ['999'], 'ncts': [], 'basis': []}, fams)['pmids'] == ['999']
    # a PMID-only identity reported by TWO families is ambiguous: recorded, never merged
    two = fams + [{'family_id': 'NCT00000009', 'reports': {'21631446'}, 'acronyms': set()},
                  {'family_id': 'NCT00000010', 'reports': {'21631446'}, 'acronyms': set()}]
    r = kt.consolidate_report_family({'pmids': ['21631446'], 'ncts': [], 'basis': []}, two)
    assert r['pmids'] == ['21631446'] and r['ncts'] == [] and any(b.startswith('report_family_ambiguous') for b in r['basis'])


def test_a_reference_seed_title_is_never_read_as_a_trial_label():
    """'Effect of Dexamethasone ... COVID-19: The CoDEX Randomized ...' carries its own PMID; reading 'COVID-19' out of
    the title as an acronym tripped the label/citation conflict and dropped a correct identity."""
    u = {'layout': 'reference', 'label': 'Effect of Dexamethasone in Patients With COVID-19: The CoDEX Randomized Trial.',
         'cited': [{'pmid': '90000001', 'doi': None, 'basis': None}], 'ncts': [], 'author': '', 'year': '',
         'acronyms': []}
    r = kt.resolve_unit(u, None, IDX, None)
    assert r['pmids'] == ['90000001'] and not any('COVID' in b for b in r['basis'])


def test_consolidation_never_merges_two_registered_trials_through_a_shared_paper():
    """PACMAN-AMI (NCT03067844) carries the PMIDs associated with its NCT; one is also a report in ODYSSEY LONG TERM's
    family (NCT01507831). An identity with an NCT consolidates only into THAT NCT's family."""
    fams = [{'family_id': 'NCT01507831', 'reports': {'26330422', 'NCT01507831'}, 'acronyms': set()}]
    r = kt.consolidate_report_family({'pmids': ['26330422', '35368058'], 'ncts': ['NCT03067844'], 'basis': []}, fams)
    assert r['ncts'] == ['NCT03067844'] and not any(b.startswith('report_family_consolidated') for b in r['basis'])
    # a PMID-only identity still consolidates by its report
    r = kt.consolidate_report_family({'pmids': ['26330422'], 'ncts': [], 'basis': []}, fams)
    assert r['ncts'] == ['NCT01507831']


def test_other_agent_trial_resolves_only_by_a_globally_unique_acronym(monkeypatch):
    monkeypatch.setattr(kt, 'registered_before', kt._registered_before_real)
    idx = dict(IDX, agent_nct={},          # finerenone trials are NOT topic-agent registrations in a spironolactone topic
               acr_nct={k_gap.norm_acronym('FIGARO-DKD'): ['NCT02545049'],
                        k_gap.norm_acronym('SCORED'): ['NCT03222193', 'NCT03315143', 'NCT07509203'],
                        k_gap.norm_acronym('CORP'): ['NCT00128414']},
               study={'NCT02545049': {'study_first_submitted_date': '2015-09-14'}},
               interventions={'NCT02545049': ['Finerenone (BAY94-8862)', 'Placebo']})
    monkeypatch.setattr(kt, 'SERVED_AGENTS', ['finerenone', 'spironolactone'])
    r = kt.resolve_unit(unit('FIGARO-DKD2022', layout='row'), None, idx, None)
    assert r['ncts'] == ['NCT02545049'] and 'acronym_aact_any_agent_acronym:FIGARO-DKD' in r['basis']
    # unique but UNCORROBORATED (its interventions name no served topic's drug): a candidate, never an identity
    monkeypatch.setattr(kt, 'SERVED_AGENTS', ['spironolactone'])
    r = kt.resolve_unit(unit('FIGARO-DKD2022', layout='row'), None, idx, None)
    assert r['ncts'] == [] and 'uncorroborated_any_agent_acronym_acronym:FIGARO-DKD:NCT02545049' in r['basis']
    monkeypatch.setattr(kt, 'SERVED_AGENTS', ['finerenone', 'spironolactone'])
    r = kt.resolve_unit(unit('SCORED', layout='text'), None, idx, None)
    assert r['ncts'] == [] and 'acronym_aact_any_agent_ambiguous_acronym:SCORED:3' in r['basis']
    r = kt.resolve_unit(unit('CORP study', layout='text'), None, idx, None)
    assert r['ncts'] == []                        # 4 characters: too short to be a global identity
    r = kt.resolve_unit(unit('FIGARO-DKD2014', layout='row'), None, idx, None)
    assert r['ncts'] == []                        # registered 2015: cannot be a 2014 trial


NAMES = ['Abel', 'Baker', 'Carter', 'Dalton', 'Ellis', 'Foster', 'Garner', 'Hughes', 'Irwin', 'Jordan']


def _shifted_table(n=6, off=1):
    refs = [{'rid': f'R{i}', 'label': str(i), 'pmid': str(90000000 + i), 'first_author': NAMES[i - 1], 'year': '2010'}
            for i in range(1, n + 3)]
    units = [dict(unit(f'{NAMES[i + off - 1]} 2010 [{i}]', layout='row', table='T1'),
                  distrust_links='shifted') for i in range(1, n + 1)]
    return units, parsed(*refs)


def test_a_systematic_shift_is_learned_and_applied_row_by_row():
    units, p = _shifted_table()
    out = kt.learn_marker_offsets(units, p)
    assert out['T1']['offset'] == 1 and all(u['marker_offset'] == 1 for u in units)
    r = kt.resolve_unit(units[0], p, IDX, None)
    assert r['pmids'] == ['90000002'] and any(b.startswith('label_marker_ref_shifted:+1:1->2') for b in r['basis'])
    # a row whose shifted reference disagrees with its own label is NOT admitted
    bad = dict(units[1], label='Someoneelse 2010 [2]', author='Someoneelse')
    r = kt.resolve_unit(bad, p, IDX, None)
    assert r['pmids'] == [] and 'label_marker_shifted_ref_disagrees_with_row:2->3' in r['basis']


def test_no_offset_is_learned_from_a_table_that_does_not_prove_one():
    units, p = _shifted_table(n=6, off=1)
    for u in units[:3]:                          # half the rows agree at 0, half at +1: no systematic shift
        pass
    mixed = [dict(unit(f'{NAMES[i - 1]} 2010 [{i}]', layout='row', table='T1'), distrust_links='s') for i in range(1, 4)] + units[3:]
    out = kt.learn_marker_offsets(mixed, p)
    assert out['T1']['offset'] is None and not any('marker_offset' in u for u in mixed)
