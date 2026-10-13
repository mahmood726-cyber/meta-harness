"""D8 incident #3 (Mahmood, signed 13 Oct: "both" -- record it as a named incident AND redact going forward).

Every committed model-call record whose prompt carries text from a copy that is not CC BY / CC0 (the class is derived
from the shared guard, record_licence.record_problems -- 33 records on 13 Oct, not the 13 first reported). For each:
  * the prompt BYTES are withheld; its sha256 and length stay, plus `d8_redaction` naming the incident, the PMIDs and
    licences, and the original record_id -- so the redaction is auditable and the run ledger's prompt digest still links;
  * the response is untouched (its blob is byte-identical -- asserted). A withheld prompt cannot replay (precedent:
    evidence/scripts/codex_job.py), so record_problems must report exactly that and nothing else -- asserted;
  * a recorded read that rested on one of these calls (registry/provenance_recorded_reads.json) is WITHDRAWN: the
    upgrade to RECORDED_MODEL_CALL requires a replayable read (harness/provenance_class.served_class), and its `shown`
    said "CC full text" when the copy was NC. The served number is unchanged; the row's class returns to HAND_ENTERED;
  * the record is re-identified (record_id is a digest of the whole record) and every reference in the tree is rewritten;
  * the lane-log line's transcript (which can echo the prompt) is withheld the same way.
The incident itself is written to registry/d8_incidents.json. History is NOT rewritten (main is never rewritten): the
withheld bytes remain in git history; this is redaction going forward, as signed.

    python scripts/d8_redact_incident3.py            (idempotent: an already-redacted record is skipped)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_source as ms  # noqa: E402

DECISION = {"by": "Mahmood", "via": "Dispatch", "when": "2026-10-13",
            "words": "sign and do as you suggested for all",
            "item": "MORNING_SUMMARY_2026-10-13 item 2 (D8 incident #3): both -- named incident + redact going forward",
            "packet_sha256": "6bf07e9d1cf314bb594c3ed2dd2eb70cf526913f797d5e930344a9f93c63ffa6"}
# The class is DERIVED, never typed: every tracked record the shared guard (reproducible_ai/record_licence.record_problems)
# says carries text from a copy not CC BY / CC0. The 13 Oct summary said "13"; the guard's own list was 33 (the 13 came
# from a fingerprint audit, a reach figure). Each source's licence is the guard's verdict plus, for a Creative Commons
# copy, the restriction its own statement names.
from reproducible_ai import record_licence as rl  # noqa: E402

_PROB = re.compile(r"prompt carries (\d+) chars of (.+?) text(?: \((?:structural|declared)\))?; its (?:Unpaywall )?copy is "
                   r"not (?:CC-licensed|marked open) \((?:licence|copy_licence)?=?(.*)\)$")


def _restriction(source, verdict):
    """The restriction the copy's OWN statement names (NonCommercial, NoDerivs, CC BY-NC-ND, ...), else None."""
    m = re.match(r"comparator JATS (\d+)", source)
    txt = ""
    if m and rl._comparator_jats(m.group(1)):
        x = open(rl._comparator_jats(m.group(1)), encoding="utf-8", errors="replace").read()
        txt = " ".join(re.findall(r"<permissions>.*?</permissions>", x, re.S))
    m = re.match(r"PMID (\d+)", source)
    if m:
        idx = json.load(open(rl.INDEX, encoding="utf-8")) if os.path.exists(rl.INDEX) else {}
        txt = str((idx.get(m.group(1)) or {}).get("copy_statement") or "")
    hit = rl._RESTRICTED.search(txt)
    return hit.group(0) if hit else (verdict if "nc" in verdict.lower() or "nd" in verdict.lower() else None)


def incident_class():
    lic, out = rl.licences(), {}
    for f in rl.tracked_records():
        r = json.load(open(f, encoding="utf-8"))
        for pr in rl.record_problems(r, lic):
            m = _PROB.search(pr)
            assert m, f"unparsed guard problem (refusing to guess): {pr}"
            srcs = out.setdefault(r["record_id"], {})
            verdict = m.group(3).strip().strip("'\"")
            srcs.setdefault(m.group(2), {"source": m.group(2), "guard_licence": verdict, "chars": int(m.group(1)),
                                         "restriction_named": _restriction(m.group(2), verdict)})
    return {k: sorted(v.values(), key=lambda x: x["source"]) for k, v in sorted(out.items())}


LEDGER = os.path.join(ROOT, "registry", "d8_incidents.json")


