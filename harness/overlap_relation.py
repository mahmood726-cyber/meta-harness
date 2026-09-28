"""THE comparator overlap relation: one computed object, read by every surface that states it.

External review (V1.0.1, balanced-crystalloids): the index said OVERLAPPING against the 2018 comparator while the
two pools share ZERO trials. The relation was inferred from COUNTS (ours_k < theirs_k and a non-empty
publication-date list => OVERLAPPING) and never from the trial sets; `only_ours` named every pooled trial and the
count logic still called it an overlap. Several surfaces (index, parity row, panel, overlap counts) each derived
their own word.

This module computes the relation from the pooled trial-FAMILY sets of the primary outcome:

  ours   = the families pooled for the primary outcome (the served pool, not the included list).
  theirs = the comparator's trials, only from a typed enumeration, in this order of precedence:
             1. the comparator panel's located trial_set (cache/<slug>/comparators.json), restricted to the
                endpoint the panel binds to this outcome (other endpoints are listed as out of scope); a trial
                binds to one of our families only through the panel's witnessed aliases;
             2. comparator-truth's named set (trials located by name in the comparator's text, with the count
                the text states);
             3. the second pass's measured named trials (names located in the comparator's text).
           For 2 and 3 a name binds to a family only when its normalised form (lower-case alphanumerics) equals
           an acronym held for exactly one family -- the family ledger's acronym or its registry record's acronym
           field. Abstract text is never used to bind (abstracts cite other trials).
  NO publication-year rule. A trial's standalone paper can post-date a comparator that already analysed its data
           (COVID STEROID's 2021 paper; its data are in the 2020 WHO prospective meta-analysis; RECOVERY's report
           is dated 2021 in print). Membership is trial identity plus actual analysis membership, never a date.

Relation (IDENTICAL_SET / SUBSET / SUPERSET / OVERLAPPING / DISJOINT) is a set operation. When the sets are not known
well enough to decide -- no enumeration, or an unbound comparator trial that could be one of ours -- the relation is
NOT_ENUMERABLE, never a guess from counts or dates; what IS known is kept as a stated constraint.
Participant level: a shared TRIAL is not necessarily shared PARTICIPANTS -- a comparator can analyse a subgroup (WHO
REACT used RECOVERY's invasively ventilated subgroup). When a comparator member states its analysis population and it
differs from ours, the shared family is reported as SAME_TRIAL_DIFFERENT_PARTICIPANTS.
"""
from __future__ import annotations

import json
import re
from typing import Callable, Optional

from .membership import canonical_trial_key

RELATIONS = ("IDENTICAL_SET", "SUBSET", "SUPERSET", "OVERLAPPING", "DISJOINT", "NOT_ENUMERABLE")
LABELS = {
    "IDENTICAL_SET": "identical -- the same trial families; agreement between the two is arithmetic on the same trials, not a second evidence base",
    "SUBSET": "subset -- every pooled family is in the comparator set",
    "SUPERSET": "superset -- every comparator trial is in our pool",
    "OVERLAPPING": "overlapping -- some families shared, each side has trials the other lacks",
    "DISJOINT": "disjoint -- no trial family in common",
    "NOT_ENUMERABLE": "not enumerable -- the comparator trial set is not known well enough to compare",
}
NO_DATE_RULE = ("publication year is never used to decide membership: a trial's own paper can post-date a comparator "
                "that already analysed its data (V1.0.1, COVID-corticosteroids review)")


def _year(value) -> Optional[int]:
    try:
        return int(str(value)[:4])
    except (TypeError, ValueError):
        return None


def _key(k) -> str:
    """Identity key: canonical trial key, with DOIs lower-cased (DOIs are case-insensitive)."""
    ck = canonical_trial_key(k)
    return ck.lower() if isinstance(ck, str) and ck.startswith("10.") else ck


def norm_name(s) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def _primary(review: dict) -> Optional[dict]:
    return next((o for o in review.get("outcomes") or [] if o.get("primary")), None)


def _families(review: dict) -> list:
    tf = review.get("trial_families")
    fams = tf.get("families") if isinstance(tf, dict) else tf
    return [f for f in (fams or []) if isinstance(f, dict) and f.get("family_id")]


def _panel_entry(review: dict) -> Optional[dict]:
    """The panel entry for the REGISTERED comparator (matched by PMID in its citation or id)."""
    pmid = str(((review.get("comparator") or {}).get("pmid")) or "")
    for c in review.get("comparator_panel") or []:
        if pmid and (pmid in str(c.get("citation") or "") or pmid == str(c.get("id") or "")):
            return c
    return None


