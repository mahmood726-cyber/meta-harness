"""CI probe: dump the replayed review core for a slug beside the committed one, so a platform-specific
replay mismatch can be diffed field by field. Not part of the standard; lives on a probe branch only."""
import json
import os
import platform
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from reproduce_review import replay_core  # noqa: E402
from harness.canonical import review_sha256  # noqa: E402

slug = sys.argv[1]
os.makedirs(os.path.join(ROOT, "probe_out"), exist_ok=True)
core = replay_core(slug)
json.dump(core, open(os.path.join(ROOT, "probe_out", f"{slug}.replay.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump({"platform": platform.platform(), "python": sys.version, "review_sha256": review_sha256(core)},
          open(os.path.join(ROOT, "probe_out", "meta.json"), "w", encoding="utf-8"), indent=1)
print("replay review_sha256", review_sha256(core))
