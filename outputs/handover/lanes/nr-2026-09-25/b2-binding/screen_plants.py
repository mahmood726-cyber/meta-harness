"""Execute the REAL structural screen (harness.trial_family.screen_family) on held family nodes, then change ONE
field -- the one the lane blames -- and re-run. If the code moves past the blamed step, the blame is shown by
execution, not by reading. In memory only."""
import copy
import json
import subprocess
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
from harness import trial_family  # noqa: E402

REV = "1fa77f2c4852ee79e55d540083e3c35bbff0cecc"


def show(path):
    return subprocess.run(["git", "show", f"{REV}:{path}"], cwd=W, capture_output=True, check=True).stdout


def node(slug, fid):
    review = json.loads(show(f"docs/reviews/{slug}/review.json"))
    return next(f for f in review["trial_families"] if f["family_id"] == fid)


def config(slug):
    return trial_family.protocol_requirements(str(W), slug, json.loads(show(f"topics/{slug}.json")))


def code(c):
    return c.get("absence_code") or c.get("code") or c.get("state")


def run(label, slug, fid, mutate):
    cfg = config(slug)
    fam = node(slug, fid)
    before = trial_family.screen_family(copy.deepcopy(fam), cfg)
    changed = copy.deepcopy(fam)
    mutate(changed, cfg)
    after = trial_family.screen_family(changed, cfg)
    print(f"{label}: {fid} held -> {before.get('state')}/{code(before)}; one field changed -> "
          f"{after.get('state')}/{code(after)}")


def set_conditions(value):
    def m(f, cfg):
        f["population"]["conditions"]["value"] = value
    return m


def as_placebo_control(f, cfg):
    # re-shape the comparator arm as a placebo arm (no active intervention); nothing else changes
    agents = list(cfg["include"]["intervention_any"])
    for a in f["arms"]:
        if not any(ag.lower() in " ".join(a["active_interventions"]).lower() for ag in agents):
            a["active_interventions"] = []
    # the build derives the stored contrasts from the arms (trial_family.families); re-derive them the same way
    f["randomised_contrasts"] = trial_family.randomised_contrasts(
        [dict(a, span=None) for a in f["arms"]], agents, True)


def recompute_only(f, cfg):
    # control plant: nothing about the arms changes, only the stored contrasts are re-derived -> must stay NOT_PROVEN
    f["randomised_contrasts"] = trial_family.randomised_contrasts(
        [dict(a, span=None) for a in f["arms"]], list(cfg["include"]["intervention_any"]), True)


def star_honoured(f, cfg):
    cfg["include"]["population_any"] = [t.rstrip("*") for t in cfg["include"]["population_any"]]


run("TERM_FORM   DELIVER (N09)", "dapagliflozin-hfpef-hosp", "NCT03030235",
    set_conditions(["Heart failure with preserved ejection fraction"]))
run("TERM_FORM   CARMELINA (N17-19)", "dpp4-mace-t2d", "NCT01897532", set_conditions(["Type 2 diabetes"]))
run("TERM_FORM   esketamine TRANSFORM (N20)", "esketamine-trd-madrs", "NCT02422186",
    set_conditions(["Treatment-resistant depression"]))
run("WILDCARD    probiotics (N29)", "probiotics-aad-prevention", "NCT03334604", star_honoured)
run("ACTIVE_COMP ROCKET AF (N25)", "noac-vs-warfarin-af-stroke", "NCT00403767", as_placebo_control)
run("ACTIVE_COMP PLATO (N39)", "ticagrelor-vs-clopidogrel-acs", "NCT00391872", as_placebo_control)
run("ACTIVE_COMP PARADIGM-HF (N32)", "sacubitril-valsartan-hfref", "NCT01035255", as_placebo_control)
run("CONTROL     ROCKET AF re-derive only (N25)", "noac-vs-warfarin-af-stroke", "NCT00403767", recompute_only)
