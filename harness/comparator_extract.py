"""Offline, conservative comparator extraction. Unknowns are never pool inputs.

PARSED means a lexical binding, not a judgement of clinical equivalence. Flattened
tables without recoverable cell boundaries generate proposals for adjudication.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import TypedDict, Any

ROOT = Path(__file__).resolve().parents[1]
NUM = r"-?\d+(?:[.·]\d+)?"
EFFECT = re.compile(rf"\b(HR|RR|OR|IRR|SMD|MD)\s*[=:,]?\s*({NUM})\s*[,;]?\s*[\[(]\s*(?:95\s*%\s*CI\s*[:,]?\s*)?({NUM})\s*(?:to|[-–−])\s*({NUM})\s*[\])]", re.I)
AUTHOR = r"[A-ZÀ-ÖØ-Þ](?:[a-zà-öø-ÿ]+|[’'‐-][A-Za-zÀ-ÿ]+)+(?:\s+et\s+al\.?)?\s*[,;(]?\s*(?:\[\s*\d+\s*\]|\(\s*\d+\s*\))?\s*[,;]?\s*(?:19|20)\d{2}"
ACRONYM = r"[A-Z][A-Z0-9]*(?:[-‐–][A-Za-z0-9]+)+|[A-Z]{3,}(?:\s+\d+)?"
LABEL = re.compile(rf"^(?P<label>{AUTHOR}|{ACRONYM})\b")


class Fact(TypedDict):
    status: str
    value: Any
    span: str


class Comparator(TypedDict):
    slug: str
    status: str
    primary_outcome: str
    trial_set: list[dict]
    pooled: dict[str, Fact]
    proposals: list[dict]
    membership_complete: bool


def flat(text):
    return re.sub(r"\s+", " ", text).strip()


def fact(value=None, span="") -> Fact:
    return {"status": "PARSED" if value is not None else "UNPARSED", "value": value, "span": flat(span)}


def norm(text):
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def _number(text):
    return float(text.replace("·", "."))


def _fields(span):
    fields = {k: fact(span=span) for k in ("registration", "pmid", "n", "n1", "n2", "events1", "events2", "effect", "ci_low", "ci_high", "measure", "timepoint", "population")}
    patterns = {
        "registration": r"\b(NCT\d{8})\b", "pmid": r"\bPMID\s*[:=]?\s*(\d{6,9})\b",
        "n": r"\bn\s*=\s*(\d[\d,]*)\b", "n1": r"\bn1\s*=\s*(\d[\d,]*)\b",
        "n2": r"\bn2\s*=\s*(\d[\d,]*)\b", "events1": r"\bevents1\s*=\s*(\d[\d,]*)\b",
        "events2": r"\bevents2\s*=\s*(\d[\d,]*)\b",
        "timepoint": r"\b(?:timepoint\s*[:=]\s*)?((?:\d+(?:\.\d+)?)[ -](?:days?|weeks?|months?|years?))\b",
        "population": r"\b(intention.to.treat|per.protocol|modified intention.to.treat)\b",
    }
    for key, pat in patterns.items():
        hits = list(re.finditer(pat, span, re.I))
        if len(hits) == 1:
            value = hits[0][1]
            if key in {"n", "n1", "n2", "events1", "events2"}:
                value = int(value.replace(",", ""))
            fields[key] = fact(value, hits[0][0])
    hits = list(EFFECT.finditer(span))
    if len(hits) == 1:
        m = hits[0]
        values = list(map(_number, m.group(2, 3, 4)))
        if values[1] <= values[0] <= values[2] and (m[1].upper() in {"MD", "SMD"} or min(values) > 0):
            for key, value in zip(("effect", "ci_low", "ci_high"), values):
                fields[key] = fact(value, m[0])
            fields["measure"] = fact(m[1].upper(), m[0])
    if re.search(r"\b(?:relayed|investigator[- ]supplied|personal communication)\b", span, re.I):
        for key in ("n", "n1", "n2", "events1", "events2", "effect", "ci_low", "ci_high"):
            fields[key]["status"] = "RELAYED"
    return fields


def parse_text(text: str, topic: dict) -> Comparator:
    """Parse supplied held text; public disk entry point verifies its hash first."""
    primary = topic["primary_outcome"]["name"]
    out = Comparator(slug=topic.get("slug", ""), status="PARSED", primary_outcome=primary,
                     trial_set=[], pooled={k: fact() for k in ("k", "effect", "ci_low", "ci_high", "measure", "model", "i2", "tau2")},
                     proposals=[], membership_complete=False)
    def proposal(field, span, why):
        item = {"field": field, "candidate_span": flat(span), "why_regex_failed": why, "status": "PROPOSAL"}
        if item not in out["proposals"]:
            out["proposals"].append(item)

    # Explicit headings bind only their own rows; never propagate across sections.
    outcome = None
    mode = None
    pooled_rows = 0
    recognized = set()
    for raw in text.splitlines():
        line = flat(raw)
        heading = re.fullmatch(r"(?:Outcome|Forest plot)\s*:\s*(.+)", line, re.I)
        if heading:
            outcome = heading[1]
            mode = "forest"
            continue
        if re.fullmatch(r"(?:Table\s+\d+[.:]?\s*)?Included[- ]studies(?:\s+table)?\s*:?", line, re.I):
            mode, outcome = "table", None
            continue
        if not line:
            mode, outcome = None, None
            continue
        cells = [x.strip() for x in re.split(r"\||\t", raw) if x.strip()]
        if mode and len(cells) > 1 and LABEL.fullmatch(cells[0]):
            row_outcome = next((x.split(":", 1)[1].strip() for x in cells if re.match(r"outcome:", x, re.I)), outcome)
            row = {"label": cells[0], "span": line, "outcome": fact(row_outcome, line), **_fields(line)}
            out["trial_set"].append(row)
            recognized.add(line)
        elif mode and re.match(r"(?:Pooled|Total)\b", line, re.I) and norm(outcome) == norm(primary):
            pooled_rows += 1
            values = _fields(line)
            for key in ("effect", "ci_low", "ci_high", "measure"):
                out["pooled"][key] = values[key]
            for key, pat in {"k": r"\bk\s*=\s*(\d+)", "i2": rf"\bI\s*[²2]\s*=\s*({NUM})", "tau2": rf"\btau\s*[²2]\s*=\s*({NUM})", "model": r"\b((?:random|fixed|common)[ -]effects?)\b"}.items():
                m = re.search(pat, line, re.I)
                if m:
                    out["pooled"][key] = fact(m[1] if key == "model" else int(m[1]) if key == "k" else _number(m[1]), line)
            recognized.add(line)
        elif mode and len(line) < 150 and re.match(r"(?:Discussion|References|Methods|Results|Secondary outcome)\b", line, re.I):
            mode, outcome = None, None

    # Recover labels, but no guessed column values, in flattened included-study
    # tables. A bounded table requires a header AND a subsequent section marker.
    flattext = flat(text)
    tables = re.finditer(r"\bTable\s+\d+[.:]?\s+(?:Baseline characteristics|Characteristics|Summary|Patient baseline characteristics|Baseline demographics)[^.]{0,150}?\.?\s+(?=Study\b|Studies\b|Trial\b|First author\b|[A-Z][A-Z]+[-‐])", flattext)
    for header in tables:
        tail = flattext[header.end():]
        stop = re.search(r"\b(?:Fig(?:ure)?\.?\s+\d+|Table\s+\d+|\d+\.\d+\s+[A-Z]|Outcomes\b|Discussion\b|Abbreviations:)", tail)
        block = tail[:stop.start()] if stop else tail[:4000]
        candidates = list(re.finditer(rf"\b(?:{AUTHOR})\b|\b(?:{ACRONYM})\s*\(\s*n\s*=\s*\d[\d,]*\s*\)", block))
        for m in candidates:
            span = m[0]
            label = re.sub(r"\s*\(\s*n\s*=.*", "", span)
            if not any(norm(r["label"]) == norm(label) for r in out["trial_set"]):
                out["trial_set"].append({"label": label, "span": flat(span), "outcome": fact(span=header[0]), **_fields(span)})
        proposal("trial_set", header[0] + block, "Flattened table: outcome and column-to-trial binding not proven; recovered labels only" )

    # Explicit enumeration, not arbitrary acronyms mentioned in discussion.
    for m in re.finditer(r"(?:studies|trials) included\s*(?:were|:)\s*([^.;\n]+)", text, re.I):
        items = re.split(r",\s*|\s+and\s+", m[1])
        if items and all(LABEL.fullmatch(x.strip()) for x in items):
            for label in items:
                if not any(norm(t["label"]) == norm(label) for t in out["trial_set"]):
                    out["trial_set"].append({"label": label.strip(), "span": flat(m[0]), "outcome": fact(span=m[0]), **_fields(label)})
        else:
            proposal("trial_set", m[0], "Included-studies enumeration has unresolved label boundaries")

    # All source sentences with effect/table/inclusion evidence remain available
    # for replay when the strict grammar cannot assign their primary endpoint.
    pooled_candidates = []
    for segment in re.split(r"(?<=[.!?])\s+(?=[A-Z])|\n", text):
        if (re.search(r"(?<!\w)" + re.escape(primary) + r"(?!\w)", segment, re.I)
                and len(list(EFFECT.finditer(segment))) == 1
                and re.search(r"\b(?:pooled|meta-analysis|overall analysis)\b", segment, re.I)
                and not re.search(r"\b(?:subgroup|sensitivity|secondary)\b", segment, re.I)):
            others = topic.get("secondary_outcomes", []) + topic.get("harm_outcomes", [])
            if not any(re.search(re.escape(o["name"]), segment, re.I) for o in others if o.get("name")):
                pooled_candidates.append(segment)
        if re.search(r"\b(?:Table\s+\d+|forest plot|included|pooled)\b", segment, re.I) or EFFECT.search(segment):
            if flat(segment) not in recognized:
                proposal("primary_binding", segment, "No unambiguous row/outcome grammar; numerical proximity is not endpoint evidence")
    if len(pooled_candidates) == 1 and pooled_rows == 0:
        segment = pooled_candidates[0]
        fields = _fields(segment)
        for key in ("effect", "ci_low", "ci_high", "measure"):
            out["pooled"][key] = fields[key]
        for key, pat in {"k": r"\b(\d+)\s+(?:trials|studies|RCTs)\b", "i2": rf"\bI\s*[²2]\s*=\s*({NUM})", "tau2": rf"\btau\s*[²2]\s*=\s*({NUM})", "model": r"\b((?:random|fixed|common)[ -]effects?)\b"}.items():
            hits = list(re.finditer(pat, segment, re.I))
            if len(hits) == 1:
                m = hits[0]
                out["pooled"][key] = fact(m[1] if key == "model" else int(m[1]) if key == "k" else _number(m[1]), segment)
    if pooled_rows > 1 or (pooled_rows == 0 and len(pooled_candidates) > 1):
        out["pooled"] = {k: fact(span=text) for k in out["pooled"]}
        proposal("pooled", text, "Multiple primary pooled estimates: model/timepoint binding ambiguous")
    for key, field in out["pooled"].items():
        if field["status"] == "UNPARSED":
            field["span"] = flat(text)
            proposal("pooled." + key, text, "No unique primary-outcome pooled field binding")
    primary_rows = [r for r in out["trial_set"] if norm(r["outcome"]["value"]) == norm(primary)]
    k = out["pooled"]["k"]["value"]
    out["membership_complete"] = k is not None and k > 0 and len(primary_rows) == k and len({norm(r["label"]) for r in primary_rows}) == k
    for row in out["trial_set"]:
        missing = [k for k, v in row.items() if isinstance(v, dict) and v.get("status") == "UNPARSED"]
        if missing:
            proposal(",".join(missing), row["span"], "Fields not explicitly printed/bound in recoverable row")
    return out


def extract(slug: str, root=ROOT) -> Comparator:
    root = Path(root).resolve()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ValueError("REFUSED_INVALID_SLUG: " + slug)
    topic = json.loads((root / "topics" / (slug + ".json")).read_text(encoding="utf-8"))
    panel_path = root / "cache" / slug / "comparators.json"
    if not panel_path.exists():
        raise ValueError("REFUSED_MISSING_COMPARATOR: " + slug)
    panel = json.loads(panel_path.read_text(encoding="utf-8"))
    if len(panel) != 1:
        pmid = str(topic.get("comparator_pmid") or "")
        panel = [c for c in panel if pmid and (str(c.get("id")) == pmid or re.search(r"\bPMID\s+" + re.escape(pmid) + r"\b", c.get("citation", "")))]
    if len(panel) != 1:
        raise ValueError("REFUSED_AMBIGUOUS_COMPARATOR: " + slug)
    c = panel[0]
    if not c.get("held"):
        raise ValueError("REFUSED_DOCUMENT_NOT_HELD: " + slug)
    path = (root / c.get("document_ref", "")).resolve()
    if not path.is_relative_to(root / "cache") or not path.is_file():
        raise ValueError("REFUSED_DOCUMENT_PATH: " + slug)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != c.get("document_sha256"):
        raise ValueError("REFUSED_SHA256_MISMATCH: " + slug)
    result = parse_text(raw.decode("utf-8"), topic)
    result["document_ref"] = c["document_ref"]
    result["document_sha256"] = c["document_sha256"]
    return result
