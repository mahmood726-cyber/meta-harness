"""Typed, located adjustment evidence; never infer adjustment from arbitrary source words."""
from pathlib import Path


def axis_for_trial(trial):
    axis = trial.get("adjustment_axis") or {}
    if axis.get("status") not in {"ADJUSTED", "UNADJUSTED"}:
        return {"status": "UNRESOLVED"}
    span = axis.get("span")
    if not span or not axis.get("source"):
        return {"status": "UNRESOLVED"}
    if axis.get("source_path"):
        root = Path(__file__).resolve().parents[1]
        path = (root / axis["source_path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            return {"status": "UNRESOLVED"}
        text = path.read_text(encoding="utf-8")
    else:
        text = trial.get("source") or ""
    start = axis.get("start")
    end = axis.get("end")
    if not isinstance(start, int) or not isinstance(end, int) or start < 0 or text[start:end] != span:
        return {"status": "UNRESOLVED"}
    return dict(axis)


def label(trial):
    scale = str(trial.get("scale") or "EFFECT").upper()
    return "PUBLISHED_" + scale
