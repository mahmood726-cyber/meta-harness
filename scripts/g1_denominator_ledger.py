"""THE G1 DENOMINATOR LEDGER: every comparator row that left the pinned baseline (main 6efd9c00, 367 rows) and every row
that joined it, as a TYPED record with a rule ID and a verbatim source span, so the drop in N can be audited from the
artefact itself (dispatch 2026-10-04: a shrinking denominator is how a match score flatters itself).

    python scripts/g1_denominator_ledger.py          -> outputs/k_gap/G1_DENOMINATOR.json
    python scripts/g1_denominator_ledger.py --check  -> exit 1 on any removal without rule + a span found in its source

Kinds (removed): NOT_A_TRIAL (a comparator table row that names no study: a subgroup row of another study's line),
DUPLICATE_UNIT (one trial listed in two of the comparator's tables), OTHER_AGENT (the trial's registered arms name another
agent), RELABELLED (the same trial, now labelled by the comparator's own table), NOT_IN_COMPARATOR_TABLE (a unit the
older reference-title enumeration listed that the comparator's own trial table does not contain), COMPARATOR_RETIRED (a row
of a comparator REPLACED for the topic: registry/comparator_selection/<slug>.adoption.json names the retired comparator, its
reason code and spans verbatim in its held source). Anything else is
UNEXPLAINED and fails --check. Spans are copied VERBATIM from the cited held file (sha256 recorded); the check re-reads
the file and finds the span (whitespace-insensitive, as the files differ only in line breaks).
"""
from __future__ import annotations

import glob
import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "k_gap")
BASE = os.path.join(ROOT, "docs", "evidence", "g1-denominator", "baseline-6efd9c00.json")
LEDGER = os.path.join(OUT, "G1_DENOMINATOR.json")
EVID = os.path.join(ROOT, "docs", "evidence", "g1-denominator")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _squash(t):
    return re.sub(r"\s+", "", html.unescape(t or ""))


def _source_text(path):
    """The comparable text of a held source: markup sources (.xml/.html) tag-stripped and unescaped; plain text as is."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    if path.lower().endswith((".xml", ".html", ".htm")):
        raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return raw


def find_span(path, needle):
    """The VERBATIM substring of the file at `path` that equals `needle` up to whitespace, or None."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    target = _squash(needle)
    if not target:
        return None
    # map squashed positions back to raw positions
    idx, keep = [], []
    for i, ch in enumerate(raw):
        if not ch.isspace():
            idx.append(i)
            keep.append(ch)
    hay = "".join(keep)
    k = hay.find(target)
    if k < 0:
        return None
    return raw[idx[k]: idx[k + len(target) - 1] + 1]


def comparator_sources(cpmid):
    d = os.path.join(ROOT, "cache", "comparators", str(cpmid))
    return sorted(p for p in glob.glob(os.path.join(d, "*")) if p.endswith((".txt", ".xml")))


def span_in_sources(cpmid, needle):
    for p in comparator_sources(cpmid):
        v = find_span(p, needle)
        if v:
            return {"text": v, "source": os.path.relpath(p, ROOT).replace(os.sep, "/"), "source_sha256": _sha(p)}
    return None


TITLES = os.path.join(OUT, "pubmed_titles.json")
CHAIN = os.path.join(OUT, "identity_chain.json")


def chain_other_agent_span(slug, label, other_agent_units):
    """An OTHER_AGENT removal decided by k-gap's IDENTITY CHAIN (not by AACT interventions): the tracker lists the unit
    among its other-agent units, the chain's result for it is scoped OTHER_AGENT:<agent>, and one of the trial's OWN
    self-naming reports has a held PubMed title that names that agent -- quoted verbatim from outputs/k_gap/
    pubmed_titles.json. None when any link is missing (the removal then stays unexplained: fail-closed)."""
    if label not in (other_agent_units or []) or not (os.path.exists(CHAIN) and os.path.exists(TITLES)):
        return None, None
    r = ((_j(CHAIN).get("results") or {}).get(f"{slug}::{label}") or {})
    scope = str(r.get("scope") or "")
    if not scope.startswith("OTHER_AGENT:"):
        return None, None
    agent = scope.split(":", 1)[1].strip().lower()
    titles = _j(TITLES)
    for pm in r.get("self_naming_pmids") or []:
        t = titles.get(str(pm)) or ""
        if agent and agent in t.lower():
            v = find_span(TITLES, t)
            if v:
                return ({"text": v, "source": os.path.relpath(TITLES, ROOT).replace(os.sep, "/"),
                         "source_sha256": _sha(TITLES), "pmid": str(pm)},
                        {"agent": agent, "ncts": r.get("ncts"), "chain_state": r.get("state"), "chain_basis": r.get("basis")})
    return None, None


