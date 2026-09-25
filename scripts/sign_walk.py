"""Present one audited result-change notice, then exit without signing or saving progress.

Run from the repository root using Windows PowerShell:
  python scripts/sign_walk.py
  python scripts/sign_walk.py --notice N20
  python scripts/sign_walk.py --position 19
  python scripts/sign_walk.py --notice D01

Positions are one-based in a fixed audit order, including notices subsequently signed.
Only an explicit invocation chooses another notice. Group rationale appears at the
first member; --show-group-reason repeats it when entering a group elsewhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import result_changes  # noqa: E402
from scripts import countersign_result_change as countersign  # noqa: E402
from scripts import notice_anchor  # noqa: E402

AUDIT = ROOT / "registry" / "notice_adjudication.json"


def ordered_notices(audit: dict) -> list[dict]:
    """Audit order within mandatory, shared-reason groups, then remaining notices."""
    rows = audit["notices"]
    by_id = {row["audit_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("duplicate audit_id in registry/notice_adjudication.json")
    ordered = [row for row in rows if row["individual_review_required_by_lane"]]
    used = {row["audit_id"] for row in ordered}
    group_ids = set()
    for group in audit["decision_groups"]:
        if group["group_id"] in group_ids or not group["members"]:
            raise ValueError("duplicate or empty decision group in registry/notice_adjudication.json")
        group_ids.add(group["group_id"])
        for member in group["members"]:
            if member not in by_id or member in used:
                raise ValueError(f"invalid/overlapping decision-group member {member}")
            row = by_id[member]
            if row["decision_group"] != group["group_id"]:
                raise ValueError(f"decision-group mismatch for {member}")
            ordered.append(row)
            used.add(member)
    ordered.extend(row for row in rows if row["audit_id"] not in used)
    return ordered


def load_walk() -> tuple[dict, list[dict], list[dict], dict[str, int]]:
    """Validate the audit against live source fields, allowing later signature acts.

    Signature fields never come from the audit and are never written here. Review
    and HTML source hashes bind its adjudication to the held source snapshot.
    """
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit["audit_progress"] != "complete":
        raise ValueError("registry/notice_adjudication.json audit is not complete")
    notices = json.loads(countersign.PATH.read_text(encoding="utf-8"))["notices"]
    chains = result_changes.chain_integrity(notices)
    if any(not chain["ok"] for chain in chains):
        raise ValueError("ledger chain integrity failed: " + "; ".join(
            f"{chain['slug']} / {chain['outcome']}: {', '.join(chain['problems'])}"
            for chain in chains if not chain["ok"]))
    mapping = {}
    # Decision B: every anchor names the version judged; a working-tree anchor refuses outright.
    for ref in audit["source_digests"]:
        notice_anchor.parse(ref)
    if audit["source_digests"] != notice_anchor.source_digest_map(audit):
        raise ValueError("source_digests are not exactly the anchors of the current judgements; "
                         "anchors change only by appending a judgement (scripts/notice_rejudge.py)")
    for row in audit["notices"]:
        matches = [i for i, notice in enumerate(notices)
                   if all(notice[k] == row[k] for k in ("slug", "outcome", "when_utc"))]
        if len(matches) != 1:
            raise ValueError(f"{row['audit_id']}: audit identity does not select exactly one live notice; refresh audit")
        index = matches[0]
        live = notices[index]
        # Compare every original notice field, including before/after notes and reason.
        fields = (set(live) | set(result_changes.REQUIRED) | {"before_note", "after_note", "reason_locked", "record_note"})
        if any(row.get(k) != live.get(k) for k in fields if k != "reviewer_countersignature"):
            raise ValueError(f"{row['audit_id']}: notice changed since registry/notice_adjudication.json; refresh audit")
        if set(result_changes.REQUIRED) - set(live):
            raise ValueError(f"{row['audit_id']}: incomplete notice")
        mapping[row["audit_id"]] = index
    # A new unaudited OPEN notice cannot silently disappear from this walk.
    for index, notice in enumerate(notices):
        state = (notice.get("reviewer_countersignature") or {}).get("state", "OPEN")
        if state not in result_changes.SIGNATURE_STATES:
            raise ValueError(f"ledger index {index}: unrecognised signature state")
        if state == "OPEN" and index not in mapping.values():
            raise ValueError(f"ledger index {index}: OPEN notice has no adjudication in registry/notice_adjudication.json; refresh audit")
    # Decision B, for every audited notice: each pinned anchor verifies (else DETACHED), and this tree still serves
    # what was judged -- the after tuple, the pooled membership, the signing digest and the rendered block in the
    # page (else STALE). Either refuses the whole walk; only an appended re-judgement clears it, never a digest edit.
    for row in audit["notices"]:
        notice = notices[mapping[row["audit_id"]]]
        _, block, sha = countersign._block_and_sha(notice)
        notice_anchor.guard(ROOT, row, notice, block, sha)
    ordered_notices(audit)  # Validate the complete queue before presenting a command.
    return audit, notices, chains, mapping


class _BlockText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_endtag(self, tag):
        if tag in ("h4", "div", "p"):
            self.parts.append("\n")


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _ps(value: str) -> str:
    """PowerShell literal quoting, including apostrophes and dollar/backtick text."""
    return "'" + value.replace("'", "''") + "'"


def d01() -> str:
    return ("D01 (J-EMPHASIS-HF): NOT SIGNABLE. The RR correction is not in the ledger because the change "
            "has not been made. Mahmood rules; the change is made; a notice is generated from the actual "
            "transition; only then does it become signable. This is a pending decision, not a notice or "
            "an empty signature slot. Source: outputs/findings-2026-09-22/PROPOSED_NOTICE_j-emphasis-hf.json (drafted, NOT raised) and DAY_REPORT_2026-09-22.md decision D01.")


def present(audit: dict, notices: list[dict], chains: list[dict], mapping: dict[str, int],
            position: int, show_group_reason: bool = False) -> str:
    ordered = ordered_notices(audit)
    if not 1 <= position <= len(ordered):
        raise ValueError(f"position must be between 1 and {len(ordered)} (audited notices)")
    row = ordered[position - 1]
    index = mapping[row["audit_id"]]
    notice = notices[index]
    chain = next(c for c in chains if (c["slug"], c["outcome"]) == (notice["slug"], notice["outcome"]))
    chain_position = chain["indices"].index(index) + 1
    _, block, sha = countersign._block_and_sha(notice)
    judgement, drifted = notice_anchor.guard(ROOT, row, notice, block, sha)
    lines = [f"Walk position {position} of {len(ordered)} audited notices (fixed order; no automatic advance).",
             f"{row['audit_id']}: {notice['slug']} / {notice['outcome']}",
             f"Judged version (decision B): judgement {judgement['judgement_id']} on {judgement['judged_utc']} -- "
             f"served page git:{judgement['served_commit'][:12]}, page carrying the notice "
             f"git:{judgement['proposed_commit'][:12]}; {len(judgement['anchors'])} of {len(judgement['anchors'])} "
             "commit-pinned anchors verified; this tree still serves the judged after, pooled membership and "
             "rendered block. Before -> after as judged: " + judgement["before_after"],
             ("Rebuilt since judgement (disclosed; the checks above still hold): " + "; ".join(drifted)) if drifted
             else "No judged file differs in this tree.",
             f"Ledger index {index} (zero-based); recorded {notice['when_utc']}.",
             f"Outcome chain: notice {chain_position} of {len(chain['indices'])} notices for this exact (slug, outcome)."]
    for offset, prior_index in enumerate(chain["indices"][:chain_position - 1], 1):
        sig = notices[prior_index].get("reviewer_countersignature") or {}
        if sig.get("state") in result_changes.SIGNED_STATES:
            lines.append(f"Earlier notice {offset} of {len(chain['indices'])} notices in this outcome chain: "
                         f"signed {sig.get('when_utc')} by {sig.get('by')} ({sig['state']}; recorded history).")
        else:
            lines.append(f"Earlier notice {offset} of {len(chain['indices'])} notices in this outcome chain: OPEN.")
    lines += [f"Before (ledger): {_json(notice['before'])}", f"After (ledger): {_json(notice['after'])}",
              f"Scale before / after (audit): {row['scale_before']} / {row['scale_after']}; "
              f"declared estimand: {row['declared_estimand']}; null value: {row['null_value']}.",
              f"Direction (harness-team audit): {row['direction']}. {row['direction_explanation']}",
              f"Departing trials (ledger): {', '.join(notice['left_pool']) or 'none'}",
              f"Entering trials (ledger): {', '.join(notice['entered_pool']) or 'none'}",
              f"Mechanism (harness-team audit): {row['mechanism']}. {row['mechanism_detail']}"]
    mandatory = row["individual_review_required_by_lane"]
    lines.append("Mandatory individual review (audit): " + ("YES" if mandatory else "no lane flag")
                 + "; triggers: " + (", ".join(row["individual_review_triggers"]) or "none"))
    if row["additional_individual_review_reason"]:
        lines.append("Additional individual review reason (harness team): " + row["additional_individual_review_reason"])
    lines.append("Gate signature requirement (audit): " + (
        "individual SEEN_AND_SIGNED" if row["gate_requires_per_notice_signature"] else "batch eligible under existing gate"))
    group = next((g for g in audit["decision_groups"] if row["audit_id"] in g["members"]), None)
    if group:
        member_position = group["members"].index(row["audit_id"]) + 1
        lines.append(f"Shared-reason group {group['group_id']}: member {member_position} of "
                     f"{len(group['members'])} notices in this group; {group['title']}.")
        if member_position == 1 or show_group_reason:
            lines += ["Shared argument (harness-team recommendation): " + group["shared_sentence"],
                      "Grouping limitations (harness team): " + group["batching_loss"]]
        else:
            lines.append(f"Shared argument is presented at {group['members'][0]}; to read it here, explicitly rerun "
                         f"python scripts/sign_walk.py --notice {row['audit_id']} --show-group-reason. "
                         "No prior reading is assumed or recorded.")
    for defect in judgement.get("defects") or []:
        lines.append(f"RE-JUDGEMENT DEFECT ({judgement['judgement_id']}; the lane's finding, not Mahmood's decision): "
                     + defect)
    lines += ["HARNESS-TEAM ADJUDICATION (recommendation, not Mahmood's decision): " + row["recommendation_reason"],
              "HARNESS-TEAM RECOMMENDATION: " + row["recommendation"],
              "Departing-trial adjudication and held evidence (harness-team audit):"]
    for trial in row["departing_trials"]:
        lines.append(f"{trial['trial_id']}; family {trial['family_id']}; {trial['eligibility_label']}: "
                     f"{trial['absence_code']}. Candidate values: {_json(trial['candidate_tuple'])}. "
                     f"Source: {row['page_evidence']['review_path']}#{trial['current_pointer']}\n"
                     + trial["source_excerpt"])
    if not row["departing_trials"]:
        lines.append("No departing-trial adjudication in the audit.")
    lines.append("Recovery evidence requested (harness-team recommendation):")
    for recovery in row["recovery_evidence"]:
        lines.append(f"{recovery['trial_id']}: {recovery['requirement']}")
    if not row["recovery_evidence"]:
        lines.append("No per-trial recovery requirement in the audit; see the recommendation above.")
    if row["audit_id"] in audit.get("specific_conflicts", {}):
        lines.append("Held-source conflict (harness-team audit): " + _json(audit["specific_conflicts"][row["audit_id"]]))
    reader = _BlockText()
    reader.feed(block)
    lines += ["Canonical rendered block, readable text (digest covers the canonical HTML bytes):",
              "".join(reader.parts).strip(), f"Rendered block sha256: {sha}"]
    sig = notice.get("reviewer_countersignature") or {}
    if sig.get("state") in result_changes.SIGNED_STATES:
        problem = result_changes.signature_problem(countersign._annotated(notice), block)
        lines.append(f"Recorded signature: {sig['state']} by {sig.get('by')} on {sig.get('when_utc')}. "
                     + (f"Validation issue: {problem}" if problem else "Valid for this block."))
        lines.append("No signing command offered for an already signed notice.")
    else:
        lines += ["If Mahmood accepts this exact notice, he runs this separate command from the repository root "
                  "in PowerShell. --basis prompts him to describe what he actually read:",
                  "python scripts/countersign_result_change.py sign " + _ps(notice["slug"]) + " " + _ps(notice["outcome"])
                  + f" --notice-index {index} --expect-digest {sha} --by 'Mahmood'"
                  + f" --judgement {judgement['judgement_id']}"
                  + " --basis (Read-Host 'Describe how this notice reached you and what you read')"]
    lines += [d01(), "STOP. No signature or progress state was written. Another notice requires another explicit invocation."]
    return "\n\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    choose = parser.add_mutually_exclusive_group()
    choose.add_argument("--notice", help="audit ID from registry/notice_adjudication.json, or D01 for the pending, non-signable decision")
    choose.add_argument("--position", type=int, help="one-based fixed audit-order position; defaults to 1")
    parser.add_argument("--show-group-reason", action="store_true", help="repeat this group's shared argument")
    args = parser.parse_args(argv)
    if args.notice == "D01":
        print(d01())
        return 0
    try:
        audit, notices, chains, mapping = load_walk()
        ordered = ordered_notices(audit)
        if args.notice:
            if args.notice not in mapping:
                raise ValueError(f"unknown audit notice {args.notice!r}")
            position = next(i for i, row in enumerate(ordered, 1) if row["audit_id"] == args.notice)
        else:
            position = args.position if args.position is not None else 1
        print(present(audit, notices, chains, mapping, position, args.show_group_reason))
    except (OSError, KeyError, TypeError, ValueError) as error:
        print(f"refused: {error}; no signing command offered", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
