import tempfile
import unittest
from pathlib import Path
from harness.evidence_provenance import (append_event, read_events, validate_extraction,
                                         can_pool, sha256)

class ProvenanceTests(unittest.TestCase):
    def record(self, data=b"page 1: HR 0.80"):
        return dict.fromkeys((
            "review_id", "study_id", "document_sha256", "source_uri",
            "source_page_or_locator", "verbatim_passage", "field_name",
            "raw_value", "normalised_value", "unit", "population",
            "outcome", "time_point", "effect_measure", "extractor_identity",
            "extracted_at_utc", "status"), "x") | {
            "document_sha256": sha256(data), "verbatim_passage": "HR 0.80",
            "source_page_or_locator": "p1", "status": "SOURCE_CHECKED"}

    def test_source_checked(self):
        self.assertTrue(validate_extraction(self.record(), b"page 1: HR 0.80"))

    def test_tampered_archive(self):
        with self.assertRaises(ValueError):
            validate_extraction(self.record(), b"page 1: HR 0.90")

    def test_missing_passage(self):
        record = self.record()
        record["verbatim_passage"] = ""
        with self.assertRaises(ValueError):
            validate_extraction(record, b"page 1: HR 0.80")

    def test_journal_tampering(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "events.jsonl"
            event = dict(event_id="1", timestamp_utc="2026-10-24T12:00:00Z",
                         actor_type="MODEL", actor_id="test", action="SCREEN",
                         study_id="study1", source_digest="a", reason="test",
                         supersedes_event_id=None)
            append_event(p, event)
            self.assertEqual(len(read_events(p)), 1)
            p.write_bytes(p.read_bytes().replace(b'"reason":"test"', b'"reason":"fake"'))
            with self.assertRaises(ValueError):
                read_events(p)

    def test_refusal(self):
        studies = {"a": {"eligibility": "INCLUDE", "extractionReviewed": True, "estimand": "HR"}}
        self.assertTrue(can_pool({"decision": "ALLOW", "estimand": "HR", "studyIds": ["a"]}, studies))
        self.assertFalse(can_pool({"decision": "REFUSE", "estimand": "HR", "studyIds": ["a"]}, studies))
        self.assertFalse(can_pool({"decision": "ALLOW", "estimand": "RR", "studyIds": ["a"]}, studies))

if __name__ == "__main__":
    unittest.main()
