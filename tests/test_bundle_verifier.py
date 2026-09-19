"""The independent verifier (scripts/verify_bundle.py, standard library only) agrees with the bundle, reproduces the
pool without importing the harness, and -- the property that separates a gate from a badge -- a single controlled
corruption of any mandatory per-row limb makes EXACTLY that row inadmissible.

Run as a subprocess so the verifier's independence from the harness is a fact of the test, not a convention."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))   # test-side helpers only; the verifier under test runs as a subprocess
SLUG = "glp1-ra-mace-t2d"
VERIFIER = os.path.join(ROOT, "scripts", "verify_bundle.py")
PER_ROW_LIMBS = ("span", "effect", "components", "eligibility", "conflict", "nontarget_span", "unlisted_span", "fragment")
MIGRATION_LIMB = "binding"


def _run(*extra):
    p = subprocess.run([sys.executable, VERIFIER, "--root", "docs", "--slug", SLUG, "--json", *extra],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    assert p.returncode in (0, 1), p.stderr
    return json.loads(p.stdout)


def test_verifier_imports_nothing_from_the_repository():
    src = open(VERIFIER, encoding="utf-8").read()
    assert "from harness" not in src and "import harness" not in src and "sys.path.insert" not in src


@pytest.fixture(scope="module")
def baseline():
    return _run()


def test_baseline_passes_and_agrees_with_bundle(baseline):
    assert baseline["verdict"] == "PASS", baseline["failures"]
    assert all(a.get("bytes_ok") and a.get("declared_digest_ok") for a in baseline["artefacts"] if "bytes_ok" in a)
    assert all(s["ok"] for s in baseline["supporting"])
    assert baseline["certificate"]["release_sha256_recomputed"] and baseline["certificate"]["review_sha256_recomputed"]
    assert all(r["agrees_with_bundle"] and r["predicates_agree_with_bundle"] for r in baseline["rows"])
    assert all(r["offsets_reproduce_span"] for r in baseline["rows"])


def test_pool_reproduced_without_the_harness(baseline):
    p = baseline["pool"]
    assert p["reproduced_to_1e-9"], p["abs_deltas"]
    assert abs(p["recomputed"]["estimate"] - 0.8559934175938467) < 1e-9
    assert abs(p["recomputed"]["tau2"] - 0.00004447972517261924) < 1e-9
    assert abs(p["t_crit_recomputed"] - 2.3646242515927853) < 1e-9   # t_{0.975, 7}
    assert p["k_declared"] == 8 and p["admissible_rows"] == 7


def test_absence_claims_judged_from_recomputed_preservation(baseline):
    neg = [c for c in baseline["absence_claims"] if c["claim_kind"] == "NEGATIVE"]
    assert neg
    soul = [c for c in neg if c["pmid"] == "40162642"]
    assert soul and all(c["coverage_recomputed"] == "EXCERPT_ONLY" and c["negative_claim_admissible"] is False for c in soul)
    assert all(c["preservation"]["missing"] == c["preservation"]["units"] for c in soul)
    assert all(c["agrees"] for c in neg if "agrees" in c)


@pytest.mark.parametrize("pmid", ["40162642", "27295427"])
@pytest.mark.parametrize("limb", PER_ROW_LIMBS)
def test_one_corrupted_limb_makes_exactly_that_row_inadmissible(baseline, pmid, limb):
    base_bad = {r["pmid"] for r in baseline["rows"] if r["final"] == "INADMISSIBLE"}
    rep = _run("--corrupt", pmid, limb)
    now_bad = {r["pmid"] for r in rep["rows"] if r["final"] == "INADMISSIBLE"}
    assert now_bad == base_bad | {pmid}, (limb, sorted(now_bad))


@pytest.mark.parametrize("pmid", ["40162642", "27295427"])
def test_unbinding_a_row_makes_it_a_migration_state_not_admissible_and_not_refused(baseline, pmid):
    """The admit_rows fail-open, as the bundle must render it: an unbound_legacy row leaves the admissible set but is
    NOT INADMISSIBLE -- it is MIGRATION_STATE_UNBOUND_LEGACY, and exactly that row changes."""
    base_states = {r["pmid"]: r["final"] for r in baseline["rows"]}
    rep = _run("--corrupt", pmid, MIGRATION_LIMB)
    states = {r["pmid"]: r["final"] for r in rep["rows"]}
    assert states[pmid] == "MIGRATION_STATE_UNBOUND_LEGACY"
    assert {k: v for k, v in states.items() if k != pmid} == {k: v for k, v in base_states.items() if k != pmid}
    assert rep["pool"]["admissible_rows"] == baseline["pool"]["admissible_rows"] - 1


def test_rendered_unbound_legacy_rows_are_reported_and_never_counted_admissible(baseline):
    bs = baseline["binding_states"]
    assert bs["migration_state_unbound_legacy"] == 2
    unbound = {(r["outcome"], r["id"]) for r in bs["rendered_rows"] if r["binding_class"] != "BOUND"}
    assert unbound == {("Gastrointestinal adverse events", "PMID 31189511"), ("Adverse events leading to discontinuation", "PMID 27295427")}
    assert bs["migration_rows_counted_admissible"] == 0
    assert all(r["final"] == "ADMISSIBLE" for r in baseline["rows"] if r["predicates"]["P8_endpoint_bound"] and all(r["predicates"].values()))


def test_failures_carry_named_codes():
    src = open(VERIFIER, encoding="utf-8").read()
    for code in ("ANCHOR_PRESERVATION_FAILURE", "ANCHOR_XML_DIGEST_MISMATCH", "ARTEFACT_DIGEST_MISMATCH", "CERTIFICATE_MISMATCH",
                 "DIGEST_SCOPE_MISMATCH", "ROW_VERDICT_DISAGREES", "ABSENCE_CLAIM_DISAGREES", "POOL_NOT_REPRODUCED", "SELECTOR_REFUSED"):
        assert code in src, code


def test_corrupting_the_shared_container_fails_every_row_that_depends_on_it(baseline):
    """records.json is one container for all abstracts; damaging it must not be silent for any row."""
    rep = _run("--corrupt", "40162642", "container")
    assert all(r["final"] == "INADMISSIBLE" for r in rep["rows"])


def test_verifier_reports_its_non_claims_and_reproduces_digest_scopes(baseline):
    assert baseline["digest_scopes_reproduced"] is True
    assert "the production admission path" in baseline["not_checked"]
    assert baseline["endpoint_compatibility"]["state"] == "COMPATIBLE_WITH_DECLARED_VARIATION"
    assert baseline["statistical_input"]["PMID 40162642"]["interval_construction"] == "GROUP_SEQUENTIAL_ADJUSTED"
    src = open(VERIFIER, encoding="utf-8").read()
    assert "does NOT check" in src and "PRODUCTION admission path" in src
    assert len(src.splitlines()) <= 800   # 686 after the panel's round 3 (P9, refusal codes, no-crash paths, live anchor); the 200-500 target was for a minimal checker


def _copy_served_tree(bundle, dst):
    """Copy only what the verifier reads: artefacts, supporting files, review-dir files."""
    import shutil
    paths = {a["served_path"] for a in bundle["artefacts"] if a["state"] == "SERVED"}
    paths |= {f["path"].removeprefix("docs/") for f in bundle["supporting_files"]}
    paths |= {r["served_path"] for r in bundle["review_files"]} | {f"reviews/{SLUG}/BUNDLE.json"}
    for p in paths:
        src = os.path.join(ROOT, "docs", *p.split("/"))
        out = os.path.join(dst, *p.split("/"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copyfile(src, out)


def test_h1_delete_a_sentence_and_recompute_every_digest_is_caught_by_the_anchor(tmp_path):
    """The panel's H1: delete a sentence from a cached abstract, recompute EVERY digest (artefact, digest_scopes, both
    certificate scopes, release_sha256) so the package is perfectly self-consistent. Inside the recomputable set nothing
    can notice. The retained EFetch XML is outside it: the verifier's preservation recomputation must FAIL the run."""
    import hashlib
    from harness.canonical import canonical_json, sha256_text   # test-side helper only; the verifier itself imports nothing
    bundle = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    root = str(tmp_path / "site")
    _copy_served_tree(bundle, root)
    rec_path = os.path.join(root, "cache", SLUG, "records.json")
    records = json.load(open(rec_path, encoding="utf-8"))
    victim = next(r for r in records["records"] if str(r["id"]) == "27295427")          # LEADER, currently COMPLETE_ABSTRACT
    sentences = victim["abstract"].split(". ")
    idx = next(i for i, x in enumerate(sentences) if "adverse events" in x.lower())      # LEADER's safety sentence
    dropped = sentences.pop(idx)
    assert "gastrointestinal" in dropped.lower(), dropped
    victim["abstract"] = ". ".join(sentences)
    new_raw = json.dumps(records, ensure_ascii=False, indent=1).encode("utf-8")
    open(rec_path, "wb").write(new_raw)
    raw_sha, canon_sha = hashlib.sha256(new_raw).hexdigest(), sha256_text(canonical_json(json.loads(new_raw)))
    corpus_sha = sha256_text(canonical_json(json.loads(new_raw)["records"]))
    cert_path = os.path.join(root, "reviews", SLUG, "CERTIFICATE.json")
    cert = json.load(open(cert_path, encoding="utf-8"))
    cert["records_file_sha256"], cert["retrieved_corpus_sha256"] = canon_sha, corpus_sha
    cert.pop("release_sha256")
    cert["release_sha256"] = sha256_text(canonical_json(cert))
    cert_bytes = json.dumps(cert, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    open(cert_path, "wb").write(cert_bytes)
    b = json.load(open(os.path.join(root, "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    for a in b["artefacts"]:
        if a["ref"].endswith("records.json"):
            a["sha256"], a["bytes"], a["declared_digest"] = raw_sha, len(new_raw), canon_sha
    for sc in b["digest_scopes"][0]["scopes"]:
        sc["value"] = {"raw served bytes": raw_sha, "whole file as JSON object": canon_sha, "obj['records'] only": corpus_sha}[sc["subject"]]
    b["certificate"]["sha256_of_file"], b["certificate"]["bytes"], b["certificate"]["release_sha256"] = hashlib.sha256(cert_bytes).hexdigest(), len(cert_bytes), cert["release_sha256"]
    parsed_sha = sha256_text(victim["abstract"])
    for r in b["verification_rows"]:
        r["source"]["source_sha256"] = raw_sha
        for d in r["source"]["digests"]:
            d["value"] = {"container file": raw_sha, "container as JSON object": canon_sha}.get(d["subject"], d["value"])
        if r["trial"]["id"] == "PMID 27295427":
            r["source"]["representation_sha256"] = parsed_sha
            r["span"]["representation_sha256"] = parsed_sha
            i = victim["abstract"].find(r["span"]["text"])
            assert i >= 0, "the result span must survive the deletion for H1 to be the right experiment"
            r["span"]["start"], r["span"]["end"] = i, i + len(r["span"]["text"])
    for rf in b["review_files"]:
        if rf["file"] == "CERTIFICATE.json":
            rf["sha256"], rf["bytes"] = hashlib.sha256(cert_bytes).hexdigest(), len(cert_bytes)
    doc = next(d for d in b["documents"] if d["document_id"] == "pubmed:27295427")
    doc["representations"]["PARSED_SOURCE"]["container_sha256"] = raw_sha
    doc["representations"]["PARSED_SOURCE"]["sha256_parsed"] = parsed_sha
    json.dump(b, open(os.path.join(root, "reviews", SLUG, "BUNDLE.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    p = subprocess.run([sys.executable, VERIFIER, "--root", root, "--slug", SLUG, "--json"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    rep = json.loads(p.stdout)
    assert all(a.get("bytes_ok") and a.get("declared_digest_ok") for a in rep["artefacts"] if "bytes_ok" in a)   # every digest layer green
    assert rep["certificate"]["release_sha256_recomputed"] and rep["digest_scopes_reproduced"]
    assert next(r for r in rep["rows"] if r["pmid"] == "27295427")["final"] == "ADMISSIBLE"                     # positive claim still stands
    anchor = next(a for a in rep["anchors"] if a["pmid"] == "27295427")                                          # ...and the anchor notices
    assert anchor["preservation"]["verdict"] == "FAILURE" and anchor["coverage_recomputed"] == "EXCERPT_ONLY" and anchor["coverage_recorded"] == "COMPLETE_ABSTRACT"
    assert rep["verdict"] == "FAIL" and any(f.startswith("ANCHOR_PRESERVATION_FAILURE 27295427") for f in rep["failures"]), rep["failures"]
    assert anchor["preservation"]["missing"] == 1 and anchor["preservation"]["preserved"] == 3
    assert dropped



# ---------------------------------------------------------------------------------------------------------------
# panel round 3: doctored sites with EVERY digest recomputed (the shape of the panel's mutations)
# ---------------------------------------------------------------------------------------------------------------

def _recompute_everything(root, edited_pmids=()):
    """After editing records.json and/or review.json in a copied served tree, recompute every digest the bundle and
    the certificate carry so the package is self-consistent: artefact raw/canonical digests, digest_scopes, both
    certificate scopes, review_sha256, release_sha256, review_files, per-row representation digests and offsets."""
    import hashlib
    from harness.canonical import canonical_json, sha256_text, review_core
    from build_bundle import normalize, locate
    rec_path = os.path.join(root, "cache", SLUG, "records.json")
    new_raw = open(rec_path, "rb").read()
    records = json.loads(new_raw.decode("utf-8"))
    raw_sha, canon_sha = hashlib.sha256(new_raw).hexdigest(), sha256_text(canonical_json(records))
    corpus_sha = sha256_text(canonical_json(records["records"]))
    rev_path = os.path.join(root, "reviews", SLUG, "review.json")
    review_bytes = open(rev_path, "rb").read()
    review = json.loads(review_bytes.decode("utf-8"))
    review_sha = sha256_text(canonical_json(review_core(review)))
    cert_path = os.path.join(root, "reviews", SLUG, "CERTIFICATE.json")
    cert = json.load(open(cert_path, encoding="utf-8"))
    cert["records_file_sha256"], cert["retrieved_corpus_sha256"], cert["review_sha256"] = canon_sha, corpus_sha, review_sha
    cert.pop("release_sha256")
    cert["release_sha256"] = sha256_text(canonical_json(cert))
    cert_bytes = json.dumps(cert, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    open(cert_path, "wb").write(cert_bytes)
    bpath = os.path.join(root, "reviews", SLUG, "BUNDLE.json")
    b = json.load(open(bpath, encoding="utf-8"))
    for a in b["artefacts"]:
        if a["ref"].endswith("records.json"):
            a["sha256"], a["bytes"], a["declared_digest"] = raw_sha, len(new_raw), canon_sha
    for sc in b["digest_scopes"][0]["scopes"]:
        sc["value"] = {"raw served bytes": raw_sha, "whole file as JSON object": canon_sha, "obj['records'] only": corpus_sha}[sc["subject"]]
    b["certificate"]["sha256_of_file"], b["certificate"]["bytes"], b["certificate"]["release_sha256"] = hashlib.sha256(cert_bytes).hexdigest(), len(cert_bytes), cert["release_sha256"]
    for rf in b["review_files"]:
        if rf["file"] == "CERTIFICATE.json":
            rf["sha256"], rf["bytes"] = hashlib.sha256(cert_bytes).hexdigest(), len(cert_bytes)
        if rf["file"] == "review.json":
            rf["sha256"], rf["bytes"] = hashlib.sha256(review_bytes).hexdigest(), len(review_bytes)
    by_pmid = {str(r["id"]): r for r in records["records"]}
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    trial_by = {str(t["id"]).replace("PMID ", ""): t for t in primary["trials"]}
    for r in b["verification_rows"]:
        pmid = r["trial"]["id"].replace("PMID ", "")
        r["source"]["source_sha256"] = raw_sha
        for d in r["source"]["digests"]:
            d["value"] = {"container file": raw_sha, "container as JSON object": canon_sha}.get(d["subject"], d["value"])
        parsed = by_pmid[pmid]["abstract"]
        r["source"]["representation_sha256"] = sha256_text(parsed)
        t = trial_by[pmid]
        if pmid in edited_pmids:
            span = t.get("endpoint_result_span") or ""
            loc = locate(span, parsed)
            r["span"].update({"text": span, "match": loc["match"], "parent_representation": loc.get("parent"), "start": loc.get("start"), "end": loc.get("end")})
            r["effect"].update({"estimate": t["effect"], "ci_low": t["ci_low"], "ci_high": t["ci_high"]})
            r["admission"]["final"] = "ADMISSIBLE"      # what a producer running the fail-open would record
        r["span"]["representation_sha256"] = sha256_text(parsed) if r["span"].get("parent_representation") == "PARSED_SOURCE" else sha256_text(normalize(parsed))
    for d in b["documents"]:
        if d["document_id"].startswith("pubmed:"):
            pm = d["document_id"].split(":")[1]
            if pm in by_pmid:
                d["representations"]["PARSED_SOURCE"]["container_sha256"] = raw_sha
                d["representations"]["PARSED_SOURCE"]["sha256_parsed"] = sha256_text(by_pmid[pm]["abstract"])
    json.dump(b, open(bpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def _doctored_site(tmp_path, edit_records=None, edit_review=None, edited_pmids=()):
    bundle = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    root = str(tmp_path / "site")
    _copy_served_tree(bundle, root)
    if edit_records:
        p = os.path.join(root, "cache", SLUG, "records.json")
        rec = json.load(open(p, encoding="utf-8"))
        edit_records(rec)
        open(p, "wb").write(json.dumps(rec, ensure_ascii=False, indent=1).encode("utf-8"))
    if edit_review:
        p = os.path.join(root, "reviews", SLUG, "review.json")
        rev = json.load(open(p, encoding="utf-8"))
        edit_review(rev)
        open(p, "wb").write(json.dumps(rev, ensure_ascii=False, indent=2).encode("utf-8"))
    _recompute_everything(root, edited_pmids)
    return root


def _verify(root, *extra):
    p = subprocess.run([sys.executable, VERIFIER, "--root", root, "--slug", SLUG, "--json", *extra], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    assert p.stdout.strip(), "verifier produced NO JSON -- a crash, not a verdict: " + p.stderr[-800:]
    return json.loads(p.stdout)


def _set_primary_row(rev, pmid, span, effect, lo, hi):
    o = next(x for x in rev["outcomes"] if x.get("primary"))
    t = next(x for x in o["trials"] if str(x["id"]).replace("PMID ", "") == pmid)
    t["endpoint_result_span"], t["effect"], t["ci_low"], t["ci_high"] = span, effect, lo, hi


def test_m7a_genuine_nontarget_sentence_with_its_own_tuple_is_refused_at_binding(tmp_path):
    """LEADER's cardiovascular-death sentence -- verbatim in the record, its own genuine HR -- bound to the MACE claim.
    Every digest layer is clean; P2 and P3 PASS; P9 must refuse ENDPOINT_INCOMPATIBLE naming the bound mention."""
    span = ("Fewer patients died from cardiovascular causes in the liraglutide group (219 patients [4.7%]) than in the placebo group "
            "(278 [6.0%]) (hazard ratio, 0.78; 95% CI, 0.66 to 0.93; P=0.007).")
    root = _doctored_site(tmp_path, edit_review=lambda rev: _set_primary_row(rev, "27295427", span, 0.78, 0.66, 0.93), edited_pmids=("27295427",))
    rep = _verify(root)
    row = next(r for r in rep["rows"] if r["pmid"] == "27295427")
    assert rep["certificate"]["release_sha256_recomputed"] and rep["digest_scopes_reproduced"]
    assert row["predicates"]["P2_span_located"] and row["predicates"]["P3_effect_tokens_in_span"]
    assert row["p9"]["state"] == "ENDPOINT_INCOMPATIBLE" and "CARDIOVASCULAR_DEATH" in json.dumps(row["p9"]["witness"])
    assert row["final"] == "INADMISSIBLE" and row["refusal"] == "ENDPOINT_INCOMPATIBLE"
    assert any(f.startswith("ENDPOINT_INCOMPATIBLE 27295427") for f in rep["failures"]) and rep["verdict"] == "FAIL"


def test_m7b_rewind_all_cause_mortality_sentence_is_refused_at_binding(tmp_path):
    span = ("All-cause mortality did not differ between groups (536 [10\u00b78%] in the dulaglutide group vs 592 [12\u00b70%] in the placebo group; "
            "HR 0\u00b790, 95% CI 0\u00b780-1\u00b701; p=0\u00b7067).")
    root = _doctored_site(tmp_path, edit_review=lambda rev: _set_primary_row(rev, "31189511", span, 0.9, 0.8, 1.01), edited_pmids=("31189511",))
    rep = _verify(root)
    row = next(r for r in rep["rows"] if r["pmid"] == "31189511")
    assert row["predicates"]["P2_span_located"] and row["span_match"] == "VERBATIM"
    assert row["p9"]["state"] == "ENDPOINT_INCOMPATIBLE" and "all-cause mortality" in json.dumps(row["p9"]["witness"])
    assert row["final"] == "INADMISSIBLE"


def test_m8_unlisted_outcome_sentence_is_ambiguous_never_admitted(tmp_path):
    def edit(rec):
        r = next(x for x in rec["records"] if str(x["id"]) == "27295427")
        r["abstract"] += " Retinopathy complications occurred in more patients in the liraglutide group (hazard ratio, 0.87; 95% CI, 0.78 to 0.97)."
    span = "Retinopathy complications occurred in more patients in the liraglutide group (hazard ratio, 0.87; 95% CI, 0.78 to 0.97)."
    root = _doctored_site(tmp_path, edit_records=edit, edit_review=lambda rev: _set_primary_row(rev, "27295427", span, 0.87, 0.78, 0.97), edited_pmids=("27295427",))
    rep = _verify(root)
    row = next(r for r in rep["rows"] if r["pmid"] == "27295427")
    assert row["predicates"]["P2_span_located"] and row["predicates"]["P3_effect_tokens_in_span"]
    assert row["p9"]["state"] in ("AMBIGUOUS_ENDPOINT_BINDING", "ENDPOINT_INCOMPATIBLE") and row["final"] == "INADMISSIBLE"


def test_h1a_sustain6_deleted_safety_sentence_is_caught_although_it_carries_no_negative_claim(tmp_path):
    """SUSTAIN-6 carries only POSITIVE_REFUSAL harms claims. The anchor must still run for it."""
    victim_sentence = "Fewer serious adverse events occurred in the semaglutide group, although more patients discontinued treatment because of adverse events, mainly gastrointestinal."

    def edit(rec):
        r = next(x for x in rec["records"] if str(x["id"]) == "27633186")
        assert victim_sentence in r["abstract"]
        r["abstract"] = r["abstract"].replace(" " + victim_sentence, "")
    root = _doctored_site(tmp_path, edit_records=edit)
    rep = _verify(root)
    an = next(a for a in rep["anchors"] if a["pmid"] == "27633186")
    assert an["preservation"]["verdict"] == "FAILURE" and an["coverage_recomputed"] == "EXCERPT_ONLY" and an["coverage_recorded"] == "COMPLETE_ABSTRACT"
    assert rep["verdict"] == "FAIL" and any(f.startswith("ANCHOR_PRESERVATION_FAILURE 27633186") for f in rep["failures"])
    assert rep["pool"]["admissible_rows"] == 7   # the positive claims stand; the coverage claim does not


def test_m11_rewritten_fragment_is_a_selector_mismatch(tmp_path):
    bundle = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    root = str(tmp_path / "site")
    _copy_served_tree(bundle, root)
    bpath = os.path.join(root, "reviews", SLUG, "BUNDLE.json")
    b = json.load(open(bpath, encoding="utf-8"))
    row = next(r for r in b["verification_rows"] if r["trial"]["id"] == "PMID 27633186")
    row["source"]["document_ref"] = row["source"]["document_ref"].split("#")[0] + "#PMID-99999999"
    json.dump(b, open(bpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    rep = _verify(root)
    r = next(x for x in rep["rows"] if x["pmid"] == "27633186")
    assert r["refusal"] == "SELECTOR_MISMATCH" and r["final"] == "INADMISSIBLE"
    assert any(f.startswith("SELECTOR_MISMATCH 27633186") for f in rep["failures"])


def test_m5b_eligibility_unresolved_in_the_certified_copy_only_is_read_from_the_certified_copy(tmp_path):
    bundle = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    root = str(tmp_path / "site")
    _copy_served_tree(bundle, root)
    fpath = os.path.join(root, "cache", SLUG, "families.json")
    fam = json.load(open(fpath, encoding="utf-8"))
    next(f for f in fam["families"] if f["family_id"] == "NCT01179048")["eligibility"] = {"state": "UNRESOLVED"}   # LEADER, certified copy only
    open(fpath, "wb").write(json.dumps(fam, ensure_ascii=False, indent=2).encode("utf-8"))
    rep = _verify(root)   # the artefact digest for families.json now mismatches too -- both are reported, neither is silent
    row = next(r for r in rep["rows"] if r["pmid"] == "27295427")
    assert row["predicates"]["P5_family_eligible"] is False and row["final"] == "INADMISSIBLE"
    assert any(f.startswith("ELIGIBILITY_COPIES_DISAGREE NCT01179048") for f in rep["failures"])
    assert any(f.startswith("ARTEFACT_DIGEST_MISMATCH") and "families.json" in f for f in rep["failures"])


def test_m10_duplicate_record_id_is_a_verdict_not_a_crash(tmp_path):
    def edit(rec):
        rec["records"].append(dict(next(x for x in rec["records"] if str(x["id"]) == "27633186")))
    root = _doctored_site(tmp_path, edit_records=edit)
    rep = _verify(root)
    assert rep["verdict"] == "FAIL"
    assert any(f.startswith("SELECTOR_REFUSED") and "27633186" in f for f in rep["failures"])
    assert next(r for r in rep["rows"] if r["pmid"] == "27633186")["final"] == "INADMISSIBLE"


def test_m4_records_json_removed_is_a_refused_verdict_with_json(tmp_path):
    bundle = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    root = str(tmp_path / "site")
    _copy_served_tree(bundle, root)
    os.remove(os.path.join(root, "cache", SLUG, "records.json"))
    rep = _verify(root)
    assert rep["verdict"] == "REFUSED" and rep["refusal_code"] == "ARTEFACT_UNREACHABLE" and "records.json" in rep["detail"]


def test_h2_held_pdf_removed_is_reported_and_the_run_completes(tmp_path):
    bundle = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "BUNDLE.json"), encoding="utf-8"))
    root = str(tmp_path / "site")
    _copy_served_tree(bundle, root)
    os.remove(os.path.join(root, "outputs", "handover", "glp1_regulatory", "held", "209637s025lbl.pdf"))
    rep = _verify(root)
    assert rep["verdict"] == "FAIL"
    assert any(f.startswith("ARTEFACT_UNREACHABLE") and "209637s025lbl.pdf" in f for f in rep["failures"])
    assert rep["pool"]["reproduced_to_1e-9"]   # everything else still ran and reported


def test_baseline_p9_passes_all_eight_genuine_spans(baseline):
    assert all(r["p9"]["state"] == "PASS" for r in baseline["rows"]), [(r["pmid"], r["p9"]) for r in baseline["rows"] if r["p9"]["state"] != "PASS"]



def test_upper_limit_swapped_for_another_endpoints_genuine_limit_is_refused_by_p3(tmp_path):
    """The producer's verify_pooled checks the point estimate only: LEADER 0.87 (0.78-0.97) with the upper limit replaced by
    0.93 -- the genuine upper limit of the cardiovascular-death endpoint in the same abstract -- still earns its label.
    P3 checks estimate AND both limits against the clause; the row must be refused."""
    def edit(rev):
        o = next(x for x in rev["outcomes"] if x.get("primary"))
        t = next(x for x in o["trials"] if str(x["id"]).endswith("27295427"))
        t["ci_high"] = 0.93
    root = _doctored_site(tmp_path, edit_review=edit, edited_pmids=("27295427",))
    rep = _verify(root)
    row = next(r for r in rep["rows"] if r["pmid"] == "27295427")
    assert row["predicates"]["P2_span_located"] is True and row["predicates"]["P3_effect_tokens_in_span"] is False
    assert row["final"] == "INADMISSIBLE" and rep["verdict"] == "FAIL"
