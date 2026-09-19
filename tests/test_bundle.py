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
    assert src["generating_commit"] == "NOT_RECORDED"
    for name, blob in src["served_blob_git_sha1"].items():
        at = subprocess.run(["git", "rev-parse", f"{src['content_commit']}:docs/reviews/{SLUG}/{name}"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        data = _bytes(os.path.join(REVIEW_DIR, name))
        assert at == blob == hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest(), name
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
        assert set(r["admission"]["predicates"]) == set(bundle["vocabulary"]["admission_predicates"]) - {"ADMISSIBLE", "MIGRATION_STATE_UNBOUND_LEGACY", "INADMISSIBLE"}
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
    assert "not refused" in bs["statement"] and "UNVERIFIABLE" in bs["statement"]


# ------------------------------------------------------------------ 3.4: P9 positive binding, certified eligibility, L11

def test_p9_is_read_from_the_span_and_passes_every_genuine_row(bundle):
    for r in bundle["verification_rows"]:
        p9 = r["admission"]["predicates"]["P9_span_target_mention"]
        assert p9["state"] == "PASS", (r["trial"]["id"], p9)
        assert p9["clause"] and (p9["clause"] in r["span"]["text"])
    cc = ["CARDIOVASCULAR_DEATH", "MYOCARDIAL_INFARCTION", "STROKE"]
    assert build_bundle.span_target_mention("Fewer patients died from cardiovascular causes (hazard ratio, 0.78; 95% CI, 0.66 to 0.93).", ["0.78", "0.66", "0.93"], "The primary composite outcome was cardiovascular death, MI or stroke", cc)["state"] == "ENDPOINT_INCOMPATIBLE"
    assert build_bundle.span_target_mention("Cataract surgery occurred more often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).", ["0.87", "0.78", "0.97"], "The primary composite outcome was cardiovascular death, MI or stroke", cc)["state"] == "AMBIGUOUS_ENDPOINT_BINDING"
    assert build_bundle.span_target_mention("Retinopathy occurred more often (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).", ["0.87", "0.78", "0.97"], "x", cc)["state"] == "ENDPOINT_INCOMPATIBLE"
    assert build_bundle.span_target_mention("The primary outcome occurred in fewer patients (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).", ["0.87", "0.78", "0.97"], "The primary composite outcome was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke.", cc)["state"] == "PASS"
    # a primary-outcome name whose definition span does NOT bind to the target is not admitted by the name alone
    assert build_bundle.span_target_mention("The primary outcome occurred in fewer patients (hazard ratio, 0.87; 95% CI, 0.78 to 0.97).", ["0.87", "0.78", "0.97"], "The primary outcome was hospitalization for heart failure.", cc)["state"] != "PASS"


def test_eligibility_is_read_from_the_certified_copy_and_named(bundle):
    assert "families.json" in bundle["eligibility_source"]["authoritative"]
    for r in bundle["verification_rows"]:
        p5 = r["admission"]["predicates"]["P5_family_eligible"]
        assert "families.json" in p5["authoritative_copy"] and p5["copies_agree"] is True


def test_l11_coacquisition_rewrite_limit_is_printed(bundle):
    assert any(l["id"] == "L11_coacquisition_rewrite" and "signed release" in l["limit"] for l in bundle["limits"])
