"""Replay recorded dual readings with the current engine, without model calls.

Requires ROBGRADE_LOCAL_FT=1 and ROBGRADE_DEV_OPEN_CC=1, matching the
reproducibility audit. Frozen objects are read only for comparison.
"""
from __future__ import annotations

import os
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import rob2_dual as rd  # noqa: E402


def redact_remaining_closed_text(obj, item):
    """Extend the frozen answer redaction to conflicts and other copied text.

    Inspect whole string values without a minimum length. Schema identifiers and
    machine decisions are not quotations; source-linked quotations always follow
    their own licence, while unattributed text is checked against held sources.
    """
    sources = item.get("sources", [])
    by_id = {s["id"]: s for s in sources}
    closed = [s for s in sources if s["kind"] == "fulltext"
              and not str(s.get("licence") or "").startswith("CC")]
    if not closed:
        return
    def normalise(text):
        return " ".join(text.split())

    open_texts = [normalise(s.get("text") or "") for s in sources if s not in closed]
    closed_texts = {s["id"]: normalise(s.get("text") or "") for s in closed}
    short_notice = {"why": "a short closed span was redacted"}
    metadata_keys = {"answer", "question", "qid", "judgement", "how", "kind",
                     "source_ref", "source_id", "source_sha256", "sha256", "id",
                     "trial", "nct", "outcome", "family", "licence", "domain", "if_ni_resolved_favourably"}
    machine_containers = {"disagreements", "answer_provenance", "missing_domains",
                          "ni_questions", "decisive_ni_questions", "ni_driven_domains"}
    changed = False

    def source_for(text, source, key):
        if not text or key in metadata_keys or key.endswith("_sha256"):
            return None
        normal = normalise(text)
        if not normal:
            return None
        if source is not None:
            if source not in closed:
                return None
            if key in ("span", "quote") or normal in closed_texts[source["id"]]:
                return source
        # Unattributed text also present in an open source stays published: open text is publishable.
        if not any(normal in t for t in open_texts):
            return next((s for s in closed if normal in closed_texts[s["id"]]), None)
        return None

    def metadata(text, source):
        # Below 20 characters, publish only a notice: no span hash, offset, or length.
        if len(normalise(text)) < 20:
            return dict(short_notice)
        result = {"why": "the source text is not CC-licensed: the span is not published",
                  "span_sha256": rd.rt.sha(text)}
        match = re.search(r"\s+".join(re.escape(part) for part in text.split()), source["text"])
        if match:
            result.update(start=match.start(), length=match.end() - match.start())
        return result

    def walk(value, inherited=None):
        nonlocal changed
        if isinstance(value, dict):
            source = by_id.get(value.get("source_ref") or value.get("source_id"), inherited)
            for key, child in list(value.items()):
                if key.endswith("_redacted"):
                    # Frozen metadata without a usable length stays unchanged, even with span_sha256.
                    if isinstance(child, dict) and isinstance(child.get("length"), int):
                        length = child["length"]
                        if source is not None and isinstance(child.get("start"), int):
                            start = child["start"]
                            length = len(normalise(source["text"][start:start + length]))
                        if length < 20:
                            value[key] = dict(short_notice)
                            changed = True
                    continue
                if key in machine_containers:
                    continue
                if isinstance(child, str):
                    found = source_for(child, source, key)
                    if found:
                        value[key] = None
                        value[key + "_redacted"] = metadata(child, found)
                        if key != "span" and "span_sha256" in value[key + "_redacted"]:
                            value[key + "_redacted"]["source_sha256"] = found["sha256"]
                        changed = True
                else:
                    walk(child, source)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                if isinstance(child, str):
                    found = source_for(child, inherited, "")
                    if found:
                        value[i] = {"span": None, "span_redacted": metadata(child, found),
                                    "source_ref": found["id"], "source_sha256": found["sha256"]}
                        changed = True
                else:
                    walk(child, inherited)

    walk(obj)
    if changed:
        obj.pop("sha256", None)
        obj["sha256"] = hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def main():
    for setting in ("ROBGRADE_LOCAL_FT", "ROBGRADE_DEV_OPEN_CC"):
        if os.environ.get(setting) != "1":
            raise SystemExit(f"{setting} must be exactly '1'")

    runs = rd._j(ROOT / "registry/model_proposals/rob2_dual_runs.json")
    groups = {}
    for key in sorted(runs):
        slug, pmid, outcome = key.split("::")
        if not slug or Path(slug).name != slug or "/" in slug or "\\" in slug or ":" in slug or slug in (".", ".."):
            raise ValueError(f"Invalid manifest slug: {slug!r}")
        if not pmid.isdecimal() or not outcome:
            raise ValueError(f"Invalid manifest key: {key!r}")
        group = groups.setdefault(slug, {"outcome": outcome, "pmids": []})
        if group["outcome"] != outcome:
            raise ValueError(f"Multiple manifest outcomes for {slug}")
        group["pmids"].append(pmid)

    rd.prefetch_registry([(slug, group["pmids"]) for slug, group in groups.items()])
    reproduced = total = 0
    for slug, group in groups.items():
        items = rd.items(slug, group["pmids"])
        expected = {f"{slug}::{pmid}::{group['outcome']}" for pmid in group["pmids"]}
        if len(items) != len(expected) or {item["key"] for item in items} != expected:
            raise ValueError(f"Current items do not match manifest identities/outcome for {slug}")
        committed = []
        frozen = ROOT / "outputs/robgrade/rob2"
        for directory in (frozen, frozen / "dev"):
            path = directory / f"{slug}.json"
            if path.is_file():
                committed.append(rd._j(path))
        trials = {}
        for item in items:
            obj, _ = rd.process(item, runs, False, {})
            rd.redact_closed_spans(obj, item)
            redact_remaining_closed_text(obj, item)
            pmid = item["pmid"]
            equal = any(data.get("outcome") == item["outcome"] and
                        data.get("trials", {}).get(pmid) == obj for data in committed)
            print(f"{slug} {pmid} equals committed: {equal}", flush=True)
            reproduced += equal
            total += 1
            trials[pmid] = obj
        rd._save(ROOT / "outputs/robgrade/rob2_current" / f"{slug}.json", {
            "slug": slug, "family": rd.rf.FAMILY, "outcome": group["outcome"],
            "trials": trials,
            "generated_by": "scripts/rob2_current.py (replay, no model call)",
        })
    print(f"reproduced {reproduced} of {total}", flush=True)


if __name__ == "__main__":
    main()
