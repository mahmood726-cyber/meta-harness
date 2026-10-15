"""Synthetic-only G1 explanation contracts; no document stores or network."""
import hashlib
import importlib
from datetime import date

import pytest

DAY = date(2026, 10, 15)
BODY = b"Synthetic report. The analysis used the safety population. End."
SHA = hashlib.sha256(BODY).hexdigest()


def api():
    return importlib.import_module("scripts.g1_explanation")


def context():
    return dict(build_date=DAY, held_bytes=lambda sha: BODY if sha == SHA else None,
                decisions={"decisions": [{"id": "SYNTHETIC-DECISION"}]})


def divergence():
    return dict(state="DIVERGENT_NAMED", reason_code="ANALYSIS_SET", detail="Synthetic difference",
                evidence=dict(source_ref="synthetic.txt", sha256=SHA,
                              verbatim_span="The analysis used the safety population."),
                decided_by="synthetic verifier")


def search():
    return dict(identifiers=dict(pmids=[], dois=[], ncts=[], eudract=[], title="Synthetic", acronym=None,
                                 approved_drug=False), secondary_value_available=False,
                searched=[dict(source=s, identifier_or_query="Synthetic", when_utc="2026-10-15T00:00:00Z",
                               step_reached="NOT_FOUND", outcome="No synthetic record", response_sha256=None)
                          for s in ("PUBMED_EPMC_TITLE", "WHO_ICTRP")])


def test_plant_missing_required_source_is_unexplained():
    log = search()
    log["searched"].pop()
    result = api().build_explanation({"label": "Synthetic", "route": "NO_ROW"}, search_log=log, **context())
    assert result["state"] == "UNEXPLAINED"
    assert "WHO_ICTRP" in result["why_unexplained"]


def test_plant_span_absent_from_held_bytes_is_invalid():
    entry = divergence()
    entry["evidence"]["verbatim_span"] = "Not in the synthetic report"
    assert api().validate_explanation(entry, {"route": "NO_ROW"}, **context())


def test_plant_secondary_single_cannot_be_matched():
    entry = dict(state="MATCHED", route="SECONDARY_SINGLE", source_ref="synthetic.txt", sha256=SHA,
                 verified_by="synthetic verifier")
    assert api().validate_explanation(entry, {"route": "SECONDARY_SINGLE"}, **context())


def test_plant_missing_state_is_refused():
    assert api().validate_explanation({}, {}, **context())


def test_plant_unknown_decision_is_invalid():
    entry = dict(divergence(), reason_code="DECISION_EXCLUDED", decided_by="UNKNOWN")
    assert api().validate_explanation(entry, {}, **context())


@pytest.mark.parametrize("source,empty,full", [
    ("PUBMED_EPMC_PMID", False, True), ("PUBMED_EPMC_TITLE", True, True),
    ("UNPAYWALL_DOI", False, True), ("CTGOV_V2", False, True), ("AACT", False, True),
    ("EUCTR", False, True), ("WHO_ICTRP", True, True), ("FDA", False, True),
    ("EMA", False, True), ("PMDA", False, True), ("TGA_AUSPAR", False, True),
    ("FDA_ADCOMM", False, True), ("AHRQ_NIHR_HTA", False, True), ("SPONSOR_REGISTER", False, True),
    ("HEALTH_CANADA", False, False), ("EMA_CLINICAL_DATA", False, False)])
def test_each_applicability_rule(source, empty, full):
    ids = search()["identifiers"]
    assert api().APPLICABILITY[source](ids) is empty
    ids.update(pmids=["synthetic-pmid"], dois=["synthetic-doi"], ncts=["synthetic-nct"],
               eudract=["synthetic-ctis"], approved_drug=True)
    assert api().APPLICABILITY[source](ids) is full


@pytest.mark.parametrize("rule,expected", [
    ("X1", "DESIGN"), ("X-DESIGN", "DESIGN"), ("X2", "POPULATION"),
    ("X-DOSE", "INTERVENTION_DOSE_OR_REGIMEN"), ("E2:COMPARATOR_NOT_PLACEBO", "COMPARATOR"),
    ("PROTOCOL_TEXT:POPULATION", "POPULATION"),
    ("PROTOCOL_TEXT:INTERVENTION_DOSE_AND_REGIMEN", "INTERVENTION_DOSE_OR_REGIMEN"),
    ("PROTOCOL_TEXT:DESIGN_AND_COMPARATOR", "DESIGN"),
    ("G1-OUTCOME-SET", "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS"),
    ("NOT_IN_COMPARATOR_OUTCOME_ANALYSIS", "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS"),
    ("G1-ONE-TRIAL-ONE-UNIT", "DESIGN"), ("SAME_TRIAL_AS_ANOTHER_UNIT", "DESIGN"),
    ("GATE:composite_component_mismatch", "OUTCOME_DEFINITION"), ("ESTIMAND_DIFFERENCE", "ESTIMAND"),
    ("NOT_AN_INCLUDED_TRIAL", "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS"),
    ("COMPARATOR_STATED_K", "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS"),
    ("DECISION_EXCLUDED_FROM_SERVED_POOL", "DECISION_EXCLUDED"),
    ("NAMED_DIVERGENCE_POST_HOC_SAFETY_POPULATION_ON_TREATMENT_WINDOW", "ANALYSIS_SET")])
