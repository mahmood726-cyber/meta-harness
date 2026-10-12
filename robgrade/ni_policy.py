"""Pre-registered scoring for the NI policy (outputs/robgrade/NI_POLICY.md): agreement with the published per-trial
judgements as n of N, two ways -- over ALL domain pairs, and EXCLUDING the pairs whose (our) domain judgement is
NI-driven -- plus the NI-driven stratum itself, so nothing excluded disappears from view. A pair without an ni_driven
label is refused: an unlabelled pair would silently fall into one side or the other."""

DOMS = ("D1", "D2", "D3", "D4", "D5")


def _tally(pairs):
    out = {d: {"agree": 0, "N": 0} for d in DOMS}
    for p in pairs:
        out[p["domain"]]["N"] += 1
        out[p["domain"]]["agree"] += p["ours"] == p["theirs"]
    out["all"] = {"agree": sum(out[d]["agree"] for d in DOMS), "N": sum(out[d]["N"] for d in DOMS)}
    return out


def two_way(pairs):
    for p in pairs:
        if not isinstance(p.get("ni_driven"), bool):
            raise ValueError(f"pair without an ni_driven label: {p}")
    return {"all": _tally(pairs), "excluding_ni_driven": _tally([p for p in pairs if not p["ni_driven"]]),
            "ni_driven_only": _tally([p for p in pairs if p["ni_driven"]])}
