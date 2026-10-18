"""Synthetic explanation contracts and an offline all-topic denominator regression."""
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


def test_PLANT_latest_record_per_source_identifier_decides():
    """16 Oct: with 'any fresh record' an older NOT_FOUND satisfied a source whose NEWER record says NEW_REPORT_FOUND,
    and why_unexplained quoted a superseded ERROR. The latest record per (source, identifier) decides."""
    log = search()
    first = log["searched"][0]
    newer = dict(first, when_utc="2026-10-15T12:00:00Z", step_reached="NEW_REPORT_FOUND", outcome="new PMID")
    log["searched"][0] = dict(first, when_utc="2026-10-15T00:00:00Z", step_reached="NOT_FOUND")
    log["searched"].append(newer)
    got = api().build_explanation({}, search_log=log, **context())
    assert got["state"] == "UNEXPLAINED" and "NEW_REPORT_FOUND" in got["why_unexplained"]
    old_error = dict(first, when_utc="2026-10-15T00:00:00Z", step_reached="ERROR", outcome="superseded")
    log2 = search()
    log2["searched"][0] = dict(log2["searched"][0], when_utc="2026-10-15T12:00:00Z")
    log2["searched"].insert(0, old_error)
    got2 = api().build_explanation({}, search_log=log2, **context())
    assert got2["state"] == "NO_OPEN_SOURCE" and "superseded" not in (got2.get("why_unexplained") or "")


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
    store._read_many = lambda paths: [store.read(path) for path in paths]
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
                                                               n_no_open_source_with_unreachable=0,
                                                               unexplained_trials=["UNEXPLAINED"])
    assert result["totals"]["explained_all"] == 3 and result["totals"]["explained_without_unreachable"] == 3


def test_PLANT_explained_is_also_reported_without_unreachable_only_trials():
    """Ruling 18 Oct: a technical block is not a search; a NO_OPEN_SOURCE that lists an unreachable source is counted
    in explained_all but NOT in explained_without_unreachable."""
    from scripts import g1_tracker
    trials = [dict(label="a", route="NO_ROW", g1_explanation={"state": "NO_OPEN_SOURCE",
                                                               "unreachable": [{"source": "WHO_ICTRP"}]}),
              dict(label="b", route="NO_ROW", g1_explanation={"state": "NO_OPEN_SOURCE", "unreachable": []})]
    topic = dict(slug="synthetic", trials=trials, k_matched=0, N_comparator_trials=2, N_eligible=2)
    t = g1_tracker.canonical([topic])["totals"]
    assert (t["explained_all"], t["explained_without_unreachable"], t["n_no_open_source_with_unreachable"]) == (2, 1, 1)


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


@pytest.mark.parametrize("outcome,valid", [("recorded result", True), ({"status": "no result"}, True),
                                            ({}, False), ([], False), (None, False), ("  ", False)])
def test_job_b_outcome_shapes(outcome, valid):
    log = search()
    log["searched"][0]["outcome"] = outcome
    got = api().build_explanation({}, search_log=log, **context())
    assert (got["state"] == "NO_OPEN_SOURCE") is valid


def test_derived_queries_use_source_identifiers_without_mutation():
    import copy
    log = search()
    log["identifiers"]["pmids"] = ["synthetic-pmid"]
    rec = dict(log["searched"][0], source="PUBMED_EPMC_PMID", identifier_or_query=None,
               outcome={"status": "derived"})
    log["searched"].append(rec)
    log["searched"][0]["identifier_or_query"] = ""
    before = copy.deepcopy(log)
    got = api().build_explanation({}, search_log=log, **context())
    assert got["state"] == "NO_OPEN_SOURCE"
    assert got["searched"][-1]["identifier_or_query"] == "PUBMED_EPMC_PMID: synthetic-pmid"
    assert "Synthetic" in got["searched"][0]["identifier_or_query"]
    assert log == before


def test_missing_query_cannot_be_invented_without_identifiers():
    log = search()
    log["identifiers"].update(title=None, acronym=None)
    log["searched"][0]["identifier_or_query"] = None
    assert api().build_explanation({}, search_log=log, **context())["state"] == "UNEXPLAINED"


