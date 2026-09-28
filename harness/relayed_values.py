"""RELAYED VALUES (docs/relayed_values.json): numbers passed to the evidence lane that are NOT verified against held
bytes, because the source is not openly held. Shown beside their row, labelled relayed; never data. A relayed value is
attached to its named outcome only (Moll's discontinuation counts never reach the GI-incidence row)."""
from __future__ import annotations

import json
import os
import re
from typing import Any

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def attach(review: dict[str, Any], slug: str | None, root: str = _ROOT) -> None:
    p = os.path.join(root, "docs", "relayed_values.json")
    if not os.path.exists(p):
        return
    mine = [v for v in json.load(open(p, encoding="utf-8")).get("values") or [] if v.get("topic") == slug]
    pid = lambda x: (re.search(r"NCT\d{8}|\b\d{7,8}\b", str(x or "")) or re.search("", "")).group(0)
    for v in mine:
        for o in review.get("outcomes") or []:
            if o.get("name") != v["outcome"]:
                continue
            for row in (o.get("trials") or []) + (o.get("declared_absent_trials") or []):
                if pid(row.get("id")) == pid(v["trial"]):
                    row["relayed_not_held"] = {k: v.get(k) for k in ("value", "relayed_by", "said_to_be_in", "why_not_held")}