def chain_registry_span(slug, label, other_agent_units):
    """An OTHER_AGENT removal decided by k-gap's identity chain from the trial's REGISTERED interventions (chain basis
    ...REGISTERED_INTERVENTIONS; dapagliflozin SOLOIST-WHF NCT03521934, SCORED NCT03315143): the tracker lists the
    unit among its other-agent units, the chain scopes it OTHER_AGENT:<agent> on one NCT, and the committed AACT
    interventions extract for that NCT (docs/evidence/g1-denominator/aact_interventions_<nct>.txt, snapshot digest in its
    header) names that agent. None when any link is missing (fail-closed)."""
    if label not in (other_agent_units or []) or not os.path.exists(CHAIN):
        return None, None
    r = ((_j(CHAIN).get("results") or {}).get(f"{slug}::{label}") or {})
    scope, nct = str(r.get("scope") or ""), str(r.get("nct") or "")
    if not scope.startswith("OTHER_AGENT:") or not nct.startswith("NCT") or "REGISTERED_INTERVENTIONS" not in str(r.get("basis")):
        return None, None
    agent = scope.split(":", 1)[1].strip().lower()
    ev = os.path.join(EVID, f"aact_interventions_{nct}.txt")
    if not os.path.exists(ev):
        return None, None
    lines = [l for l in open(ev, encoding="utf-8").read().splitlines() if f"|{nct}|" in l]
    if not agent or not any(agent in l.lower() for l in lines):
        return None, None
    return ({"text": "\n".join(lines), "source": os.path.relpath(ev, ROOT).replace(os.sep, "/"), "source_sha256": _sha(ev)},
            {"agent": agent, "nct": nct, "chain_state": r.get("state"), "chain_basis": r.get("basis")})


ADOPT = os.path.join(ROOT, "registry", "comparator_selection", "{slug}.adoption.json")
ENUM = os.path.join(ROOT, "registry", "comparator_enumerations", "{slug}.json")


LICENCES = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "licences.json")


def _is_open_licence(lic):
    """CC BY (any version, no NC/ND/SA qualifier), CC0 or public domain -- the licences rule criterion C1 accepts. Normalised
    so 'CC BY 4.0' / 'cc-by-4.0' / 'CC0 1.0' are open (codex v9-apply-r8 #1); 'cc by-nc' is not."""
    import re
    s = re.sub(r"[\s_-]+", " ", str(lic or "").lower()).strip()
    return bool(re.fullmatch(r"cc by( \d+(\.\d+)?)?|cc ?0( \d+(\.\d+)?)?|cc zero|public domain|pd", s))


def _licence_entry(pmid):
    """The recorded licence probe's entry for a PMID ({license, open, pmcid, state}), or None."""
    if not os.path.exists(LICENCES):
        return None
    return _j(LICENCES).get(str(pmid))


