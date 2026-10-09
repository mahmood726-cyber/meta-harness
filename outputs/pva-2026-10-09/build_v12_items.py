"""Write the V12 items (handover items whose fix would change a stored review object, a signed record or a served count)
from the span-gated codex classification. Never applied by this lane: each needs the Captain's packet and Mahmood's
signature.  python outputs/pva-2026-10-09/build_v12_items.py <out.md>"""
import glob
import json
import sys
from pathlib import Path

A = Path(__file__).resolve().parent / "codex_handover"
gate = json.loads((A / "classify" / "gate.json").read_text(encoding="utf-8"))
items = {}
for f in sorted((A / "classify" / "out").glob("job*.json")):
    for it in json.loads(f.read_text(encoding="utf-8"))["items"]:
        items[it["id"]] = it
WHAT = {   # one line per item: what the page says today (from the handover) -- for the reader of the packet
    "H2": "dpp4 (and the funding sentence generally): absence counts read 0 / 0 while the funding rows hold one full-text-silent and one abstract-only trial",
    "H3": "finerenone, semaglutide-weight: 'Nothing was pooled on this page' where a point estimate is served (CI refused)",
    "H4": "dpp4: TECOS listed as a known eligible trial NOT in the pool, while it is pooled",
    "H5": "dpp4: the TECOS notice reads NOT APPLIED (HELD), overtaken by a later signed route",
    "H6": "doac: comparator note endorses van Es 2014, which the comparator panel retired (open-licence gate)",
    "H7": "sacubitril: comparator note says PARADIGM-HF is the only extractable estimate; PARALLEL-HF is extracted too",
    "H8": "tocilizumab: comparator note says COVACTA gives mortality as a RATE only; the row holds counts 58/294 v 28/144",
    "H9": "tocilizumab, tranexamic, colchicine-pericarditis: '✓ same question' while each review's own note records a broader comparator",
    "H10": "pcsk9: 'pooled trials use each trial's OWN primary composite'; FOURIER contributes its secondary composite",
    "H14": "tocilizumab, tranexamic: search funnel 'unknown -> 0 -> 0' for queries whose yields were never recorded",
    "H15": "empagliflozin: a SIGNED notice says 'a pooled estimate is now served' for a k = 1 single-trial estimate",
    "H16": "metformin (every higher-is-better outcome): claim direction 'harm' for ovulation OR > 1",
}
SERVED_CHANGE = {
    "H2": "limitations[funding-coi].rendered_text (stored) + the Risk-of-bias sentence; counts 0/0 -> 1/1 on dpp4",
    "H3": "limitations[claim-check-zero].rendered_text + text_sha256 (stored) on 2 reviews",
    "H4": "outcomes[primary].known_missing_sensitivity.rows loses the TECOS row (stored)",
    "H5": "docs/result_changes.json: the notice's held block gains a resolution (a SIGNED record's metadata)",
    "H6": "review.json comparator_scope_note (copied from the topic config) -- topic config + rebuild",
    "H7": "review.json comparator_scope_note -- topic config + rebuild",
    "H8": "review.json comparator_scope_note -- topic config + rebuild",
    "H9": "comparator.scope.scope_valid / note / intervention_level_match (stored) on 3 reviews",
    "H10": "outcomes[0].result.composite_heterogeneity (stored) on pcsk9",
    "H14": "a displayed search count changes from 0 to 'unknown' (served number on the page; review.json unchanged)",
    "H15": "a SUCCESSOR signed notice (the signed bytes cannot change) + docs/result_changes.json",
    "H16": "outcomes[*].result.claim.direction (stored; gate-checked against every surface) + an explicit outcome polarity field",
}
out = ["# V12 items from the pva lane (review-tabs handover) -- for the Captain's packet, NOT applied\n",
       "Each item below would change a stored review object, a signed record, or a count the page serves, so this lane does "
       "not apply it. Root causes are from a recorded codex classification (outputs/pva-2026-10-09/codex_handover/classify, "
       "calls.jsonl); every quoted code line and data value passed a span gate against the files (classify/gate.json). "
       "The presentation-only items (H11, H12, H13, H17, H18, H19, A1) are fixed, with plants, on branch pva/handover-fixes.\n",
       "H1 (noac ENGAGE CI) is already decided: D16 'c then b' (8 Oct).\n"]
for n, k in enumerate(["H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H14", "H15", "H16"], 1):
    it = items[k]
    out.append(f"## V12-PVA-{n:02d} ({k})\n")
    out.append(f"- **What the page says:** {WHAT[k]}.")
    out.append(f"- **What would change:** {SERVED_CHANGE[k]}.")
    out.append(f"- **Root cause:** `{it['root_cause_file']}` -- {it['root_cause_code'][:600]}")
    out.append(f"- **Proposed fix:** {it['fix'][:900]}")
    out.append(f"- **Plant:** {it['plant'][:600]}")
    out.append(f"- **Evidence** (span-gated {sum(1 for s in gate[k] if s.startswith('OK'))}/{len(gate[k])}): "
               + " · ".join(f"`{e['file']}`: \"{e['quote'][:160]}\"" for e in it["evidence"][:3]))
    out.append("- **Decision needed:** apply as proposed / apply differently / leave as is.\n")
Path(sys.argv[1]).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("wrote", sys.argv[1])
