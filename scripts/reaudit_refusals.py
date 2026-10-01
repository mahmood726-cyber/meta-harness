"""Re-run the refusal auditor corpus-wide with typed evidence identities (V1.0.1) and report every verdict that flips.

For every served review: each declared-absent row's SERVED reason_code_audit verdict (the before) vs the verdict harness.reason_audit
now gives on the same row and the same held sources, built exactly as harness/pipeline.py builds them (the after). A flip changes
served content, so each is written as a derived NOTICE (before -> after, the evidence the old verdict cited, why it no longer counts).
Also lists every candidate span whose ROLE the regex could not decide -- the input to the recorded model-proposal step.
Nothing served is written here.
  python scripts/reaudit_refusals.py   -> outputs/refusal_audit/REAUDIT.{json,md}, outputs/refusal_audit/undecided_spans.json"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import pipeline, reason_audit  # noqa: E402

OUT = ROOT / "outputs" / "refusal_audit"
BASE = "23642e0d"          # the pre-fix auditor (V1 candidate + lane OC), loaded from git so both versions see IDENTICAL inputs


def _old_auditor():
    """The pre-fix harness.reason_audit, from git, as a side module in the harness package (its relative imports resolve)."""
    import importlib.util
    import subprocess
    src = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:harness/reason_audit.py"], capture_output=True, text=True,
                         encoding="utf-8", check=True).stdout
    spec = importlib.util.spec_from_loader("harness._reason_audit_prefix", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    exec(compile(src, f"{BASE}:harness/reason_audit.py", "exec"), mod.__dict__)
    return mod


# What is SERVED is what the deploy ref carries, not the working tree: once this branch's pages are regenerated with the new
# auditor, the working tree's reason_code_audit IS the new rule's output, and comparing the old rule to it measures nothing.
SERVED_REF = "origin/main"


def _served_verdicts(slug: str) -> dict:
    """{(outcome name, row id): verdict} from docs/reviews/<slug>/review.json AT SERVED_REF (empty if the page is not served)."""
    import subprocess
    got = subprocess.run(["git", "-C", str(ROOT), "show", f"{SERVED_REF}:docs/reviews/{slug}/review.json"], capture_output=True)
    if got.returncode != 0:
        return {}
    review = json.loads(got.stdout.decode("utf-8"))
    return {(o.get("name"), a.get("id") or a.get("label")): (a.get("reason_code_audit") or {}).get("verdict")
            for o in review.get("outcomes") or [] for a in o.get("declared_absent_trials") or []}


def _served_citations(slug: str) -> dict:
    """{(outcome name, row id): the span the SERVED audit cited} at SERVED_REF."""
    import subprocess
    got = subprocess.run(["git", "-C", str(ROOT), "show", f"{SERVED_REF}:docs/reviews/{slug}/review.json"], capture_output=True)
    if got.returncode != 0:
        return {}
    review = json.loads(got.stdout.decode("utf-8"))
    return {(o.get("name"), a.get("id") or a.get("label")): (a.get("reason_code_audit") or {}).get("source_span")
            for o in review.get("outcomes") or [] for a in o.get("declared_absent_trials") or []}


def _chain_and_routes(outcome, row, spec, sources, served, cited_by) -> dict:
    """For a served REASON_FALSE_VALUE_HELD row: the cited chain's own verdict, and routes found elsewhere -- kept apart."""
    k = (outcome.get("name"), row.get("id") or row.get("label"))
    if served.get(k) != "REASON_FALSE_VALUE_HELD":
        return {}
    cited = cited_by.get(k) or ""
    return {"served_chain": reason_audit.audit_cited_chain(outcome, row, cited, spec),
            "recovery_routes": reason_audit.recovery_routes(outcome, row, sources, spec, cited)}


