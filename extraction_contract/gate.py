"""The P3 claim gate: may this bundle claim to MATCH a published meta-analysis?

bundle = {
  "contract": "p3/1.x.y",
  "topic": str,
  "claim": {"kind": "matches_published_meta", "published": str},
  "trials": [{
      "trial_id": str, "measure": "binary"|"continuous"|"ratio",
      "values": [item, ...],          # the SERVED values (what is pooled), each with its passage
      "readings": [reading, reading], # the two independent readings (dual.py)
      "adjudications": [adjudication, ...]
  }, ...]
}
Verdict ALLOW_MATCH_CLAIM only if, for every trial:
  1. every value required by its measure is served, exactly once;
  2. every served value is well-typed, carries a verified passage, and is literally in that passage;
  3. the served values are coherent (events <= total, CI brackets the point, ratios > 0, ...);
  4. every served OUTCOME value is AGREED by independently recorded dual readings and equals
     the resolved value. Differing readings and any proposed human/model adjudication are
     UNRESOLVED until an authenticated, blinded external-review verifier exists; a quoted
     source passage or self-reported reviewer identity alone never promotes a claim.
and the bundle names this contract's major version and has at least one trial. Anything unreadable is REFUSE.
"""
from __future__ import annotations

from . import CONTRACT_MAJOR, CONTRACT_VERSION
from . import fields as F
from .dual import item_problems, resolve, same_value

ALLOW, REFUSE = "ALLOW_MATCH_CLAIM", "REFUSE"



def _call_record_problems(trial, docs_root, call_records) -> list[str]:
    """Replay and bind *both* recorded calls to the exact trial, document, prompt and readings.

    A self-consistent stored record is not remote-provider attestation or human validation.
    Unrecorded metadata is useful for diagnosis but can never authorize ALLOW_MATCH_CLAIM.
    """
    if not isinstance(call_records, dict) or not call_records:
        return ["CALL_RECORDS_NOT_VERIFIED: two replayable call records are required for an authoritative match claim"]
    from pathlib import Path
    from hashlib import sha256
    import base64
    from reproducible_ai import model_source
    from . import readers as model_readers
    from .passage import _resolve

    readings = trial.get("readings")
    if not isinstance(readings, list) or len(readings) != 2:
        return ["CALL_RECORDS_NOT_VERIFIED: exactly two readings must bind to their call records"]
    problems = []
    root = Path(docs_root).resolve()
    for reading in readings:
        if not isinstance(reading, dict):
            problems.append("CALL_RECORDS_NOT_VERIFIED: malformed reading")
            continue
        declared = reading.get("reader") or {}
        if not isinstance(declared, dict):
            problems.append("CALL_RECORDS_NOT_VERIFIED: malformed reader identity")
            continue
        record_id = declared.get("record_id")
        record = call_records.get(record_id) if isinstance(record_id, str) else None
        if not isinstance(record, dict):
            problems.append("CALL_RECORDS_NOT_VERIFIED: missing referenced model call record")
            continue
        try:
            model_source.replay(record)  # verifies exact stored prompt/response bytes and canonical record ID
        except (model_source.ReplayRefused, ValueError, TypeError, KeyError) as exc:
            problems.append(f"CALL_RECORDS_NOT_VERIFIED: call record replay refused: {exc}")
            continue
        model = record.get("model") or {}
        if (not isinstance(model, dict) or model.get("provider") != declared.get("family")
                or model.get("id_reported") != declared.get("model_reported")
                or model.get("id_requested") != model.get("id_reported")):
            problems.append("CALL_RECORDS_NOT_VERIFIED: call-record provider/model pin does not match reading")
        items = reading.get("items")
        if not isinstance(items, list) or not items:
            problems.append("CALL_RECORDS_NOT_VERIFIED: no recorded reading items to bind")
            continue
        refs = set()
        for item in items:
            passage = item.get("passage") if isinstance(item, dict) else None
            if isinstance(passage, dict):
                ref, digest = passage.get("document_ref"), passage.get("document_sha256")
                if isinstance(ref, str) and isinstance(digest, str):
                    refs.add((ref, digest))
        if len(refs) != 1:
            problems.append("CALL_RECORDS_NOT_VERIFIED: reading has no single pinned source document")
            continue
        ref, digest = next(iter(refs))
        path = _resolve(docs_root, ref)
        if path is None:
            problems.append("CALL_RECORDS_NOT_VERIFIED: source path is not inside the documents root")
            continue
        source_path = Path(path).resolve()
        if not source_path.is_relative_to(root):
            problems.append("CALL_RECORDS_NOT_VERIFIED: source resolves outside the documents root")
            continue
        try:
            raw = source_path.read_bytes()
            source_text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            problems.append(f"CALL_RECORDS_NOT_VERIFIED: unreadable source document: {exc}")
            continue
        if sha256(raw).hexdigest() != digest:
            problems.append("CALL_RECORDS_NOT_VERIFIED: source bytes differ from pinned document digest")
            continue
        inputs = record.get("input_digests")
        if (not isinstance(inputs, list) or not any(
                isinstance(d, dict) and d.get("ref") == ref and d.get("sha256") == digest
                for d in inputs)):
            problems.append("CALL_RECORDS_NOT_VERIFIED: source document is not bound in call input digests")
        try:
            expected_prompt = model_readers.build_prompt(
                source_text, str(trial.get("trial_id") or ""), trial["measure"])
            recorded_prompt = base64.b64decode(record["prompt"]["b64"], validate=True)
        except (KeyError, TypeError, ValueError) as exc:
            problems.append(f"CALL_RECORDS_NOT_VERIFIED: cannot reproduce trial-specific prompt: {exc}")
            continue
        if recorded_prompt != expected_prompt:
            problems.append("CALL_RECORDS_NOT_VERIFIED: recorded prompt differs from source/trial/measure prompt")
        reconstructed = model_readers.reading_from_record(
            record, declared.get("family"), source_text, ref, digest)
        if (reconstructed["reader"].get("record_id") != record_id
                or reconstructed.get("items") != items):
            problems.append("CALL_RECORDS_NOT_VERIFIED: declared reading items differ from recorded response")
    return problems

