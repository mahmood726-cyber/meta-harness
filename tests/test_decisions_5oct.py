"""PLANTS for the 5 Oct decisions (captain, under Mahmood's delegation). Decision 1 (HR vs RR: a named
MEASURE_DIFFERENCE passes only on the same conclusion) is planted in tests/test_result_agrees_class.py.
  2/3  a trial is named out of scope only when our REGISTERED protocol's own words exclude it, both spans verbatim
  4    double-blind required and no held source states it -> ELIGIBILITY_UNVERIFIABLE: not counted, not named
  5    a comparator row contradicting the trial's own report is compared on the trial's own values, finding kept
  6    a model prompt carries a full text only when its copy is marked open"""
import json
import os
import sys

from harness import secondary_meta as sm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_tracker as gt  # noqa: E402
import secondary_meta_build as smb  # noqa: E402

PROTO = ("## Eligibility - Include a record iff all hold: - **I2** - adult chronic kidney disease population, judged from "
         "title; Exclude: - **X2** - wrong population (for example heart failure, or another non-CKD population); - **X3** "
         "- wrong intervention/comparison; ## Outcomes")


def _adj(monkeypatch, entry, held_ok=True):
    monkeypatch.setattr(gt, "_ADJ", {"__control_dec::PMID 99999931": entry})
    monkeypatch.setattr(gt, "protocol_text", lambda slug: gt._ws(PROTO))
    monkeypatch.setattr(gt, "span_is_verbatim", lambda slug, pmid, sp: held_ok)


def test_a_trial_is_named_only_with_the_registered_protocols_own_words_and_its_own_span(monkeypatch):
    entry = {"decision": "d", "axis": "POPULATION",
             "protocol_spans": ["wrong population (for example heart failure, or another non-CKD population)"],
             "trial_span": {"pmid": "99999931", "field": "abstract", "text": "patients with type 2 diabetes"}}
    _adj(monkeypatch, entry)
    x = {"family": "PMID 99999931"}
    d = gt.scope_difference(x, {}, "__control_dec")
    assert d["kind"] == "PROTOCOL_SCOPE_DIFFERENCE" and d["protocol_spans"] == entry["protocol_spans"]
    assert d["span"]["text"] == "patients with type 2 diabetes" and d["rule_id"].startswith("PROTOCOL_TEXT:")
    # a protocol span that is not the registered protocol's words: not named, stays eligible, reason recorded
    _adj(monkeypatch, dict(entry, protocol_spans=["phase 2 and dose-finding trials are excluded"]))
    x = {"family": "PMID 99999931"}
    assert gt.scope_difference(x, {}, "__control_dec") is None
    assert x["scope_adjudication_refused"] == "PROTOCOL_SPAN_NOT_VERBATIM_IN_REGISTERED_PROTOCOL"
    # the trial's span not in its held record: not named either
    _adj(monkeypatch, entry, held_ok=False)
    x = {"family": "PMID 99999931"}
    assert gt.scope_difference(x, {}, "__control_dec") is None
    assert x["scope_adjudication_refused"] == "TRIAL_SPAN_NOT_VERBATIM_IN_HELD_RECORD"


def test_the_protocols_own_bullet_is_quoted_for_a_screen_rule(monkeypatch):
    monkeypatch.setattr(gt, "protocol_text", lambda slug: gt._ws(PROTO))
    sp = gt.protocol_rule_span("__control_dec", "X2")
    assert sp["text"].startswith("wrong population (for example heart failure") and "X3" not in sp["text"]
    assert gt.protocol_rule_span("__control_dec", "X9") is None


def test_every_registered_adjudication_verifies_against_the_real_protocol_and_held_record():
    adj = json.load(open(os.path.join(ROOT, "registry", "scope_adjudications.json"), encoding="utf-8"))["adjudications"]
    assert adj
    for key, a in adj.items():
        slug = key.split("::", 1)[0]
        assert gt.protocol_spans_ok(slug, a["protocol_spans"]), key
        ts = a["trial_span"]
        assert gt.span_is_verbatim(slug, ts["pmid"], {"field": ts["field"], "text": ts["text"]}), key


