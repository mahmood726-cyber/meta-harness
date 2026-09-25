"""Run ONE lightweight model job through the repository's recorded model-call contract and archive its result.

  python codex_job.py --kind gap --key UA-008 --brief evidence/GAP_BRIEF.md --dest evidence/gaps/UA-008.json
     [--with-adjudication]

Every call goes through reproducible_ai.model_call_live.call -- the repository's ONLY model caller (see
tests/test_model_inventory.py): `codex exec --ignore-user-config -c project_doc_max_bytes=0 --sandbox read-only
--cd <empty dir with LANE_CONTEXT.md>` with the prompt on stdin and a strict output schema. So the client's global
instructions (which read the owner's private files) are NOT loaded, the model sees only the prompt, and the call
produces a model_source record (prompt bytes, response bytes, model reported by the client, digests). This replaced
an earlier version of this script that ran codex itself; main's inventory test refused it, rightly.

The record goes to evidence/model_calls/<kind>/<key>.json; the parsed response to --dest (sha256 checked at the
destination); one metadata line to evidence/CODEX_CALLS.jsonl. Exit 0 only for RAN_OK with an archived result."""
import argparse, base64, hashlib, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FULL_PACKETS = r"C:\mh-lanes\evid-codex\packets_full"
FULL_RECORDS = r"C:\mh-lanes\evid-codex\records_full"
sys.path.insert(0, ROOT)
from reproducible_ai import model_call_live  # noqa: E402

MODEL, EFFORT = "gpt-6-astra", "medium"
NO_PACKET = {"setread"}
S = {"type": "string"}
NS = {"type": ["string", "null"]}


def obj(props):
    return {"type": "object", "additionalProperties": False, "properties": props, "required": list(props)}


