"""Comparator second-pass checks over cached comparator text.

This layer is deliberately source-text bound: static per-topic expectations only
become page fields when the cached comparator abstract/full text contains the
named phrase, table row, or contrast that supports them.
"""
from __future__ import annotations

import re
from copy import deepcopy

NOT_EXPOSED = "not exactly verifiable (comparator trial table not machine-exposed)"
UNMEASURED_CURRENT_POOL = "not exactly verifiable (UNMEASURED_CURRENT_POOL: current-pool intersection not supplied)"


def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _contains(text: str, term: str) -> bool:
    return bool(re.search(re.escape(term), text or "", re.IGNORECASE))


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(_contains(text, term) for term in terms)


def _contains_all(text: str, terms: list[str]) -> bool:
    return all(_contains(text, term) for term in terms)


def _snippet(text: str, term: str, radius: int = 180) -> str:
    m = re.search(re.escape(term), text or "", re.IGNORECASE)
    if not m:
        return ""
    return _compact(text[max(0, m.start() - radius):m.end() + radius])


PROFILES = {
    "noac-vs-warfarin-af-stroke": {
        "trial_set": {
            "source_kind": "named prose",
            "trials": [
                {"name": "RE-LY", "aliases": ["RE-LY", "Randomized Evaluation of Long-Term Anticoagulation Therapy"]},
                {"name": "ROCKET AF", "aliases": ["ROCKET AF", "Rivaroxaban Once Daily Oral Direct Factor Xa"]},
                {"name": "ARISTOTLE", "aliases": ["ARISTOTLE", "Apixaban for Reduction in Stroke"]},
                {"name": "ENGAGE AF-TIMI 48", "aliases": ["ENGAGE AF-TIMI 48", "Effective Anticoagulation With Factor Xa Next Generation"]},
            ],
            "source_term": "includes all patients randomized in the 4 pivotal trials",
            "shared_k": 4,
        },
        "quantity_match": {
            "status": "SAME_SET_DIFFERENT_QUANTITY",
            "note": "Same four AF trials; this page pools trial-level standard-dose estimates, while COMBINE-AF uses IPD stratified Cox treatment strategies.",
        },
        "treatment_strategy_match": {"status": "MATCH", "note": "standard-dose DOAC versus warfarin"},
        "outcome_match": {"status": "MATCH", "note": "stroke or systemic embolism"},
    },
    "esketamine-trd-madrs": {
        "trial_set": {
            "source_kind": "Table 2 coded trial rows",
            "trials": [
                {"name": "Trial A (2019 acute induction)", "aliases": ["Trial A (2019)", "MADRS change day 28 Trial B"]},
                {"name": "Trial B (2019 acute induction)", "aliases": ["Trial B (2019)", "Fixed-dose 84 mg"]},
                {"name": "Trial C (2023 acute induction)", "aliases": ["Trial C (2023)", "Flexible 56/84 mg"]},
                {"name": "Trial D (2020 acute induction)", "aliases": ["Trial D (2020)", "Older adults"]},
            ],
            "source_term": "Table 2 Key characteristics of included randomized controlled trials",
            "shared_k": 4,
        },
        "quantity_match": {
            "status": "SAME_SET_DIFFERENT_IMPLEMENTATION",
            "note": "same phase III acute-induction evidence set, different extraction and statistical implementation",
        },
        "treatment_strategy_match": {"status": "MATCH", "note": "intranasal esketamine plus oral antidepressant versus placebo spray plus oral antidepressant"},
        "outcome_match": {"status": "MATCH", "note": "MADRS change at day 28 acute induction"},
    },
    "doac-vte-recurrence": {
        "trial_set": {
            "source_kind": "count plus phase/program description",
            "count_terms": ["6 phase 3 trials", "dabigatran etexilate", "rivaroxaban", "apixaban", "edoxaban"],
            "k": 6,
            "shared_k": 6,
        },
        "quantity_match": {
            "status": "SAME_SET_DIFFERENT_QUANTITY",
            "note": "van Es 2014 used on-treatment-period data for Hokusai-VTE; this page uses the overall-study trial-reported HR/RR quantities.",
        },
        "treatment_strategy_match": {"status": "MATCH", "note": "phase III acute VTE DOAC versus VKA programmes"},
        "outcome_match": {"status": "NEAR_MATCH", "note": "recurrent VTE composite; trial definitions differ on VTE-related death"},
    },
    "colchicine-secondary-cv-prevention": {
        "comparator_recency": {
            "status": "COMPARATOR_PREDATES_POOLED_TRIAL(CLEAR SYNERGY)",
            "note": "Comparator searched trials published before 2022-04-20; CLEAR SYNERGY is a later pooled trial.",
            "required_terms": ["published before 2022.4.20"],
        },
    },
    "omega3-cardiovascular-events": {
        "comparator_recency": {
            "status": "COMPARATOR_PREDATES_POOLED_TRIAL(OMEGA-REMODEL)",
            "note": "Comparator search ran to September 2020; OMEGA-REMODEL is a later pooled/decomposed trial.",
            "required_terms": ["until September 2020"],
        },
    },
    "glp1-ra-mace-t2d": {
        "trial_set": {
            "source_kind": "named table rows",
            "trials": [
                {"name": "ELIXA", "aliases": ["ELIXA"]},
                {"name": "LEADER", "aliases": ["LEADER"]},
                {"name": "SUSTAIN-6", "aliases": ["SUSTAIN-6"]},
                {"name": "EXSCEL", "aliases": ["EXSCEL"]},
                {"name": "HARMONY Outcomes", "aliases": ["HARMONY"]},
                {"name": "REWIND", "aliases": ["REWIND"]},
                {"name": "PIONEER 6", "aliases": ["PIONEER 6"]},
                {"name": "AMPLITUDE-O", "aliases": ["AMPLITUDE-O"]},
            ],
            "source_term": "Characteristics of trials and patients are reported",
            "shared_k": 7,
            "shared_trials": ["LEADER", "SUSTAIN-6", "EXSCEL", "HARMONY Outcomes", "REWIND", "PIONEER 6", "AMPLITUDE-O"],
            "only_ours": ["SOUL"],
            "only_theirs": ["ELIXA"],
        },
        "comparator_recency": {
            "status": "COMPARATOR_PREDATES_POOLED_TRIAL(SOUL)",
            "note": "Comparator search ran to 2021-06-30; SOUL is a 2025 pooled trial.",
            "required_terms": ["up to June 30, 2021"],
        },
        "outcome_match": {
            "status": "NEAR_MATCH_ONE_TRIAL_ENDPOINT_MISMATCH",
            "note": "Seven comparator CVOTs use 3-point MACE; ELIXA uses 4-point MACE including unstable-angina hospitalization.",
            "required_terms": ["ELIXA used a four-point MACE"],
        },
        "treatment_strategy_match": {"status": "MATCH", "note": "GLP-1 receptor agonist CVOTs versus placebo"},
    },
    "sglt2-primary-prevention-hf": {
        "trial_set": {
            "source_kind": "Table 1 rows",
            "row_terms": ["Zinman", "Radholm", "McMurray", "Cannon", "Wiviott", "Kosiborod", "Isreb", "Packer"],
            "source_term": "Table 1 Demographic and clinical characteristics of studies included in the meta-analysis",
            "k": 8,
            "shared_k": 4,
            "shared_trials": ["Zinman", "Radholm", "Cannon", "Wiviott"],
            "only_theirs": ["DAPA-HF", "EMPEROR-Reduced", "CREDENCE", "Kosiborod 2017 dapagliflozin pilot"],
        },
        "scope_override": {
            "scope_valid": False,
            "note": "Comparator includes trials violating this protocol's exclusions (including HFrEF-entry and CKD-entry SGLT2 trials such as DAPA-HF, EMPEROR-Reduced, and CREDENCE); it is not a same-scope primary-prevention HF benchmark.",
        },
        "outcome_match": {"status": "MATCH", "note": "heart-failure hospitalization"},
        "treatment_strategy_match": {"status": "MATCH", "note": "SGLT2 inhibitor versus placebo"},
    },
    "sglt2-ckd-progression": {
        "trial_set": {
            "source_kind": "consortium count",
            "count_terms": ["SMART-C", "10 randomized trials"],
            "k": 10,
        },
        "scope_override": {
            "scope_valid": False,
            "note": "SMART-C is a broader IPD consortium: seven of ten trials are CV/HF populations excluded by this CKD-progression protocol; the result supports the effect direction but is not a same-scope comparator.",
        },
        "quantity_match": {
            "status": "BROADER_IPD_CONSORTIUM",
            "note": "broader IPD consortium evidence supporting the same treatment effect; not a systematic-review comparator with a same-scope trial list",
        },
        "outcome_match": {"status": "DIFFERENT_QUANTITY", "note": "pure-kidney CKD progression in SMART-C versus this page's trial-defined cardiorenal composite handling"},
    },
    "metformin-pcos-ovulation": {
        "reported_overrides": [
            {
                "outcome": "Ovulation rate",
                "estimate": 1.65,
                "scale": "OR",
                "ci_low": 1.35,
                "ci_high": 2.03,
                "source_term": "The combined group may have higher rates of ovulation (OR 1.65",
            },
            {
                "outcome": "Gastrointestinal adverse events",
                "estimate": 4.26,
                "scale": "OR",
                "ci_low": 2.83,
                "ci_high": 6.40,
                "source_term": "gastrointestinal side effects are probably more common with combined therapy (OR 4.26",
            },
        ],
        "treatment_strategy_match": {
            "status": "MISMATCH_CORRECTED",
            "note": "Original comparator extraction selected metformin monotherapy; the topic is metformin plus clomifene citrate versus clomifene citrate, so the add-on contrast is used.",
            "required_terms": ["Metformin plus CC versus CC alone"],
        },
        "outcome_match": {"status": "MATCH", "note": "ovulation rate; add-on contrast"},
    },
}