def test_mapping_rows(rule, expected):
    assert api().reason_code({"rule_id": rule}) == expected


@pytest.mark.parametrize("rule,protocol,expected", [
    ("X3", "include.comparator_any", "COMPARATOR"),
    ("X3", "include.intervention_any", "INTERVENTION_DOSE_OR_REGIMEN"),
    ("ARM_OBJECT", "arm_object.dose.required", "INTERVENTION_DOSE_OR_REGIMEN"),
    ("ARM_OBJECT", "primary_outcome.timepoint", "TIMEPOINT"),
    ("X3", "unknown", None), ("ARM_OBJECT", "unknown", None),
    ("GATE:unknown", "", None), ("PROTOCOL_TEXT:unknown", "", None), ("unknown", "", None)])
def test_conditional_mapping_rows(rule, protocol, expected):
    assert api().reason_code(dict(rule_id=rule, protocol_rule=protocol)) == expected


def test_closed_axis_mapping_and_vocab_are_imported():
    from scripts import g1_explanation_vocab as vocab
    for axis in vocab.REASON_CODES:
        assert api().reason_code({"rule_id": "PROTOCOL_TEXT:" + axis}) == axis
    for name in ("REASON_CODES", "STATES", "SOURCES", "STEPS", "ACCESS_OUTCOMES", "FRESH_DAYS"):
        assert getattr(api(), name) is getattr(vocab, name)
    assert set(api().RULE_REASONS.values()) <= set(vocab.REASON_CODES)
    assert set(api().APPLICABILITY) == set(vocab.SOURCES)


@pytest.mark.parametrize("stamp,valid", [("2026-09-14T00:00:00Z", False),
                                       ("2026-09-15T00:00:00Z", True),
                                       ("2026-10-16T00:00:00Z", False),
                                       ("2026-10-15", False)])
def test_freshness_boundary_and_invalid_dates(stamp, valid):
    log = search()
    log["searched"][0]["when_utc"] = stamp
    got = api().build_explanation({}, search_log=log, **context())
    assert (got["state"] == "NO_OPEN_SOURCE") is valid
    if not valid:
        assert "PUBMED_EPMC_TITLE" in got["why_unexplained"]


@pytest.mark.parametrize("gate", ["BLOCKED_BOT_CHALLENGE", "BLOCKED_ACCOUNT", "BLOCKED_TERMS", "ERROR",
                                  "NOT_ATTEMPTED_PENDING_DECISION"])
def test_required_source_gate_never_counts(gate):
    log = search()
    log["searched"][1]["step_reached"] = gate
    got = api().build_explanation({}, search_log=log, **context())
    assert got["state"] == "UNEXPLAINED"
    assert "required source WHO_ICTRP gated:" in got["why_unexplained"]
    assert gate in got["why_unexplained"]


def test_all_missing_and_stale_sources_are_named():
    log = search()
    log["identifiers"].update(pmids=["synthetic"], dois=["synthetic"], ncts=["synthetic"],
                              eudract=["synthetic"], approved_drug=True)
    log["searched"][0]["when_utc"] = "2026-09-14T00:00:00Z"
    got = api().build_explanation({}, search_log=log, **context())
    for source in api().required_sources(log["identifiers"]):
        if source != "WHO_ICTRP":
            assert source in got["why_unexplained"]


def test_optional_gate_is_recorded_but_not_required():
    log = search()
    log["searched"].append(dict(log["searched"][0], source="HEALTH_CANADA", step_reached="BLOCKED_ACCOUNT"))
    got = api().build_explanation({}, search_log=log, **context())
    assert got["state"] == "NO_OPEN_SOURCE" and len(got["searched"]) == 3


@pytest.mark.parametrize("route", ["TWO_SOURCE", "SECONDARY_SINGLE", "SWEEP_SECONDARY_SINGLE"])
def test_secondary_values_are_available_but_never_matched(route):
    got = api().build_explanation({"route": route}, search_log=search(),
                                  primary=dict(source_ref="synthetic", sha256=SHA, verified_by="reader"), **context())
    assert got["state"] == "NO_OPEN_SOURCE" and got["secondary_value_available"] is True


