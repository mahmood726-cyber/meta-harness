"""The `arm_roles` block every witness packet carries (the main lane's ARM_ROLE_ANCHOR contract, item 36).

Role is the PROTOCOL's, never the extraction's:
  intervention / comparator : the topic config's canonical terms (topics/<slug>.json intervention_terms,
                              comparator_terms) -- the same source the pipeline reads (pipeline.py passes them on);
  registry                  : for every registry scope that defines groups (each outcome measure, the adverse-event
                              eventGroups, the baseline and participant-flow groups), the (intervention, comparator)
                              group ids assigned by harness.ctgov_results._classify_arms from the group TITLES and those
                              terms -- the pipeline's own classifier, including its two-arm elimination fallback. A
                              scope where it cannot assign two distinct groups is listed as unclassified, never guessed.
check_witness.py T6 reads the terms; T5b requires a registry-owned arm's group id to be the one classified for its role
in the scope its witnesses sit in.
usage (library): arm_roles_for(slug, [registry json paths]) ; CLI: stamp_arm_roles.py"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from harness.ctgov_results import _classify_arms  # noqa: E402  (the pipeline's classifier, not a copy)


def topic_terms(slug):
    p = os.path.join(ROOT, "topics", f"{slug}.json")
    if not os.path.exists(p):
        return None, None, None
    cfg = json.load(open(p, encoding="utf-8"))
    return cfg.get("intervention_terms") or [], cfg.get("comparator_terms") or [], f"topics/{slug}.json"


def registry_scopes(reg):
    """(scope label, kind, measure index, groups) for every groups-defining object of a ClinicalTrials.gov v2 record,
    labelled the way check_witness.token_place labels a witness's scope: a measure by its title (kind 'measure', with
    its index -- titles can repeat), the AE groups as 'eventGroups', the baseline and participant-flow modules by name."""
    rs = reg.get("resultsSection") or {}
    out = []
    for k, m in enumerate((rs.get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []):
        out.append((m.get("title"), "measure", k, m.get("groups") or []))
    ae = rs.get("adverseEventsModule") or {}
    if ae.get("eventGroups"):
        out.append(("eventGroups", "eventGroups", None, ae["eventGroups"]))
    for mod in ("baselineCharacteristicsModule", "participantFlowModule"):
        g = (rs.get(mod) or {}).get("groups")
        if g:
            out.append((mod, "module", None, g))
    return out


def classify(groups, il, cl):
    """The pipeline's _classify_arms, accepted ONLY when it is unambiguous (review 5, 2026-09-25: on a multi-arm scope
    its last match wins -- a subgroup, a follow-up phase, a factorial cell -- and a title matching both vocabularies,
    'Drugx plus placebo-matched ...', or a substring such as 'placebo' inside the drug arm's title, reversed the roles).
    A group is decisively the intervention when its title carries an intervention term and no comparator term, and
    decisively the comparator when the reverse; CLASSIFIED needs exactly one of each (or, in a two-group scope, one
    decisive group and one matching neither), and _classify_arms must agree. Otherwise UNCLASSIFIED, with the reason."""
    def has(title, terms):
        return any(t and t in title for t in terms)
    dec_i = [g.get("id") for g in groups if has((g.get("title") or "").lower(), il) and not has((g.get("title") or "").lower(), cl)]
    dec_c = [g.get("id") for g in groups if has((g.get("title") or "").lower(), cl) and not has((g.get("title") or "").lower(), il)]
    neither = [g.get("id") for g in groups if not has((g.get("title") or "").lower(), il) and not has((g.get("title") or "").lower(), cl)]
    gi, gc = _classify_arms(groups, il, cl)
    if len(dec_i) == 1 and len(dec_c) == 1:
        want = (dec_i[0], dec_c[0])
    elif len(groups) == 2 and len(neither) == 1 and len(dec_i) + len(dec_c) == 1:
        want = (dec_i[0], neither[0]) if dec_i else (neither[0], dec_c[0])
    else:
        return None, (f"{len(groups)} groups: {len(dec_i)} decisively intervention, {len(dec_c)} decisively comparator"
                      f" -- not a single contrast")
    if (gi, gc) != want:
        return None, f"_classify_arms says {(gi, gc)}, the decisive titles say {want}"
    return want, None


def arm_roles_for(slug, registry_paths=()):
    i_terms, c_terms, src = topic_terms(slug)
    roles = {"intervention": i_terms, "comparator": c_terms, "source": src, "registry": []}
    if not src:
        roles["source"] = None
        return roles
    il, cl = [t.lower() for t in i_terms], [t.lower() for t in c_terms]
    for p in registry_paths:
        reg = json.load(open(p, encoding="utf-8"))
        nct = ((reg.get("protocolSection") or {}).get("identificationModule") or {}).get("nctId") or os.path.basename(p)
        for label, kind, idx, groups in registry_scopes(reg):
            pair, why = classify(groups, il, cl)
            entry = {"nct": nct, "scope": label, "kind": kind, "index": idx, "n_groups": len(groups)}
            if pair:
                entry.update(intervention_group=pair[0], comparator_group=pair[1], state="CLASSIFIED")
            else:
                entry.update(state="UNCLASSIFIED", why=why)
            roles["registry"].append(entry)
    return roles
