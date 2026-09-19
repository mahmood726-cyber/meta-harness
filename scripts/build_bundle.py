"""Serve the evidence bundle a review's CERTIFICATE.json commits to -- without touching the certificate.

THE BUNDLE IS THE VERIFICATION API (architectural review, 2026-09-19). Not "files an auditor can download" but the
input to an independent checker that knows nothing about harness/pipeline.py. Per primary-pool row it carries a
source object, a span object with offsets into a named representation, an endpoint object, an effect object, a
decision object and an admission object, so a stdlib verifier (scripts/verify_bundle.py) can PROVE invariants rather
than read assertions, and a single controlled corruption of any mandatory limb makes exactly that row inadmissible.
`verified: true` is a producer assertion; this file carries the material the assertion is about.

HISTORY OF THE FORMAT (all 2026-09-19):
  v1  CERTIFICATE.json committed digests to files that 404'd on the served site (14 of 18 probed URLs). Every input
      is mirrored at docs/<repo-root-relative ref>; BUNDLE.json names each with digest, path and length; an input we
      may not redistribute is declared, never silently omitted.
  v2  A verifier proved "this quotation occurs in our cache" and reported "faithful to the source". SOUL's cached
      span is stitched; REWIND's and Harmony's rendered spans fold Lancet middle-dot decimals. Two identities per
      document and a mechanical span-match ladder.
  v3  (a) Resolvability is RECURSIVE: aact_inputs.json and review.json referenced ~15,000 AACT rows by {keys, digest}
      with no body -- a hash without its row body is a promise. Bodies are re-selected from the same-named snapshot,
      digest-matched and published under docs/acquisitions/; a walk from this file reports every edge that still
      ends in a digest with no body. (b) The cached SOUL abstract omits the safety sentence, so the page's
      OUTCOME_NOT_IN_SOURCE for its gastrointestinal row is true of our cache and false of the cited abstract -- an
      absence claim from a truncated copy is guaranteed to succeed and every cryptographic check passes. Four
      IMMUTABLE representations per document (ACQUIRED_SOURCE / PARSED_SOURCE / NORMALIZED_SOURCE / EXCERPT), a
      coverage_status BACKED BY A PRESERVATION RECORD against a retained EFetch acquisition (every abstract unit
      PRESERVED or MISSING), and the asymmetric rule: a positive claim may rest on a located excerpt; a negative
      claim only on a representation certified complete for the scope searched. (c) Four separate questions, four
      names: acquisition_complete / content_preserved / source_set_examined / outcome_understood -- never one badge.
      (d) Custody: the MedR original is producer-held off the package; stated with reacquisition route and expected
      digest, distinct from a licence restriction. (e) BagIt's words: this package is COMPLETE when required files
      are present and VALID when checksums verify -- neither means it contains complete scientific evidence.

THE SERVED SURFACE HAS ITS OWN CLOCK. Pages serves through a CDN; cache:'no-store' bypasses the browser cache only.
manifest.json and this file carry a `source` block (git blob ids of the served files + the commit that introduced
them; generating_commit NOT_RECORDED, stated) so a stale edge copy is checkable.

THE TRAP. `* text=auto eol=lf` is repo-wide and three held text exports carry CRLF; mirror paths carry -text and this
script refuses to mirror a path whose text attribute is not unset.

Usage:  python scripts/build_bundle.py <slug>            (idempotent; rerun after any rebuild; commit the rebuild first)
        python scripts/build_bundle.py <slug> --check    (verify only; exit 1 on any drift, write nothing)
Prerequisite: python scripts/acquire_bundle_evidence.py <slug>   (immutable acquisition objects under docs/acquisitions/)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import certificate  # noqa: E402
from harness import synth  # noqa: E402
from harness.target_endpoint import _components_from_text  # noqa: E402
from harness.canonical import canonical_json, review_core, sha256_text  # noqa: E402

SITE_ROOT = "https://mahmood726-cyber.github.io/meta-harness/"
REPO_URL = "https://github.com/mahmood726-cyber/meta-harness.git"
SCHEMA_VERSION = 3
FORMAT_REVISION = "3.11"
FORMAT_CHANGELOG = [
    "3.11 (2026-09-19, design memo): observed and registered estimand values are separate typed fields with no conversion (an unknown observed value is never filled from the specification); location and binding results are tagged states -- LOCATED / NOT_FOUND / AMBIGUOUS (carrying every competing candidate) / UNSUPPORTED_REPRESENTATION -- so the schema distinguishes 'binding failed' from 'binding not attempted'; admission means 'admissible for this exact analysis under this policy version and evidence version', never 'verified', and carries both versions; the verifier REVALIDATES on load -- regulatory strategy from the span, estimand bases from the source -- instead of trusting a deserialised state because it parses.",
    "3.10 (2026-09-19): statistical_input.ci_level -- the CI level the source STATES in the tuple's own clause (with basis) against the level the SE derivation ASSUMED (95%, z = 1.959963984540054); a MISMATCH (e.g. a 95.03% alpha-adjusted interval, EMPEROR-Preserved) is a refusal (P12_ci_level / CI_LEVEL_MISMATCH), never a relabel; UNSTATED is recorded as an assumption. Selection rule stated: by identity, never array order; ABSTAIN where the population cannot be resolved against the registered analysis set (DELIVER carries two PRIMARY composites).",
    "3.9 (2026-09-19): analysis_identity is no longer a set of bare values. Each of analysis_set, treatment_strategy, follow_up_window, comparator_direction and estimator is {value, basis, span, start, end, parent_representation} with basis STATED_IN_OWNING_EVIDENCE / REGISTERED_DEFAULT / UNRESOLVED (a default never renders as a statement); the review-target fallback ('trial end' on every row) is gone; stated fields also appear in spans[] with role analysis_method; regulatory candidates carry their (on-study)/(on-treatment) row label as a column_header span with offsets into the served text; the verifier refuses ESTIMAND_EVIDENCE_MISMATCH when a stated field does not reproduce at its offsets or a default carries a span.",
    "3.8 (2026-09-19, panel round 4 + 37-variant run): P9 rewritten to the panel's rule -- clause boundaries at sentence ends AND semicolons outside brackets; a target DEFINITION requires a definitional cue (component co-occurrence is not ownership); a clause carrying both a target and a non-target mention is AMBIGUOUS_ENDPOINT_BINDING, never a pass; P3 by NUMERIC equality (0.80 == 0.8 accepted; 0.96 vs 1.0 and 0.8 vs 0.84 refused); zero / one / many span occurrences are three states (SPAN_NOT_IN_SOURCE / located / SPAN_LOCATION_AMBIGUOUS, offsets pin one); estimand_evidence per row -- analysis_set, analysis_window, contrast, estimator each STATED with a located span and offsets, DEFAULT_REGISTERED when the held representation is silent, ESTIMAND_UNBOUND when the same source states two values; regulatory candidates carry strategy evidence (label / counts / unbound); the source stamp is content-addressed (blob ids computed from the working tree) and content_commit is informational (PENDING_COMMIT before the bytes are committed) so the stamp no longer needs its own commit to exist; L13/L14 stated.",
    "3.7 (2026-09-19): regulatory_facts[] -- every held regulatory fact with each candidate analysis of the same endpoint carried separately (tuple parsed from its own located span, analysis_identity with treatment strategy and precision, distinct analysis_identity_key), the selected analysis bound to the tuple the decision carries, and any source-internal discrepancy between representations of the SAME analysis recorded. Two authentic analyses of one endpoint in one document (ELIXA on-study 1.02 (0.89-1.18) 392/400 vs on-treatment 1.01 (0.87-1.17) 342/334) are distinguishable from the bundle alone, and the verifier refuses ANALYSIS_IDENTITY_MISMATCH when a tuple is bound to the wrong one.",
    "3.6 (2026-09-19): analysis_identity per row (analysis set, follow-up / treatment strategy, comparator direction, estimator) because endpoint identity is not estimand identity -- ELIXA's FDA document holds on-study 1.02 (0.89-1.18) and on-treatment 1.01 (0.87-1.17) for the same 3-point endpoint; spans[] with roles (result, definition, column_header, section_heading, analysis_method, footnote) so table-sourced evidence can be bound by more than one span instead of being refused; producer_label_scope states that the page's 'verified' (verify_pooled) checks the point estimate only while P3 checks estimate AND both limits.",
    "3.5 (2026-09-19): five verifier defects measured before/after on doctored sites; SPAN_NOT_IN_RECORD; positive refusals marked unevaluated (L12).",
    "3.4 (2026-09-19, panel run of verify_bundle.py against 21 mutations): P9_span_target_mention -- a POSITIVE binding requirement read from the tuple's own clause (target phrase, target definition, or a name bound to one), refusing ENDPOINT_INCOMPATIBLE on a recognised non-target mention and AMBIGUOUS_ENDPOINT_BINDING on no recognised mention (never a fallback to the definition span); eligibility read from the CERTIFIED families.json (trial_family_map_sha256) and named authoritative, the rendered copy cross-checked; selector resolved from the document_ref fragment; the verifier never crashes -- every refusal is a JSON verdict with a code; L11 states that acquisition digests inside the package can be rewritten together (H1c) and only a signed release, a third-party timestamp or a fetch at verification time closes it.",
    "3.3 (2026-09-19, admit_rows fail-open audit): UNBOUND_LEGACY surfaced as its own state -- a MIGRATION state, not an admissible one and not a refusal. binding_states lists every rendered row of every outcome with its binding class; P8_endpoint_bound joins the admission predicates and a row that fails only P8 by unbound_legacy gets final MIGRATION_STATE_UNBOUND_LEGACY (counted separately from admissible_rows); the verifier gains the same predicate, a `binding` corruption limb and named refusal codes.",
    "3.2 (2026-09-19, verifier panel round 2): extraction_objects_coverage states that verified_effects.json holds the primary outcome for SOUL alone (an override) and harms refusals for the rest -- the primary-outcome evidence chain for the other seven rows is records.json (records_file_sha256) -> analysis code blobs -> review.json (review_sha256), and every verification row names which; an explicit `anchor` block per document makes the retained EFetch XML mechanically comparable to the cached abstract (the only thing that can catch a self-consistent deletion), and the verifier gains --anchor live (re-fetch EFetch now and compare units: the external observation); a `limits` section prints what the bundle cannot establish, including the closed-list endpoint vocabulary.",
    "3.1 (2026-09-19, ninth audit): canonicalisation scheme published beside every canonical digest and both digest scopes of "
    "records.json stated (raw file vs canonical JSON -- same object, different procedures; a shared container digest across rows is "
    "correct, identity = container digest + deterministic selector); selector resolution rule stated and enforced (0 or >=2 matches "
    "refuse); per-evidence-object digest descriptors (subject / procedure / selector / representation the quotation must occur in); "
    "coordinate units on every location; endpoint_compatibility COMPATIBLE_WITH_DECLARED_VARIATION with per-trial "
    "undetermined_death_counted_as_cv; statistical_input per row (interval construction, SE reported vs derived, approximation "
    "named); heterogeneity precision statement; the verifier served at the path this file names, with its non-claims stated.",
    "3   (2026-09-19): recursive resolvability, four representations, preservation-backed coverage_status, per-row admission objects, stdlib verifier",
    "2   (2026-09-19): two identities per document, value_index span-match ladder, source block",
    "1   (2026-09-19): every certificate input served byte-identical; licence-held inputs declared",
]
CANONICALISATION = {
    "scheme": "Python json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')), encoded as UTF-8",
    "not": "RFC 8785 (JCS). Differences that matter: number formatting follows Python repr (e.g. 1e-05, 0.1), ensure_ascii=False keeps "
           "non-ASCII code points literal, key order is Python's default string sort (code point order).",
    "applies_to": "every digest whose digest_method says 'canonical JSON': records_file_sha256, retrieved_corpus_sha256, "
                  "retrieval_ledger_sha256, trial_family_map_sha256, rob_object_sha256, config_sha256, extraction_objects_sha256, "
                  "analysis_code_sha256, screening_ledger_sha256, review_sha256, release_sha256, and the AACT row_hash_method",
    "warning": "an auditor who assumes a different canonicalisation gets a mismatch and reports a defect that is not there; "
               "reproduce with the scheme above before concluding anything",
}
SELECTOR_RULE = {
    "scheme": "<container ref>#PMID-<identifier>",
    "resolution": "the UNIQUE element of container['records'] whose id_type == 'pmid' and str(id) == <identifier>",
    "zero_matches": "REFUSE",
    "two_or_more_matches": "REFUSE -- never silently take the first",
    "quotation_scope": "a quotation attributed to the selected record must occur in THAT record's designated representation "
                       "(PARSED_SOURCE = the record's 'abstract' string, or NORMALIZED_SOURCE derived from it), not merely somewhere in the container",
}
COORDINATES = {
    "unit": "Unicode code points of the decoded Python str (NOT bytes)",
    "range": "half-open [start, end): representation[start:end] == text",
    "encoding_for_digests": "UTF-8 encoding of the str; representation_sha256 is over those bytes",
    "note": "text position (code points) and data position (bytes) are not interchangeable; every location names its representation digest",
}
LIMITS = [
    {"id": "L1_self_consistency", "limit": "a package can be internally consistent and wrong: delete a sentence from a cached abstract, "
     "recompute every digest including both certificate scopes, and nothing INSIDE the package detects it (the SOUL defect as an experiment). "
     "Detection needs an anchor OUTSIDE the recomputable set: documents[*].anchor names the retained EFetch XML and how to compare; the verifier's "
     "--anchor live re-fetches from PubMed. Without one of those, coverage_status is a claim about two files that were packaged together."},
    {"id": "L2_closed_vocabulary", "limit": "endpoint mention vocabulary is a closed list in code (harness/target_endpoint.py). An unlisted non-target "
     "endpoint phrase can bind to the definition-span target mention and pass P4; 'died from cardiovascular causes' had to be added by hand after "
     "reading LEADER. This cannot be closed by extending the list; it is carried, not solved."},
    {"id": "L3_p4_not_rederivable", "limit": "P4 compares producer-canonicalised component tokens; an independent verifier cannot re-derive the mapping "
     "from the stated strings because the lexicon is code, not data."},
    {"id": "L4_container_level_identity", "limit": "P1 binds each row to the container digest + selector; a corruption of the container fails every row "
     "that depends on it (correct) and a per-record digest does not exist as a certified quantity."},
    {"id": "L5_extraction_object_coverage", "limit": "verified_effects.json, a certified extraction input, carries the primary outcome for one trial only; "
     "see extraction_objects_coverage for where the other rows' evidence chain lives. An auditor who follows extraction_objects_sha256 alone "
     "will find 1 of 9."},
    {"id": "L6_upstream_fidelity", "limit": "a retained acquisition and its digest establish what was saved, not that it came from the claimed "
     "publisher; the live anchor is one observation at one time, and PubMed records are revised (DateRevised is recorded)."},
    {"id": "L7_ci_to_se", "limit": "every SE is derived from a published CI under a Wald assumption; SOUL's interval is group-sequential-adjusted; "
     "appropriateness is NOT_ESTABLISHED and no sensitivity analysis exists."},
    {"id": "L8_fda_extraction", "limit": "FDA PDF -> text extraction tool is unrecorded and no page-level preservation record exists; those documents are UNKNOWN_COMPLETENESS."},
    {"id": "L10_admit_rows_fail_open", "limit": "the producer's target_endpoint.admit_rows admits a row with no endpoint class as UNBOUND_LEGACY "
     "(external audit: an authentic ELIXA 4-point row is refused when classified DIFFERENT_OUTCOME and admitted when the class is stripped). Two rendered "
     "harms rows carry it. The bundle counts them as a migration state; it cannot say whether the live build behaves as the audited code does, because "
     "target_endpoint.py is not pinned in the certificate and generating_commit is NOT_RECORDED."},
    {"id": "L11_coacquisition_rewrite", "limit": "if the cached abstract AND the retained acquisition XML are edited together and every digest including "
     "ACQUIRED_SOURCE.sha256_original is recomputed, the package is consistent and nothing inside it -- this bundle, its verifier, or any verifier "
     "reading only the package -- can detect it (panel H1c). Closing it needs the acquisition digests committed somewhere the bundle cannot rewrite: "
     "a signed release, a third-party timestamp, or a fetch at verification time (`verify_bundle.py --anchor live` is that fetch; it is one "
     "observation at one time)."},
    {"id": "L13_location_by_full_text_and_offsets", "limit": "spans are located by their FULL text (verbatim, or normalised under the published manifest) "
     "and recorded with code-point offsets, not by a prefix match; a prefix-locator's failure mode (two sentences sharing a long opening) does not "
     "apply, and a span that occurs more than once is SPAN_LOCATION_AMBIGUOUS unless offsets pin one occurrence -- measured by the B3 fixture."},
    {"id": "L14_verification_rows_source_pubmed_only", "limit": "verification_rows[] bind rows whose evidence is a PubMed record in records.json; a row "
     "whose evidence is a text artefact (FDA extraction) is not expressible as a verification row and is carried under regulatory_facts[] with its own "
     "identity binding. A fixture that sources a primary row from a text artefact will fail P1/P2 for that reason, not for a defect in the row."},
    {"id": "L9_production_path", "limit": "nothing here tests the producer's admission gate; no production falsification test has been executed by anyone."},
]
ANCHOR_HOWTO = ("parse ACQUIRED_SOURCE (EFetch XML) with any XML parser; take every //Abstract/AbstractText element in document order; for each, "
                "join its text nodes, collapse whitespace runs to one space and strip; that unit must be a substring of PARSED_SOURCE (the cached "
                "abstract string, whitespace-collapsed); after removing every located unit and its 'Label:' prefix the residual must be empty. "
                "All units present and no residual => PRESERVED; otherwise FAILURE. A checker that cannot do this comparison has no anchor.")
DIGEST_MISMATCH_POLICY = ("never resolve a digest mismatch by replacing the stored digest with the current one. Establish what changed "
                          "first: a formatting-only change and the deletion of a safety paragraph require opposite responses. A decision may "
                          "legitimately stay bound to an older retrievable source; what must never happen is silently substituting a new "
                          "source while keeping the old verification claim.")
Z975 = 1.959963984540054
GENERATED_FILES = ("review.json", "index.html", "CERTIFICATE.json", "REPRODUCTION.json")

# Inputs we hold but may not redistribute. PMC separates ACCESS from REUSE: the reference and the verification
# method are exposed, and the external-access dependency is declared. Anything not listed here is served.
NOT_IN_PACKAGE_LICENCE = {
    "cache/glp1-ra-mace-t2d/ft_27295427.txt": {
        "reason": "PMC author manuscript (nihms809153; N Engl J Med 2016, LEADER). PMC licence text: 'This file is "
                  "available for text mining. It may also be used consistent with the principles of fair use under "
                  "the copyright law.' -- a text-mining permission, not a redistribution licence; the publisher's "
                  "copyright applies to the article text.",
        "external_access_dependency": "PMC (open access to read; reuse restricted)",
        "obtain_from": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC4985288&retmode=xml",
        "identifiers": {"pmid": "27295427", "pmcid": "PMC4985288"},
    },
    "cache/glp1-ra-mace-t2d/ft_28910237.txt": {
        "reason": "PMC author manuscript (nihms-1856461; N Engl J Med 2017, EXSCEL). PMC licence text: 'This file is "
                  "available for text mining. It may also be used consistent with the principles of fair use under "
                  "the copyright law.' -- a text-mining permission, not a redistribution licence; the publisher's "
                  "copyright applies to the article text.",
        "external_access_dependency": "PMC (open access to read; reuse restricted)",
        "obtain_from": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC9792409&retmode=xml",
        "identifiers": {"pmid": "28910237", "pmcid": "PMC9792409"},
    },
}

SERVED_LICENCE = {
    "cache/glp1-ra-mace-t2d/comparator_fulltext.txt":
        "Giugliano 2021, Cardiovasc Diabetol, DOI 10.1186/s12933-021-01366-8; Crossref licence CC BY 4.0.",
    "outputs/handover/glp1_regulatory/":
        "US FDA review documents, briefing material and approved labelling: works of the United States "
        "Government / FDA-published, not subject to copyright restriction on redistribution.",
}

STALENESS_NOTICE = (
    "The served copy of this directory may lag the repository. GitHub Pages serves through a CDN: a fetch with "
    "cache:'no-store' bypasses the browser cache only, and two readers can hold different versions of the same URL "
    "at the same moment. Before treating these bytes as current, compute the git blob id of the review.json you "
    "hold (git hash-object review.json) and compare it with the blob at refs/heads/main "
    "(GET https://api.github.com/repos/mahmood726-cyber/meta-harness/contents/docs/reviews/<slug>/review.json?ref=main "
    "returns it as 'sha'); a mismatch means you are holding a stale edge copy or a superseded build."
)

VOCABULARY = {
    "representation_levels": {
        "ACQUIRED_SOURCE": "original response / PDF / XML bytes as received; sha256_original; created before any parsing",
        "PARSED_SOURCE": "complete text derived from the original by a named parser; sha256_parsed; parser identity and version",
        "NORMALIZED_SOURCE": "PARSED_SOURCE after narrowly defined, documented Unicode/whitespace transforms; sha256_normalized; transformation manifest",
        "EXCERPT": "a located span: parent representation + start/end offsets + exact text",
    },
    "operations": {
        "normalization": "narrowly defined documented transforms (whitespace, Unicode punctuation); listed by name",
        "selection": "choosing specified parts of a source (offsets into a parent representation)",
        "summarisation": "generating a new interpretation or compression; NOT a representation of the source and never labelled as one",
    },
    "coverage_status": {
        "COMPLETE_SOURCE": "full text; a preservation record shows every source unit PRESERVED or explicitly excluded",
        "COMPLETE_ABSTRACT": "abstract scope; a preservation record against a retained acquisition shows every abstract unit PRESERVED",
        "EXCERPT_ONLY": "a fragment or a summarisation; a preservation record shows units MISSING, or the object is not a complete unit of anything",
        "UNKNOWN_COMPLETENESS": "no retained acquisition to build a preservation record against",
    },
    "asymmetric_rule": "a POSITIVE claim (a result appears in the source) is allowed from a located authenticated excerpt; a NEGATIVE / "
                       "absence claim (an outcome is not reported) is allowed only from a representation whose coverage_status is "
                       "COMPLETE_* for the evidential scope searched. Positive extraction can be verified from a fragment; negative "
                       "extraction cannot. An unadjudicated deletion from a fixed source representation must not increase confidence "
                       "that an outcome was unreported.",
    "four_questions": {
        "acquisition_complete": "the response was received with no detected transfer failure (NOT: that the server returned the article rather than an abstract or a login page)",
        "content_preserved": "the representation was transformed without unexplained loss, unit by unit (NOT: that all relevant publications and supplements were acquired)",
        "source_set_examined": "the named documents and versions were assessed (NOT: that no additional report exists elsewhere)",
        "outcome_understood": "the interpretation is supported by context and adjudication (NOT: that a matching hash makes the clinical judgment true)",
    },
    "question_states": ["PASS", "FAIL", "NOT_RETAINED", "NOT_ASSESSED_BY_BUNDLE", "PRODUCER_ASSERTION"],
    "ci_level_rule": "the interval level the source states is part of the analysis identity; the SE derivation assumes 95%; a stated level that differs "
                     "(e.g. 95.03%, alpha-adjusted for interim looks) is CI_LEVEL_MISMATCH and the row is refused -- a mismatch is never resolved by relabelling",
    "selection_rule_for_multiple_candidates": "selection by identity (endpoint components, population / analysis set, treatment strategy, CI level), never by "
                                              "array order or first match; where the population cannot be resolved against the registered analysis set the "
                                              "answer is ABSTAIN, not the first primary (DELIVER NCT03619213 carries two PRIMARY composites, 0.82 (0.73-0.92) "
                                              "and 0.83 (0.73-0.95), differing by population)",
    "typed_states": {
        "LOCATED": "exactly one occurrence, or offsets pin one; offsets and parent representation present",
        "NOT_FOUND": "the search ran against the named representation and found nothing (distinct from not attempted)",
        "AMBIGUOUS": "more than one candidate; the competing candidates are carried (occurrence offsets, or the target/non-target mentions, or the two analyses)",
        "UNSUPPORTED_REPRESENTATION": "the source kind cannot be searched by this checker (e.g. a pooled row sourced from a text artefact); no claim is made",
        "NOT_ATTEMPTED": "the check was not run for this object (stated, never implied by a missing field)",
    },
    "observed_vs_registered": "every estimand field carries `observed` (from the row's own evidence, with span and offsets, or null) and `registered` "
                              "(the protocol's requirement) as SEPARATE typed values; an unknown observed value is NEVER filled from the registered one -- "
                              "otherwise the system manufactures compatibility by reading its own specification. Compatibility is established only when "
                              "observed equals registered, or is left open when observed is null.",
    "admission_meaning": "ADMISSIBLE means: admissible for THIS analysis (analysis_identity_key), under THIS policy_version (the predicate set) and THIS "
                         "evidence_version (the served bytes' digests). It never means 'verified' and it is not to be trusted on read-back: a verifier "
                         "revalidates every predicate from the served bytes.",
    "estimand_basis": {
        "STATED_IN_OWNING_EVIDENCE": "the value is read from a located span of the row's own evidence; span, start, end and parent_representation are present",
        "BOUND_VIA_COUNTS": "regulatory only: an unlabelled span whose event counts equal those of a labelled candidate inherits its strategy; the labelled span is cited",
        "BOUND_VIA_ROUNDING": "regulatory only: an unrounded tuple that rounds to a labelled candidate's tuple inherits its strategy; the labelled span is cited",
        "REGISTERED_DEFAULT": "the held representation is silent; the registered primary-analysis reading is applied and SAID to be a default -- never rendered as a statement; no span",
        "UNRESOLVED": "the same source states two values for the field (or names neither where it carries both analyses); the field cannot default",
    },
    "endpoint_compatibility_states": {
        "HOMOGENEOUS": "every pooled row states literally the same definition on the dimension",
        "COMPATIBLE_WITH_DECLARED_VARIATION": "rows differ on a dimension the protocol explicitly permits to vary; the variation is recorded per "
                                              "trial so an authorised difference stays distinguishable from literal identity and from an "
                                              "unauthorised difference",
        "HETEROGENEOUS_UNAUTHORISED": "rows differ on a dimension the protocol does not permit to vary",
    },
    "statistical_input": {
        "interval_construction": ["WALD", "GROUP_SEQUENTIAL_ADJUSTED", "EXACT", "UNSTATED_IN_HELD_REPRESENTATION"],
        "se_source": ["REPORTED_BY_SOURCE", "DERIVED_FROM_CI"],
        "rule": "a CI-to-SE conversion silently assumes the interval's construction method; where the construction is not Wald or is "
                "unstated, the appropriateness of the conversion is NOT_ESTABLISHED and is recorded, not resolved, here",
    },
    "resolvability_states": {
        "RESOLVED_IN_PACKAGE": "the referenced bytes are served by this package at the stated path",
        "RESOLVED_BODY_IN_ACQUISITIONS": "a digest-only reference whose body is served under acquisitions/ and re-hashes to the digest",
        "NOT_IN_PACKAGE_LICENCE": "held; not redistributed; reference + verification method + external-access dependency stated",
        "NOT_IN_PACKAGE_PRODUCER_HELD": "held by the producer off the package (size); reacquisition route + expected digest stated",
        "IN_REPOSITORY_NOT_PACKAGE": "the repository holds the file but this package does not serve it (not a certificate input)",
        "DIGEST_WITHOUT_BODY": "a reference that terminates in a digest with no retrievable body -- a promise, reported as such",
        "DANGLING": "a reference to nothing the package or the repository holds",
    },
    "span_roles": {
        "result": "the clause carrying the effect tuple",
        "definition": "the clause defining the endpoint the tuple belongs to",
        "column_header": "for a table cell: the column header that names the arm / statistic",
        "section_heading": "for a table cell: the table caption or parent heading that names the outcome and population",
        "analysis_method": "the clause stating the analysis set, model or censoring rule the tuple was computed under",
        "footnote": "a footnote that qualifies the cell (e.g. on-treatment, per-protocol, imputation)",
    },
    "span_binding_rule": "a value is bound by its spans[] jointly; an abstract-sourced value needs result + definition; a table-sourced value "
                         "needs result (the cell/row) + column_header + section_heading, plus analysis_method or footnote where the table carries one. "
                         "A single span is a partial binding for table evidence and must be recorded as such, not refused.",
    "producer_label_scope": {
        "verified": "the page's 'verified' / 'numerically verified' comes from the producer's verify_pooled, which checks that the POINT ESTIMATE occurs "
                    "in the committed source; it does NOT check the confidence limits. A row whose upper limit was replaced by another endpoint's genuine "
                    "limit would still carry that label. The bundle's P3_effect_tokens_in_span checks the estimate AND both limits against the clause.",
    },
    "analysis_identity_rule": "endpoint identity is not estimand identity: analysis set, treatment strategy (on-study / on-treatment), follow-up, "
                              "comparator direction and estimator are part of what a value IS; two authentic rows with identical components in one "
                              "document are told apart by analysis_identity_key, never by the endpoint alone",
    "binding_classes": {
        "BOUND": "endpoint_binding == named_endpoint_resolved_to_definition_span: the row's value is bound to a definition span of the target endpoint",
        "MIGRATION_STATE_UNBOUND_LEGACY": "the producer's target_endpoint.admit_rows returned admissible=True with verdict UNBOUND_LEGACY because the row has "
                                          "no endpoint class and fell through a narrow keyword check (fail-open demonstrated by an external audit with an "
                                          "authentic ELIXA 4-point row: classified DIFFERENT_OUTCOME it is refused; with the class stripped the same row is "
                                          "admitted). In this bundle such a row is NEITHER admissible NOR refused: table-sourced harms need multi-span binding "
                                          "(row, column header, parent heading, footnote) that does not exist yet, and blanket refusal would strip exactly the "
                                          "evidence that is hardest to recover. It is a migration state and is counted on its own.",
        "OTHER": "any other binding value; reported verbatim",
    },
    "admission_predicates": {
        "P10_estimand_evidence": "every STATED_IN_OWNING_EVIDENCE field reproduces at its offsets; no REGISTERED_DEFAULT carries a span (verifier-side)",
        "P11_registered_estimand": "a stated analysis set / treatment strategy agrees with the estimand the served protocol registers; UNRESOLVED fails; a default agrees by construction",
        "P12_ci_level": "the CI level stated in the tuple's clause equals the level the SE derivation assumed (95%); MISMATCH refuses; UNSTATED passes with the assumption recorded",
        "P9_span_target_mention": "POSITIVE binding: the tuple's own clause carries a target phrase, the target definition (>=2 canonical components), "
                                  "or a primary-outcome name bound by the row's definition span to the target; a recognised non-target mention refuses "
                                  "ENDPOINT_INCOMPATIBLE; no recognised mention refuses AMBIGUOUS_ENDPOINT_BINDING. Read from the span, not from metadata.",
        "P1_source_bytes": "sha256(served source bytes) == declared digest for the container of the representation the span is located in",
        "P2_span_located": "span text == representation[start:end] in the named representation (VERBATIM in PARSED_SOURCE, or in NORMALIZED_SOURCE with the transform manifest applied)",
        "P3_effect_tokens_in_span": "every number token of the effect object (estimate, CI bounds) occurs in the selected span",
        "P4_endpoint_components": "the row's component set equals the outcome's canonical component set",
        "P5_family_eligible": "the trial family's eligibility state == ELIGIBLE",
        "P6_no_unresolved_conflict": "no unresolved source conflict is recorded for the row's family",
        "P7_coverage_adequate_for_claim": "a positive claim: the excerpt is located (P2); a negative claim: coverage_status of the searched representation is COMPLETE_*",
        "P8_endpoint_bound": "endpoint_binding == named_endpoint_resolved_to_definition_span (an unbound_legacy row is a migration state, see binding_classes)",
        "ADMISSIBLE": "all predicates PASS",
        "MIGRATION_STATE_UNBOUND_LEGACY": "P8 is the ONLY failing predicate and the binding is unbound_legacy: not admissible, not refused, counted separately",
        "INADMISSIBLE": "any other failing predicate",
    },
}


# ----------------------------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------------------------

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha1(data: bytes, lf_normalise: bool = False) -> str:
    if lf_normalise:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def _text_attr(path: str) -> str:
    return _git("check-attr", "text", "--", path).rsplit(":", 1)[-1].strip()


def _rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


_WS = re.compile(r"\s+")
NORMALIZATION_MANIFEST = [
    {"step": "whitespace", "rule": "collapse every run of Unicode whitespace to one ASCII space; strip ends"},
    {"step": "unicode_punctuation", "rule": "U+00B7 middle dot -> '.'; U+2013/2014/2212/2010/2011 dashes -> '-'; "
                                            "U+00A0/2009/202F spaces -> ' '; U+2018/2019 -> \"'\"; U+201C/201D -> '\"'; "
                                            "U+2264 -> '<='; U+2265 -> '>='"},
]
_UNICODE_MAP = str.maketrans({
    "·": ".", "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-",
    " ": " ", " ": " ", " ": " ", "‘": "'", "’": "'", "“": '"', "”": '"',
    "≤": "<=", "≥": ">=",
})


def normalize(text: str) -> str:
    return _WS.sub(" ", text).strip().translate(_UNICODE_MAP)


def locate(span: str, hay: str) -> dict:
    """Mechanical ladder: where, if anywhere, does this rendered span occur in the document text? Offsets are into
    the named parent representation (PARSED_SOURCE verbatim, or NORMALIZED_SOURCE = normalize(PARSED_SOURCE))."""
    if not span:
        return {"match": "NO_SPAN"}
    i = hay.find(span)
    if i >= 0:
        return {"match": "VERBATIM", "parent": "PARSED_SOURCE", "start": i, "end": i + len(span)}
    s, h = normalize(span), normalize(hay)
    i = h.find(s)
    if i >= 0:
        steps = ["whitespace"] if _WS.sub(" ", span).strip() in _WS.sub(" ", hay) else [m["step"] for m in NORMALIZATION_MANIFEST]
        return {"match": "NORMALISED", "parent": "NORMALIZED_SOURCE", "start": i, "end": i + len(s), "normalisation": steps}
    return {"match": "NOT_LOCATED", "tried": [m["step"] for m in NORMALIZATION_MANIFEST]}


# ----------------------------------------------------------------------------------------------------------------
# certificate inputs (unchanged contract from v1)
# ----------------------------------------------------------------------------------------------------------------

def enumerate_inputs(slug: str, cert: dict) -> list[dict]:
    cache = ROOT / "cache" / slug
    protocol = ROOT / "protocols" / f"{slug}.md"
    if not protocol.exists():
        protocol = ROOT / "PREREGISTRATION_v2.md"
    entries = [
        {"ref": _rel(protocol), "role": "protocol_text_sha256",
         "digest_method": "sha256 of the file decoded as UTF-8 with universal newlines (bytes identical here: no CR present)",
         "declared": cert["protocol_text_sha256"]},
        {"ref": _rel(cache / "records.json"), "role": "records_file_sha256",
         "digest_method": "sha256 of canonical JSON (sorted keys, separators (',',':'), ensure_ascii=False, UTF-8) of the whole file; "
                          "['records'] alone feeds retrieved_corpus_sha256",
         "declared": cert["records_file_sha256"]},
        {"ref": _rel(cache / "retrieval_ledger.json"), "role": "retrieval_ledger_sha256",
         "digest_method": "sha256 of canonical JSON of the whole file; its [{source_id, query}] list, in order, feeds search_query_sha256",
         "declared": cert["retrieval_ledger_sha256"]},
        {"ref": _rel(cache / "families.json"), "role": "trial_family_map_sha256",
         "digest_method": "sha256 of canonical JSON", "declared": cert["trial_family_map_sha256"]},
        {"ref": _rel(cache / "rob2.json"), "role": "rob_object_sha256",
         "digest_method": "sha256 of canonical JSON", "declared": cert["rob_object_sha256"]},
        {"ref": _rel(ROOT / "topics" / f"{slug}.json"), "role": "config_sha256",
         "digest_method": "sha256 of canonical JSON", "declared": cert["config_sha256"]},
    ]
    for p in sorted(set(cache.glob("verified_*.json")) | set(cache.glob("*effect_type*.json"))):
        entries.append({"ref": _rel(p), "role": "extraction_objects_sha256",
                        "digest_method": "one member of the canonical ref-to-JSON map {ref: parsed JSON} whose canonical JSON is hashed",
                        "declared": None})
    for ref, blob in cert["analysis_code_blobs"].items():
        if blob != certificate.NOT_PRESENT:
            entries.append({"ref": ref, "role": "analysis_code_sha256",
                            "digest_method": "Git blob SHA-1 of LF-normalised bytes: sha1(b'blob <len>\\0' + bytes); the map of these feeds analysis_code_sha256",
                            "declared": blob})
    for h in cert["held_documents"]:
        entries.append({"ref": h["ref"], "role": "held_documents", "digest_method": "sha256 of exact file bytes", "declared": h["sha256"]})
    return entries


def recompute(entry: dict, data: bytes) -> str | None:
    role = entry["role"]
    if role == "protocol_text_sha256":
        return sha256_text(data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
    if role in ("records_file_sha256", "retrieval_ledger_sha256", "trial_family_map_sha256", "rob_object_sha256", "config_sha256"):
        return sha256_text(canonical_json(json.loads(data.decode("utf-8"))))
    if role == "analysis_code_sha256":
        return _git_blob_sha1(data, lf_normalise=True)
    if role == "held_documents":
        return _sha256(data)
    return None


# ----------------------------------------------------------------------------------------------------------------
# acquisitions (immutable; produced by scripts/acquire_bundle_evidence.py)
# ----------------------------------------------------------------------------------------------------------------

def load_acquisitions(slug: str) -> dict:
    base = ROOT / "docs" / "acquisitions" / slug
    out = {"pubmed": {}, "aact": {}, "manifests": [], "files": []}
    if not base.exists():
        return out
    for man in sorted(base.glob("*/ACQUISITION*.json")):
        m = _read_json(man)
        raw = man.read_bytes()
        out["manifests"].append({"path": _rel(man), "sha256": _sha256(raw), "bytes": len(raw), "kind": m.get("kind"),
                                 "source": m.get("source"), "acquisition_date": m.get("acquisition_date"),
                                 "origin_authentication": m.get("origin_authentication"), "relation_to_cache": m.get("relation_to_cache")})
        out["files"].append({"path": _rel(man), "sha256": _sha256(raw), "bytes": len(raw)})
        for e in m.get("entries", []):
            f = man.parent / e["file"]
            data = f.read_bytes()
            if _sha256(data) != e["sha256"]:
                raise ValueError(f"acquisition {f} does not hash to its manifest entry")
            out["files"].append({"path": _rel(f), "sha256": e["sha256"], "bytes": len(data)})
            if "identifier" in e and e["identifier"].get("pmid"):
                out["pubmed"][e["identifier"]["pmid"]] = {**e, "path": _rel(f), "manifest": _rel(man)}
            if e["file"] in ("rows.json", "review_source_references.json"):
                body = json.loads(data.decode("utf-8"))
                for table, rows in body.get("tables", {}).items():
                    for r in rows:
                        out["aact"][r["sha256"]] = {"table": table, "path": _rel(f), "snapshot": body.get("snapshot")}
    return out


def abstract_units(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    return [{"index": i, "label": a.get("Label"), "nlm_category": a.get("NlmCategory"),
             "text": _WS.sub(" ", "".join(a.itertext())).strip()}
            for i, a in enumerate(root.findall(".//Abstract/AbstractText"))]


def preservation_record(cached_abstract: str, units: list[dict]) -> dict:
    """Where did every unit of the acquired abstract go? PRESERVED (verbatim after whitespace collapse) or MISSING;
    plus any residual text in the cached copy that no unit accounts for."""
    cached = _WS.sub(" ", cached_abstract or "").strip()
    rows, resid = [], cached
    for u in units:
        ok = bool(u["text"]) and u["text"] in cached
        rows.append({"index": u["index"], "label": u["label"], "state": "PRESERVED" if ok else "MISSING",
                     "chars": len(u["text"]), "text_if_missing": (u["text"] if not ok else None)})
        if ok:
            resid = resid.replace(u["text"], "")
            if u["label"]:
                resid = resid.replace(u["label"] + ":", "")
    resid = _WS.sub(" ", resid).strip()
    n_p = sum(1 for r in rows if r["state"] == "PRESERVED")
    return {"units": rows, "preserved": n_p, "missing": len(rows) - n_p,
            "extra_chars_in_cached_not_in_acquired": len(resid), "extra_text": resid[:400] if resid else None,
            "verdict": "PRESERVED" if rows and n_p == len(rows) and not resid else "FAILURE"}


def _date_revised(xml_bytes: bytes) -> str | None:
    try:
        d = ET.fromstring(xml_bytes).find(".//MedlineCitation/DateRevised")
        return f"{d.findtext('Year')}-{d.findtext('Month')}-{d.findtext('Day')}" if d is not None else None
    except ET.ParseError:
        return None


# ----------------------------------------------------------------------------------------------------------------
# documents: four representations, preservation, coverage, four questions
# ----------------------------------------------------------------------------------------------------------------

def _regulatory_sources() -> dict:
    path = ROOT / "outputs" / "handover" / "glp1_regulatory" / "regulatory_sources_glp1.json"
    by_text, by_pdf = {}, {}
    if path.exists():
        for s in _read_json(path).get("sources", []):
            held = s.get("held") or {}
            t = held.get("extracted_text") or s.get("extracted_text_path")
            p = held.get("held_in_tree") or s.get("document_path")
            if t:
                by_text[t] = s
            if p:
                by_pdf[p] = s
    return {"by_text": by_text, "by_pdf": by_pdf}


def _not_retained(reason: str) -> dict:
    return {"state": "NOT_RETAINED", "note": reason}


def documents(slug: str, records: dict, acq: dict, art_by_ref: dict, reg: dict, review: dict) -> list[dict]:
    docs = []
    rec_ref = f"cache/{slug}/records.json"
    rec_art = art_by_ref[rec_ref]
    fetch_blob = _git("rev-parse", "HEAD:harness/fetch.py")
    displayed = {}
    for o in review.get("outcomes", []):
        for t in o.get("trials", []):
            pmid = str(t.get("id", "")).replace("PMID ", "")
            if t.get("endpoint_result_span"):
                displayed.setdefault(pmid, []).append({"outcome": o["name"], "span": t["endpoint_result_span"]})

    # -- PubMed records -------------------------------------------------------------------------------------------
    for r in records.get("records", []):
        pmid = str(r["id"])
        parsed_text = r.get("abstract") or ""
        norm_text = normalize(parsed_text)
        a = acq["pubmed"].get(pmid)
        entry = {"document_id": f"pubmed:{pmid}",
                 "identifiers": {"pmid": pmid, "doi": r.get("doi"), "nct": r.get("nct"), "title": r.get("title")},
                 "role_in_review": "pooled-row source (abstract)" if pmid in displayed else "screened record",
                 "representations": {}, "custody": "PACKAGE"}
        if a:
            xml_bytes = (ROOT / a["path"]).read_bytes()
            pres = preservation_record(parsed_text, abstract_units(xml_bytes))
            entry["representations"]["ACQUIRED_SOURCE"] = {
                "state": "RETAINED_POST_HOC", "ref": a["path"], "sha256_original": a["sha256"], "bytes": a["bytes"],
                "acquired_utc": a["acquired_utc"], "requested_url": a["requested_url"], "http_status": a["http_status"],
                "content_type": a["content_type"], "truncation": a["truncation"], "date_revised_in_record": _date_revised(xml_bytes),
                "note": "acquired 2026-09-19, AFTER the cache (records.json fetched_utc " + str(records.get("fetched_utc")) +
                        "); the acquisition the cache was projected from was not retained. A difference between this and "
                        "PARSED_SOURCE is recorded below as a discrepancy, not attributed -- except where DateRevised precedes "
                        "the cache date, in which case the record had not changed upstream between the two."}
            entry["preservation_record"] = pres
            if pres["verdict"] == "PRESERVED":
                coverage = "COMPLETE_ABSTRACT"
                basis = (f"all {pres['preserved']} AbstractText units of the retained EFetch acquisition are PRESERVED verbatim in "
                         "PARSED_SOURCE and PARSED_SOURCE carries no text outside them")
            else:
                coverage = "EXCERPT_ONLY"
                basis = (f"{pres['missing']} of {len(pres['units'])} AbstractText units of the retained acquisition are MISSING from PARSED_SOURCE"
                         + (f"; {pres['extra_chars_in_cached_not_in_acquired']} chars of PARSED_SOURCE occur in no acquired unit (rephrased or stitched text)"
                            if pres["extra_chars_in_cached_not_in_acquired"] else ""))
            q_acq = "PASS" if (a["http_status"] == 200 and not a["truncation"]["detected"] and a["truncation"]["well_formed_xml"]) else "FAIL"
            q_pres = "PASS" if pres["verdict"] == "PRESERVED" else "FAIL"
        else:
            entry["representations"]["ACQUIRED_SOURCE"] = _not_retained("no retained EFetch response for this record")
            coverage, basis = "UNKNOWN_COMPLETENESS", "no retained acquisition to build a preservation record against"
            q_acq = q_pres = "NOT_RETAINED"
        entry["representations"]["PARSED_SOURCE"] = {
            "state": "SERVED", "container_ref": rec_ref, "container_sha256": rec_art["sha256"], "selector": f"#PMID-{pmid} .abstract",
            "sha256_parsed": sha256_text(parsed_text), "chars": len(parsed_text),
            "parser": {"identity": "harness/fetch.py::_efetch -- AbstractText sections joined as 'Label: text' with single spaces",
                       "version": f"git blob {fetch_blob} of harness/fetch.py at the bundle's content commit"}}
        entry["representations"]["NORMALIZED_SOURCE"] = {
            "state": "DERIVED_BY_RULE", "sha256_normalized": sha256_text(norm_text), "chars": len(norm_text),
            "transformation_manifest": NORMALIZATION_MANIFEST, "note": "not stored; recomputed from PARSED_SOURCE with the manifest"}
        entry["representations"]["EXCERPT"] = [
            {"outcome": d["outcome"], "text": d["span"], "sha256_excerpt": sha256_text(d["span"]), **locate(d["span"], parsed_text)}
            for d in displayed.get(pmid, [])] or {"state": "NONE_DISPLAYED"}
        summarised = coverage == "EXCERPT_ONLY"
        entry["transforms"] = [
            {"from": "ACQUIRED_SOURCE", "to": "PARSED_SOURCE", "operation": "summarisation" if summarised else "selection+normalization",
             "detail": ("the cached text is neither a normalization nor a selection of the acquired units (see preservation_record); "
                        "it is a compression/rephrasing and is labelled as such") if summarised else "XML AbstractText nodes -> labelled text"},
            {"from": "PARSED_SOURCE", "to": "NORMALIZED_SOURCE", "operation": "normalization", "detail": NORMALIZATION_MANIFEST},
            {"from": "PARSED_SOURCE|NORMALIZED_SOURCE", "to": "EXCERPT", "operation": "selection", "detail": "offsets recorded per excerpt"}]
        entry["coverage_status"] = {"value": coverage, "scope": "abstract", "basis": basis, "backed_by": "preservation_record" if a else None}
        entry["anchor"] = ({"anchors": "PARSED_SOURCE (the cached abstract in records.json) against ACQUIRED_SOURCE (retained EFetch XML)",
                            "acquired_ref": a["path"], "acquired_sha256": a["sha256"],
                            "external": {"uri": a["requested_url"], "note": "re-fetch and compare units to BOTH the retained XML and the cached abstract; "
                                                                             "record DateRevised; a difference is a discrepancy to record, not to attribute"},
                            "how_to_compare": ANCHOR_HOWTO,
                            "what_it_catches": "a deletion or rephrasing in the cached abstract even when every digest in the package has been recomputed to match",
                            "what_it_cannot_catch": "an alteration applied to the retained XML as well (only the external re-fetch can), or a record PubMed itself has revised"}
                           if a else {"anchors": None, "note": "no retained acquisition: this document has no anchor and its coverage is UNKNOWN_COMPLETENESS"})
        entry["which_representation"] = {
            "hashed_by_certificate": f"the container file {rec_ref} (records_file_sha256 / retrieved_corpus_sha256): PARSED_SOURCE for every record at once",
            "searched_by_page": "PARSED_SOURCE (the page's verify_basis 'effect present in committed source' is a search of this file); "
                                "where the displayed span is NORMALISED the page compared after normalization",
            "displayed_by_page": "EXCERPT as rendered (representations.EXCERPT[*].match is VERBATIM or NORMALISED relative to PARSED_SOURCE)"}
        entry["four_questions"] = {
            "acquisition_complete": {"state": q_acq, "basis": "HTTP 200, Content-Length == received, well-formed XML" if a else "no retained acquisition"},
            "content_preserved": {"state": q_pres, "basis": "preservation_record" if a else "no retained acquisition"},
            "source_set_examined": {"state": "NOT_ASSESSED_BY_BUNDLE", "basis": "lives in retrieval_ledger.json and review.json['screening']; not re-assessed here"},
            "outcome_understood": {"state": "PRODUCER_ASSERTION", "basis": "the page's endpoint_binding / adjudication fields are the producer's; carried in verification_rows, not independently adjudicated"}}
        docs.append(entry)

    # -- comparator full text -------------------------------------------------------------------------------------
    cref = f"cache/{slug}/comparator_fulltext.txt"
    if cref in art_by_ref:
        text = (ROOT / cref).read_text(encoding="utf-8", errors="replace")
        docs.append({
            "document_id": "comparator:PMID " + str(records.get("comparator_pmid")),
            "identifiers": {"pmid": str(records.get("comparator_pmid")), "oa_url": (records.get("comparator_oa") or {}).get("oa_url")},
            "role_in_review": "comparator meta-analysis (parity benchmark)",
            "representations": {
                "ACQUIRED_SOURCE": _not_retained("the PMC XML for the comparator was not retained"),
                "PARSED_SOURCE": {"state": "SERVED", "ref": cref, "sha256_parsed": art_by_ref[cref]["sha256"], "bytes": art_by_ref[cref]["bytes"],
                                  "parser": {"identity": "harness.fetch._pmc_fulltext -> harness/fulltext.py parse_pmc_xml/combined_text (JATS XML -> body prose + table rows)",
                                             "version": "harness/fulltext.py at the content commit"}},
                "NORMALIZED_SOURCE": {"state": "DERIVED_BY_RULE", "sha256_normalized": sha256_text(normalize(text)), "transformation_manifest": NORMALIZATION_MANIFEST},
                "EXCERPT": {"state": "NONE_DISPLAYED_BY_THIS_BUNDLE", "note": "comparator_panel spans are the producer's; not re-located here"}},
            "transforms": [{"from": "ACQUIRED_SOURCE", "to": "PARSED_SOURCE", "operation": "selection+normalization", "detail": "JATS body + tables -> prose"}],
            "coverage_status": {"value": "UNKNOWN_COMPLETENESS", "scope": "full text", "basis": "no retained acquisition; cannot be checked unit by unit", "backed_by": None},
            "custody": "PACKAGE",
            "which_representation": {"hashed_by_certificate": "PARSED_SOURCE (held_documents)", "searched_by_page": "PARSED_SOURCE", "displayed_by_page": "producer spans"},
            "four_questions": {"acquisition_complete": {"state": "NOT_RETAINED"}, "content_preserved": {"state": "NOT_RETAINED"},
                               "source_set_examined": {"state": "NOT_ASSESSED_BY_BUNDLE"}, "outcome_understood": {"state": "PRODUCER_ASSERTION"}}})

    # -- FDA documents (PDF original + text export) ----------------------------------------------------------------
    for text_ref, s in reg["by_text"].items():
        held = s.get("held") or {}
        pdf_ref = held.get("held_in_tree") or s.get("document_path")
        pdf_art = art_by_ref.get(pdf_ref) if pdf_ref else None
        txt_art = art_by_ref.get(text_ref)
        if pdf_art:
            acquired = {"state": "SERVED", "ref": pdf_ref, "sha256_original": pdf_art["sha256"], "bytes": pdf_art["bytes"],
                        "acquired_from": s.get("query"), "fetched_utc": s.get("fetched_utc"),
                        "sha256_recorded_at_acquisition": s.get("document_sha256"),
                        "acquisition_digest_matches_served_bytes": s.get("document_sha256") == pdf_art["sha256"]}
            custody = "PACKAGE"
        else:
            acquired = {"state": "NOT_IN_PACKAGE_PRODUCER_HELD", "sha256_original": s.get("document_sha256"),
                        "bytes": int(s["document_bytes"]) if s.get("document_bytes") else None, "pages": s.get("pages"),
                        "acquired_from": s.get("query"), "fetched_utc": s.get("fetched_utc"),
                        "custody": "producer-held off the package (size); the source manifest records the archive location",
                        "reacquire": "fetch the document at acquired_from (accessdata.fda.gov); sha256 of the bytes must equal sha256_original; "
                                     "then PARSED_SOURCE below is checkable against it",
                        "statement": "this package is NOT a complete producer-held binary archive: this original is described, digested and "
                                     "reacquirable, but its bytes are not served"}
            custody = "PARTIAL: original off-package (producer-held), text export in package"
        text = (ROOT / text_ref).read_bytes().decode("utf-8", "replace") if txt_art else ""
        docs.append({
            "document_id": "fda:" + s.get("source_id", text_ref),
            "identifiers": {"source_id": s.get("source_id"), "kind": s.get("kind"), "url": (s.get("query") or "").split(" ")[0]},
            "role_in_review": "regulatory source (level 2)",
            "representations": {
                "ACQUIRED_SOURCE": acquired,
                "PARSED_SOURCE": {"state": "SERVED", "ref": text_ref, "sha256_parsed": txt_art["sha256"] if txt_art else None,
                                  "bytes": txt_art["bytes"] if txt_art else None, "sha256_recorded_at_extraction": s.get("extracted_text_sha256"),
                                  "parser": {"identity": "PDF -> text; the extraction tool is NOT recorded in regulatory_sources_glp1.json (stated, not guessed)", "version": None}},
                "NORMALIZED_SOURCE": {"state": "DERIVED_BY_RULE", "sha256_normalized": sha256_text(normalize(text)), "transformation_manifest": NORMALIZATION_MANIFEST},
                "EXCERPT": [{"trial": d.get("trial"), "outcome": d.get("outcome"), "decision": d.get("decision"), "span_page_pdf": d.get("span_page_pdf"),
                             "text": d.get("span"), **locate(d.get("span") or "", text)} for d in s.get("decisions", []) if d.get("span")]},
            "transforms": [{"from": "ACQUIRED_SOURCE", "to": "PARSED_SOURCE", "operation": "unrecorded", "detail": "PDF text extraction; tool unrecorded; no per-page preservation record exists"}],
            "coverage_status": {"value": "UNKNOWN_COMPLETENESS", "scope": "full document", "basis": "no page-by-page preservation record of the text extraction against the PDF", "backed_by": None},
            "custody": custody,
            "which_representation": {"hashed_by_certificate": "both: ACQUIRED_SOURCE (held/*.pdf) where served, and PARSED_SOURCE (*.pdf.txt)",
                                     "searched_by_page": "PARSED_SOURCE", "displayed_by_page": "producer spans (regulatory_sources_glp1.json decisions[*].span)"},
            "four_questions": {"acquisition_complete": {"state": "PASS" if pdf_art and acquired.get("acquisition_digest_matches_served_bytes") else "NOT_ASSESSED_BY_BUNDLE",
                                                        "basis": "acquisition digest recorded by the acquiring agent equals served bytes" if pdf_art else "original off-package"},
                               "content_preserved": {"state": "NOT_ASSESSED_BY_BUNDLE", "basis": "no preservation record for the PDF->text extraction"},
                               "source_set_examined": {"state": "NOT_ASSESSED_BY_BUNDLE"}, "outcome_understood": {"state": "PRODUCER_ASSERTION"}},
            "span_location_check_owed_by_producer": s.get("span_location_check")})

    # -- PMC full texts (licence-restricted) -----------------------------------------------------------------------
    for ref, lic in NOT_IN_PACKAGE_LICENCE.items():
        a = art_by_ref.get(ref)
        if not a:
            continue
        docs.append({
            "document_id": "pmc:" + lic["identifiers"]["pmcid"], "identifiers": lic["identifiers"],
            "role_in_review": "full text (PMC author manuscript) held for span checks",
            "representations": {
                "ACQUIRED_SOURCE": {"state": "NOT_IN_PACKAGE_LICENCE", "ref_in_repository": ref, "sha256_original": a["sha256"], "bytes": a["bytes"],
                                    "acquisition_digest_recorded": False, "obtain_from": lic["obtain_from"],
                                    "verification_method": "fetch obtain_from; sha256 of the response must equal sha256_original (PMC may re-render; a mismatch is a discrepancy to record)",
                                    "external_access_dependency": lic["external_access_dependency"]},
                "PARSED_SOURCE": _not_retained("not derived by the bundle"), "NORMALIZED_SOURCE": _not_retained("not derived by the bundle"),
                "EXCERPT": {"state": "NONE_DISPLAYED_BY_THIS_BUNDLE"}},
            "transforms": [],
            "coverage_status": {"value": "UNKNOWN_COMPLETENESS", "scope": "full text", "basis": "no acquisition digest was taken; structural completeness of the stored XML not assessed", "backed_by": None},
            "custody": "REPOSITORY_NOT_PACKAGE (licence)",
            "which_representation": {"hashed_by_certificate": "ACQUIRED_SOURCE bytes (held_documents)", "searched_by_page": "unknown to the bundle", "displayed_by_page": "none"},
            "four_questions": {"acquisition_complete": {"state": "NOT_ASSESSED_BY_BUNDLE"}, "content_preserved": {"state": "NOT_ASSESSED_BY_BUNDLE"},
                               "source_set_examined": {"state": "NOT_ASSESSED_BY_BUNDLE"}, "outcome_understood": {"state": "PRODUCER_ASSERTION"}}})
    return docs


# ----------------------------------------------------------------------------------------------------------------
# verification rows (primary pool) and absence claims
# ----------------------------------------------------------------------------------------------------------------

def resolve_selector(records: dict, pmid: str) -> dict:
    """Apply SELECTOR_RULE: the unique record with id_type pmid and id == pmid. Raises on 0 or >=2 matches."""
    matches = [r for r in records.get("records", []) if str(r.get("id_type", "pmid")).lower() == "pmid" and str(r.get("id")) == str(pmid)]
    if len(matches) != 1:
        raise ValueError(f"selector #PMID-{pmid} resolves to {len(matches)} records; the rule refuses anything but exactly one")
    return matches[0]


_UNDETERMINED = re.compile(r"(undetermined|unknown)[^.;]{0,40}(cause|death)|death[^.;]{0,60}(undetermined|unknown)", re.I)


def undetermined_death_field(definition_span) -> dict:
    """Per-trial `undetermined_death_counted_as_cv` read mechanically from the trial's OWN definition span: 'yes' when the
    span says undetermined/unknown-cause death is counted; 'unstated' otherwise. Never 'no' from an abstract that is silent."""
    m = _UNDETERMINED.search(definition_span or "")
    return {"value": "yes" if m else "unstated", "evidence": m.group(0) if m else None,
            "basis": "trial's own endpoint_definition_span" if definition_span else "no definition span held"}


def statistical_input(t: dict, pmid: str, clause: str | None = None) -> dict:
    """What the CI-to-SE conversion assumed for this row, and whether that assumption is established."""
    se = ((t.get("study_effect") or {}).get("standard_error"))
    rec = {
        "ci_level": ci_level_record(clause, se, t.get("ci_low"), t.get("ci_high")),
        "se_source": "DERIVED_FROM_CI",
        "approximation": f"Wald: SE_log = (ln ci_high - ln ci_low) / (2 * {Z975}) -- assumes a normal-theory interval",
        "se_log_used": se,
        "interval_construction": "UNSTATED_IN_HELD_REPRESENTATION",
        "construction_basis": "the held representation (abstract) does not state how the interval was constructed",
        "approximation_appropriate": "NOT_ESTABLISHED",
        "standing_rule": "do not replace a source's adjusted interval with an unadjusted analysis to obtain a convenient SE; obtain a "
                         "compatible source-reported estimate/SE pair, or justify the approximation with a sensitivity analysis",
    }
    if pmid == "40162642":
        rec.update({
            "interval_construction": "GROUP_SEQUENTIAL_ADJUSTED",
            "construction_basis": "ninth external audit, from the publication's Statistical Analysis section (PDF p.3): primary HR, CI and "
                                  "P were adjusted for the group-sequential design using likelihood-ratio ordering. NOT verified by this "
                                  "bundle against a held representation (the full text is not held); recorded as an external observation",
            "approximation_appropriate": "NOT_ESTABLISHED -- the Wald conversion assumes a construction the source did not use; no "
                                         "numerical distortion of the pool has been quantified; sensitivity analysis NOT_DONE (recorded, not resolved)",
        })
    return rec


# ---- endpoint binding (P9): a POSITIVE requirement read from the tuple's own clause --------------------------------
TARGET_PHRASES = ("major adverse cardiovascular", "mace")
PRIMARY_NAMES = ("primary outcome", "primary composite outcome", "primary-outcome", "primary end point", "primary endpoint",
                 "primary composite end point", "primary cardiovascular end-point", "primary cardiovascular end point",
                 "primary cardiovascular endpoint", "primary cardiovascular outcome")
DEFINITION_CUES = ("composite", "first occurrence", "defined as", "consisting of", "consisted of", "major adverse", "mace",
                   "primary outcome", "primary end point", "primary endpoint", "primary composite", "primary cardiovascular")
COMPONENT_WORDS = {"CARDIOVASCULAR_DEATH": ("cardiovascular death", "death from cardiovascular", "cardiovascular causes", "cardiovascular mortality"),
                   "MYOCARDIAL_INFARCTION": ("myocardial infarction",), "STROKE": ("stroke",)}
NON_TARGET_MENTIONS = ("death from any cause", "all-cause mortality", "all-cause death", "any-cause death", "hospitalization for heart failure",
                       "hospitalisation for heart failure", "heart failure", "kidney", "renal", "nephropathy", "retinopathy", "amputation",
                       "pancreatitis", "adverse event", "serious adverse", "gastrointestinal", "hypoglyc", "unstable angina")
_NUM = re.compile(r"\d+(?:\.\d+)?")


_STAT_CONTINUATION = re.compile(r"\s*(?:95\s*%|CI\b|P\s*[=<>]|p\s*[=<>]|HR\b|hazard ratio)")   # a ';' inside a statistical tuple does not end a clause


def clauses(span):
    """Clause boundaries: sentence ends (period + space + capital) AND semicolons OUTSIDE brackets."""
    out, buf, depth = [], [], 0
    text = span or ""
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        buf.append(ch)
        if depth == 0 and ch == ";" and not _STAT_CONTINUATION.match(text, i + 1):
            out.append("".join(buf).strip()); buf = []
        elif depth == 0 and ch == "." and i + 2 < len(text) and text[i + 1] == " " and text[i + 2].isupper():
            out.append("".join(buf).strip()); buf = []
        i += 1
    if "".join(buf).strip():
        out.append("".join(buf).strip())
    return [c for c in out if c]


def clause_numbers(clause):
    return [float(x) for x in _NUM.findall(normalize(clause))]


def clause_with_effect(span, values):
    """The clause whose own numbers contain every value of the tuple -- by NUMERIC equality, never substring."""
    vals = [float(v) for v in values]
    for c in clauses(span):
        nums = clause_numbers(c)
        if all(any(abs(v - n) < 1e-12 for n in nums) for v in vals):
            return c
    return None


def span_target_mention(span, values, definition_span, canonical_components):
    """POSITIVE binding. The tuple's own clause must carry a TARGET mention: a target phrase, a target DEFINITION (>= 2 canonical
    components AND a definitional cue -- co-occurrence of component words is not ownership), or a primary-outcome name that the
    row's definition span binds to the target. A clause that ALSO carries a non-target mention (or a lone component) is
    AMBIGUOUS_ENDPOINT_BINDING, never a pass; a clause with only a non-target mention is ENDPOINT_INCOMPATIBLE; a clause with no
    recognised mention is AMBIGUOUS_ENDPOINT_BINDING. Never a fallback to the definition span."""
    clause = clause_with_effect(span, values)
    if clause is None:
        return {"state": "AMBIGUOUS_ENDPOINT_BINDING", "mention": "no clause of the span carries the tuple's numbers by numeric equality",
                "witness": span, "clause": None}
    c, d = normalize(clause).lower(), normalize(definition_span or "").lower()
    named = lambda text: sorted(k for k, ws in COMPONENT_WORDS.items() if any(w in text for w in ws))
    comps_c, comps_d = named(c), named(d)
    canon = set(canonical_components or [])
    primary_named = any(n in c for n in PRIMARY_NAMES)
    cue = any(k in c for k in DEFINITION_CUES)
    target = []
    if any(ph in c for ph in TARGET_PHRASES):
        target.append({"kind": "target phrase", "witness": [ph for ph in TARGET_PHRASES if ph in c]})
    if len(set(comps_c) & canon) >= 2 and cue:
        target.append({"kind": "target definition in clause", "witness": comps_c})
    if primary_named and "primary" in d and len(set(comps_d) & canon) >= 2:
        target.append({"kind": "primary-outcome name bound by the row's definition span", "witness": [n for n in PRIMARY_NAMES if n in c]})
    non_target = [m for m in NON_TARGET_MENTIONS if m in c]
    lone_component = (len(comps_c) == 1 and not primary_named and not target)
    if target and (non_target or lone_component):
        return {"state": "AMBIGUOUS_ENDPOINT_BINDING", "mention": "clause carries BOTH a target mention and a non-target mention",
                "witness": {"target": target, "non_target": non_target or comps_c}, "clause": clause}
    if target:
        return {"state": "PASS", "mention": target[0]["kind"], "witness": target[0]["witness"], "clause": clause}
    if non_target or lone_component:
        return {"state": "ENDPOINT_INCOMPATIBLE", "mention": "recognised NON-target mention bound to the target claim",
                "witness": non_target or comps_c, "clause": clause}
    return {"state": "AMBIGUOUS_ENDPOINT_BINDING", "mention": "no recognised target mention in the tuple's own clause", "witness": clause, "clause": clause}


def locate_all(span, hay):
    """Zero / one / many are three states. Returns match kind, occurrence count and the first offset."""
    if not span:
        return {"match": "NO_SPAN", "occurrences": 0}
    n = hay.count(span)
    if n:
        i = hay.find(span)
        return {"match": "VERBATIM", "parent": "PARSED_SOURCE", "start": i, "end": i + len(span), "occurrences": n}
    s, h = normalize(span), normalize(hay)
    n = h.count(s)
    if n:
        i = h.find(s)
        return {"match": "NORMALISED", "parent": "NORMALIZED_SOURCE", "start": i, "end": i + len(s), "occurrences": n}
    return {"match": "NOT_LOCATED", "occurrences": 0}


# ---- estimand evidence: analysis set / window / contrast / estimator WITH a span, or an explicit default ----------
_ESTIMAND = {
    "analysis_set": [(r"intention[- ]to[- ]treat|\bITT\b", "intention-to-treat"), (r"per[- ]protocol", "per-protocol"),
                     (r"as[- ]treated", "as-treated"), (r"on[- ]treatment (?:population|analysis)", "on-treatment population")],
    "analysis_window": [(r"on[- ]treatment", "on-treatment"), (r"on[- ]study|in[- ]trial", "on-study"),
                        (r"time[- ]to[- ](?:first[- ])?event|time to (?:the )?first (?:occurrence|event)", "time-to-first-event (treatment-policy)"),
                        (r"median follow-up (?:of|was) [\d.]+ (?:years|months)|(?:over|during) a median (?:follow-up )?of [\d.]+ (?:years|months)", "follow-up stated")],
    "estimator": [(r"hazard ratio", "hazard ratio"), (r"(?-i:\bHR\b)", "hazard ratio"), (r"odds ratio", "odds ratio"), (r"(?-i:\bOR\b)", "odds ratio"),
                  (r"relative risk|risk ratio", "risk ratio"), (r"(?-i:\bRR\b)", "risk ratio"), (r"rate ratio|incidence rate ratio", "rate ratio")],
}
DEFAULT_REGISTERED = {"analysis_set": "intention-to-treat (registered primary-analysis default)",
                      "analysis_window": "on-study, treatment-policy (registered primary-analysis default)",
                      "contrast": "intervention vs placebo; effect < 1 favours intervention (topic registration)",
                      "estimator": "UNSTATED"}


def _sentence_at(text, pos):
    s = text.rfind(". ", 0, pos) + 1
    e = text.find(". ", pos)
    e = len(text) if e < 0 else e + 1
    return s, e


def estimand_evidence(parsed, result_clause):
    """Per field: STATED (value + located sentence with code-point offsets in PARSED_SOURCE), DEFAULT_REGISTERED (no statement in the
    held representation), or ESTIMAND_UNBOUND (the same source states >= 2 differing values for the field)."""
    out = {}
    for field, pats in _ESTIMAND.items():
        hits = []
        for rx, value in pats:
            for m in re.finditer(rx, parsed, re.I):
                s, e = _sentence_at(parsed, m.start())
                hits.append({"value": value, "matched": m.group(0), "start": s, "end": e, "span": parsed[s:e].strip()})
        values = {h["value"] for h in hits}
        if field == "analysis_window":
            strategies = {v for v in values if v in ("on-treatment", "on-study")}
            if len(strategies) >= 2:
                out[field] = {"state": "UNRESOLVED", "values": sorted(values), "evidence": hits[:4],
                              "rule": "the same source states two strategies for the analysis; the field cannot default"}
                continue
            if "on-treatment" in values and "on-study" not in values:
                pick = next(h for h in hits if h["value"] == "on-treatment")
                out[field] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": "on-treatment", **{k: pick[k] for k in ("start", "end", "span")}, "parent_representation": "PARSED_SOURCE"}
                continue
            prefer = [h for h in hits if h["value"] == "on-study"] or [h for h in hits if h["value"].startswith("time-to")] or [h for h in hits if h["value"] == "follow-up stated"]
            if prefer:
                pick = prefer[0]
                out[field] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": pick["value"], **{k: pick[k] for k in ("start", "end", "span")}, "parent_representation": "PARSED_SOURCE",
                              "also_stated": sorted(values - {pick["value"]})}
            else:
                out[field] = {"state": "REGISTERED_DEFAULT", "value": DEFAULT_REGISTERED[field]}
            continue
        if len(values) >= 2:
            out[field] = {"state": "UNRESOLVED", "values": sorted(values), "evidence": hits[:4]}
        elif hits:
            pick = hits[0]
            out[field] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": pick["value"], **{k: pick[k] for k in ("start", "end", "span")}, "parent_representation": "PARSED_SOURCE"}
        else:
            out[field] = {"state": "REGISTERED_DEFAULT", "value": DEFAULT_REGISTERED[field]}
    rc = result_clause or ""
    if "placebo" in rc.lower():
        i = parsed.find(rc)
        if i >= 0:
            out["contrast"] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": "vs placebo (named in the result clause)", "span": rc,
                               "start": i, "end": i + len(rc), "parent_representation": "PARSED_SOURCE"}
        else:   # the clause exists only after normalisation (e.g. Lancet middle dots): offsets in NORMALIZED_SOURCE coordinates
            nrc, npar = normalize(rc), normalize(parsed)
            j = npar.find(nrc)
            out["contrast"] = {"state": "STATED_IN_OWNING_EVIDENCE", "value": "vs placebo (named in the result clause)", "span": nrc,
                               "start": j if j >= 0 else None, "end": (j + len(nrc)) if j >= 0 else None, "parent_representation": "NORMALIZED_SOURCE"}
    else:
        out["contrast"] = {"state": "REGISTERED_DEFAULT", "value": DEFAULT_REGISTERED["contrast"]}
    return out


# ---- CI level: the level the source STATES vs the level the derivation ASSUMED --------------------------------------
_CI_PCT = re.compile(r"(\d{2}(?:[.\u00b7]\d+)?)\s*%\s*(?:confidence interval|CI\b|credible interval)", re.I)
Z_ASSUMED_BY_DERIVATION = 1.959963984540054   # the harness derives SE_log with the 97.5th normal quantile, i.e. a 95% two-sided interval


def inverse_normal(p):
    """Phi^-1(p) by bisection on math.erf; standard library only; |error| < 1e-12."""
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0))) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def stated_ci_pct(clause):
    """The CI level the tuple's own clause states, e.g. '95% CI', '95.03% confidence interval'; None when unstated."""
    if not clause:
        return None
    m = _CI_PCT.search(normalize(clause))
    return float(m.group(1).replace("\u00b7", ".")) if m else None


