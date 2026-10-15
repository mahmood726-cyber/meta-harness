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
import hashlib
import json
from pathlib import Path
import re
import subprocess

from scripts.g1_explanation_vocab import STATES, REASON_CODES, SOURCES, STEPS, ACCESS_OUTCOMES, FRESH_DAYS


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
        if not _nonempty(ev.get("source_ref")):
            errors.append("DIVERGENT_NAMED missing source_ref")
        if not _nonempty(ev.get("verbatim_span")):
            return errors + ["DIVERGENT_NAMED span not in held bytes (missing verbatim_span)"]
        if not _sha(ev.get("sha256")):
            return errors + ["DIVERGENT_NAMED missing or invalid sha256"]
        body = held_bytes(ev["sha256"])
        if body is None:
            return errors + ["DIVERGENT_NAMED held bytes not committed"]
        if not isinstance(body, bytes) or hashlib.sha256(body).hexdigest() != ev["sha256"]:
            return errors + ["DIVERGENT_NAMED held bytes hash mismatch"]
        try:
            text = _document_text(body)
        except UnicodeDecodeError:
            return errors + ["DIVERGENT_NAMED held bytes are not UTF-8 text"]
        span = ev.get("verbatim_span")
        if not _nonempty(span) or _norm(span) not in _norm(text):
            errors.append("DIVERGENT_NAMED span not in held bytes")
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
    fresh, seen, gated = set(), set(), {}
    for i, rec in enumerate(searched):
        if not isinstance(rec, dict):
            errors.append(f"searched[{i}] invalid record")
            continue
        source, step = rec.get("source"), rec.get("step_reached")
        if source not in SOURCES or step not in (*STEPS, *ACCESS_OUTCOMES):
            errors.append(f"searched[{i}] unknown source or step_reached")
            continue
        seen.add(source)
        if not all(_nonempty(rec.get(k)) for k in ("identifier_or_query", "outcome")):
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
            if step in STEPS:
                fresh.add(source)
            else:
                gated.setdefault(source, []).append(f"{step}: {rec.get('outcome')}")
    for source in required_sources(identifiers):
        if source not in fresh:
            if source in gated:
                errors.append(f"required source {source} gated: " + "; ".join(gated[source]))
            else:
                errors.append(f"required source {source} " + ("stale" if source in seen else "missing"))
    return errors


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
    for candidate in divergences:
        entry = dict(candidate, state="DIVERGENT_NAMED")
        bad = validate_explanation(entry, trial, **ctx)
        if not bad:
            if errors:
                entry["note"] = "; ".join(errors)
            return entry
        errors.extend(bad)
    if search_log is not None:
        entry = {"state": "NO_OPEN_SOURCE", "searched": deepcopy(search_log.get("searched")),
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
        body = self.read(path)
        return json.loads(body) if body is not None else {}

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
            for path in sorted(self.paths):
                if (path.startswith(("cache/", "outputs/k_gap/_ft/", "outputs/k_gap/_upw/",
                                     "outputs/k_gap/_reg/", "outputs/k_gap/_ctgov/"))
                        or path == "outputs/k_gap/member_records.json") and path.endswith((".txt", ".json", ".xml")):
                    self.read(path)
            self.scanned = True
        return self.by_sha.get(sha256)

    def evidence(self, record, slug):
        ev = deepcopy(record.get("evidence") or {})
        span = record.get("span") or {}
        if isinstance(span, str):
            span = {"text": span}
        ev.setdefault("verbatim_span", span.get("text") or record.get("quote"))
        ev.setdefault("source_ref", span.get("source") or record.get("span_source") or record.get("source"))
        ev.setdefault("sha256", span.get("fulltext_sha256") or record.get("sha256") or record.get("source_sha256"))
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


def held_bytes(sha256, *, root=None):
    return CommittedRecords(root or Path(__file__).resolve().parents[1]).held_bytes(sha256)


def _primary(trial, store):
    """Only structured own-source provenance; comparator-row provenance is excluded."""
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
        if key == "confirm_binding" and record.get("admitted"):
            verifier = "scripts/g1_tracker.py:apply_confirm_bindings"
        if source and not sha:
            body = store.read(source)
            if body is not None:
                sha = hashlib.sha256(body).hexdigest()
        if source and sha and verifier:
            return dict(source_ref=source, sha256=sha, verified_by=verifier)
    return None


def attach_explanations(topic, *, build_date, records):
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
        trial["g1_explanation"] = build_explanation(trial, build_date=build_date, held_bytes=records.held_bytes,
                                                   decisions=decisions, search_log=log, divergences=candidates,
                                                   primary=_primary(trial, records))
        errors = validate_explanation(trial["g1_explanation"], trial, build_date=build_date,
                                      held_bytes=records.held_bytes, decisions=decisions,
                                      identifiers=(log or {}).get("identifiers"))
        if errors:
            raise ValueError(f"G1 explanation refused for {label}: {'; '.join(errors)}")
    topic["matched"] = sum(t["g1_explanation"]["state"] == "MATCHED" for t in topic["trials"])
    topic["explained"] = sum(t["g1_explanation"]["state"] != "UNEXPLAINED" for t in topic["trials"])
    topic["unexplained_trials"] = [t["label"] for t in topic["trials"] if t["g1_explanation"]["state"] == "UNEXPLAINED"]
    return topic
