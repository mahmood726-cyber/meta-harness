"""A clone WITHOUT the gitignored full-text cache (outputs/k_gap/_ft) still verifies a full-text span, from the
COMMITTED copy of an OPEN body (cache/<slug>/ft_<pmid>.txt) -- only when its sha256 equals the one
outputs/k_gap/fulltext_index.json recorded and the copy is marked CC. Zarpelon [20] (PMID 27223641, PMC4976950,
CC BY 4.0) is the case: its open-label statement is in the full text only (re-fetched 5 Oct, byte-identical)."""
import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_counterfactual as cfm  # noqa: E402

PMID = "27223641"
SHA = "25981c8eb7aec5684034785a60fbe922976c47e1c2192b4e9a5a74906543f51a"


def test_the_committed_copy_is_the_recorded_open_body():
    b = open(os.path.join(ROOT, "cache", "colchicine-postop-af", f"ft_{PMID}.txt"), "rb").read()
    e = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "fulltext_index.json"), encoding="utf-8"))[PMID]
    assert hashlib.sha256(b).hexdigest() == e["sha256"] == SHA and e["copy_licence"] == "CC" and len(b) == e["bytes"]


def test_PLANT_a_clone_without_the_cache_reads_the_committed_copy_and_refuses_other_bytes(tmp_path, monkeypatch):
    monkeypatch.setattr(cfm, "FT_DIR", str(tmp_path / "_ft_absent"))          # the clone has no _ft
    t = cfm.pmc_fulltext_cached(PMID, offline=True)
    assert hashlib.sha256(t.encode("utf-8")).hexdigest() == SHA
    assert "This is a prospective, randomized, open" in t
    # a committed copy whose bytes are not the recorded body is never used
    fake = tmp_path / "root"
    shutil.copytree(os.path.join(ROOT, "outputs", "k_gap"), fake / "outputs" / "k_gap",
                    ignore=shutil.ignore_patterns("_ft", "_upw", "g1", "sweep", "*.gz"))
    (fake / "cache" / "colchicine-postop-af").mkdir(parents=True)
    (fake / "cache" / "colchicine-postop-af" / f"ft_{PMID}.txt").write_bytes(b"randomized, open -- altered")
    monkeypatch.setattr(cfm, "ROOT", str(fake))
    monkeypatch.setattr(cfm, "OUT", str(fake / "outputs" / "k_gap"))
    assert cfm.committed_open_fulltext(PMID) is None
