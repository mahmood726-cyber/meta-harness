"""Deterministic synthetic paired-outcome negative controls; no external sources."""
import unittest
from benchmarks.paired_false_positive import SCHEMA, fixture_digest, measure


def pair(key, split, positive, negative):
    def case(suffix, truth, pred):
        return {
            "case_id": key + suffix, "pair_id": key, "family_id": "family-" + key,
            "split": split, "truth": truth, "prediction": pred,
            "severity": "S3" if truth == "ISSUE" else "NONE",
            "root_cause": "ARITHMETIC" if truth == "ISSUE" else "NONE",
            "abstention_reason": "OUT_OF_SCOPE" if pred == "ABSTAIN" else "NONE",
        }
    return [case("1", "ISSUE", positive), case("0", "CLEAN", negative)]


def run(rows, split="HELD_OUT"):
    manifest = {
        "schema": SCHEMA, "method_id": "mock", "method_version": "v1",
        "spec_sha256": "a" * 64, "fixture_sha256": fixture_digest(rows),
        "truth_provenance": "SYNTHETIC",
    }
    return measure(rows, manifest)["by_split"][split]


class PairDiscriminationTests(unittest.TestCase):
    def test_paired_exact_success_and_non_discrimination(self):
        rows = pair("alpha", "HELD_OUT", "ISSUE", "CLEAN")
        rows += pair("beta", "HELD_OUT", "ISSUE", "ISSUE")
        out = run(rows)
        d = out["paired_discrimination"]
        self.assertEqual(d["strict_successes"], 1)
        self.assertEqual(d["decided_pairs"], 2)
        self.assertEqual(d["strict_success_rate_all_pairs"], 0.5)
        self.assertEqual(d["strict_success_rate_decided_pairs"], 0.5)
        self.assertIsNone(d["generalization_uncertainty_interval"])
        self.assertEqual(d["generalization_uncertainty_status"], "NOT_MEASURED_SYNTHETIC_ONLY")
        self.assertEqual(out["paired_outcome_matrix"]["ISSUE->CLEAN"], 1)
        self.assertEqual(out["paired_outcome_matrix"]["ISSUE->ISSUE"], 1)

    def test_unpaired_aggregation_cannot_invent_paired_success(self):
        rows = pair("alpha", "HELD_OUT", "ISSUE", "ISSUE")
        rows += pair("beta", "HELD_OUT", "CLEAN", "CLEAN")
        h = run(rows)
        self.assertEqual(h["confusion_with_abstentions"]["tp"], 1)
        self.assertEqual(h["confusion_with_abstentions"]["tn"], 1)
        self.assertEqual(h["paired_discrimination"]["strict_successes"], 0)
        self.assertEqual(h["paired_discrimination"]["strict_success_rate_all_pairs"], 0.0)
        contrasted = pair("alpha", "HELD_OUT", "ISSUE", "CLEAN")
        contrasted += pair("beta", "HELD_OUT", "CLEAN", "ISSUE")
        h2 = run(contrasted)
        self.assertEqual(h2["confusion_with_abstentions"], h["confusion_with_abstentions"])
        self.assertEqual(h2["paired_discrimination"]["strict_successes"], 1)

    def test_one_side_abstains_denominator_not_promoted(self):
        rows = pair("alpha", "HELD_OUT", "ISSUE", "ABSTAIN")
        rows += pair("beta", "HELD_OUT", "ISSUE", "CLEAN")
        out = run(rows)
        d = out["paired_discrimination"]
        self.assertEqual(d["abstaining_pairs"], 1)
        self.assertEqual(d["decided_pairs"], 1)
        self.assertEqual(d["pair_decision_coverage"], 0.5)
        self.assertEqual(d["strict_success_rate_decided_pairs"], 1.0)
        self.assertEqual(d["strict_success_rate_all_pairs"], 0.5)
        self.assertEqual(out["paired_outcome_matrix"]["ISSUE->ABSTAIN"], 1)

    def test_all_abstain_never_100_percent_success_or_coverage(self):
        out = run(pair("alpha", "HELD_OUT", "ABSTAIN", "ABSTAIN"))
        d = out["paired_discrimination"]
        self.assertEqual(d["decided_pairs"], 0)
        self.assertEqual(d["strict_success_rate_all_pairs"], 0.0)
        self.assertIsNone(d["strict_success_rate_decided_pairs"])
        self.assertEqual(d["pair_decision_coverage"], 0.0)
        self.assertEqual(out["paired_outcome_matrix"]["ABSTAIN->ABSTAIN"], 1)

    def test_empty_split_all_rates_are_null(self):
        h = run(pair("alpha", "DEV", "ISSUE", "CLEAN"))
        self.assertEqual(h["paired_discrimination"]["strict_successes"], 0)
        self.assertIsNone(h["paired_discrimination"]["pair_decision_coverage"])
        self.assertIsNone(h["paired_discrimination"]["strict_success_rate_all_pairs"])
        self.assertIsNone(h["paired_discrimination"]["strict_success_rate_decided_pairs"])
        self.assertEqual(sum(h["paired_outcome_matrix"].values()), 0)

    def test_all_nine_joint_prediction_states_are_accounted_for(self):
        predictions = ("ISSUE", "CLEAN", "ABSTAIN")
        rows = []
        for i, positive in enumerate(predictions):
            for j, negative in enumerate(predictions):
                rows += pair(f"case{i}{j}", "HELD_OUT", positive, negative)
        out = run(rows)
        self.assertEqual(out["paired_controls"], 9)
        self.assertEqual(out["paired_outcome_matrix"], {
            f"{p}->{n}": 1 for p in predictions for n in predictions
        })
        self.assertEqual(out["paired_discrimination"]["decided_pairs"], 4)
        self.assertEqual(out["paired_discrimination"]["abstaining_pairs"], 5)
        self.assertEqual(out["paired_discrimination"]["strict_successes"], 1)
        self.assertEqual(out["paired_discrimination"]["strict_success_rate_all_pairs"], 1 / 9)
        self.assertEqual(out["paired_discrimination"]["pair_decision_coverage"], 4 / 9)

    def test_case_and_pair_order_do_not_change_paired_scores(self):
        rows = pair("alpha", "HELD_OUT", "ISSUE", "CLEAN")
        rows += pair("beta", "HELD_OUT", "CLEAN", "ISSUE")
        orig = run(rows)
        permuted = run(list(reversed(rows)))
        self.assertEqual(orig["paired_outcome_matrix"], permuted["paired_outcome_matrix"])
        self.assertEqual(orig["paired_discrimination"], permuted["paired_discrimination"])
        self.assertEqual(sum(orig["paired_outcome_matrix"].values()), orig["paired_controls"])


if __name__ == "__main__":
    unittest.main()
