"""LOCAL rehearsal candidate (never pushed): 1fa77f2c with N28's served after moved 0.85 -> 0.84 consistently in the
ledger, review.json and index.html -- the shape of a notice the V1 fix CHANGES. Built with a temporary index."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

R = r"C:/mh-lanes/nr/repo"
B = "1fa77f2c4852ee79e55d540083e3c35bbff0cecc"


def g(*a, env=None, data=None):
    p = subprocess.run(["git", *a], cwd=R, capture_output=True, env=env, input=data)
    assert p.returncode == 0, p.stderr
    return p.stdout


ledger = json.loads(g("show", f"{B}:docs/result_changes.json"))
n = ledger["notices"][40]
assert n["slug"] == "pcsk9-mace" and n["after"]["estimate"] == 0.85, n["after"]
n["after"]["estimate"] = 0.84
review = json.loads(g("show", f"{B}:docs/reviews/pcsk9-mace/review.json"))
o = next(o for o in review["outcomes"] if o["name"] == n["outcome"])
assert o["result"]["estimate"] == 0.85
o["result"]["estimate"] = 0.84
html = g("show", f"{B}:docs/reviews/pcsk9-mace/index.html").decode("utf-8")
old = "Now: k = 1, 0.85 (0.78 to 0.93)."
assert html.count(old) == 1, html.count(old)
html = html.replace(old, "Now: k = 1, 0.84 (0.78 to 0.93).")
with tempfile.TemporaryDirectory() as t:
    env = dict(os.environ, GIT_INDEX_FILE=str(Path(t) / "idx"))
    g("read-tree", B, env=env)
    for path, data in (("docs/result_changes.json", json.dumps(ledger, ensure_ascii=False, indent=1) + "\n"),
                       ("docs/reviews/pcsk9-mace/review.json", json.dumps(review, ensure_ascii=False, indent=1) + "\n"),
                       ("docs/reviews/pcsk9-mace/index.html", html)):
        b = g("hash-object", "-w", "--stdin", data=data.encode("utf-8")).decode().strip()
        g("update-index", "--cacheinfo", f"100644,{b},{path}", env=env)
    tree = g("write-tree", env=env).decode().strip()
c = g("commit-tree", tree, "-p", B, "-m", "LOCAL PLANT (changed N28) -- never pushed").decode().strip()
g("update-ref", "refs/plants/changed", c)
print("refs/plants/changed", c)
