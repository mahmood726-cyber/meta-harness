"""Build docs/audit/ -- the external audit pack -- from committed files only (pva lane, 2026-10-08).

Everything an outside auditor needs, served from the site or downloadable from the public repository, with no access to
our machines:
  docs/audit/index.html         the auditor's guide: what the harness claims and does NOT claim, how to replay any number,
                                the provenance types, the decisions in force, the open-sources-only policy, known limits
  docs/audit/reviews.html       every served review: URL, ACTIVE / ABANDONED_BY_DECISION, pinned identities, the files
  docs/audit/checklist/<slug>.html   a per-review checklist, pre-filled with that review's own sample rows and commands
  docs/audit/sample.html        a random sample of extraction rows (seed fixed below, committed before the draw), each
                                linked to its row on the page and to its source record
  docs/audit/findings_template.md    the form an auditor files findings on
  docs/audit/audit_pack.json    the same content, machine-readable

No pooled statistic is written here (harness/leakscan forbids publishing one for a suppressed-state topic, and an
audit pack is not a results surface): per-row extracted values only, each with its passage and digest.

  python scripts/build_audit_pack.py            write docs/audit/
  python scripts/build_audit_pack.py --check    exit 1 if docs/audit/ differs from a fresh build
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import review_tabs as T  # noqa: E402

SITE = "https://mahmood726-cyber.github.io/meta-harness/"
REPO = "https://github.com/mahmood726-cyber/meta-harness"
# PRE-REGISTERED SAMPLE (fixed before any draw; changing either is a new sample and must be named as one)
SAMPLE_SEED = 20261008
SAMPLE_N = 40
SCREEN_PER_REVIEW = 5
OUT = ROOT / "docs" / "audit"


def e(x) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def reviews() -> list[dict]:
    out = []
    for d in sorted((ROOT / "docs" / "reviews").iterdir()):
        if not (d / "review.json").is_file():
            continue
        r, m = j(d / "review.json"), j(d / "manifest.json")
        st = T.topic_status(d.name)
        out.append({"slug": d.name, "title": r.get("title"), "question": r.get("question"), "status": st["state"],
                    "status_reason": st.get("reason"), "review_sha256": m.get("review_sha256"), "html_sha256": m.get("html_sha256"),
                    "protocol_sha": (r.get("protocol") or {}).get("sha"), "page": f"{SITE}reviews/{d.name}/index.html",
                    "files": {f: f"{SITE}reviews/{d.name}/{f}" for f in sorted(p.name for p in d.iterdir() if p.is_file())},
                    "_r": r})
    return out


def extraction_population(revs) -> list[dict]:
    pop = []
    for v in revs:
        for x in T.extraction_rows(v["_r"]):
            pop.append({"slug": v["slug"], **x, "row_url": f"{v['page']}#{x['anchor']}",
                        "pmid": T._ids({"id": x["id"], "label": x["trial"]})[0]})
    return pop


def screening_sample(v) -> list[dict]:
    recs = [x for x in ((v["_r"].get("screening") or {}).get("records") or []) if x.get("id")]
    rng = random.Random(f"{SAMPLE_SEED}:{v['slug']}")
    pick = sorted(rng.sample(range(len(recs)), min(SCREEN_PER_REVIEW, len(recs))))
    return [{"id": recs[i].get("id"), "decision": recs[i].get("decision"), "rule_id": recs[i].get("rule_id"),
             "reason": recs[i].get("reason"), "span": (recs[i].get("span") or recs[i].get("evidence") or "")} for i in pick]


CSS = ("body{font:15px/1.55 system-ui,Segoe UI,Arial,sans-serif;max-width:1040px;margin:0 auto;padding:20px;color:#12232e;"
       "background:#fff}h1{font-size:22px}h2{font-size:18px;margin-top:28px}table{border-collapse:collapse;width:100%;"
       "margin:10px 0}th,td{border:1px solid #c9d4dc;padding:5px 8px;font-size:13px;text-align:left;vertical-align:top}"
       "th{background:#eef2f5}code{font-size:12px}blockquote{margin:4px 0;padding:4px 8px;border-left:3px solid #6b8396;"
       "background:#f5f8fa}.st-a{color:#7a1f14;font-weight:600}.st-ok{color:#1b4d2c;font-weight:600}.muted{color:#4a5b66}"
       "a{color:#0b5394}")


def page(title, body) -> str:
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,"
            f"initial-scale=1'><title>{e(title)}</title><style>{CSS}</style></head><body><p><a href='index.html'>Audit "
            f"pack</a> &middot; <a href='../index.html'>All reviews</a></p><h1>{e(title)}</h1>{body}</body></html>\n")


def decisions_html() -> str:
    reg = j(ROOT / "registry" / "g1_decisions.json")
    rows = "".join(f"<tr><td><code>{e(d.get('id'))}</code></td><td>{e(d.get('decided'))}</td><td>{e(d.get('by'))}</td>"
                   f"<td>{e(d.get('rule'))}</td><td>{e(d.get('applied_in'))}</td></tr>" for d in reg["decisions"])
    return (f"<p>{e(reg.get('rule'))}</p><table><tr><th>Decision</th><th>Decided</th><th>By</th><th>Rule</th>"
            f"<th>Applied in</th></tr>{rows}</table>")


def policy_html() -> str:
    reg = {d["id"]: d for d in j(ROOT / "registry" / "g1_decisions.json")["decisions"]}
    out = []
    for k in sorted(reg):
        if k.startswith(("D8", "D9")):
            out.append(f"<p><strong><code>{e(k)}</code></strong>: {e(reg[k].get('rule'))}<br><em>Enforcement as recorded "
                       f"with the decision:</em> {e(reg[k].get('applied_in'))}</p>")
    return "".join(out)


def provenance_counts(pop) -> dict:
    c = {}
    for x in pop:
        c[x["class"]] = c.get(x["class"], 0) + 1
    return dict(sorted(c.items()))


def guide(revs, pop) -> str:
    n_ab = sum(1 for v in revs if v["status"] == "ABANDONED_BY_DECISION")
    counts = provenance_counts(pop)
    cnt = "".join(f"<tr><td><strong>{e(k)}</strong></td><td>{v}</td></tr>" for k, v in counts.items())
    return page("External audit pack: auditor's guide", f"""