# a hyphenated acronym ('RE-LY', 'ROCKET-AF') or a spaced one of capital-led words ('ROCKET AF'); never a drug code
# with digits after a space ('BAY 59-7939')
_TITLE_ACR = re.compile(r"\(([A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]+)+|[A-Z][A-Z0-9]{2,}(?: [A-Z][A-Z0-9]*){0,3})\)")


def _held_registry_acronyms(registry_ids) -> list:
    """V1.0.1 (NOAC-AF review): the acronym a trial's own HELD registry record prints -- its acronym field, or a
    parenthesised acronym in its brief/official title ('Randomized Evaluation of Long Term Anticoagulant Therapy (RE-LY)').
    RE-LY's family carried no acronym, so COMBINE AF's four named trials could not all bind."""
    from pathlib import Path
    out = []
    base = Path(__file__).resolve().parents[1] / "evidence" / "held" / "registry"
    for r in registry_ids:
        p = base / f"{r}.json"
        if not str(r).upper().startswith("NCT") or not p.exists():
            continue
        try:
            im = (json.loads(p.read_text(encoding="utf-8")).get("protocolSection") or {}).get("identificationModule") or {}
        except (OSError, ValueError):
            continue
        if im.get("acronym"):
            out.append(im["acronym"])
        for t in (im.get("briefTitle"), im.get("officialTitle")):
            out += _TITLE_ACR.findall(str(t or ""))
    return out


def _acronym_index(review: dict, report_acronym: Callable[[str], Optional[str]]) -> dict:
    """normalised acronym -> set of family ids (ledger acronyms + the family's registry records' acronym field)."""
    idx = {}
    for f in _families(review):
        al = f.get("aliases") or {}
        names = list(al.get("acronym") or []) + [a for r in al.get("registry_ids") or [] for a in [report_acronym(r)] if a]
        names += _held_registry_acronyms(al.get("registry_ids") or [])
        for n in names:
            if norm_name(n):
                idx.setdefault(norm_name(n), set()).add(f["family_id"])
    return idx


def _family_index(review: dict) -> dict:
    """identity key -> family id for EVERY family in the ledger (report ids, registry ids, DOIs, bib keys)."""
    idx = {}
    for f in _families(review):
        al = f.get("aliases") or {}
        for k in [f["family_id"]] + list(al.get("report_ids") or []) + list(al.get("registry_ids") or []) \
                + list(al.get("dois") or []) + list(al.get("bib_keys") or []):
            idx.setdefault(_key(k), f["family_id"])
    return idx


# V1.0.1 (esketamine review): a generic row label ('Trial A', 'Study 2', 'RCT 3') is never an identity; only a cited
# identifier or a real trial name binds a comparator row to one of our families
_GENERIC = re.compile(r"^\s*(?i:trial|study|rct|cohort|arm|comparison)\s*(?:[A-Z]{1,2}|\d{1,3})\b(?:\s*\(\d{4}\))?")


def generic_label(name) -> bool:
    return bool(_GENERIC.match(str(name or "")))