def _licence_retirement(r, a):
    """V9-03: a comparator retired ONLY for its licence (R0 C1_OPEN_LICENCE) has no open text to quote -- that is the
    reason it was retired. Its span is the recorded licence probe's VERBATIM entry for the retired PMID
    (outputs/k_gap/g1_binding/licences.json, sha256 recorded), which must say LOOKED_UP, not open, and carry no CC BY /
    CC0 licence. Anything else: None (the removal then stays a ledger problem)."""
    import re
    pmid = str(r.get("comparator_pmid") or "")
    e = _licence_entry(pmid)
    # a complete probe only: 'open' explicitly false and the 'license' field present (codex v9-apply-r7 #2 -- missing
    # fields are unknown status, not a closed licence)
    if not e or e.get("state") != "LOOKED_UP" or e.get("open") is not False or "license" not in e \
            or _is_open_licence(e.get("license")):
        return None
    raw = open(LICENCES, encoding="utf-8").read()
    m = re.search(r'"' + re.escape(pmid) + r'"\s*:\s*\{[^{}]*\}', raw)     # any JSON spacing (codex v9-apply-r9 #2)
    if not m:
        return None
    return {"retired_pmid": pmid, "reason_code": r["reason_code"], "new_pmid": a["comparator_pmid"],
            "span": {"text": m.group(0), "parts": [m.group(0)],
                     "source": os.path.relpath(LICENCES, ROOT).replace(os.sep, "/"), "source_sha256": _sha(LICENCES)}}


def retired_comparator(slug, cur_pmid):
    """A COMPARATOR REPLACEMENT recorded for this topic (registry/comparator_selection/<slug>.adoption.json): the topic's
    current comparator is the adopted one, and the old one is retired with a reason code and spans copied VERBATIM from
    the old comparator's held source (sha256 recorded). None when there is no adoption, or it is for another comparator."""
    p = ADOPT.format(slug=slug)
    if not os.path.exists(p):
        return None
    a = _j(p)
    if str(a.get("comparator_pmid")) != str(cur_pmid) or not a.get("retired"):
        return None
    r = a["retired"]
    if not r.get("spans") and str(r.get("reason_code") or "").startswith("R0:C1_OPEN_LICENCE"):
        return _licence_retirement(r, a)
    src = os.path.join(ROOT, (r.get("source") or {}).get("path") or "")
    if not os.path.isfile(src) or _sha(src) != r["source"].get("sha256"):
        return None
    if src.lower().endswith((".xml", ".html", ".htm")):
        hay = _squash(_source_text(src))
        spans = [t if _squash(t) in hay else None for t in r.get("spans") or []]
    else:
        spans = [find_span(src, t) for t in r.get("spans") or []]
    if not spans or not all(spans):
        return None
    return {"retired_pmid": r["comparator_pmid"], "reason_code": r["reason_code"], "new_pmid": a["comparator_pmid"],
            "span": {"text": " | ".join(spans), "parts": spans, "source": os.path.relpath(src, ROOT).replace(os.sep, "/"),
                     "source_sha256": _sha(src)}}


def enumeration_span(slug, label):
    """The added row's own span from the typed enumeration input (verbatim, whitespace-insensitive, in its held source)."""
    p = ENUM.format(slug=slug)
    if not os.path.exists(p):
        return None
    e = _j(p)
    u = next((u for u in e.get("units") or [] if u.get("label") == label), None)
    src = os.path.join(ROOT, (e.get("source") or {}).get("path") or "")
    if not u or not os.path.isfile(src):
        return None
    raw = open(src, encoding="utf-8", errors="replace").read()
    if src.lower().endswith((".xml", ".html", ".htm")):
        raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    if _squash(u["span"]) not in _squash(raw):
        return None
    return {"text": u["span"], "ref": u.get("ref"), "pmid": u.get("pmid"),
            "source": os.path.relpath(src, ROOT).replace(os.sep, "/"), "source_sha256": _sha(src)}


def current_rows():
    out = {}
    for p in sorted(glob.glob(os.path.join(OUT, "g1", "*.json"))):
        d = _j(p)
        out[d["slug"]] = d
    return out


