"""Build ONE bulk-signing packet for every pending (unsigned) result-change notice across the lanes, for Mahmood.

  python scripts/nr_bulk_signing_packet.py OUT_DIR

Writes OUT_DIR/BULK_SIGNING_MANIFEST.json (the canonical manifest; its sha256 is what Mahmood signs),
OUT_DIR/BULK_SIGNING_PACKET.md (readable copy) and OUT_DIR/BULK_SIGNING_MANIFEST.sha256.

Every item carries: its own sha256 (canonical JSON of the notice / move exactly as found), its source (path or branch, the
source file's sha256 and commit where known), a one-line plain-English change, old -> new number, and flags derived by
harness.result_changes.conclusion_changed plus: STALE (its 'before' is not what is served now), CHAINED (its 'before' is
another pending item's 'after'), CONFLICT (another lane changes the same outcome differently). Nothing is signed here:
there is no signing code in this script, and a lane never signs for the reviewer.
"""
from __future__ import annotations

import datetime
import hashlib
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import result_changes  # noqa: E402

SIGNED = {"SEEN_AND_SIGNED", "BATCH_SEEN_AND_SIGNED"}


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(x) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def git(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


# ---- sources (current lane tips; decided 2026-09-29 from the per-source census in the handover) ---------------------
JSON_SOURCES = [
    # the cascade's current tip; F:/mh-lanes-wt/acq-a and acq-b hold 5 EARLIER drafts of 5 of these notices (same lane,
    # same outcomes, different bytes, 2026-09-27) -- superseded, not included (SUPERSEDED_DRAFTS below)
    ("evid (acquisition cascade)", "file", "F:/mh-lanes-wt/screen/docs/result_changes.json", "F:/mh-lanes-wt/screen"),
    ("evid (glp1 admission)", "file", "C:/mh-lanes/evid-wt/docs/result_changes.json", "C:/mh-lanes/evid-wt"),
    ("evid2 (q-decisions)", "branch", "origin/evid2/q-decisions:docs/result_changes.json", ROOT),
    ("enforcement-gate (2026-09-21 wave)", "branch", "origin/enforcement-gate:docs/result_changes.json", ROOT),
]
SUPERSEDED_DRAFTS = {"path": "F:/mh-lanes-wt/acq-a (and acq-b) docs/result_changes.json", "n": 5,
                     "why": "earlier drafts (2026-09-27) of 5 evid acquisition-cascade notices whose current versions are "
                            "on evid/v1.0.1-acquisition-cascade"}
# The 41 enforcement-gate notices: ids and the established hash to sign (notice_block_sha256) are in record 24; their
# statuses were corrected by record 39's header (2026-09-25): 34 sign-as-is, 5 withdraw, 2 re-issue. Static, cited.
EG_RECORD_24 = "docs/evidence/enforcement-gate-2026-09-21/24-the-41-notices-for-signature.md"
EG_WITHDRAW = {"N09", "N17", "N18", "N19", "N29"}
EG_REISSUE = {"N30", "N35"}
EG_STATUS_SOURCE = "docs/evidence/enforcement-gate-2026-09-21/39-p5-rederivation-for-nr.md (CORRECTED header, 2026-09-25)"
NR_FILES = ["outputs/handover/lanes/nr-v101-regex/NOTICE_TO_APPEND.json"] + [
    f"outputs/handover/lanes/nr-v101-regex/items/NOTICES_TO_APPEND_V101_{x}.json" for x in ("B", "C", "D", "E", "F", "G",
                                                                                              "H_LABELS")]
OC_MOVES = ("oc (V1.0.1 candidate stack)", "C:/mh-lanes/oc-sema/evidence/v101_candidate/moves_83495751.json",
            "C:/mh-lanes/oc-sema/evidence/v101_candidate/NOTICES.md", "C:/mh-lanes/oc-sema")


def _load_source(kind, where, cwd):
    if kind == "file":
        raw = open(where, "rb").read()
        commit = (git(cwd, "log", "-1", "--format=%H", "--", os.path.relpath(where, cwd)) or "").strip()
        dirty = bool((git(cwd, "status", "--porcelain", "--", os.path.relpath(where, cwd)) or "").strip())
        branch = (git(cwd, "branch", "--show-current") or "").strip()
        return raw, {"path": where, "branch": branch, "last_commit": commit or None,
                     "working_copy_uncommitted": dirty}
    ref, path = where.split(":", 1)
    raw = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=cwd, capture_output=True).stdout
    return raw, {"branch": ref, "path": path, "commit": (git(cwd, "rev-parse", ref) or "").strip()}