SPAN = obj({"ref": S, "span": S})
GAP_FIELD = {"anyOf": [obj({"ref": S, "span": S, "scope": S}), S]}
VERDICT3 = {"type": "string", "enum": ["AGREE", "DISAGREE", "CANNOT_TELL"]}
QUOTES = {"type": "array", "items": obj({"ref": S, "span": S})}
SCHEMAS = {
    "setread": obj({"key": S, "reading": {"type": "string", "enum": ["ITT_STATED", "OTHER_SET_STATED", "NOT_STATED"]}, "why": S}),
    "second": obj({"key": S,
                   "number": obj({"verdict": VERDICT3, "why": S, "quotes": QUOTES}),
                   "entry": obj({"verdict": VERDICT3, "your_ruling": {"type": "string", "enum": ["ESTABLISHED", "PARTLY", "NOT_ESTABLISHED"]},
                                 "why": S, "quotes": QUOTES}),
                   "missed": S}),
    "citation":obj({"key": S, "verdict": {"type": "string", "enum": ["RIGHT_ENDPOINT", "WRONG_ENDPOINT", "OUTCOME_NAME_ONLY",
                                                                       "NOTE_NOT_A_SPAN", "CANNOT_TELL"]},
                     "why": S, "quote": NS}),
    "gap":obj({"key": S, "analysis_set": GAP_FIELD, "follow_up": GAP_FIELD, "entry_age": GAP_FIELD,
                "entry_other": GAP_FIELD, "notes": S}),
    "retest": obj({
        "key": S, "verdict": {"type": "string", "enum": ["BOUND", "SET_ASIDE"]}, "set_aside_reason": NS,
        "fields": obj({f: {"anyOf": [SPAN, {"type": "null"}]} for f in
                       ("population", "endpoint", "estimate", "ci", "analysis_set", "treatment_strategy", "follow_up")}),
        "absent_reason": S,
        "bound_values": obj({k: NS for k in ("scale", "estimate", "ci_low", "ci_high", "ci_level", "events_t", "n_t",
                                             "events_c", "n_c", "mean_t", "sd_t", "mean_c", "sd_c")}),
        "served_mismatch": NS,
        "candidate_rejections": {"type": "array", "items": obj({"ref": S, "span": S, "why": S})},
        "entry_population_matches_question": obj({"value": S, "why": S, "ref": NS, "span": NS}),
        "notes": S}),
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=sorted(SCHEMAS)); ap.add_argument("--key", required=True)
    ap.add_argument("--brief", required=True); ap.add_argument("--dest", required=True)
    ap.add_argument("--with-adjudication", action="store_true")
    ap.add_argument("--extra", help="a JSON file appended to the prompt (digest recorded)")
    a = ap.parse_args()
    brief = open(os.path.join(ROOT, a.brief), "rb").read()
    full = os.path.join(FULL_PACKETS, f"{a.key}.json")   # includes local-only full texts; never committed
    packet = open(full if os.path.exists(full) else os.path.join(ROOT, "evidence", "packets", f"{a.key}.json"), "rb").read()
    parts = [b"You are given everything you need in this message; there are no files to read.\n\nBRIEF:\n", brief,
             f"\n\nROW KEY: {a.key}\n".encode()]
    digests = [{"ref": a.brief, "sha256": sha(brief), "what": "task brief"}]
    if a.kind not in NO_PACKET:   # a one-span classification needs no packet (lightweight jobs)
        parts += [b"\nPACKET (the only evidence; spans must be verbatim from sources[i].text):\n", packet]
        digests.append({"ref": f"evidence/packets/{a.key}.json", "sha256": sha(packet), "what": "the row's held sources, rendered"})
    if a.with_adjudication:
        adj = open(os.path.join(ROOT, "evidence", "adjudication", f"{a.key}.json"), "rb").read()
        parts += [b"\n\nTHE LANE'S RULING FOR THIS ROW (adjudication.json):\n", adj]
        digests.append({"ref": f"evidence/adjudication/{a.key}.json", "sha256": sha(adj), "what": "the lane's ruling"})
    if a.extra:
        ex = open(a.extra, "rb").read()
        parts += [b"\n\nITEM TO JUDGE:\n", ex]
        digests.append({"ref": f"{a.kind} input for {a.key} (built from the committed sweep/adjudication files)",
                        "sha256": sha(ex), "what": f"the item the {a.kind} brief asks to judge"})
    prompt = b"".join(parts)
    rec = model_call_live.call(prompt, schema=SCHEMAS[a.kind], model=MODEL, effort=EFFORT,
                               caller={"file": "evidence/scripts/codex_job.py", "line": sys._getframe().f_lineno,
                                       "purpose": f"evidence lane {a.kind} job for row {a.key} (brief {a.brief})",
                                       "lane": "evid/evidence-records", "kind": a.kind, "key": a.key},
                               input_digests=digests, timeout_s=1200)
    # the full record (its prompt may contain local-only full text) stays OUTSIDE the repo; the committed record keeps
    # every digest and the response, with the prompt blob replaced by its sha256 and length
    full_dir = os.path.join(FULL_RECORDS, a.kind); os.makedirs(full_dir, exist_ok=True)
    json.dump(rec, open(os.path.join(full_dir, f"{a.key}.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    slim = dict(rec, prompt={"sha256": rec["prompt"]["sha256"], "bytes": rec["prompt"]["bytes"], "b64": None,
                             "note": "prompt bytes withheld (may contain local-only full text); full record kept locally"})
    rp = os.path.join(ROOT, "evidence", "model_calls", a.kind, f"{a.key}.json")
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    json.dump(slim, open(rp, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    line = {"kind": a.kind, "key": a.key, "record": os.path.relpath(rp, ROOT).replace(os.sep, "/"),
            "state": rec.get("state"), "error": rec.get("error"), "dest": a.dest}
    ok = False
    if rec.get("state") == "RAN_OK":
        text = base64.b64decode(rec["response"]["b64"]).decode("utf-8")
        try:
            obj_ = json.loads(text)
            dest = os.path.join(ROOT, a.dest); os.makedirs(os.path.dirname(dest), exist_ok=True)
            data = json.dumps(obj_, indent=1, ensure_ascii=False).encode("utf-8")
            open(dest, "wb").write(data)
            line["result_sha256"] = sha(data)
            ok = sha(open(dest, "rb").read()) == line["result_sha256"]
        except (TypeError, ValueError) as e:
            line["parse_error"] = str(e)[:200]
    with open(os.path.join(ROOT, "evidence", "CODEX_CALLS.jsonl"), "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(line) + "\n")
    print(("OK" if ok else "FAILED"), a.key, rec.get("state"), (rec.get("error") or "")[:160])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