<p>This pack lets you audit the {len(revs)} served reviews of the meta-harness without access to our machines. Everything
it refers to is either served on this site or in the public repository <a href='{REPO}'>{REPO}</a>. It is generated by
<code>scripts/build_audit_pack.py</code> from committed files; nothing in it is typed by hand except this prose.</p>
<ul>
<li><a href='reviews.html'>The {len(revs)} reviews</a> ({len(revs) - n_ab} active, {n_ab} abandoned by decision), with pinned identities.</li>
<li><a href='sample.html'>Extraction spot-check sample</a> ({min(SAMPLE_N, len(pop))} rows drawn at seed {SAMPLE_SEED} from the {len(pop)} extracted trial rows shown on the pages' Data extraction tabs).</li>
<li>Per-review checklists: <code>checklist/&lt;slug&gt;.html</code>, linked from the review list.</li>
<li><a href='findings_template.md'>Findings template</a> &middot; <a href='audit_pack.json'>audit_pack.json</a> (all of the above, machine-readable).</li>
</ul>

<h2 id='claims'>What the harness claims, and what it does not</h2>
<p><strong>Claimed.</strong> Every served pooled number is computed by committed code from committed inputs, and every
extracted trial number shown on a page's Data extraction tab carries the passage it was read from. Each review page names a certificate (<code>CERTIFICATE.json</code>) whose digests
cover the protocol, the search record, the screening ledger, the extraction objects, the analysis code and the rendered
review; <code>scripts/reproduce_review.py &lt;slug&gt;</code> rebuilds the review offline from the committed cache and fails
if any digest or the served page differs. Changes to a served result are published as notices, each countersigned on the
exact bytes shown (Changes &amp; signatures tab).</p>
<p><strong>Not claimed.</strong> Replay proves the same inputs give the same outputs; it does not prove the inputs are right,
that the search found every eligible trial, or that a fresh search today would return the same records. Agreement with a
published meta-analysis (the G1 panel) is a comparison, not independent corroboration. Risk-of-bias judgements are the
rule-based ratings; the recorded dual-model sign-off required by decision D11 is not yet applied (each page says so). A
topic marked ABANDONED_BY_DECISION stays served but is not counted as matched. Each page's Overview lists its own stated
limitations.</p>

<h2 id='replay'>How to replay any number</h2>
<ol>
<li>Open the review page, tab <em>Data extraction</em>. Each extracted trial number shows its source passage and
<code>sha256</code> of that passage (UTF-8), and the outcome's served state (pooled, single trial, refused). Recompute the
digest from the passage; compare the passage with the source record (the PMID links to PubMed; registry ids link to
ClinicalTrials.gov or ISRCTN). Outcomes the gate withholds (incomplete harm ledgers, suppressed pools) are named with the
reason instead of rows.</li>
<li>For the pooled result: <pre>git clone {REPO}.git &amp;&amp; cd meta-harness
python -m pip install --require-hashes -r docs/offline/requirements.lock
python scripts/reproduce_review.py &lt;slug&gt;</pre> The replay compares <code>review_sha256</code> (listed per review in
<a href='reviews.html'>reviews.html</a>) and the served page bytes (<code>html_sha256</code> in each review's
<code>manifest.json</code>).</li>
<li>To check a certificate without our code: <code>python docs/scripts/audit_certificate_stdlib.py</code> (standard library only).</li>
<li>Cite <code>review_sha256</code> in every finding: the page you audited is identified by it, not by its URL.</li>
</ol>

<h2 id='provenance'>Provenance types</h2>
<p>Every extracted row carries a recorded <code>provenance</code> value (where the value was read: <code>abstract</code>,
<code>ctgov_results</code>, <code>fulltext_verified</code>, ...) and a provenance class computed by the gate
(<code>harness/provenance_class.py</code>, the same function the page uses):</p>
<table><tr><th>Class</th><th>Rows shown on the pages</th></tr>{cnt}</table>
<p><strong>EXTRACTOR</strong>: a deterministic regex or typed extractor over a held source, with the span it read.
<strong>RECORDED_MODEL_CALL</strong>: a recorded model call that replays offline; its record id (<code>mc-&lt;32 hex&gt;</code>) is
in the repository and linked from the row. <strong>HAND_ENTERED</strong>: entered outside the harness and bound to a held
span; allowed only while listed in <code>registry/provenance_hand_entered.json</code>, a list that may only shrink.
<strong>UNTRACED</strong>: refused by the gate (none should appear on a served page).</p>

<h2 id='decisions'>Decisions in force</h2>{decisions_html()}

<h2 id='open-sources'>Open sources only</h2>{policy_html()}

<h2 id='limits'>Known limitations</h2>
<p>Each review lists its own limitations (Overview tab, <em>Stated limitations</em>); the per-review checklist links them.
Across the corpus, the index page states the selection effect (which pre-registered topics were built) and the honest
split of what the external audits found. Topics registered but never served are listed in <a href='reviews.html#unserved'>reviews.html</a>.</p>
""")


def unserved() -> list[dict]:
    served = {d.name for d in (ROOT / "docs" / "reviews").iterdir() if (d / "review.json").is_file()}
    return [{"slug": p.stem} for p in sorted((ROOT / "topics").glob("*.json")) if p.stem not in served]


def reviews_page(revs) -> str:
    rows = []
    for v in revs:
        cls = "st-a" if v["status"] == "ABANDONED_BY_DECISION" else "st-ok"
        rows.append(f"<tr><td><a href='{e(v['page'])}'>{e(v['title'])}</a><br><code>{e(v['slug'])}</code></td>"
                    f"<td class='{cls}'>{e(v['status'])}" + (f"<br><span class='muted'>{e(v['status_reason'])}</span>" if v.get('status_reason') else "")
                    + f"</td><td><code>{e(v['review_sha256'])}</code></td><td><a href='checklist/{e(v['slug'])}.html'>checklist</a> &middot; "
                    f"<a href='{e(v['files'].get('CERTIFICATE.json', ''))}'>certificate</a> &middot; <a href='{e(v['files'].get('review.json', ''))}'>review.json</a>"
                    + (f" &middot; <a href='{e(v['files']['BUNDLE.json'])}'>bundle</a>" if "BUNDLE.json" in v["files"] else "") + "</td></tr>")
    un = "".join(f"<li><code>{e(u['slug'])}</code> (<a href='{REPO}/blob/main/topics/{e(u['slug'])}.json'>topic file</a>)</li>" for u in unserved())
    return page("The served reviews", "<p>Each review's pinned identity is its <code>review_sha256</code>. Status is read from "
                f"<code>registry/g1_abandoned.json</code>.</p><table><tr><th>Review</th><th>Status</th><th>review_sha256</th>"
                f"<th>Audit</th></tr>{''.join(rows)}</table><h2 id='unserved'>Registered but never served</h2><p>These topic "
                "files were registered and never produced a served page; the repository history records each decline.</p>"
                f"<ul>{un}</ul>")


CHECKS = [
    ("Protocol adherence", "Protocol tab: the registered PICO and eligibility; any dated amendment; decisions in force. "
                           "Check the Screening and Included-studies tabs apply the same P/I/C/design."),
    ("Search reproducibility", "Search tab: databases, the exact queries, the run date and counts. Re-run a query at the "
                               "source and compare; a different count today is expected (living search) -- the page states the snapshot."),
    ("Screening sample", "For the sampled records below, read the record at its source and judge the decision and rule."),
    ("Extraction spot-checks", "For the sampled rows below, compare the passage with the source record and recompute its sha256."),
    ("Analysis replay", "Run the replay command; it must reproduce review_sha256 below and the served page bytes."),
    ("Risk of bias / GRADE", "Risk of bias &amp; GRADE tab: the rule-based ratings and their inputs; D11 sign-off status."),
    ("Comparator comparison", "Comparison tab and the G1 row on /g1/: matched trials, named differences, open gaps."),
]


def checklist(v, rows) -> str:
    items = "".join(f"<tr><td>{i + 1}</td><td><strong>{n}</strong></td><td>{d}</td><td>&#9744; pass &#9744; finding</td></tr>"
                    for i, (n, d) in enumerate(CHECKS))
    scr = "".join(f"<tr><td><code>{e(s['id'])}</code></td><td>{e(s['decision'])}</td><td>{e(s['rule_id'])}</td>"
                  f"<td>{e(s['reason'])}</td></tr>" for s in screening_sample(v))
    ext = "".join(f"<tr><td><a href='{e(x['row_url'])}'>{e(x['outcome'])} / {e(x['trial'])}</a></td><td>{x['value']}</td>"
                  f"<td>{e(x['class'])}</td><td><code>{e(x['passage_sha256'])}</code></td></tr>" for x in rows[:8])
    return page(f"Audit checklist: {v['title']}", f"""
<p>Review page: <a href='{e(v['page'])}'>{e(v['page'])}</a>. Status: <strong>{e(v['status'])}</strong>.
Pinned identity <code>review_sha256 {e(v['review_sha256'])}</code>; served page <code>html_sha256 {e(v['html_sha256'])}</code>;
protocol commit <code>{e(v['protocol_sha'])}</code>.</p>
<pre>python scripts/reproduce_review.py {e(v['slug'])}</pre>
<table><tr><th>#</th><th>Check</th><th>What to do</th><th>Result</th></tr>{items}</table>
<h2>Screening sample (seed {SAMPLE_SEED}:{e(v['slug'])}, {SCREEN_PER_REVIEW} records)</h2>
<table><tr><th>Record</th><th>Decision</th><th>Rule</th><th>Reason given</th></tr>{scr}</table>
<h2>Extraction rows of this review ({"first 8 of " + str(len(rows)) if len(rows) > 8 else "all " + str(len(rows))}; every row is on the page's Data extraction tab)</h2>
<table><tr><th>Outcome / trial</th><th>Value</th><th>Class</th><th>Passage sha256</th></tr>{ext}</table>
""")


def sample_page(sample, pop_n) -> str:
    rows = "".join(
        f"<tr><td>{i + 1}</td><td><code>{e(x['slug'])}</code><br><a href='{e(x['row_url'])}'>{e(x['outcome'])} / {e(x['trial'])}</a>"
        + (f"<br><a href='https://pubmed.ncbi.nlm.nih.gov/{e(x['pmid'])}/'>PMID {e(x['pmid'])}</a>" if x.get("pmid") else "")
        + f"</td><td>{x['value']}</td><td>{e(x['provenance'])}<br><strong>{e(x['class'])}</strong></td>"
        f"<td><blockquote>{e(x['passage'])}</blockquote><code>sha256 {e(x['passage_sha256'])}</code></td></tr>"
        for i, x in enumerate(sample))
    return page("Extraction spot-check sample", f"""
<p>{len(sample)} rows drawn without replacement from the {pop_n} pooled rows shown on the review pages, with
<code>random.Random({SAMPLE_SEED}).sample</code> over the rows sorted by (slug, row anchor). The seed and size were fixed in
<code>scripts/build_audit_pack.py</code> before the draw. For each row: open its link (the row on the page), compare the
passage with the source, and recompute the digest:
<code>python -c "import hashlib,sys;print(hashlib.sha256(sys.argv[1].encode()).hexdigest())" "&lt;passage&gt;"</code>.</p>
<table><tr><th>#</th><th>Row</th><th>Value</th><th>Provenance</th><th>Passage + digest</th></tr>{rows}</table>
""")


TEMPLATE = """# Audit finding

One finding per file (or per table row). Fill every field; a finding without a pinned identity cannot be checked.

| field | value |
|---|---|
| finding id | AUD-<your initials>-<nnn> |
| auditor | |
| date audited (UTC) | |
| review slug | |
| review_sha256 audited | (from the page header or docs/audit/reviews.html) |
| tab and element | e.g. Data extraction / row x0-2 |
| what the page states (verbatim) | |
| what the source states (verbatim, with link) | |
| defect class | C1 held text vs "absent" / C2 effect measure / C3 endpoint relation / C4 population / C5 report-family-version / C6 comparator record / C7 auditor identity / C8 metadata link / other |
| severity | changes a served number / changes served wording / record only |
| how to reproduce | commands or clicks |
| suggested fix (optional) | |
"""


def build() -> dict[str, str]:
    revs = reviews()
    pop = sorted(extraction_population(revs), key=lambda x: (x["slug"], x["anchor"]))
    sample = random.Random(SAMPLE_SEED).sample(pop, min(SAMPLE_N, len(pop)))
    sample.sort(key=lambda x: (x["slug"], x["anchor"]))
    files = {"index.html": guide(revs, pop), "reviews.html": reviews_page(revs), "sample.html": sample_page(sample, len(pop)),
             "findings_template.md": TEMPLATE}
    for v in revs:
        files[f"checklist/{v['slug']}.html"] = checklist(v, [x for x in pop if x["slug"] == v["slug"]])
    pack = {"generator": "scripts/build_audit_pack.py", "sample_seed": SAMPLE_SEED, "sample_n": SAMPLE_N,
            "reviews": [{k: v[k] for k in v if not k.startswith("_")} for v in revs], "unserved": unserved(),
            "extraction_population_n": len(pop), "provenance_class_counts": provenance_counts(pop),
            "sample": [{k: x[k] for k in ("slug", "outcome", "trial", "pmid", "value", "provenance", "class", "passage",
                                          "passage_sha256", "row_url")} for x in sample],
            "screening_samples": {v["slug"]: screening_sample(v) for v in revs}}
    files["audit_pack.json"] = json.dumps(pack, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    files = build()
    if a.check:
        bad = [k for k, v in files.items() if not (OUT / k).is_file() or (OUT / k).read_text(encoding="utf-8") != v]
        extra = [p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.relative_to(OUT).as_posix() not in files]
        for k in bad + extra:
            print("STALE docs/audit/" + k)
        return 1 if bad or extra else 0
    for k, v in files.items():
        p = OUT / k
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(v, encoding="utf-8", newline="\n")
    print(f"wrote {len(files)} files to docs/audit/ ({hashlib.sha256(files['audit_pack.json'].encode()).hexdigest()[:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
