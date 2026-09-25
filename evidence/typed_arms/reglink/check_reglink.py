"""Mechanical check of the registry-linkage reading (reglink/BRIEF.md) and the neutral intermediate it produces.

For each arm link: the RFC-6901 pointer must resolve in the registry record whose sha256 the packet recorded, to an
object whose "id" (or "groupId") and "title" equal what the reader copied -- else LINK_REFUSED with the reason.
For each outcome candidate: the measure pointer must resolve; every per-group value/denominator pointer must resolve to
exactly the copied value, inside the candidate's own measure (pointer prefix), with a group_id the reader linked to one
of the row's arms. A candidate the reader calls same_outcome whose resolved numbers equal the written row's is
REGISTRY_CARRIES_OUTCOME_EQUAL (ownership should come from the registry); unequal is REGISTRY_CARRIES_OUTCOME_DIFFERS.
Nothing here edits a v2 observation: the output is evidence/typed_arms/reglink/REGISTRY_LINKS.json, a neutral format
awaiting the schema owner's answer on where registry arm identity lives when the outcome is not a registry measure.
usage: check_reglink.py <jobs_dir> <out.json>"""
import hashlib, json, os, sys


def resolve(doc, ptr):
    if not isinstance(ptr, str) or not ptr.startswith("/"):
        raise KeyError("not an RFC-6901 pointer")
    o = doc
    for part in ptr[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        o = o[int(part)] if isinstance(o, list) else o[part]
    return o


def num(x):
    try:
        return float(str(x).replace(",", "").strip())
    except ValueError:
        return None


def check_job(job):
    rows = json.load(open(os.path.join(job, "rows.json"), encoding="utf-8"))
    raw = open(os.path.join(job, rows["registry_file"]), "rb").read()
    if hashlib.sha256(raw).hexdigest() != rows["registry_sha256"]:
        return {"nct": rows["nct"], "error": "registry bytes differ from the packet's sha256"}
    reg = json.loads(raw)
    try:
        out = json.load(open(os.path.join(job, "out.json"), encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {"nct": rows["nct"], "error": f"no readable out.json ({type(e).__name__})"}
    got = {r.get("row_key"): r for r in out.get("rows", [])}
    res = []
    for row in rows["rows"]:
        g = got.get(row["row_key"]) or {}
        rec = {"row_key": row["row_key"], "population": row["population"], "nct": rows["nct"],
               "registry_file": f"evidence/typed_arms/registry/{rows['nct']}.json", "registry_sha256": rows["registry_sha256"],
               "outcome": row["outcome"], "arm_correspondence": g.get("arm_correspondence"), "arms": [], "outcome_candidates": []}
        gid_role = {}
        for arm in row["arms"]:
            ga = next((a for a in g.get("arms", []) if a.get("role") == arm["role"]), {})
            links = []
            for ln in ga.get("links", []):
                try:
                    o = resolve(reg, ln.get("pointer"))
                    rid = o.get("id") or o.get("groupId")
                    ok = rid == ln.get("id") and o.get("title") == ln.get("title")
                    why = None if ok else f"pointer resolves to id={rid!r} title={o.get('title')!r}"
                except (KeyError, IndexError, ValueError, TypeError, AttributeError) as e:
                    ok, why = False, f"pointer does not resolve ({type(e).__name__})"
                links.append({"pointer": ln.get("pointer"), "group_id": ln.get("id"), "title": ln.get("title"),
                              "state": "LINKED" if ok else "LINK_REFUSED", "why": why})
                if ok:
                    gid_role[(ln["pointer"].rsplit("/groups/", 1)[0].rsplit("/eventGroups/", 1)[0], ln["id"])] = arm["role"]
            rec["arms"].append({"role": arm["role"], "arm_name": arm["arm_name"], "links": links})
        want = {a["role"]: (a["events"], a["total"]) for a in row["arms"]}
        for c in g.get("outcome_candidates", []):
            cand = {"pointer": c.get("pointer"), "title": c.get("title"), "same_outcome": c.get("same_outcome"),
                    "why": c.get("why"), "per_group": [], "problems": []}
            try:
                resolve(reg, c.get("pointer"))
            except Exception:
                cand["problems"].append("measure pointer does not resolve")
            got_roles = {}
            for pg in c.get("per_group", []):
                item = dict(pg)
                for fld in ("value", "denominator"):
                    p = pg.get(f"{fld}_pointer")
                    try:
                        v = resolve(reg, p)
                        if isinstance(v, dict):   # an AE stats object carries both numbers
                            v = v.get("value", v.get("numAffected") if fld == "value" else v.get("numAtRisk"))
                        if num(v) != num(pg.get(fld)):
                            cand["problems"].append(f"{pg.get('group_id')} {fld}: pointer holds {v!r}, reader copied {pg.get(fld)!r}")
                    except Exception:
                        cand["problems"].append(f"{pg.get('group_id')} {fld}: pointer does not resolve")
                roles = {r for (scope, gid), r in gid_role.items() if gid == pg.get("group_id") and (c.get("pointer") or "").startswith(scope)}
                item["role"] = roles.pop() if len(roles) == 1 else None
                if item["role"]:
                    got_roles[item["role"]] = (num(pg.get("value")), num(pg.get("denominator")))
                cand["per_group"].append(item)
            if cand["problems"]:
                cand["state"] = "CANDIDATE_REFUSED"
            elif not c.get("same_outcome"):
                cand["state"] = "DIFFERENT_OUTCOME"
            elif set(got_roles) != set(want):
                cand["state"] = "SAME_OUTCOME_ARMS_NOT_LINKED_IN_THIS_MEASURE"
            elif all(got_roles[r] == (float(want[r][0]), float(want[r][1])) for r in want):
                cand["state"] = "REGISTRY_CARRIES_OUTCOME_EQUAL"
            else:
                cand["state"] = "REGISTRY_CARRIES_OUTCOME_DIFFERS"
            rec["outcome_candidates"].append(cand)
        n_links = sum(1 for a in rec["arms"] for x in a["links"] if x["state"] == "LINKED")
        rec["state"] = ("NO_READING" if not g else
                        "NOT_ONE_TO_ONE" if not str(g.get("arm_correspondence", "")).startswith("ONE_TO_ONE") else
                        "LINKED" if all(any(x["state"] == "LINKED" for x in a["links"]) for a in rec["arms"]) else
                        "PARTLY_LINKED" if n_links else "UNLINKED")
        res.append(rec)
    return {"nct": rows["nct"], "rows": res}


def main(jobs, out):
    doc = {"format": "evid2 neutral intermediate: registry arm links + registry outcome search, pending schema placement",
           "registrations": [check_job(os.path.join(jobs, d)) for d in sorted(os.listdir(jobs))
                             if os.path.isdir(os.path.join(jobs, d))]}
    rows = [r for g in doc["registrations"] for r in g.get("rows", [])]
    tally = {}
    for r in rows:
        tally[r["state"]] = tally.get(r["state"], 0) + 1
    cands = {}
    for r in rows:
        for c in r["outcome_candidates"]:
            cands[c["state"]] = cands.get(c["state"], 0) + 1
    doc["summary"] = {"rows": len(rows), "row_states": tally, "outcome_candidate_states": cands}
    json.dump(doc, open(out, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps(doc["summary"]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
