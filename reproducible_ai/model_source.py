"""Model call as a SOURCE: record, replay, proposal, gate. Nothing here admits anything into a served number.

The standing contract (Mahmood, 2026-09-16; outputs/handover/lanes/REPRODUCIBLE_MODEL_CONTRACT.md): a model may be used
anywhere provided the call is reproducible -- and a model never supplies a number. This module is the smallest thing
that makes one model call reproducible in the only sense available to us: the call's RECORDED output is replayed,
byte for byte, offline, and every downstream use of it is a PROPOSAL that stays inert until three independent
conditions hold.

  record   build_record(...)  one object per call: model id requested AND reported, every parameter we set and the
           ones the client does not let us set (named, not hidden), the EXACT prompt bytes and the EXACT response bytes
           (base64 inside JSON, so no end-of-line normalisation can touch them), each with sha256, timestamps, the
           caller (file:line, purpose) and the digests of every input the prompt was derived from. The record id is
           the sha256 of the canonical record without its id: editing any field changes the id, so a tampered record
           cannot keep its name. A call whose prompt bytes are not recoverable is refused (RecordIncomplete).
  replay   replay(record) returns the STORED response after re-deriving every digest and the id. It never calls a
           model: this module imports nothing that can reach a network or spawn a process (tested by AST). A RAN_ERROR
           record never replays as a response.
  proposal Proposal(...) is status PROPOSED, immutable, and refuses to be consumed: truth-testing, numeric
           conversion, indexing, iteration, formatting and JSON encoding all raise ProposalNotAdmissible. The pinned
           producers never import this module (tested against the certificate closure).
  gate     status_of(entry, record, held_text) is COUNTERSIGNED only when ALL of: (a) the same deterministic verifier
           the harness uses for spans (scripts/build_bundle.py::locate, and for estimand fields the bundle's own
           _ESTIMAND vocabulary) accepts the claim against the held text; (b) the record replays and the claim in the
           queue IS the claim the record's response decodes to; (c) a human countersignature passes
           harness.result_changes.signature_problem -- reused as-is -- over the sha256 of the rendered proposal block.
           A rule/model disagreement is passed as the notice's `conclusion_changed`, so it accepts an individual
           signature only, never a batch. There is no timeout, no default, no "assume accepted": anything else is
           PROPOSED, forever. COUNTERSIGNED is review material; in this landing no producer reads it
           (admits_into_build is False by construction).

What this does NOT make reproducible: the model. Re-asking the same model the same prompt tomorrow may answer
differently; the client adds its own system instructions (recorded by digest where we can read them, named as
not_controllable where we cannot); sampling parameters the client does not expose are listed, not invented. Replay
reproduces THIS call's recorded output and nothing else. If a stored response is lost, the record cannot replay,
the proposal can never be countersigned, and the only honest recovery is a NEW call with a NEW record id -- never a
reconstruction under the old one (write_record refuses to overwrite a stored record whose bytes differ).
"""
from __future__ import annotations

import base64
import binascii
import copy
import hashlib
import html
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "model_call_record/1"
RECORD_STATES = ("RAN_OK", "RAN_ERROR")
STATUSES = ("PROPOSED", "COUNTERSIGNED")
ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = "registry/model_calls"
PROPOSAL_DIR = "registry/model_proposals"


class RecordIncomplete(ValueError):
    """The call cannot be a source: something needed to re-derive or re-read it is missing."""


class ReplayRefused(Exception):
    """The stored record does not reproduce its own digests or id; its response is not returned."""


class ProposalNotAdmissible(Exception):
    """A PROPOSED model output reached a path that consumes values."""


# ------------------------------------------------------------------------------------------------------ digests
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def record_id_of(record: dict) -> str:
    body = {k: v for k, v in record.items() if k != "record_id"}
    return "mc-" + sha256_bytes(canonical(body))[:32]


def _blob(b: bytes) -> dict:
    return {"b64": base64.b64encode(b).decode("ascii"), "sha256": sha256_bytes(b), "bytes": len(b)}


