# Sources inspected

## Pinned repository sources

Base: https://github.com/mahmood726-cyber/meta-harness/blob/0730234d0b4f/

- `registry/g1_abandoned.json`: status.
- `topics/omega3-cardiovascular-events.json`: config, keywords, trial annotations.
- `docs/reviews/omega3-cardiovascular-events/index.html`: all six extracted inputs,
  hashes, rendered result, refusal/harms/assessment states and screening order.
- `docs/reviews/omega3-cardiovascular-events/CERTIFICATE.json`: recorded identity.
- `cache/omega3-cardiovascular-events/rob2.json`, lines950–1250: actual DO-HEALTH
  registered-outcome input and false hypertension matching record.
- `harness/target_endpoint.py`, component parser and folding functions:
  blob f5ccfb00a5109ffbb0ba8ed71293df69f20ca55e; excerpt test source.
- `harness/rob2.py`: inspected partial-machine-assessment matching machinery;
  complete caller/callback was NOT executed.
- `cache/omega3-cardiovascular-events/ft_33190147.txt`: partial cached XML,
  publisher restriction notice and absence of body element.
- `docs/reviews/omega3-cardiovascular-events/review.json`: fetch attempted but
  returned empty content; not read as the canonical numerical object.

## Original publications

- STRENGTH, DOI10.1001/jama.2020.22258, PMID33190147:
  https://jamanetwork.com/journals/jama/fullarticle/2773120
  Original Table2 three-point secondary HR1.05 [0.93,1.19]; tertiary AF HR1.69
  [1.29,2.21], 144 versus86, investigator-reported. Table5 safety populations and
  bleeding counts. HTML text inspected, not PDF or image-table inspection.
- VITAL, PMID30415637, DOI10.1056/NEJMoa1811403:
  https://pubmed.ncbi.nlm.nih.gov/30415637/
  Abstract supports HR0.92 [0.80,1.06].
- REDUCE-IT, PMID30415628, DOI10.1056/NEJMoa1812792:
  https://pubmed.ncbi.nlm.nih.gov/30415628/
  Abstract supports key secondary three-point HR0.74 [0.65,0.83], distinct from
  five-point primary HR0.75. Hospitalised AF/flutter endpoint differs from incident AF.
- Alpha Omega, PMID20929341, DOI10.1056/NEJMoa1003603:
  https://pubmed.ncbi.nlm.nih.gov/20929341/
  https://www.nejm.org/doi/abs/10.1056/NEJMoa1003603
  Original abstract supports EPA-DHA marginal HR1.01 [0.87,1.17] and broad primary
  endpoint including cardiac interventions. Original HTML confirms PCI/CABG components.
- SU.FOL.OM3, PMID21115589, DOI10.1136/bmj.c6273:
  https://pubmed.ncbi.nlm.nih.gov/21115589/
  Original abstract confirms marginal omega3 HR1.08 [0.79,1.47], not B-vitamin result.
- DO-HEALTH, PMID38199870, DOI10.1016/j.jnha.2024.100037:
  https://pubmed.ncbi.nlm.nih.gov/38199870/
  Original abstract explicitly separates exploratory MACE from secondary incident
  hypertension and reports omega3 aHR1.00 [0.64,1.56].
- GISSI-HF AF companion, PMID23839902, DOI10.1093/eurjhf/hft103:
  https://pubmed.ncbi.nlm.nih.gov/23839902/
  Original abstract reports post-hoc incident-AF analysis; 444 versus408 events,
  unadjusted hazard1.10, p=.19. Not a printed two-sided CI or exact per-arm denominators.

## Seeded screening publications

- https://pubmed.ncbi.nlm.nih.gov/23351824/ — GISSI-HF biomarker substudy.
- https://pubmed.ncbi.nlm.nih.gov/21145429/ — ovine experiment.
- https://pubmed.ncbi.nlm.nih.gov/39059357/ — diabetes perspective/review.
- https://pubmed.ncbi.nlm.nih.gov/34468792/ — EASD conference abstract collection.
- https://pubmed.ncbi.nlm.nih.gov/32745277/ — HF conference abstract collection.

Some direct PubMed opens returned browser-check pages. Successful indexed original
PubMed records and original publisher HTML supplied the source checks; a blocked
open was not treated as source content. Third-party summaries were not relied upon
for the numerical/admissibility findings. No original journal full text, PDF or
font files are redistributed in this bundle.
