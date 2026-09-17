"""Reviewed held-source harm adjudications. Static judgments, source-backed values.

No network. Does not change primary outcomes or screening membership.
"""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.verified_inputs import entries, load

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')

SPECS = {
 'dapagliflozin-hfpef-hosp': [('Adverse events', 'RR', ['adverse events'])],
 'doac-vte-recurrence': [
     ('Major bleeding', 'HR', ['major bleeding']),
     ('Major or clinically relevant nonmajor bleeding', 'HR', ['clinically relevant nonmajor bleeding', 'principal safety outcome', 'safety outcome']),
     ('Any bleeding', 'HR', ['any bleeding']),
     ('Adverse events', 'RR', ['adverse events']),
     ('Adverse events leading to discontinuation', 'RR', ['adverse events leading to discontinuation'])],
 'dpp4-mace-t2d': [('Adverse events', 'RR', ['adverse events']),
     ('Hypoglycemia', 'RR', ['hypoglycemia', 'hypoglycaemia']),
     ('Acute pancreatitis', 'RR', ['pancreatitis']),
     ('Hospitalization for heart failure', 'HR', ['hospitalization for heart failure', 'hospitalized for heart failure'])],
 'sglt2-primary-prevention-hf': [('Adverse events', 'RR', ['adverse events', 'adverse reactions']),
     ('Lower-limb amputation', 'HR', ['amputation']),
     ('Genital infection', 'RR', ['genital infection']),
     ('Diabetic ketoacidosis', 'RR', ['ketoacidosis'])],
}
DECISIONS = []

def add(slug, pid, outcome, start, end=None, *, values=None, scale=None, reason=None, code='REFUSED_ON_EVIDENCE'):
    records = read(ROOT/f'cache/{slug}/records.json')['records']
    abstract = next(r['abstract'] for r in records if str(r['id']) == pid)
    pos = abstract.index(start)
    # Retain through the conclusion boundary: punctuation in "vs." must not
    # truncate a confidence interval out of its source span.
    stop = abstract.index(end, pos) if end else -1
    span = abstract[pos:] if stop < 0 else abstract[pos:stop + (0 if end else 1)]
    entry = dict(outcome=outcome, source_span=span,
                 document_ref=f'cache/{slug}/records.json', source_level=1, override=True)
    if values:
        entry.update(kind='extracted_effect', effect=values[0], ci_low=values[1], ci_high=values[2],
                     scale=scale, source=span, provenance='abstract_verified',
                     verification='Exact arm-oriented published effect and two-sided CI in held abstract; not a reconstructed effect.')
    else:
        entry.update(kind='typed_refusal', provenance=code, reason=reason)
    path = ROOT/f'cache/{slug}/verified_effects.json'
    data = read(path) if path.exists() else {}
    rows = [e for e in entries(data.get(pid)) if e['outcome'] != outcome] + [entry]
    data[pid] = rows[0] if len(rows) == 1 else rows
    write(path, data)
    DECISIONS.append(dict(slug=slug, pmid=pid, outcome=outcome, entry=entry))

