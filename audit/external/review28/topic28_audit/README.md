# Topic 28 independent audit — omega-3 cardiovascular events

Date: 2026-10-10. Repository: mahmood726-cyber/meta-harness.
Pinned reference: `0730234d0b4f`.
Review hash: `4e2bd3f4f704c2cfa3a0ae658f2b92f054edf4b4a8a700c5c905e91c6a375b6a`.
Status: ABANDONED_BY_DECISION. This audit does not reinstate the topic.

## Execute

With Python 3.10 or newer, run:

```sh
python audit.py --output my_results.json
```

The delivered execution uses only the Python standard library. It recalculates
six-input inverse-variance log-HR meta-analysis, Paule–Mandel tau-squared,
floored HKSJ confidence intervals and the page's t(k-1) prediction convention;
it also recalculates all six displayed passage hashes and the seeded screening
sample from the manually transcribed displayed row order.

`target_excerpt.py` is a manually transcribed isolated component-recognition
function from the pinned repository, with original executable logic and shortened
comments. Its fixtures demonstrate loss of unrecognised components; they do NOT
exercise the complete source selector, admission route, D5 callback or page build.
In particular, the DO-HEALTH D5 finding is an inspection of stored source/endpoint
bindings, not a production-code replay.

`crosscheck.json` records a separate SciPy numerical implementation check run by
the auditor. SciPy is NOT needed for the delivered audit.py. Agreement of two
numerical implementations does not independently validate source data.

## Scope and limitations

All numerical inputs, passage strings and screening IDs were manually transcribed
from connector-returned pinned HTML; they were not parsed from full review.json.
All six numerical triplets were checked against original publications accessible
through indexed abstracts or original publisher HTML. Certificate identity was
read and compared, not canonically recomputed.

The full review JSON fetch returned empty content. The live page fetch failed;
raw-GitHub acquisition through the local Python environment failed DNS resolution.
No current-deployment byte equality is claimed. The relevant rendered sections,
code and cache records were read through the GitHub connector.

No complete repository replay, production gate test, actual endpoint admission,
formal RoB/GRADE assessment, live registry JSON validation, complete trial-family
census, systematic evidence search or G1 execution was performed. No repository or
website was modified. No PDF was analysed; tables were read from original HTML.

The STRENGTH source-recovery calculations are separate, unadmitted single-trial
RR diagnostics. They do not replace its reported AF HR, pool a safety outcome,
or override the incomplete-harms gate. No new AF HR/CI is inferred for GISSI-HF
from a p-value or rounded percentages. No broad-vs-narrow efficacy substitution
is authorised by this audit.

The screening sample uses seed `20261008:omega3-cardiovascular-events:screen` and
114 manually transcribed record IDs. It is a reconstruction of the sampling
procedure, not a direct parse of the missing canonical review object.

The 22 reported checks are computational/fixture checks, including deliberate
reproduction of a defect. They are not 22 independent scientific validations.