def _served(slug, outcome):
    raw = git(ROOT, "show", f"HEAD:docs/reviews/{slug}/review.json")
    if not raw:
        return None, None
    for o in json.loads(raw).get("outcomes") or []:
        if o.get("name") == outcome:
            r = o.get("result") or {}
            return {k: r.get(k) for k in ("k", "estimate", "ci_low", "ci_high")}, (r.get("scale") or o.get("estimand"))
    return None, None


def _fmt(r):
    r = r or {}
    if r.get("estimate") is None:
        return f"no pooled estimate (k={r.get('k')})" if r.get("k") else "no pooled estimate"
    ci = f" ({r['ci_low']}–{r['ci_high']})" if r.get("ci_low") is not None else " (CI withheld)"
    return f"{r['estimate']}{ci}, k={r.get('k')}"


def _first_sentence(s, n=170):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    m = re.match(r"(.{20,}?[.;:])\s", s + " ")
    s = m.group(1) if m else s
    return s if len(s) <= n else s[:n - 1] + "…"


def _oc_rules(md_text):
    rules = {}
    for line in md_text.splitlines():
        if line.startswith("|") and " / " in line and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 4:
                rules[cells[0].split(" / ")[0].split("-")[0].lower()] = rules.get(cells[0].split(" / ")[0].split("-")[0].lower(), [])
                rules[cells[0].split(" / ")[0].split("-")[0].lower()].append((cells[0], cells[3]))
    return rules


def collect():
    items, sources = [], []
    for lane, kind, where, cwd in JSON_SOURCES:
        raw, meta = _load_source(kind, where, cwd)
        meta = dict(meta, lane=lane, sha256=_sha(raw))
        sources.append(meta)
        for n in json.loads(raw.decode("utf-8"))["notices"]:
            if ((n.get("reviewer_countersignature") or {}).get("state")) in SIGNED:
                continue
            items.append({"lane": lane, "source": meta, "kind": "notice", "record": n})
    for rel in NR_FILES:
        p = os.path.join(ROOT, rel)
        raw = open(p, "rb").read()
        meta = {"lane": "nr (V1.0.1 regex)", "path": rel, "branch": "nr/v101-regex", "sha256": _sha(raw),
                "last_commit": (git(ROOT, "log", "-1", "--format=%H", "--", rel) or "").strip() or None}
        sources.append(meta)
        data = json.loads(raw.decode("utf-8"))
        for n in (data if isinstance(data, list) else [data]):
            items.append({"lane": meta["lane"], "source": meta, "kind": "notice", "record": n})
    lane, mpath, mdpath, cwd = OC_MOVES
    raw = open(mpath, "rb").read()
    md = open(mdpath, encoding="utf-8").read()
    meta = {"lane": lane, "path": mpath, "branch": (git(cwd, "branch", "--show-current") or "").strip(), "sha256": _sha(raw),
            "notices_md_sha256": _sha(md.encode("utf-8")),
            "last_commit": (git(cwd, "log", "-1", "--format=%H", "--", os.path.relpath(mpath, cwd)) or "").strip() or None}
    sources.append(meta)
    for m in json.loads(raw.decode("utf-8"))["moves"]:
        items.append({"lane": lane, "source": meta, "kind": "oc_move", "record": m})
    return items, sources


