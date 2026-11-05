"""No publication input; test artificial positive/negative benchmark pairs."""
import copy
import unittest

from benchmarks.paired_false_positive import (
    BenchmarkRefusal, SCHEMA, fixture_digest, measure,
)


def row(case, pair, family, split, truth, prediction, reason="NONE"):
    return {
        "case_id": case, "pair_id": pair, "family_id": family,
        "split": split, "truth": truth, "prediction": prediction,
        "severity": "S3" if truth == "ISSUE" else "NONE",
        "root_cause": "ARITHMETIC" if truth == "ISSUE" else "NONE",
        "abstention_reason": reason,
    }


def cases():
    return [
        row("d1", "d", "family-d", "DEV", "ISSUE", "ISSUE"),
        row("d0", "d", "family-d", "DEV", "CLEAN", "CLEAN"),
        row("h1", "h", "family-h", "HELD_OUT", "ISSUE", "ABSTAIN", "LOW_CONFIDENCE"),
        row("h0", "h", "family-h", "HELD_OUT", "CLEAN", "ISSUE"),
    ]


def manifest(rows):
    return {
        "schema": SCHEMA, "method_id": "synthetic-checker",
        "method_version": "v1-fixed", "spec_sha256": "a" * 64,
        "fixture_sha256": fixture_digest(rows), "truth_provenance": "SYNTHETIC",
    }


