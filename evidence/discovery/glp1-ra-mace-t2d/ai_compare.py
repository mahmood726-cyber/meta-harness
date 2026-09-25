"""Record the AI screening proposals verbatim and list where they disagree with the deterministic screen (STRATEGY.md,
screening step 2). The AI never decides: this only lists disagreements. usage: ai_compare.py <proposals dir> <run dir>
(reads proposals{1,2,3}.json, the batch files beside them, TRIALS.json and AI_SAMPLE.json; writes AI_PROPOSALS.json)"""
import json, os, sys

READER = {"model": "claude-opus-5-5 (Claude Code subagent, general-purpose)", "role": "AI screener, proposals only",
          "instructions": "three independent subagents, one per shuffled batch; each read only its batch file and "
                          "judged P, I, C, design, primary report and reports-MACE from the record's own text, "
                          "with a verbatim quote for each yes/no"}


def main(pdir, run):
    sample = json.load(open(os.path.join(run, "AI_SAMPLE.json"), encoding="utf-8"))
    wanted = set(sample["included_records"]) | set(sample["excluded_sample"])
    det = {}
    for t in json.load(open(os.path.join(run, "TRIALS.json"), encoding="utf-8"))["trials"]:
        for x in t["records"]:
            det[x["key"]] = {"trial": t["trial"], "decision": (x["screen"] or {}).get("decision"),
                             "rule_id": (x["screen"] or {}).get("rule_id"), "reason": (x["screen"] or {}).get("reason")}
    props, texts = {}, {}
    for i in (1, 2, 3):
        batch = json.load(open(os.path.join(pdir, f"batch{i}.json"), encoding="utf-8"))
        prop = json.load(open(os.path.join(pdir, f"proposals{i}.json"), encoding="utf-8"))
        assert [p["key"] for p in prop] == [b["key"] for b in batch], f"batch {i}: proposals do not match the batch"
        for b, p in zip(batch, prop):
            hay = json.dumps(b, ensure_ascii=False)
            for f, q in (p.get("quotes") or {}).items():
                assert not q or q in hay or json.dumps(q, ensure_ascii=False)[1:-1] in hay, (p["key"], f, q[:80])
            assert p["proposal"] in ("include", "exclude"), (p["key"], p["proposal"])
            props[p["key"]] = dict(p, batch=i)
    unread = sorted(wanted - set(props))
    extra = sorted(set(props) - wanted)
    assert not extra, extra
    dis = []
    for k in sorted(props):
        d = det[k]["decision"]
        if (d == "include") != (props[k]["proposal"] == "include"):
            dis.append({"key": k, "trial": det[k]["trial"], "deterministic": d, "rule_id": det[k]["rule_id"],
                        "deterministic_reason": det[k]["reason"], "ai_proposal": props[k]["proposal"],
                        "ai_reason": props[k]["reason"]})
    counts = {}
    for k, p in props.items():
        c = (det[k]["decision"], p["proposal"])
        counts[f"det_{c[0]}__ai_{c[1]}"] = counts.get(f"det_{c[0]}__ai_{c[1]}", 0) + 1
    out = {"reader": READER, "n_proposals": len(props), "not_read_no_text": unread, "agreement_counts": counts,
           "disagreements": dis, "proposals": [props[k] for k in sorted(props)]}
    json.dump(out, open(os.path.join(run, "AI_PROPOSALS.json"), "w", encoding="utf-8", newline="\n"), indent=1,
              ensure_ascii=False)
    print(len(props), "proposals;", counts, ";", len(dis), "disagreements; not read:", unread)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
