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


# What was served BEFORE the switches: main as it stood before PR #13 merged them (469a97eb). Pinned to that commit, never
# to origin/main -- a moving ref made this control retire itself the moment PR #13 merged (main's CI, e2b927c3), because
# from then on 'origin/main' IS the tree under test. The commit is in main's history, so every clone of main holds it.
SERVED_BEFORE = "469a97eb6a783eab92dcc117699abc2c0a9836c8"


def _main(path):
    return json.loads(subprocess.run(["git", "show", f"{SERVED_BEFORE}:{path}"], cwd=ROOT, capture_output=True,
                                     check=True).stdout)


def _unsigned_root(tmp_path):
    """The adoption records with NO signatures file: the switches as they stood before Mahmood signed V8. Synthetic on
    purpose -- read against the live registry this control retired itself the day V8 was signed (7 Oct)."""
    d = tmp_path / "registry" / "comparator_selection"
    d.mkdir(parents=True)
    for s in SLUGS:
        src = os.path.join(ROOT, "registry", "comparator_selection", s + ".adoption.json")
        (d / (s + ".adoption.json")).write_text(open(src, encoding="utf-8").read(), encoding="utf-8")
    return str(tmp_path)


def test_unsigned_switches_serve_the_previous_comparator_exactly(tmp_path):
    root = _unsigned_root(tmp_path)
    for s in SLUGS:
        cfg = json.load(open(os.path.join(ROOT, "topics", s + ".json"), encoding="utf-8"))
        panel = json.load(open(os.path.join(ROOT, "cache", s, "comparators.json"), encoding="utf-8"))
        assert sc.served_config(s, cfg, root)["comparator_pmid"] == _main(f"topics/{s}.json")["comparator_pmid"], s
        assert sc.served_panel(s, panel, root) == _main(f"cache/{s}/comparators.json"), s


def test_the_v8_signed_switches_serve_the_adopted_comparators():
    """Mahmood signed all five (V8, 7 Oct): the committed register now serves each adopted comparator."""
    for s in SLUGS:
        cfg = json.load(open(os.path.join(ROOT, "topics", s + ".json"), encoding="utf-8"))
        a = json.load(open(os.path.join(ROOT, "registry", "comparator_selection", s + ".adoption.json"), encoding="utf-8"))
        assert sc.served_config(s, cfg)["comparator_pmid"] == str(a["comparator_pmid"]), s


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


def test_the_served_pages_name_exactly_the_comparator_the_signatures_permit():
    """The REQUIREMENT, not a snapshot: a served page names served_config's comparator -- the previous one while a switch
    is unsigned, the adopted one once signed (V8, 7 Oct). The earlier form pinned 'the previous comparator' and turned
    red the day the switches were signed."""
    for s in SLUGS:
        r = json.load(open(os.path.join(ROOT, "docs", "reviews", s, "review.json"), encoding="utf-8"))
        cfg = json.load(open(os.path.join(ROOT, "topics", s + ".json"), encoding="utf-8"))
        assert str(r["comparator"].get("pmid")) == str(sc.served_config(s, cfg)["comparator_pmid"]), s
        assert r["comparator"].get("pmid") is not None, (s, "a served comparator block always names its PMID")