@pytest.mark.parametrize("step", api().ACCESS_OUTCOMES)
def test_dictionary_outcomes_do_not_bypass_access_gates(step):
    log = search()
    log["searched"][0].update(step_reached=step, outcome={"status": step})
    got = api().build_explanation({}, search_log=log, **context())
    assert got["state"] == "UNEXPLAINED"
    assert f"required source PUBMED_EPMC_TITLE gated: {step}" in got["why_unexplained"]


class AdapterRecords(SyntheticRecords):
    source_document = api().CommittedRecords.source_document
    evidence = api().CommittedRecords.evidence

    def read(self, path):
        import json
        obj = self.files.get(path.split("#", 1)[0])
        return json.dumps(obj, sort_keys=True).encode() if obj is not None else None

    def record_digest(self, rid):
        if rid == "synthetic-call":
            return "registry/model_calls/synthetic-call.json", SHA


def test_acquired_primary_hashes_the_recorded_call_not_the_identifier():
    trial = dict(route="PRIMARY", acquired=dict(source="synthetic registry outcome", record_id="synthetic-call"))
    got = api()._primary(trial, AdapterRecords(), "synthetic")
    assert got["sha256"] == SHA and got["verified_by"] == "synthetic-call"
    trial["acquired"]["record_id"] = "missing-call"
    assert api()._primary(trial, AdapterRecords(), "synthetic") is None


def test_comparator_provenance_is_never_primary_provenance():
    trial = dict(route="PRIMARY", comparator_sourced=dict(provenance=dict(digest=SHA, read="synthetic-call")),
                 comparator_row_provenance=dict(digest=SHA, read="synthetic-call"))
    assert api()._primary(trial, AdapterRecords(), "synthetic") is None


def test_signed_extraction_record_requires_identity_and_current_value():
    path = "docs/reviews/synthetic/review.json"
    row = dict(id="PMID synthetic", effect=2, ci_low=1, ci_high=3, provenance="served_pool_signed_notice",
               served_pool_admission={"route": "PRIMARY"}, verified="verified", source="synthetic source span",
               verify_basis="synthetic gate")
    store = AdapterRecords({path: {"outcomes": [{"primary": True, "trials": [row]}]}})
    trial = dict(route="PRIMARY", family=row["id"], in_our_pool=True,
                 our_value=dict(effect="2", lower="1", upper="3"))
    got = api()._primary(trial, store, "synthetic")
    assert got["sha256"] == hashlib.sha256(store.read(path)).hexdigest()
    assert got["sha256_kind"] == "recorded_extraction" and row["id"] in got["source_ref"]
    trial["our_value"]["effect"] = "9"
    assert api()._primary(trial, store, "synthetic") is None
    trial["our_value"]["effect"] = "2"
    trial["family"] = "another report"
    assert api()._primary(trial, store, "synthetic") is None


def test_primary_continuous_values_are_taken_from_current_pool_at_attachment():
    row = dict(id="NCT00000000", mean1=2, sd1=1, nc1=20, mean2=1, sd2=1, nc2=20,
               provenance="served_pool_signed_notice", served_pool_admission={"route": "PRIMARY"},
               verified="verified", source="synthetic registry means", verify_basis="synthetic gate")
    store = AdapterRecords({"docs/reviews/synthetic/review.json":
                            {"outcomes": [{"primary": True, "trials": [row]}]}})
    trial = dict(route="PRIMARY", label="Synthetic", family=row["id"], in_our_pool=True,
                 our_value=dict(n_t=20, n_c=20))
    assert api()._primary(trial, store, "synthetic") is None
    assert api()._primary(trial, store, "synthetic", [row])["sha256_kind"] == "recorded_extraction"


def test_registry_source_follows_recorded_pmid_to_nct_and_requires_posted_results():
    store = AdapterRecords({"cache/synthetic/records.json": {"records": [dict(id="123", nct="NCT00000000")]},
                            "outputs/k_gap/ctgov_index.json": {"NCT00000000": dict(sha256=SHA, posted=True)}})
    doc = store.source_document("synthetic", "123", "ctgov_results")
    assert "NCT00000000" in doc[0] and doc[1] == SHA
    store.files["outputs/k_gap/ctgov_index.json"]["NCT00000000"]["posted"] = False
    assert store.source_document("synthetic", "123", "ctgov_results") is None


