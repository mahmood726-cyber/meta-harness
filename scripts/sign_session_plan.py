"""Build the plan for ONE signing sitting (scripts/sign_session.py): every item Mahmood is asked to act on, in order.

  python scripts/sign_session_plan.py --signing-json FILE --decisions FILE --out PLAN.json
        [--glp1-ref origin/main] [--rulings FILE]

Items, each clearly labelled by kind:
  notice  a result-change notice to countersign (from the signing list: plain before -> after, the exact digest and
          judgement the sign command checks). Notices in decisions["hold"] or decisions["exclude"] (e.g. those
          the V1 fix removes or changes) are NOT in the plan; notices in
          decisions["ruling"] are, labelled as rulings, and are only signed if he accepts the ruling.
  bundle  the GLP-1 MACE FLOW/ELIXA/FREEDOM-CVO admission request (evidence/glp1_adjudication/SIGNATURE_REQUEST.md
          at --glp1-ref): the bound files, their sha256 and the bundle sha256, recomputed here from committed bytes
          exactly as make_signature_request.py computes it; the session recomputes it again before recording.
  ruling  a protocol-scope ruling (e.g. DELIVER's registry wording) from --rulings: a question, what "yes" and "no"
          each change; recorded as his decision, never as a notice signature.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import v1_final_list  # noqa: E402

GLP1_DIR = "evidence/glp1_adjudication"
GLP1_BOUND = [f"{GLP1_DIR}/FLOW.json", f"{GLP1_DIR}/ELIXA.json", f"{GLP1_DIR}/FREEDOM-CVO.json",
              f"{GLP1_DIR}/BEFORE_AFTER.json", f"{GLP1_DIR}/compute_before_after.py", f"{GLP1_DIR}/build_decisions.py",
              "docs/reviews/glp1-ra-mace-t2d/review.json", "protocols/glp1-ra-mace-t2d.md",
              "outputs/handover/lanes/DECISION_CLASS_BOUNDARY_STRANDS.md"]


def show(ref: str, path: str) -> bytes:
    p = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"refused: cannot read {ref}:{path}")
    return p.stdout


def glp1_bundle(ref: str) -> tuple[str, list[dict]]:
    """The bundle sha256 exactly as evidence/glp1_adjudication/make_signature_request.py computes it."""
    files = [{"path": p, "sha256": hashlib.sha256(show(ref, p)).hexdigest()} for p in GLP1_BOUND]
    manifest = "\n".join(f"{f['sha256']}  {f['path']}" for f in files)
    return hashlib.sha256(manifest.encode()).hexdigest(), files


def glp1_item(ref: str) -> dict:
    commit = subprocess.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()
    request = show(commit, f"{GLP1_DIR}/SIGNATURE_REQUEST.md").decode("utf-8")
    stated = re.search(r"Bundle sha256 \(sign this\): `([0-9a-f]{64})`", request)
    bundle, files = glp1_bundle(commit)
    if not stated or stated.group(1) != bundle:
        raise SystemExit(f"refused: the GLP-1 request at {commit[:12]} states bundle "
                         f"{stated.group(1) if stated else None} but its bound bytes hash to {bundle}; the evidence "
                         "lane must regenerate it (make_signature_request.py)")
    ba = json.loads(show(commit, f"{GLP1_DIR}/BEFORE_AFTER.json"))
    b = ba["served_before"]
    a = ba["after"]["CONVENTIONAL_GLP1RA (primary strand): + FLOW + ELIXA"]
    fmt = lambda r: f"k={r['k']}, HR {r['estimate']} ({r['ci_low']} to {r['ci_high']})"  # noqa: E731
    return {"kind": "bundle", "id": "GLP1-FLOW-ELIXA", "label": "GLP-1 MACE: admit FLOW and ELIXA (and FREEDOM-CVO "
            "on the any-delivery strand)", "source_commit": commit, "bundle_sha256": bundle, "bound_files": files,
            "lines": [f"Served now: {fmt(b)}", f"After (primary strand, + FLOW + ELIXA): {fmt(a)}",
                      "Conclusion unchanged (still significant, same direction); heterogeneity rises (tau2 0.0027) "
                      "and the prediction interval widens.",
                      "FREEDOM-CVO enters only the GLP1RA_ANY_DELIVERY strand; the request asks you to confirm that "
                      "strand pair (the class-boundary decision still lists it as proposed).",
                      f"Full request: {GLP1_DIR}/SIGNATURE_REQUEST.md at {commit[:12]}"],
            "record_path": "signatures/GLP1_MACE_FLOW_ELIXA.json"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--signing-json", required=True)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--glp1-ref", default="origin/main")
    ap.add_argument("--rulings")
    args = ap.parse_args(argv)
    sl = json.loads(Path(args.signing_json).read_text(encoding="utf-8"))["rows"]
    audit = {r["audit_id"]: r for r in json.loads((ROOT / "registry/notice_adjudication.json")
                                                   .read_text(encoding="utf-8"))["notices"]}
    dec = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
    hold, ruling, exclude = dec.get("hold") or {}, dec.get("ruling") or {}, dec.get("exclude") or {}
    known = {r["audit_id"] for r in sl}
    if (set(hold) | set(ruling) | set(exclude)) - known:
        raise SystemExit(f"refused: decisions name notices not on the signing list: "
                         f"{sorted((set(hold) | set(ruling) | set(exclude)) - known)}")
    items = []
    for r in sl:
        if r["state"] != "OPEN" or r["audit_id"] in hold or r["audit_id"] in exclude:
            continue
        cmd = r["command"]
        items.append({"kind": "notice", "id": r["audit_id"],
                      "label": ("RULING, then sign if you accept: " + ruling[r["audit_id"]]) if r["audit_id"] in ruling
                      else "Countersign this result-change notice",
                      "plain": v1_final_list.plain(audit[r["audit_id"]]),
                      "slug": r["slug"], "outcome": r["outcome"], "ledger_index": r["ledger_index"],
                      "expect_digest": r["rendered_block_sha256"], "judgement": r["judgement_id"],
                      "printed_command": cmd})
    items.sort(key=lambda i: i["id"] in ruling)  # plain notices first, then those that hinge on a ruling
    items.append(glp1_item(args.glp1_ref))
    if args.rulings:
        for q in json.loads(Path(args.rulings).read_text(encoding="utf-8")):
            items.append(dict(q, kind="ruling", record_path="signatures/RULINGS.json"))
    plan = {"held_not_in_session": hold, "excluded_not_in_session": exclude, "items": items}
    Path(args.out).write_bytes((json.dumps(plan, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    counts = {k: sum(i["kind"] == k for i in items) for k in ("notice", "bundle", "ruling")}
    print(f"plan: {counts['notice']} notices, {counts['bundle']} bundle, {counts['ruling']} rulings; "
          f"{len(hold)} held and {len(exclude)} excluded (not in the session) -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
