"""Independent numerical reconstruction from explicitly transcribed pinned-page inputs.
Not a repository replay or an end-to-end gate test. Requires numpy and scipy.
"""
import hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm, t, chi2
ROOT = Path(__file__).resolve().parent
rows = [
 {"trial":"STEP 3", "pmid":"33625476", "effect":-10.3, "lower":-12.0, "upper":-8.6,
  "passage":"abstract reported mean difference + CI: At week 68, the estimated mean body weight change from baseline was -16.0% for semaglutide vs -5.7% for placebo (difference, -10.3 percentage points [95% CI, -12.0 to -8.6]; P\u2009<\u2009.001).",
  "expected_sha256":"f6c097da3295fe70911542a4f27fa37dd0a441c0d64e1f8dee55b852f34be123"},
 {"trial":"STEP 1", "pmid":"33567185", "effect":-12.4, "lower":-13.4, "upper":-11.5,
  "passage":"abstract reported mean difference + CI: RESULTS: The mean change in body weight from baseline to week 68 was -14.9% in the semaglutide group as compared with -2.4% with placebo, for an estimated treatment difference of -12.4 percentage poin",
  "expected_sha256":"70324c29fd7d8ac10f9f67e9e23212d7dacff616ce25943ed8288b6e5aa8c0bc"}
]

def pool(rows, z=float(norm.ppf(.975))):
    y=np.array([r['effect'] for r in rows],float)
    v=np.array([((r['upper']-r['lower'])/(2*z))**2 for r in rows])
    k=len(y);df=k-1
    def vals(tau2):
        w=1/(v+tau2);m=np.sum(w*y)/np.sum(w)
        q=np.sum(w*(y-m)**2)
        return w,m,q
    w0,m0,q0=vals(0)
    high=1.
    while vals(high)[2]>df:high*=2
    tau2=0. if q0<=df else brentq(lambda x:vals(x)[2]-df,0,high,xtol=1e-14)
    w,m,q=vals(tau2)
    se=math.sqrt(max(1.,q/df)/sum(w))
    margin=t.ppf(.975,df)*se
    return {'k':k,'inputs':[{k:v for k,v in r.items() if k in ('trial','pmid','effect','lower','upper')} for r in rows],
       'z_for_SE_reconstruction':z,'sampling_variances':v.tolist(),'sampling_SE':np.sqrt(v).tolist(),
       'tau2':float(tau2),'Q':float(q0),'Q_p':float(chi2.sf(q0,df)),
       'I2_percent':float(max(0,(q0-df)/q0)*100),'PM_estimate':float(m),
       'HKSJ_95CI_diagnostic_only':[float(m-margin),float(m+margin)],
       'HKSJ_SE':float(se),'random_effect_weights_percent':(100*w/sum(w)).tolist(),
       'common_effect':float(m0),'common_effect_95CI':[float(m0-z/math.sqrt(sum(w0))),float(m0+z/math.sqrt(sum(w0)))]}
res={'identity':{'ref':'0730234d0b4f','slug':'semaglutide-obesity-weight','review_sha256_claimed':'f4438abd8845e86c345fee8631b94629c278f781990d9750fdfe1d8e38ca50a2'},
     'source_input_basis':'Manual transcription from the user audit pack and pinned page. Passage strings copied from the supplied audit pack, HTML entities decoded.',
     'primary_reconstruction':pool(rows),
     'rounded_1_96_quantile_sensitivity':pool(rows,1.96),
     'hash_checks':[{'pmid':r['pmid'],'computed':hashlib.sha256(r['passage'].encode()).hexdigest(),'expected':r['expected_sha256'],'match':hashlib.sha256(r['passage'].encode()).hexdigest()==r['expected_sha256']} for r in rows],
     'scope_limits':['Not full offline replay','No canonical review or HTML hash recomputed','HKSJ interval is an auditor diagnostic, not a proposed replacement for a withheld interval']}
(ROOT/'inputs.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
(ROOT/'results.json').write_text(json.dumps(res,indent=2,ensure_ascii=False))
print(json.dumps(res,indent=2))

# Newly recovered original-table safety input, not an admitted harness result.
a, nt, c, nc = 337, 407, 129, 204
rr = (a/nt)/(c/nc)
se = math.sqrt(1/a-1/nt+1/c-1/nc)
z = float(norm.ppf(.975))
safety = {"trial":"STEP 3", "pmid":"33625476", "source":"https://jamanetwork.com/journals/jama/fullarticle/2777025",
          "location":"Table 3, Gastrointestinal disorders, participant columns",
          "participants_with_GI_event":[a,c], "group_denominators":[nt,nc],
          "total_event_counts_not_used":[1760,333],
          "auditor_derived_unadjusted_RR":rr,
          "auditor_derived_log_Wald_95CI":[math.exp(math.log(rr)-z*se),math.exp(math.log(rr)+z*se)],
          "caveat":"Not a served or admitted estimate. The source's safety observation period must be retained in any new extraction."}
(ROOT/'safety_recovery.json').write_text(json.dumps(safety,indent=2))
assert all(item['match'] for item in res['hash_checks'])
assert round(res['primary_reconstruction']['PM_estimate'],2) == -11.47
assert round(res['primary_reconstruction']['tau2'],5) == 1.71137
print(json.dumps(safety,indent=2))