def test_precedence_and_invalid_divergence_note():
    primary = dict(source_ref="synthetic", sha256=SHA, verified_by="reader")
    got = api().build_explanation({"route": "PRIMARY"}, primary=primary, divergences=[divergence()],
                                  search_log=search(), **context())
    assert got["state"] == "MATCHED"
    got = api().build_explanation({}, divergences=[divergence()], search_log=search(), **context())
    assert got["state"] == "DIVERGENT_NAMED"
    bad = divergence()
    bad["evidence"]["verbatim_span"] = "Absent synthetic text"
    got = api().build_explanation({}, divergences=[bad], search_log=search(), **context())
    assert got["state"] == "NO_OPEN_SOURCE"
    assert "DIVERGENT_NAMED span not in held bytes" in got["note"]


def test_whole_document_and_whitespace_normalization():
    body = b"prefix " * 20000 + b"The analysis\nused the safety population."
    entry = divergence()
    entry["evidence"]["sha256"] = hashlib.sha256(body).hexdigest()
    ctx = dict(context(), held_bytes=lambda sha: body)
    assert api().validate_explanation(entry, {}, **ctx) == []
    ctx["held_bytes"] = lambda sha: body[:100]
    assert "hash mismatch" in "; ".join(api().validate_explanation(entry, {}, **ctx))
    ctx["held_bytes"] = lambda sha: None
    assert "held bytes not committed" in "; ".join(api().validate_explanation(entry, {}, **ctx))


def test_known_decision_and_schema_rejection():
    entry = dict(divergence(), reason_code="DECISION_EXCLUDED", decided_by="SYNTHETIC-DECISION")
    assert api().validate_explanation(entry, {}, **context()) == []
    for key in ("detail", "evidence", "decided_by", "reason_code"):
        broken = dict(entry)
        broken.pop(key)
        assert api().validate_explanation(broken, {}, **context())


class SyntheticRecords:
    def __init__(self, files=None):
        self.files = files or {}

    def json(self, path):
        return self.files.get(path, {})

    def read(self, path):
        return None

    def held_bytes(self, sha):
        return BODY if sha == SHA else None

    def evidence(self, record, slug):
        return record.get("evidence", {})


def test_gate_every_trial_has_one_valid_state_and_totals_preserve_legacy_fields():
    import copy
    trials = [{"label": "primary", "route": "PRIMARY", "primary_provenance":
               dict(source_ref="synthetic", sha256=SHA, verified_by="reader")},
              {"label": "divergent", "route": "NO_ROW", "scope_difference":
               dict(divergence(), kind="ESTIMAND_DIFFERENCE")},
              {"label": "secondary", "route": "SECONDARY_SINGLE"}, {"label": "unknown", "route": "NO_ROW"}]
    topic = dict(slug="synthetic", trials=trials, k_matched=99, N_comparator_trials=4, N_eligible=3)
    before = copy.deepcopy(topic)
    records = SyntheticRecords({"registry/g1_search_log/synthetic.json":
                                dict(slug="synthetic", trials={"secondary": search()})})
    api().attach_explanations(topic, build_date=DAY, records=records)
    assert topic["matched"] == 1 and topic["explained"] == 3
    assert topic["unexplained_trials"] == ["unknown"]
    for trial in trials:
        assert api().validate_explanation(trial["g1_explanation"], trial,
                                          identifiers=search()["identifiers"], **context()) == []
    for key in before:
        if key != "trials":
            assert topic[key] == before[key]
    for old, new in zip(before["trials"], trials):
        assert old == {k: v for k, v in new.items() if k != "g1_explanation"}


def test_not_bound_uses_ruling_axis_and_ruler_but_missing_span_is_unexplained():
    trial = dict(label="Synthetic", route="NO_ROW")
    key = "synthetic|Synthetic|" + SHA
    records = SyntheticRecords({"registry/g1_regulatory_bindings.json": {key: dict(
        decision="NOT_BOUND", reason="NAMED_DIVERGENCE_POST_HOC_SAFETY_POPULATION_ON_TREATMENT_WINDOW",
        ruled_by="synthetic captain", ruled_on="2026-10-15", evidence=divergence()["evidence"])}})
    topic = dict(slug="synthetic", trials=[trial])
    api().attach_explanations(topic, build_date=DAY, records=records)
    assert trial["g1_explanation"]["state"] == "DIVERGENT_NAMED"
    assert trial["g1_explanation"]["reason_code"] == "ANALYSIS_SET"
    assert trial["g1_explanation"]["decided_by"] == "synthetic captain / 2026-10-15"
    del records.files["registry/g1_regulatory_bindings.json"][key]["evidence"]
    api().attach_explanations(topic, build_date=DAY, records=records)
    assert trial["g1_explanation"]["state"] == "UNEXPLAINED"


