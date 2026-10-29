"""Sealed held-out leak detector for prospective search validation.

An external auditor has disqualified ALL 32 current topics from ever serving as
prospective validation of the search engine: every one has been exposed through
audits, URLs, commit history or regression work. They remain the adversarial
REGRESSION corpus and nothing else. Therefore an in-repo held-out register
(`registry/heldout.json` listing five slugs) cannot do the job: a list committed
to the repository is published by definition. The auditor's design: the topic
list is held OUTSIDE the development repository, chosen only after the
architecture is frozen, never committed before execution, revealed to the
harness only when the prospective run begins. What lives in the repo is the
LEAK DETECTOR, not the register.

GUARANTEED (given the key is only where the register-holder puts it): no
identifier whose HMAC is sealed can land on main in any tracked text file or
commit message after enforced_since (CI runs the detector with the secret; the
ruleset makes CI mandatory); the register's plaintext is not readable from the
repository.

NOT GUARANTEED: anyone holding the key or the external register can read the
names; names not sealed are not protected; a low-entropy name can be recovered
from its HMAC by someone who holds the key (the HMAC hides names from the
repository, not from the key-holder); the detector cannot stop a person from
being TOLD a name out of band. The key-holder should not be the person tuning
retrieval; we cannot enforce that.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Iterable

from harness.target import TargetUnresolvable, describe_target, refusal as target_refusal


REGISTRY_PATH = os.path.join("registry", "heldout_sealed.json")
MEASUREMENT_PATH = os.path.join("docs", "search_recall_regression_corpus.json")
KEY_FILE = os.path.join("~", ".meta-harness", "heldout.key")
MISSING_KEY_REASON = "held-out key not available: the detector cannot run; fail closed"
COMMIT_MESSAGE_REFUSAL = "held-out sealed identifier may not be named in commit messages"
IDENTIFIER_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _root_path(root) -> str:
    return os.path.abspath(os.fspath(root))


def _posix(path: str) -> str:
    return path.replace("\\", "/")


_GIT_KEEP = ("GIT_TERMINAL_PROMPT", "GIT_ASKPASS", "GIT_SSH_COMMAND")


def _isolated_git_env() -> dict:
    """The environment for git in a SCRATCH directory: no inherited GIT_DIR / GIT_INDEX_FILE / GIT_WORK_TREE.
    2026-10-11: verify_all's held-out limb runs self_test IN-PROCESS under the pre-commit hook, where tests/conftest.py's
    scrub never runs; self_test's 'git add probe.txt' in a temp dir went into the LIVE index the hook had exported
    (seen as 'AD probe.txt' staged in a lane worktree). Only scratch calls are isolated: a scan of the live repository
    keeps the hook's environment, which is what lets it see the commit being made."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_") or k in _GIT_KEEP}


def _run_git(root: str, args: list[str], isolate: bool = False) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_isolated_git_env() if isolate else None,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout



def _run_git_bytes(root: str, args: list[str], isolate: bool = False) -> bytes:
    """Preserve NUL-delimited Git paths and exact staged blob bytes."""
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        env=_isolated_git_env() if isolate else None,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"staged-index Git operation failed (exit {proc.returncode}); path and output redacted")
    return proc.stdout


def load(root) -> dict:
    """Load the sealed detector registry."""
    with open(os.path.join(_root_path(root), REGISTRY_PATH), encoding="utf-8") as f:
        return json.load(f)


def describe_check_target(root) -> str:
    """Return a target line for the sealed held-out detector."""

    root = _root_path(root)
    paths = [REGISTRY_PATH, MEASUREMENT_PATH, os.path.join("harness", "acquisition.py")]
    if not os.path.isfile(os.path.join(root, REGISTRY_PATH)):
        return target_refusal("heldout", f"missing required path: {_posix(REGISTRY_PATH)}")
    try:
        return describe_target(root, paths=paths, label="heldout")
    except TargetUnresolvable as exc:
        return target_refusal("heldout", str(exc))


