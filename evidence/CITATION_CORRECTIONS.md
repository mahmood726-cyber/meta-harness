# Citation corrections queued (served-page metadata; not landed)

The served row's `compat_dimensions.endpoint_definition.span` cites a DIFFERENT endpoint than the served outcome. No served number changes; the page text would. Found by the evidence lane by eye (2026-09-24) and independently by lane WS (6 of 6 agreement).

- **UA-009** (All-cause mortality): the served citation reads "or placebo (n = 59) for 5 days started within 36 hours of hospital admission. MAIN OUTCOMES AND MEASURES: The primary outcome was treatment failure (composite outcome of ..."; the lane's bound endpoint span: "In-hospital mortality was a secondary outcome and adverse events were assessed."
- **UA-010** (Hyperglycaemia): the served citation reads "or placebo (n = 59) for 5 days started within 36 hours of hospital admission. MAIN OUTCOMES AND MEASURES: The primary outcome was treatment failure (composite outcome of ..."; the lane's bound endpoint span: "Hyperglycemia occurred in 11 patients (18%) in the methylprednisolone group and in 7 patients (12%) in the placebo group (P = .34)."
- **UA-030** (Atrial fibrillation): the served citation reads "1-g capsules containing either n-3 fatty acids (fatty acid group) or matching placebo (olive oil) daily. The primary outcome was a first serious vascular event (i.e., non..."; the lane's bound endpoint span: "RESULT OUTCOME 22 [OTHER_PRE_SPECIFIED]: Number of Participants With Event: Atrial Fibrillation (Omega-3 Comparison Only) | DESCRIPTION: Includes fata"
- **UA-042** (All-cause mortality): the served citation reads "EF ≤35% received eplerenone (n=111) or placebo (n=110) on top of standard therapy for at least 12 months. The primary endpoint was a composite of death from cardiovascula..."; the lane's bound endpoint span: "RESULT OUTCOME 2 [SECONDARY]: Number of Participants With With First Occurrence of All-Cause Mortality"
- **UA-044** (Serious adverse events): the served citation reads "of the participants received a second dose of tocilizumab or placebo 8 to 24 hours after the first dose. The primary outcome was clinical status at day 28 on an ordinal s..."; the lane's bound endpoint span: "In the safety population, serious adverse events occurred"
- **UA-045** (Serious adverse events): the served citation reads "acebo. Site selection was focused on the inclusion of sites enrolling high-risk and minority populations. The primary outcome was mechanical ventilation or death by day 2..."; the lane's bound endpoint span: "In the safety population, serious adverse events occurred in 38 of 250 patients (15.2%) in the tocilizumab group and 25 of 127 patients (19.7%) in the"

- UA-039: the served note says DAPA-HF's primary includes urgent HF visits; true, but the served number is the registry's exact CV-death-or-HHF analysis (UA-039 adjudication), so the disclosure is stale for this row.

- **S16-14** (EMPA-KIDNEY, Lower-limb amputation): the served endpoint citation is the trial's primary kidney/CV composite, not amputation. Eye label committed before a blind codex verdict (agree 16 of 16 on S16); lane WS flagged the same row.

### M rows (15; lane eye labels, no blind second opinion: codex budget exhausted) -- queued, not landed
Field: compat_dimensions.endpoint_definition. Wrong endpoint cited, 5 of 15:
- **M-01** LoDoCo2, Non-cardiovascular death: cites the primary MACE composite.
- **M-06** RE-COVER, Major bleeding: cites the primary outcome (recurrent VTE and related deaths).
- **M-11** RE-COVER, Any bleeding: cites the same primary VTE outcome.
- **M-13** ARISTOTLE, Major bleeding: cites the primary stroke/systemic-embolism outcome.
- **M-14** CANVAS Program, Lower-limb amputation: cites the primary CV composite.
Served value wrong, span right, 2 of 15: **M-03** FREEDOM nonvertebral fracture and **M-04** FREEDOM hip fracture. The value reads 'primary end point was new vertebral fracture'; the same span says 'Secondary end points included nonvertebral and hip fractures'.
