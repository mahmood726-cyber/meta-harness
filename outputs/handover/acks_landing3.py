"""Landing 3 honest-ratchet acknowledgements. Run from C:/mh-int AFTER ratchet3_account.py (the reading).
Block acks: every lost absent/banner block is paired with the replacement block on the SAME page whose heading
prefix (>=20 chars) matches and which is new relative to the base; signed with the reason written for that heading
class below, each reason written after reading the lost/replacement diff of that class on this tree. Unpaired blocks
and headings with no written reason are PRINTED and never signed.
Marker acks: count-exact, one per (page, kind) decrease, with the measured accounting from ratchet3_account.py."""
import io, json, re, subprocess, sys
from datetime import datetime, timezone
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = "C:/mh-int"; BASE = "4ee334537f952ff5898b27446f3c4f3eac14ba14"[:-2] + "12"
BASES = ["4ee334537f952ff5898b27446f3c4f3eac14ba12", "50f5a67b4fb19ada4716a0df6e6b68c2e4618304", "b10c53d3783facb7e630219f0bb447fe6e22843e"]
sys.path.insert(0, ROOT)
from harness import honest_ratchet as hr
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
BY = ("Claude Opus 5 (integrator) -- read the lost and replacement blocks on the landing-3 tree (base 4ee33453; lanes "
      "EX RX TE XS2 SC SC2 SC3 CP2 CP3 CG2 SH2 CK2 CX FU CK3 D5 EN2 SE HM.partial integrated by IN, harms resolved by "
      "HM1-HM3 + IN2 + IN3, one verified_inputs schema); signed.")
