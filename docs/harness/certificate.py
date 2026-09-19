"""Deterministic evidence custody certificate. No acquisition and no writes on verification.

JSON uses canonical_json; held documents use exact bytes (including text newlines).
Git blob identities use LF-normalized source bytes, matching Git's repository form.
The certificate lives outside the review core, in reproduction, to avoid a hash cycle.

The analysis code map is DERIVED, never listed by hand: it is the static import closure
of the declared ROOTS (harness.code_closure). A hand-written tuple of five files drifted
from the code that decides verdicts -- the endpoint binder, the publication gate, the
manuscript renderer, the canonicalizer that computes every digest here, and this builder
-- so a swapped implementation of any of them produced a byte-identical certificate, and
a fourth independent audit rightly refused to let a checksum success read as a safeguard
success. Pinning this file creates no cycle: a blob identity of source bytes does not
depend on the certificate's contents.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

from .canonical import canonical_json, review_sha256, sha256_text
from .code_closure import closure
from . import manuscript

ROOT = Path(__file__).resolve().parents[1]
NOT_PRESENT = "NOT_PRESENT"
# Entry points whose import closure is the code that builds, renders, gates and verifies a page.
ROOTS = ("scripts/build_topic.py", "harness/pipeline.py", "harness/manuscript.py",
         "harness/page.py", "harness/gate.py", "harness/certificate.py",
         "scripts/reproduce_review.py")
# Declared names that may legitimately be absent; recorded as NOT_PRESENT, never dropped.
OPTIONAL = ("harness/effect_type.py",)
REF = re.compile(r"(?:cache|outputs)/[^\s\"'<>(),;]+\.(?:json|txt|pdf)")


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hash(obj):
    return sha256_text(canonical_json(obj))


def _file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ref(path):
    return path.relative_to(ROOT).as_posix()


def _safe(ref):
    path = (ROOT / ref).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f"certificate input escapes bundle: {ref}")
    return path


def _held(cache, review, objects):
    paths = set(cache.glob("ft_*.txt")) | set(cache.glob("aact_*.json"))
    # Follow explicit local source refs and their source manifest, including PDF/text pairs.
    pending = [review, *objects]
    visited = set()
    while pending:
        obj = pending.pop()
        for ref in REF.findall(canonical_json(obj)):
            if ref in visited:
                continue
            visited.add(ref)
            path = _safe(ref)
            if not path.is_file():
                # Non-document JSON refs can describe unavailable historical artefacts.
                if path.suffix in (".txt", ".pdf"):
                    raise ValueError(f"held document missing: {ref}")
                continue
            if path.suffix in (".txt", ".pdf") or path.name.startswith("aact_"):
                paths.add(path)
            if path.suffix == ".json":
                pending.append(_json(path))
            if ref.startswith("outputs/"):
                for source_manifest in path.parent.glob("*sources*.json"):
                    if _ref(source_manifest) not in visited:
                        visited.add(_ref(source_manifest))
                        paths.add(source_manifest)
                        pending.append(_json(source_manifest))
    return [{"ref": _ref(p), "sha256": _file_hash(p)}
            for p in sorted(paths, key=_ref)]


def _blob_sha1(path):
    """Git blob identity of LF-normalized source bytes; stdlib only, so an auditor without
    git recomputes it, and equal to `git hash-object` under the repository's text=auto."""
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _code_blobs():
    """Blob identity of every in-tree module the ROOTS reach, plus NOT_PRESENT for any
    declared root or optional module that is absent. Absence is recorded, never dropped."""
    blobs = {}
    for ref in closure(ROOTS, ROOT):
        blobs[ref] = _blob_sha1(ROOT / ref)
    for ref in (*ROOTS, *OPTIONAL):
        if ref not in blobs:
            blobs[ref] = NOT_PRESENT
    return dict(sorted(blobs.items()))


