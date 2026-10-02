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
        if v['state'] == 'NOT_IN_PUBMED_FIRST_AUTHOR_NOT_INDEXED':
            # the ONLY term PubMed could not find is the first author's whole surname: no such author is indexed
            assert [w.lower() for w in v['errors']['phrasesnotfound']] == [v['ref']['first_author'].lower()]
        elif v['state'].startswith('NOT_IN_PUBMED'):
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


# ---------------------------------------------------------------- long forms (RALES, EPHESUS)
def test_long_form_matcher_names_trials_only():
    assert kt.acronym_long_form('RALES', 'heart failure. Randomized aldactone evaluation study investigators. N Engl J Med')
    assert kt.acronym_long_form('EPHESUS', 'Eplerenone Post-Acute Myocardial Infarction Heart Failure Efficacy and '
                                           'Survival Study Investigators')
    # a loose phrase inside a sentence is not a trial's name (no study/trial/investigators anchor)
    assert not kt.acronym_long_form('COPE', 'Colchicine in addition to conventional therapy for acute pericarditis: results')
    assert not kt.acronym_long_form('RALES', 'Eplerenone, a selective aldosterone blocker, in patients with left '
                                             'ventricular dysfunction after myocardial infarction.')
    assert not kt.acronym_long_form('ASCEND', 'A Study of Cardiovascular Events in Diabetes')


def test_long_form_step_text_and_collective_author(monkeypatch):
    rales = {'rid': 'B1', 'pmid': '10471456', 'year': '1999', 'text': 'Pitt B. The effect of spironolactone. Randomized '
             'aldactone evaluation study investigators. N Engl J Med. (1999)'}
    ephesus = {'rid': 'B14', 'pmid': '12668699', 'year': '2003', 'text': 'Pitt B. Eplerenone, a selective aldosterone '
               'blocker, in patients with left ventricular dysfunction after myocardial infarction. (2003)'}
    other = {'rid': 'B17', 'pmid': '24716680', 'year': '2014', 'text': 'Pitt B. Spironolactone for HFpEF. (2014)'}
    p = parsed(rales, ephesus, other)
    monkeypatch.setattr(kt, 'COLLECTIVE', {'12668699': {'collective': [
        'Eplerenone Post-Acute Myocardial Infarction Heart Failure Efficacy and Survival Study Investigators']}})
    r = kt.resolve_unit(unit('RALES1999', layout='row'), p, IDX, None)
    assert r['pmids'] == ['10471456'] and any(b.startswith('acronym_long_form_in_comparator_ref:RALES:B1') for b in r['basis'])
    r = kt.resolve_unit(unit('EPHESUS2003', layout='row'), p, IDX, None)
    assert r['pmids'] == ['12668699']             # the long form is ONLY in the collective author
    # the wrong year never matches; without the collective name EPHESUS stays unresolved and says so
    assert kt.resolve_unit(unit('RALES2005', layout='row'), p, IDX, None)['pmids'] == []
    monkeypatch.setattr(kt, 'COLLECTIVE', {})
    r = kt.resolve_unit(unit('EPHESUS2003', layout='row'), p, IDX, None)
    assert r['pmids'] == [] and any(b.startswith('unresolved_at') for b in r['basis'])


def test_long_form_in_two_references_is_ambiguous():
    a = {'rid': 'A', 'pmid': '1', 'year': '', 'text': 'Randomized aldactone evaluation study investigators.'}
    b = {'rid': 'B', 'pmid': '2', 'year': '', 'text': 'Randomized aldactone evaluation study group. Follow-up.'}
    r = kt.resolve_unit(unit('RALES', layout='text'), parsed(a, b), IDX, None)
    assert r['pmids'] == [] and 'acronym_long_form_ambiguous:RALES:2' in r['basis']