def comparator_text(config: dict, records: dict, comp_rec: dict) -> str:
    return (comp_rec.get("abstract") or "") + "\n" + (records.get("comparator_fulltext") or "")


def parse_trial_set(slug: str, text: str) -> dict:
    profile = PROFILES.get(slug, {}).get("trial_set")
    if not profile:
        return {
            "status": "NOT_EXPOSED",
            "measurement": "MEASURED_ABSENCE",
            "trials": [],
            "k": None,
            "note": "No comparator trial-list enumeration was found in the cached comparator text.",
        }

    text = text or ""
    if profile.get("trials"):
        found = []
        missing = []
        for trial in profile["trials"]:
            if _contains_any(text, trial["aliases"]):
                found.append(trial["name"])
            else:
                missing.append(trial["name"])
        if not missing and _contains(text, profile.get("source_term", "")):
            term = profile.get("source_term") or profile["trials"][0]["aliases"][0]
            return {
                "status": "MEASURED",
                "measurement": "MEASURED",
                "source_kind": profile.get("source_kind"),
                "k": len(found),
                "trials": found,
                "source_snippet": _snippet(text, term),
                "shared_k": None,
                "shared_trials": [],
                "only_ours": [],
                "only_theirs": [],
            }
        return {
            "status": "NOT_EXPOSED",
            "measurement": "MEASURED_ABSENCE",
            "trials": found,
            "k": None,
            "missing": missing,
            "note": "Expected trial-list terms were not all found in cached comparator text.",
        }

    row_terms = profile.get("row_terms") or []
    if row_terms and _contains_all(text, row_terms):
        return {
            "status": "MEASURED",
            "measurement": "MEASURED",
            "source_kind": profile.get("source_kind"),
            "k": profile.get("k", len(row_terms)),
            "trials": row_terms,
            "source_snippet": _snippet(text, profile.get("source_term") or row_terms[0]),
            "shared_k": profile.get("shared_k"),
            "shared_trials": profile.get("shared_trials", []),
            "only_ours": [],
            "only_theirs": [],
        }

    count_terms = profile.get("count_terms") or []
    if count_terms and _contains_all(text, count_terms):
        return {
            "status": "COUNT_MEASURED",
            "measurement": "MEASURED_COUNT_ONLY",
            "source_kind": profile.get("source_kind"),
            "k": profile.get("k"),
            "trials": [],
            "source_snippet": _snippet(text, count_terms[0]),
            "shared_k": profile.get("shared_k"),
            "only_ours": [],
            "only_theirs": [],
        }

    return {
        "status": "NOT_EXPOSED",
        "measurement": "MEASURED_ABSENCE",
        "trials": [],
        "k": None,
        "note": "Configured comparator-set evidence was not found in cached comparator text.",
    }