def ci_level_record(clause, se_used, ci_low, ci_high):
    """source_ci_pct with its basis, the z the derivation assumed, the z the stated level implies, and MATCH / MISMATCH / UNSTATED.
    A mismatch is a refusal, not a relabel: an SE derived with z(95%) from a 95.03% interval is wrong, and silently so."""
    pct = stated_ci_pct(clause)
    rec = {"assumed_ci_pct": 95.0, "z_assumed_by_derivation": Z_ASSUMED_BY_DERIVATION}
    if pct is None:
        rec.update({"source_ci_pct": None, "basis": "UNSTATED", "level_agreement": "UNSTATED",
                    "note": "the tuple's clause does not state the interval's level; the derivation assumed 95% and that assumption is recorded, not verified"})
        return rec
    z_stated = inverse_normal(1.0 - (1.0 - pct / 100.0) / 2.0)
    rec.update({"source_ci_pct": pct, "basis": "STATED_IN_OWNING_EVIDENCE", "z_for_stated_level": z_stated,
                "level_agreement": "MATCH" if abs(pct - 95.0) < 1e-9 else "MISMATCH"})
    if ci_low and ci_high and se_used:
        rec["se_log_at_stated_level"] = (math.log(ci_high) - math.log(ci_low)) / (2.0 * z_stated)
        rec["se_log_used"] = se_used
    return rec


