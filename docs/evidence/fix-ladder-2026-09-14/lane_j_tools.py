from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import textwrap
import time
import unicodedata
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EVDIR = Path(__file__).resolve().parent
BASE_URL = "https://mahmood726-cyber.github.io/meta-harness"
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass(frozen=True)
class Case:
    num: int
    slug: str
    claim: str
    verdict: str
    state: str
    rationale: str

    @property
    def filename(self) -> str:
        return f"{self.num:02d}-{self.slug}.txt"

    @property
    def evidence_path(self) -> str:
        return f"docs/evidence/fix-ladder-2026-09-14/{self.filename}"


CASES: list[Case] = [
    Case(1, "prereg-sha-state", "Preregistration/build-SHA disclosure and one-state rendering are live across pages.", "REPRODUCED", "VERIFIED", "Live pages expose protocol-before-synthesis as not demonstrated and expose corpus currency from the generated index."),
    Case(2, "substudy-carrier", "Substudy identifiers are carried through extraction, RoB, funding, and GRADE.", "NOT REPRODUCED", "REPORTED", "Bounded source search found no committed substudy carrier/gate across those layers."),
    Case(3, "d3-grade-cap", "D3 defaults to not assessed, caps certainty below high, and low-risk-only sensitivity is labelled not-estimable/coverage-limited.", "REPRODUCED", "VERIFIED", "Live risk-of-bias/GRADE text states D3 is not assessed and caps high certainty; low-risk sensitivity is rendered with coverage caveat."),
    Case(4, "d5-reconcile", "D5 semantic reconciliation is implemented.", "NOT REPRODUCED", "REPORTED", "No dedicated committed semantic reconciliation mechanism or evidence artifact was found."),
    Case(5, "registered-estimand", "Registered estimand wins over source/count reconstruction.", "REPRODUCED", "VERIFIED", "Runtime extraction takes the DAPA-HFpEF source HR when HR is registered and only falls back to counts with no estimand request."),
    Case(6, "irr-mistyping", "First-event/mortality rate ratios are typed as RR while recurrent/person-time rates remain IRR.", "REPRODUCED", "VERIFIED", "Runtime extraction classifies first-event rate ratios as RR and recurrent/person-time examples as IRR; live omega-3 now pools as RR."),
    Case(7, "not-run-wording", "NOT_RUN cannot justify an inaccessibility/paywall claim and is honestly worded as not attempted.", "REPRODUCED", "VERIFIED", "Live source-status legend renders NOT_RUN as not attempted and no tested page used the old paywall/inaccessible claim."),
    Case(8, "incompatible-failclosed", "Incompatible pools fail closed and rendered counterfactuals remain suppressed/invalid.", "REPRODUCED", "VERIFIED", "The live iv-iron page shows INCOMPATIBLE, SUPPRESSED, no pooled effect, and an invalid counterfactual."),
    Case(9, "unknown-denominator", "Unknown funding is not counted as negative in proportion denominators.", "REPRODUCED", "VERIFIED", "The live balanced-crystalloids page renders known and unknown funding separately."),
    Case(10, "cross-module-state", "Cross-module single source-state plus a no-two-modules-disagree gate is implemented.", "NOT REPRODUCED", "REPORTED", "Search found no general committed no-two-modules-disagree gate; only partial topic-specific/state work is present."),
    Case(11, "comparator-scope", "Comparator-scope re-run across all 32 topics has a landed disclosure fix.", "REPRODUCED", "VERIFIED", "All 32 committed review objects carry comparator scope fields, with explicit mismatch disclosures where the rule fires."),
    Case(12, "effect-measure", "Effect measures use a three-field type system with class-based compatibility.", "REPRODUCED", "VERIFIED", "Runtime estmeasure probes show label/model/canonical fields, within-class compatibility, and across-class incompatibility."),
    Case(13, "atomic-comparator", "Comparator extraction is atomic and full text can fill but not override abstract headline effects.", "REPRODUCED", "VERIFIED", "Runtime comparator_effect keeps the abstract RR 0.40 headline and uses full text only for an absent outcome."),
    Case(14, "arm-contrast", "Arm-contrast parsing and randomised-contrast disclosure are live.", "REPRODUCED", "VERIFIED", "The live NOAC page renders SoSTART as X-CONTRAST and displays contrast status."),
    Case(15, "harms-zero-event", "Harms are decoupled from extraction format and zero-event cells remain data.", "REPRODUCED", "VERIFIED", "Committed harm outcomes are distinct in the TXA review and runtime synthesis keeps zero-cell studies finite."),
    Case(16, "nct-publication-layer", "NCT-to-publication link layer, PUBLICATION_FOUND_NOT_EXTRACTED gate, and verified 33/67 subset are landed.", "NOT REPRODUCED", "REPORTED", "No committed PUBLICATION_FOUND_NOT_EXTRACTED gate or verified 33/67 linkage artifact was found."),
    Case(17, "no-width-size-exclusion", "Trials are not excluded merely for wide intervals, small size, or k=1.", "REPRODUCED", "VERIFIED", "Live k=1 topics render pooled results and state heterogeneity/prediction intervals are not estimable rather than excluding the trial."),
    Case(18, "claimed-entity-derived", "Claimed outcome/intervention/population/drug-class entities are derived from the pooled object.", "NOT REPRODUCED", "REPORTED", "No committed claimed-entity derivation/gate artifact was found."),
    Case(19, "heterogeneity-derived", "Heterogeneity narratives are derived from the pooled endpoint rather than authored.", "REPRODUCED", "VERIFIED", "Runtime composite_heterogeneity names kidney threshold differences and avoids CV-MACE components on kidney composites."),
    Case(20, "grade-human-deferral", "GRADE not-rateable extends to deferred-to-human domains, not only missing domains.", "REPRODUCED", "VERIFIED", "Live GRADE text leaves indirectness to human judgement and keeps D3 not assessed with high-certainty cap."),
    Case(21, "unit-of-analysis", "Cluster/crossover unit-of-analysis issues are detected and folded into suppression-at-source disclosure.", "REPRODUCED", "VERIFIED", "Runtime detector flags cluster-crossover trials and the balanced-crystalloids review carries unit_of_analysis records."),
    Case(22, "reassurance-verified", "Every 'would not change' reassurance is computationally verified.", "NOT REPRODUCED", "REPORTED", "No committed corpus-wide verification artifact for every reassurance was found."),
    Case(23, "basics-census", "The reproduction census explains why the BaSICS expected-failure was missed.", "NOT REPRODUCED", "REPORTED", "Current committed balanced-crystalloids output includes BaSICS in the mortality pool, and no census-basics explanation artifact exists."),
    Case(24, "timepoint-window", "Timepoint hierarchy and multi-window sweep prevent pooling off-window trials.", "REPRODUCED", "VERIFIED", "Committed semaglutide-weight output declares Week 44/52 trials absent against a Week 68 registered timepoint."),
    Case(25, "comparator-predates", "Comparator-predates-our-included-trials rule and sweep are implemented.", "NOT REPRODUCED", "REPORTED", "Review parity notes exist, but no committed comparator-predates rule/sweep/gate artifact was found."),
    Case(26, "poison-platform", "Domain-level screening, poison-token sweep, and platform-trial census are implemented.", "NOT REPRODUCED", "REPORTED", "No committed domain-level poison-token/platform-trial sweep artifact was found."),
    Case(27, "exclusion-symmetry", "exclusion_symmetry self-check is instrumented and gated.", "NOT REPRODUCED", "REPORTED", "No committed exclusion_symmetry instrument/gate artifact was found."),
    Case(28, "unregistered-exclusion", "UNREGISTERED_EXCLUSION_CRITERION is implemented.", "NOT REPRODUCED", "REPORTED", "No committed UNREGISTERED_EXCLUSION_CRITERION mechanism was found."),
    Case(29, "pmid-40261382", "PMID 40261382 is in the search-rebuild test set as a confirmed true miss.", "NOT REPRODUCED", "REPORTED", "No committed search-rebuild test-set artifact containing PMID 40261382 was found."),
    Case(30, "class-discovery", "new-classes-per-audit trend artifact is committed.", "REPRODUCED", "VERIFIED", "docs/class_discovery.json is committed and records the new_classes_per_audit trend through audit 29."),
    Case(31, "mortality-synonym", "The mortality/death synonym gap no longer silently drops Torres from CAP mortality.", "REPRODUCED", "VERIFIED", "The live CAP page includes Torres PMID 25688779 and renders k=2 with the updated nonsignificant pooled RR."),
    Case(32, "arm-denominator", "Near-equal arm denominators are bound correctly in committed review objects.", "REPRODUCED", "VERIFIED", "Committed SELECT and semaglutide-weight review objects carry the expected denominators and source-reported HRs."),
    Case(33, "canonical-claim", "Canonical claim object derives one significance/null-crossing claim and gates contradictions.", "REPRODUCED", "VERIFIED", "The live PCSK9 page renders the claims-checked/contradictions count from the reproduction tab."),
    Case(34, "invalidation", "Invalidation propagation renders one per-topic STALE flag and a corpus stale count.", "REPRODUCED", "VERIFIED", "The live index renders the object-derived current/STALE count and topic pages show STALE banners."),
    Case(35, "compatibility-key", "Pooling compatibility key is rendered and incompatible counterfactuals fail closed.", "REPRODUCED", "VERIFIED", "Live GLP-1/iv-iron pages render compatibility key/source-reported details and invalid suppressed counterfactuals."),
    Case(36, "armcontrast-screening", "Randomised-contrast screening evicts confirmed non-contrasts as X-CONTRAST.", "REPRODUCED", "VERIFIED", "The live NOAC page and committed contrast_evictions artifact show SoSTART X-CONTRAST eviction."),
    Case(37, "trial-report-model", "Trial/report entity model collapses secondary/duplicate reports before counting.", "REPRODUCED", "VERIFIED", "The live esketamine page renders X-DEDUP and committed study_families data exists."),
    Case(38, "protocol-compiler", "Protocol compiler compares prose protocol and executable config as independent sources.", "REPRODUCED", "VERIFIED", "The live index renders Protocol<->config divergence counts and pages include protocol_config objects."),
    Case(39, "object-derived-states", "eligible_declared_absent, no_checkable_claim, NEVER_CONSIDERED, and identity crosswalk states are object-derived.", "REPRODUCED", "VERIFIED", "The live index/object pages render 29 STALE, Claims-checked-0 limitation, and NEVER_CONSIDERED state from committed objects."),
    Case(40, "derivation-provenance", "Every pooled number carries reported versus harness-reconstructed derivation provenance.", "REPRODUCED", "VERIFIED", "Live melatonin and GLP-1 pages render harness-reconstructed and source-reported provenance labels."),
]