def test_double_blind_required_and_unstated_is_unverifiable_not_counted_not_named(monkeypatch):
    monkeypatch.setattr(gt, "exclusion_audit_class", lambda slug, pmid: ("INSUFFICIENT_RECORD", "BLINDING_NOT_STATED"))
    x = {"in_our_pool": False, "seeded_funnel": {"stage": "SCREENED_OUT", "rule_id": "X-DESIGN", "pmid": "99999932"}}
    cfg = {"include": {"design_double_blind": True}}
    se = gt.screen_eligibility(x, None, "99999932", [], slug="__control_dec", cfg=cfg)
    assert se["state"] == "ELIGIBILITY_UNVERIFIABLE"
    counted = {"in_our_pool": False, "route": "SECONDARY_SINGLE", "g1_countable": True, "scope_difference": None,
               "screen_eligibility": se}
    assert not gt.is_matched(counted)
    # a protocol that does not require blinding: an ordinary exclusion
    assert gt.screen_eligibility(x, None, "99999932", [], slug="__control_dec", cfg={"include": {}})["state"] == "NOT_ELIGIBLE"
    # the audit established the design (not 'unstated'): an ordinary exclusion too
    monkeypatch.setattr(gt, "exclusion_audit_class", lambda slug, pmid: ("TRUE_SCOPE_DIFFERENCE", "OPEN_LABEL"))
    assert gt.screen_eligibility(x, None, "99999932", [], slug="__control_dec", cfg=cfg)["state"] == "NOT_ELIGIBLE"


def test_tsutsui_is_a_screener_error_established_by_its_registration():
    # captain, 5 Oct: Tsutsui (PARALLEL-HF) is a screener error. The record and held full text are silent on blinding,
    # its REGISTRATION (NCT02468232, linked by the title's acronym, unique in AACT) states RANDOMIZED + QUADRUPLE masking.
    # From COMMITTED inputs only (exclusion audit, topic config, outputs/k_gap/aact_designs.json).
    slug, pmid = "sacubitril-valsartan-hfref", "33731544"
    cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    x = {"in_our_pool": False, "seeded_funnel": {"stage": "SCREENED_OUT", "rule_id": "X-DESIGN", "pmid": pmid}}
    se = gt.screen_eligibility(x, None, pmid, [], slug=slug, cfg=cfg)
    assert se["state"] == "ELIGIBLE" and se["basis"] == "SCREENER_ERROR:REGISTRY_STATES_BLINDING"
    assert se["span"]["nct"] == "NCT02468232" and "QUADRUPLE" in se["span"]["text"] and "Double-blind" in se["span"]["text"]


def test_a_registration_decides_a_blinding_silent_exclusion_and_silence_still_fails_closed(monkeypatch):
    monkeypatch.setattr(gt, "exclusion_audit_class", lambda slug, pmid: ("INSUFFICIENT_RECORD", "BLINDING_NOT_STATED"))
    monkeypatch.setattr(gt, "_DESIGNS", {
        "99999971": {"state": "RECORDED", "nct": "NCT1", "allocation": "RANDOMIZED", "masking": "QUADRUPLE", "snapshot": "s"},
        "99999972": {"state": "RECORDED", "nct": "NCT2", "allocation": "RANDOMIZED", "masking": "NONE", "snapshot": "s"},
        "99999973": {"state": "NO_UNIQUE_REGISTRATION", "ncts": []}})
    cfg = {"include": {"design_double_blind": True}}

    def se(p):
        x = {"in_our_pool": False, "seeded_funnel": {"stage": "SCREENED_OUT", "rule_id": "X-DESIGN", "pmid": p}}
        return gt.screen_eligibility(x, None, p, [], slug="__control_dec", cfg=cfg)["state"]
    assert se("99999971") == "ELIGIBLE"
    assert se("99999972") == "NOT_ELIGIBLE"                         # registered open-label: the exclusion stands
    assert se("99999973") == "ELIGIBILITY_UNVERIFIABLE"              # no unique registration: still fails closed


def _crow(state, side, **v):
    r = sm.SecondaryRow(meta_pmid="11111111", meta_doi="", location={}, source_digest="", provenance="COMPARATOR_ROW",
                        trial_label="Imazio", measure="RR", outcome_definition="", effect="0.66", lower="0.45", upper="0.96")
    r.state, r.verification = state, ({"which_side": side} if side else None)
    for k, x in v.items():
        setattr(r, k, x)
    return r


