"""Held-bytes digests: every recorded sha256 that names a file in the tree equals the sha256 of that file's bytes.

A digest beside a path is a provenance claim: "the bytes I read are these". Two ways it can be false without any
check noticing (both found on 2026-09-19 by a corpus sweep): the digest is of CRLF bytes git never stored (the
cache/pcsk9-mace/harms_aact_held.json class: 1 file, 4 citing records incl. a served review), and the digest is of
an ORIGINAL the tree does not hold, recorded against its extracted text (the glp1 MedR class: 1 PDF, 7 citing
records incl. a served review and the provenance index). Provenance then looks complete while pointing at nothing.

Contract checked here (fail-closed):
  * a digest key (document_sha256, extracted_text_sha256, body_sha256, document_sha256_from_manifest, or sha256
    beside a path key) paired with its most specific path-like sibling must equal sha256(bytes on disk);
  * a digest whose path is not in the tree is UNHELD and refused unless the record says so itself
    (held: false / original_pdf_held: false / held_in_tree: false / status containing NOT_HELD);
  * text digests (limitations[].text_sha256, *_text_sha256 with no path sibling) and object hashes are not file
    digests and are not checked; records with a digest and NO path sibling are counted as NOT_CHECKABLE, by name.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

HEX = re.compile(r"^[0-9a-f]{64}$")
PATHISH = re.compile(r"^\S+\.(pdf|txt|json|xml|gz|csv|html)$|^\S*[\\/]\S*$", re.I)  # a file path has no whitespace
DIGEST_KEYS = ("document_sha256", "extracted_text_sha256", "body_sha256", "document_sha256_from_manifest", "sha256")
PATH_KEYS = ("document_ref", "document", "held_path", "path", "file", "document_path", "text_file", "held", "source_file",
             "extracted_text_path", "extracted_text", "held_in_tree", "ref")
ROOTS = ("cache", "docs", "outputs", "registry")
SKIP_DIRS = {".git", ".tmp", "node_modules", "__pycache__"}
NOT_HELD_MARKERS = ("held", "held_in_tree", "in_tree", "document_held")

MATCH, CRLF_OF_COMMITTED, LF_OF_CRLF_FILE, UNHELD, UNHELD_DECLARED, OTHER_MISMATCH, NOT_CHECKABLE = (
    "MATCH", "CRLF_OF_COMMITTED", "LF_OF_CRLF_FILE", "UNHELD", "UNHELD_DECLARED", "OTHER_MISMATCH", "NOT_CHECKABLE")
REFUSING = {CRLF_OF_COMMITTED, LF_OF_CRLF_FILE, UNHELD, OTHER_MISMATCH}


def _sha_forms(path: str, cache: dict[str, tuple[str, str, str]]) -> tuple[str, str, str]:
    if path not in cache:
        with open(path, "rb") as f:
            b = f.read()
        cache[path] = (hashlib.sha256(b).hexdigest(),
                       hashlib.sha256(b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest(),
                       hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest())
    return cache[path]


def _resolve(root: str, ref: str, json_path: str) -> str | None:
    ref = str(ref).split("#")[0]
    for c in (os.path.join(root, ref), os.path.join(os.path.dirname(json_path), ref)):
        if os.path.isfile(c):
            return os.path.normpath(c)
    return None


def _declared_unheld(obj: dict[str, Any]) -> bool:
    if obj.get("document_held") is False:
        return True
    for k in NOT_HELD_MARKERS:
        v = obj.get(k)
        if v is False:
            return True
        if isinstance(v, dict) and (v.get("held_in_tree") is False or v.get("in_tree") is False):
            return True
    held = obj.get("held")
    if isinstance(held, dict) and held.get("held_in_tree") in (None, False) and held.get("held_off_tree"):
        return True  # the record itself says the original lives off the tree
    st = str(obj.get("status") or obj.get("state") or "")
    return "NOT_HELD" in st or "UNHELD" in st


def _pair(obj: dict[str, Any], dk: str) -> str | None:
    """The path a digest key claims: text digests pair with text refs, document digests with document refs
    (top level first, then the nested `held` block), and a document digest never pairs with a text ref while a
    document ref exists -- that mis-pairing is how a PDF's digest looked like the digest of its .txt."""
    def pathish(v: Any) -> bool:
        return (isinstance(v, str) and PATHISH.search(v) is not None and len(v) < 300
                and not v.lower().startswith(("http://", "https://")))  # a URL is a retrieval address, not held bytes
    refs = {k: v for k, v in obj.items() if k != "slug" and pathish(v)}
    held = obj.get("held")
    if isinstance(held, dict):
        refs.update({"held." + k: v for k, v in held.items() if pathish(v)})
    if not refs:
        return None
    # 1. by name: X_sha256 pairs with X_file / X_path / X_ref / X (body_sha256 -> body_file, document_sha256 ->
    #    document_path, extracted_text_sha256 -> extracted_text_path); the record's own naming outranks any guess
    stem = re.sub(r"_?sha256(_from_manifest)?$", "", dk)
    if stem:
        for cand in (stem + "_file", stem + "_path", stem + "_ref", stem, "held." + stem + "_path", "held." + stem):
            if cand in refs:
                return refs[cand]
    is_text = "text" in dk.lower()
    text_refs = {k: v for k, v in refs.items() if "text" in k.lower()}  # by KEY: a document may itself be a .txt
    doc_refs = {k: v for k, v in refs.items() if k not in text_refs}
    # 2. by kind: a text digest pairs with a text ref; a document digest pairs ONLY with a document ref -- a
    #    record holding a document's digest beside its extracted text alone is not claiming the text's digest
    pool = (text_refs or refs) if is_text else doc_refs
    if not pool:
        return None
    for k in PATH_KEYS + tuple("held." + k for k in PATH_KEYS):
        if k in pool:
            return pool[k]
    return next(iter(pool.values())) if len(pool) == 1 else None


