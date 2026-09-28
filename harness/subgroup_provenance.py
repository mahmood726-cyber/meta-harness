"""SUBGROUP PROVENANCE of a pooled row: whole_trial | prespecified_subgroup | post_hoc_subgroup -- DERIVED from a source
span, never asserted (lane NR V1.0.1; statins-older-adults review).

JUPITER's >=70-years result (PMID 20404379) was served as a 'pre-specified' subgroup because the topic asserted it
(`evidence_unit: prespecified_subgroup`); the paper's own LIMITATION says the opposite: 'Effect estimates from this
exploratory analysis with age cut-point chosen after trial completion should be viewed in the context of the overall
trial results.' The topic now declares only THAT the row is a subgroup; whether it was pre-specified is read from the
held text:
  * a post-hoc statement ('post hoc', a cut-point/threshold chosen or defined AFTER trial completion, 'not
    pre-specified', 'retrospectively defined') -> post_hoc_subgroup; it wins over a general 'prespecified' elsewhere,
    because it is about the cut-point that defines THIS subgroup;
  * an explicit pre-specification of the subgroup ('prespecified subgroup', 'subgroup ... specified a priori')
    -> prespecified_subgroup;
  * neither -> UNRESOLVED (value None): not stated is not pre-specified.
A row that is not a subgroup is whole_trial. The value feeds RoB (D5, selection of the reported result); it never
excludes the row -- the number stays.
"""
from __future__ import annotations

import re
from typing import Any

WHOLE_TRIAL, PRESPECIFIED, POST_HOC = "whole_trial", "prespecified_subgroup", "post_hoc_subgroup"

# A bare 'post hoc' counts only in a sentence that is about the SUBGROUP (its cut-point, strata, age band, or 'this
# exploratory/subgroup analysis'): a post-hoc ADHERENCE or sensitivity analysis elsewhere in the paper says nothing about
# how the subgroup was defined, and must not override a pre-specification.
# A negated statement ('were not post hoc', 'prespecified, not post hoc', 'not selected after trial completion') is not
# post-hoc evidence (lane NR codex call NR-C18, cases verified by execution). Text is whitespace-collapsed first, so
# the fixed-width 'not ' lookbehinds see exactly one space.
_BARE_POST_HOC = re.compile(r"(?<!\bnot )\bpost[\s-]?hoc\b", re.I)
_SUBGROUP_CUE = re.compile(
    r"\bsubgroups?\b|\bcut[\s-]?(?:point|off)s?\b|\bthresholds?\b|\bstrat(?:um|a|ified)\b|\bage[ds]?\b|"
    r"\bthis\s+(?:exploratory\s+|secondary\s+)?analysis\b", re.I)
_POST_HOC = re.compile(
    r"\b(?:cut[\s-]?(?:point|off)s?|thresholds?|subgroups?)\b[^.;]{0,60}?(?<!\bnot )"
    r"\b(?:chosen|selected|defined|determined|set|devised|planned)\s+"
    r"(?:after|following)\s+(?:the\s+)?(?:trial|study)(?:'s)?\s+(?:completion|was\s+completed|ended|close)|"
    r"\bnot\s+(?:been\s+)?(?:prospectively\s+)?pre-?specified\b|\bretrospectively\s+(?:defined|chosen|selected)\b", re.I)
_PRESPECIFIED = re.compile(
    r"\b(?:pre-?specified|pre-?defined|pre-?planned|a\s+priori)\s+(?:[a-z-]+\s+){0,2}?subgroups?\b|"
    r"\bsubgroups?\s+(?:were\s+|was\s+)?(?:defined|specified|planned)\s+a\s+priori\b|"
    r"\bsubgroups?\b[^.;]{0,40}?\b(?:were|was|had\s+been)\s+"
    r"(?:pre-?specified|pre-?defined|specified\s+a\s+priori|planned\s+a\s+priori)\b",
    re.I)
# sentence boundary, but not after common abbreviations ('vs.', 'e.g.', 'i.e.', 'et al.') that split one statement in two
_SENT = re.compile(r"(?<=[.;])(?<!\bvs\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bal\.)\s+(?=[A-Z])")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.split(re.sub(r"\s+", " ", text or "")) if s.strip()]


def _bare_post_hoc_about_subgroup(sentence: str) -> bool:
    """A bare 'post hoc' and a subgroup cue in the SAME clause: 'The subgroup analysis was prespecified; a post hoc
    sensitivity analysis excluded ...' must not borrow 'subgroup' from the other clause."""
    return any(_BARE_POST_HOC.search(c) and _SUBGROUP_CUE.search(c) for c in sentence.split(";"))


def derive(trial: dict[str, Any], record: dict[str, Any] | None, declared_unit: str | None) -> dict[str, Any]:
    """{'value', 'basis', 'span', 'source', 'rule_id'} for one pooled row. `declared_unit` is the topic's evidence unit
    ('trial' or any '*subgroup*'); only THAT the row is a subgroup is declared, never how it was specified."""
    if "subgroup" not in str(declared_unit or "").lower():
        return {"value": WHOLE_TRIAL, "source": "declared evidence unit",
                "basis": "the pooled row is the trial's randomised population (declared evidence unit: trial)",
                "span": None, "rule_id": "subgroup_provenance:whole_trial_v1"}
    record = record or {}
    held = [("held abstract", record.get("abstract") or ""), ("held full text", record.get("fulltext") or ""),
            ("row source", str(trial.get("source") or ""))]
    post, pre = None, None
    for source, text in held:
        for s in _sentences(text):
            if post is None and (_POST_HOC.search(s) or _bare_post_hoc_about_subgroup(s)):
                post = (source, s)
            if pre is None and _PRESPECIFIED.search(s):
                pre = (source, s)
    if post:
        return {"value": POST_HOC, "source": post[0], "span": post[1],
                "basis": "the source states the subgroup was defined post hoc (e.g. its cut-point chosen after trial "
                         "completion)", "rule_id": "subgroup_provenance:post_hoc_statement_v1"}
    if pre:
        return {"value": PRESPECIFIED, "source": pre[0], "span": pre[1],
                "basis": "the source states the subgroup was pre-specified", "rule_id": "subgroup_provenance:prespecified_statement_v1"}
    return {"value": None, "source": None, "span": None,
            "basis": "a subgroup whose pre-specification the held text does not state -- UNRESOLVED, not assumed pre-specified",
            "rule_id": "subgroup_provenance:unresolved_v1"}


def evidence_unit(prov: dict[str, Any]) -> str:
    """The rendered evidence unit, from the DERIVED provenance."""
    return prov.get("value") or "subgroup_unresolved"