def test_a_comparator_row_contradicted_by_the_trials_report_is_compared_on_the_reports_values():
    prim = {"measure": "RR", "events_t": 61, "n_t": 180, "events_c": 75, "n_c": 180}
    r = gt.trial_report_in_place_of(_crow(sm.MISMATCH, "SECONDARY_WRONG (primary numbers are in the primary's own span)"), prim)
    assert (r.events_t, r.n_t, r.events_c, r.n_c, r.effect) == (61, 180, 75, 180, None)
    assert any(f["finding"] == "COMPARATOR_ROW_DIFFERS_FROM_TRIAL_REPORT" for f in r.findings)
    # the evidence does not point at the comparator, or the row agrees: unchanged
    same = _crow(sm.MISMATCH, "PRIMARY_WRONG")
    assert gt.trial_report_in_place_of(same, prim) is same
    ok = _crow(sm.VERIFIED, None)
    assert gt.trial_report_in_place_of(ok, prim) is ok
    # the report gives another measure (an HR): never converted, row unchanged
    hr = {"measure": "HR", "effect": "0.80", "lower": "0.6", "upper": "1.0"}
    row = _crow(sm.MISMATCH, "SECONDARY_WRONG x")
    assert gt.trial_report_in_place_of(row, hr) is row


def test_a_prompt_carries_a_full_text_only_from_a_copy_marked_open():
    lic = {"1": "CC", "2": "PMC_AUTHOR_MANUSCRIPT", "3": "NOT_OPEN"}
    assert smb.prompt_fulltext("1", "FULL", lic) == "FULL"
    assert smb.prompt_fulltext("2", "FULL", lic) == "" and smb.prompt_fulltext("3", "FULL", lic) == ""
    assert smb.prompt_fulltext("4", "FULL", lic) == ""                # unknown licence: not open


def test_no_quarantined_licence_record_is_tracked_or_listed():
    import subprocess
    exc = json.load(open(os.path.join(ROOT, "registry", "record_licence_exceptions.json"), encoding="utf-8"))
    tracked = subprocess.run(["git", "--git-dir=.git", "--work-tree=.", "ls-files", "evidence/model_calls",
                              "registry/model_calls"], cwd=ROOT, capture_output=True, text=True,
                             stdin=subprocess.DEVNULL).stdout
    for rid in exc.get("resolved") or {}:
        assert rid not in tracked, f"{rid}: a quarantined record is tracked again"


def test_every_registered_adjudication_renders_in_the_tracker_table():
    # 5 Oct: the PROTOCOL_TEXT adjudication record lacked 'screen_reason' / 'registered_eligibility', and the table
    # renderer (which needs both) crashed the tracker's markdown on the first full regeneration
    adj = json.load(open(os.path.join(ROOT, "registry", "scope_adjudications.json"), encoding="utf-8"))["adjudications"]
    for key in adj:
        slug, fam = key.split("::", 1)
        d = gt.scope_adjudication(slug, {"family": fam})
        assert d, key
        line = gt.scope_difference_line(dict(d, trial=fam))
        assert d["span"]["text"] in line and "PROTOCOL_TEXT:" in line


def test_every_named_difference_kind_renders_in_the_tracker_table():
    # SAME_TRIAL_AS_ANOTHER_UNIT fell into the registry-gate branch ('gate' KeyError) and crashed the table: every kind
    # the tracker emits must render, checked over the real per-topic files and one planted record per non-registry kind
    import glob
    seen = set()
    for f in glob.glob(os.path.join(ROOT, "outputs", "k_gap", "g1", "*.json")):
        for d in json.load(open(f, encoding="utf-8")).get("named_differences") or []:
            assert gt.named_difference_line(d).startswith("- NAMED " + d["kind"]), (f, d["kind"])
            seen.add(d["kind"])
    same = {"kind": "SAME_TRIAL_AS_ANOTHER_UNIT", "trial": "PLATO substudy", "rule_id": "G1-ONE-TRIAL-ONE-UNIT",
            "same_trial_as": "PLATO", "span": {"text": "NCT00391872"}, "span_source": "registry", "pmid": "1",
            "protocol_rule": "one trial, one unit"}
    assert "the same trial as PLATO" in gt.named_difference_line(same)
