"""Synthetic PLANTS only. No fixture quantities are corpus evidence."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from harness.proposal_gate import (POOLED, SCOPE, TRIAL, ROOT, flat, parse_estimate,
                                   to_comparator, verify)

HELD = ("Outcome: Mortality at 28 days. Pooled 2 trials: RR 0.80 (95% CI 0.60 to 0.95). "
        "ALPHA NCT00000001 PMID 12345678 events_1=4 n_1=20 events_2=6 n_2=20 "
        "RR 0.70 (95% CI 0.40 to 0.90). "
        "Secondary: Hospitalization RR 0.55 (95% CI 0.30 to 0.75). "
        "Investigator-supplied BETA n_1=40.")


def proposal(text=HELD):
    pooled_span = "Pooled 2 trials: RR 0.80 (95% CI 0.60 to 0.95)."
    row_span = "ALPHA NCT00000001 PMID 12345678 events_1=4 n_1=20 events_2=6 n_2=20 RR 0.70 (95% CI 0.40 to 0.90)."
    return dict(slug="plant", comparator_pmid="12345679", document_ref="cache/plant/held.txt",
                document_sha256=hashlib.sha256(text.encode()).hexdigest(), proposed_by="synthetic PLANT",
                scope_note="Synthetic primary mortality; not a clinical source.", not_found=[],
                trial_set_scope="selected_outcome",
                primary_scope=dict(outcome_as_printed="Mortality", timepoint_as_printed="28 days",
                                   measure_as_printed=None, span="Outcome: Mortality at 28 days."),
                pooled=dict(k=2, effect=0.8, ci_low=0.6, ci_high=0.95, measure="RR", span=pooled_span),
                trials=[dict(label="ALPHA", registration="NCT00000001", pmid="12345678", events_1=4,
                             n_1=20, events_2=6, n_2=20, effect=0.7, ci_low=0.4, ci_high=0.9,
                             measure="RR", span=row_span)])


def install(root, text=HELD):
    p = proposal(text)
    (root / "topics").mkdir()
    (root / "cache/plant").mkdir(parents=True)
    (root / "topics/plant.json").write_text(json.dumps({"slug": "plant", "comparator_pmid": "12345679",
        "primary_outcome": {"name": "Mortality"}}), encoding="utf-8")
    (root / p["document_ref"]).write_bytes(text.encode())
    panel = {"id": "12345679", "held": True, "document_ref": p["document_ref"],
             "document_sha256": p["document_sha256"]}
    (root / "cache/plant/comparators.json").write_text(json.dumps([panel]), encoding="utf-8")
    return p


def field(result, name):
    return next(x for x in result["fields"] if x["path"] == name)


def test_correct_item_and_whitespace_negative_plant(tmp_path):
    p = install(tmp_path, HELD.replace(" ", "\n\t "))
    got = verify(p, tmp_path)
    assert got["status"] == "accepted"
    assert got["accepted"]["pooled"]["k"] == 2
    assert field(got, "trials.0.pmid")["status"] == "accepted"


def test_fabricated_span(tmp_path):
    p = install(tmp_path)
    p["pooled"]["span"] = "Pooled 2 trials: RR 0.80 (95% CI 0.60 to 0.95). invented tail"
    got = verify(p, tmp_path)
    assert field(got, "pooled.effect")["reason"] == "REFUSED_SPAN_NOT_HELD"
    assert got["accepted"]["pooled"]["effect"] is None
    assert got["accepted"]["trials"][0]["effect"] == 0.7


@pytest.mark.parametrize("key,value", [("effect", 0.55), ("effect", 0.95), ("ci_low", 0.8),
                                       ("k", 28), ("k", True), ("k", 2.0), ("effect", float("nan"))])
def test_number_not_in_own_role_or_typed_domain(tmp_path, key, value):
    p = install(tmp_path)
    p["pooled"][key] = value
    assert field(verify(p, tmp_path), "pooled." + key)["status"] == "rejected"


def test_foreign_field_span_cannot_launder_secondary_number(tmp_path):
    p = install(tmp_path)
    p["pooled"]["effect"] = 0.55
    p["pooled"]["field_spans"] = {"effect": "Hospitalization RR 0.55 (95% CI 0.30 to 0.75)."}
    assert field(verify(p, tmp_path), "pooled.effect")["reason"] == "REFUSED_SPAN_NOT_HELD"


def test_cross_row_ci_assembly_is_refused(tmp_path):
    p = install(tmp_path)
    p["pooled"]["span"] = HELD.split(" Investigator-supplied")[0]
    a = "RR 0.80 (95% CI 0.60 to 0.95)"
    b = "RR 0.55 (95% CI 0.30 to 0.75)"
    p["pooled"]["field_spans"] = {"effect": a, "ci_low": b, "ci_high": a}
    p["pooled"]["ci_low"] = 0.3
    assert field(verify(p, tmp_path), "pooled.effect")["reason"] == "REFUSED_MIXED_ESTIMATE_BINDINGS"


@pytest.mark.parametrize("kind", ["changed_bytes", "proposal_hash", "self_rehashed"])
def test_sha_mismatch_rejects_whole_file(tmp_path, kind):
    p = install(tmp_path)
    if kind == "proposal_hash":
        p["document_sha256"] = "0" * 64
    else:
        raw = (HELD + " changed").encode()
        (tmp_path / p["document_ref"]).write_bytes(raw)
        if kind == "self_rehashed":
            p["document_sha256"] = hashlib.sha256(raw).hexdigest()
    got = verify(p, tmp_path)
    assert got["status"] == "rejected" and got["accepted"] is None
    assert got["fields"] and all(f["status"] == "rejected" for f in got["fields"])


@pytest.mark.parametrize("kind", ["wrong_pmid", "unheld", "missing", "outside_cache", "ambiguous"])
def test_source_contract(tmp_path, kind):
    p = install(tmp_path)
    path = tmp_path / "cache/plant/comparators.json"
    panels = json.loads(path.read_text())
    if kind == "wrong_pmid":
        p["comparator_pmid"] = "12345680"
    elif kind == "unheld":
        panels[0]["held"] = False
    elif kind == "missing":
        (tmp_path / p["document_ref"]).unlink()
    elif kind == "outside_cache":
        p["document_ref"] = "topics/plant.json"
        panels[0]["document_ref"] = p["document_ref"]
    else:
        panels.append(deepcopy(panels[0]))
    path.write_text(json.dumps(panels), encoding="utf-8")
    assert verify(p, tmp_path)["accepted"] is None


def test_citation_pmid_is_supported_without_trusting_panel_slug(tmp_path):
    p = install(tmp_path)
    path = tmp_path / "cache/plant/comparators.json"
    panels = json.loads(path.read_text())
    panels[0].update(id="author-year", citation="Comparator; PMID 12345679")
    path.write_text(json.dumps(panels), encoding="utf-8")
    assert verify(p, tmp_path)["status"] == "accepted"


@pytest.mark.parametrize("change", [lambda p: p.update(trials={}),
    lambda p: p["pooled"].update(unrecognized_number=42),
    lambda p: p["pooled"].update(field_spans=[]),
    lambda p: p.update(trial_set_scope="trust_me"),
    lambda p: p.pop("scope_note")])
def test_malformed_proposal_is_explicitly_refused(tmp_path, change):
    p = install(tmp_path)
    change(p)
    assert verify(p, tmp_path)["reason"].startswith("REFUSED_")


def test_relayed_is_not_data(tmp_path):
    p = install(tmp_path)
    r = {k: None for k in TRIAL}
    r.update(label="BETA", n_1=40, span="Investigator-supplied BETA n_1=40.")
    p["trials"] = [r]
    got = verify(p, tmp_path)
    assert field(got, "trials.0.n_1")["reason"] == "REFUSED_RELAYED_NOT_DATA"
    assert got["accepted"]["trials"][0]["n_1"] is None


def test_count_semantics_and_impossible_arm(tmp_path):
    text = HELD + " GAMMA events_1=30 n_1=20."
    p = install(tmp_path, text)
    r = {k: None for k in TRIAL}
    r.update(label="GAMMA", events_1=30, n_1=20, span="GAMMA events_1=30 n_1=20.")
    p["trials"] = [r]
    assert field(verify(p, tmp_path), "trials.0.n_1")["reason"] == "REFUSED_EVENTS_EXCEED_N"
    p = proposal(text)
    p["trials"][0]["events_1"] = 6  # printed, but it is the other arm
    assert field(verify(p, tmp_path), "trials.0.events_1")["status"] == "rejected"


def test_interval_order_and_ratio_domain(tmp_path):
    text = HELD + " Bad RR 0.80 (95% CI 0.90 to 0.70). Negative RR 0.80 (95% CI -0.20 to 0.90)."
    p = install(tmp_path, text)
    for s in ("RR 0.80 (95% CI 0.90 to 0.70)", "RR 0.80 (95% CI -0.20 to 0.90)"):
        p["pooled"] = dict(k=None, **parse_estimate(s), span=s)
        assert field(verify(p, tmp_path), "pooled.effect")["status"] == "rejected"


@pytest.mark.parametrize("span,expected", [
    ("RR¼0.39, 95% CI 0.27 to 0.56", ("RR", 0.39, 0.27, 0.56)),
    ("ORs were 0.83 (95% CI, 0.74-0.92)", ("ORs", 0.83, 0.74, 0.92)),
    ("WMD) = 7.06 minutes [95% CI: 4.37 to 9.75]", ("WMD", 7.06, 4.37, 9.75)),
    ("MD −2.99 (−5.10 to −0.89)", ("MD", -2.99, -5.10, -0.89)),
    ("0·81 [0·66–1·00]", (None, 0.81, 0.66, 1.0))])
def test_printed_numeric_grammars(span, expected):
    got = parse_estimate(span)
    assert tuple(got.get(k) for k in ("measure", "effect", "ci_low", "ci_high")) == expected


def test_ambiguous_estimates_abstain_and_correct_negative():
    a = "RR 0.80 (95% CI 0.60 to 0.95)"
    b = "RR 0.70 (95% CI 0.40 to 0.90)"
    assert parse_estimate(a + " " + b) == {}
    assert parse_estimate(a)["effect"] == 0.8


def test_records_json_cannot_launder_another_pmid(tmp_path):
    p = install(tmp_path)
    data = {"records": [{"id": "12345679", "id_type": "pmid", "abstract": "Comparator abstract only."},
                        {"id": "12345678", "id_type": "pmid", "abstract": HELD}]}
    raw = json.dumps(data).encode()
    p.update(document_ref="cache/plant/records.json", document_sha256=hashlib.sha256(raw).hexdigest())
    (tmp_path / p["document_ref"]).write_bytes(raw)
    (tmp_path / "cache/plant/comparators.json").write_text(json.dumps([dict(id="12345679", held=True,
        document_ref=p["document_ref"], document_sha256=p["document_sha256"])]), encoding="utf-8")
    assert field(verify(p, tmp_path), "pooled.effect")["reason"] == "REFUSED_SPAN_OUTSIDE_COMPARATOR_RECORD"


def test_adapter_never_reintroduces_rejected_fields(tmp_path):
    p = install(tmp_path)
    p["trials"][0]["effect"] = 0.55
    got = to_comparator(p, tmp_path)
    assert got["trial_set"][0]["effect"]["value"] is None
    assert got["trial_set"][0]["outcome"]["value"] == "Mortality"
    p["trial_set_scope"] = "included_studies_only"
    assert to_comparator(p, tmp_path)["trial_set"][0]["outcome"]["value"] is None
    assert to_comparator(p, tmp_path)["membership_complete"] is False


def test_complete_declaration_requires_accepted_unique_full_set(tmp_path):
    p = install(tmp_path, HELD + " GAMMA NCT00000002: Mortality.")
    p["trial_set_complete"] = True
    # One accepted row cannot certify a printed two-trial set.
    assert not to_comparator(p, tmp_path)["membership_complete"]
    p["trials"].append(deepcopy(p["trials"][0]))
    assert not to_comparator(p, tmp_path)["membership_complete"]
    p["trials"][1] = {k: None for k in TRIAL}
    # BETA's only held span is RELAYED, and cannot complete the set.
    p["trials"][1].update(label="BETA", span="Investigator-supplied BETA n_1=40.")
    assert not to_comparator(p, tmp_path)["membership_complete"]
    # A second independent printed label is the valid negative control.
    p["trials"][1].update(label="GAMMA", span="GAMMA NCT00000002: Mortality.")
    assert to_comparator(p, tmp_path)["membership_complete"]


def test_corpus_proposals_replay_without_rejections():
    paths = sorted((ROOT / "evidence/g1_proposals").glob("*.json"))
    assert paths
    for p in paths:
        v = verify(json.loads(p.read_text(encoding="utf-8")))
        assert v["status"] == "accepted", (p.name, v)


def test_census_contract_on_one_topic_and_registry_alias_negative(tmp_path):
    from scripts.g1_proposal_census import census, link_for_comparison
    p = install(tmp_path)
    (tmp_path / "evidence/g1_proposals").mkdir(parents=True)
    (tmp_path / "evidence/g1_proposals/plant.json").write_text(json.dumps(p), encoding="utf-8")
    (tmp_path / "docs/reviews/plant").mkdir(parents=True)
    review = {"outcomes": [{"name": "Mortality", "primary": True, "result": {"k": 1},
                           "trials": [{"label": "ALPHA"}]}]}
    (tmp_path / "docs/reviews/plant/review.json").write_text(json.dumps(review), encoding="utf-8")
    out = census(tmp_path)
    assert out["accepted_pooled_k"]["n_of_N"] == "1 of 1"
    assert out["K_MATCH"]["n_of_N"] == "0 of 1"
    f = out["rules"]["field_accepted"]
    assert f["n"] == f["N"] == len(f["items"])
    assert out == census(tmp_path)
    c = to_comparator(p, tmp_path)
    c["trial_set"][0]["registration"] = None
    registry = {n: {"raw": {"studies": [{"nct_id": n, "acronym": "ALPHA"}]}}
                for n in ("NCT00000001", "NCT00000002")}
    _, linked, links = link_for_comparison(review, c, registry)
    assert linked["trial_set"][0]["registration"] is None
    assert links == []


def pre_fix_examples():
    """Executed base behavior: fact() trusts callers; extract() already hashes disk.

    This is not a claim that the old disk extractor accepts a mismatched hash.
    It shows the missing proposal replay boundary using the same planted items.
    """
    from harness.comparator_extract import fact, parse_text
    p = proposal()
    cases = {
        "fabricated_span": (0.8, p["pooled"]["span"] + " invented tail"),
        "number_elsewhere_in_document": (0.55, p["pooled"]["span"]),
        "swapped_effect_and_ci": (0.95, p["pooled"]["span"]),
        "relayed": (40, "Investigator-supplied BETA n_1=40."),
        "correct_negative": (0.8, p["pooled"]["span"]),
    }
    return {"base_fact_on_same_plants": {k: fact(v, span) for k, (v, span) in cases.items()},
            "base_parser_on_held_text": parse_text(HELD, {"slug": "plant", "primary_outcome": {"name": "Mortality"}})["pooled"],
            "hash_boundary": "fact(value, span) has no document/hash argument; base extract(slug, root) already rejects changed held bytes (tested separately)."}


def test_base_hash_boundary_already_refuses_changed_bytes(tmp_path):
    from harness.comparator_extract import extract
    p = install(tmp_path)
    (tmp_path / p["document_ref"]).write_bytes((HELD + " changed").encode())
    with pytest.raises(ValueError, match="REFUSED_SHA256_MISMATCH"):
        extract("plant", tmp_path)
