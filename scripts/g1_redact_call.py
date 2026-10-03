"""Redact ABSOLUTE local paths from a recorded model call before it is committed, the way the V1.0.1 round-14 recorder
(evid2 branch, reproducible_ai/model_call_live._local_path_redacted) does at record time; acq/k-gap's recorder predates
that fix, and this lane does not edit the shared module. The file NAME is kept, the directory becomes a digest. The
record is re-identified (record_id is a digest of the whole record) and carries `redacted_post_hoc` with the original
id; references in the lane's own outputs and the lane log are rewritten to the new id. Replay is unchanged (the
response is not touched).

  python scripts/g1_redact_call.py RECORD_ID [JSON files that reference it ...]
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_source as ms  # noqa: E402

REC_DIR = os.path.join(ROOT, "registry", "model_calls")
LANE_LOG = os.path.join(REC_DIR, "lane_log", "unattributed.jsonl")
_ABS = re.compile(r"^(?:[A-Za-z]:[\\/]|/(?:[a-z]/|Users/|home/))")


def redact_path(p):
    if not isinstance(p, str) or not _ABS.match(p):
        return p
    return ("<local path outside the workdir, sha256 " + hashlib.sha256(p.encode("utf-8")).hexdigest()[:12] + ">/"
            + re.split(r"[\\/]+", p.rstrip("\\/"))[-1])


def walk(x):
    if isinstance(x, dict):
        return {k: walk(v) for k, v in x.items()}
    if isinstance(x, list):
        return [walk(v) for v in x]
    return redact_path(x)


_ABS_IN = re.compile(r"(?<![\w<])(?:[A-Za-z]:[\\/]{1,8}|/Users/|/home/)")


def redact_log_line(d):
    """A lane-log line of a call that read OUTSIDE its workdir: the transcript is withheld (it can carry the contents of
    the files read -- here the head of two of the user's own registries) with the prompt digest kept, as the round-14
    recorder does; tool-call commands naming an absolute path are withheld, their outcome kept; paths become digests."""
    d = walk(d)
    outside = any(str(f).startswith("<local path outside") for f in d.get("files_read") or [])
    if outside or _ABS_IN.search(json.dumps(d.get("transcript_redacted") or "")):
        m = re.search(r"<prompt sha256 ([0-9a-f]{64})>", d.get("transcript_redacted") or "")
        d["transcript_redacted"] = ("<withheld: the call read outside its workdir" +
                                    (f"; prompt sha256 {m.group(1)}" if m else "") + ">")
        d["outside_workdir_reads"] = True
    for t in d.get("tool_calls") or []:
        for k in ("command", "outcome"):
            if isinstance(t.get(k), str) and _ABS_IN.search(t[k]):
                t[k] = "<withheld: names an absolute local path>" if k == "command" else t[k].split(":", 1)[0] + ": <withheld>"
    return d


def main(argv):
    old, refs = argv[0], argv[1:]
    rec = ms.load_record(os.path.join(REC_DIR, old + ".json"))
    red = dict(rec, client_evidence=walk(rec.get("client_evidence")))
    if red == rec:
        print("nothing to redact")
        return
    red.pop("record_id")
    red["redacted_post_hoc"] = {"by": "scripts/g1_redact_call.py", "original_record_id": old,
                                "fields": ["client_evidence"], "why": "absolute local paths read by the client"}
    red["record_id"] = ms.record_id_of(red)
    new = red["record_id"]
    assert ms.replay(red) == ms.replay(rec)
    open(os.path.join(REC_DIR, new + ".json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(red, indent=1, ensure_ascii=False) + "\n")
    os.remove(os.path.join(REC_DIR, old + ".json"))
    lines = open(LANE_LOG, encoding="utf-8").read().splitlines()
    out = []
    for ln in lines:
        if old in ln:
            ln = json.dumps(dict(redact_log_line(json.loads(ln)), record_id=new), ensure_ascii=False)
        out.append(ln)
    open(LANE_LOG, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    for f in refs:
        s = open(f, encoding="utf-8").read()
        open(f, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print(old, "->", new)


if __name__ == "__main__":
    main(sys.argv[1:])
