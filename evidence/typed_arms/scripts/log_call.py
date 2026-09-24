"""Summarise one codex --json event stream into one CALL_LOG line: prompt, model, commands run, files read, tokens,
whether out.json exists (an artefact fact, not an exit code), and any path read OUTSIDE the job dir (named, never copied)."""
import json, sys, os, re, hashlib
key, job, stream, model, prompt = sys.argv[1:6]
cmds, usage, errors = [], {}, []
for line in open(stream, encoding="utf-8", errors="replace"):
    try: ev = json.loads(line)
    except Exception: continue
    t = ev.get("type", "")
    item = ev.get("item") or {}
    if item.get("type") == "command_execution" and t == "item.completed": cmds.append(item.get("command", ""))
    if t == "turn.completed": usage = ev.get("usage") or usage
    if t in ("error", "turn.failed"): errors.append(str(ev)[:300])
paths = sorted({m for c in cmds for m in re.findall(r"[A-Za-z]:[\/][^\s'\"]+|(?:\.\/)?[\w.-]+\.(?:json|txt|md)", c)})
jobn = os.path.normcase(os.path.abspath(job))
outside = [p for p in paths if re.match(r"[A-Za-z]:", p) and not os.path.normcase(os.path.abspath(p)).startswith(jobn)]
out = os.path.join(job, "out.json")
sys.stdout.buffer.write((json.dumps({"key": key, "stream": os.path.basename(stream), "model": model, "prompt": prompt,
                  "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "commands": cmds, "files_named": paths,
                  "outside_job_dir": outside, "tokens": usage, "errors": errors,
                  "out_json_exists": os.path.exists(out) and os.path.getsize(out) > 0}, ensure_ascii=False) + chr(10)).encode("utf-8"))
