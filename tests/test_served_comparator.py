"""Plant: a served page keeps naming its comparator until Mahmood signs the switch (packet V8). The binding lane's
replacement comparators (5 Oct) changed topics/<slug>.json and cache/<slug>/comparators.json; on 6 Oct a rebuild would
have switched five served comparators unsigned (four pages lost their comparator PMID, denosumab named the new one)."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import served_comparator as sc  # noqa: E402

SLUGS = ["dpp4-mace-t2d", "esketamine-trd-madrs", "melatonin-primary-insomnia-sol", "denosumab-vertebral-fracture",
         "statins-primary-prevention-elderly"]


def _main(path):
    return json.loads(subprocess.run(["git", "show", f"origin/main:{path}"], cwd=ROOT, capture_output=True).stdout)


def test_unsigned_switches_serve_the_previous_comparator_exactly():
    for s in SLUGS:
        cfg = json.load(open(os.path.join(ROOT, "topics", s + ".json"), encoding="utf-8"))
        panel = json.load(open(os.path.join(ROOT, "cache", s, "comparators.json"), encoding="utf-8"))
        assert sc.served_config(s, cfg)["comparator_pmid"] == _main(f"topics/{s}.json")["comparator_pmid"], s
        assert sc.served_panel(s, panel) == _main(f"cache/{s}/comparators.json"), s


def test_a_signed_switch_serves_the_adopted_comparator(tmp_path):
    s = "dpp4-mace-t2d"
    (tmp_path / "registry" / "comparator_selection").mkdir(parents=True)
    a = json.load(open(os.path.join(ROOT, "registry", "comparator_selection", s + ".adoption.json"), encoding="utf-8"))
    (tmp_path / "registry" / "comparator_selection" / (s + ".adoption.json")).write_text(json.dumps(a), encoding="utf-8")
    cfg = {"comparator_pmid": a["comparator_pmid"]}
    assert sc.served_config(s, cfg, str(tmp_path))["comparator_pmid"] == a["retired"]["comparator_pmid"]
    (tmp_path / "registry" / "comparator_switch_signatures.json").write_text(json.dumps({"switches": {s: {
        "state": "SEEN_AND_SIGNED", "from": a["retired"]["comparator_pmid"], "to": a["comparator_pmid"]}}}), encoding="utf-8")
    assert sc.served_config(s, cfg, str(tmp_path))["comparator_pmid"] == a["comparator_pmid"]


def test_the_served_pages_name_the_previous_comparator():
    for s in SLUGS:
        r = json.load(open(os.path.join(ROOT, "docs", "reviews", s, "review.json"), encoding="utf-8"))
        assert str(r["comparator"].get("pmid")) == _main(f"topics/{s}.json")["comparator_pmid"], s
