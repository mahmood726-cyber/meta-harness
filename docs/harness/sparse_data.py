"""SPARSE DATA: the method applied to a zero cell is DECLARED where it is used, never silent.

harness.synth adds 0.5 to all four cells of a study that has a zero cell -- and only to such a study (an unconditional
correction biases towards the null). DAPA-HF's adjudicated diabetic ketoacidosis, 3/2,368 vs 0/2,368, is such a row: its
risk ratio exists only through that correction. So every pooled count row with a zero cell carries the correction on
its own row (harms.py discloses it on harm rows; this adds it where none exists), and the outcome's result names its
sparse-data method.
"""
from __future__ import annotations

from typing import Any

METHOD = ("0.5 added to all four cells of a study with a zero cell, applied only to such a study (never "
          "unconditionally); risk ratio on the corrected counts, inverse-variance pooling")


def attach(review: dict[str, Any]) -> None:
    for o in review.get("outcomes") or []:
        zero = []
        for t in o.get("trials") or []:
            a, n1, c, n2 = (t.get(k) for k in ("ai", "n1i", "ci", "n2i"))
            if None in (a, n1, c, n2):
                continue
            if min(a, c, n1 - a, n2 - c) == 0:
                # harms.py already discloses the correction on HARM rows; never overwrite a disclosure, add it where
                # none exists (an efficacy row with a zero cell)
                t.setdefault("continuity_correction", f"zero cell ({a}/{n1} vs {c}/{n2}): " + METHOD)
                zero.append(str(t.get("id")))
        if zero:
            res = o.setdefault("result", {})
            res["sparse_data_method"] = {"method": METHOD, "rows": zero}
