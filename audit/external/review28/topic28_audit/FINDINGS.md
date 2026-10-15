# Findings

Audited identity: omega3-cardiovascular-events @ 0730234d0b4f,
review_sha256 4e2bd3f4f704c2cfa3a0ae658f2b92f054edf4b4a8a700c5c905e91c6a375b6a.

## Numerical result

The six selected HRs (1.05, 0.92, 0.74, 1.01, 1.08, 1.00) and their intervals
are supported at published precision. Independent PM/HKSJ reconstruction is
0.9386057929 [0.8025867855, 1.0976767252], with tau2 0.0129153281 and
I2 74.075371%. All six displayed passage hashes match. This validates the
calculation conditional on those inputs, not endpoint harmonisation or completeness.

## 28-01 — false exact-target certification of a broader endpoint

Alpha Omega's selected definition includes cardiac interventions, but the page
labels it EXACT_TARGET with only cardiovascular death, MI and stroke components.
The inspected component parser recognises none of the definition's specific
components without named-composite expansion and expands its generic term to
three-point MACE. A synthetic explicitly named revascularization control retains
that extra component, while cardiac interventions are lost. The complete selector
and publication path were not executed.

Broader outcome definitions were already disclosed on the page; the new finding
is not that disclosure is absent. It is that a broader endpoint receives a false
exact-match state while narrower requirements exclude other trials (e.g. ASCEND).
Current STRENGTH and REDUCE-IT selections are their three-point secondary outcomes,
although older notices still describe their five-point primaries. Fix policy and
bindings rather than adding or removing studies based on effect direction.
Severity: changes served wording/endpoint metadata. No primary numerical correction
is established by this audit.

## 28-02 — hypertension is not MACE

Cached DO-HEALTH D5 input and output identify `Cardio-vascular: Incident Hypertension`
as a matched prespecified secondary outcome for `Major vascular events / MACE`.
Its registered description is empty; this is not a broader title hiding a MACE
definition. The original publication separates exploratory MACE from secondary
incident hypertension. The numerical HR 1.00 belongs to MACE and remains supported.
Do not automatically impose a formal high-risk judgement; correct the evidence
used in the partial machine signal. No D5 production callback was executed here.
Severity: changes served wording/assessment evidence.

## 28-03 — AF reporting misclassified as absent

The page's GISSI-HF companion-report row PMID23839902 labels AF unreported in the
source. Its original abstract explicitly reports incident AF, 444 versus 408 events,
and unadjusted hazard 1.10 with p=0.19, in participants without AF at entry. The
abstract does not supply a two-sided CI or exact per-arm eligible denominators.
It therefore establishes reporting, NOT immediate extractability. It describes a
post-hoc analysis, and its parent-family linkage/admissibility must be adjudicated.
Severity: changes served wording/source-status record, no automatic new safety pool.

## STRENGTH safety recovery (not a false abstract-refusal claim)

The cached ft_33190147.txt explicitly warns full article XML is unavailable, and
contains no body element. It is a partial document, not the complete Results or
Table 2/5. Its abstract's silence does not establish silence of the publication.
The original publisher HTML reports investigator-reported new-onset AF HR1.69
[1.29,2.21] with 144 versus 86 events, and separate bleeding outcomes in safety
populations of 6532/6535. The bundle computes RR diagnostics for any bleeding
322/6532 versus 322/6535 and TIMI major bleeding 52/6532 versus 46/6535.
None is admitted, and no percentages are converted into guessed event counts.
Source acquisition/licensing, endpoint definition, follow-up, analysis set, and
incident AF versus hospitalised AF/flutter require explicit binding.

## Seeded screening sample

Positions 17,21,35,54,59 in the manual 114-ID transcription:
- 23351824: inclusion defensible as GISSI-HF biomarker/companion report, not an
  independent randomised trial or an observational plasma-level mortality HR to pool.
- 21145429: adult-review exclusion supported; ovine experimental study, not human RCT.
- 39059357: X1 exclusion supported; diabetes perspective/review.
- 34468792: do not count whole conference abstract collection as one trial. No
  claim that every constituent conference abstract was inspected or irrelevant.
- 32745277: same collection-level qualification for HF conference proceedings.

## Boundaries

Known missing studies and the existing model-adjudicator disagreement about
PISCES's fish-oil title were not claimed as new discoveries. No G1 predicates
were run; the topic remains abandoned. The registered comparator's total trial
count is not a verified MACE-specific comparator census. No scientific claim
about class-wide clinical benefit or absence of harm follows from this audit.