def test_fulltext_scope_span_resolves_document_hash_from_its_own_pmid():
    store = AdapterRecords({"outputs/k_gap/fulltext_index.json": {"123": dict(sha256=SHA, copy_licence="CC")}})
    ev = store.evidence(dict(pmid="123", span=dict(field="fulltext", text="Synthetic report.")), "synthetic")
    assert ev["sha256"] == SHA and "123" in ev["source_ref"]
    assert store.evidence(dict(pmid="456", span=dict(field="fulltext", text="Synthetic report.")),
                          "synthetic").get("sha256") is None


def test_toci_reading_must_match_selected_tuple_and_bound_record():
    path = "g1/data/vnh_reads.json"
    counts = dict(deaths_t=1, n_t=10, deaths_c=2, n_c=11)
    candidate = dict(counts, label="Synthetic", span="synthetic span", extractor="TABLE")
    rec = dict(state="VERIFIED_NOT_HELD", bound_labels=["Synthetic"], candidates=[candidate])
    store = AdapterRecords({path: {"123": rec}})
    trial = dict(label="Synthetic", route="PRIMARY", our_value=dict(events_t=1, n_t=10, events_c=2, n_c=11),
                 readings=[dict(values=counts, sources=[dict(source="TEXT PMID 123 (VERIFIED_NOT_HELD)",
                                                            span="synthetic span")])])
    got = api()._primary(trial, store, "synthetic")
    assert got["sha256"] == hashlib.sha256(store.read(path)).hexdigest()
    assert got["sha256_kind"] == "recorded_read"
    trial["our_value"]["events_t"] = 3
    assert api()._primary(trial, store, "synthetic") is None


@pytest.fixture(scope="module")
def regenerated_topics(tmp_path_factory):
    import os
    from pathlib import Path
    from scripts import g1_tracker
    # CI can consume the same full regeneration just produced by the preview
    # command. Without it this is a real offline build, not a snapshot-only test.
    supplied = os.environ.get("G1_EXPLANATION_REGEN_DIR")
    if supplied:
        return Path(supplied)
    target = tmp_path_factory.mktemp("g1-regenerated")
    slugs = sorted(p.stem for p in Path(g1_tracker.G1_DIR).glob("*.json"))
    g1_tracker.main([*slugs, "--out-dir", str(target), "--no-table"])
    return target


def _topic_slugs():
    from pathlib import Path
    return sorted(p.stem for p in (Path(__file__).resolve().parents[1] / "outputs/k_gap/g1").glob("*.json"))


@pytest.mark.parametrize("slug", _topic_slugs())
def test_regeneration_preserves_every_committed_topic_denominator(slug, regenerated_topics):
    import json
    import subprocess
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    committed = json.loads(subprocess.check_output(["git", "-C", str(root), "show",
                                                   f"HEAD:outputs/k_gap/g1/{slug}.json"]))
    generated = json.loads((regenerated_topics / f"{slug}.json").read_text(encoding="utf-8"))
    assert generated["N_comparator_trials"] == committed["N_comparator_trials"]
    assert len(generated["trials"]) == len(committed["trials"])
    assert all(t.get("g1_explanation", {}).get("state") in api().STATES for t in generated["trials"])


def test_tracker_cli_dispatches_toci_to_its_own_builder_and_keeps_default_output_untouched(tmp_path, monkeypatch):
    import copy
    import json
    from scripts import g1_tracker, g1_toci_tracker
    monkeypatch.setattr(g1_tracker, "_j", lambda p: {})
    monkeypatch.setattr(g1_tracker, "with_identity_chain", lambda x: x)
    monkeypatch.setattr(g1_tracker, "topic", lambda *a, **k: pytest.fail("generic builder used for toci"))
    monkeypatch.setattr(g1_tracker, "cite_or_demote", lambda d, s: d)
    monkeypatch.setattr(g1_tracker, "g1_status", lambda d: {})
    monkeypatch.setattr(api(), "committed_records", lambda root: SyntheticRecords())
    fixture = dict(slug=g1_toci_tracker.SLUG, trials=[dict(label="Synthetic", route="NO_ROW")])
    monkeypatch.setattr(g1_toci_tracker, "build", lambda: copy.deepcopy(fixture))
    monkeypatch.setattr(g1_tracker, "table", lambda: pytest.fail("preview must not write canonical table"))
    g1_tracker.main([g1_toci_tracker.SLUG, "--out-dir", str(tmp_path)])
    got = json.loads((tmp_path / f"{g1_toci_tracker.SLUG}.json").read_text())
    assert got["trials"][0]["g1_explanation"]["state"] == "UNEXPLAINED"