def _members(review, panel, prim_name, acr_idx, ours_keys):
    """(source, in_scope members, out_of_scope members, endpoint) from the best typed enumeration, or None.
    A member is {name, family (ANY family of our ledger it is, or None), alias_ids, identity, endpoint, span};
    whether that family is in our POOL is decided by the caller."""
    comp = review.get("comparator") or {}
    truth = (comp.get("truth") or {}).get("completeness") or {}
    # V1.0.1 (semaglutide-obesity review): the governing analysis' plot rows name the panel rows they are
    # (harness/comparator_analysis.py panel_row); only those are this outcome's pool -- Stefanou 2024's MACE plot is 7 of
    # its 16 table rows
    _am = (comp.get("analysis") or {}).get("membership") or {}
    plot_rows = {m["panel_row"] for m in _am.get("members") or [] if m.get("panel_row")}
    plot_label = _am.get("endpoint_label") or "the governing analysis"
    panel_outcome_specific = bool(panel and panel.get("trial_set") and ((panel.get("outcome_endpoints") or {}).get(prim_name)
                                                                         or plot_rows))
    truth_outcome_specific = truth.get("relation") == "IDENTICAL_SET" and bool(truth.get("present"))
    # "the comparator's pool FOR THE SAME OUTCOME": an outcome-specific enumeration (a panel whose endpoints are bound
    # to this outcome, or comparator-truth's named set for it) outranks a whole included-studies table
    if panel and panel.get("trial_set") and (panel_outcome_specific or not truth_outcome_specific):
        expected = (panel.get("outcome_endpoints") or {}).get(prim_name) or (plot_label if plot_rows else None)
        alias_of, collisions = {}, []
        for m in panel["trial_set"]:
            for key in [m["family_id"]] + [a["id"] for a in m.get("aliases", [])] + ([m["bib_key"]] if m.get("bib_key") else []):
                ck = _key(key)
                if ck in alias_of and alias_of[ck] != m["family_id"]:
                    collisions.append(f"{key} ({alias_of[ck]} / {m['family_id']})")
                    continue
                alias_of[ck] = m["family_id"]
        if collisions:
            # one identifier claimed by two different comparator rows: the rows' identities are ambiguous
            return {"source": f"comparator panel trial_set ({panel.get('document_ref')})",
                    "endpoint_for_outcome": None, "ambiguous": collisions}, [], []
        fam_idx = _family_index(review)
        fam_reg = {f["family_id"]: list((f.get("aliases") or {}).get("registry_ids") or []) for f in _families(review)}
        # screening's X-DEDUP decision is a typed link: a record it excluded as the companion/secondary publication of
        # a trial names that trial's registration. A comparator row bound to such a record IS the parent trial (the
        # family ledger kept the publication as a separate node, e.g. a trial pooled from its registry record only).
        parent_of = {}
        for d in (review.get("screening") or {}).get("records") or []:
            if d.get("rule_id") != "X-DEDUP" or not d.get("secondary_publication_of"):
                continue
            child = fam_idx.get(_key(d.get("id")))
            parents = {fam_idx[_key(n)] for n in re.findall(r"NCT\d{8}", str(d["secondary_publication_of"])) if _key(n) in fam_idx}
            if child and len(parents) == 1 and child not in parents:
                parent_of[child] = (next(iter(parents)), d.get("id"))
        ins, outs = [], []
        for m in panel["trial_set"]:
            ep = m.get("endpoint")
            if plot_rows:
                ep = plot_label if m["family_id"] in plot_rows else f"not in {plot_label}"
            ids = [a["id"] for a in m.get("aliases", [])] + ([m["bib_key"]] if m.get("bib_key") else [])
            hits = {fam_idx[_key(i)] for i in ids if _key(i) in fam_idx}
            via = [parent_of[h] for h in hits if h in parent_of]
            hits = {parent_of[h][0] if h in parent_of else h for h in hits}
            title_acr, unlinked = None, None
            # V1.0.1 (sacubitril review): a row whose reference binds ONLY to a report-only family (a paper we hold with
            # no registration, e.g. PARALLEL-HF's Circ J report, SYN-...) is re-read by its printed title acronym: if
            # that names exactly one REGISTERED family, the row is that trial and the paper is disclosed as unlinked
            unregistered_only = bool(hits) and all(not fam_reg.get(h) for h in hits)
            if (not hits or unregistered_only) and m.get("aliases"):
                # the row's reference carries a PMID/DOI no family of ours holds (e.g. a trial we hold only by its
                # registry record): bind by the acronym PRINTED IN THAT REFERENCE'S OWN ARTICLE TITLE, as a whole
                # hyphenated token (TRANSFORM-3 never TRANSFORM-2), only when it names exactly one family of ours
                titles = " ".join(t for a in m["aliases"] for t in re.findall(
                    r"<article-title>(.*?)</article-title>", (a.get("span") or {}).get("quote") or "", re.S))
                # V1.0.1 (sacubitril review): JATS prints 'PARALLEL‐HF' with a Unicode hyphen; read as '-' so the
                # whole token is compared, never its 'PARALLEL' prefix
                titles = titles.translate(_UNICODE_HYPHENS)
                toks = set(re.findall(r"(?<![A-Za-z0-9])(?<![A-Z0-9]-)[A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)*(?![A-Za-z0-9-])", titles))
                acr_hits = sorted((t, f) for t in toks for f in acr_idx.get(norm_name(t)) or ())
                if len({f for _, f in acr_hits}) == 1 and (not unregistered_only or fam_reg.get(acr_hits[0][1])):
                    if unregistered_only:
                        unlinked = sorted(hits)
                    title_acr, fam = acr_hits[0]
                    hits = {fam}
            rec = {"name": m["family_id"], "family": (next(iter(hits)) if len(hits) == 1 else None),
                   "alias_ids": [a["id"] for a in m.get("aliases", [])],
                   "identity": ("bound by the acronym printed in its cited article title (" + title_acr + ")"
                                + (f"; the cited paper is held as unlinked report-only family {', '.join(unlinked)}"
                                   if unlinked else "") if title_acr else
                                "bound by panel alias to record " + via[0][1] + ", which screening excluded (X-DEDUP) as a "
                                "secondary publication of " + via[0][0] if via and len(hits) == 1 else
                                "bound by panel alias" if m.get("aliases") else
                                "identified by bibliographic key " + m["bib_key"] if m.get("bib_key") else "unbound (name only)"),
                   "endpoint": ep, "span": (m.get("span") or {}).get("quote"),
                   **({"analysis_population": m["analysis_population"]} if m.get("analysis_population") else {})}
            (outs if (ep and expected and ep != expected) else ins).append(rec)
        tsd = panel.get("trial_set_document") or {}
        doc = tsd.get("document_ref") or panel.get("document_ref")
        scope = ("per-outcome membership bound (" + str(expected) + ")" if expected else
                 "the comparator's included-trial table (all outcomes; per-outcome pool membership is not in the table)")
        return {"source": f"comparator panel trial_set ({doc}, located spans; {scope})",
                "endpoint_for_outcome": expected}, ins, outs
    am = (comp.get("analysis") or {}).get("membership") or {}
    if am.get("members"):
        # V1.0.1 (metformin review): the governing analysis' forest-plot rows (harness/comparator_analysis.py), an
        # outcome-specific enumeration; a row binds to a family of ours only through a report whose counts matched ours
        fam_idx = _family_index(review)
        ins = []
        for m in am["members"]:
            fam = fam_idx.get(_key(m["report_pmid"])) if m.get("report_pmid") else None
            ins.append({"name": m["label"], "family": fam, "alias_ids": [m["report_pmid"]] if m.get("report_pmid") else [],
                        "identity": ("bound to our report PMID " + m["report_pmid"] + " (same counts in the plot and our row)")
                                    if fam else "unbound (name only)",
                        "endpoint": am.get("endpoint"), "span": f"forest-plot row: {m['label']} {m['counts']}"})
        return {"source": f"governing analysis forest plot ({am['figure']['caption']['quote']}; read from source, image not held)",
                "endpoint_for_outcome": am.get("endpoint")}, ins, []
    named, src = None, None
    if truth.get("relation") == "IDENTICAL_SET" and truth.get("present"):
        named = [{"name": p.get("trial"), "span": p.get("span")} for p in truth["present"] if p.get("trial")]
        src = "comparator-truth named set (trials located in the comparator text; count " \
              f"{truth.get('expected_count')} stated there)"
    ts = comp.get("comparator_trial_set") or {}
    if named is None and ts.get("status") == "MEASURED" and ts.get("trials"):
        named = [{"name": (t if isinstance(t, str) else t.get("name")), "span": ts.get("source_snippet")}
                 for t in ts["trials"]]
        src = f"second-pass named trials located in the comparator text ({ts.get('source_kind')})"
    if not named:
        return None
    ins = []
    for n in named:
        fams = set() if generic_label(n["name"]) else (acr_idx.get(norm_name(n["name"])) or set())
        ins.append({"name": n["name"], "family": (next(iter(fams)) if len(fams) == 1 else None), "alias_ids": [],
                    "identity": ("bound by acronym" if len(fams) == 1 else
                                 "ambiguous acronym (several families)" if fams else "unbound (name only)"),
                    "endpoint": None, "span": n.get("span")})
    return {"source": src, "endpoint_for_outcome": None}, ins, []


