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

from . import gitenv
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


def _run_git(root: str, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=gitenv.clean_env(),  # never the repository a hook's GIT_DIR names (see gitenv)
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
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


def _is_binary(blob: bytes) -> bool:
    return b"\0" in blob


def _scan_tracked_paths(root: str) -> Iterable[str]:
    for raw_path in _run_git(root, ["ls-files"]).splitlines():
        path = _posix(raw_path)
        if path == _posix(REGISTRY_PATH):
            continue
        yield path


def scan_tree(root, key: str, registry: dict) -> list[dict]:
    """Scan every tracked text file for sealed identifiers without revealing them."""
    root = _root_path(root)
    hits = []
    for path in _scan_tracked_paths(root):
        abs_path = os.path.join(root, *path.split("/"))
        try:
            blob = open(abs_path, "rb").read()
        except OSError:
            continue
        if _is_binary(blob):
            continue
        text = blob.decode("utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for digest in _matching_hmacs(line, key, registry):
                hits.append({"path": path, "identifier_hmac": digest, "line_no": line_no})
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
        _run_git(tmp, ["init"])
        probe = os.path.join(tmp, "probe.txt")
        with open(probe, "w", encoding="utf-8", newline="\n") as f:
            f.write(canary(key) + "\n")
        _run_git(tmp, ["add", "probe.txt"])
        hits = scan_tree(tmp, key, registry)
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