def describe(it):
    rec = it["record"]
    slug, outcome = rec["slug"], rec.get("outcome")
    served, served_scale = _served(slug, outcome)
    if it["kind"] == "oc_move":
        res = rec.get("result") or [None, None]
        before = {k: (res[0] or {}).get(k) for k in ("k", "estimate", "ci_low", "ci_high")} if res[0] else None
        after = {k: (res[1] or {}).get(k) for k in ("k", "estimate", "ci_low", "ci_high")} if res[1] else None
        scale = (res[0] or {}).get("scale") or served_scale
        after_label = (res[1] or {}).get("scale")
        if before is None and after is None:
            ab = rec.get("absent") or [[], []]
            add = sorted(set(ab[1]) - set(ab[0])) if len(ab) > 1 else []
            rem = sorted(set(ab[0]) - set(ab[1])) if len(ab) > 1 else []
            plain = (f"No pooled number moves; declared-absent list changes (+{len(add)} / -{len(rem)})"
                     + (f": +{', '.join(add[:3])}" if add else "") + (f" -{', '.join(rem[:3])}" if rem else ""))
        else:
            plain = f"{_fmt(before)} → {_fmt(after)}" + (f" [{after_label}]" if after_label and after_label != scale else "")
        reason = "oc candidate stack (see NOTICES.md for the rule)"
    else:
        before, after = rec.get("before"), rec.get("after")
        scale = served_scale
        reason = _first_sentence(rec.get("reason"))
        plain = f"{_fmt(before)} → {_fmt(after)}"
        if rec.get("served_change"):
            plain += f" ({rec['served_change']})"
    flags = []
    cc = result_changes.conclusion_changed(before or {}, after or {}, scale) if (before or after) else None
    if cc:
        flags.append("CHANGES A CONCLUSION: " + cc)
    return {"slug": slug, "outcome": outcome, "before": before, "after": after, "scale": scale,
            "served_now": served, "plain": plain, "reason": reason, "flags": flags}


def eg_index():
    """{(slug, outcome): (N-id, notice_block_sha256)} from record 24 at HEAD."""
    md = git(ROOT, "show", f"HEAD:{EG_RECORD_24}") or ""
    out = {}
    for m in re.finditer(r"\*\*(N\d+)\s+([^/*]+?)\s+/\s+([^*]+?)\*\*(.*?)(?=\n\*\*N\d+|\n## |\Z)", md, re.S):
        h = re.search(r"hash to sign:\s*`([0-9a-f]{64})`", m.group(4))
        out[(m.group(2).strip(), m.group(3).strip())] = (m.group(1), h.group(1) if h else None)
    return out


