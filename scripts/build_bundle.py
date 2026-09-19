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
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import certificate  # noqa: E402
from harness.canonical import canonical_json, review_core, sha256_text  # noqa: E402

SITE_ROOT = "https://mahmood726-cyber.github.io/meta-harness/"
SCHEMA_VERSION = 1

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


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    data = data.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _text_attr(path: str) -> str:
    """The effective `text` attribute for a repo path, as git will apply it on checkin ('unset' == -text)."""
    out = subprocess.run(["git", "check-attr", "text", "--", path], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return out.rsplit(":", 1)[-1].strip()


def _head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def _rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


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
        return _git_blob_sha1(data)
    if role == "held_documents":
        return _sha256(data)
    return None


def build(slug: str, check_only: bool) -> tuple[dict, list[str]]:
    review_dir = ROOT / "docs" / "reviews" / slug
    cert_path = review_dir / "CERTIFICATE.json"
    cert_bytes = cert_path.read_bytes()
    cert = json.loads(cert_bytes.decode("utf-8"))
    problems: list[str] = []

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
        artefacts.append(row)

    if not problems:
        for dst, data in to_write:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)

    review_files = []
    for name in sorted(os.listdir(review_dir)):
        p = review_dir / name
        if p.is_file() and name != "BUNDLE.json":
            b = p.read_bytes()
            review_files.append({"file": name, "served_path": f"reviews/{slug}/{name}",
                                 "served_url": f"{SITE_ROOT}reviews/{slug}/{name}",
                                 "bytes": len(b), "sha256": _sha256(b)})

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

    n_served = sum(1 for a in artefacts if a["state"] == "SERVED")
    n_withheld = sum(1 for a in artefacts if a["state"] == "WITHHELD")
    bundle = {
        "schema_version": SCHEMA_VERSION,
        "slug": slug,
        "purpose": "Every object CERTIFICATE.json commits a digest to, with its declared digest, served path and byte "
                   "length -- so a reader can start here and reach each one without guessing a path, and can tell "
                   "'not served because we may not' (WITHHELD, reason given) from 'not served because we forgot' "
                   "(which this file makes impossible: every certificate input appears below, in one state or the other).",
        "certificate_unmodified": True,
        "certificate": {
            "served_path": f"reviews/{slug}/CERTIFICATE.json",
            "bytes": len(cert_bytes),
            "sha256_of_file": _sha256(cert_bytes),
            "release_sha256": cert["release_sha256"],
            "note": "left byte-identical; an external auditor has reproduced release_sha256 and analysis_code_sha256 "
                    "from the listed inputs with an isolated standard-library script, and that result must survive this bundle",
        },
        "path_scheme": {
            "rule": "each `ref` is repository-root-relative exactly as the certificate spells it; the same bytes are served "
                    "at <site_root>/<ref> (from this file's directory: ../../<ref>)",
            "site_root": SITE_ROOT,
            "source_commit": _head() + "  (the commit whose tree the mirrored bytes were copied from)",
            "byte_identity": "mirror paths carry `-text` in .gitattributes so git never normalises line endings on "
                             "checkin; three held text exports contain CRLF and would otherwise be served off their digest",
        },
        "counts": {"certificate_inputs": len(artefacts), "served": n_served, "withheld": n_withheld,
                   "served_bytes": sum(a["bytes"] for a in artefacts if a["state"] == "SERVED")},
        "artefacts": artefacts,
        "review_files": review_files,
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
        else:
            current = json.loads(out.read_text(encoding="utf-8"))
            fresh = json.loads(rendered)
            # source_commit legitimately differs between the build commit and the commit that carries the bundle.
            current.get("path_scheme", {}).pop("source_commit", None)
            fresh.get("path_scheme", {}).pop("source_commit", None)
            if canonical_json(current) != canonical_json(fresh):
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
          f"{c['served']} served ({c['served_bytes']:,} B), {c['withheld']} withheld with reason")
    return 0


if __name__ == "__main__":
    sys.exit(main())
