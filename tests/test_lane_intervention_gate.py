"""Plant (5 Oct, forest lane): a lane figure enters a topic's build only when its caption or the meta's own title names
the topic's INTERVENTION (topics/<slug>.json intervention_terms). The IL-6 receptor-antagonist meta 35343397 was ACCEPTED
under corticosteroids-covid19-mortality; its REMAP-CAP / RECOVERY rows (the IL-6 domains of those platform trials, same
registrations) then BLOCKED the corticosteroid rows by cross-check."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import secondary_meta_build as smb  # noqa: E402

CORT = ["dexamethasone", "hydrocortisone", "corticosteroid", "corticosteroids", "steroid"]


def test_il6_caption_under_corticosteroids_is_refused():
    cap = ("Forest plot of all-cause 28-day mortality. Forest plot showing the risk ratio in mortality between patients "
           "treated with IL-6 receptor antagonist compared with standard of care (SOC).")
    assert smb.lane_intervention_refusal(CORT, cap, "Efficacy of IL-6 receptor antagonists in COVID-19") \
        == "INTERVENTION_NOT_THE_TOPICS"


def test_corticosteroid_caption_passes_and_a_silent_caption_needs_the_title():
    assert smb.lane_intervention_refusal(CORT, "Forest plot comparing corticosteroids treatment vs. no corticosteroids",
                                         "") is None
    assert smb.lane_intervention_refusal(CORT, "Forest plot of 28-day mortality", "Dexamethasone for COVID-19: a "
                                         "meta-analysis") is None
    assert smb.lane_intervention_refusal(CORT, "Forest plot of 28-day mortality", "") == "INTERVENTION_NOT_THE_TOPICS"


def test_terms_match_whole_words_only():
    # 'steroid' must not be found inside 'nonsteroidal'; an abbreviation matches as a word
    assert smb.lane_intervention_refusal(["steroid"], "nonsteroidal anti-inflammatory drugs", "") \
        == "INTERVENTION_NOT_THE_TOPICS"
    assert smb.lane_intervention_refusal(["FCM"], "FCM versus placebo", "") is None


def test_plural_and_unicode_hyphen_are_the_same_term():
    assert smb.lane_intervention_refusal(["PCSK9 inhibitor"], "", "Efficacy of PCSK9 inhibitors in ACS") is None
    assert smb.lane_intervention_refusal(["sodium-glucose co-transporter 2"], "",
                                         "Effects of sodium\u2010glucose co\u2010transporter 2 inhibitors") is None


def test_topic_terms_add_only_the_explicit_class_map():
    dapa = smb.topic_intervention_terms("dapagliflozin-hfpef-hosp")
    assert smb.lane_intervention_refusal(dapa, "", "SGLT2 inhibitors decrease cardiovascular death") is None
    toci = smb.topic_intervention_terms("tocilizumab-covid19-mortality")
    assert smb.lane_intervention_refusal(toci, "", "Efficacy and safety of IL-6 inhibitors in COVID-19") is None
    assert smb.lane_intervention_refusal(toci, "", "Convalescent Plasma Treatment in Patients with Covid-19") \
        == "INTERVENTION_NOT_THE_TOPICS"
    iron = smb.topic_intervention_terms("iv-iron-hfref-hosp")
    assert smb.lane_intervention_refusal(iron, "", "Intravenous iron infusion in patients with heart failure") is None
    # an MRA class meta is NOT the spironolactone topic's class when it is about finerenone only
    spi = smb.topic_intervention_terms("spironolactone-hfref-mortality")
    assert smb.lane_intervention_refusal(spi, "patients hospitalized for heart failure",
                                         "Efficacy and Safety of Finerenone Therapy") == "INTERVENTION_NOT_THE_TOPICS"
    cort = smb.topic_intervention_terms("corticosteroids-covid19-mortality")
    assert smb.lane_intervention_refusal(cort, "IL-6 receptor antagonist compared with standard of care",
                                         "interleukin-6 receptor antagonists (tocilizumab and sarilumab)") \
        == "INTERVENTION_NOT_THE_TOPICS"


def test_pcsk9_class_reads_a_parenthesised_abbreviation():
    pc = smb.topic_intervention_terms("pcsk9-mace")
    assert smb.lane_intervention_refusal(pc, "Forest plot showing MACEs", "Efficacy of proprotein convertase subtilisin "
                                         "kexin type (PCSK9) inhibitors") is None
    assert smb.lane_intervention_refusal(pc, "Risk of three-point MACE", "Benefits of intensive lipid-lowering "
                                         "therapies in acute coronary syndrome") == "INTERVENTION_NOT_THE_TOPICS"


def test_reader_skips_a_wrong_intervention_meta_before_any_model_call(monkeypatch):
    import g1_forest_reader as gfr
    monkeypatch.setattr(gfr, "comparator_of", lambda slug: "999")
    monkeypatch.setattr(gfr, "_meta_title", lambda pmid, run: {"1": "Interleukin-6 receptor antagonists in COVID-19",
                                                               "2": "Corticosteroids for COVID-19"}.get(pmid))
    its = [{"slug": "corticosteroids-covid19-mortality", "pmid": "1", "figure": {"fig_id": "F2", "caption": "Mortality"}},
           {"slug": "corticosteroids-covid19-mortality", "pmid": "2", "figure": {"fig_id": "F1", "caption": "Mortality"}},
           {"slug": "corticosteroids-covid19-mortality", "pmid": "999", "figure": {"fig_id": "F3", "caption": "x"}}]
    skipped = {}
    kept = gfr.intervention_skip(its, skipped, run=False)
    assert [i["pmid"] for i in kept] == ["2", "999"]          # the comparator is never filtered here
    assert skipped == {"corticosteroids-covid19-mortality::1": "INTERVENTION_NOT_THE_TOPICS"}
