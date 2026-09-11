"""Collect model spans from the 7 Fable task-output files into scratchpad/dual_spans.json.
Parses each subagent transcript as JSONL, walks string values, and extracts the span-map JSON
(keys contain '|'). Runs in a subprocess so transcripts never enter the caller's context."""
import json
import os
import re
import sys

TASKS, SCRATCH = sys.argv[1], sys.argv[2]
IDS = ["a502a86548a078736", "a51003d4125fcdcab", "a3bf64656979597fb", "aa0fe185a7336d6d4",
       "abb912e2c59b59022", "aee6c88b7b5946166", "a6906bd20851251b2"]


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)


def _extract_map(text):
    """Find a JSON object in text whose keys contain '|' (our span map)."""
    # strip code fences
    for block in re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S) + [text]:
        # try progressively: whole block, then the largest {...}
        for cand in ([block] + re.findall(r"\{.*\}", block, re.S)):
            try:
                d = json.loads(cand)
                if isinstance(d, dict) and any("|" in k for k in d):
                    return d
            except Exception:
                continue
    return None


merged = {}
for i in IDS:
    p = os.path.join(TASKS, i + ".output")
    if not os.path.exists(p):
        print("missing", i); continue
    found = None
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        for s in _strings(ev):
            if "|" in s and "{" in s:
                d = _extract_map(s)
                if d:
                    found = d  # keep the last (final result)
    if found:
        merged.update(found)
    else:
        print("no span-map parsed for", i)
json.dump(merged, open(os.path.join(SCRATCH, "dual_spans.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("collected", len(merged), "spans")
