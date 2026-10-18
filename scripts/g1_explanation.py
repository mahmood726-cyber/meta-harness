"""Deterministic G1 explanations; no fetching and no implicit clock.

Reason mapping (unknown rules fail closed, including unknown GATE/PROTOCOL_TEXT):
X1, X-DESIGN -> DESIGN
X2 -> POPULATION
X3 -> COMPARATOR when the protocol rule names include.comparator; otherwise
      INTERVENTION_DOSE_OR_REGIMEN when it names include.intervention
X-DOSE -> INTERVENTION_DOSE_OR_REGIMEN
E2:COMPARATOR_NOT_PLACEBO -> COMPARATOR
PROTOCOL_TEXT:POPULATION -> POPULATION
PROTOCOL_TEXT:INTERVENTION_DOSE_AND_REGIMEN -> INTERVENTION_DOSE_OR_REGIMEN
PROTOCOL_TEXT:DESIGN_AND_COMPARATOR -> DESIGN (the recorded combined axis)
PROTOCOL_TEXT:<closed reason code> -> that reason code
ARM_OBJECT -> INTERVENTION_DOSE_OR_REGIMEN for arm_object.dose;
              TIMEPOINT for primary_outcome.timepoint
G1-OUTCOME-SET, NOT_IN_COMPARATOR_OUTCOME_ANALYSIS -> NOT_IN_COMPARATOR_OUTCOME_ANALYSIS
G1-ONE-TRIAL-ONE-UNIT, SAME_TRIAL_AS_ANOTHER_UNIT -> DESIGN (unit of analysis)
GATE:composite_component_mismatch -> OUTCOME_DEFINITION
ESTIMAND_DIFFERENCE -> ESTIMAND (unless the specific composite gate above applies)
NOT_AN_INCLUDED_TRIAL, COMPARATOR_STATED_K -> NOT_IN_COMPARATOR_OUTCOME_ANALYSIS
DECISION_EXCLUDED_FROM_SERVED_POOL -> DECISION_EXCLUDED
NAMED_DIVERGENCE_POST_HOC_SAFETY_POPULATION_ON_TREATMENT_WINDOW -> ANALYSIS_SET

Static: these mappings and source applicability. Dynamic: all claims, hashes,
spans, decisions, searches and totals. No research values are manufactured.
The repository adapter reads HEAD blobs only: a local/gitignored body cannot
establish committed evidence. It never truncates a document or hashes a window.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
from functools import lru_cache
import hashlib
import base64
import binascii
import ast
import json
from pathlib import Path
import re
import subprocess

from scripts.g1_explanation_vocab import STATES, REASON_CODES, SOURCES, STEPS, ACCESS_OUTCOMES, FRESH_DAYS
from scripts.g1_explanation_vocab import SOURCE_UNREACHABLE, UNREACHABLE_STEPS, EVIDENCE_KINDS


def pubmed_epmc_pmid(ids):
    return bool(ids.get("pmids"))


def pubmed_epmc_title(ids):
    return True


def unpaywall_doi(ids):
    return bool(ids.get("dois"))


def ctgov_v2(ids):
    return bool(ids.get("ncts"))


def aact(ids):
    return bool(ids.get("ncts"))


def euctr(ids):
    return bool(ids.get("eudract"))


def who_ictrp(ids):
    return True


def fda(ids):
    return ids.get("approved_drug") is True


def ema(ids):
    return ids.get("approved_drug") is True


def pmda(ids):
    return ids.get("approved_drug") is True


def tga_auspar(ids):
    return ids.get("approved_drug") is True


def fda_adcomm(ids):
    return ids.get("approved_drug") is True


def ahrq_nihr_hta(ids):
    return ids.get("approved_drug") is True


def sponsor_register(ids):
    return ids.get("approved_drug") is True


def health_canada(ids):
    return False


def ema_clinical_data(ids):
    return False


APPLICABILITY = {s: globals()[s.lower()] for s in SOURCES}


def required_sources(identifiers):
    return [s for s in SOURCES if APPLICABILITY[s](identifiers)]


RULE_REASONS = {
    "X1": "DESIGN", "X-DESIGN": "DESIGN", "X2": "POPULATION",
    "X-DOSE": "INTERVENTION_DOSE_OR_REGIMEN",
    "E2:COMPARATOR_NOT_PLACEBO": "COMPARATOR",
    "PROTOCOL_TEXT:POPULATION": "POPULATION",
    "PROTOCOL_TEXT:INTERVENTION_DOSE_AND_REGIMEN": "INTERVENTION_DOSE_OR_REGIMEN",
    "PROTOCOL_TEXT:DESIGN_AND_COMPARATOR": "DESIGN",
    "G1-OUTCOME-SET": "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS",
    "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS": "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS",
    "G1-ONE-TRIAL-ONE-UNIT": "DESIGN", "SAME_TRIAL_AS_ANOTHER_UNIT": "DESIGN",
    "GATE:composite_component_mismatch": "OUTCOME_DEFINITION",
    "ESTIMAND_DIFFERENCE": "ESTIMAND",
    "NOT_AN_INCLUDED_TRIAL": "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS",
    "COMPARATOR_STATED_K": "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS",
    "DECISION_EXCLUDED_FROM_SERVED_POOL": "DECISION_EXCLUDED",
    "NAMED_DIVERGENCE_POST_HOC_SAFETY_POPULATION_ON_TREATMENT_WINDOW": "ANALYSIS_SET",
}


def reason_code(record):
    rule = record.get("rule_id") or record.get("kind") or record.get("reason")
    protocol = record.get("protocol_rule") or ""
    if rule == "X3":
        if "include.comparator" in protocol:
            return "COMPARATOR"
        if "include.intervention" in protocol:
            return "INTERVENTION_DOSE_OR_REGIMEN"
        return None
    if rule == "ARM_OBJECT":
        if "arm_object.dose" in protocol:
            return "INTERVENTION_DOSE_OR_REGIMEN"
        if "primary_outcome.timepoint" in protocol:
            return "TIMEPOINT"
        return None
    if str(rule).startswith("PROTOCOL_TEXT:") and str(rule).split(":", 1)[1] in REASON_CODES:
        return str(rule).split(":", 1)[1]
    return RULE_REASONS.get(rule)


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _norm(text):
    return " ".join(text.split())


def _document_text(body):
    """Decode a WHOLE UTF-8 document, including escaped strings in JSON records."""
    text = body.decode("utf-8")
    try:
        obj = json.loads(text)
    except ValueError:
        return text

    def strings(x):
        if isinstance(x, str):
            yield x
        elif isinstance(x, dict):
            for v in x.values():
                yield from strings(v)
        elif isinstance(x, list):
            for v in x:
                yield from strings(v)
    # Separate fields so a synthetic cross-field span cannot validate.
    return text + "\n\x00\n" + "\n\x00\n".join(strings(obj))


def _recorded_answers(body):
    """Only answer/quote fields qualify; prompts and metadata never do."""
    obj = json.loads(body)
    if not isinstance(obj, dict):
        raise ValueError("record must be an object")
    answers = []
    def collect(value):
        if isinstance(value, str):
            answers.append(value)
        elif isinstance(value, list):
            for item in value:
                collect(item)
        elif isinstance(value, dict):
            answers.append(json.dumps(value, ensure_ascii=False, separators=(",", ":")))
            for item in value.values():
                collect(item)
    for key in ("answer", "recorded_answer", "quote", "quotes"):
        if key in obj:
            collect(obj[key])
    response = obj.get("response")
    if isinstance(response, dict) and "b64" in response:
        raw = base64.b64decode(response["b64"], validate=True)
        if response.get("sha256") and hashlib.sha256(raw).hexdigest() != response["sha256"]:
            raise ValueError("recorded response hash mismatch")
        if response.get("bytes") is not None and len(raw) != response["bytes"]:
            raise ValueError("recorded response length mismatch")
        answer = raw.decode("utf-8")
        answers.append(answer)
        try:
            collect(json.loads(answer))
        except ValueError:
            pass
    elif isinstance(response, str):
        collect(response)
    return answers


def _record_evidence_errors(ev, held_bytes):
    kind = ev["kind"]
    rid = ev.get("record_id")
    if not _nonempty(rid) or not _sha(ev.get("sha256")):
        return [f"{kind} missing record_id or invalid sha256: {rid}"]
    store = getattr(held_bytes, "__self__", None)
    if store is None or not hasattr(store, "read"):
        return [f"{kind} committed record resolver unavailable: {rid}"]
    path = rid
    if not rid.endswith(".json") and hasattr(store, "record_digest"):
        resolved = store.record_digest(rid)
        if not resolved:
            return [f"{kind} record file not committed: {rid}"]
        path = resolved[0]
    body = store.read(path)
    if body is None:
        return [f"{kind} record file not committed: {path}"]
    if hashlib.sha256(body).hexdigest() != ev["sha256"]:
        return [f"{kind} record sha mismatch: {path}"]
    try:
        if kind == "RECORDED_READ":
            fields = _recorded_answers(body)
        else:
            obj = json.loads(body)
            if not isinstance(obj, dict):
                raise ValueError("registry record must be an object")
            if ev.get("nct") is not None:
                obj = obj.get(ev["nct"], {})
            if not isinstance(obj, dict):
                raise ValueError("registry study must be an object")
            snapshot = obj.get("_snapshot", obj.get("snapshot"))
            sid = snapshot.get("id") if isinstance(snapshot, dict) else snapshot
            if (not _nonempty(ev.get("snapshot_id")) or sid != ev.get("snapshot_id")
                    or not _nonempty(ev.get("outcome_id"))):
                return [f"REGISTRY_RECORD snapshot/outcome identity missing or mismatched: {path}"]
            outcomes = obj.get("outcomes", {})
            row = outcomes.get(ev["outcome_id"]) if isinstance(outcomes, dict) else None
            if not isinstance(row, dict):
                return [f"REGISTRY_RECORD outcome {ev.get('outcome_id')} absent: {path}"]
            fields = [v for v in row.values() if isinstance(v, str)]
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error) as exc:
        return [f"{kind} invalid record: {path}: {exc}"]
    span = ev.get("verbatim_span")
    if not _nonempty(span) or not any(_norm(span) in _norm(field) for field in fields):
        return [f"{kind} span missing from recorded answer/quote fields: {path}"]
    return []


def _decision_ids(decisions):
    return {d.get("id") for d in decisions.get("decisions", []) if isinstance(d, dict)}


def _build_day(build_date):
    if isinstance(build_date, datetime):
        if build_date.tzinfo is None:
            raise ValueError("build_date datetime must have a timezone")
        return build_date.astimezone(timezone.utc).date()
    if isinstance(build_date, date):
        return build_date
    return date.fromisoformat(build_date)


def validate_explanation(entry, trial, *, build_date, held_bytes, decisions, identifiers=None):
    """Return all defects (empty means valid). UNEXPLAINED is valid with a reason."""
    day = _build_day(build_date)
    if not isinstance(entry, dict) or entry.get("state") not in STATES:
        return ["missing or invalid explanation state"]
    state = entry["state"]
    errors = []
    if state == "UNEXPLAINED":
        return [] if _nonempty(entry.get("why_unexplained")) else ["UNEXPLAINED needs why_unexplained"]
    if state == "MATCHED":
        from scripts.g1_tracker import route_group
        if route_group(trial.get("route")) != "PRIMARY" or entry.get("route") != trial.get("route"):
            errors.append("MATCHED requires the trial's PRIMARY route")
        for key in ("source_ref", "verified_by"):
            if not _nonempty(entry.get(key)):
                errors.append(f"MATCHED missing {key}")
        if not _sha(entry.get("sha256")):
            errors.append("MATCHED missing or invalid sha256")
        return errors
    if state == "DIVERGENT_NAMED":
        if entry.get("reason_code") not in REASON_CODES:
            errors.append("DIVERGENT_NAMED unknown reason_code")
        for key in ("detail", "decided_by"):
            if not _nonempty(entry.get(key)):
                errors.append(f"DIVERGENT_NAMED missing {key}")
        if entry.get("reason_code") == "DECISION_EXCLUDED" and entry.get("decided_by") not in _decision_ids(decisions):
            errors.append("DECISION_EXCLUDED unknown decision id")
        ev = entry.get("evidence")
        if not isinstance(ev, dict):
            return errors + ["DIVERGENT_NAMED missing evidence"]
        if ev.get("resolution_error"):
            return errors + [ev["resolution_error"]]
        if ev.get("kind") in EVIDENCE_KINDS:
            return errors + _record_evidence_errors(ev, held_bytes)
        if ev.get("kind") is not None:
            return errors + ["DIVERGENT_NAMED unknown evidence kind"]
        if not _nonempty(ev.get("source_ref")):
            errors.append("DIVERGENT_NAMED missing source_ref")
        if not _nonempty(ev.get("verbatim_span")):
            return errors + ["DIVERGENT_NAMED span not in held bytes (missing verbatim_span)"]
        if not _sha(ev.get("sha256")):
            return errors + [f"DIVERGENT_NAMED missing or invalid sha256: {ev.get('source_ref')}"]
        body = held_bytes(ev["sha256"])
        if body is None:
            return errors + [f"DIVERGENT_NAMED held bytes not committed: {ev.get('source_ref')}"]
        if not isinstance(body, bytes) or hashlib.sha256(body).hexdigest() != ev["sha256"]:
            return errors + ["DIVERGENT_NAMED held bytes hash mismatch"]
        try:
            text = _document_text(body)
        except UnicodeDecodeError:
            return errors + ["DIVERGENT_NAMED held bytes are not UTF-8 text"]
        span = ev.get("verbatim_span")
        if not _nonempty(span) or _norm(span) not in _norm(text):
            errors.append(f"DIVERGENT_NAMED span not in held bytes: {ev.get('source_ref')}")
        return errors
    if not isinstance(identifiers, dict):
        return ["NO_OPEN_SOURCE missing identifiers/applicability evidence"]
    for key in ("pmids", "dois", "ncts", "eudract"):
        if not isinstance(identifiers.get(key), list) or any(not _nonempty(v) for v in identifiers[key]):
            errors.append(f"NO_OPEN_SOURCE invalid identifiers.{key}")
    if not isinstance(identifiers.get("approved_drug"), bool):
        errors.append("NO_OPEN_SOURCE missing approved_drug applicability")
    for key in ("title", "acronym"):
        if key not in identifiers or (identifiers[key] is not None and not isinstance(identifiers[key], str)):
            errors.append(f"NO_OPEN_SOURCE invalid identifiers.{key}")
    if not isinstance(entry.get("secondary_value_available"), bool):
        errors.append("NO_OPEN_SOURCE missing secondary_value_available")
    from scripts.g1_tracker import route_group
    if route_group(trial.get("route")) in ("SECONDARY_SINGLE", "TWO_SOURCE") and entry.get("secondary_value_available") is not True:
        errors.append("NO_OPEN_SOURCE secondary route requires secondary_value_available true")
    searched = entry.get("searched")
    if not isinstance(searched, list):
        return errors + ["NO_OPEN_SOURCE missing searched records"]
    fresh, seen, gated, latest = set(), set(), {}, {}
    for i, rec in enumerate(searched):
        if not isinstance(rec, dict):
            errors.append(f"searched[{i}] invalid record")
            continue
        source, step = rec.get("source"), rec.get("step_reached")
        if source not in SOURCES or step not in (*STEPS, *ACCESS_OUTCOMES):
            errors.append(f"searched[{i}] unknown source or step_reached")
            continue
        seen.add(source)
        outcome = rec.get("outcome")
        if not _nonempty(rec.get("identifier_or_query")) or not (
                _nonempty(outcome) or isinstance(outcome, dict) and bool(outcome)):
            errors.append(f"searched[{i}] missing identifier_or_query/outcome")
        if rec.get("response_sha256") is not None and not _sha(rec["response_sha256"]):
            errors.append(f"searched[{i}] invalid response_sha256")
        try:
            stamp = rec["when_utc"]
            if not isinstance(stamp, str) or not stamp.endswith("Z") or "T" not in stamp:
                raise ValueError()
            when = datetime.fromisoformat(stamp[:-1] + "+00:00")
            age = (day - when.date()).days
        except (KeyError, ValueError, TypeError):
            errors.append(f"searched[{i}] invalid when_utc")
            continue
        if age < 0:
            errors.append(f"searched[{i}] future when_utc")
        if 0 <= age <= FRESH_DAYS:
            key = (source, str(rec.get("identifier_or_query")))
            if key not in latest or stamp >= latest[key][0]:
                latest[key] = (stamp, step, rec.get("outcome"))
    # the LATEST record per (source, identifier) decides (16 Oct): the log keeps history, so with "any fresh record"
    # an older NOT_FOUND satisfied a source whose newer record says NEW_REPORT_FOUND, and why_unexplained quoted a
    # superseded 'ERROR' ahead of the current outcome
    for (source, _q), (_stamp, step, outcome) in sorted(latest.items()):
        if step in STEPS:
            fresh.add(source)
        else:
            gated.setdefault(source, []).append(f"{step}: {outcome}")
    unreachable = entry.get("unreachable", [])
    listed = set()
    if not isinstance(unreachable, list):
        errors.append("NO_OPEN_SOURCE invalid unreachable records")
        unreachable = []
    for rec in unreachable:
        if not isinstance(rec, dict):
            errors.append("invalid SOURCE_UNREACHABLE record")
            continue
        source = rec.get("source")
        blocked = [(stamp, step) for (s, _), (stamp, step, _) in latest.items()
                   if s == source and step in UNREACHABLE_STEPS]
        try:
            stamp = rec["when_utc"]
            if not isinstance(stamp, str) or not stamp.endswith("Z") or "T" not in stamp:
                raise ValueError()
            age = (day - datetime.fromisoformat(stamp[:-1] + "+00:00").date()).days
            valid = 0 <= age <= FRESH_DAYS
        except (KeyError, TypeError, ValueError):
            valid = False
        if (source not in required_sources(identifiers) or not blocked or not valid
                or not _nonempty(rec.get("reason")) or source in listed):
            errors.append(f"invalid SOURCE_UNREACHABLE: {source}")
        else:
            listed.add(source)
    for source in required_sources(identifiers):
        unfinished = [step for (s, _), (_, step, _) in latest.items()
                      if s == source and step not in (*STEPS, *UNREACHABLE_STEPS)]
        blocked = any(s == source and step in UNREACHABLE_STEPS
                      for (s, _), (_, step, _) in latest.items())
        if unfinished or blocked and source not in listed or not blocked and source not in fresh:
            if source in gated:
                errors.append(f"required source {source} gated: " + "; ".join(gated[source]))
            else:
                errors.append(f"required source {source} " + ("stale" if source in seen else "missing"))
    return errors


def source_states(searched):
    """Latest per source+identifier; availability is distinct from search work."""
    latest = {}
    for rec in searched if isinstance(searched, list) else []:
        if not isinstance(rec, dict) or rec.get("source") not in SOURCES:
            continue
        stamp = rec.get("when_utc")
        try:
            if not isinstance(stamp, str) or not stamp.endswith("Z") or "T" not in stamp:
                continue
            when = datetime.fromisoformat(stamp[:-1] + "+00:00")
        except ValueError:
            continue
        key = rec["source"], str(rec.get("identifier_or_query"))
        if key not in latest or when >= latest[key][0]:
            latest[key] = when, rec
    blocked = {}
    for _, rec in latest.values():
        if rec.get("step_reached") in UNREACHABLE_STEPS:
            source = rec["source"]
            reason = rec.get("outcome")
            reason = reason if isinstance(reason, str) else json.dumps(reason, sort_keys=True)
            item = dict(state=SOURCE_UNREACHABLE, source=source, when_utc=rec["when_utc"],
                        reason=rec["step_reached"] + ": " + reason)
            if source not in blocked or item["when_utc"] >= blocked[source]["when_utc"]:
                blocked[source] = item
    return [blocked[s] for s in sorted(blocked)]


def _searched(log):
    """Adapt derived job-B records without rewriting the log or inventing a search."""
    searched = deepcopy(log.get("searched"))
    ids = log.get("identifiers") or {}
    fields = {"PUBMED_EPMC_PMID": ("pmids",), "UNPAYWALL_DOI": ("dois",),
              "CTGOV_V2": ("ncts",), "AACT": ("ncts",), "EUCTR": ("eudract",)}
    for rec in searched if isinstance(searched, list) else []:
        if not isinstance(rec, dict):
            continue
        query = rec.get("identifier_or_query")
        if _nonempty(query) or query is not None and not isinstance(query, str):
            continue
        source = rec.get("source")
        values = []
        for key in fields.get(source, ("pmids", "ncts", "dois", "eudract", "title", "acronym")):
            value = ids.get(key)
            values.extend(v for v in (value if isinstance(value, list) else [value]) if _nonempty(v))
        if source in SOURCES and values:
            rec["identifier_or_query"] = source + ": " + "; ".join(dict.fromkeys(values))
    return searched


def build_explanation(trial, *, build_date, held_bytes, decisions, search_log=None,
                      divergences=(), primary=None):
    """Pure builder. Invalid candidates never escape; precedence is explicit."""
    from scripts.g1_tracker import route_group
    ctx = dict(build_date=build_date, held_bytes=held_bytes, decisions=decisions)
    errors = []
    if route_group(trial.get("route")) == "PRIMARY":
        entry = dict(primary or {}, state="MATCHED", route=trial.get("route"))
        bad = validate_explanation(entry, trial, **ctx)
        if not bad:
            return entry
        errors.extend(bad)
        if primary and primary.get("missing_evidence"):
            errors.append(primary["missing_evidence"])
    unresolved_record = False
    for candidate in divergences:
        entry = dict(candidate, state="DIVERGENT_NAMED")
        bad = validate_explanation(entry, trial, **ctx)
        if not bad:
            if errors:
                entry["note"] = "; ".join(errors)
            return entry
        errors.extend(bad)
        unresolved_record |= (entry.get("evidence") or {}).get("kind") in EVIDENCE_KINDS
    if unresolved_record:
        return {"state": "UNEXPLAINED", "why_unexplained": "; ".join(dict.fromkeys(errors))}
    if search_log is not None:
        entry = {"state": "NO_OPEN_SOURCE", "searched": _searched(search_log),
                 "unreachable": deepcopy(search_log.get("unreachable", [])),
                 "secondary_value_available": search_log.get("secondary_value_available")}
        if route_group(trial.get("route")) in ("TWO_SOURCE", "SECONDARY_SINGLE"):
            entry["secondary_value_available"] = True
        bad = validate_explanation(entry, trial, identifiers=search_log.get("identifiers"), **ctx)
        if not bad:
            if errors:
                entry["note"] = "; ".join(errors)
            return entry
        errors.extend(bad)
    else:
        errors.append("NO_OPEN_SOURCE search log missing")
    return {"state": "UNEXPLAINED", "why_unexplained": "; ".join(dict.fromkeys(errors))}


class CommittedRecords:
    """Offline HEAD reader and whole-document SHA resolver.

    Paths follow k_gap_counterfactual's fulltext_index/_ft and ctgov_index/_ctgov,
    k_gap.unpaywall_text's DOI SHA1/_upw, regulatory _reg and held-record caches.
    Only HEAD files are considered, never untracked/ignored cache bytes. Source
    references are tried first; fallback scans only held document directories.
    """
    def __init__(self, root):
        self.root = Path(root)
        self.revision = self._git("rev-parse", "HEAD").decode("ascii").strip()
        result = self._git("ls-tree", "-r", "--name-only", self.revision)
        self.paths = set(result.decode("utf-8").splitlines())
        self.blobs = {}
        self.by_sha = {}
        self.scanned = False

    def _git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def read(self, path):
        path = str(path).replace("\\", "/").split("#", 1)[0]
        if path not in self.paths:
            return None
        if path not in self.blobs:
            body = self._git("show", f"{self.revision}:{path}")
            self.blobs[path] = body
            self.by_sha[hashlib.sha256(body).hexdigest()] = body
            if path.endswith("/records.json"):
                # The harness also commits WHOLE reports inside this named field.
                for text in (json.loads(body).get("fulltext_by_pmid") or {}).values():
                    if isinstance(text, str):
                        raw = text.encode("utf-8")
                        self.by_sha[hashlib.sha256(raw).hexdigest()] = raw
        return self.blobs[path]

    def json(self, path):
        if not hasattr(self, "json_cache"):
            self.json_cache = {}
        if path not in self.json_cache:
            body = self.read(path)
            self.json_cache[path] = json.loads(body) if body is not None else {}
        return self.json_cache[path]

    def _read_many(self, paths):
        # Whole committed documents, in bounded batches; thousands of individual
        # git-show processes made the all-topic preview needlessly expensive.
        paths = [p for p in paths if p not in self.blobs]
        for offset in range(0, len(paths), 128):
            batch = paths[offset:offset + 128]
            request = "".join(f"{self.revision}:{p}\n" for p in batch).encode("utf-8")
            raw = subprocess.run(["git", "-C", str(self.root), "cat-file", "--batch"], input=request,
                                 check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
            pos = 0
            for path in batch:
                end = raw.index(b"\n", pos)
                size = int(raw[pos:end].split()[2])
                body = raw[end + 1:end + 1 + size]
                pos = end + size + 2
                self.blobs[path] = body
                self.by_sha[hashlib.sha256(body).hexdigest()] = body
                if path.endswith("/records.json"):
                    for text in (json.loads(body).get("fulltext_by_pmid") or {}).values():
                        if isinstance(text, str):
                            encoded = text.encode("utf-8")
                            self.by_sha[hashlib.sha256(encoded).hexdigest()] = encoded

    def record_digest(self, record_id):
        """Only a committed call file is evidence; never its id's hex suffix."""
        paths = sorted(p for p in self.paths if p.endswith(f"/{record_id}.json")
                       and p.startswith(("registry/model_calls/", "evidence/model_calls/")))
        for path in paths:
            body = self.read(path)
            if body is not None:
                return path, hashlib.sha256(body).hexdigest()
        return None

    def source_document(self, slug, identifier, kind):
        """Resolve an explicitly identified source, not a comparator or nearby paper."""
        if kind == "fulltext":
            rec = self.json("outputs/k_gap/fulltext_index.json").get(identifier, {})
            if _sha(rec.get("sha256")) and rec.get("copy_licence") in (None, "CC"):
                return f"PMID {identifier} fulltext (outputs/k_gap/fulltext_index.json)", rec["sha256"]
        if kind == "ctgov_results":
            rec = self.json("outputs/k_gap/ctgov_index.json").get(identifier, {})
            if _sha(rec.get("sha256")) and rec.get("posted") is True:
                return identifier + " (outputs/k_gap/ctgov_index.json)", rec["sha256"]
        for path in (f"cache/{slug}/records.json", f"cache/{slug}/comparator_records.json",
                     "outputs/k_gap/member_records.json"):
            data = self.json(path)
            if kind == "fulltext":
                body = (data.get("fulltext_by_pmid") or {}).get(identifier)
                if _nonempty(body):
                    return f"PMID {identifier} {path}#fulltext_by_pmid", hashlib.sha256(body.encode("utf-8")).hexdigest()
            elif kind == "ctgov_results":
                rows = data.get("records", []) if "records" in data else list(data.values())
                ncts = {r.get("nct") for r in rows if isinstance(r, dict) and str(r.get("id")) == identifier
                        and re.fullmatch(r"NCT\d+", str(r.get("nct") or ""))}
                if len(ncts) == 1 and identifier not in ncts:
                    doc = self.source_document(slug, next(iter(ncts)), kind)
                    if doc:
                        return doc
                if (data.get("ctgov_results") or {}).get(identifier):
                    return f"{identifier} {path}#ctgov_results", hashlib.sha256(self.read(path)).hexdigest()
            else:
                rows = data.get("records", []) if "records" in data else list(data.values())
                if any(isinstance(r, dict) and str(r.get("id")) == identifier and _nonempty(r.get("abstract"))
                       for r in rows):
                    return f"PMID {identifier} {path}#abstract", hashlib.sha256(self.read(path)).hexdigest()
        return None

    def held_bytes(self, sha256):
        if not _sha(sha256):
            return None
        if sha256 in self.by_sha:
            return self.by_sha[sha256]
        # The indexes pin whole documents; they are not themselves the document.
        # In particular regulatory_index.sha256 is the PDF hash, NOT text_sha256.
        for index, kind in (("outputs/k_gap/fulltext_index.json", "pmid"),
                            ("outputs/k_gap/unpaywall_text_index.json", "doi"),
                            ("outputs/k_gap/ctgov_index.json", "nct"),
                            ("registry/regulatory_sources.json", "regulator")):
            for key, rec in self.json(index).items():
                if not isinstance(rec, dict) or rec.get("text_sha256" if kind == "regulator" else "sha256") != sha256:
                    continue
                if kind == "pmid":
                    paths = [f"outputs/k_gap/_ft/{key}.txt"] + sorted(
                        p for p in self.paths if p.startswith("cache/") and p.endswith(f"/ft_{key}.txt"))
                elif kind == "nct":
                    paths = [f"outputs/k_gap/_ctgov/{key}.json"]
                else:
                    token = key.lower() if kind == "doi" else key
                    folder = "_upw" if kind == "doi" else "_reg"
                    paths = [f"outputs/k_gap/{folder}/{hashlib.sha1(token.encode('utf-8')).hexdigest()[:16]}.txt"]
                for path in paths:
                    self.read(path)
                if sha256 in self.by_sha:
                    return self.by_sha[sha256]
        if sha256 not in self.by_sha and not self.scanned:
            paths = []
            for path in sorted(self.paths):
                if (path.startswith(("cache/", "outputs/k_gap/_ft/", "outputs/k_gap/_upw/",
                                     "outputs/k_gap/_reg/", "outputs/k_gap/_ctgov/"))
                        or path == "outputs/k_gap/member_records.json") and path.endswith((".txt", ".json", ".xml")):
                    paths.append(path)
            self._read_many(paths)
            self.scanned = True
        return self.by_sha.get(sha256)

    def registry_record(self, record, ev):
        source = str(ev.get("source_ref") or "")
        match = re.fullmatch(r"AACT snapshot (.+) outcome (\d+)", source)
        if not match:
            return None
        sid, oid = match.groups()
        # This is the typed index used by g1_tracker.registry_binding, not a
        # regenerated tracker repeating its own claim or an unrelated outcome.
        path = "outputs/k_gap/_aact_results.json"
        body = self.read(path)
        if body is not None:
            data = json.loads(body)
            matches = [nct for nct, row in data.items() if isinstance(row, dict)
                       and (row.get("_snapshot") or {}).get("id") == sid
                       and oid in row.get("outcomes", {})
                       and (not record.get("snapshot", {}).get("digest") or
                            row["_snapshot"].get("digest") == record["snapshot"]["digest"])]
            if len(matches) == 1:
                return dict(kind="REGISTRY_RECORD", record_id=path, source_ref=path,
                            sha256=hashlib.sha256(body).hexdigest(), snapshot_id=sid,
                            outcome_id=oid, nct=matches[0], verbatim_span=ev.get("verbatim_span"))
        return dict(ev, kind="REGISTRY_RECORD", snapshot_id=sid, outcome_id=oid,
                    resolution_error=f"REGISTRY_RECORD {sid} outcome {oid}: "
                    f"{path} not committed or snapshot/outcome not uniquely present")

    def recorded_read(self, record, slug, ev):
        source = str(ev.get("source_ref") or "")
        if "recorded read" not in source:
            return None
        ids = re.findall(r"mc-[0-9a-f]{32}", source)
        if not ids and "g1/forest-reader" in source:
            match = re.search(r"comparator PMID (\d+) figure (\S+)", source)
            if match:
                prefix = f"{slug}::{match[1]}::{match[2]}::"
                runs = self.json("registry/model_proposals/g1_forest_reader_runs.json")
                ids = [v.get("record_id") for k, v in sorted(runs.items())
                       if k.startswith(prefix) and v.get("state") == "RAN_OK"]
        for rid in ids:
            call = self.record_digest(rid)
            if not call:
                continue
            body = self.read(call[0])
            try:
                answers = _recorded_answers(body)
            except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
                continue
            span = ev.get("verbatim_span")
            # The old outcome-set 'span' was generated narration. Tie its exact
            # complete row set to an answer, then quote that answer verbatim.
            if record.get("rule_id") == "G1-OUTCOME-SET":
                match = re.search(r": rows (\[.*?\]); positive control", str(span))
                if not match:
                    continue
                try:
                    expected = ast.literal_eval(match[1])
                except (ValueError, SyntaxError):
                    continue
                span = None
                for answer in answers:
                    try:
                        parsed = json.loads(answer)
                    except ValueError:
                        continue
                    if (isinstance(parsed, dict) and isinstance(parsed.get("rows"), list)
                            and all(isinstance(r, dict) for r in parsed["rows"])
                            and [r.get("label") for r in parsed["rows"]] == expected):
                        span = answer
                        break
            if _nonempty(span) and any(_norm(span) in _norm(a) for a in answers):
                return dict(kind="RECORDED_READ", record_id=rid, sha256=call[1],
                            source_ref=call[0], verbatim_span=span)
        return dict(ev, kind="RECORDED_READ", resolution_error=
                    f"RECORDED_READ unresolved answer/row set: {source}; records {ids or 'not found'}")

    def evidence(self, record, slug):
        ev = deepcopy(record.get("evidence") or {})
        span = record.get("span") or {}
        if isinstance(span, str):
            span = {"text": span}
        ev.setdefault("verbatim_span", span.get("text") or record.get("quote"))
        ev.setdefault("source_ref", span.get("source") or record.get("span_source") or record.get("source"))
        ev.setdefault("sha256", span.get("fulltext_sha256") or record.get("sha256") or record.get("source_sha256"))
        if ev.get("kind") in EVIDENCE_KINDS:
            return ev
        if hasattr(self, "registry_record"):
            registry = self.registry_record(record, ev)
            if registry is not None:
                return registry
        if hasattr(self, "recorded_read"):
            recorded = self.recorded_read(record, slug, ev)
            if recorded is not None:
                return recorded
        if not ev.get("sha256") and record.get("pmid") and span.get("field") == "fulltext":
            doc = self.source_document(slug, str(record["pmid"]), "fulltext")
            if doc:
                ev["source_ref"], ev["sha256"] = doc
        if not ev.get("sha256"):
            for rid in re.findall(r"mc-[0-9a-f]{32}", str(ev.get("source_ref") or "")):
                call = self.record_digest(rid)
                if call:
                    ev["source_ref"] += "; " + call[0]
                    ev["sha256"] = call[1]
                    break
        if ev.get("source_ref"):
            body = self.read(ev["source_ref"])
            if body is not None and not ev.get("sha256"):
                ev["sha256"] = hashlib.sha256(body).hexdigest()
        # An abstract span can be tied to its complete committed record container,
        # only after locating that trial's own PMID and field (never a text search
        # over unrelated records to manufacture provenance).
        if not ev.get("sha256") and record.get("pmid") and span.get("field") != "fulltext":
            for path in (f"cache/{slug}/records.json", "outputs/k_gap/member_records.json"):
                data = self.json(path)
                rows = data.get("records", []) + data.get("ctgov", []) if "records" in data else list(data.values())
                for row in rows:
                    if isinstance(row, dict) and str(row.get("id")) == str(record["pmid"]):
                        value = row.get(span.get("field"))
                        values = value if isinstance(value, list) else [value]
                        if _nonempty(ev.get("verbatim_span")) and any(isinstance(v, str) and
                                _norm(ev["verbatim_span"]) in _norm(v) for v in values):
                            ev["source_ref"] = path
                            ev["sha256"] = hashlib.sha256(self.read(path)).hexdigest()
                            return ev
        return ev


