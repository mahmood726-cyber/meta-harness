"""Commit-pinned anchors for the result-change notice adjudication (decision B, 2026-09-24).

A notice judgement is a judgement of SPECIFIC bytes: the page a reader is served before the change and the page
that carries the change. Before decision B the registry recorded sha256 digests of working-tree paths
(`docs/reviews/<slug>/index.html` -> digest). A rebuild changed the bytes, the digest stopped matching, and nothing
said WHICH version had been judged, so the only way forward was to refresh the digest, which re-points a judgement at
bytes nobody judged. Measured 2026-09-25 against served main c9d665e0: 53 of 78 anchors broken (26 review.json,
24 index.html, 3 harness sources) and 25 intact: the 24 recorded as `git:38c04411:<path>` and one cache record
main never touched. (The brief that ordered this counted 51 / 27 at an earlier main.)

Decision B (taken by Dispatch under Mahmood's delegation, 2026-09-24), as implemented here:
  1. Every anchor names the exact version judged: `git:<commit>:<path>`, its git blob id and the sha256 of the
     blob's bytes. A working-tree anchor is refused outright. Because a commit-pinned anchor names bytes that
     cannot change, a page REBUILD NO LONGER DETACHES A NOTICE.
  2. The guards stay strict. An anchor that cannot be verified (commit absent from the clone, path absent, blob
     or sha256 not the recorded one) is DETACHED, and the walker and `sign` REFUSE. A refusal on a detached anchor
     stays a refusal. Separately, `guard()` refuses a notice as STALE when the presenting tree no longer serves
     what was judged: a different result tuple or pooled membership for the outcome, a signing digest different
     from the judged one, or an index.html that no longer carries the exact rendered block. Byte churn a rebuild
     makes elsewhere on the page is DISCLOSED (`drift`), never silently accepted and never a refusal on its own.
  3. There is no re-pointing without re-judgement. Anchors change only by APPENDING a judgement record (see
     `append_only_problem`), and a judgement record is bound to the digests it judged (scripts/notice_rejudge.py).
     They are never refreshed in place.

This module lives in scripts/, not harness/, on purpose: every harness/*.py blob is in the certificates'
analysis_code closure, so editing one re-certifies all 32 pages.

Anchor sides (all verified pinned; none is required to equal the working tree byte for byte)
  served   -- the page a reader is served now (origin/main at judgement time).
  proposed -- the page that carries the notice; `guard()` checks the tree still serves what it judged.
  code     -- renderer sources the judgement relied on; drift is disclosed.
  held     -- held source bytes a judgement quotes (e.g. a cache record); drift is disclosed.
  record   -- the result-change ledger as judged. A countersignature is itself a ledger write, so the walker
              requires every audited field of the live notice to equal the judged notice instead.
"""
from __future__ import annotations

import functools
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SIDES = ("served", "proposed", "code", "held", "record")
PREFIX = "git:"


class AnchorRefused(ValueError):
    """An anchor that cannot be verified, or that the presenting tree no longer carries. Never a warning."""


def parse(ref: str) -> tuple[str, str]:
    """`git:<commit>:<path>` -> (commit, path). A working-tree path is refused: it names no version."""
    if not isinstance(ref, str) or not ref.startswith(PREFIX):
        raise AnchorRefused(f"working-tree anchor {ref!r}: decision B requires git:<commit>:<path> (the version judged)")
    commit, sep, path = ref[len(PREFIX):].partition(":")
    if not sep or not path or len(commit) < 7 or any(c not in "0123456789abcdef" for c in commit):
        raise AnchorRefused(f"malformed anchor {ref!r}: expected git:<hex commit>:<path>")
    return commit, path


def _git(root: Path, *args: str, data: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, input=data, capture_output=True)


def pinned_blob(root: Path, ref: str) -> tuple[str, bytes]:
    """(blob id, bytes) of the judged version. Refuses if the commit or path is not available in this clone."""
    parse(ref)
    return _pinned(str(Path(root).resolve()), ref)