def main() -> int:
    import subprocess
    served_sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", SERVED_REF], capture_output=True, text=True, check=True).stdout.strip()
    old = _old_auditor()
    rows, undecided, pages = [], {}, 0
    for rv_path in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        slug = rv_path.parent.name
        topic = ROOT / "topics" / f"{slug}.json"
        records = ROOT / "cache" / slug / "records.json"
        if not topic.exists() or not records.exists():
            continue
        pages += 1
        review = json.loads(rv_path.read_text(encoding="utf-8"))
        served = _served_verdicts(slug)
        cited_by = _served_citations(slug)
        specs = {sp.get("name"): sp for sp, _ in pipeline._outcome_specs(json.loads(topic.read_text(encoding="utf-8")))}
        sources = reason_audit.sources_by_trial(slug, json.loads(records.read_text(encoding="utf-8")), ROOT)
        for outcome in review.get("outcomes") or []:
            for row in outcome.get("declared_absent_trials") or []:
                key = reason_audit.canonical_trial_id(row.get("id") or row.get("label"))
                spec = {**(specs.get(outcome.get("name")) or {}), "target_population": review.get("question")}   # as annotate_review
                prior = old.audit_reason_row(outcome, row, sources.get(key, []), spec)      # the SAME inputs, the pre-fix rule
                before = prior["verdict"]
                after = reason_audit.audit_reason_row(outcome, row, sources.get(key, []), spec)
                for c in after.get("candidates", []):
                    if c.get("role") == "UNDECIDED":
                        undecided.setdefault(c["span"], {"slug": slug, "trial": key, "outcome": outcome.get("name")})
                rows.append({"slug": slug, "outcome": outcome.get("name"), "trial": key, "stated_reason_code": after.get("stated_reason_code"),
                             "before": before, "after": after["verdict"],
                             "served": served.get((outcome.get("name"), row.get("id") or row.get("label"))),
                             "before_cited": prior.get("source_span"),
                             "after_cited": after.get("source_span"),
                             "why": (after.get("detail") if after["verdict"] != before else None),
                             **_chain_and_routes(outcome, row, spec, sources.get(key, []), served, cited_by)})
    chain_invalid = [r for r in rows if r.get("served_chain", {}).get("chain_verdict") == "REASON_NOT_DISPROVED"]
    flips = [r for r in rows if r["before"] != r["after"]]
    trans = Counter(f"{r['before']} -> {r['after']}" for r in flips)
    OUT.mkdir(parents=True, exist_ok=True)
    notices = [{"kind": "REFUSAL_AUDIT_VERDICT_CHANGED", "slug": r["slug"], "outcome": r["outcome"], "trial": r["trial"],
                "before": r["before"], "after": r["after"], "before_cited": r["before_cited"], "why": r["why"],
                "served_number_changed": False,
                "note": "a served AUDIT verdict about a refusal changes; no pooled number, membership or refusal itself changes"}
               for r in flips] + \
              [{"kind": "SERVED_AUDIT_CHAIN_INVALID", "slug": r["slug"], "outcome": r["outcome"], "trial": r["trial"],
                "served_verdict": r["served"], "served_cited": r["served_chain"]["chain_evidence"],
                "chain_verdict": r["served_chain"]["chain_verdict"], "fails_on": r["served_chain"]["fails_on"],
                "recovery_routes": r.get("recovery_routes") or [],
                "note": "the served verdict's cited evidence does not match the refusal's outcome/timepoint/aggregation/measure/unit; "
                        "a recovery route, if listed, is a separate extraction lead and does NOT validate the cited chain"}
               for r in chain_invalid]
    # A named reproduction check, not an assumption: the pre-fix rule re-run on THESE inputs vs the verdict actually SERVED.
    # A shortfall means the served audit was built from different inputs or auditor version (not isolated), so 'before' is the pre-fix
    # rule on today's inputs -- the like-for-like baseline -- and the served verdict is reported beside it, never equated with it.
    reproduced = sum(1 for r in rows if r["served"] == r["before"])
    report = {"old_rule_reproduces_served": {"n": reproduced, "N": len(rows), "served_ref": f"{SERVED_REF} = {served_sha}",
                                             "served_missing": sum(1 for r in rows if r["served"] is None),
                                             "line": f"the pre-fix rule reproduces {reproduced} of {len(rows)} served audit verdicts (served = {SERVED_REF} {served_sha[:8]})"},
              "pages": pages, "N": len(rows), "flipped": len(flips), "line": f"{len(flips)} of {len(rows)} refusal-audit verdicts flip",
              "transitions": dict(trans), "by_page": dict(Counter(r["slug"] for r in flips)), "notices": notices, "rows": rows}
    (OUT / "REAUDIT.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "undecided_spans.json").write_text(json.dumps({"n": len(undecided), "spans": undecided}, indent=1, ensure_ascii=False) + "\n",
                                              encoding="utf-8")
    md = ["# Refusal-audit re-run (typed evidence identities, V1.0.1)", "", f"**{report['line']}** across {pages} pages.", "",
          f"Reproduction check: {report['old_rule_reproduces_served']['line']}. The rest were not produced by this rule on these "
          "inputs -- the served audit was built from different inputs or a different auditor version (not isolated) -- so flips "
          "are measured against the pre-fix rule on the same inputs, never against the served verdict.", "",
          "| transition | n |", "|---|---|"] + [f"| {k} | {v} |" for k, v in trans.most_common()] + \
         ["", "Every flip is a served AUDIT-verdict change (a notice), never a pooled-number change.", "",
          "| page | outcome | trial | before | after | before cited | why |", "|---|---|---|---|---|---|---|"] + \
         [f"| {r['slug']} | {r['outcome']} | {r['trial']} | {r['before']} | {r['after']} | {(r['before_cited'] or '')[:90]} | {(r['why'] or '')[:140]} |"
          for r in flips]
    (OUT / "REAUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(report["line"], f"| undecided-role spans: {len(undecided)}")
    for k, v in trans.most_common():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