def compute(review: dict, report_year: Callable[[str], Optional[int]],
            report_acronym: Callable[[str], Optional[str]] = lambda _r: None) -> dict:
    """The overlap relation of the primary outcome's pool with the registered comparator.
    report_year(report_id): a PUBLICATION report's year (None for registry records / unknown).
    report_acronym(registry_id): the registry record's own acronym field, or None."""
    comp = review.get("comparator") or {}
    comp_year = _year(comp.get("year"))
    prim = _primary(review) or {}
    fams = {f["family_id"]: f for f in _families(review)}
    rows = [t for t in prim.get("trials") or [] if isinstance(t, dict)]

    ours, ours_keys = [], {}
    for t in rows:
        fid = t.get("family_id") or t.get("id") or t.get("label")
        al = (fams.get(fid) or {}).get("aliases") or {}
        reports = al.get("report_ids") or [t.get("label") or t.get("id")]
        dated = sorted({(str(r), y) for r in reports for y in [report_year(str(r))] if y is not None}, key=lambda x: (x[1], x[0]))
        ours.append({"family_id": fid, "row_id": t.get("id"), "label": t.get("label"),
                     "earliest_report": ({"report_id": dated[0][0], "year": dated[0][1]} if dated else None)})
        ours_keys[fid] = [k for k in (fid, t.get("id"), t.get("label"), *(al.get("report_ids") or []),
                                      *(al.get("registry_ids") or []), *(al.get("dois") or []),
                                      *(al.get("bib_keys") or [])) if k]
    out = {"outcome": prim.get("name"), "comparator_pmid": comp.get("pmid"), "comparator_year": comp_year,
           "ours": ours, "ours_k": len(ours), "membership_rule": NO_DATE_RULE, "constraints": []}
    if not ours:
        return _finish(out, "NOT_ENUMERABLE", basis="no pooled trials for the primary outcome")

    got = _members(review, _panel_entry(review), prim.get("name"), _acronym_index(review, report_acronym), ours_keys)
    if got is None:
        out["theirs"] = {"status": "NOT_ENUMERATED",
                         "note": "the registered comparator's trial set is not enumerated in a typed, located source"}
        return _finish(out, "NOT_ENUMERABLE", basis="comparator trial set not enumerated")

    meta, ins, outs = got
    if meta.get("ambiguous"):
        out["theirs"] = {"status": "AMBIGUOUS", **meta}
        out["constraints"].append("comparator rows share an identifier: " + "; ".join(meta["ambiguous"]))
        return _finish(out, "NOT_ENUMERABLE", basis="enumerated comparator set with ambiguous row identities")
    ours_set = {o["family_id"] for o in ours}
    for m in ins + outs:
        # bound_to = one of OUR POOLED families; a member that is a non-pooled family of our ledger is a known
        # trial on their side only (it is reported in the inventory comparison, never counted as shared)
        m["bound_to"] = m.get("family") if m.get("family") in ours_set else None
    out["theirs"] = {"status": "ENUMERATED", **meta, "members": ins, "out_of_scope": outs}
    # theirs is counted in TRIALS: rows resolving to the same family are one trial
    out["theirs_k"] = len({m.get("family") or ("row:" + m["name"]) for m in ins})
    bound_ours = {m["bound_to"] for m in ins if m["bound_to"]}
    # a member identified by an alias (PMID/DOI) or a bibliographic key is a KNOWN trial: if it is not bound to one of
    # ours it is theirs-only. Only a member with no identifier at all is an unknown identity.
    # KNOWN-and-distinct needs an identifier our families can be COMPARED on: a panel alias (PMID/DOI) always can;
    # a bibliographic key (journal:year:volume:first page) only when some pooled family carries bibliographic keys
    # (a journal-route record) -- otherwise a bib-key-only row could be one of ours and is an unknown identity.
    ours_have_bib = any(str(k).startswith("bib:") for keys in ours_keys.values() for k in keys)
    known = lambda m: (bool(m.get("family")) or m["identity"] == "bound by panel alias"
                       or (m["identity"].startswith("identified by bibliographic key") and ours_have_bib))
    unbound = [m["name"] for m in ins if not m["bound_to"] and not known(m)]
    undecidable = [o["family_id"] for o in ours if o["family_id"] not in bound_ours]
    if unbound and undecidable:
        out["constraints"].append(
            f"{len(ins) - len(unbound)} of {len(ins)} comparator trial(s) bound to a trial family; unbound: "
            f"{', '.join(unbound)}; pooled famil(ies) {', '.join(undecidable)} could be among them, so the shared set "
            "cannot be decided")
        return _finish(out, "NOT_ENUMERABLE", basis="enumerated comparator set with unbound members")
    out["inventory_comparison"] = _inventory(review, ins)
    shared = sorted(bound_ours)
    only_ours = [o["family_id"] for o in ours if o["family_id"] not in bound_ours]
    only_theirs = [m["name"] for m in ins if not m["bound_to"]]
    out.update(shared=shared, shared_k=len(shared), only_ours=only_ours, only_theirs=only_theirs)
    # participant level: a shared trial analysed in a different population on the comparator's side
    ours_pop = {t.get("family_id") or t.get("id"): (t.get("analysis_population") or "the randomised population as pooled here")
                for t in prim.get("trials") or [] if isinstance(t, dict)}
    part = []
    for m in ins:
        if m.get("bound_to") and m.get("analysis_population"):
            same = str(m["analysis_population"]).strip().lower() == str(ours_pop.get(m["bound_to"])).strip().lower()
            part.append({"family": m["bound_to"], "comparator_trial": m["name"],
                         "comparator_population": m["analysis_population"], "our_population": ours_pop.get(m["bound_to"]),
                         "state": "SAME_PARTICIPANTS" if same else "SAME_TRIAL_DIFFERENT_PARTICIPANTS"})
    if part:
        out["participant_level"] = part
        diff = [p["family"] for p in part if p["state"] != "SAME_PARTICIPANTS"]
        if diff:
            out["constraints"].append("shared trial(s) analysed in a different population by the comparator: "
                                      + ", ".join(diff) + " (a trial-name match is not the same participants)")
    if not shared:
        rel = "DISJOINT"
    elif not only_ours and not only_theirs:
        rel = "IDENTICAL_SET"
    elif not only_ours:
        rel = "SUBSET"
    elif not only_theirs:
        rel = "SUPERSET"
    else:
        rel = "OVERLAPPING"
    return _finish(out, rel, basis="set operation on the enumerated comparator trial set")


