"""After a rebuild: revert every review directory whose manifest hashes did not move (pure serialisation
noise -- the landing hash check refuses a touched review whose content hash did not move). Prints the moved list."""
import json, subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); moved = []; reverted = []
for d in sorted((root / "docs/reviews").glob("*/")):
    slug = d.name; mp = f"docs/reviews/{slug}/manifest.json"
    try:
        new = json.loads((root / mp).read_text(encoding="utf-8"))
        old = json.loads(subprocess.check_output(["git", "-C", str(root), "show", f"HEAD:{mp}"]).decode("utf-8"))
    except Exception as e:
        print("SKIP", slug, e); continue
    if new.get("review_sha256") == old.get("review_sha256") and new.get("html_sha256") == old.get("html_sha256"):
        subprocess.run(["git", "-C", str(root), "checkout", "-q", "--", f"docs/reviews/{slug}"]); reverted.append(slug)
    else:
        moved.append(slug)
print("moved:", len(moved), moved); print("reverted (unmoved):", len(reverted))
