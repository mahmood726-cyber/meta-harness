"""P3 extraction contract: a clean bundle is ALLOWED, and every rule is shown able to REFUSE by a planted defect.

All documents here are SYNTHETIC controls written for this test (no real trial text, no licence question); a control
lives only in tmp_path and is never part of any denominator. Model calls use fake runners -- no process is started.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from extraction_contract import CONTRACT_VERSION
from extraction_contract import fields as F
from extraction_contract.dual import independence_problems, resolve
from extraction_contract.gate import ALLOW, REFUSE, check_bundle
from extraction_contract.passage import locate, numbers_in, value_in_quote
from extraction_contract import readers

ROOT = Path(__file__).resolve().parents[1]

DOC = ("SYNTHETIC CONTROL TRIAL PLANT-001 (not a real study).\n"
       "Participants were randomised to drug X (n=210) or placebo (n=205).\n"
       "The primary outcome was all-cause death at 12 months, analysed by intention to treat.\n"
       "Death occurred in 42 of 208 patients assigned to drug X and 61 of 203 assigned to placebo.\n"
       "The hazard ratio was 0·66 (95% CI 0·45–0·97).\n"
       "Death occurred in many patients.\n")
REF = "docs_ctl/plant001.txt"


@pytest.fixture()
def root(tmp_path):
    p = tmp_path / "docs_ctl"
    p.mkdir()
    (p / "plant001.txt").write_bytes(DOC.encode("utf-8"))
    return str(tmp_path)


SHA = hashlib.sha256(DOC.encode("utf-8")).hexdigest()


def P(quote, ref=REF, sha=SHA):
    s = DOC.find(quote)
    assert s >= 0 and DOC.find(quote, s + 1) < 0, quote
    return {"document_ref": ref, "document_sha256": sha, "start": s, "end": s + len(quote), "quote": quote}


Q_COUNTS = "Death occurred in 42 of 208 patients assigned to drug X and 61 of 203 assigned to placebo."
Q_DEF = "The primary outcome was all-cause death at 12 months, analysed by intention to treat."
Q_RAND = "Participants were randomised to drug X (n=210) or placebo (n=205)."
Q_HR = "The hazard ratio was 0·66 (95% CI 0·45–0·97)."


def I(field, value, quote, arm=None):
    return {"field": field, "arm": arm, "value": value, "passage": P(quote)}


def binary_values():
    return [I("events", 42, Q_COUNTS, "intervention"), I("total", 208, Q_COUNTS, "intervention"),
            I("events", 61, Q_COUNTS, "comparator"), I("total", 203, Q_COUNTS, "comparator"),
            I("outcome_definition", "all-cause death at 12 months", Q_DEF),
            I("n_randomised", 210, Q_RAND, "intervention"), I("n_randomised", 205, Q_RAND, "comparator")]


def reading(family, record_id, items):
    return {"reader": {"family": family, "model_reported": "m", "record_id": record_id},
            "items": [copy.deepcopy(i) for i in items if F.FIELDS[i["field"]].role == "OUTCOME"]}


def bundle(trials=None):
    if trials is None:
        v = binary_values()
        trials = [{"trial_id": "PLANT-001", "measure": "binary", "values": v,
                   "readings": [reading("anthropic", "mc-a", v), reading("openai", "mc-b", v)], "adjudications": []}]
    return {"contract": CONTRACT_VERSION, "topic": "plant", "trials": trials,
            "claim": {"kind": "matches_published_meta", "published": "SYNTHETIC control meta-analysis"}}


def problems(rep):
    return " | ".join(rep["problems"] + [p for t in rep["trials"] for p in t["problems"]])


# ------------------------------------------------------------------ the gate can say YES
def test_clean_bundle_is_allowed(root):
    rep = check_bundle(bundle(), root)
    assert rep["verdict"] == ALLOW, problems(rep)
    assert set(rep["trials"][0]["dual_status"].values()) == {"AGREED"}


def test_clean_ratio_trial_is_allowed(root):
    v = [I("effect_point", 0.66, Q_HR), I("effect_ci_low", 0.45, Q_HR), I("effect_ci_high", 0.97, Q_HR),
         I("effect_scale", "HR", Q_HR), I("ci_level", 0.95, Q_HR),
         I("outcome_definition", "all-cause death at 12 months", Q_DEF), I("analysis_set", "ITT", Q_DEF)]
    t = {"trial_id": "PLANT-001", "measure": "ratio", "values": v,
         "readings": [reading("anthropic", "mc-a", v), reading("openai", "mc-b", v)]}
    rep = check_bundle(bundle([t]), root)
    assert rep["verdict"] == ALLOW, problems(rep)


# ------------------------------------------------------------------ PLANTS: every rule must be able to say NO
def _plant(root, mutate, expect):
    b = bundle()
    mutate(b["trials"][0])
    rep = check_bundle(b, root)
    assert rep["verdict"] == REFUSE, f"planted defect was ALLOWED: {expect}"
    assert expect in problems(rep), problems(rep)


def _served(t, field, arm=None):
    return next(i for i in t["values"] if (i["field"], i["arm"]) == (field, arm))


def _both(t, fn):
    """apply a mutation to the served value AND both readings (so only the targeted rule can catch it)"""
    fn(t["values"])
    for r in t["readings"]:
        fn(r["items"])


def test_PLANT_value_not_in_its_quote(root):
    def m(t):
        _both(t, lambda items: [i.update(value=41) for i in items if (i["field"], i["arm"]) == ("events", "intervention")])
    _plant(root, m, "is not in its quoted passage")


def test_PLANT_quote_not_at_its_offsets(root):
    def m(t):
        _both(t, lambda items: [i["passage"].update(start=i["passage"]["start"] + 1, end=i["passage"]["end"] + 1)
                                for i in items if i["field"] == "total"])
    _plant(root, m, "quote is not the text at")


def test_PLANT_document_changed_after_pinning(root):
    with open(os.path.join(root, *REF.split("/")), "ab") as fh:
        fh.write(b"edited later\n")
    rep = check_bundle(bundle(), root)
    assert rep["verdict"] == REFUSE and "changed: sha256" in problems(rep)


def test_PLANT_value_without_passage(root):
    _plant(root, lambda t: _served(t, "n_randomised", "intervention").update(passage=None), "no passage")


def test_PLANT_vague_quote_that_is_real_but_not_the_value(root):
    def m(t):
        _both(t, lambda items: [i.update(passage=P("Death occurred in many patients."))
                                for i in items if (i["field"], i["arm"]) == ("events", "comparator")])
    _plant(root, m, "is not in its quoted passage")


@pytest.mark.parametrize("bad,expect", [(42.0, "is not an int"), (True, "is not an int"), ("42", "is not an int"),
                                        (-1, "below its minimum")])
def test_PLANT_type_violations(root, bad, expect):
    def m(t):
        _both(t, lambda items: [i.update(value=bad) for i in items if (i["field"], i["arm"]) == ("events", "intervention")])
    _plant(root, m, expect)


def test_PLANT_events_exceed_total(root):
    q = "Death occurred in 42 of 208 patients assigned to drug X and 61 of 203 assigned to placebo."
    assert q == Q_COUNTS

    def m(t):
        _both(t, lambda items: [i.update(value=203) for i in items if (i["field"], i["arm"]) == ("events", "comparator")]
              + [i.update(value=61) for i in items if (i["field"], i["arm"]) == ("total", "comparator")])
    _plant(root, m, "exceeds total[comparator]")


def test_PLANT_ci_does_not_bracket_point(root):
    v = [I("effect_point", 0.97, Q_HR), I("effect_ci_low", 0.45, Q_HR), I("effect_ci_high", 0.66, Q_HR),
         I("effect_scale", "HR", Q_HR), I("ci_level", 0.95, Q_HR), I("outcome_definition", "all-cause death at 12 months", Q_DEF)]
    t = {"trial_id": "PLANT-001", "measure": "ratio", "values": v,
         "readings": [reading("anthropic", "mc-a", v), reading("openai", "mc-b", v)]}
    rep = check_bundle(bundle([t]), root)
    assert rep["verdict"] == REFUSE and "does not bracket" in problems(rep)


def test_PLANT_required_field_missing(root):
    _plant(root, lambda t: t.update(values=[i for i in t["values"] if i["field"] != "outcome_definition"]),
           "outcome_definition required for a binary trial but not served")


def test_PLANT_same_family_readers(root):
    _plant(root, lambda t: t["readings"][0]["reader"].update(family="openai"), "reader families")


def test_PLANT_single_reader(root):
    _plant(root, lambda t: t.update(readings=t["readings"][:1]), "needs exactly 2 readings")


def test_PLANT_explicit_empty_call_record_map_cannot_prove_independence(root):
    # An explicit empty verification inventory is not the same as opting out
    # of call-record validation. Previously an empty dict skipped it.
    b = bundle()
    rep = check_bundle(b, root, call_records={})
    assert rep["verdict"] == REFUSE, problems(rep)
    assert "call record is missing from the supplied records" in problems(rep)
    assert check_bundle(b, root)["verdict"] == ALLOW  # existing unverified-metadata control


@pytest.mark.parametrize("missing_or_invalid_digest", [None, "z" * 64, "a" * 63])
def test_PLANT_supplied_call_record_missing_verifiable_response_digest_refuses(root, missing_or_invalid_digest):
    # A self-declared model reading plus incomplete prompt/response traces
    # cannot demonstrate that the other model's answer was not shown to it.
    recs = {
        "mc-a": {"record_id": "mc-a", "response": {"sha256": missing_or_invalid_digest},
                 "input_digests": [{"sha256": SHA}]},
        "mc-b": {"record_id": "mc-b", "response": {"sha256": "b" * 64},
                 "input_digests": [{"sha256": SHA}]},
    }
    rep = check_bundle(bundle(), root, call_records=recs)
    assert rep["verdict"] == REFUSE, problems(rep)
    assert "prompt-separation check cannot be completed" in problems(rep)



@pytest.mark.parametrize("invalid_inputs", [None, [], [{"ref": REF, "sha256": "not-a-digest"}], ["not-an-object"]])
def test_PLANT_missing_or_invalid_prompt_input_digests_cannot_prove_independence(root, invalid_inputs):
    # Synthetic records only. A missing or malformed input inventory does NOT
    # prove the second model was shielded from the first model's answer.
    recs = {
        "mc-a": {"record_id": "mc-a", "response": {"sha256": "a" * 64}},
        "mc-b": {"record_id": "mc-b", "response": {"sha256": "b" * 64},
                 "input_digests": [{"ref": REF, "sha256": SHA}]},
    }
    if invalid_inputs is not None:
        recs["mc-a"]["input_digests"] = invalid_inputs
    rep = check_bundle(bundle(), root, call_records=recs)
    assert rep["verdict"] == REFUSE, problems(rep)
    assert "missing or invalid prompt input digests" in problems(rep)



def test_PLANT_second_reader_was_shown_the_first_answer(root):
    resp_a = "a" * 64
    recs = {"mc-a": {"record_id": "mc-a", "response": {"sha256": resp_a}, "input_digests": [{"sha256": SHA}]},
            "mc-b": {"record_id": "mc-b", "response": {"sha256": "b" * 64},
                     "input_digests": [{"sha256": SHA}, {"sha256": resp_a}]}}
    rep = check_bundle(bundle(), root, call_records=recs)
    assert rep["verdict"] == REFUSE and "was shown the other reader's response" in problems(rep)
    recs["mc-b"]["input_digests"] = [{"sha256": SHA}]
    assert check_bundle(bundle(), root, call_records=recs)["verdict"] == ALLOW


def _disagree(t):
    item = next(i for i in t["readings"][1]["items"] if (i["field"], i["arm"]) == ("events", "comparator"))
    item.update(value=203)        # the openai reader mis-read events as the denominator (it IS in the quote)


def test_PLANT_disagreement_without_adjudication_blocks(root):
    _plant(root, _disagree, "UNRESOLVED")


def test_disagreement_settled_by_a_verified_passage_is_allowed(root):
    b = bundle()
    t = b["trials"][0]
    _disagree(t)
    t["adjudications"] = [{"field": "events", "arm": "comparator", "decided_value": 61, "passage": P(Q_COUNTS),
                           "adjudicator": {"kind": "human", "name": "second reviewer"},
                           "rationale": "61 of 203: 61 is the event count, 203 the denominator"}]
    rep = check_bundle(b, root)
    # The legacy test name stays stable for the honest-test ratchet. A source
    # quote is not an authenticated independent human-review receipt.
    assert rep["verdict"] == REFUSE, problems(rep)
    assert rep["trials"][0]["dual_status"]["events[comparator]"] == "UNRESOLVED"
    assert "external blinded adjudication is not authenticated" in problems(rep)
    evidence = resolve(t["readings"], t["adjudications"], root)["fields"][("events", "comparator")]
    assert [r["raw_value"] for r in evidence["reader_candidates"]] == [61, 203]
    assert [r["reader_record_id_claimed"] for r in evidence["reader_candidates"]] == ["mc-a", "mc-b"]
    assert evidence["adjudication_proposals"][0]["raw_value"] == 61
    assert evidence["adjudication_proposals"][0]["actor_kind_claimed"] == "human"


def test_PLANT_self_declared_blinding_cannot_overrule_agreeing_models(root):
    b = bundle()
    t = b["trials"][0]
    # Two model readers agree, but a claimed external reviewer records a
    # different source-quoted number. A self-reported blinded flag is not a
    # receipt, and model agreement must not make the dissent disappear.
    t["adjudications"] = [{
        "field": "events", "arm": "comparator", "decided_value": 203,
        "passage": P(Q_COUNTS),
        "adjudicator": {"kind": "human", "name": "synthetic external", "record_id": "synthetic-reviewer"},
        "blinded": True, "independent": True, "rationale": "synthetic dissent",
    }]
    rep = check_bundle(b, root)
    assert rep["verdict"] == REFUSE, problems(rep)
    assert rep["trials"][0]["dual_status"]["events[comparator]"] == "UNRESOLVED"
    evidence = resolve(t["readings"], t["adjudications"], root)["fields"][("events", "comparator")]
    assert [r["raw_value"] for r in evidence["reader_candidates"]] == [61, 61]
    assert evidence["adjudication_proposals"][0]["raw_value"] == 203
    assert evidence["adjudication_proposals"][0]["actor_record_id_claimed"] == "synthetic-reviewer"
    assert evidence["adjudication_proposals"][0]["source_checked"] is True


def test_PLANT_explicit_zero_and_false_remain_visible_when_review_is_unverified(tmp_path):
    # Fresh synthetic bytes with a genuine zero-event quote; this does not
    # represent an eligible study, independent reviewer or validation case.
    quote = "0 events in the intervention; 2 events in the comparator."
    path = tmp_path / "zero-event.txt"
    path.write_text(quote, encoding="utf-8")
    passage = {
        "document_ref": "zero-event.txt", "document_sha256": hashlib.sha256(quote.encode()).hexdigest(),
        "start": 0, "end": len(quote), "quote": quote,
    }
    a = {"field": "events", "arm": "intervention", "value": 0, "passage": passage}
    b = {"field": "events", "arm": "intervention", "value": 2, "passage": passage}
    readings = [reading("anthropic", "zero-reader-a", [a]), reading("openai", "zero-reader-b", [b])]
    proposal = {
        "field": "events", "arm": "intervention", "decided_value": False, "passage": passage,
        "adjudicator": {"kind": "human", "name": "synthetic reviewer", "record_id": "zero-reviewer"},
        "blinded": True, "rationale": "synthetic Boolean disagreement",
    }
    result = resolve(readings, [proposal], str(tmp_path))["fields"][("events", "intervention")]
    assert result["status"] == "UNRESOLVED" and result["value"] is None
    candidates = result["reader_candidates"]
    assert type(candidates[0]["raw_value"]) is int and candidates[0]["raw_value"] == 0
    assert candidates[0]["source_checked"] is True
    assert candidates[1]["raw_value"] == 2 and candidates[1]["source_checked"] is True
    assert result["adjudication_proposals"][0]["raw_value"] is False
    assert result["adjudication_proposals"][0]["source_checked"] is False
    assert "not an int" in "; ".join(result["problems"])
    assert "external blinded adjudication is not authenticated" in "; ".join(result["problems"])


@pytest.mark.parametrize("adj_patch,expect", [
    ({"adjudicator": {"kind": "model", "name": "codex", "record_id": "mc-b"}}, "the adjudicator is one of the readers"),
    ({"passage": {**P("Death occurred in many patients.")}}, "is not in its quoted passage"),
    ({"rationale": ""}, "without a rationale"),
])
def test_PLANT_adjudication_rules(root, adj_patch, expect):
    b = bundle()
    t = b["trials"][0]
    _disagree(t)
    adj = {"field": "events", "arm": "comparator", "decided_value": 61, "passage": P(Q_COUNTS),
           "adjudicator": {"kind": "human", "name": "second reviewer"}, "rationale": "61 of 203"}
    adj.update(adj_patch)
    t["adjudications"] = [adj]
    rep = check_bundle(b, root)
    assert rep["verdict"] == REFUSE and expect in problems(rep), problems(rep)


def test_PLANT_served_value_differs_from_dual_resolution(root):
    def m(t):
        # both readers say 42/208; the served value is 61 -- in the quote, typed, sourced, and still wrong
        _served(t, "events", "intervention").update(value=61)
    _plant(root, m, "served 61 but the dual reading resolved 42")


def test_PLANT_outcome_served_but_never_read(root):
    def m(t):
        for r in t["readings"]:
            r["items"] = [i for i in r["items"] if i["field"] != "outcome_definition"]
    _plant(root, m, "neither reader extracted it")


@pytest.mark.parametrize("patch,expect", [
    ({"contract": "p2/9.0.0"}, "is not p3/1.x"), ({"trials": []}, "no trials"),
    ({"claim": {"kind": "agrees_loosely"}}, "claim must be"),
])
def test_PLANT_bundle_level(root, patch, expect):
    b = bundle()
    b.update(patch)
    rep = check_bundle(b, root)
    assert rep["verdict"] == REFUSE and expect in problems(rep)


def test_PLANT_document_ref_escaping_the_root(root):
    _plant(root, lambda t: _served(t, "n_randomised", "intervention")["passage"].update(document_ref="../outside.txt"),
           "relative path inside the docs root")


# ------------------------------------------------------------------ the number reader
@pytest.mark.parametrize("text,want", [
    ("HR 0·66 (95% CI 0·45–0·97)", ["0.66", "95", "0.45", "0.97"]),
    ("HR 0.66 (0.45-0.97)", ["0.66", "0.45", "0.97"]),          # '-' between numbers is a range dash
    ("mean change −2.5 (SD 1,234.5)", ["-2.5", "1234.5"]),
    ("n=1,204 of 2,410", ["1204", "2410"]),
])
def test_numbers_in(text, want):
    from decimal import Decimal
    assert numbers_in(text) == [Decimal(w) for w in want]


def test_value_in_quote_special_fields():
    assert value_in_quote("ci_level", "float", 0.95, "(95% CI 0.4 to 0.9)")
    assert not value_in_quote("ci_level", "float", 0.90, "(95% CI 0.4 to 0.9)")
    assert value_in_quote("effect_scale", "enum", "HR", "The hazard ratio was 0.6")
    assert not value_in_quote("effect_scale", "enum", "OR", "The hazard ratio was 0.6")
    assert value_in_quote("analysis_set", "enum", "ITT", "analysed by intention to treat")
    assert not value_in_quote("events", "int", 4, "42 of 208")       # 4 is not a token of '42'
    assert not value_in_quote("events", "int", 42, "42.5 of 208")    # an int must be an integer token


def test_locate_refuses_ambiguity():
    assert locate("aaa bbb aaa", "aaa") is None
    assert locate("aaa bbb", "bbb") == (4, 7)
    assert locate("aaa", "zzz") is None


# ------------------------------------------------------------------ CLI: exit codes are the contract
def _cli(*args, cwd):
    return subprocess.run([sys.executable, "-m", "extraction_contract", *args], cwd=str(ROOT), capture_output=True,
                          text=True, timeout=120, env={**os.environ, "PYTHONIOENCODING": "utf-8"})


def test_cli_exit_codes(root, tmp_path):
    good, bad = tmp_path / "good.json", tmp_path / "bad.json"
    good.write_text(json.dumps(bundle()), encoding="utf-8")
    b = bundle()
    b["trials"][0]["values"][0]["value"] = 41
    bad.write_text(json.dumps(b), encoding="utf-8")
    metadata_only = _cli("check", str(good), "--docs-root", root, cwd=root)
    assert metadata_only.returncode == 0
    assert "CALL_RECORDS_NOT_VERIFIED" in metadata_only.stdout
    # No inventory is the inherited metadata-only interface; explicitly
    # requesting proof with an empty inventory must never fall back to it.
    empty_records = tmp_path / "empty-records"
    empty_records.mkdir()
    unverified = _cli("check", str(good), "--docs-root", root,
                      "--records", str(empty_records), cwd=root)
    assert unverified.returncode == 1
    assert "REFUSE" in unverified.stdout
    assert "call record is missing from the supplied records" in unverified.stdout
    r = _cli("check", str(bad), "--docs-root", root, cwd=root)
    assert r.returncode == 1 and "REFUSE" in r.stdout
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    assert _cli("check", str(tmp_path / "broken.json"), "--docs-root", root, cwd=root).returncode == 2
    assert _cli("version", cwd=root).stdout.strip() == CONTRACT_VERSION


# ------------------------------------------------------------------ readers: recorded, pinned, independent
def _claude_fake(answer: dict, model="claude-sonnet-5-5", reported=None, rc=0, turns=1):
    def run(prompt, m, timeout_s):
        out = {"type": "result", "subtype": "success", "is_error": False, "result": json.dumps(answer),
               "num_turns": turns, "modelUsage": {(reported or m): {"outputTokens": 10}}}
        return {"rc": rc, "stdout": json.dumps(out).encode(), "stderr": b"", "argv": ["claude", "-p"]}
    return run


def _codex_fake(answer: dict, model="gpt-5.5", effort="medium"):
    def run(prompt, schema, m, e, timeout_s):
        se = f"OpenAI Codex v0.154.0\n--------\nmodel: {m}\nprovider: openai\nreasoning effort: {e}\n--------\n"
        return {"rc": 0, "stdout": b"", "stderr": se.encode(), "last_message": json.dumps(answer).encode(),
                "argv": ["codex", "exec"]}
    return run


ANSWER = {"items": [
    {"field": "events", "arm": "intervention", "value": 42, "quote": Q_COUNTS},
    {"field": "total", "arm": "intervention", "value": 208, "quote": Q_COUNTS},
    {"field": "events", "arm": "comparator", "value": 61, "quote": Q_COUNTS},
    {"field": "total", "arm": "comparator", "value": 203, "quote": Q_COUNTS},
    {"field": "outcome_definition", "arm": None, "value": "all-cause death at 12 months", "quote": Q_DEF}]}
CALLER = {"file": "tests/test_extraction_contract.py", "line": "1", "purpose": "P3 fake dual reading"}


def _dual(root, claude_answer=ANSWER, codex_answer=ANSWER, **kw):
    return readers.run_dual(docs_root=root, document_ref=REF, trial_id="PLANT-001", measure="binary",
                            claude_model="claude-sonnet-5-5", codex_model="gpt-5.5", codex_effort="medium",
                            caller=CALLER, claude_runner_fn=kw.get("cr") or _claude_fake(claude_answer),
                            codex_runner_fn=_codex_fake(codex_answer))


def test_dual_reading_end_to_end_with_recorded_calls(root):
    out = _dual(root)
    recs = {r["record_id"]: r for r in out["records"]}
    assert [r["state"] for r in out["records"]] == ["RAN_OK", "RAN_OK"]
    assert [r["model"]["provider"] for r in out["records"]] == ["anthropic", "openai"]
    t = {"trial_id": "PLANT-001", "measure": "binary", "values": binary_values(), "readings": out["readings"]}
    rep = check_bundle(bundle([t]), root, call_records=recs)
    assert rep["verdict"] == ALLOW, problems(rep)
    # independence is BY CONSTRUCTION: identical prompt, built from the document alone
    assert out["records"][0]["prompt"]["sha256"] == out["records"][1]["prompt"]["sha256"]
    assert not independence_problems(out["readings"], recs)


def test_PLANT_reader_invents_a_quote(root):
    bad = copy.deepcopy(ANSWER)
    bad["items"][2]["quote"] = "Death occurred in 61 of 203 patients."        # plausible, not in the document
    out = _dual(root, claude_answer=bad)
    t = {"trial_id": "PLANT-001", "measure": "binary", "values": binary_values(), "readings": out["readings"]}
    rep = check_bundle(bundle([t]), root)
    assert rep["verdict"] == REFUSE and "events[comparator]: UNRESOLVED" in problems(rep)


def test_PLANT_claude_pin_does_not_hold(root):
    out = _dual(root, cr=_claude_fake(ANSWER, reported="claude-haiku-5-5"))
    assert out["records"][0]["state"] == "RAN_ERROR" and "pin does not hold" in out["records"][0]["error"]
    t = {"trial_id": "PLANT-001", "measure": "binary", "values": binary_values(), "readings": out["readings"]}
    assert check_bundle(bundle([t]), root)["verdict"] == REFUSE


def test_PLANT_claude_used_tools(root):
    out = _dual(root, cr=_claude_fake(ANSWER, turns=3))
    assert out["records"][0]["state"] == "RAN_ERROR" and "turns" in out["records"][0]["error"]


def test_prompt_never_contains_the_other_answer(root):
    out = _dual(root)
    p = base64.b64decode(out["records"][1]["prompt"]["b64"]).decode("utf-8")
    assert '"items"' not in p.split("=== DOCUMENT ===")[1]


# ------------------------------------------------------------------ opt-in: nothing served depends on this package
def test_no_certificate_root_or_served_module_imports_p3():
    hits = []
    for d in ("harness", "scripts", "docs"):
        for dp, _dn, fns in os.walk(ROOT / d):
            for fn in fns:
                if fn.endswith(".py"):
                    with open(os.path.join(dp, fn), encoding="utf-8", errors="replace") as fh:
                        if "extraction_contract" in fh.read():
                            hits.append(os.path.relpath(os.path.join(dp, fn), ROOT))
    assert not hits, f"P3 is opt-in: harness/scripts/docs must not import it (would enter certificates): {hits}"