def _tokens(x) -> list[str]:
    if x is None:
        return []
    s = repr(float(x)) if isinstance(x, (int, float)) else str(x)
    return [s[:-2] if s.endswith(".0") else s]


def _extraction_entries(slug: str) -> dict:
    """{pmid: [(file, outcome, provenance, has_effect)]} across the certified extraction objects."""
    out = {}
    for name in ("verified_effects.json", "verified_arms.json"):
        path = ROOT / "cache" / slug / name
        if not path.exists():
            continue
        for pmid, e in _read_json(path).items():
            for x in (e if isinstance(e, list) else [e]):
                out.setdefault(str(pmid), []).append({"file": f"cache/{slug}/{name}", "outcome": x.get("outcome"),
                                                      "provenance": x.get("provenance"), "has_effect": "effect" in x})
    return out


def extraction_objects_coverage(slug: str, review: dict, cert: dict) -> dict:
    """What the certified extraction objects (extraction_objects_sha256) actually cover, per outcome, so nobody has to
    discover '1 of 9' by following the certificate."""
    entries = _extraction_entries(slug)
    per_outcome = []
    for o in review.get("outcomes", []):
        pooled = [str(t["id"]).replace("PMID ", "") for t in o.get("trials", [])]
        absent = [str(d["id"]).replace("PMID ", "") for d in (o.get("declared_absent_trials") or [])]
        with_entry = sorted({p for p, es in entries.items() if any(e["outcome"] == o["name"] for e in es)})
        per_outcome.append({"outcome": o["name"], "primary": bool(o.get("primary")),
                            "pooled_rows": len(pooled), "pooled_rows_with_an_extraction_object": sorted(p for p in pooled if p in with_entry),
                            "declared_absent_rows": len(absent), "declared_absent_rows_with_an_extraction_object": sorted(p for p in absent if p in with_entry),
                            "trials_with_any_entry_for_this_outcome": with_entry})
    primary = next(x for x in per_outcome if x["primary"])
    return {
        "files": sorted({e["file"] for es in entries.values() for e in es}),
        "certificate_key": "extraction_objects_sha256",
        "per_outcome": per_outcome,
        "plain_statement": (f"{cert.get('slug')}: verified_effects.json holds the PRIMARY outcome for "
                            f"{len(primary['pooled_rows_with_an_extraction_object'])} of {primary['pooled_rows']} pooled rows "
                            f"({', '.join(primary['pooled_rows_with_an_extraction_object'])}: an override entry) and harms refusals for the rest. "
                            "The primary-outcome evidence chain for the OTHER pooled rows is: records.json (certified as records_file_sha256 / "
                            "retrieved_corpus_sha256) -> the certified analysis code blobs (analysis_code_sha256) -> the review.json trial rows "
                            "(certified as review_sha256), which verification_rows[*].source binds to the container + selector + span. "
                            "An auditor who follows extraction_objects_sha256 alone will find the primary outcome for one trial; that is a fact "
                            "about which certified input carries which evidence, not a missing row."),
    }


