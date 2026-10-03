"""Abstract-sourced harm adjudications for the acq/k-gap integration (2026-10-03).

Integrating acq/k-gap's widened pools exposed 16 harm term hits in screened-in trials whose ABSTRACT mentions adverse
events (gate.check_harms_complete refused probiotics-aad-prevention and semaglutide-obesity-weight). Each was read in the
held record (cache/<slug>/records.json) and decided here with a verbatim span the loader re-validates
(harness.verified_inputs._validate). Conventions are those of scripts/held_harms_adjudication.py:
  * a narrative statement ("similar", "no serious adverse events") with no per-arm participant counts, per-symptom
    EVENT counts in place of participants with an event, or a different intervention's arm: REFUSED_ON_EVIDENCE;
  * a term hit in an aim, methods, outcome-list or background sentence, or a 'side effect' that is the efficacy
    endpoint: SIGNAL_SPURIOUS.
FINDING (not decided here, for the probiotics topic lane): 41707673 (IBS-D) and 40727106 / 36742013 / 30694338
(H. pylori eradication or recurrence) are screened in to antibiotic-associated diarrhoea PREVENTION.

No network. Idempotent. `--check` exits 1 if any decision or audit row is missing or differs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.verified_inputs import entries, load  # noqa: E402

R, S = "REFUSED_ON_EVIDENCE", "SIGNAL_SPURIOUS"
P, AE, SAE = "probiotics-aad-prevention", "Any adverse events", "Serious adverse events"

# (slug, pmid, outcome, provenance, verbatim abstract span, reason)
DECISIONS = [
    (P, "41707673", AE, S, "aimed to evaluate the effectiveness and safety of the dual-strain probiotic",
     "The hit is the aim sentence of an IBS-D trial; the abstract reports no adverse-event counts."),
    (P, "40727106", AE, R, "Secondary outcomes included treatment-related gastrointestinal symptoms, medication "
                           "adherence, and adverse events.",
     "Adverse events are listed as an outcome only; no per-arm participant counts are reported."),
    (P, "40727106", SAE, R, "No serious adverse events were reported in either group.",
     "A narrative zero with no safety-analysis denominators stated; efficacy denominators are not substituted."),
    (P, "36742013", AE, R, "the two groups exhibited similar adverse event rates for epigastric pain, abdominal "
                           "distention, dizzy, vomiting, and rash (p\u2009>\u20090.05)",
     "A per-symptom similarity statement with a p-value; no per-arm counts of participants with any adverse event."),
    (P, "36742013", SAE, S, "reduce adverse events",
     "The hit is the background question; the abstract reports no serious adverse event outcome."),
    (P, "30694338", AE, R, "Adverse events (AEs) were recorded throughout the study",
     "A methods sentence; the abstract reports no per-arm adverse-event counts."),
    (P, "30694338", SAE, S, "Adverse events (AEs) were recorded throughout the study",
     "A methods sentence; the abstract reports no serious adverse event outcome."),
    (P, "25588782", AE, R, "The probiotic group reported fewer adverse events (1 had abdominal pain, 1 vomited and 1 "
                           "had headache) than the placebo group (6 had abdominal pain, 4 had loss of appetite and 1 "
                           "had nausea).",
     "Per-symptom EVENT counts; the number of participants with at least one adverse event is not reported and the "
     "events may overlap within a child."),
    (P, "25588782", SAE, S, "The probiotic group reported fewer adverse events",
     "The sentence reports minor symptoms, not serious adverse events; no serious adverse event outcome is reported."),
    (P, "24309198", AE, R, "Duration and severity of diarrhoea, common gastrointestinal symptoms, serious adverse "
                           "events and quality of life measures were also similar in the two arms.",
     "A narrative similarity statement; no per-arm counts of participants with any adverse event."),
    (P, "24309198", SAE, R, "Duration and severity of diarrhoea, common gastrointestinal symptoms, serious adverse "
                            "events and quality of life measures were also similar in the two arms.",
     "A narrative similarity statement; no per-arm counts of participants with a serious adverse event."),
    (P, "19727002", AE, S, "To examine if intake of Lactobacillus plantarum can prevent gastrointestinal side effects "
                           "in antibiotic-treated patients.",
     "The 'side effects' are the trial's efficacy endpoint (antibiotic-induced GI symptoms), not adverse events of "
     "the intervention."),
    (P, "19727002", SAE, S, "To examine if intake of Lactobacillus plantarum can prevent gastrointestinal side effects "
                            "in antibiotic-treated patients.",
     "The aim sentence; the abstract reports no serious adverse event outcome."),
    (P, "17900321", AE, S, "One of the side effects of antimicrobial therapy is a disturbance of the intestinal "
                           "microbiota",
     "The hit is the background sentence about antibiotics; the abstract reports no adverse events of the probiotic."),
    (P, "17900321", SAE, S, "One of the side effects of antimicrobial therapy is a disturbance of the intestinal "
                            "microbiota",
     "The background sentence; the abstract reports no serious adverse event outcome."),
    ("semaglutide-obesity-weight", "40544433", "Gastrointestinal adverse events", R,
     "Gastrointestinal adverse events (affecting 79.6%\xa0in the cagrilintide-semaglutide group and 39.9% in the "
     "placebo group)",
     "The reported rates are for the cagrilintide-semaglutide COMBINATION arm versus placebo, not semaglutide; no "
     "semaglutide-arm count is reported in the held record."),
]

AUDIT = ROOT / "docs" / "evidence" / "override-audit-2026-09-14" / "overrides.json"


def entry_for(slug: str, pid: str, outcome: str, prov: str, span: str, reason: str) -> dict:
    return dict(outcome=outcome, source_level=1, document_ref=f"cache/{slug}/records.json#{pid}.abstract",
                source_span=span, kind="typed_refusal", provenance=prov, reason=reason)


def audit_row(slug: str, pid: str, outcome: str, entry: dict) -> dict:
    return dict(topic=slug, trial=pid, outcome=outcome, file="verified_effects.json", source_committed=True,
                source_committed_evidence=entry["document_ref"],
                override_replaces="Unresolved abstract harm reporting signal (HARMS_INCOMPLETE)",
                override_with=entry["kind"], stated_reason=entry["reason"], judgement=entry["reason"],
                rule_group="Abstract harm adjudication 2026-10-03 (scripts/abstract_harms_adjudication.py)")


def _read(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def apply(check: bool = False) -> list[str]:
    problems = []
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    akey = lambda r: (r["topic"], str(r["trial"]), r["outcome"])  # noqa: E731
    for slug, pid, outcome, prov, span, reason in DECISIONS:
        recs = _read(ROOT / "cache" / slug / "records.json").get("records") or []
        abstract = next((r.get("abstract") or "" for r in recs if str(r.get("id")) == pid), "")
        if span not in abstract:
            problems.append(f"{slug}/{pid}/{outcome}: span not verbatim in the held abstract")
            continue
        entry = entry_for(slug, pid, outcome, prov, span, reason)
        arms = _read(ROOT / "cache" / slug / "verified_arms.json")
        if any(e["outcome"] == outcome for e in entries(arms.get(pid))):
            problems.append(f"{slug}/{pid}/{outcome}: a decision already exists in verified_arms.json")
            continue
        row = audit_row(slug, pid, outcome, entry)
        if check and row not in audit:
            problems.append(f"{slug}/{pid}/{outcome}: override-audit row missing or different")
        audit = [r for r in audit if akey(r) != akey(row)] + [row]
        path = ROOT / "cache" / slug / "verified_effects.json"
        data = _read(path)
        rows = entries(data.get(pid))
        if check:
            if entry not in rows:
                problems.append(f"{slug}/{pid}/{outcome}: decision missing or different")
            continue
        rows = [e for e in rows if e["outcome"] != outcome] + [entry]
        data[pid] = rows[0] if len(rows) == 1 else rows
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if not check:
        AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        for slug in sorted({d[0] for d in DECISIONS}):
            load(slug)
    return problems


if __name__ == "__main__":
    probs = apply(check="--check" in sys.argv)
    for p in probs:
        print("REFUSED:", p)
    print(f"{len(DECISIONS) - len(probs)} of {len(DECISIONS)} decisions {'present' if '--check' in sys.argv else 'written'}")
    sys.exit(1 if probs else 0)
