import json
import sys

sys.path.insert(0, "evidence/v11_tag_strip")
sys.path.insert(0, ".")
import rederive_audit_surfaces as ras  # noqa: E402

ras.old_strip = lambda text, repl=" ": ""          # the plant: a stripper that deletes ALL held text
open("evidence/v11_tag_strip/control_slugs.txt", "w").write("glp1-ra-mace-t2d\ncolchicine-postop-af\n")
ras.main("evidence/v11_tag_strip/control_slugs.txt", "evidence/v11_tag_strip/audit_surfaces_POSITIVE_CONTROL.json")