def test_author_only_et_al_needs_exactly_one_first_author(monkeypatch):
    assert k_gap.identity_tokens('Finkelstein Y et al')['author'] == 'Finkelstein'
    assert k_gap.identity_tokens('Finkelstein')['author'] == ''         # a bare name is not an author reading
    ref = {'rid': 'REF:10', 'label': '10', 'first_author': 'Finke lstein', 'year': '2002',
           'title': 'Colchicine for the prevention of postpericardiotomy syndrome'}
    other = {'rid': 'REF:6', 'label': '6', 'first_author': 'Adler', 'year': '1998', 'title': 'x'}
    monkeypatch.setattr(kt, 'REF_PMID', {kt._ref_key(ref): {'state': 'CONFIRMED', 'pmid': '12574898'}})
    # no trial words in the citation and no publication type known: a unique first author is not yet a trial
    r = kt.resolve_unit(unit('Finkelstein Y et al', layout='text'), parsed(ref, other), IDX, None)
    assert r['pmids'] == [] and 'author_only_ref_refused_no_trial_context:REF:10' in r['basis']
    # PubMed types its confirmed PMID as a Randomized Controlled Trial: admitted
    monkeypatch.setattr(kt, 'COLLECTIVE', {'12574898': {'collective': [], 'pubtypes': ['Randomized Controlled Trial']}})
    r = kt.resolve_unit(unit('Finkelstein Y et al', layout='text'), parsed(ref, other), IDX, None)
    assert r['pmids'] == ['12574898'] and 'author_only_ref:REF:10' in r['basis']
    two = dict(ref, rid='REF:11', label='11')
    r = kt.resolve_unit(unit('Finkelstein Y et al', layout='text'), parsed(ref, two), IDX, None)
    assert r['pmids'] == [] and 'author_only_ref_ambiguous:2' in r['basis']


def test_two_references_that_are_reports_of_one_registered_trial_are_one_trial(monkeypatch):
    monkeypatch.setattr(kt, 'COLLECTIVE', {'32966714': {'collective': ['VERTIS CV Investigators']}})
    primary = {'rid': 'bib20', 'pmid': '32966714', 'year': '2020', 'text': 'Cannon CP. Cardiovascular outcomes with ertugliflozin.'}
    secondary = {'rid': 'bib8', 'pmid': '33026243', 'year': '2020', 'text': 'Cosentino F. Heart failure events: the VERTIS CV trial.'}
    idx = dict(IDX, pmid_nct={'32966714': [('NCT01986881', 'RESULT')], '33026243': [('NCT01986881', 'DERIVED')]})
    r = kt.resolve_unit(unit('VERTIS-CV', layout='text'), parsed(primary, secondary), idx, None)
    assert r['ncts'] == ['NCT01986881'] and r['pmids'] == ['32966714', '33026243']
    assert any(b.startswith('acronym_in_comparator_refs_one_trial:VERTIS-CV:NCT01986881') for b in r['basis'])
    # two references registered to DIFFERENT trials stay ambiguous
    idx2 = dict(IDX, pmid_nct={'32966714': [('NCT01986881', 'RESULT')], '33026243': [('NCT09999999', 'RESULT')]})
    r = kt.resolve_unit(unit('VERTIS-CV', layout='text'), parsed(primary, secondary), idx2, None)
    assert r['ncts'] == [] and 'acronym_in_comparator_refs_ambiguous:VERTIS-CV:2' in r['basis']


def test_a_two_word_trial_name_never_resolves_to_its_sibling(monkeypatch):
    """'EMPEROR Preserved, 2020' resolved to EMPEROR-Reduced (NCT03057977) when only 'EMPEROR' was read. The name is
    read whole, its bare head is dropped, and the sibling's reference can never match it."""
    assert k_gap.identity_tokens('EMPEROR Preserved, 2020')['acronyms'] == ['EMPEROR Preserved']
    assert k_gap.identity_tokens('DELIVER Trial, 2022')['acronyms'] == ['DELIVER']          # generic word: not a name
    reduced = {'rid': 'R15', 'pmid': '32865377', 'year': '2020', 'text': 'Packer M. EMPEROR-Reduced Trial Investigators.'}
    r = kt.resolve_unit(unit('EMPEROR Preserved, 2020', layout='row'), parsed(reduced), IDX, None)
    assert r['pmids'] == [] and r['ncts'] == []
    preserved = {'rid': 'R11', 'pmid': '34449189', 'year': '2020', 'text': 'Anker SD. Empagliflozin in HFpEF.'}
    monkeypatch.setattr(kt, 'COLLECTIVE', {'34449189': {'collective': ['EMPEROR-Preserved Trial Investigators']}})
    r = kt.resolve_unit(unit('EMPEROR Preserved, 2020', layout='row'), parsed(reduced, preserved), IDX, None)
    assert r['pmids'] == ['34449189']


