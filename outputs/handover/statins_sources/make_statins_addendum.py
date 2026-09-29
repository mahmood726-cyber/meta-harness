"""Statins-older-adults ADDENDUM (fuller review), 2026-09-28 -- what remains a RECORDED DECISION after the harness derives
the rest ("fix all in harness", Mahmood):
  * DERIVED by harness code, nothing declared here:
      - each pooled input's component set (harness/component_typing.py, from its held definition sentence);
      - PREVENTABLE's eligibility: a condition label its own registry criteria list only under EXCLUSION never vetoes,
        and its population is read from its INCLUSION criteria (harness/registry_criteria.py);
      - ALLHAT-LLT's report family (harness/report_linkage.py), subgroup provenance (harness/subgroup_provenance.py),
        the RMST measure guard (harness/measure_guard.py), NO_RESULT_YET and the search-completeness label.
  * RECORDED here (a human decision, or a value with no held text to derive it from):
      - the endpoint POLICY for 'major vascular events' (TRIAL_DEFINED_BROAD_COMPOSITE, as the protocol already applied);
      - HOPE-3 >= 70 as a PENDING input: its 3-point component set is RELAYED (Ridker 2017 not held), state
        DECISION_REQUIRED_BEFORE_INTERVAL, with the relayed diagnostic recorded as already seen.
  PYTHONPATH=. python outputs/handover/statins_sources/make_statins_addendum.py"""
import hashlib, json, os, re

SLUG = "statins-primary-prevention-elderly"
H = "evidence/acquisition_cascade/held"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}
MVE = "Major vascular events"


def dump(path, data):
    ind = 1
    if os.path.exists(path):
        m = re.match(r"[\[{]\n( +)", open(path, encoding="utf-8").read())
        ind = len(m.group(1)) if m else 1
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")


R_REC = f"{H}/Ridker-2017-JUPITER-HOPE3-older/europepmc_record_28385949.json"
R_TITLE = ("Primary Prevention With Statin Therapy in the Elderly: New Meta-Analyses From the Contemporary JUPITER and "
           "HOPE-3 Randomized Trials.")
assert R_TITLE in open(R_REC, encoding="utf-8").read()
ep = "docs/endpoint_policies.json"
epd = json.load(open(ep, encoding="utf-8")) if os.path.exists(ep) else {
    "_doc": ("Endpoint policies (harness/endpoint_policy.py): the RECORDED policy per outcome and any PENDING input whose "
             "component set no held text types. Every pooled input's component set is DERIVED (harness/component_typing.py). "
             "A pending input needs a recorded decision before the interval of any pool containing it is computed or "
             "inspected; a pooled row the policy does not admit is blocking."),
    "topics": {}}
epd["topics"].setdefault(SLUG, {})[MVE] = {
    "policy": {"id": "TRIAL_DEFINED_BROAD_COMPOSITE",
               "statement": ("each trial's OWN prespecified major-cardiovascular-event composite is the input; component "
                             "sets differ between trials and are typed per input from their definition sentences"),
               "decided_by": "the topic protocol (outcome 'major vascular events', evidence units named in the question)",
               "basis": "the rule the two retained inputs were admitted under; recorded here, not changed"},
    "pending": [{
        "input": "NCT00468923", "label": "HOPE-3 (>= 70)",
        "component_set": ["cardiovascular death", "nonfatal myocardial infarction", "nonfatal stroke"],
        "component_basis": "RELAYED (Ridker 2017, PMID 28385949, a letter that is not held): no held text to derive it from",
        "mismatch": ("a 3-POINT outcome: no revascularisation and no unstable-angina hospitalisation, while both retained "
                     "inputs are broader trial-defined composites"),
        "state": "DECISION_REQUIRED_BEFORE_INTERVAL",
        "decision_options": ["keep TRIAL_DEFINED_BROAD_COMPOSITE (HOPE-3 >= 70 not admitted)",
                             "adopt a typed-component policy that admits narrower composites, disclosed per input",
                             "re-express every input as 3-point MACE where each trial reports it"],
        "decision_rule": ("the decision is recorded (who, when, which option, why) BEFORE the interval of any pool containing "
                          "HOPE-3 is computed for use or inspected; it is never chosen by whether that interval excludes 1"),
        "diagnostic_already_seen": {
            "note": ("a 3-input DIAGNOSTIC was relayed on 2026-09-28, before any policy decision; recorded so the decision's "
                     "timing relative to it stays auditable -- it is not a served result"),
            "estimate": 0.7101, "ci": [0.5148, 0.9795], "tau2": 0.004755, "i2_percent": 20.4, "pi": [0.4585, 1.0999]},
        "witness_of_report": W(R_REC, R_TITLE)}]}
dump(ep, epd)
print("statins addendum written")