def build():
    base = _j(BASE)
    cur = current_rows()
    T = _j(os.path.join(OUT, "k_gap_table.json"))
    topics = {t["slug"]: t for t in T["topics"]}
    units = {(t["slug"], t["label"]): t for t in T["trials"]}
    removed, added = [], []
    for slug, b in sorted(base["topics"].items()):
        d = cur.get(slug) or {}
        now = {t["label"]: t for t in d.get("trials") or []}
        cpmid = d.get("comparator_pmid")
        top = topics.get(slug) or {}
        nat = {u["label"]: u for u in top.get("not_a_trial_units") or []}
        old_rows = b["rows"]
        gone = [l for l in old_rows if l not in now]
        new = [l for l in now if l not in old_rows]
        ret = retired_comparator(slug, cpmid) if gone else None
        for lab in gone:
            u = units.get((slug, lab)) or {}
            rec = {"slug": slug, "label": lab, "comparator_pmid": cpmid}
            if ret:
                rec.update(kind="COMPARATOR_RETIRED", rule_id="COMPARATOR_RETIRED:" + ret["reason_code"],
                           retired_comparator_pmid=ret["retired_pmid"], replaced_by=ret["new_pmid"],
                           detail=(f"a row of the retired comparator {ret['retired_pmid']} ({ret['reason_code']}); the topic's "
                                   f"comparator is now {ret['new_pmid']} (registry/comparator_selection/{slug}.adoption.json)"),
                           span=ret["span"])
            elif lab in nat:
                rec.update(kind="NOT_A_TRIAL", rule_id="K-GAP:NOT_A_TRIAL:" + nat[lab]["why"],
                           detail=f"a row of the comparator's {nat[lab]['table']} that names no study (a subgroup row "
                                  "of another study's line, with its group size)", span=span_in_sources(cpmid, lab))
                if rec["span"]:
                    raw = open(os.path.join(ROOT, rec["span"]["source"]), encoding="utf-8", errors="replace").read()
                    i = raw.find(rec["span"]["text"])
                    rec["span"]["context_before"] = " ".join(raw[max(0, i - 400):i].split())[-300:]
            elif u.get("status") == "DUPLICATE_UNIT":
                rec.update(kind="DUPLICATE_UNIT", rule_id="K-GAP:DUPLICATE_UNIT:SAME_IDENTITY_SAME_FIRST_AUTHOR",
                           duplicate_of=u.get("duplicate_of"), identity={"pmids": u.get("pmids"), "ncts": u.get("ncts")},
                           detail="the same trial listed in two of the comparator's tables; counted once",
                           span=span_in_sources(cpmid, lab),
                           span_duplicate_of=span_in_sources(cpmid, u.get("duplicate_of") or ""))
            elif u.get("drug") == "OTHER_AGENT" and u.get("ncts"):
                ev = os.path.join(EVID, f"aact_interventions_{u['ncts'][0]}.txt")
                sp = None
                if os.path.exists(ev):
                    lines = [l for l in open(ev, encoding="utf-8").read().splitlines() if f"|{u['ncts'][0]}|" in l]
                    if lines:
                        sp = {"text": "\n".join(lines), "source": os.path.relpath(ev, ROOT).replace(os.sep, "/"),
                              "source_sha256": _sha(ev)}
                rec.update(kind="OTHER_AGENT", rule_id="K-GAP:OTHER_AGENT:REGISTRY_INTERVENTIONS",
                           identity={"pmids": (u.get("pmids") or [])[:3], "ncts": u.get("ncts")},
                           detail="the trial's registered arms (AACT) name another agent than the topic's", span=sp)
            elif chain_other_agent_span(slug, lab, d.get("other_agent_units"))[0]:
                sp, ev = chain_other_agent_span(slug, lab, d.get("other_agent_units"))
                rec.update(kind="OTHER_AGENT", rule_id="K-GAP:OTHER_AGENT:IDENTITY_CHAIN",
                           identity={"ncts": ev.get("ncts"), "chain": f"{ev.get('chain_state')}:{ev.get('chain_basis')}"},
                           detail=(f"k-gap's identity chain scopes the trial OTHER_AGENT:{ev['agent']} (its own reports "
                                   f"name {ev['agent']}, not the topic's agent); the span is a held PubMed title of one of "
                                   f"those reports (PMID {sp['pmid']})"), span=sp)
            elif chain_registry_span(slug, lab, d.get("other_agent_units"))[0]:
                sp, ev = chain_registry_span(slug, lab, d.get("other_agent_units"))
                rec.update(kind="OTHER_AGENT", rule_id="K-GAP:OTHER_AGENT:IDENTITY_CHAIN_REGISTRY",
                           identity={"ncts": [ev["nct"]], "chain": f"{ev.get('chain_state')}:{ev.get('chain_basis')}"},
                           detail=(f"k-gap's identity chain scopes the trial OTHER_AGENT:{ev['agent']} from its REGISTERED "
                                   f"interventions; the span is the committed AACT interventions extract for {ev['nct']}"),
                           span=sp)
            else:
                fam = (b.get("families") or {}).get(lab)
                match = next((nl for nl in new if fam and (now[nl].get("family") == fam)), None)
                if match:
                    rec.update(kind="RELABELLED", rule_id="K-GAP:ENUMERATION:COMPARATOR_TABLE_LABEL", now_label=match,
                               identity={"family": fam},
                               detail="the same trial (same family), now labelled as the comparator's own trial table "
                                      "labels it", span=span_in_sources(cpmid, match))
                elif top.get("comparator_set_state") == "TABLE_ENUMERATED":
                    table_rows = [t["label"] for t in T["trials"] if t["slug"] == slug]
                    rec.update(kind="NOT_IN_COMPARATOR_TABLE", rule_id="K-GAP:ENUMERATION:COMPARATOR_TABLE",
                               identity={"family": fam},
                               detail="an older reference-title unit; the comparator's own included-studies table "
                                      f"({', '.join(top.get('tables_used') or [])}) lists the {len(table_rows)} rows "
                                      "quoted here, and this trial is not one of them",
                               span={"rows": [span_in_sources(cpmid, l) for l in table_rows]})
                else:
                    rec.update(kind="UNEXPLAINED", rule_id=None, span=None)
            removed.append(rec)
        for lab in new:
            if any(r.get("now_label") == lab for r in removed if r["slug"] == slug):     # a relabel, not an addition
                continue
            es = enumeration_span(slug, lab)
            added.append({"slug": slug, "label": lab, "comparator_pmid": cpmid,
                          "basis": ("a unit of the comparator's typed enumeration (registry/comparator_enumerations)" if es
                                    else "a row of the comparator's own trial table"),
                          "span": es or span_in_sources(cpmid, lab)})
    n_now = sum((cur.get(s) or {}).get("N_comparator_trials") or 0 for s in base["topics"])
    out = {"baseline": {"commit": base["pinned_commit"], "N": base["N"], "fixture": os.path.relpath(BASE, ROOT).replace(os.sep, "/")},
           "current": {"N": n_now},
           "removed_n": sum(1 for r in removed if r["kind"] != "RELABELLED"), "relabelled_n": sum(1 for r in removed if r["kind"] == "RELABELLED"),
           "added_n": len(added), "removed": removed, "added": added}
    return out


