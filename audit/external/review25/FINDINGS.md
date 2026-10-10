# Findings

## 25-01 — Wrong endpoint / randomized-factor verification
Severity: changes served wording and risk-of-bias metadata, not a demonstrated
change to the currently pooled efficacy inputs.

CLEAR's selected colchicine HR is 0.99 (0.85–1.16), for CV death, recurrent MI,
stroke and unplanned ischemia-driven revascularization. The D5 cache instead
matches a spironolactone co-primary endpoint containing new/worsening HF and not
revascularization. The cached description explicitly says 'spironolactone
comparison'. COLCOT similarly matches a secondary endpoint omitting the urgent
angina/revascularization component instead of its selected primary endpoint.

Both cached D5 objects pass the generic string 'Major adverse cardiovascular
events' to the matcher. The transcribed component parser assumes three-point MACE
for that generic label; it does not recognize unqualified new/worsening HF or
resuscitated arrest as additional components. This yields the demonstrated wrong
matches. Passing the actual selected endpoint text distinguishes the particular
pairs tested, but is not a comprehensive fix for every unrecognized component.

Repair: bind D5 to the selected row's exact endpoint and randomized factor; treat
unknown components and missing contrast linkage as unresolved, not exact identity.
Do not replace the supported primary HRs with a different trial endpoint.

## 25-02 — Safety evidence states reuse efficacy data
Severity: changes served wording and safety evidence-status metadata.

COPS's current harm rows receive the primary-efficacy extraction-debt tuple
24/396 versus 38/399 rather than outcome-specific information. The non-CV death
row is presented as not reported, although the original abstract explicitly
reports 5 versus 0. GI symptoms are also described separately (percentages).
The correct evidence state is reported but unresolved/not yet admitted, not
unreported. No zero-cell HR or binomial safety meta-analysis has been generated.

LoDoCo2's reported non-CV-death HR 1.51 (0.99–2.31) remains numerically supported;
its compatibility definition must not describe the cardiovascular primary
composite. None of this authorizes restoring a class-level safety conclusion.

## 25-03 — DRC-04 false no-contrast exclusion
Severity: changes served screening reason and reconciliation of evidence states;
no demonstrated change to current primary k or estimate.

Record-level exclusion says colchicine appears in every arm. The family table
lists colchicine 0.5 mg, colchicine 0.25 mg and placebo and marks the family
eligible. Original UMIN000029170 independently identifies three randomized,
double-blind arms in adults with type 2 diabetes and coronary artery disease.
The placebo arm directly contradicts the background-only reason. Its primary
outcome is an inflammatory biomarker, so eligibility does not create a clinical
cardiovascular-event HR. No production contrast parser was run for this finding.

## Findings deliberately not asserted

* No numerical error demonstrated in COLCOT, LoDoCo2 or CLEAR primary inputs.
* Heterogeneous trial-defined composites and LoDoCo2's tolerance run-in are
  already disclosed; they are not newly discovered hidden scope violations.
* Missing COPS/other primary-outcome data are already acknowledged. The newly
  demonstrated problem is outcome-specific status/verification, not discovering
  COPS for the first time.
* Two registrations associated with COLCHICINE-PCI are not automatically two
  independent trials; this audit makes no denominator correction based on them.
* No automatic 'high risk' RoB conclusion or G1 status change is asserted.
