"""Serve the evidence bundle a review's CERTIFICATE.json commits to -- without touching the certificate.

THE DEFECT THIS CLOSES (2026-09-19). docs/reviews/<slug>/CERTIFICATE.json commits SHA-256 digests to
cache/<slug>/records.json, verified_*.json, families.json, rob2.json and twelve held documents, but the served
site (GitHub Pages from docs/) carried none of them: probed from the Pages origin with cache:'no-store',
14 of 18 candidate URLs were 404. Three independent audits stalled at exactly that edge. A digest of a file
nobody can fetch is a promise, not a proof.

THE DESIGN. The certificate is left byte-identical (an external auditor has reproduced its release_sha256
with an isolated standard-library script; that result must survive). Every input the certificate names is
mirrored at docs/<repo-root-relative ref>, so the refs the certificate already carries resolve unmodified
against the site root, and a new BUNDLE.json at the review root lets a reader start there and reach every
object -- declared digest, served path, byte length -- without guessing a path. An input we may not
redistribute gets an explicit WITHHELD entry naming the reason, its digest and where the same bytes come
from, so "not served because we may not" is never confused with "not served because we forgot".

TWO IDENTITIES PER DOCUMENT (fourth audit, 2026-09-19). A verifier can prove "this quotation occurs in our
cache" while failing to prove "our cache faithfully preserves the cited upstream source": SOUL's cached result
span is stitched relative to the current PubMed abstract; REWIND's and Harmony's rendered spans have the
Lancet middle-dot decimals silently normalised. A single document_sha256 cannot express the difference between
the acquired original and a representation derived from it, so every artefact entry carries a `representation`
block naming which of the two it is, what it was derived from, the transform, and whether the original was
retained -- and where it was not, the entry says so instead of presenting the derived copy as the original.
The `value_index` closes the traversal value -> span -> representation -> document digest in one hop, and
records mechanically whether each rendered span is located VERBATIM, only after NORMALISATION, or NOT at all.

THE SERVED SURFACE HAS ITS OWN CLOCK. GitHub Pages serves through a CDN; cache:'no-store' bypasses the browser
cache only, and two readers can hold different versions of one URL at the same moment (measured: the same
manifest.json returned two review_sha256 values 32 minutes apart with no intervening commit). Nothing in the
served manifest tied bytes to a commit. This script stamps a `source` block into manifest.json (and BUNDLE.json)
carrying the git blob ids of the served files and the commit that introduced them, so a reader can compare
against the repository and tell a stale edge copy from the current one. The generating commit is NOT_RECORDED,
because the generator does not record it; build_utc records when, not from what, and is not repurposed.

THE TRAP. .gitattributes applies `* text=auto eol=lf` repo-wide and three held text exports carry CRLF.
A mirror added without a `-text` rule would be normalised on checkin and served off its digest -- a bundle
that looks complete and verifies as corrupt. This script refuses to write a mirror path whose `text`
attribute is not unset, and tests/test_bundle.py refuses the standard if that ever regresses.

Usage:  python scripts/build_bundle.py <slug>          (idempotent; rerun after any rebuild of the page)
        python scripts/build_bundle.py <slug> --check  (verify only; exit 1 on any drift, write nothing)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import certificate  # noqa: E402
from harness.canonical import canonical_json, review_core, sha256_text  # noqa: E402

SITE_ROOT = "https://mahmood726-cyber.github.io/meta-harness/"
REPO_URL = "https://github.com/mahmood726-cyber/meta-harness.git"
SCHEMA_VERSION = 2
GENERATED_FILES = ("review.json", "index.html", "CERTIFICATE.json", "REPRODUCTION.json")

# Inputs we hold but may not redistribute. Keyed by repo-root-relative ref; the value is the reason an
# auditor reads and the route to the same bytes. Anything not listed here is served.
WITHHELD = {
    "cache/glp1-ra-mace-t2d/ft_27295427.txt": {
        "reason": "PMC author manuscript (nihms809153; N Engl J Med 2016, LEADER). PMC licence text: 'This file is "
                  "available for text mining. It may also be used consistent with the principles of fair use under "
                  "the copyright law.' -- a text-mining permission, not a redistribution licence; the publisher's "
                  "copyright applies to the article text.",
        "obtain_from": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC4985288&retmode=xml",
        "identifiers": {"pmid": "27295427", "pmcid": "PMC4985288"},
    },
    "cache/glp1-ra-mace-t2d/ft_28910237.txt": {
        "reason": "PMC author manuscript (nihms-1856461; N Engl J Med 2017, EXSCEL). PMC licence text: 'This file is "
                  "available for text mining. It may also be used consistent with the principles of fair use under "
                  "the copyright law.' -- a text-mining permission, not a redistribution licence; the publisher's "
                  "copyright applies to the article text.",
        "obtain_from": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC9792409&retmode=xml",
        "identifiers": {"pmid": "28910237", "pmcid": "PMC9792409"},
    },
}

# Licence notes for served held documents whose redistribution rests on something a reader should be able to check.
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


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha1(data: bytes, lf_normalise: bool = False) -> str:
    if lf_normalise:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def _text_attr(path: str) -> str:
    """The effective `text` attribute for a repo path, as git will apply it on checkin ('unset' == -text)."""
    return _git("check-attr", "text", "--", path).rsplit(":", 1)[-1].strip()


def _rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


# ----------------------------------------------------------------------------------------------------------------
# certificate inputs
# ----------------------------------------------------------------------------------------------------------------

def enumerate_inputs(slug: str, cert: dict) -> list[dict]:
    """Every file the certificate's digests were computed from, exactly as harness.certificate.compute reads them.

    Each entry: ref (repo-root-relative), role (the certificate key it feeds), digest_method (how the certificate's
    value is derived from the file) and declared (the certificate's value, or None when the file is one of several
    inputs to a composite digest)."""
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
         "digest_method": "sha256 of canonical JSON",
         "declared": cert["trial_family_map_sha256"]},
        {"ref": _rel(cache / "rob2.json"), "role": "rob_object_sha256",
         "digest_method": "sha256 of canonical JSON",
         "declared": cert["rob_object_sha256"]},
        {"ref": _rel(ROOT / "topics" / f"{slug}.json"), "role": "config_sha256",
         "digest_method": "sha256 of canonical JSON",
         "declared": cert["config_sha256"]},
    ]
    extraction_paths = sorted(set(cache.glob("verified_*.json")) | set(cache.glob("*effect_type*.json")))
    for p in extraction_paths:
        entries.append({"ref": _rel(p), "role": "extraction_objects_sha256",
                        "digest_method": "one member of the canonical ref-to-JSON map {ref: parsed JSON} whose canonical JSON is hashed",
                        "declared": None})
    for ref, blob in cert["analysis_code_blobs"].items():
        if blob == certificate.NOT_PRESENT:
            continue
        entries.append({"ref": ref, "role": "analysis_code_sha256",
                        "digest_method": "Git blob SHA-1 of LF-normalised bytes: sha1(b'blob <len>\\0' + bytes); the map of these feeds analysis_code_sha256",
                        "declared": blob})
    for h in cert["held_documents"]:
        entries.append({"ref": h["ref"], "role": "held_documents",
                        "digest_method": "sha256 of exact file bytes",
                        "declared": h["sha256"]})
    return entries


def recompute(entry: dict, data: bytes) -> str | None:
    """The certificate's digest for this file, from the bytes about to be served. None for composite members."""
    role = entry["role"]
    if role == "protocol_text_sha256":
        text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        return sha256_text(text)
    if role in ("records_file_sha256", "retrieval_ledger_sha256", "trial_family_map_sha256",
                "rob_object_sha256", "config_sha256"):
        return sha256_text(canonical_json(json.loads(data.decode("utf-8"))))
    if role == "analysis_code_sha256":
        return _git_blob_sha1(data, lf_normalise=True)
    if role == "held_documents":
        return _sha256(data)
    return None


