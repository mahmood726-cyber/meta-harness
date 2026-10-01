"""Reproducible AI for the refusal auditor (V1.0.1): propose the ROLE of each held number the regex could not decide.

One RECORDED model call (reproducible_ai.model_call_live: read-only, ephemeral, lane-logged) over outputs/refusal_audit/
undecided_spans.json; the record is stored (model_source.write_record, never overwritten); the proposals file
registry/model_proposals/evidence_role.json is DERIVED from that record and can be rebuilt from it alone with --replay (no model
call). A proposal is only a proposal: harness.evidence_identity uses it only if its verbatim quote passes the deterministic check.
  python scripts/propose_evidence_roles.py            # live: one call, record stored, proposals written
  python scripts/propose_evidence_roles.py --replay   # rebuild proposals from the stored record; byte-compare"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import evidence_identity as ei  # noqa: E402
from reproducible_ai import model_call_live, model_source  # noqa: E402

SPANS = ROOT / "outputs" / "refusal_audit" / "undecided_spans.json"
OUT = ROOT / "registry" / "model_proposals" / "evidence_role.json"
RECORD_DIR = ROOT / model_source.RECORD_DIR if hasattr(model_source, "RECORD_DIR") else ROOT / "registry" / "model_calls"
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["items"],
          "properties": {"items": {"type": "array", "items": {
              "type": "object", "additionalProperties": False, "required": ["key", "role", "quote"],
              "properties": {"key": {"type": "string"}, "role": {"type": "string", "enum": list(ei.ROLES)},
                             "quote": {"type": "string"}}}}}}


def _prompt(spans: dict) -> bytes:
    lines = ["Each item is a sentence from a clinical-trial report that contains numbers. For each, decide what the numbers ARE:",
             "  OUTCOME_COUNT   - counts of patients who had the outcome/event (e.g. died, developed diarrhoea) in the arms",
             "  EXPOSURE_COUNT  - counts of patients who received/crossed over to/were exposed to a treatment (NOT an outcome)",
             "  DENOMINATOR     - numbers randomised/assigned/analysed",
             "  BASELINE        - baseline characteristics before treatment",
             "  EFFECT_ESTIMATE - a ratio (OR/HR/RR) with its confidence interval",
             "  UNDECIDED       - none of these, or the sentence is not a result (e.g. a reference list, a table of demographics)",
             "Return for every item its key, the role, and `quote`: a VERBATIM substring of the sentence (copied exactly) containing",
             "the numbers and the words that show the role. If UNDECIDED, quote may be empty. Do not guess.", ""]
    for key, meta in spans.items():
        lines.append(f"[{key}] {meta['sentence']}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def _proposals(record: dict, response: bytes, spans: dict) -> dict:
    items = json.loads(response.decode("utf-8"))["items"]
    props = {}
    for it in items:
        if it["key"] in spans:
            props[it["key"]] = {"role": it["role"], "quote": it["quote"], "record_id": record["record_id"],
                                "passes_deterministic_check": ei.proposal_supported(it["role"], it["quote"], spans[it["key"]]["sentence"])}
    return {"schema": "evidence_role proposals v1", "record_id": record["record_id"],
            "response_sha256": (record.get("response") or {}).get("sha256"),
            "note": "PROPOSALS from one recorded model call; harness.evidence_identity uses one only if its quote passes the check",
            "proposals": dict(sorted(props.items()))}


def main(argv: list[str]) -> int:
    raw = json.loads(SPANS.read_text(encoding="utf-8"))["spans"]
    spans = {ei.span_key(s): {"sentence": s, **m} for s, m in raw.items()}
    if "--replay" in argv:
        prev = json.loads(OUT.read_text(encoding="utf-8"))
        rec = model_source.load_record(Path(RECORD_DIR) / f"{prev['record_id']}.json")
        rebuilt = _proposals(rec, model_source.replay(rec), spans)
        same = json.dumps(rebuilt, sort_keys=True) == json.dumps(prev, sort_keys=True)
        print(f"replay of {rec['record_id']}: proposals {'IDENTICAL' if same else 'DIFFER'} ({len(rebuilt['proposals'])} items)")
        return 0 if same else 1
    rec = model_call_live.call(_prompt(spans), schema=SCHEMA, model="gpt-6-astra", effort="high",
                               caller={"file": "scripts/propose_evidence_roles.py", "lane": "rai", "line": "main",
                                       "purpose": f"evidence-role proposals for {len(spans)} undecided spans (refusal auditor, V1.0.1)"},
                               input_digests=[{"ref": "outputs/refusal_audit/undecided_spans.json",
                                               "sha256": model_source.sha256_bytes(SPANS.read_bytes())}],
                               runner=None)
    path = model_source.write_record(rec, RECORD_DIR)
    if rec["state"] != "RAN_OK":
        print(f"model call {rec['record_id']} state {rec['state']}: {rec.get('error')}; record kept at {path}; NO proposals written")
        return 1
    out = _proposals(rec, model_source.replay(rec), spans)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    ok = sum(p["passes_deterministic_check"] for p in out["proposals"].values())
    print(f"record {rec['record_id']} stored at {path}; {len(out['proposals'])} proposals, {ok} pass the deterministic check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