def _unblob(blob: Any, what: str) -> bytes:
    if not isinstance(blob, dict) or not isinstance(blob.get("b64"), str):
        raise ReplayRefused(f"{what}: no stored bytes (the stored {what} is lost -- this record cannot replay)")
    try:
        raw = base64.b64decode(blob["b64"].encode("ascii"), validate=True)
    except (binascii.Error, ValueError, UnicodeEncodeError) as exc:
        raise ReplayRefused(f"{what}: stored bytes are not valid base64 ({exc})") from None
    if sha256_bytes(raw) != blob.get("sha256"):
        raise ReplayRefused(f"{what}: sha256 of the stored bytes {sha256_bytes(raw)[:12]} != recorded "
                            f"{str(blob.get('sha256'))[:12]} -- the stored {what} was altered")
    if len(raw) != blob.get("bytes"):
        raise ReplayRefused(f"{what}: stored length {len(raw)} != recorded {blob.get('bytes')}")
    return raw


# ------------------------------------------------------------------------------------------------------ the record
def build_record(*, prompt_bytes: bytes, response_bytes: bytes, model: dict, params: dict, not_controllable: list,
                 client: dict, request_utc: str, response_utc: str, caller: dict, input_digests: list,
                 state: str = "RAN_OK", error: str | None = None, client_evidence: dict | None = None) -> dict:
    if not isinstance(prompt_bytes, (bytes, bytearray)) or not prompt_bytes:
        raise RecordIncomplete("prompt bytes missing: a call whose prompt is not recoverable is not a source")
    if not isinstance(response_bytes, (bytes, bytearray)):
        raise RecordIncomplete("response must be bytes (empty bytes for RAN_ERROR)")
    if state not in RECORD_STATES:
        raise RecordIncomplete(f"state {state!r} is not one of {RECORD_STATES}")
    if state == "RAN_OK" and not response_bytes:
        raise RecordIncomplete("RAN_OK with an empty response: an empty answer is RAN_ERROR, never RAN_ZERO")
    if state == "RAN_ERROR" and not (error or "").strip():
        raise RecordIncomplete("RAN_ERROR needs the error text")
    if not isinstance(model, dict) or not all(str(model.get(k) or "").strip() for k in ("id_requested", "id_reported", "provider")):
        raise RecordIncomplete("model pin incomplete: id_requested, id_reported and provider are all required "
                               "(MODEL_PIN_MISSING -- an unpinned model is an unpinned dependency)")
    if not isinstance(params, dict):
        raise RecordIncomplete("params must be the dict of every parameter set on the call")
    if not isinstance(not_controllable, list):
        raise RecordIncomplete("not_controllable must list the parameters the client does not expose (may be empty)")
    if not isinstance(client, dict) or not str(client.get("name") or "").strip():
        raise RecordIncomplete("client name missing")
    if not isinstance(caller, dict) or not all(str(caller.get(k) or "").strip() for k in ("file", "line", "purpose")):
        raise RecordIncomplete("caller must name file, line and purpose")
    if not isinstance(input_digests, list) or not input_digests or not all(
            isinstance(d, dict) and str(d.get("ref") or "").strip() and re.fullmatch(r"[0-9a-f]{64}", str(d.get("sha256") or ""))
            for d in input_digests):
        raise RecordIncomplete("input_digests must name every input the prompt was derived from (ref + sha256)")
    for k, v in (("request_utc", request_utc), ("response_utc", response_utc)):
        if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", str(v or "")):
            raise RecordIncomplete(f"{k} must be UTC YYYY-MM-DDTHH:MM:SSZ")
    rec = {"schema": SCHEMA, "state": state, "model": dict(model), "params": dict(params),
           "not_controllable": list(not_controllable), "client": dict(client), "request_utc": request_utc,
           "response_utc": response_utc, "caller": dict(caller), "input_digests": [dict(d) for d in input_digests],
           "prompt": _blob(bytes(prompt_bytes)), "response": _blob(bytes(response_bytes))}
    if error:
        rec["error"] = error
    if client_evidence:
        rec["client_evidence"] = client_evidence
    rec["record_id"] = record_id_of(rec)
    return rec


def record_problems(record: Any) -> list[str]:
    if not isinstance(record, dict):
        return ["not a record"]
    out = []
    if record.get("schema") != SCHEMA:
        out.append(f"schema {record.get('schema')!r} != {SCHEMA}")
    for what in ("prompt", "response"):
        try:
            _unblob(record.get(what), what)
        except ReplayRefused as exc:
            out.append(str(exc))
    if record.get("record_id") != record_id_of(record):
        out.append(f"record_id {record.get('record_id')} != {record_id_of(record)} re-derived from the record's "
                   "contents -- a field was changed after the call")
    return out


