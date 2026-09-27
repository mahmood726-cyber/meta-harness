"""One codex audit job for one topic. Read-only sandbox in the extract; stdin closed; every call logged to calls.jsonl."""
import datetime
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

A = Path(__file__).resolve().parent
slug = sys.argv[1]
ctx = (A / "LANE_CONTEXT.md").read_text(encoding="utf-8")
census = json.loads((A / "census_by_topic.json").read_text(encoding="utf-8")).get(slug, "- (no census rows)")
prompt = ((A / "prompt_template.md").read_text(encoding="utf-8")
          .replace("{LANE_CONTEXT}", ctx).replace("{SLUG}", slug).replace("{CENSUS}", census))
(A / "prompts").mkdir(exist_ok=True)
(A / "out").mkdir(exist_ok=True)
(A / "logs").mkdir(exist_ok=True)
(A / "prompts" / f"{slug}.md").write_text(prompt, encoding="utf-8")
out = A / "out" / f"{slug}.json"
t0 = time.time()
start = datetime.datetime.now().isoformat(timespec="seconds")
CODEX = "C:/Users/mahmo/AppData/Roaming/npm/codex.cmd"
cmd = [CODEX, "exec", "-s", "read-only", "--skip-git-repo-check", "-C", str(A / "tree"),
       "--output-schema", str(A / "schema.json"), "-o", str(out), "-"]      # prompt on stdin: a file, so EOF is certain
try:
    import os
    tmp = A / "tmp"
    tmp.mkdir(exist_ok=True)
    env = {**os.environ, "TEMP": str(tmp), "TMP": str(tmp), "TMPDIR": str(tmp)}   # never F:\claude-temp (disk emergency)
    with open(A / "prompts" / f"{slug}.md", "rb") as fin:
        p = subprocess.run(cmd, stdin=fin, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=2700, env=env)
    rc, so, se = p.returncode, p.stdout, p.stderr
except subprocess.TimeoutExpired as e:
    rc, so, se = "TIMEOUT", (e.stdout or ""), (e.stderr or "")
    so = so if isinstance(so, str) else so.decode("utf-8", "replace")
    se = se if isinstance(se, str) else se.decode("utf-8", "replace")
(A / "logs" / f"{slug}.log").write_text(so + "\n----STDERR----\n" + se, encoding="utf-8")
tok = re.findall(r"tokens used\s*\n?\s*([\d,]+)", so + se)
rec = {"topic": slug, "start": start, "end": datetime.datetime.now().isoformat(timespec="seconds"),
       "seconds": round(time.time() - t0), "rc": rc, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
       "tokens": tok[-1] if tok else None, "output": str(out), "output_exists": out.is_file(),
       "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest() if out.is_file() else None}
with open(A / "calls.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