def _label(k):
    return k[0] + (f"[{k[1]}]" if k[1] else "")


def check_trial(trial, docs_root, call_records=None, cache=None) -> dict:
    cache = cache if cache is not None else {}
    tid = str(trial.get("trial_id") or "?")
    measure = trial.get("measure")
    probs = []
    if measure not in F.REQUIRED_BY_MEASURE:
        return {"trial_id": tid, "ok": False, "problems": [f"measure {measure!r} not in {sorted(F.REQUIRED_BY_MEASURE)}"]}
    call_problems = _call_record_problems(trial, docs_root, call_records)
    probs.extend(call_problems)
    served = {}
    for it in trial.get("values") or []:
        k = F.key(it)
        if k in served:
            probs.append(f"{_label(k)} served twice")
            continue
        served[k] = it
    for k in F.REQUIRED_BY_MEASURE[measure]:
        if k not in served:
            probs.append(f"{_label(k)} required for a {measure} trial but not served")
    resolved_vals = {}
    for k, it in served.items():
        ip = item_problems(it, docs_root, cache)
        if ip:
            probs += [f"{_label(k)}: {p}" for p in ip]
        else:
            resolved_vals[k] = it["value"]
    probs += F.coherence_problems(resolved_vals)
    dual = resolve(trial.get("readings"), trial.get("adjudications"), docs_root, call_records, cache)
    probs += [f"independence: {p}" for p in dual["independence"]]
    # Never silently discard extra or misspelled review records. A human/model
    # challenge that does not map to a dual-read outcome requires manual review.
    unmatched = dual.get("unmatched_adjudications", [])
    if unmatched:
        probs.append(f"{len(unmatched)} unmatched adjudication record(s) have no dual-read OUTCOME field; "
                     "UNRESOLVED, manual review required")
    status = {}
    for k, it in served.items():
        spec = F.FIELDS.get(k[0])
        if spec is None or spec.role != "OUTCOME":
            continue
        d = dual["fields"].get(k)
        if d is None:
            probs.append(f"{_label(k)}: OUTCOME value served but neither reader extracted it (no dual reading)")
            status[_label(k)] = "NOT_READ"
            continue
        status[_label(k)] = d["status"]
        if d["status"] == "UNRESOLVED":
            probs.append(f"{_label(k)}: UNRESOLVED -- " + "; ".join(d["problems"]))
        elif not same_value(it.get("value"), d["value"]):
            probs.append(f"{_label(k)}: served {it.get('value')!r} but the dual reading resolved {d['value']!r}")
    return {"trial_id": tid, "ok": not probs, "problems": probs,
            "call_record_status": "REPLAY_VERIFIED" if not call_problems else "NOT_VERIFIED",
            "dual_status": status,
            "unmatched_adjudications": unmatched}


def check_bundle(bundle, docs_root, call_records=None) -> dict:
    report = {"contract_version": CONTRACT_VERSION, "verdict": REFUSE, "problems": [], "trials": [],
              "remote_provider_attested": False, "independent_human_validated": False}
    if not isinstance(bundle, dict):
        report["problems"].append("bundle is not a JSON object")
        return report
    c = str(bundle.get("contract") or "")
    if not (c == CONTRACT_MAJOR or c.startswith(CONTRACT_MAJOR + ".")):
        report["problems"].append(f"bundle contract {c!r} is not {CONTRACT_MAJOR}.x (refused, never coerced)")
        return report
    claim = bundle.get("claim") or {}
    if claim.get("kind") != "matches_published_meta" or not str(claim.get("published") or "").strip():
        report["problems"].append("claim must be {kind: matches_published_meta, published: <which meta-analysis>}")
    trials = bundle.get("trials")
    if not isinstance(trials, list) or not trials:
        report["problems"].append("no trials: an empty bundle cannot support a match claim")
        return report
    ids = [str(t.get("trial_id") or "") for t in trials if isinstance(t, dict)]
    if len(ids) != len(trials) or len(set(ids)) != len(ids) or not all(ids):
        report["problems"].append("every trial needs a unique, non-empty trial_id")
    cache = {}
    for t in trials:
        if isinstance(t, dict):
            report["trials"].append(check_trial(t, docs_root, call_records, cache))
    n_ok = sum(1 for t in report["trials"] if t["ok"])
    report["summary"] = {"trials": len(trials), "trials_ok": n_ok}
    if not report["problems"] and n_ok == len(trials):
        report["verdict"] = ALLOW
    return report
