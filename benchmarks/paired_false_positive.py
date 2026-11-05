"""Fail-closed, deterministic measurement of *synthetic* paired benchmark controls.

Development utility only. Never opens publication content, benchmarks against
real people, certifies held-out custody, or supplies independent adjudication.
The caller supplies synthetic outcomes and a frozen fixture digest; verifying
a caller-supplied digest does not provide independent custody.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter

SCHEMA = "synthetic-paired-fp/v1"
MANIFEST_FIELDS = frozenset({
    "schema", "method_id", "method_version", "spec_sha256",
    "fixture_sha256", "truth_provenance",
})
ROW_FIELDS = frozenset({
    "case_id", "pair_id", "family_id", "split", "truth", "prediction",
    "severity", "root_cause", "abstention_reason",
})
IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
SPLITS = ("DEV", "HELD_OUT")
TRUTHS = ("ISSUE", "CLEAN")
PREDICTIONS = ("ISSUE", "CLEAN", "ABSTAIN")
ROOT_CAUSES = ("ARITHMETIC", "DENOMINATOR", "LABEL_SWITCH")
ABSTENTION_REASONS = ("LOW_CONFIDENCE", "INSUFFICIENT_EVIDENCE", "OUT_OF_SCOPE")


class BenchmarkRefusal(ValueError):
    """Invalid provenance, paired case, split or score input."""


def fixture_digest(rows: list[dict]) -> str:
    """Hash the exact ordered JSON fixture (a self-check, not external custody)."""
    try:
        raw = json.dumps(
            rows, sort_keys=True, ensure_ascii=False, allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise BenchmarkRefusal("fixture is not canonical JSON") from exc
    return hashlib.sha256(raw).hexdigest()


def _ratio(num: int, den: int) -> float | None:
    return num / den if den else None


def _score(rows: list[dict]) -> dict:
    c = Counter()
    severity_misses = Counter()
    cause_detected = Counter()
    cause_missed = Counter()
    # Keep abstention reasons separate from ordinary false positives / misses.
    # These are descriptive counts for validated synthetic truth labels only.
    reasons = {truth: Counter() for truth in TRUTHS}
    for row in rows:
        truth, decision = row["truth"], row["prediction"]
        if decision == "ABSTAIN":
            c["abstain_" + truth.lower()] += 1
            reasons[truth][row["abstention_reason"]] += 1
        elif truth == "ISSUE":
            c["tp" if decision == "ISSUE" else "fn"] += 1
        else:
            c["fp" if decision == "ISSUE" else "tn"] += 1
        if truth == "ISSUE":
            if decision == "ISSUE":
                cause_detected[row["root_cause"]] += 1
            else:
                cause_missed[row["root_cause"]] += 1
                severity_misses[row["severity"]] += 1
    for key in ("tp", "fp", "fn", "tn", "abstain_issue", "abstain_clean"):
        c.setdefault(key, 0)
    # Attribute false alarms on CLEAN controls to the planted issue in their
    # validated pair.  A clean row correctly has no intrinsic root cause;
    # treating it as root cause NONE would hide failure-mode-specific FPs.
    planted_by_pair = {
        row["pair_id"].casefold(): row for row in rows if row["truth"] == "ISSUE"
    }
    negative_strata = {"root_cause": {}, "severity": {}}
    for row in rows:
        if row["truth"] != "CLEAN":
            continue
        planted = planted_by_pair[row["pair_id"].casefold()]
        decision = {"ISSUE": "fp", "CLEAN": "tn", "ABSTAIN": "abstain"}[row["prediction"]]
        for dimension in negative_strata:
            key = planted[dimension]
            counts = negative_strata[dimension].setdefault(key, Counter())
            counts["cases"] += 1
            counts[decision] += 1

    # Positive controls must not hide abstentions inside a combined miss count.
    # These denominators describe planted synthetic ISSUE controls, not evidence
    # of effectiveness on external articles or human-adjudicated cases.
    positive_strata = {"root_cause": {}, "severity": {}}
    for row in rows:
        if row["truth"] != "ISSUE":
            continue
        decision = {"ISSUE": "tp", "CLEAN": "fn", "ABSTAIN": "abstain"}[row["prediction"]]
        for dimension in positive_strata:
            key = row[dimension]
            counts = positive_strata[dimension].setdefault(key, Counter())
            counts["cases"] += 1
            counts[decision] += 1

    # Count outcomes at the MATCHED-PAIR level. Marginal TP/TN counts can
    # misleadingly suggest discrimination even when no individual pair has
    # both its ISSUE and CLEAN versions correctly classified. Include all
    # nine joint decision states so abstention cannot silently disappear.
    decisions_by_pair = {}
    for row in rows:
        key = row["pair_id"].casefold()
        decisions_by_pair.setdefault(key, {})[row["truth"]] = row["prediction"]
    pair_matrix = {
        f"{issue}->{clean}": 0
        for issue in PREDICTIONS for clean in PREDICTIONS
    }
    for decisions in decisions_by_pair.values():
        pair_matrix[f"{decisions['ISSUE']}->{decisions['CLEAN']}"] += 1
    total_pairs = len(decisions_by_pair)
    decided_pairs = sum(
        count for outcome, count in pair_matrix.items()
        if "ABSTAIN" not in outcome
    )
    strict_successes = pair_matrix["ISSUE->CLEAN"]
    pair_discrimination = {
        "strict_successes": strict_successes,
        "decided_pairs": decided_pairs,
        "abstaining_pairs": total_pairs - decided_pairs,
        "pair_decision_coverage": _ratio(decided_pairs, total_pairs),
        "strict_success_rate_all_pairs": _ratio(strict_successes, total_pairs),
        "strict_success_rate_decided_pairs": _ratio(strict_successes, decided_pairs),
        "generalization_uncertainty_interval": None,
        "generalization_uncertainty_status": "NOT_MEASURED_SYNTHETIC_ONLY",
    }

    def report_positive_strata(dimension: str) -> dict:
        return {
            key: {
                "cases": counts["cases"],
                "tp": counts["tp"],
                "fn": counts["fn"],
                "abstain": counts["abstain"],
                "issue_decision_coverage": _ratio(
                    counts["tp"] + counts["fn"], counts["cases"]
                ),
                "recall_decided_issues": _ratio(
                    counts["tp"], counts["tp"] + counts["fn"]
                ),
                "recall_all_issues_abstentions_count_as_missed": _ratio(
                    counts["tp"], counts["cases"]
                ),
            }
            for key, counts in sorted(positive_strata[dimension].items())
        }

    def report_strata(dimension: str) -> dict:
        return {
            key: {
                "cases": counts["cases"],
                "fp": counts["fp"],
                "tn": counts["tn"],
                "abstain": counts["abstain"],
                "negative_decision_coverage": _ratio(
                    counts["fp"] + counts["tn"], counts["cases"]
                ),
                "fpr_decided_negatives": _ratio(
                    counts["fp"], counts["fp"] + counts["tn"]
                ),
            }
            for key, counts in sorted(negative_strata[dimension].items())
        }

    n = len(rows)
    decided = c["tp"] + c["fp"] + c["fn"] + c["tn"]
    neg = c["fp"] + c["tn"] + c["abstain_clean"]
    pos = c["tp"] + c["fn"] + c["abstain_issue"]
    return {
        "cases": n, "paired_controls": n // 2,
        "paired_outcome_matrix": pair_matrix,
        "paired_discrimination": pair_discrimination,
        "confusion_with_abstentions": dict(sorted(c.items())),
        "abstention_reasons_by_truth": {
            truth: dict(sorted(reasons[truth].items())) for truth in TRUTHS
        },
        "coverage": _ratio(decided, n),
        "precision_decided": _ratio(c["tp"], c["tp"] + c["fp"]),
        "fpr_decided_negatives": _ratio(c["fp"], c["fp"] + c["tn"]),
        "fp_yield_all_negatives": _ratio(c["fp"], neg),
        "negative_control_decision_coverage": _ratio(c["fp"] + c["tn"], neg),
        "negative_controls_by_planted_root_cause": report_strata("root_cause"),
        "negative_controls_by_planted_severity": report_strata("severity"),
        "positive_controls_by_planted_root_cause": report_positive_strata("root_cause"),
        "positive_controls_by_planted_severity": report_positive_strata("severity"),
        "recall_all_issues_abstentions_count_as_missed": _ratio(c["tp"], pos),
        "misses_by_severity": dict(sorted(severity_misses.items())),
        "detected_by_root_cause": dict(sorted(cause_detected.items())),
        "missed_or_abstained_by_root_cause": dict(sorted(cause_missed.items())),
        "always_clean_baseline": {
            "false_positives": 0, "recall_all_issues": 0.0 if pos else None,
            "coverage": 1.0 if n else None,
        },
    }


def measure(rows: list[dict], manifest: dict) -> dict:
    """Score positive/negative pairs without hiding negatives or abstentions.

    Input is *only* deterministic synthetic truth; no prospective/real-world
    inference follows from the output. Splits are reported separately and never
    pooled into an unqualified "held-out" score.
    """
    if type(rows) is not list or not rows:
        raise BenchmarkRefusal("nonempty list of synthetic rows required")
    if type(manifest) is not dict or set(manifest) != MANIFEST_FIELDS:
        raise BenchmarkRefusal("manifest fields must match frozen v1 contract")
    if manifest["schema"] != SCHEMA or manifest["truth_provenance"] != "SYNTHETIC":
        raise BenchmarkRefusal("only explicitly synthetic benchmark evidence allowed")
    for field in ("method_id", "method_version"):
        if type(manifest[field]) is not str or not IDENTITY.fullmatch(manifest[field]):
            raise BenchmarkRefusal("invalid frozen method identity: " + field)
    for field in ("spec_sha256", "fixture_sha256"):
        if type(manifest[field]) is not str or not HEX64.fullmatch(manifest[field]):
            raise BenchmarkRefusal("invalid frozen SHA-256: " + field)
    if fixture_digest(rows) != manifest["fixture_sha256"]:
        raise BenchmarkRefusal("fixture bytes differ from manifest declaration")

    case_ids: set[str] = set()
    families: dict[str, str] = {}
    pairs: dict[str, list[dict]] = {}
    for i, row in enumerate(rows):
        if type(row) is not dict or set(row) != ROW_FIELDS:
            raise BenchmarkRefusal(f"row {i}: missing or extra fields")
        for field in ("case_id", "pair_id", "family_id"):
            if type(row[field]) is not str or not IDENTITY.fullmatch(row[field]):
                raise BenchmarkRefusal(f"row {i}: invalid {field}")
        case_key = row["case_id"].casefold()
        if case_key in case_ids:
            raise BenchmarkRefusal("duplicate case identity")
        case_ids.add(case_key)
        if row["split"] not in SPLITS or row["truth"] not in TRUTHS:
            raise BenchmarkRefusal(f"row {i}: invalid split/truth")
        if row["prediction"] not in PREDICTIONS:
            raise BenchmarkRefusal(f"row {i}: invalid prediction")
        family = row["family_id"].casefold()
        split = row["split"]
        if family in families and families[family] != split:
            raise BenchmarkRefusal("family leakage across DEV and HELD_OUT")
        families[family] = split
        if row["truth"] == "CLEAN":
            if row["severity"] != "NONE" or row["root_cause"] != "NONE":
                raise BenchmarkRefusal("clean control cannot carry planted issue")
        elif row["severity"] not in ("S2", "S3") or row["root_cause"] not in ROOT_CAUSES:
            raise BenchmarkRefusal("issue needs planted severity and root cause")
        if row["prediction"] == "ABSTAIN":
            if row["abstention_reason"] not in ABSTENTION_REASONS:
                raise BenchmarkRefusal("abstention requires explicit reason")
        elif row["abstention_reason"] != "NONE":
            raise BenchmarkRefusal("decided case cannot carry abstention reason")
        pairs.setdefault(row["pair_id"].casefold(), []).append(row)
    for pair_id, pair in pairs.items():
        if (len(pair) != 2 or {x["truth"] for x in pair} != set(TRUTHS)
                or len({x["family_id"].casefold() for x in pair}) != 1
                or len({x["split"] for x in pair}) != 1):
            raise BenchmarkRefusal(f"pair {pair_id}: need matched issue/clean controls")
    return {
        "status": "SYNTHETIC_MEASUREMENT_ONLY",
        "schema": SCHEMA,
        "method_id": manifest["method_id"],
        "method_version": manifest["method_version"],
        "spec_sha256": manifest["spec_sha256"],
        "fixture_sha256": manifest["fixture_sha256"],
        "evaluation": {
            "replay": "NOT_MEASURED",
            "external_oracle_parity": "NOT_MEASURED",
            "independent_human_adjudication": "NOT_MEASURED",
            "prospective_real_world_accuracy": "NOT_MEASURED",
        },
        "by_split": {
            split: _score([row for row in rows if row["split"] == split])
            for split in SPLITS
        },
    }