def _analysis_identity(t: dict, review: dict, ee: dict) -> dict:
    """Endpoint identity is not estimand identity -- and an estimand field without evidence is a producer assertion. Every field
    here is {value, basis, span, start, end, parent_representation}; the review-target fallback ('trial end' on every row) is gone."""
    reg = registered_estimand(review["slug"])
    reg_value = {"analysis_set": reg["analysis_set"], "treatment_strategy": reg["treatment_strategy"], "follow_up_window": "prespecified randomised follow-up to end of blinded follow-up (on-study)",
                 "comparator_direction": reg["contrast"], "estimator": reg["estimator"]}

    def field(name, ev, value=None):
        basis = ev["state"]
        eff = value if value is not None else ev.get("value")
        out = {"value": eff, "basis": basis, "registered": reg_value.get(name),
               "observed": None if basis != "STATED_IN_OWNING_EVIDENCE" else {"value": eff, "span": ev.get("span"), "start": ev.get("start"),
                                                                             "end": ev.get("end"), "parent_representation": ev.get("parent_representation")},
               "note": "observed is never filled from registered; a REGISTERED_DEFAULT is the requirement standing in for an unknown observation, and says so"}
        if basis == "STATED_IN_OWNING_EVIDENCE":
            out.update({"span": ev.get("span"), "start": ev.get("start"), "end": ev.get("end"), "parent_representation": ev.get("parent_representation")})
        elif basis == "UNRESOLVED":
            out.update({"values_stated": ev.get("values"), "evidence": ev.get("evidence")})
        return out
    se = t.get("study_effect") or {}
    window = ee["analysis_window"]
    strategy_value = ("on-treatment" if window.get("value") == "on-treatment" else
                      "treatment-policy (on-study)" if window["state"] == "STATED_IN_OWNING_EVIDENCE" else window.get("value"))
    ident = {
        "analysis_set": field("analysis_set", ee["analysis_set"]),
        "treatment_strategy": field("treatment_strategy", window, strategy_value),
        "follow_up_window": field("follow_up_window", window, window.get("span") if window["state"] == "STATED_IN_OWNING_EVIDENCE" and window.get("value") == "follow-up stated"
                                  else window.get("value")),
        "comparator_direction": {**field("comparator_direction", ee["contrast"]),
                                 "effect_less_than_1_favours": "experimental (ratio measures; the row's own clause names the comparator arm when STATED)"},
        "estimator": {**field("estimator", ee["estimator"]),
                      "producer_fields": {"method": se.get("estimator_method"), "reported_label": (t.get("effect_object") or {}).get("reported_label"),
                                          "canonical_estimand": (t.get("effect_object") or {}).get("canonical_estimand")}},
    }
    ident["analysis_identity_key"] = " | ".join(f"{k}={ident[k]['value']}[{ident[k]['basis'][:3]}]" for k in ("analysis_set", "treatment_strategy", "follow_up_window", "estimator"))
    ident["rule"] = "a value with basis REGISTERED_DEFAULT is a default, not a statement; two rows that differ only in defaults are NOT shown to differ"
    return ident


