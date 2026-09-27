"""Reproduce the class-denominator census from pinned git objects (no network)."""
import json
import subprocess
from collections import Counter
from pathlib import Path

PIN = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def show(path):
    return json.loads(git("show", f"{PIN}:{path}"))


def counts(blocks):
    return {c["groupId"]: float(str(c["value"]).replace(",", ""))
            for block in blocks or [] for c in block.get("counts", [])}


def objects(value, path):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from objects(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from objects(child, f"{path}[{index}]")


def main():
    paths = git("ls-tree", "-r", "--name-only", PIN, "docs/reviews").decode().splitlines()
    slugs = [path.split("/")[2] for path in paths if path.endswith("/review.json")]
    items, served, topic_counts = [], [], []
    row_types, measure_types = Counter(), Counter()
    for slug in slugs:
        blob = show(f"cache/{slug}/records.json")
        review = show(f"docs/reviews/{slug}/review.json")
        records = {str(r["id"]): r for r in blob.get("records", [])}
        mismatches, topic_total, topic_rows = [], 0, 0
        for nct, measures in blob.get("ctgov_results", {}).items():
            for index, measure in enumerate(measures):
                topic_total += 1
                measure_types[measure.get("paramType") or "UNSPECIFIED"] += 1
                classes = measure.get("classes") or []
                selected = {0} if classes and classes[0].get("categories") else set()
                # The consumer reader can select a later first nonempty class.
                for ci, klass in enumerate(classes):
                    if any(cat.get("measurements") for cat in klass.get("categories", [])):
                        selected.add(ci)
                        break
                for ci in sorted(selected):
                    klass = classes[ci]
                    measure_n, class_n = counts(measure.get("denoms")), counts(klass.get("denoms"))
                    if class_n and class_n != measure_n:
                        item = dict(slug=slug, nct=nct, index=index, title=measure["title"],
                                    param=measure.get("paramType"), class_index=ci,
                                    class_title=klass.get("title"), measure_n=measure_n,
                                    class_n=class_n, groups=measure.get("groups"))
                        items.append(item)
                        mismatches.append(item)
        for oi, outcome in enumerate(review["outcomes"]):
            for ti, trial in enumerate(outcome.get("trials", [])):
                topic_rows += 1
                row_types["continuous" if "nc1" in trial else "count" if "n1i" in trial
                          else "reported_effect"] += 1
                trial_id = str(trial.get("id", "")).removeprefix("PMID ")
                ncts = {trial.get(key) for key in ("nct", "family_id", "trial_family_id")}
                ncts.add(records.get(trial_id, {}).get("nct"))
                if trial_id.startswith("NCT"):
                    ncts.add(trial_id)
                for path, obj in objects(trial, f"outcomes[{oi}].trials[{ti}]"):
                    for item in mismatches:
                        title_match = obj.get("registry_title") == item["title"] or any(
                            f"outcome '{item['title'][:limit]}'" in str(obj.get("source", ""))
                            for limit in (70, 80, 100))
                        if not title_match:
                            continue
                        # Exact source-backed registry join; a title alone is not an identity.
                        if item["nct"] not in ncts:
                            continue
                        fields = {k: v for k, v in obj.items() if k in (
                            "source", "ctgov_source", "n1i", "n2i", "nc1", "nc2", "endpoint_counts",
                            "n_analysis_set", "provenance", "scale")}
                        served.append(dict(slug=slug, outcome=outcome["name"], row=trial.get("id"),
                                           path=path, measure_index=item["index"], nct=item["nct"],
                                           title=item["title"], fields=fields))
        topic_counts.append(dict(slug=slug, measures=topic_total, mismatches=len(mismatches),
                                 served_rows=topic_rows))
    result = dict(pin=PIN, topic_slugs=slugs, topics=len(slugs),
                  measures=sum(measure_types.values()), served_rows=sum(row_types.values()),
                  row_types=dict(row_types), measure_types=dict(measure_types),
                  topic_counts=topic_counts, mismatches=items, served_matches=served)
    (Path(__file__).parent / "measurement.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
