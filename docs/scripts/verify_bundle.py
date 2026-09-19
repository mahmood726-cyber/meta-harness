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
     conflict | binding | container) and reports which rows changed admissibility, so "an executable gate refuses when the
     evidence is damaged" is demonstrated rather than asserted;
  3. for EVERY document with a retained acquisition, recomputes the preservation record (cached abstract vs the
     retained EFetch XML, unit by unit) and FAILS if the bundle's coverage_status disagrees -- a self-consistent
     package that deleted a sentence and recomputed every digest is caught here, provided the XML was not altered too;
  4. with --anchor live, re-fetches EFetch XML from PubMed NOW for every pooled record and compares its abstract units
     to BOTH the retained XML and the cached abstract. That is the external observation nothing inside the package can
     substitute for; a difference is reported as a discrepancy (with DateRevised), not attributed.

What a PASS here establishes: identity (bytes hash as declared, under the canonicalisation the bundle publishes:
Python json.dumps sort_keys / compact separators / ensure_ascii=False, NOT RFC 8785), selection (every #PMID selector
resolves to exactly one record -- zero or two matches refuse), location (spans sit at the stated code-point offsets in
the stated representation of THAT record), arithmetic (the pool follows from the rows), and the asymmetric rule.

What it does NOT check, stated in the same breath:
  * that any acquired or cached representation faithfully preserves the upstream publication. SOUL's cache is known to
    omit the HbA1c entry range, the follow-up figures and the safety sentence; the preservation record detects that
    against a POST-HOC acquisition, and a saved response plus its hash establish what was saved, not that it came from
    the claimed publisher;
  * that the source set is complete, or that the clinical interpretation is right (four_questions carry those states);
  * whether a CI-to-SE conversion was appropriate for a source whose interval was not a Wald interval (statistical_input
    records the construction; SOUL's is group-sequential-adjusted; the pool is reproduced, its appropriateness is not);
  * the PRODUCTION admission path. No production falsification test has been executed by anyone. This verifier checks
    the bundle, not the producer's gate. A green run here is not evidence that the producer refuses damaged evidence.

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
            try:
                data = (Path(self.root) / path).read_bytes()
            except FileNotFoundError:
                raise Refusal("ARTEFACT_UNREACHABLE", f"{path} is not present in the served tree")
        else:
            req = urllib.request.Request(self.url.rstrip("/") + "/" + path, headers={"Cache-Control": "no-cache", "User-Agent": "verify_bundle/1"})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    data = r.read()
            except urllib.error.HTTPError as e:
                raise Refusal("ARTEFACT_UNREACHABLE", f"{path}: HTTP {e.code}")
            except Exception as e:  # noqa: BLE001
                raise Refusal("ARTEFACT_UNREACHABLE", f"{path}: {str(e)[:120]}")
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

TARGET_PHRASES = ("major adverse cardiovascular", "mace")
PRIMARY_NAMES = ("primary outcome", "primary composite outcome", "primary-outcome", "primary end point", "primary endpoint", "primary composite end point")
COMPONENT_WORDS = {"CARDIOVASCULAR_DEATH": ("cardiovascular death", "death from cardiovascular", "cardiovascular causes", "cardiovascular mortality"),
                   "MYOCARDIAL_INFARCTION": ("myocardial infarction",), "STROKE": ("stroke",)}
NON_TARGET_MENTIONS = ("death from any cause", "all-cause mortality", "all-cause death", "any-cause death", "hospitalization for heart failure",
                       "hospitalisation for heart failure", "heart failure", "kidney", "renal", "retinopathy", "amputation", "pancreatitis",
                       "adverse event", "serious adverse", "gastrointestinal", "hypoglyc")


def clause_with_effect(span, tokens):
    parts = [x for x in re.split(r"(?<=\.)\s+(?=[A-Z])", span or "") if x.strip()]
    for part in parts:
        if all(tok in part or tok in normalize(part) for tok in tokens):
            return part
    return span or ""


def span_target_mention(span, tokens, definition_span, canonical_components):
    """POSITIVE binding: the tuple's own clause must carry a target mention; a recognised non-target mention refuses
    ENDPOINT_INCOMPATIBLE; no recognised mention refuses AMBIGUOUS_ENDPOINT_BINDING (never a fallback to the definition)."""
    clause = clause_with_effect(span, tokens)
    c, d = normalize(clause).lower(), normalize(definition_span or "").lower()
    named = lambda text: sorted(k for k, ws in COMPONENT_WORDS.items() if any(w in text for w in ws))
    comps_c, comps_d = named(c), named(d)
    primary_named = any(n in c for n in PRIMARY_NAMES)
    non_target = [m for m in NON_TARGET_MENTIONS if m in c]
    if any(ph in c for ph in TARGET_PHRASES):
        return {"state": "PASS", "mention": "target phrase", "clause": clause}
    if len(set(comps_c) & set(canonical_components or [])) >= 2:
        return {"state": "PASS", "mention": "target definition in clause", "witness": comps_c, "clause": clause}
    if primary_named and "primary" in d and len(set(comps_d) & set(canonical_components or [])) >= 2:
        return {"state": "PASS", "mention": "primary-outcome name bound by definition span", "witness": comps_d, "clause": clause}
    if non_target or (len(comps_c) == 1 and not primary_named):
        return {"state": "ENDPOINT_INCOMPATIBLE", "witness": non_target or comps_c, "clause": clause}
    return {"state": "AMBIGUOUS_ENDPOINT_BINDING", "witness": clause, "clause": clause}


class Refusal(Exception):
    """A named refusal that must become a JSON verdict, never a crash."""

    def __init__(self, code, detail):
        super().__init__(f"{code} {detail}")
        self.code, self.detail = code, detail


def resolve_selector(records, pmid):
    """The bundle's selector rule: the UNIQUE record with id_type pmid and id == pmid; 0 or >=2 matches refuse."""
    m = [r for r in records["records"] if str(r.get("id_type", "pmid")).lower() == "pmid" and str(r.get("id")) == str(pmid)]
    if len(m) != 1:
        raise Refusal("SELECTOR_REFUSED", f"#PMID-{pmid}: resolves to {len(m)} records (rule requires exactly one)")
    return m[0]


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


def live_anchor(pmid: str, retained_xml: bytes, cached_abstract: str) -> dict:
    """External observation: EFetch NOW, compare abstract units with the retained XML and with the cached abstract."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml&tool=verify_bundle&email=meta-harness@example.org"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "verify_bundle/1"})
        with urllib.request.urlopen(req, timeout=120) as r:
            live = r.read()
    except Exception as exc:  # network is an external dependency; report, do not pretend
        return {"fetched": False, "error": str(exc)[:200]}

    def units(b):
        root = ET.fromstring(b)
        return [_WS.sub(" ", "".join(a.itertext())).strip() for a in root.findall(".//Abstract/AbstractText")]

    def revised(b):
        d = ET.fromstring(b).find(".//MedlineCitation/DateRevised")
        return f"{d.findtext('Year')}-{d.findtext('Month')}-{d.findtext('Day')}" if d is not None else None

    lu, ru = units(live), units(retained_xml)
    c = _WS.sub(" ", cached_abstract or "").strip()
    return {"fetched": True, "live_sha256": sha256(live), "live_bytes": len(live), "live_date_revised": revised(live), "retained_date_revised": revised(retained_xml),
            "live_units": len(lu), "retained_units": len(ru),
            "units_in_live_not_in_retained": [u[:120] for u in lu if u not in ru],
            "units_in_retained_not_in_live": [u[:120] for u in ru if u not in lu],
            "live_units_missing_from_cached_abstract": sum(1 for u in lu if u and u not in c),
            "live_equals_retained_bytes": sha256(live) == sha256(retained_xml)}


def run(store: Store, slug: str, corrupt: tuple[str, str] | None, anchor_live: bool = False):
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
        try:
            data = store.get(a["served_path"])
        except Refusal as r:
            report["artefacts"].append({"ref": a["ref"], "bytes_ok": False, "declared_digest_ok": False, "refusal": r.code})
            failures.append(f"{r.code} {r.detail}")
            continue
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
            failures.append(f"ARTEFACT_DIGEST_MISMATCH {a['ref']}: bytes_ok={ok_bytes} declared_digest_ok={ok_decl}")
    for f in bundle.get("supporting_files", []):
        try:
            data = store.get(f["path"].removeprefix("docs/"))
        except Refusal as r:
            report["supporting"].append({"path": f["path"], "ok": False, "refusal": r.code})
            failures.append(f"{r.code} {r.detail}")
            continue
        ok = sha256(data) == f["sha256"] and len(data) == f["bytes"]
        report["supporting"].append({"path": f["path"], "ok": ok})
        if not ok:
            failures.append(f"SUPPORTING_FILE_DIGEST_MISMATCH {f['path']}")

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
            failures.append(f"CERTIFICATE_MISMATCH {name}")

    # 3. load records / families; apply corruption in memory ----------------------------------------------------
    records = store.json(f"cache/{slug}/records.json")
    rec_by_pmid, selector_refusals = {}, {}
    for br in bundle["verification_rows"]:
        pmid = br["trial"]["id"].replace("PMID ", "")
        frag = (br["source"].get("document_ref") or "").split("#PMID-")[-1] if "#PMID-" in (br["source"].get("document_ref") or "") else None
        try:
            if frag is None:
                raise Refusal("SELECTOR_REFUSED", f"{pmid}: document_ref carries no #PMID fragment")
            if frag != pmid:
                raise Refusal("SELECTOR_MISMATCH", f"{pmid}: document_ref fragment #PMID-{frag} does not name the row's trial")
            rec_by_pmid[pmid] = resolve_selector(records, frag)       # refuses on 0 or >=2, by the FRAGMENT the rule names
        except Refusal as r:
            selector_refusals[pmid] = r
            failures.append(f"{r.code} {r.detail}")
    for r in records["records"]:
        rec_by_pmid.setdefault(str(r["id"]), r)
    try:
        certified = store.json(f"cache/{slug}/families.json")
        fam_certified = {f.get("family_id"): f for f in certified.get("families", []) if isinstance(f, dict)}
    except Refusal as r:
        fam_certified, certified = {}, None
        failures.append(f"{r.code} {r.detail} (certified eligibility copy)")
    # digest scopes the bundle publishes for the container: all three must reproduce
    raw = store.get(f"cache/{slug}/records.json")
    scopes = {sc["subject"]: sc["value"] for d in bundle.get("digest_scopes", []) for sc in d["scopes"]}
    if scopes:
        got = {"raw served bytes": sha256(raw), "whole file as JSON object": sha256_text(canonical(json.loads(raw.decode("utf-8")))),
               "obj['records'] only": sha256_text(canonical(json.loads(raw.decode("utf-8"))["records"]))}
        for k, v in scopes.items():
            if got.get(k) != v:
                failures.append(f"DIGEST_SCOPE_MISMATCH '{k}' does not reproduce under the published canonicalisation")
        report["digest_scopes_reproduced"] = all(got.get(k) == v for k, v in scopes.items())
    container_sha = sha256(store.get(f"cache/{slug}/records.json"))
    families = {f.get("family_id"): f for f in review.get("trial_families", []) if isinstance(f, dict)}   # rendered copy (cross-check only)
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
            fam_certified[t["family_id"]] = dict(fam_certified.get(t["family_id"], {}), eligibility={"state": "UNKNOWN", "absence_code": "CORRUPTED_BY_VERIFIER"})
        elif limb == "conflict":
            families[t["family_id"]] = dict(families[t["family_id"]], conflicts=[{"state": "UNRESOLVED", "note": "planted by verifier"}])
        elif limb == "binding":
            t["endpoint_binding"] = "unbound_legacy"
        elif limb == "nontarget_span":     # M7a shape: a genuine non-target sentence from the same record, numbers intact
            t["endpoint_result_span"] = f"Death from cardiovascular causes occurred in fewer patients (hazard ratio, {t['effect']}; 95% CI, {t['ci_low']} to {t['ci_high']})."
        elif limb == "unlisted_span":      # M8 shape: an unlisted outcome with genuine numbers
            t["endpoint_result_span"] = f"Retinopathy complications occurred in more patients (hazard ratio, {t['effect']}; 95% CI, {t['ci_low']} to {t['ci_high']})."
        elif limb == "fragment":           # M11 shape: document_ref fragment rewritten
            br["source"]["document_ref"] = br["source"]["document_ref"].split("#")[0] + "#PMID-99999999"
        elif limb == "container":
            rec_by_pmid[pmid] = dict(rec_by_pmid[pmid], abstract=rec_by_pmid[pmid]["abstract"] + " ")
            container_sha = sha256(container_sha.encode())  # the container bytes would differ; represent that
        else:
            raise SystemExit(f"unknown limb {limb}")
        report["corruption"] = {"pmid": pmid, "limb": limb}
        if limb == "fragment":
            frag = br["source"]["document_ref"].split("#PMID-")[-1]
            try:
                if frag != pmid:
                    raise Refusal("SELECTOR_MISMATCH", f"{pmid}: document_ref fragment #PMID-{frag} does not name the row's trial")
            except Refusal as r:
                selector_refusals[pmid] = r

    # 4. predicates per row -----------------------------------------------------------------------------------
    for t in trials:
        pmid = str(t["id"]).replace("PMID ", "")
        br = bundle_rows.get(pmid)
        parsed = (rec_by_pmid.get(pmid) or {}).get("abstract") or ""
        span = t.get("endpoint_result_span") or ""
        loc = locate(span, parsed)
        fam_c = fam_certified.get(t.get("family_id")) or {}
        fam = families.get(t.get("family_id")) or {}
        elig = (fam_c.get("eligibility") or {}).get("state") if fam_c else None          # CERTIFIED copy is authoritative
        elig_rendered = (fam.get("eligibility") or {}).get("state")
        if fam_c and elig != elig_rendered and not corrupt:
            failures.append(f"ELIGIBILITY_COPIES_DISAGREE {t.get('family_id')}: certified {elig} vs rendered {elig_rendered}")
        conf = (fam_c.get("conflicts") if fam_c.get("conflicts") is not None else fam.get("conflicts")) or []
        unresolved = [c for c in conf if isinstance(c, dict) and str(c.get("state", "")).upper().startswith("UNRESOLVED")]
        toks = tokens_of(t.get("effect")) + tokens_of(t.get("ci_low")) + tokens_of(t.get("ci_high"))
        span_n = normalize(span)
        located = loc["match"] in ("VERBATIM", "NORMALISED")
        # span offsets as recorded by the bundle must reproduce the span text in the named representation
        offsets_ok = None
        if br and br["span"].get("start") is not None and not (corrupt and corrupt[0] == pmid and corrupt[1] == "span"):
            rep = parsed if br["span"]["parent_representation"] == "PARSED_SOURCE" else normalize(parsed)
            piece = rep[br["span"]["start"]:br["span"]["end"]]     # code-point slice, half-open, per bundle.coordinates
            offsets_ok = piece == (span if br["span"]["parent_representation"] == "PARSED_SOURCE" else normalize(span))
            rep_sha_ok = sha256_text(rep) == br["span"]["representation_sha256"]
            offsets_ok = offsets_ok and rep_sha_ok
        comps_canon = (br or {}).get("endpoint", {}).get("components_canonical") or []
        P = {
            "P1_source_bytes": container_sha == (br or {}).get("source", {}).get("source_sha256") and sha256_text(parsed) == (br or {}).get("source", {}).get("representation_sha256") if not (corrupt and corrupt[1] == "container" and corrupt[0] == pmid) else False,
            "P2_span_located": located and (offsets_ok is not False),
            "P3_effect_tokens_in_span": bool(toks) and all((tok in span or tok in span_n) for tok in toks),
            "P4_endpoint_components": bool(comps_canon) and sorted(comps_canon) == canonical_components,
            "P5_family_eligible": elig == "ELIGIBLE",
            "P6_no_unresolved_conflict": not unresolved,
            "P7_coverage_adequate_for_claim": located,
            "P8_endpoint_bound": t.get("endpoint_binding") == "named_endpoint_resolved_to_definition_span",
        }
        p9 = span_target_mention(span, toks, t.get("endpoint_definition_span"), canonical_components)
        P["P9_span_target_mention"] = p9["state"] == "PASS"
        if pmid in selector_refusals:
            P["P1_source_bytes"] = False
        failing = [k for k, ok in P.items() if not ok]
        final = ("ADMISSIBLE" if not failing else
                 "MIGRATION_STATE_UNBOUND_LEGACY" if failing == ["P8_endpoint_bound"] and t.get("endpoint_binding") == "unbound_legacy" else
                 "INADMISSIBLE")
        recorded = (br or {}).get("admission", {}).get("final")
        recorded_P = {k: v["state"] == "PASS" for k, v in ((br or {}).get("admission", {}).get("predicates") or {}).items()}
        span_code = None
        if not located and span:
            container_text = json.dumps(records, ensure_ascii=False)
            span_code = "SPAN_NOT_IN_RECORD" if (span in container_text or normalize(span) in normalize(container_text)) else "SPAN_NOT_LOCATED"
            if not corrupt:
                failures.append(f"{span_code} {pmid}: the quotation is {'elsewhere in the container but' if span_code == 'SPAN_NOT_IN_RECORD' else 'not'} in the selected record's representation")
        report["rows"].append({"pmid": pmid, "label": t.get("label"), "predicates": P, "final": final, "bundle_recorded": recorded,
                               "p9": p9, "refusal": (selector_refusals[pmid].code if pmid in selector_refusals else
                                                     span_code if span_code else
                                                     p9["state"] if p9["state"] != "PASS" else None),
                               "agrees_with_bundle": (final == recorded) if not corrupt else None,
                               "predicates_agree_with_bundle": (P == recorded_P) if not corrupt else None,
                               "span_match": loc["match"], "offsets_reproduce_span": offsets_ok})
        if p9["state"] != "PASS" and not corrupt:
            failures.append(f"{p9['state']} {pmid}: {json.dumps(p9.get('witness'), ensure_ascii=False)[:160]}")
        if not corrupt and final != recorded:
            failures.append(f"ROW_VERDICT_DISAGREES {pmid}: verifier says {final}, bundle recorded {recorded}")

    # 5. anchors: every document with a retained acquisition -- recompute preservation, compare to recorded coverage ----
    acq_by_pmid = {}
    report["anchors"] = []
    for d in bundle.get("documents", []):
        ac = (d.get("representations") or {}).get("ACQUIRED_SOURCE") or {}
        if d["document_id"].startswith("pubmed:") and ac.get("ref"):
            pmid = d["document_id"].split(":")[1]
            acq_by_pmid[pmid] = ac["ref"].removeprefix("docs/")
            xml_bytes = store.get(acq_by_pmid[pmid])
            xml_ok = sha256(xml_bytes) == ac.get("sha256_original")
            pres = preservation((rec_by_pmid.get(pmid) or {}).get("abstract") or "", xml_bytes)
            recorded = (d.get("coverage_status") or {}).get("value")
            recomputed = "COMPLETE_ABSTRACT" if pres["verdict"] == "PRESERVED" else "EXCERPT_ONLY"
            row = {"pmid": pmid, "acquired_xml_sha256_ok": xml_ok, "preservation": pres, "coverage_recomputed": recomputed,
                   "coverage_recorded": recorded, "agrees": recomputed == recorded}
            if anchor_live:
                row["live"] = live_anchor(pmid, xml_bytes, (rec_by_pmid.get(pmid) or {}).get("abstract") or "")
                if row["live"].get("units_in_live_not_in_retained") or row["live"].get("units_in_retained_not_in_live"):
                    row["live"]["discrepancy"] = "RECORDED (not attributed): live PubMed and the retained acquisition differ; see DateRevised"
            report["anchors"].append(row)
            if not xml_ok:
                failures.append(f"ANCHOR_XML_DIGEST_MISMATCH {pmid}: retained XML does not hash to ACQUIRED_SOURCE.sha256_original")
            if recomputed != recorded:
                failures.append(f"ANCHOR_PRESERVATION_FAILURE {pmid}: {pres['missing']} of {pres['units']} retained-XML abstract units MISSING from the cached "
                                f"abstract (extra chars {pres['extra_chars']}); coverage recomputed {recomputed} vs recorded {recorded} -- the cached "
                                f"abstract does not preserve the retained XML as the bundle claims")
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
                failures.append(f"ABSENCE_CLAIM_DISAGREES {pmid}/{c['outcome']}: verifier {admissible} vs bundle {c['negative_claim_admissible']}")
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
    report["binding_states"] = {"rendered_rows": [], "migration_state_unbound_legacy": 0}
    for o in review.get("outcomes", []):
        for t in o.get("trials", []):
            b = t.get("endpoint_binding")
            cls = "BOUND" if b == "named_endpoint_resolved_to_definition_span" else "MIGRATION_STATE_UNBOUND_LEGACY" if b == "unbound_legacy" else "OTHER"
            report["binding_states"]["rendered_rows"].append({"outcome": o["name"], "id": t.get("id"), "binding_class": cls})
            report["binding_states"]["migration_state_unbound_legacy"] += (cls == "MIGRATION_STATE_UNBOUND_LEGACY")
    report["binding_states"]["migration_rows_counted_admissible"] = sum(
        1 for r in report["rows"] if r["final"] == "MIGRATION_STATE_UNBOUND_LEGACY")  # by construction never in admissible set
    report["pool"] = {"k_declared": len(inputs), "recomputed": got, "declared": exp, "abs_deltas": deltas, "reproduced_to_1e-9": pool_ok,
                      "t_crit_recomputed": got["t_crit"], "admissible_rows": len(adm),
                      "admissible_only_pool_for_information": pool(adm) if len(adm) >= 2 and len(adm) != len(inputs) else None,
                      "note": "the declared pool is the page's; admissible_only_pool is a verifier sensitivity, not a replacement result"}
    if not pool_ok:
        failures.append(f"POOL_NOT_REPRODUCED {deltas}")

    report["endpoint_compatibility"] = {"state": (bundle.get("endpoint_compatibility") or {}).get("state"),
                                        "per_trial": {k: v["value"] for k, v in ((bundle.get("endpoint_compatibility") or {}).get("per_trial") or {}).items()}}
    report["statistical_input"] = {r["trial"]["id"]: {"interval_construction": r["statistical_input"]["interval_construction"],
                                                      "se_source": r["statistical_input"]["se_source"],
                                                      "approximation_appropriate": r["statistical_input"]["approximation_appropriate"]}
                                   for r in bundle["verification_rows"] if "statistical_input" in r}
    report["not_checked"] = ["upstream fidelity of any representation", "completeness of the source set", "clinical interpretation",
                             "appropriateness of CI-to-SE conversions for non-Wald intervals", "the production admission path"]
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="stdlib verifier for a served evidence bundle")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--root", help="directory mirroring the site root (e.g. docs)")
    g.add_argument("--url", help="site root URL")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--corrupt", nargs=2, metavar=("PMID", "LIMB"), help="mutate one limb of one row in memory: span|effect|components|eligibility|conflict|binding|nontarget_span|unlisted_span|fragment|container")
    ap.add_argument("--anchor", choices=["live"], help="live: re-fetch EFetch XML from PubMed now and compare to the retained acquisition and the cached abstract")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:  # the report carries source text (thin spaces, middle dots); a cp1252 console must not turn a verdict into a crash
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    store = Store(a.root, a.url)
    try:
        rep = run(store, a.slug, tuple(a.corrupt) if a.corrupt else None, anchor_live=(a.anchor == "live"))
    except Refusal as r:
        rep = {"slug": a.slug, "verdict": "REFUSED", "refusal_code": r.code, "detail": r.detail, "failures": [f"{r.code} {r.detail}"],
               "note": "the verifier could not complete; this is a verdict, not a crash"}
        print(json.dumps(rep, indent=1, ensure_ascii=False) if a.json else f"verdict REFUSED  {r.code}: {r.detail}")
        return 1
    except Exception as e:  # noqa: BLE001 -- a validator that crashes only when it has something to say looks like a clean corpus
        rep = {"slug": a.slug, "verdict": "REFUSED", "refusal_code": "VERIFIER_INTERNAL_ERROR", "detail": f"{type(e).__name__}: {str(e)[:300]}",
               "failures": [f"VERIFIER_INTERNAL_ERROR {type(e).__name__}: {str(e)[:300]}"]}
        print(json.dumps(rep, indent=1, ensure_ascii=False) if a.json else f"verdict REFUSED  VERIFIER_INTERNAL_ERROR: {type(e).__name__}: {e}")
        return 1
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
        print(f"endpoint_compatibility {rep['endpoint_compatibility']['state']} {rep['endpoint_compatibility']['per_trial']}")
        print("statistical_input: " + "; ".join(f"{k}={v['interval_construction']}" for k, v in rep["statistical_input"].items() if v["interval_construction"] != "UNSTATED_IN_HELD_REPRESENTATION") + " (others UNSTATED_IN_HELD_REPRESENTATION; all SE DERIVED_FROM_CI)")
        for an in rep.get("anchors", []):
            live = an.get("live")
            extra = (f" live: fetched={live.get('fetched')} equal_bytes={live.get('live_equals_retained_bytes')} "
                     f"revised live={live.get('live_date_revised')} retained={live.get('retained_date_revised')} "
                     f"units +{len(live.get('units_in_live_not_in_retained', []))}/-{len(live.get('units_in_retained_not_in_live', []))} "
                     f"live_units_missing_from_cache={live.get('live_units_missing_from_cached_abstract')}") if live else ""
            print(f"  anchor {an['pmid']} xml_ok={an['acquired_xml_sha256_ok']} preservation={an['preservation']['verdict']} "
                  f"({an['preservation']['preserved']}/{an['preservation']['units']}) coverage {an['coverage_recomputed']} recorded {an['coverage_recorded']}{extra}")
        bs = rep["binding_states"]
        print(f"binding: {bs['migration_state_unbound_legacy']} rendered row(s) UNBOUND_LEGACY = migration state, not admissible, not refused: "
              + ", ".join(f"{r['id']} ({r['outcome'][:28]})" for r in bs["rendered_rows"] if r["binding_class"] != "BOUND"))
        print("NOT checked: " + "; ".join(rep["not_checked"]))
        if rep["corruption"]:
            print(f"corruption {rep['corruption']}: rows no longer ADMISSIBLE = {[(r['pmid'], r['final']) for r in rep['rows'] if r['final'] != 'ADMISSIBLE']}")
        for f in rep["failures"]:
            print("  FAIL:", f)
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
