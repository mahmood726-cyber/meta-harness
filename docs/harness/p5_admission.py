"""D04 option 1, as amended: a recovered P5 fact FILLS an abstention, never overturns a finding.

`evidence/p5_populations/POLICY.md` holds that the P5 ledger "decides how evidence is *recorded*.
It does **not** admit any row: admission ... is Mahmood's decision D04." This module is that
decision, and nothing more: it reads the committed ledger and re-interprets no evidence. A row's
state is whatever the ledger says it is.

THE AMENDMENT IS THE WHOLE POINT. `fill()` acts only on a cell whose state is UNKNOWN -- an
abstention, a gap the screen said it could not close. A cell that is INELIGIBLE is a FINDING: the
screen proved the family out. Filling a gap and overturning a finding are different permissions,
and the ruling grants only the first. That is enforced here by the shape of the data rather than
by a list of excluded rows, so it cannot be defeated by a row the list did not anticipate:

    state == 'UNKNOWN'   -> may be filled
    state == 'INELIGIBLE'-> returned untouched (a proven exclusion)
    state == 'ELIGIBLE'  -> returned untouched (nothing to fill)

The code must also MATCH. A row that recovered `randomized_contrast` evidence may fill an
INTERVENTION_CONTRAST_NOT_PROVEN abstention and nothing else; it may not fill an abstention about
the entry population, which its evidence does not address. Measured on the committed corpus this
is not decoration: it is what keeps two rows out (P53-26, whose cell abstains on
PLACEBO_CONTROL_NOT_PROVEN, and P53-46, whose cell abstains on INTERVENTION_CONTRAST_NOT_PROVEN).

A filled cell is marked `P5_LEDGER_ADMISSION` and carries the row key, the recovered fact ids, the
ledger's sha256 and the decision's signer, so a page can say the family is eligible BY ADMISSION
rather than by the structural screen. This follows the existing precedent for
RETROSPECTIVE_VOCABULARY_CLARIFICATION in `screen_family`: admitted only via X, so record X.
"""
import hashlib
import json
import os

LEDGER_REL = os.path.join("evidence", "p5_populations", "ledger.json")

DECISION = {
    "id": "D04-OPT1-AMENDED",
    "signer": "Dispatch, on Mahmood's delegation",
    "ruling": (
        "D04 option 1 is amended so that it fills only UNKNOWN or abstained facts. It never "
        "overturns a fact proven INELIGIBLE. So P53-49 (spironolactone, "
        "ALLOCATION_NOT_RANDOMIZED) stays excluded."
    ),
    "admits_row_state": "ALL_RECOVERED",
    "ledger": LEDGER_REL,
    "basis": (
        "Dispatch message of 2026-10-16, on Mahmood's delegation, following the measured dry run "
        "that showed the rule moves no pooled result: 37 of 38 admitted rows name a trial already "
        "in a pool, and the 38th has no verified outcome span."
    ),
}

FILLED_BASIS = "P5_LEDGER_ADMISSION"


def load(root, slug):
    """Admissions for one topic: {family_id: row}. Empty when the ledger is absent.

    A row with no `p5_absence_code` names no abstention, so it can fill nothing and is dropped
    here. That is not what keeps a proven exclusion out -- `fill` is -- and the tests prove the
    two guards independently.
    """
    path = os.path.join(str(root), LEDGER_REL)
    if not os.path.exists(path):
        return {}
    with open(path, "rb") as fh:
        raw = fh.read()
    digest = hashlib.sha256(raw).hexdigest()
    doc = json.loads(raw.decode("utf-8"))
    out = {}
    for row in doc.get("rows") or []:
        if row.get("slug") != slug:
            continue
        if row.get("row_state") != DECISION["admits_row_state"]:
            continue
        code = row.get("p5_absence_code")
        if not code:
            continue
        out[str(row.get("family_id"))] = {
            "row_key": row.get("key"),
            "p5_absence_code": code,
            "recovered_fact_ids": sorted({f.get("fact_id") for f in (row.get("facts") or [])
                                          if f.get("fact_id")}),
            "ledger_sha256": digest,
        }
    return out


def fill(eligibility, family_id, admissions):
    """Return the cell, filled if and only if D04 as amended permits it."""
    if not admissions:
        return eligibility
    row = admissions.get(str(family_id))
    if row is None:
        return eligibility
    cell = eligibility or {}
    if cell.get("state") != "UNKNOWN":
        # ELIGIBLE has no gap to fill; INELIGIBLE is a proven exclusion and the ruling does not
        # reach it. Either way the cell is returned exactly as the screen decided it.
        return eligibility
    if cell.get("absence_code") != row["p5_absence_code"]:
        # The recovered evidence does not answer the abstention that actually holds this family.
        return eligibility
    return {
        "state": "ELIGIBLE",
        "span": {
            "source": DECISION["ledger"],
            "eligibility_basis": FILLED_BASIS,
            "decision": DECISION["id"],
            "signer": DECISION["signer"],
            "ruling": DECISION["ruling"],
            "row_key": row["row_key"],
            "filled_absence_code": row["p5_absence_code"],
            "recovered_fact_ids": row["recovered_fact_ids"],
            "ledger_sha256": row["ledger_sha256"],
        },
    }
