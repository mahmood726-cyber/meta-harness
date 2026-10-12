"""Isolated transcription of two inspected target_endpoint.py functions.
Source ref: 0730234d0b4f, blob f5ccfb00a5109ffbb0ba8ed71293df69f20ca55e.
Comments/docstrings shortened; executable function logic transcribed unchanged.
NOT a complete selector, production extractor, D5 matcher, or publication-path test.
"""
import re

def _fold(text):
    s=str(text or '').lower()
    replacements={'hospitalisation':'hospitalization','hospitalisations':'hospitalizations',
                  'cardiovascular':'cardiovascular','cv ':'cardiovascular ',
                  'hhf':'heart failure hospitalization','e-gfr':'egfr'}
    for old,new in replacements.items():s=s.replace(old,new)
    s=re.sub(r'\bteaes?\b','treatment-emergent adverse events',s)
    s=re.sub(r'\bsaes?\b','serious adverse events',s)
    s=re.sub(r'\baes?\b','adverse events',s)
    return re.sub(r'\s+',' ',s)

def _components_from_text(text,expand_named_composites=True):
    s=_fold(text);comps=set()
    if ('coronary heart disease death' in s or 'death from coronary heart disease' in s
        or re.search(r'\bchd\b.{0,30}death|death.{0,30}\bchd\b',s)):
        comps.add('coronary heart disease death')
    s_cv=re.sub(r'\bnon-?\s?cardiovascular\b','noncv',s)
    if ('cardiovascular death' in s_cv or 'death from cardiovascular' in s_cv
        or 'cardiovascular causes' in s_cv
        or re.search(r'cardiovascular(?:(?!\b(?:or|and)\b|[,;]).){0,30}death|death(?:(?!\b(?:or|and)\b|[,;]).){0,30}cardiovascular',s_cv)
        or re.search(r'\bcv\b.*death|death.*\bcv\b',s_cv)
        or re.search(r'(?<!cerebro)(?<!cardio)(?<!non-)(?<!non)\bvascular death|(?<!non-)death from vascular causes',s)):
        comps.add('cardiovascular death')
    if 'transient ischemic attack' in s or 'transient ischaemic attack' in s or re.search(r'\btia\b',s):
        comps.add('transient ischemic attack')
    if (('heart failure' in s and 'hospitalization' in s)
        or 'hospitalizations due to heart failure' in s
        or (re.search(r'\bhf\b',s) and re.search(r'hospitali[sz]',s))
        or (re.search(r'\bhospitali[sz]ed\s+(?:for|because of|due to)\s+(?:acute\s+|worsening\s+)?(?:heart failure|hf)\b',s)
            and (re.search(r'\b(?:were|was|been|being|be)\s+(?:re)?hospitali[sz]ed\b',s)
                 or re.search(r'hazard ratio|odds ratio|risk ratio|\b(?:hr|rr|or)\b|%|\bvs\b|versus',s))
            and not re.search(r'\b(?:eligib|enrol|inclusion|recruit)',s))):
        comps.add('heart failure hospitalization')
    if re.search(r'(?<!non-)(?<!non)\bfatal\b.{0,25}\b(?:hf|heart failure)\b|death from heart failure|heart failure death',s):
        comps.add('heart failure death')
    if 'urgent visit' in s and ('heart failure' in s or re.search(r'\bhf\b',s)):
        comps.add('urgent heart failure visit')
    if ('recurrent' in s and ('hospitalization' in s or 'event' in s)
        and ('rate of recurrent' in s or 'recurrent event rate' in s or 'total recurrent' in s
             or 'first and recurrent' in s
             or re.search(r'analy[sz]ed as (?:a )?recurrent event|recurrent[- ]event analysis',s))):
        comps.add('recurrent events')
    if 'myocardial infarction' in s or re.search(r'\bmi\b',s):comps.add('myocardial infarction')
    if 'stroke' in s:comps.add('stroke')
    if 'unstable angina' in s:comps.add('unstable angina')
    if 'coronary revascularization' in s or 'revascularisation' in s:comps.add('coronary revascularization')
    if 'kidney failure' in s:comps.add('kidney failure')
    if 'kidney composite' in s or 'renal composite' in s or 'composite kidney outcome' in s:
        comps.update({'kidney failure','sustained egfr decline','renal death'})
    if 'egfr' in s and any(w in s for w in ('decline','decrease','reduction')):comps.add('sustained egfr decline')
    if 'renal death' in s or 'death from renal' in s:comps.add('renal death')
    if expand_named_composites and ('mace' in s or 'major adverse cardiovascular' in s or 'major cardiovascular' in s):
        if not comps or '3-point' in s or 'three-point' in s:
            comps.update({'cardiovascular death','myocardial infarction','stroke'})
        if '4-point' in s or 'four-point' in s:comps.add('unstable angina')
    return comps

def tests():
    canonical={'cardiovascular death','myocardial infarction','stroke'}
    fixtures={
        'alpha_omega_displayed_definition':"The primary end point was the rate of major cardiovascular events, which comprised fatal and nonfatal cardiovascular events and cardiac interventions.",
        'synthetic_explicit_three_point':'Major cardiovascular events comprised cardiovascular death, myocardial infarction and stroke.',
        'synthetic_extra_cardiac_interventions':'Major cardiovascular events comprised cardiovascular death, myocardial infarction, stroke and cardiac interventions.',
        'synthetic_extra_named_revascularization':'Major cardiovascular events comprised cardiovascular death, myocardial infarction, stroke and coronary revascularization.',
        'hypertension_label_from_cached_D5':'Cardio-vascular: Incident Hypertension',
    }
    outputs={k:{'expanded':sorted(_components_from_text(v)),
                'without_named_expansion':sorted(_components_from_text(v,False))} for k,v in fixtures.items()}
    checks={
        'Alpha Omega becomes canonical three-point':set(outputs['alpha_omega_displayed_definition']['expanded'])==canonical,
        'Alpha Omega has no parsed components without named expansion':outputs['alpha_omega_displayed_definition']['without_named_expansion']==[],
        'Positive three-point control':set(outputs['synthetic_explicit_three_point']['expanded'])==canonical,
        'Unrecognised extra cardiac interventions are dropped':set(outputs['synthetic_extra_cardiac_interventions']['expanded'])==canonical,
        'Explicit revascularization extra is retained':set(outputs['synthetic_extra_named_revascularization']['expanded'])==canonical|{'coronary revascularization'},
        'Hypertension has no cardiovascular composite components':outputs['hypertension_label_from_cached_D5']['expanded']==[],
    }
    if not all(checks.values()):raise AssertionError(checks)
    return {'scope':'Isolated component-recognition functions only; no D5 callback or admission pipeline executed.',
            'fixtures':fixtures,'outputs':outputs,'checks':checks}