def _spans_for_row(t: dict, span: str, loc: dict, parsed: str) -> list[dict]:
    """Multi-span binding record. Abstract-sourced rows carry result + definition; the structure admits column_header /
    section_heading / analysis_method / footnote so table-sourced evidence can be expressed rather than refused."""
    out = [{"role": "result", "text": span, "parent_representation": loc.get("parent"), "start": loc.get("start"), "end": loc.get("end"), "match": loc.get("match")}]
    d = t.get("endpoint_definition_span")
    if d:
        dl = locate(d, parsed)
        out.append({"role": "definition", "text": d, "parent_representation": dl.get("parent"), "start": dl.get("start"), "end": dl.get("end"), "match": dl.get("match")})
    return out


def verification_rows(slug: str, review: dict, docs_by_id: dict, art_by_ref: dict, records: dict) -> tuple[list[dict], dict]:
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    extraction = _extraction_entries(slug)
    canonical_components = sorted((primary.get("endpoint_canonical") or {}).get("components") or [])
    lexicon_blob = _git("rev-parse", "HEAD:harness/target_endpoint.py")
    fam_rendered = {f.get("family_id"): f for f in review.get("trial_families", []) if isinstance(f, dict)}
    certified = _read_json(ROOT / "cache" / slug / "families.json")
    fam_by_id = {f.get("family_id"): f for f in certified.get("families", []) if isinstance(f, dict)}   # AUTHORITATIVE: trial_family_map_sha256
    rec_ref = f"cache/{slug}/records.json"
    rec_raw_sha = art_by_ref[rec_ref]["sha256"]
    rec_canon_sha = art_by_ref[rec_ref]["declared_digest"]
    rows = []
    for t in primary["trials"]:
        trial_id = str(t.get("id") or "")
        pmid = trial_id.replace("PMID ", "")
        doc = docs_by_id.get(f"pubmed:{pmid}") or {}
        selected = resolve_selector(records, pmid)      # refuses on 0 or >=2 matches
        parsed = selected.get("abstract") or ""
        span = t.get("endpoint_result_span") or ""
        loc = locate_all(span, parsed)
        fam = fam_by_id.get(t.get("family_id")) or {}
        fam_r = fam_rendered.get(t.get("family_id")) or {}
        elig = (fam.get("eligibility") or {}).get("state") if fam else None
        elig_rendered = (fam_r.get("eligibility") or {}).get("state") if fam_r else None
        conflicts = (fam.get("conflicts") if fam and fam.get("conflicts") is not None else fam_r.get("conflicts")) if (fam or fam_r) else None
        unresolved = [c for c in conflicts if isinstance(c, dict) and str(c.get("state", "")).upper().startswith("UNRESOLVED")] if isinstance(conflicts, list) else []
        effect = {"scale": t.get("scale"), "estimate": t.get("effect"), "ci_low": t.get("ci_low"), "ci_high": t.get("ci_high")}
        tokens = _tokens(effect["estimate"]) + _tokens(effect["ci_low"]) + _tokens(effect["ci_high"])
        values = [effect["estimate"], effect["ci_low"], effect["ci_high"]]
        eff_clause = clause_with_effect(span, values) if all(v is not None for v in values) else None
        nums = clause_numbers(eff_clause) if eff_clause else []
        tokens_in = {tok: any(abs(float(tok) - n) < 1e-12 for n in nums) for tok in tokens}
        components = sorted(t.get("components") or [])
        components_canonical = sorted(x.upper().replace(" ", "_") for x in
                                      _components_from_text(" ; ".join(components), expand_named_composites=False)) if components else []
        cov = (doc.get("coverage_status") or {}).get("value")
        located = loc["match"] in ("VERBATIM", "NORMALISED")
        ee = estimand_evidence(parsed, eff_clause)
        predicates = {
            "P1_source_bytes": {"state": "PASS" if art_by_ref[rec_ref]["sha256"] == (doc.get("representations", {}).get("PARSED_SOURCE", {}).get("container_sha256")) else "FAIL",
                                "declared": art_by_ref[rec_ref]["sha256"], "container": rec_ref},
            "P2_span_located": {"state": "PASS" if located else "FAIL", **loc,
                                "typed_state": ("LOCATED" if located and loc.get("occurrences", 0) == 1 else
                                                "LOCATED" if located and loc.get("occurrences", 0) > 1 else
                                                "NOT_FOUND" if span else "NOT_ATTEMPTED"),
                                "competing_candidates": ([m.start() for m in re.finditer(re.escape(span), parsed)] if loc.get("occurrences", 0) > 1 else []),
                                "occurrence_rule": "0 = SPAN_NOT_IN_SOURCE; 1 = located; >1 = SPAN_LOCATION_AMBIGUOUS unless offsets pin one occurrence (they do here)"},
            "P3_effect_tokens_in_span": {"state": "PASS" if tokens and all(tokens_in.values()) else "FAIL", "tokens": tokens_in,
                                         "rule": "NUMERIC equality against the numbers of the tuple's own clause (0.80 == 0.8 accepted; 0.96 vs 1.0 refused; "
                                                 "0.8 vs 0.84 refused); never substring", "clause_numbers": nums},
            "P4_endpoint_components": {"state": "PASS" if components_canonical == canonical_components and components_canonical else "FAIL",
                                       "row_components_as_stated": components, "row_components_canonical": components_canonical,
                                       "outcome_canonical": canonical_components,
                                       "canonicalisation": f"PRODUCER STEP: harness/target_endpoint.py::_components_from_text (git blob {lexicon_blob}); "
                                                           "a context-sensitive lexicon in code, not data -- an independent verifier compares the shipped "
                                                           "canonical sets mechanically but cannot re-derive the mapping from the stated strings (limitation stated)"},
            "P5_family_eligible": {"state": "PASS" if elig == "ELIGIBLE" else "FAIL", "family_id": t.get("family_id"), "eligibility_state": elig,
                                   "authoritative_copy": f"cache/{slug}/families.json (certified: trial_family_map_sha256)",
                                   "rendered_copy_state": elig_rendered, "copies_agree": elig == elig_rendered,
                                   "absence_code": ((fam_r.get("eligibility") or {}).get("absence_code") if fam_r else None)},
            "P6_no_unresolved_conflict": {"state": "PASS" if not unresolved else "FAIL", "unresolved": unresolved},
            "P7_coverage_adequate_for_claim": {"state": "PASS" if located else "FAIL", "claim_kind": "POSITIVE",
                                               "rule": "positive claim: a located excerpt suffices; coverage_status of the source is " + str(cov)},
            "P8_endpoint_bound": {"state": "PASS" if t.get("endpoint_binding") == "named_endpoint_resolved_to_definition_span" else "FAIL",
                                  "endpoint_binding": t.get("endpoint_binding"), "endpoint_admissibility": t.get("endpoint_admissibility")},
            "P9_span_target_mention": span_target_mention(span, values, t.get("endpoint_definition_span"), canonical_components) if all(v is not None for v in values)
                                      else {"state": "AMBIGUOUS_ENDPOINT_BINDING", "mention": "no effect tuple"},
        }
        reg = registered_estimand(slug)
        aset = ee["analysis_set"]; win = ee["analysis_window"]
        unregistered = []
        if aset["state"] == "STATED_IN_OWNING_EVIDENCE" and aset["value"] != reg["analysis_set"]:
            unregistered.append(("analysis_set", aset["value"]))
        if win["state"] == "STATED_IN_OWNING_EVIDENCE" and win.get("value") == "on-treatment":
            unregistered.append(("treatment_strategy", "on-treatment"))
        if aset["state"] == "UNRESOLVED" or win["state"] == "UNRESOLVED":
            unregistered.append(("estimand", "UNRESOLVED"))
        cil = ci_level_record(eff_clause, (t.get("study_effect") or {}).get("standard_error"), t.get("ci_low"), t.get("ci_high"))
        predicates["P12_ci_level"] = {"state": "FAIL" if cil["level_agreement"] == "MISMATCH" else "PASS", **{k: cil.get(k) for k in ("source_ci_pct", "basis", "level_agreement", "assumed_ci_pct")}}
        predicates["P11_registered_estimand"] = {"state": "PASS" if not unregistered else "FAIL", "registered": {k: reg[k] for k in ("analysis_set", "treatment_strategy")},
                                                 "protocol_ref": reg["protocol_ref"], "protocol_span_start": reg["start"], "departures": unregistered,
                                                 "rule": "a stated field must agree with the registered estimand; a REGISTERED_DEFAULT agrees by construction; UNRESOLVED fails"}
        failing = [k for k, v in predicates.items() if v["state"] != "PASS"]
        final = ("ADMISSIBLE" if not failing else
                 "MIGRATION_STATE_UNBOUND_LEGACY" if failing == ["P8_endpoint_bound"] and t.get("endpoint_binding") == "unbound_legacy" else
                 "INADMISSIBLE")
        rows.append({
            "outcome_effect_id": t.get("outcome_effect_id"),
            "trial": {"label": t.get("label"), "id": trial_id, "family_id": t.get("family_id"), "trial_family_id": t.get("trial_family_id")},
            "source": {"source_id": f"pubmed:{pmid}", "document_ref": f"{rec_ref}#PMID-{pmid}",
                       "selector": {"scheme": SELECTOR_RULE["scheme"], "resolution": SELECTOR_RULE["resolution"], "matches": 1,
                                    "selected_identifier": {"id_type": selected.get("id_type", "pmid"), "id": str(selected.get("id"))}},
                       "identity": "container digest + deterministic selector (rows drawn from one container legitimately share its digest)",
                       "digests": [
                           {"subject": "container file", "ref": rec_ref, "procedure": "sha256 of the raw served bytes", "value": rec_raw_sha,
                            "shared_by": "every row whose document_ref names this container"},
                           {"subject": "container as JSON object", "ref": rec_ref, "procedure": "sha256 of canonical JSON (see canonicalisation)",
                            "value": rec_canon_sha, "certificate_key": "records_file_sha256"},
                           {"subject": "selected record's decoded abstract text (PARSED_SOURCE)", "procedure": "sha256 of the UTF-8 encoding of the str",
                            "value": sha256_text(parsed)},
                           {"subject": "selected record's NORMALIZED_SOURCE", "procedure": "sha256 of UTF-8 of normalize(PARSED_SOURCE) per the transformation manifest",
                            "value": sha256_text(normalize(parsed))}],
                       "source_sha256": rec_raw_sha,
                       "representation": "PARSED_SOURCE", "representation_sha256": sha256_text(parsed),
                       "quotation_must_occur_in": "the selected record's PARSED_SOURCE (or its NORMALIZED_SOURCE with the manifest applied), never elsewhere in the container",
                       "parent_evidence": (doc.get("representations", {}).get("ACQUIRED_SOURCE") or {}).get("ref"),
                       "acquisition_uri": f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml",
                       "coverage_status": cov},
            "span": {"source_id": f"pubmed:{pmid}", "parent_representation": loc.get("parent"),
                     "representation_sha256": sha256_text(parsed) if loc.get("parent") == "PARSED_SOURCE" else sha256_text(normalize(parsed)),
                     "start": loc.get("start"), "end": loc.get("end"), "coordinates": COORDINATES,
                     "text": span, "match": loc["match"], "normalisation": loc.get("normalisation"),
                     "definition_span": t.get("endpoint_definition_span")},
            "endpoint": {"components": components, "components_canonical": components_canonical, "canonical_components": canonical_components, "target_endpoint_class": t.get("target_endpoint_class"),
                         "undetermined_death_counted_as_cv": undetermined_death_field(t.get("endpoint_definition_span")),
                         "population": {"analysis_set": t.get("analysis_set"), "population_age": t.get("population_age")},
                         "intervention": t.get("intervention_ontology"), "comparator": "placebo (topic config)", "timepoint": t.get("follow_up_window"),
                         "estimand": (t.get("effect_object") or {}).get("canonical_estimand"), "endpoint_definition": t.get("endpoint_definition")},
            "effect": {**effect, "number_tokens": tokens, "study_effect": t.get("study_effect")},
            "estimand_evidence": ee,
            "analysis_identity": _analysis_identity(t, review, ee),
            "spans": _spans_for_row(t, span, loc, parsed) + [
                {"role": "analysis_method", "field": k, "text": v["span"], "parent_representation": v.get("parent_representation"),
                 "start": v.get("start"), "end": v.get("end"), "match": "VERBATIM" if v.get("start") is not None else "NORMALISED"}
                for k, v in ee.items() if v["state"] == "STATED_IN_OWNING_EVIDENCE" and v.get("span")],
            "producer_label_scope": "the page's 'verified' checks the point estimate only (verify_pooled); P3 below checks estimate and both limits",
            "certified_evidence_chain": {
                "extraction_object_for_this_outcome": next(({"file": e["file"], "provenance": e["provenance"]} for e in extraction.get(pmid, [])
                                                            if e["outcome"] == primary["name"]), "ABSENT"),
                "chain": ["cache/%s/records.json (records_file_sha256 / retrieved_corpus_sha256)" % slug,
                          "analysis code blobs (analysis_code_sha256)",
                          "reviews/%s/review.json trial row (review_sha256)" % slug]
                         if not any(e["outcome"] == primary["name"] for e in extraction.get(pmid, []))
                         else ["cache/%s/verified_effects.json override entry (extraction_objects_sha256)" % slug,
                               "cache/%s/records.json record (records_file_sha256)" % slug,
                               "reviews/%s/review.json trial row (review_sha256)" % slug],
            },
            "statistical_input": statistical_input(t, pmid, eff_clause),
            "decision": {"selected_candidate": t.get("selected_estimator"), "selection_rule": t.get("selection_rule"), "rejected_alternatives": t.get("alternatives"),
                         "endpoint_binding": t.get("endpoint_binding"), "endpoint_binding_reason": t.get("endpoint_binding_reason"),
                         "adjudication_status": t.get("endpoint_admissibility"), "family_identity_state": t.get("family_identity_state"),
                         "producer_labels": {"verified": t.get("verified"), "verify_basis": t.get("verify_basis"), "provenance": t.get("provenance")},
                         "narrowed_states": {
                             "result_concordant_with_located_span": "SUPPORTED" if located and predicates["P3_effect_tokens_in_span"]["state"] == "PASS" else "NOT_SUPPORTED",
                             "cached_representation_faithful_and_complete": {"COMPLETE_ABSTRACT": "SUPPORTED (abstract scope)", "COMPLETE_SOURCE": "SUPPORTED"}.get(cov, "NOT_SUPPORTED: " + str(cov))}},
            "admission": {"required_predicates": list(predicates), "predicates": predicates, "final": final,
                          "meaning": "admissible for this exact analysis under this policy version and evidence version; NOT 'verified'; revalidate on load",
                          "analysis_identity_key": None,   # filled below once analysis_identity exists
                          "policy_version": {"format_revision": FORMAT_REVISION, "predicates": sorted(predicates)},
                          "evidence_version": {"records_json_sha256": art_by_ref[rec_ref]["sha256"], "certificate_release_sha256": None,
                                               "review_blob": None}},
        })
    return rows, {"canonical_components": canonical_components, "k": len(rows)}


