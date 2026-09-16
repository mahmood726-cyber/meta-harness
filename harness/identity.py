"""Trial-identity and publication-unit resolution.

A trial is known by several identifiers -- NCT, PMID, PMCID, DOI, acronym. A check keyed on one
identifier space silently passes on a trial the corpus holds in another. This builds one identity per
trial from the committed records by union-ing records that share any identifier, so a check can
resolve any id to the full set of identifiers the corpus knows for that trial.

Resolution is only as complete as the committed links. A record carrying just a PMID+DOI (no NCT)
cannot be resolved to NCT-space from committed data alone; curated family rows fill only
audit-identified report/trial links and are reported, never inferred.
"""

NON_TRIAL_PUBLICATION_ROLES = {"secondary", "economic", "protocol", "correction"}


def _norm(x):
    s = str(x or "").strip()
    for sep in ("Â·", "·", "�"):
        if sep in s:
            s = s.split(sep)[-1].strip()
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
    """Union-find over records sharing any identifier.

    Returns a list of identity dicts:
    {members:[record ids], nct:set, pmid:set, doi:set, acronym:set}.
    """
    records = list(records or [])
    parent = list(range(len(records)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        parent[find(i)] = find(j)

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
            if r.get("id_type") == "pmid":
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


def _family_id(idobj):
    if idobj.get("acronym"):
        return sorted(idobj["acronym"])[0].upper()
    if idobj.get("nct"):
        return sorted(idobj["nct"])[0]
    if idobj.get("pmid"):
        return "PMID:" + sorted(idobj["pmid"])[0]
    if idobj.get("doi"):
        return "DOI:" + sorted(idobj["doi"])[0]
    members = [m for m in idobj.get("members", []) if m]
    return "REC:" + (sorted(members)[0] if members else "unknown")


def _role_from_kind(kind):
    k = str(kind or "").lower()
    if any(w in k for w in ("economic", "cost-effect", "cost effect", "cost-utility")):
        return "economic"
    if any(w in k for w in ("protocol", "design", "rationale")):
        return "protocol"
    if any(w in k for w in ("erratum", "correction", "corrigendum", "retraction")):
        return "correction"
    if any(w in k for w in ("secondary", "post-hoc", "post hoc", "substudy", "sub-study",
                            "sub-analysis", "subanalysis", "pooled analysis", "duplicate")):
        return "secondary"
    return "secondary" if k else "primary"


def _role_from_record(rec):
    title = str(rec.get("title") or "").lower()
    pts = " ".join(str(p).lower() for p in rec.get("pubtypes") or [])
    text = title + " " + pts
    if any(w in text for w in ("erratum", "correction", "corrigendum", "retraction")):
        return "correction"
    if "protocol" in text or "rationale and design" in title or "study design" in title:
        return "protocol"
    if any(w in title for w in ("cost-effect", "cost effect", "economic", "cost-utility")):
        return "economic"
    if any(w in title for w in ("secondary analysis", "post-hoc", "post hoc", "substudy",
                                "sub-study", "sub-analysis", "subanalysis", "pooled analysis")):
        return "secondary"
    return "primary"


def _companion_family(companion):
    return (companion.get("trial_family_id") or companion.get("parent")
            or companion.get("parent_pmid") or companion.get("pmid"))


def build_publication_units(records, companion_reports=None):
    """Return raw-id -> publication-unit metadata.

    Identifier union supplies the default trial family. Curated companion rows can then bind
    secondary/economic/protocol/correction publications to a parent trial even when the record lacks a
    shared NCT/DOI/PMID link in the committed cache.
    """
    records = list(records or [])
    companions = {str(c.get("pmid")): dict(c) for c in (companion_reports or []) if c.get("pmid")}
    identities = build_identities(records)
    units = {}

    def put(key, ann):
        nk = _norm(key)
        if nk:
            units[nk] = dict(ann)

    for idobj in identities:
        fid = _family_id(idobj)
        ann = {"trial_family_id": fid, "publication_role": "primary"}
        for key in set(idobj.get("members", [])) | set(idobj.get("pmid", [])) | set(idobj.get("nct", [])):
            put(key, ann)

    by_id = {_norm(r.get("id")): r for r in records}
    for rid, rec in by_id.items():
        ann = dict(units.get(rid, {"trial_family_id": rid or "unknown"}))
        ann["publication_role"] = _role_from_record(rec)
        put(rid, ann)

    # If a curated companion names a pooled/parent PMID, rename the whole parent identity to the
    # human family key (e.g. COLCOT instead of NCT02551094) so parent and companions share one id.
    for comp in companions.values():
        parent = _norm(comp.get("parent_pmid"))
        family = _companion_family(comp)
        if parent and parent in units and family:
            old = units[parent].get("trial_family_id")
            for ann in units.values():
                if ann.get("trial_family_id") == old:
                    ann["trial_family_id"] = family
                    ann.setdefault("trial_family_label", comp.get("parent") or family)

    for pmid, comp in companions.items():
        family = _companion_family(comp)
        role = comp.get("publication_role") or _role_from_kind(comp.get("kind"))
        ann = {
            "trial_family_id": family,
            "trial_family_label": comp.get("parent") or family,
            "publication_role": role,
            "publication_state": f"SECONDARY_PUBLICATION_OF {family}",
            "secondary_publication_of": family,
        }
        if comp.get("parent_pmid"):
            ann["parent_pmid"] = str(comp.get("parent_pmid"))
        put(pmid, ann)
    return units


def annotate_item(item, units):
    """Attach publication-unit fields to one rendered screening/outcome item in-place."""
    if not isinstance(item, dict):
        return item
    ann = units.get(_norm(item.get("id"))) or {}
    if ann:
        for k, v in ann.items():
            item.setdefault(k, v)
    else:
        fid = _norm(item.get("id")) or "unknown"
        item.setdefault("trial_family_id", fid)
        item.setdefault("publication_role", "primary")
    return item


def annotate_review(review, records, companion_reports=None):
    """Attach publication-unit metadata throughout a review object and return the unit map."""
    units = build_publication_units(records, companion_reports)
    for rec in ((review.get("screening") or {}).get("records") or []):
        annotate_item(rec, units)
    for outcome in review.get("outcomes") or []:
        for row in outcome.get("trials") or []:
            annotate_item(row, units)
        for row in outcome.get("declared_absent_trials") or []:
            annotate_item(row, units)
    review["publication_units"] = {
        "source": "harness.identity.build_publication_units",
        "n_records_annotated": len(units),
    }
    return units


def _family_of(item):
    return item.get("trial_family_id") or _norm(item.get("id"))


def unit_counts(items, *, exclude_families=None):
    """Return {'trials': family count, 'publications': row count} for annotated items."""
    exclude_families = set(exclude_families or [])
    publications = 0
    families = set()
    for item in items or []:
        family = _family_of(item)
        if not family or family in exclude_families:
            continue
        publications += 1
        if item.get("publication_role") not in NON_TRIAL_PUBLICATION_ROLES:
            families.add(family)
    return {"trials": len(families), "publications": publications}


def included_counts(review):
    recs = [r for r in ((review.get("screening") or {}).get("records") or [])
            if r.get("decision") == "include"]
    return unit_counts(recs)


def outcome_counts(outcome):
    pooled = unit_counts(outcome.get("trials") or [])
    pooled_families = {_family_of(t) for t in outcome.get("trials") or [] if _family_of(t)}
    absent = unit_counts(outcome.get("declared_absent_trials") or [], exclude_families=pooled_families)
    return {"pooled": pooled, "absent": absent}


def count_phrase(counts, noun="trial"):
    n_trials = counts.get("trials", 0)
    n_pubs = counts.get("publications", n_trials)
    if n_trials == 1:
        label = noun
    elif noun == "trial family":
        label = "trial families"
    else:
        label = noun + "s"
    if n_pubs != n_trials:
        return f"{n_trials} {label} ({n_pubs} publications)"
    return f"{n_trials} {label}"


def classify_screened_in_not_pooled(review):
    """Rows screened in but not pooled in any outcome, classified by publication unit."""
    pooled_record_ids = {
        _norm(t.get("id") or t.get("label"))
        for outcome in review.get("outcomes") or []
        for t in outcome.get("trials") or []
        if _norm(t.get("id") or t.get("label"))
    }
    pooled_families = {
        _family_of(t)
        for outcome in review.get("outcomes") or []
        for t in outcome.get("trials") or []
        if _family_of(t)
    }
    out = []
    for rec in ((review.get("screening") or {}).get("records") or []):
        if rec.get("decision") != "include":
            continue
        if _norm(rec.get("id")) in pooled_record_ids:
            continue
        family = _family_of(rec)
        if family not in pooled_families:
            continue
        if rec.get("publication_role") in {"secondary", "economic"}:
            out.append({
                "id": _norm(rec.get("id")),
                "trial_family_id": family,
                "publication_role": rec.get("publication_role"),
                "publication_state": rec.get("publication_state") or f"SECONDARY_PUBLICATION_OF {family}",
            })
    return out