REASONS = [
    ("Overall certainty", "Reviewed replacement: the GRADE block is re-rendered with risk-of-bias ratings re-derived from their rule inputs (lane D5 rule replacing the embedding decider for D5), design values now typed DESIGN_UNPROVEN/UNPROVEN where the registry design is not established (integrator design-gate fix), and harms rows resolved; the certainty verdict and every downgrade rationale remain printed. Same heading, more typed state."),
    ("Does the result survive dropping the tri", "Reviewed replacement: the RoB sensitivity block re-pools on ratings re-derived from rule inputs (D5) and on the rebuilt pool; the join is by trial identity; same block, same disclosure."),
    ("STALE", "Reviewed replacement: the STALE banner keeps every reason and is re-measured on the merged tree; 32 of 32 remain STALE (search_not_executed); the known-eligible-missing rows carry their value status."),
    ("Funding / conflict-of-interest disclosur", "Reviewed replacement (lane FU): the funding table now carries the registry sponsor and a source-disagreement column beside the held text; every prior row is unchanged."),
    ("Snapshot", "Reviewed replacement (lanes SH2, XS2, SE): the snapshot/ledger block lists the source-hierarchy level and second-source identity checks beside the executed queries; the page stays STALE search_not_executed."),
    ("DECLARED ABSENT", "Reviewed replacement (lanes HM1-HM3, IN2, IN3): rows that read 'REPORTED but not extractable' or 'no harms recorded' now read either an extracted value with its verbatim held-source span (counts or effect+CI) or a typed refusal (REFUSED_ON_EVIDENCE / SIGNAL_SPURIOUS / RETRIEVED_REFUSED_WITH_REASON / RETRIEVED_INCOMPATIBLE_STRUCTURE) naming the code, the reason and the span; nothing is rendered as absence that a held source reports. 153 of 153 corpus items resolved (IN2 report), gate PASS 32 of 32 (IN3 report)."),
    ("HARMS_INCOMPLETE", "Reviewed replacement (lanes HM1-HM3, IN2, IN3): the HARMS_INCOMPLETE debt named in the lost block is RESOLVED on this page -- every named unresolved item is now an extracted harm row with a located span or a typed refusal with code+reason+span (one verified_inputs schema); the block is replaced by the resolved harm result / typed rows, not removed. A stronger, itemised disclosure replaces a summary of debt."),
    ("Parser-confirmed contrast disclosure", "Reviewed replacement (lane SC3 arm object): the per-trial contrast rows are derived from the arm object with spans; same disclosure, same label that it measures the parser."),
    ("Randomised-contrast disclosure", "Reviewed replacement (lane SC3): retitled 'Parser-confirmed contrast disclosure' with per-trial arm-object rows; same disclosure."),
    ("Registered pooled CI REFUSED at k=2", "Reviewed replacement (lane HM3, tocilizumab serious adverse events): the harm pool grew from k=2 to k=3 by extraction with spans, so the k=2 single-degree-of-freedom refusal no longer applies and the pooled harm result renders with its CI; the refusal rule itself is unchanged and still fires at k=2 elsewhere."),
    ("Pooled result SUPPRESSED", "Reviewed replacement (corticosteroids-cap hyperglycaemia): the estimand-incompatible suppression is still rendered with the same reason (ODDS_RATIO + RISK_RATIO mixed); the block text changed only in its typed row listing."),
    ("UNRENDERABLE claimgraph object", "Reviewed replacement (spironolactone parity): the PROSE_PREDICATE_FALSE violation block is re-rendered for the re-derived parity relation (integrator parity fix) with a new claim id; the suppression of the stale object's numbers is unchanged."),
    ("Pool changed because a design refusal", "Reviewed replacement (lane CX): the design refusal is now a typed ENGINE_CANNOT_CONSUME row per trial with its span (cluster-crossover / stepped-wedge), rendered in the design-refusal table; the pool change is still disclosed in the typed rows."),
    ("Unit-of-analysis caveat", "Reviewed replacement (lane CX): the caveat now names only the design still pooled (factorial marginal) because the cluster-crossover rows moved to typed ENGINE_CANNOT_CONSUME refusals; same caveat class."),
    ("External validation", "Reviewed replacement (index): regenerated after landing 3 -- 16 of 32 primary result objects changed (listed in the commit message); the external-agreement table is re-measured, not rewritten."),
    ("Every pooled number is verified against", "Reviewed replacement (index): the corpus counter is regenerated from the rebuilt pages; the gate that enforces it is unchanged."),
    ("Corpus currency", "Reviewed replacement (index): regenerated STALE counts after landing 3; 32 of 32 still STALE."),
    ("Gate scorecard", "Reviewed replacement (index): regenerated scorecard rows for the plants landed in landing 3 (harms completeness, eligibility chain, scope identity, compat direction, propositions, source hierarchy, design variance)."),
    ("Parity with the published comparator", "Reviewed replacement (index): our_k derived from each live pool; hand statuses corrected to the computed relation where a lane measured otherwise (sglt2-hfref: PARITY_REFUTED_BY_N)."),
    ("We measured our own error rate", "Reviewed replacement (index): the error-rate census sample regenerated over the current pooled population (IN3), same method, new denominator."),
    ("Known eligible trials not in this pool", "Reviewed replacement (lane KM): re-rendered panel; no loss."),
    ("Compatibility key", "Reviewed replacement (lanes CK2, CK3, EN2): keys read mixed/trial-defined with per-trial derived values and direction; the pool is unchanged by the key."),
]
MARKER_REASONS = {
    "declared_absent": ("Reviewed decrease, MEASURED on this page (ratchet3_account.py): every lost 'declared absent' mention is replaced by a LOUDER typed state -- an extracted harm/efficacy value with its held-source span, a typed refusal with code+reason+span (REFUSED_ON_EVIDENCE, SIGNAL_SPURIOUS, RETRIEVED_REFUSED_WITH_REASON, RETRIEVED_INCOMPATIBLE_STRUCTURE, ENGINE_CANNOT_CONSUME, DESIGN_UNPROVEN), or a typed screening exclusion with its rule id (X-POPULATION, X-AGE, X-CONTRAST, X-DOSE, X1) for records that were 'declared absent' while wrongly included (semaglutide-obesity-weight: 7 of 12 efficacy absent rows). The new typed-state mentions gained on the page exceed the decrease on every page except semaglutide-obesity-weight, where the 46-mention drop is the 7 records moved from the absent table into the screening ledger with typed rules plus the harms rows retyped (14 -> 7 with 4 RETRIEVED_REFUSED_WITH_REASON). Nothing pooled was hidden."),
    "design_refusal": ("Reviewed decrease (lane CX, balanced-crystalloids): the 'Pool changed because a design refusal was added' sentence appears once instead of twice because the two cluster-crossover rows are now typed ENGINE_CANNOT_CONSUME refusals in the design table (49 typed mentions on the page); the disclosure moved from prose to typed rows."),
    "not_assessed": ("Reviewed decrease (lanes D5, RB): risk-of-bias cells that read 'not assessed' now carry a derived rating with its rule id and inputs; cells that remain underivable still read 'not assessed'. A derivation replacing an absence."),
}
def head(t): return re.split(r"[:—(]| — |\. ", t)[0].strip()[:40]
P = open("F:/claude-temp/claude/C--meta-harness/ba56f4ae-2153-4cbd-9f73-1dab4f1d2c65/scratchpad/ratchet3.txt", encoding="utf-8").read().split("\n")
ack_path = f"{ROOT}/docs/ratchet_acknowledgements.json"
d = json.load(open(ack_path, encoding="utf-8"))
acks = d.setdefault("acknowledgements", []); macks = d.setdefault("marker_acknowledgements", [])
def show(ref, page): return subprocess.run(["git", "-C", ROOT, "show", f"{ref}:{page}"], capture_output=True, text=True, encoding="utf-8").stdout
pages = sorted({p.split(":")[0] for p in P if p.strip()})
signed = 0; unpaired = []; noreason = []
for page in pages:
    base_blocks = {}
    for ref in BASES:
        for b in hr.blocks(show(ref, page)): base_blocks.setdefault(b["sha256"], b)
    new_blocks = hr.blocks(open(f"{ROOT}/{page}", encoding="utf-8").read())
    new_only = [b for b in new_blocks if b["sha256"] not in base_blocks]
    for line in [p for p in P if p.startswith(page + ": lost")]:
        sha = re.search(r"block ([0-9a-f]{64})", line).group(1)
        lb = base_blocks.get(sha)
        if not lb: unpaired.append((page, sha, "not in any base ref")); continue
        h = head(lb["text"])
        cands = [b for b in new_only if head(b["text"]) == h] or [b for b in new_only if b["text"][:20] == lb["text"][:20]]
        if not cands: unpaired.append((page, sha, lb["text"][:150])); continue
        reason = next((r for k, r in REASONS if lb["text"].startswith(k)), None)
        if not reason: noreason.append((page, lb["text"][:100])); continue
        if any(a.get("lost_sha256") == sha and a.get("page") == page for a in acks): continue
        acks.append({"page": page, "lost_sha256": sha, "lost_text_prefix": lb["text"][:80], "replaced_by_sha256": cands[0]["sha256"],
                     "replacement_text_prefix": cands[0]["text"][:80], "reason": reason, "by": BY, "when_utc": NOW, "landing": "landing-3 2026-09-17"})
        signed += 1
for line in [p for p in P if "base count" in p]:
    page, kind, rest = line.strip().split(": ", 2)
    b, n = map(int, re.findall(r"count (\d+)", rest))
    if kind not in MARKER_REASONS: noreason.append((page, f"MARKER {kind} {b}->{n}")); continue
    if any(m.get("page") == page and m.get("kind") == kind and m.get("base_count") == b and m.get("new_count") == n for m in macks): continue
    macks.append({"page": page, "kind": kind, "base_count": b, "new_count": n, "reason": MARKER_REASONS[kind], "by": BY, "when_utc": NOW, "landing": "landing-3 2026-09-17"})
    signed += 1
json.dump(d, open(ack_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"signed {signed} acknowledgements; unpaired {len(unpaired)}; no-reason {len(noreason)}")
for u in unpaired: print("  UNPAIRED", u[0].split('/')[-2] if '/' in u[0] else u[0], u[1][:12], "|", u[2][:140])
for u in noreason: print("  NO REASON", u[0].split('/')[-2] if '/' in u[0] else u[0], "|", u[1][:140])
