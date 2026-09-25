"""Temporarily edit harness/result_changes.py and harness/page.py in the worktree with W1+W2 (restored by the caller
with `git checkout -- harness/`)."""
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
p = W / "harness/result_changes.py"
s = p.read_text(encoding="utf-8")
old = '''    b, a = significance(before, scale), significance(after, scale)
    if before.get("estimate") is not None and after.get("estimate") is None:'''
new = '''    b, a = significance(before, scale), significance(after, scale)
    if before.get("estimate") is None and after.get("estimate") is None:
        # No estimate was served before and none is served now: nothing is withdrawn. (The block says so.)
        return None
    if before.get("estimate") is not None and after.get("estimate") is None:'''
assert old in s
s = s.replace(old, new)
old = '''    if b == "includes_null" and a == "excludes_null":
        return "the interval now excludes the null: a difference is now claimed that was not before"
    return None'''
new = '''    if b == "includes_null" and a == "excludes_null":
        return "the interval now excludes the null: a difference is now claimed that was not before"
    if b is None and before.get("estimate") is not None and a == "excludes_null":
        return ("an interval is now served and it excludes the null: a difference is now claimed; no interval "
                "was served before")
    return None'''
assert old in s
s = s.replace(old, new)
p.write_bytes(s.encode("utf-8"))

p = W / "harness/page.py"
s = p.read_text(encoding="utf-8")
old = '''                else "The direction of the estimate is unchanged. ")'''
new = '''                else ("No pooled estimate was served before and none is served now; only the candidate trials "
                      "changed, and no conclusion is withdrawn. ")
                if b.get("estimate") is None and a.get("estimate") is None
                else "The direction of the estimate is unchanged. ")'''
assert old in s
s = s.replace(old, new)
p.write_bytes(s.encode("utf-8"))
print("applied")