@lru_cache(maxsize=2)
def _committed_records(root, revision):
    records = CommittedRecords(root)
    if records.revision != revision:
        raise ValueError("HEAD changed while opening explanation evidence")
    return records


def committed_records(root):
    """Share immutable HEAD evidence across topics; a new HEAD gets a new reader."""
    root = str(Path(root).resolve())
    revision = subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip()
    return _committed_records(root, revision)


def held_bytes(sha256, *, root=None):
    return CommittedRecords(root or Path(__file__).resolve().parents[1]).held_bytes(sha256)


def _same_value(left, right):
    """Compare the actual selected tuple, not just a trial identity."""
    aliases = (("events_t", "deaths_t", "ai"), ("n_t", "n1i"),
               ("events_c", "deaths_c", "ci"), ("n_c", "n2i"),
               ("effect",), ("lower", "ci_low"), ("upper", "ci_high"))
    def value(row, keys):
        v = next((row[k] for k in keys if row.get(k) is not None), None)
        try:
            return float(v) if v is not None else None
        except (TypeError, ValueError):
            return v
    # Count rows can also carry a redundant meta effect/CI: compare the counts.
    if left.get("mean_t") is not None:
        aliases = (("mean_t", "mean1"), ("sd_t", "sd1"), ("n_t", "nc1"),
                   ("mean_c", "mean2"), ("sd_c", "sd2"), ("n_c", "nc2"))
        return all(value(left, k) is not None and value(left, k) == value(right, k) for k in aliases)
    keys = aliases[:4] if all(value(left, k) is not None for k in aliases[:4]) else aliases[4:]
    return all(value(left, k) is not None for k in keys) and all(value(left, k) == value(right, k) for k in keys)