def absence_claims(slug: str, review: dict, docs_by_id: dict) -> list[dict]:
    out = []
    for o in review.get("outcomes", []):
        for d in o.get("declared_absent_trials") or []:
            trial_id = str(d.get("id") or "")
            pmid = trial_id.replace("PMID ", "")
            ref = d.get("document_ref")
            if ref and ref.startswith("outputs/"):
                doc = next((x for x in docs_by_id.values() if (x["representations"].get("PARSED_SOURCE") or {}).get("ref") == ref.split("#")[0]), None)
            else:
                doc = docs_by_id.get(f"pubmed:{pmid}")
            cov = ((doc or {}).get("coverage_status") or {}).get("value", "UNKNOWN_COMPLETENESS")
            state = d.get("state") or d.get("reason_code")
            kind = "NEGATIVE" if state == "OUTCOME_NOT_IN_SOURCE" else "POSITIVE_REFUSAL" if state in ("REFUSED_ON_EVIDENCE", "SIGNAL_SPURIOUS") else "OTHER"
            if kind == "NEGATIVE":
                admissible = cov in ("COMPLETE_SOURCE", "COMPLETE_ABSTRACT")
                rule = ("negative claim requires a searched representation certified complete for the scope; coverage_status is " + cov +
                        (" -> NOT admissible: the absence verdict is true of the cached copy and says nothing about the cited source"
                         if not admissible else " -> admissible for the abstract scope only (a full-text absence claim would need COMPLETE_SOURCE)"))
            elif kind == "POSITIVE_REFUSAL":
                admissible = None
                rule = ("a refusal grounded on evidence is a positive claim about what a span says and is not subject to the coverage rule; "
                        "the bundle does NOT locate or evaluate it -- it is carried as a producer assertion (see limits L12)")
            else:
                admissible, rule = None, "not classified by the bundle"
            non_pubmed = bool(ref) and not ref.startswith(f"cache/{slug}/records.json")
            out.append({"outcome": o["name"], "trial": {"id": trial_id, "label": d.get("label")},
                        "evaluated_by_bundle": kind == "NEGATIVE",
                        "not_evaluated_because": (None if kind == "NEGATIVE" else
                                                  ("no contractual preservation parser for FDA text extractions / PMC full text, and the refusal's span is not located by the bundle"
                                                   if non_pubmed else "positive refusals are producer assertions; the bundle locates and evaluates negative claims only")),
                        "producer_state": state, "producer_reason": d.get("reason"), "producer_reason_code": d.get("reason_code"),
                        "searched_document_ref": ref or (f"cache/{slug}/records.json#PMID-{pmid}" if pmid else None),
                        "searched_representation": "PARSED_SOURCE", "searched_representation_coverage_status": cov,
                        "claim_kind": kind, "negative_claim_admissible": admissible, "rule_applied": rule,
                        "preservation_verdict": ((doc or {}).get("preservation_record") or {}).get("verdict")})
    return out


# ----------------------------------------------------------------------------------------------------------------
# pooled reference (canonical path) and resolvability walk
# ----------------------------------------------------------------------------------------------------------------

_CV_WORDS = re.compile(r"myocardial infarction|stroke|cardiovascular", re.I)


def binding_states(review: dict, primary_ids: set) -> dict:
    """Every rendered row of every outcome with its binding class, so a migration state is visible where an outsider
    looks, and never folded into an admissible count."""
    rows = []
    for o in review.get("outcomes", []):
        for t in o.get("trials", []):
            b = t.get("endpoint_binding")
            cls = "BOUND" if b == "named_endpoint_resolved_to_definition_span" else "MIGRATION_STATE_UNBOUND_LEGACY" if b == "unbound_legacy" else "OTHER"
            row = {"outcome": o["name"], "primary": bool(o.get("primary")), "trial": {"id": t.get("id"), "label": t.get("label")},
                   "endpoint_binding": b, "endpoint_admissibility": t.get("endpoint_admissibility"), "target_endpoint_class": t.get("target_endpoint_class"),
                   "binding_class": cls, "producer_labels": {"verified": t.get("verified"), "verify_basis": t.get("verify_basis"), "provenance": t.get("provenance")},
                   "in_verification_rows": bool(o.get("primary")) and t.get("id") in primary_ids,
                   "counted_in_admissible_rows": False}
            if cls != "BOUND":
                defn = t.get("endpoint_definition") or ""
                src = str(t.get("source") or "")
                row["observations"] = {
                    "definition_span": t.get("endpoint_definition_span"),
                    "endpoint_definition_carried": defn[:200],
                    "definition_names_another_outcome": bool(defn and not o.get("primary") and _CV_WORDS.search(defn) and not _CV_WORDS.search(o["name"])),
                    "table_sourced": src.lstrip().startswith("<table-wrap") or "<table" in src[:200],
                    "what_would_bind_it": "spans[] with roles result (the table row/cell) + column_header + section_heading (+ analysis_method / footnote "
                                          "where present), each located in a named representation with offsets -- see vocabulary.span_binding_rule; "
                                          "a single definition span cannot bind a table cell and its absence must not refuse the row",
                    "spans_present": [],
                }
            rows.append(row)
    n_unb = sum(1 for r in rows if r["binding_class"] == "MIGRATION_STATE_UNBOUND_LEGACY")
    return {"rows": rows, "counts": {"rows": len(rows), "bound": sum(1 for r in rows if r["binding_class"] == "BOUND"),
                                      "migration_state_unbound_legacy": n_unb, "other": sum(1 for r in rows if r["binding_class"] == "OTHER")},
            "statement": (f"{n_unb} rendered row(s) carry UNBOUND_LEGACY. The producer's admit_rows returns admissible=True for them through a fail-open "
                          "(external audit, ELIXA 4-point demonstration). This bundle counts them as a migration state: not in admissible_rows, not refused. "
                          "Whether the LIVE build behaves as the audited code does is UNVERIFIABLE from here until target_endpoint.py is pinned in the "
                          "certificate and generating_commit is recorded (the certificate lane's closure).")}


_TUPLE_FORMS = [
    # 1.02 (0.89, 1.18) | 1.24 (0.90, 1.70) | HR=1.24 (95% CI: 0.9, 1.70) | HR (95% CI) of 1.24 (0.90, 1.70)
    re.compile(r"(?<![\d.])(\d\.\d{1,3})\s*\n?\s*\((?:95%\s*CI:?\s*)?(\d\.\d{1,3}),?\s*\n?\s*(?:to\s*)?(\d\.\d{1,3})\s*\)"),
    # (0.887, 1.172) with a point estimate of 1.02
    re.compile(r"\((\d\.\d{1,3}),\s*\n?\s*(\d\.\d{1,3})\)\s*with a point estimate of\s*(\d\.\d{1,3})"),
    # hazard ratio estimate of 1.02 with an associated 95% confidence interval of (0.89, 1.17)
    re.compile(r"estimate of\s*(\d\.\d{1,3})\s*with an associated 95% confidence interval of\s*\n?\s*\((\d\.\d{1,3}),\s*\n?\s*(\d\.\d{1,3})\)"),
]


def _parse_tuple(text: str):
    flat = text.replace("\n", " ")
    for i, rx in enumerate(_TUPLE_FORMS):
        m = rx.search(flat)
        if m:
            g = m.groups()
            est, lo, hi = (g[2], g[0], g[1]) if i == 1 else (g[0], g[1], g[2])
            return {"estimate": float(est), "ci_low": float(lo), "ci_high": float(hi),
                    "precision_decimals": max(len(x.split(".")[1]) for x in (est, lo, hi)), "form": i}
    return None


def _endpoint_of(kind: str, text: str, tuple_text: str | None = None) -> str:
    """Endpoint of the analysis a span carries. For a linearised table span the classification is made on the piece
    that holds the tuple plus its left neighbour (the row label), never on the caption, which may name both endpoints."""
    k = kind.lower()
    if "4p" in k:
        return "4-point MACE+"
    if "3p" in k:
        return "3-point MACE"
    scope = text
    if tuple_text and "|" in text:
        pieces = [x.strip() for x in text.split("|") if x.strip()]
        for i, pc in enumerate(pieces):
            if tuple_text in pc.replace("\n", " "):
                j = i
                while j > 0 and not re.search(r"mace|point|composite", pieces[j].lower()):
                    j -= 1                      # back to the row label that names the endpoint
                scope = " ".join(pieces[j:i + 1])
                break
    t = scope.lower().replace("\n", " ")
    if "4-point" in t or "mace+" in t or "unstable angina" in t:
        return "4-point MACE+"
    if "3-point" in t or "mace endpoint" in t:
        return "3-point MACE"
    comps = sum(1 for w in ("cardiovascular death", "myocardial infarction", "stroke") if w in t)
    if comps >= 2 and "unstable angina" not in t:
        return "3-point MACE"
    return "UNSTATED"


def _locate_pieces(span_text: str, text: str) -> dict:
    """A linearised table span ('caption | header | cells') is a selection, not verbatim text. Locate each piece."""
    pieces = [x.strip() for x in span_text.split("|") if x.strip()]
    if len(pieces) < 2:
        return {"linearised": False}
    located = [{"piece": pc[:80], "match": locate(pc, text)["match"]} for pc in pieces]
    n = sum(1 for x in located if x["match"] != "NOT_LOCATED")
    return {"linearised": True, "pieces": len(pieces), "pieces_located": n, "detail": located}
_COUNTS = re.compile(r"(\d{3,4})\s*\(\s*\d+\.\d%\)\s*(\d{3,4})\s*\(\s*\d+\.\d%\)")


def _strategy_of(kind: str, text: str) -> str:
    t = (kind + " " + text).lower().replace("\n", " ")
    if "on-treatment" in t or "ontreatment" in t:
        return "on-treatment"
    if "on-study" in t or "onstudy" in t or "itt" in t or "intention-to-treat" in t:
        return "on-study (ITT)"
    return "UNSTATED"


def registered_estimand(slug: str) -> dict:
    """The estimand the protocol registers, read from the served protocol text with its line located, so 'bound to an identity'
    can be checked against 'bound to the REGISTERED identity'."""
    path = ROOT / "protocols" / f"{slug}.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    line = next((ln for ln in text.splitlines() if ln.strip().lower().startswith("- **estimand.**")), "")
    start = text.find(line) if line else -1
    low = line.lower()
    return {
        "protocol_ref": f"protocols/{slug}.md", "protocol_span": line.strip(), "start": start if start >= 0 else None,
        "end": (start + len(line)) if start >= 0 else None, "parent_representation": "PARSED_SOURCE (protocol text, code points)",
        "analysis_set": "intention-to-treat" if "intention-to-treat" in low else "UNSTATED",
        "treatment_strategy": "on-study (ITT)",
        "treatment_strategy_basis": "the protocol registers the intention-to-treat effect during the prespecified randomised follow-up: a treatment-policy (on-study) strategy",
        "contrast": "GLP-1 RA vs placebo" if "versus placebo" in low or "vs placebo" in low else "UNSTATED",
        "estimator": "hazard ratio, time to first event" if "time to first" in low else "UNSTATED",
        "rule": "a binding whose identity differs from the registered estimand on analysis set or treatment strategy is BOUND_TO_UNREGISTERED_ESTIMAND -- "
                "internally consistent is necessary and not sufficient",
    }