def replay(record: dict) -> bytes:
    """The STORED response, after every digest and the id re-derive. Never calls a model."""
    problems = record_problems(record)
    if problems:
        raise ReplayRefused("; ".join(problems))
    if record.get("state") != "RAN_OK":
        raise ReplayRefused(f"state {record.get('state')}: {record.get('error')!r} -- an error is recorded, never replayed as a response")
    return _unblob(record["response"], "response")


def write_record(record: dict, directory: str | Path) -> Path:
    problems = record_problems(record)
    if problems:
        raise ReplayRefused("refusing to store a record that does not reproduce: " + "; ".join(problems))
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{record['record_id']}.json"
    data = json.dumps(record, indent=1, sort_keys=True, ensure_ascii=True) + "\n"
    if path.exists():
        on_disk = path.read_bytes()
        if on_disk != data.encode("ascii"):
            raise ReplayRefused(f"{path.name} exists with different bytes: a stored record is never overwritten "
                                "(a lost or altered response is recovered by a NEW call under a NEW id)")
        return path
    path.write_bytes(data.encode("ascii"))
    return path


def load_record(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="ascii"))


# ------------------------------------------------------------------------------------------------------ proposal
def _refuse(self, *a, **k):
    raise ProposalNotAdmissible(f"a PROPOSED model output ({object.__getattribute__(self, '_item_id')}) was consumed "
                                "as a value; it is review material until countersigned, and even then no producer reads it")


class Proposal:
    """A model's claim about one item. Inert: every value-consuming protocol raises. Immutable."""
    __slots__ = ("_task", "_item_id", "_record_id", "_claim")

    def __init__(self, task: str, item_id: str, record_id: str, claim: dict):
        object.__setattr__(self, "_task", str(task))
        object.__setattr__(self, "_item_id", str(item_id))
        object.__setattr__(self, "_record_id", str(record_id))
        object.__setattr__(self, "_claim", copy.deepcopy(claim))

    @classmethod
    def from_entry(cls, entry: dict) -> "Proposal":
        return cls(entry["task"], entry["item_id"], entry["record_id"], entry["claim"])

    status = property(lambda self: "PROPOSED")
    task = property(lambda self: object.__getattribute__(self, "_task"))
    item_id = property(lambda self: object.__getattribute__(self, "_item_id"))
    record_id = property(lambda self: object.__getattribute__(self, "_record_id"))
    claim = property(lambda self: copy.deepcopy(object.__getattribute__(self, "_claim")))

    def __setattr__(self, name, value):
        raise AttributeError(f"a Proposal is immutable ({name}); its status is PROPOSED and only status_of() over a "
                             "queue entry, a replayable record and a countersignature can say otherwise")

    __delattr__ = __setattr__

    def __getattr__(self, name):
        """Any attribute a consumer reaches for (rec.get, s.yi_vi, row.decision, ...) is a consumption: refuse it."""
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        raise ProposalNotAdmissible(f"a PROPOSED model output ({object.__getattribute__(self, '_item_id')}) was read "
                                    f"as .{name} by a consumer; it is review material, not an input")

    def __repr__(self):
        return f"<Proposal PROPOSED {self._task} {self._item_id} from {self._record_id}>"

    __bool__ = __float__ = __int__ = __index__ = __complex__ = __round__ = __iter__ = __len__ = _refuse
    __getitem__ = __contains__ = __format__ = __str__ = __hash__ = __reduce__ = __reduce_ex__ = _refuse
    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __truediv__ = __rtruediv__ = _refuse
    __lt__ = __le__ = __gt__ = __ge__ = __eq__ = __ne__ = _refuse