def _primary(trial, store, slug=None, primary_rows=()):
    """Only structured own-source provenance; comparator-row provenance is excluded."""
    from scripts.g1_tracker import route_group
    if route_group(trial.get("route")) != "PRIMARY":
        return None
    missing_primary = None
    for key in ("primary_provenance", "confirm_binding", "acquired", "sweep"):
        record = trial.get(key) or {}
        if key == "confirm_binding" and record.get("admitted") is not True:
            continue
        if key == "sweep":
            record = record.get("basis") or {}
        if not isinstance(record, dict):
            continue
        source = record.get("source_ref") or record.get("source")
        sha = record.get("sha256") or record.get("source_sha256") or record.get("text_sha256")
        verifier = record.get("verified_by") or record.get("record_id")
        if key == "sweep" and trial.get("route") == "SWEEP_AACT_PRIMARY":
            snapshot = record.get("snapshot") or {}
            if all(record.get(k) for k in ("nct", "outcome", "guard")) and snapshot.get("id"):
                source = f"{snapshot['id']} {record['nct']} outcome {record['outcome']}"
                sha = snapshot.get("digest")
                verifier = "scripts/g1_two_source_sweep.py:aact_single_primary"
        if key == "acquired":
            hashes = re.findall(r"(?:text |full text )?sha256 ([0-9a-f]{64})(?![0-9a-f])", str(source or ""))
            sha = sha or (hashes[-1] if hashes else None)
            verifier = verifier or ("scripts/g1_trial_acquire.py:ADMITTED" if trial.get("matched_by") == "ACQUIRED_PRIMARY" else None)
            if not sha and record.get("record_id") and hasattr(store, "record_digest"):
                call = store.record_digest(record["record_id"])
                if call:
                    source = f"{source}; recorded read {call[0]}"
                    sha = call[1]
        if key == "confirm_binding" and record.get("admitted"):
            verifier = "scripts/g1_tracker.py:apply_confirm_bindings"
        if source and not sha:
            body = store.read(source)
            if body is not None:
                sha = hashlib.sha256(body).hexdigest()
        if source and sha and verifier:
            return dict(source_ref=source, sha256=sha, verified_by=verifier)
    if not slug or not hasattr(store, "source_document"):
        return None
    # A committed extraction record can carry the value even when report bytes
    # cannot be retained. Require identity AND the current tuple to match it.
    selected = trial.get("our_value") or {}
    for row in primary_rows:
        if trial.get("in_our_pool") and row.get("id") == trial.get("family"):
            from scripts.g1_tracker import our_value_from_row
            selected = our_value_from_row(row) or selected
            break
    path = f"docs/reviews/{slug}/review.json"
    review = store.json(path)
    for outcome in review.get("outcomes", []):
        if not outcome.get("primary"):
            continue
        for row in outcome.get("trials", []):
            if (row.get("id") != trial.get("family") or not trial.get("in_our_pool")
                    or not _same_value(selected, row)):
                continue
            admission = row.get("served_pool_admission") or {}
            if (row.get("verified") == "verified" and _nonempty(row.get("source"))
                    and _nonempty(row.get("verify_basis")) and
                    (admission.get("route") or row.get("provenance") in
                     ("fulltext_verified", "pmc_fulltext", "pmc_fulltext_effect"))):
                body = store.read(path)
                admission_basis = str(admission.get("basis") or "")
                calls = re.findall(r"mc-[0-9a-f]{32}", admission_basis)
                if calls and any(not store.record_digest(rid) for rid in calls):
                    continue
                source_ids = re.findall(r"NCT\d+|outcome \d+", admission_basis)
                if body is not None:
                    return dict(source_ref=f"{row['id']}; {' '.join(source_ids)}; {path}#primary trial {row['id']}",
                                sha256=hashlib.sha256(body).hexdigest(),
                                sha256_kind="recorded_extraction",
                                verified_by=("served_pool_admission:" + admission["route"] if admission.get("route")
                                             else "harness.verify:" + row["provenance"]) + "; " + row["verify_basis"])
    basis = str(trial.get("basis") or "") + " " + str((trial.get("our_value") or {}).get("source") or "")
    match = re.search(r"our held-source pool (PMID \d+|NCT\d+) \(([a-z_]+)\)", basis)
    if match and trial.get("in_our_pool"):
        ref, provenance = match.groups()
        kind = ("ctgov_results" if provenance == "ctgov_results" else "fulltext"
                if provenance in ("pmc_fulltext", "pmc_fulltext_effect", "fulltext_verified") else "abstract")
        # These are the existing extractor/verification routes, not inferred from the comparator.
        from harness.provenance_class import EXTRACTOR_PROV
        if provenance in EXTRACTOR_PROV | {"fulltext_verified", "abstract_verified"}:
            doc = store.source_document(slug, ref.replace("PMID ", ""), kind)
            if doc:
                return dict(source_ref=doc[0], sha256=doc[1], verified_by=f"harness.extract:{provenance}; harness.verify")
            if kind == "fulltext":
                identifier = ref.replace("PMID ", "")
                missing_primary = dict(missing_evidence=f"MATCHED missing committed fulltext: outputs/k_gap/_ft/{identifier}.txt; "
                            f"no committed fulltext_by_pmid[{identifier}] in cache/{slug}/records.json, "
                            f"cache/{slug}/comparator_records.json or outputs/k_gap/member_records.json")
    for row in store.json(f"registry/secondary_meta/{slug}.json").get("rows", []):
        verification = row.get("verification") or {}
        if (row.get("family_id") == trial.get("family") and row.get("state") == "PRIMARY_VERIFIED"
                and verification.get("route") == "PRIMARY_TEXT" and _same_value(trial.get("our_value") or {}, row)):
            source = verification.get("source") or ""
            m = re.fullmatch(r"PMID (\d+) abstract", source)
            if m and _nonempty(verification.get("span")):
                ev = store.evidence(dict(pmid=m[1], span=dict(field="abstract", text=verification["span"])), slug)
                if ev.get("sha256"):
                    return dict(source_ref=ev["source_ref"] + f" (PMID {m[1]})", sha256=ev["sha256"],
                                verified_by="harness.secondary_meta:PRIMARY_TEXT:TYPED_MATCH")
    for reading in trial.get("readings") or []:
        if not _same_value(trial.get("our_value") or {}, reading.get("values") or {}):
            continue
        for src in reading.get("sources") or []:
            source = src.get("source") or ""
            m = re.match(r"TEXT PMID (\d+)", source)
            if not m:
                continue
            pmid = m[1]
            if "VERIFIED_NOT_HELD" in source:
                path = "g1/data/vnh_reads.json"
                rec = store.json(path).get(pmid, {})
                if rec.get("state") != "VERIFIED_NOT_HELD" or trial["label"] not in rec.get("bound_labels", []):
                    continue
                for candidate in rec.get("candidates", []):
                    if (candidate.get("label") == trial["label"] and candidate.get("span") == src.get("span")
                            and _same_value(trial["our_value"], candidate)):
                        return dict(source_ref=f"PMID {pmid}; {path}#{pmid}",
                                    sha256=hashlib.sha256(store.read(path)).hexdigest(), sha256_kind="recorded_read",
                                    verified_by="g1.tocilizumab:vnh_candidates:" + str(candidate.get("extractor")))
            elif _nonempty(src.get("span")):
                doc = store.source_document(slug, pmid, "fulltext")
                if doc:
                    return dict(source_ref=doc[0], sha256=doc[1], verified_by="g1.tocilizumab:assess")
    return missing_primary


