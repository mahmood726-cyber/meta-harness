"""Blinded model reviews of the served review pages (Mahmood, 9 Oct: "use codex, Gemini and Claude for blinded reviews on
the URLs"). One independent call per topic per model; no model sees another model's output or any prior finding.

What each model is shown (and nothing else), all pinned to ONE commit whose served bytes were checked against the live
site first (scripts/check_live_deploy.py):
  * the review page's rendered text at that commit (byte-identical to the live URL), with its tab boundaries;
  * that topic's section of the external audit pack (lane_status/AUDITOR_PACK.md; its Findings rows are empty);
  * the served tuples of every outcome (review.json at the commit: per-trial effect/CI/scale and the served pool);
  * OPEN primary sources only (D8): PubMed abstracts and ClinicalTrials.gov / AACT records always; a held full text or
    the comparator's text only when its licence is CC BY / CC0 (scripts/g1_licence.py, the stricter lane rule) -- and
    the call-time guard in reproducible_ai.model_call_live refuses any prompt the record guard would refuse.
Every call is a RECORDED call (reproducible_ai.model_call_live: prompt / input / output sha256, model id as reported).

    python scripts/blinded_review.py prepare --commit <sha> --pack <AUDITOR_PACK.md> --first 11 --last 32
    python scripts/blinded_review.py run --model codex --workers 8
    python scripts/blinded_review.py unavailable --model gemini --reason "<probe command and its output>"
    python scripts/blinded_review.py adjudicate
    python scripts/blinded_review.py summary --out <lane_status/blinded_review.md>

Adjudication (outputs/blinded/<slug>/adjudicated.json): a finding is CONFIRMED when >=2 models raise it (same tab,
overlapping page quote), or when one model raises it AND a typed check against the held source passes:
  * every finding: its page quote is in the page text shown and its source quote is in a held source shown (the same
    bytes the model was given -- never a re-read, never a window);
  * changes_number additionally: the served value is a number in the page quote, the source value a number in the
    source quote, and the two differ.
For changes_wording / record a typed check can only establish that both quotes are real ("typed_check": "spans"); the
reasoning connecting them is the model's and is labelled so. Pools are also recomputed deterministically from the
served tuples (Paule-Mandel tau^2, HKSJ on t_{k-1} with floor max(1, Q/(k-1))), independently of the harness code.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import html
import json
import math
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "outputs", "blinded")
SITE = "https://mahmood726-cyber.github.io/meta-harness"
MODEL, EFFORT = "gpt-6-astra", "high"
SEVERITIES = ("changes_number", "changes_wording", "record")
RATIO = {"HR", "RR", "OR", "IRR", "RATE RATIO", "RATIO"}

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["findings", "numeric_checks", "screening_sample"],
    "properties": {
        "findings": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["tab", "page_quote", "source_evidence", "severity", "claim", "served_value", "source_value"],
            "properties": {
                "tab": {"type": "string"},
                "page_quote": {"type": "string"},
                "source_evidence": {"type": "object", "additionalProperties": False, "required": ["url", "quote"],
                                    "properties": {"url": {"type": "string"}, "quote": {"type": "string"}}},
                "severity": {"type": "string", "enum": list(SEVERITIES)},
                "claim": {"type": "string"},
                "served_value": {"type": "string"},
                "source_value": {"type": "string"}}}},
        "numeric_checks": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["outcome", "k", "recomputed_estimate", "recomputed_ci_low", "recomputed_ci_high",
                         "served_estimate", "served_ci_low", "served_ci_high", "agrees", "note"],
            "properties": {"outcome": {"type": "string"}, "k": {"type": "integer"},
                           "recomputed_estimate": {"type": "number"}, "recomputed_ci_low": {"type": "number"},
                           "recomputed_ci_high": {"type": "number"}, "served_estimate": {"type": "number"},
                           "served_ci_low": {"type": "number"}, "served_ci_high": {"type": "number"},
                           "agrees": {"type": "boolean"}, "note": {"type": "string"}}}},
        "screening_sample": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["record", "served_decision", "verdict", "reason", "quote"],
            "properties": {"record": {"type": "string"}, "served_decision": {"type": "string"},
                           "verdict": {"type": "string", "enum": ["AGREE", "DISAGREE", "CANNOT_TELL"]},
                           "reason": {"type": "string"}, "quote": {"type": "string"}}}}}}

INSTR = """You are an independent reviewer of ONE published meta-analysis page. You work alone: you are not shown any
other reviewer's opinion and there are no prior findings. Use ONLY the material below (no browsing, no memory of the
papers): the page text exactly as served at the pinned commit, the audit-pack section for this review, the served
tuples, and the open primary sources. Do not run commands.

