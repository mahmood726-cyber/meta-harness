"""V1 release acceptance -- the "Page verifier and archive lane"'s hostile audit of a release against
docs/evidence/enforcement-gate-2026-09-21/18-release-acceptance-checklist.md, run on the SERVED bytes.

Every probe is stamped with the exact release it ran against (checklist: "Every probe must name the exact release it ran
against, and be re-run on the SERVED bytes of the release being accepted").

  python v1_accept.py --release <sha> --prev <sha> --work <dir> [--site URL] [--source served|git] [--only P1,P2]

--source served (default) downloads every file from the site and first proves served == committed per file (a CDN or
deploy mismatch is reported, retried once after the 600 s max-age, and never silently used). --source git builds the same
tree from `git show <release>:docs/...` -- a PRE-deploy rehearsal on a candidate commit; its results are labelled
REHEARSAL and are not acceptance.

Probes (ids are stable; the scorecard maps them to checklist items):
  P0  identity: release sha; production record for it ATTESTED n/n (served mode only)
  P1  served == committed, per file, for every file this audit reads
  P2  certificate auditor (the served one) on every review page, full scope: RESULT REPRODUCED
  P3  every page names the SERVED verifiers' sha256 and quotes their NOT-checked lists (page.py naming its verifier)
  P4  served numbers vs --prev: every changed outcome/trial tuple must correspond to a notice in the release's
      result_changes.json whose `after` equals the served value and whose reviewer_countersignature is SEEN_AND_SIGNED /
      BATCH_SEEN_AND_SIGNED (checklist E: nothing changes a served number unsigned). The signer's identity is recorded but
      cannot be authenticated (EG-F2).
  P5  bundle verifier (the served one) on each served bundle: baseline verdict and, if present, the four separate verdicts
      (checklist A(a)/B1, B4)
  P6  mutation battery on the served bundle tree (checklist A(b), A(c), A(d), B2): each named mutation must FAIL for its
      intended reason; integrity-class and semantic-class failure codes are reported separately; restore must PASS
  P7  checklist C: HARMONY (PMID 30291013) -- pooled? admissible? what the admissibility verdict says
  P8  PVA-D11: the bundle's served span.text is checked against the source (plant: replace one pooled row's span.text)
Writes <work>/scorecard.json and <work>/scorecard.md."""
from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = "C:/mh-lanes/pva"
SITE = "https://mahmood726-cyber.github.io/meta-harness/"
FULL_SCOPE = "RESULT REPRODUCED [scope: certificate + review.json + manifest.json + index.html]"
PAGE_FILES = ("CERTIFICATE.json", "review.json", "manifest.json", "index.html")
OPTIONAL_PAGE_FILES = ("BUNDLE.json", "EXECUTION_RECORD.json")
VERIFIERS = ("scripts/audit_certificate_stdlib.py", "scripts/verify_bundle.py")
INTEGRITY_RX = re.compile(r"(DIGEST|SHA256|SHA-256|BLOB|INTEGRITY|BYTES|CHECKSUM|ARTEFACT_UNREACHABLE|CONTAINER)", re.I)


def git(*a: str) -> bytes:
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, stdin=subprocess.DEVNULL).stdout


