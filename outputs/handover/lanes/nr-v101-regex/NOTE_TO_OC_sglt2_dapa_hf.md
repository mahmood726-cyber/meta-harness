# Note to lane oc: stale DAPA-HF compatibility narrative (sglt2-hfref-hosp-cvdeath)

From lane NR, 2026-09-28, relaying the SGLT2-HFrEF review. **Keep the input; fix the narrative.**

## What the page pools (correct, unchanged)
- **DAPA-HF (PMID 31535829):** the registry's first-event composite, a secondary outcome.
  - ClinicalTrials.gov NCT03036124, 'Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due to
    Heart Failure'.
  - Hazard Ratio 0.75 (95% CI 0.65 to 0.85), Regression, Cox.
- **The row's own components:** `['cardiovascular death', 'heart failure hospitalization']`.

## What the narrative still says (stale)
- **`docs/definition_audit.json`:** the DAPA-HF entry feeds the page's compatibility dimension
  `compat_dimensions.endpoint_definition` (`source: docs/definition_audit.json`). It reads:
  > DISCLOSED (composite-component difference ...): DAPA-HF (31535829) defines its primary as worsening heart failure —
  > HF HOSPITALISATION or an URGENT HF VISIT requiring IV therapy — or cardiovascular death ... The urgent-visit
  > component is a minor broadening in DAPA-HF; disclosed, still poolable.

  That describes DAPA-HF's broader PRIMARY. The pooled input is not that primary: it is the CV death / HF
  hospitalisation first-event secondary, so there is no urgent-visit broadening in what is pooled.
- **`topics/sglt2-hfref-hosp-cvdeath.json`:** `primary_outcome.trial_annotations["31535829"].components` still lists
  `urgent visit requiring intravenous therapy for heart failure`. It is not applied to the row, because the row carries
  its own components, but it is the same stale description.

## Suggested fix (yours to make)
- **Definition audit:** restate the DAPA-HF entry as what is pooled. The first-event CV death/HHF secondary (HR 0.75,
  0.65 to 0.85, Cox) is the same component set as EMPEROR-Reduced and the outcome label. DAPA-HF's broader primary (with
  urgent HF visits, HR 0.74) stays an endpoint-sensitivity alternative, not pooled.
- **Topic annotation:** align the annotation's components with the pooled result.
- **Nothing numeric changes.**

## Related (lane NR, same review)
DAPA-HF's registry also holds the TOTAL-event result:
- 'Events Included in the Composite Endpoint of Recurrent Hospitalizations Due to Heart Failure and CV Death'.
- 567 vs 742 events, Rate Ratio 0.75 (0.65 to 0.88), LWYY proportional rates model.

It has the same point estimate and the same components as the pooled first-event result. The live page listed it as an
EXACT_TARGET alternative. Lane NR's endpoint module now refuses it as `EVENT_PROCESS_MISMATCH`. It is planted in
`tests/test_nr_v101_event_process.py`, and the refusal also holds without the word 'recurrent', from the registry's
'Events Included in' label and the rate model.
