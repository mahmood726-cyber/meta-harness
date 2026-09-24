"""R2 for sites outside extract.py (regex_layer/site_measure.py): measures the harness's own compiled pattern, refuses a
label that quotes text not present, and never drops an unmeasurable site."""
from __future__ import annotations

from regex_layer import site_measure as m
from regex_layer.site_detects import DETECTS
from regex_layer.specs import INLINE_SPECS
from regex_layer.defects import KNOWN_DEFECTS


def test_every_site_is_measured_or_has_a_reason():
    for site in DETECTS:
        assert (m.population_of(site) is None) == (m.not_measured_reason(site) is not None), site


def test_the_measured_pattern_is_the_one_the_plants_hold_to():
    # every accept plant of a measured site fires through site_measure (the same pattern the harness compiles)
    for site in DETECTS:
        if m.population_of(site) is None:
            continue
        for i, (text, _groups) in enumerate(INLINE_SPECS[site]["plants"]["accept"]):
            if f"{site}-accept-{i}" not in KNOWN_DEFECTS:          # a located defect fails its plant by design
                assert m.fires(site, text), (site, text)
        for i, text in enumerate(INLINE_SPECS[site]["plants"]["refuse"]):
            if f"{site}-refuse-{i}" not in KNOWN_DEFECTS:
                assert not m.fires(site, text), (site, text)


def test_a_quote_not_in_the_text_is_refused_and_counts_are_classifier_counts():
    site = next(s for s in DETECTS if m.population_of(s))
    accept = INLINE_SPECS[site]["plants"]["accept"][0][0]
    refuse = INLINE_SPECS[site]["plants"]["refuse"][0]
    assert m.verify_site_label({"states": True, "quote": "not there at all"}, accept, site)["state"] == "VERIFIER_REFUSED"
    per = m.measure([(site, accept, True), (site, refuse, True), (site, accept, False)])[site]
    assert (per["tp"], per["fn"], per["fp"]) == (1, 1, 1)


def test_comparator_sourced_sites_are_not_sampled_from_trial_sentences():
    comp = [s for s, d in DETECTS.items() if (d.get("text_source") or "").lower().startswith("comparator")]
    assert comp and all(m.population_of(s) is None for s in comp)