def build(out_dir):
    items, sources = collect()
    eg = eg_index()
    rows = []
    for it in items:
        d = describe(it)
        d.update(lane=it["lane"], kind=it["kind"], item_sha256=_sha(canon(it["record"])),
                 source=it["source"].get("path") or it["source"].get("branch"))
        rows.append(d)
    # de-duplicate identical records found in more than one source
    seen, uniq = {}, []
    for r in rows:
        if r["item_sha256"] in seen:
            seen[r["item_sha256"]]["also_in"].append(r["source"])
            continue
        r["also_in"] = []
        seen[r["item_sha256"]] = r
        uniq.append(r)
    rows = uniq

    def same(a, b):
        return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)

    for r in rows:
        if r["served_now"] is not None and r["before"] is not None and not same(r["before"], r["served_now"]):
            chained = [x for x in rows if x is not r and x["slug"] == r["slug"] and x["outcome"] == r["outcome"]
                       and x["after"] is not None and same(x["after"], r["before"])]
            if chained:
                r["flags"].append("CHAINED: its 'before' is the 'after' of item " + chained[0]["item_sha256"][:12])
            else:
                r["flags"].append("STALE: its 'before' (" + _fmt(r["before"]) + ") is not what is served now ("
                                  + _fmt(r["served_now"]) + ")")
    for r in rows:
        if any(f.startswith("STALE") for f in r["flags"]):
            continue
        others = [x for x in rows if x is not r and x["slug"] == r["slug"] and x["outcome"] == r["outcome"]
                  and x["lane"] != r["lane"] and not any(f.startswith("STALE") for f in x["flags"])
                  and not same(x["after"], r["after"])]
        if others:
            r["flags"].append("CONFLICT: " + "; ".join(f"{x['lane']} → {_fmt(x['after'])}" for x in others))
    order = {"oc (V1.0.1 candidate stack)": 0, "evid (acquisition cascade)": 1, "evid (glp1 admission)": 2,
             "evid2 (q-decisions)": 3, "acq": 4, "nr (V1.0.1 regex)": 5, "enforcement-gate (2026-09-21 wave)": 6}
    rows.sort(key=lambda r: (order.get(r["lane"], 9), r["slug"], str(r["outcome"])))
    for r in rows:
        r["notice_id"], r["notice_hash"] = None, None
        if r["lane"].startswith("enforcement-gate"):
            nid, nh = eg.get((r["slug"], r["outcome"]), (None, None))
            r["notice_id"], r["notice_hash"] = nid, nh
            if nid is None:
                r["flags"].append("NOT IN RECORD 24: no established hash to sign; do not sign")
            elif nid in EG_WITHDRAW:
                r["flags"].append(f"WITHDRAWN ({nid}) by the corrected re-derivation: {EG_STATUS_SOURCE}")
            elif nid in EG_REISSUE:
                r["flags"].append(f"RE-ISSUE REQUIRED ({nid}) before signing: {EG_STATUS_SOURCE}")
    blocking = ("STALE", "WITHDRAWN", "RE-ISSUE", "NOT IN RECORD 24")
    for i, r in enumerate(rows, 1):
        r["n"] = i
        r["signable"] = not any(f.startswith(blocking) for f in r["flags"])
    manifest = {"what": "bulk-signing manifest of every pending result-change notice (lane NR, for Mahmood)",
                # the commit that last wrote the served pages (docs/reviews), not the lane's HEAD
                "served_baseline": (git(ROOT, "log", "-1", "--format=%H", "--", "docs/reviews") or "").strip(),
                "built_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sources": sources,
                "superseded_drafts_not_included": SUPERSEDED_DRAFTS,
                "items": [{k: r[k] for k in ("n", "item_sha256", "notice_id", "notice_hash", "lane", "kind", "slug",
                                             "outcome", "before", "after",
                                             "served_now", "plain", "reason", "flags", "signable", "source", "also_in")}
                          for r in rows]}
    raw = canon(manifest)
    msha = _sha(raw)
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "BULK_SIGNING_MANIFEST.json"), "wb").write(raw)
    open(os.path.join(out_dir, "BULK_SIGNING_MANIFEST.sha256"), "w", encoding="utf-8").write(
        f"{msha}  BULK_SIGNING_MANIFEST.json\n")
    open(os.path.join(out_dir, "BULK_SIGNING_PACKET.md"), "w", encoding="utf-8").write(render_md(manifest, msha))
    return manifest, msha


