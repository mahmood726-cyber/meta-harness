"""FINAL signing list for Mahmood: only notices that still exist, unchanged, after the proposed P5 fix."""
import json
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
B = W / "outputs/handover/lanes/nr-2026-09-25"
rows = {r["audit_id"]: r for r in json.loads((B / "signing_list.json").read_text(encoding="utf-8"))["rows"]}
audit = {r["audit_id"]: r for r in json.loads((W / "registry/notice_adjudication.json").read_text(encoding="utf-8"))["notices"]}
cat = json.loads(Path(r"C:/mh-lanes/nr/work/fix_category.json").read_text())
CLONE = r"C:\mh-sign"
BRANCH = "sign/mahmood-2026-09-25"

SIGN = ["N02", "N03", "N04", "N05", "N07", "N10", "N11", "N12", "N16", "N22", "N24", "N31", "N33", "N34", "N36",
        "N37", "N41"]
HOLD = {"N06": "the notice is the only place on the page that shows a harm number (RR 3.74) the page otherwise withholds",
        "N27": "the notice is the only place on the page that shows RR 1.23, and it gives no cause (no trial entered or left)",
        "N28": "it creates a new 'significant benefit' claim (HR 0.85, 0.78-0.93) but says 'direction unchanged'",
        "N38": "it creates a new 'significant benefit' claim (HR 0.70, 0.61-0.82) but says 'direction unchanged'"}
RULING = {"N08": "the control arm (saline) is registered as an active drug, so the check sees no contrast; the fix "
                 "does not change this. Do you accept the registry's coding as grounds to set the trial aside?",
          "N23": "the IV-iron arm is registered as plain 'iron' (not 'ferric carboxymaltose'); the fix does not "
                 "change this. Do you accept that as grounds to set the trial aside?"}
assert sorted(SIGN + list(HOLD) + list(RULING)) == sorted(a for a, c in cat.items() if c == "UNCHANGED")

WHY = {"ENTRY_POPULATION_NOT_ESTABLISHED": "its registry record doesn't name the review's patient group",
       "REGISTRY_PARENT_UNRESOLVED": "no trial-registry record is linked to it",
       "INSUFFICIENT_PICD_EVIDENCE": "it is registered outside ClinicalTrials.gov, which the check cannot read",
       "INTERVENTION_CONTRAST_NOT_PROVEN": "its registered arms don't show the comparison",
       None: "the registry record says it is not randomised (the record conflicts with the paper)"}


def num(x):
    return f"{x:.2f}"


def res(t, scale):
    if not t.get("k"):
        return "no pooled result"
    if t.get("estimate") is None:
        return f"no pooled number ({t['k']} trials)"
    trials = f"{t['k']} trial" + ("s" if t["k"] != 1 else "")
    if t.get("ci_low") is None:
        return f"{scale} {num(t['estimate'])}, no interval ({trials})"
    return f"{scale} {num(t['estimate'])} ({num(t['ci_low'])} to {num(t['ci_high'])}), {trials}"


def plain(aid):
    a = audit[aid]
    scale = a.get("scale_before") or a.get("scale_after") or ""
    why = {}
    for t in a["departing_trials"]:
        why.setdefault(WHY.get(t["absence_code"], t["absence_code"]), []).append(t["trial_id"])
    reasons = "; ".join(f"{len(v)} because {k} ({', '.join(v)})" for k, v in why.items())
    title = a["slug"].replace("-", " ")
    return (f"**{aid}**: {title}, *{a['outcome']}*\n"
            f"- Served now: {res(a['before'], scale)}\n"
            f"- After: {res(a['after'], a.get('scale_after') or scale)}\n"
            f"- Why: {len(a['departing_trials'])} trial(s) set aside: {reasons}.")


out = [f"""# FINAL signing list: result-change notices, 25 Sep 2026

**Mahmood: 17 to sign, 4 to hold, 2 need your ruling.** The other 18 of the 41 are **not** for signing: the
admission-check fix going into V1 removes 11 of them and changes 7.

Nothing here has been signed by anyone. A lane cannot sign these, and the delegated bulk acceptance does not cover
them.

## Run it on your laptop, in the clone `{CLONE}`
In Windows PowerShell, once:
```
git clone --filter=blob:none --no-checkout --branch nr/notice-anchors https://github.com/mahmood726-cyber/meta-harness.git {CLONE}
cd {CLONE}
git sparse-checkout set --no-cone '/*' '!/*/' '/harness/' '/scripts/' '/tests/' '/registry/' '/topics/' '/protocols/' '/docs/result_changes.json' '/docs/reviews/*/review.json' '/docs/reviews/*/index.html' '/cache/spironolactone-hfref-mortality/records.json'
git checkout nr/notice-anchors
git switch -c {BRANCH}
python -m pip install -r requirements.txt
```

For each notice below:
1. Read it: `python scripts/sign_walk.py --notice NXX`. This prints the exact block you sign, its hash, and every
   finding.
2. If you accept it, run its one-line sign command, copied exactly. It prompts you for your own account of what
   you read (`--basis`). It refuses and writes nothing if the notice's hash or version anchor has moved.

When you have finished, push once:
```
git add docs/result_changes.json
git commit -m "Countersign result-change notices (Mahmood, laptop clone {CLONE})"
git push -u origin {BRANCH}
```
Then say "pushed". The lane checks every signature from the pushed bytes: hash, judgement and your basis.
"""]
out.append("## A. Sign (17): each notice is the same before and after the V1 fix\n")
for aid in SIGN:
    r = rows[aid]
    out.append(plain(aid) + (f"\n- Note: {audit[aid]['recommendation_reason']}" if aid == "N37" else "")
               + f"\n- Hash: `{r['rendered_block_sha256']}`\n- Version anchor: judgement `{r['judgement_id']}`\n"
               f"```\n{r['command']}\n```\n")
out.append("## B. Hold (4): the notice exists, but its wording misstates the change. Don't sign until it's reworded\n")
for aid, why in HOLD.items():
    out.append(plain(aid) + f"\n- Hold because {why}.\n")
out.append("## C. Your ruling first (2): the check may be misreading the registry. The fix doesn't touch these\n")
for aid, q in RULING.items():
    r = rows[aid]
    out.append(plain(aid) + f"\n- Question: {q}\n- If you accept, sign with:\n```\n{r['command']}\n```\n")
out.append("## Not on this list (18)\n"
           "- **Removed by the V1 fix (11)**, because every trial they drop is readmitted: N09, N15, N17, N18, "
           "N19, N20, N21, N25, N32, N39, N40. The check was misreading data the site already holds.\n"
           "- **Changed by the V1 fix (7)**, to be regenerated and re-judged: N01, N13, N14, N26, N29, N30, N35.\n"
           "- **D01** (EMPHASIS-HF): not signable until you rule and the correction is made.\n")
text = "\n".join(out)
for dest in (Path(r"C:/mh-lanes/nr/FINAL_SIGNING_LIST_2026-09-25.md"), B / "FINAL_SIGNING_LIST.md"):
    dest.write_bytes(text.encode("utf-8"))
print(len(SIGN), len(HOLD), len(RULING), len(text))
