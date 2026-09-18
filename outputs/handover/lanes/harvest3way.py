"""Three-way harvest of a lane's working tree into the integration tree.

usage: python harvest3way.py <lane_clone> <base_ref_or_dir> <target_tree> <list_file> [--dry]
  lane_clone   : the lane's clone (its working tree = 'theirs')
  base         : a git ref (resolved in the lane clone) or a directory holding the common base versions
  target_tree  : the integration tree ('ours')
  list_file    : one relative path per line (the lane's changed/untracked paths to harvest)
For each path: absent in target -> copy; target == base -> copy theirs; theirs == base -> keep ours; else git merge-file
(ours, base, theirs) -> clean merge written, or CONFLICT left with markers and reported. Deleted-in-lane paths are
listed for manual decision (never deleted automatically). Prints a table; exit 1 if any conflict.
"""
import filecmp
import io
import os
import pathlib
import shutil
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
lane, base, target, listfile = sys.argv[1:5]
dry = "--dry" in sys.argv
base_is_dir = os.path.isdir(base)
tmp = pathlib.Path(target) / ".tmp" / "harvest3way"
tmp.mkdir(parents=True, exist_ok=True)


def base_bytes(rel):
    if base_is_dir:
        p = pathlib.Path(base) / rel
        return p.read_bytes() if p.exists() else None
    proc = subprocess.run(["git", "-C", lane, "show", f"{base}:{rel}"], capture_output=True)
    return proc.stdout if proc.returncode == 0 else None


rows = {"copied-new": [], "copied-theirs": [], "kept-ours": [], "merged": [], "CONFLICT": [], "identical": [], "deleted-in-lane": []}
for rel in [x.strip() for x in open(listfile, encoding="utf-8") if x.strip()]:
    theirs = pathlib.Path(lane) / rel
    ours = pathlib.Path(target) / rel
    if not theirs.exists():
        rows["deleted-in-lane"].append(rel)
        continue
    if not ours.exists():
        rows["copied-new"].append(rel)
        if not dry:
            ours.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(theirs, ours)
        continue
    if filecmp.cmp(theirs, ours, shallow=False):
        rows["identical"].append(rel)
        continue
    b = base_bytes(rel)
    if b is None or ours.read_bytes() == b:
        rows["copied-theirs"].append(rel)
        if not dry:
            shutil.copy2(theirs, ours)
        continue
    if theirs.read_bytes() == b:
        rows["kept-ours"].append(rel)
        continue
    bfile = tmp / (rel.replace("/", "__") + ".base")
    bfile.write_bytes(b)
    merged = tmp / (rel.replace("/", "__") + ".merged")
    shutil.copy2(ours, merged)
    proc = subprocess.run(["git", "merge-file", "-L", "ours", "-L", "base", "-L", "theirs", str(merged), str(bfile), str(theirs)],
                          capture_output=True, text=True)
    if proc.returncode == 0:
        rows["merged"].append(rel)
        if not dry:
            shutil.copy2(merged, ours)
    else:
        rows["CONFLICT"].append(rel)
        if not dry:
            shutil.copy2(merged, ours)
for k, v in rows.items():
    print(f"{k:16s} {len(v)}")
    for rel in v:
        if k in ("CONFLICT", "merged", "deleted-in-lane", "kept-ours"):
            print("   ", rel)
sys.exit(1 if rows["CONFLICT"] else 0)
