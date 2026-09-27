"""REPORT FAMILIES: several reports of ONE trial at different follow-up times (COPS: the 12-month primary report and the
2-year follow-up letter). One family, one trial in every count; the report whose follow-up matches the PROTOCOL's
timepoint is the timepoint report, every other report is a SENSITIVITY_CANDIDATE, never a second trial.

Declared in docs/report_families.json, and never trusted as declared:
  * each report carries a witness -- a held file (path + sha256) and a verbatim span in it; the bytes are re-hashed and
    the span must occur, or the family FAILS CLOSED (ValueError);
  * the follow-up length is PARSED from the witnessed span ('12-month', 'Two-Year') and must equal the declared value;
  * the timepoint is chosen from the protocol's own words ('trial end' / 'longest follow-up' -> the longest follow-up
    report), not from which report the search happened to retrieve.
A refusal or a pooled row judged on a non-timepoint report must say so (report_role SENSITIVITY_CANDIDATE); two
reports of one family counted as two rows in an outcome is a double count. Both are blocking consistency problems.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

PATH = os.path.join("docs", "report_families.json")
TIMEPOINT_REPORT, SENSITIVITY_CANDIDATE = "TIMEPOINT_REPORT", "SENSITIVITY_CANDIDATE"
_LONGEST = re.compile(r"trial end|end of (?:the )?trial|longest|final follow", re.I)
_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
          "twelve": 12, "eighteen": 18, "twenty-four": 24, "thirty-six": 36}
_DUR = re.compile(r"\b(\d{1,3}|" + "|".join(_WORDS) + r")[\s-]+(year|month)s?\b", re.I)


def _pmid(x) -> str:
    m = re.search(r"(\d{7,8})", str(x or ""))
    return m.group(1) if m else ""


def months_in(span: str) -> int | None:
    """Follow-up length stated in a witnessed span, in months ('12-month' -> 12, 'Two-Year' -> 24); None if absent."""
    m = _DUR.search(span or "")
    if not m:
        return None
    n = m.group(1).lower()
    n = int(n) if n.isdigit() else _WORDS[n]
    return n * 12 if m.group(2).lower() == "year" else n


def _witness_text(root: str, w: dict[str, Any]) -> str:
    p = os.path.join(root, w["path"])
    raw = open(p, "rb").read()
    if hashlib.sha256(raw).hexdigest() != w.get("sha256"):
        raise ValueError(f"report-family witness digest mismatch: {w['path']}")
    text = raw.decode("utf-8")
    if w["path"].endswith(".json"):
        vals = []                                   # the file's string VALUES (title, abstract), not its escaping

        def walk(x):
            if isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
            elif isinstance(x, str):
                vals.append(x)
        walk(json.loads(text))
        text = " \n ".join(vals)
    # strip real markup only (<h4>, </p>): a bare '<' in prose ('P<0.05') must not swallow text up to the next '>'
    return re.sub(r"\s+", " ", re.sub(r"</?[A-Za-z][A-Za-z0-9]*(?:\s[^<>]{0,200})?/?>", " ", text))


def verify_family(root: str, fam: dict[str, Any]) -> list[dict[str, Any]]:
    """Each report with its witnessed follow-up; raises on a digest mismatch, a missing span, or a declared follow-up
    the span does not state."""
    out = []
    for rep in fam.get("reports") or []:
        w = rep["follow_up_witness"]
        text = _witness_text(root, w)
        span = re.sub(r"\s+", " ", w["span"])
        if span not in text:
            raise ValueError(f"report-family witness span not in {w['path']}: {span!r}")
        got = months_in(span)
        if got is None or got != rep.get("follow_up_months"):
            raise ValueError(f"declared follow-up {rep.get('follow_up_months')} months for {rep.get('report_id')} "
                             f"but the witnessed span states {got}")
        out.append({**rep, "follow_up_months_witnessed": got})
    return out


def select(reports: list[dict[str, Any]], protocol_timepoint: str | None) -> dict[str, Any]:
    """The timepoint report under the protocol's stated timepoint; every other report is a sensitivity candidate."""
    tp = protocol_timepoint or ""
    if _LONGEST.search(tp):
        rule = "PROTOCOL_TIMEPOINT_TRIAL_END_LONGEST_FOLLOW_UP"
        chosen = max(reports, key=lambda r: r["follow_up_months_witnessed"])
    else:
        want = months_in(tp)
        match = [r for r in reports if want is not None and r["follow_up_months_witnessed"] == want]
        if len(match) != 1:
            return {"rule": "PROTOCOL_TIMEPOINT_UNRESOLVED", "protocol_timepoint": tp, "timepoint_report": None,
                    "reports": [{**r, "report_role": SENSITIVITY_CANDIDATE} for r in reports]}
        rule, chosen = "PROTOCOL_TIMEPOINT_MATCHED", match[0]
    return {"rule": rule, "protocol_timepoint": tp, "timepoint_report": chosen["report_id"],
            "reports": [{**r, "report_role": TIMEPOINT_REPORT if r is chosen else SENSITIVITY_CANDIDATE}
                        for r in reports]}


