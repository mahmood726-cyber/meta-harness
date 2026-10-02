"""Held-full-text harm adjudications (2026-10-01): the cells the held-full-text enables exposed.

Enabling held full texts let harms.reporting_signal see 17 term hits in primary-pool trials that the abstracts never
showed, and gate.check_harms_complete refused 7 pages (HARMS_INCOMPLETE). Each hit was read in its held document and
is resolved here as a static, source-backed decision -- one extraction where the held text reports per-arm counts,
otherwise a typed refusal whose verbatim span the loader re-validates against the held bytes
(harness.verified_inputs._validate). Conventions follow the corpus's existing decisions:
  * a narrative zero or an arm-attributed statement with no control-arm count is REFUSED_ON_EVIDENCE
    (probiotics 18701826, 18410562, 9570649, 34541475);
  * a count not reported at the protocol's day-28 window is TIMEPOINT_MISMATCH (tocilizumab 38157348);
  * a term hit in background, methods, references or a definition list is SIGNAL_SPURIOUS.

No network. Idempotent: re-running rewrites the same entries. `--check` exits 1 if any entry is missing or differs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.verified_inputs import entries, load  # noqa: E402

R, S, T = "REFUSED_ON_EVIDENCE", "SIGNAL_SPURIOUS", "TIMEPOINT_MISMATCH"

# (slug, pmid, outcome, provenance-or-None, span, reason, counts-or-None)
DECISIONS = [
    ("colchicine-secondary-cv-prevention", "32295417", "Gastrointestinal adverse effects", None,
     # header (arm denominators) through the GI row: verify.verify_pooled checks every count's digits in this span
     '<thead><tr><th align="left" valign="top" rowspan="1" colspan="1"/><th align="center" valign="middle" '
     'rowspan="1" colspan="1">Colchicine<break/>(n=366)</th><th align="center" valign="middle" rowspan="1" '
     'colspan="1">Placebo<break/>(n=348)</th><th align="center" valign="middle" rowspan="1" colspan="1">p-value</th>'
     '</tr></thead><tbody><tr><td align="left" valign="middle" rowspan="1" colspan="1">Chest pain, %</td>'
     '<td align="center" valign="middle" rowspan="1" colspan="1">33 (9.0)</td><td align="center" valign="middle" '
     'rowspan="1" colspan="1">25 (7.2)</td><td align="center" valign="middle" rowspan="1" colspan="1">0.45</td></tr>'
     '<tr><td align="left" valign="middle" rowspan="1" colspan="1">Gastrointestinal symptoms, %</td>'
     '<td align="center" valign="middle" rowspan="1" colspan="1">34 (9.3)</td>'
     '<td align="center" valign="middle" rowspan="1" colspan="1">11 (3.2)</td>'
     '<td align="center" valign="middle" rowspan="1" colspan="1">0.001</td></tr>',
     "Table 4 (adverse events, colchicine n=366, placebo n=348): gastrointestinal symptoms 34 (9.3%) vs 11 (3.2%). "
     "The safety assessment uses the entire randomized cohort (366 and 348 randomized).",
     (34, 366, 11, 348)),
    ("corticosteroids-cap-mortality", "21406101", "Hyperglycaemia", R,
     "among the 23 patients of the MPDN group, only one needed insulin for adequate diabetes control",
     "Only the steroid arm is described, and insulin need is not the hyperglycaemia outcome; no control-arm count "
     "is reported.", None),
    ("corticosteroids-cap-mortality", "21406101", "Gastrointestinal bleeding", R,
     "one patient suffered a digestive haemorrhage related to an active peptic ulcer",
     "A single haemorrhage is narrated for one patient after steroid discontinuation; no per-arm count for the "
     "control group is reported.", None),
    ("corticosteroids-cap-mortality", "35723686", "Gastrointestinal bleeding", S,
     "Active gastrointestinal bleeding requiring transfusion of at least 5 units",
     "The hit is a footnote defining a reason for study-drug withdrawal, not a bleeding outcome count; the held "
     "text reports no gastrointestinal bleeding outcome.", None),
    ("iv-iron-hfref-hosp", "25176939", "Injection-site reactions", R,
     "two patients experienced injection site discolouration",
     "Injection-site events are narrated only among treatment-related adverse events in the ferric carboxymaltose "
     "arm; no placebo-arm count is reported.", None),
    ("iv-iron-hfref-hosp", "25176939", "Hypersensitivity reactions", R,
     "No severe allergic reactions related to the study treatment were reported.",
     "A narrative zero restricted to severe, treatment-related allergic reactions; it does not count participants "
     "with any hypersensitivity reaction in either arm.", None),
    ("iv-iron-hfref-hosp", "28701470", "Hypersensitivity reactions", R,
     "No hypersensitivity reactions to the drug occurred",
     "A narrative zero attributed to the study drug (active arm only); no control-arm count or safety denominator "
     "is stated.", None),
    ("melatonin-primary-insomnia-sol", "27559258", "Adverse events", R,
     "We did not observe any adverse effects of melatonin in our patients.",
     "A narrative zero attributed to melatonin; no placebo-arm count or safety denominator is stated.", None),
    ("omega3-cardiovascular-events", "30415637", "Atrial fibrillation", S,
     "Ancillary studies examining diabetes, atrial fibrillation, cognition, autoimmune disorders, and other outcomes "
     "will inform the overall benefit-risk balance",
     "The hit names future ancillary studies; this report gives no atrial fibrillation outcome.", None),
    ("omega3-cardiovascular-events", "38199870", "Bleeding", S,
     "intracerebral haemorrhage (I61)",
     "The hit is an ICD-10 code in the stroke definition list; the held text reports no bleeding outcome.", None),
    ("probiotics-aad-prevention", "39497860", "Any adverse events", R,
     "the reported side effects were nausea in nine patients, bloating in 13 patients, abdominal pain in 16 patients, "
     "and flatulence in six patients",
     "Per-symptom counts only; the number of participants with at least one adverse event is not reported and the "
     "symptoms may overlap within a participant.", None),
    ("probiotics-aad-prevention", "39497860", "Serious adverse events", S,
     "reported side effects between the groups",
     "The hit is the statistical-methods sentence; the held text reports no serious adverse event outcome.", None),
    ("probiotics-aad-prevention", "38258024", "Any adverse events", R,
     "No adverse events were reported with the use of probiotics.",
     "A narrative zero restricted to the probiotic arm in an open-label trial; no control-arm count is stated.", None),
    ("probiotics-aad-prevention", "38258024", "Serious adverse events", R,
     "No adverse events were reported with the use of probiotics.",
     "A narrative zero restricted to the probiotic arm; no control-arm count of serious adverse events is "
     "stated.", None),
    ("probiotics-aad-prevention", "30912409", "Serious adverse events", R,
     "no adverse events were reported in any of the two arms",
     "The narrative zero statement does not present a per-arm adverse-event table or explicitly identify "
     "safety-analysis denominators; efficacy denominators are not substituted.", None),
    ("probiotics-aad-prevention", "21165295", "Serious adverse events", R,
     "there were no significant adverse events associated with the use of Lacidofil",
     "An attribution-qualified narrative; the five adverse-event withdrawals are not split by arm and no per-arm "
     "serious adverse event count is reported.", None),
    ("tocilizumab-covid19-mortality", "33472855", "Secondary infections by 28 days", T,
     "time to independence from supplemental oxygen within 29 days; duration of hospital stay; secondary infections;",
     "Secondary infections (10/65 vs 10/64) are reported over the trial follow-up, which runs to day 29, with no "
     "count by day 28; refused on the same basis as 38157348's day-29 table.", None),
]


def entry_for(slug: str, pid: str, outcome: str, prov: str | None, span: str, reason: str, counts) -> tuple[str, dict]:
    base = dict(outcome=outcome, source_level=1, document_ref=f"cache/{slug}/ft_{pid}.txt", source_span=span)
    if counts:
        ai, n1i, ci, n2i = counts
        return "verified_arms.json", dict(base, override=True, ai=ai, n1i=n1i, ci=ci, n2i=n2i, source=span,
                                          provenance="fulltext_verified_arms", kind="extracted_counts",
                                          verification=reason)
    return "verified_effects.json", dict(base, kind="typed_refusal", provenance=prov, reason=reason)


def _read(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


AUDIT = ROOT / "docs" / "evidence" / "override-audit-2026-09-14" / "overrides.json"


def audit_row(slug: str, pid: str, outcome: str, fname: str, entry: dict) -> dict:
    """The override-audit row (tests/test_override_audit.py requires one per committed override)."""
    why = entry.get("reason") or entry.get("verification")
    return dict(topic=slug, trial=pid, outcome=outcome, file=fname, source_committed=True,
                source_committed_evidence=entry["document_ref"],
                override_replaces="Unresolved held-full-text harm reporting signal (HARMS_INCOMPLETE)",
                override_with=entry["kind"], stated_reason=why, judgement=why,
                rule_group="Held-full-text harm adjudication 2026-10-01 (scripts/held_harms_adjudication.py)")


def apply(check: bool = False) -> list[str]:
    problems = []
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    akey = lambda r: (r["topic"], r["file"], str(r["trial"]), r["outcome"])  # noqa: E731
    for slug, pid, outcome, prov, span, reason, counts in DECISIONS:
        raw = (ROOT / "cache" / slug / f"ft_{pid}.txt").read_text(encoding="utf-8")
        if span not in raw:
            problems.append(f"{slug}/{pid}/{outcome}: span not verbatim in held text")
            continue
        fname, entry = entry_for(slug, pid, outcome, prov, span, reason, counts)
        path = ROOT / "cache" / slug / fname
        other = ROOT / "cache" / slug / ("verified_effects.json" if fname == "verified_arms.json" else "verified_arms.json")
        if any(e["outcome"] == outcome for e in entries(_read(other).get(pid))):
            problems.append(f"{slug}/{pid}/{outcome}: a decision already exists in {other.name}")
            continue
        row = audit_row(slug, pid, outcome, fname, entry)
        if check and row not in audit:
            problems.append(f"{slug}/{pid}/{outcome}: override-audit row missing or different")
        audit = [r for r in audit if akey(r) != akey(row)] + [row]
        data = _read(path)
        rows = entries(data.get(pid))
        if check:
            if entry not in rows:
                problems.append(f"{slug}/{pid}/{outcome}: decision missing or different in {fname}")
            continue
        rows = [e for e in rows if e["outcome"] != outcome] + [entry]
        data[pid] = rows[0] if len(rows) == 1 else rows
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if not check:
        AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        for slug in sorted({d[0] for d in DECISIONS}):
            load(slug)  # re-validates every span against the held bytes; raises on any mismatch
    return problems


if __name__ == "__main__":
    probs = apply(check="--check" in sys.argv)
    for p in probs:
        print("REFUSED:", p)
    print(f"{len(DECISIONS) - len(probs)} of {len(DECISIONS)} decisions {'present' if '--check' in sys.argv else 'written'}")
    sys.exit(1 if probs else 0)