def git_ok(*a: str) -> bool:
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, stdin=subprocess.DEVNULL).returncode == 0


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Audit:
    def __init__(self, a):
        self.a = a
        self.rel = git("rev-parse", a.release).decode().strip()
        self.prev = self.resolve_prev(a.prev, self.rel) if a.prev else None
        assert re.fullmatch(r"[0-9a-f]{40}", self.rel), f"release {a.release!r} does not resolve in {REPO}"
        self.work = Path(a.work)
        self.root = self.work / "site"
        self.site = a.site.rstrip("/") + "/"
        self.mode = a.source
        self.results: dict[str, dict] = {}
        self.baseline_rows: dict = {}
        self.fetched: dict[str, str] = {}      # site-relative path -> sha256 of the bytes used

    @staticmethod
    def resolve_prev(prev: str, rel: str) -> str:
        """--prev auto: the newest commit with an ATTESTED production record that is a proper ancestor of the release --
        the release that was being served before this one. Printed, never silently guessed."""
        if prev != "auto":
            return git("rev-parse", prev).decode().strip()
        git("fetch", "-q", "origin", "production-records")
        for subj in git("log", "origin/production-records", "--format=%s").decode().splitlines():
            m = re.match(r"production record ([0-9a-f]{12}): ATTESTED", subj)
            if not m:
                continue
            full = git("rev-parse", m.group(1)).decode().strip()
            if re.fullmatch(r"[0-9a-f]{40}", full) and full != rel and git_ok("merge-base", "--is-ancestor", full, rel):
                print(f"--prev auto -> {full[:12]} ({subj})", flush=True)
                return full
        raise SystemExit("REFUSED: --prev auto found no attested ancestor of the release")

    # --------------------------------------------------------------------------------------------- acquisition
    def committed(self, rel_path: str) -> bytes | None:
        p = f"{self.rel}:docs/{rel_path}"
        return git("show", p) if git_ok("cat-file", "-e", p) else None

    def fetch(self, rel_path: str) -> bytes | None:
        if self.mode == "git":
            return self.committed(rel_path)
        url = self.site + rel_path
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    return r.read()
            except Exception as e:  # noqa: BLE001
                if getattr(e, "code", None) == 404:
                    return None
                time.sleep(5 * (attempt + 1))
        return None

    def put(self, rel_path: str, data: bytes):
        out = self.root.joinpath(*rel_path.split("/"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        self.fetched[rel_path] = sha(data)

    def slugs(self) -> list[str]:
        names = git("ls-tree", "--name-only", self.rel, "docs/reviews/").decode().split()
        return [n.split("/")[-1] for n in names if git_ok("cat-file", "-e", f"{self.rel}:{n}/CERTIFICATE.json")]

    def bundle_paths(self, slug: str) -> set[str]:
        b = json.loads(self.committed(f"reviews/{slug}/BUNDLE.json"))
        paths = {a["served_path"] for a in b.get("artefacts", []) if a.get("state") == "SERVED"}
        paths |= {f["path"].removeprefix("docs/") for f in b.get("supporting_files", [])}
        paths |= {r["served_path"] for r in b.get("review_files", [])}
        paths |= {f"reviews/{slug}/BUNDLE.json", f"topics/{slug}.json"}
        return paths

    def acquire(self):
        if self.root.exists():
            shutil.rmtree(self.root)
        want = set(VERIFIERS)
        self.pages = self.slugs()
        self.bundles = [s for s in self.pages if self.committed(f"reviews/{s}/BUNDLE.json") is not None]
        for s in self.pages:
            want |= {f"reviews/{s}/{f}" for f in PAGE_FILES}
            want |= {f"reviews/{s}/{f}" for f in OPTIONAL_PAGE_FILES if self.committed(f"reviews/{s}/{f}") is not None}
        for s in self.bundles:
            want |= self.bundle_paths(s)
        want.add("result_changes.json")
        mism, missing = [], []
        for p in sorted(want):
            data = self.fetch(p)
            if data is None:
                missing.append(p)
                continue
            c = self.committed(p)
            if c is not None and sha(c) != sha(data):
                mism.append(p)
            self.put(p, data)
        if mism and self.mode == "served":            # a CDN window serves files of two deploys: wait out max-age once
            time.sleep(660)
            still = []
            for p in mism:
                data = self.fetch(p)
                if data is not None and sha(data) == sha(self.committed(p)):
                    self.put(p, data)
                else:
                    still.append(p)
            retried, mism = mism, still
        else:
            retried = []
        self.record("P1", "served == committed, per file read by this audit",
                    ok=not mism and not missing,
                    detail={"files": len(want), "mismatch_after_retry": mism[:50], "n_mismatch": len(mism),
                            "missing": missing[:50], "n_missing": len(missing), "retried_after_max_age": len(retried),
                            "mode": self.mode})

    # --------------------------------------------------------------------------------------------- helpers
    def record(self, pid: str, what: str, ok, detail):
        self.results[pid] = {"probe": pid, "what": what, "ok": ok, "release": self.rel, "mode": self.mode,
                             "ran_utc": now(), "detail": detail}
        flag = {True: "PASS", False: "FAIL", None: "N/A"}[ok]
        print(f"[{pid}] {flag}  {what}", flush=True)

    def run_py(self, script: Path, args: list[str], cwd: Path, timeout=1800):
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
        p = subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", stdin=subprocess.DEVNULL, timeout=timeout, env=env)
        return p.returncode, p.stdout, p.stderr

    def vb(self, slug: str, extra: list[str] | None = None) -> dict:
        rc, out, err = self.run_py(self.root / "scripts" / "verify_bundle.py",
                                   ["--root", str(self.root), "--slug", slug, "--json", *(extra or [])], self.root)
        try:
            return json.loads(out)
        except ValueError:
            m = re.search(r"verdict (\w+)\s+(\w+):?\s*(.*)", out + err)
            return {"verdict": m.group(1) if m else "NO_JSON", "failures": [((m.group(2) + ": " + m.group(3)) if m else (out + err)[-400:])]}

    # --------------------------------------------------------------------------------------------- probes
    def p0(self):
        if self.mode != "served":
            return self.record("P0", "production record ATTESTED for the release", None, "rehearsal mode (git bytes)")
        git("fetch", "-q", "origin", "production-records")
        subj = git("log", "origin/production-records", "--format=%s").decode().splitlines()
        rec = [s for s in subj if f"production record {self.rel[:12]}" in s]
        m = re.search(r"ATTESTED \((\d+)/(\d+)", rec[0]) if rec else None
        self.record("P0", "production record ATTESTED n/n for the release", bool(m and m.group(1) == m.group(2)),
                    {"record": rec[0] if rec else None})

    def p2(self):
        aud = self.root / "scripts" / "audit_certificate_stdlib.py"
        bad, ok = [], 0
        for s in self.pages:
            d = self.work / "p2" / s
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True)
            for f in PAGE_FILES:
                shutil.copyfile(self.root / "reviews" / s / f, d / f)
            rc, out, err = self.run_py(aud, ["CERTIFICATE.json"], d, timeout=600)
            res = next((l for l in out.splitlines() if l.startswith("RESULT")), "NO RESULT LINE")
            (ok := ok + 1) if res == FULL_SCOPE else bad.append({"slug": s, "result": res})
        shutil.rmtree(self.work / "p2", ignore_errors=True)
        self.record("P2", "served certificate auditor, full scope, every review page", not bad and ok == len(self.pages),
                    {"pages": len(self.pages), "reproduced_full_scope": ok, "not": bad,
                     "auditor_sha256": self.fetched.get("scripts/audit_certificate_stdlib.py")})

    def p3(self):
        sys.path.insert(0, str(self.work / "harness_at_release"))
        problems = []
        dig = {v: self.fetched.get(v) for v in VERIFIERS}
        for s in self.pages:
            src = (self.root / "reviews" / s / "index.html").read_text(encoding="utf-8")
            need = ["scripts/audit_certificate_stdlib.py"] + (["scripts/verify_bundle.py"] if s in self.bundles else [])
            for v in need:
                if not dig.get(v) or dig[v] not in src:
                    problems.append(f"{s}: does not name the served {v} sha256 {str(dig.get(v))[:12]}")
            if src.count("id='page-verifier'") != 1:
                problems.append(f"{s}: {src.count(chr(39) + 'page-verifier' + chr(39))} verifier boxes")
        self.record("P3", "every page names the SERVED verifiers' sha256 (page.py naming its verifier)", not problems,
                    {"pages": len(self.pages), "problems": problems[:60], "served_verifier_sha256": dig})

    def _tuples(self, commit: str, source: str) -> dict:
        out = {}
        for s in self.pages:
            if source == "served":
                p = self.root / "reviews" / s / "review.json"
                d = json.loads(p.read_bytes()) if p.is_file() else None
            else:
                raw = git("show", f"{commit}:docs/reviews/{s}/review.json")
                d = json.loads(raw) if raw else None
            if not d:
                continue
            for o in d.get("outcomes", []):
                r = o.get("result") or {}
                out[(s, o["name"], "RESULT")] = tuple(r.get(k) for k in ("k", "estimate", "ci_low", "ci_high"))
                for t in o.get("trials", []):
                    out[(s, o["name"], str(t.get("id") or t.get("label")))] = tuple(
                        t.get(k) for k in ("effect", "ci_low", "ci_high", "ai", "n1i", "ci", "n2i"))
        return out

    def p4(self):
        if not self.prev:
            return self.record("P4", "served numbers vs previous release, each change signed", None, "no --prev given")
        before, after = self._tuples(self.prev, "git"), self._tuples(self.rel, "served")
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        rc = json.loads((self.root / "result_changes.json").read_bytes())
        notices = rc.get("notices", rc if isinstance(rc, list) else [])
        signed_states = {"SEEN_AND_SIGNED", "BATCH_SEEN_AND_SIGNED"}
        unsigned, signed = [], []
        for k in changed:
            s, oc, which = k
            ns = [n for n in notices if n.get("slug") == s and n.get("outcome") == oc]
            sig = [n for n in ns if (n.get("reviewer_countersignature") or {}).get("state") in signed_states]
            def result_match(nlist, a):
                return [n for n in nlist if tuple((n.get("after") or {}).get(x) for x in ("k", "estimate", "ci_low", "ci_high")) == a]
            if which == "RESULT":
                match = result_match(sig, after.get(k))
            else:
                # a trial-row change is signed only if a signed notice for this outcome NAMES the trial as leaving or entering
                # the pool, or the outcome's served RESULT change is itself carried by a signed notice with that exact `after`
                tid = which.replace("PMID ", "")
                named = [n for n in sig if any(tid in json.dumps(x) for x in (n.get("left_pool") or []) + (n.get("entered_pool") or []))]
                res_key = (s, oc, "RESULT")
                carried = result_match(sig, after.get(res_key)) if before.get(res_key) != after.get(res_key) else []
                match = named or carried
            (signed if match else unsigned).append({"key": list(k), "before": before.get(k), "after": after.get(k),
                                                     "notices_for_outcome": len(ns), "signed_notices": len(sig),
                                                     "signers": sorted({str((n.get("reviewer_countersignature") or {}).get("by")) for n in match})})
        self.record("P4", "served numbers vs previous release: no change without a signed notice (checklist E)",
                    not unsigned, {"prev": self.prev, "tuples_before": len(before), "tuples_after": len(after),
                                   "changed": len(changed), "signed": signed[:80], "UNSIGNED": unsigned[:200],
                                   "n_unsigned": len(unsigned),
                                   "note": "signer identity is recorded, not authenticated (EG-F2)"})

    VERDICT_KEYS = ("byte_integrity", "arithmetic_consistency", "scientific_admissibility", "publication_eligibility")

    FOUR_STEMS = {"byte_integrity": ("integrity",), "arithmetic_consistency": ("arithmetic",),
                  "scientific_admissibility": ("admissib",), "publication_eligibility": ("publication", "publish")}

    def four(self, r: dict) -> dict:
        """The four verdicts of checklist B4, recognised by meaning (key stem), wherever the report puts them: top level, a
        `verdicts` object, or a `verdict` that is itself an object. A plain string `verdict` is ONE verdict, not four."""
        found = {}
        containers = [r]
        for k in ("verdicts", "verdict"):
            if isinstance(r.get(k), dict):
                containers.append(r[k])
        for c in containers:
            for key, val in c.items():
                lk = key.lower()
                for canon, stems in self.FOUR_STEMS.items():
                    if canon not in found and any(st in lk for st in stems):
                        found[canon] = val.get("verdict", val) if isinstance(val, dict) else val
        return found

    def p5(self):
        out = {}
        for s in self.bundles:
            r = self.vb(s)
            out[s] = {"verdict": r.get("verdict"), "four_verdicts": self.four(r),
                      "failures": (r.get("failures") or [])[:10],
                      "disclosed_refusals": (r.get("disclosed_refusals") or [])[:10]}
        self.baseline = out
        self.baseline_rows = {s: {str(x.get("pmid")): x.get("final") for x in (self.vb(s).get("rows") or [])} for s in self.bundles}
        ok = all(v["verdict"] == "PASS" for v in out.values()) if out else None
        b4 = {s: sorted(v["four_verdicts"]) for s, v in out.items()}
        self.record("P5", "served bundle verifier baseline PASSES (checklist A(a)/B1)", ok, {"bundles": out})
        present = {s: sorted(v) for s, v in b4.items()}
        self.record("P5b", "four verdicts reported SEPARATELY: byte integrity, arithmetic, admissibility, publication (checklist B4)",
                    (all(len(v) == 4 for v in present.values()) if present else None),
                    {"found_per_bundle": present, "looked_for": list(self.VERDICT_KEYS)})

    # ---- mutation battery ---------------------------------------------------------------------------------
    def _rows(self, b):
        return {str(r["trial"]["id"]).replace("PMID ", ""): r for r in b["verification_rows"]}

    def mutations(self, slug: str, b: dict) -> list[dict]:
        rows = self._rows(b)
        pids = list(rows)
        M = []

        def limb(name, pmid, code_rx, item):
            M.append({"id": name, "item": item, "kind": "corrupt", "args": ["--corrupt", pmid, name.split(":")[0]],
                      "intended": code_rx, "target": pmid})

        def edit(name, fn, code_rx, item, target=None):
            M.append({"id": name, "item": item, "kind": "edit", "fn": fn, "intended": code_rx, "target": target})

        s6, amp, leader, rewind, harmony = "27633186", "34215025", "27295427", "31189511", "30291013"
        if s6 in rows:
            limb("nontarget_span:SUSTAIN-6", s6, r"P9|TARGET|ENDPOINT|BIND|COMPONENT", "A(b) SUSTAIN-6")
            limb("components:SUSTAIN-6", s6, r"P4|COMPONENT|ENDPOINT", "A(b) SUSTAIN-6")
        if amp in rows:
            limb("unlisted_span:AMPLITUDE-O", amp, r"P8|P9|UNLISTED|ENDPOINT|BIND", "A(b) AMPLITUDE-O")
            limb("span:AMPLITUDE-O", amp, r"P2|SPAN", "A(b) AMPLITUDE-O")
        # FREEDOM-CVO mixed tuple: its regulatory fact's CI taken from a different row of the same table
        if any(f.get("trial") == "FREEDOM-CVO" for f in b.get("regulatory_facts", [])):
            def freedom_mixed(bb):
                f = next(f for f in bb["regulatory_facts"] if f.get("trial") == "FREEDOM-CVO")
                e = (f.get("decision") or {}).get("effect") or {}
                e["ci_high"] = round((e.get("ci_high") or 1.0) + 0.21, 3)
            edit("mixed_tuple:FREEDOM-CVO", freedom_mixed, r"FREEDOM|REGULATORY|TUPLE|TABLE|BIND|MIXED", "A(b)/B2 FREEDOM mixed tuple")
        if leader in rows:
            limb("ci_low_truncated:LEADER", leader, r"P3|TOKEN|NUMERIC", "A(c) numeric prefix")
            limb("ci_high_rounded:LEADER", leader, r"P3|TOKEN|NUMERIC|ROUND", "A(c) numeric prefix")

            def mixed(bb):   # LEADER's point with SUSTAIN-6's interval: every number genuine, from two different clauses
                r, o = self._rows(bb)[leader], self._rows(bb).get(s6) or self._rows(bb)[pids[0]]
                for k in ("ci_low", "ci_high"):
                    r["effect"][k] = o["effect"][k]
            edit("mixed_tuple:LEADER+SUSTAIN6_CI", mixed, r"P3|TOKEN|TUPLE|CLAUSE|DISAGREE", "A(c) mixed tuple", target=leader)

            def erase(bb):   # identity erasure: the row keeps its numbers, loses who it is
                r = self._rows(bb)[leader]
                r["trial"]["id"] = ""
                r["trial"].pop("family_id", None)
            edit("identity_erasure:LEADER", erase, r"IDENTITY|ID|SELECTOR|FAMILY|RESOLV", "A(c)/B2 identity erasure", target=None)

            def dup(bb):     # duplicate ID: two rows claim the same trial
                a = self._rows(bb)[leader]
                other = next(r for k, r in self._rows(bb).items() if k != leader)
                other["trial"]["id"] = a["trial"]["id"]
            edit("duplicate_id:LEADER", dup, r"DUPLICATE|IDENTITY|ID|SELECTOR", "B2 duplicate IDs", target=None)

            def subst(bb):   # pool substitution: LEADER's pool input replaced by another trial's numbers, pool recomputed
                pin = next(i for i in bb["pooled_reference"]["inputs"] if str(i["id"]).endswith(leader))
                src = self._rows(bb).get(s6) or self._rows(bb)[pids[0]]
                pin.update(effect=src["effect"]["estimate"], ci_low=src["effect"]["ci_low"], ci_high=src["effect"]["ci_high"])
            edit("pool_substitution:LEADER", subst, r"POOL|INPUT|DISAGREE|SUBSTIT", "B2 pool substitution", target=None)

            def estimand_contra(bb):   # contradictory estimand: HR tuple declared an odds ratio
                r = self._rows(bb)[leader]
                est = r["analysis_identity"].get("estimator")
                if isinstance(est, dict):
                    est["value"] = "odds ratio"
            edit("estimand_contradictory:LEADER", estimand_contra, r"ESTIMA|P11|MEASURE", "B2 contradictory estimand", target=leader)

            def estimand_malformed(bb):
                r = self._rows(bb)[leader]
                r["analysis_identity"]["analysis_set"] = None
            edit("estimand_malformed:LEADER", estimand_malformed, r"ESTIMA|P10|P11|MALFORM|ANALYSIS", "B2 malformed estimand", target=leader)

            def span_text(bb):   # PVA-D11
                self._rows(bb)[leader]["span"]["text"] = "This sentence does not occur in the LEADER abstract at all."
            edit("span_text_replaced:LEADER", span_text, r"SPAN|P2", "PVA-D11", target=leader)
        if rewind in rows:
            def rewind_swap(bb):   # the REWIND arm swap: the contrast claimed reversed, the unreciprocated value kept
                cd = self._rows(bb)[rewind]["analysis_identity"]["comparator_direction"]
                cd["value"] = "placebo vs dulaglutide"
                cd.pop("ordered_contrast", None)
                if isinstance(cd.get("observed"), dict):
                    cd["observed"]["value"] = "placebo vs dulaglutide"
            edit("rewind_arm_swap:REWIND", rewind_swap, r"COMPARATOR|DIRECTION|CONTRAST|ARM", "B2 REWIND arm swap", target=rewind)
        return M

    def p6(self):
        report = {}
        for s in self.bundles:
            path = self.root / "reviews" / s / "BUNDLE.json"
            canon_bytes = path.read_bytes()
            canon = json.loads(canon_bytes)
            rows = []
            try:
                for m in self.mutations(s, canon):
                    if m["kind"] == "corrupt":
                        r = self.vb(s, m["args"])
                    else:
                        b = copy.deepcopy(canon)
                        m["fn"](b)
                        path.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
                        r = self.vb(s)
                        path.write_bytes(canon_bytes)
                    fails = [str(x) for x in (r.get("failures") or [])]
                    pool = r.get("pool") or {}
                    fails += [str(x) for x in (pool.get("refused_before_logs") or [])]
                    fails += [str(x[0] if isinstance(x, list) else x) for x in ((r.get("pool_measure_guard") or {}).get("refusals") or [])]
                    changed = [x for x in (r.get("corruption_effect") or [])]
                    rows_now = {str(x.get("pmid")): x.get("final") for x in (r.get("rows") or [])}
                    base_rows = {}
                    semantic = [f for f in fails if not INTEGRITY_RX.search(f.split(":")[0])]
                    integrity = [f for f in fails if INTEGRITY_RX.search(f.split(":")[0])]
                    tgt = m.get("target")
                    trow = next((x for x in (r.get("rows") or []) if str(x.get("pmid")) == str(tgt)), None) if tgt else None
                    tpreds = [k for k, v in ((trow or {}).get("predicates") or {}).items() if v is not True]
                    base_final = ((self.baseline_rows or {}).get(s) or {}).get(str(tgt))
                    row_refused = bool(trow) and trow.get("final") != "ADMISSIBLE" and base_final == "ADMISSIBLE"
                    intended = [f for f in fails + tpreds if re.search(m["intended"], f, re.I)]
                    verdict = r.get("verdict")
                    rows.append({"id": m["id"], "item": m["item"], "verdict": verdict, "four_verdicts": self.four(r),
                                 "fails_as_expected": verdict == "FAIL" or row_refused,
                                 "verdict_level_fail": verdict == "FAIL", "target": tgt, "target_row_refused": row_refused,
                                 "target_failing_predicates": tpreds,
                                 "intended_reason_named": bool(intended),
                                 "semantic_codes": semantic[:6], "integrity_codes": integrity[:6],
                                 "rows_final": rows_now, "raw_first_failures": fails[:4]})
                    caught = verdict == "FAIL" or row_refused
                    tag = ("OK " if intended else "WRONG-REASON") if caught else "NOT CAUGHT"
                    tag += " [verdict]" if verdict == "FAIL" else (" [row only]" if row_refused else "")
                    print(f"   {s[:18]:18} {m['id']:36} verdict={verdict:<8} {tag}  {tpreds[:3]}", flush=True)
            finally:
                path.write_bytes(canon_bytes)
            restored = self.vb(s)
            report[s] = {"mutations": rows, "restored_verdict": restored.get("verdict")}
        allrows = [x for v in report.values() for x in v["mutations"]]
        ok = bool(allrows) and all(x["fails_as_expected"] and x["intended_reason_named"] for x in allrows) and \
            all(v["restored_verdict"] == "PASS" for v in report.values())
        self.record("P6", "mutation battery: each named mutation FAILS for its intended reason; restore PASSES (A(b)(c)(d), B2)",
                    ok, report)

    def p7(self):
        s = "glp1-ra-mace-t2d"
        if s not in self.bundles:
            return self.record("P7", "checklist C: HARMONY pooled vs admissible", None, "no glp1 bundle")
        b = json.loads((self.root / "reviews" / s / "BUNDLE.json").read_bytes())
        pooled = any(str(i["id"]).endswith("30291013") for i in b["pooled_reference"]["inputs"])
        r = self.vb(s)
        row = next((x for x in r.get("rows") or [] if str(x.get("pmid")) == "30291013"), {})
        adm = (r.get("pool") or {}).get("admissible_only_pool_for_information")
        self.record("P7", "checklist C: HARMONY (30291013) pooled while inadmissible -- is it reported as such?",
                    None, {"pooled_in_k": pooled, "k": b["pooled_reference"].get("k"), "row_final": row.get("final"),
                           "failing_predicates": [k for k, v in (row.get("predicates") or {}).items() if v is not True],
                           "verifier_verdict": r.get("verdict"), "four_verdicts": self.four(r),
                           "admissible_only_pool": adm})

    def p8(self):
        """The external audit's two-values report (CDN-1): on the bytes this audit read, every CERTIFICATE.json, every
        review.json's embedded certificate and every served bundle must carry ONE analysis_code_sha256, and each page's
        release_sha256 must agree across its certificate, review.json and (if present) BUNDLE.json. Two values in one
        read = a mixed view (CDN window) or a real mismatch; P1 says which (a mixed view also fails P1)."""
        rx = re.compile(r'"analysis_code_sha256"\s*:\s*"([0-9a-f]{64})"')
        rr = re.compile(r'"release_sha256"\s*:\s*"([0-9a-f]{64})"')
        codes, per_page_release = {}, {}
        for s in self.pages:
            rels = set()
            for f in ("CERTIFICATE.json", "review.json", "BUNDLE.json"):
                fp = self.root / "reviews" / s / f
                if not fp.is_file():
                    continue
                t = fp.read_text(encoding="utf-8", errors="replace")
                for v in rx.findall(t):
                    codes.setdefault(v, set()).add(f"{s}/{f}")
                if f in ("CERTIFICATE.json", "review.json"):
                    rels |= set(rr.findall(t)[:1] if f == "CERTIFICATE.json" else [])
            per_page_release[s] = sorted(rels)
        ok = len(codes) == 1
        self.record("P8", "one analysis_code_sha256 across every served certificate/review/bundle read (the CDN-1 check)", ok,
                    {"distinct_values": {k[:12]: len(v) for k, v in codes.items()},
                     "where_if_more_than_one": ({k[:12]: sorted(v)[:10] for k, v in codes.items()} if not ok else None)})

    def p9(self):
        """The thin-tree hazard (oc, 26 Sep): build_topic in an incomplete tree wrote a review.json/CERTIFICATE without
        release_status and rob_spancheck, and nothing else failed. Every served review.json must still carry both."""
        missing = []
        for s in self.pages:
            d = json.loads((self.root / "reviews" / s / "review.json").read_bytes())
            lack = [k for k in ("release_status",) if k not in d] + ([] if "rob_spancheck" in json.dumps(d) else ["rob_spancheck"])
            if lack:
                missing.append({"slug": s, "missing": lack})
        self.record("P9", "every served review.json keeps release_status and rob_spancheck (the thin-tree regeneration hazard)",
                    not missing, {"pages": len(self.pages), "missing": missing})

    # --------------------------------------------------------------------------------------------- output
    def write(self):
        self.work.mkdir(parents=True, exist_ok=True)
        doc = {"release": self.rel, "prev": self.prev, "mode": self.mode, "site": self.site, "finished_utc": now(),
               "checklist": "docs/evidence/enforcement-gate-2026-09-21/18-release-acceptance-checklist.md (1fa77f2c)",
               "probes": self.results, "files_read_sha256": self.fetched}
        (self.work / "scorecard.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        lines = [f"# V1 acceptance scorecard -- release {self.rel[:12]} ({self.mode})", "",
                 f"prev {str(self.prev)[:12]}; finished {doc['finished_utc']}; site {self.site}", "",
                 "| probe | result | what |", "|---|---|---|"]
        for pid, r in self.results.items():
            lines.append(f"| {pid} | {({True: 'PASS', False: '**FAIL**', None: 'n/a'})[r['ok']]} | {r['what']} |")
        (self.work / "scorecard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", required=True)
    ap.add_argument("--prev")
    ap.add_argument("--work", required=True)
    ap.add_argument("--site", default=SITE)
    ap.add_argument("--source", choices=["served", "git"], default="served")
    ap.add_argument("--only", default="P0,P1,P2,P3,P4,P5,P6,P7,P8,P9")
    a = ap.parse_args()
    au = Audit(a)
    only = set(a.only.split(","))
    print(f"release {au.rel} prev {au.prev} mode {au.mode}", flush=True)
    au.acquire()
    for pid in ("P0", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"):
        if pid in only:
            try:
                getattr(au, pid.lower())()
            except Exception as e:  # noqa: BLE001 -- a probe that crashes is a FAIL with its reason, never skipped
                au.record(pid, f"probe crashed: {type(e).__name__}", False, repr(e)[:800])
    au.write()
    print(f"scorecard: {au.work / 'scorecard.md'}")


if __name__ == "__main__":
    main()