def _inventory(review: dict, members: list) -> dict:
    """The comparator's trials against our BROADER eligible inventory -- kept apart from the pooled-set relation. A
    comparator trial we do not pool is not automatically 'missing eligible': it may be in our ledger and screened
    out (open-label, another population), eligible but not poolable, or absent from our records altogether."""
    scr = {str(x.get("id")): x for x in ((review.get("screening") or {}).get("records") or [])}
    fams = {f["family_id"]: f for f in _families(review)}
    prim = _primary(review) or {}
    absent = {_key(str(a.get("id") or "").replace("PMID ", "")): a for a in prim.get("declared_absent_trials") or []}
    rows = []
    design_re = re.compile(r"\b(double[- ]blind|single[- ]blind|open[- ]label)\b[^.;]{0,20}?\b(RCT|randomi[sz]ed|trial)\b", re.I)
    for m in members:
        _d = design_re.search(m.get("span") or "")
        row_design = ({"row_design_as_printed": _d.group(0)} if _d else {})
        if m.get("bound_to"):
            rows.append({"comparator_trial": m["name"], "status": "POOLED", "family": m["bound_to"], **row_design})
            continue
        ids = list(m.get("alias_ids") or [])
        if m.get("family"):
            ids = list(((fams.get(m["family"]) or {}).get("aliases") or {}).get("report_ids") or []) + ids
        decisions = [scr[i] for i in ids if i in scr]
        inc = [d for d in decisions if d.get("decision") == "include"]
        if inc:
            ab = next((absent[_key(i)] for i in ids if _key(i) in absent), None)
            rows.append({"comparator_trial": m["name"], "status": "ELIGIBLE_NOT_POOLED", "family": m.get("family"),
                         "record": inc[0].get("id"), "state": (ab or {}).get("state"),
                         "reason": (ab or {}).get("reason") or inc[0].get("reason"), **row_design})
        elif decisions:
            d = decisions[0]
            rows.append({"comparator_trial": m["name"], "status": "SCREENED_OUT", "family": m.get("family"),
                         "record": d.get("id"), "rule": d.get("rule_id"), "reason": d.get("reason"), **row_design})
        elif m.get("family"):
            rows.append({"comparator_trial": m["name"], "status": "IN_LEDGER_NOT_SCREENED", "family": m["family"], **row_design})
        else:
            rows.append({"comparator_trial": m["name"], "status": "NOT_IN_OUR_RECORDS",
                         "note": "no held record carries this trial's identity", **row_design})
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return {"rows": rows, "counts": counts,
            "note": "comparison with our eligible inventory; separate from the pooled-set relation"}


