"""ROUTES LEDGER: every open route of the ALL-16 list, per UNMATCHED trial, for the active topics (CLOSE-4 dispatch, 8 Oct:
"run the not-yet-tried routes on every unmatched trial, recorded, regex first, and fold the per-route ledger into
cache/<slug>/routes_ledger.json").

Routes and how each is tried (one recorded attempt per HOST: a host that refuses at its door refuses every trial, so the
host attempt is the trial's attempt and is cited by every row -- hammering a refusing host trial by trial is not tried):
  ANZCTR        www.anzctr.org.au search                  TLS/HTTP, challenge detected -> BOT_CHALLENGE (never solved)
  JRCT          jrct.niph.go.jp / rctportal.niph.go.jp    TLS handshake refused for every client -> TLS_REFUSED
  TGA           www.tga.gov.au AusPAR search              bounded retries with backoff -> UNREACHABLE after them
  CADTH         www.cda-amc.ca search                     challenge -> BOT_CHALLENGE (never solved)
  CORE          api.core.ac.uk                            needs an account key -> NOT_TRIED_ACCOUNT_REQUIRED (Mahmood)
and, per trial, the routes already recorded in this lane (registry/open_sources.json: EUCTR / CTIS / OPEN_LOCATION;
registry/regulatory_sources.json: FDA / EMA / NICE documents naming the trial; PMDA when a record exists).
Population: every trial row of the topic's G1 tracker (main) that is not PRIMARY-matched and not named out of scope.

    python scripts/g1_routes_ledger.py SLUG [SLUG ...] [--ref=origin/main]
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
ATTEMPTS = os.path.join(ROOT, "registry", "route_attempts.json")

HOSTS = {
    "ANZCTR": ["https://www.anzctr.org.au/TrialSearch.aspx?searchTxt=denosumab&isBasic=True"],
    "JRCT": ["https://jrct.niph.go.jp/en-search?searchText=denosumab", "https://rctportal.niph.go.jp/en/result?keyword=denosumab"],
    "TGA": ["https://www.tga.gov.au/resources/auspar?keywords=denosumab"],
    "CADTH": ["https://www.cda-amc.ca/search?keywords=denosumab"],
}
BACKOFF = (0, 20, 60)


def attempt(url, timeout=90):
    import g1_open_sources as osrc
    st, ct, body, final = osrc.fetch(url, timeout=timeout)
    rec = {"url": url, "status": st, "content_type": ct, "bytes": len(body or b""),
           "body_sha256": hashlib.sha256(body or b"").hexdigest(), "at": datetime.datetime.now(
               datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if osrc.is_challenge(st, body):
        rec["state"] = "BOT_CHALLENGE"
    elif st == 200:
        rec["state"] = "ANSWERED"
    elif st == "EXCEPTION":
        msg = (body or b"").decode("utf-8", "replace")
        rec["state"] = "TLS_REFUSED" if ("HANDSHAKE" in msg.upper() or "SSL" in msg.upper()) else \
            ("TIMEOUT" if "timed out" in msg else "FETCH_FAILED")
        rec["error"] = msg[:200]
    else:
        rec["state"] = f"HTTP_{st}"
    return rec


def host_attempts():
    """One recorded attempt per host (TGA with bounded backoff); written to registry/route_attempts.json."""
    out = {}
    for route, urls in HOSTS.items():
        tries = []
        for u in urls:
            for w in (BACKOFF if route == "TGA" else (0,)):
                time.sleep(w)
                r = attempt(u)
                tries.append(r)
                if r["state"] in ("ANSWERED", "BOT_CHALLENGE", "TLS_REFUSED"):
                    break
        states = {t["state"] for t in tries}
        out[route] = {"state": "ANSWERED" if "ANSWERED" in states else
                      ("UNREACHABLE" if states <= {"TIMEOUT", "FETCH_FAILED"} else sorted(states)[0]),
                      "tries": tries}
    out["CORE"] = {"state": "NOT_TRIED_ACCOUNT_REQUIRED", "tries": [],
                   "note": "api.core.ac.uk requires a registered API key: listed for Mahmood, never created on his behalf"}
    with open(ATTEMPTS, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    return out


def tracker(slug, ref):
    p = subprocess.run(["git", "show", f"{ref}:outputs/k_gap/g1/{slug}.json"], cwd=ROOT, capture_output=True,
                       stdin=subprocess.DEVNULL)
    return json.loads(p.stdout.decode("utf-8")) if p.returncode == 0 else {}


def unmatched(o):
    return [t for t in o.get("trials") or [] if t.get("route") != "PRIMARY" and not t.get("scope_difference")]


def trial_ids(t):
    fam = str(t.get("family") or "")
    pmid = fam.replace("PMID ", "") if fam.startswith("PMID ") else str((t.get("seeded_funnel") or {}).get("pmid") or "")
    ncts = sorted({c.get("nct") for c in ((t.get("registry_binding") or {}).get("candidates") or []) if c.get("nct")}
                  | ({fam} if fam.startswith("NCT") else set()))
    return pmid or None, ncts


def lane_routes(pmid, ncts):
    """The routes this lane already recorded for the trial (typed records, with digests)."""
    import g1_open_sources as osrc
    import g1_regulatory_source as rs
    out = []
    ids = osrc.registry_ids(ncts) if ncts else {"eudract": [], "ctis": []}
    for u, r in osrc._load().items():
        if (r.get("route") == "OPEN_LOCATION" and pmid and r.get("pmid") == pmid) or \
                (r.get("route") == "EUCTR" and r.get("eudract") in ids["eudract"]) or \
                (r.get("route") == "CTIS" and r.get("ctis") in ids["ctis"]):
            out.append({"route": r["route"], "url": u, "state": r.get("state"), "licence": r.get("licence"),
                        "doc_sha256": r.get("doc_sha256"), "text_sha256": r.get("text_sha256")})
    names = rs.trial_names("", ncts, codes=[c for v in rs.study_codes(ncts).values() for c in v]) if ncts else []
    if names:
        for u, r in rs._load(rs.SOURCES).items():
            if r.get("state") != "TEXT":
                continue
            t = rs.doc_text(u) or ""
            if any(n in t for n in names if len(n) >= 6):
                out.append({"route": r.get("agency"), "url": u, "state": "NAMES_TRIAL", "licence": r.get("licence"),
                            "text_sha256": r.get("text_sha256")})
    return out


def main(argv):
    ref = next((a.split("=", 1)[1] for a in argv if a.startswith("--ref=")), "origin/main")
    slugs = [a for a in argv if not a.startswith("--")]
    hosts = host_attempts()
    summary = {k: v["state"] for k, v in hosts.items()}
    print("hosts:", summary, flush=True)
    extra = json.load(open(os.path.join(ROOT, "registry", "route_extra.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(ROOT, "registry", "route_extra.json")) else {}
    for slug in slugs:
        o = tracker(slug, ref)
        rows = []
        for t in unmatched(o):
            pmid, ncts = trial_ids(t)
            routes = [{"route": k, "state": v["state"], "attempt": f"registry/route_attempts.json#{k}"}
                      for k, v in hosts.items()]
            routes += lane_routes(pmid, ncts)
            routes += extra.get(f"{slug}::{pmid}", [])
            rows.append({"label": t.get("label"), "pmid": pmid, "ncts": ncts, "tracker_route": t.get("route"),
                         "blocker": t.get("blocker"), "routes": routes,
                         "admitted": any(r.get("state") == "ADMITTED" for r in routes)})
        led = {"slug": slug, "tracker_ref": ref, "written": datetime.date.today().isoformat(),
               "writer": "scripts/g1_routes_ledger.py", "hosts": summary, "n_unmatched": len(rows), "rows": rows}
        os.makedirs(os.path.join(ROOT, "cache", slug), exist_ok=True)
        with open(os.path.join(ROOT, "cache", slug, "routes_ledger.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(led, fh, indent=1, ensure_ascii=False)
        print(f"{slug}: {len(rows)} unmatched trials; admitted by these routes: "
              f"{sum(r['admitted'] for r in rows)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
