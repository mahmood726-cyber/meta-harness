"""The served evidence bundle (schema 3): every object the certificate commits a digest to is reachable from
BUNDLE.json byte-identical to its digest and never silently omitted; every evidential document carries four
representations with coverage_status backed by a preservation record; every primary-pool row carries recomputable
admission predicates; every absence claim is judged by the asymmetric rule; the resolvability walk ends in bytes.

Closes the 2026-09-19 defects: 14 of 18 probed URLs 404 (v1); "verified against source" that meant "located in our
cache" (v2); digests without bodies and an absence claim from a truncated abstract (v3).
See scripts/build_bundle.py for the design and scripts/verify_bundle.py for the independent checker.
"""
import hashlib
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import build_bundle  # noqa: E402

SLUG = "glp1-ra-mace-t2d"
REVIEW_DIR = os.path.join(ROOT, "docs", "reviews", SLUG)
BUNDLE = os.path.join(REVIEW_DIR, "BUNDLE.json")
CERT = os.path.join(REVIEW_DIR, "CERTIFICATE.json")


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _bytes(path):
    with open(path, "rb") as f:
        return f.read()


def _check_attr(path):
    out = subprocess.run(["git", "check-attr", "text", "--", path], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return out.rsplit(":", 1)[-1].strip()


@pytest.fixture(scope="module")
def bundle():
    if not os.path.exists(BUNDLE):
        pytest.fail("docs/reviews/%s/BUNDLE.json absent -- python scripts/build_bundle.py %s" % (SLUG, SLUG))
    return _load(BUNDLE)


# ------------------------------------------------------------------ v1: served, byte-identical, never omitted

def test_bundle_is_current():
    """A stale bundle is the same defect as no bundle: a digest table that does not describe the served bytes."""
    _, problems = build_bundle.build(SLUG, check_only=True)
    assert not problems, "\n".join(problems)


def test_certificate_unmodified(bundle):
    raw = _bytes(CERT)
    assert bundle["certificate_unmodified"] is True
    assert bundle["certificate"]["sha256_of_file"] == hashlib.sha256(raw).hexdigest()
    assert bundle["certificate"]["release_sha256"] == json.loads(raw)["release_sha256"]


def test_every_certificate_input_appears_in_one_state(bundle):
    cert = _load(CERT)
    expected = {e["ref"] for e in build_bundle.enumerate_inputs(SLUG, cert)} | {h["ref"] for h in cert["held_documents"]}
    listed = {a["ref"] for a in bundle["artefacts"]}
    assert listed == expected, {"missing": sorted(expected - listed), "extra": sorted(listed - expected)}
    assert {a["state"] for a in bundle["artefacts"]} <= {"SERVED", "NOT_IN_PACKAGE_LICENCE"}
    assert bundle["counts"]["served"] + bundle["counts"]["not_in_package_licence"] == len(bundle["artefacts"])


def test_served_bytes_match_declared_digests(bundle):
    for a in bundle["artefacts"]:
        if a["state"] != "SERVED":
            continue
        data = _bytes(os.path.join(ROOT, "docs", *a["ref"].split("/")))
        assert len(data) == a["bytes"] and hashlib.sha256(data).hexdigest() == a["sha256"], a["ref"]
        if a["declared_digest"] is not None:
            assert build_bundle.recompute(a, data) == a["declared_digest"], (a["ref"], a["role"])


def test_licence_held_inputs_expose_reference_and_method(bundle):
    """PMC separates access from reuse: the reference, the verification method and the external-access dependency
    are stated; the bytes we hold still hash to the certificate's digest; nothing is served at the ref."""
    held = [a for a in bundle["artefacts"] if a["state"] == "NOT_IN_PACKAGE_LICENCE"]
    assert len(held) == 2
    for a in held:
        assert a["served_path"] is None and a["obtain_from"].startswith("https://") and a["external_access_dependency"]
        assert not os.path.exists(os.path.join(ROOT, "docs", *a["ref"].split("/")))
        assert hashlib.sha256(_bytes(os.path.join(ROOT, *a["ref"].split("/")))).hexdigest() == a["sha256"] == a["declared_digest"]


def test_mirror_and_acquisition_paths_are_never_normalised(bundle):
    """The CRLF trap: every served mirror path and every acquisition file carries -text (git's own resolution)."""
    crlf_seen = 0
    for a in bundle["artefacts"]:
        if a["state"] == "SERVED":
            rel = "docs/" + a["ref"]
            assert _check_attr(rel) == "unset", rel
            crlf_seen += b"\r" in _bytes(os.path.join(ROOT, *rel.split("/")))
    for f in bundle["supporting_files"]:
        assert _check_attr(f["path"]) == "unset", f["path"]
    assert crlf_seen >= 3
    assert _check_attr("docs/reviews/%s/review.json" % SLUG) == "auto"


def test_normalised_copy_would_be_refused(bundle):
    victim = next(a for a in bundle["artefacts"] if a["state"] == "SERVED" and a["ref"].endswith(".pdf.txt")
                  and b"\r" in _bytes(os.path.join(ROOT, *a["ref"].split("/"))))
    data = _bytes(os.path.join(ROOT, *victim["ref"].split("/")))
    assert build_bundle.recompute(victim, data.replace(b"\r\n", b"\n")) != victim["declared_digest"]
    assert build_bundle.recompute(victim, data) == victim["declared_digest"]


def test_review_files_listed_with_current_digests(bundle):
    listed = {r["file"]: r for r in bundle["review_files"]}
    on_disk = {n for n in os.listdir(REVIEW_DIR) if os.path.isfile(os.path.join(REVIEW_DIR, n)) and n != "BUNDLE.json"}
    assert set(listed) == on_disk
    for name, row in listed.items():
        data = _bytes(os.path.join(REVIEW_DIR, name))
        assert row["bytes"] == len(data) and row["sha256"] == hashlib.sha256(data).hexdigest(), name


# ------------------------------------------------------------------ source identity of the served bytes

def test_source_block_names_a_commit_that_holds_the_served_bytes(bundle):
    src = bundle["source"]
    # generating_commit is read from EXECUTION_RECORD.json when the generator wrote one (from the relabel on), else it is the true value
    # NOT_RECORDED -- never inferred from history
    if src["execution_record"] is None:
        assert src["generating_commit"] == "NOT_RECORDED"
    else:
        assert len(src["generating_commit"]) == 40 and src["execution_record"]["tree_state"] in ("CLEAN", "CLEAN_EXCEPT_OWN_OUTPUTS", "DIRTY")
    assert src["identity"].startswith("content-addressed")
    for name, blob in src["served_blob_git_sha1"].items():
        data = _bytes(os.path.join(REVIEW_DIR, name))
        assert blob == hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest(), name       # the identity: computable from bytes alone
        if src["content_commit"] != "PENDING_COMMIT":                                          # informational; verified when it names a commit
            at = subprocess.run(["git", "rev-parse", f"{src['content_commit']}:docs/reviews/{SLUG}/{name}"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
            assert at == blob, name
    assert "may lag" in src["served_copy_may_lag"]


def test_manifest_carries_the_same_source_block(bundle):
    manifest = _load(os.path.join(REVIEW_DIR, "manifest.json"))
    assert manifest["source"] == bundle["source"]
    assert manifest["build_utc"] and manifest["build_utc"] not in manifest["source"].values()


# ------------------------------------------------------------------ v3: four representations, preservation, coverage

def test_every_document_has_four_representations_and_a_backed_coverage_status(bundle):
    levels = set(bundle["vocabulary"]["representation_levels"])
    for d in bundle["documents"]:
        assert set(d["representations"]) == levels, d["document_id"]
        cov = d["coverage_status"]
        assert cov["value"] in bundle["vocabulary"]["coverage_status"], d["document_id"]
        if cov["value"] in ("COMPLETE_ABSTRACT", "COMPLETE_SOURCE"):
            assert cov["backed_by"] == "preservation_record" and d["preservation_record"]["verdict"] == "PRESERVED", d["document_id"]
        if cov["value"] == "EXCERPT_ONLY":
            assert d["preservation_record"]["verdict"] == "FAILURE", d["document_id"]
        assert set(d["four_questions"]) == set(bundle["vocabulary"]["four_questions"]), d["document_id"]
        for q in d["four_questions"].values():
            assert q["state"] in bundle["vocabulary"]["question_states"], (d["document_id"], q)
        assert set(d["which_representation"]) == {"hashed_by_certificate", "searched_by_page", "displayed_by_page"}


def test_coverage_status_is_never_declared_without_an_acquisition(bundle):
    """A flag is another assertion. COMPLETE_* may only appear where a retained acquisition backs it."""
    for d in bundle["documents"]:
        acq = d["representations"]["ACQUIRED_SOURCE"]
        if d["coverage_status"]["value"].startswith("COMPLETE"):
            assert acq.get("state") == "RETAINED_POST_HOC" and acq.get("sha256_original"), d["document_id"]
            assert os.path.exists(os.path.join(ROOT, *acq["ref"].split("/"))), acq["ref"]


def test_soul_cache_is_recorded_as_a_summarisation_and_its_absence_claims_fail_closed(bundle):
    """The fifth audit's defect, made mechanical: the cached SOUL abstract preserves none of the acquired units and
    omits the safety sentence; its OUTCOME_NOT_IN_SOURCE rows are NOT admissible as negative claims."""
    soul = next(d for d in bundle["documents"] if d["document_id"] == "pubmed:40162642")
    assert soul["coverage_status"]["value"] == "EXCERPT_ONLY"
    assert soul["preservation_record"]["missing"] == len(soul["preservation_record"]["units"]) >= 4
    assert soul["transforms"][0]["operation"] == "summarisation"
    missing_text = " ".join(u["text_if_missing"] or "" for u in soul["preservation_record"]["units"])
    assert "gastrointestinal" in missing_text.lower() and "serious adverse events" in missing_text.lower()
    neg = [c for c in bundle["absence_claims"] if c["trial"]["id"] == "PMID 40162642" and c["claim_kind"] == "NEGATIVE"]
    assert neg and all(c["negative_claim_admissible"] is False for c in neg)
    row = next(r for r in bundle["verification_rows"] if r["trial"]["id"] == "PMID 40162642")
    assert row["admission"]["final"] == "ADMISSIBLE"
    assert row["decision"]["narrowed_states"]["result_concordant_with_located_span"] == "SUPPORTED"
    assert row["decision"]["narrowed_states"]["cached_representation_faithful_and_complete"].startswith("NOT_SUPPORTED")


def test_ten_records_are_complete_abstract_relative_to_a_retained_acquisition(bundle):
    counts = bundle["counts"]["documents_by_coverage_status"]
    assert counts.get("COMPLETE_ABSTRACT") == 10 and counts.get("EXCERPT_ONLY") == 1


def test_deleting_a_unit_from_a_preserved_abstract_fails_preservation():
    """The specialisation of the deletion rule: an unadjudicated deletion must make the evidence LESS complete."""
    units = [{"index": 0, "label": "METHODS", "text": "We randomised 100 patients."},
             {"index": 1, "label": "RESULTS", "text": "HR 0.86 (0.77-0.96)."},
             {"index": 2, "label": "SAFETY", "text": "Serious adverse events 47.9% vs 50.3%."}]
    full = "METHODS: We randomised 100 patients. RESULTS: HR 0.86 (0.77-0.96). SAFETY: Serious adverse events 47.9% vs 50.3%."
    assert build_bundle.preservation_record(full, units)["verdict"] == "PRESERVED"
    cut = full.replace(" SAFETY: Serious adverse events 47.9% vs 50.3%.", "")
    rec = build_bundle.preservation_record(cut, units)
    assert rec["verdict"] == "FAILURE" and rec["units"][2]["state"] == "MISSING"


# ------------------------------------------------------------------ v3: custody, resolvability, package semantics

def test_medr_original_is_declared_producer_held_not_licence(bundle):
    medr = next(d for d in bundle["documents"] if d["document_id"] == "fda:FDA_NDA208471_MedR_2016")
    acq = medr["representations"]["ACQUIRED_SOURCE"]
    assert acq["state"] == "NOT_IN_PACKAGE_PRODUCER_HELD" and acq["sha256_original"] and "accessdata.fda.gov" in acq["reacquire"]
    assert "NOT a complete producer-held binary archive" in acq["statement"]
    assert bundle["package_semantics"]["producer_held_binary_archive"] is False
    stat = next(d for d in bundle["documents"] if d["document_id"] == "fda:FDA_NDA208471_StatR_2016")
    assert stat["representations"]["ACQUIRED_SOURCE"]["state"] == "SERVED", "the statistical review original IS in the package"
    assert "neither_means" in bundle["package_semantics"]


def test_resolvability_walk_ends_in_bytes(bundle):
    walk = bundle["resolvability"]
    assert walk["edge_counts"].get("DIGEST_WITHOUT_BODY", 0) == 0, walk["edges_not_resolved_to_bytes_in_package"]
    assert walk["edge_counts"].get("DANGLING", 0) == 0
    assert walk["edge_counts"]["RESOLVED_BODY_IN_ACQUISITIONS"] >= 15000
    for e in walk["edges_not_resolved_to_bytes_in_package"]:
        assert e["state"] in ("NOT_IN_PACKAGE_LICENCE", "NOT_IN_PACKAGE_PRODUCER_HELD"), e


def test_aact_bodies_rehash_to_the_digests_they_resolve(bundle):
    """A hash without its row body is a promise: every published body re-hashes to the recorded digest."""
    from harness.canonical import canonical_json, sha256_text
    checked = 0
    for f in bundle["supporting_files"]:
        if os.path.basename(f["path"]) in ("rows.json", "review_source_references.json"):
            body = _load(os.path.join(ROOT, *f["path"].split("/")))
            for table, rows in body["tables"].items():
                for r in rows:
                    assert sha256_text(canonical_json(r["row"])) == r["sha256"], (table, r["sha256"])
                    checked += 1
    assert checked >= 15000


# ------------------------------------------------------------------ v3: verification rows

def test_verification_rows_cover_the_pool_and_carry_all_six_objects(bundle):
    review = _load(os.path.join(REVIEW_DIR, "review.json"))
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    assert [r["trial"]["id"] for r in bundle["verification_rows"]] == [t["id"] for t in primary["trials"]]
    for r in bundle["verification_rows"]:
        assert set(r) >= {"source", "span", "endpoint", "effect", "decision", "admission"}
        assert set(r["admission"]["predicates"]) == set(bundle["vocabulary"]["admission_predicates"]) - {"ADMISSIBLE", "MIGRATION_STATE_UNBOUND_LEGACY", "INADMISSIBLE", "P10_estimand_evidence"}   # P10 is verifier-side
        assert r["admission"]["final"] in ("ADMISSIBLE", "MIGRATION_STATE_UNBOUND_LEGACY", "INADMISSIBLE")


def test_harmony_is_inadmissible_because_its_family_eligibility_is_unknown(bundle):
    """A finding, not a bug: the page pools NCT02465515 while its family eligibility object says UNKNOWN
    (ENTRY_POPULATION_NOT_ESTABLISHED). Under the declared invariant the row is inadmissible. Recorded so that the
    eligibility lane sees it; if the family object is repaired, update this deliberately."""
    row = next(r for r in bundle["verification_rows"] if r["trial"]["id"] == "PMID 30291013")
    assert row["admission"]["final"] == "INADMISSIBLE"
    assert row["admission"]["predicates"]["P5_family_eligible"]["eligibility_state"] == "UNKNOWN"
    assert bundle["counts"]["admissible_rows"] == 7


def test_lancet_rows_are_normalised_not_verbatim_and_offsets_reproduce(bundle):
    rows = {r["trial"]["id"]: r for r in bundle["verification_rows"]}
    assert rows["PMID 31189511"]["span"]["match"] == "NORMALISED" and rows["PMID 30291013"]["span"]["match"] == "NORMALISED"
    assert rows["PMID 40162642"]["span"]["match"] == "VERBATIM"
    records = _load(os.path.join(ROOT, "cache", SLUG, "records.json"))
    by = {str(x["id"]): x["abstract"] for x in records["records"]}
    for pid, r in rows.items():
        s = r["span"]
        parsed = by[pid.replace("PMID ", "")]
        rep = parsed if s["parent_representation"] == "PARSED_SOURCE" else build_bundle.normalize(parsed)
        want = s["text"] if s["parent_representation"] == "PARSED_SOURCE" else build_bundle.normalize(s["text"])
        assert rep[s["start"]:s["end"]] == want, pid


def test_pooled_reference_matches_the_settled_value(bundle):
    e = bundle["pooled_reference"]["expected"]
    assert abs(e["estimate"] - 0.8559934175938467) < 1e-9
    assert abs(e["ci_low"] - 0.8086248326601262) < 1e-9 and abs(e["ci_high"] - 0.9061368157017332) < 1e-9
    assert abs(e["tau2"] - 0.00004447972517261924) < 1e-9


# ------------------------------------------------------------------ 3.1: canonicalisation, selector, coordinates, variation, inputs

def test_canonicalisation_is_published_and_all_three_records_scopes_reproduce(bundle):
    """Two valid scopes over one file are not a defect; an auditor who assumes the wrong scheme reports one that isn't there."""
    from harness.canonical import canonical_json, sha256_text
    assert "RFC 8785" in bundle["canonicalisation"]["not"] and "sort_keys=True" in bundle["canonicalisation"]["scheme"]
    raw = _bytes(os.path.join(ROOT, "cache", SLUG, "records.json"))
    scopes = {s["subject"]: s["value"] for s in bundle["digest_scopes"][0]["scopes"]}
    assert scopes["raw served bytes"] == hashlib.sha256(raw).hexdigest()
    assert scopes["whole file as JSON object"] == sha256_text(canonical_json(json.loads(raw))) == _load(CERT)["records_file_sha256"]
    assert scopes["obj['records'] only"] == sha256_text(canonical_json(json.loads(raw)["records"])) == _load(CERT)["retrieved_corpus_sha256"]
    # rows drawn from the one container legitimately share its raw digest -- and say so
    shared = {r["source"]["source_sha256"] for r in bundle["verification_rows"]}
    assert shared == {scopes["raw served bytes"]}
    assert all("container digest + deterministic selector" in r["source"]["identity"] for r in bundle["verification_rows"])


def test_selector_rule_is_stated_enforced_and_refuses_ambiguity(bundle):
    assert bundle["selector_rule"]["two_or_more_matches"].startswith("REFUSE")
    for r in bundle["verification_rows"]:
        assert r["source"]["selector"]["matches"] == 1
        assert r["source"]["selector"]["selected_identifier"]["id"] == r["trial"]["id"].replace("PMID ", "")
    good = {"records": [{"id": "1", "id_type": "pmid"}, {"id": "2", "id_type": "pmid"}]}
    assert build_bundle.resolve_selector(good, "1")["id"] == "1"
    with pytest.raises(ValueError):
        build_bundle.resolve_selector({"records": [{"id": "1", "id_type": "pmid"}, {"id": "1", "id_type": "pmid"}]}, "1")
    with pytest.raises(ValueError):
        build_bundle.resolve_selector(good, "3")


def test_every_location_states_its_coordinate_convention(bundle):
    for r in bundle["verification_rows"]:
        c = r["span"]["coordinates"]
        assert "code points" in c["unit"] and "half-open" in c["range"]
        digests = {d["subject"]: d["value"] for d in r["source"]["digests"]}
        assert r["span"]["representation_sha256"] in digests.values()


def test_declared_variation_is_recorded_per_trial_not_collapsed(bundle):
    c = bundle["endpoint_compatibility"]
    assert c["state"] == "COMPATIBLE_WITH_DECLARED_VARIATION" and c["trials_stay_pooled"] is True
    assert "undetermined death as cardiovascular death" in c["protocol_permission"]
    pt = {k: v["value"] for k, v in c["per_trial"].items()}
    assert pt["PMID 34215025"] == "yes" and pt["PMID 31189511"] == "yes"          # AMPLITUDE-O, REWIND -- from their own spans
    assert pt["PMID 30291013"] == "unstated"                                       # HARMONY: the 'unknown causes' phrase is not its
    assert "no" not in pt.values(), "an abstract that is silent never yields 'no'"
    assert c["page_label"] == "HOMOGENEOUS" and c["page_direction_audit"] == "ASSERTED_HOMOGENEOUS_UNDERLYING_HETEROGENEOUS"
    assert build_bundle.undetermined_death_field("death from cardiovascular or undetermined causes")["value"] == "yes"
    assert build_bundle.undetermined_death_field("cardiovascular death, nonfatal MI or nonfatal stroke")["value"] == "unstated"


def test_statistical_input_records_construction_and_does_not_replace_the_se(bundle):
    review = _load(os.path.join(REVIEW_DIR, "review.json"))
    se_page = {t["id"]: t["study_effect"]["standard_error"] for t in next(o for o in review["outcomes"] if o["primary"])["trials"]}
    for r in bundle["verification_rows"]:
        si = r["statistical_input"]
        assert si["se_source"] == "DERIVED_FROM_CI" and si["se_log_used"] == se_page[r["trial"]["id"]]
        assert si["interval_construction"] in bundle["vocabulary"]["statistical_input"]["interval_construction"]
        assert si["approximation_appropriate"].startswith("NOT_ESTABLISHED")
    soul = next(r for r in bundle["verification_rows"] if r["trial"]["id"] == "PMID 40162642")["statistical_input"]
    assert soul["interval_construction"] == "GROUP_SEQUENTIAL_ADJUSTED" and "NOT verified by this bundle" in soul["construction_basis"]


def test_heterogeneity_statement_carries_input_precision_not_a_categorical_claim(bundle):
    h = bundle["pooled_reference"]["heterogeneity"]
    assert abs(h["Q"] - 7.06072) < 1e-4 and h["df"] == 7 and 0 < h["Q_minus_df"] < 0.1
    rs = h["rounding_sensitivity"]
    assert 0.2 < rs["fraction_tau2_zero"] < 0.8 and rs["finding_untouched"] is True and rs["max_ci_upper"] < 1.0
    assert "effectively zero and rounding-sensitive" in h["honest_statement"]


def test_verifier_is_served_byte_identical_at_the_path_the_bundle_names(bundle):
    v = bundle["verifier"]
    served = os.path.join(ROOT, "docs", *v["served_path"].split("/"))
    src = os.path.join(ROOT, "scripts", "verify_bundle.py")
    assert _bytes(served) == _bytes(src) and hashlib.sha256(_bytes(served)).hexdigest() == v["sha256"]
    assert any(f["path"] == "docs/scripts/verify_bundle.py" and f["sha256"] == v["sha256"] for f in bundle["supporting_files"])
    assert "PRODUCTION admission path" in v["does_not_check"] and "HbA1c" in v["does_not_check"]
    assert "digest_mismatch_policy" in bundle["package_semantics"]


# ------------------------------------------------------------------ 3.2: extraction coverage, anchors, limits

def test_extraction_object_coverage_is_stated_not_discovered(bundle):
    x = bundle["extraction_objects_coverage"]
    primary = next(o for o in x["per_outcome"] if o["primary"])
    assert primary["pooled_rows"] == 8 and primary["pooled_rows_with_an_extraction_object"] == ["40162642"]
    assert "1 of 8" in x["plain_statement"]
    for r in bundle["verification_rows"]:
        ch = r["certified_evidence_chain"]
        if r["trial"]["id"] == "PMID 40162642":
            assert ch["extraction_object_for_this_outcome"] != "ABSENT" and "verified_effects.json" in ch["chain"][0]
        else:
            assert ch["extraction_object_for_this_outcome"] == "ABSENT" and "records.json" in ch["chain"][0]


def test_every_anchored_document_says_how_to_compare(bundle):
    anchored = [d for d in bundle["documents"] if d.get("anchor", {}).get("anchors")]
    assert len(anchored) == 11
    for d in anchored:
        an = d["anchor"]
        assert os.path.exists(os.path.join(ROOT, *an["acquired_ref"].split("/")))
        assert "AbstractText" in an["how_to_compare"] and an["external"]["uri"].startswith("https://eutils")
        assert "recomputed" in an["what_it_catches"]


def test_limits_section_prints_the_closed_vocabulary_and_self_consistency_limits(bundle):
    ids = {l["id"] for l in bundle["limits"]}
    assert {"L1_self_consistency", "L2_closed_vocabulary", "L5_extraction_object_coverage", "L9_production_path"} <= ids
    assert any("closed list" in l["limit"] for l in bundle["limits"])


# ------------------------------------------------------------------ 3.3: the admit_rows fail-open as a visible migration state

def test_unbound_legacy_rows_are_a_migration_state_outside_the_admissible_count(bundle):
    bs = bundle["binding_states"]
    assert bs["counts"]["migration_state_unbound_legacy"] == 2 and bs["counts"]["rows"] == 10
    unbound = [r for r in bs["rows"] if r["binding_class"] == "MIGRATION_STATE_UNBOUND_LEGACY"]
    assert {(r["outcome"], r["trial"]["id"]) for r in unbound} == {("Gastrointestinal adverse events", "PMID 31189511"), ("Adverse events leading to discontinuation", "PMID 27295427")}
    assert all(r["counted_in_admissible_rows"] is False and r["producer_labels"]["verified"] == "verified" for r in unbound)
    rewind = next(r for r in unbound if r["trial"]["id"] == "PMID 31189511")
    assert rewind["observations"]["definition_names_another_outcome"] is True          # the CV primary definition on a GI row
    leader = next(r for r in unbound if r["trial"]["id"] == "PMID 27295427")
    assert leader["observations"]["table_sourced"] is True                              # the multi-span case
    assert bundle["counts"]["unbound_legacy_rows_inside_admissible_rows"] == 0
    assert bundle["counts"]["admissible_rows"] + bundle["counts"]["migration_state_rows_in_primary_pool"] + bundle["counts"]["inadmissible_rows_in_primary_pool"] == 8
    assert all(r["admission"]["predicates"]["P8_endpoint_bound"]["state"] == "PASS" for r in bundle["verification_rows"])
    assert any(l["id"] == "L10_admit_rows_fail_open" for l in bundle["limits"])
    assert "not refused" in bs["statement"]
    # B2 (panel): a row that reached the gate unclassified is a different state from one that never reached it; both named, pins checked
    assert bs["gate"]["pin_matches_this_tree"] == {"harness/pipeline.py": True, "harness/target_endpoint.py": True}
    assert bs["gate"]["admit_rows_applies_to_every_route"] is True and bs["gate"]["appends_to_trials_after_gate_in_same_function"] == 0
    assert all(r["route"] == "OVERRIDE_BEFORE_CLASSIFICATION" and r["gate_state"] == "REACHED_GATE_UNCLASSIFIED"
               and r["route_evidence"] == "cache/glp1-ra-mace-t2d/verified_arms.json" for r in unbound)
    assert bs["counts"]["gate_states"] == {"REACHED_GATE_CLASSIFIED": 8, "REACHED_GATE_UNCLASSIFIED": 2, "NEVER_REACHED_GATE": 0}
    assert "UNVERIFIABLE" not in bs["statement"] and "pinned" in bs["statement"]


# ------------------------------------------------------------------ 3.4: P9 positive binding, certified eligibility, L11

def test_p9_is_read_from_the_span_and_passes_every_genuine_row(bundle):
    for r in bundle["verification_rows"]:
        p9 = r["admission"]["predicates"]["P9_span_target_mention"]
        assert p9["state"] == "PASS", (r["trial"]["id"], p9)
        assert p9["clause"] and (p9["clause"] in r["span"]["text"])
    cc = ["CARDIOVASCULAR_DEATH", "MYOCARDIAL_INFARCTION", "STROKE"]
    assert build_bundle.span_target_mention("Fewer patients died from cardiovascular causes (hazard ratio, 0.78; 95% CI, 0.66 to 0.93).", [0.78, 0.66, 0.93], "The primary composite outcome was cardiovascular death, MI or stroke", cc)["state"] == "ENDPOINT_INCOMPATIBLE"
    assert build_bundle.span_target_mention("Cataract surgery occurred more often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).", [0.87, 0.78, 0.97], "The primary composite outcome was cardiovascular death, MI or stroke", cc)["state"] == "AMBIGUOUS_ENDPOINT_BINDING"
    assert build_bundle.span_target_mention("Retinopathy occurred more often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).", [0.87, 0.78, 0.97], "x", cc)["state"] == "ENDPOINT_INCOMPATIBLE"
    assert build_bundle.span_target_mention("The primary outcome occurred in fewer patients (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).", [0.87, 0.78, 0.97], "The primary composite outcome was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke.", cc)["state"] == "PASS"
    # a primary-outcome name whose definition span does NOT bind to the target is not admitted by the name alone
    assert build_bundle.span_target_mention("The primary outcome occurred in fewer patients (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).", [0.87, 0.78, 0.97], "The primary outcome was hospitalization for heart failure.", cc)["state"] != "PASS"


def test_eligibility_is_read_from_the_certified_copy_and_named(bundle):
    assert "families.json" in bundle["eligibility_source"]["authoritative"]
    for r in bundle["verification_rows"]:
        p5 = r["admission"]["predicates"]["P5_family_eligible"]
        assert "families.json" in p5["authoritative_copy"] and p5["copies_agree"] is True


def test_l11_coacquisition_rewrite_limit_is_printed(bundle):
    assert any(l["id"] == "L11_coacquisition_rewrite" and "signed release" in l["limit"] for l in bundle["limits"])


# ------------------------------------------------------------------ 3.6: analysis identity, multi-span, producer label scope

def test_every_row_carries_analysis_identity_not_only_endpoint_identity(bundle):
    for r in bundle["verification_rows"]:
        ai = r["analysis_identity"]
        assert set(ai) >= {"analysis_set", "treatment_strategy", "follow_up_window", "comparator_direction", "estimator", "analysis_identity_key"}
        for f in ("analysis_set", "treatment_strategy", "follow_up_window", "comparator_direction", "estimator"):
            assert ai[f]["basis"] in bundle["vocabulary"]["estimand_basis"], (r["trial"]["id"], f)
            if ai[f]["basis"] == "REGISTERED_DEFAULT":
                assert "span" not in ai[f], (r["trial"]["id"], f, "a default rendered as a statement")
            if ai[f]["basis"] == "STATED_IN_OWNING_EVIDENCE":
                assert ai[f].get("span") and ai[f].get("start") is not None, (r["trial"]["id"], f)
        assert "placebo" in ai["comparator_direction"]["value"] and ai["estimator"]["value"] == "hazard ratio"
        assert ai["analysis_identity_key"].count("|") == 3 and "[REG]" in ai["analysis_identity_key"] or "[STA]" in ai["analysis_identity_key"]


def test_rows_carry_spans_with_roles_and_the_vocabulary_admits_table_roles(bundle):
    roles = set(bundle["vocabulary"]["span_roles"])
    assert {"result", "definition", "column_header", "section_heading", "analysis_method", "footnote"} <= roles
    for r in bundle["verification_rows"]:
        got = [s["role"] for s in r["spans"]]
        assert got[:2] == ["result", "definition"], r["trial"]["id"]
        assert all(s["match"] in ("VERBATIM", "NORMALISED") for s in r["spans"]), r["trial"]["id"]
    unbound = [b for b in bundle["binding_states"]["rows"] if b["binding_class"] != "BOUND"]
    assert all("column_header" in b["observations"]["what_would_bind_it"] and b["observations"]["spans_present"] == [] for b in unbound)


def test_producer_verified_label_is_scoped_to_what_it_checked(bundle):
    assert "point estimate" in bundle["vocabulary"]["producer_label_scope"]["verified"].lower()
    assert all("point estimate" in r["producer_label_scope"] for r in bundle["verification_rows"])


# ------------------------------------------------------------------ 3.7: two authentic analyses of one endpoint, distinguishable from the bundle alone

def test_elixa_on_study_and_on_treatment_are_distinct_analyses_in_the_bundle(bundle):
    elixa = next(r for r in bundle["regulatory_facts"] if r["trial"] == "ELIXA")
    by_kind = {a["kind"]: a for a in elixa["candidate_analyses"]}
    on_study, on_treat = by_kind["table8_onstudy_3p"], by_kind["table8_ontreatment_3p"]
    assert on_study["tuple"] == {"estimate": 1.02, "ci_low": 0.89, "ci_high": 1.18} and on_study["counts"] == {"placebo_events": 392, "treatment_events": 400}
    assert on_treat["tuple"] == {"estimate": 1.01, "ci_low": 0.87, "ci_high": 1.17} and on_treat["counts"] == {"placebo_events": 342, "treatment_events": 334}
    assert on_study["analysis_identity"]["endpoint"] == on_treat["analysis_identity"]["endpoint"] == "3-point MACE"     # same endpoint...
    assert on_study["analysis_identity"]["analysis_identity_key"] != on_treat["analysis_identity"]["analysis_identity_key"]  # ...different analysis
    assert on_study["analysis_identity"]["treatment_strategy"].startswith("on-study") and on_treat["analysis_identity"]["treatment_strategy"] == "on-treatment"
    assert all(a["span_binding"] == "VERBATIM_SPAN" for a in elixa["candidate_analyses"])
    assert len(elixa["distinct_analysis_identity_keys"]) >= 4
    # the 4-point rows are a different ENDPOINT, separated on that axis
    assert by_kind["primary_4p_table6"]["analysis_identity"]["endpoint"] == "4-point MACE+"
    # the decision's tuple is bound to the analysis whose identity it claims
    assert elixa["tuple_to_identity_binding"] == "BOUND" and elixa["selected_analysis_kinds"] == ["text_unrounded_3p"]
    assert elixa["decision"]["claimed_treatment_strategy"].startswith("on-study") and elixa["decision"]["claimed_endpoint"] == "3-point MACE"


def test_elixa_source_internal_discrepancy_is_recorded_not_resolved(bundle):
    elixa = next(r for r in bundle["regulatory_facts"] if r["trial"] == "ELIXA")
    disc = [d for d in elixa["source_internal_discrepancies"] if d["treatment_strategy"].startswith("3-point MACE / on-study")]
    assert disc, elixa["source_internal_discrepancies"]
    tuples = {json.dumps(r["tuple"], sort_keys=True) for r in disc[0]["representations"]}
    assert len(tuples) >= 2      # 1.02 (0.89, 1.18) table vs 1.02 (0.89, 1.17) executive summary vs 0.887-1.172 unrounded


def test_freedom_row_is_a_partial_table_binding_of_the_three_point_row(bundle):
    fr = next(r for r in bundle["regulatory_facts"] if r["trial"] == "FREEDOM-CVO")
    a = fr["candidate_analyses"][0]
    assert a["span_binding"] == "PARTIAL_TABLE_BINDING" and a["table_pieces"]["pieces_located"] >= a["table_pieces"]["pieces"] - 1
    located = {d["piece"][:20] for d in a["table_pieces"]["detail"] if d["match"] != "NOT_LOCATED"}
    assert any(p.startswith("3-Point MACE*") for p in located) and any(p.startswith("1.24 (0.90, 1.70)") for p in located)   # row label + tuple cell
    assert all(d["piece"].startswith("Source:") for d in a["table_pieces"]["detail"] if d["match"] == "NOT_LOCATED")          # only the footnote fails
    assert a["tuple"] == {"estimate": 1.24, "ci_low": 0.9, "ci_high": 1.7} and a["analysis_identity"]["endpoint"] == "3-point MACE"
    assert fr["tuple_to_identity_binding"] == "BOUND"      # the FREEDOM-only 3-point row, not the pooled 1.13 nor the 4-point 1.21


def test_flow_label_row_resolves_endpoint_from_components(bundle):
    fl = next(r for r in bundle["regulatory_facts"] if r["trial"] == "FLOW")
    assert fl["candidate_analyses"][0]["analysis_identity"]["endpoint"] == "3-point MACE" and fl["tuple_to_identity_binding"] == "BOUND"


# ------------------------------------------------------------------ 3.8: P9 per the panel's rule, numeric P3, estimand evidence, content-addressed stamp

CC = ["CARDIOVASCULAR_DEATH", "MYOCARDIAL_INFARCTION", "STROKE"]
DEFN = "The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke."


def test_p9_panel_shapes_all_refuse_and_the_regression_pair_agrees():
    m8 = ("The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke and "
          "hospitalization for heart failure occurred in fewer patients (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).")
    a1 = ("The primary composite outcome was cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke; cardiovascular death alone had a "
          "hazard ratio, 0.88 (95% CI, 0.79 to 0.99).")
    a2_semi = ("The primary outcome was cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke; the secondary outcome was hospitalization "
               "for heart failure, which occurred less often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).")
    a2_stop = a2_semi.replace("; the secondary", ". The secondary")
    sus6 = ("Rates of new or worsening nephropathy were lower in the semaglutide group, but rates of retinopathy complications (vitreous hemorrhage, "
            "blindness, or conditions requiring treatment with an intravitreal agent or photocoagulation) were significantly higher (hazard ratio, 1.76; "
            "95% CI, 1.11 to 2.78; P=0.02).")
    S = lambda span, vals: build_bundle.span_target_mention(span, vals, DEFN, CC)["state"]
    assert S(m8, [0.87, 0.78, 0.97]) == "AMBIGUOUS_ENDPOINT_BINDING"          # both a target and a non-target mention: never a pass
    assert S(a1, [0.88, 0.79, 0.99]) == "ENDPOINT_INCOMPATIBLE"               # semicolon ends the clause; a lone component is not the composite
    assert S(a2_semi, [0.87, 0.78, 0.97]) == S(a2_stop, [0.87, 0.78, 0.97]) == "ENDPOINT_INCOMPATIBLE"   # the regression pair agrees
    assert S(sus6, [1.76, 1.11, 2.78]) == "ENDPOINT_INCOMPATIBLE"             # the live SUSTAIN-6 miss
    assert S("The primary cardiovascular end-point event occurred in 189 of 2717 patients (hazard ratio, 0.73; 95% CI, 0.58 to 0.92).", [0.73, 0.58, 0.92]) == "PASS"
    # co-occurrence without a definitional cue is not ownership
    assert S("Cardiovascular death and stroke were adjudicated centrally, and cataract surgery occurred more often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).", [0.87, 0.78, 0.97]) != "PASS"


def test_clause_boundaries_include_semicolons_outside_brackets():
    c = build_bundle.clauses("A occurred (hazard ratio, 0.87; 95% CI, 0.78 to 0.97); B did not. C was measured.")
    assert c == ["A occurred (hazard ratio, 0.87; 95% CI, 0.78 to 0.97);", "B did not.", "C was measured."]
    # a semicolon that continues a statistical tuple does not end the clause (the panel's own example is unbracketed)
    assert len(build_bundle.clauses("hazard ratio, 0.8; 95% confidence interval, 0.7 to 1.0; P=0.04.")) == 1


def test_p3_is_numeric_equality_not_substring():
    assert build_bundle.clause_with_effect("hazard ratio, 0.8; 95% confidence interval, 0.7 to 1.0.", [0.80, 0.70, 1.00]) is not None   # lossless
    assert build_bundle.clause_with_effect("hazard ratio, 0.8; 95% confidence interval, 0.7 to 1.0.", [0.8, 0.7, 0.96]) is None         # 0.96 vs 1.0
    assert build_bundle.clause_with_effect("hazard ratio, 0.84; 95% CI, 0.7 to 1.0.", [0.8, 0.7, 1.0]) is None                          # 0.8 vs 0.84
    assert build_bundle.clause_with_effect("hazard ratio, 0.87; 95% CI, 0.78 to 0.97.", [0.87, 0.7, 0.97]) is None                       # 0.7 vs 0.78
    assert build_bundle.clause_with_effect("HR 0\u00b790, 95% CI 0\u00b780-1\u00b701", [0.9, 0.8, 1.01]) is not None                     # declared normalisation
    for r in bundle_rows():
        assert r["admission"]["predicates"]["P3_effect_tokens_in_span"]["state"] == "PASS" and "NUMERIC" in r["admission"]["predicates"]["P3_effect_tokens_in_span"]["rule"]


def bundle_rows():
    return _load(BUNDLE)["verification_rows"]


def test_estimand_fields_carry_a_span_or_an_explicit_default_never_a_bare_assertion(bundle):
    records = _load(os.path.join(ROOT, "cache", SLUG, "records.json"))
    by = {str(x["id"]): x["abstract"] for x in records["records"]}
    stated_set = stated_window = 0
    for r in bundle["verification_rows"]:
        ee = r["estimand_evidence"]
        assert set(ee) == {"analysis_set", "analysis_window", "estimator", "contrast"}
        parsed = by[r["trial"]["id"].replace("PMID ", "")]
        for field, v in ee.items():
            assert v["state"] in ("STATED_IN_OWNING_EVIDENCE", "REGISTERED_DEFAULT", "UNRESOLVED"), (r["trial"]["id"], field)
            if v["state"] == "STATED_IN_OWNING_EVIDENCE":
                rep_text = build_bundle.normalize(parsed) if v.get("parent_representation") == "NORMALIZED_SOURCE" else parsed
                assert v.get("start") is not None and rep_text[v["start"]:v["end"]].strip() == v["span"].strip(), (r["trial"]["id"], field)   # offsets reproduce the span
        assert ee["estimator"]["state"] == "STATED_IN_OWNING_EVIDENCE" and ee["estimator"]["value"] == "hazard ratio"
        assert ee["analysis_window"]["state"] != "UNRESOLVED" and ee["analysis_set"]["state"] != "UNRESOLVED"   # no pooled abstract states two
        stated_set += ee["analysis_set"]["state"] == "STATED_IN_OWNING_EVIDENCE"; stated_window += ee["analysis_window"]["state"] == "STATED_IN_OWNING_EVIDENCE"
    assert stated_set == 3        # measured: analysis set stated in 3 of 8 abstracts (REWIND, Harmony, EXSCEL); the rest default to the registered value
    assert stated_window >= 2


def test_elixa_strategy_evidence_separates_the_pair_through_structured_fields(bundle):
    el = next(r for r in bundle["regulatory_facts"] if r["trial"] == "ELIXA")
    ev = {a["kind"]: (a["analysis_identity"]["treatment_strategy"], a["strategy_evidence"]["state"]) for a in el["candidate_analyses"]}
    assert ev["table8_onstudy_3p"] == ("on-study (ITT)", "STATED_IN_OWNING_EVIDENCE") and ev["table8_ontreatment_3p"] == ("on-treatment", "STATED_IN_OWNING_EVIDENCE")
    assert ev["text_unrounded_3p"] == ("on-study (ITT)", "BOUND_VIA_COUNTS")     # the prose binds through its 392/400 counts, not by assertion
    assert el["tuple_to_identity_binding"] == "BOUND"
    fr = next(r for r in bundle["regulatory_facts"] if r["trial"] == "FREEDOM-CVO")
    assert fr["candidate_analyses"][0]["strategy_evidence"]["state"] == "STATED_IN_OWNING_EVIDENCE"   # 'ITT Population End of Study' in its own span


def test_source_stamp_is_content_addressed_and_needs_no_commit_of_its_own(bundle):
    src = bundle["source"]
    assert src["identity"].startswith("content-addressed") and "INFORMATIONAL" in src["content_commit_meaning"]
    assert src["content_commit"] == "PENDING_COMMIT" or len(src["content_commit"]) == 40
    assert any(l["id"] == "L13_location_by_full_text_and_offsets" for l in bundle["limits"]) and any(l["id"] == "L14_verification_rows_source_pubmed_only" for l in bundle["limits"])


# ------------------------------------------------------------------ 3.9: a default never renders as a statement; registered estimand

def test_registered_estimand_is_read_from_the_served_protocol_and_every_row_agrees(bundle):
    reg = bundle["registered_estimand"]
    proto = open(os.path.join(ROOT, "protocols", SLUG + ".md"), encoding="utf-8").read()
    assert proto[reg["start"]:reg["end"]].strip() == reg["protocol_span"] and "Intention-to-treat" in reg["protocol_span"]
    assert reg["analysis_set"] == "intention-to-treat" and reg["treatment_strategy"].startswith("on-study")
    for r in bundle["verification_rows"]:
        assert r["admission"]["predicates"]["P11_registered_estimand"]["state"] == "PASS"
    for rf in bundle["regulatory_facts"]:
        assert rf["tuple_to_identity_binding"] == "BOUND" and rf["registered_estimand"]["claimed_matches_registered"] is True


def test_elixa_row_labels_are_column_header_spans_with_offsets(bundle):
    el = next(r for r in bundle["regulatory_facts"] if r["trial"] == "ELIXA")
    text = open(os.path.join(ROOT, "outputs", "handover", "glp1_regulatory", "208471Orig1s000StatR.pdf.txt"), encoding="utf-8", errors="replace").read()
    for kind, label in (("table8_onstudy_3p", "(on-study)"), ("table8_ontreatment_3p", "(on-treatment)")):
        a = next(x for x in el["candidate_analyses"] if x["kind"] == kind)
        hdr = next(s for s in a["spans"] if s["role"] == "column_header")
        assert hdr["text"].strip("()") == label.strip("()") and text[hdr["start"]:hdr["end"]] == hdr["text"]
        assert a["strategy_evidence"]["state"] == "STATED_IN_OWNING_EVIDENCE"
    prose = next(x for x in el["candidate_analyses"] if x["kind"] == "text_unrounded_3p")
    assert prose["strategy_evidence"]["state"] == "BOUND_VIA_COUNTS" and prose["strategy_evidence"]["labelled_span"].strip("()") == "on-study"


def test_default_and_stated_bases_are_both_present_and_visibly_distinct(bundle):
    bases = [r["analysis_identity"]["analysis_set"]["basis"] for r in bundle["verification_rows"]]
    assert bases.count("STATED_IN_OWNING_EVIDENCE") == 3 and bases.count("REGISTERED_DEFAULT") == 5   # measured: 3 of 8 abstracts state the analysis set
    assert "UNRESOLVED" not in bases


# ------------------------------------------------------------------ 3.10: the CI level the source states vs the level assumed

def test_every_row_states_its_ci_level_or_records_the_assumption(bundle):
    for r in bundle["verification_rows"]:
        cil = r["statistical_input"]["ci_level"]
        assert cil["assumed_ci_pct"] == 95.0 and abs(cil["z_assumed_by_derivation"] - 1.959963984540054) < 1e-15
        assert cil["level_agreement"] in ("MATCH", "UNSTATED")
        if cil["level_agreement"] == "MATCH":
            assert cil["source_ci_pct"] == 95.0 and cil["basis"] == "STATED_IN_OWNING_EVIDENCE"
            assert abs(cil["se_log_at_stated_level"] - cil["se_log_used"]) < 1e-9
        assert r["admission"]["predicates"]["P12_ci_level"]["state"] == "PASS"
    assert sum(1 for r in bundle["verification_rows"] if r["statistical_input"]["ci_level"]["level_agreement"] == "MATCH") == 8   # all eight clauses state '95%'


def test_ci_level_mismatch_is_detected_and_z_recomputed_by_stdlib():
    rec = build_bundle.ci_level_record("hazard ratio, 0.79; 95.03% CI, 0.69 to 0.90", 0.0678, 0.69, 0.90)
    assert rec["source_ci_pct"] == 95.03 and rec["level_agreement"] == "MISMATCH"
    assert abs(rec["z_for_stated_level"] - 1.9631) < 1e-3 and rec["z_for_stated_level"] > build_bundle.Z_ASSUMED_BY_DERIVATION
    assert abs(build_bundle.inverse_normal(0.975) - 1.959963984540054) < 1e-9
    assert build_bundle.ci_level_record("hazard ratio, 0.79 (0.69 to 0.90)", 0.0678, 0.69, 0.90)["level_agreement"] == "UNSTATED"
    assert "ABSTAIN" in bundle_vocab()["selection_rule_for_multiple_candidates"]


def bundle_vocab():
    return _load(BUNDLE)["vocabulary"]


# ------------------------------------------------------------------ 3.11: observed vs registered, typed states, admission meaning

def test_observed_is_never_filled_from_registered(bundle):
    for r in bundle["verification_rows"]:
        for f in ("analysis_set", "treatment_strategy", "follow_up_window", "comparator_direction", "estimator"):
            fv = r["analysis_identity"][f]
            assert "observed" in fv and "registered" in fv, (r["trial"]["id"], f)
            if fv["basis"] == "REGISTERED_DEFAULT":
                assert fv["observed"] is None and fv["registered"], (r["trial"]["id"], f)     # the requirement stands in, visibly, and observed stays unknown
            if fv["basis"] == "STATED_IN_OWNING_EVIDENCE":
                assert fv["observed"]["span"] and fv["observed"]["start"] is not None, (r["trial"]["id"], f)
    assert "never filled" in bundle["vocabulary"]["observed_vs_registered"].lower() or "NEVER filled" in bundle["vocabulary"]["observed_vs_registered"]


def test_admission_carries_its_meaning_policy_and_evidence_versions(bundle):
    for r in bundle["verification_rows"]:
        adm = r["admission"]
        assert "NOT 'verified'" in adm["meaning"] and adm["analysis_identity_key"] == r["analysis_identity"]["analysis_identity_key"]
        assert adm["policy_version"]["format_revision"] == bundle["format_revision"] and set(adm["policy_version"]["predicates"]) == set(adm["predicates"])
        assert adm["evidence_version"]["certificate_release_sha256"] == bundle["certificate"]["release_sha256"]
        assert adm["evidence_version"]["review_blob"] == bundle["source"]["served_blob_git_sha1"]["review.json"]
        assert adm["evidence_version"]["records_json_sha256"] == next(a["sha256"] for a in bundle["artefacts"] if a["ref"].endswith("records.json"))
    assert set(bundle["vocabulary"]["typed_states"]) == {"LOCATED", "NOT_FOUND", "AMBIGUOUS", "UNSUPPORTED_REPRESENTATION", "NOT_ATTEMPTED"}
    assert all(r["admission"]["predicates"]["P2_span_located"]["typed_state"] == "LOCATED" for r in bundle["verification_rows"])
    for rf in bundle["regulatory_facts"]:
        assert "competing_candidates" in rf and rf["competing_candidates"] == []


# ------------------------------------------------------------------ 3.12: five assessment states; withdrawn needs its record; clean negatives

def test_assessment_states_cover_every_row_and_never_render_alike(bundle):
    a = bundle["assessment_states"]
    review = _load(os.path.join(REVIEW_DIR, "review.json"))
    n_rows = sum(len(o["trials"]) + len(o.get("declared_absent_trials") or []) for o in review["outcomes"])
    assert len(a["rows"]) == n_rows
    assert set(a["counts"]) <= set(bundle["vocabulary"]["assessment_states"]) - {"rule"}
    assert a["counts"]["ASSESSED"] >= 8 + 4 and a["counts"]["MIGRATION_STATE"] == 2 and a["counts"]["NOT_ASSESSED_BY_BUNDLE"] == 13
    assert "WITHDRAWN" not in a["counts"]


NOTICE = {   # the served notice shape from bd9a0751 (dapagliflozin-hfpef-hosp), abbreviated statements
    "date": "2026-09-19",
    "summary": "The result previously published on this page for its primary outcome was a cardiovascular-death-only registry measure served as the composite outcome. It is withdrawn.",
    "statements": ["What was published: DELIVER HR 0.88 (95% CI 0.74 to 1.05), a component of the composite served as the k=1 primary result.",
                   "What the held evidence holds: the registered PRIMARY composite reports HR 0.82 (95% CI 0.73 to 0.92), p=0.0008.",
                   "Why: the topic declared the composite's components as ['cardiovascular death'] and the binder matched the wrong target faithfully.",
                   "The corrected estimate is not yet published; it lands with its own correction record."],
    "status": "Pooled estimate withheld until the corrected selection is served with its own correction record.",
}
WITHDRAWN_ROW = {"id": "PMID 36027570", "absent_kind": "result_withdrawn", "state": "EXTRACTION_NOT_PERFORMED",
                 "withdrawn_effect": {"effect": 0.88, "ci_low": 0.74, "ci_high": 1.05, "scale": "HR"}}


def _review_with(withdrawn=NOTICE, k=None, trials=()):
    return {"withdrawn": withdrawn, "outcomes": [{"primary": True, "result": {"k": k}, "trials": list(trials)}]}


def test_withdrawn_binds_to_the_served_notice_schema_and_refuses_the_three_bad_shapes():
    S = lambda row, review: build_bundle.assessment_state(row, "x", False, False, False, review=review, review_ref="reviews/x/review.json", review_sha256="a" * 64)
    ok = S(WITHDRAWN_ROW, _review_with())
    assert ok["state"] == "WITHDRAWN"
    rec = ok["basis"]["withdrawal_record"]
    assert rec["ref"] == "reviews/x/review.json#withdrawn" and rec["sha256"] == "a" * 64 and rec["date"] == "2026-09-19"
    assert rec["what_was_published"] == WITHDRAWN_ROW["withdrawn_effect"] and all(rec["contract"]["required_phrases_present"].values())
    with pytest.raises(ValueError):                                     # row marked result_withdrawn, review carries no notice
        S(WITHDRAWN_ROW, {"outcomes": [{"primary": True, "result": {}, "trials": []}]})
    with pytest.raises(ValueError):                                     # declared but empty: no statements
        S(WITHDRAWN_ROW, _review_with(withdrawn={**NOTICE, "statements": []}))
    with pytest.raises(ValueError):                                     # declared but contradicted: a number still pooled beside it
        S(WITHDRAWN_ROW, _review_with(k=1, trials=[{"id": "PMID 36027570"}]))
    with pytest.raises(ValueError):                                     # a required phrase missing
        S(WITHDRAWN_ROW, _review_with(withdrawn={**NOTICE, "statements": [x for x in NOTICE["statements"] if "not yet published" not in x] + ["extra"]}))
    with pytest.raises(ValueError):                                     # the page does not say RESULT WITHDRAWN
        build_bundle.assessment_state(WITHDRAWN_ROW, "x", False, False, False, review=_review_with(), review_ref="r", review_sha256="a" * 64, page_text="<html>HR 0.88</html>")
    page_ok = build_bundle.assessment_state(WITHDRAWN_ROW, "x", False, False, False, review=_review_with(), review_ref="r", review_sha256="a" * 64, page_text="<h2>Result withdrawn</h2>")
    assert page_ok["basis"]["withdrawal_record"]["contract"]["page_carries_result_withdrawn"] is True
    # a review with no notice and no withdrawn row: never WITHDRAWN
    assert build_bundle.assessment_state({"id": "PMID 1"}, "x", False, False, False, review={"outcomes": []})["state"] == "ASSESSED"


def test_clean_negative_is_recorded_as_a_negative_with_its_scope(bundle):
    cn = bundle["clean_negatives"][0]
    assert cn["result"].startswith("8 of 8") and "says nothing about the defect" in cn["meaning"] and "95.03" in cn["meaning"]
    assert "constant across every row" in cn["why_the_field_stays"]


# ------------------------------------------------------------------ 3.13: mentioning what is excluded must never make it included

def test_exclusion_scopes_are_cut_before_membership_is_read():
    S = lambda span, defn=DEFN: build_bundle.span_target_mention(span, [0.87, 0.78, 0.97], defn, CC)
    excl = S("The primary outcome was cardiovascular death only, excluding nonfatal myocardial infarction and nonfatal stroke, and occurred less often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).")
    assert excl["state"] == "ENDPOINT_INCOMPATIBLE" and excl["excluded_components"] == ["MYOCARDIAL_INFARCTION", "STROKE"]     # three components named; refused
    assert S("The primary outcome was cardiovascular death and occurred less often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).")["state"] == "ENDPOINT_INCOMPATIBLE"   # the contrast
    ctrl = S("The primary outcome was 3-point MACE excluding unstable angina and occurred less often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).")
    assert ctrl["state"] == "PASS"                                                                                                  # false-refusal control
    assert S("The primary composite outcome of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke occurred less often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).")["state"] == "PASS"
    # an exclusion in the row's DEFINITION span cannot be rescued by the primary-outcome name in the clause
    assert S("The primary outcome occurred less often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).",
             "The primary outcome was cardiovascular death only, excluding nonfatal myocardial infarction and nonfatal stroke.")["state"] == "ENDPOINT_INCOMPATIBLE"
    inc, exc = build_bundle.split_exclusions("cardiovascular death only, excluding nonfatal myocardial infarction and nonfatal stroke, and occurred less often (hazard ratio, 0.87)")
    assert "myocardial" in exc and "myocardial" not in inc and "hazard ratio" in inc




# ------------------------------------------------------------------ 3.17: three pooled states, extra/missing rendered, P13/P14

ODYSSEY_FIELDS = {"id": "PMID 30403574", "target_endpoint_class": "NEAR_MATCH", "endpoint_admissibility": "NEAR_MATCH_DECLARED",
                  "target_endpoint_components": "['coronary heart disease death', 'myocardial infarction', 'stroke', 'unstable angina']",
                  "target_endpoint_extra_components": "['unstable angina']", "target_endpoint_missing_components": "[]"}


def test_component_set_checks_fail_on_odyssey_and_pass_on_an_exact_row():
    c = build_bundle.component_set_checks(ODYSSEY_FIELDS, ["CORONARY_HEART_DISEASE_DEATH", "MYOCARDIAL_INFARCTION", "STROKE", "UNSTABLE_ANGINA"], CC)
    assert c["pooled_state"] == "NEAR_MATCH_POOLED" and c["P13_no_extra_components"] is False and c["P14_missing_components_consistent"] is False
    assert c["row_lacks"] == ["CARDIOVASCULAR_DEATH"] and c["row_surplus"] == ["CORONARY_HEART_DISEASE_DEATH", "UNSTABLE_ANGINA"]
    ok = build_bundle.component_set_checks({"target_endpoint_class": "EXACT_TARGET", "target_endpoint_extra_components": [], "target_endpoint_missing_components": []}, CC, CC)
    assert ok["pooled_state"] == "EXACT_TARGET_POOLED" and ok["P13_no_extra_components"] and ok["P14_missing_components_consistent"]
    unb = build_bundle.component_set_checks({"endpoint_binding": "unbound_legacy", "endpoint_admissibility": "UNBOUND_LEGACY"}, [], CC)
    assert unb["pooled_state"] == "UNBOUND_POOLED" and unb["P13_no_extra_components"] and unb["P14_missing_components_consistent"]   # nothing to compare: not a clear, not a fail
    # a row that RECORDS what it lacks is consistent: the refusal then comes from P4/P9, not from P14
    rec = build_bundle.component_set_checks({"target_endpoint_class": "NEAR_MATCH", "target_endpoint_extra_components": [], "target_endpoint_missing_components": ["cardiovascular death"]},
                                            ["MYOCARDIAL_INFARCTION", "STROKE"], CC)
    assert rec["P14_missing_components_consistent"] is True and rec["row_lacks"] == ["CARDIOVASCULAR_DEATH"]


def test_bundle_renders_pooled_state_and_component_lists_per_row(bundle):
    for r in bundle["verification_rows"]:
        assert r["pooled_state"] == "EXACT_TARGET_POOLED"
        assert r["admission"]["predicates"]["P13_no_extra_components"]["state"] == "PASS"
        assert r["admission"]["predicates"]["P14_missing_components_consistent"]["state"] == "PASS"
    bs = bundle["binding_states"]
    assert bs["counts"]["pooled_states"] == {"EXACT_TARGET_POOLED": 8, "UNBOUND_POOLED": 2} and bs["counts"]["rows_with_extra_components"] == 0
    for r in bs["rows"]:
        assert "extra_components" in r and "missing_components" in r and "components_as_classified" in r
    assert any(l["id"] == "L15_pooled_state_is_rendered_not_enforced_upstream" for l in bundle["limits"])
