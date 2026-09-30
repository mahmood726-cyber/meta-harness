"""Defect plants exercise base behavior and the proposed fail-closed boundary."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import pytest
from harness import table_binding as b, table_rows, synth, extract, dose_arms, measure_identity, verified_inputs
from scripts import make_philo_excerpt as philo, make_plato_fda_excerpt as plato
from scripts.ticagrelor_census import lane_bindings, proposed_pool, relay_block

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'ticagrelor-vs-clopidogrel-acs'


@pytest.fixture(scope='module')
def bound():
    return lane_bindings()


def get(bound,name,trial):
    return next(row for n,row in bound if n==name and row['trial']==trial)


def test_deterministic_excerpts_and_actual_sources():
    assert philo.render() == philo.render() == (ROOT/philo.OUTPUT).read_bytes()
    assert plato.render() == plato.render()
    for name,data in plato.render().items():
        assert (ROOT/name).read_bytes() == data
        assert not data.startswith(b'\xef\xbb\xbf')
    assert hashlib.sha256((ROOT/philo.PDF).read_bytes()).hexdigest() == philo.SHA
    assert hashlib.sha256((ROOT/plato.PDF).read_bytes()).hexdigest() == plato.SHA


def test_source_sha_and_tampering_fail_closed(tmp_path):
    pdf = tmp_path/philo.PDF
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b'not the source')
    with pytest.raises(ValueError,match='SHA mismatch'):
        philo.render(tmp_path)
    path=tmp_path/Path(philo.OUTPUT).name
    path.write_bytes((ROOT/philo.OUTPUT).read_bytes().replace(b'40 (10.3)',b'41 (10.3)'))
    with pytest.raises(ValueError,match='SOURCE_BINDING_MISMATCH'):
        b.bind(SLUG,{'name':'Major bleeding','estimand':'HR'},path)


@pytest.mark.parametrize('label,name',[
    ('Major bleeding non-CABG-related','Major bleeding'),
    ('Dyspnea leading to discontinuation','Dyspnea'),
    ('Dyspnea serious adverse event','Dyspnea')])
def test_wrong_variant_plant(label,name):
    table=table_rows.parse(ROOT/philo.OUTPUT)[0]
    row=deepcopy(table['rows'][0]); row['label']=label
    table['rows']=[row]
    # Base selector with no exclusions admits a uniquely matching wrong variant.
    assert table_rows.select(table,[name],[])[0] == row
    with pytest.raises(ValueError,match='ROW_IDENTITY'):
        b.select_row(table,{'name':name})


def test_identity_negative_plants(bound):
    assert get(bound,'Major bleeding','PHILO')['row_label']=='Major bleeding (PLATO-defined)'
    assert get(bound,'Dyspnea','PHILO')['variant_flags']==[]
    assert get(bound,'Dyspnea','PLATO')['row_label']=='Dyspnea adverse event'


def test_published_preference_and_count_precedence_plant(bound):
    row=get(bound,'Major bleeding','PHILO')
    counts={k:row[k] for k in ('ai','n1i','ci','n2i')}
    pub=row['input']
    # Base Study silently prioritizes counts if both representations are supplied.
    base=synth.Study('plant',**counts,effect=pub['effect'],ci_low=pub['ci_low'],ci_high=pub['ci_high'],measure='HR')
    assert math.exp(base.yi_vi()[0]) == pytest.approx((row['ai']/row['n1i'])/(row['ci']/row['n2i']))
    assert math.exp(base.yi_vi()[0]) != pytest.approx(pub['effect'])
    assert pub['derivation']=='PUBLISHED' and pub['measure']=='HAZARD_RATIO'
    assert 'ai' not in pub
    assert any(c['derivation']=='RECONSTRUCTED' for c in row['candidates'])
    assert get(bound,'Dyspnea','PHILO')['input']['derivation']=='RECONSTRUCTED'


def test_abstract_absence_superseded(bound):
    row=get(bound,'Dyspnea','PHILO')
    review=json.loads((ROOT/'docs/reviews'/SLUG/'review.json').read_text(encoding='utf-8'))
    old=next(r for o in review['outcomes'] if o['name']=='Dyspnea'
             for r in o['declared_absent_trials'] if row['pmid'] in r['id'])
    assert old['result_status']['state']=='RETRIEVED_NOT_REPORTED'
    records=json.loads((ROOT/'cache'/SLUG/'records.json').read_text(encoding='utf-8'))['records']
    abstract=next(r['abstract'] for r in records if str(r['id'])==row['pmid'])
    base=extract.extract_trial(abstract,['dyspnea','dyspnoea'],['ticagrelor'],['clopidogrel'],declared_composite=False,estimand='RR')
    assert not base or not base.get('effect') and base.get('ai') is None
    updated=b.supersede_absence(old,row)
    assert updated['state']=='TABLE_BOUND'
    assert updated['result_status']['state']=='TABLE_BOUND'
    assert old['state']=='OUTCOME_NOT_IN_SOURCE'  # caller is not mutated
    with pytest.raises(ValueError,match='not an abstract-scoped absence'):
        b.supersede_absence(dict(id=old['id'],state='REFUSED',reason='wrong population'),row)


def test_mixed_pool_plant(bound):
    ph=get(bound,'Major bleeding','PHILO')['input']
    pl=get(bound,'Major bleeding','PLATO')
    counts={k:pl[k] for k in ('ai','n1i','ci','n2i')}
    # Base engine pools the invalid mixed inputs under a single HR label.
    base=synth.pool([synth.Study('PHILO',effect=ph['effect'],ci_low=ph['ci_low'],ci_high=ph['ci_high']),
                     synth.Study('PLATO',**counts)],scale='HR')
    assert base.k==2 and base.scale=='HR'
    with pytest.raises(ValueError,match='MEASURE_MIX_POOLED'):
        b.require_pool([ph,counts])
    assert b.require_pool([ph,pl['input']])
    assert b.require_pool([get(bound,'Dyspnea','PHILO')['input'],get(bound,'Dyspnea','PLATO')['input']])


def test_patients_not_events_or_km(bound):
    pl=get(bound,'Major bleeding','PLATO')
    assert [a['count_unit'] for a in pl['excluded_columns']]==['EVENTS','EVENTS']
    assert pl['count_unit']=='PATIENTS'
    table=table_rows.parse(ROOT/plato.OUTPUTS[0])[0]
    row=deepcopy(table['rows'][0]); row['cells'][1]='11.6%'; row['cells'][4]='11.2%'
    with pytest.raises(ValueError,match='COUNT_UNIT'):
        b.choose(table,row,['HR'])


def test_disperse_km_shared_control_and_mi_plants():
    d=b.disperse(); record=d['record']
    assert d['status']=='REFUSED' and d['recovery']=='ACTIVE'
    assert len(d['arms'])==3 and all(a['n'] is None for a in d['arms'])
    # Synthetic test denominator only; never derived from 1:1:1 or exposed as evidence.
    abstract=record['abstract']
    km=next(s for s in abstract.split(';') if 'Kaplan-Meier' in s and '%' in s)
    import re
    pct=float(re.search(r'(\d+(?:\.\d+)?)%',km)[1])
    fabricated=dict(ai=round(pct*1000/100),n1i=1000,ci=1,n2i=1000)
    assert math.isfinite(synth.Study('KM plant',**fabricated).yi_vi()[0])
    assert dose_arms.km_products(fabricated,km)
    assert not dose_arms.km_products(fabricated,'Observed patient counts explicitly reported.')
    with pytest.raises(ValueError,match='FULL_TABLE_NOT_HELD'):
        dose_arms.require_poolable(record,fabricated)
    repeated=[dict(trial_id=d['pmid'],outcome='major bleeding',control_id='shared',
                   n2i=100,ci=10,control_n=100,control_events=10) for _ in range(2)]
    assert synth.pool([synth.Study(str(i),ai=12,n1i=100,ci=r['ci'],n2i=r['n2i']) for i,r in enumerate(repeated)]).k==2
    with pytest.raises(ValueError,match='SHARED_CONTROL_DOUBLE_COUNTED'):
        dose_arms.require_controls(repeated)
    assert dose_arms.require_controls(dose_arms.split_control(repeated))
    assert dose_arms.require_controls(repeated[:1])
    mi='Myocardial infarction (HR 0.8; 95% CI 0.6 to 1.0).'
    assert extract.extract_effect(mi)
    assert dose_arms.endpoint_problem(mi,'MACE composite')=='MI_ONLY_NOT_COMPOSITE'
    assert dose_arms.endpoint_problem('Composite of death, myocardial infarction and stroke','MACE composite') is None


def test_relay_never_admitted_definition_separate(bound):
    data=relay_block(bound)
    d,m=data['entries']
    assert d['values']['ai']['binding_state']=='DEFINITION_DIFFERS'
    assert d['values']['ci']['binding_state']=='DEFINITION_DIFFERS'
    assert d['values']['effect']['binding_state']=='RELAYED_ONLY'
    assert m['values']['effect']['binding_state']=='BOUND'
    assert all(not e['poolable'] for e in data['entries'])
    # Base input normalizer accepts a relayed effect unless a new gate intervenes.
    plant=dict(outcome='Dyspnea',derivation='RELAYED',effect=d['values']['effect']['value'])
    assert verified_inputs.runtime(plant)['kind']=='extracted_effect'
    with pytest.raises(ValueError,match='relayed'):
        b.require_pool([plant])
    assert get(bound,'Dyspnea','PLATO')['published_effect'] is None
    with pytest.raises(ValueError,match='MEASURE_REFUSED'):
        b.bind(SLUG,{'name':'Dyspnea','estimand':'HR'},ROOT/plato.OUTPUTS[1])


def test_proposed_canonical_pool_and_reml_equivalence(bound):
    p=proposed_pool(bound)
    assert p['label']=='PROPOSED SERVED CHANGE'
    assert p['result']['k']==2 and not p['disperse_in_pool']
    assert p['result']['tau2']==pytest.approx(p['reml_two_study_check'],abs=1e-9)
    assert p['result']['pi_low'] < p['result']['ci_low'] < p['result']['estimate'] < p['result']['ci_high'] < p['result']['pi_high']
    assert p['result']['ci_provenance']==synth.CI_PROVENANCE