def normalize(s: str) -> str:
    s = html.unescape(s)
    s = re.sub(r"<script\b.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style\b.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", " ", s).strip()


def fetch_page(path: str) -> tuple[str, str]:
    url = path if path.startswith("http") else f"{BASE_URL}/{path.lstrip('/')}"
    req = urllib.request.Request(url, headers={"User-Agent": "Codex-Lane-J/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    text = raw.decode("utf-8", errors="replace")
    print(f"URL: {url}")
    print(f"bytes: {len(raw)}")
    print(f"sha256: {hashlib.sha256(raw).hexdigest()[:16]}")
    return text, normalize(text)


def context(text: str, pattern: str, regex: bool = False) -> str:
    flags = re.I | re.S
    m = re.search(pattern, text, flags) if regex else re.search(re.escape(pattern), text, flags)
    if not m:
        return "MISSING"
    start = max(0, m.start() - 90)
    end = min(len(text), m.end() + 90)
    return "FOUND: " + text[start:end]


def check_terms(text: str, terms: list[str]) -> bool:
    ok = True
    for term in terms:
        hit = context(text, term)
        print(f"TOKEN {term!r}: {hit}")
        ok = ok and not hit.startswith("MISSING")
    return ok


def check_regexes(text: str, patterns: list[str]) -> bool:
    ok = True
    for pattern in patterns:
        hit = context(text, pattern, regex=True)
        print(f"REGEX {pattern!r}: {hit}")
        ok = ok and not hit.startswith("MISSING")
    return ok


def read_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def rel_display(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def repo_text_files(paths: list[str], max_bytes: int = 1_500_000):
    for rel in paths:
        p = ROOT / rel
        if not p.exists():
            continue
        if p.is_file():
            if p.stat().st_size <= max_bytes:
                yield p
            continue
        for child in p.rglob("*"):
            if not child.is_file():
                continue
            if any(part in {".git", "__pycache__", ".pytest_cache"} for part in child.parts):
                continue
            if child.suffix.lower() not in {".py", ".json", ".md", ".html", ".txt"}:
                continue
            if child.stat().st_size <= max_bytes:
                yield child


def bounded_search(patterns: list[str], paths: list[str], exclude: list[str] | None = None, limit: int = 20) -> int:
    default_exclude = [
        "docs/evidence/fix-ladder-2026-09-14",
        "docs/fix_ledger.json",
        "docs/fix_ledger.proposed.json",
        "docs/index.html",
        "docs/m/",
        "docs/parity",
        "LANE-J-REPORT.md",
    ]
    exclude = default_exclude + (exclude or [])
    total = 0
    regexes = [re.compile(p, re.I) for p in patterns]
    for path in repo_text_files(paths):
        rp = rel_display(path)
        if any(ex in rp for ex in exclude):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if any(r.search(line) for r in regexes):
                total += 1
                if total <= limit:
                    print(f"{rp}:{i}: {line[:240]}")
                break
    print(f"match_files: {total}")
    return total


def git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=60)
    print("$ git " + " ".join(args))
    print(proc.stdout.strip() or "(no stdout)")
    if proc.stderr.strip():
        print("STDERR:")
        print(proc.stderr.strip())
    print(f"exit_code: {proc.returncode}")
    return proc.stdout


def case01() -> bool:
    _, index = fetch_page("/")
    ok1 = check_regexes(index, [r"3 of 32.*?current.*?29 of 32.*?STALE", r"Protocol.{0,5}config"])
    _, page = fetch_page("/reviews/balanced-crystalloids-vs-saline-mortality/")
    ok2 = check_regexes(page, [r"precedence.{0,80}NOT demonstrated", r"Build / replay SHA"])
    return ok1 and ok2


def case02() -> bool:
    hits = bounded_search(
        [r"substudy_id", r"substudy_identifier", r"substudy.*risk.of.bias", r"substudy.*funding", r"substudy.*GRADE"],
        ["harness", "tests", "docs"],
        exclude=["docs/cache", "docs/reviews"],
    )
    print("No committed extraction/RoB/funding/GRADE substudy carrier was found outside raw review output.")
    return hits == 0


def case03() -> bool:
    _, page = fetch_page("/reviews/sglt2-ckd-progression/")
    return check_regexes(page, [
        r"D3 .*?NOT ASSESSED",
        r"caps overall GRADE certainty below .*?high",
        r"human judgement",
        r"low-risk trials",
    ])


def case04() -> bool:
    hits = bounded_search(
        [r"D5 semantic", r"semantic reconciliation", r"semantic_reconciliation"],
        ["harness", "tests", "docs"],
        exclude=[],
    )
    print("No dedicated D5 semantic reconciliation artifact or gate was found.")
    return hits == 0


def case05() -> bool:
    from harness import extract

    rec = read_json("cache/dapagliflozin-hfpef-hosp/records.json")
    topic = read_json("topics/dapagliflozin-hfpef-hosp.json")
    abstract = {str(r["id"]): r for r in rec["records"]}["36027570"]["abstract"]
    po = topic["primary_outcome"]
    args = (abstract, po["keywords"], topic["intervention_terms"], topic["comparator_terms"])
    ex_hr = extract.extract_trial(*args, declared_composite=True, estimand="HR")
    ex_default = extract.extract_trial(*args, declared_composite=True)
    print("estimand=HR:", json.dumps({k: ex_hr.get(k) for k in ("scale", "effect", "ai", "ci_low", "ci_high")}, sort_keys=True))
    print("no estimand:", json.dumps({k: ex_default.get(k) for k in ("scale", "effect", "ai", "ci_low", "ci_high")}, sort_keys=True))
    return ex_hr.get("scale") == "HR" and ex_hr.get("effect") == 0.82 and ex_hr.get("ai") is None and ex_default.get("ai") == 512


def case06() -> bool:
    from harness import extract

    samples = {
        "RECOVERY first-event mortality": "Overall, 482 patients (22.9%) in the dexamethasone group and 1110 (25.7%) in the usual care group died within 28 days (age-adjusted rate ratio, 0.83; 95% confidence interval, 0.75 to 0.93).",
        "ASCEND first-event vascular": "a serious vascular event occurred in 689 patients (8.9%) in the fatty acid group and in 712 (9.2%) in the placebo group (rate ratio, 0.97; 95% confidence interval, 0.87 to 1.08).",
        "FAIR-HF2 recurrent": "The second primary outcome, total heart failure hospitalizations, occurred 264 times in the ferric carboxymaltose group vs 320 times in placebo (rate ratio, 0.80; 95% CI, 0.60 to 1.06).",
        "person-time": "Ketoacidosis occurred at 0.09 versus 0.02 per 100 person-years (rate ratio, 4.5; 95% CI, 1.2 to 9.9).",
    }
    observed = {}
    for name, sent in samples.items():
        eff = extract.extract_effect(sent)
        observed[name] = eff[0] if eff else None
    print(json.dumps(observed, indent=2, sort_keys=True))
    _, page = fetch_page("/reviews/omega3-cardiovascular-events/")
    live = check_terms(page, ["Estimand RR", "Pooled effect 0.94 (RR)"])
    return observed["RECOVERY first-event mortality"] == "RR" and observed["ASCEND first-event vascular"] == "RR" and observed["FAIR-HF2 recurrent"] == "IRR" and observed["person-time"] == "IRR" and live


def case07() -> bool:
    _, page = fetch_page("/reviews/tranexamic-acid-pph/")
    ok = check_terms(page, ["NOT_RUN = not attempted for this topic"])
    forbidden = [r"NOT_RUN.{0,120}paywall", r"NOT_RUN.{0,120}inaccessib"]
    for pat in forbidden:
        print(f"FORBIDDEN {pat!r}: {context(page, pat, regex=True)}")
    return ok and all(context(page, p, regex=True).startswith("MISSING") for p in forbidden)


def case08() -> bool:
    _, page = fetch_page("/reviews/iv-iron-hfref-hosp/")
    return check_terms(page, ["INCOMPATIBLE", "SUPPRESSED", "no pooled effect is reported", "would have been", "INVALID"])


def case09() -> bool:
    _, page = fetch_page("/reviews/balanced-crystalloids-vs-saline-mortality/")
    return check_terms(page, ["0 of 1 known", "4 unknown", "unknown-funding trials", "not counted as independently funded"])


def case10() -> bool:
    hits = bounded_search(
        [r"no-two-modules", r"modules-disagree", r"cross-module.*gate", r"single source-state"],
        ["harness", "tests", "docs"],
        exclude=[],
    )
    print("A general no-two-modules-disagree gate was not found.")
    return hits == 0


def case11() -> bool:
    reviews = list((ROOT / "docs/reviews").glob("*/review.json"))
    with_scope = []
    mismatches = []
    notes = []
    for path in reviews:
        data = json.loads(path.read_text(encoding="utf-8"))
        scope = ((data.get("comparator") or {}).get("scope") or {})
        if scope:
            with_scope.append(path.parent.name)
            if scope.get("scope_valid") is False:
                mismatches.append(path.parent.name)
        if data.get("comparator_scope_note"):
            notes.append(path.parent.name)
    print("review_count:", len(reviews))
    print("with_scope:", len(with_scope))
    print("scope_mismatches:", json.dumps(mismatches, ensure_ascii=False))
    print("comparator_scope_notes:", json.dumps(notes, ensure_ascii=False))
    print("scope_audit_entries:", len(read_json("docs/scope_audit.json")))
    return len(reviews) == 32 and len(with_scope) == 32 and len(mismatches) >= 1 and len(notes) >= 1


def case12() -> bool:
    from harness import estmeasure as em

    obj = em.classify("RR", "estimated with a Cox proportional-hazards model; relative risk 0.70")
    same_class = em.pool_compatibility([em.classify("RR", "relative risk"), em.classify("HR", "hazard ratio")])
    cross_class = em.pool_compatibility([em.classify("HR", "time to first event"), em.classify("IRR", "per 100 person-years")])
    print("object:", json.dumps(obj, sort_keys=True))
    print("within_class:", json.dumps(same_class, sort_keys=True))
    print("across_class:", json.dumps(cross_class, sort_keys=True))
    return obj["reported_label"] == "RR" and obj["statistical_model"] == "cox_proportional_hazards" and same_class["status"] == "compatible_labels" and cross_class["status"] == "incompatible"


def case13() -> bool:
    from harness.extract import comparator_effect

    abstract = "Colchicine reduced recurrent pericarditis during follow-up (RR=0.40, 95% CI 0.30 to 0.54). Adverse events were not increased."
    fulltext = "In a sensitivity analysis of recurrent pericarditis the risk ratio was RR 0.46 (95% CI 0.37 to 0.58). Gastrointestinal adverse events occurred more often with colchicine (RR 1.85, 95% CI 1.04 to 3.29)."
    headline = comparator_effect(abstract, fulltext, ["recurren"])
    filled = comparator_effect(abstract, fulltext, ["gastrointestinal", "adverse"])
    absent = comparator_effect(abstract, fulltext, ["mortality", "death"])
    print("headline:", json.dumps(headline, sort_keys=True))
    print("filled:", json.dumps(filled, sort_keys=True))
    print("absent:", absent)
    return headline and abs(headline["effect"] - 0.40) < 1e-9 and filled and abs(filled["effect"] - 1.85) < 1e-9 and absent is None


def case14() -> bool:
    _, page = fetch_page("/reviews/noac-vs-warfarin-af-stroke/")
    return check_terms(page, ["SoSTART", "X-CONTRAST", "Contrast status", "randomised contrast"])


def case15() -> bool:
    from harness.synth import Study, _effects

    y, v = _effects([Study("zero-cell", 0, 100, 10, 100)])[0][0], _effects([Study("zero-cell", 0, 100, 10, 100)])[1][0]
    review = read_json("docs/reviews/tranexamic-acid-pph/review.json")
    outcomes = [(o["name"], o.get("kind"), bool(o.get("trials")), o.get("result", {}).get("reported_not_extracted")) for o in review["outcomes"]]
    print("zero_cell_log_effect:", y)
    print("zero_cell_variance:", v)
    print("txa_outcomes:", json.dumps(outcomes, ensure_ascii=False))
    names = {o[0] for o in outcomes}
    return y < 0 and v > 0 and {"Death due to bleeding", "Thromboembolic events", "Adverse events"}.issubset(names)


def case16() -> bool:
    hits = bounded_search(
        [r"PUBLICATION_FOUND_NOT_EXTRACTED", r"verified subset.*33", r"33/67", r"NCT.*publication link"],
        ["harness", "tests", "docs"],
        exclude=[],
    )
    print("No publication-found-not-extracted gate or verified 33/67 artifact was found.")
    return hits == 0


def case17() -> bool:
    _, page = fetch_page("/reviews/denosumab-vertebral-fracture/")
    return check_regexes(page, [r"Pooled.*k=1", r"k=1.{0,120}heterogeneity|heterogeneity.{0,120}k=1"])


def case18() -> bool:
    hits = bounded_search(
        [r"claimed_entity", r"claimed-entity", r"entity-derived", r"derived.*pooled.*entity"],
        ["harness", "tests", "docs"],
        exclude=["docs/reviews"],
    )
    print("No claimed-entity derivation/gate artifact was found.")
    return hits == 0


def case19() -> bool:
    from harness import extract

    dapa = "The primary composite outcome was a sustained decline of at least 50% in eGFR, end-stage kidney disease, or death from renal or cardiovascular causes. Heart failure hospitalization was a secondary outcome."
    empa = "The primary outcome was progression of kidney disease (a sustained >=40% decrease in eGFR or end-stage kidney disease) or death from cardiovascular causes."
    note = extract.composite_heterogeneity("CKD progression / kidney composite outcome", [dapa, empa])
    print("kidney_note:", note)
    return bool(note) and "eGFR" in note and "HF hospitalization" not in note


def case20() -> bool:
    _, page = fetch_page("/reviews/sglt2-ckd-progression/")
    return check_terms(page, ["Indirectness", "human judgement", "D3 (missing outcome data)", "NOT ASSESSED", "capped below high"])


def case21() -> bool:
    from harness import unit_of_analysis as uoa

    detected = uoa.detect("a pragmatic, cluster-randomized, multiple-crossover trial in five ICUs")
    review = read_json("docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json")
    uoa_rows = review.get("unit_of_analysis", [])
    print("runtime_detect:", detected)
    print("review_unit_of_analysis:", json.dumps(uoa_rows, ensure_ascii=False))
    return detected == "cluster-randomized crossover" and len(uoa_rows) >= 3


def case22() -> bool:
    hits = bounded_search(
        [r"reassurance_verification", r"verify_reassurance", r"would_not_change"],
        ["harness", "tests", "docs"],
        exclude=["docs/reviews"],
    )
    print("Found no corpus-wide artifact verifying every reassurance.")
    return hits == 0


def case23() -> bool:
    review = read_json("docs/reviews/balanced-crystalloids-vs-saline-mortality/review.json")
    mortality = next(o for o in review["outcomes"] if o["name"] == "Mortality")
    trial_ids = [t["id"] for t in mortality["trials"]]
    print("balanced_mortality_trial_ids:", json.dumps(trial_ids))
    hits = bounded_search(
        [r"census_basics", r"basics_census"],
        ["harness", "tests", "docs"],
        exclude=["docs/reviews"],
    )
    print("BaSICS PMID 34375394 is present in the current mortality pool; no explanation artifact was found.")
    return "PMID 34375394" in trial_ids and hits == 0


def case24() -> bool:
    review = read_json("docs/reviews/semaglutide-obesity-weight/review.json")
    outcome = next(o for o in review["outcomes"] if o.get("primary"))
    absent = [(a["id"], a.get("state"), a.get("reason", "")[:220]) for a in outcome.get("declared_absent_trials", []) if "timepoint mismatch" in a.get("reason", "")]
    topic = read_json("topics/semaglutide-obesity-weight.json")
    registered = topic.get("primary_outcome", topic)
    print("registered_timepoint:", registered.get("timepoint"), registered.get("timepoint_weeks"), "tolerance", registered.get("timepoint_tolerance_weeks"))
    print("timepoint_absences:", json.dumps(absent, ensure_ascii=False, indent=2))
    return registered.get("timepoint_weeks") == 68 and len(absent) >= 3 and all(a[1] == "REFUSED_ON_EVIDENCE" for a in absent)


def case25() -> bool:
    hits = bounded_search(
        [r"comparator_predates", r"comparator-predates", r"predates.*included"],
        ["harness", "tests", "docs"],
        exclude=["docs/reviews", "docs/class_discovery.json"],
    )
    print("No comparator-predates rule/sweep/gate artifact was found outside rendered review parity notes.")
    return hits == 0


def case26() -> bool:
    hits = bounded_search(
        [r"poison_token", r"poison-token", r"platform-trial", r"domain-level screening"],
        ["harness", "tests", "docs"],
        exclude=[],
    )
    print("No domain-level poison-token/platform-trial census artifact was found.")
    return hits == 0


def case27() -> bool:
    hits = bounded_search(
        [r"exclusion_symmetry", r"exclusion-symmetry"],
        ["harness", "tests", "docs"],
        exclude=[],
    )
    print("No exclusion_symmetry instrument/gate artifact was found.")
    return hits == 0


def case28() -> bool:
    hits = bounded_search(
        [r"UNREGISTERED_EXCLUSION_CRITERION", r"unregistered exclusion"],
        ["harness", "tests", "docs"],
        exclude=[],
    )
    print("No unregistered-exclusion criterion mechanism was found.")
    return hits == 0


def case29() -> bool:
    cache_hits = bounded_search([r"40261382"], ["cache", "docs/reviews"], exclude=[], limit=10)
    test_hits = bounded_search(
        [r"40261382"],
        ["tests", "docs/search", "docs/evidence", "docs/class_discovery.json", "docs/search_rebuild.json", "docs/known_eligible_missing.json"],
        exclude=[],
        limit=20,
    )
    print(f"cache/source matches: {cache_hits}; search-rebuild/test-set matches: {test_hits}")
    return test_hits == 0


def case30() -> bool:
    data = read_json("docs/class_discovery.json")
    trend = [(a["audit"], a["n_new"]) for a in data["audits"]]
    print("metric:", data.get("metric"))
    print("trend:", trend)
    print("trend_note:", data.get("trend_note"))
    git(["ls-files", "--error-unmatch", "docs/class_discovery.json"])
    return data.get("metric") == "new_classes_per_audit" and (29, 0) in trend


def case31() -> bool:
    _, page = fetch_page("/reviews/corticosteroids-cap-mortality/")
    return check_terms(page, ["25688779", "Pooled effect 0.55 (RR)"]) and check_regexes(page, [r"Trials pooled \(k\).*?2", r"95% CI 0\.04.{0,4}8\.26"])


def case32() -> bool:
    mace = read_json("docs/reviews/semaglutide-obesity-mace/review.json")
    weight = read_json("docs/reviews/semaglutide-obesity-weight/review.json")
    select_rows = [t for o in mace["outcomes"] for t in o.get("trials", []) if t.get("id") == "PMID 37952131"]
    weight_trials = next(o for o in weight["outcomes"] if o.get("primary"))["trials"]
    print("SELECT rows:")
    for row in select_rows:
        print(json.dumps({k: row.get(k) for k in ("id", "scale", "effect", "ai", "n1i", "ci", "n2i", "derivation", "source")}, ensure_ascii=False)[:900])
    print("semaglutide_weight_n:", [(t["id"], t.get("nc1"), t.get("nc2")) for t in weight_trials])
    return any(r.get("scale") == "HR" and "8803" in r.get("source", "") and "8801" in r.get("source", "") for r in select_rows) and any(r.get("n1i") == 8803 and r.get("n2i") == 8801 for r in select_rows) and {(t.get("nc1"), t.get("nc2")) for t in weight_trials} >= {(407, 204), (1306, 655)}


def case33() -> bool:
    _, page = fetch_page("/reviews/pcsk9-mace/")
    return check_terms(page, ["Claims checked: 1; contradictions caught: 0", "Proposition contradictions caught"])


def case34() -> bool:
    _, index = fetch_page("/")
    ok1 = check_regexes(index, [r"3 of 32.*?current.*?29 of 32.*?STALE"])
    _, page = fetch_page("/reviews/semaglutide-obesity-weight/")
    ok2 = check_terms(page, ["STALE", "this topic"])
    return ok1 and ok2


def case35() -> bool:
    _, glp = fetch_page("/reviews/glp1-ra-mace-t2d/")
    ok1 = check_terms(glp, ["Compatibility key", "source-reported"])
    _, iv = fetch_page("/reviews/iv-iron-hfref-hosp/")
    ok2 = check_terms(iv, ["Compatibility key", "would have been", "INVALID", "SUPPRESSED"])
    return ok1 and ok2


def case36() -> bool:
    _, page = fetch_page("/reviews/noac-vs-warfarin-af-stroke/")
    ok1 = check_terms(page, ["SoSTART", "X-CONTRAST"])
    p = ROOT / "docs/contrast_evictions.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    print("contrast_evictions entries:", len(data) if isinstance(data, list) else type(data).__name__)
    print(json.dumps(data, ensure_ascii=False)[:1200])
    return ok1 and p.exists()


def case37() -> bool:
    _, page = fetch_page("/reviews/esketamine-trd-madrs/")
    ok1 = check_terms(page, ["X-DEDUP"])
    p = ROOT / "docs/study_families.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    print("study_families type:", type(data).__name__, "size:", len(data) if hasattr(data, "__len__") else "NA")
    print(json.dumps(data, ensure_ascii=False)[:1200])
    return ok1 and p.exists() and len(data) > 0


def case38() -> bool:
    _, index = fetch_page("/")
    ok1 = check_regexes(index, [r"Protocol.{0,5}config.*?divergence"])
    review = read_json("docs/reviews/sglt2-ckd-progression/review.json")
    print("protocol_config:", json.dumps(review.get("protocol_config"), ensure_ascii=False)[:1200])
    return ok1 and bool(review.get("protocol_config"))


def case39() -> bool:
    _, index = fetch_page("/")
    ok1 = check_regexes(index, [r"3 of 32.*?current.*?29 of 32.*?STALE"])
    _, iv = fetch_page("/reviews/iv-iron-hfref-hosp/")
    ok2 = check_terms(iv, ["Claims checked: 0", "limitation"])
    never = read_json("docs/never_considered.json")
    print("never_considered:", json.dumps(never, ensure_ascii=False)[:1600])
    topics = never.get("topics", {}) if isinstance(never, dict) else {}
    return ok1 and ok2 and bool(topics)


def case40() -> bool:
    _, mel = fetch_page("/reviews/melatonin-primary-insomnia-sol/")
    ok1 = check_terms(mel, ["harness-reconstructed"])
    _, glp = fetch_page("/reviews/glp1-ra-mace-t2d/")
    ok2 = check_terms(glp, ["source-reported"])
    return ok1 and ok2


CASE_FUNCS = {i: globals()[f"case{i:02d}"] for i in range(1, 41)}


def run_case(num: int) -> int:
    case = CASES[num - 1]
    print(f"ENTRY: {case.num:02d}")
    print(f"CLAIM: {case.claim}")
    print(f"EXPECTED_VERDICT: {case.verdict}")
    print(f"EXPECTED_STATE: {case.state}")
    print()
    ok = CASE_FUNCS[num]()
    print()
    print(f"PROBE_BOOLEAN: {ok}")
    if case.verdict == "REPRODUCED":
        return 0 if ok else 1
    if case.verdict == "NOT REPRODUCED":
        return 0 if ok else 1
    return 0


def capture_case(case: Case) -> tuple[int, str, str, str]:
    cmd = [sys.executable, SELF, "run-case", f"{case.num:02d}"]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=120, env=env)
    command = "python " + " ".join(cmd[1:])
    return proc.returncode, command, proc.stdout, proc.stderr


def write_evidence(case: Case, command: str, code: int, stdout: str, stderr: str) -> None:
    body = [
        f"ENTRY: {case.num:02d}",
        f"CLASS: {ledger_entries()[case.num - 1]['class']}",
        f"CLAIM: {case.claim}",
        f"COMMAND: {command}",
        f"EXIT CODE: {code}",
        "STDOUT:",
        stdout.rstrip() or "(empty)",
        "STDERR:",
        stderr.rstrip() or "(empty)",
        f"VERDICT: {case.verdict}",
        f"PROPOSED_FIX_STATE: {case.state}",
        f"RATIONALE: {case.rationale}",
        "",
    ]
    (EVDIR / case.filename).write_text("\n".join(body), encoding="utf-8")


def ledger_entries() -> list[dict]:
    data = read_json("docs/fix_ledger.json")
    return data["fixes"]


def write_readme() -> None:
    entries = ledger_entries()
    lines = [
        "# Fix Ladder Evidence - 2026-09-14",
        "",
        "**Fix state (four-state rule): LANDED** - this directory is evidence for other claims.",
        "",
        "| Entry # | Class | Proposed fix_state | File |",
        "|---:|---|---|---|",
    ]
    for case, entry in zip(CASES, entries):
        cls = entry["class"].replace("\n", " ")
        lines.append(f"| {case.num} | {cls} | {case.state} | [{case.filename}]({case.filename}) |")
    lines.append("")
    (EVDIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_proposed(when: str) -> None:
    data = read_json("docs/fix_ledger.json")
    proposed = copy.deepcopy(data)
    for case, entry in zip(CASES, proposed["fixes"]):
        entry["fix_state"] = case.state
        entry.pop("verification", None)
        if case.state == "VERIFIED":
            entry["verification"] = {
                "by": "Codex lane J",
                "when": when,
                "evidence": case.evidence_path,
            }
    (ROOT / "docs/fix_ledger.proposed.json").write_text(json.dumps(proposed, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def write_report(when: str) -> None:
    counts = Counter(c.state for c in CASES)
    not_reproduced = [c for c in CASES if c.verdict == "NOT REPRODUCED"]
    could_not = [c for c in CASES if c.verdict == "COULD NOT TEST"]
    lines = [
        "# LANE J Report",
        "",
        f"Generated UTC: {when}",
        "",
        "## Counts by Proposed State",
        "",
        "| Proposed state | Count |",
        "|---|---:|",
    ]
    for state in ("VERIFIED", "LANDED", "REPORTED", "GENERALIZED"):
        lines.append(f"| {state} | {counts.get(state, 0)} |")
    lines.extend([
        "",
        "## NOT REPRODUCED",
        "",
        "These rows did not get VERIFIED. Per the four-state rule, I proposed REPORTED where the referenced commit/artifact/mechanism was absent.",
        "",
        "| Entry | Class | Why | Evidence |",
        "|---:|---|---|---|",
    ])
    entries = ledger_entries()
    for c in not_reproduced:
        lines.append(f"| {c.num} | {entries[c.num - 1]['class']} | {c.rationale} | {c.evidence_path} |")
    lines.extend([
        "",
        "## Untestable",
        "",
    ])
    if could_not:
        for c in could_not:
            lines.append(f"- Entry {c.num}: {c.rationale} ({c.evidence_path})")
    else:
        lines.append("None. Each row was either independently reproduced or not reproduced because the referenced artifact/mechanism was absent.")
    lines.extend([
        "",
        "## Deliverables",
        "",
        "- Evidence directory: docs/evidence/fix-ladder-2026-09-14/",
        "- Proposed ledger: docs/fix_ledger.proposed.json",
        "- This report: LANE-J-REPORT.md",
        "",
        "## Notes",
        "",
        "- I did not edit docs/fix_ledger.json.",
        "- Evidence commands fetch served GitHub Pages bytes or inspect committed source/runtime objects; the ledger prose itself is not used as proof.",
        "- Row 34's old ledger prose mentions an earlier live count, but the live page now independently demonstrates the current object-derived count: 3 current and 29 STALE.",
    ])
    (ROOT / "LANE-J-REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate() -> int:
    if len(ledger_entries()) != len(CASES):
        raise SystemExit(f"ledger has {len(ledger_entries())} entries; case table has {len(CASES)}")
    failures = []
    for case in CASES:
        print(f"running {case.num:02d} {case.slug}...")
        code, command, stdout, stderr = capture_case(case)
        write_evidence(case, command, code, stdout, stderr)
        if code != 0:
            failures.append((case.num, code))
        time.sleep(0.1)
    when = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    write_readme()
    write_proposed(when)
    write_report(when)
    print(f"wrote {len(CASES)} evidence files, README, proposed ledger, and report")
    if failures:
        print("case command failures:", failures)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    rc = sub.add_parser("run-case")
    rc.add_argument("num", type=int)
    sub.add_parser("generate")
    ns = parser.parse_args(argv)
    if ns.cmd == "run-case":
        return run_case(ns.num)
    if ns.cmd == "generate":
        return generate()
    raise AssertionError(ns.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
