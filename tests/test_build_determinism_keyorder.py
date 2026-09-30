"""Offline byte-order replay. Run this file with --census for the lane census.

The held reproduction envelope is retained: certificates describe committed code,
and recomputing them after a source edit would measure provenance changes as well.
All review-core fields are rebuilt from held inputs, without canonical sorting.
"""
import ast
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import hashlib
import inspect
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SLUG = "colchicine-postop-af"


def _refuse_network(*args, **kwargs):
    raise AssertionError("DETERM refused network access during held-input replay")


@contextmanager
def _unordered_plant(enabled):
    from harness import pipeline
    original = pipeline._apply_trial_annotations
    if enabled:
        tree = ast.parse(inspect.getsource(original))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "allowed" for t in node.targets
            ):
                node.value = ast.Set(elts=node.value.elts)
        namespace = {}
        exec(compile(ast.fix_missing_locations(tree), "<unordered-plant>", "exec"),
             pipeline.__dict__, namespace)
        pipeline._apply_trial_annotations = namespace[original.__name__]
    try:
        yield
    finally:
        pipeline._apply_trial_annotations = original


def _build(slug):
    from harness.pipeline import build_review_core
    def read(path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    held_path = ROOT / f"docs/reviews/{slug}/review.json"
    held = read(f"docs/reviews/{slug}/review.json") if held_path.exists() else None
    if held is None:
        from harness.registration import protocol_sha
        anchor = protocol_sha(slug)
        if not anchor:
            raise ValueError(f"DETERM refused missing protocol anchor: {slug}")
    else:
        anchor = held["reproduction"]["protocol_sha"]
    core = build_review_core(
        slug, read(f"topics/{slug}.json"), read(f"cache/{slug}/records.json"),
        anchor,
    )
    if held is not None:
        core["reproduction"] = held["reproduction"]
    return core


def _bytes(review):
    return json.dumps(review, ensure_ascii=False, indent=2).encode("utf-8")


def _run(seed, plant=False, census=False):
    args = [sys.executable, "-B", str(Path(__file__).resolve()),
            "--census-worker" if census else "--worker"]
    if plant:
        args.append("--plant")
    if census:
        args.append(census)
    result = subprocess.run(
        args, cwd=ROOT, env=dict(os.environ, PYTHONHASHSEED=str(seed),
                                PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
                                GIT_OPTIONAL_LOCKS="0"),
        capture_output=True, timeout=180 if census else 600,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    return result.stdout


@contextmanager
def _dummy_file():
    path = ROOT / "harness" / "_determ_unimported_probe.py"
    # Exclusive creation prevents overwriting an unrelated file; always remove ours.
    with path.open("x", encoding="utf-8", newline="") as handle:
        handle.write("raise AssertionError('DETERM dummy must never be imported')\n")
    try:
        yield
    finally:
        path.unlink()


def _assert_same(left, right):
    assert left == right, f"DETERM refused non-identical review.json replay: {SLUG}"


def test_topic_bytes_across_seeds_and_unimported_file():
    baseline = _run(0)
    _assert_same(baseline, _run(12345))
    with _dummy_file():
        _assert_same(baseline, _run(0))
        _assert_same(baseline, _run(12345))


def test_unordered_iteration_plant_is_caught():
    left, right = _run(0, plant=True), _run(12345, plant=True)
    assert json.loads(left) == json.loads(right), "plant must change only key order"
    with _dummy_file():
        _assert_same(left, _run(0, plant=True))
    with pytest.raises(AssertionError, match="DETERM refused non-identical"):
        _assert_same(left, right)


def test_annotations_preserve_existing_keys_and_values():
    from harness.pipeline import _apply_trial_annotations
    config = json.loads((ROOT / "topics" / f"{SLUG}.json").read_text(encoding="utf-8"))
    spec = next(spec for spec in _specs(config) if spec.get("trial_annotations"))
    pid, annotation = next(iter(spec["trial_annotations"].items()))
    existing = list(annotation)
    row = {"id": pid, **annotation}
    before = list(row)
    _apply_trial_annotations(spec, [row])
    assert list(row) == before
    assert all(row[k] == annotation[k] for k in existing)
    _apply_trial_annotations({}, [row])
    assert list(row) == before


def _specs(config):
    from harness.pipeline import _outcome_specs
    return [spec for spec, _kind in _outcome_specs(config)]


def _differences(a, b, path="$", values=False):
    if type(a) is not type(b):
        return [path] if values else []
    if isinstance(a, dict):
        out = ([path] if (a.keys() != b.keys() if values else
                         a.keys() == b.keys() and list(a) != list(b)) else [])
        for key in a.keys() & b.keys():
            out.extend(_differences(a[key], b[key], f"{path}.{key}", values))
        return sorted(out)
    if isinstance(a, list):
        out = [path] if values and len(a) != len(b) else []
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(_differences(x, y, f"{path}[{i}]", values))
        return out
    return [path] if values and a != b else []


def _census_worker(slug):
    rows = []
    for topic in [ROOT / "topics" / f"{slug}.json"]:
        slug = topic.stem
        try:
            held_path = ROOT / "docs/reviews" / slug / "review.json"
            held_bytes = held_path.read_bytes() if held_path.exists() else None
            held = json.loads(held_bytes) if held_bytes is not None else None
            rebuilt = _build(slug)
            payload = _bytes(rebuilt)
            # Compare JSON values, not producer types (e.g. numpy.float64 versus
            # the built-in float produced by json.loads on the held artifact).
            rebuilt = json.loads(payload)
            rows.append(dict(slug=slug, sha256=hashlib.sha256(payload).hexdigest(),
                             value_sha256=hashlib.sha256(json.dumps(rebuilt, sort_keys=True).encode()).hexdigest(),
                             baseline_missing=held is None,
                             bytes_changed=held is not None and payload != held_bytes,
                             value_paths=_differences(held, rebuilt, values=True) if held else [],
                             order_paths=_differences(held, rebuilt) if held else []))
        except Exception as exc:
            rows.append(dict(slug=slug, error=f"{type(exc).__name__}: {exc}"))
    return rows


def census():
    slugs = [p.stem for p in sorted((ROOT / "topics").glob("*.json"))]
    def examine(slug):
        try:
            row = json.loads(_run(0, census=slug))[0]
        except Exception as exc:
            row = {"slug": slug, "error": f"{type(exc).__name__}: {exc}"}
        print(f"DETERM examined {slug}: {'ERROR' if 'error' in row else 'built'}", file=sys.stderr, flush=True)
        return row
    with ThreadPoolExecutor(max_workers=3) as executor:
        fixed = list(executor.map(examine, slugs))
    def rule(items):
        return {"n": len(items), "N": len(fixed), "items": items}
    result = {
        "scope": "rebuilt full core; held reproduction envelope; no artifact writes",
        "errors": rule([r for r in fixed if "error" in r]),
        "missing_committed_baselines": rule([slug for slug in slugs
            if not (ROOT / "docs/reviews" / slug / "review.json").exists()]),
        "committed_byte_changes": rule([
            {k: v for k, v in r.items() if k not in ("sha256", "value_sha256", "baseline_missing")}
            for r in fixed if r.get("bytes_changed")]),
        "committed_value_changes": rule([r["slug"] for r in fixed if r.get("value_paths")]),
    }
    print(json.dumps(result, indent=2))
    return bool(result["errors"]["n"] or result["committed_value_changes"]["n"])


if __name__ == "__main__":
    socket.socket.connect = _refuse_network
    socket.create_connection = _refuse_network
    if "--census" in sys.argv:
        sys.exit(census())
    else:
        with _unordered_plant("--plant" in sys.argv):
            if "--census-worker" in sys.argv:
                print(json.dumps(_census_worker(sys.argv[-1])))
            else:
                sys.stdout.buffer.write(_bytes(_build(SLUG)))
