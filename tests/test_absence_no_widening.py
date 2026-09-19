"""PLANT (fired pre-fix on main 8c8874b4): harness/absence._effect_candidates returned `primary or fallback` --
when no effect's clause named the requested outcome it returned EVERY effect in the candidate sentences, and the
served declared-absent row printed another outcome's number beside this outcome's name. Served instances at
8c8874b4: balanced-crystalloids Acute kidney injury and New renal-replacement therapy (SMART 29485925) carried
MAKE30's OR 0.91; probiotics AAD (24044687) carried a risk-factor OR 5.04; iv-iron Heart-failure hospitalization
(IRONMAN 36347265) carried the composite rate ratio 0.82. The pre-fix function is executed from git so the plant
is a measurement."""
from __future__ import annotations

import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import absence  # noqa: E402

PRE_FIX = "8c8874b4"

# The held SMART record (PMID 29485925) and the topic's own keywords: the only effect in the candidate sentences
# belongs to the MAKE30 composite; the requested outcome is acute kidney injury.
SLUG = "balanced-crystalloids-vs-saline-mortality"
PID = "29485925"
KEYWORDS = ["acute kidney injury", "AKI", "kidney injury"]
OUTCOME = "Acute kidney injury"


def _held():
    import json
    records = json.loads((ROOT / "cache" / SLUG / "records.json").read_text(encoding="utf-8"))
    rec = next(r for r in records["records"] if str(r.get("id")) == PID)
    ft_path = ROOT / "cache" / SLUG / f"ft_{PID}.txt"
    return rec.get("abstract") or "", (ft_path.read_text(encoding="utf-8") if ft_path.exists() else None)


def _prefix_module():
    src = subprocess.run(["git", "show", f"{PRE_FIX}:harness/absence.py"], cwd=ROOT, check=True, capture_output=True,
                         text=True, encoding="utf-8").stdout
    mod = types.ModuleType("absence_prefix")
    mod.__package__ = "harness"
    exec(compile(src, f"<{PRE_FIX}:harness/absence.py>", "exec"), mod.__dict__)
    return mod


def _sentences(mod):
    abstract, fulltext = _held()
    out = list(mod._candidate_sentences(abstract, KEYWORDS, OUTCOME))
    if fulltext:
        out += list(mod._candidate_sentences(fulltext, KEYWORDS, OUTCOME))
    return out


def test_plant_prefix_attributed_the_composite_effect_to_the_requested_outcome():
    pre = _prefix_module()
    sents = _sentences(pre)
    assert any("major adverse kidney event" in s for s in sents), "the composite's sentence must be a candidate for the plant to bite"
    effects = pre._effect_candidates(sents, pre._terms(KEYWORDS, OUTCOME))
    assert effects and effects[0]["effect"] == 0.91, "pre-fix: MAKE30's OR 0.91 was returned for Acute kidney injury"
    abstract, fulltext = _held()
    ann = pre.classify_reason(KEYWORDS, abstract, fulltext, outcome_name=OUTCOME, declared_estimand="RR", reason="not reported")
    assert ann["reason_code"] == pre.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH and "0.91" in ann["state_basis"]


def test_postfix_no_effect_is_attributed_when_no_clause_names_the_outcome():
    sents = _sentences(absence)
    assert absence._effect_candidates(sents, absence._terms(KEYWORDS, OUTCOME)) == []
    abstract, fulltext = _held()
    ann = absence.classify_reason(KEYWORDS, abstract, fulltext, outcome_name=OUTCOME, declared_estimand="RR", reason="not reported")
    assert ann["reason_code"] != absence.EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH
    assert "0.91" not in str(ann.get("state_basis"))


def test_postfix_an_effect_whose_clause_names_the_outcome_is_still_found():
    text = ("Acute kidney injury occurred less often with balanced crystalloids (relative risk, 0.85; 95% CI, 0.78 to 0.93). "
            "Mortality did not differ (odds ratio, 0.99; 95% CI, 0.90 to 1.09).")
    sents = list(absence._candidate_sentences(text, KEYWORDS, OUTCOME))
    effects = absence._effect_candidates(sents, absence._terms(KEYWORDS, OUTCOME))
    assert [e["effect"] for e in effects] == [0.85]


def test_postfix_bare_counts_from_another_outcomes_clause_are_not_candidates():
    text = ("Death occurred in 530 of 2433 patients and 530 of 2413 patients. "
            "Acute kidney injury was not reported.")
    sents = list(absence._candidate_sentences(text, KEYWORDS, OUTCOME))
    counts = absence._count_candidates(sents, absence._terms(KEYWORDS, OUTCOME))
    assert all("kidney" in c.lower() for c in counts), counts