def main():
    for slug, specs in SPECS.items():
        path = ROOT/f'topics/{slug}.json'
        cfg = read(path)
        cfg['harm_outcomes'] = [dict(name=n, estimand=e, keywords=k,
            population=('trial-wide randomized/safety cohort, not a primary-prevention-only subgroup'
                        if slug=='sglt2-primary-prevention-hf' else
                        'trial-reported randomized comparison / safety population'),
            timepoint='trial-reported follow-up') for n,e,k in specs]
        write(path,cfg)
    s='dapagliflozin-hfpef-hosp'
    add(s,'36027570','Adverse events','The incidence of adverse events',
        reason='Narrative similarity supplies no all-adverse-event numerator or effect and CI. Held AACT separates serious and other adverse events; these overlapping populations cannot be summed into any-AE patients.')
    add_counts(s,'34711976','Adverse events',(44,162,38,162),
        'Adverse events were similar between dapagliflozin and placebo',
        'Published patients with adverse events; denominators 162 per arm independently read from NCT03030235 AACT safety totals and checked against 27.2% and 23.5%.',
        denominator_nct='NCT03030235')
    # The abstract supplies event counts but not explicit arm denominators; use
    # the held AACT denominator with the published percentage cross-check below.
    s='doac-vte-recurrence'
    for pid,start,v in [('24344086','The safety end point, major bleeding',(0.69,0.36,1.32)),
                        ('19966341','Major bleeding episodes occurred',(0.82,0.45,1.48)),
                        ('22449293','Major bleeding was observed',(0.49,0.31,0.79))]:
        add(s,pid,'Major bleeding',start,values=v,scale='HR')
    add(s,'23808982','Major bleeding','Major bleeding occurred',
        reason='Published major-bleeding effect is a risk ratio, not the registered hazard ratio. Percentages do not supply an HR or its variance.',code='EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH')
    add(s,'21128814','Major bleeding','In the continued-treatment study, which included', 'CONCLUSIONS:',
        reason='The numerically reported major bleeding is the extended-treatment placebo comparison, not the acute-DVT VKA comparison; registry preferred terms do not establish the adjudicated major-bleeding endpoint.',code='POPULATION_MISMATCH')
    add(s,'23991658','Major bleeding','The principal safety outcome was',
        reason='The reported safety effect combines major and clinically relevant nonmajor bleeding. It cannot be used as major bleeding alone; preferred-term AACT diagnoses cannot reconstruct an adjudicated major-bleeding aggregate.')
    for pid,start,v in [('22449293','The principal safety outcome occurred',(0.90,0.76,1.07)),
                        ('23991658','The safety outcome occurred',(0.81,0.71,0.94))]:
        add(s,pid,'Major or clinically relevant nonmajor bleeding',start,values=v,scale='HR')
    add(s,'21128814','Major or clinically relevant nonmajor bleeding','The principal safety outcome occurred',
        reason='Only equal rounded percentages are given for the acute-treatment safety composite; no HR and CI. AACT individual bleeding diagnoses cannot recover that adjudicated composite effect.')
    add(s,'23808982','Major or clinically relevant nonmajor bleeding','The composite outcome of major bleeding',
        reason='The composite effect is a risk ratio rather than the registered hazard ratio; no HR variance is supplied.',code='EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH')
    for pid,start,v in [('24344086','Any bleeding occurred',(0.67,0.56,0.81)),
                        ('19966341','Major bleeding episodes occurred',(0.71,0.59,0.85))]:
        add(s,pid,'Any bleeding',start,values=v,scale='HR')
    for pid,start in [('24344086','Deaths, adverse events'),('19966341','Adverse events leading to discontinuation'),
                      ('22449293','Rates of other adverse events'),('23991658','The rates of other adverse events'),
                      ('23808982','Rates of other adverse events')]:
        add(s,pid,'Adverse events',start,reason='No deduplicated all-adverse-event count or RR with CI is supplied. Registry serious and nonserious preferred-term rows overlap and cannot be summed; discontinuation is a different endpoint from any AE.')
    for pid,start in [('24344086','The safety end point, major bleeding'),('19966341','Safety end points included')]:
        add(s,pid,'Major or clinically relevant nonmajor bleeding',start,
            reason='Broad bleeding-term detector matched major or any bleeding; neither is the clinically relevant nonmajor composite. The held abstract does not report that composite estimate.',code='SIGNAL_SPURIOUS')
    for pid,start in [('22449293','The principal safety outcome was'),('21128814','The principal safety outcome was'),
                      ('23991658','The principal safety outcome was'),('23808982','The principal safety outcomes were')]:
        add(s,pid,'Any bleeding',start,
            reason='Broad bleeding-term detector matched major/clinically relevant bleeding, not all bleeding. Those narrower endpoint values cannot be relabeled as any bleeding.',code='SIGNAL_SPURIOUS')
    for pid,start in [('24344086','Deaths, adverse events'),('22449293','Rates of other adverse events'),
                      ('23991658','The rates of other adverse events'),('23808982','Rates of other adverse events')]:
        add(s,pid,'Adverse events leading to discontinuation',start,
            reason='Generic adverse-event narrative does not report discontinuation due to adverse events; broad term matching is spurious for this endpoint.',code='SIGNAL_SPURIOUS')
    add(s,'19966341','Adverse events leading to discontinuation','Adverse events leading to discontinuation',
        reason='Rounded discontinuation percentages only, without exact numerators or effect and CI; cannot invent events by multiplying randomized denominators. Held registry event terms do not identify a deduplicated discontinuation aggregate.')
    s='dpp4-mace-t2d'
    for outcome,values in [('Adverse events',(2697,3494,2723,3485)),('Hypoglycemia',(1036,3494,1024,3485))]:
        add_counts(s,'30418475',outcome,values,'INTERVENTIONS:',
                   'Arm sizes and patient counts stated explicitly in the same held abstract, in linagliptin then placebo order; safety population received at least one dose.')
    add(s,'30418475','Acute pancreatitis','Adverse events occurred',
        reason='The abstract calls the pancreatitis values events, rather than unique patients. No deduplicated participant numerator is established; registry preferred-term pancreatitis is not the adjudication-confirmed endpoint.')
    add(s,'26052984','Adverse events','CONCLUSIONS:',reason='Conclusion reports no apparent increase in other adverse events without all-AE counts or a ratio interval. AACT serious/other event strata cannot be summed into unique any-AE participants.')
    add(s,'23992602','Hypoglycemia','Incidences of hypoglycemia',reason='Narrative comparison supplies no hypoglycemia numerator or RR and CI. Registry preferred terms for severe and other hypoglycemia are not an adjudicated all-hypoglycemia aggregate.')
    for pid,start in [('23992602','Incidences of hypoglycemia'),('23992601','Rates of adjudicated cases'),('26052984','There were no significant between-group differences in rates of acute pancreatitis')]:
        add(s,pid,'Acute pancreatitis',start,reason='Narrative or rounded percentages only for adjudicated pancreatitis; no exact numerator and denominator pair or effect with CI. Registry pancreatitis preferred terms are not equivalent to adjudication-confirmed cases and must not be summed.')
    for pid,start,v in [('23992601','More patients in the saxagliptin',(1.27,1.07,1.51)),
                        ('26052984','Rates of hospitalization for heart failure',(1.00,0.83,1.20))]:
        add(s,pid,'Hospitalization for heart failure',start,values=v,scale='HR')
    s='sglt2-primary-prevention-hf'
    add(s,'28605608','Lower-limb amputation','Adverse reactions were consistent',values=(1.97,1.41,2.75),scale='HR')
    add(s,'32966714','Lower-limb amputation','Amputations were performed',
        reason='Dose-specific counts and rounded percentages are reported, but no hazard ratio or CI; a cumulative count RR cannot supply the registered HR.',code='EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH')
    for pid,start in [('28605608','Adverse reactions were consistent'),('26378978','Among patients receiving empagliflozin'),('30415602','Diabetic ketoacidosis was more common')]:
        add(s,pid,'Adverse events',start,reason='The source gives specific adverse-event signals rather than a deduplicated any-AE total. Held AACT serious and other adverse-event populations may overlap and cannot be summed.')
    for pid,start in [('26378978','Among patients receiving empagliflozin'),('30415602','Diabetic ketoacidosis was more common')]:
        add(s,pid,'Genital infection',start,reason='No exact all-genital-infection count or RR interval is supplied. DECLARE reports the narrower serious-or-discontinuation endpoint; AACT sex-specific and preferred-term categories cannot be summed into a deduplicated all-genital-infection count.')
    add(s,'30415602','Diabetic ketoacidosis','Diabetic ketoacidosis was more common',
        reason='Rounded percentages only for the reported trial endpoint. AACT splits diabetic, euglycemic and unspecified ketoacidosis in a treated population; their sum is not a deduplicated adjudicated endpoint and does not recover the abstract numerator.')
    registry_dispositions()
    for slug in SPECS:
        load(slug)
    write(ROOT/'outputs/handover/in3/decisions.json',DECISIONS)
    audit_path=ROOT/'docs/evidence/override-audit-2026-09-14/overrides.json'
    audit=read(audit_path)
    key=lambda r:(r['topic'],r['file'],str(r['trial']),r['outcome'])
    for d in DECISIONS:
        e=d['entry']
        row=dict(topic=d['slug'],trial=d['pmid'],outcome=d['outcome'],
                 file='verified_arms.json' if e['kind']=='extracted_counts' else 'verified_effects.json',
                 source_committed=True,source_committed_evidence=e['document_ref'],
                 override_replaces='Unregistered harm or unresolved held-source reporting signal',
                 override_with=e['kind'],stated_reason=e.get('reason') or e.get('verification'),
                 judgement=e.get('reason') or e.get('verification'),
                 rule_group='IN3 held-source endpoint and population adjudication')
        audit=[r for r in audit if key(r)!=key(row)]+[row]
    write(audit_path,audit)

