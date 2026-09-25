"""Plants run against the PRE-B walker (scripts/sign_walk.py at 1fa77f2c) and the post-B walker, in memory only.

Shows the two defects decision B removes, observed on the old code first:
  P1 a rebuild that only churns the page REFUSES the old walker (a rebuild detaches a notice);
  P2 after P1, the old recovery (refresh the working-tree digest) lets a notice whose served number has CHANGED
     present with a signing command (re-pointing without re-judgement serves a stale transition).
The post-B walker presents P1 with a disclosure and refuses P2 as STALE; neither run writes a file.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
OLD_REV = "1fa77f2c4852ee79e55d540083e3c35bbff0cecc"


def show(path):
    return subprocess.run(["git", "show", f"{OLD_REV}:{path}"], cwd=W, capture_output=True, check=True).stdout


old_src = W / "scripts" / "_sign_walk_pre_b_tmp.py"
old_src.write_bytes(show("scripts/sign_walk.py"))
try:
    spec = importlib.util.spec_from_file_location("sign_walk_pre_b", old_src)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
finally:
    old_src.unlink()
from scripts import sign_walk as new  # noqa: E402

OLD_AUDIT = json.loads(show("registry/notice_adjudication.json"))
page = W / "docs/reviews/pcsk9-mace/index.html"
review = W / "docs/reviews/pcsk9-mace/review.json"
real_read_bytes, real_read_text = Path.read_bytes, Path.read_text
fake: dict[Path, bytes] = {}
audit_override = {}


def read_bytes(p):
    return fake.get(Path(p).resolve(), None) or real_read_bytes(p)


def read_text(p, *a, **k):
    if Path(p).resolve() == old.AUDIT.resolve() and "audit" in audit_override:
        return json.dumps(audit_override["audit"])
    if Path(p).resolve() in fake:
        return fake[Path(p).resolve()].decode("utf-8")
    return real_read_text(p, *a, **k)


Path.read_bytes, Path.read_text = read_bytes, read_text


def run(mod, args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mod.main(args)
    text = out.getvalue()
    return rc, ("presents WITH a signing command" if "countersign_result_change.py sign" in text else
                "presents, no command" if text else "REFUSES: " + err.getvalue().strip()[:230])


def report(label, mod, args):
    rc, what = run(mod, args)
    print(f"{label}: rc={rc}; {what}")


try:
    audit_override["audit"] = OLD_AUDIT
    report("P0 old walker, no plant (positive control)", old, ["--notice", "N28"])
    audit_override.clear()
    report("P0 new walker, no plant (positive control)", new, ["--notice", "N28"])

    fake[page.resolve()] = real_read_bytes(page) + b"<!-- rebuilt -->"
    audit_override["audit"] = OLD_AUDIT
    report("P1 old walker, page re-rendered (churn only)", old, ["--notice", "N28"])
    audit_override.clear()
    report("P1 new walker, page re-rendered (churn only)", new, ["--notice", "N28"])

    doc = json.loads(real_read_bytes(review))
    for o in doc["outcomes"]:
        if o["name"] == "Major adverse cardiovascular events":
            o["result"]["estimate"] = 0.84  # the served number moves; the notice still says 0.85
    fake[review.resolve()] = json.dumps(doc).encode("utf-8")
    repointed = json.loads(json.dumps(OLD_AUDIT))
    for rel in ("docs/reviews/pcsk9-mace/index.html", "docs/reviews/pcsk9-mace/review.json"):
        repointed["source_digests"][rel] = hashlib.sha256(fake[(W / rel).resolve()]).hexdigest()  # the old recovery
    audit_override["audit"] = repointed
    report("P2 old walker, served number moved + digests refreshed", old, ["--notice", "N28"])
    audit_override.clear()
    report("P2 new walker, served number moved (no digest to refresh)", new, ["--notice", "N28"])
finally:
    Path.read_bytes, Path.read_text = real_read_bytes, real_read_text
print("files written in the repository: 0 (plants in memory; the temporary copy of the old walker was removed)")