def problems(led):
    """Every removal names a rule and carries span(s) found verbatim (whitespace-insensitive) in the cited source, whose
    sha256 matches; the arithmetic closes. Empty list = sound."""
    bad = []
    for r in led.get("removed") or []:
        if not r.get("rule_id") or r.get("kind") in (None, "UNEXPLAINED"):
            bad.append(f"{r.get('slug')}::{r.get('label')}: no rule")
            continue
        sp = r.get("span")
        spans = (sp.get("rows") if isinstance(sp, dict) and "rows" in sp else [sp]) + (
            [r.get("span_duplicate_of")] if r.get("kind") == "DUPLICATE_UNIT" else [])
        for s in spans:
            if not s or not s.get("text") or not s.get("source"):
                bad.append(f"{r['slug']}::{r['label']}: no span")
                continue
            p = os.path.join(ROOT, s["source"])
            if not os.path.exists(p):
                bad.append(f"{r['slug']}::{r['label']}: span source missing {s['source']}")
            elif _sha(p) != s.get("source_sha256"):
                bad.append(f"{r['slug']}::{r['label']}: span source changed {s['source']}")
            elif not all(_squash(t) in _squash(_source_text(p)) for t in (s.get("parts") or [s["text"]])):
                bad.append(f"{r['slug']}::{r['label']}: span not in its source")
            elif s.get("parts") and _squash(s["text"]) != _squash(" | ".join(s["parts"])):
                # the displayed text must BE its verified parts: checking only the parts let an edited text pass
                bad.append(f"{r['slug']}::{r['label']}: span not in its source (text is not its verified parts)")
    b = led.get("baseline", {}).get("N")
    if isinstance(b, int) and b - led.get("removed_n", 0) + led.get("added_n", 0) != led.get("current", {}).get("N"):
        bad.append(f"arithmetic: {b} - {led.get('removed_n')} + {led.get('added_n')} != {led.get('current', {}).get('N')}")
    return bad