def regulatory_facts(review: dict, art_by_ref: dict) -> list:
    """Each held regulatory fact with EVERY candidate analysis of the endpoint carried separately, so two authentic
    analyses of the same endpoint in the same document are distinguishable from the bundle alone."""
    out = []
    for f in review.get("held_regulatory_facts") or []:
        text_ref = f.get("extracted_text_path")
        text = (ROOT / text_ref).read_text(encoding="utf-8", errors="replace") if text_ref and (ROOT / text_ref).exists() else ""
        dec = f.get("decision") or {}
        eff = dec.get("effect") or {}
        analyses = []
        for sp in f.get("spans") or []:
            span_text = sp.get("span") or ""
            tup = _parse_tuple(span_text)
            if not tup:
                continue
            loc = locate(span_text, text)
            pieces = _locate_pieces(span_text, text) if loc["match"] == "NOT_LOCATED" else {"linearised": False}
            binding_kind = ("VERBATIM_SPAN" if loc["match"] != "NOT_LOCATED" else
                            "PARTIAL_TABLE_BINDING" if pieces.get("linearised") and pieces.get("pieces_located", 0) else "NOT_LOCATED")
            c = _COUNTS.search(span_text.replace("\n", " "))
            strategy = _strategy_of(sp.get("kind", ""), span_text)
            endpoint = _endpoint_of(sp.get("kind", ""), span_text, tuple_text=f"{tup['estimate']}")
            ident = {"trial": f.get("trial"), "endpoint": endpoint,
                     "analysis_set": "ITT" if ("itt" in (dec.get("outcome") or "").lower() or "itt" in span_text.lower()) else "UNSTATED",
                     "treatment_strategy": strategy, "estimator": eff.get("estimator") or "UNSTATED",
                     "precision_decimals": tup["precision_decimals"], "representation_kind": sp.get("kind")}
            ident["analysis_identity_key"] = f"{ident['trial']} | {endpoint} | {ident['analysis_set']} | {strategy} | {tup['precision_decimals']}dp"
            flat = span_text.replace("\n", " ")
            words = {("on-treatment" if "treatment" in m.lower() else "on-study") for m in re.findall(r"on-?\s?study|on-?\s?treatment|end of study|\bEOS\b", flat, re.I)}
            label = None
            if len(words) == 1:
                m = re.search(r"on-?\s?study|on-?\s?treatment|end of study|\bEOS\b", flat, re.I)
                label = m
            elif len(words) >= 2:
                label = "BOTH"
            count_set = sorted({int(x) for x in re.findall(r"(?<![\d.])(\d{3,4})(?![\d.%])", span_text.replace("\n", " "))})
            label_span = None
            if label and label != "BOTH":
                inner = span_text.find(label.group(0))
                base = loc.get("start") if loc.get("match") == "VERBATIM" else None
                ok = base is not None and inner >= 0 and text[base + inner: base + inner + len(label.group(0))] == label.group(0)
                label_span = {"role": "column_header", "text": label.group(0), "parent_representation": "PARSED_SOURCE" if ok else None,
                              "start": (base + inner) if ok else None, "end": (base + inner + len(label.group(0))) if ok else None,
                              "note": "the (on-study)/(on-treatment) row label that qualifies this row's tuple"}
            analyses.append({"kind": sp.get("kind"), "pdf_page": sp.get("pdf_page"), "text": span_text, "located": loc,
                             "spans": [{"role": "result", "text": span_text, "parent_representation": loc.get("parent"), "start": loc.get("start"), "end": loc.get("end"), "match": loc.get("match")}]
                                      + ([label_span] if label_span else []),
                             "strategy_evidence": ({"state": "STATED_IN_OWNING_EVIDENCE", "how": "strategy named in the span", "span": label.group(0)} if label and label != "BOTH" else
                                                   {"state": "UNRESOLVED", "how": "the span itself names both strategies", "span": sorted(words)} if label == "BOTH" else None),
                             "span_binding": binding_kind, "table_pieces": pieces if pieces.get("linearised") else None,
                             "tuple": {k: tup[k] for k in ("estimate", "ci_low", "ci_high")},
                             "counts": ({"placebo_events": int(c.group(1)), "treatment_events": int(c.group(2))} if c else None),
                             "integers_in_span": count_set,
                             "analysis_identity": ident})
        # strategy evidence for unlabelled candidates: via counts that match a labelled candidate, else UNBOUND when the source
        # carries both strategies for that endpoint, else the registered default
        for a in analyses:
            ev = a.get("strategy_evidence") or {}
            if ev.get("state") == "STATED_IN_OWNING_EVIDENCE":
                a["analysis_identity"]["treatment_strategy"] = "on-treatment" if "treatment" in ev["span"].lower() else "on-study (ITT)"
            elif ev.get("state") == "UNRESOLVED":
                a["analysis_identity"]["treatment_strategy"] = "UNRESOLVED"
            ident = a["analysis_identity"]
            ident["analysis_identity_key"] = f"{ident['trial']} | {ident['endpoint']} | {ident['analysis_set']} | {ident['treatment_strategy']} | {ident['precision_decimals']}dp"
        labelled = [a for a in analyses if (a.get("strategy_evidence") or {}).get("state") == "STATED_IN_OWNING_EVIDENCE"]
        for a in analyses:
            if a.get("strategy_evidence"):
                continue
            same_ep = [b for b in labelled if b["analysis_identity"]["endpoint"] == a["analysis_identity"]["endpoint"]]
            by_counts = [b for b in same_ep if b.get("counts") and set(b["counts"].values()) <= set(a.get("integers_in_span") or [])]
            by_rounding = [b for b in same_ep if all(abs(round(a["tuple"][k], 2) - b["tuple"][k]) < 1e-9 for k in ("estimate", "ci_low", "ci_high"))
                           and a["analysis_identity"]["precision_decimals"] > b["analysis_identity"]["precision_decimals"]]
            strategies_in_source = {b["analysis_identity"]["treatment_strategy"] for b in same_ep}
            flat_text = text.lower()
            source_states_both = len(strategies_in_source) >= 2 or ("on-treatment" in flat_text and "on-study" in flat_text)
            if by_counts:
                a["analysis_identity"]["treatment_strategy"] = by_counts[0]["analysis_identity"]["treatment_strategy"]
                a["strategy_evidence"] = {"state": "BOUND_VIA_COUNTS", "how": "the event counts in this span equal those of the labelled candidate " + by_counts[0]["kind"],
                                          "counts": by_counts[0]["counts"], "labelled_span": by_counts[0]["strategy_evidence"]["span"]}
            elif by_rounding:
                a["analysis_identity"]["treatment_strategy"] = by_rounding[0]["analysis_identity"]["treatment_strategy"]
                a["strategy_evidence"] = {"state": "BOUND_VIA_ROUNDING", "how": "this unrounded tuple rounds to the labelled candidate " + by_rounding[0]["kind"],
                                          "labelled_span": by_rounding[0]["strategy_evidence"]["span"]}
            elif source_states_both:
                a["analysis_identity"]["treatment_strategy"] = "UNRESOLVED"
                a["strategy_evidence"] = {"state": "UNRESOLVED", "how": "the source carries both on-study and on-treatment analyses and this span names neither"}
            else:
                a["strategy_evidence"] = {"state": "REGISTERED_DEFAULT", "how": "no label; the source carries one strategy for this endpoint"}
            ident = a["analysis_identity"]
            ident["analysis_identity_key"] = f"{ident['trial']} | {ident['endpoint']} | {ident['analysis_set']} | {ident['treatment_strategy']} | {ident['precision_decimals']}dp"
        # which analysis does the decision's tuple belong to?
        def _matches(a, e):
            t = a["tuple"]
            return abs(t["estimate"] - float(e.get("estimate", -1))) < 1e-9 and abs(t["ci_low"] - float(e.get("ci_low", -1))) < 1e-9 and abs(t["ci_high"] - float(e.get("ci_high", -1))) < 1e-9
        selected = [a for a in analyses if eff and _matches(a, eff)]
        claimed_strategy = _strategy_of("", dec.get("outcome") or "")
        claimed_endpoint = _endpoint_of("", dec.get("outcome") or "")
        reg = registered_estimand(review["slug"])
        consistent = bool(selected) and all((a["analysis_identity"]["treatment_strategy"] == claimed_strategy or
                                              (claimed_strategy == "UNSTATED" and a["analysis_identity"]["treatment_strategy"] in ("UNSTATED", reg["treatment_strategy"]))) and
                                             a["analysis_identity"]["endpoint"] == claimed_endpoint for a in selected)
        selected_unresolved = any((a.get("strategy_evidence") or {}).get("state") == "UNRESOLVED" for a in selected)
        registered_ok = (claimed_strategy == reg["treatment_strategy"]) or (claimed_strategy == "UNSTATED" and not selected_unresolved)   # an unstated claim defaults to the registered estimand
        holder_ids = {(a["analysis_identity"]["treatment_strategy"], a["analysis_identity"]["endpoint"]) for a in selected}
        binding = ("AMBIGUOUS" if len(holder_ids) > 1 else
                   "BOUND" if consistent and registered_ok else
                   "BOUND_TO_UNREGISTERED_ESTIMAND" if consistent else
                   "ANALYSIS_IDENTITY_MISMATCH" if selected else "TUPLE_NOT_IN_ANY_CANDIDATE_SPAN")
        competing = [{"kind": a["kind"], "identity": a["analysis_identity"]["analysis_identity_key"]} for a in selected] if len(holder_ids) > 1 else []
        # the same analysis under different representations may disagree by rounding -- record it, do not resolve it
        by_strategy = {}
        for a in analyses:
            by_strategy.setdefault(a["analysis_identity"]["endpoint"] + " / " + a["analysis_identity"]["treatment_strategy"], []).append(a)
        discrepancies = []
        for strat, group in by_strategy.items():
            twodp = {(round(a["tuple"]["estimate"], 2), round(a["tuple"]["ci_low"], 2), round(a["tuple"]["ci_high"], 2)) for a in group}
            if len(twodp) > 1:
                discrepancies.append({"treatment_strategy": strat, "representations": [{"kind": a["kind"], "tuple": a["tuple"]} for a in group],
                                      "note": "representations of the SAME analysis disagree at two decimals; recorded, not resolved (a rounding of an unrounded "
                                              "value and a table entry can genuinely differ)"})
        out.append({
            "trial": f.get("trial"), "trial_key": f.get("trial_key"), "nct": f.get("nct"),
            "document": {"original_ref": f.get("document_path"), "original_served": f.get("document_path") in art_by_ref and art_by_ref[f["document_path"]]["state"] == "SERVED",
                         "parsed_ref": text_ref, "parsed_served": text_ref in art_by_ref, "parsed_sha256": art_by_ref.get(text_ref, {}).get("sha256")},
            "decision": {"outcome": dec.get("outcome"), "decision": dec.get("decision"), "effect": eff, "counts": dec.get("counts"),
                         "claimed_treatment_strategy": claimed_strategy, "claimed_endpoint": claimed_endpoint, "rule_id": dec.get("rule_id")},
            "candidate_analyses": analyses,
            "selected_analysis_kinds": [a["kind"] for a in selected],
            "tuple_to_identity_binding": binding,
            "competing_candidates": competing,
            "registered_estimand": {"treatment_strategy": reg["treatment_strategy"], "analysis_set": reg["analysis_set"], "protocol_ref": reg["protocol_ref"],
                                    "protocol_span_start": reg["start"], "claimed_matches_registered": registered_ok},
            "distinct_analysis_identity_keys": sorted({a["analysis_identity"]["analysis_identity_key"] for a in analyses}),
            "source_internal_discrepancies": discrepancies,
            "adjudication": f.get("adjudication"), "admissible_per_producer": f.get("admissible"),
            "rule": "a tuple is bound to the analysis whose located span contains it AND whose identity the decision claims; a tuple that occurs only "
                    "in a span of a different treatment strategy is ANALYSIS_IDENTITY_MISMATCH; endpoint identity alone never binds",
        })
    return out


def endpoint_compatibility(review: dict, rows: list) -> dict:
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    proto_path = ROOT / "protocols" / (review["slug"] + ".md")
    protocol = proto_path.read_text(encoding="utf-8") if proto_path.exists() else ""
    line = next((ln.strip() for ln in protocol.splitlines() if "undetermined death as cardiovascular death" in ln), "NOT FOUND IN PROTOCOL TEXT")
    per_trial = {r["trial"]["id"]: r["endpoint"]["undetermined_death_counted_as_cv"] for r in rows}
    values = {v["value"] for v in per_trial.values()}
    direction = next((d for d in ((primary.get("compat_direction") or {}).get("dimensions") or []) if d.get("dimension") == "endpoint_definition"), {})
    return {
        "dimension": "endpoint_definition / undetermined_death_counted_as_cv",
        "state": "COMPATIBLE_WITH_DECLARED_VARIATION" if len(values) > 1 else "HOMOGENEOUS",
        "declared_variation": "undetermined_death_counted_as_cv: yes/no/unstated",
        "protocol_permission": line,
        "per_trial": per_trial,
        "trials_stay_pooled": True,
        "page_label": (primary.get("endpoint_canonical") or {}).get("status"),
        "page_direction_audit": direction.get("key_direction"),
        "note": "the page collapses an accepted variation into HOMOGENEOUS while its own direction audit says " + str(direction.get("key_direction")) +
                "; those are different things. The bundle records the variation per trial from each trial's OWN definition span, so an authorised "
                "difference stays distinguishable from literal identity and from an unauthorised difference. Attribution is per span: the "
                "'including unknown causes' wording is REWIND's (31189511), 'cardiovascular or undetermined causes' is AMPLITUDE-O's (34215025).",
    }


def heterogeneity_statement(primary: dict, res, inputs: list) -> dict:
    """The page says 'tau^2 = 4.448e-05 (non-zero; not 0)'. tau^2 is positive only because Q exceeds df by a hair, and the
    inputs are two-decimal published limits. Measured here: re-pool over inputs perturbed uniformly within their printed
    rounding (+/- half a unit in the last printed place), seeded, and report how often Paule-Mandel returns tau^2 = 0."""
    k = res.k
    rng = random.Random(20260919)
    n, zero, hrs, uppers = 2000, 0, [], []

    def places(x):
        sx = repr(float(x))
        return len(sx.split(".")[1]) if "." in sx else 0

    for _ in range(n):
        studies = []
        for i in inputs:
            e, lo, hi = i["effect"], i["ci_low"], i["ci_high"]
            he, hl, hh = 0.5 * 10 ** -max(places(e), 2), 0.5 * 10 ** -max(places(lo), 2), 0.5 * 10 ** -max(places(hi), 2)
            studies.append(synth.Study(label=i["id"], effect=e + rng.uniform(-he, he), ci_low=lo + rng.uniform(-hl, hl), ci_high=hi + rng.uniform(-hh, hh)))
        r = synth.pool(studies, scale=res.scale)
        zero += (r.tau2 == 0.0)
        hrs.append(r.estimate)
        uppers.append(r.ci_high)
    return {
        "page_statement": f"tau^2 = {primary['result'].get('tau2')} (rendered as non-zero)",
        "Q": res.Q, "df": k - 1, "Q_minus_df": res.Q - (k - 1),
        "input_precision": "published point estimates and 95% limits printed to two decimals (one limit to one decimal); the pool inherits that precision",
        "rounding_sensitivity": {"method": f"{n} seeded (20260919) uniform perturbations of every input within +/- half a unit of its printed last place (minimum two decimals), re-pooled by the canonical path",
                                 "fraction_tau2_zero": zero / n, "pooled_hr_range": [min(hrs), max(hrs)], "max_ci_upper": max(uppers),
                                 "finding_untouched": max(uppers) < 1.0},
        "honest_statement": f"tau^2 ~= {res.tau2:.3g} from published rounded inputs; effectively zero and rounding-sensitive (Q exceeds df by "
                            f"{res.Q - (k - 1):.3f}; {100 * zero / n:.0f}% of within-rounding input sets give tau^2 = 0 under Paule-Mandel). "
                            "The pooled HR and the CI below 1 are not sensitive to this.",
        "rule": "the precision of an output cannot exceed the precision of its inputs; a boundary estimator (tau^2 >= 0) turns input rounding into a categorical claim",
    }


def pooled_reference(review: dict) -> dict:
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    studies = [synth.Study(label=str(t["id"]), effect=t["effect"], ci_low=t["ci_low"], ci_high=t["ci_high"]) for t in primary["trials"]]
    res = synth.pool(studies, scale=primary["trials"][0].get("scale", "HR"))
    inputs = [{"id": str(t["id"]), "effect": t["effect"], "ci_low": t["ci_low"], "ci_high": t["ci_high"]} for t in primary["trials"]]
    return {"outcome": primary["name"], "k": res.k, "scale": res.scale,
            "heterogeneity": heterogeneity_statement(primary, res, inputs),
            "inputs": [{"id": str(t["id"]), "effect": t["effect"], "ci_low": t["ci_low"], "ci_high": t["ci_high"]} for t in primary["trials"]],
            "method": "log-scale inverse-variance random effects; yi = ln(effect), se = (ln(ci_high) - ln(ci_low)) / (2 * 1.959963984540054); "
                      "Paule-Mandel tau^2 by bisection on Q_gen(tau^2) = k-1 (tol 1e-10; upper bound doubled from 1 until F(hi) <= 0; 200 iterations); "
                      "HKSJ: se_HK = se_RE * sqrt(max(1, Q_gen/(k-1))); CI = mu +/- t_{0.975, k-1} * se_HK; back-transform exp",
            "expected": {"estimate": res.estimate, "ci_low": res.ci_low, "ci_high": res.ci_high, "tau2": res.tau2, "mu_log": res.mu_log, "se_log": res.se_log, "Q": res.Q},
            "computed_by": "harness.synth.pool (the canonical path the page's ci_provenance names); scripts/verify_bundle.py recomputes it with no harness import and compares to 1e-9",
            "served_page_rounding": {k: primary["result"].get(k) for k in ("estimate", "ci_low", "ci_high", "tau2")}}


REF = re.compile(r"(?:cache|outputs)/[^\s\"'<>(),;]+\.(?:json|txt|pdf|xml)")


def _collect_source_refs(obj, out):
    if isinstance(obj, dict):
        if "row_sha256" in obj and "table" in obj:
            out.append(obj)
        for v in obj.values():
            _collect_source_refs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_source_refs(v, out)


def resolvability_walk(slug: str, art_by_ref: dict, acq: dict, supporting: dict, reg: dict) -> dict:
    """Start at BUNDLE.json, follow every reference in every served JSON object, classify each edge."""
    edges, seen = {}, set()
    queue = [a["ref"] for a in art_by_ref.values() if a["state"] == "SERVED" and a["ref"].endswith(".json")] + [f"docs/reviews/{slug}/review.json"]

    def classify(base: str) -> str:
        if base in art_by_ref:
            return "RESOLVED_IN_PACKAGE" if art_by_ref[base]["state"] == "SERVED" else art_by_ref[base]["state"]
        if base in supporting or ("docs/" + base) in supporting:
            return "RESOLVED_IN_PACKAGE"
        return "IN_REPOSITORY_NOT_PACKAGE" if (ROOT / base).exists() else "DANGLING"

    while queue:
        path = queue.pop()
        if path in seen or not (ROOT / path).exists():
            continue
        seen.add(path)
        try:
            obj = _read_json(ROOT / path)
        except Exception:
            continue
        for ref in sorted(set(REF.findall(canonical_json(obj)))):
            base = ref.split("#")[0]
            state = classify(base)
            edges[(path, base, "path_ref")] = state
            if state == "RESOLVED_IN_PACKAGE" and base.endswith(".json") and base not in seen:
                queue.append(base)
        srefs = []
        _collect_source_refs(obj, srefs)
        for r in srefs:
            edges[(path, f"AACT {r.get('table')} row_sha256 {r['row_sha256'][:12]}", "digest_ref")] = \
                "RESOLVED_BODY_IN_ACQUISITIONS" if r["row_sha256"] in acq["aact"] else "DIGEST_WITHOUT_BODY"
        if path.endswith("aact_inputs.json"):
            for table, rows in obj.get("source_rows", {}).items():
                for r in rows:
                    edges[(path, f"AACT {table} sha256 {r['sha256'][:12]}", "digest_ref")] = \
                        "RESOLVED_BODY_IN_ACQUISITIONS" if r["sha256"] in acq["aact"] else "DIGEST_WITHOUT_BODY"
    for text_ref, s in reg["by_text"].items():
        held = s.get("held") or {}
        if not (held.get("held_in_tree") or s.get("document_path")):
            edges[("outputs/handover/glp1_regulatory/regulatory_sources_glp1.json",
                   f"original PDF of {text_ref} (sha256 {str(s.get('document_sha256'))[:12]})", "custody")] = "NOT_IN_PACKAGE_PRODUCER_HELD"
    counts = {}
    for st in edges.values():
        counts[st] = counts.get(st, 0) + 1
    unresolved = sorted([{"from": k[0], "to": k[1], "kind": k[2], "state": v} for k, v in edges.items()
                         if v not in ("RESOLVED_IN_PACKAGE", "RESOLVED_BODY_IN_ACQUISITIONS")], key=lambda e: (e["state"], e["from"], e["to"]))
    return {"start": f"reviews/{slug}/BUNDLE.json", "objects_walked": sorted(seen), "edge_counts": counts,
            "edges_not_resolved_to_bytes_in_package": unresolved,
            "statement": f"{counts.get('DIGEST_WITHOUT_BODY', 0)} edge(s) terminate in a digest with no retrievable body (a promise); "
                         f"{counts.get('RESOLVED_BODY_IN_ACQUISITIONS', 0)} digest-only references resolve to bodies under acquisitions/"}


# ----------------------------------------------------------------------------------------------------------------
# source identity of the served bytes
# ----------------------------------------------------------------------------------------------------------------

def source_block(slug: str, review_dir: Path) -> dict:
    """Content-addressed identity of the served bytes. The blob ids are computed from the WORKING TREE, so the stamp exists before
    any commit and never needs its own commit to be true (the earlier content_commit-must-hold-the-blobs rule forced a two-commit
    dance and could not pass the pre-commit hook by construction). content_commit is informational: the most recent commit whose
    tree holds exactly these blobs, or PENDING_COMMIT when the bytes are not yet in any commit."""
    paths = [f"docs/reviews/{slug}/{n}" for n in GENERATED_FILES]
    blobs = {}
    for n in GENERATED_FILES:
        p = review_dir / n
        if p.exists():
            blobs[n] = _git_blob_sha1(p.read_bytes())
    content_commit = "PENDING_COMMIT"
    try:
        for c in _git("log", "-40", "--format=%H", "--", *paths).split():
            ok = True
            for n, b in blobs.items():
                try:
                    if _git("rev-parse", f"{c}:docs/reviews/{slug}/{n}") != b:
                        ok = False; break
                except subprocess.CalledProcessError:
                    ok = False; break
            if ok:
                content_commit = c; break
    except subprocess.CalledProcessError:
        pass
    return {"identity": "content-addressed: served_blob_git_sha1 (git hash-object of the served bytes); verifiable against bytes you already hold",
            "content_commit": content_commit, "_inconsistent": [],
            "content_commit_meaning": "INFORMATIONAL: the most recent commit whose tree holds exactly the served blobs, or PENDING_COMMIT if the bytes "
                                      "are not yet committed; NOT the identity of the bytes and NOT necessarily the commit the generator ran at",
            "generating_commit": "NOT_RECORDED",
            "generating_commit_meaning": "the generator does not record the commit it ran at; build_utc records when the build "
                                         "metadata was authored, not what the bytes were built from, and is not evidence of either",
            "served_blob_git_sha1": blobs,
            "how_to_check_currency": [
                "git ls-remote " + REPO_URL + " refs/heads/main   -> the current main commit",
                f"git rev-parse <that commit>:docs/reviews/{slug}/review.json   (or the GitHub contents API 'sha') -> the blob id main serves from",
                "git hash-object review.json   on the bytes you fetched -> must equal served_blob_git_sha1.review.json above AND the blob at main; "
                "if it equals the former but not the latter, you hold a stale edge copy or a superseded build"],
            "served_copy_may_lag": STALENESS_NOTICE.replace("<slug>", slug)}


