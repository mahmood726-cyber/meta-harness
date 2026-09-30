"""Read-only census of every tracked table excerpt, including outside evidence/."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.table_rows import _measures, parse, typed


def census(root=ROOT):
    names = subprocess.check_output(["git", "ls-files", "--", "*.tables.txt", "topics/*.json"],
                                    cwd=root, text=True, encoding="utf-8").splitlines()
    paths = sorted(n for n in names if n.endswith(".tables.txt"))
    topics = sorted(n for n in names if n.startswith("topics/") and n.endswith(".json"))
    # All topics inspected; excerpt coverage is file/row based, not inferred trial binding.
    for name in topics:
        json.loads((root / name).read_text(encoding="utf-8-sig"))
    hits = {key: [] for key in ("resolved_measure", "footnote_measure", "ambiguous_header_unknown",
                               "variant", "NON_CABG", "LEADING_TO_DISCONTINUATION", "SERIOUS")}
    rows = tables = 0
    for name in paths:
        for ti, table in enumerate(parse(root / name), 1):
            tables += 1
            table_id = f"{name} :: table {ti} :: {table['caption']}"
            unknown = False
            for ri, row in enumerate(table["rows"], 1):
                rows += 1
                value = typed(row, table)
                rid = f"{table_id} :: row {ri} :: {row['label']}"
                if value["measure"] != "UNKNOWN":
                    hits["resolved_measure"].append(rid)
                    if value["measure_basis"] == "footnote":
                        hits["footnote_measure"].append(rid)
                else:
                    unknown = True
                if value["variant_flags"]:
                    hits["variant"].append(rid)
                for flag in value["variant_flags"]:
                    hits[flag].append(rid)
            if unknown and len(_measures(" ".join(table["header"]))) > 1:
                hits["ambiguous_header_unknown"].append(table_id)
    rules = {}
    for key, items in hits.items():
        total = tables if key == "ambiguous_header_unknown" else rows
        rules[key] = dict(n=len(items), N=total, census=f"{len(items)} of {total}", items=items)
    return dict(excerpt_files=paths, topic_files_examined=len(topics), tables=tables, rows=rows, rules=rules)


if __name__ == "__main__":
    print(json.dumps(census(), ensure_ascii=False, indent=2))