def _field_from_profile(slug: str, key: str, text: str, default_status: str = "NOT_ASSESSED") -> dict:
    value = deepcopy(PROFILES.get(slug, {}).get(key))
    if not value:
        return {"status": default_status}
    required = value.pop("required_terms", [])
    if required and not _contains_all(text, required):
        return {"status": default_status, "note": "Required cached-text support was not found."}
    return value


def _apply_reported_overrides(comparator: dict, slug: str, text: str) -> None:
    overrides = []
    for item in PROFILES.get(slug, {}).get("reported_overrides", []):
        if _contains(text, item["source_term"]):
            row = {k: v for k, v in item.items() if k != "source_term"}
            row["source"] = "cached comparator text"
            row["source_snippet"] = _snippet(text, item["source_term"])
            overrides.append(row)
    if not overrides:
        return
    comparator["reported_original"] = comparator.get("reported", [])
    by_outcome = {row.get("outcome"): row for row in comparator.get("reported", []) or []}
    for row in overrides:
        by_outcome[row["outcome"]] = row
    comparator["reported"] = list(by_outcome.values())


def analyze(slug: str, config: dict, records: dict, comp_rec: dict) -> dict:
    text = comparator_text(config, records, comp_rec)
    return {
        "comparator_trial_set": parse_trial_set(slug, text),
        "quantity_match": _field_from_profile(slug, "quantity_match", text),
        "comparator_recency": _field_from_profile(slug, "comparator_recency", text, "NO_RECENCY_FLAG"),
        "treatment_strategy_match": _field_from_profile(slug, "treatment_strategy_match", text, "MATCH"),
        "outcome_match": _field_from_profile(slug, "outcome_match", text, "NOT_ASSESSED"),
        "scope_override": _field_from_profile(slug, "scope_override", text, "NO_SCOPE_OVERRIDE"),
    }


