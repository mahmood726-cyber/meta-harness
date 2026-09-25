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
    """(scope label, groups) for every groups-defining object of a ClinicalTrials.gov v2 record, labelled the way
    check_witness.token_place labels a witness's scope (a measure by its title, the AE module as 'eventGroups')."""
    rs = reg.get("resultsSection") or {}
    out = []
    for m in (rs.get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []:
        out.append((m.get("title"), m.get("groups") or []))
    ae = rs.get("adverseEventsModule") or {}
    if ae.get("eventGroups"):
        out.append(("eventGroups", ae["eventGroups"]))
    for mod, key in (("baselineCharacteristicsModule", "groups"), ("participantFlowModule", "groups")):
        g = (rs.get(mod) or {}).get(key)
        if g:
            out.append((mod, g))
    return out


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
        for label, groups in registry_scopes(reg):
            gi, gc = _classify_arms(groups, il, cl)
            entry = {"nct": nct, "scope": label, "n_groups": len(groups)}
            if gi and gc and gi != gc:
                entry.update(intervention_group=gi, comparator_group=gc, state="CLASSIFIED")
            else:
                entry.update(state="UNCLASSIFIED")
            roles["registry"].append(entry)
    return roles
