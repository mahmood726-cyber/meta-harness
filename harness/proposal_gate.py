"""Offline lexical verification of recorded model proposals; never pool admission.

Accepted means printed and typed, NOT that a model's clinical scope mapping is
correct. Null fields are unproposed. Provenance is checked against the held panel,
not against a hash supplied solely by the proposer. Optional field_spans narrow
a field to its own evidence inside the item's contiguous span.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ("outcome_as_printed", "timepoint_as_printed", "measure_as_printed")
POOLED = ("k", "effect", "ci_low", "ci_high", "measure")
TRIAL = ("label", "registration", "pmid", "events_1", "n_1", "events_2", "n_2",
         "effect", "ci_low", "ci_high", "measure")
NUM = r"[+−‐-]?(?:\d+(?:[.·]\d+)?|\.\d+)"
MEASURE = r"(?:HR|ORs|OR|RR|IRR|MD|SMD|WMD|mean difference|Mean difference|Odds Ratio)"
CI = rf"(?:95\s*%\s*(?:confidence interval\s*)?(?:\[?CI\]?|C\.I\.)\s*[:,=]?\s*[\[(]?\s*)?({NUM})\s*(?:to|[–−,-])\s*({NUM})"
EFFECT = re.compile(
    rf"(?<!\w)({MEASURE})(?:\s+were)?[\])]?[\s,:=¼]*(?:of\s+)?({NUM})"
    rf"(?:\s*(?:minutes|points|%)\s*)?[\s,;\[(]*{CI}")
BARE_EFFECT = re.compile(rf"(?<![\w.·])({NUM})\s*[\[(]\s*{CI}\s*[\])]")
K = re.compile(r"(?<![\w.+−‐-])([1-9]\d*)\s+(?:(?:randomized|randomised|controlled|clinical|relevant|remaining|pivotal|phase\s+\d+)\s+)*(?:trials|studies|RCTs|CVOTs)\b", re.I)
RELAYED = re.compile(r"\b(?:relayed|investigator[- ]supplied|personal communication|unpublished data supplied)\b", re.I)


def flat(text):
    return re.sub(r"\s+", " ", text).strip()


def number(token):
    return float(token.replace("−", "-").replace("‐", "-").replace("·", "."))


def parse_estimate(span):
    """A unique labelled estimate; or one bare estimate/CI with no invented measure."""
    hits = list(EFFECT.finditer(span))
    if len(hits) == 1:
        m = hits[0]
        return dict(zip(("measure", "effect", "ci_low", "ci_high"),
                        [m[1], *map(number, m.group(2, 3, 4))]))
    if hits:
        return {}
    hits = list(BARE_EFFECT.finditer(span))
    if len(hits) == 1:
        return dict(zip(("effect", "ci_low", "ci_high"), map(number, hits[0].group(1, 2, 3))))
    return {}


def _source(proposal, root):
    slug = proposal.get("slug")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ValueError("REFUSED_INVALID_SLUG")
    topic = json.loads((root / "topics" / (slug + ".json")).read_text(encoding="utf-8"))
    panels = json.loads((root / "cache" / slug / "comparators.json").read_text(encoding="utf-8"))
    pmid = str(proposal.get("comparator_pmid", ""))
    panels = [p for p in panels if str(p.get("id")) == pmid or
              re.search(r"\bPMID\s+" + re.escape(pmid) + r"\b", p.get("citation", ""))]
    if not re.fullmatch(r"\d{6,9}", pmid) or len(panels) != 1 or pmid != str(topic.get("comparator_pmid")):
        raise ValueError("REFUSED_COMPARATOR_IDENTITY")
    panel = panels[0]
    if panel.get("held") is not True:
        raise ValueError("REFUSED_DOCUMENT_NOT_HELD")
    for key in ("document_ref", "document_sha256"):
        if not isinstance(proposal.get(key), str) or proposal[key] != panel.get(key):
            raise ValueError("REFUSED_" + key.upper() + "_MISMATCH")
    path = (root / panel["document_ref"]).resolve()
    if not path.is_relative_to((root / "cache").resolve()) or not path.is_file():
        raise ValueError("REFUSED_DOCUMENT_PATH")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != panel["document_sha256"]:
        raise ValueError("REFUSED_SHA256_MISMATCH")
    text = flat(raw.decode("utf-8"))
    allowed = text
    if path.suffix == ".json":
        records = json.loads(raw).get("records", [])
        rows = [r for r in records if str(r.get("id")) == pmid and r.get("id_type") == "pmid"]
        if len(rows) != 1:
            raise ValueError("REFUSED_COMPARATOR_RECORD_AMBIGUOUS")
        # Both raw-byte text containment and the selected record are required.
        allowed = flat(rows[0].get("abstract", ""))
    return text, allowed, topic


def _schema(p):
    if not isinstance(p, dict):
        return "REFUSED_PROPOSAL_TYPE"
    required = {"slug", "comparator_pmid", "document_ref", "document_sha256", "proposed_by",
                "scope_note", "primary_scope", "pooled", "trials", "not_found"}
    if not required.issubset(p):
        return "REFUSED_MISSING_KEYS:" + ",".join(sorted(required - p.keys()))
    if not all(isinstance(p[k], str) and p[k].strip() for k in
               ("proposed_by", "scope_note", "comparator_pmid")):
        return "REFUSED_METADATA_TYPE"
    if not isinstance(p["not_found"], list) or not all(isinstance(x, str) for x in p["not_found"]):
        return "REFUSED_NOT_FOUND_TYPE"
    if not isinstance(p["trials"], list):
        return "REFUSED_TRIALS_TYPE"
    if p.get("trial_set_scope", "included_studies_only") not in {"selected_outcome", "included_studies_only"}:
        return "REFUSED_TRIAL_SET_SCOPE"
    if type(p.get("trial_set_complete", False)) is not bool:
        return "REFUSED_COMPLETENESS_TYPE"
    for item, fields in [(p["primary_scope"], SCOPE), (p["pooled"], POOLED)] + [(r, TRIAL) for r in p["trials"]]:
        if not isinstance(item, dict) or not set(fields).issubset(item) or not isinstance(item.get("span"), str):
            return "REFUSED_ITEM_SCHEMA"
        allowed = set(fields) | {"span", "field_spans"}
        if set(item) - allowed:
            return "REFUSED_UNKNOWN_ITEM_FIELDS:" + ",".join(sorted(set(item) - allowed))
        fs = item.get("field_spans", {})
        if not isinstance(fs, dict) or set(fs) - set(fields) or not all(isinstance(s, str) for s in fs.values()):
            return "REFUSED_FIELD_SPANS_SCHEMA"
    return None


def _reparse(key, value, span):
    if key in {"effect", "ci_low", "ci_high", "k", "events_1", "n_1", "events_2", "n_2"}:
        if type(value) not in (int, float) or not math.isfinite(value):
            return "REFUSED_NONFINITE_OR_NONNUMERIC"
    if key in {"k", "events_1", "n_1", "events_2", "n_2"}:
        if type(value) is not int or value < (1 if key in {"k", "n_1", "n_2"} else 0):
            return "REFUSED_COUNT_TYPE_OR_RANGE"
        if key == "k":
            hits = [int(m[1]) for m in K.finditer(span)]
        else:
            hits = [int(m[1].replace(",", "")) for m in re.finditer(
                rf"\b{re.escape(key)}\s*[:=]\s*(\d[\d,]*)\b", span)]
            pairs = list(re.finditer(r"\b(\d+)/(\d+)\s+(?:vs\.?|versus)\s+(\d+)/(\d+)\b", span))
            if len(pairs) == 1 and not hits:
                hits = [int(pairs[0][{"events_1": 1, "n_1": 2, "events_2": 3, "n_2": 4}[key]])]
        return None if len(hits) == 1 and hits[0] == value else "REFUSED_NUMBER_ROLE_NOT_IN_OWN_SPAN"
    if key in {"effect", "ci_low", "ci_high"}:
        parsed = parse_estimate(span)
        if parsed.get(key) != value:
            return "REFUSED_NUMBER_ROLE_NOT_IN_OWN_SPAN"
        if not parsed["ci_low"] <= parsed["effect"] <= parsed["ci_high"]:
            return "REFUSED_INTERVAL_ORDER"
        if parsed.get("measure") in {"RR", "OR", "ORs", "HR", "IRR"} and parsed["ci_low"] <= 0:
            return "REFUSED_RATIO_RANGE"
        return None
    if not isinstance(value, str) or not value.strip():
        return "REFUSED_STRING_TYPE"
    # PDF's quarter glyph is a printed equals-sign artifact, not a word suffix.
    boundary_span = span.replace("¼", "=")
    if not re.search(r"(?<!\w)" + re.escape(flat(value)) + r"(?!\w)", boundary_span):
        return "REFUSED_LITERAL_NOT_IN_OWN_SPAN"
    if key == "registration" and not re.fullmatch(r"NCT\d{8}", value):
        return "REFUSED_REGISTRATION_TYPE"
    if key == "pmid" and not re.search(r"\bPMID\s*[:=]?\s*" + re.escape(value) + r"\b", span):
        return "REFUSED_PMID_ROLE"
    if key in {"measure", "measure_as_printed"} and not re.fullmatch(MEASURE, value):
        return "REFUSED_MEASURE_TYPE"
    return None


def verify(proposal, root=ROOT):
    """Return accepted/rejected/non-proposed fields and a sanitized value tree.

    Any document or schema failure rejects the entire proposal. A field failure
    rejects only that field. No unverified value is returned in accepted.
    """
    result = {"status": "rejected", "reason": None, "fields": [], "accepted": None}
    reason = _schema(proposal)
    if reason:
        result["reason"] = reason
        return result
    groups = [("primary_scope", proposal["primary_scope"], SCOPE), ("pooled", proposal["pooled"], POOLED)]
    groups += [(f"trials.{i}", row, TRIAL) for i, row in enumerate(proposal["trials"])]
    try:
        text, allowed, _ = _source(proposal, Path(root).resolve())
    except (ValueError, OSError, UnicodeError, TypeError, KeyError) as exc:
        reason = str(exc)
        if not reason.startswith("REFUSED_"):
            reason = "REFUSED_SOURCE_READ:" + type(exc).__name__
        result["reason"] = reason
        for prefix, item, keys in groups:
            for key in keys:
                if item[key] is not None:
                    result["fields"].append({"path": prefix + "." + key, "status": "rejected", "reason": reason})
        return result
    clean = {"primary_scope": {}, "pooled": {}, "trials": []}
    for prefix, item, keys in groups:
        target = {} if prefix.startswith("trials.") else clean[prefix]
        if prefix.startswith("trials."):
            clean["trials"].append(target)
        for key in keys:
            path = prefix + "." + key
            value = item[key]
            span = flat(item.get("field_spans", {}).get(key, item["span"]))
            parent = flat(item["span"])
            reason = None
            if value is None:
                status = "not_proposed"
            else:
                if not parent or parent not in text or not span or span not in parent:
                    reason = "REFUSED_SPAN_NOT_HELD"
                elif parent not in allowed:
                    reason = "REFUSED_SPAN_OUTSIDE_COMPARATOR_RECORD"
                elif RELAYED.search(parent):
                    reason = "REFUSED_RELAYED_NOT_DATA"
                else:
                    reason = _reparse(key, value, span)
                status = "rejected" if reason else "accepted"
            result["fields"].append({"path": path, "status": status, "reason": reason})
            target[key] = value if status == "accepted" else None
        # Do not assemble one estimate from independently valid but different rows.
        bound = set()
        for key in ("effect", "ci_low", "ci_high"):
            if target.get(key) is not None:
                parsed = parse_estimate(flat(item.get("field_spans", {}).get(key, item["span"])))
                bound.add(tuple(parsed.get(x) for x in ("effect", "ci_low", "ci_high")))
        if len(bound) > 1:
            for key in ("effect", "ci_low", "ci_high"):
                if target.get(key) is not None:
                    target[key] = None
                    field = next(f for f in result["fields"] if f["path"] == prefix + "." + key)
                    field.update(status="rejected", reason="REFUSED_MIXED_ESTIMATE_BINDINGS")
        # Field support alone cannot authorize an impossible arm count.
        if prefix.startswith("trials."):
            for arm in ("1", "2"):
                e, n = target.get("events_" + arm), target.get("n_" + arm)
                if e is not None and n is not None and e > n:
                    for key in ("events_" + arm, "n_" + arm):
                        target[key] = None
                        field = next(f for f in result["fields"] if f["path"] == prefix + "." + key)
                        field.update(status="rejected", reason="REFUSED_EVENTS_EXCEED_N")
    result["accepted"] = clean
    result["status"] = "partial" if any(f["status"] == "rejected" for f in result["fields"]) else "accepted"
    return result


def to_comparator(proposal, root=ROOT):
    """Adapt printed fields and the recorded model's selected-outcome mapping.

    This is an audit of the PROPOSED closest scope, never equivalence certification.
    General included-study inventories keep OUTCOME_UNPARSED. Completeness needs
    a recorded model declaration AND accepted k, all labels and unique identities.
    That remains a proposed set, not a certification of clinical equivalence.
    """
    from .comparator_extract import fact, norm
    from .meta_match import _join
    checked = verify(proposal, root)
    if checked["accepted"] is None:
        raise ValueError(checked["reason"])
    topic = json.loads((Path(root) / "topics" / (proposal["slug"] + ".json")).read_text(encoding="utf-8"))
    clean = checked["accepted"]
    rows = []
    for r in clean["trials"]:
        if r["label"] is None:
            continue
        primary = topic["primary_outcome"]["name"]
        selected = proposal.get("trial_set_scope") == "selected_outcome" and clean["primary_scope"]["outcome_as_printed"] is not None
        row = {"label": r["label"], "outcome": fact(primary if selected else None),
               "timepoint": fact(), "population": fact()}
        for key in TRIAL[1:]:
            row[{"events_1": "events1", "events_2": "events2", "n_1": "n1", "n_2": "n2"}.get(key, key)] = fact(r[key])
        rows.append(row)
    k = clean["pooled"]["k"]
    complete = (proposal.get("trial_set_complete") is True
                and proposal.get("trial_set_scope") == "selected_outcome"
                and clean["primary_scope"]["outcome_as_printed"] is not None
                and k is not None and len(rows) == len(proposal["trials"]) == k
                and len({norm(r["label"]) for r in rows}) == k
                and not any(_join(a, b) for i, a in enumerate(rows) for b in rows[i + 1:]))
    return {"slug": proposal["slug"], "primary_outcome": topic["primary_outcome"]["name"],
            "status": "LEXICALLY_VERIFIED_PROPOSAL", "trial_set": rows,
            "pooled": {k: fact(v) for k, v in clean["pooled"].items()},
            "membership_complete": complete, "scope_note": proposal["scope_note"]}
