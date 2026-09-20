"""The strict-subset sweep must fire on the two withdrawn rows' exact published strings (pinned here as fixtures -- a control is
pinned, never read from the live tree, because the live rows are withdrawn and would retire the control) and must not fire on the
titles that name every clause. It must also NOT use the pinned lexicon as its instrument: the lexicon collapses the two-clause
name to one component, which is the mechanism of the defect."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import strict_subset_sweep as sw  # noqa: E402

NAME = "Composite cardiovascular death or worsening heart failure"
DELIVER_TITLE = "Subjects Included in the Endpoint of Cardiovascular Death"                      # dapagliflozin-hfpef-hosp PMID 36027570, withdrawn 2026-09-19
EMPEROR_TITLE = "Time to Adjudicated Cardiovascular (CV) Death"                                    # empagliflozin-hfpef-hosp PMID 34449189, withdrawn 2026-09-19


def test_positive_controls_the_two_withdrawn_rows_fire():
    for title in (DELIVER_TITLE, EMPEROR_TITLE):
        c = sw.compare(NAME, title)
        assert c["strict_subset"] is True, c
        assert c["named_by_title"] == ["cardiovascular death"] and c["missed_by_title"] == ["worsening heart failure"]


def test_the_lexicon_would_have_missed_them():
    from harness import target_endpoint as te
    assert set(te._components_from_text(NAME)) == {"cardiovascular death"}          # the collapse: 'worsening heart failure' -> nothing
    assert set(te._components_from_text(DELIVER_TITLE)) == set(te._components_from_text(NAME))   # title == name under the lexicon: EXACT


def test_titles_naming_every_clause_do_not_fire():
    for name, title in [
        ("Composite cardiovascular death or hospitalisation for heart failure", "Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due to Heart Failure."),   # sglt2-hfref, DAPA-HF
        ("Composite cardiovascular death or heart-failure hospitalization", "cardiovascular death ; heart failure hospitalization"),                                                  # hyphen vs space
        ("Stroke or systemic embolism", "The primary outcome was ischemic or hemorrhagic stroke or systemic embolism."),
        ("Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke", "a composite of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke--had occurred"),
    ]:
        c = sw.compare(name, title)
        assert c["strict_subset"] is False and not c["missed_by_title"], (name, c)


def test_opaque_title_is_a_third_state_not_a_hit_and_not_a_clear():
    c = sw.compare("Composite cardiovascular death or heart-failure hospitalization", "Exposure-adjusted Incident Rate (EAIR) of CEC Confirmed Composite Endpoints")
    assert c["strict_subset"] is False and c["names_no_clause"] is True


def test_single_clause_names_never_fire():
    assert sw.compare("All-cause mortality", "Death from any cause")["strict_subset"] is False
    assert sw.compare("Cardiovascular death", "Time to Adjudicated Cardiovascular (CV) Death")["strict_subset"] is False


def test_sweep_over_the_served_state_reports_denominator_and_the_two_known_hits():
    out = sw.sweep("316d2e48")            # the served state on 2026-09-20 (both wrong rows still pooled there)
    assert out["reviews"] == 32 and out["rows_swept"] == 147
    known = {("dapagliflozin-hfpef-hosp", "PMID 36027570"), ("empagliflozin-hfpef-hosp", "PMID 34449189")}
    assert known <= {(h["slug"], h["trial"]) for h in out["hits"]}
    assert out["rows_not_swept"]["count"] == 119 and out["rows_not_swept"]["primary_rows_among_them"] == 71