def annotate_tracker(led):
    """The removal records live IN the tracker artefact too (dispatch 2026-10-04): every topic file carries its own
    `removed_comparator_rows` (and `added_comparator_rows`), and G1_SOURCE.json the denominator summary. A tracker file
    whose records differ from the ledger, or lack rule + span, fails tracker_problems() (plant: tests/test_g1_denominator.py)."""
    by = {}
    for r in led.get("removed") or []:
        by.setdefault(r["slug"], {"removed": [], "added": []})["removed"].append(r)
    for a in led.get("added") or []:
        by.setdefault(a["slug"], {"removed": [], "added": []})["added"].append(a)
    for path in sorted(glob.glob(os.path.join(OUT, "g1", "*.json"))):
        d = _j(path)
        rec = by.get(d["slug"]) or {"removed": [], "added": []}
        d["removed_comparator_rows"] = rec["removed"]
        d["added_comparator_rows"] = rec["added"]
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False)
    sp = os.path.join(OUT, "G1_SOURCE.json")
    src = _j(sp) if os.path.exists(sp) else {}
    src["denominator"] = {"baseline_commit": led["baseline"]["commit"], "baseline_N": led["baseline"]["N"],
                          "current_N": led["current"]["N"], "removed": led["removed_n"], "relabelled": led["relabelled_n"],
                          "added": led["added_n"], "by_kind": _by_kind(led), "ledger": "outputs/k_gap/G1_DENOMINATOR.json"}
    with open(sp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(src, indent=1, ensure_ascii=False) + "\n")


def _by_kind(led):
    out = {}
    for r in led.get("removed") or []:
        out[r["kind"]] = out.get(r["kind"], 0) + 1
    return out


def tracker_problems(led):
    """The tracker files must carry exactly the ledger's records for their topic, each with rule + span."""
    bad = []
    want = {}
    for r in led.get("removed") or []:
        want.setdefault(r["slug"], []).append((r["label"], r.get("kind"), r.get("rule_id")))
    for path in sorted(glob.glob(os.path.join(OUT, "g1", "*.json"))):
        d = _j(path)
        got = [(r.get("label"), r.get("kind"), r.get("rule_id")) for r in d.get("removed_comparator_rows") or []]
        if "removed_comparator_rows" not in d:
            bad.append(f"{d['slug']}: tracker file carries no removed_comparator_rows")
        elif sorted(got) != sorted(want.get(d["slug"], [])):
            bad.append(f"{d['slug']}: tracker removal records differ from the ledger")
        for r in d.get("removed_comparator_rows") or []:
            if not r.get("rule_id") or not r.get("span"):
                bad.append(f"{d['slug']}::{r.get('label')}: removal in the tracker without rule + span")
    return bad


def main(argv):
    if "--check" in argv:
        led0 = _j(LEDGER)
        bad = problems(led0) + tracker_problems(led0)
        for x in bad:
            print("REFUSED:", x)
        print("OK" if not bad else f"{len(bad)} problem(s)")
        return 1 if bad else 0
    led = build()
    with open(LEDGER, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(led, fh, indent=1, ensure_ascii=False)
    annotate_tracker(led)
    bad = problems(led) + tracker_problems(led)
    print(f"baseline {led['baseline']['N']} -> current {led['current']['N']}: removed {led['removed_n']}, relabelled "
          f"{led['relabelled_n']}, added {led['added_n']}; problems {len(bad)}")
    for x in bad:
        print("  ", x)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
