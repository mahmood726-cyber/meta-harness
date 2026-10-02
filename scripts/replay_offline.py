"""Read-only corpus replay with denied networking and observed dependency reporting."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def deny_network(event, args):
    if event in {"socket.connect", "socket.connect_ex", "socket.getaddrinfo", "socket.sendto"}:
        raise RuntimeError("REFUSED: offline replay attempted network access: " + event)
    if event == "subprocess.Popen":
        raise RuntimeError("REFUSED: offline replay attempted a child process")


def recorded_registration(slug):
    """Replay recorded presentation metadata, never infer history from a dirty commit.

    The regenerated page/certificate bind this field. It is not new evidence that a
    registration was prospective; an independent history audit is outside replay.
    """
    review = json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))
    return dict(review["reproduction"]["preregistration"])


def snapshot_reader(root, held_documents):
    """Adapt the legacy git-show custody read to certificate-bound package bytes.

    This replays a recorded snapshot, not Git's assertion of historical custody.
    All other subprocess requests remain forbidden. No numerical output is reused.
    """
    root = Path(root).resolve()
    pinned = {item["ref"]: item["sha256"] for item in held_documents}

    def read(command, *, cwd):
        if (Path(cwd).resolve() != root or not isinstance(command, list)
                or len(command) != 3 or command[:2] != ["git", "show"]
                or not command[2].startswith("HEAD:")):
            raise RuntimeError("REFUSED: unsupported snapshot lookup")
        ref = command[2][5:]
        path = (root / ref).resolve()
        if ref not in pinned or not path.is_relative_to(root):
            raise RuntimeError("REFUSED: unpinned snapshot document: " + ref)
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != pinned[ref]:
            raise RuntimeError("REFUSED: snapshot document digest mismatch: " + ref)
        return data

    return read


def observed_dependencies():
    # Namespace names alone are ambiguous: unrelated installed distributions may
    # advertise `scripts` or `tests`, although this replay imported our local files.
    loaded = {name for name, module in sys.modules.items() if "." not in name
              and any(part in {"site-packages", "dist-packages"}
                      for part in Path(getattr(module, "__file__", "") or "").parts)}
    mapping = importlib.metadata.packages_distributions()
    return {dist: importlib.metadata.version(dist)
            for name in sorted(loaded) for dist in mapping.get(name, [])
            if name not in sys.stdlib_module_names}


def dependency_errors(dependencies):
    lock = ROOT / "docs/offline/requirements.lock"
    pinned = {}
    for line in lock.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            name, version = line.split()[0].split("==")
            pinned[name.lower().replace("_", "-")] = version
    return [f"unlocked runtime distribution: {name}=={version}"
            for name, version in dependencies.items()
            if pinned.get(name.lower().replace("_", "-")) != version]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="*")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    # CPython's Windows platform probe may invoke the local `ver` shell builtin.
    # Cache that OS identity before denying every replay child process.
    platform.system()
    sys.addaudithook(deny_network)
    from scripts.generate_replay import check
    problems = check(ROOT)
    if problems:
        raise RuntimeError("REFUSED: " + "; ".join(problems))
    from scripts.reproduce_review import reproduce
    from harness import registration
    registration.preregistration_sha = recorded_registration
    slugs = args.slugs or [p.name for p in sorted((ROOT / "docs/reviews").iterdir())
                           if (p / "manifest.json").is_file()]
    results = []
    for slug in slugs:
        if slug not in {p.name for p in (ROOT / "docs/reviews").iterdir() if (p / "manifest.json").is_file()}:
            raise ValueError("Unknown topic: " + slug)
        directory = ROOT / "docs/reviews" / slug
        cert = json.loads((directory / "CERTIFICATE.json").read_text(encoding="utf-8"))
        subprocess.check_output = snapshot_reader(ROOT, cert["held_documents"])
        try:
            ok, reasons = reproduce(slug)
        except (OSError, ValueError, RuntimeError) as exc:
            ok, reasons = False, [str(exc)]
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        manifest_agrees = hashlib.sha256((directory / "index.html").read_bytes()).hexdigest() == manifest["html_sha256"]
        if not manifest_agrees:
            reasons.append("served page bytes disagree with manifest.html_sha256")
        ok = ok and manifest_agrees
        results.append({"slug": slug, "exact": ok, "manifest_agrees": manifest_agrees, "reasons": reasons})
        print(f"{'PASS' if ok else 'FAIL'} {slug}", flush=True)
    report = {"topics": results, "dependencies": observed_dependencies(),
              "python": sys.version, "network": "socket operations and child processes denied",
              "registration": "recorded presentation metadata; no Git history required",
              "custody": "certificate-bound held-document bytes; historical Git custody not independently established"}
    report["dependency_errors"] = dependency_errors(report["dependencies"])
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"exact": sum(r["exact"] for r in results), "topics": len(results),
                      "manifest_agrees": sum(r["manifest_agrees"] for r in results),
                      "dependencies": report["dependencies"], "dependency_errors": report["dependency_errors"]}))
    return int(any(not r["exact"] for r in results) or bool(report["dependency_errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
