"""PLANTS for the comparator enumerator (scripts/g1_binding_enumerate.py), on the real row shapes of the denosumab
comparator's supplementary trial table (PMID 36852077, PMC9958453 mmc1)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

import g1_binding_enumerate as ge  # noqa: E402

TABLE = """Cummings 200985 29 MN III Double-blind  72.3 99.0 >=1000 >=800 1 3,902 Denosumab 60 mg/6 mo, sc 36
          2 3,906 Placebo
Brown 2009239 31 MN III Double-blind  64.4 84.4 >=500 >=400 1 594 Denosumab 60 mg/6 mo, sc 12
          2 595 Alendronate 70 mg/ wk, oral
Kendler 2010#250 51 MN III Double-blind  67.6 NR 1000 400 1 253  Denosumab 60 mg/6 mo, sc 12
          2 249 Alendronate 70 mg/ wk, oral
McClung 2006a236 22 MN III Both  63.2 85.0  1000 400 1 47 Alendronate 70 mg/ wk, oral 12
          2 272 Denosumab 6, 14 or 30 mg/3 mo; 14, 60, 100 or 210 mg/6 mo, sc
          3 46 Placebo
Black 1996104 20 MN III Double-blind  70.8  97.0 500  250  1 1022  Alendronate 5 or 10 mg/d, oral 36
          2 1005 Placebo
"""


def test_rows_and_arms_parse_including_hash_before_ref():
    rows = {r["label"]: r for r in ge.parse_table(TABLE)}
    assert set(rows) == {"Cummings 2009", "Brown 2009", "Kendler 2010", "McClung 2006a", "Black 1996"}
    assert rows["Kendler 2010"]["ref"] == "250"
    assert [a["n"] for a in rows["McClung 2006a"]["arms"]] == [47, 272, 46]
    assert rows["Cummings 2009"]["arms"][0]["n"] == 3902


def test_reference_fields():
    au, title, yr = ge.ref_fields("Cummings SR, San Martin J, McClung MR, et al. Denosumab for prevention of fractures "
                                  "in postmenopausal women with osteoporosis. The New England journal of medicine. "
                                  "2009;361(8):756-765.")
    assert (au, yr) == ("Cummings", "2009")
    assert title == "Denosumab for prevention of fractures in postmenopausal women with osteoporosis"


def test_wrapped_references_join():
    refs = ge.parse_refs("239. Brown JP, Prince RL, et al. Comparison of the effect of denosumab and alendronate: a "
                         "randomized,\nblinded, phase 3 trial. J Bone Miner Res. 2009;24(1):153-161.\n240. Next A. X. 2001;1.")
    assert refs["239"].endswith("2009;24(1):153-161.") and "randomized, blinded" in refs["239"]
