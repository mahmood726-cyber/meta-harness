"""Phase 3 availability census (read-only, typed): for each identity-less MISSING trial with a PMID, where an OPEN full
text of the report exists NOW and under which licence.
  held PMC index   outputs/k_gap/fulltext_index.json (what the acquisition lane could read) + g1_trial_acquire.pmc_copy
  Europe PMC       REST search EXT_ID:<pmid> SRC:MED, resultType=core (pmcid, isOpenAccess, license, doi)
  Unpaywall        v2 <doi> (is_oa, best_oa_location: host_type, license, version, url)
Class per trial (D8: only CC BY / CC0 text may enter a prompt; other open text is regex-only):
  OPEN_CC_MODEL_READABLE   a CC BY / CC0 copy (Europe PMC licence or Unpaywall licence cc-by / cc0 / pd)
  OPEN_CC_OTHER_REGEX_ONLY a CC licence that is not BY/CC0 (NC / ND / SA): typed reading only
  OPEN_NO_LICENCE_REGEX_ONLY an open copy with no stated licence (bronze / author manuscript): typed reading only
  NOT_OPEN                 no open copy found by either service
  LOOKUP_FAILED            a service did not answer (never read as NOT_OPEN)
"""
import collections
import json
import os
import sys
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
os.chdir(ROOT)
from harness import http  # noqa: E402

EMAIL = "meta-harness@example.org"
import glob  # noqa: E402

# scope (default): the phase-1 funnel's identity-less MISSING trials (no NCT) that carry a PMID.
# --registered: the REGISTERED trials (an NCT) phases 1-2 did not fill, that carry a PMID (the source ladder's phase 3 is
# the remainder, not only the identity-less) -> PHASE3_OPEN_CENSUS_REGISTERED.json
REGISTERED = "--registered" in sys.argv


def _admitted(slug):
    out = set()
    for sub in ("g1_acquired_registry", "g1_acquired_regulator"):
        p_ = os.path.join(ROOT, "registry", sub, f"{slug}.json")
        if os.path.exists(p_):
            out |= {r["label"] for r in json.load(open(p_, encoding="utf-8")).get("rows") or [] if r.get("verdict") == "ADMITTED"}
    return out


scope = []
for _f in sorted(glob.glob(os.path.join(ROOT, "outputs", "k_gap", "registry_fill", "*.funnel.json"))):
    _d = json.load(open(_f, encoding="utf-8"))
    _done = _admitted(_d["slug"])
    scope += [dict(r, slug=_d["slug"]) for r in _d["rows"] if r.get("pmid") and r["label"] not in _done and
              ((bool(r.get("ncts")) and REGISTERED) or (not REGISTERED and r.get("stage") == "MISSING" and not r.get("ncts")))]
idx = json.load(open("outputs/k_gap/fulltext_index.json", encoding="utf-8"))
MODEL_OK = ("cc-by", "cc0", "cc by", "public-domain", "pd")


def lic_class(lic):
    l = (lic or "").lower().replace("_", "-")
    if not l:
        return None
    if l in ("cc-by", "cc0", "pd", "public-domain") or l.startswith("cc-by-4") or l == "cc by":
        return "CC_BY_OR_CC0"
    if l.startswith("cc"):
        return "CC_OTHER"
    return "OTHER:" + l


def epmc(pmid):
    try:
        st, b = http.get_raw("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                             {"query": f"EXT_ID:{pmid} AND SRC:MED", "resultType": "core", "format": "json"},
                             tries=3, timeout=60)
        r = (json.loads(b).get("resultList") or {}).get("result") or []
        if st != 200:
            return {"state": f"HTTP_{st}"}
        if not r:
            return {"state": "NO_RECORD"}
        r = r[0]
        return {"state": "OK", "pmcid": r.get("pmcid"), "is_oa": r.get("isOpenAccess"), "license": r.get("license"),
                "doi": r.get("doi"), "in_epmc": r.get("inEPMC"), "in_pmc": r.get("inPMC")}
    except Exception as exc:  # noqa: BLE001 - typed
        return {"state": "LOOKUP_FAILED", "error": str(exc)[:100]}


def upw(doi):
    if not doi:
        return {"state": "NO_DOI"}
    try:
        st, b = http.get_raw("https://api.unpaywall.org/v2/" + urllib.parse.quote(doi), {"email": EMAIL}, tries=3,
                             timeout=60)
        if st != 200:
            return {"state": f"HTTP_{st}"}
        d = json.loads(b)
        loc = d.get("best_oa_location") or {}
        return {"state": "OK", "is_oa": d.get("is_oa"), "oa_status": d.get("oa_status"), "host": loc.get("host_type"),
                "license": loc.get("license"), "version": loc.get("version"),
                "url": loc.get("url_for_pdf") or loc.get("url")}
    except Exception as exc:  # noqa: BLE001
        code = getattr(exc.__cause__, "code", None)
        return {"state": "NOT_IN_UNPAYWALL" if code == 404 else "LOOKUP_FAILED", "error": str(exc)[:100]}


rows = []
for t in scope:
    pmid = str(t["pmid"])
    e = epmc(pmid)
    time.sleep(0.3)
    u = upw(e.get("doi"))
    time.sleep(0.3)
    held = idx.get(pmid) or {}
    lics = [lic_class(e.get("license")) if e.get("is_oa") == "Y" else None,
            lic_class(u.get("license")) if u.get("is_oa") else None]
    if "CC_BY_OR_CC0" in lics:
        cls = "OPEN_CC_MODEL_READABLE"
    elif "CC_OTHER" in lics:
        cls = "OPEN_CC_OTHER_REGEX_ONLY"
    elif e.get("is_oa") == "Y" or u.get("is_oa") or e.get("pmcid"):
        cls = "OPEN_NO_LICENCE_REGEX_ONLY"
    elif e.get("state") == "LOOKUP_FAILED" or u.get("state") == "LOOKUP_FAILED":
        cls = "LOOKUP_FAILED"
    else:
        cls = "NOT_OPEN"
    rows.append({"slug": t["slug"], "label": t["label"], "pmid": pmid, "blocker_now": t.get("blocker_now"),
                 "route_now": t.get("route_now"), "held_pmcid": held.get("pmcid"),
                 "held_copy_licence": held.get("copy_licence"), "europepmc": e, "unpaywall": u, "class": cls,
                 "new_vs_held": bool(e.get("pmcid")) and not held.get("pmcid")})
    print(cls, "|", t["slug"][:22], "|", t["label"][:26], "|", pmid, "| epmc", e.get("pmcid"), e.get("license"),
          "| upw", u.get("oa_status"), u.get("license"), "| held", held.get("pmcid"), flush=True)

out = {"retrieved": time.strftime("%Y-%m-%d"), "n": len(rows), "class": dict(collections.Counter(r["class"] for r in rows)),
       "pmcid_not_in_held_index": sum(r["new_vs_held"] for r in rows), "rows": rows}
json.dump(out, open(os.path.join(ROOT, "outputs", "k_gap", "registry_fill",
                                 "PHASE3_OPEN_CENSUS_REGISTERED.json" if REGISTERED else "PHASE3_OPEN_CENSUS.json"),
                    "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("CENSUS", out["class"], "pmcid not in held index:", out["pmcid_not_in_held_index"])
