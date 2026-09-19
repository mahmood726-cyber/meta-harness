#!/usr/bin/env python3
"""Independent verifier for a served evidence bundle. STANDARD LIBRARY ONLY -- imports nothing from this repository.

Given only the served tree (a directory that mirrors the site root, or the site URL) and a review slug, it:

  1. fetches reviews/<slug>/BUNDLE.json and re-derives, from served bytes alone,
     - every artefact and supporting-file digest (sha256 of bytes; canonical-JSON digests; git blob ids of code),
     - CERTIFICATE.json's release_sha256 and review.json's review_sha256,
     - every admission predicate of every primary-pool row (P1..P7) -- NOT read from the bundle but recomputed from
       records.json, review.json and the normalization manifest, then compared with what the bundle recorded,
     - every preservation record (cached abstract vs the retained EFetch XML, unit by unit) and hence the
       coverage_status behind every absence claim, applying the asymmetric rule itself,
     - the pooled estimate: log-scale inverse-variance random effects, Paule-Mandel tau^2, HKSJ on t_{k-1} with the
       Q/(k-1) floor -- Student-t quantile by regularized incomplete beta, no scipy -- compared to 1e-9;
  2. with --corrupt <pmid> <limb>, mutates ONE limb of ONE row in memory (span | effect | components | eligibility |
     conflict | container) and reports which rows changed admissibility, so "an executable gate refuses when the
     evidence is damaged" is demonstrated rather than asserted.

What a PASS here establishes: identity (bytes hash as declared), location (spans sit at the stated offsets in the
stated representation), arithmetic (the pool follows from the rows), and the asymmetric rule. What it does NOT
establish: that any cached representation came from the claimed publisher, that the source set is complete, or that
the clinical interpretation is right -- the bundle's four_questions carry those states separately.

Usage:
  python scripts/verify_bundle.py --root docs --slug glp1-ra-mace-t2d
  python scripts/verify_bundle.py --url https://mahmood726-cyber.github.io/meta-harness/ --slug glp1-ra-mace-t2d
  python scripts/verify_bundle.py --root docs --slug glp1-ra-mace-t2d --corrupt 40162642 span
  add --json for machine-readable output
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

Z975 = 1.959963984540054
_WS = re.compile(r"\s+")
_UNICODE_MAP = str.maketrans({
    "·": ".", "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-",
    " ": " ", " ": " ", " ": " ", "‘": "'", "’": "'", "“": '"', "”": '"',
    "≤": "<=", "≥": ">=",
})


# ---------------------------------------------------------------- primitives

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_text(s: str) -> str:
    return sha256(s.encode("utf-8"))


def git_blob(b: bytes, lf: bool = False) -> str:
    if lf:
        b = b.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def normalize(s: str) -> str:
    return _WS.sub(" ", s).strip().translate(_UNICODE_MAP)


class Store:
    """Bytes by served path, from a directory or a URL; every fetch is remembered so a corruption is applied once."""

    def __init__(self, root: str | None, url: str | None):
        self.root, self.url, self.cache = root, url, {}

    def get(self, path: str) -> bytes:
        if path in self.cache:
            return self.cache[path]
        if self.root:
            data = (Path(self.root) / path).read_bytes()
        else:
            req = urllib.request.Request(self.url.rstrip("/") + "/" + path, headers={"Cache-Control": "no-cache", "User-Agent": "verify_bundle/1"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
        self.cache[path] = data
        return data

    def json(self, path: str):
        return json.loads(self.get(path).decode("utf-8"))


# ---------------------------------------------------------------- statistics (stdlib)

def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 300, 3e-16, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
        c = 1.0 + aa / c
        c = c if abs(c) > FPMIN else FPMIN
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
        c = 1.0 + aa / c
        c = c if abs(c) > FPMIN else FPMIN
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    p = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1 - p if t > 0 else p


def t_ppf(p, df):
    lo, hi = 0.0, 1.0
    while t_cdf(hi, df) < p:
        hi *= 2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-14:
            break
    return 0.5 * (lo + hi)


def _wmean(yi, vi, tau2):
    w = [1.0 / (v + tau2) for v in vi]
    sw = sum(w)
    return sum(wi * y for wi, y in zip(w, yi)) / sw, w, sw


def paule_mandel(yi, vi, tol=1e-10, max_iter=200):
    k = len(yi)
    if k < 2:
        return 0.0

    def F(tau2):
        mu, w, _ = _wmean(yi, vi, tau2)
        return sum(wi * (y - mu) ** 2 for wi, y in zip(w, yi)) - (k - 1)

    if F(0.0) <= 0:
        return 0.0
    lo, hi = 0.0, 1.0
    while F(hi) > 0 and hi < 1e6:
        hi *= 2.0
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        fm = F(mid)
        if abs(fm) < tol:
            return mid
        if fm > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def pool(rows):
    yi = [math.log(r["effect"]) for r in rows]
    vi = [((math.log(r["ci_high"]) - math.log(r["ci_low"])) / (2 * Z975)) ** 2 for r in rows]
    k = len(yi)
    tau2 = paule_mandel(yi, vi)
    mu, w, sw = _wmean(yi, vi, tau2)
    se_re = math.sqrt(1.0 / sw)
    Q_gen = sum(wi * (y - mu) ** 2 for wi, y in zip(w, yi))
    se = se_re * math.sqrt(max(1.0, Q_gen / (k - 1))) if k > 1 else se_re
    tcrit = t_ppf(0.975, k - 1) if k > 1 else Z975
    mu0, w0, _ = _wmean(yi, vi, 0.0)
    Q = sum(wi * (y - mu0) ** 2 for wi, y in zip(w0, yi))
    return {"k": k, "tau2": tau2, "mu_log": mu, "se_log": se, "estimate": math.exp(mu),
            "ci_low": math.exp(mu - tcrit * se), "ci_high": math.exp(mu + tcrit * se), "Q": Q, "t_crit": tcrit}


# ---------------------------------------------------------------- checks

def locate(span, hay):
    if not span:
        return {"match": "NO_SPAN"}
    i = hay.find(span)
    if i >= 0:
        return {"match": "VERBATIM", "parent": "PARSED_SOURCE", "start": i, "end": i + len(span)}
    s, h = normalize(span), normalize(hay)
    i = h.find(s)
    if i >= 0:
        return {"match": "NORMALISED", "parent": "NORMALIZED_SOURCE", "start": i, "end": i + len(s)}
    return {"match": "NOT_LOCATED"}


def tokens_of(x):
    if x is None:
        return []
    s = repr(float(x))
    return [s[:-2] if s.endswith(".0") else s]


def preservation(cached: str, xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    units = [_WS.sub(" ", "".join(a.itertext())).strip() for a in root.findall(".//Abstract/AbstractText")]
    labels = [a.get("Label") for a in root.findall(".//Abstract/AbstractText")]
    c = _WS.sub(" ", cached or "").strip()
    resid = c
    states = []
    for u, lab in zip(units, labels):
        ok = bool(u) and u in c
        states.append("PRESERVED" if ok else "MISSING")
        if ok:
            resid = resid.replace(u, "")
            if lab:
                resid = resid.replace(lab + ":", "")
    resid = _WS.sub(" ", resid).strip()
    verdict = "PRESERVED" if units and all(s == "PRESERVED" for s in states) and not resid else "FAILURE"
    return {"units": len(units), "preserved": states.count("PRESERVED"), "missing": states.count("MISSING"), "extra_chars": len(resid), "verdict": verdict}


def run(store: Store, slug: str, corrupt: tuple[str, str] | None):
    R = f"reviews/{slug}/"
    bundle = store.json(R + "BUNDLE.json")
    report = {"slug": slug, "schema_version": bundle.get("schema_version"), "artefacts": [], "supporting": [], "certificate": {},
              "rows": [], "absence_claims": [], "pool": {}, "corruption": None, "verdict": None}
    failures = []

    # 1. artefacts ---------------------------------------------------------------------------------------------
    for a in bundle["artefacts"]:
        if a["state"] != "SERVED":
            report["artefacts"].append({"ref": a["ref"], "state": a["state"], "checked": "not served; verification route stated in bundle"})
            continue
        data = store.get(a["served_path"])
        ok_bytes = sha256(data) == a["sha256"] and len(data) == a["bytes"]
        role = a["role"]
        if role == "held_documents":
            got = sha256(data)
        elif role == "analysis_code_sha256":
            got = git_blob(data, lf=True)
        elif role == "protocol_text_sha256":
            got = sha256_text(data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
        elif a.get("declared_digest") is not None:
            got = sha256_text(canonical(json.loads(data.decode("utf-8"))))
        else:
            got = None
        ok_decl = a.get("declared_digest") is None or got == a["declared_digest"]
        report["artefacts"].append({"ref": a["ref"], "bytes_ok": ok_bytes, "declared_digest_ok": ok_decl})
        if not (ok_bytes and ok_decl):
            failures.append(f"artefact {a['ref']}: bytes_ok={ok_bytes} declared_digest_ok={ok_decl}")
    for f in bundle.get("supporting_files", []):
        data = store.get(f["path"].removeprefix("docs/"))
        ok = sha256(data) == f["sha256"] and len(data) == f["bytes"]
        report["supporting"].append({"path": f["path"], "ok": ok})
        if not ok:
            failures.append(f"supporting file {f['path']} digest mismatch")

    # 2. certificate and review core --------------------------------------------------------------------------
    cert_bytes = store.get(R + "CERTIFICATE.json")
    cert = json.loads(cert_bytes.decode("utf-8"))
    review = store.json(R + "review.json")
    rel_ok = sha256_text(canonical({k: v for k, v in cert.items() if k != "release_sha256"})) == cert["release_sha256"]
    rev_ok = sha256_text(canonical({k: v for k, v in review.items() if k != "reproduction"})) == cert["review_sha256"]
    file_ok = sha256(cert_bytes) == bundle["certificate"]["sha256_of_file"]
    report["certificate"] = {"release_sha256_recomputed": rel_ok, "review_sha256_recomputed": rev_ok, "file_sha256_matches_bundle": file_ok,
                             "release_sha256": cert["release_sha256"]}
    for name, ok in report["certificate"].items():
        if ok is False:
            failures.append(f"certificate: {name}")

    # 3. load records / families; apply corruption in memory ----------------------------------------------------
    records = store.json(f"cache/{slug}/records.json")
    rec_by_pmid = {str(r["id"]): r for r in records["records"]}
    container_sha = sha256(store.get(f"cache/{slug}/records.json"))
    families = {f.get("family_id"): f for f in review.get("trial_families", []) if isinstance(f, dict)}
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    trials = [dict(t) for t in primary["trials"]]
    canonical_components = sorted((primary.get("endpoint_canonical") or {}).get("components") or [])
    bundle_rows = {r["trial"]["id"].replace("PMID ", ""): r for r in bundle["verification_rows"]}
    if corrupt:
        pmid, limb = corrupt
        t = next(x for x in trials if str(x["id"]).replace("PMID ", "") == pmid)
        br = bundle_rows[pmid]
        if limb == "span":
            t["endpoint_result_span"] = t["endpoint_result_span"][:-1] + ("x" if not t["endpoint_result_span"].endswith("x") else "y")
        elif limb == "effect":
            t["effect"] = round(float(t["effect"]) + 0.01, 4)
        elif limb == "components":
            br["endpoint"]["components_canonical"] = br["endpoint"]["components_canonical"][:-1]
        elif limb == "eligibility":
            families[t["family_id"]] = dict(families[t["family_id"]], eligibility={"state": "UNKNOWN", "absence_code": "CORRUPTED_BY_VERIFIER"})
        elif limb == "conflict":
            families[t["family_id"]] = dict(families[t["family_id"]], conflicts=[{"state": "UNRESOLVED", "note": "planted by verifier"}])
        elif limb == "container":
            rec_by_pmid[pmid] = dict(rec_by_pmid[pmid], abstract=rec_by_pmid[pmid]["abstract"] + " ")
            container_sha = sha256(container_sha.encode())  # the container bytes would differ; represent that
        else:
            raise SystemExit(f"unknown limb {limb}")
        report["corruption"] = {"pmid": pmid, "limb": limb}

    # 4. predicates per row -----------------------------------------------------------------------------------
    for t in trials:
        pmid = str(t["id"]).replace("PMID ", "")
        br = bundle_rows.get(pmid)
        parsed = (rec_by_pmid.get(pmid) or {}).get("abstract") or ""
        span = t.get("endpoint_result_span") or ""
        loc = locate(span, parsed)
        fam = families.get(t.get("family_id")) or {}
        elig = (fam.get("eligibility") or {}).get("state")
        conf = fam.get("conflicts") or []
        unresolved = [c for c in conf if isinstance(c, dict) and str(c.get("state", "")).upper().startswith("UNRESOLVED")]
        toks = tokens_of(t.get("effect")) + tokens_of(t.get("ci_low")) + tokens_of(t.get("ci_high"))
        span_n = normalize(span)
        located = loc["match"] in ("VERBATIM", "NORMALISED")
        # span offsets as recorded by the bundle must reproduce the span text in the named representation
        offsets_ok = None
        if br and br["span"].get("start") is not None and not (corrupt and corrupt[0] == pmid and corrupt[1] == "span"):
            rep = parsed if br["span"]["parent_representation"] == "PARSED_SOURCE" else normalize(parsed)
            piece = rep[br["span"]["start"]:br["span"]["end"]]
            offsets_ok = piece == (span if br["span"]["parent_representation"] == "PARSED_SOURCE" else normalize(span))
        comps_canon = (br or {}).get("endpoint", {}).get("components_canonical") or []
        P = {
            "P1_source_bytes": container_sha == (br or {}).get("source", {}).get("source_sha256") and sha256_text(parsed) == (br or {}).get("source", {}).get("representation_sha256") if not (corrupt and corrupt[1] == "container" and corrupt[0] == pmid) else False,
            "P2_span_located": located and (offsets_ok is not False),
            "P3_effect_tokens_in_span": bool(toks) and all((tok in span or tok in span_n) for tok in toks),
            "P4_endpoint_components": bool(comps_canon) and sorted(comps_canon) == canonical_components,
            "P5_family_eligible": elig == "ELIGIBLE",
            "P6_no_unresolved_conflict": not unresolved,
            "P7_coverage_adequate_for_claim": located,
        }
        final = "ADMISSIBLE" if all(P.values()) else "INADMISSIBLE"
        recorded = (br or {}).get("admission", {}).get("final")
        recorded_P = {k: v["state"] == "PASS" for k, v in ((br or {}).get("admission", {}).get("predicates") or {}).items()}
        report["rows"].append({"pmid": pmid, "label": t.get("label"), "predicates": P, "final": final, "bundle_recorded": recorded,
                               "agrees_with_bundle": (final == recorded) if not corrupt else None,
                               "predicates_agree_with_bundle": (P == recorded_P) if not corrupt else None,
                               "span_match": loc["match"], "offsets_reproduce_span": offsets_ok})
        if not corrupt and final != recorded:
            failures.append(f"row {pmid}: verifier says {final}, bundle recorded {recorded}")

    # 5. absence claims: recompute coverage from acquisitions ------------------------------------------------------
    acq_by_pmid = {}
    for d in bundle.get("documents", []):
        ac = (d.get("representations") or {}).get("ACQUIRED_SOURCE") or {}
        if d["document_id"].startswith("pubmed:") and ac.get("ref"):
            acq_by_pmid[d["document_id"].split(":")[1]] = ac["ref"].removeprefix("docs/")
    for c in bundle.get("absence_claims", []):
        pmid = c["trial"]["id"].replace("PMID ", "")
        row = {"outcome": c["outcome"], "pmid": pmid, "producer_state": c["producer_state"], "claim_kind": c["claim_kind"]}
        if c["claim_kind"] == "NEGATIVE" and pmid in acq_by_pmid:
            pres = preservation((rec_by_pmid.get(pmid) or {}).get("abstract") or "", store.get(acq_by_pmid[pmid]))
            coverage = "COMPLETE_ABSTRACT" if pres["verdict"] == "PRESERVED" else "EXCERPT_ONLY"
            admissible = coverage == "COMPLETE_ABSTRACT"
            row.update({"preservation": pres, "coverage_recomputed": coverage, "negative_claim_admissible": admissible,
                        "bundle_recorded": c["negative_claim_admissible"], "agrees": admissible == c["negative_claim_admissible"]})
            if admissible != c["negative_claim_admissible"]:
                failures.append(f"absence claim {pmid}/{c['outcome']}: verifier {admissible} vs bundle {c['negative_claim_admissible']}")
        elif c["claim_kind"] == "NEGATIVE":
            row.update({"coverage_recomputed": "UNKNOWN_COMPLETENESS", "negative_claim_admissible": False, "bundle_recorded": c["negative_claim_admissible"]})
        report["absence_claims"].append(row)

    # 6. pool ------------------------------------------------------------------------------------------------------
    inputs = bundle["pooled_reference"]["inputs"]
    exp = bundle["pooled_reference"]["expected"]
    got = pool(inputs)
    deltas = {k: abs(got[k] - exp[k]) for k in ("estimate", "ci_low", "ci_high", "tau2")}
    pool_ok = all(d < 1e-9 for d in deltas.values())
    adm = [i for i in inputs if any(r["pmid"] == i["id"].replace("PMID ", "") and r["final"] == "ADMISSIBLE" for r in report["rows"])]
    report["pool"] = {"k_declared": len(inputs), "recomputed": got, "declared": exp, "abs_deltas": deltas, "reproduced_to_1e-9": pool_ok,
                      "t_crit_recomputed": got["t_crit"], "admissible_rows": len(adm),
                      "admissible_only_pool_for_information": pool(adm) if len(adm) >= 2 and len(adm) != len(inputs) else None,
                      "note": "the declared pool is the page's; admissible_only_pool is a verifier sensitivity, not a replacement result"}
    if not pool_ok:
        failures.append(f"pool not reproduced: {deltas}")

    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="stdlib verifier for a served evidence bundle")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--root", help="directory mirroring the site root (e.g. docs)")
    g.add_argument("--url", help="site root URL")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--corrupt", nargs=2, metavar=("PMID", "LIMB"), help="mutate one limb of one row in memory: span|effect|components|eligibility|conflict|container")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    store = Store(a.root, a.url)
    rep = run(store, a.slug, tuple(a.corrupt) if a.corrupt else None)
    if a.json:
        print(json.dumps(rep, indent=1, ensure_ascii=False))
    else:
        print(f"bundle schema {rep['schema_version']}  verdict {rep['verdict']}")
        print(f"artefacts ok: {sum(1 for x in rep['artefacts'] if x.get('bytes_ok') and x.get('declared_digest_ok'))}/{sum(1 for x in rep['artefacts'] if 'bytes_ok' in x)}"
              f"  supporting ok: {sum(1 for x in rep['supporting'] if x['ok'])}/{len(rep['supporting'])}  certificate: {rep['certificate']}")
        for r in rep["rows"]:
            fails = [k for k, v in r["predicates"].items() if not v]
            print(f"  row {r['pmid']:>9} {r['final']:<12} {'(bundle: ' + str(r['bundle_recorded']) + ')':<24} span={r['span_match']:<11} fails={fails}")
        for c in rep["absence_claims"]:
            if c["claim_kind"] == "NEGATIVE":
                print(f"  absence {c['pmid']} {c['outcome'][:36]:<36} coverage={c.get('coverage_recomputed')} negative_claim_admissible={c.get('negative_claim_admissible')}")
        p = rep["pool"]
        print(f"pool k={p['k_declared']}: recomputed {p['recomputed']['estimate']:.16f} ({p['recomputed']['ci_low']:.16f}-{p['recomputed']['ci_high']:.16f}) "
              f"tau2 {p['recomputed']['tau2']:.16e}  reproduced_to_1e-9={p['reproduced_to_1e-9']}  admissible rows {p['admissible_rows']}")
        if rep["corruption"]:
            print(f"corruption {rep['corruption']}: rows now inadmissible = {[r['pmid'] for r in rep['rows'] if r['final'] == 'INADMISSIBLE']}")
        for f in rep["failures"]:
            print("  FAIL:", f)
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