def admit(proposal: Any, *, entry: dict | None, record: dict | None, held_text: str | None) -> dict:
    """The only door. Raises unless all three conditions hold over the QUEUED entry (the object the reviewer's
    signature names) and the Proposal is that entry; even then returns inert review material."""
    if not isinstance(proposal, Proposal):
        raise ProposalNotAdmissible("admit() takes a Proposal")
    if entry is None or record is None or held_text is None:
        raise ProposalNotAdmissible(f"{proposal!r}: the queued entry, its record and the held text are all required")
    same = (entry.get("task"), entry.get("item_id"), entry.get("record_id"), canonical(entry.get("claim"))) == \
           (proposal.task, proposal.item_id, proposal.record_id, canonical(proposal.claim))
    if not same:
        raise ProposalNotAdmissible(f"{proposal!r} is not the queued entry it is presented with")
    problems = gate_problems(entry, record, held_text)
    if problems:
        raise ProposalNotAdmissible(f"{proposal!r} stays PROPOSED: " + "; ".join(problems))
    return {"status": "COUNTERSIGNED", "item_id": proposal.item_id, "record_id": proposal.record_id,
            "claim": proposal.claim, "admits_into_build": False,
            "note": "review material: no producer in this landing reads a countersigned proposal"}


# ------------------------------------------------------------------------------------------------------ verifiers
_BUNDLE = None