Report three things, as JSON matching the schema:
1. findings -- each a concrete defect on the page. For each: the tab it is on; page_quote = a VERBATIM span copied from
   the page text (short, unique); source_evidence = the URL of the source block you rely on (copy the URL shown in its
   header) and a VERBATIM quote from that block; severity:
     changes_number  = a served number (effect, CI, count, k, pooled result) differs from what the source supports;
     changes_wording = wording on the page misstates the source or the analysis (a number is not affected);
     record          = provenance / labelling / identifier / bookkeeping defect that changes neither.
   claim = one or two sentences on what is wrong. served_value / source_value = the two numbers for changes_number
   (copied as written), otherwise "". A finding you cannot support with a verbatim source quote is not a finding: leave
   it out. No findings is a valid answer.
2. numeric_checks -- for EVERY outcome in the served tuples that has a served pool with k >= 2: recompute the pool from
   the per-trial effect and 95% CI (log scale for ratio measures; SE = (ln hi - ln lo) / (2 * 1.959964); Paule-Mandel
   tau^2; HKSJ CI on t with k-1 df, variance factor floored at max(1, Q/(k-1))) and compare with the served pool.
   agrees = estimate and both CI limits agree to the served rounding (allow 0.002 on the ratio scale).
3. screening_sample -- for each record of the audit pack's screening sample: does the served decision follow from the
   record's title/abstract shown below? AGREE / DISAGREE / CANNOT_TELL (CANNOT_TELL when the record is not shown), with
   a short reason and a verbatim quote from the record ("" if none).