def attach_explanations(topic, *, build_date, records, primary_rows=()):
    """Add explanations and totals; existing tracker fields are never rewritten."""
    slug = topic["slug"]
    decisions = records.json("registry/g1_decisions.json")
    excluded = records.json("registry/g1_decision_named_divergences.json").get("entries", [])
    rulings = records.json("registry/g1_regulatory_bindings.json")
    logs = records.json(f"registry/g1_search_log/{slug}.json")
    dec = {d["id"]: d for d in decisions.get("decisions", [])}
    for trial in topic["trials"]:
        label = trial["label"]
        candidates = []
        differences = list(trial.get("named_differences") or [])
        if trial.get("scope_difference"):
            differences.append(trial["scope_difference"])
        differences += [d for d in topic.get("named_differences", []) if d.get("trial") == label]
        for d in differences:
            candidates.append(dict(reason_code=reason_code(d),
                                   detail=d.get("detail") or d.get("reason") or d.get("protocol_rule") or d.get("screen_reason"),
                                   evidence=records.evidence(d, slug),
                                   decided_by=d.get("decided_by") or d.get("decided") or d.get("rule_id") or d.get("gate")))
        for e in excluded:
            if e.get("slug") == slug and str(e.get("trial", "")).casefold() == label.casefold():
                decision = dec.get(e.get("decision"), {})
                d = dict(e, span={"text": decision.get("rule"), "source": "registry/g1_decisions.json"})
                candidates.append(dict(reason_code="DECISION_EXCLUDED", detail=e.get("detail"),
                                       evidence=records.evidence(d, slug),
                                       decided_by=e.get("decision") if (e.get("signed") or {}).get("state") == "SEEN_AND_SIGNED" else None))
        for key, ruling in rulings.items():
            parts = key.split("|")
            if len(parts) == 3 and parts[:2] == [slug, label] and ruling.get("decision") == "NOT_BOUND":
                d = dict(ruling, sha256=parts[2], source=ruling.get("url"))
                candidates.append(dict(reason_code=reason_code(d), detail=ruling.get("reason"),
                                       evidence=records.evidence(d, slug),
                                       decided_by=" / ".join(ruling[k] for k in ("ruled_by", "ruled_on"))
                                       if all(_nonempty(ruling.get(k)) for k in ("ruled_by", "ruled_on")) else None))
        log = (logs.get("trials") or {}).get(label) if logs.get("slug") == slug else None
        if log is not None and "unreachable" not in log:
            log = deepcopy(log)
            applicable = required_sources(log.get("identifiers") or {})
            log["unreachable"] = [{k: v for k, v in item.items() if k != "state"}
                                  for item in source_states(_searched(log)) if item["source"] in applicable]
        trial["g1_explanation"] = build_explanation(trial, build_date=build_date, held_bytes=records.held_bytes,
                                                   decisions=decisions, search_log=log, divergences=candidates,
                                                   primary=_primary(trial, records, slug, primary_rows))
        errors = validate_explanation(trial["g1_explanation"], trial, build_date=build_date,
                                      held_bytes=records.held_bytes, decisions=decisions,
                                      identifiers=(log or {}).get("identifiers"))
        if errors:
            raise ValueError(f"G1 explanation refused for {label}: {'; '.join(errors)}")
    topic["matched"] = sum(t["g1_explanation"]["state"] == "MATCHED" for t in topic["trials"])
    topic["explained"] = sum(t["g1_explanation"]["state"] != "UNEXPLAINED" for t in topic["trials"])
    topic["explained_all"] = topic["explained"]
    topic["n_no_open_source_with_unreachable"] = sum(
        t["g1_explanation"]["state"] == "NO_OPEN_SOURCE" and bool(t["g1_explanation"].get("unreachable"))
        for t in topic["trials"])
    topic["explained_without_unreachable"] = topic["explained_all"] - topic["n_no_open_source_with_unreachable"]
    topic["unexplained_trials"] = [t["label"] for t in topic["trials"] if t["g1_explanation"]["state"] == "UNEXPLAINED"]
    return topic