def scan(root: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cache: dict[str, tuple[str, str, str]] = {}

    def walk(obj: Any, json_path: str, trail: str) -> None:
        if isinstance(obj, dict):
            for dk, dv in obj.items():
                if not (isinstance(dv, str) and HEX.match(dv) and dk in DIGEST_KEYS):
                    continue
                if dk == "sha256" and not any(k in obj for k in PATH_KEYS):
                    continue  # an object hash (release/records/review/block ...), not a file digest
                rel = os.path.relpath(json_path, root).replace(os.sep, "/")
                if dk.startswith("document") and _declared_unheld(obj):
                    rows.append({"json": rel, "trail": trail + "/" + dk, "digest": dv, "ref": None, "class": UNHELD_DECLARED})
                    continue  # the record says its document is not in the tree; its digest names nothing here to check
                ref = _pair(obj, dk)
                row = {"json": rel, "trail": trail + "/" + dk, "digest": dv, "ref": ref}
                if ref is None:
                    row["class"] = UNHELD_DECLARED if _declared_unheld(obj) else NOT_CHECKABLE
                    rows.append(row)
                    continue
                p = _resolve(root, ref, json_path)
                if not p:
                    row["class"] = UNHELD_DECLARED if _declared_unheld(obj) else UNHELD
                    rows.append(row)
                    continue
                plain, crlf, lf = _sha_forms(p, cache)
                row["class"] = MATCH if dv == plain else CRLF_OF_COMMITTED if dv == crlf else LF_OF_CRLF_FILE if dv == lf else OTHER_MISMATCH
                row["on_disk"] = plain
                rows.append(row)
            for k, v in obj.items():
                walk(v, json_path, trail + "/" + str(k))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, json_path, trail + f"[{i}]")

    for base in ROOTS:
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for dp, dns, fns in os.walk(top):
            dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith("snapshots")]
            for fn in fns:
                if not fn.endswith(".json"):
                    continue
                jp = os.path.join(dp, fn)
                try:
                    with open(jp, encoding="utf-8") as f:
                        doc = json.load(f)
                except (OSError, ValueError):
                    continue
                walk(doc, jp, "")
    return rows


def check(root: str) -> tuple[bool, list[str], dict[str, int]]:
    rows = scan(root)
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    problems = []
    for r in rows:
        if r["class"] in REFUSING:
            what = {CRLF_OF_COMMITTED: "digest is of the CRLF form of bytes git never stored",
                    LF_OF_CRLF_FILE: "digest is of the LF form of a CRLF file",
                    UNHELD: "names a file that is not in the tree and does not declare it unheld",
                    OTHER_MISMATCH: "does not equal the bytes on disk"}[r["class"]]
            on_disk = f"; on disk {r['on_disk'][:12]}" if r.get("on_disk") else ""
            problems.append(f"{r['json']}{r['trail']}: {r['digest'][:12]} -> {r['ref']}: {what}{on_disk}")
    return (not problems), problems, counts