def _tracked(name):
    out = subprocess.run(["git", "ls-files", f"*{name}*"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    return [p for p in out if p.endswith(".json") and os.path.basename(p) == name + ".json"]


def _refs(old):
    return [p for p in subprocess.run(["git", "grep", "-l", old], cwd=ROOT, capture_output=True, text=True).stdout.split()
            if not p.endswith(old + ".json")]


def redact(old, sources):
    paths = _tracked(old)
    if not paths:
        return None
    path = os.path.join(ROOT, paths[0])
    rec = ms.load_record(path)
    p = rec.get("prompt") or {}
    note = {"incident": "D8-3", "sources": sources, "original_record_id": old, "decision": DECISION,
            "what": "prompt bytes withheld (NC/ND full text); sha256 and length kept; response untouched"}
    red = dict(rec, prompt={"b64": None, "sha256": p.get("sha256"), "bytes": p.get("bytes")}, d8_redaction=note)
    red.pop("record_id")
    red["record_id"] = ms.record_id_of(red)
    new = red["record_id"]
    assert red["response"] == rec["response"], "response changed"
    probs = ms.record_problems(red)
    assert len(probs) == 1 and probs[0].startswith("prompt: no stored bytes"), probs
    newpath = os.path.join(os.path.dirname(path), new + ".json")
    open(newpath, "w", encoding="ascii", newline="\n").write(json.dumps(red, indent=1, sort_keys=True, ensure_ascii=True) + "\n")
    os.remove(path)
    for f in [f for f in _refs(old) if f != "registry/held_record_ids.json"]:
        fp = os.path.join(ROOT, f)
        if f.endswith(".jsonl"):
            lines = []
            for ln in open(fp, encoding="utf-8").read().splitlines():
                if old in ln:
                    d = json.loads(ln)
                    if "transcript_redacted" in d:
                        d["transcript_redacted"] = f"<withheld: D8 incident #3, NC/ND text; prompt sha256 {p.get('sha256')}>"
                    ln = json.dumps(d, ensure_ascii=False).replace(old, new)
                lines.append(ln)
            open(fp, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
        else:
            s = open(fp, encoding="utf-8").read()
            open(fp, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    return {"old": old, "new": new, "sources": sources, "path": os.path.relpath(newpath, ROOT).replace(os.sep, "/"),
            "prompt_sha256": p.get("sha256"), "prompt_bytes": p.get("bytes"), "request_utc": rec.get("request_utc"),
            "purpose": (rec.get("caller") or {}).get("purpose")}


def withdraw_reads(news):
    """A recorded read resting on a redacted call no longer upgrades its row: harness/provenance_class.served_class
    upgrades only on a REPLAYABLE read, and the read's `shown` said "CC full text" of a copy that was not CC BY / CC0.
    The served number is untouched. Idempotent."""
    p = os.path.join(ROOT, "registry", "provenance_recorded_reads.json")
    d = json.load(open(p, encoding="utf-8"))
    n = 0
    for r in (d.get("reads") or {}).values():
        if r.get("record_id") in news and r.get("state") != "WITHDRAWN_D8_3":
            r.update(state="WITHDRAWN_D8_3",
                     shown=str(r.get("shown") or "").replace("CC full text", "full text NOT CC BY / CC0") + " -- D8 incident #3",
                     withdrawn={"why": "the read's prompt carried text from a copy not CC BY / CC0; its bytes are withheld, "
                                       "so the read cannot replay and no longer upgrades the row", "decision": DECISION})
            n += 1
    open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    return n


def main():
    cls = incident_class()
    done = [r for r in (redact(o, v) for o, v in cls.items()) if r]
    led = json.load(open(LEDGER, encoding="utf-8")) if os.path.exists(LEDGER) else {"incidents": []}
    prev = next((i for i in led["incidents"] if i.get("id") == "D8-3"), None)
    if done:
        entry = dict(prev or {}, **{
            "id": "D8-3", "found": "2026-10-12 (captain audit after the robgrade lane's D8 incident #2)",
            "what": f"{len(done)} committed model-call records sent text from copies not CC BY / CC0 to a model; the 13 "
                    "Oct summary said 13 (a fingerprint-audit reach figure); the shared guard's own list is the class",
            "cause": "jats_licence / _is_open / g1_trial_acquire counted any creativecommons.org licence (or any 'cc*' "
                     "string) as open; fixed in PR #94 (one restriction pattern; only CC BY / CC0 opens a prompt)",
            "decision": DECISION, "remedy": "redacted going forward (prompt bytes withheld, hashes kept); git history "
                                            "not rewritten", "records": sorted(done, key=lambda r: r["old"])})
        led["incidents"] = [i for i in led["incidents"] if i.get("id") != "D8-3"] + [entry]
        open(LEDGER, "w", encoding="utf-8", newline="\n").write(json.dumps(led, indent=1, ensure_ascii=False) + "\n")
        # the held index is generated from the store (harness/review_tabs reads it; tests keep it equal to the store)
        subprocess.run([sys.executable, "scripts/provenance_census.py", "--write-held-index"], cwd=ROOT, check=True)
    entry = next((i for i in led["incidents"] if i.get("id") == "D8-3"), {"records": []})
    w = withdraw_reads({r["new"] for r in entry["records"]})
    print(f"redacted {len(done)} of {len(cls)} still carrying such text; ledger D8-3 names {len(entry['records'])}; "
          f"reads withdrawn now {w}")
    for r in done:
        print(" ", r["old"], "->", r["new"], "; ".join(f"{x['source']} [{x['guard_licence']}|{x['restriction_named']}]" for x in r["sources"]))


if __name__ == "__main__":
    main()