def add_counts(slug,pid,outcome,values,start,note,denominator_nct=None):
    rec = next(r for r in read(ROOT/f'cache/{slug}/records.json')['records'] if str(r['id'])==pid)
    span=rec['abstract'][rec['abstract'].index(start):]
    entry=dict(kind='extracted_counts',outcome=outcome,override=True,
               **dict(zip(('ai','n1i','ci','n2i'),values)),
               source_span=span,source=span,source_level=1,
               document_ref=f'cache/{slug}/records.json',
               provenance='abstract_verified_arms',verification=note)
    if denominator_nct:
        from harness import aact
        path=ROOT/'outputs/handover/in3/aact/reported_event_totals.txt'
        totals=[r for r in aact._iter_rows(str(path)) if r['nct_id']==denominator_nct and r['event_type']=='serious']
        assert len(totals)==2 and [int(r['subjects_at_risk']) for r in totals]==[values[1],values[3]]
        entry['denominator_source']=dict(document_ref=path.relative_to(ROOT).as_posix(),nct=denominator_nct,rows=totals)
        raw=path.read_text(encoding='utf-8').splitlines()
        cited=[line for line in raw if line.split('|')[0] in {r['id'] for r in totals}]
        assert len(cited)==2
        entry['source']=span+'\nAACT denominator source '+path.relative_to(ROOT).as_posix()+':\n'+ '\n'.join(cited)
    path=ROOT/f'cache/{slug}/verified_arms.json'
    data=read(path) if path.exists() else {}
    rows=[e for e in entries(data.get(pid)) if e['outcome']!=outcome]+[entry]
    data[pid]=rows[0] if len(rows)==1 else rows
    write(path,data)
    DECISIONS.append(dict(slug=slug,pmid=pid,outcome=outcome,entry=entry))