def test_committed_resolver_never_reads_local_or_window_bytes(tmp_path):
    import subprocess
    def git(*args):
        return subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)
    git("init")
    folder = tmp_path / "outputs" / "k_gap" / "_ft"
    folder.mkdir(parents=True)
    path = folder / "synthetic.txt"
    path.write_bytes(BODY)
    git("add", "outputs")
    git("-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid", "commit", "-m", "Synthetic fixture")
    path.write_bytes(b"local changed bytes")
    (folder / "untracked.txt").write_bytes(b"untracked body")
    store = api().CommittedRecords(tmp_path)
    assert store.held_bytes(SHA) == BODY
    assert store.held_bytes(hashlib.sha256(b"untracked body").hexdigest()) is None
    assert store.held_bytes(hashlib.sha256(BODY[:10]).hexdigest()) is None
    assert store.read("../escape") is None


@pytest.mark.parametrize("kind", ["pmid", "doi", "nct", "regulator", "embedded"])
def test_whole_document_index_resolution_without_real_stores(kind):
    import json
    store = api().CommittedRecords.__new__(api().CommittedRecords)
    store.blobs, store.by_sha, store.scanned = {}, {}, False
    store.revision = "synthetic-commit"
    key = "synthetic"
    token = hashlib.sha1(key.encode()).hexdigest()[:16]
    paths = {"pmid": ("outputs/k_gap/fulltext_index.json", "outputs/k_gap/_ft/synthetic.txt"),
             "doi": ("outputs/k_gap/unpaywall_text_index.json", f"outputs/k_gap/_upw/{token}.txt"),
             "nct": ("outputs/k_gap/ctgov_index.json", "outputs/k_gap/_ctgov/synthetic.json"),
             "regulator": ("registry/regulatory_sources.json", f"outputs/k_gap/_reg/{token}.txt")}
    if kind == "embedded":
        files = {"cache/synthetic/records.json": json.dumps({"fulltext_by_pmid": {key: BODY.decode()}}).encode()}
    else:
        index, doc = paths[kind]
        field = "text_sha256" if kind == "regulator" else "sha256"
        files = {index: json.dumps({key: {field: SHA}}).encode(), doc: BODY}
    store.paths = set(files)
    store._git = lambda *args: files[args[1].split(":", 1)[1]]
    assert store.held_bytes(SHA) == BODY


def test_aact_primary_uses_the_recorded_snapshot_and_guard():
    trial = dict(route="SWEEP_AACT_PRIMARY", sweep={"basis": dict(
        nct="synthetic-nct", outcome="synthetic outcome", guard="synthetic verified guard",
        snapshot={"id": "synthetic snapshot", "digest": SHA})})
    primary = api()._primary(trial, SyntheticRecords())
    assert primary["sha256"] == SHA and "synthetic snapshot" in primary["source_ref"]
    assert api().build_explanation(trial, primary=primary, **context())["state"] == "MATCHED"


def test_canonical_totals_include_all_comparator_trials_and_preserve_existing_count():
    from scripts import g1_tracker
    trials = [dict(label=state, route="NO_ROW", g1_explanation={"state": state}) for state in api().STATES]
    topic = dict(slug="synthetic", trials=trials, k_matched=99, N_comparator_trials=4, N_eligible=3)
    result = g1_tracker.canonical([topic])
    assert result["totals"]["k_matched"] == 99
    assert result["totals"]["matched"] == 1 and result["totals"]["explained"] == 3
    assert result["explanation_by_topic"]["synthetic"] == dict(matched=1, explained=3, N=4,
                                                               unexplained_trials=["UNEXPLAINED"])


def test_incomplete_applicability_evidence_never_defaults_to_not_applicable():
    log = search()
    del log["identifiers"]["approved_drug"]
    del log["identifiers"]["title"]
    result = api().build_explanation({}, search_log=log, **context())
    assert result["state"] == "UNEXPLAINED"
    assert "approved_drug" in result["why_unexplained"] and "title" in result["why_unexplained"]


def test_builder_does_not_mutate_committed_inputs():
    import copy
    trial, log, candidate = {"route": "SECONDARY_SINGLE"}, search(), divergence()
    before = copy.deepcopy((trial, log, candidate))
    api().build_explanation(trial, search_log=log, divergences=[candidate], **context())
    assert (trial, log, candidate) == before
