# T5 proves group ownership, not protocol role — reproduced, and anchored

Item 1 of the overnight audit passes. Reproduced by execution on the real checker, then repaired.
2026-09-25. Nothing landed; no served number moved.

## The defect, reproduced with working controls

`evidence/typed_arms/witness/check_witness.py` (on `origin/main`; absent from the `enforcement-gate`
worktree and from `mh-f4`) proves **number -> groupId -> arm title**. It never proves **protocol role ->
group**, because it reads `role` straight off the object —

    check_witness.py:139   role = a.get("role")

— and then keys the tuple comparison by that same role:

    check_witness.py:173   got  = {a.get("role"): (a.get("events"), a.get("total")) for a in arms}
    check_witness.py:174   want = {"intervention": (s["ai"], s["n1i"]), "comparator": (s["ci"], s["n2i"])}

So a **consistently** reversed object satisfies `got == want`. Run against the real `check_job`:

    AUTHENTIC (control)                          WITNESSED
    GROUP_ID SWAP (their control)                INCOMPLETE  "T5 arm 0 event_witness: enclosing groupId
                                                              is 'EG001', not the arm's 'EG000'"
    ROLE REVERSED + tuple reversed  (the claim)  WITNESSED   <- the defect
    ROLE REVERSED, tuple NOT reversed            DIFFERS

In the reversed case placebo's group is declared the **intervention**, every witness still points at its
own group's own tokens, and every group title still equals its `arm_name`. Only the clinical direction is
inverted, and nothing looks at it. Their own negative controls are a group_id swap and a wrong group
title — a role reversal is not among them (`tests/test_witness.py:83, 114, 139` all hard-code the role).

## The repair: anchor role to the protocol, and add ARM_ROLE_MISMATCH

`check_job` reads only `row.json` (held_key, served, documents, registry_results) — it has **no access to
the topic config**, which is why the role could not be anchored. The patch adds an optional `arm_roles`
block to `row.json`, carrying the canonical terms from the topic config
(`intervention_terms` / `comparator_terms`), and a `_role_anchor` check:

- an arm whose name matches the **other** role's terms and not its own -> **`ARM_ROLE_MISMATCH`**;
- an arm matching neither -> flag `ROLE_UNMATCHED`;
- **`arm_roles` absent -> flag `ROLE_UNANCHORED`, never a silent pass.** A check that cannot run must
  say so rather than contribute a pass, or the coverage number counts jobs it never checked. That is
  the same rule that produced `REGISTRY_NOT_USED` in this file already.

Measured, all four cases against the real `check_job`:

| case | anchored | unanchored |
|---|---|---|
| AUTHENTIC | **WITNESSED** | WITNESSED + `ROLE_UNANCHORED` |
| GROUP_ID SWAP (their control) | INCOMPLETE | INCOMPLETE |
| ROLE REVERSED + tuple reversed | **INCOMPLETE / `ARM_ROLE_MISMATCH`** | WITNESSED (unchanged) |
| ROLE REVERSED, tuple not reversed | INCOMPLETE / `ARM_ROLE_MISMATCH` | DIFFERS |

The authentic row is not falsely refused, their control still fires for its own reason, and the defect is
caught. Absent the anchor, behaviour is unchanged but visible.

`ARM_ROLE_ANCHOR.patch` — 3,228 bytes, sha256 `ee5316763799b39b…`, against
`origin/main:evidence/typed_arms/witness/check_witness.py`.

## Ownership note

The file is the **data lane's**, not the harness's. I own the T5 item, so the patch and its evidence are
delivered to that lane rather than applied by me. The `arm_roles` block must be written by whatever
builds the witness jobs, from the topic config — that producer change is theirs.

There is already a config-anchored role assignment elsewhere in the system, which is the right source:

    harness/ctgov_results.py:62      _classify_arms(groups, interv_l, comp_l)  -- by group title,
                                     with the standard 2-arm placebo/control fallback
    harness/count_observations.py:379, 388, 404   stamps role from it
    harness/pipeline.py:1318, 1898-1899           terms come from the topic config

**A related weakness, recorded not worked:** the prose path stamps role **positionally** —
`count_observations.py:180`, `for side, ek, nk in (("intervention","ai","n1i"), ("comparator","ci","n2i"))`
— so prose-owned rows carry a role that is asserted by position rather than derived from the protocol.
Anchoring there is the same fix applied at a second site.

## For the ordered-contrast lane

Until this lands, treat `role` as **asserted, not proven**, and say so in anything published. Once it
lands, an ordered contrast can trust `experimental_arm` / `reference_arm` instead of re-deriving
orientation.