def set_invariant(ours_k, theirs_k, shared_k, only_ours_n=None) -> list:
    """V1.0.1 (esketamine review): arithmetic every served overlap must satisfy -- shared <= min(ours, theirs) and
    ours_only + shared = ours. The V1 manifest served ours=3, theirs=4, shared=4."""
    bad = []
    if all(isinstance(v, int) for v in (ours_k, theirs_k, shared_k)) and shared_k > min(ours_k, theirs_k):
        bad.append(f"shared {shared_k} > min(ours {ours_k}, theirs {theirs_k})")
    if isinstance(ours_k, int) and isinstance(shared_k, int) and isinstance(only_ours_n, int) and only_ours_n + shared_k != ours_k:
        bad.append(f"ours_only {only_ours_n} + shared {shared_k} != ours {ours_k}")
    return bad


def _finish(out: dict, relation: str, basis: str) -> dict:
    assert relation in RELATIONS, relation
    for k in ("theirs_k", "shared", "shared_k", "only_ours", "only_theirs"):
        out.setdefault(k, None)
    bad = set_invariant(out.get("ours_k"), out.get("theirs_k"), out.get("shared_k"),
                        len(out["only_ours"]) if isinstance(out.get("only_ours"), list) else None)
    if bad:   # fail closed: an impossible set is never served as a relation
        out["constraints"] = list(out.get("constraints") or []) + ["SET_INVARIANT_VIOLATED: " + "; ".join(bad)]
        out.update(shared=None, shared_k=None, only_ours=None, only_theirs=None)
        relation, basis = "NOT_ENUMERABLE", "set invariant violated -- " + "; ".join(bad)
    out.update(relation=relation, label=LABELS[relation], basis=basis)
    return out


