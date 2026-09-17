"""Apply individually reviewed HM3 decisions from held bytes, offline.

Static: endpoint adjudications and transcribed digits below.
Dynamic: exact raw spans, baseline identities, audit coverage. No inferred counts.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import absence
from harness.verified_inputs import entries, load

EVIDENCE = ROOT / 'docs/evidence/hm3-held-source-audit'
EVIDENCE.mkdir(parents=True, exist_ok=True)
ROWS = json.loads((EVIDENCE / 'baseline-debt.json').read_text(encoding='utf-8'))
for row in ROWS:
    records = json.loads((ROOT/'cache'/row['slug']/'records.json').read_text(encoding='utf-8'))['records']
    row['record'] = next(r for r in records if str(r['id']) == row['id'])
DECISIONS = []


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def ab(i):
    return ROWS[i]['record']['abstract']


def ft(i):
    r = ROWS[i]
    return (ROOT / 'cache' / r['slug'] / ('ft_' + r['id'] + '.txt')).read_text(encoding='utf-8')


def table(i, marker):
    matches = [t for t in re.findall(r'<table-wrap\b.*?</table-wrap>', ft(i), re.S)
               if marker in absence._strip_markup(t)]
    assert len(matches) == 1, (i, marker, len(matches))
    return matches[0]


def sentence(i, start):
    text = ab(i)
    pos = text.index(start)
    end = text.find('. ', pos)
    return text[pos:] if end < 0 else text[pos:end+1]


def add(i, entry, category, fulltext=False):
    r = ROWS[i]
    span = entry.get('source_span') or entry['source']
    assert span in (ft(i) if fulltext else ab(i)), (i, 'not verbatim')
    entry.update(outcome=r['outcome'], override=True,
                 source_level='fulltext' if fulltext else 'abstract',
                 document_ref=f"cache/{r['slug']}/" + (f"ft_{r['id']}.txt" if fulltext else 'records.json'))
    filename = 'verified_arms.json' if 'ai' in entry else 'verified_effects.json'
    path = ROOT / 'cache' / r['slug'] / filename
    data = load(r['slug'])[filename]
    values = [v for v in entries(data.get(r['id'])) if v['outcome'] != r['outcome']]
    values.append(entry)
    data[r['id']] = values[0] if len(values) == 1 else values
    write(path, data)
    DECISIONS.append(dict(index=i, topic=r['slug'], trial=r['id'], outcome=r['outcome'],
                          file=filename, category=category, entry=entry))


def refuse(i, reason, span, code='REFUSED_ON_EVIDENCE', fulltext=False):
    add(i, dict(absent=True, provenance=code, reason=reason, source_span=span),
        'spurious signal' if code == 'SIGNAL_SPURIOUS' else 'typed refusal', fulltext)


def counts(i, values, span, note, fulltext=False):
    for value in values:
        assert re.search(r'(?<!\d)' + str(value) + r'(?!\d)', span), (i, value)
    add(i, dict(zip(('ai','n1i','ci','n2i'), values), source=span,
                provenance='fulltext_verified_arms' if fulltext else 'abstract_verified_arms',
                verification=note), 'extracted (counts)', fulltext)


def effect(i, values, span, note, fulltext=False):
    for value in values:
        assert str(value) in span or format(value, '.2f') in span, (i, value)
    add(i, dict(zip(('effect','ci_low','ci_high'), values), scale='HR', source=span,
                verification=note), 'extracted (effect+CI)', fulltext)


refuse(0, 'The abstract reports no serious adverse events, but the held safety analysis uses SOC 29 and tocilizumab 33 rather than the randomized 30 and 32, so an as-randomized safety denominator is not established.',
       table(0, 'Safety analysis'), 'POPULATION_MISMATCH', True)
refuse(1, 'The held table gives patients with serious adverse events through study day 29, whereas this protocol specifies by day 28; the day-28 counts are not separately reported.',
       table(1, 'Serious adverse events by system organ class'), 'TIMEPOINT_MISMATCH', True)
refuse(2, 'The safety table reports 128/429 and 72/213 in the treated safety population rather than the randomized 434 and 215 required by the protocol.',
       table(2, 'Safety to day 28'), 'POPULATION_MISMATCH', True)
refuse(3, 'The source reports 20 and 29 serious-adverse-event patients but excludes a tocilizumab consent withdrawal from analysis, so these are not the protocol as-randomized counts over 64 and 67.',
       ab(3)[ab(3).index('RESULTS:'):ab(3).index('CONCLUSIONS')], 'POPULATION_MISMATCH')
# Raw contiguous full-text span retains both the participant counts and table denominators.
t4 = table(4, 'Adverse Events in the Safety Population')
text4 = ft(4)
span4 = text4[text4.index('There were 36 serious adverse events'):text4.index(t4)+len(t4)]
counts(4, (28,161,12,82), span4,
       'Published safety narrative reports 28 and 12 participants with serious adverse events (not 36 and 38 recurrent events); Table 4 provides the randomized 161 and 82 denominators. AACT totals differ (19 and 8); the published all-SAE participant counts are used, not summed registry categories.', True)
refuse(5, 'The safety table explicitly assigns patients according to treatment received (67 and 62), whereas the protocol requires the randomized groups (65 and 64).',
       table(5, 'Adverse events (safety population)'), 'POPULATION_MISMATCH', True)
refuse(6, 'The source reports no serious adverse events but supplies no count of patients with any adverse event or side effect, the registered broader endpoint.',
       sentence(6, 'No serious adverse events were reported.'))
refuse(7, 'The safety analysis pools randomized, single-blind and open-label studies and therefore cannot supply an independent randomized-trial adverse-event comparison.',
       sentence(7, 'Safety measures included'), 'POPULATION_MISMATCH')
counts(8, (136,394,142,395), table(8, 'Number (%) of patients who had an adverse event'),
       'Table 8: Any AE in the initial three-week randomized treatment period, entire adult safety population; extension-period rerandomization is not combined with it.', True)
refuse(9, 'The source describes a low incidence and minor severity of adverse events but reports no arm counts or effect with confidence interval.',
       sentence(9, 'The incidence of adverse events'))
refuse(10, 'The source reports no significant side-effect difference across placebo and two melatonin doses without dose-specific counts or effect with confidence interval.',
       sentence(10, 'RESULTS: There were no significant'), 'MULTI_ARM_UNRESOLVED')
refuse(11, 'The source gives renal-replacement therapy counts and mean creatinine changes, but no incidence count or ratio estimate for acute kidney injury itself.',
       ab(11)[ab(11).index('New renal-replacement therapy was initiated'):ab(11).index('The number of adverse')])
refuse(12, 'The acute-kidney-injury phrase describes background literature, not a reported kidney-injury result of this trial.',
       sentence(12, 'Clinical and laboratory studies'), 'SIGNAL_SPURIOUS')
refuse(13, 'The study uses a cluster-randomized multiple-crossover design; held AACT supplies unadjusted AKI counts but no cluster-adjusted harm effect or design effect, so a binomial participant analysis would ignore the randomized unit.',
       sentence(13, 'METHODS: This was a cluster-randomized'))
refuse(14, 'The source reports only a P value for the AKI comparison, without per-arm counts or a ratio estimate and confidence interval.',
       sentence(14, 'There was no significant difference in the incidence'))
counts(15, (1,16,0,14), sentence(15, 'At day 28,'),
       'Direct serious-adverse-reaction fractions at day 28; matches the harm specification keywords and randomized hydrocortisone/placebo arms.')
refuse(16, 'The source reports separate fixed-dose and shock-dependent hydrocortisone arms against one control without a prespecified harm arm-selection or combination rule.',
       sentence(16, 'Serious adverse events were reported'), 'MULTI_ARM_UNRESOLVED')
refuse(17, 'The source says no serious adverse events were related to treatment but does not provide per-arm all-SAE incidence or a serious-reaction result at the specified day 28.',
       sentence(17, 'No serious adverse events were related'))
refuse(18, 'The source reports other serious adverse events separately from secondary infections and insulin use, without a deduplicated total matching serious adverse reactions.',
       sentence(18, 'Thirty-three patients'))
refuse(19, 'The source reports hospitalization for atrial fibrillation or flutter as percentages only; AACT serious preferred-term rows are narrower treated-population events and do not reconstruct that hospitalized composite.',
       sentence(19, 'A larger percentage'))
refuse(20, 'The held text gives only a narrative bleeding comparison; AACT reports gastrointestinal bleeding and nosebleeds separately, without a deduplicated overall bleeding count.',
       sentence(20, 'No excess risks'))
refuse(21, 'The source reports serious bleeding percentages without event counts; AACT splits bleeding across potentially overlapping preferred terms, so their sum cannot establish patients with bleeding.',
       sentence(21, 'Serious bleeding events'))
refuse(22, 'The signal is an exclusion in the vascular efficacy endpoint definition, not a bleeding result; the AACT major-bleed endpoint is explicitly for the aspirin comparison only.',
       sentence(22, 'The primary outcome was'), 'SIGNAL_SPURIOUS')
refuse(23, 'The source describes transient mild-to-moderate gastrointestinal effects without per-arm numbers or an effect and confidence interval.',
       sentence(23, 'Adverse events were transient'))
refuse(24, 'The source calls gastrointestinal events the most common adverse events but supplies no aggregate per-arm incidence; AACT individual symptom rows cannot be summed into unique patients.',
       sentence(24, 'Gastrointestinal adverse events'))
refuse(25, 'The source provides gastrointestinal-event percentages without numerators, while AACT reports individual symptoms and total event counts rather than deduplicated gastrointestinal patients.',
       sentence(25, 'Gastrointestinal adverse events'))
refuse(26, 'The source counts treatment discontinuations due to gastrointestinal events rather than all patients with gastrointestinal events; AACT individual symptom rows do not supply that aggregate.',
       sentence(26, 'More participants in the semaglutide group'))
refuse(27, 'The source describes serious hyperkalemia as minimal in both groups without arm counts or a reported effect and confidence interval.',
       sentence(27, 'The incidence of serious hyperkalemia'))
refuse(28, 'The source gives potassium-threshold percentages only; AACT separates serious and nonserious investigator-coded hyperkalemia and hospitalization, which do not reconstruct the unique patients exceeding that laboratory threshold.',
       sentence(28, 'A serum potassium level'))
refuse(29, 'The source reports hyperkalemia narratively; AACT supplies nonserious coded hyperkalemia and hospitalization endpoints, without the overall laboratory-threshold count or a matching effect and confidence interval.',
       sentence(29, 'Adverse events, including hyperkalemia'))
refuse(30, 'The source reports gynecomastia or breast pain percentages among men, without male-specific arm denominators or numerators.',
       sentence(30, 'Gynecomastia or breast pain'))
counts(31, (14,203,1,198), ab(31)[ab(31).index('RESULTS:'):ab(31).index('CONCLUSION:')],
       'Explicit randomized arm denominators and hyperglycaemia counts in the same results paragraph; no percentage inversion.')
counts(32, (67,151,35,153), sentence(32, 'In-hospital mortality'),
       'Explicit per-arm patients with hyperglycaemia and denominators in the same sentence.')
refuse(33, 'The source describes similar gastrointestinal bleeding frequencies without per-arm counts or an effect and confidence interval.',
       sentence(33, 'The frequencies of hospital-acquired'))
counts(34, (120,126,89,126), table(34, 'Safety Summary During the Double-Blind Treatment Phase'),
       'Table 4 reports patients with at least one treatment-emergent AE in the double-blind induction phase, not a sum of symptom events.', True)
refuse(35, 'The source lists common adverse events and discontinuation percentages, while AACT separates serious and other events without a deduplicated any-AE total for induction.',
       sentence(35, 'The five most common adverse events'))
refuse(36, 'The source reports discontinuation because of side effects rather than gastrointestinal-specific adverse-event incidence.',
       sentence(36, 'A significantly larger proportion'), 'SIGNAL_SPURIOUS')
refuse(37, 'The source reports discontinuation percentages and a risk-difference interval, without exact discontinuation numerators or a ratio effect and confidence interval for the registered RR.',
       sentence(37, 'A significantly larger proportion'), 'EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH')
refuse(38, 'The source reports no significant amputation difference without counts or a ratio interval, and the AACT amputation-stump-pain term is not an amputation endpoint.',
       sentence(38, 'There were no significant differences in rates'))
effect(39, (1.43,0.80,2.57), table(39, 'Primary, Secondary, Tertiary and Safety Outcomes'),
       'Table 2 explicitly labels hazard ratios (95% CI) and reports lower limb amputation HR 1.43 (0.80-2.57); preserve the published HR rather than derive an RR.', True)
refuse(40, 'The source reports volume depletion narratively; AACT separates hypotension, orthostatic hypotension and dehydration in a treated safety population, without a deduplicated as-randomized composite.',
       sentence(40, 'The frequency of adverse events'))
refuse(41, 'The abstract signal concerns volume depletion, renal dysfunction and hypoglycemia; AACT has separate diabetic-ketoacidosis and ketoacidosis preferred terms in treated patients, without a deduplicated as-randomized ketoacidosis total.',
       sentence(41, 'The frequency of adverse events'))
refuse(42, 'The source describes musculoskeletal events within aggregate serious adverse events, without muscle-symptom or myopathy-specific counts or effect with confidence interval.',
       sentence(42, 'Serious adverse events occurred'))
refuse(43, 'The source says diabetes-related adverse events were more common but does not provide new-onset diabetes counts or an effect with confidence interval.',
       sentence(43, 'Serious adverse events occurred'))
refuse(44, 'The source reports Kaplan-Meier major-bleeding percentages for two ticagrelor doses and one clopidogrel arm, without harm event counts or a dose-specific ratio effect and confidence interval.',
       ab(44)[ab(44).index('RESULTS:'):ab(44).index('Although not statistically')], 'MULTI_ARM_UNRESOLVED')
effect(45, (1.54,0.94,2.53), ab(45)[ab(45).index('Primary safety and efficacy'):ab(45).index('For both analyses')],
       'PHILO 12-month major bleeding HR and 95% CI, not the adjacent primary efficacy HR 1.47; endpoint and treatment direction checked in held abstract.')
refuse(46, 'The source reports similar side effects and acceptability without an adverse-event count or effect with confidence interval.',
       sentence(46, 'Reports of side effects'))
refuse(47, 'The source reports no significant difference in adverse events including thromboembolism but gives no aggregate adverse-event counts or effect with confidence interval.',
       sentence(47, 'Adverse events (including'))
refuse(48, 'The source describes no increased infection risk but gives no serious-infection aggregate; AACT lists individual infection diagnoses which may overlap and cannot be summed into unique patients.',
       sentence(48, 'There was no increase'))
refuse(49, 'The signal counts all-cause adverse-event discontinuations rather than gastrointestinal events; AACT serious gastrointestinal diagnoses do not supply the deduplicated all-GI endpoint.',
       sentence(49, 'Adverse events leading to permanent'), 'SIGNAL_SPURIOUS')

assert len(DECISIONS) == len(ROWS) == 50
write(EVIDENCE / 'decisions.json', DECISIONS)
write(EVIDENCE / 'baseline-debt.json', [{k:r[k] for k in ('slug','id','outcome','signal','spec')} for r in ROWS])

audit_path = ROOT / 'docs/evidence/override-audit-2026-09-14/overrides.json'
audit = json.loads(audit_path.read_text(encoding='utf-8'))
key = lambda r: (r['topic'],r['file'],str(r['trial']),r['outcome'])
for d in DECISIONS:
    e = d['entry']
    row = {k:d[k] for k in ('topic','file','trial','outcome')}
    row.update(source_committed=True, source_committed_evidence=e['document_ref'],
               override_replaces='Baseline KNOWN_REPORTED_NOT_YET_EXTRACTED harm item',
               override_with=d['category'], stated_reason=e.get('reason') or e.get('verification'),
               judgement=e.get('reason') or e.get('verification'),
               rule_group='HM3 held-source endpoint, population and timepoint adjudication')
    audit = [a for a in audit if key(a) != key(row)] + [row]

# Three pre-existing overrides identified by the base audit failure, on HM3 pages.
for slug, filename, pid in [('esketamine-trd-madrs','verified_arms.json','NCT02417064'),
                           ('sglt2-ckd-progression','verified_effects.json','32970396'),
                           ('sglt2-ckd-progression','verified_effects.json','36331190')]:
    value = load(slug)[filename][pid]
    e = entries(value)[0]
    row = dict(topic=slug,file=filename,trial=pid,outcome=e['outcome'],
               source_committed=True,source_committed_evidence=f'cache/{slug}/records.json',
               override_replaces='Previously unaudited endpoint/scale or multi-dose correction',
               override_with=e['outcome'],stated_reason=e['verification'],
               judgement=('Existing combined-dose raw MADRS contrast: per-arm values held in CT.gov cache; combination is derived, not a published adjusted estimate.'
                          if slug.startswith('esketamine') else
                          'Existing published primary-composite HR matches the held abstract; preserve source HR rather than substituting a count-derived RR.'))
    # The base still carries the superseded outcome labels for these same inputs.
    # Replace those rows, rather than retaining stale audit entries.
    audit = [a for a in audit if not (a['topic']==slug and a['file']==filename
                                    and str(a['trial'])==pid
                                    and a['outcome'] != 'Lower-limb amputation')] + [row]
write(audit_path, audit)
print('Wrote 50 individually adjudicated harm inputs and 53 audit rows.')
