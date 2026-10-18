"""Closed vocabularies for the G1 "matched or explained" state (captain's design, DISPATCH 15 Oct; Mahmood's decision).

ONE module, imported by the tracker (scripts/g1_tracker.py writes trials[].g1_explanation), the validator and the
search-log fetcher (scripts/g1_search_log.py), so the three can never drift apart. Changing a vocabulary here is a
design change for the captain, not a fix.
"""

STATES = ("MATCHED", "DIVERGENT_NAMED", "NO_OPEN_SOURCE", "UNEXPLAINED")

# DIVERGENT_NAMED.reason_code -- closed (captain's list, verbatim).
REASON_CODES = ("POPULATION", "TIMEPOINT", "ESTIMAND", "ANALYSIS_SET", "INTERVENTION_DOSE_OR_REGIMEN", "COMPARATOR",
                "OUTCOME_DEFINITION", "DESIGN", "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS", "DECISION_EXCLUDED")

# NO_OPEN_SOURCE.searched[].step_reached: only STEPS are completed searches.
# Dispatch 18 Oct: technical blocks require explicit fresh unreachable records;
# unfinished assessment, new reports and pending decisions remain UNEXPLAINED.
STEPS = ("NOT_FOUND", "FOUND_NOT_OPEN", "OPEN_NO_OUTCOME", "OPEN_OUTCOME_NOT_BINDABLE")
ACCESS_OUTCOMES = ("BLOCKED_BOT_CHALLENGE", "BLOCKED_ACCOUNT", "BLOCKED_TERMS", "ERROR", "NOT_ATTEMPTED_PENDING_DECISION",
                   # 15 Oct, first live search log: 'ERROR' was being used for three different facts; each is now named.
                   "BLOCKED_JS_ONLY",          # the source's search renders only with JavaScript (WHO ICTRP): a gate
                   "OPEN_NOT_ASSESSED",        # an open copy EXISTS but nobody has assessed it for the outcome: a
                                               # defect we can act on, never an explanation
                   "NEW_REPORT_FOUND")         # a search found a report naming the trial that the lane does not hold:
                                               # a defect (new identity to follow up), never an explanation

# searched[].source -- closed.
SOURCES = (
    "PUBMED_EPMC_PMID",      # PubMed / Europe PMC by PMID: OA flag + licence
    "PUBMED_EPMC_TITLE",     # Europe PMC by title (and acronym): finds the report when no PMID is known
    "UNPAYWALL_DOI",         # Unpaywall by DOI
    "CTGOV_V2",              # ClinicalTrials.gov API v2, every known NCT
    "AACT",                  # the AACT snapshot, every known NCT
    "EUCTR",                 # EU CTR / EudraCT results (CTIS when the trial transitioned)
    "WHO_ICTRP",             # identifier discovery by title / acronym
    "FDA",                   # Drugs@FDA reviews + label for an approved drug
    "EMA",                   # EMA EPAR for an approved drug
    "PMDA", "TGA_AUSPAR", "FDA_ADCOMM", "AHRQ_NIHR_HTA", "SPONSOR_REGISTER",   # mandate sources, where applicable
    "HEALTH_CANADA", "EMA_CLINICAL_DATA",     # gated: pending Mahmood
)

FRESH_DAYS = 30          # a required search older than this does not count (captain: stops a thin, stale search passing)

# Dispatch 18 Oct: technical blocks are source availability, never searches.
SOURCE_UNREACHABLE = "SOURCE_UNREACHABLE"
UNREACHABLE_STEPS = ("BLOCKED_JS_ONLY", "BLOCKED_BOT_CHALLENGE", "BLOCKED_ACCOUNT", "BLOCKED_TERMS", "ERROR")
EVIDENCE_KINDS = ("RECORDED_READ", "REGISTRY_RECORD")
