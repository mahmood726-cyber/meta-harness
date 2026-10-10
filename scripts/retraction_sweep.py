"""RETRACTION SWEEP + GATE (captain dispatch review 27-A, 10 Oct 2026).

Every PMID in all live topics, in EVERY role it plays, is checked for a retraction / expression of concern /
correction notice against two independent sources, and every response is held (sha256 + fetch time + url):

  PubMed efetch XML  PublicationType "Retracted Publication" / "Retraction of Publication" / "Expression of Concern";
                     CommentsCorrections RefType RetractionIn / ExpressionOfConcernIn / ErratumIn (and the
                     retracted-and-republished / partial-retraction variants), recording the referenced notice PMID.
  Crossref by DOI    the work's update-to / updated-by / relation entries of type retraction, withdrawal,
                     expression_of_concern, correction (DOI taken from the PubMed ArticleIdList).

States per PMID: RETRACTED / EXPRESSION_OF_CONCERN / CORRECTED / NONE_FOUND / NOT_CHECKED(reason).
NONE_FOUND only when BOTH legs were actually checked: PubMed returned and parsed the record AND Crossref answered for
its DOI (or the absence of a DOI / a Crossref record was recorded explicitly). A fetch failure is NOT_CHECKED with
reason FETCH_FAILED -- never "not retracted". A positive notice from either leg stands even if the other leg failed.

The roles (kinds of occurrence) are enumerated BEFORE any count, each with its own denominator (see KINDS). The gate:
a RETRACTED or EXPRESSION_OF_CONCERN PMID in a SERVED role (a served pool row, or a countable G1 tracker row's own
report) -> REFUSED, named. A served PMID the sweep never checked -> UNVERIFIED (fail-closed; absence is not clean).
Elsewhere (screened / excluded / family / comparator / held text) a hit is listed, not refused.

    python scripts/retraction_sweep.py --kinds          enumerate kinds + denominators only (offline)
    python scripts/retraction_sweep.py --sweep          fetch both legs, write registry/retraction_sweep.json
    python scripts/retraction_sweep.py --check          offline gate over the committed registry (verify_all limb)
                                                        exit 0 PASS, 1 REFUSED, 2 UNVERIFIED / could not execute
Raw response bytes are written under --raw-dir (never committed); the registry carries their hashes.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import glob
import hashlib
import io
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_REL = "registry/retraction_sweep.json"
SCHEMA = "retraction_sweep_v1"

TOOL, EMAIL = "meta-harness", "meta-harness@example.org"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
CROSSREF = "https://api.crossref.org/works/"
UA = f"meta-harness/1.0 (retraction-sweep; mailto:{EMAIL})"
BATCH = 150
SLEEP = 0.4
TRIES = 4

RETRACTED, EOC, CORRECTED, NONE_FOUND, NOT_CHECKED = (
    "RETRACTED", "EXPRESSION_OF_CONCERN", "CORRECTED", "NONE_FOUND", "NOT_CHECKED")
STATES = (RETRACTED, EOC, CORRECTED, NONE_FOUND, NOT_CHECKED)
_RANK = {RETRACTED: 3, EOC: 2, CORRECTED: 1}
BLOCKING = (RETRACTED, EOC)
NOTICE_WORD = {RETRACTED: "retraction", EOC: "expression-of-concern", CORRECTED: "correction/erratum"}

# leg states
LEG_OK, LEG_FAILED, LEG_NOT_RETURNED, LEG_NO_DOI, LEG_NOT_IN_CROSSREF, LEG_NOT_RUN = (
    "OK", "FETCH_FAILED", "NOT_RETURNED", "NO_DOI", "NOT_IN_CROSSREF", "NOT_RUN")

# ---------------------------------------------------------------------------------------------------------------
# KINDS -- every role a PMID can play, enumerated before anything is counted.
# ---------------------------------------------------------------------------------------------------------------
SERVED_POOL, TRACKER_SERVED = "served_pool", "tracker_served"
SERVED_ROLES = (SERVED_POOL, TRACKER_SERVED)
KINDS = [
    (SERVED_POOL, "a pooled row served on a live page: review.json outcomes[*].trials id / family_report_id, "
                  "strands members, integrity.membership_pooled"),
    (TRACKER_SERVED, "the own report of a COUNTABLE G1 tracker row (g1_countable or in_our_pool): family, "
                     "seeded_funnel / screen_eligibility / identity / confirm_binding pmid, pool_join pool_row"),
    ("screening_record", "review.json screening.records[*] with id_type pmid (included AND excluded)"),
    ("family_report", "review.json trial_families[*].reports[*].report_id"),
    ("comparator_meta", "the topic's comparator meta-analysis: review.json comparator.pmid, comparator_panel id / "
                        "replaces"),
    ("comparator_trial_set", "trials the comparator panel lists: comparator_panel[*].trial_set[*].aliases id"),
    ("comparator_cache", "a held comparator record directory: cache/comparators/<pmid>/ (shared across topics)"),
    ("tracker_row", "any other PMID in a G1 tracker row or topic block (non-countable rows, candidates, named "
                    "differences): outputs/k_gap/g1/<slug>.json, outputs/k_gap/G1_TRACKER.json"),
    ("tracker_meta", "a meta-analysis PMID cited by the tracker (comparator_pmid, meta_pmid, source_meta, ...)"),
    ("held_fulltext", "a held full text: cache/<slug>/ft_<pmid>.txt, fulltext_ledger rows HELD/FETCHED, "
                      "cache/<slug>/comparator_fulltext.txt"),
]
ROLE_ORDER = [k for k, _ in KINDS]
SHARED_TOPIC = "(shared)"

_PMID_STR = re.compile(r"^\s*(?:PMID[\s:]*)?(\d{1,8})\s*$", re.I)
_PMID_STRICT = re.compile(r"^\s*(?:PMID[\s:]*)?(\d{6,8})\s*$", re.I)

TRACKER_META_KEYS = {"meta_pmid", "source_meta", "comparator_pmid", "comparator", "meta",
                     "retired_comparator_pmid", "replaced_by", "comparator_cites", "independent_pairs",
                     "independent_pair_ids", "supports"}
# a countable row's OWN report -- the dotted path inside the row
TRACKER_OWN_PATHS = {"family", "seeded_funnel.pmid", "screen_eligibility.pmid", "identity.pmid",
                     "confirm_binding.pmid", "analysis_set_attribution.report_pmid", "pool_join.pool_row",
                     "sweep.basis.report_pmid", "matched_via_other_report.pool_row"}


def pmid_of(value, strict=False):
    """A PMID string from 'PMID 123', '123', 123; None for anything else (NCT ids, DOIs, labels)."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        value = str(value)
    if not isinstance(value, str):
        return None
    m = (_PMID_STRICT if strict else _PMID_STR).match(value)
    return m.group(1).lstrip("0") or None if m else None


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Collector:
    """Occurrences (pmid, topic, role, where) + per-kind denominators, including the non-PMID ids seen."""

    def __init__(self):
        self.occ = set()
        self.seen = {}  # (role, where) -> {"entries": n, "pmid": n, "non_pmid": n}

    def add(self, role, topic, where, value, strict=False):
        s = self.seen.setdefault((role, where), {"entries": 0, "pmid": 0, "non_pmid": 0})
        s["entries"] += 1
        p = pmid_of(value, strict=strict)
        if p:
            s["pmid"] += 1
            self.occ.add((p, topic, role, where))
        else:
            s["non_pmid"] += 1
        return p

    def occurrences(self):
        return sorted(self.occ, key=lambda o: (o[1], ROLE_ORDER.index(o[2]), o[0], o[3]))

    def kinds_report(self):
        out = []
        for role, desc in KINDS:
            subs = sorted(w for (r, w) in self.seen if r == role)
            pm = {o[0] for o in self.occ if o[2] == role}
            out.append({
                "role": role, "served": role in SERVED_ROLES, "description": desc,
                "sources": [{"where": w, **self.seen[(role, w)]} for w in subs],
                "entries_seen": sum(self.seen[(role, w)]["entries"] for w in subs),
                "non_pmid_ids": sum(self.seen[(role, w)]["non_pmid"] for w in subs),
                "occurrences": sum(1 for o in self.occ if o[2] == role),
                "unique_pmids": len(pm),
                "topics": len({o[1] for o in self.occ if o[2] == role}),
            })
        return out