def _scope(blobs):
    """What the code map covers and what it does not, in terms a reader can act on."""
    unreached = sorted("harness/" + p.name for p in (ROOT / "harness").glob("*.py")
                       if "harness/" + p.name not in blobs)
    pinned = sorted(k for k, v in blobs.items() if v != NOT_PRESENT)
    absent = sorted(k for k, v in blobs.items() if v == NOT_PRESENT)
    return {
        "method": ("analysis_code_blobs is the static import closure (ast; module-level and "
                   "function-local import statements, relative and absolute) of the roots, "
                   "restricted to modules that resolve to a file under harness/ or scripts/. "
                   "Nothing in the map is listed by hand. Values are Git SHA-1 blob identities: "
                   "sha1('blob ' + len + NUL + bytes) over the file with CRLF normalised to LF, "
                   "recomputable with `git hash-object -- <path>` at the anchoring commit."),
        "roots": list(ROOTS),
        "covers": (f"{len(pinned)} in-tree modules: the topic build (scripts/build_topic.py), the "
                   "pipeline that computes every effect and its endpoint binding, the page and "
                   "manuscript renderers, the two-limb publication gate, the canonical JSON and "
                   "SHA-256 routines every digest in this certificate is computed with, this "
                   "certificate builder, and the replay driver CI runs against it. A change of one "
                   "byte in any of them moves analysis_code_sha256 and release_sha256."),
        "declared_but_absent": absent,
        "not_covered": {
            "in_tree_modules_not_imported_by_any_root": unreached,
            "why": ("not reached from any root, so not part of building, rendering, gating or "
                    "replaying this page: repository-level standard limbs run by "
                    "scripts/verify_all.py on the whole tree (fix-state ledger, honest ratchet, "
                    "held-out leak detector, served-artefact leak scan, search completeness), the "
                    "search_v2 acquisition engine -- whose blob the search-completeness limb pins to "
                    "the sealed measurement, not this certificate -- and adapters or stages outside "
                    "the default build path. They are identified by the anchoring commit, not here."),
            "interpreter_and_packages": ("the Python interpreter, its standard library and third-party packages (scipy on "
                                         "the analysis path; openpyxl and sentence_transformers on "
                                         "optional paths) are not pinned by this certificate. Their "
                                         "effect is bounded by CI, which replays every page on a fresh "
                                         "install and refuses a byte difference; it is not bounded by "
                                         "a digest here."),
            "dynamic_imports": ("one dynamic import exists on the covered path "
                                "(harness/acquisition.py resolves a source adapter by name for "
                                "acquisition-time provenance); every adapter it can name lives under "
                                "harness/ and is reached statically. importlib.metadata is queried "
                                "for package versions only."),
            "data_read_by_code": ("the certificate pins code by blob and inputs by the other "
                                  "*_sha256 fields; a non-Python file under harness/ would be "
                                  "neither and is listed here if one exists."),
            "non_python_files_under_harness": sorted(
                "harness/" + p.name for p in (ROOT / "harness").iterdir()
                if p.is_file() and p.suffix != ".py"),
        },
        "pins_bytes_not_self_reports": (
            "the map binds the BYTES of each module at the anchoring commit. It does not vouch for "
            "what any pinned component's own status fields say about themselves: a status value "
            "carried in the review or its cache (for example a span_location_check of OWED, or a "
            "REASON_TRUE on an absence row) is data recorded at build time and is covered as bytes by "
            "review_sha256 or extraction_objects_sha256, but this certificate does not assert that "
            "such a field is current, true of the implementation, or wired to code that enforces it. "
            "An OWED field can be stale in either direction. Whether a pinned check is in fact wired "
            "is established only by exercising the pinned bytes at the pinned commit, never by "
            "reading the field."),
        "how_to_use": ("bind a verdict to this certificate by release_sha256; check that "
                       "analysis_code_blobs[path] equals `git hash-object -- path` at the commit "
                       "you audited for every path you exercised, and that the path is in the map. "
                       "A path missing from the map is a finding against the map, not a pass."),
    }


