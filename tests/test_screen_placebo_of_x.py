"""12-01 root cause (reviews 7, 9, 12; final-push k-gap 1): harness/screen.py read a PLACEBO OF the intervention of interest
as an active arm carrying it, so a drug-v-placebo trial looked 'background only' and was excluded (CONTRAST_ABSENT /
X-CONTRAST). (a) `_PLACEBO.fullmatch` let 'placebo Circadin' stay an active drug and ignored pure 'Placebo' entries;
(b) a STRUCTURAL False from AACT fell through to the weaker intervention-list fallback. The intervention strings below are
the real CT.gov entries held in cache/<slug>/records.json."""
from __future__ import annotations

from harness import screen
from harness import armcontrast


def _bg(interventions, keywords):
    return screen._record_arm_interventions_background_only({"interventions": interventions}, keywords)[0]


def test_PLANT_circadin_placebo_of_x_is_not_an_active_arm():
    # melatonin NCT00816673 (Circadin elderly): ['placebo Circadin', 'Circadin']
    assert _bg(["placebo Circadin", "Circadin"], ["melatonin", "circadin"]) is False


def test_PLANT_sak_placebo_for_empagliflozin_with_shared_background():
    # empagliflozin-hfpef NCT05138575 (SAK): KCl background in both compared arms; 'Placebo for Empagliflozin' is the control
    ivs = ["Empagliflozin + Potassium Chloride", "Empagliflozin + Potassium Nitrate",
           "Potassium Chloride + Placebo for Empagliflozin"]
    assert _bg(ivs, ["empagliflozin"]) is False


def test_PLANT_arts_dn_japan_dose_arms_against_pure_placebo():
    # finerenone NCT01968668 (ARTS-DN Japan): several BAY94-8862 dose entries and a pure 'Placebo' entry
    ivs = ["BAY94-8862"] * 5 + ["Placebo", "BAY 94-8862", "BAY 94-8862"]
    assert _bg(ivs, ["finerenone", "BAY94-8862", "BAY 94-8862"]) is False


def test_PLANT_genuine_background_combination_is_still_caught():
    # MIRO-CKD NCT06350123 (double-dummy): dapagliflozin is in EVERY arm, unqualified; balcinrenone is the contrast
    ivs = ["Balcinrenone/dapagliflozin 15 mg/10 mg and matching placebo for dapagliflozin 10 mg",
           "Dapagliflozin 10 mg and matching placebo for balcinrenone/dapagliflozin"]
    assert _bg(ivs, ["dapagliflozin"]) is True
    # and the plain background pattern: the drug in every entry, a different drug differs
    assert _bg(["Dapagliflozin + Balcinrenone", "Dapagliflozin + Placebo"], ["dapagliflozin"]) is True


def test_PLANT_structural_false_is_decisive_never_falls_through(monkeypatch):
    # AACT proves the interest IS the randomised contrast (False); the intervention-list fallback alone would say
    # 'background' (every entry names the drug, no placebo entry) -- the structural verdict wins
    rec = {"id": "NCT00000001", "id_type": "nct", "interventions": ["Drugx 10 mg", "Drugx 20 mg"]}
    assert _bg(rec["interventions"], ["drugx"]) is True                    # the fallback alone
    monkeypatch.setattr(armcontrast, "background_only_inclusion", lambda nct, kw, idx: False)
    assert screen._background_only_randomised_contrast(rec, ["drugx"], {})[0] is False
    # abstention (None) still lets the fallback speak
    monkeypatch.setattr(armcontrast, "background_only_inclusion", lambda nct, kw, idx: None)
    assert screen._background_only_randomised_contrast(rec, ["drugx"], {})[0] is True