@pytest.mark.parametrize("query", [42, [], {}])
def test_invalid_query_types_are_not_repaired_as_missing_derived_queries(query):
    log = search()
    log["searched"][0]["identifier_or_query"] = query
    got = api().build_explanation({}, search_log=log, **context())
    assert got["state"] == "UNEXPLAINED"
    assert "identifier_or_query" in got["why_unexplained"]


def test_empty_registry_result_is_not_primary_source_evidence():
    store = AdapterRecords({"cache/synthetic/records.json":
                            {"records": [dict(id="NCT00000000", nct="NCT00000000")],
                             "ctgov_results": {"NCT00000000": None}}})
    assert store.source_document("synthetic", "NCT00000000", "ctgov_results") is None


@pytest.mark.parametrize("step", api().UNREACHABLE_STEPS)
def test_blocked_source_requires_explicit_fresh_unreachable_listing(step):
    log = search()
    log["searched"][1].update(step_reached=step, outcome="Synthetic access block")
    assert api().build_explanation({}, search_log=log, **context())["state"] == "UNEXPLAINED"
    log["unreachable"] = [dict(source="WHO_ICTRP", when_utc="2026-10-15T00:00:00Z", reason="Synthetic access block")]
    got = api().build_explanation({}, search_log=log, **context())
    assert got["state"] == "NO_OPEN_SOURCE"
    assert got["unreachable"] == log["unreachable"]
    log["unreachable"][0]["when_utc"] = "2026-09-01T00:00:00Z"
    assert api().build_explanation({}, search_log=log, **context())["state"] == "UNEXPLAINED"


@pytest.mark.parametrize("step", ["OPEN_NOT_ASSESSED", "NEW_REPORT_FOUND", "NOT_ATTEMPTED_PENDING_DECISION"])
def test_unfinished_work_is_never_unreachable(step):
    log = search()
    log["searched"][1].update(step_reached=step)
    log["unreachable"] = [dict(source="WHO_ICTRP", when_utc="2026-10-15T00:00:00Z", reason="Not finished")]
    assert api().source_states(log["searched"]) == []
    assert api().build_explanation({}, search_log=log, **context())["state"] == "UNEXPLAINED"


def test_unreachable_counts_and_latest_identifier_work():
    log = search()
    log["searched"][1].update(step_reached="BLOCKED_JS_ONLY", outcome="ICTRP JS-only")
    records = SyntheticRecords({"registry/g1_search_log/synthetic.json": dict(slug="synthetic", trials={"S": log})})
    topic = dict(slug="synthetic", trials=[dict(label="S", route="NO_ROW")])
    api().attach_explanations(topic, build_date=DAY, records=records)
    assert topic["explained"] == topic["explained_all"] == topic["n_no_open_source_with_unreachable"] == 1
    assert topic["explained_without_unreachable"] == 0
    states = api().source_states(log["searched"])
    assert states[0]["state"] == "SOURCE_UNREACHABLE"
    log["searched"].append(dict(log["searched"][1], step_reached="OPEN_NOT_ASSESSED", when_utc="2026-10-15T12:00:00Z"))
    assert api().source_states(log["searched"]) == []
    api().attach_explanations(topic, build_date=DAY, records=records)
    assert topic["explained_all"] == 0


def test_one_successful_identifier_cannot_mask_an_unfinished_identifier():
    log = search()
    log["searched"].append(dict(log["searched"][0], identifier_or_query="Other", step_reached="OPEN_NOT_ASSESSED"))
    assert api().build_explanation({}, search_log=log, **context())["state"] == "UNEXPLAINED"