def render_md(m, msha):
    items = m["items"]
    sign = [i for i in items if i["signable"]]
    stale = [i for i in items if not i["signable"]]
    sd = m.get("superseded_drafts_not_included") or {}
    concl = [i for i in sign if any(f.startswith("CHANGES A CONCLUSION") for f in i["flags"])]
    conf = [i for i in sign if any(f.startswith("CONFLICT") for f in i["flags"])]
    L = [f"# Bulk-signing packet: every pending result-change notice",
         "",
         f"**Manifest sha256 (what you sign):** `{msha}`",
         f"- File: `BULK_SIGNING_MANIFEST.json` (canonical JSON; recompute with `sha256sum BULK_SIGNING_MANIFEST.json`).",
         f"- Served baseline these changes are measured against: `{m['served_baseline']}` (the live pages).",
         f"- Built {m['built_utc']} by lane NR. **Nothing here is signed.** A lane never signs for you.",
         "",
         "## How to sign",
         "- You sign the manifest hash yourself, and record how the packet reached you (`how_it_reached_the_reviewer`),",
         "  e.g. 'read BULK_SIGNING_PACKET.md, sha256 …, attached to <channel> on <date>'.",
         f"- **{len(concl)} items change a conclusion.** The harness's countersign tool refuses a batch signature for a",
         "  notice that withdraws or reverses a conclusion (`scripts/countersign_result_change.py sign --batch`). Those",
         "  need their own signature even if you bulk-sign the rest; they are listed first below.",
         f"- **{len(conf)} items CONFLICT** with another lane's pending change to the same outcome. Signing both does not",
         "  certify the value the release captain's integration will produce; that combined value needs its own notice.",
         f"- **{len(stale)} items are NOT signable**: stale (their 'before' is not what is served now), withdrawn or awaiting",
         "  re-issue by the enforcement-gate record's correction. They are listed at the end, outside the signable set.",
         f"- Not included: {sd.get('n')} superseded drafts ({sd.get('why')}; {sd.get('path')}).",
         "- Enforcement-gate items also show `notice_hash`: the established per-notice hash to sign from record 24.",
         "",
         f"## Counts",
         f"- Items: {len(items)} ({len(sign)} signable, {len(stale)} not signable).",
         "- By lane: " + ", ".join(f"{l} {sum(1 for i in items if i['lane'] == l)}"
                                   for l in dict.fromkeys(i["lane"] for i in items)) + ".",
         "",
         "## Sources (each file's own sha256)"]
    for s in m["sources"]:
        L.append(f"- {s['lane']}: `{s.get('path') or ''}` {('branch ' + s['branch']) if s.get('branch') else ''} "
                 f"sha256 `{s['sha256'][:16]}…`" + (f", commit `{(s.get('last_commit') or s.get('commit') or '')[:10]}`"
                                                    if (s.get('last_commit') or s.get('commit')) else "")
                 + (" (working copy has UNCOMMITTED changes)" if s.get("working_copy_uncommitted") else ""))

    def table(title, rows):
        out = ["", f"## {title} ({len(rows)})", "",
               "| # | item sha256 | lane | topic / outcome | change (old → new) | flags |", "|---|---|---|---|---|---|"]
        for i in rows:
            fl = "<br>".join(f.replace("|", "/") for f in i["flags"]) or ""
            nid = f"<br>{i['notice_id']} `{(i['notice_hash'] or '')[:12]}`" if i.get("notice_id") else ""
            out.append(f"| {i['n']} | `{i['item_sha256'][:12]}`{nid} | {i['lane']} | {i['slug']} / {str(i['outcome'])[:60]} | "
                       f"{i['plain'].replace('|', '/')}<br><sub>{i['reason'].replace('|', '/')}</sub> | {fl} |")
        return out

    L += table("Changes a conclusion: sign individually", concl)
    L += table("Other signable items", [i for i in sign if i not in concl])
    L += table("NOT signable: stale, withdrawn or awaiting re-issue", stale)
    L += ["", "Full item hashes are in the manifest JSON (`items[].item_sha256`)."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    m, h = build(sys.argv[1])
    items = m["items"]
    print(f"items {len(items)}; signable {sum(i['signable'] for i in items)}; "
          f"conclusion-changing {sum(1 for i in items if i['signable'] and any(f.startswith('CHANGES') for f in i['flags']))}; "
          f"conflicts {sum(1 for i in items if i['signable'] and any(f.startswith('CONFLICT') for f in i['flags']))}")
    print("manifest sha256", h)
