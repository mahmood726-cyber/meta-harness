"""Write the phone-readable FINAL signing list for Mahmood from a sign branch (run in a checkout of it).

  python scripts/v1_final_list.py --signing-json FILE --decisions FILE --branch <sign branch> --out FILE.md
        [--clone C:\\mh-sign-v1] [--push-branch sign/mahmood-v1]

--signing-json: output of scripts/notice_signing_list.py on the sign branch (rows with the exact commands).
--decisions: the lane's JSON {"hold": {audit_id: why}, "ruling": {audit_id: question}}; every other OPEN notice is
listed to sign. Nothing here signs; the commands are copied verbatim from the signing list, which the walker and
`sign` both re-check (hash, judgement, anchors) at the moment he runs them.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WHY = {"ENTRY_POPULATION_NOT_ESTABLISHED": "its registry record doesn't name the review's patient group",
       "REGISTRY_PARENT_UNRESOLVED": "no trial-registry record is linked to it",
       "INSUFFICIENT_PICD_EVIDENCE": "it is registered outside ClinicalTrials.gov, which the check cannot read",
       "INTERVENTION_CONTRAST_NOT_PROVEN": "its registered arms don't show the comparison",
       "PLACEBO_CONTROL_NOT_PROVEN": "its control is not shown to be a placebo",
       "BLINDING_NOT_PROVEN": "its blinding is not shown",
       None: "the registry says it is not randomised"}


def num(x):
    return f"{x:.2f}"


def res(t, scale):
    if not t or not t.get("k"):
        return "no pooled result"
    if t.get("estimate") is None:
        return f"no pooled number ({t['k']} trials)"
    trials = f"{t['k']} trial" + ("s" if t["k"] != 1 else "")
    if t.get("ci_low") is None:
        return f"{scale} {num(t['estimate'])}, no interval ({trials})"
    return f"{scale} {num(t['estimate'])} ({num(t['ci_low'])} to {num(t['ci_high'])}), {trials}"


def plain(row: dict) -> str:
    scale = row.get("scale_before") or row.get("scale_after") or ""
    why: dict[str, list[str]] = {}
    for t in row.get("departing_trials") or []:
        why.setdefault(WHY.get(t.get("absence_code"), t.get("absence_code") or "set aside"), []).append(t["trial_id"])
    entered = row.get("entered_pool") or []
    reasons = "; ".join(f"{len(v)} because {k} ({', '.join(v)})" for k, v in why.items())
    lines = [f"**{row['audit_id']}**: {row['slug'].replace('-', ' ')}, *{row['outcome']}*",
             f"- Served now: {res(row.get('before'), scale)}",
             f"- After: {res(row.get('after'), row.get('scale_after') or scale)}"]
    if reasons:
        lines.append(f"- Why: {len(row.get('departing_trials') or [])} trial(s) set aside: {reasons}.")
    if entered:
        lines.append(f"- Entered the pool: {', '.join(entered)}.")
    if not reasons and not entered:
        lines.append("- Why: the pooled number changed with no trial entering or leaving; read the notice's own reason.")
    if row.get("supersedes_audit_id"):
        lines.append(f"- New in V1: it replaces {row['supersedes_audit_id']}, which the V1 fix changed.")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--signing-json", required=True)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--branch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--clone", default=r"C:\mh-sign-v1")
    ap.add_argument("--push-branch", default="sign/mahmood-v1")
    args = ap.parse_args(argv)
    sl = {r["audit_id"]: r for r in json.loads(Path(args.signing_json).read_text(encoding="utf-8"))["rows"]}
    audit = {r["audit_id"]: r for r in json.loads((ROOT / "registry/notice_adjudication.json").read_text(encoding="utf-8"))["notices"]}
    dec = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
    hold, ruling = dec.get("hold") or {}, dec.get("ruling") or {}
    unknown = (set(hold) | set(ruling)) - set(sl)
    if unknown:
        raise SystemExit(f"refused: decisions name notices not on the signing list: {sorted(unknown)}")
    open_ids = [a for a, r in sl.items() if r["state"] == "OPEN"]
    sign = [a for a in open_ids if a not in hold and a not in ruling]
    head = f"""# FINAL signing list: result-change notices for V1

**Mahmood: {len(sign)} to sign, {len(hold)} to hold, {len(ruling)} need your ruling.** Nothing here is signed. A lane
cannot sign these notices, and the delegated bulk acceptance does not cover them.

## Run it on your laptop, in the clone `{args.clone}`
In Windows PowerShell, once:
```
git clone --filter=blob:none --no-checkout --branch {args.branch} https://github.com/mahmood726-cyber/meta-harness.git {args.clone}
cd {args.clone}
git sparse-checkout set --no-cone '/*' '!/*/' '/harness/' '/scripts/' '/tests/' '/registry/' '/topics/' '/protocols/' '/docs/result_changes.json' '/docs/reviews/*/review.json' '/docs/reviews/*/index.html' '/cache/spironolactone-hfref-mortality/records.json' '/signatures/'
git checkout {args.branch}
git switch -c {args.push_branch}
python -m pip install -r requirements.txt
```
For each notice:
1. Read it: `python scripts/sign_walk.py --notice ID`
2. If you accept it, run its one-line command exactly as written below. It asks for your own account of what you
   read. It refuses, and writes nothing, if the notice's hash or version anchor has moved.

When you have finished, push once:
```
git add docs/result_changes.json
git commit -m "Countersign V1 result-change notices (Mahmood, laptop clone {args.clone})"
git push -u origin {args.push_branch}
```
Then say "pushed". Lane NR checks every signature from the pushed bytes.
"""
    out = [head, f"## A. Sign ({len(sign)})\n"]
    for a in sign:
        r = sl[a]
        out.append(plain(audit[a]) + f"\n- Hash: `{r['rendered_block_sha256']}`\n- Version anchor: judgement "
                   f"`{r['judgement_id']}`\n```\n{r['command']}\n```\n")
    if hold:
        out.append(f"## B. Hold ({len(hold)}): don't sign these yet\n")
        out += [plain(audit[a]) + f"\n- Hold because: {why}\n" for a, why in hold.items()]
    if ruling:
        out.append(f"## C. Your ruling first ({len(ruling)})\n")
        out += [plain(audit[a]) + f"\n- Question: {q}\n- If you accept, sign with:\n```\n{sl[a]['command']}\n```\n"
                for a, q in ruling.items()]
    Path(args.out).write_bytes("\n".join(out).encode("utf-8"))
    print(f"{len(sign)} to sign, {len(hold)} hold, {len(ruling)} ruling -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