def _walk_tracker(c, topic, obj, path, row_countable, where):
    """Generic walk of a tracker object; leaf strings that are PMIDs are classed by their key / path."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_tracker(c, topic, v, f"{path}.{k}" if path else k, row_countable, where)
    elif isinstance(obj, list):
        for v in obj:
            _walk_tracker(c, topic, v, path, row_countable, where)
    elif isinstance(obj, (str, int)) and not isinstance(obj, bool):
        if pmid_of(obj, strict=True) is None:
            if row_countable is not None and path in TRACKER_OWN_PATHS and isinstance(obj, str):
                # an own-report field holding a non-PMID id (an NCT family): counted in the denominator, not checked
                c.add(TRACKER_SERVED if row_countable else "tracker_row", topic, f"{where}:{path}", obj, strict=True)
            return
        leaf = path.rsplit(".", 1)[-1]
        if leaf in TRACKER_META_KEYS:
            role = "tracker_meta"
        elif row_countable is not None and path in TRACKER_OWN_PATHS and row_countable:
            role = TRACKER_SERVED
        else:
            role = "tracker_row"
        c.add(role, topic, f"{where}:{path}", obj, strict=True)


def topics(root):
    return sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(root, "docs", "reviews", "*", "review.json")))


def collect_review(c, slug, rev):
    for o in rev.get("outcomes") or []:
        for t in o.get("trials") or []:
            c.add(SERVED_POOL, slug, "review.outcomes.trials.id", t.get("id"))
            if t.get("family_report_id"):
                c.add(SERVED_POOL, slug, "review.outcomes.trials.family_report_id", t.get("family_report_id"))
    strands = rev.get("strands") or {}
    for s in (strands.get("strands") or []) if isinstance(strands, dict) else []:
        for m in s.get("members") or []:
            c.add(SERVED_POOL, slug, "review.strands.members.pmid", m.get("pmid") or m.get("id"))
    for m in (rev.get("integrity") or {}).get("membership_pooled") or []:
        c.add(SERVED_POOL, slug, "review.integrity.membership_pooled", m)
    for r in (rev.get("screening") or {}).get("records") or []:
        c.add("screening_record", slug, "review.screening.records.id", r.get("id") if r.get("id_type") in (None, "pmid") else f"{r.get('id_type')}:{r.get('id')}")
    for fam in rev.get("trial_families") or []:
        for rep in fam.get("reports") or []:
            c.add("family_report", slug, "review.trial_families.reports.report_id", rep.get("report_id"))
    comp = rev.get("comparator") or {}
    if comp.get("pmid") is not None:
        c.add("comparator_meta", slug, "review.comparator.pmid", comp.get("pmid"))
    for p in rev.get("comparator_panel") or []:
        c.add("comparator_meta", slug, "review.comparator_panel.id", p.get("id"))
        for rp in p.get("replaces") or []:
            c.add("comparator_meta", slug, "review.comparator_panel.replaces.id", rp.get("id") if isinstance(rp, dict) else rp)
        for ts in p.get("trial_set") or []:
            for a in (ts.get("aliases") or []) if isinstance(ts, dict) else []:
                c.add("comparator_trial_set", slug, "review.comparator_panel.trial_set.aliases.id", a.get("id") if isinstance(a, dict) else a)


def collect_tracker(c, slug, trk, where):
    for t in trk.get("trials") or []:
        countable = bool(t.get("g1_countable") or t.get("in_our_pool"))
        _walk_tracker(c, slug, t, "", countable, where + ":trials[]")
    for k, v in trk.items():
        if k != "trials":
            _walk_tracker(c, slug, v, k, None, where)


def collect(root=ROOT):
    """Enumerate every (pmid, topic, role, where) occurrence across all live topics. Pure over the tree."""
    c = Collector()
    slugs = topics(root)
    for slug in slugs:
        rev = _load(os.path.join(root, "docs", "reviews", slug, "review.json"))
        collect_review(c, slug, rev)
        tp = os.path.join(root, "outputs", "k_gap", "g1", f"{slug}.json")
        if os.path.exists(tp):
            collect_tracker(c, slug, _load(tp), "outputs/k_gap/g1/<slug>.json")
        cdir = os.path.join(root, "cache", slug)
        for ft in sorted(glob.glob(os.path.join(cdir, "ft_*.txt"))):
            c.add("held_fulltext", slug, "cache/<slug>/ft_<pmid>.txt", os.path.basename(ft)[3:-4])
        led = os.path.join(cdir, "fulltext_ledger.json")
        if os.path.exists(led):
            for row in _load(led).get("rows") or []:
                if row.get("state") in ("HELD", "FETCHED"):
                    c.add("held_fulltext", slug, "cache/<slug>/fulltext_ledger.json rows HELD/FETCHED", row.get("pmid"))
        if os.path.exists(os.path.join(cdir, "comparator_fulltext.txt")):
            c.add("held_fulltext", slug, "cache/<slug>/comparator_fulltext.txt (comparator pmid)", (rev.get("comparator") or {}).get("pmid"))
    g1 = os.path.join(root, "outputs", "k_gap", "G1_TRACKER.json")
    if os.path.exists(g1):
        for slug, block in (_load(g1).get("topics") or {}).items():
            collect_tracker(c, slug, block, "outputs/k_gap/G1_TRACKER.json")
    cc = os.path.join(root, "cache", "comparators")
    if os.path.isdir(cc):
        for name in sorted(os.listdir(cc)):
            c.add("comparator_cache", SHARED_TOPIC, "cache/comparators/<pmid>/", name)
    return c, slugs


def served_occurrences(occurrences):
    return [o for o in occurrences if o[2] in SERVED_ROLES]


# ---------------------------------------------------------------------------------------------------------------
# PARSERS (pure)
# ---------------------------------------------------------------------------------------------------------------
PUBTYPE_SIGNAL = {"Retracted Publication": RETRACTED, "Retraction of Publication": RETRACTED,
                  "Expression of Concern": EOC, "Published Erratum": CORRECTED}
REFTYPE_SIGNAL = {"RetractionIn": RETRACTED, "RetractedandRepublishedIn": RETRACTED, "PartialRetractionIn": RETRACTED,
                  "ExpressionOfConcernIn": EOC, "ErratumIn": CORRECTED, "CorrectedandRepublishedIn": CORRECTED}


def parse_pubmed(xml_bytes):
    """{pmid: {"doi", "signals": [{"source","type","state","notice_pmid"}], "pubtypes": [...]}} for each
    PubmedArticle in an efetch response. Raises on unparseable XML (caller types it as FETCH_FAILED)."""
    root = ET.fromstring(xml_bytes)
    out = {}
    for art in root.iter("PubmedArticle"):
        mc = art.find("MedlineCitation")
        pm = mc.find("PMID") if mc is not None else None
        if pm is None or not (pm.text or "").strip():
            continue
        pmid = pm.text.strip()
        pubtypes = [(pt.text or "").strip() for pt in mc.iter("PublicationType")]
        signals = []
        for pt in pubtypes:
            if pt in PUBTYPE_SIGNAL:
                signals.append({"source": "pubmed", "type": f"PublicationType:{pt}", "state": PUBTYPE_SIGNAL[pt],
                                "notice_pmid": pmid if pt in ("Retraction of Publication", "Expression of Concern",
                                                              "Published Erratum") else None,
                                "self_is_notice": pt in ("Retraction of Publication", "Expression of Concern",
                                                         "Published Erratum")})
        ccl = mc.find("CommentsCorrectionsList")
        for cc in (ccl.findall("CommentsCorrections") if ccl is not None else []):
            rt = cc.get("RefType") or ""
            if rt in REFTYPE_SIGNAL:
                npm = cc.find("PMID")
                signals.append({"source": "pubmed", "type": f"CommentsCorrections:{rt}", "state": REFTYPE_SIGNAL[rt],
                                "notice_pmid": (npm.text or "").strip() if npm is not None else None,
                                "ref_source": (cc.findtext("RefSource") or "").strip()[:200]})
        doi = None
        pd = art.find("PubmedData")
        ail = pd.find("ArticleIdList") if pd is not None else None
        for aid in (ail.findall("ArticleId") if ail is not None else []):
            if aid.get("IdType") == "doi" and (aid.text or "").strip():
                doi = aid.text.strip()
                break
        if doi is None:
            for el in mc.iter("ELocationID"):
                if el.get("EIdType") == "doi" and (el.text or "").strip():
                    doi = el.text.strip()
                    break
        out[pmid] = {"doi": doi, "signals": signals}
    return out


CROSSREF_SIGNAL = {"retraction": RETRACTED, "withdrawal": RETRACTED, "removal": RETRACTED, "partial_retraction": RETRACTED,
                   "expression_of_concern": EOC, "correction": CORRECTED, "erratum": CORRECTED,
                   "corrigendum": CORRECTED, "addendum": CORRECTED, "clarification": CORRECTED}


def _crossref_type(t):
    t = (t or "").strip().lower().replace("-", "_").replace(" ", "_")
    if t in CROSSREF_SIGNAL:
        return CROSSREF_SIGNAL[t]
    if "retract" in t or "withdraw" in t:
        return RETRACTED
    if "concern" in t:
        return EOC
    if "correct" in t or "errat" in t or "corrigend" in t:
        return CORRECTED
    return None


def parse_crossref(json_bytes):
    """Signals from a Crossref /works/<doi> message: update-to, updated-by, relation. Raises on bad JSON."""
    msg = json.loads(json_bytes.decode("utf-8")).get("message") or {}
    signals = []
    for field in ("updated-by", "update-to"):
        for u in msg.get(field) or []:
            st = _crossref_type(u.get("type"))
            if st:
                signals.append({"source": "crossref", "type": f"{field}:{u.get('type')}", "state": st,
                                "notice_doi": u.get("DOI"), "via": u.get("source"),
                                "self_is_notice": field == "update-to"})
    for rel, items in (msg.get("relation") or {}).items():
        st = _crossref_type(rel)
        if st:
            for it in items if isinstance(items, list) else [items]:
                signals.append({"source": "crossref", "type": f"relation:{rel}", "state": st,
                                "notice_doi": (it or {}).get("id") if isinstance(it, dict) else None})
    return signals


def classify(pubmed_leg, crossref_leg, signals):
    """(state, reason). A positive notice from any leg decides; NONE_FOUND needs both legs actually checked."""
    best = None
    for s in signals:
        if s.get("self_is_notice"):
            continue  # the record IS a notice (about another article); that is not a notice ABOUT it -> is_notice
        if best is None or _RANK[s["state"]] > _RANK[best]:
            best = s["state"]
    if best:
        return best, None
    if pubmed_leg != LEG_OK:
        return NOT_CHECKED, f"PUBMED_{pubmed_leg}"
    if crossref_leg not in (LEG_OK, LEG_NO_DOI, LEG_NOT_IN_CROSSREF):
        return NOT_CHECKED, f"CROSSREF_{crossref_leg}"
    return NONE_FOUND, None


# ---------------------------------------------------------------------------------------------------------------
# GATE (pure)
# ---------------------------------------------------------------------------------------------------------------
def retraction_gate(sweep, served):
    """sweep: {pmid: {"state", "notice_pmids", "notice_dois"}}; served: iterable of (pmid, topic, role, where).
    REFUSED when any served PMID is RETRACTED / EXPRESSION_OF_CONCERN; else UNVERIFIED when any served PMID is
    missing from the sweep or NOT_CHECKED (absence is not clean); else PASS."""
    refused, unverified = [], []
    for pmid, topic, role, where in served:
        rec = sweep.get(pmid)
        if rec is None:
            unverified.append({"pmid": pmid, "topic": topic, "role": role, "where": where, "reason": "NOT_IN_SWEEP"})
            continue
        st = rec.get("state")
        own = [n for n in rec.get("is_notice") or [] if n in BLOCKING]
        if own and st not in BLOCKING:
            refused.append({"pmid": pmid, "topic": topic, "role": role, "where": where, "state": f"IS_NOTICE:{own[0]}",
                            "notice_pmids": [], "notice_dois": rec.get("notice_for_dois") or []})
        elif st in BLOCKING:
            refused.append({"pmid": pmid, "topic": topic, "role": role, "where": where, "state": st,
                            "notice_pmids": rec.get("notice_pmids") or [], "notice_dois": rec.get("notice_dois") or []})
        elif st not in (NONE_FOUND, CORRECTED):
            unverified.append({"pmid": pmid, "topic": topic, "role": role, "where": where,
                               "reason": f"{st}:{rec.get('reason')}"})
    verdict = "REFUSED" if refused else ("UNVERIFIED" if unverified else "PASS")
    return {"verdict": verdict, "refused": refused, "unverified": unverified}


def notice_line(rec):
    bits = []
    if rec.get("notice_pmids"):
        bits.append("notice PMID " + ", ".join(rec["notice_pmids"]))
    if rec.get("notice_dois"):
        bits.append("notice DOI " + ", ".join(rec["notice_dois"]))
    if not bits and rec.get("notice_refs"):
        bits.append("notice (no PMID) " + " | ".join(rec["notice_refs"]))
    return "; ".join(bits) or "notice not linked"


# ---------------------------------------------------------------------------------------------------------------
# NETWORK (held responses)
# ---------------------------------------------------------------------------------------------------------------
def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Fetcher:
    """GET with bounded retry/backoff; every final response (or failure) is held: raw bytes under raw_dir, and a
    fetch record {leg, url, status, sha256, bytes, fetched_utc, raw_name, error}. Resumable via raw_dir/index.json."""

    def __init__(self, raw_dir, sleep=SLEEP, tries=TRIES):
        self.raw_dir, self.sleep, self.tries = raw_dir, sleep, tries
        os.makedirs(raw_dir, exist_ok=True)
        self.index_path = os.path.join(raw_dir, "index.json")
        self.index = _load(self.index_path) if os.path.exists(self.index_path) else {}
        self.lock = threading.Lock()
        self.n_new = 0

    def save_index(self):
        with self.lock:
            tmp = self.index_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.index, f)
            os.replace(tmp, self.index_path)

    def get(self, leg, url, ext, headers=None):
        with self.lock:
            prev = self.index.get(url)
        if prev and prev.get("status") in (200, 404) and prev.get("raw_name"):
            p = os.path.join(self.raw_dir, prev["raw_name"])
            if os.path.exists(p):
                body = open(p, "rb").read()
                if hashlib.sha256(body).hexdigest() == prev["sha256"]:
                    return prev, body
        rec, body = self._fetch(leg, url, ext, headers or {})
        with self.lock:
            self.index[url] = rec
            self.n_new += 1
            if self.n_new % 200 == 0:
                pass
        if self.n_new % 200 == 0:
            self.save_index()
        return rec, body

    def _fetch(self, leg, url, ext, headers):
        err, status, body = None, None, b""
        for i in range(self.tries):
            time.sleep(self.sleep)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA, **headers})
                with urllib.request.urlopen(req, timeout=60) as r:
                    status, body, err = int(r.getcode() or 0), r.read(), None
                    break
            except urllib.error.HTTPError as exc:
                status, body, err = int(exc.code), (exc.read() or b""), f"HTTP {exc.code}"
                if exc.code == 404:
                    break
            except Exception as exc:  # noqa: BLE001 -- typed below, never read as clean
                status, body, err = None, b"", f"{type(exc).__name__}: {exc}"[:300]
            if i + 1 < self.tries:
                time.sleep(2 * (2 ** i))
        sha = hashlib.sha256(body).hexdigest()
        raw_name = f"{leg}_{hashlib.sha256(url.encode()).hexdigest()[:20]}.{ext}"
        with open(os.path.join(self.raw_dir, raw_name), "wb") as f:
            f.write(body)
        rec = {"leg": leg, "url": url, "status": status, "sha256": sha, "bytes": len(body),
               "fetched_utc": _utc(), "raw_name": raw_name, "error": err if status not in (200,) else None}
        return rec, body


def efetch_url(pmids):
    return EFETCH + "?" + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml",
                                                  "tool": TOOL, "email": EMAIL})


def crossref_url(doi):
    return CROSSREF + urllib.parse.quote(doi, safe="/:;()[]") + "?mailto=" + urllib.parse.quote(EMAIL)


def run_sweep(pmids, fetcher, workers=3, log=print):
    """Both legs over the unique PMIDs. Returns ({pmid: record}, [fetch records])."""
    pmids = sorted(set(pmids), key=int)
    res = {p: {"pubmed_leg": LEG_NOT_RUN, "crossref_leg": LEG_NOT_RUN, "doi": None, "signals": [],
               "pubmed_fetch": None, "crossref_fetch": None, "errors": []} for p in pmids}
    fetches = []
    for i in range(0, len(pmids), BATCH):
        chunk = pmids[i:i + BATCH]
        rec, body = fetcher.get("pubmed", efetch_url(chunk), "xml")
        fetches.append(rec)
        fid = len(fetches) - 1
        parsed, perr = None, None
        if rec["status"] == 200:
            try:
                parsed = parse_pubmed(body)
            except ET.ParseError as exc:
                perr = f"XML parse error: {exc}"
        else:
            perr = rec.get("error") or f"HTTP {rec['status']}"
        for p in chunk:
            r = res[p]
            r["pubmed_fetch"] = fid
            if parsed is None:
                r["pubmed_leg"] = LEG_FAILED
                r["errors"].append(f"pubmed: {perr}")
            elif p in parsed:
                r["pubmed_leg"] = LEG_OK
                r["doi"] = parsed[p]["doi"]
                r["signals"].extend(parsed[p]["signals"])
            else:
                r["pubmed_leg"] = LEG_NOT_RETURNED
                r["errors"].append("pubmed: PMID not returned by efetch")
        log(f"  pubmed batch {i // BATCH + 1}/{(len(pmids) + BATCH - 1) // BATCH}: status {rec['status']}"
            f" parsed {0 if parsed is None else len(parsed)}/{len(chunk)}")
    fetcher.save_index()

    todo = []
    for p in pmids:
        r = res[p]
        if r["pubmed_leg"] != LEG_OK:
            continue  # no DOI source -> Crossref leg NOT_RUN (the PMID is NOT_CHECKED unless PubMed flagged it)
        if not r["doi"]:
            r["crossref_leg"] = LEG_NO_DOI
            continue
        todo.append(p)
    flock = threading.Lock()
    done = [0]

    def one(p):
        r = res[p]
        rec, body = fetcher.get("crossref", crossref_url(r["doi"]), "json")
        with flock:
            fetches.append(rec)
            r["crossref_fetch"] = len(fetches) - 1
            done[0] += 1
            if done[0] % 500 == 0:
                log(f"  crossref {done[0]}/{len(todo)}")
        if rec["status"] == 200:
            try:
                r["signals"].extend(parse_crossref(body))
                r["crossref_leg"] = LEG_OK
            except (ValueError, AttributeError) as exc:
                r["crossref_leg"] = LEG_FAILED
                r["errors"].append(f"crossref: JSON parse error: {exc}")
        elif rec["status"] == 404:
            r["crossref_leg"] = LEG_NOT_IN_CROSSREF
        else:
            r["crossref_leg"] = LEG_FAILED
            r["errors"].append(f"crossref: {rec.get('error')}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, todo))
    fetcher.save_index()
    for p, r in res.items():
        r["state"], r["reason"] = classify(r["pubmed_leg"], r["crossref_leg"], r["signals"])
        about = [s for s in r["signals"] if not s.get("self_is_notice")]
        r["notice_pmids"] = sorted({s["notice_pmid"] for s in about if s.get("notice_pmid") and s["notice_pmid"] != p})
        r["notice_dois"] = sorted({s["notice_doi"] for s in about if s.get("notice_doi")})
        r["notice_refs"] = sorted({s["ref_source"] for s in about if s.get("ref_source") and not s.get("notice_pmid")})
        own = [s for s in r["signals"] if s.get("self_is_notice")]
        r["is_notice"] = sorted({s["state"] for s in own})
        r["notice_for_dois"] = sorted({s["notice_doi"] for s in own if s.get("notice_doi")})
    return res, fetches


# ---------------------------------------------------------------------------------------------------------------
# REPORT / REGISTRY
# ---------------------------------------------------------------------------------------------------------------
def summarise(occurrences, sweep):
    by_role_state = {r: {s: 0 for s in STATES} for r in ROLE_ORDER}
    uniq_role_state = {r: {s: set() for s in STATES} for r in ROLE_ORDER}
    for p, t, role, w in occurrences:
        st = sweep.get(p, {}).get("state", NOT_CHECKED)
        uniq_role_state[role][st].add((p, t))
    for r in ROLE_ORDER:
        for s in STATES:
            by_role_state[r][s] = len(uniq_role_state[r][s])
    unique = {s: 0 for s in STATES}
    for p in {o[0] for o in occurrences}:
        unique[sweep.get(p, {}).get("state", NOT_CHECKED)] += 1
    reasons = {}
    for p in {o[0] for o in occurrences}:
        rec = sweep.get(p, {})
        if rec.get("state", NOT_CHECKED) == NOT_CHECKED:
            k = rec.get("reason") or "NOT_IN_SWEEP"
            reasons[k] = reasons.get(k, 0) + 1
    hits, notices = [], []
    seen = set()
    for p, t, role, w in occurrences:
        rec = sweep.get(p, {})
        if rec.get("is_notice") and (p, t, role, "notice") not in seen:
            seen.add((p, t, role, "notice"))
            notices.append({"pmid": p, "topic": t, "role": role, "served": role in SERVED_ROLES,
                            "is_notice": rec["is_notice"], "notice_for_dois": rec.get("notice_for_dois") or [],
                            "listing": f"this record IS a {'/'.join(NOTICE_WORD[x] for x in rec['is_notice'])} notice"
                                       f" for {', '.join(rec.get('notice_for_dois') or ['(unlinked)'])}"})
        if rec.get("state") in (RETRACTED, EOC, CORRECTED) and (p, t, role) not in seen:
            seen.add((p, t, role))
            hits.append({"pmid": p, "topic": t, "role": role, "served": role in SERVED_ROLES, "state": rec["state"],
                         "notice_pmids": rec.get("notice_pmids") or [], "notice_dois": rec.get("notice_dois") or [],
                         "listing": f"{'retracted' if rec['state'] == RETRACTED else rec['state'].lower().replace('_', ' ')}, {notice_line(rec)}"})
    hits.sort(key=lambda h: (-_RANK[h["state"]], h["pmid"], h["topic"], ROLE_ORDER.index(h["role"])))
    return {"by_role_state_pmid_topic_pairs": by_role_state, "by_state_unique_pmids": unique,
            "not_checked_reasons_unique_pmids": reasons, "hits": hits, "records_that_are_notices": notices}


def _dump_registry(path, reg):
    """Stable, diff-friendly JSON: one line per PMID / fetch / occurrence."""
    lines = ["{"]
    keys = list(reg)
    for ki, k in enumerate(keys):
        v = reg[k]
        comma = "," if ki < len(keys) - 1 else ""
        if k in ("pmids",):
            lines.append(f'  "{k}": {{')
            items = list(v.items())
            for i, (pk, pv) in enumerate(items):
                lines.append(f"    {json.dumps(pk)}: {json.dumps(pv, ensure_ascii=False, sort_keys=True)}" + ("," if i < len(items) - 1 else ""))
            lines.append("  }" + comma)
        elif k in ("fetches", "occurrences"):
            lines.append(f'  "{k}": [')
            for i, item in enumerate(v):
                lines.append("    " + json.dumps(item, ensure_ascii=False, sort_keys=isinstance(item, dict)) + ("," if i < len(v) - 1 else ""))
            lines.append("  ]" + comma)
        else:
            body = json.dumps(v, ensure_ascii=False, indent=2, sort_keys=False)
            lines.append(f'  "{k}": ' + body.replace("\n", "\n  ") + comma)
    lines.append("}")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def build_registry(slugs, collector, res, fetches, started):
    occurrences = collector.occurrences()
    pm = {}
    for p in sorted(res, key=int):
        r = res[p]
        e = {"state": r["state"], "pubmed_leg": r["pubmed_leg"], "crossref_leg": r["crossref_leg"], "doi": r["doi"],
             "pubmed_fetch": r["pubmed_fetch"], "crossref_fetch": r["crossref_fetch"]}
        if r["reason"]:
            e["reason"] = r["reason"]
        if r["errors"]:
            e["errors"] = r["errors"]
        if r["signals"]:
            e["signals"] = r["signals"]
            for k in ("notice_pmids", "notice_dois", "notice_refs", "is_notice", "notice_for_dois"):
                if r.get(k):
                    e[k] = r[k]
        pm[p] = e
    summ = summarise(occurrences, pm)
    leg_counts = {"pubmed": {}, "crossref": {}}
    for e in pm.values():
        leg_counts["pubmed"][e["pubmed_leg"]] = leg_counts["pubmed"].get(e["pubmed_leg"], 0) + 1
        leg_counts["crossref"][e["crossref_leg"]] = leg_counts["crossref"].get(e["crossref_leg"], 0) + 1
    return {
        "schema": SCHEMA,
        "_doc": ("Retraction sweep: every PMID in every role across all live topics, checked against PubMed efetch "
                 "and Crossref. Raw responses are held outside the tree; each fetch here carries url, status, sha256, "
                 "fetched_utc. A fetch failure is NOT_CHECKED (never NONE_FOUND). Generated by "
                 "scripts/retraction_sweep.py --sweep; gated by --check (verify_all limb)."),
        "started_utc": started, "finished_utc": _utc(),
        "topics": slugs, "n_topics": len(slugs),
        "states": list(STATES),
        "kinds": collector.kinds_report(),
        "unique_pmids": len(pm),
        "leg_counts_unique_pmids": leg_counts,
        "summary": summ,
        "gate": retraction_gate(pm, served_occurrences(occurrences)),
        "pmids": pm,
        "fetches": fetches,
        "occurrences": [list(o) for o in occurrences],
    }


def print_kinds(kinds, out=print):
    out("KINDS (enumerated before any count; denominator per kind):")
    for k in kinds:
        out(f"  {k['role']:<22} served={str(k['served']):<5} entries_seen={k['entries_seen']:>6} "
            f"non_pmid={k['non_pmid_ids']:>5} occurrences={k['occurrences']:>6} unique_pmids={k['unique_pmids']:>5} "
            f"topics={k['topics']}")
        for s in k["sources"]:
            out(f"      {s['where']}: entries {s['entries']}, pmid {s['pmid']}, non-pmid {s['non_pmid']}")


def check(root=ROOT, registry_path=None, out=print):
    """Offline gate: committed sweep x LIVE served occurrences. Returns exit code 0/1/2."""
    path = registry_path or os.path.join(root, *REGISTRY_REL.split("/"))
    if not os.path.exists(path):
        out(f"RETRACTION-GATE: COULD-NOT-EXECUTE -- {REGISTRY_REL} missing; run --sweep")
        return 2
    try:
        reg = _load(path)
        sweep = reg["pmids"]
    except (OSError, ValueError, KeyError) as exc:
        out(f"RETRACTION-GATE: COULD-NOT-EXECUTE -- cannot read {REGISTRY_REL} ({exc})")
        return 2
    c, slugs = collect(root)
    served = served_occurrences(c.occurrences())
    g = retraction_gate(sweep, served)
    out(f"RETRACTION-GATE: {len(served)} served occurrences ({len({o[0] for o in served})} unique PMIDs) across "
        f"{len(slugs)} topics vs sweep of {len(sweep)} PMIDs ({reg.get('finished_utc')})")
    for r in g["refused"]:
        out(f"REFUSED {r['state']} PMID {r['pmid']} served in {r['topic']} as {r['role']} ({r['where']}); "
            f"{notice_line(r)}")
    for u in g["unverified"][:40]:
        out(f"UNVERIFIED PMID {u['pmid']} served in {u['topic']} as {u['role']} ({u['where']}): {u['reason']}")
    if len(g["unverified"]) > 40:
        out(f"... +{len(g['unverified']) - 40} more UNVERIFIED")
    listed = [h for h in (reg.get("summary") or {}).get("hits", []) if not h.get("served")]
    out(f"listed (not served, not refused): {len(listed)} occurrence(s) of a flagged PMID")
    if g["verdict"] == "REFUSED":
        out(f"RETRACTION-GATE: REFUSED -- {len(g['refused'])} served occurrence(s) RETRACTED / EXPRESSION_OF_CONCERN")
        return 1
    if g["verdict"] == "UNVERIFIED":
        out(f"RETRACTION-GATE: COULD-NOT-EXECUTE -- {len(g['unverified'])} served occurrence(s) not checked by the sweep")
        return 2
    out("RETRACTION-GATE: PASS -- no served PMID is retracted or under an expression of concern")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--kinds", action="store_true")
    g.add_argument("--sweep", action="store_true")
    g.add_argument("--check", action="store_true")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--raw-dir", default=os.environ.get("RETRACTION_RAW_DIR"))
    ap.add_argument("--registry", default=None)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(argv)
    if a.check:
        return check(a.root, a.registry)
    started = _utc()
    c, slugs = collect(a.root)
    print(f"{len(slugs)} topics")
    print_kinds(c.kinds_report())
    occ = c.occurrences()
    print(f"occurrences {len(occ)}; unique PMIDs {len({o[0] for o in occ})}")
    if a.kinds:
        return 0
    if not a.raw_dir:
        print("--sweep needs --raw-dir (or RETRACTION_RAW_DIR): raw responses are held OUTSIDE the tree")
        return 2
    fetcher = Fetcher(a.raw_dir)
    res, fetches = run_sweep([o[0] for o in occ], fetcher, workers=a.workers)
    reg = build_registry(slugs, c, res, fetches, started)
    _dump_registry(a.registry or os.path.join(a.root, *REGISTRY_REL.split("/")), reg)
    s = reg["summary"]
    print("unique PMIDs by state:", s["by_state_unique_pmids"])
    print("NOT_CHECKED reasons:", s["not_checked_reasons_unique_pmids"])
    print("legs:", reg["leg_counts_unique_pmids"])
    for h in s["records_that_are_notices"]:
        print(f"  NOTICE-RECORD PMID {h['pmid']:<9} {h['topic']:<45} {h['role']:<20} {h['listing']}")
    for h in s["hits"]:
        print(f"  HIT {h['state']:<22} PMID {h['pmid']:<9} {h['topic']:<45} {h['role']:<20} {h['listing']}")
    print("gate:", reg["gate"]["verdict"], len(reg["gate"]["refused"]), "refused,", len(reg["gate"]["unverified"]), "unverified")
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.exit(main())