def sentence(obj: Optional[dict]) -> str:
    """The one prose rendering, shared by the page, the manuscript and the index."""
    if not obj:
        return "Overlap with the published comparator was not computed."
    parts = [f"our pooled trial families {obj.get('ours_k')}"]
    if obj.get("theirs_k") is not None:
        parts.append(f"comparator trials {obj['theirs_k']}")
    if obj.get("shared_k") is not None:
        parts.append(f"shared {obj['shared_k']}")
    extra = ("; " + "; ".join(obj["constraints"])) if obj.get("constraints") else ""
    return (f"Computed overlap relation with the published comparator: {obj.get('relation')} ({obj.get('label')}); "
            f"{', '.join(parts)}; basis: {obj.get('basis')}{extra}.")


def attach(review: dict, rec_by_id: dict) -> dict:
    """Compute THE relation for this review and make the legacy `comparator.overlap` counts a projection of it, so
    every surface that prints ours/theirs/shared or a relation word reads this one object. Returns the comparator."""
    comp = dict(review.get("comparator") or {})
    ov = dict(comp.get("overlap") or {})

    def report_year(rid):
        r = rec_by_id.get(str(rid)) or {}
        return _year(r.get("year")) if r.get("id_type") == "pmid" else None

    def report_acronym(rid):
        r = rec_by_id.get(str(rid)) or {}
        return r.get("acronym") if r.get("id_type") == "nct" else None

    obj = compute(review, report_year, report_acronym)
    stated = ov.get("theirs_k")
    obj["theirs_k_stated"] = {"value": stated, "source": ov.get("theirs_k_source")} if stated is not None else None
    comp["overlap_relation"] = obj
    ov["ours_k"] = obj["ours_k"]
    if obj["theirs_k"] is not None:
        ov["theirs_k"] = obj["theirs_k"]
        ov["theirs_k_source"] = (f"{obj['theirs']['source']}: {obj['theirs_k']} comparator trial(s) for this outcome"
                                 + (f"; {len(obj['theirs']['out_of_scope'])} with another endpoint excluded"
                                    if obj["theirs"].get("out_of_scope") else ""))
    if obj["shared_k"] is not None:
        ov["shared_k"] = obj["shared_k"]
        ov["only_ours"] = list(obj["only_ours"] or [])
        ov["only_theirs"] = list(obj["only_theirs"] or [])
    else:
        ov["shared_k"] = "not computed: " + obj["basis"]
        ov["only_ours"], ov["only_theirs"] = [], []
    for k in ("shared_trials", "shared_k_measurement"):
        ov.pop(k, None)
    ov["relation"] = obj["relation"]
    ov["method"] = "computed overlap relation (harness/overlap_relation.py): " + obj["basis"]
    ov["note"] = sentence(obj)
    comp["overlap"] = ov
    return comp


