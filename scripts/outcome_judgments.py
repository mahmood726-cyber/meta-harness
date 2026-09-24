"""Produce the OUTCOME-IDENTITY judgments cache (the sanctioned model-as-source use).

For a topic, this enumerates the candidate ClinicalTrials.gov outcome-measure TITLES that the
ctgov extractor would consider (title substring-matches the review's outcome keywords), and for each
records a MODEL judgment of whether that measure IS the review's declared outcome -- same population,
same timepoint, same definition. The judgment is a SOURCE: it is cached to
cache/<slug>/outcome_judgments.json (committed, so a fresh clone reproduces without a model call) and
rendered model-derived on the page. It NEVER supplies the effect number -- the counts still come from
the structured arm table. The gate lives in harness/ctgov_results.py::extract_ctgov(judgments=...):
an OM is pooled only if its title carries an is_match=True judgment here. This closes the azithromycin
class (a broadened keyword matched an ED-visit OM / a subgroup HR that is not the review's outcome).

Usage:
  python scripts/outcome_judgments.py <slug> --candidates      # list candidate OM titles (no model)
  python scripts/outcome_judgments.py <slug> --prompts         # emit the per-candidate model prompts
  python scripts/outcome_judgments.py <slug> --codex --model M [--effort E]  # one RECORDED call per candidate
        (reproducible_ai.model_call_live -> registry/model_calls/); a failed/invalid answer is listed under
        not_judged, never dropped; no --model = refused (MODEL_PIN_MISSING)
  python scripts/outcome_judgments.py <slug> --write judg.json --author NAME  # HAND judgments, named author

The 5 checkable model-derived fields per judgment: candidate_population, candidate_timepoint,
candidate_definition, is_match, rationale (declared_outcome is echoed for the reader). A judgment
missing any field is REJECTED -- the cache is never written half-formed.
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_FIELDS = ("candidate_population", "candidate_timepoint", "candidate_definition",
                   "is_match", "rationale")


def _load(slug):
    config = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    records = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    return config, records


def _primary_spec(config):
    # Matches harness.pipeline._outcome_specs: the review's primary outcome lives under
    # config["primary_outcome"].
    return dict(config.get("primary_outcome") or {}, primary=True)


def collect_candidates(slug):
    """Unique OM titles that substring-match the primary outcome's keywords, with the NCTs they
    appear in and their measure type. Mirrors extract_ctgov's title_matches so the gate and the
    producer consider exactly the same set."""
    config, records = _load(slug)
    spec = _primary_spec(config)
    kws = [k.lower() for k in spec.get("keywords", []) if len(k) > 3]
    cgr = records.get("ctgov_results") or {}
    by_title = {}
    for nct, oms in cgr.items():
        for om in (oms or []):
            title = om.get("title") or ""
            if any(k in title.lower() for k in kws):
                e = by_title.setdefault(title, {"title": title, "type": om.get("type"),
                                                "paramType": om.get("paramType"), "ncts": []})
                if nct not in e["ncts"]:
                    e["ncts"].append(nct)
    return spec, sorted(by_title.values(), key=lambda c: c["title"])


def build_prompt(spec, cand):
    declared = (f"name: {spec.get('name')}\npopulation: {spec.get('population')}\n"
                f"timepoint: {spec.get('timepoint')}\nestimand/definition: {spec.get('estimand')}")
    return (
        "You are an outcome-identity adjudicator for a meta-analysis. Decide whether a "
        "ClinicalTrials.gov outcome measure IS the review's declared outcome -- i.e. the SAME "
        "population, the SAME timepoint, and the SAME event definition. Judge identity only; do "
        "NOT estimate or infer any effect size or number.\n\n"
        f"REVIEW'S DECLARED OUTCOME:\n{declared}\n\n"
        f"CANDIDATE OUTCOME MEASURE (from CT.gov):\n title: {cand['title']}\n type: {cand.get('type')}\n"
        f" paramType: {cand.get('paramType')}\n\n"
        "Reply with ONLY a JSON object, no prose, with exactly these keys:\n"
        '{"candidate_population": "<the measure\'s population, from its title>", '
        '"candidate_timepoint": "<its timepoint, or \'unspecified\'>", '
        '"candidate_definition": "<its event definition>", '
        '"is_match": true|false, '
        '"rationale": "<one sentence: why it is or is not the declared outcome>"}\n'
        "Set is_match=false if the population is a subgroup, the timepoint differs, or the event "
        "definition is a different endpoint (e.g. a component, a broader/narrower composite, an "
        "ED-visit count, a device-therapy endpoint). When unsure, is_match=false."
    )


def validate(j):
    if not isinstance(j, dict):
        return "not a JSON object"
    for f in REQUIRED_FIELDS:
        if f not in j:
            return f"missing field '{f}'"
    if not isinstance(j.get("is_match"), bool):
        return "is_match must be a bool"
    return None


OUTCOME_SCHEMA = {"type": "object", "additionalProperties": False, "required": list(REQUIRED_FIELDS),
                  "properties": {"candidate_population": {"type": "string"}, "candidate_timepoint": {"type": "string"},
                                 "candidate_definition": {"type": "string"}, "is_match": {"type": "boolean"},
                                 "rationale": {"type": "string"}}}
RUNNER = None   # tests inject a fake client runner here; None = the real codex client


def _file_digest(rel):
    import hashlib
    return {"ref": rel, "sha256": hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest(),
            "what": "raw bytes of the committed file the prompt was built from"}


def ask_recorded(slug, cand, prompt, model, effort):
    """ONE recorded model call per candidate, through the contract's single caller (reproducible_ai.model_call_live):
    exact prompt bytes, pinned model, response bytes and digests stored under registry/model_calls/. Returns
    (record, judgment-or-None, why-not)."""
    from reproducible_ai import model_call_live, model_source
    rec = model_call_live.call(
        prompt.encode("utf-8"), schema=OUTCOME_SCHEMA, model=model, effort=effort,
        caller={"file": "scripts/outcome_judgments.py", "line": "ask_recorded",
                "purpose": f"outcome identity, {slug}: {cand['title'][:100]}"},
        input_digests=[_file_digest(f"topics/{slug}.json"), _file_digest(f"cache/{slug}/records.json")],
        runner=RUNNER)
    model_source.write_record(rec, os.path.join(ROOT, model_source.RECORD_DIR))
    if rec["state"] != "RAN_OK":
        return rec, None, f"RAN_ERROR: {rec.get('error', '')[:200]}"
    try:
        j = model_source.extract_claim("outcome", model_source.replay(rec))
    except ValueError as exc:
        return rec, None, f"RESPONSE_NOT_A_CLAIM: {exc}"
    err = validate(j)
    if err:
        return rec, None, f"INVALID: {err}"
    return rec, j, None


def write_cache(slug, spec, judgments, model, not_judged=None, provenance=None):
    """judgments: {title: judgment}. A recorded judgment carries record_id (and model); a hand judgment carries
    author. not_judged lists every candidate the model was asked about and did not answer validly -- the denominator
    is never shrunk by a failure. The file's own provenance key is `provenance`, never a bare 'model' string."""
    for title, j in judgments.items():
        err = validate(j)
        if err:
            print(f"REFUSE to write: judgment for '{title[:60]}' invalid: {err}", file=sys.stderr)
            return 2
        j.setdefault("declared_outcome", spec.get("name"))
    out = {"slug": slug, "declared_outcome": spec.get("name"),
           "provenance": provenance or {"kind": "UNSTATED", "model_named": model},
           "produced_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "judgments": judgments, "not_judged": not_judged or []}
    p = os.path.join(ROOT, "cache", slug, "outcome_judgments.json")
    with open(p, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    n_match = sum(1 for j in judgments.values() if j.get("is_match"))
    print(f"wrote {p}: {len(judgments)} judgments, {n_match} is_match=True")
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    slug = argv[0]
    spec, cands = collect_candidates(slug)
    if "--candidates" in argv:
        print(f"{len(cands)} candidate OM titles for '{spec.get('name')}':")
        for c in cands:
            print(f"  [{c.get('type')}] {c['title']}  (NCTs {c['ncts']})")
        return 0
    if "--prompts" in argv:
        for c in cands:
            print("=" * 80)
            print(build_prompt(spec, c))
        return 0
    if "--write" in argv:
        # HAND judgments: a named person authored them. They are not model output and must not be labelled as such.
        if "--author" not in argv or not argv[argv.index("--author") + 1].strip():
            print("REFUSE: --write needs --author NAME (who authored these judgments); a hand judgment with no author "
                  "is an assertion with no source", file=sys.stderr)
            return 2
        author = argv[argv.index("--author") + 1].strip()
        src = argv[argv.index("--write") + 1]
        judgments = json.load(open(src, encoding="utf-8"))
        judgments = judgments.get("judgments", judgments)
        for j in judgments.values():
            if isinstance(j, dict):
                j["author"] = author
        return write_cache(slug, spec, judgments, model=None,
                           provenance={"kind": "HAND", "author": author})
    if "--codex" in argv:
        # A model call is a SOURCE: pinned model, recorded prompt/response, replayable (reproducible_ai.model_source).
        if "--model" not in argv:
            print("REFUSE: --codex needs --model <id> (MODEL_PIN_MISSING: an unpinned model is an unpinned "
                  "dependency)", file=sys.stderr)
            return 2
        model = argv[argv.index("--model") + 1]
        effort = argv[argv.index("--effort") + 1] if "--effort" in argv else "medium"
        judgments, not_judged = {}, []
        for c in cands:
            rec, j, why = ask_recorded(slug, c, build_prompt(spec, c), model, effort)
            if j is None:
                not_judged.append({"title": c["title"], "record_id": rec["record_id"], "state": why.split(":")[0],
                                   "why": why})
                print(f"  NOT JUDGED '{c['title'][:60]}': {why[:120]}", file=sys.stderr)
                continue
            j["record_id"], j["model"] = rec["record_id"], rec["model"]["id_reported"]
            judgments[c["title"]] = j
            print(f"  {c['title'][:60]} -> is_match={j.get('is_match')} ({rec['record_id']})")
        print(f"{len(judgments)} of {len(cands)} candidates judged; {len(not_judged)} not judged (listed in the cache)")
        return write_cache(slug, spec, judgments, model=model, not_judged=not_judged,
                           provenance={"kind": "RECORDED_MODEL_CALLS", "model_requested": model, "effort": effort,
                                       "record_dir": "registry/model_calls",
                                       "note": "each judgment names its record_id; replay with "
                                               "reproducible_ai.model_source.replay"})
    print("specify one of --candidates | --prompts | --codex | --write <file>")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