class PairedFalsePositiveTests(unittest.TestCase):
    def test_controlled_false_positive_and_abstention_are_both_visible(self):
        rows = cases()
        out = measure(rows, manifest(rows))
        h = out["by_split"]["HELD_OUT"]
        self.assertEqual(h["confusion_with_abstentions"]["fp"], 1)
        self.assertEqual(h["confusion_with_abstentions"]["abstain_issue"], 1)
        self.assertEqual(h["confusion_with_abstentions"]["tn"], 0)
        self.assertEqual(h["fpr_decided_negatives"], 1.0)
        self.assertEqual(h["recall_all_issues_abstentions_count_as_missed"], 0.0)
        self.assertEqual(h["coverage"], 0.5)
        self.assertEqual(h["precision_decided"], 0.0)
        self.assertEqual(out["evaluation"]["independent_human_adjudication"], "NOT_MEASURED")

    def test_correct_clean_control_counts_as_true_negative(self):
        rows = cases()
        rows[-1]["prediction"] = "CLEAN"
        h = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        self.assertEqual(h["confusion_with_abstentions"]["tn"], 1)
        self.assertEqual(h["fpr_decided_negatives"], 0.0)
        self.assertEqual(h["fp_yield_all_negatives"], 0.0)

    def test_abstaining_on_negative_is_not_true_negative(self):
        rows = cases()
        rows[-1]["prediction"] = "ABSTAIN"
        rows[-1]["abstention_reason"] = "INSUFFICIENT_EVIDENCE"
        h = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        self.assertEqual(h["confusion_with_abstentions"]["tn"], 0)
        self.assertEqual(h["confusion_with_abstentions"]["abstain_clean"], 1)
        self.assertIsNone(h["fpr_decided_negatives"])
        self.assertEqual(h["fp_yield_all_negatives"], 0.0)
        self.assertEqual(h["coverage"], 0.0)

    def test_false_positive_is_attributed_to_paired_planted_root_cause(self):
        rows = cases()
        rows[0]["severity"] = "S2"
        rows[0]["root_cause"] = "DENOMINATOR"
        rows[1]["prediction"] = "ISSUE"
        result = measure(rows, manifest(rows))["by_split"]["DEV"]
        cause = result["negative_controls_by_planted_root_cause"]
        sev = result["negative_controls_by_planted_severity"]
        self.assertEqual(cause["DENOMINATOR"]["fp"], 1)
        self.assertEqual(cause["DENOMINATOR"]["cases"], 1)
        self.assertEqual(cause["DENOMINATOR"]["fpr_decided_negatives"], 1.0)
        self.assertEqual(sev["S2"]["fp"], 1)
        self.assertEqual(result["negative_control_decision_coverage"], 1.0)

    def test_negative_abstention_is_visible_within_planted_root_cause(self):
        rows = cases()
        rows[-1]["prediction"] = "ABSTAIN"
        rows[-1]["abstention_reason"] = "OUT_OF_SCOPE"
        result = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        cause = result["negative_controls_by_planted_root_cause"]["ARITHMETIC"]
        self.assertEqual(cause["abstain"], 1)
        self.assertEqual(cause["fp"], 0)
        self.assertEqual(cause["negative_decision_coverage"], 0.0)
        self.assertIsNone(cause["fpr_decided_negatives"])
        self.assertEqual(result["negative_control_decision_coverage"], 0.0)

    def test_abstention_reasons_split_by_truth_without_hiding_negatives(self):
        rows = cases()
        rows[-1]["prediction"] = "ABSTAIN"
        rows[-1]["abstention_reason"] = "INSUFFICIENT_EVIDENCE"
        h = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        self.assertEqual(h["abstention_reasons_by_truth"], {
            "ISSUE": {"LOW_CONFIDENCE": 1},
            "CLEAN": {"INSUFFICIENT_EVIDENCE": 1},
        })
        self.assertEqual(h["confusion_with_abstentions"]["abstain_issue"], 1)
        self.assertEqual(h["confusion_with_abstentions"]["abstain_clean"], 1)

    def test_abstention_reason_counts_exclude_decisions_and_are_split_scoped(self):
        rows = cases()
        rows += [
            row("h2", "h2", "family-h2", "HELD_OUT", "ISSUE", "ABSTAIN", "OUT_OF_SCOPE"),
            row("h3", "h2", "family-h2", "HELD_OUT", "CLEAN", "CLEAN"),
        ]
        measured = measure(rows, manifest(rows))["by_split"]
        self.assertEqual(measured["DEV"]["abstention_reasons_by_truth"], {
            "ISSUE": {}, "CLEAN": {},
        })
        self.assertEqual(measured["HELD_OUT"]["abstention_reasons_by_truth"], {
            "ISSUE": {"LOW_CONFIDENCE": 1, "OUT_OF_SCOPE": 1},
            "CLEAN": {},
        })
        self.assertEqual(measured["HELD_OUT"]["confusion_with_abstentions"]["fp"], 1)

    def test_stratified_negative_control_denominators_include_true_negatives(self):
        rows = cases()
        rows += [
            row("h2", "h2", "family-h2", "HELD_OUT", "ISSUE", "ISSUE"),
            row("h3", "h2", "family-h2", "HELD_OUT", "CLEAN", "CLEAN"),
        ]
        rows[-2]["severity"] = "S2"
        rows[-2]["root_cause"] = "LABEL_SWITCH"
        h = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        self.assertEqual(h["negative_controls_by_planted_root_cause"]["ARITHMETIC"]["fp"], 1)
        self.assertEqual(h["negative_controls_by_planted_root_cause"]["LABEL_SWITCH"]["tn"], 1)
        self.assertEqual(h["negative_controls_by_planted_severity"]["S2"]["cases"], 1)
        self.assertEqual(h["negative_control_decision_coverage"], 1.0)

    def test_empty_split_negative_control_metrics_are_unmeasured(self):
        rows = cases()[:2]
        h = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        self.assertIsNone(h["negative_control_decision_coverage"])
        self.assertEqual(h["negative_controls_by_planted_severity"], {})
        self.assertEqual(h["negative_controls_by_planted_root_cause"], {})

    def test_issue_severity_strata_separate_false_negatives_and_abstentions(self):
        rows = cases()
        rows += [
            row("h2", "h2", "family-h2", "HELD_OUT", "ISSUE", "CLEAN"),
            row("h3", "h2", "family-h2", "HELD_OUT", "CLEAN", "CLEAN"),
        ]
        rows[-2]["severity"] = "S2"
        rows[-2]["root_cause"] = "DENOMINATOR"
        h = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        severity = h["positive_controls_by_planted_severity"]
        self.assertEqual(severity["S3"]["cases"], 1)
        self.assertEqual((severity["S3"]["tp"], severity["S3"]["fn"], severity["S3"]["abstain"]), (0, 0, 1))
        self.assertEqual(severity["S3"]["issue_decision_coverage"], 0.0)
        self.assertIsNone(severity["S3"]["recall_decided_issues"])
        self.assertEqual(severity["S2"]["fn"], 1)
        self.assertEqual(severity["S2"]["abstain"], 0)
        self.assertEqual(severity["S2"]["issue_decision_coverage"], 1.0)
        self.assertEqual(severity["S2"]["recall_all_issues_abstentions_count_as_missed"], 0.0)
        self.assertEqual(h["misses_by_severity"], {"S2": 1, "S3": 1})
        self.assertEqual(h["confusion_with_abstentions"]["fp"], 1)

    def test_issue_root_cause_strata_count_detected_and_missed_separately(self):
        rows = cases()
        rows += [
            row("h2", "h2", "family-h2", "HELD_OUT", "ISSUE", "ISSUE"),
            row("h3", "h2", "family-h2", "HELD_OUT", "CLEAN", "ABSTAIN", "OUT_OF_SCOPE"),
        ]
        rows[-2]["root_cause"] = "LABEL_SWITCH"
        rows[-2]["severity"] = "S2"
        result = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        by_cause = result["positive_controls_by_planted_root_cause"]
        self.assertEqual(by_cause["LABEL_SWITCH"]["tp"], 1)
        self.assertEqual(by_cause["LABEL_SWITCH"]["recall_all_issues_abstentions_count_as_missed"], 1.0)
        self.assertEqual(by_cause["LABEL_SWITCH"]["recall_decided_issues"], 1.0)
        self.assertEqual(by_cause["ARITHMETIC"]["abstain"], 1)
        self.assertIsNone(by_cause["ARITHMETIC"]["recall_decided_issues"])
        self.assertEqual(result["confusion_with_abstentions"]["abstain_clean"], 1)
        self.assertEqual(result["confusion_with_abstentions"]["fp"], 1)

    def test_empty_split_positive_strata_are_empty_not_perfect(self):
        rows = cases()[:2]
        h = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        self.assertEqual(h["positive_controls_by_planted_severity"], {})
        self.assertEqual(h["positive_controls_by_planted_root_cause"], {})
        d = measure(rows, manifest(rows))["by_split"]["DEV"]
        self.assertEqual(d["positive_controls_by_planted_severity"]["S3"]["tp"], 1)
        self.assertEqual(d["positive_controls_by_planted_severity"]["S3"]["recall_decided_issues"], 1.0)

    def test_family_split_leakage_refused_even_with_valid_digest(self):
        rows = cases()
        rows[-2]["family_id"] = rows[0]["family_id"]
        with self.assertRaisesRegex(BenchmarkRefusal, "family leakage"):
            measure(rows, manifest(rows))

    def test_pair_must_contain_both_truth_types(self):
        rows = cases()
        rows[-1]["truth"] = "ISSUE"
        rows[-1]["severity"] = "S3"
        rows[-1]["root_cause"] = "ARITHMETIC"
        with self.assertRaisesRegex(BenchmarkRefusal, "matched issue/clean"):
            measure(rows, manifest(rows))

    def test_pair_cannot_span_splits_even_if_family_names_differ(self):
        rows = cases()
        rows[-1]["split"] = "DEV"
        rows[-1]["family_id"] = "family-other"
        with self.assertRaisesRegex(BenchmarkRefusal, "matched issue/clean"):
            measure(rows, manifest(rows))

    def test_duplicate_case_rejected(self):
        rows = cases()
        rows[1]["case_id"] = "d1"
        with self.assertRaisesRegex(BenchmarkRefusal, "duplicate case"):
            measure(rows, manifest(rows))

    def test_duplicate_case_casing_across_splits_refused(self):
        # A DEV id must not be scored again as a different HELD_OUT id.
        rows = cases()
        rows[-1]["case_id"] = "D1"
        with self.assertRaisesRegex(BenchmarkRefusal, "duplicate case"):
            measure(rows, manifest(rows))

    def test_duplicate_case_casing_within_pair_refused(self):
        rows = cases()
        rows[1]["case_id"] = "D1"
        with self.assertRaisesRegex(BenchmarkRefusal, "duplicate case"):
            measure(rows, manifest(rows))

    def test_manifests_pin_exact_synthetic_fixture(self):
        rows = cases()
        m = manifest(rows)
        rows[-1]["prediction"] = "CLEAN"
        with self.assertRaisesRegex(BenchmarkRefusal, "fixture bytes differ"):
            measure(rows, m)

    def test_non_synthetic_truth_cannot_be_promoted(self):
        rows = cases()
        m = manifest(rows)
        m["truth_provenance"] = "INDEPENDENT_HUMAN"
        with self.assertRaisesRegex(BenchmarkRefusal, "explicitly synthetic"):
            measure(rows, m)

    def test_undeclared_input_field_refused(self):
        rows = cases()
        rows[0]["posthoc_performance_claim"] = 1.0
        with self.assertRaisesRegex(BenchmarkRefusal, "extra fields"):
            measure(rows, manifest(rows))

    def test_missing_frozen_version_refused(self):
        rows = cases()
        m = manifest(rows)
        m["method_version"] = ""
        with self.assertRaisesRegex(BenchmarkRefusal, "method identity"):
            measure(rows, m)

    def test_empty_split_has_not_measured_metrics(self):
        rows = cases()[:2]
        h = measure(rows, manifest(rows))["by_split"]["HELD_OUT"]
        self.assertEqual(h["cases"], 0)
        self.assertIsNone(h["coverage"])
        self.assertIsNone(h["fpr_decided_negatives"])

    def test_determinism_and_input_nonmutation(self):
        rows = cases()
        before = copy.deepcopy(rows)
        m = manifest(rows)
        self.assertEqual(measure(rows, m), measure(rows, m))
        self.assertEqual(rows, before)
        self.assertEqual(m, manifest(rows))


if __name__ == "__main__":
    unittest.main()
