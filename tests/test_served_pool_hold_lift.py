"""Plant: a HOLD on a signed served-pool notice is lifted only by its signer's own recorded words (Mahmood 7 Oct: "lift
v6-01 and agree"). A hold stays on the record with final.state LIFTED_BY_SIGNER, by and verbatim quote; only then does
build_served_pool_additions admit the notice. A lift with no signer or no quote, or any other final state (a withdrawal),
keeps the notice out."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import build_served_pool_additions as b  # noqa: E402


def test_only_a_signed_lift_releases_a_hold():
    h = {"slug": "s", "id": "PMID 1", "code": "X"}
    assert b.hold_applies(h)
    assert not b.hold_applies(dict(h, final={"state": "LIFTED_BY_SIGNER", "by": "Mahmood", "quote": "lift v6-01"}))
    for bad in ({"state": "LIFTED_BY_SIGNER", "by": "Mahmood"}, {"state": "LIFTED_BY_SIGNER", "quote": "lift"},
                {"state": "WITHDRAWN_BY_SIGNER", "by": "Mahmood", "quote": "withdraw v6-02"}, {"state": "LIFTED"}):
        assert b.hold_applies(dict(h, final=bad)), bad


def test_the_v6_01_hold_is_lifted_and_its_rows_are_admitted_at_the_signed_numbers():
    adds, exc = b.build()
    row = next(a for a in adds if a["slug"] == "dpp4-mace-t2d" and a["outcome"].startswith("3-point"))
    assert row["after"] == {"k": 4, "estimate": 1.0007, "ci_low": 0.8998, "ci_high": 1.1129}
    tecos = next(r for r in row["rows"] if r["id"] == "PMID 26052984")
    assert (tecos["effect"], tecos["ci_low"], tecos["ci_high"]) == (0.99, 0.89, 1.1)
    assert "unstable angina" not in tecos["source"].lower()          # its own 3-point registry outcome, not the comparator's
    assert not any("dpp4-mace-t2d" in e["notice"] for e in exc)
