"""Deterministic evidence custody certificate. No acquisition and no writes on verification.

JSON uses canonical_json; held documents use exact bytes (including text newlines).
Git blob identities use LF-normalized source bytes, matching Git's repository form.
The certificate lives outside the review core, in reproduction, to avoid a hash cycle.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

from .canonical import canonical_json, review_sha256, sha256_text
from . import manuscript

ROOT = Path(__file__).resolve().parents[1]
NOT_PRESENT = "NOT_PRESENT"
CODE = ("harness/synth.py", "harness/pipeline.py", "harness/grade.py",
        "harness/effect_type.py", "scripts/build_topic.py")
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


def _require_retained_document_digests(extraction):
    """A rebuild cannot erase a committed row's existing source binding.

    Compare identities, not list offsets. Legacy rows that never carried a digest
    remain outside this deletion check; removal of an entire row is a separate gate.
    The anchor is the running repository's HEAD, including for scratch input roots.
    """
    import subprocess
    repo = Path(__file__).resolve().parents[1]
    for ref, current in extraction.items():
        if Path(ref).name not in ('verified_arms.json', 'verified_effects.json'):
            continue
        try:
            source = subprocess.run(['git', '-C', str(repo), 'show', 'HEAD:' + ref],
                                    capture_output=True, encoding='utf-8')
            if source.returncode:
                tracked = subprocess.run(['git', '-C', str(repo), 'ls-files', '--', ref],
                                         capture_output=True, encoding='utf-8', check=True)
                if not tracked.stdout.strip():
                    continue  # new input with no committed deletion anchor
                raise ValueError('DOCUMENT_DIGEST_SNAPSHOT_UNAVAILABLE: ' + ref)
            baseline = json.loads(source.stdout)
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
            raise ValueError('DOCUMENT_DIGEST_SNAPSHOT_UNAVAILABLE: ' + ref) from exc
        for pid, value in current.items():
            old = baseline.get(pid, [])
            old_rows = old if isinstance(old, list) else [old]
            bound = {row.get('outcome') for row in old_rows if row.get('document_sha256')}
            for row in value if isinstance(value, list) else [value]:
                if row.get('outcome') in bound and not row.get('document_sha256'):
                    raise ValueError(f'MISSING_DOCUMENT_SHA256: {ref}/{pid}/{row.get("outcome")}')


def _verify_document_bindings(slug, saved):
    """Check exact bytes, including JSON whitespace excluded by canonical hashing."""
    bindings = [(d['ref'], d['sha256']) for d in saved.get('held_documents', [])]
    for name in ('verified_arms.json', 'verified_effects.json'):
        path = _safe(f'cache/{slug}/{name}')
        if not path.is_file():
            continue  # the extraction-object certificate comparison catches deletion
        for value in _json(path).values():
            for row in value if isinstance(value, list) else [value]:
                if row.get('document_sha256'):
                    ref = (row.get('document_ref') or '').split('#')[0]
                    if not ref:
                        raise ValueError(f'MISSING_DOCUMENT_REF: {name}/{row.get("outcome")}')
                    # Regulatory transcriptions distinguish the PDF digest from its text digest.
                    bindings.append((ref, row.get('extracted_text_sha256') or row['document_sha256']))
    for ref, digest in bindings:
        path = _safe(ref)
        if not path.is_file():
            raise ValueError('HELD_DOCUMENT_MISSING: ' + ref)
        if _file_hash(path) != digest:
            raise ValueError('DOCUMENT_SHA256_MISMATCH: ' + ref)


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
    _require_retained_document_digests(extraction)
    family = cache / "families.json"
    blobs = {}
    for ref in CODE:
        path = ROOT / ref
        if not path.exists() and ref == "harness/effect_type.py":
            blobs[ref] = NOT_PRESENT
            continue
        data = path.read_bytes().replace(b"\r\n", b"\n")
        blobs[ref] = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
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
            "analysis_code_sha256": "canonical analysis_code_blobs map; values are Git SHA-1 blob identities of LF-normalized working source, optional missing file = NOT_PRESENT",
            "manuscript_sha256": "UTF-8 bytes of harness.manuscript.render(review), including its reproduction context",
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
        _verify_document_bindings(manifest['slug'], saved)
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