def registry_dispositions():
    """Reviewed endpoint-specific reasons for registry-only reporting signals.

    Select exact-NCT held rows dynamically; never manufacture an event total.
    """
    from harness import aact
    folder=ROOT/'outputs/handover/in3/aact'
    identities=read(folder/'manifest.json')['identities']
    specs=[
        ('dapagliflozin-hfpef-hosp',['37534453'],'Adverse events',None),
        ('doac-vte-recurrence',['21128814'],'Adverse events',None),
        ('dpp4-mace-t2d',['23992602','23992601','28893244'],'Adverse events',None),
        ('sglt2-primary-prevention-hf',['32966714'],'Adverse events',None),
        ('dpp4-mace-t2d',['23992601','26052984','28893244'],'Hypoglycemia',['hypogly']),
        ('dpp4-mace-t2d',['28893244'],'Acute pancreatitis',['pancreatitis']),
        ('sglt2-primary-prevention-hf',['26378978','30415602'],'Lower-limb amputation',['amput']),
        ('sglt2-primary-prevention-hf',['28605608','32966714'],'Genital infection',['genital infection','genital mycotic','vulvovaginal','balanitis']),
        ('sglt2-primary-prevention-hf',['28605608','26378978','32966714'],'Diabetic ketoacidosis',['ketoacidosis']),
    ]
    reasons={
        'Adverse events':'Held registry reports serious and other adverse-event totals, not a deduplicated any-adverse-event total. The sets may overlap; summing them would invent unique patients.',
        'Hypoglycemia':'Held registry distinguishes serious and nonserious preferred-term hypoglycemia and related diagnoses; these are not a deduplicated all-hypoglycemia patient total, and overlapping rows must not be summed.',
        'Acute pancreatitis':'Registry preferred-term pancreatitis is not the adjudication-confirmed acute-pancreatitis endpoint; a matching participant aggregate or RR interval is not established.',
        'Lower-limb amputation':'Registry amputation terms include traumatic amputation and/or stump complications; these do not establish the trial-defined lower-limb-amputation endpoint or its hazard ratio.',
        'Genital infection':'Registry separates sex-specific genital infections and preferred terms, with reporting thresholds and possible overlap. No deduplicated all-genital-infection count is established.',
        'Diabetic ketoacidosis':'Registry separates diabetic, unspecified and related ketoacidosis preferred terms and safety populations. These rows do not establish a deduplicated trial-defined ketoacidosis aggregate; categories cannot be summed.',
    }
    for slug,pids,outcome,terms in specs:
        filename='reported_events.txt' if terms else 'reported_event_totals.txt'
        path=folder/filename
        raw=path.read_text(encoding='utf-8').splitlines()
        names=raw[0].split('|')
        for pid in pids:
            ids=next(i['ncts'] for i in identities if i['slug']==slug and i['pmid']==pid)
            matched=[]
            for line in raw[1:]:
                row=dict(zip(names,line.split('|')))
                if row['nct_id'] not in ids:
                    continue
                if terms and not any(t in row.get('adverse_event_term','').lower() for t in terms):
                    continue
                if not terms and row.get('event_type') not in ('serious','other'):
                    continue
                matched.append(line)
            if not matched:
                continue  # no held registry signal for this endpoint; never invent one
            # One exact row is the cited reporting signal; the retained full
            # table supplies every candidate inspected, including other arms.
            entry=dict(kind='typed_refusal',outcome=outcome,provenance='REFUSED_ON_EVIDENCE',
                       reason=reasons[outcome],source_span=matched[0],
                       document_ref=path.relative_to(ROOT).as_posix(),source_level=1,
                       registry_ncts=ids,registry_candidate_rows=len(matched))
            target=ROOT/f'cache/{slug}/verified_effects.json'
            data=read(target) if target.exists() else {}
            rows=[e for e in entries(data.get(pid)) if e['outcome']!=outcome]+[entry]
            data[pid]=rows[0] if len(rows)==1 else rows
            write(target,data)
            DECISIONS.append(dict(slug=slug,pmid=pid,outcome=outcome,entry=entry))

if __name__ == '__main__':
    main()
