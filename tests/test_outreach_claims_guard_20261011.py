"""Regression checks for publicly displayed meta-harness claims."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs" / "index.html"
GENERATOR = ROOT / "harness" / "index.py"

BANNED = (
    "the whole review regenerates from a committed protocol commit",
    "On reporting and reproducibility we are clearly better",
    "the most auditable synthesis, not the most complete",
    "A reader cannot check a Cochrane review number-by-number",
    "No published meta-analysis makes",
    "no meta-analysis reports this about itself",
    "not an artefact of an AI liking a page",
    "genuinely independent check",
)
REQUIRED = (
    "Research-stage meta-analysis audit and replay workflow",
    "a protocol-only registration commit does not reproduce",
    "The legacy corpus is an adversarial regression corpus",
    "not independent human adjudication or proof of general superiority",
)

class HomepageClaimGuard(unittest.TestCase):
    def test_rendered_claims(self):
        rendered = SITE.read_text(encoding="utf-8")
        for phrase in BANNED:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, rendered)
        for phrase in REQUIRED:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, rendered)

    def test_generator_claims(self):
        source = GENERATOR.read_text(encoding="utf-8")
        for phrase in BANNED[:4]:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, source)

if __name__ == "__main__":
    unittest.main()
