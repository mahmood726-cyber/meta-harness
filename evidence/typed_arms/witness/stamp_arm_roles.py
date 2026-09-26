"""Write the `arm_roles` block (arm_roles.py) into every witness packet's row.json.
usage: stamp_arm_roles.py <packets dir> [<packets dir> ...]   (job dirs and the committed extractions_* copies)"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from arm_roles import arm_roles_for, ROOT  # noqa: E402


def registry_paths(row):
    out = []
    for d in row.get("documents") or []:
        o = d.get("origin") or ""
        if o.startswith("evidence/typed_arms/registry/") and o.endswith(".json"):
            out.append(os.path.join(ROOT, o))
    return out


def main(dirs):
    n = 0
    for base in dirs:
        for j in sorted(os.listdir(base)):
            p = os.path.join(base, j, "row.json")
            if not os.path.exists(p):
                continue
            row = json.load(open(p, encoding="utf-8"))
            slug = row.get("slug") or (row.get("held_key") or "").split("/")[0]
            row["arm_roles"] = arm_roles_for(slug, registry_paths(row))
            json.dump(row, open(p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
            n += 1
    print(n, "packets stamped")


if __name__ == "__main__":
    main(sys.argv[1:])