def load_key(root) -> str | None:
    """Load the detector key from the environment or the register-holder's local file."""
    _ = root
    env_key = os.environ.get("HELDOUT_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    key_path = os.path.expanduser(KEY_FILE)
    try:
        key = open(key_path, encoding="utf-8").read().strip()
    except OSError:
        return None
    return key or None


def hmac_token(key: str, identifier: str) -> str:
    """Return HMAC-SHA256 over the lowercase identifier, as lowercase hex."""
    return hmac.new(
        key.encode("utf-8"),
        identifier.lower().encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def candidate_identifiers(text: str):
    """Yield every possible sealed identifier in `text`: each maximal [a-z0-9-] run of length >= 3 and, for
    hyphenated runs, every contiguous window of 1..6 hyphen-tokens (a slug inside prose or a path segment is
    still found). STREAMED WITHOUT A CAP: a bounded candidate set would stop scanning a large file part-way
    (cache/embeddings.json, 14 MB, exceeded the first draft's 50,000 cap), so a sealed name late in such a file
    would be missed silently -- the detector-gap class. Duplicates are suppressed per call with a seen-set that
    grows with the file; memory is proportional to distinct identifiers, never truncated."""
    seen: set[str] = set()
    for match in IDENTIFIER_RE.finditer(text.lower()):
        run = match.group(0)
        if len(run) >= 3 and run not in seen:
            seen.add(run)
            yield run
        if "-" not in run:
            continue
        parts = run.split("-")
        for start in range(len(parts)):
            for end in range(start + 1, min(len(parts), start + 6) + 1):
                w = "-".join(parts[start:end])
                if len(w) >= 3 and w not in seen:
                    seen.add(w)
                    yield w


def _tokens(registry: dict) -> set[str]:
    raw = registry.get("tokens")
    if not isinstance(raw, list):
        return set()
    return {str(t).lower() for t in raw}


def _matching_hmacs(text: str, key: str, registry: dict) -> list[str]:
    tokens = _tokens(registry)
    if not tokens:
        return []
    matches = {
        token
        for identifier in candidate_identifiers(text)
        for token in [hmac_token(key, identifier)]
        if token in tokens
    }
    return sorted(matches)


class _Matcher:
    """_matching_hmacs for a whole scan: the keyed HMAC state is built once and copied per identifier, and each
    distinct identifier is hashed once per scan (prose and slugs repeat across thousands of lines; the per-line
    rebuild was most of the held-out limb's 7-10 minutes in CI). Same candidates, same digests, same membership
    test: only repeated work is removed (tests/test_heldout.py::test_matcher_equals_the_per_line_scan)."""

    def __init__(self, key: str, registry: dict):
        self.tokens = _tokens(registry)
        self._base = hmac.new(key.encode("utf-8"), digestmod=hashlib.sha256)
        self._cache: dict[str, str] = {}

    def _token(self, identifier: str) -> str:
        t = self._cache.get(identifier)
        if t is None:
            h = self._base.copy()
            h.update(identifier.lower().encode("utf-8"))
            t = self._cache[identifier] = h.hexdigest()
        return t

    def __call__(self, text: str) -> list[str]:
        if not self.tokens:
            return []
        return sorted({t for identifier in candidate_identifiers(text) for t in [self._token(identifier)]
                       if t in self.tokens})


def _is_binary(blob: bytes) -> bool:
    return b"\0" in blob


def _scan_tracked_paths(root: str, isolate: bool = False) -> Iterable[str]:
    for raw_path in _run_git(root, ["ls-files"], isolate=isolate).splitlines():
        path = _posix(raw_path)
        if path == _posix(REGISTRY_PATH):
            continue
        yield path


def scan_tree(root, key: str, registry: dict, isolate: bool = False) -> list[dict]:
    """Scan every tracked text file for sealed identifiers without revealing them. isolate: root is a SCRATCH repository
    (self_test), so git must address it by cwd and never through an inherited GIT_DIR / GIT_INDEX_FILE."""
    root = _root_path(root)
    hits = []
    match = _Matcher(key, registry)
    for path in _scan_tracked_paths(root, isolate=isolate):
        abs_path = os.path.join(root, *path.split("/"))
        try:
            blob = open(abs_path, "rb").read()
        except OSError:
            continue
        if _is_binary(blob):
            continue
        text = blob.decode("utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for digest in match(line):
                hits.append({"path": path, "identifier_hmac": digest, "line_no": line_no})
    return hits



def scan_staged_index(root, key: str, registry: dict, isolate: bool = False) -> list[dict]:
    """Scan index blobs for added/modified paths, even if the worktree was cleaned after staging.

    scan_tree examines working-tree bytes, which can differ from what a pre-commit hook
    is about to publish. This is an additional index guard, not a replacement for
    the working-tree and committed-history checks. NUL paths preserve unusual names.
    """
    root = _root_path(root)
    paths = _run_git_bytes(
        root, ["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMRT"], isolate=isolate
    ).split(b"\0")
    match = _Matcher(key, registry)
    hits = []
    for raw_path in paths:
        if not raw_path:
            continue
        path = _posix(os.fsdecode(raw_path))
        if path == _posix(REGISTRY_PATH):
            continue
        # Stage pathnames are source metadata too; redact any matching sealed name.
        path_tokens = match(path)
        safe_path = "<redacted staged path>" if path_tokens else path
        for digest in path_tokens:
            hits.append({"kind": "staged_path", "identifier_hmac": digest})
        blob = _run_git_bytes(root, ["cat-file", "blob", ":" + path], isolate=isolate)
        if _is_binary(blob):
            continue
        for line_no, line in enumerate(blob.decode("utf-8", errors="replace").splitlines(), start=1):
            for digest in match(line):
                hits.append({"path": safe_path, "identifier_hmac": digest, "line_no": line_no})
    return hits


def check_message(text: str, key: str, registry: dict) -> list[str]:
    """Return sealed identifier HMACs found in a commit message."""
    return _matching_hmacs(text, key, registry)


def scan_commit_messages(root, key: str, registry: dict) -> list[dict]:
    """Scan first-parent commit messages after enforced_since for sealed identifiers."""
    root = _root_path(root)
    enforced_since = registry.get("enforced_since")
    if not enforced_since:
        return []
    out = _run_git(
        root,
        ["log", "--first-parent", "--format=%H%x00%B%x00", f"{enforced_since}..HEAD"],
    )
    parts = out.split("\0")
    hits = []
    for i in range(0, len(parts) - 1, 2):
        sha = parts[i].strip()
        message = parts[i + 1].lstrip("\n")
        if not sha:
            continue
        for digest in check_message(message, key, registry):
            hits.append({"sha": sha, "identifier_hmac": digest})
    return hits


def canary(key: str) -> str:
    return "zz-canary-heldout-" + hmac_token(key, "canary")[:8]


def canary_token(key: str) -> str:
    return hmac_token(key, canary(key))


def self_test(key: str, registry: dict) -> tuple[bool, str]:
    """Prove the detector can actually match a sealed canary through scan_tree."""
    sealed_canary = canary_token(key)
    if sealed_canary not in _tokens(registry):
        return False, "canary not sealed -- detector unproven"
    with tempfile.TemporaryDirectory(prefix="heldout-canary-") as tmp:
        _run_git(tmp, ["init"], isolate=True)
        probe = os.path.join(tmp, "probe.txt")
        with open(probe, "w", encoding="utf-8", newline="\n") as f:
            f.write(canary(key) + "\n")
        _run_git(tmp, ["add", "probe.txt"], isolate=True)
        hits = scan_tree(tmp, key, registry, isolate=True)
    if any(hit.get("identifier_hmac") == sealed_canary for hit in hits):
        return True, "canary matched sealed token through scan_tree"
    return False, "canary did not match through scan_tree -- detector unproven"


def _engine_sha(root: str) -> str:
    return _run_git(root, ["hash-object", os.path.join("harness", "acquisition.py")]).strip()


def measurement_current(root, registry: dict) -> tuple[bool, str]:
    """Return whether the regression-corpus recall artefact matches the engine blob."""
    root = _root_path(root)
    if registry.get("enforced_since") is None:
        return True, "not enforced yet"
    artefact = os.path.join(root, MEASUREMENT_PATH)
    if not os.path.exists(artefact):
        return False, "no published regression-corpus measurement"
    try:
        data = json.load(open(artefact, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return False, f"published regression-corpus measurement unreadable: {exc}"
    current = _engine_sha(root)
    published = data.get("engine_sha")
    if published != current:
        return (
            False,
            "engine changed since the published regression-corpus measurement "
            f"({published} -> {current}); re-measure and publish before landing",
        )
    history = data.get("history")
    if not isinstance(history, list) or not history:
        return False, "published regression-corpus measurement history is empty"
    last = history[-1]
    if not isinstance(last, dict) or last.get("engine_sha") != published:
        return False, "published regression-corpus measurement history does not end at engine_sha"
    return True, "published regression-corpus measurement matches current engine"


def check(root) -> tuple[bool, list[str]]:
    """Run key, canary, tree, commit-message, and measurement checks."""
    root = _root_path(root)
    key = load_key(root)
    if key is None:
        return False, [MISSING_KEY_REASON]
    reasons = []
    try:
        registry = load(root)
    except Exception as exc:
        return False, [f"sealed held-out registry could not be loaded: {exc}"]
    ok, detail = self_test(key, registry)
    if not ok:
        reasons.append(detail)
    try:
        for hit in scan_tree(root, key, registry):
            reasons.append(
                f"{hit['path']}:{hit['line_no']}: sealed identifier "
                f"{hit['identifier_hmac'][:12]}... appears in a tracked text file"
            )
    except Exception as exc:
        reasons.append(f"sealed held-out tree scan could not run: {exc}")
    try:
        for hit in scan_staged_index(root, key, registry):
            if hit.get("kind") == "staged_path":
                reasons.append(
                    f"sealed identifier {hit['identifier_hmac'][:12]}... appears in a staged path "
                    "(filename redacted)"
                )
            else:
                reasons.append(
                    f"{hit['path']}:{hit['line_no']}: sealed identifier "
                    f"{hit['identifier_hmac'][:12]}... appears in a staged index blob"
                )
    except Exception as exc:
        reasons.append(f"sealed held-out staged index scan could not run: {exc}")
    try:
        for hit in scan_commit_messages(root, key, registry):
            reasons.append(
                f"{hit['sha'][:12]}: sealed identifier "
                f"{hit['identifier_hmac'][:12]}... appears in a commit message"
            )
    except Exception as exc:
        reasons.append(f"sealed held-out commit-message scan could not run: {exc}")
    try:
        ok, detail = measurement_current(root, registry)
        if not ok:
            reasons.append(detail)
    except Exception as exc:
        reasons.append(f"regression-corpus measurement check could not run: {exc}")
    return not reasons, reasons


def _message_check(root: str, path: str) -> int:
    key = load_key(root)
    if key is None:
        print(MISSING_KEY_REASON)
        return 2
    try:
        registry = load(root)
    except Exception as exc:
        print(f"held-out commit-message check: REFUSED ({exc})")
        return 1
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        print(f"held-out commit-message check: REFUSED ({exc})")
        return 1
    bad = check_message(text, key, registry)
    if bad:
        print(COMMIT_MESSAGE_REFUSAL)
        print("offending sealed identifier hmac prefix(es): " + ", ".join(h[:12] + "..." for h in bad))
        return 1
    print("held-out commit-message check: PASS")
    return 0


def _need_key(root: str) -> str | None:
    key = load_key(root)
    if key is None:
        print(MISSING_KEY_REASON)
    return key


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m harness.heldout")
    parser.add_argument("--message", help="commit message file to check")
    parser.add_argument("--seal", help="print the HMAC token for one identifier")
    parser.add_argument("--canary-token", action="store_true", help="print the HMAC token for the live canary")
    args = parser.parse_args(argv)
    root = _root_path(os.getcwd())

    if args.message:
        return _message_check(root, args.message)
    if args.seal is not None:
        key = _need_key(root)
        if key is None:
            return 1
        print(hmac_token(key, args.seal))
        return 0
    if args.canary_token:
        key = _need_key(root)
        if key is None:
            return 1
        print(canary_token(key))
        return 0

    target_line = describe_check_target(root)
    print(target_line)
    if target_line.startswith("TARGET heldout: COULD-NOT-EXECUTE"):
        return 1
    ok, reasons = check(root)
    print(f"HELD-OUT: registry={REGISTRY_PATH}")
    if not ok:
        verdict = "COULD-NOT-EXECUTE" if MISSING_KEY_REASON in reasons else "REFUSED"
        print(f"HELD-OUT: {verdict}")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    registry = load(root)
    _, detail = measurement_current(root, registry)
    print(f"HELD-OUT: PASS ({detail})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