def load(root: str, slug: str) -> list[dict[str, Any]]:
    p = os.path.join(root, PATH)
    if not os.path.exists(p):
        return []
    return list(((json.load(open(p, encoding="utf-8")) or {}).get("topics") or {}).get(slug) or [])


def attach(review: dict[str, Any], root: str) -> None:
    """review['report_families']: each declared family verified and resolved against the primary outcome's timepoint."""
    fams = load(root, review.get("slug"))
    if not fams:
        return
    prim = next((o for o in review.get("outcomes") or [] if o.get("primary")), None) or {}
    tp = prim.get("timepoint")
    out = []
    for fam in fams:
        sel = select(verify_family(root, fam), tp)
        out.append({"family_id": fam["family_id"], "trial": fam.get("trial"), "counted_as_trials": 1,
                    "selection": sel})
        for tf in review.get("trial_families") or []:
            if tf.get("family_id") == fam["family_id"]:
                tf["report_family_selection"] = {"timepoint_report": sel["timepoint_report"], "rule": sel["rule"],
                                                 "reports": [{"report_id": r["report_id"], "report_role": r["report_role"],
                                                              "follow_up_months": r["follow_up_months_witnessed"]}
                                                             for r in sel["reports"]]}
    review["report_families"] = out


def _role_of(review: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    roles = {}
    for fam in review.get("report_families") or []:
        for r in fam["selection"]["reports"]:
            roles[_pmid(r["report_id"])] = (fam["family_id"], {**r, "timepoint_report": fam["selection"]["timepoint_report"]})
    return roles


def annotate_refusals(rows: list[dict[str, Any]] | None, review: dict[str, Any]) -> list[dict[str, Any]] | None:
    """A refusal judged on one report of a family says which report it judged and which report the protocol's
    timepoint selects (and that report's result state)."""
    if not rows:
        return rows
    roles = _role_of(review)
    fams = {f["family_id"]: f for f in review.get("report_families") or []}
    out = []
    for row in rows:
        hit = roles.get(_pmid(row.get("trial")))
        if hit:
            fid, r = hit
            tp = next(x for x in fams[fid]["selection"]["reports"] if x["report_id"] == r["timepoint_report"]) \
                if r["timepoint_report"] else None
            row = {**row, "report_family": {
                "family_id": fid, "judged_report": r["report_id"], "judged_report_role": r["report_role"],
                "judged_follow_up_months": r["follow_up_months_witnessed"],
                "timepoint_report": r["timepoint_report"],
                "timepoint_report_label": (tp or {}).get("label"),
                "timepoint_result_state": (tp or {}).get("result_state"),
                "rule": fams[fid]["selection"]["rule"]}}
        out.append(row)
    return out


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    """Blocking: two reports of one family as two rows of an outcome (FAMILY_DOUBLE_COUNT); a served row or refusal
    that is judged on a non-timepoint report without saying so (FAMILY_TIMEPOINT_UNLABELLED)."""
    roles = _role_of(review)
    out = []
    for o in review.get("outcomes") or []:
        seen = {}
        for t in o.get("trials") or []:
            hit = roles.get(_pmid(t.get("id")))
            if not hit:
                continue
            fid, r = hit
            if fid in seen:
                out.append({"kind": "FAMILY_DOUBLE_COUNT", "report_id": r["report_id"],
                            "detail": f"{o.get('name')}: {seen[fid]} and {r['report_id']} are reports of ONE trial "
                                      f"({fid}) pooled as two rows"})
            seen[fid] = r["report_id"]
            if r["report_role"] != TIMEPOINT_REPORT and t.get("report_role") != SENSITIVITY_CANDIDATE:
                out.append({"kind": "FAMILY_TIMEPOINT_UNLABELLED", "report_id": r["report_id"],
                            "detail": f"{o.get('name')}: pooled from the {r['follow_up_months_witnessed']}-month report, "
                                      f"not the protocol-timepoint report {r['timepoint_report']}, without saying so"})
    for row in ((review.get("reproduction") or {}).get("refusals") or []):
        hit = roles.get(_pmid(row.get("trial")))
        if hit and hit[1]["report_role"] != TIMEPOINT_REPORT and not row.get("report_family"):
            out.append({"kind": "FAMILY_TIMEPOINT_UNLABELLED", "report_id": hit[1]["report_id"],
                        "detail": f"refusal of {row.get('trial')} is judged on a sensitivity-candidate report without "
                                  "naming the protocol-timepoint report"})
    return out
