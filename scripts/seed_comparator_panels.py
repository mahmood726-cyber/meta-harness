"""Offline, reviewable extraction into source panels; no overlap snapshots."""
import hashlib
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.comparator_panel import span, validate


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def seed_from_protocol(slug):
    """Seed one committed protocol from held OA XML, without a review dependency."""
    from scripts.comparator_correctness_sweep import _text_from_markup

    def require(value, field):
        if value is None or not str(value).strip():
            raise ValueError(f"PROTOCOL_PANEL: required {field} not derivable")
        return value

    def read(path, field):
        try:
            return path.read_bytes()
        except OSError as exc:
            raise ValueError(f"PROTOCOL_PANEL: required {field} not readable") from exc

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("PROTOCOL_PANEL: invalid slug")
    rel = f"topics/{slug}.json"
    try:
        committed = subprocess.check_output(["git", "show", f"HEAD:{rel}"], cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        raise ValueError("PROTOCOL_PANEL: topic not committed") from exc
    raw_topic = read(ROOT / rel, "topic")
    topic = json.loads(committed)
    if json.loads(raw_topic) != topic:
        raise ValueError("PROTOCOL_PANEL: topic differs from committed topic")
    pmid = str(require(topic.get("comparator_pmid"), "comparator_pmid"))
    if not re.fullmatch(r"[1-9][0-9]*", pmid):
        raise ValueError("PROTOCOL_PANEL: invalid comparator_pmid")
    registry = json.loads(read(ROOT / "registry/benchmarks/candidates_v1_1.json", "benchmark registry"))
    rows = [r for r in registry["screened"] if str(r.get("pmid")) == pmid]
    if len(rows) != 1:
        raise ValueError("PROTOCOL_PANEL: comparator registry mapping not unique")
    pmcid = str(require(rows[0].get("pmcid"), "pmcid"))
    if not re.fullmatch(r"PMC[0-9]+", pmcid):
        raise ValueError("PROTOCOL_PANEL: invalid pmcid")
    source = ROOT / "cache/benchmarks/v1" / (pmcid + ".xml")
    raw = read(source, "held XML")
    try:
        xml = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("PROTOCOL_PANEL: invalid held XML") from exc
    meta = require(xml.find("./front/article-meta"), "article-meta")

    def value(parent, path, field):
        node = parent.find(path)
        return require("" if node is None else "".join(node.itertext()).strip(), field)

    source_pmid = value(meta, "article-id[@pub-id-type='pmid']", "XML PMID")
    if source_pmid != pmid:
        raise ValueError("PROTOCOL_PANEL: XML PMID mismatch")
    pmc_tag = "pmcid" if meta.find("article-id[@pub-id-type='pmcid']") is not None else "pmc"
    source_pmc = value(meta, f"article-id[@pub-id-type='{pmc_tag}']", "XML PMCID")
    if source_pmc.removeprefix("PMC") != pmcid.removeprefix("PMC"):
        raise ValueError("PROTOCOL_PANEL: XML PMCID mismatch")
    licenses = meta.findall("permissions/license")
    if not any("creativecommons.org/licenses/by/" in ET.tostring(n, encoding="unicode") for n in licenses):
        raise ValueError("PROTOCOL_PANEL: CC BY license not derivable")
    title = value(meta, "title-group/article-title", "citation title")
    year = value(meta, "pub-date/year", "citation year")
    journal = value(xml, "./front/journal-meta/journal-title-group/journal-title", "citation journal")
    doi = value(meta, "article-id[@pub-id-type='doi']", "citation DOI")
    scope = require(topic.get("eligibility_summary"), "scope_note")
    require(xml.find("body"), "body")
    body = (require(_text_from_markup(raw), "body text") + "\n").encode("utf-8")
    doc = ROOT / "cache/comparators" / pmid / "body.txt"
    digest = hashlib.sha256(body).hexdigest()
    panel = dict(id=pmid, comparator_pmid=pmid,
                 citation=f"{title} ({year}); {journal}; DOI {doi}; PMID {pmid}",
                 year=year, scope_note=scope, held=True,
                 document_ref=doc.relative_to(ROOT).as_posix(), document_sha256=digest,
                 source_ref=source.relative_to(ROOT).as_posix(),
                 source_sha256=hashlib.sha256(raw).hexdigest(),
                 protocol_ref=rel, protocol_sha256=hashlib.sha256(committed).hexdigest(),
                 trial_set=[], k=None, effect=None, ci=None, i2=None, pi=None, method=None)
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_bytes(body)
    doc.with_suffix(".sha256").write_bytes((digest + "\n").encode())
    write(doc.with_name("protocol_source.json"), dict(pmid=pmid, pmcid=pmcid,
          body_file=panel["document_ref"], body_sha256=digest,
          body_raw_file=panel["source_ref"], source_sha256=panel["source_sha256"],
          extraction="scripts.comparator_correctness_sweep._text_from_markup"))
    validate(panel, ROOT)
    target = ROOT / "cache" / slug / "comparators.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    write(target, [panel])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug")
    parser.add_argument("--from-protocol", action="store_true")
    args = parser.parse_args(argv)
    if args.slug or args.from_protocol:
        if not (args.slug and args.from_protocol):
            parser.error("--slug and --from-protocol are required together")
        return seed_from_protocol(args.slug)
    for rp in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        slug = rp.parent.name
        r = json.loads(rp.read_text(encoding="utf-8"))
        old = r["comparator"]
        doc = ROOT / "cache" / slug / "comparator_fulltext.txt"
        if not doc.exists() or not doc.read_text(encoding="utf-8").strip():
            doc = ROOT / "cache/comparators" / str(old.get("pmid")) / "body.txt"
        document_field = None
        if not doc.exists() or not doc.read_text(encoding="utf-8").strip():
            records_path = ROOT / "cache" / slug / "records.json"
            if json.loads(records_path.read_text(encoding="utf-8")).get("comparator_fulltext"):
                doc = records_path
                document_field = "comparator_fulltext"
        held = doc.exists() and bool(doc.read_text(encoding="utf-8").strip())
        c = dict(id=str(old.get("pmid") or slug), citation=f"{old.get('name')} ({old.get('year')}); {old.get('journal')}; DOI {old.get('doi')}; PMID {old.get('pmid')}",
                 year=old.get("year"), scope_note="Registered comparator identity; unextracted quantities and trial membership remain unknown.",
                 held=held, document_ref=doc.relative_to(ROOT).as_posix() if held else None,
                 document_sha256=hashlib.sha256(doc.read_bytes()).hexdigest() if held else None,
                 trial_set=[], k=None, effect=None, ci=None, i2=None, pi=None, method=None)
        if document_field:
            c["document_field"] = document_field
        panel = [c]
        if slug == "glp1-ra-mace-t2d":
            text = doc.read_text(encoding="utf-8")
            c["id"] = "giugliano-2021"
            c["scope_note"] = "T2DM CVOTs; seven three-point MACE trials plus ELIXA four-point MACE. Search through June 30, 2021."
            table = "MACE All 8 0.86 0.79–0.94 0.006 50.0 0.080"
            for key, value in (("k", 8), ("effect", 0.86), ("ci", [0.79, 0.94]), ("i2", 50.0)):
                c[key] = {"value": value, "span": span(text, table)}
            method = "Pooled summary estimates were calculated according to random effects model using the empirical Bayes method that corresponds to Paule-Mandel method [ 13 ] with a Hartung-Knapp confidence interval adjustment [ 14 ]"
            c["method"] = {"value": "Paule-Mandel / Hartung-Knapp", "span": span(text, method)}
            endpoint = "The primary outcome for LEADER, SUSTAIN-6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6 and AMPLITUDE-O was a three-point MACE, whereas ELIXA used a four-point MACE, including also hospital admission for unstable angina."
            recpath = ROOT / "cache" / slug / "records.json"
            rectext = recpath.read_text(encoding="utf-8")
            records = json.loads(rectext)["records"]
            names = ["ELIXA", "LEADER", "SUSTAIN-6", "EXSCEL", "HARMONY Outcomes", "REWIND", "PIONEER 6", "AMPLITUDE-O"]
            for name in names:
                matches = [rec for rec in records if name.lower() in (rec.get("title", "") + " " + rec.get("abstract", "")).lower() and rec["id"] != str(old["pmid"])]
                if len(matches) != 1:
                    raise ValueError(f"Ambiguous source-backed family mapping {name}: {[m['id'] for m in matches]}")
                rec = matches[0]
                # The entire JSON record binds its PMID and family name in one locatable span.
                begin = rectext.index('"id": "' + rec["id"] + '"')
                begin = rectext.rfind("{", 0, begin)
                decoded, length = json.JSONDecoder().raw_decode(rectext[begin:])
                assert decoded["id"] == rec["id"]
                quote = rectext[begin:begin + length]
                assert name.lower() in quote.lower(), name
                c["trial_set"].append({"family_id": name, "span": span(text, endpoint),
                    "endpoint": "4-point MACE" if name == "ELIXA" else "3-point MACE",
                    "endpoint_span": span(text, endpoint),
                    "aliases": [{"id": rec["id"], "document_ref": recpath.relative_to(ROOT).as_posix(),
                                 "document_sha256": hashlib.sha256(recpath.read_bytes()).hexdigest(),
                                 "span": span(rectext, quote)}]})
            primary = next(o for o in r["outcomes"] if o.get("primary"))
            c["outcome_endpoints"] = {primary["name"]: "3-point MACE"}
            for author, year in (("Sattar", 2021), ("Hasebe", 2025), ("Lee", 2025), ("Abdalla", 2026)):
                panel.append(dict(id=f"{author.lower()}-{year}", citation=f"{author} {year} (identity supplied by lane adjudication; complete citation not held)",
                                  year=year, scope_note="Named GLP-1 comparator; no matching comparator document identified in the local tree. No network retrieval.",
                                  held=False, document_ref=None, document_sha256=None, trial_set=[],
                                  k=None, effect=None, ci=None, i2=None, pi=None, method=None))
        for item in panel:
            validate(item)
        write(ROOT / "cache" / slug / "comparators.json", panel)


if __name__ == "__main__":
    main()