class _Batch:
    """One `git cat-file --batch` process per repository: hundreds of anchors, one process (Windows spawns are slow)."""

    def __init__(self, root: Path):
        self.proc = subprocess.Popen(["git", "cat-file", "--batch"], cwd=root, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def get(self, spec: str) -> tuple[str, str, bytes] | None:
        """(oid, type, body) or None when git reports the object missing or ambiguous."""
        self.proc.stdin.write(spec.encode("utf-8") + b"\n")
        self.proc.stdin.flush()
        header = self.proc.stdout.readline().decode("utf-8", "replace").rstrip("\n")
        parts = header.split()
        if len(parts) != 3 or parts[1] not in ("blob", "commit", "tree", "tag"):
            return None
        body = self.proc.stdout.read(int(parts[2]))
        self.proc.stdout.read(1)  # the LF that terminates every object
        return parts[0], parts[1], body


@functools.lru_cache(maxsize=None)
def _batch(root_s: str) -> _Batch:
    return _Batch(Path(root_s))


@functools.lru_cache(maxsize=None)
def _pinned(root_s: str, ref: str) -> tuple[str, bytes]:
    # Cached per process: the content of <commit>:<path> is immutable, and a refusal raises (never cached).
    batch = _batch(root_s)
    commit, path = parse(ref)
    got = batch.get(f"{commit}^{{commit}}")
    if got is None or got[1] != "commit":
        raise AnchorRefused(f"{ref}: judged commit {commit} is not in this clone (fetch it: git fetch origin "
                            f"{commit}); an anchor that cannot be read is not verified")
    got = batch.get(f"{commit}:{path}")
    if got is None or got[1] != "blob":
        raise AnchorRefused(f"{ref}: path does not exist at the judged commit")
    return got[0], got[2]


def working_blob(root: Path, path: str, expected: str | None = None) -> str | None:
    """The blob id git would store for the working-tree file (clean filters applied: CRLF checkouts compare equal)."""
    target = (root / path)
    if not target.resolve().is_relative_to(root.resolve()):
        raise AnchorRefused(f"anchor path {path!r} escapes the repository")
    if not target.exists():
        return None
    body = target.read_bytes()
    raw = hashlib.sha1(b"blob %d\0" % len(body) + body).hexdigest()
    if raw == expected:
        return raw  # the raw bytes ARE the judged blob: definitive, no clean filter can change that
    proc = _git(root, "hash-object", "--path", path, "--stdin", data=body)
    if proc.returncode != 0:
        raise AnchorRefused(f"git hash-object failed for {path}: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout.decode().strip()


def make(root: Path, side: str, commit: str, path: str) -> dict:
    """Record an anchor for bytes that exist at `commit` (used only when a judgement is appended)."""
    if side not in SIDES:
        raise AnchorRefused(f"unknown anchor side {side!r}")
    ref = f"{PREFIX}{commit}:{path}"
    blob, body = pinned_blob(root, ref)
    return {"side": side, "ref": ref, "blob": blob, "sha256": hashlib.sha256(body).hexdigest()}


def verify(root: Path, anchor: dict) -> str:
    """Refuse (DETACHED) unless the anchor's pinned bytes are exactly what was recorded. Returns the blob id."""
    side = anchor.get("side")
    if side not in SIDES:
        raise AnchorRefused(f"DETACHED: anchor {anchor.get('ref')!r} has unknown side {side!r}")
    try:
        blob, body = pinned_blob(root, anchor["ref"])
    except AnchorRefused as error:
        raise AnchorRefused(f"DETACHED: {error}") from None
    if blob != anchor.get("blob"):
        raise AnchorRefused(f"DETACHED: {anchor['ref']}: recorded blob {anchor.get('blob')} but the judged commit "
                            f"holds {blob}")
    digest = hashlib.sha256(body).hexdigest()
    if digest != anchor.get("sha256"):
        raise AnchorRefused(f"DETACHED: {anchor['ref']}: recorded sha256 {anchor.get('sha256')} but the judged "
                            f"bytes hash to {digest}")
    return blob


def drift(root: Path, judgement: dict) -> list[str]:
    """Disclosure, not a verdict: which judged files the presenting tree carries in different bytes."""
    lines = []
    for a in judgement.get("anchors") or []:
        if a["side"] in ("served", "record"):
            continue  # the served tree is not this tree; the ledger is checked field by field instead
        _, path = parse(a["ref"])
        now = working_blob(root, path, a["blob"])
        if now != a["blob"]:
            lines.append(f"{path} ({a['side']}): judged blob {a['blob'][:12]}, this tree "
                         + (f"blob {now[:12]}" if now else "absent"))
    return lines


def _outcome(review: dict, name: str) -> dict:
    hits = [o for o in review.get("outcomes") or [] if o.get("name") == name]
    if len(hits) != 1:
        raise AnchorRefused(f"STALE: {len(hits)} outcomes named {name!r} on the page")
    return hits[0]


def guard(root: Path, row: dict, notice: dict, block_html: str, sha: str) -> tuple[dict, list[str]]:
    """Every refusal the walker and `sign` share. Returns (judgement, drift lines) or raises AnchorRefused.

    DETACHED: a pinned anchor cannot be verified. STALE: the presenting tree no longer serves what was judged.
    Neither is ever repaired by editing a digest; only an appended re-judgement can clear it."""
    from harness import result_changes  # read-only import; harness/ is never edited by this lane

    judgement = verify_row(root, row)
    aid, jid = row.get("audit_id"), judgement.get("judgement_id")
    if sha != judgement.get("rendered_block_sha256"):
        raise AnchorRefused(f"STALE: {aid}: the notice now renders sha256 {sha}; judgement {jid} judged "
                            f"{judgement.get('rendered_block_sha256')}; re-judgement required")
    slug = notice["slug"]
    judged_ref = next(a["ref"] for a in judgement["anchors"]
                      if a["side"] == "proposed" and a["ref"].endswith(f"docs/reviews/{slug}/review.json"))
    judged = _outcome(json.loads(pinned_blob(root, judged_ref)[1]), notice["outcome"])
    try:
        current_review = json.loads((root / "docs" / "reviews" / slug / "review.json").read_bytes())
    except (OSError, ValueError) as error:
        raise AnchorRefused(f"STALE: {aid}: this tree's review.json for {slug} is unreadable ({error}); the "
                            f"page no longer serves what judgement {jid} judged") from None
    current = _outcome(current_review, notice["outcome"])
    rt = result_changes.result_tuple
    if not result_changes._same(rt(current.get("result")), notice["after"]) or \
            not result_changes._same(rt(judged.get("result")), notice["after"]):
        raise AnchorRefused(f"STALE: {aid}: this tree serves {rt(current.get('result'))} for {notice['outcome']!r}, "
                            f"not the after the notice records {notice['after']}; judgement {jid} no longer holds")
    pooled = lambda o: sorted((o.get("membership") or {}).get("pooled") or [])  # noqa: E731
    if pooled(current) != pooled(judged):
        raise AnchorRefused(f"STALE: {aid}: pooled membership is now {pooled(current)}, judged {pooled(judged)}; "
                            f"judgement {jid} no longer holds")
    try:
        page = (root / "docs" / "reviews" / slug / "index.html").read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise AnchorRefused(f"STALE: {aid}: this tree's index.html for {slug} is unreadable ({error})") from None
    if " ".join(block_html.split()) not in " ".join(page.split()):
        raise AnchorRefused(f"STALE: {aid}: this tree's index.html no longer carries the rendered block with sha256 "
                            f"{sha}; what a reader sees is not what judgement {jid} judged")
    return judgement, drift(root, judgement)


def current_judgement(row: dict) -> dict:
    """The latest appended judgement of an audited notice; refuses a notice with none."""
    judgements = row.get("judgements") or []
    if not judgements:
        raise AnchorRefused(f"{row.get('audit_id')}: no commit-pinned judgement recorded; re-judgement required")
    return judgements[-1]


def verify_row(root: Path, row: dict) -> dict:
    """Verify every anchor of a notice's current judgement; return that judgement."""
    judgement = current_judgement(row)
    anchors = judgement.get("anchors") or []
    sides = {a.get("side") for a in anchors}
    if not {"served", "proposed"} <= sides:
        raise AnchorRefused(f"{row.get('audit_id')}: judgement {judgement.get('judgement_id')} lacks a served or "
                            "proposed anchor; a notice is a judgement of both pages")
    for anchor in anchors:
        try:
            verify(root, anchor)
        except AnchorRefused as error:
            raise AnchorRefused(f"{row.get('audit_id')} (judgement {judgement.get('judgement_id')}): {error}") from None
    return judgement


def source_digest_map(audit: dict) -> dict[str, str]:
    """The top-level `source_digests` a registry must carry: exactly the anchors of every current judgement."""
    out: dict[str, str] = {}
    for row in audit["notices"]:
        for anchor in current_judgement(row).get("anchors") or []:
            if out.setdefault(anchor["ref"], anchor["sha256"]) != anchor["sha256"]:
                raise AnchorRefused(f"{anchor['ref']}: two judgements record different digests for one version")
    return out


def append_only_problem(old: dict, new: dict) -> str | None:
    """None when `new` only APPENDS judgements to `old`; else why it re-points. Every judgement already recorded
    must survive unchanged, in order, on the same notice; notices are neither dropped nor renamed."""
    old_rows = {r["audit_id"]: r for r in old.get("notices", [])}
    new_rows = {r["audit_id"]: r for r in new.get("notices", [])}
    if set(old_rows) - set(new_rows):
        return f"audited notices dropped: {sorted(set(old_rows) - set(new_rows))}"
    for audit_id, row in old_rows.items():
        before = row.get("judgements") or []
        after = new_rows[audit_id].get("judgements") or []
        if after[:len(before)] != before:
            return (f"{audit_id}: a recorded judgement was edited or removed -- anchors change only by appending a "
                    "new judgement of the new bytes")
    return None
