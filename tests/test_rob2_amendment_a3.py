"""Amendment A3 and the two pre-registered variants (Mahmood via Dispatch, 13 Oct: "ok" to the four codex rule
candidates; outputs/robgrade/SIGNING_RULE_CANDIDATES.md). Written BEFORE the code and run failing first.
A3 (adopted directly): (1) a rationale citing a source the readers were never shown is not context; (4) a contextual
decision on a branch since closed is rendered on the served tab. VARIANTS (each pre-registered, scored separately):
v43_setting -- 4.3 joins the setting-based questions; vcommonly -- "commonly" leaves the USUAL markers."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from robgrade import contextual as cx  # noqa: E402
from robgrade import rob2_formal as rf  # noqa: E402
from robgrade import rob2_tab as tab  # noqa: E402
import rob2_contextual as rc  # noqa: E402
import rob2_ctx_score as cs  # noqa: E402

AB = {"id": "abstract:PMID 1", "kind": "abstract", "sha256": "a" * 64, "open_for_prompt": True,
      "text": "A multicentre trial with central web-based randomisation of 4000 patients."}
REG = {"id": "registry:NCT1", "kind": "registry", "sha256": "b" * 64, "open_for_prompt": True,
       "text": "Allocation: Randomized. Masking: Outcomes Assessor."}
FT = {"id": "fulltext:PMID 1", "kind": "fulltext", "sha256": "c" * 64, "open_for_prompt": True,
      "text": "Methods. Allocation used central web-based randomisation run by the trials unit."}
QUOTE = "central web-based randomisation"
UNSEEN = "RATIONALE_CITES_A_SOURCE_NOT_SHOWN"


def _r(qid, ans, quote, sid, why):
    return {"answers": [{"qid": qid, "answer": ans, "quote": quote, "source_id": sid, "rationale": why}]}


# ======================= A3 (1): a source the readers were never shown is not context =======================
@pytest.mark.parametrize("why", [
    "the original manuscript confirms central web-based randomisation was concealed",
    "according to the protocol, central web-based randomisation was concealed",
    "the supplementary appendix shows central web-based randomisation was concealed",
    "the statistical analysis plan states central web-based randomisation",
    "the methods section of the full text says central web-based randomisation was concealed",
    "the CONSORT diagram shows central web-based randomisation was used",
    "the trial registration states central web-based randomisation was concealed",
])
def test_PLANT_a3_a_rationale_citing_a_document_never_shown_is_dropped(why):
    v = cx.verify(_r("1.2", "PY", QUOTE, AB["id"], why), [AB], ["1.2"])
    assert v["1.2"]["answer"] == "NI" and v["1.2"]["dropped"]["why"] == UNSEEN, why


def test_PLANT_a3_a_document_that_WAS_shown_may_be_named():
    why = "the registry record lists the outcomes assessor as masked"
    v = cx.verify(_r("4.3", "PN", "Masking: Outcomes Assessor", REG["id"], why), [AB, REG], ["4.3"])
    assert v["4.3"]["answer"] == "PN"
    why = "the methods section reports central web-based randomisation by the trials unit, so it was concealed"
    v = cx.verify(_r("1.2", "PY", QUOTE, FT["id"], why), [FT], ["1.2"])
    assert v["1.2"]["answer"] == "PY"


def test_PLANT_a3_a_document_named_IN_THE_QUOTE_may_be_named():
    src = dict(AB, text="As specified in the protocol, allocation used central web-based randomisation.")
    q = "As specified in the protocol, allocation used central web-based randomisation"
    why = "the protocol specified central web-based randomisation, so allocation was concealed"
    assert cx.verify(_r("1.2", "PY", q, src["id"], why), [src], ["1.2"])["1.2"]["answer"] == "PY"


def test_PLANT_a3_the_rest_of_the_rule_is_unchanged():
    why = "central randomisation implies concealment"
    assert cx.verify(_r("1.2", "PY", QUOTE, AB["id"], why), [AB], ["1.2"])["1.2"]["answer"] == "PY"
    why = "I recall that central web-based randomisation was concealed"           # MEMORY: unchanged
    assert cx.verify(_r("1.2", "PY", QUOTE, AB["id"], why), [AB], ["1.2"])["1.2"]["answer"] == "NI"


# ======================= A3 (4): a closed-branch contextual decision is rendered =======================
def _closed(answer="PN"):
    na = rf.answer("NA", how="not asked once an upstream question was answered contextually")
    na["closed_contextual"] = {"answer": answer, "span": None, "context": [
        {"who": "reader 1", "quote": "no deviations occurred", "source_id": "abstract:PMID 1"},
        {"who": "reader 2", "quote": "all patients received the allocated treatment", "source_id": "registry:NCT1"}]}
    return na


def test_PLANT_a3_a_closed_branch_decision_is_shown_with_every_quote():
    note = tab.contextual_note({"answers": {"2.4": _closed()}})
    assert "2.4 not asked: its branch closed after a contextual answer" in note
    assert "it had been decided probably no, from 'no deviations occurred' (abstract:PMID 1); " \
           "'all patients received the allocated treatment' (registry:NCT1)" in note


def test_PLANT_a3_a_domain_with_only_a_closed_decision_is_named_in_the_overall_label():
    assert tab._contextual_domains({"D2": {"answers": {"2.4": _closed()}}}) == " [contextual answers in: D2]"


def test_PLANT_a3_rob2_tab_is_amendable():
    assert "robgrade/rob2_tab.py" in cs.AMENDABLE


# ======================= VARIANTS (pre-registered; never the default) =======================
SURG = dict(AB, text="Participants recorded their own symptoms; the trial compared surgery with physiotherapy.")
SQ = "the trial compared surgery with physiotherapy"
SWHY = "participants report this outcome themselves and know whether they had surgery or physiotherapy"


def test_PLANT_v43_4_3_is_setting_based_only_under_its_variant():
    assert cx.verify(_r("4.3", "PY", SQ, SURG["id"], SWHY), [SURG], ["4.3"])["4.3"]["answer"] == "NI"   # the default
    v = cx.verify(_r("4.3", "PY", SQ, SURG["id"], SWHY), [SURG], ["4.3"], variant="v43_setting")
    assert v["4.3"]["answer"] == "PY"
    # MEMORY and the unseen-source check still apply under the variant
    for why in ("I recall that participants knew: surgery or physiotherapy",
                "the protocol says participants knew whether they had surgery or physiotherapy"):
        v = cx.verify(_r("4.3", "PY", SQ, SURG["id"], why), [SURG], ["4.3"], variant="v43_setting")
        assert v["4.3"]["answer"] == "NI", why


def test_PLANT_vcommonly_releases_commonly_and_nothing_else():
    why = "central web-based randomisation is commonly concealed"
    assert cx.verify(_r("1.2", "PY", QUOTE, AB["id"], why), [AB], ["1.2"])["1.2"]["answer"] == "NI"       # the default
    assert cx.verify(_r("1.2", "PY", QUOTE, AB["id"], why), [AB], ["1.2"], variant="vcommonly")["1.2"]["answer"] == "PY"
    for why in ("central web-based randomisation is usually concealed",
                "central web-based randomisation is typically concealed"):
        v = cx.verify(_r("1.2", "PY", QUOTE, AB["id"], why), [AB], ["1.2"], variant="vcommonly")
        assert v["1.2"]["answer"] == "NI", why
    assert cx.verify(_r("4.3", "PY", SQ, SURG["id"], SWHY), [SURG], ["4.3"], variant="vcommonly")["4.3"]["answer"] == "NI"


def test_PLANT_an_unknown_variant_is_refused():
    with pytest.raises(KeyError):
        cx.verify(_r("1.2", "PY", QUOTE, AB["id"], "r"), [AB], ["1.2"], variant="v_unregistered")
    assert set(cx.VARIANTS) == {"v43_setting", "vcommonly"}


def test_PLANT_a_variant_run_keeps_its_own_records_and_reads_the_base_ones(tmp_path, monkeypatch):
    for n in ("OUT_DIR", "REC_DIR", "RUNS", "REC_READ_DIRS", "VARIANT"):    # configure() rebinds them: restore after
        monkeypatch.setattr(rc, n, getattr(rc, n))
    base = tmp_path / "rob2_ctx"
    base.mkdir()
    monkeypatch.setattr(rc, "BASE_REC_DIR", str(base))
    try:
        rc.configure("v43_setting")
        assert rc.VARIANT == "v43_setting"
        assert rc.REC_DIR == str(base) + "_v43_setting"                           # new calls go here
        assert rc.REC_READ_DIRS == [str(base) + "_v43_setting", str(base)]       # held readers are reused
        assert rc.RUNS.endswith("rob2_ctx_runs_v43_setting.json") and rc.OUT_DIR.endswith("rob2_ctx_v43_setting")
    finally:
        rc.configure(None)
    assert rc.VARIANT is None and rc.REC_DIR == str(base) and rc.REC_READ_DIRS == [str(base)]
    assert rc.RUNS.endswith("rob2_ctx_runs.json") and rc.OUT_DIR.endswith(os.path.join("robgrade", "rob2_ctx"))
    with pytest.raises(KeyError):
        rc.configure("v_unregistered")


def test_PLANT_the_pipeline_verifies_under_the_configured_variant(monkeypatch):
    for n in ("OUT_DIR", "REC_DIR", "RUNS", "REC_READ_DIRS", "VARIANT"):    # configure() rebinds them: restore after
        monkeypatch.setattr(rc, n, getattr(rc, n))
    monkeypatch.setattr(rc, "fresh", lambda run, p: run if run and run.get("state") == "RAN_OK" else None)
    monkeypatch.setattr(rc, "prompt", lambda it, targets, kind="reader", readings=None: kind.encode())
    row = {"qid": "1.2", "answer": "PY", "quote": QUOTE, "source_id": AB["id"],
           "rationale": "central web-based randomisation is commonly concealed"}
    monkeypatch.setattr(rc, "_reading", lambda run: {"answers": [row], "notes": ""} if run else None)
    run = {"codex": {"state": "RAN_OK", "record_id": "mc-c"}, "agy": {"state": "RAN_OK", "record_id": "mc-a"}}
    obj = rf.assessment("PMID 1", "o", {q: (rf.answer(v, how="t", span="s", source_sha256="0" * 64) if v != "NI"
                                            else rf.answer("NI", how="t"))
                                        for q, v in {"1.1": "Y", "1.2": "NI", "1.3": "N"}.items()})
    item = {"pmid": "1", "nct": None, "outcome": "o"}
    try:
        _, c, _ = rc._one_pass(item, obj, ["1.2"], dict(run), False, {}, [AB])
        assert c["1.2"]["answer"] == "NI"                                        # the default: "commonly" is USUAL
        rc.configure("vcommonly")
        _, c, _ = rc._one_pass(item, obj, ["1.2"], dict(run), False, {}, [AB])
        assert c["1.2"]["answer"] == "PY"
    finally:
        rc.configure(None)


# ======================= the scorer: variant pre-registration, supersession under A3 =======================
def _git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout.strip()


def _vrepo(tmp_path, name="v43_setting", edit_after=False, doc=True):
    repo = tmp_path / "r"
    (repo / "robgrade").mkdir(parents=True)
    (repo / "outputs" / "robgrade").mkdir(parents=True)
    (repo / "robgrade" / "contextual.py").write_text("rule v1\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "code")
    if doc:
        (repo / "outputs" / "robgrade" / f"CONTEXTUAL_VARIANT_{name}.md").write_text("variant\n", encoding="utf-8")
    else:
        (repo / "outputs" / "robgrade" / "OTHER.md").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "prereg variant")
    sha = _git(repo, "rev-parse", "HEAD")
    if edit_after:
        (repo / "robgrade" / "contextual.py").write_text("rule v2 edited after the variant was registered\n",
                                                          encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "edit")
    return repo, sha


def test_PLANT_a_variant_must_be_preregistered_by_the_commit_that_added_its_document(tmp_path, monkeypatch):
    repo, sha = _vrepo(tmp_path)
    monkeypatch.setattr(cs, "ROOT", str(repo))
    assert cs.check_variant_prereg("v43_setting", sha) == sha
    with pytest.raises(SystemExit, match="REFUSED"):
        cs.check_variant_prereg("vcommonly", sha)                              # not the commit that added ITS document
    repo2, sha2 = _vrepo(tmp_path / "b", doc=False)
    monkeypatch.setattr(cs, "ROOT", str(repo2))
    with pytest.raises(SystemExit, match="REFUSED"):
        cs.check_variant_prereg("v43_setting", sha2)


def test_PLANT_the_rule_must_be_unchanged_since_the_variant_was_registered(tmp_path, monkeypatch):
    repo, sha = _vrepo(tmp_path, edit_after=True)
    monkeypatch.setattr(cs, "ROOT", str(repo))
    with pytest.raises(SystemExit, match="changed since"):
        cs.check_variant_prereg("v43_setting", sha)


def test_PLANT_the_scorer_arguments():
    assert cs.parse_args(["abc"]) == ("abc", None, None)
    assert cs.parse_args(["abc", "--variant", "vcommonly", "def"]) == ("abc", "vcommonly", "def")
    for bad in ([], ["abc", "--variant", "v_unregistered", "def"], ["abc", "--variant", "vcommonly"], ["a", "b"]):
        with pytest.raises(SystemExit, match="REFUSED"):
            cs.parse_args(bad)


def test_PLANT_supersession_is_tested_by_each_declarations_own_criterion():
    assert cs.SUPERSESSION_TESTS == ("defect_caused", "rule_changed")
    assert cs.supersession_test({"id": "A2.1"}) == "defect_caused"                 # A2 declared without the field
    assert cs.supersession_test({"id": "A3.1", "superseded_test": "rule_changed"}) == "rule_changed"
    with pytest.raises(SystemExit, match="REFUSED"):
        cs.supersession_test({"id": "A3.1", "superseded_test": "because"})


def test_PLANT_rule_changed_means_the_amended_rule_shows_the_adjudicator_different_readings():
    from test_rob2_amendment_a2 import _adj_src, _rec_src
    q = "central web-based randomisation"
    ni = {"answers": [{"qid": "1.2", "answer": "NI", "quote": "", "source_id": "", "rationale": "nothing said"}], "notes": ""}
    for why, changed in (("according to the protocol, central web-based randomisation means concealment", True),
                         ("central web-based randomisation means concealment", False)):
        py = {"answers": [{"qid": "1.2", "answer": "PY", "quote": q, "source_id": "s", "rationale": why}], "notes": ""}
        shown = {"1.2": {"reader 1": {"answer": "PY", "quote": q, "source_id": "s", "source_sha256": "a" * 64,
                                      "rationale": why},
                         "reader 2": {"answer": "NI", "rationale": "nothing said"}}}        # what the OLD rule showed
        recs = {"mc-c": _rec_src("codex", json.dumps(py)), "mc-a": _rec_src("agy", json.dumps(ni)),
                "mc-j": _adj_src(shown)}
        assert cs.rule_changed("mc-j", recs.get, list(recs)) is changed, why


def test_PLANT_a3_a_document_REPORTED_BY_A_SHOWN_SOURCE_may_be_named():
    # the frozen r4 test's case: the shown abstract reports the plan, outside the quoted words -- the reader relies on
    # what a SHOWN source says about that document, not on the unseen document itself
    src = dict(AB, text="A protocol was registered before enrolment and the statistical analysis plan published.")
    why = "a protocol registered before enrolment and a published statistical analysis plan support a prespecified plan"
    v = cx.verify(_r("5.1", "PY", "A protocol was registered before enrolment", src["id"], why), [src], ["5.1"])
    assert v["5.1"]["answer"] == "PY"
    # ... while a document NO shown source mentions is still unseen
    why = "the original manuscript reports a protocol registered before enrolment, so the plan was prespecified"
    v = cx.verify(_r("5.1", "PY", "A protocol was registered before enrolment", src["id"], why), [src], ["5.1"])
    assert v["5.1"]["answer"] == "NI" and v["5.1"]["dropped"]["why"] == UNSEEN


# ======================= review of A3 (round 16; codex REVISE 5, agy REVISE 6): failing-first tests =================
def _v(qid, ans, quote, why, text, kind="abstract"):
    src = {"id": "s1", "kind": kind, "text": text, "sha256": "0" * 64, "open_for_prompt": True}
    return cx.verify(_r(qid, ans, quote, "s1", why), [src], [qid])[qid]


def test_PLANT_a3r16_a_document_merely_mentioned_ELSEWHERE_in_the_source_is_not_reported_context():   # codex1
    v = _v("1.2", "PY", "Randomisation details were omitted.", "According to the protocol, randomisation was concealed.",
           "The protocol was unavailable. Randomisation details were omitted.")
    assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN
    # the frozen r4 case still stands: the plan is reported in the QUOTED sentence
    why = "a protocol registered before enrolment and a published statistical analysis plan support a prespecified plan"
    assert _v("5.1", "PY", "A protocol was registered before enrolment", why,
              "A protocol was registered before enrolment and the statistical analysis plan published.")["answer"] == "PY"


def test_PLANT_a3r16_documents_are_matched_as_words_with_their_aliases():          # agy0, agy1, agy2, agy4
    v = _v("5.1", "PY", "randomisation was concealed", "the sap confirms randomisation was concealed",
           "Trial of saphenous vein graft with randomisation was concealed.")
    assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN                          # "saphenous" is not the SAP
    plan = "A protocol was registered before enrolment and the statistical analysis plan published."
    assert _v("5.1", "PY", "A protocol was registered", "a registered protocol and the published SAP confirm "
              "prespecification", plan)["answer"] == "PY"                                  # SAP = statistical analysis plan
    assert _v("3.1", "PY", "participant flow and complete follow-up", "fig 1 shows participant flow and complete "
              "follow-up, so follow-up was complete",
              "Figure 1 shows participant flow and complete follow-up.")["answer"] == "PY"  # fig 1 = Figure 1
    assert _v("1.2", "PY", "central web-based randomisation", "as specified in the protocols, central web-based "
              "randomisation was concealed", "A protocol was registered; central web-based randomisation of 4000 "
              "patients.")["answer"] == "PY"                                                # protocols = protocol


def test_PLANT_a3r16_a_shown_registry_source_of_either_kind_may_be_named():          # agy3
    for kind in ("registry_text", "registry_row"):
        v = _v("1.2", "PY", "interactive voice response system", "the registry record confirms concealment via "
               "interactive voice response system", "Allocation by an interactive voice response system held at the "
               "coordinating centre.", kind=kind)
        assert v["answer"] == "PY", kind


def test_PLANT_a3r16_protocol_as_a_concept_is_not_a_document():                     # agy5
    for why in ("full analysis set was analysed without exclusions for non-adherence to the protocol",
                "full analysis set with no exclusions for deviations from the protocol",
                "a per-protocol analysis was not used; the full analysis set of all randomised patients was"):
        assert _v("2.6", "PY", "full analysis set of all randomised patients", why,
                  "Analyses were based on the full analysis set of all randomised patients.")["answer"] == "PY", why


def test_PLANT_a3r16_an_A2_supersession_proof_is_judged_under_A2s_rule():           # codex2
    from test_rob2_amendment_a2 import _adj_src, _rec_src, UNREAD_
    why = "according to the protocol, central web-based randomisation means concealed"
    good = {"answers": [{"qid": "1.2", "answer": "PY", "quote": "central web-based randomisation", "source_id": "s",
                         "rationale": why}], "notes": ""}
    ok_row = {"answer": "PY", "quote": "q", "source_id": "s", "source_sha256": "a" * 64, "rationale": "r"}
    recs = {"mc-c": _rec_src("codex", json.dumps(good)), "mc-a": _rec_src("agy", "Checking.\n" + json.dumps(good)),
            "mc-j": _adj_src({"1.2": {"reader 1": ok_row, "reader 2": UNREAD_}})}
    assert cs.defect_caused("mc-j", recs.get, list(recs)) is True      # A3 would drop it; A2's proof is about A2's rule


def test_PLANT_a3r16_a_variant_never_runs_before_its_document_is_committed(tmp_path, monkeypatch):   # codex4
    repo, sha = _vrepo(tmp_path)
    monkeypatch.setattr(rc, "ROOT", str(repo))
    assert rc.variant_registered("v43_setting") == sha
    with pytest.raises(SystemExit, match="REFUSED"):
        rc.variant_registered("vcommonly")                                  # its document was never committed
    (repo / "outputs" / "robgrade" / "CONTEXTUAL_VARIANT_v43_setting.md").write_text("edited\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="REFUSED"):
        rc.variant_registered("v43_setting")                                # the registered text was edited


def test_PLANT_a3r16_a_variant_overlays_the_base_manifest(monkeypatch):            # codex0
    import hashlib
    for n in ("OUT_DIR", "REC_DIR", "RUNS", "REC_READ_DIRS", "VARIANT"):
        monkeypatch.setattr(rc, n, getattr(rc, n))
    monkeypatch.setattr(rc.rd, "open_sources", lambda it: [AB])
    monkeypatch.setattr(rc, "prompt", lambda it, targets, kind="reader", readings=None: ("P:" + ",".join(targets)).encode())
    sha = hashlib.sha256(b"P:1.2,5.1").hexdigest()
    monkeypatch.setattr(rc, "record_prompt_sha256", lambda rid: sha)
    row = {"qid": "1.2", "answer": "PY", "quote": QUOTE, "source_id": AB["id"],
           "rationale": "central web-based randomisation means concealment"}
    monkeypatch.setattr(rc, "_reading", lambda run: {"answers": [row], "notes": ""} if run else None)
    obj = rf.assessment("PMID 1", "o", {q: (rf.answer(v, how="t", span="s", source_sha256="0" * 64) if v != "NI"
                                            else rf.answer("NI", how="t"))
                                        for q, v in {"1.1": "Y", "1.2": "NI", "1.3": "N", "2.1": "N", "2.2": "N",
                                                     "2.6": "Y", "3.1": "Y", "4.1": "N", "4.2": "N", "4.3": "N",
                                                     "5.1": "NI", "5.2": "N", "5.3": "N"}.items()})
    item = {"pmid": "1", "nct": None, "outcome": "o", "key": "k"}
    base = {"k": {"passes": [{"codex": {"state": "RAN_OK", "record_id": "mc-c", "prompt_sha256": sha},
                              "agy": {"state": "RAN_OK", "record_id": "mc-a", "prompt_sha256": sha}}]}}
    try:
        rc.configure("vcommonly")
        new, r, c = rc.process(item, obj, {}, False, {}, base_runs=base)      # an EMPTY variant manifest
    finally:
        rc.configure(None)
    assert c["1.2"]["answer"] == "PY" and sorted(r["consumed"]) == ["mc-a", "mc-c"]    # the base readers are read
    assert r["passes"] == [{}]                                                # the variant stores only its own entries
    # a variant entry may never stand in for a fresh base reader of the same prompt
    vr = {"k": {"passes": [{"codex": {"state": "RAN_OK", "record_id": "mc-other", "prompt_sha256": sha}}]}}
    with pytest.raises(SystemExit, match="REFUSED"):
        cs.check_variant_manifest(vr, base)
    cs.check_variant_manifest({"k": {"passes": [{"adjudicator": {"state": "RAN_OK", "record_id": "mc-j",
                                                                 "prompt_sha256": "e" * 64}}]}}, base)


# ======================= review of A3 (round 17; codex REVISE 4, agy REVISE 4): failing-first tests =================
def test_PLANT_a3r17_a_quote_ending_its_sentence_does_not_reach_into_the_next():   # codex1, agy0
    assert cx.quoted_sentence("Concealment was central.", "Concealment was central. The protocol was registered.") \
        == "concealment was central."
    v = _v("1.2", "PY", "Randomisation details were omitted.", "According to the protocol, randomisation was concealed.",
           "Randomisation details were omitted. The protocol was unavailable.")
    assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN


def test_PLANT_a3r17_the_manuscript_is_the_shown_full_text():                       # agy1
    assert cx.cites_unseen("the manuscript describes central randomisation", "central randomisation", {"fulltext"}) is None
    # REVISED in round 19 (codex1): kind is not identity -- "the ORIGINAL publication" names another paper than the
    # shown full text, so it is unseen unless the quoted sentence reports it (the round-17 expectation was None)
    assert cx.cites_unseen("the original publication describes central randomisation", "central randomisation",
                           {"fulltext"}) == "original publication"
    assert cx.cites_unseen("the manuscript describes central randomisation", "central randomisation", {"abstract"}) \
        == "manuscript"


def test_PLANT_a3r17_registry_aliases_are_one_document():                           # agy2
    assert cx._doc("trial register") == cx._doc("ClinicalTrials.gov") == cx._doc("registry") == "registry"
    assert cx.cites_unseen("the registry confirms central randomisation", "central randomisation", set(),
                           "a trial register entry was made") is None


def test_PLANT_a3r17_a_document_the_rationale_says_was_NOT_available_is_not_relied_on():   # codex3
    for why in ("No protocol was available, but central web-based randomisation supports concealment.",
                "Without access to the protocol, central web-based randomisation still supports concealment.",
                "The protocol was not available; central web-based randomisation supports concealment."):
        assert _v("1.2", "PY", QUOTE, why, AB["text"])["answer"] == "PY", why
    v = _v("1.2", "PY", QUOTE, "The protocol confirms central web-based randomisation was concealed.", AB["text"])
    assert v["answer"] == "NI"                                                    # an affirmative reliance still is


def test_PLANT_a3r17_a_variant_entry_may_never_shadow_a_base_entry_of_the_same_prompt():   # codex0, agy3
    base = {"k": {"passes": [{"codex": {"state": "RAN_OK", "record_id": "r-c", "prompt_sha256": "p"},
                              "adjudicator": {"state": "RAN_OK", "record_id": "r1", "prompt_sha256": "q"}}]}}
    for shadow in ({"codex": {"state": "RAN_ERROR", "record_id": "r-c", "prompt_sha256": "p"}},   # same id, new state
                   {"adjudicator": {"state": "RAN_OK", "record_id": "r2", "prompt_sha256": "q"}}):  # another adjudicator
        with pytest.raises(SystemExit, match="REFUSED"):
            cs.check_variant_manifest({"k": {"passes": [shadow]}}, base)
    cs.check_variant_manifest({"k": {"passes": [{"adjudicator": {"state": "RAN_OK", "record_id": "r3",
                                                                 "prompt_sha256": "other"}}]}}, base)


# ======================= review of A3 (round 18; codex REVISE 3, agy ACCEPT): failing-first tests =================
def test_PLANT_a3r18_a_source_sentence_saying_the_document_was_unavailable_does_not_report_it():   # codex1
    v = _v("1.2", "PY", "randomisation details were omitted", "According to the protocol, randomisation was concealed.",
           "The protocol was unavailable and randomisation details were omitted.")
    assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN


def test_PLANT_a3r18_a_fresh_base_record_always_wins_over_an_overlay(monkeypatch):   # codex0
    import hashlib
    for n in ("OUT_DIR", "REC_DIR", "RUNS", "REC_READ_DIRS", "VARIANT"):
        monkeypatch.setattr(rc, n, getattr(rc, n))
    monkeypatch.setattr(rc.rd, "open_sources", lambda it: [AB])
    monkeypatch.setattr(rc, "prompt", lambda it, targets, kind="reader", readings=None: ("P:" + ",".join(targets)).encode())
    sha = hashlib.sha256(b"P:1.2,5.1").hexdigest()
    monkeypatch.setattr(rc, "record_prompt_sha256", lambda rid: sha if rid in ("mc-c", "mc-a") else None)
    row = {"qid": "1.2", "answer": "PY", "quote": QUOTE, "source_id": AB["id"],
           "rationale": "central web-based randomisation means concealment"}
    monkeypatch.setattr(rc, "_reading", lambda run: {"answers": [row], "notes": ""} if run else None)
    obj = rf.assessment("PMID 1", "o", {q: (rf.answer(v, how="t", span="s", source_sha256="0" * 64) if v != "NI"
                                            else rf.answer("NI", how="t"))
                                        for q, v in {"1.1": "Y", "1.2": "NI", "1.3": "N", "2.1": "N", "2.2": "N",
                                                     "2.6": "Y", "3.1": "Y", "4.1": "N", "4.2": "N", "4.3": "N",
                                                     "5.1": "NI", "5.2": "N", "5.3": "N"}.items()})
    item = {"pmid": "1", "nct": None, "outcome": "o", "key": "k"}
    base = {"k": {"passes": [{"codex": {"state": "RAN_OK", "record_id": "mc-c", "prompt_sha256": sha},
                              "agy": {"state": "RAN_OK", "record_id": "mc-a", "prompt_sha256": sha}}]}}
    overlay = {"k": {"passes": [{"codex": {"state": "RAN_ERROR", "record_id": None, "prompt_sha256": "q" * 64}}]}}
    try:
        rc.configure("vcommonly")
        new, r, c = rc.process(item, obj, overlay, False, {}, base_runs=base)
    finally:
        rc.configure(None)
    assert c["1.2"]["answer"] == "PY" and sorted(r["consumed"]) == ["mc-a", "mc-c"]


# ======================= review of A3 (round 19; codex REVISE 3, agy ACCEPT): failing-first tests =================
def test_PLANT_a3r19_a_quote_cropped_after_a_disclaimer_does_not_report_the_document():   # codex0
    v = _v("1.2", "PY", "protocol, randomisation details were omitted",
           "According to the protocol, randomisation was concealed.",
           "Without access to the protocol, randomisation details were omitted.")
    assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN


def test_PLANT_a3r19_a_shown_full_text_is_not_another_publication():                    # codex1
    for doc in ("parent publication", "original publication", "primary publication", "main report"):
        v = _v("1.2", "PY", "randomisation details", f"The {doc} confirms randomisation details showed concealment.",
               "This follow-up report omits randomisation details.", kind="fulltext")
        assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN, doc
    # the shown full text itself may be named
    assert cx.cites_unseen("the manuscript describes central randomisation", "central randomisation", {"fulltext"}) is None


# ======================= review of A3 (round 20; codex REVISE 3, agy ACCEPT): failing-first tests =================
def test_PLANT_a3r20_an_original_manuscript_is_another_paper_than_the_shown_full_text():   # codex0
    v = _v("1.2", "PY", "randomisation details", "The original manuscript confirms randomisation details showed "
           "concealment.", "This follow-up report omits randomisation details.", kind="fulltext")
    assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN


def test_PLANT_a3r20_an_abbreviation_does_not_end_the_quoted_sentence():               # codex2
    assert cx.quoted_sentence("complete follow-up for all participants",
                              "Fig. 1 shows complete follow-up for all participants.") == \
        "fig. 1 shows complete follow-up for all participants."
    assert _v("3.1", "PY", "complete follow-up for all participants", "Fig. 1 shows complete follow-up for all "
              "participants", "Fig. 1 shows complete follow-up for all participants.")["answer"] == "PY"


# ======================= review of A3 (round 21; codex REVISE 3, agy ACCEPT) =================
def test_PLANT_a3r21_another_NAMED_registry_is_unseen_when_only_clinicaltrials_gov_is_shown():   # codex0
    for kind in ("registry_text", "registry_row"):
        v = _v("1.2", "PY", "Randomisation details were omitted.", "The ISRCTN registry confirms randomisation was "
               "concealed.", "Randomisation details were omitted.", kind=kind)
        assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN, kind
    # ... reported in the quoted sentence, it may be named
    assert _v("1.2", "PY", "central web-based randomisation", "the ISRCTN registry entry shows central web-based "
              "randomisation, so allocation was concealed", "Registered as ISRCTN12345678; central web-based "
              "randomisation was used.")["answer"] == "PY"


def test_a3r21_protocol_deviations_is_a_concept_PINNED():                              # codex2 (declined: already PY)
    q = "All randomised participants were analysed in their assigned groups."
    assert _v("2.6", "PY", q, "Keeping all randomised participants in their assigned groups avoids exclusions for "
              "protocol deviations.", q)["answer"] == "PY"


# ======================= review of A3 (round 22; codex REVISE 2, agy ACCEPT): failing-first test =================
def test_PLANT_a3r22_a_trial_identifier_must_be_one_the_readers_were_shown():          # codex0
    src = {"id": "registry:NCT00000001:description", "kind": "registry_text", "nct": "NCT00000001",
           "text": "Randomisation details were omitted.", "sha256": "0" * 64, "open_for_prompt": True}
    q = "Randomisation details were omitted."

    def v(why):
        return cx.verify(_r("1.2", "PY", q, src["id"], why), [src], ["1.2"])["1.2"]
    for why in ("ClinicalTrials.gov record NCT09999999 confirms randomisation details were concealed.",
                "Another registry record confirms randomisation details were concealed.",
                "ISRCTN12345678 confirms randomisation details were concealed."):
        r = v(why)
        assert r["answer"] == "NI" and r["dropped"]["why"] == UNSEEN, why
    # positive control (REVISED round 23, codex2): the shown identifier, with real concealment context to quote
    ok = dict(src, text="Allocation by central web-based randomisation.")
    v_ok = cx.verify(_r("1.2", "PY", "central web-based randomisation", ok["id"], "ClinicalTrials.gov record "
                        "NCT00000001 shows central web-based randomisation, so allocation was concealed."), [ok], ["1.2"])
    assert v_ok["1.2"]["answer"] == "PY"


# ======================= review of A3 (round 23; codex REVISE 3, agy ACCEPT): failing-first test =================
def test_PLANT_a3r23_another_record_REPORTED_in_the_quoted_sentence_may_be_named():   # codex1
    q = "Another registry record reports central web-based randomisation."
    v = _v("1.2", "PY", q, "The abstract reports another registry record describing central web-based randomisation, "
           "supporting concealment.", q)
    assert v["answer"] == "PY"


# ======================= review of A3 (round 24; codex REVISE 2, agy RAN_ERROR): failing-first test =================
def test_PLANT_a3r24_another_record_the_sentence_says_was_unavailable_is_not_reported():   # codex0
    q = "Another registry record was unavailable and randomisation details were omitted."
    v = _v("1.2", "PY", q, "Another registry record confirms randomisation details were concealed.", q)
    assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN


# ======================= review of A3 (round 25; codex REVISE 3, agy ACCEPT): failing-first tests =================
def _reg(text):
    return {"id": "registry:NCT00000001:description", "kind": "registry_text", "nct": "NCT00000001", "text": text,
            "sha256": "0" * 64, "open_for_prompt": True}


def test_PLANT_a3r25_an_identifier_a_shown_text_says_was_unavailable_is_not_shown():   # codex0
    src = _reg("Record NCT09999999 was unavailable. Randomisation details were omitted.")
    v = cx.verify(_r("1.2", "PY", "Randomisation details were omitted.", src["id"], "ClinicalTrials.gov record "
                     "NCT09999999 confirms randomisation details were concealed."), [src], ["1.2"])["1.2"]
    assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN


def test_PLANT_a3r25_a_rationale_disclaiming_another_record_does_not_rely_on_it():      # codex2
    src = _reg("Allocation by central web-based randomisation.")
    v = cx.verify(_r("1.2", "PY", "central web-based randomisation", src["id"], "No other registry record was "
                     "available, but central web-based randomisation supports concealment."), [src], ["1.2"])["1.2"]
    assert v["answer"] == "PY"


# ======================= review of A3 (round 26; codex REVISE 3, agy ACCEPT): failing-first tests =================
def test_PLANT_a3r26_an_identifier_counts_as_reported_only_in_the_quoted_sentence():   # codex0
    src = _reg("Related trial: NCT09999999. Randomisation details were omitted.")
    v = cx.verify(_r("1.2", "PY", "Randomisation details were omitted.", src["id"], "ClinicalTrials.gov record "
                     "NCT09999999 confirms randomisation details were concealed."), [src], ["1.2"])["1.2"]
    assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN


def test_PLANT_a3r26_a_rationale_disclaiming_an_identifier_does_not_rely_on_it():      # codex2
    src = _reg("Allocation by central web-based randomisation.")
    v = cx.verify(_r("1.2", "PY", "central web-based randomisation", src["id"], "Record NCT09999999 was unavailable, "
                     "but central web-based randomisation supports concealment."), [src], ["1.2"])["1.2"]
    assert v["answer"] == "PY"


# ======================= review of A3 (round 27; codex REVISE 2, agy ACCEPT): failing-first test =================
def test_PLANT_a3r27_a_disclaimer_after_the_documents_noun_still_counts():          # codex0 (beside a3r24)
    q = "Another registry record was unavailable and randomisation details were omitted."
    for why in ("The registry confirms randomisation details were concealed.",
                "Another registry record confirms randomisation details were concealed."):
        v = _v("1.2", "PY", q, why, q)
        assert v["answer"] == "NI" and v["dropped"]["why"] == UNSEEN, why
    # a disclaimer with the noun, in the rationale, is still a disclaimer
    assert _v("1.2", "PY", QUOTE, "The registry record was not available; central web-based randomisation supports "
              "concealment.", AB["text"])["answer"] == "PY"