# ----------------------------------------------------------------------------------------------------------------
# two identities per document
# ----------------------------------------------------------------------------------------------------------------

def _regulatory_sources(slug: str) -> dict:
    """Map extracted-text ref -> its source record, and held-PDF ref -> its source record, from the source manifest."""
    path = ROOT / "outputs" / "handover" / "glp1_regulatory" / "regulatory_sources_glp1.json"
    by_text, by_pdf = {}, {}
    if not path.exists():
        return {"by_text": by_text, "by_pdf": by_pdf}
    src = json.loads(path.read_text(encoding="utf-8"))
    for s in src.get("sources", []):
        held = s.get("held") or {}
        text_ref = held.get("extracted_text") or s.get("extracted_text_path")
        pdf_ref = held.get("held_in_tree") or s.get("document_path")
        if text_ref:
            by_text[text_ref] = s
        if pdf_ref:
            by_pdf[pdf_ref] = s
    return {"by_text": by_text, "by_pdf": by_pdf}


def representation(ref: str, slug: str, records: dict, reg: dict) -> dict:
    """Which identity this file is: the acquired original, a representation derived from one, or an authored object.

    Every field here is either read from a source manifest we hold or is a statement of what was NOT retained;
    nothing asserts upstream fidelity that was not measured."""
    cache_prefix = f"cache/{slug}/"
    name = ref.rsplit("/", 1)[-1]

    if ref.startswith("cache/") and name.startswith("ft_"):
        pmid = name[3:-4]
        return {
            "kind": "ACQUIRED_AS_STORED",
            "description": "PMC efetch response body (JATS XML) as written to the cache by harness.fetch; no separate digest "
                           "was taken of the HTTP response at acquisition, so byte identity with what PMC served is asserted "
                           "by the storing code path, not proven",
            "acquired_from": f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=<pmcid for PMID {pmid}>&retmode=xml",
            "acquired_original": {"retained": True, "is_this_file": True, "acquisition_digest_recorded": False},
            "derived_representations": [],
            "upstream_identity": "NOT_PROVEN -- re-fetch from acquired_from and compare digests; PMC may re-render",
        }
    if ref == cache_prefix + "records.json":
        return {
            "kind": "DERIVED",
            "description": "projection of PubMed efetch XML: per record {id, id_type, title, abstract, pubtypes, year, journal, doi, "
                           "nct}; the abstract is the AbstractText sections joined as 'Label: text' with single spaces "
                           "(harness/fetch.py::_efetch). Also embeds comparator_fulltext (see that entry).",
            "acquired_from": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml (fetched_utc "
                             + str(records.get("fetched_utc")) + ")",
            "acquired_original": {"retained": False, "note": "the efetch XML response bodies were not retained and were not "
                                                             "digested at acquisition; this file is the only representation held"},
            "derived_representations": [{"ref": ref, "is_this_file": True,
                                         "transform": "XML -> field projection; AbstractText sections joined with labels"}],
            "upstream_identity": "NOT_PROVEN -- PubMed abstracts are revised upstream; a 2026-09-19 audit found the current "
                                 "PubMed abstract for PMID 40162642 (SOUL) contains clauses absent from this cached copy. "
                                 "'verified' on the page means located in THIS file, not in the publisher's document.",
        }
    if ref == cache_prefix + "aact_inputs.json":
        return {
            "kind": "DERIVED",
            "description": "header-keyed rows selected from a local AACT (ClinicalTrials.gov) snapshot, each row digested as "
                           "sha256(canonical_json(row)) inside the file (its own row_hash_method field)",
            "acquired_from": "AACT snapshot " + str(json.loads((ROOT / ref).read_text(encoding="utf-8")).get("snapshot")),
            "acquired_original": {"retained": False, "note": "the snapshot tables are not part of the bundle; per-row digests "
                                                             "inside the file are the only tie to them"},
            "derived_representations": [{"ref": ref, "is_this_file": True, "transform": "SQL row selection -> JSON"}],
            "upstream_identity": "NOT_PROVEN against the live registry; the snapshot date is stated",
        }
    if ref == cache_prefix + "comparator_fulltext.txt":
        oa = records.get("comparator_oa") or {}
        return {
            "kind": "DERIVED",
            "description": "prose text of the comparator meta-analysis (PMID " + str(records.get("comparator_pmid")) +
                           ") produced by harness.fetch._pmc_fulltext: PMC JATS XML -> body prose + structured tables "
                           "(harness/fulltext.py parse_pmc_xml/combined_text)",
            "acquired_from": "PMC efetch for the comparator PMID; open-access location per Unpaywall: " + str(oa.get("oa_url")),
            "acquired_original": {"retained": False, "note": "the PMC XML for the comparator was not retained; this text is the "
                                                             "only representation held"},
            "derived_representations": [{"ref": ref, "is_this_file": True,
                                         "transform": "JATS XML -> prose + table rows (whitespace collapsed)"}],
            "upstream_identity": "NOT_PROVEN -- the article is CC BY 4.0; re-derive from PMC and compare",
        }
    if ref in reg["by_text"]:
        s = reg["by_text"][ref]
        held = s.get("held") or {}
        pdf_ref = held.get("held_in_tree") or s.get("document_path")
        original = {
            "sha256": s.get("document_sha256"),
            "bytes": int(s["document_bytes"]) if s.get("document_bytes") else None,
            "acquired_from": s.get("query"),
            "fetched_utc": s.get("fetched_utc"),
            "acquisition_digest_recorded": True,
        }
        if pdf_ref:
            original.update({"retained": True, "ref": pdf_ref, "served": pdf_ref not in WITHHELD})
        else:
            original.update({"retained": True, "ref": None, "served": False,
                             "location": "off-repository raw archive, custody = author's machine (the source manifest "
                                         "regulatory_sources_glp1.json records the archive path; a local path is not "
                                         "reproduced here)",
                             "note": "original held OFF the repository (size); its digest was recorded at acquisition and is "
                                     "stated here so a reader who fetches the FDA document from acquired_from can check it, "
                                     "but the bytes are not served by this bundle"})
        return {
            "kind": "DERIVED",
            "description": "text extraction of an FDA PDF",
            "acquired_original": original,
            "derived_representations": [{"ref": ref, "is_this_file": True,
                                         "transform": "PDF -> text; the extraction tool is not recorded in "
                                                      "regulatory_sources_glp1.json (stated, not guessed)",
                                         "sha256_recorded_at_extraction": s.get("extracted_text_sha256")}],
            "upstream_identity": "the ORIGINAL's digest was recorded at acquisition; this derived text has no upstream "
                                 "counterpart to compare against",
        }
    if ref in reg["by_pdf"]:
        s = reg["by_pdf"][ref]
        held = s.get("held") or {}
        text_ref = held.get("extracted_text") or s.get("extracted_text_path")
        return {
            "kind": "ACQUIRED_AS_STORED",
            "description": "FDA document bytes as downloaded",
            "acquired_from": s.get("query"),
            "acquired_original": {"retained": True, "is_this_file": True, "acquisition_digest_recorded": True,
                                  "sha256_recorded_at_acquisition": s.get("document_sha256"),
                                  "fetched_utc": s.get("fetched_utc")},
            "derived_representations": [{"ref": text_ref, "transform": "PDF -> text (tool not recorded)"}] if text_ref else [],
            "upstream_identity": "digest recorded at acquisition by the acquiring agent and equal to the served bytes; "
                                 "independent check = re-fetch acquired_from and compare",
        }
    return {
        "kind": "AUTHORED",
        "description": "an object authored inside this project (configuration, protocol, analysis code, ledger, verified "
                       "extraction, family map, risk-of-bias object or source manifest); it is its own original and has "
                       "no upstream document",
        "acquired_original": {"is_this_file": True},
        "derived_representations": [],
        "upstream_identity": "NOT_APPLICABLE",
    }


# ----------------------------------------------------------------------------------------------------------------
# value -> span -> representation -> document digest, in one hop
# ----------------------------------------------------------------------------------------------------------------

_WS = re.compile(r"\s+")
_UNICODE_MAP = str.maketrans({
    "·": ".",   # middle dot (Lancet decimal)
    "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-",
    " ": " ", " ": " ", " ": " ",
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "≤": "<=", "≥": ">=",
})


def locate(span: str, hay: str) -> dict:
    """Mechanical ladder: where, if anywhere, does this rendered span occur in the document text?"""
    if not span:
        return {"match": "NO_SPAN"}
    if span in hay:
        return {"match": "VERBATIM"}
    steps = []
    s, h = _WS.sub(" ", span).strip(), _WS.sub(" ", hay)
    steps.append("whitespace collapsed")
    if s in h:
        return {"match": "NORMALISED", "normalisation": steps}
    s2, h2 = s.translate(_UNICODE_MAP), h.translate(_UNICODE_MAP)
    steps.append("unicode punctuation folded (middle dot -> '.', dashes -> '-', NBSP -> ' ', curly quotes)")
    if s2 in h2:
        return {"match": "NORMALISED", "normalisation": steps}
    return {"match": "NOT_LOCATED", "tried": steps}


def value_index(slug: str, review: dict, artefact_by_ref: dict, records: dict) -> list[dict]:
    """One entry per rendered per-trial row of every outcome, plus the pooled result per outcome."""
    rec_ref = f"cache/{slug}/records.json"
    rec_art = artefact_by_ref.get(rec_ref, {})
    by_pmid = {str(r.get("id")): r for r in records.get("records", [])}
    out = []
    for o in review.get("outcomes", []):
        result = o.get("result") or {}
        out.append({
            "entry": "POOLED",
            "outcome": o.get("name"),
            "primary": bool(o.get("primary")),
            "k": result.get("k"),
            "value": {k: result.get(k) for k in ("estimate", "ci_low", "ci_high", "tau2", "pi_low", "pi_high", "scale") if k in result},
            "derived_from": "the per-trial rows below, by the method stated in manifest.json (served_method); "
                            "the pooled numbers are recomputable from review.json alone",
        })
        for t in o.get("trials", []):
            trial_id = str(t.get("id") or "")
            pmid = trial_id.replace("PMID ", "")
            span = t.get("endpoint_result_span") or ""
            rec = by_pmid.get(pmid)
            docs = []
            if rec is not None:
                loc = locate(span, str(rec.get("abstract") or "") + "\n" + str(rec.get("title") or ""))
                docs.append({"document_ref": f"{rec_ref}#PMID-{pmid}", "document_sha256": rec_art.get("sha256"),
                             "served_path": rec_art.get("served_path"),
                             "representation": "DERIVED (PubMed abstract projection; upstream identity NOT_PROVEN)",
                             **loc})
            ft_ref = f"cache/{slug}/ft_{pmid}.txt"
            if ft_ref in artefact_by_ref and span:
                ft_art = artefact_by_ref[ft_ref]
                loc = locate(span, (ROOT / ft_ref).read_text(encoding="utf-8", errors="replace"))
                docs.append({"document_ref": ft_ref, "document_sha256": ft_art.get("sha256"),
                             "served_path": ft_art.get("served_path"), "state": ft_art.get("state"),
                             "representation": "ACQUIRED_AS_STORED (PMC JATS XML; upstream identity NOT_PROVEN)", **loc})
            if not docs:
                docs.append({"document_ref": None, "match": "NO_DOCUMENT_IN_BUNDLE"})
            best = "NO_SPAN" if not span else (
                "VERBATIM" if any(d.get("match") == "VERBATIM" for d in docs) else
                "NORMALISED" if any(d.get("match") == "NORMALISED" for d in docs) else "NOT_LOCATED")
            out.append({
                "entry": "TRIAL_ROW",
                "outcome_effect_id": t.get("outcome_effect_id"),
                "outcome": o.get("name"),
                "trial": {"label": t.get("label"), "id": trial_id},
                "value": {"scale": t.get("scale"), "effect": t.get("effect"), "ci_low": t.get("ci_low"), "ci_high": t.get("ci_high")},
                "page_labels": {"verified": t.get("verified"), "verify_basis": t.get("verify_basis"), "provenance": t.get("provenance")},
                "endpoint_result_span": span or None,
                "span_location": docs,
                "span_match": best,
                "what_verified_means_here": "the span was located in the served representation named above; that is a fact "
                                            "about our copy, not about the publisher's document (see the representation's "
                                            "upstream_identity)",
            })
    return out


# ----------------------------------------------------------------------------------------------------------------
# source identity of the served bytes
# ----------------------------------------------------------------------------------------------------------------

def source_block(slug: str, review_dir: Path) -> dict:
    """What can be established about which commit the served bytes come from -- named honestly.

    content_commit = the most recent commit in this history that changed any generated file of the review directory;
    checkable: `git rev-parse <content_commit>:docs/reviews/<slug>/review.json` equals the blob id below.
    generating_commit = NOT_RECORDED: the generator (harness.census.build_review_dir) does not record the commit it ran
    at, and a build committed after the fact has no such commit at build time. build_utc is left as it is (when, not
    from what)."""
    paths = [f"docs/reviews/{slug}/{n}" for n in GENERATED_FILES]
    content_commit = _git("log", "-1", "--format=%H", "--", *paths)
    blobs = {}
    inconsistent = []
    for n in GENERATED_FILES:
        p = review_dir / n
        if p.exists():
            blobs[n] = _git_blob_sha1(p.read_bytes())
            try:
                at_commit = _git("rev-parse", f"{content_commit}:docs/reviews/{slug}/{n}")
            except subprocess.CalledProcessError:
                at_commit = None
            if at_commit != blobs[n]:
                inconsistent.append(n)
    return {
        "content_commit": content_commit,
        "_inconsistent": inconsistent,
        "content_commit_meaning": "the most recent commit that changed any of " + ", ".join(GENERATED_FILES) +
                                  " in this review directory; NOT necessarily the commit the generator ran at",
        "generating_commit": "NOT_RECORDED",
        "generating_commit_meaning": "the generator does not record the commit it ran at; build_utc records when the build "
                                     "metadata was authored, not what the bytes were built from, and is not evidence of either",
        "served_blob_git_sha1": blobs,
        "how_to_check_currency": [
            "git ls-remote " + REPO_URL + " refs/heads/main   -> the current main commit",
            f"git rev-parse <that commit>:docs/reviews/{slug}/review.json   (or the GitHub contents API 'sha') -> the blob id main serves from",
            "git hash-object review.json   on the bytes you fetched -> must equal served_blob_git_sha1.review.json above AND the blob at main; "
            "if it equals the former but not the latter, you hold a stale edge copy or a superseded build",
        ],
        "served_copy_may_lag": STALENESS_NOTICE.replace("<slug>", slug),
    }


def stamp_manifest(review_dir: Path, source: dict, check_only: bool) -> list[str]:
    """Add/refresh the `source` block in manifest.json, preserving the generator's formatting (indent=2, no trailing
    newline, LF). manifest.json is not a certificate input and the gate only reads it, so this cannot move any digest
    the certificate commits to; review_sha256/html_sha256 are untouched."""
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
        return [f"manifest.json `source` is stale: {k} differs" for k in source if have.get(k) != source[k]] or \
               ["manifest.json differs from the stamped form (formatting)"]
    p.write_bytes(rendered)
    return []


# ----------------------------------------------------------------------------------------------------------------
# build
# ----------------------------------------------------------------------------------------------------------------

def build(slug: str, check_only: bool) -> tuple[dict, list[str]]:
    review_dir = ROOT / "docs" / "reviews" / slug
    cert_path = review_dir / "CERTIFICATE.json"
    cert_bytes = cert_path.read_bytes()
    cert = json.loads(cert_bytes.decode("utf-8"))
    problems: list[str] = []
    records = json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))
    reg = _regulatory_sources(slug)

    artefacts = []
    to_write: list[tuple[Path, bytes]] = []   # second pass: nothing touches docs/ until every input has been checked
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
        row = {
            "ref": ref,
            "role": entry["role"],
            "bytes": len(data),
            "sha256": _sha256(data),
            "git_blob_sha1": _git_blob_sha1(data),
            "declared_digest": entry["declared"],
            "digest_method": entry["digest_method"],
        }
        if ref in WITHHELD:
            row["state"] = "WITHHELD"
            row["served_path"] = None
            row.update(WITHHELD[ref])
            row["verification"] = ("fetch the bytes from obtain_from, confirm sha256 == this entry's sha256, "
                                   "then treat as served; the certificate digest above is over those bytes")
        else:
            row["state"] = "SERVED"
            row["served_path"] = ref
            row["served_url"] = SITE_ROOT + ref
            dst = ROOT / "docs" / ref
            attr = _text_attr(_rel(dst))
            if attr != "unset":
                problems.append(f"docs/{ref}: git `text` attribute is '{attr}', not unset -- a checkin could normalise "
                                f"line endings and serve bytes off the digest; add a `-text` rule before mirroring")
            if dst.exists():
                served = dst.read_bytes()
                if served != data:
                    if check_only:
                        problems.append(f"docs/{ref}: mirrored bytes differ from the certificate input ({len(served)} vs {len(data)} B)")
                    else:
                        to_write.append((dst, data))
            elif check_only:
                problems.append(f"docs/{ref}: not mirrored")
            else:
                to_write.append((dst, data))
            for prefix, note in SERVED_LICENCE.items():
                if ref == prefix or ref.startswith(prefix):
                    row["licence"] = note
        row["representation"] = representation(ref, slug, records, reg)
        artefacts.append(row)

    # Representation cross-checks: a derived text whose original we hold must point at an original whose served bytes
    # carry the digest the source manifest recorded -- otherwise the two-identity claim is decoration.
    by_ref = {a["ref"]: a for a in artefacts}
    for a in artefacts:
        rep = a["representation"]
        orig = rep.get("acquired_original") or {}
        if rep["kind"] == "DERIVED" and orig.get("ref"):
            o = by_ref.get(orig["ref"])
            if o is None:
                problems.append(f"{a['ref']}: derived from {orig['ref']}, which is not a certificate input")
            elif orig.get("sha256") and o["sha256"] != orig["sha256"]:
                problems.append(f"{a['ref']}: source manifest says original {orig['ref']} is {orig['sha256'][:12]}..., served bytes are {o['sha256'][:12]}...")
        if rep["kind"] == "ACQUIRED_AS_STORED":
            rec = orig.get("sha256_recorded_at_acquisition")
            if rec and rec != a["sha256"]:
                problems.append(f"{a['ref']}: acquisition digest {rec[:12]}... != served bytes {a['sha256'][:12]}...")

    if not problems:
        for dst, data in to_write:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)

    source = source_block(slug, review_dir)
    inconsistent = source.pop("_inconsistent")
    if inconsistent:
        problems.append("content_commit " + source["content_commit"][:12] + " does not hold the served bytes of "
                        + ", ".join(inconsistent) + " -- the rebuild is not committed yet; commit it, then stamp "
                        "(a stamp must name a commit that contains what it describes)")
    problems += stamp_manifest(review_dir, source, check_only=check_only or bool(problems))

    review_files = []
    for name in sorted(os.listdir(review_dir)):
        p = review_dir / name
        if p.is_file() and name != "BUNDLE.json":
            b = p.read_bytes()
            review_files.append({"file": name, "served_path": f"reviews/{slug}/{name}",
                                 "served_url": f"{SITE_ROOT}reviews/{slug}/{name}",
                                 "bytes": len(b), "sha256": _sha256(b), "git_blob_sha1": _git_blob_sha1(b)})

    review = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
    derived = {
        "retrieved_corpus_sha256": "sha256(canonical_json(records.json['records']))",
        "search_query_sha256": "sha256(canonical_json([{source_id, query} for each of retrieval_ledger.json['sources'], in order]))",
        "screening_ledger_sha256": "sha256(canonical_json(review.json['screening']))",
        "extraction_objects_sha256": "sha256(canonical_json({ref: parsed JSON for each extraction_objects member, keyed by ref}))",
        "analysis_code_sha256": "sha256(canonical_json(analysis_code_blobs)) -- the map exactly as printed in the certificate, NOT_PRESENT included",
        "review_sha256": "sha256(canonical_json(review.json with the top-level key 'reproduction' removed))",
        "manuscript_sha256": "sha256 of UTF-8 bytes of harness.manuscript.render(review) at the source commit; the renderer is "
                             "harness/manuscript.py in the repository, not a served file -- an auditor recomputes it from a checkout",
        "release_sha256": "sha256(canonical_json(certificate with the key 'release_sha256' removed))",
    }
    # Two derived digests are cheap to prove from served bytes alone; assert them here so the bundle never claims
    # an equality it did not check.
    if sha256_text(canonical_json(review_core(review))) != cert["review_sha256"]:
        problems.append("review.json does not hash to the certificate's review_sha256")
    body = {k: v for k, v in cert.items() if k != "release_sha256"}
    if sha256_text(canonical_json(body)) != cert["release_sha256"]:
        problems.append("CERTIFICATE.json does not hash to its own release_sha256")

    vindex = value_index(slug, review, by_ref, records)
    match_counts = {}
    for v in vindex:
        if v["entry"] == "TRIAL_ROW":
            match_counts[v["span_match"]] = match_counts.get(v["span_match"], 0) + 1

    n_served = sum(1 for a in artefacts if a["state"] == "SERVED")
    n_withheld = sum(1 for a in artefacts if a["state"] == "WITHHELD")
    bundle = {
        "schema_version": SCHEMA_VERSION,
        "slug": slug,
        "purpose": "Every object CERTIFICATE.json commits a digest to, with its declared digest, served path and byte "
                   "length -- so a reader can start here and reach each one without guessing a path, and can tell "
                   "'not served because we may not' (WITHHELD, reason given) from 'not served because we forgot' "
                   "(which this file makes impossible: every certificate input appears below, in one state or the other). "
                   "Each artefact carries two identities where two exist: the acquired original and the representation "
                   "derived from it, with the transform named; value_index goes from a rendered value to its document "
                   "digest in one hop and states whether the rendered span is verbatim in that document.",
        "certificate_unmodified": True,
        "certificate": {
            "served_path": f"reviews/{slug}/CERTIFICATE.json",
            "bytes": len(cert_bytes),
            "sha256_of_file": _sha256(cert_bytes),
            "git_blob_sha1": _git_blob_sha1(cert_bytes),
            "release_sha256": cert["release_sha256"],
            "note": "left byte-identical; an external auditor has reproduced release_sha256 and analysis_code_sha256 "
                    "from the listed inputs with an isolated standard-library script, and that result must survive this bundle",
        },
        "source": source,
        "path_scheme": {
            "rule": "each `ref` is repository-root-relative exactly as the certificate spells it; the same bytes are served "
                    "at <site_root>/<ref> (from this file's directory: ../../<ref>)",
            "site_root": SITE_ROOT,
            "byte_identity": "mirror paths carry `-text` in .gitattributes so git never normalises line endings on "
                             "checkin; three held text exports contain CRLF and would otherwise be served off their digest",
        },
        "representation_kinds": {
            "ACQUIRED_AS_STORED": "the bytes as received from the upstream source; whether a digest was taken at acquisition is stated",
            "DERIVED": "a representation produced from an acquired original by a named transform; whether the original was retained, "
                       "and where, is stated; if it was not retained the entry says so rather than presenting the derived copy as the original",
            "AUTHORED": "an object authored in this project; it is its own original",
        },
        "counts": {"certificate_inputs": len(artefacts), "served": n_served, "withheld": n_withheld,
                   "served_bytes": sum(a["bytes"] for a in artefacts if a["state"] == "SERVED"),
                   "value_index_trial_rows_by_span_match": match_counts},
        "artefacts": artefacts,
        "review_files": review_files,
        "value_index": vindex,
        "derived_digests": derived,
        "canonical_json": "json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')) encoded as UTF-8",
        "regenerate": f"python scripts/build_bundle.py {slug}   (after any rebuild of the page; tests/test_bundle.py refuses a stale bundle)",
    }
    return bundle, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("--check", action="store_true", help="verify only; write nothing")
    args = ap.parse_args(argv)
    bundle, problems = build(args.slug, check_only=args.check)
    out = ROOT / "docs" / "reviews" / args.slug / "BUNDLE.json"
    rendered = json.dumps(bundle, indent=1, ensure_ascii=False) + "\n"
    if args.check:
        if not out.exists():
            problems.append("BUNDLE.json absent")
        elif canonical_json(json.loads(out.read_text(encoding="utf-8"))) != canonical_json(json.loads(rendered)):
            problems.append("BUNDLE.json is stale (differs from a fresh build); regenerate: " + bundle["regenerate"])
    if problems:
        print("REFUSED -- bundle not written" if not args.check else "REFUSED", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1
    if not args.check:
        out.write_text(rendered, encoding="utf-8", newline="\n")
    c = bundle["counts"]
    print(f"{'OK' if args.check else 'WROTE'} {out.relative_to(ROOT).as_posix()}: {c['certificate_inputs']} certificate inputs, "
          f"{c['served']} served ({c['served_bytes']:,} B), {c['withheld']} withheld with reason; "
          f"value_index span matches {c['value_index_trial_rows_by_span_match']}; content_commit {bundle['source']['content_commit'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