def test_a_named_trials_standalone_year_is_read_and_proves_a_shifted_reference(monkeypatch):
    t = k_gap.identity_tokens('Risk & Prevention 2013 [42]')
    assert (t['year'], t['marker']) == ('2013', '42')
    assert k_gap.identity_tokens('Trial A (2019) (19)')['year'] == '2019'
    assert k_gap.identity_tokens('(2015 and 2016 cohorts)')['year'] == ''         # two different years: no year
    monkeypatch.setattr(kt, 'registered_before', kt._registered_before_real)
    refs = [{'rid': f'R{i}', 'label': str(i), 'pmid': str(23000000 + i), 'year': y, 'first_author': a, 'text': f'{a} 2013'}
            for i, (y, a) in enumerate([('2012', 'Bosch'), ('2013', 'Macchia'), ('2013', 'Roncaglioni')], start=41)]
    u = dict(unit('Risk & Prevention 2013 [42]', layout='row'), distrust_links='shifted', marker_offset=1,
             marker_offset_evidence='27/28 rows agree at +1')
    # the real reference 43's collective author names the trial; without it the label's first word is guessed to be
    # a surname ('Risk' vs 'Roncaglioni') and the row is refused
    r = kt.resolve_unit(u, parsed(*refs), IDX, None)
    assert r['pmids'] == [] and 'label_marker_shifted_ref_disagrees_with_row:42->43' in r['basis']
    monkeypatch.setattr(kt, 'COLLECTIVE', {'23000043': {'collective': ['Risk and Prevention Study Collaborative Group']}})
    r = kt.resolve_unit(u, parsed(*refs), IDX, None)
    assert r['pmids'] == ['23000043'] and any(b.startswith('label_marker_ref_shifted:+1:42->43') for b in r['basis'])


def test_name_words_match_is_positive_name_evidence(monkeypatch):
    monkeypatch.setattr(kt, 'COLLECTIVE', {'23656645': {'collective': ['Risk and Prevention Study Collaborative Group']}})
    ref = {'pmid': '23656645', 'text': 'Roncaglioni MC. n-3 fatty acids in patients with multiple cardiovascular risk factors.'}
    assert kt.name_words_match('Risk & Prevention 2013 [42]', ref)
    assert not kt.name_words_match('Risk & Outcomes 2013 [42]', ref)       # every name word must be there
    assert not kt.name_words_match('Prevention 2013 [42]', ref)             # one word is not a name


def test_congress_abstract_title_and_unindexed_first_author(monkeypatch):
    text = ('18.RatanaratRSanguanwitPChitsomkasemAThe effects of normal saline versus balanced crystalloid solution as a '
            'resuscitation fluid on acute kidney injury in shock patients: a randomized opened label-controlled trial. '
            '30th Annu Congr Eur Soc intensive care Med ESICM 20172017')
    assert kt.ref_title({'title': '', 'text': text}).startswith('The effects of normal saline versus balanced')
    assert kt.ref_title({'title': '', 'text': 'The A trial. The B study.'}) == ''      # two candidate titles: none
    ref = {'rid': 'CR18', 'label': '18', 'first_author': 'Ratanarat', 'year': '2017', 'title': '', 'text': text}
    monkeypatch.setattr(kt, 'REF_PMID', {kt._ref_key(ref): {'state': 'NOT_IN_PUBMED_BY_TITLE_WORDS_AND_FIRST_AUTHOR'}})
    r = kt.resolve_unit(unit('Ratanarat [18]', layout='row'), parsed(ref), IDX, None)
    assert r['pmids'] == [] and 'ref_not_in_pubmed:NOT_IN_PUBMED_BY_TITLE_WORDS_AND_FIRST_AUTHOR' in r['basis']
    # a first author PubMed's author index does not hold is a NOT_IN_PUBMED finding too
    monkeypatch.setattr(kt, 'REF_PMID', {kt._ref_key(ref): {'state': 'NOT_IN_PUBMED_FIRST_AUTHOR_NOT_INDEXED'}})
    r = kt.resolve_unit(unit('Ratanarat [18]', layout='row'), parsed(ref), IDX, None)
    assert 'ref_not_in_pubmed:NOT_IN_PUBMED_FIRST_AUTHOR_NOT_INDEXED' in r['basis']
