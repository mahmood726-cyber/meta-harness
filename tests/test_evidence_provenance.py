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


    def test_duplicate_study_refusal(self):
        studies = {"a": {"eligibility": "INCLUDE", "extractionReviewed": True, "estimand": "HR"}}
        self.assertFalse(can_pool({"decision": "ALLOW", "estimand": "HR",
                                   "studyIds": ["a", "a"]}, studies))

    def test_duplicate_journal_event_refusal(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "events.jsonl"
            event = dict(event_id="1", timestamp_utc="2026-10-24T12:00:00Z",
                         actor_type="MODEL", actor_id="test", action="SCREEN",
                         study_id="study1", source_digest="a", reason="test",
                         supersedes_event_id=None)
            append_event(p, event)
            with self.assertRaises(ValueError):
                append_event(p, event)

    def test_previous_hash_spoofing_refusal(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "events.jsonl"
            event = dict(event_id="1", timestamp_utc="2026-10-24T12:00:00Z",
                         actor_type="MODEL", actor_id="test", action="SCREEN",
                         study_id="study1", source_digest="a", reason="test",
                         supersedes_event_id=None, previous_event_sha256="spoof")
            with self.assertRaises(ValueError):
                append_event(p, event)


    def test_malformed_study_inputs_fail_closed(self):
        analysis = {"decision": "ALLOW", "estimand": "HR", "studyIds": ["a"]}
        self.assertFalse(can_pool(analysis, {"a": None}))
        self.assertFalse(can_pool(analysis, {"a": "included"}))
        self.assertFalse(can_pool(analysis, None))
        self.assertFalse(can_pool({**analysis, "studyIds": [None]}, {}))
        self.assertFalse(can_pool({**analysis, "studyIds": [1]}, {}))


    def test_adjudication_cannot_be_self_declared(self):
        record = self.record()
        record["status"] = "ADJUDICATED"
        with self.assertRaises(ValueError):
            validate_extraction(record, b"page 1: HR 0.80")

    def test_missing_clinical_context_cannot_be_source_checked(self):
        for key in ("population", "outcome", "time_point", "effect_measure", "study_id"):
            with self.subTest(key=key):
                record = self.record()
                record[key] = ""
                with self.assertRaises(ValueError):
                    validate_extraction(record, b"page 1: HR 0.80")


    def test_invalid_analysis_object_refused(self):
        self.assertFalse(can_pool(None, {}))
        self.assertFalse(can_pool([], {}))
        self.assertFalse(can_pool("ALLOW", {}))

if __name__ == "__main__":
    unittest.main()
