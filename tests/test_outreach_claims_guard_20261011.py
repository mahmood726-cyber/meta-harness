"""Checks the stand-alone, claims-bounded outreach landing page without changing pinned review code."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "docs" / "research-stage" / "index.html"
CLAIMS = ROOT / "docs" / "OUTREACH_CLAIMS.md"

def test_outreach_landing_exists_with_scoped_claims():
    text = LANDING.read_text(encoding="utf-8")
    assert "research-stage" in text.lower()
    for phrase in (
        "replay from committed analysis inputs",
        "not the same as reproduction from a protocol-only registration commit",
        "does not establish registration-time reproduction",
        "Model-family comparisons",
        "Source-location checks",
        "Clinical and publication safeguard",
    ):
        assert phrase in text
    assert "https://mahmood726-cyber.github.io/allmeta/" in text
    assert "https://mahmood726-cyber.github.io/synthesis-courses/" in text

def test_outreach_claims_are_explicit_about_unresolved_public_index():
    content = CLAIMS.read_text(encoding="utf-8").lower()
    assert "registration-time reproduction is not established" in content
    assert "public homepage" in content