"""


# ------------------------------------------------------------------------------------------------ text + gates
_DASH = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")
_QUOTE = {ord("‘"): "'", ord("’"): "'", ord("“"): '"', ord("”"): '"', ord(" "): " ",
          ord(" "): " ", ord(" "): " "}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", html.unescape(s or "")).translate(_DASH).translate(_QUOTE)
    return re.sub(r"\s+", " ", s).strip().lower()


def page_text(page_html: str) -> str:
    """The rendered text a reader sees, with each tab's boundary marked. Scripts and styles are not text."""
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", page_html)
    s = re.sub(r'(?is)<section class="tab" id="tab-([a-z]+)"><h3 class="tabname">([^<]*)</h3>',
               lambda m: f"\n\n=== TAB: {m.group(2)} ===\n", s)
    s = re.sub(r"(?i)<(br|/p|/li|/tr|/h[1-6]|/div|/table)\b[^>]*>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def contains(hay_norm: str, quote: str) -> bool:
    q = norm(quote).strip(" .\"'")
    return len(q) >= 8 and q in hay_norm


_NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?")


def numbers(s: str) -> list[float]:
    # a middle dot between digits is a decimal point (Lancet style "0·045"); a thousands comma is not a separator
    s = re.sub(r"(?<=\d)[·∙](?=\d)", ".", s or "")
    return [float(x) for x in _NUM.findall(s.replace(",", ""))]


def model_numeric_state(c: dict, ratio_tol: float = 0.002) -> str:
    """Compare the model's recomputed pool with the served pool OURSELVES (never trust its boolean). A served CI of
    0/0 is the schema's placeholder for a withheld (null) CI: nothing to compare, so NOT_ASSESSABLE."""
    sv = (c.get("served_estimate"), c.get("served_ci_low"), c.get("served_ci_high"))
    rc = (c.get("recomputed_estimate"), c.get("recomputed_ci_low"), c.get("recomputed_ci_high"))
    if any(not isinstance(x, (int, float)) for x in sv + rc) or (sv[1] == 0 and sv[2] == 0) or rc == (0, 0, 0):
        return "NOT_ASSESSABLE"
    def tol(v):     # the served value's own printed precision: 0.61 agrees with anything in [0.605, 0.615]
        txt = repr(float(v))
        dp = len(txt.split(".")[1].rstrip("0")) if "." in txt and "e" not in txt else 4
        return max(ratio_tol, 0.5 * 10 ** -dp + 1e-12, 0.002 * abs(v))
    return "AGREES" if all(abs(a - b) <= tol(b) for a, b in zip(rc, sv)) else "DIFFERS"


# ------------------------------------------------------------------------------------------------ deterministic pool
def pm_hksj(effects: list[tuple[float, float, float]], ratio: bool) -> dict:
    from scipy import stats
    z = 1.959963984540054
    ys, vs = [], []
    for e, lo, hi in effects:
        if ratio:
            ys.append(math.log(e))
            vs.append(((math.log(hi) - math.log(lo)) / (2 * z)) ** 2)
        else:
            ys.append(e)
            vs.append(((hi - lo) / (2 * z)) ** 2)
    k = len(ys)

    def q_at(t2):
        w = [1 / (v + t2) for v in vs]
        mu = sum(wi * y for wi, y in zip(w, ys)) / sum(w)
        return sum(wi * (y - mu) ** 2 for wi, y in zip(w, ys)), w, mu
    q0, _, _ = q_at(0.0)
    tau2 = 0.0
    if q0 > k - 1:
        lo_t, hi_t = 0.0, 1.0
        while q_at(hi_t)[0] > k - 1:
            hi_t *= 2
        for _ in range(200):
            mid = (lo_t + hi_t) / 2
            (lo_t, hi_t) = (mid, hi_t) if q_at(mid)[0] > k - 1 else (lo_t, mid)
        tau2 = (lo_t + hi_t) / 2
    _, w, mu = q_at(tau2)
    qh = sum(wi * (y - mu) ** 2 for wi, y in zip(w, ys)) / (k - 1)
    se = math.sqrt(max(1.0, qh) / sum(w))
    t = stats.t.ppf(0.975, k - 1)
    f = math.exp if ratio else (lambda x: x)
    return {"k": k, "estimate": f(mu), "ci_low": f(mu - t * se), "ci_high": f(mu + t * se), "tau2": tau2}


def recompute(outcome: dict) -> dict:
    res = outcome.get("result") or {}
    k = res.get("k")
    if not isinstance(k, int) or k < 2 or res.get("estimate") is None:
        return {"outcome": outcome.get("name"), "status": "NO_POOL_SERVED"}
    scale = str(res.get("scale") or outcome.get("served_estimand") or "").upper()
    ratio = scale in RATIO
    tr = [(t.get("effect"), t.get("ci_low"), t.get("ci_high")) for t in outcome.get("trials") or []]
    tr = [x for x in tr if all(isinstance(v, (int, float)) for v in x) and (not ratio or min(x) > 0)]
    if len(tr) != k:
        return {"outcome": outcome.get("name"), "status": "CANNOT_RECOMPUTE",
                "why": f"served k={k} but {len(tr)} trial rows carry a numeric effect and CI"}
    if any(res.get(a) is None for a in ("estimate", "ci_low", "ci_high")):
        return {"outcome": outcome.get("name"), "status": "CANNOT_RECOMPUTE", "why": "served pool has no CI"}
    r = pm_hksj(tr, ratio)
    tol = 0.002 if ratio else 0.02 * max(1.0, abs(res["estimate"]))
    agree = all(abs(r[a] - res[b]) <= tol for a, b in (("estimate", "estimate"), ("ci_low", "ci_low"), ("ci_high", "ci_high")))
    return {"outcome": outcome.get("name"), "status": "AGREES" if agree else "DIFFERS", "scale": scale, "k": k,
            "recomputed": {a: round(r[a], 4) for a in ("estimate", "ci_low", "ci_high", "tau2")},
            "served": {a: res.get(a) for a in ("estimate", "ci_low", "ci_high", "tau2")}, "tolerance": tol}


# ------------------------------------------------------------------------------------------------ prepare
def git_show(commit: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, check=True).stdout


def pack_sections(pack_md: str) -> list[tuple[int, str, str]]:
    """[(n, slug, section text)] in the pack's order (### 2.n)."""
    parts = re.split(r"(?m)^### 2\.(\d+) ", pack_md)
    out = []
    for i in range(1, len(parts) - 1, 2):
        body = "### 2." + parts[i] + " " + parts[i + 1].split("\n## ", 1)[0]
        m = re.search(r"/reviews/([a-z0-9-]+)/index\.html", body)
        out.append((int(parts[i]), m.group(1) if m else "", body.strip()))
    return out


def served_tuples(review: dict) -> list[dict]:
    out = []
    for o in review.get("outcomes") or []:
        res = o.get("result") or {}
        out.append({"outcome": o.get("name"), "served_estimand": o.get("served_estimand"), "method": o.get("method"),
                    "pool": ({a: res.get(a) for a in ("k", "estimate", "scale", "ci_low", "ci_high", "tau2", "Q", "i2",
                                                       "pi_low", "pi_high")} if res else "no pooled estimate served"),
                    "trials": [{a: t.get(a) for a in ("label", "id", "effect", "ci_low", "ci_high", "scale", "source")}
                               for t in o.get("trials") or []]})
    return out


def _pmids(review: dict) -> list[str]:
    ids = set()
    for o in review.get("outcomes") or []:
        for t in o.get("trials") or []:
            for f in ("id", "report_id", "trial_id", "label"):
                m = re.search(r"\b(\d{7,8})\b", str(t.get(f) or ""))
                if m:
                    ids.add(m.group(1))
    return sorted(ids)


_OPEN_LIC = re.compile(r"^cc[ -]?(by|0)([ -]?\d(\.\d)?)?$")


def open_sources(commit: str, slug: str, review: dict, sample_ids: list[str]) -> tuple[list[dict], list[dict]]:
    """(shown, dropped). Every block: ref (as the call guard reads it), url, sha256 of the exact text, text."""
    import g1_licence
    from reproducible_ai import record_licence as rl
    shown, dropped = [], []

    def add(ref, url, kind, text):
        b = text.encode("utf-8")
        shown.append({"ref": ref, "url": url, "kind": kind, "sha256": hashlib.sha256(b).hexdigest(), "text": text})

    recs = json.loads(git_show(commit, f"cache/{slug}/records.json"))
    by_id = {str(r.get("id")): r for r in recs.get("records") or []}
    for pid in sorted(set(_pmids(review)) | set(sample_ids)):
        r = by_id.get(pid)
        if not r:
            continue
        url = (f"https://pubmed.ncbi.nlm.nih.gov/{pid}/" if r.get("id_type") == "pmid"
               else f"https://clinicaltrials.gov/study/{pid}")
        add(f"PubMed/CT.gov record {pid} (ABSTRACT)", url, "ABSTRACT",
            f"TITLE: {r.get('title') or ''}\nABSTRACT: {r.get('abstract') or ''}")
    try:
        aact = git_show(commit, f"cache/{slug}/aact_inputs.json").decode("utf-8")
        add(f"cache/{slug}/aact_inputs.json", "https://clinicaltrials.gov/ (AACT posted results; cite the NCT id)",
            "AACT", aact)
    except subprocess.CalledProcessError:
        pass
    ls = subprocess.run(["git", "ls-tree", "--name-only", commit, f"cache/{slug}/"], cwd=ROOT, capture_output=True,
                        text=True).stdout.split()
    for path in ls:
        m = re.search(r"/ft_(\d+)\.txt$", path)
        if not m:
            continue
        pmid, text = m.group(1), git_show(commit, path).decode("utf-8", "replace")
        kept, why = g1_licence.gate(pmid, [("HELD_CACHE_FT", text)])
        if kept:
            add(f"held open text PMID {pmid} (HELD_CACHE_FT)", f"https://europepmc.org/article/MED/{pmid}", "FULLTEXT", text)
        else:
            dropped.append({"ref": path, "why": why})
    comp = f"cache/{slug}/comparator_fulltext.txt"
    if comp in ls:
        lics = rl.ref_licences(comp, rl.licences(), rl.doi_licences())
        ok = bool(lics) and all(_OPEN_LIC.match(str(l or "").strip().lower()) for _, l in lics)
        topic = json.loads(git_show(commit, f"topics/{slug}.json"))
        cp = topic.get("comparator_pmid")
        if ok:
            add(comp, f"https://pubmed.ncbi.nlm.nih.gov/{cp}/", "COMPARATOR_FULLTEXT",
                git_show(commit, comp).decode("utf-8", "replace"))
        else:
            dropped.append({"ref": comp, "why": f"comparator licence {lics!r} is not CC BY / CC0 (D8)"})
    return shown, dropped


def build_prompt(job: dict) -> bytes:
    parts = [INSTR, f"\nREVIEW: {job['slug']}  LIVE URL: {job['url']}  PINNED COMMIT: {job['commit']}\n",
             "\n##### AUDIT-PACK SECTION #####\n", job["pack_section"],
             "\n\n##### SERVED TUPLES (review.json at the pinned commit) #####\n",
             json.dumps(job["tuples"], ensure_ascii=False, indent=1),
             "\n\n##### PAGE TEXT (as served) #####\n", job["page_text"], "\n\n##### OPEN PRIMARY SOURCES #####\n"]
    for s in job["sources"]:
        # <<<TEXT ... TEXT>>> is the block the call-time licence guard (reproducible_ai.record_licence) reads: a source
        # outside it is invisible to the guard (9 Oct: the first codex run's blocks were, and only the pre-filter held)
        # Full text is what the guard licenses; abstracts and AACT/CT.gov are always open under D8 and are not
        # licensable text in the guard's sense (it would refuse a large AACT block as "no declared source").
        body = f"<<<TEXT\n{s['text']}\nTEXT>>>" if s["kind"] in ("FULLTEXT", "COMPARATOR_FULLTEXT") else s["text"]
        parts.append(f"\n=== SOURCE {s['url']}  [{s['kind']}; {s['ref']}] ===\n{body}\n")
    return "".join(parts).encode("utf-8")


def guard_problems(job: dict, prompt: bytes) -> list:
    """What the call-time licence guard would say about this prompt (empty = it would send)."""
    import base64
    from reproducible_ai import record_licence
    return record_licence.record_problems({"record_id": "pre-call", "input_digests": input_digests(job),
                                           "prompt": {"b64": base64.b64encode(prompt).decode("ascii")}})


def input_digests(job: dict) -> list:
    slug = job["slug"]
    d = [{"ref": f"docs/reviews/{slug}/index.html@{job['commit'][:12]} (rendered text)",
          "sha256": job.get("page_sha256", ""), "what": "served page bytes (live, byte-identical)"},
         {"ref": f"AUDITOR_PACK.md section 2.{job.get('n')}",
          "sha256": hashlib.sha256(job["pack_section"].encode("utf-8")).hexdigest(), "what": "audit-pack section"}]
    return d + [{"ref": s["ref"], "sha256": s.get("sha256", ""), "what": f"open source ({s['kind']}) {s['url']}"}
                for s in job["sources"]]


def cmd_prepare(a):
    commit = subprocess.run(["git", "rev-parse", a.commit], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    pack = open(a.pack, encoding="utf-8").read()
    secs = [s for s in pack_sections(pack) if a.first <= s[0] <= a.last]
    assert len(secs) == a.last - a.first + 1 and all(s[1] for s in secs), "pack sections not found for every number"
    for n, slug, body in secs:
        page = git_show(commit, f"docs/reviews/{slug}/index.html")
        url = f"{SITE}/reviews/{slug}/index.html"
        live = urllib.request.urlopen(url, timeout=60).read()
        if live != page:
            raise SystemExit(f"REFUSED: {url} is not byte-identical to {commit[:12]} (pin a live commit)")
        review = json.loads(git_show(commit, f"docs/reviews/{slug}/review.json"))
        sample = re.findall(r"\|\s*\S\s*\|\s*`([^`]+)`\s*\|\s*(include|exclude)", body)
        shown, dropped = open_sources(commit, slug, review, [s[0] for s in sample])
        job = {"n": n, "slug": slug, "url": url, "commit": commit, "page_sha256": hashlib.sha256(page).hexdigest(),
               "pack_section": body, "tuples": served_tuples(review), "page_text": page_text(page.decode("utf-8")),
               "sources": shown, "dropped_by_licence": dropped,
               "recompute": [recompute(o) for o in review.get("outcomes") or []]}
        p = build_prompt(job)
        probs = guard_problems(job, p)
        if probs:
            raise SystemExit(f"REFUSED by the licence guard (D8), {slug}: {probs[:3]}")
        job["prompt_sha256"], job["prompt_chars"] = hashlib.sha256(p).hexdigest(), len(p.decode("utf-8"))
        job["prompt_format"] = "v2-guarded-blocks"
        d = os.path.join(OUT, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "input.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(job, fh, ensure_ascii=False, indent=1)
        print(f"{n:>2} {slug:45} prompt {job['prompt_chars']:>8} chars, {len(shown)} sources shown, "
              f"{len(dropped)} dropped (licence)", flush=True)


# ------------------------------------------------------------------------------------------------ run
def _load_job(slug):
    return json.load(open(os.path.join(OUT, slug, "input.json"), encoding="utf-8"))


def _slugs():
    return sorted((json.load(open(os.path.join(OUT, s, "input.json"), encoding="utf-8"))["n"], s)
                  for s in os.listdir(OUT) if os.path.exists(os.path.join(OUT, s, "input.json")))


def quota_reset(error) -> str | None:
    """'Resets in 4h31m28s' from a quota error (9 Oct: Gemini's individual quota; 4 retries per topic at 30-240 s
    were spent against a 4.5 h reset). The run stops retrying and records when to come back."""
    m = re.search(r"[Rr]esets in ((?:\d+h)?(?:\d+m)?(?:\d+s)?)", str(error or ""))
    return m.group(1) if m and m.group(1) else None


def run_one(slug: str, model: str, retries: int = 3) -> dict:
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    job = _load_job(slug)
    prompt = build_prompt(job)
    assert hashlib.sha256(prompt).hexdigest() == job["prompt_sha256"], "prompt drifted from the prepared input"
    digests = input_digests(job)
    caller = {"file": "scripts/blinded_review.py", "line": "run_one", "lane": "pva",
              "purpose": f"blinded review {slug} at {job['commit'][:12]} ({model})"}
    attempts = []
    for n in range(retries + 1):
        if model == "codex":
            rec = mcl.call(prompt, schema=SCHEMA, model=MODEL, effort=EFFORT, caller=caller, input_digests=digests,
                           timeout_s=3600)
        elif model == "agy-gemini":
            # agy takes the prompt on its command line (~32k chars on Windows), so the input goes as work-dir parts with
            # canaries (model_call_live.agy_call chunk_chars); the answer must list every canary in parts_read.
            schema = json.loads(json.dumps(SCHEMA))
            schema["required"].append("parts_read")
            schema["properties"]["parts_read"] = {"type": "array", "items": {"type": "string"}}
            rec = mcl.agy_call(prompt + b"\n\nAnswer with ONE JSON object matching this schema (and nothing else):\n" +
                               json.dumps(schema).encode(), schema=schema, caller=caller, input_digests=digests,
                               timeout_s=3600, chunk_chars=60000)
        else:
            raise SystemExit(f"unknown model {model}")
        ms.write_record(rec, os.path.join(ROOT, ms.RECORD_DIR))
        attempts.append({"record_id": rec["record_id"], "state": rec["state"], "error": rec.get("error")})
        if rec["state"] == "RAN_OK" or not re.search(r"rate|429|quota|exhaust|overload|temporar|capacity", str(rec.get("error")), re.I):
            break
        if quota_reset(rec.get("error")):       # a quota with an hours-long reset: retrying in seconds only burns calls
            break
        time.sleep(30 * 2 ** n)
    out = {"model": model, "slug": slug, "commit": job["commit"], "prompt_sha256": job["prompt_sha256"],
           "attempts": attempts, "state": attempts[-1]["state"]}
    if out["state"] != "RAN_OK" and quota_reset(attempts[-1].get("error")):
        out["state"], out["quota_resets_in"] = "QUOTA_EXHAUSTED", quota_reset(attempts[-1].get("error"))
    if out["state"] == "RAN_OK":
        raw = ms.replay(ms.load_record(os.path.join(ROOT, ms.RECORD_DIR, attempts[-1]["record_id"] + ".json")))
        out["output_sha256"] = hashlib.sha256(raw).hexdigest()
        txt = raw.decode("utf-8")
        m = re.search(r"\{.*\}", txt, re.S)
        try:
            out["response"] = json.loads(m.group(0) if m else txt)
        except ValueError as exc:
            out["state"], out["parse_error"], out["raw_head"] = "UNPARSEABLE", str(exc), txt[:400]
    name = "gemini" if model == "agy-gemini" else model
    with open(os.path.join(OUT, slug, f"{name}.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return out


def cmd_run(a):
    known = [s for _, s in _slugs()]
    want = [w.strip().strip("/") for w in a.only.split(",") if w.strip().strip("/")]
    unknown = sorted(set(want) - set(known))
    if unknown:
        raise SystemExit(f"REFUSED: --only names no prepared topic: {unknown}")
    todo = [s for s in known if not want or s in want]
    if not todo:
        raise SystemExit("REFUSED: no topic selected (nothing would run)")
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for r in ex.map(lambda s: run_one(s, a.model), todo):
            print(r["slug"], a.model, r["state"], [x["record_id"] for x in r["attempts"]], flush=True)


def cmd_unavailable(a):
    for _, s in _slugs():
        with open(os.path.join(OUT, s, f"{a.model}.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"model": a.model, "slug": s, "state": f"{a.model.upper()}_UNAVAILABLE", "reason": a.reason},
                      fh, ensure_ascii=False, indent=1)


# ------------------------------------------------------------------------------------------------ adjudicate
def _overlap(a: str, b: str) -> bool:
    na, nb = norm(a), norm(b)
    if na and nb and (na in nb or nb in na):
        return True
    ta, tb = set(na.split()), set(nb.split())
    return bool(ta and tb) and len(ta & tb) / len(ta | tb) >= 0.5


def adjudicate(slug: str) -> dict:
    job = _load_job(slug)
    page_n = norm(job["page_text"])
    src_n = [(s["url"], s["ref"], norm(s["text"])) for s in job["sources"]]
    models = {}
    for name in ("codex", "gemini"):
        p = os.path.join(OUT, slug, f"{name}.json")
        models[name] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"state": "NOT_RUN"}
    ran = [m for m, r in models.items() if r.get("state") == "RAN_OK"]
    reviewed = bool(ran)
    # agy is not schema-constrained (no --json-schema; see model_call_live): an item missing a required key is DROPPED
    # and counted, never guessed at (9 Oct: Gemini answered noac's screening with its own keys {nct_id, agrees_with_abstract})
    violations = {}
    for m in ran:
        resp = models[m]["response"] = dict(models[m].get("response") or {})
        for part, spec in SCHEMA["properties"].items():
            need = spec["items"]["required"]
            items_ = [x for x in resp.get(part) or [] if isinstance(x, dict)]
            keep = [x for x in items_ if all(k in x for k in need)]
            if len(keep) != len(resp.get(part) or []):
                violations.setdefault(m, {})[part] = len(resp.get(part) or []) - len(keep)
            resp[part] = keep       # a topic no model reviewed has NO findings count -- never a clean 0
    items = []
    for m in ran:
        for i, f in enumerate(models[m]["response"].get("findings") or []):
            ev = f.get("source_evidence") or {}
            hit = [(u, ref) for u, ref, t in src_n if contains(t, ev.get("quote", ""))]
            same_url = [h for h in hit if h[0] == ev.get("url")]
            it = {"id": f"{m}#{i + 1}", "model": m, **f, "page_quote_found": contains(page_n, f.get("page_quote", "")),
                  "source_quote_found_in": [r for _, r in (same_url or hit)],
                  "source_url_matches": bool(same_url)}
            checks = []
            if f.get("severity") == "changes_number":
                sv, so = numbers(f.get("served_value")), numbers(f.get("source_value"))
                pq, sq = numbers(f.get("page_quote")), numbers(ev.get("quote"))
                ok = bool(sv and so) and any(abs(x - y) < 1e-9 for x in sv for y in pq) and \
                    any(abs(x - y) < 1e-9 for x in so for y in sq) and abs(sv[0] - so[0]) > 1e-9
                checks.append(("number", ok))
            it["typed_check"] = "spans+number" if checks else "spans"
            it["typed_check_passed"] = it["page_quote_found"] and bool(it["source_quote_found_in"]) and all(ok for _, ok in checks)
            items.append(it)
    def same_tab(a, b):          # models name tabs loosely ("Data extraction" / "Data extraction tab")
        a, b = norm(a).replace(" tab", ""), norm(b).replace(" tab", "")
        return bool(a and b) and (a in b or b in a)
    for it in items:
        it["agreed_with"] = [o["id"] for o in items if o["model"] != it["model"] and same_tab(o.get("tab", ""), it.get("tab", ""))
                             and _overlap(o.get("page_quote", ""), it.get("page_quote", ""))]
        it["agreed_by"] = sorted({o["model"] for o in items if o["id"] in it["agreed_with"]} | {it["model"]})
        if len(it["agreed_by"]) >= 2:
            it["status"] = "CONFIRMED_2MODEL"
        elif it["typed_check_passed"]:
            it["status"] = "CONFIRMED_TYPED"
        else:
            it["status"] = "UNCONFIRMED"
            it["why_unconfirmed"] = ("page quote not on the page" if not it["page_quote_found"] else
                                     "source quote not in any open source shown" if not it["source_quote_found_in"] else
                                     "number check failed (served/source values not both quoted, or equal)")
    screening = []
    for m in ran:
        for s in models[m]["response"].get("screening_sample") or []:
            rid = str(s.get("record"))
            blk = [t for u, ref, t in src_n if rid in ref]
            screening.append({"model": m, **s, "quote_found_in_record": bool(blk) and contains(blk[0], s.get("quote", ""))})
    numeric = {m: models[m]["response"].get("numeric_checks") or [] for m in ran}
    det = job["recompute"]
    det_states = [r["status"] for r in det if r["status"] in ("AGREES", "DIFFERS")]
    out = {"slug": slug, "n": job["n"], "commit": job["commit"], "models": {m: models[m].get("state") for m in models},
           "reviewed": reviewed, "status": "REVIEWED" if reviewed else "NO_MODEL_RAN", "schema_violations": violations,
           "findings": items, "screening": screening, "numeric_models": numeric, "numeric_deterministic": det,
           "numbers_agree": ("-" if not det_states else "y" if all(s == "AGREES" for s in det_states) else "n"),
           "models_numeric_states": {m: [dict(outcome=c.get("outcome"), state=model_numeric_state(c)) for c in v]
                                     for m, v in numeric.items()},
           "models_numbers_agree": {m: (lambda st: "-" if not st else "y" if all(x == "AGREES" for x in st) else "n")(
               [model_numeric_state(c) for c in v if model_numeric_state(c) != "NOT_ASSESSABLE"]) for m, v in numeric.items()},
           "dropped_by_licence": job["dropped_by_licence"]}
    with open(os.path.join(OUT, slug, "adjudicated.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return out


def cmd_adjudicate(a):
    for _, s in _slugs():
        r = adjudicate(s)
        c = sum(f["status"].startswith("CONFIRMED") for f in r["findings"])
        if not r["reviewed"]:
            print(f"{s:45} NO_MODEL_RAN ({r['models']}) numbers {r['numbers_agree']}", flush=True)
            continue
        print(f"{s:45} findings {len(r['findings']):>3} confirmed {c:>3} numbers {r['numbers_agree']}", flush=True)


def cmd_summary(a):
    rows, conf = [], []
    for n, s in _slugs():
        r = json.load(open(os.path.join(OUT, s, "adjudicated.json"), encoding="utf-8"))
        cnt = {k: sum(1 for f in r["findings"] if f["status"].startswith("CONFIRMED") and f.get("severity") == k)
               for k in SEVERITIES}
        unc = sum(1 for f in r["findings"] if f["status"] == "UNCONFIRMED")
        dis = sum(1 for x in r["screening"] if x.get("verdict") == "DISAGREE")
        if not r.get("reviewed"):
            rows.append(f"| {n} | {s} | {r['models'].get('codex')} | {r['models'].get('gemini')} | NOT REVIEWED | "
                        f"NOT REVIEWED | NOT REVIEWED | - | - | {r['numbers_agree']} | - |")
            continue
        rows.append(f"| {n} | {s} | {r['models'].get('codex')} | {r['models'].get('gemini')} | {cnt['changes_number']} | "
                    f"{cnt['changes_wording']} | {cnt['record']} | {unc} | {dis} | {r['numbers_agree']} | "
                    f"{', '.join(f'{m}:{v}' for m, v in r['models_numbers_agree'].items()) or '-'} |")
        conf += [dict(f, slug=s) for f in r["findings"] if f["status"].startswith("CONFIRMED")]
    lines = ["| # | review | codex | gemini | confirmed changes_number | confirmed changes_wording | confirmed record | "
             "unconfirmed | screening DISAGREE | numbers agree (deterministic recompute) | numbers agree (model) |",
             "|---|---|---|---|---|---|---|---|---|---|---|"] + rows
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(a.header + "\n\n" + "\n".join(lines) + "\n")
        for k in SEVERITIES:
            fh.write(f"\n## Confirmed findings: {k}\n\n")
            for f in [x for x in conf if x.get("severity") == k]:
                fh.write(f"- **{f['slug']}** [{f['tab']}] ({f['status']}; {f['typed_check']}; {f['id']}) {f['claim']}\n"
                         f"  - page: \"{f['page_quote']}\"\n  - source ({f['source_evidence']['url']}): "
                         f"\"{f['source_evidence']['quote']}\"\n"
                         + (f"  - served {f['served_value']} vs source {f['source_value']}\n" if f.get("served_value") else ""))
    print("wrote", a.out)


def cmd_handover(a):
    """The Captain's packet: confirmed findings by class. A two-model finding is listed ONCE (its pair named); a
    manual check (outputs/blinded/manual_checks.json) overrides a finding's class and says what was checked."""
    mp = os.path.join(OUT, "manual_checks.json")
    manual = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
    by = {k: [] for k in SEVERITIES}
    scr, seen, models_run = [], set(), set()
    for n, s in _slugs():
        r = json.load(open(os.path.join(OUT, s, "adjudicated.json"), encoding="utf-8"))
        models_run |= {m for m, st in r["models"].items() if st == "RAN_OK"}
        for f in r["findings"]:
            key = f"{s}#{f['id']}"
            if key in seen:
                continue
            m = manual.get(key)
            if not (f["status"].startswith("CONFIRMED") or m):
                continue
            seen |= {key} | {f"{s}#{x}" for x in f.get("agreed_with", [])}
            pair = [x for x in r["findings"] if x["id"] in f.get("agreed_with", [])]
            by[m["class"] if m else f["severity"]].append((n, s, f, m, pair))
        scr += [(n, s, x) for x in r["screening"] if x.get("verdict") == "DISAGREE"]
    def line(n, s, f, m, pair):
        ev = f["source_evidence"]
        if m:
            basis = f"MANUALLY VERIFIED ({m['checked']}): {m['note']}"
        elif f["status"] == "CONFIRMED_2MODEL":
            basis = "TWO MODELS (" + ", ".join(f"{x['model']} {x['id']}: \"{x['claim'][:160]}\"" for x in pair) + ")"
        else:
            basis = "single model + typed check (" + f["typed_check"] + "): quotes verbatim in the bytes shown; the claim is the model's"
        return (f"- **{n}. {s}** [{f['tab']}] ({f['status']}) {f['claim']}\n  - page: \"{f['page_quote']}\"\n"
                f"  - source {ev.get('url')}: \"{ev.get('quote')}\"\n  - basis: {basis} ({f['id']})\n")
    out = [a.header + "\n\n"]
    for k in SEVERITIES:
        two = [x for x in by[k] if x[2]["status"] == "CONFIRMED_2MODEL"]
        out.append(f"\n## {k}: {len(by[k])} ({len(two)} two-model)\n\n")
        for x in sorted(by[k], key=lambda x: (x[2]["status"] != "CONFIRMED_2MODEL", x[0], x[2]["id"])):
            out.append(line(*x))
    out.append(f"\n## Screening sample: a model DISAGREES with the served decision: {len(scr)}\n\n")
    for n, s, x in scr:
        out.append(f"- **{n}. {s}** ({x['model']}) record `{x['record']}` (served: {x['served_decision']}): {x['reason']} "
                   f"-- quote in record: {x['quote_found_in_record']} \"{x['quote']}\"\n")
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(out))
    print("wrote", a.out, {k: len(v) for k, v in by.items()}, "screening", len(scr), "models", sorted(models_run))


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--commit", required=True)
    p.add_argument("--pack", required=True)
    p.add_argument("--first", type=int, default=11)
    p.add_argument("--last", type=int, default=32)
    p = sub.add_parser("run")
    p.add_argument("--model", choices=("agy-gemini", "codex"), required=True)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--only", default="")
    p = sub.add_parser("unavailable")
    p.add_argument("--model", required=True)
    p.add_argument("--reason", required=True)
    sub.add_parser("adjudicate")
    p = sub.add_parser("handover")
    p.add_argument("--out", required=True)
    p.add_argument("--header", default="# Blinded-review findings for the Captain, by class")
    p = sub.add_parser("summary")
    p.add_argument("--out", required=True)
    p.add_argument("--header", default="# Blinded reviews")
    a = ap.parse_args(argv)
    {"prepare": cmd_prepare, "run": cmd_run, "unavailable": cmd_unavailable, "adjudicate": cmd_adjudicate,
     "summary": cmd_summary, "handover": cmd_handover}[a.cmd](a)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