def compute(slug, review, protocol_sha):
    """Re-read each listed input; fail closed on absent required files or corpus drift."""
    if Path(slug).name != slug or slug in (".", ".."):
        raise ValueError("invalid certificate slug")
    cache = ROOT / "cache" / slug
    records = _json(cache / "records.json")
    ledger = _json(cache / "retrieval_ledger.json")
    corpus_sha = _hash(records["records"])
    if corpus_sha != ledger["snapshot"]["records_sha256"]:
        raise ValueError("retrieved corpus differs from retrieval ledger records_sha256")
    protocol = ROOT / "protocols" / (slug + ".md")
    if not protocol.exists():
        protocol = ROOT / "PREREGISTRATION_v2.md"
        if slug not in protocol.read_text(encoding="utf-8"):
            raise ValueError("protocol absent from batch registration")
    extraction_paths = sorted(set(cache.glob("verified_*.json")) |
                              set(cache.glob("*effect_type*.json")))
    extraction = {_ref(p): _json(p) for p in extraction_paths}
    family = cache / "families.json"
    blobs = _code_blobs()
    queries = [{"source_id": s["source_id"], "query": s["query"]}
               for s in ledger["sources"]]
    cert = {
        "schema_version": 1,
        "slug": slug,
        "protocol_sha": protocol_sha,
        "protocol_text_sha256": sha256_text(protocol.read_text(encoding="utf-8")),
        "search_query_sha256": _hash(queries),
        "retrieved_corpus_sha256": corpus_sha,
        "records_file_sha256": _hash(records),
        "retrieval_ledger_sha256": _hash(ledger),
        "screening_ledger_sha256": _hash(review["screening"]),
        "extraction_objects_sha256": _hash(extraction),
        "trial_family_map_sha256": _hash(_json(family)) if family.exists() else NOT_PRESENT,
        "rob_object_sha256": _hash(_json(cache / "rob2.json")),
        "held_documents": _held(cache, review, [ledger, records, *extraction.values()]),
        "config_sha256": _hash(_json(ROOT / "topics" / (slug + ".json"))),
        "analysis_code_sha256": _hash(blobs),
        "analysis_code_blobs": blobs,
        "certificate_scope": _scope(blobs),
        "manuscript_sha256": sha256_text(manuscript.render(review)),
        "review_sha256": review_sha256(review),
        "hash_inputs": {
            "protocol_sha": "registration/build anchor Git commit (SHA-1, not a SHA-256 or prospective-registration claim)",
            "protocol_text_sha256": _ref(protocol) + " UTF-8 text, universal newlines",
            "search_query_sha256": "canonical ordered [{source_id, query}] from retrieval_ledger.json; query strings verbatim",
            "retrieved_corpus_sha256": "canonical records.json['records']; equals retrieval_ledger.json snapshot.records_sha256",
            "records_file_sha256": "canonical entire cache/<slug>/records.json",
            "retrieval_ledger_sha256": "canonical entire retrieval_ledger.json (including any raw-index digest)",
            "screening_ledger_sha256": "canonical review.json['screening']",
            "extraction_objects_sha256": "canonical ref-to-JSON map: " + ", ".join(extraction),
            "trial_family_map_sha256": _ref(family) + " canonical JSON, else NOT_PRESENT",
            "rob_object_sha256": _ref(cache / "rob2.json") + " canonical JSON",
            "held_documents": "SHA-256 of exact file bytes at each bundle-relative ref; all topic ft_*.txt/aact_*.json plus referenced held documents and source-manifest PDF/text pairs",
            "config_sha256": "canonical topics/<slug>.json",
            "analysis_code_sha256": "canonical analysis_code_blobs map; keys are the static import closure of certificate_scope.roots (harness.code_closure), values are Git SHA-1 blob identities of LF-normalized working source, declared root or optional module missing = NOT_PRESENT",
            "certificate_scope": "prose and derived lists stating what analysis_code_blobs covers and what it does not; part of the certificate, so a change to the stated scope is a release change",
            "manuscript_sha256": "UTF-8 bytes of harness.manuscript.render(review), including its reproduction context; the renderer's own bytes are pinned at analysis_code_blobs['harness/manuscript.py']",
            "review_sha256": "canonical review core (excludes reproduction)",
            "release_sha256": "canonical entire certificate excluding only release_sha256",
        },
    }
    cert["release_sha256"] = _hash(cert)
    return cert


def verify(review_dir, review=None, protocol_sha=None):
    """Return refusal reasons, comparing to the saved certificate without rewriting it."""
    directory = Path(review_dir)
    try:
        saved = _json(directory / "CERTIFICATE.json")
        if not isinstance(saved, dict):
            raise ValueError("certificate must be a JSON object")
        review = review if review is not None else _json(directory / "review.json")
        manifest = _json(directory / "manifest.json")
        expected = compute(manifest["slug"], review, protocol_sha or manifest["protocol_sha"])
        if canonical_json(saved) != canonical_json(expected):
            return [f"CERTIFICATE.json release_sha256 mismatch: recomputed {expected['release_sha256']} vs saved {saved.get('release_sha256')}"]
        attached = (review.get("reproduction") or {}).get("certificate")
        if canonical_json(attached) != canonical_json(saved):
            return ["CERTIFICATE.json differs from rendered reproduction certificate"]
        return []
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"CERTIFICATE.json release_sha256 could not be verified: {exc}"]


def render(cert):
    if not cert:
        return ""
    e = html.escape
    ordered = {"release_sha256": cert["release_sha256"],
               **{k: v for k, v in cert.items() if k != "release_sha256"}}
    return ("<section id='evidence-certificate' class='audit-block'><h2>Evidence certificate</h2>"
            f"<p><strong>release_sha256</strong> <code style='overflow-wrap:anywhere'>{e(cert['release_sha256'])}</code></p>"
            "<p>an auditor with the bundle recomputes release_sha256 from the listed inputs</p>"
            "<p><a href='CERTIFICATE.json'>Download CERTIFICATE.json</a></p>"
            f"<pre>{e(json.dumps(ordered, ensure_ascii=False, indent=2))}</pre></section>")