def test_pmda_is_required_reachable_for_approved_drugs():
    log = search()
    log["identifiers"]["approved_drug"] = True
    for source in api().required_sources(log["identifiers"]):
        if source not in {r["source"] for r in log["searched"]}:
            log["searched"].append(dict(log["searched"][0], source=source))
    assert api().build_explanation({}, search_log=log, **context())["state"] == "NO_OPEN_SOURCE"
    next(r for r in log["searched"] if r["source"] == "PMDA")["step_reached"] = "NOT_ATTEMPTED_PENDING_DECISION"
    assert api().build_explanation({}, search_log=log, **context())["state"] == "UNEXPLAINED"


class EvidenceRecords(AdapterRecords):
    def record_digest(self, rid):
        path = "evidence/model_calls/" + rid + ".json"
        body = self.read(path)
        return (path, hashlib.sha256(body).hexdigest()) if body else None


def recorded_fixture():
    import base64
    answer = b'{"quote":"The analysis used the safety population."}'
    record = dict(record_id="synthetic-call", prompt="Prompt only quotation", response=dict(
        b64=base64.b64encode(answer).decode(), sha256=hashlib.sha256(answer).hexdigest(), bytes=len(answer)))
    store = EvidenceRecords({"evidence/model_calls/synthetic-call.json": record})
    entry = divergence()
    entry["evidence"] = dict(kind="RECORDED_READ", record_id="synthetic-call",
                             sha256=store.record_digest("synthetic-call")[1],
                             verbatim_span="The analysis used the safety   population.")
    ctx = context()
    ctx["held_bytes"] = store.held_bytes
    return entry, store, ctx


def test_recorded_read_validates_answer_not_prompt_and_whole_record_hash():
    entry, store, ctx = recorded_fixture()
    assert api().validate_explanation(entry, {}, **ctx) == []
    entry["evidence"]["verbatim_span"] = "Prompt only quotation"
    assert "span missing" in "; ".join(api().validate_explanation(entry, {}, **ctx))
    entry["evidence"]["sha256"] = "0" * 64
    assert "sha mismatch" in "; ".join(api().validate_explanation(entry, {}, **ctx))
    entry["evidence"]["record_id"] = "missing-call"
    assert "not committed" in "; ".join(api().validate_explanation(entry, {}, **ctx))


def test_registry_record_requires_snapshot_and_outcome_identity():
    path = "evidence/synthetic-registry.json"
    store = EvidenceRecords({path: dict(_snapshot=dict(id="synthetic snapshot"),
                                       outcomes={"123": dict(title="Synthetic outcome")})})
    entry = divergence()
    entry["evidence"] = dict(kind="REGISTRY_RECORD", record_id=path,
                             sha256=hashlib.sha256(store.read(path)).hexdigest(),
                             snapshot_id="synthetic snapshot", outcome_id="123", verbatim_span="Synthetic outcome")
    ctx = dict(context(), held_bytes=store.held_bytes)
    assert api().validate_explanation(entry, {}, **ctx) == []
    entry["evidence"]["outcome_id"] = "456"
    assert "absent" in "; ".join(api().validate_explanation(entry, {}, **ctx))
    entry["evidence"]["outcome_id"] = "123"
    entry["evidence"]["snapshot_id"] = "another snapshot"
    assert "mismatched" in "; ".join(api().validate_explanation(entry, {}, **ctx))


def test_unresolved_record_never_falls_back_to_no_open_source():
    entry, store, ctx = recorded_fixture()
    entry["evidence"]["verbatim_span"] = "Absent from answer"
    result = api().build_explanation({}, search_log=search(), divergences=[entry], **ctx)
    assert result["state"] == "UNEXPLAINED"
    assert "span missing" in result["why_unexplained"]


def test_missing_pmc_primary_names_the_missing_file():
    trial = dict(route="PRIMARY", in_our_pool=True,
                 basis="our held-source pool PMID 123 (pmc_fulltext)")
    primary = api()._primary(trial, AdapterRecords(), "synthetic")
    result = api().build_explanation(trial, primary=primary, **context())
    assert result["state"] == "UNEXPLAINED"
    assert "outputs/k_gap/_ft/123.txt" in result["why_unexplained"]