def _bundle():
    """scripts/build_bundle.py loaded once, for its span ladder (locate) and its estimand vocabulary (_ESTIMAND):
    the SAME verifier the served bundle's rows pass, not a second one."""
    global _BUNDLE
    if _BUNDLE is None:
        spec = importlib.util.spec_from_file_location("_mh_build_bundle", ROOT / "scripts" / "build_bundle.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _BUNDLE = mod
    return _BUNDLE


def _locate(quote: str, text: str) -> dict:
    return _bundle().locate(quote, text)


def estimand_vocabulary(field: str) -> list[str]:
    return sorted({v for _, v in _bundle()._ESTIMAND.get(field, [])})


def rule_values_on(field: str, span: str) -> list[str]:
    return sorted({v for rx, v in _bundle()._ESTIMAND.get(field, []) if re.search(rx, span, re.I)})


def verify_estimand(claim: Any, held_text: str) -> dict:
    """claim = {field, value, quote}. PASS needs: field known; value in the rule's own vocabulary or NOT_STATED; a
    stated value's quote located by the bundle's ladder in the held text; NOT_STATED carries no quote. The rule's
    regexes are then run on the located quote and the outcome is RECORDED (agree / silent / disagree), never used to
    overrule either side."""
    problems = []
    if not isinstance(claim, dict):
        return {"state": "VERIFIER_REFUSED", "problems": ["CLAIM_NOT_AN_OBJECT"]}
    field, value, quote = claim.get("field"), claim.get("value"), claim.get("quote")
    vocab = estimand_vocabulary(field) if isinstance(field, str) else []
    out: dict[str, Any] = {"task": "estimand", "field": field, "value": value}
    if not vocab:
        problems.append(f"FIELD_UNKNOWN: {field!r} is not a field the bundle's estimand rule reads")
    elif value == "NOT_STATED":
        if quote not in (None, ""):
            problems.append("NOT_STATED_WITH_SPAN: a field the model says is not stated cannot cite a span")
    elif value not in vocab:
        problems.append(f"VALUE_NOT_IN_RULE_VOCABULARY: {value!r} not in {vocab}")
    if vocab and value != "NOT_STATED":
        if not isinstance(quote, str) or not quote.strip():
            problems.append("NO_SPAN: a stated value must cite the sentence it was read from")
        else:
            loc = _locate(quote, held_text)
            out["located"] = loc
            if loc.get("match") not in ("VERBATIM", "NORMALISED"):
                problems.append("SPAN_NOT_IN_SOURCE: the quoted text is not in the held record (bundle locate ladder)")
            else:
                out["start"], out["end"], out["parent_representation"] = loc["start"], loc["end"], loc["parent"]
                rv = rule_values_on(field, quote)
                out["rule_on_span"] = {"values": rv}
                if not rv:
                    out["agreement"] = "RULE_SILENT_ON_SPAN(adjudication=OWED)"
                elif rv == [value]:
                    out["agreement"] = "RULE_AGREES_ON_SPAN"
                else:
                    out["agreement"] = f"RULE_MODEL_DISAGREE(rule={'|'.join(rv)}, model={value}, adjudication=OWED)"
    if vocab:
        out["rule_on_text"] = {"values": rule_values_on(field, held_text)}
    if vocab and value == "NOT_STATED" and not problems:
        on_text = out["rule_on_text"]["values"]
        out["agreement"] = ("RULE_MODEL_AGREE(both find no statement in the held text)" if not on_text else
                            f"RULE_MODEL_DISAGREE(rule={'|'.join(on_text)} found in the held text, model=NOT_STATED, adjudication=OWED)")
    out["problems"] = problems
    out["state"] = "VERIFIER_REFUSED" if problems else "VERIFIER_PASS"
    return out


SCREEN_AXES = ("population", "intervention", "comparator", "design")
SCREEN_VERDICTS = ("MET", "NOT_MET", "NOT_STATED")


def verify_screening(claim: Any, held_text: str, rule_decision: str) -> dict:
    """claim = {axes: {population|intervention|comparator|design: {verdict, quote}}}. The overall decision is
    DERIVED here, never taken from the model: ELIGIBLE iff every axis MET, INELIGIBLE iff any NOT_MET, else
    CANNOT_TELL. Every MET/NOT_MET must quote the held text (bundle locate ladder); NOT_STATED quotes nothing."""
    problems = []
    axes = claim.get("axes") if isinstance(claim, dict) else None
    out: dict[str, Any] = {"task": "screening", "rule_decision": rule_decision, "axes": {}}
    if not isinstance(axes, dict):
        problems.append("AXES_MISSING")
        axes = {}
    extra = sorted(set(axes) - set(SCREEN_AXES))
    if extra:
        problems.append(f"AXIS_UNKNOWN: {extra}")
    verdicts = {}
    for ax in SCREEN_AXES:
        a = axes.get(ax)
        if not isinstance(a, dict):
            problems.append(f"AXIS_MISSING: {ax}")
            continue
        v, q = a.get("verdict"), a.get("quote")
        if v not in SCREEN_VERDICTS:
            problems.append(f"VERDICT_NOT_TYPED: {ax}={v!r} not in {SCREEN_VERDICTS}")
            continue
        verdicts[ax] = v
        row: dict[str, Any] = {"verdict": v}
        if v == "NOT_STATED":
            if q not in (None, ""):
                problems.append(f"NOT_STATED_WITH_SPAN: {ax}")
        elif not isinstance(q, str) or not q.strip():
            problems.append(f"NO_SPAN: {ax} is {v} without a quote")
        else:
            loc = _locate(q, held_text)
            row["located"] = loc
            if loc.get("match") not in ("VERBATIM", "NORMALISED"):
                problems.append(f"SPAN_NOT_IN_SOURCE: {ax}")
        out["axes"][ax] = row
    if len(verdicts) == len(SCREEN_AXES):
        vals = set(verdicts.values())
        model = "INELIGIBLE" if "NOT_MET" in vals else ("ELIGIBLE" if vals == {"MET"} else "CANNOT_TELL")
        out["model_decision"] = model
        rule_elig = {"include": "ELIGIBLE", "exclude": "INELIGIBLE"}.get(rule_decision)
        if model == "CANNOT_TELL":
            out["agreement"] = f"MODEL_CANNOT_TELL(rule={rule_decision}, not_stated={sorted(a for a, v in verdicts.items() if v == 'NOT_STATED')}, adjudication=OWED)"
        elif model == rule_elig:
            out["agreement"] = "RULE_MODEL_AGREE"
        else:
            out["agreement"] = (f"RULE_MODEL_DISAGREE(rule={rule_decision}, model={model}, "
                                f"axes_not_met={sorted(a for a, v in verdicts.items() if v == 'NOT_MET')}, adjudication=OWED)")
    out["problems"] = problems
    out["state"] = "VERIFIER_REFUSED" if problems else "VERIFIER_PASS"
    return out


def _prior_agreement(pairs: list[tuple[str, Any, Any]], prior_label: str) -> str:
    """pairs: (field, prior value, model value). A prior is an earlier UNRECORDED judgment the served page reads."""
    if not pairs:
        return "MODEL_ONLY(no prior judgment; adjudication=OWED)"
    diff = [f"{f}: prior={p!r} model={m!r}" for f, p, m in pairs if p != m]
    return (f"PRIOR_MODEL_AGREE({prior_label})" if not diff
            else f"PRIOR_MODEL_DISAGREE({prior_label}; {'; '.join(diff)}; adjudication=OWED)")


OUTCOME_FIELDS = ("candidate_population", "candidate_timepoint", "candidate_definition", "is_match", "rationale")


def verify_outcome_identity(claim: Any, held_text: str, prior: dict | None = None) -> dict:
    """claim = the outcome-identity judgment of one CT.gov outcome measure. Typed check only: the held text is the
    measure's title/type, so there is no span to locate; the human signs the identity reading. The prior (the
    committed unrecorded judgment the served page reads) is compared on is_match and recorded, never resolved."""
    problems = []
    if not isinstance(claim, dict):
        return {"task": "outcome_identity", "state": "VERIFIER_REFUSED", "problems": ["CLAIM_NOT_AN_OBJECT"]}
    for f in OUTCOME_FIELDS:
        if f not in claim:
            problems.append(f"FIELD_MISSING: {f}")
    if "is_match" in claim and not isinstance(claim.get("is_match"), bool):
        problems.append("NOT_TYPED: is_match must be a bool")
    for f in ("candidate_population", "candidate_timepoint", "candidate_definition", "rationale"):
        if f in claim and not (isinstance(claim[f], str) and claim[f].strip()):
            problems.append(f"EMPTY: {f}")
    out: dict[str, Any] = {"task": "outcome_identity", "problems": problems,
                           "state": "VERIFIER_REFUSED" if problems else "VERIFIER_PASS"}
    if not problems:
        pairs = [("is_match", prior.get("is_match"), claim["is_match"])] if isinstance(prior, dict) and "is_match" in prior else []
        out["agreement"] = _prior_agreement(pairs, "prior = committed unrecorded judgment")
    return out


LOCATE_BOOLS = ("is_target_outcome", "population_matches", "both_arms")


def verify_locate(claim: Any, held_text: str, prior: dict | None = None) -> dict:
    """claim = {span, is_target_outcome, population_matches, both_arms, timepoint, why}. A span, when given, must be
    located in the held abstract by the bundle's ladder (SPAN_NOT_IN_SOURCE refuses); a claim that the outcome IS the
    target must cite one. Agreement with the prior is on is_target_outcome and population_matches."""
    problems = []
    if not isinstance(claim, dict):
        return {"task": "locate", "state": "VERIFIER_REFUSED", "problems": ["CLAIM_NOT_AN_OBJECT"]}
    for f in LOCATE_BOOLS:
        if not isinstance(claim.get(f), bool):
            problems.append(f"NOT_TYPED: {f} must be a bool")
    for f in ("timepoint", "why"):
        if not isinstance(claim.get(f), str):
            problems.append(f"NOT_TYPED: {f} must be a string")
    span = claim.get("span")
    out: dict[str, Any] = {"task": "locate"}
    if span not in (None, ""):
        if not isinstance(span, str):
            problems.append("NOT_TYPED: span")
        else:
            loc = _locate(span, held_text)
            out["located"] = loc
            if loc.get("match") not in ("VERBATIM", "NORMALISED"):
                problems.append("SPAN_NOT_IN_SOURCE: the quoted span is not in the held abstract (bundle locate ladder)")
    elif claim.get("is_target_outcome") is True:
        problems.append("NO_SPAN: a claim that the abstract reports the target outcome must quote where")
    out["problems"] = problems
    out["state"] = "VERIFIER_REFUSED" if problems else "VERIFIER_PASS"
    if not problems:
        pairs = ([(f, prior.get(f), claim[f]) for f in ("is_target_outcome", "population_matches") if f in prior]
                 if isinstance(prior, dict) else [])
        out["agreement"] = _prior_agreement(pairs, "prior = committed unrecorded judgment")
    return out


def reverify(entry: dict, held_text: str) -> dict:
    task = entry.get("task")
    prior = (entry.get("context") or {}).get("prior")
    if task == "estimand":
        return verify_estimand(entry.get("claim"), held_text)
    if task in ("screening", "screening_reader2", "screening_excluded", "screening_excluded_x1"):
        return verify_screening(entry.get("claim"), held_text, entry.get("rule_decision"))
    if task == "outcome_identity":
        return verify_outcome_identity(entry.get("claim"), held_text, prior)
    if task == "locate":
        return verify_locate(entry.get("claim"), held_text, prior)
    return {"state": "VERIFIER_REFUSED", "problems": [f"TASK_UNKNOWN: {task!r}"]}


def needs_individual_signature(verification: dict) -> bool:
    """A proposal that would change what the rule (or a prior judgment) decided, or cannot tell, is never covered by
    a batch signature."""
    return not str(verification.get("agreement") or "").startswith(
        ("RULE_MODEL_AGREE", "RULE_AGREES_ON_SPAN", "PRIOR_MODEL_AGREE"))


# ------------------------------------------------------------------------------------------------------ the gate
def queue_entry(*, task: str, item_id: str, record: dict, claim: Any, verification: dict, held_ref: str,
                held_sha256: str, rule_decision: str | None = None, context: dict | None = None,
                response_item: str | None = None) -> dict:
    e = {"task": task, "item_id": item_id, "record_id": record["record_id"],
         "response_sha256": record["response"]["sha256"], "claim": claim, "held_ref": held_ref,
         "held_sha256": held_sha256, "verification": verification, "status": "PROPOSED",
         "individual_signature_required": needs_individual_signature(verification),
         "reviewer_countersignature": {"state": "OPEN"}}
    if rule_decision is not None:
        e["rule_decision"] = rule_decision
    if response_item is not None:
        e["response_item"] = str(response_item)
    if context:
        e["context"] = context
    return e


def _esc(x: Any) -> str:
    return html.escape(x if isinstance(x, str) else json.dumps(x, sort_keys=True, ensure_ascii=False), quote=True)


def individual_required(entry: dict, verification: dict) -> bool:
    """Individual signature when the verdict does not agree, OR when a recorded re-ask of the identical prompt reached
    a different decision (the entry's flag; it can only tighten -- it is shown in the signed block, so editing it
    after a signature breaks the signature, and the queue recomputes it from the re-ask records)."""
    return needs_individual_signature(verification) or bool(entry.get("individual_signature_required"))


def render_proposal_block(entry: dict, record: dict) -> str:
    """What the reviewer sees, and what a signature names (result_changes.rendered_sha256 of this string). Carries the
    claim, the verifier's verdict, the rule/model agreement and the identity of the call (record id, prompt and
    response digests, model reported). Deterministic: no timestamps of rendering, sorted keys."""
    v = entry.get("verification") or {}
    m = record.get("model") or {}
    rows = [
        ("status", "PROPOSED (model output; inert until countersigned)"),
        ("task", entry.get("task")), ("item", entry.get("item_id")),
        ("rule decision", entry.get("rule_decision", "-")),
        ("model claim", entry.get("claim")),
        ("verifier", v.get("state")), ("verifier problems", v.get("problems") or []),
        ("rule / model", v.get("agreement", "-")),
        ("model decision (derived)", v.get("model_decision", "-")),
        ("held text", f"{entry.get('held_ref')} sha256 {entry.get('held_sha256')}"),
        ("record", f"{record.get('record_id')} ({record.get('state')})"),
        ("model reported", f"{m.get('id_reported')} via {m.get('provider')}"),
        ("prompt sha256", (record.get("prompt") or {}).get("sha256")),
        ("response sha256", (record.get("response") or {}).get("sha256")),
    ]
    rq = entry.get("reask")
    if isinstance(rq, dict):
        rows.append(("re-ask of the identical prompt",
                     ("same derived decision" if rq.get("same_derived_decision") else
                      f"DIFFERENT decision {rq.get('decisions')} -- the model does not reproduce its own answer here")
                     + f" ({', '.join(rq.get('records') or [])})"))
    rows.append(("signature required",
                 "INDIVIDUAL (rule and model do not agree, the rule cannot check the claim, or the model's answer did "
                 "not reproduce on re-ask)" if individual_required(entry, v) else "individual or batch"))
    body = "".join(f"<tr><th>{_esc(k)}</th><td>{_esc(val)}</td></tr>" for k, val in rows)
    return f"<div class='model-proposal'><table>{body}</table></div>"


def numbers_in(obj: Any, path: str = "") -> list[str]:
    """Paths of every int/float in a claim (bools are verdicts, not numbers; digits inside a quoted string are the
    source's words, located in the held text, not a value the model supplies)."""
    if isinstance(obj, bool) or obj is None or isinstance(obj, str):
        return []
    if isinstance(obj, (int, float)):
        return [path or "<claim>"]
    if isinstance(obj, dict):
        return [p for k, v in obj.items() for p in numbers_in(v, f"{path}.{k}" if path else str(k))]
    if isinstance(obj, (list, tuple)):
        return [p for i, v in enumerate(obj) for p in numbers_in(v, f"{path}[{i}]")]
    return [path or "<claim>"]


def gate_problems(entry: dict, record: dict, held_text: str) -> list[str]:
    """Empty only when all three conditions hold (and the claim carries no number). Anything else keeps it PROPOSED."""
    from harness import result_changes
    problems = []
    if not isinstance(held_text, str) or sha256_bytes(held_text.encode("utf-8")) != entry.get("held_sha256"):
        problems.append("HELD_TEXT_MISMATCH: the text handed to the gate is not the held text the entry names "
                        "(sha256 differs) -- verification against any other text proves nothing about this claim")
    nums = numbers_in(entry.get("claim"))
    if nums:
        problems.append(f"NUMBER_FROM_MODEL: {nums} -- a model never supplies a number (REPRODUCIBLE_MODEL_CONTRACT)")
    # (b) the call replays, and the queued claim is exactly what the stored response decodes to
    try:
        response = replay(record)
    except ReplayRefused as exc:
        return [f"REPLAY_REFUSED: {exc}"]
    if entry.get("record_id") != record.get("record_id"):
        problems.append("RECORD_MISMATCH: the entry names a different record")
    try:
        replayed_claim = extract_claim(entry.get("task"), response)
        if entry.get("response_item") is not None:
            replayed_claim = claim_for_item(replayed_claim, str(entry["response_item"]))
    except ValueError as exc:
        replayed_claim = None
        problems.append(f"RESPONSE_NOT_A_CLAIM: {exc}")
    if replayed_claim is not None and canonical(replayed_claim) != canonical(entry.get("claim")):
        problems.append("CLAIM_NOT_THE_RECORDED_ONE: the queued claim differs from the stored response")
    # (a) the same deterministic verifier, re-run now on the held text (never trusted from the queue)
    v = reverify(entry, held_text)
    if v.get("state") != "VERIFIER_PASS":
        problems.append(f"VERIFIER_REFUSED: {v.get('problems')}")
    if canonical(v) != canonical(entry.get("verification")):
        problems.append("VERIFICATION_STALE: the stored verdict is not what the verifier returns today")
    # (c) a human countersignature over the rendered block, with result_changes' discipline unchanged
    block = render_proposal_block(entry, record)
    notice = {"reviewer_countersignature": entry.get("reviewer_countersignature"),
              "conclusion_changed": (v.get("agreement") or "UNSTABLE_ON_REASK") if individual_required(entry, v) else None}
    sp = result_changes.signature_problem(notice, block)
    if sp:
        problems.append(f"COUNTERSIGNATURE: {sp}")
    return problems


def status_of(entry: dict, record: dict, held_text: str) -> str:
    return "COUNTERSIGNED" if not gate_problems(entry, record, held_text) else "PROPOSED"


# ------------------------------------------------------------------------------------------------------ responses
def extract_claim(task: str | None, response: bytes) -> Any:
    """The claim is the JSON object in the stored response -- parsed, never repaired. For a batched call the object
    carries {"items": [...]}, and the caller selects its item by id with claim_for_item()."""
    try:
        text = response.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"response is not UTF-8 ({exc})") from None
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```\s*$", "", s)
    try:
        obj = json.loads(s)
    except json.JSONDecodeError as exc:
        raise ValueError(f"response is not one JSON object ({exc.msg} at {exc.pos})") from None
    if not isinstance(obj, dict):
        raise ValueError("response JSON is not an object")
    return obj


def claim_for_item(obj: dict, item_key: str) -> Any:
    items = obj.get("items") if isinstance(obj, dict) else None
    if not isinstance(items, list):
        return obj
    hits = [i for i in items if isinstance(i, dict) and str(i.get("item")) == item_key]
    if len(hits) != 1:
        raise ValueError(f"{len(hits)} answers for item {item_key!r} in the response")
    return {k: v for k, v in hits[0].items() if k != "item"}


# ------------------------------------------------------------------------------------------------------ closure
def pinned_closure(root: str | Path = ROOT) -> set[str]:
    """Union of every served certificate's analysis_code_blobs: the code a served number is produced by."""
    out: set[str] = set()
    for cert in sorted(Path(root, "docs", "reviews").glob("*/CERTIFICATE.json")):
        blobs = json.loads(cert.read_text(encoding="utf-8")).get("analysis_code_blobs") or {}
        out |= set(blobs) if isinstance(blobs, dict) else {b["path"] for b in blobs}
    return out