def stamp_manifest(review_dir: Path, source: dict, check_only: bool) -> list[str]:
    p = review_dir / "manifest.json"
    raw = p.read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    wanted = dict(manifest)
    wanted["source"] = source
    rendered = json.dumps(wanted, ensure_ascii=False, indent=2).encode("utf-8")
    if rendered == raw:
        return []
    if check_only:
        have = manifest.get("source")
        if have is None:
            return ["manifest.json has no `source` block; stamp it: python scripts/build_bundle.py <slug>"]
        stale = [f"manifest.json `source` is stale: {k} differs" for k in source if k != "content_commit" and have.get(k) != source[k]]
        return stale   # content_commit is informational and legitimately moves from PENDING_COMMIT to a sha after the commit
    p.write_bytes(rendered)
    return []


# ----------------------------------------------------------------------------------------------------------------
# build
# ----------------------------------------------------------------------------------------------------------------

def build(slug: str, check_only: bool) -> tuple[dict, list[str]]:
    review_dir = ROOT / "docs" / "reviews" / slug
    cert_bytes = (review_dir / "CERTIFICATE.json").read_bytes()
    cert = json.loads(cert_bytes.decode("utf-8"))
    problems: list[str] = []
    records = _read_json(ROOT / "cache" / slug / "records.json")
    reg = _regulatory_sources()
    acq = load_acquisitions(slug)
    if not acq["pubmed"]:
        problems.append("no PubMed acquisition objects under docs/acquisitions/<slug>/ -- run scripts/acquire_bundle_evidence.py first "
                        "(coverage_status must be backed by a preservation record, never declared)")

    artefacts, to_write = [], []
    for entry in enumerate_inputs(slug, cert):
        ref = entry["ref"]
        src = ROOT / ref
        if not src.is_file():
            problems.append(f"certificate input missing from the tree: {ref}")
            continue
        data = src.read_bytes()
        got = recompute(entry, data)
        if entry["declared"] is not None and got != entry["declared"]:
            problems.append(f"{ref}: tree bytes give {got}, certificate declares {entry['declared']} ({entry['role']})")
        row = {"ref": ref, "role": entry["role"], "bytes": len(data), "sha256": _sha256(data), "git_blob_sha1": _git_blob_sha1(data),
               "declared_digest": entry["declared"], "digest_method": entry["digest_method"]}
        if ref in NOT_IN_PACKAGE_LICENCE:
            row["state"] = "NOT_IN_PACKAGE_LICENCE"
            row["served_path"] = None
            row.update(NOT_IN_PACKAGE_LICENCE[ref])
            row["verification"] = "fetch obtain_from, confirm sha256 == this entry's sha256, then treat as served; the certificate digest is over those bytes"
            row["note"] = "PMC separates access from reuse: the reference and the verification method are exposed; redistribution is not"
        else:
            row["state"] = "SERVED"
            row["served_path"] = ref
            row["served_url"] = SITE_ROOT + ref
            dst = ROOT / "docs" / ref
            attr = _text_attr(_rel(dst))
            if attr != "unset":
                problems.append(f"docs/{ref}: git `text` attribute is '{attr}', not unset -- add a `-text` rule before mirroring")
            if dst.exists():
                if dst.read_bytes() != data:
                    if check_only:
                        problems.append(f"docs/{ref}: mirrored bytes differ from the certificate input")
                    else:
                        to_write.append((dst, data))
            elif check_only:
                problems.append(f"docs/{ref}: not mirrored")
            else:
                to_write.append((dst, data))
            for prefix, note in SERVED_LICENCE.items():
                if ref == prefix or ref.startswith(prefix):
                    row["licence"] = note
        artefacts.append(row)
    art_by_ref = {a["ref"]: a for a in artefacts}

    for f in acq["files"]:
        if _text_attr(f["path"]) != "unset":
            problems.append(f"{f['path']}: acquisition file is not -text")
    supporting = {f["path"].removeprefix("docs/"): f for f in acq["files"]}
    supporting["scripts/verify_bundle.py"] = {"path": "docs/scripts/verify_bundle.py"}

    if not problems:
        for dst, data in to_write:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)

    source = source_block(slug, review_dir)
    source.pop("_inconsistent")
    problems += stamp_manifest(review_dir, source, check_only=check_only or bool(problems))

    review = _read_json(review_dir / "review.json")
    if sha256_text(canonical_json(review_core(review))) != cert["review_sha256"]:
        problems.append("review.json does not hash to the certificate's review_sha256")
    if sha256_text(canonical_json({k: v for k, v in cert.items() if k != "release_sha256"})) != cert["release_sha256"]:
        problems.append("CERTIFICATE.json does not hash to its own release_sha256")

    docs = documents(slug, records, acq, art_by_ref, reg, review) if acq["pubmed"] else []
    docs_by_id = {d["document_id"]: d for d in docs}
    vrows, vmeta = verification_rows(slug, review, docs_by_id, art_by_ref, records)
    review_blob = _git_blob_sha1((review_dir / "review.json").read_bytes())
    for r in vrows:
        r["admission"]["analysis_identity_key"] = r["analysis_identity"]["analysis_identity_key"]
        r["admission"]["evidence_version"].update({"certificate_release_sha256": cert["release_sha256"], "review_blob": review_blob})
    aclaims = absence_claims(slug, review, docs_by_id)
    pooled = pooled_reference(review)
    compat = endpoint_compatibility(review, vrows)
    xcov = extraction_objects_coverage(slug, review, cert)
    binding = binding_states(review, {r["trial"]["id"] for r in vrows})
    regfacts = regulatory_facts(review, art_by_ref)
    for b in binding["rows"]:
        vr = next((r for r in vrows if r["trial"]["id"] == b["trial"]["id"] and b["primary"]), None)
        b["counted_in_admissible_rows"] = bool(vr and vr["admission"]["final"] == "ADMISSIBLE")
    walk = resolvability_walk(slug, art_by_ref, acq, supporting, reg)

    # the verifier must be fetchable from the surface the bundle is served from, byte-identical to the repository copy
    ver_src = ROOT / "scripts" / "verify_bundle.py"
    ver_dst = ROOT / "docs" / "scripts" / "verify_bundle.py"
    ver_bytes = ver_src.read_bytes()
    if not ver_dst.exists() or ver_dst.read_bytes() != ver_bytes:
        if check_only:
            problems.append("docs/scripts/verify_bundle.py is absent or differs from scripts/verify_bundle.py -- the verifier the bundle names must be served byte-identical")
        elif not problems:
            ver_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ver_src, ver_dst)
    if _text_attr("docs/scripts/verify_bundle.py") != "unset":
        problems.append("docs/scripts/verify_bundle.py is not -text")
    verifier_file = {"path": "docs/scripts/verify_bundle.py", "sha256": _sha256(ver_bytes), "bytes": len(ver_bytes), "role": "the verifier this bundle names; standard library only"}
    rec_raw = (ROOT / "cache" / slug / "records.json").read_bytes()
    digest_scopes = {
        "object": f"cache/{slug}/records.json",
        "note": "three independently reproducible digests over one file; a reader who applies the wrong one gets a mismatch and reports a defect that is not there",
        "scopes": [
            {"subject": "raw served bytes", "procedure": "sha256(bytes)", "value": _sha256(rec_raw), "appears_as": "artefacts[].sha256; verification_rows[].source.source_sha256; verified_*.json document_sha256"},
            {"subject": "whole file as JSON object", "procedure": "sha256(canonical JSON)", "value": sha256_text(canonical_json(json.loads(rec_raw))), "appears_as": "CERTIFICATE.json records_file_sha256"},
            {"subject": "obj['records'] only", "procedure": "sha256(canonical JSON)", "value": sha256_text(canonical_json(json.loads(rec_raw)["records"])), "appears_as": "CERTIFICATE.json retrieved_corpus_sha256; retrieval_ledger.json snapshot.records_sha256"},
        ],
    }

    review_files = []
    for name in sorted(os.listdir(review_dir)):
        p = review_dir / name
        if p.is_file() and name != "BUNDLE.json":
            b = p.read_bytes()
            review_files.append({"file": name, "served_path": f"reviews/{slug}/{name}", "served_url": f"{SITE_ROOT}reviews/{slug}/{name}",
                                 "bytes": len(b), "sha256": _sha256(b), "git_blob_sha1": _git_blob_sha1(b)})

    cov_counts = {}
    for d in docs:
        cov_counts[d["coverage_status"]["value"]] = cov_counts.get(d["coverage_status"]["value"], 0) + 1
    medr = reg["by_text"].get("outputs/handover/glp1_regulatory/208471Orig1s000MedR.pdf.txt") or {}
    n_served = sum(1 for a in artefacts if a["state"] == "SERVED")
    n_lic = sum(1 for a in artefacts if a["state"] == "NOT_IN_PACKAGE_LICENCE")
    bundle = {
        "schema_version": SCHEMA_VERSION,
        "format_revision": FORMAT_REVISION,
        "format_changelog": FORMAT_CHANGELOG,
        "slug": slug,
        "canonicalisation": CANONICALISATION,
        "selector_rule": SELECTOR_RULE,
        "eligibility_source": {"authoritative": f"cache/{slug}/families.json (certified: trial_family_map_sha256)",
                               "rendered_copy": f"reviews/{slug}/review.json trial_families (certified only as part of review_sha256)",
                               "rule": "a certificate consumer reads the certified copy; the rendered copy is cross-checked and a disagreement is reported"},
        "coordinates": COORDINATES,
        "digest_scopes": [digest_scopes],
        "purpose": "The input to an independent verifier: every object CERTIFICATE.json commits a digest to (declared digest, served path, "
                   "byte length); every evidential document in four immutable representations with the transforms named and a "
                   "preservation record where an acquisition is retained; every primary-pool row as source/span/endpoint/effect/"
                   "decision/admission objects whose predicates a stranger can recompute; every absence claim with the coverage_status "
                   "of the representation that was searched; and a walk from this file reporting every reference that still ends in "
                   "a digest with no body.",
        "package_semantics": {
            "complete": "all required files are present and valid (BagIt sense)",
            "valid": "every listed checksum verifies (BagIt sense)",
            "neither_means": "that the package contains complete scientific evidence -- see coverage_status per document and the resolvability walk",
            "producer_held_binary_archive": False,
            "originals_not_in_package": [
                {"document": "fda:FDA_NDA208471_MedR_2016 original PDF (208471Orig1s000MedR.pdf, 37,422,229 B)", "state": "NOT_IN_PACKAGE_PRODUCER_HELD",
                 "sha256_original": medr.get("document_sha256"),
                 "reacquire": "https://www.accessdata.fda.gov/drugsatfda_docs/nda/2016/208471Orig1s000MedR.pdf; sha256 must equal sha256_original",
                 "note": "the ELIXA CLINICAL (medical) review -- a different document from the FDA STATISTICAL review that supports the ELIXA "
                         "source conflict; the statistical review's original IS in the package"},
                *[{"document": ref, "state": "NOT_IN_PACKAGE_LICENCE", "sha256_original": art_by_ref[ref]["sha256"], "obtain_from": lic["obtain_from"],
                   "external_access_dependency": lic["external_access_dependency"]} for ref, lic in NOT_IN_PACKAGE_LICENCE.items() if ref in art_by_ref]],
            "origin_authentication": "a saved response and its hash establish what was saved, not that it came from the claimed publisher; "
                                     "each ACQUISITION manifest states its trust assumption",
            "independence": "copies produced from the same cached representation are not independent confirmations; where a publisher and an "
                            "indexing-service version differ, both are preserved and the discrepancy recorded (documents[*].preservation_record)",
            "immutability": "acquisition objects are append-only; a correction is a new dated directory; decisions keep the evidence they were made against",
            "digest_mismatch_policy": DIGEST_MISMATCH_POLICY,
        },
        "certificate_unmodified": True,
        "certificate": {"served_path": f"reviews/{slug}/CERTIFICATE.json", "bytes": len(cert_bytes), "sha256_of_file": _sha256(cert_bytes),
                        "git_blob_sha1": _git_blob_sha1(cert_bytes), "release_sha256": cert["release_sha256"],
                        "note": "left byte-identical; an external auditor has reproduced release_sha256 and analysis_code_sha256 from the listed inputs "
                                "with an isolated standard-library script, and that result must survive this bundle"},
        "source": source,
        "path_scheme": {"rule": "each `ref` is repository-root-relative exactly as the certificate spells it; the same bytes are served at "
                                "<site_root>/<ref> (from this file's directory: ../../<ref>)", "site_root": SITE_ROOT,
                        "byte_identity": "mirror and acquisition paths carry `-text` in .gitattributes so git never normalises line endings on checkin"},
        "vocabulary": VOCABULARY,
        "counts": {"certificate_inputs": len(artefacts), "served": n_served, "not_in_package_licence": n_lic,
                   "served_bytes": sum(a["bytes"] for a in artefacts if a["state"] == "SERVED"),
                   "acquisition_files": len(acq["files"]), "acquisition_bytes": sum(f["bytes"] for f in acq["files"]),
                   "documents": len(docs), "documents_by_coverage_status": cov_counts,
                   "primary_pool_rows": vmeta["k"], "admissible_rows": sum(1 for r in vrows if r["admission"]["final"] == "ADMISSIBLE"),
                   "migration_state_rows_in_primary_pool": sum(1 for r in vrows if r["admission"]["final"] == "MIGRATION_STATE_UNBOUND_LEGACY"),
                   "inadmissible_rows_in_primary_pool": sum(1 for r in vrows if r["admission"]["final"] == "INADMISSIBLE"),
                   "unbound_legacy_rows_rendered_anywhere": binding["counts"]["migration_state_unbound_legacy"],
                   "unbound_legacy_rows_inside_admissible_rows": sum(1 for b in binding["rows"] if b["binding_class"] != "BOUND" and b["counted_in_admissible_rows"]),
                   "absence_claims": len(aclaims),
                   "negative_claims_not_admissible": sum(1 for c in aclaims if c["claim_kind"] == "NEGATIVE" and c["negative_claim_admissible"] is False),
                   "resolvability": walk["edge_counts"]},
        "artefacts": artefacts,
        "acquisitions": acq["manifests"],
        "supporting_files": acq["files"] + [verifier_file],
        "documents": docs,
        "endpoint_compatibility": compat,
        "registered_estimand": registered_estimand(slug),
        "extraction_objects_coverage": xcov,
        "binding_states": binding,
        "regulatory_facts": regfacts,
        "verification_rows": vrows,
        "absence_claims": aclaims,
        "pooled_reference": pooled,
        "resolvability": walk,
        "review_files": review_files,
        "limits": LIMITS + [{
            "id": "L12_positive_refusals_unevaluated",
            "limit": (f"{sum(1 for c in aclaims if c['claim_kind'] == 'POSITIVE_REFUSAL')} of {len(aclaims)} absence claims are POSITIVE_REFUSAL and are "
                      f"carried as producer assertions: the bundle locates and evaluates NEGATIVE claims only. "
                      f"{sum(1 for c in aclaims if c['claim_kind'] == 'POSITIVE_REFUSAL' and c['not_evaluated_because'] and 'FDA' in c['not_evaluated_because'])} of them "
                      "are over non-PubMed documents (FDA text extractions) for which no contractual preservation parser exists; the remaining "
                      f"{sum(1 for c in aclaims if c['claim_kind'] == 'POSITIVE_REFUSAL' and c['not_evaluated_because'] and 'FDA' not in c['not_evaluated_because'])} "
                      "are over PubMed records whose refusal spans the bundle does not locate."),
        }],
        "canonical_json": "json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')) encoded as UTF-8",
        "verifier": {
            "served_path": "scripts/verify_bundle.py",
            "served_url": SITE_ROOT + "scripts/verify_bundle.py",
            "sha256": verifier_file["sha256"], "bytes": verifier_file["bytes"],
            "requirements": "Python 3.9+ standard library only; no harness import; run: python verify_bundle.py --url " + SITE_ROOT + " --slug " + slug,
            "checks": "every artefact and supporting-file digest; release_sha256 and review_sha256; every predicate of every verification row; the "
                      "selector rule; the asymmetric rule on every absence claim from a recomputed preservation record; pooled_reference.expected to 1e-9; "
                      "--corrupt <pmid> <limb> shows one corrupted limb makes exactly that row inadmissible",
            "does_not_check": "that any acquired or cached representation faithfully preserves the upstream publication (SOUL's cache is known to omit "
                              "the HbA1c entry range, follow-up and the safety sentence); that the source set is complete; that the clinical "
                              "interpretation is right; and the PRODUCTION admission path -- no production falsification test has been executed by "
                              "anyone; the verifier checks the bundle, not the producer's gate",
        },
        "regenerate": f"python scripts/acquire_bundle_evidence.py {slug} (only if new acquisitions are needed); commit any page rebuild; "
                      f"python scripts/build_bundle.py {slug}; tests/test_bundle.py refuses a stale bundle",
    }
    return bundle, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    bundle, problems = build(args.slug, check_only=args.check)
    out = ROOT / "docs" / "reviews" / args.slug / "BUNDLE.json"
    rendered = json.dumps(bundle, indent=1, ensure_ascii=False) + "\n"
    if args.check:
        if not out.exists():
            problems.append("BUNDLE.json absent")
        else:
            have, fresh = json.loads(out.read_text(encoding="utf-8")), json.loads(rendered)
            for obj in (have, fresh):
                (obj.get("source") or {}).pop("content_commit", None)
            if canonical_json(have) != canonical_json(fresh):
                problems.append("BUNDLE.json is stale (differs from a fresh build); regenerate: " + bundle["regenerate"])
    if problems:
        print("REFUSED -- bundle not written" if not args.check else "REFUSED", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1
    if not args.check:
        out.write_text(rendered, encoding="utf-8", newline="\n")
    c = bundle["counts"]
    print(f"{'OK' if args.check else 'WROTE'} {out.relative_to(ROOT).as_posix()} (schema {SCHEMA_VERSION}): {c['certificate_inputs']} inputs, "
          f"{c['served']} served, {c['not_in_package_licence']} licence-held; {c['documents']} documents {c['documents_by_coverage_status']}; "
          f"pool rows admissible {c['admissible_rows']}/{c['primary_pool_rows']}; negative claims not admissible {c['negative_claims_not_admissible']}; "
          f"resolvability {c['resolvability']}; content_commit {bundle['source']['content_commit'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
