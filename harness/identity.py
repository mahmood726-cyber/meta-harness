"""Trial-identity resolution (NAMED_BUT_UNBOUND).

A trial is known by several identifiers -- NCT, PMID, PMCID, DOI, acronym. A check keyed on one
identifier space silently passes on a trial the corpus holds in another (the read-only session
found NAMED_BUT_UNBOUND is the majority state among adjudicated candidates). This builds ONE
identity per trial from the committed records by union-ing records that share ANY identifier, so a
check can resolve any id to the full set of identifiers the corpus knows for that trial.

Note on reach: resolution is only as complete as the committed links. A record carrying just a
PMID+DOI (no NCT) cannot be resolved to NCT-space from committed data alone; that cross-space link
needs external retrieval (CT.gov/PubMed). This module resolves everything the committed records
DO link, and the coverage it cannot reach is reported, never assumed.
"""


def _norm(x):
    s = str(x or "").strip()
    if "·" in s:
        s = s.split("·")[-1].strip()
    return s.replace("PMID ", "").replace("PMID:", "").strip()


def _ids_of(rec):
    ids = set()
    rid = _norm(rec.get("id"))
    if rid:
        ids.add(("id", rid))
        # an NCT that appears AS a record's id (id_type=nct) must collide with another record's
        # nct FIELD -- cross-tag any NCT-shaped value into the nct namespace regardless of field.
        if rid.upper().startswith("NCT"):
            ids.add(("nct", rid))
    for k in ("nct", "doi", "pmc", "pmcid"):
        v = rec.get(k)
        if v:
            ids.add((k, str(v).strip()))
    a = rec.get("acronym")
    if a:
        ids.add(("acronym", str(a).strip().lower()))
    return ids


def build_identities(records):
    """Union-find over records sharing any identifier. Returns a list of identity dicts:
    {members:[record ids], nct:set, pmid:set, doi:set, acronym:set}."""
    records = list(records or [])
    parent = list(range(len(records)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        parent[find(i)] = find(j)

    # map each identifier value -> first record index that carried it, union on collision
    seen = {}
    for i, r in enumerate(records):
        for tag, val in _ids_of(r):
            key = (tag, val)
            if key in seen:
                union(i, seen[key])
            else:
                seen[key] = i
    groups = {}
    for i, r in enumerate(records):
        groups.setdefault(find(i), []).append(r)
    out = []
    for members in groups.values():
        idobj = {"members": [], "nct": set(), "pmid": set(), "doi": set(), "acronym": set()}
        for r in members:
            idobj["members"].append(_norm(r.get("id")))
            if (r.get("id_type") == "pmid"):
                idobj["pmid"].add(_norm(r.get("id")))
            if r.get("nct"):
                idobj["nct"].add(str(r.get("nct")).strip())
            if r.get("doi"):
                idobj["doi"].add(str(r.get("doi")).strip())
            if r.get("acronym"):
                idobj["acronym"].add(str(r.get("acronym")).strip().lower())
        out.append(idobj)
    return out


def resolve(identifier, identities):
    """Return the identity object any identifier belongs to, or None."""
    v = _norm(identifier)
    vl = str(identifier or "").strip().lower()
    for idobj in identities:
        if (v in idobj["members"] or v in idobj["nct"] or v in idobj["pmid"]
                or v in idobj["doi"] or vl in idobj["acronym"]):
            return idobj
    return None