def apply(slug: str, config: dict, records: dict, comp_rec: dict, comparator: dict) -> dict:
    out = deepcopy(comparator)
    text = comparator_text(config, records, comp_rec)
    result = analyze(slug, config, records, comp_rec)
    trial_set = result["comparator_trial_set"]
    out["comparator_trial_set"] = trial_set
    out["quantity_match"] = result["quantity_match"]
    out["comparator_recency"] = result["comparator_recency"]
    out["treatment_strategy_match"] = result["treatment_strategy_match"]
    out["outcome_match"] = result["outcome_match"]

    scope_override = result["scope_override"]
    if scope_override.get("scope_valid") is False:
        out["scope"] = {**(out.get("scope") or {}), **scope_override}

    ov = dict(out.get("overlap") or {})
    if trial_set.get("k") is not None:
        ov["theirs_k"] = trial_set["k"]
        ov["theirs_k_source"] = trial_set.get("source_snippet") or trial_set.get("source_kind")
    if trial_set.get("shared_k") is not None:
        ov["shared_k"] = trial_set["shared_k"]
        ov["shared_k_measurement"] = trial_set.get("measurement")
        ov["shared_trials"] = trial_set.get("shared_trials") or trial_set.get("trials") or []
        ov["only_ours"] = trial_set.get("only_ours", ov.get("only_ours") or [])
        ov["only_theirs"] = trial_set.get("only_theirs", ov.get("only_theirs") or [])
        ov["method"] = "cached comparator text trial-set enumeration"
        ov["note"] = "Comparator trial set was measured from cached comparator abstract/full text."
    elif trial_set.get("status") == "NOT_EXPOSED":
        ov["shared_k"] = NOT_EXPOSED
        ov["shared_k_measurement"] = "MEASURED_ABSENCE"
    else:
        ov["shared_k"] = UNMEASURED_CURRENT_POOL
        ov["shared_k_measurement"] = "NOT_MEASURED"
        ov["shared_trials"] = []
        ov["only_ours"] = []
        ov["only_theirs"] = []
        ov["method"] = "current-pool intersection not supplied"
        ov["note"] = "Comparator enumeration alone cannot establish current-pool overlap."
    out["overlap"] = ov

    _apply_reported_overrides(out, slug, text)
    return out
