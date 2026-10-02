"""Offline endpoint decision support. This module deliberately has no synthesis path.

Identifiers below are source selectors, never numerical research inputs. Census is
an option of this script because the lane permits no separate census filename.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import component_typing, target_endpoint
from harness.trial_family import load_registry

SLUG = "statins-primary-prevention-elderly"
IDS = ("20404379", "42670961", "NCT00468923", "28531241", "NCT04262206")
THREE = {"cardiovascular death", "myocardial infarction", "stroke"}
HOPE = re.compile(r"NCT00468923|\b28385949\b|\bHOPE[\s-]*3\b", re.I)


class DecisionRequired(ValueError):
    pass


def require_no_hope(inputs):
    """Pre-computation guard; never evaluate a study effect or call synthesis."""
    for item in inputs:
        text = json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item)
        if HOPE.search(text):
            raise DecisionRequired("DECISION_REQUIRED_BEFORE_INTERVAL: refused " + HOPE.search(text).group())


def pool(inputs):
    require_no_hope(inputs)
    raise ValueError("POOLING_DISABLED: decision-support lane refuses all synthesis")


def read_json(path):
    if not path.is_file():
        raise ValueError("NOT_HELD: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def typed_definition(text, *, relayed=None):
    # A policy declaration is not an observed endpoint definition.
    if relayed is not None:
        return {"state": "RELAYED", "components": relayed["component_set"],
                "quote": relayed["component_basis"], "untyped": [], "poolable": False}
    typed = component_typing.derive(text)
    if typed is None:
        return {"state": "NOT_DERIVED", "components": [], "quote": text,
                "untyped": [], "poolable": False}
    return {"state": "HELD", "components": typed["components"],
            "quote": typed["definition_span"], "untyped": typed["untyped"],
            "poolable": not typed["untyped"]}


def three_point_result(text):
    """Conservative self-contained result spans; no summing marginal events.

    A named MACE alone, a design-only endpoint, all-cause death, or an
    unbound result is refused. NOT_HELD means no qualifying witness in this
    source scope, not proof that the trial never reported the endpoint.
    """
    for span in re.split(r"(?<=[.!?])\s+(?=[A-Z])|\n", text):
        components = target_endpoint._components_from_text(span, expand_named_composites=False)
        effect = re.search(r"(?:hazard ratio|risk ratio|\bHR\b|\bRR\b)\s*[,=:]?\s*\d+(?:\.\d+)?", span, re.I)
        counts = re.search(r"\b\d+\s+(?:events|participants|patients)\b.*\b(?:versus|vs\.?|compared with)\s+\d+", span, re.I)
        if (components == THREE and (effect or counts)
                and not re.search(r"any death|all.cause|revascular|angina|heart failure|\bTIA\b", span, re.I)):
            return {"state": "HELD", "quote": span.strip()}
    return {"state": "NOT_HELD", "quote": ""}


def witness(root, path, field, quote):
    return {"path": path.relative_to(root).as_posix(), "field": field, "quote": quote,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def build(root=ROOT, slug=SLUG):
    policies = read_json(root / "docs/endpoint_policies.json")["topics"]
    decl = policies[slug]["Major vascular events"]
    pending = next(p for p in decl["pending"] if p["input"] == IDS[2])
    if len(pending["decision_options"]) != 3 or pending["state"] != "DECISION_REQUIRED_BEFORE_INTERVAL":
        raise ValueError("POLICY_SCHEMA_CHANGED: review required")
    source = root / "cache" / slug / "records.json"
    cache = read_json(source)
    records = {str(r["id"]): r for r in cache.get("ctgov", []) + cache["records"]}
    registry = load_registry(root, slug)
    rows = []
    inventory = set()
    for rid in IDS:
        rec = records.get(rid, {})
        abstract = rec.get("abstract") or ""
        definition = typed_definition(abstract, relayed=pending if rid == pending["input"] else None)
        sources = [witness(root, source, rid + ".abstract", abstract)] if abstract else []
        texts = [abstract]
        excluded_spans = []
        nct = rec.get("nct") or (rid if rid.startswith("NCT") else "")
        reg = registry.get(nct, {})
        registered = [o for o in reg.get("design_outcomes", [])
                      if target_endpoint._components_from_text(o.get("measure", "")) == THREE]
        # Source-linked files only; do not import another trial's endpoint from its name.
        folders = []
        held = root / "evidence/acquisition_cascade/held"
        if rid == pending["input"]:
            report_witness = pending["witness_of_report"]
            report_path = root / report_witness["path"]
            if not report_path.is_file():
                raise ValueError("NOT_HELD: pending report metadata " + report_witness["path"])
            if hashlib.sha256(report_path.read_bytes()).hexdigest() != report_witness["sha256"]:
                raise ValueError("SOURCE_HASH_MISMATCH: " + report_witness["path"])
            folders.append(report_path.parent)
        for p in sorted(held.glob("*/europepmc_record_*.json")):
            if rid in p.name:
                folders.append(p.parent)
        if rid == IDS[4]:
            folders += [p.parent for p in held.glob("*/" + rid + ".json")]
        for folder in sorted(set(folders)):
            for p in sorted(folder.iterdir()):
                if p.suffix not in {".txt", ".json", ".html"}:
                    continue
                inventory.add(p.relative_to(root).as_posix())
                # Metadata JSON establishes report availability, never subgroup results.
                if p.suffix == ".txt":
                    content = p.read_text(encoding="utf-8")
                    texts.append(content)
                    sources.append(witness(root, p, "text", ""))
                    # Keep the reported alternative visibly distinct from CV death;
                    # restrict the quote to the older table block, not younger rows.
                    for block in re.finditer(r"Age 70.*?(?=Age 50)", content, re.S):
                        alt = re.search(r"MI, stroke or any death\s+.*?(?=Primary endpoint)", block.group(), re.S)
                        if alt:
                            excluded_spans.append(witness(root, p, "older-adult table; wrong death component", alt.group().strip()))
                if rid == IDS[4] and p.name == rid + ".json":
                    registration = read_json(p)
                    outcomes = registration["protocolSection"]["outcomesModule"]
                    matches = [o["measure"] for o in outcomes.get("secondaryOutcomes", [])
                               if "cardiovascular" in o["measure"].lower()]
                    if len(matches) != 1:
                        raise ValueError("AMBIGUOUS_REGISTRATION_ENDPOINT: " + rid)
                    definition = typed_definition(matches[0])
                    definition["quote"] = matches[0]
                    definition["state"] = "HELD_SECONDARY_NOT_TYPED"
                    # Report parser tokens separately: never relabel secondary as primary.
                    definition["secondary_tokens"] = sorted(target_endpoint._components_from_text(matches[0]))
                    sources.append(witness(root, p, "protocolSection.outcomesModule.secondaryOutcomes", matches[0]))
                    definition["hasResults"] = registration.get("hasResults")
                if p.suffix == ".json" and p.name.startswith("europepmc_record_"):
                    sources.append(witness(root, p, "report metadata only; not subgroup results", ""))
        for p in sorted((root / "cache" / slug).glob("ft_*")):
            if rid in p.name:
                texts.append(p.read_text(encoding="utf-8"))
                sources.append(witness(root, p, "text", ""))
        for p in sorted((root / "evidence/acquisition_cascade/excerpts").glob("*.txt")):
            content = p.read_text(encoding="utf-8")
            if any(folder.name in content for folder in folders):
                texts.append(content)
                sources.append(witness(root, p, "text", ""))
        if rid == IDS[3]:
            match = re.search(r"Secondary outcomes included[^.]+\.", abstract)
            definition["quote"] = match.group() if match else "NOT_HELD"
            definition["secondary_tokens"] = sorted(target_endpoint._components_from_text(definition["quote"]))
        # Full-text candidate spans can involve a different age stratum: report
        # such candidates for review, never automatically admit them.
        result = three_point_result(abstract)
        candidates = [r for t in texts[1:] if (r := three_point_result(t))["state"] == "HELD"]
        if candidates and result["state"] != "HELD":
            result = {"state": "POPULATION_BINDING_REQUIRED", "quote": candidates[0]["quote"]}
        if definition["state"] == "RELAYED":
            result = {"state": "NOT_HELD", "quote": ""}
        if reg.get("registry_results") and result["state"] == "NOT_HELD":
            result = {"state": "REGISTRY_RESULT_BINDING_REQUIRED", "quote": ""}
        rows.append({"id": rid, "title": pending["label"] if rid == IDS[2] else rec.get("title", rid),
                     "definition": definition, "three_point": result, "sources": sources,
                     "excluded_spans": excluded_spans,
                     "registered_three_point": registered,
                     "registry_results_present": bool(reg.get("registry_results")),
                     "fulltext_candidates": candidates})
    # Read history but select ONLY its narrative; never copy its numerical fields.
    history = pending["diagnostic_already_seen"]["note"]
    return {"slug": slug, "options": pending["decision_options"], "decision_rule": pending["decision_rule"],
            "history": history, "rows": rows, "inventory": sorted(inventory)}


def admission(row, option):
    rid, d = row["id"], row["definition"]
    if d["state"] == "RELAYED":
        return "NO (policy)" if option == 0 else "CONDITIONAL; OA subgroup definition + result and recorded decision required"
    if option == 2:
        return "YES, endpoint only" if row["three_point"]["state"] == "HELD" else "NO; " + row["three_point"]["state"] + " age-matched 3-point result"
    if d["state"] == "HELD":
        return "YES, retained broad endpoint; disclose untyped item" if d["untyped"] else "YES, endpoint only"
    return "NO; " + ("results absent; secondary CV endpoint needs explicit policy scope" if rid == IDS[4]
                     else "coronary endpoint differs; eligible broad CV composite/result needed")


def render(data):
    esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
    out = ["# HOPE-3 endpoint-policy decision — reviewer sign-off", "",
           "Endpoint eligibility only; no pooling is implemented. YES does not certify all other eligibility gates.", ""]
    out += [f"**{i + 1}.** {o}" for i, o in enumerate(data["options"])]
    out += ["", "| Input | Own definition / typing | Held 3-point result / acquisition | 1 | 2 | 3 |",
            "|---|---|---|---|---|---|"]
    for row in data["rows"]:
        d = row["definition"]
        description = f"{d['state']}: “{d['quote']}” Components: " + (", ".join(d["components"]) or "NOT_DERIVED")
        if d.get("secondary_tokens"):
            description += "; partial secondary tokens (not component_typing primary): " + ", ".join(d["secondary_tokens"])
        if d["untyped"]:
            description += "; UNTYPED: " + ", ".join(d["untyped"])
        result = row["three_point"]["state"] + (": “" + row["three_point"]["quote"] + "”" if row["three_point"]["quote"] else "")
        if row["excluded_spans"]:
            result += "; wrong composite: “" + row["excluded_spans"][0]["quote"] + "”"
        if row["registered_three_point"]:
            result += "; design only: “" + row["registered_three_point"][0]["measure"] + "”; acquire reported secondary outcome from this trial's OA report/supplement or results registration."
        elif d["state"] == "RELAYED":
            result += "; Ridker PMID 28385949 is not held; seek OA age-specific source/author manuscript (closed letter cannot be admitted)."
        else:
            result += "; acquire age-matched composite result from this report's OA supplement/results registration; do not sum components."
        out.append("| " + " | ".join(esc(x) for x in [row["id"], description, result,
                                                     *(admission(row, i) for i in range(3))]) + " |")
    out += ["", "**Prior exposure (read from policy JSON, numerical fields intentionally omitted):** " + data["history"],
            "**Decision rule:** " + data["decision_rule"],
            "", "**Witnesses:** records.json abstracts keyed by PMID; held PREVENTABLE registration; family registry via load_registry; source paths/hashes and searched files in options.json. NOT_HELD is scoped to this held corpus and conservative span binding.",
            "", "Reviewer: __________  Date/time: __________  Option: __________  Rationale independent of prior diagnostic: ____________________",
            "Prior exposure acknowledged: __________  Decision recorded before any new HOPE-3 interval is computed/inspected: __________", ""]
    return "\n".join(out)


def census(root=ROOT):
    topics = sorted((root / "topics").glob("*.json"))
    examined, flagged = [], {k: [] for k in ("DECISION_REQUIRED_BEFORE_INTERVAL", "RELAYED", "NOT_DERIVED", "UNTYPED", "THREE_POINT_NOT_HELD")}
    matched_topics = []
    for path in topics:
        topic = read_json(path)
        slug = topic.get("slug", path.stem)
        if slug != SLUG:
            continue  # This is a topic-specific decision rule, not a general evidence census.
        matched_topics.append(slug)
        for row in build(root, slug)["rows"]:
            name = slug + "/" + row["id"]
            examined.append(name)
            d = row["definition"]
            if HOPE.search(row["id"]): flagged["DECISION_REQUIRED_BEFORE_INTERVAL"].append(name)
            if d["state"] == "RELAYED": flagged["RELAYED"].append(name)
            if d["state"] in {"NOT_DERIVED", "HELD_SECONDARY_NOT_TYPED"}: flagged["NOT_DERIVED"].append(name)
            if d["untyped"]: flagged["UNTYPED"].append(name)
            if row["three_point"]["state"] != "HELD": flagged["THREE_POINT_NOT_HELD"].append(name)
    return {"topic_scope": {"n": len(matched_topics), "N": len(topics), "items": matched_topics},
            "rules": {k: {"n": len(v), "N": len(examined), "n_of_N": f"{len(v)} of {len(examined)}", "items": v} for k, v in flagged.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", action="store_true")
    args = parser.parse_args()
    if args.census:
        print(json.dumps(census(), indent=2, ensure_ascii=False))
    else:
        data = build()
        out = ROOT / ".tmp/hope3opt"
        out.mkdir(parents=True, exist_ok=True)
        (out / "options.md").write_text(render(data), encoding="utf-8")
        (out / "options.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Wrote .tmp/hope3opt/options.md and options.json; no synthesis performed.")


if __name__ == "__main__":
    main()