def render_block(obj: Optional[dict]) -> str:
    """The one HTML rendering (comparator panel / page). Every word and count comes from the object."""
    import html as _html
    e = lambda x: _html.escape(str(x))
    if not obj:
        return ""
    out = [f"<section class='overlap-relation' data-relation='{e(obj.get('relation'))}'>"
           f"<h4>Computed overlap relation (primary outcome: {e(obj.get('outcome'))})</h4>"
           f"<p><strong>{e(obj.get('relation'))}</strong> &mdash; {e(obj.get('label'))}.</p>"
           f"<p>{e(sentence(obj))}</p>"]
    out.append("<table><tr><th>Our pooled trial family</th><th>Earliest held report</th></tr>" + "".join(
        f"<tr><td>{e(o['family_id'])}</td><td>{e((o.get('earliest_report') or {}).get('report_id') or '—')} "
        f"({e((o.get('earliest_report') or {}).get('year') or 'year unknown')})</td></tr>" for o in obj.get("ours") or [])
        + "</table>")
    th = obj.get("theirs") or {}
    if th.get("status") == "ENUMERATED":
        out.append(f"<p>Comparator trial set: {e(th.get('source'))}"
                   + (f"; endpoint for this outcome: {e(th.get('endpoint_for_outcome'))}" if th.get("endpoint_for_outcome") else "")
                   + ".</p><table><tr><th>Comparator trial</th><th>Endpoint</th><th>Identity</th><th>Our family</th></tr>"
                   + "".join(f"<tr><td>{e(m['name'])}</td><td>{e(m.get('endpoint') or '—')}</td><td>{e(m['identity'])}</td>"
                             f"<td>{e(m.get('bound_to') or '—')}</td></tr>" for m in th.get("members") or [])
                   + "".join(f"<tr><td>{e(m['name'])}</td><td>{e(m.get('endpoint') or '—')}</td>"
                             "<td colspan='2'>out of scope for this outcome (another endpoint)</td></tr>"
                             for m in th.get("out_of_scope") or []) + "</table>")
    else:
        out.append(f"<p>Comparator trial set: NOT ENUMERATED ({e(th.get('note') or 'no typed source')}).</p>")
    out.append(f"<p class='small'>{e(obj.get('membership_rule') or NO_DATE_RULE)}.</p>")
    for p_ in obj.get("participant_level") or []:
        out.append(f"<p><code>{e(p_['state'])}</code>: {e(p_['comparator_trial'])} ({e(p_['family'])}) -- comparator "
                   f"analyses {e(p_['comparator_population'])}; we pool {e(p_['our_population'])}.</p>")
    inv = obj.get("inventory_comparison") or {}
    if inv.get("rows"):
        out.append("<h5>Comparator trials against our eligible inventory (separate from the pooled-set relation)</h5>"
                   "<table><tr><th>Comparator trial</th><th>Our status</th><th>Detail</th></tr>" + "".join(
                       f"<tr><td>{e(r['comparator_trial'])}</td><td>{e(r['status'])}</td><td>"
                       + e("; ".join(str(x) for x in (r.get("rule"), r.get("state"), r.get("reason") or r.get("note"),
                                                      ("comparator row: " + r["row_design_as_printed"]) if r.get("row_design_as_printed") else None)
                                     if x)) + "</td></tr>" for r in inv["rows"]) + "</table>")
    if obj.get("theirs_k_stated"):
        out.append(f"<p>Trial count the comparator states (a different quantity from its set for this outcome): "
                   f"{e(obj['theirs_k_stated'].get('value'))}.</p>")
    return "".join(out) + "</section>"


def short_sentence(obj: Optional[dict]) -> str:
    """The manuscript form: relation word, counts and basis only (no report identifiers)."""
    if not obj:
        return ""
    parts = [f"{obj.get('ours_k')} pooled trial famil{'y' if obj.get('ours_k') == 1 else 'ies'}"]
    if obj.get("theirs_k") is not None:
        parts.append(f"{obj['theirs_k']} comparator trial(s) for this outcome")
    if obj.get("shared_k") is not None:
        parts.append(f"{obj['shared_k']} shared")
    return (f"Against the published comparator the computed trial-set relation is {obj.get('relation')} "
            f"({obj.get('label')}): {', '.join(parts)}; basis: {obj.get('basis')}.")


def numerals(obj: Optional[dict]) -> set:
    """The integers the object carries, for the manuscript/index number gates."""
    return {str(v) for v in ((obj or {}).get("ours_k"), (obj or {}).get("theirs_k"), (obj or {}).get("shared_k"))
            if isinstance(v, int) and not isinstance(v, bool)}


_UNICODE_HYPHENS = {c: "-" for c in (0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2015, 0x2212)}
