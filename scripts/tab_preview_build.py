"""Read served primary outcomes and current assessment objects; write local HTML previews only.

    python scripts/tab_preview_build.py

No assessments, source records, or served pages are changed.
"""
from __future__ import annotations

from collections import Counter
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from robgrade import rob2_tab  # noqa: E402
from scripts import grade_formal_build  # noqa: E402


def escape(value):
    """Preserve structured values and nulls without interpreting them as HTML."""
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return html.escape(value, quote=True)


def table(headers, rows):
    head = "".join(f"<th scope='col'>{escape(h)}</th>" for h in headers)
    body = []
    for row in rows:
        cells = f"<th>{escape(row[0])}</th>"
        cells += "".join(f"<td>{escape(v)}</td>" for v in row[1:])
        body.append(f"<tr>{cells}</tr>")
    return f"<table border='1'><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def page(title, content):
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<title>{escape(title)}</title></head><body><header>PREVIEW -- not served</header>"
            f"<h1>{escape(title)}</h1>{content}</body></html>\n")


def read_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def render_topic(slug, review, grade):
    primary = [o for o in review["outcomes"] if o.get("primary")]
    if len(primary) != 1:
        raise ValueError(f"{slug}: expected exactly one served primary outcome")
    outcome = primary[0]
    trial_ids = [t["id"] for t in outcome.get("trials") or []]
    if len(set(trial_ids)) != len(trial_ids):
        raise ValueError(f"{slug}: duplicate pooled trial IDs")
    rob, sources = grade_formal_build.rob_for(slug, outcome["name"], trial_ids)
    if grade.get("rob_sources") != sources:
        raise ValueError(f"{slug}: GRADE rob_sources differ from current sources; rebuild grade first, then preview")
    rows = []
    for trial_id in trial_ids:
        if trial_id not in rob:
            rows.append([trial_id, "No source object"] +
                        ["No formal RoB 2 assessment yet"] * (len(rob2_tab.rf.DOMAINS) + 1))
            continue
        obj = rob[trial_id]
        rows.append([trial_id, sources[trial_id]] +
                    [rob2_tab.domain_label(obj["domains"][d]) for d in rob2_tab.rf.DOMAINS] +
                    [rob2_tab.overall_label(obj["overall"], obj["domains"])])
    content = f"<h2>{escape(outcome['name'])}</h2>"
    content += table(["Trial", "Source tier", *rob2_tab.rf.DOMAINS, "Overall"], rows)
    content += "<h2>GRADE summary</h2>"
    content += table(["Field", "Value"], [
        [key, grade[key]] for key in ("certainty", "certainty_from_assessed_domains_only")])
    content += table(["Domain", "Downgrade", "State", "Basis"], [
        [name, domain["downgrade"], domain["state"], domain["basis"]]
        for name, domain in sorted(grade["domains"].items())])
    content += table(["Field", "Value"], [["judgement_flags", grade["judgement_flags"]]])
    if grade.get("certainty_change") is not None:
        content += "<h3>certainty_change: UNSIGNED -- for the signing packet</h3>"
        content += f"<pre>{escape(grade['certainty_change'])}</pre>"
    counts = Counter(sources.values())
    tiers = "; ".join(f"{label}: {counts[label]}" for label, _ in grade_formal_build.TIERS)
    summary = [slug, len(trial_ids), len(rob), tiers, grade["certainty"], grade["judgement_flags"]]
    return page(f"RoB 2 + GRADE: {slug}", content), summary


def main(argv=None):
    if argv:
        raise ValueError("This builder takes no arguments: it previews every served topic")
    root = Path(ROOT)
    reviews = sorted((root / "docs/reviews").glob("*/review.json"))
    if not reviews:
        raise ValueError("No served reviews found")
    # Read and render everything before writing, so missing inputs fail closed.
    pages, summaries = {}, []
    for path in reviews:
        slug = path.parent.name
        rendered, summary = render_topic(
            slug, read_json(path), read_json(root / "outputs/robgrade/grade" / f"{slug}.json"))
        pages[f"{slug}.html"] = rendered
        summaries.append(summary)
    pages["index.html"] = page("Served-topic RoB 2 + GRADE preview", table(
        ["Topic", "Pooled trials", "With object", "With object by tier", "Certainty", "Flags"], summaries))
    out = root / "outputs/robgrade/tab_preview_served"
    out.mkdir(parents=True, exist_ok=True)
    for filename, rendered in pages.items():
        with (out / filename).open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(rendered)
    print(f"Pages written: {len(pages)}")
    print("topic\tpooled\twith object\tcertainty")
    for slug, pooled, assessed, _, certainty, _ in summaries:
        print(f"{slug}\t{pooled}\t{assessed}\t{certainty}")
    return summaries


if __name__ == "__main__":
    main(sys.argv[1:])
