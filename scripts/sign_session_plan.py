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
  ruling  a protocol-scope ruling (e.g. PRESERVED-HF's registry wording) from --rulings: a question, what "yes" and "no"
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


def notice_item(r: dict, audit: dict, section: str, label: str) -> dict:
    row = audit[r["audit_id"]]
    tag = (f"RE-ISSUED (replaces {row['supersedes_audit_id']})" if row.get("supersedes_audit_id")
           else ("RE-ISSUED" if r["audit_id"].startswith("V1-") else "AS-IS"))
    return {"kind": "notice", "section": section, "id": r["audit_id"], "status": tag, "label": label,
            "plain": v1_final_list.plain(row), "slug": r["slug"], "outcome": r["outcome"],
            "ledger_index": r["ledger_index"], "expect_digest": r["rendered_block_sha256"],
            "judgement": r["judgement_id"], "printed_command": r["command"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--signing-json", required=True)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--config", required=True, help="session_config.json: GLP-1 intent, evid2 notices, PRESERVED-HF")
    ap.add_argument("--out", required=True)
    ap.add_argument("--glp1-ref", default="origin/main")
    ap.add_argument("--withdrawn", default="", help="comma-separated audit ids withdrawn in the candidate (info only)")
    args = ap.parse_args(argv)
    sl = json.loads(Path(args.signing_json).read_text(encoding="utf-8"))["rows"]
    audit = {r["audit_id"]: r for r in json.loads((ROOT / "registry/notice_adjudication.json")
                                                   .read_text(encoding="utf-8"))["notices"]}
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    dec = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
    hold, ruling, exclude = dec.get("hold") or {}, dec.get("ruling") or {}, dec.get("exclude") or {}
    known = {r["audit_id"] for r in sl}
    if (set(hold) | set(ruling) | set(exclude)) - known:
        raise SystemExit(f"refused: decisions name notices not on the signing list: "
                         f"{sorted((set(hold) | set(ruling) | set(exclude)) - known)}")
    open_rows = [r for r in sl if r["state"] == "OPEN" and r["audit_id"] not in hold and r["audit_id"] not in exclude]
    by_outcome = {(r["slug"], r["outcome"]): r for r in open_rows}
    items: list[dict] = []
    # 1. GLP-1 k=10 primary, previous k=8 on the same page; intent as relayed; the ELIXA dispute in its line.
    #    If the release defers it (cfg glp1.pending_for), it is a Part B item; a stale request is information, never
    #    a reason for the plan to fail.
    pending = cfg["glp1"].get("pending_for")
    try:
        g = glp1_item(args.glp1_ref)
        g.update(section="1 GLP-1", label=cfg["glp1"]["label"], intent=cfg["glp1"]["intent"])
        g["lines"] = [g["lines"][0], g["lines"][1],
                      "The page shows the previous k=8 result beside the new k=10 primary.",
                      "ELIXA: " + cfg["glp1"]["elixa_dispute"],
                      f"Your approval in chat, as relayed: \"{cfg['glp1']['intent']['quote']}\" (recorded as intent; "
                      "this item asks you to sign it)."] + g["lines"][2:]
    except SystemExit as why:
        g = {"kind": "info", "section": "1 GLP-1", "id": "GLP1-FLOW-ELIXA", "label": cfg["glp1"]["label"] +
             " -- NOT SIGNABLE NOW", "lines": [str(why), "ELIXA: " + cfg["glp1"]["elixa_dispute"]]}
    if pending:
        g["label"] = f"PENDING for {pending} (not in this release; the served page stays k=8): " + g["label"]
        g["part"] = "B"
    items.append(g)
    # 2. the re-derived notices: as-is first, then re-issued; ruling-dependent last; withdrawn shown as information
    special = {(e["slug"], e["outcome"]) for e in cfg["evid2_notices"]}
    ph = cfg["preserved_hf"]
    special.add((ph["consequence"]["slug"], ph["consequence"]["outcome"]))
    sec2 = [notice_item(r, audit, "2 re-derived notices",
                        ("RULING, then sign if you accept: " + ruling[r["audit_id"]]) if r["audit_id"] in ruling
                        else "Countersign this result-change notice")
            for r in open_rows if (r["slug"], r["outcome"]) not in special]
    sec2.sort(key=lambda i: (i["id"] in ruling, i["status"] != "AS-IS"))
    items += sec2
    for w in [x for x in args.withdrawn.split(",") if x]:
        items.append({"kind": "info", "section": "2 re-derived notices", "id": w,
                      "label": f"{w} is WITHDRAWN in the candidate: its change no longer happens, so there is nothing "
                               "to sign", "lines": [f"{w} was: {audit[w]['before']} -> {audit[w]['after']}"
                                                    if w in audit else f"{w}: withdrawn"]})
    # 3. evid2's derived notices, matched by (review, outcome) in the candidate's signing list
    for e in cfg["evid2_notices"]:
        r = by_outcome.get((e["slug"], e["outcome"]))
        if r:
            it = notice_item(r, audit, "3 evid2", e["label"])
            it["plain"] += f"\n- Expected by evid2: {e['expected']}\n- Decision record: {e['decision_record']}"
            if e.get("overlaps"):
                it["plain"] += f"\n- Note: {e['overlaps']}"
            items.append(it)
        else:
            items.append({"kind": "info", "section": "3 evid2", "id": e["id"],
                          "label": e["label"] + " -- NOT IN THIS CANDIDATE: no notice exists yet, nothing to sign",
                          "lines": [f"Expected: {e['expected']}", f"Decision record: {e['decision_record']}"]})
    # 4. PRESERVED-HF: the wording ruling (intent as relayed), then its consequence
    items.append({"kind": "ruling", "section": "4 PRESERVED-HF", "id": ph["id"], "label": ph["label"],
                  "question": ph["question"], "if_yes": ph["if_yes"], "if_no": ph["if_no"],
                  "prior_intent": ph["prior_intent"], "record_path": "signatures/RULINGS.json"})
    r = by_outcome.get((ph["consequence"]["slug"], ph["consequence"]["outcome"]))
    if r:
        items.append(notice_item(r, audit, "4 PRESERVED-HF", "PRESERVED-HF consequence: sign only if you did NOT "
                                 "accept the ruling above (if you accepted it, this change should not happen -- say n)"))
    else:
        items.append({"kind": "info", "section": "4 PRESERVED-HF", "id": "PRESERVED-HF-consequence",
                      "label": "PRESERVED-HF consequence: the candidate has no notice on dapagliflozin HFpEF adverse "
                               "events -- PRESERVED-HF is readmitted and that change no longer happens",
                      "lines": ["Nothing to sign."]})
    # Parts: A = every item the candidate's own pages need signed for the gate (its OPEN notices, and the ruling
    # that decides one of them); B = pending items that do not change this release. Held notices that are OPEN in
    # the candidate cannot be signed today and keep the gate red: say so first.
    in_cand = {i["id"] for i in items if i["kind"] == "notice"}
    for i in items:
        if "part" not in i:
            i["part"] = "A" if i["kind"] == "notice" or i["id"] in args.withdrawn.split(",") else "B"
    if r and r["audit_id"] in in_cand:
        for i in items:
            if i["id"] == ph["id"]:
                i["part"] = "A"
    if hold:
        items.insert(0, {"kind": "info", "part": "A", "section": "0 deploy warning", "id": "HELD-OPEN",
                         "label": f"{len(hold)} notice(s) in this candidate are HELD and cannot be signed today; the "
                                  "gate stays red for them until the release captain re-words or withdraws them",
                         "lines": [f"{k}: {v[:160]}" for k, v in sorted(hold.items())]})
    items = [i for i in items if i["part"] == "A"] + [i for i in items if i["part"] == "B"]
    plan = {"held_not_in_session": hold, "excluded_not_in_session": exclude, "withdrawn": args.withdrawn, "items": items}
    Path(args.out).write_bytes((json.dumps(plan, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    counts = {k: sum(i["kind"] == k for i in items) for k in ("notice", "bundle", "ruling", "info")}
    counts["partA"] = sum(i["part"] == "A" and i["kind"] != "info" for i in items)
    counts["partB"] = sum(i["part"] == "B" and i["kind"] != "info" for i in items)
    print(f"plan: {counts}; {len(hold)} held and {len(exclude)} excluded (not in the session) -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
