"""Plants for round 8 (ticagrelor-ACS and tocilizumab-COVID reviews): each builds the defect's input and reports FIRED
when the harness under test still produces the defect. On the pre-fix harness every plant fires; on the fixed one none.

  python scripts/plants_round8.py --harness-root <dir containing harness/> [--data-root <repo>] [--out <json>]
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path


def run(harness_root: Path, data_root: Path) -> dict:
    sys.path.insert(0, str(harness_root))
    for m in [k for k in sys.modules if k == "harness" or k.startswith("harness.")]:
        del sys.modules[m]
    out = {}

    def have(mod):
        try:
            return importlib.import_module(f"harness.{mod}")
        except ImportError:
            return None

    rob2 = have("rob2")
    pooled = "Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke"
    plato_p = [{"measure": "Participants With Any Event From the Composite of Death From Vascular Causes, Myocardial "
                           "Infarction (MI), and Stroke", "description": "Participants with death from vascular causes, MI, or stroke."},
               {"measure": "Participants With Any Major Bleeding Event", "description": "Participants with major bleed."}]
    plato_s = [{"measure": "Participants With Non-CABG (Coronary Artery Bypass Graft) Related Major Bleeding",
                "description": "Participants with non-CABG related major bleeding."}]
    # the build's matcher is an embedding similarity; a word-overlap stand-in reproduces the served text-identity match
    loose = lambda a, b: bool({w for w in a.lower().split() if len(w) > 3} & {w for w in b.lower().split() if len(w) > 3})  # noqa: E731
    d = rob2.derive_d5(plato_p, pooled, loose, plato_s)
    c = d["inputs"]["comparison"]
    wrong = c.get("matched") and set(rob2._component_set(c.get("registered_text") or "")) != set(rob2._component_set(pooled))
    out["Q1_PLATO_cv_composite_matched_to_bleeding_or_no_identity_chain"] = {
        "fired": bool(wrong) or d["level"] == "low", "got": [d["level"], c.get("method"), c.get("registered_label")]}

    philo_p = [{"measure": "Major Bleeding", "description": "Time to first occurrence of any major bleeding event."},
               {"measure": "Major Adverse Cardiac Events (MACE)", "description": "Time to first occurrence of any event from "
                "the composite of death from vascular causes, Myocardial Infarction (MI) and stroke."}]
    d = rob2.derive_d5(philo_p, pooled, None, [])
    out["Q2_PHILO_registered_MACE_reported_as_no_match"] = {"fired": not d["inputs"]["comparison"].get("matched"),
                                                           "got": [d["level"], d["inputs"]["comparison"].get("registered_label")]}

    screen = have("screen")
    slug = "tocilizumab-covid19-mortality"
    recs = json.loads((data_root / "cache" / slug / "records.json").read_text(encoding="utf-8"))
    rec = next(r for r in recs["records"] if str(r.get("id")) == "38485912")
    cfg = dict(json.loads((data_root / "topics" / f"{slug}.json").read_text(encoding="utf-8")), slug="plant-no-protocol")
    dd = screen.run([dict(rec)], cfg)["decisions"][0]
    out["Q3_standard_of_care_SOC_not_a_comparator"] = {"fired": dd["rule_id"] == "X3", "got": [dd["decision"], dd["rule_id"]]}

    ca, cn = have("comparator_analysis"), have("comparator_nesting")
    s2 = "ticagrelor-vs-clopidogrel-acs"
    try:
        a = ca.assess(ca.load(data_root, s2), {"outcomes": []})
        panel = json.loads((data_root / "cache" / s2 / "comparators.json").read_text(encoding="utf-8"))[0]
        n = cn.assess(data_root, s2, a, panel, ["NCT00391872"]) if cn else None
    except Exception as exc:  # noqa: BLE001 -- the pre-fix harness may not read the analysis at all
        n = {"state": f"ERROR {type(exc).__name__}"}
    out["Q4_PLATO_counted_twice_in_comparator_undetected"] = {"fired": (n or {}).get("state") != "DUPLICATED_POPULATION",
                                                              "got": (n or {}).get("state")}

    dm = have("date_membership")
    txt = "<p>IMMCoVA is a new trial not in the comparator because its paper was published after the REACT meta-analysis.</p>"
    out["Q5_membership_decided_by_publication_date_not_refused"] = {"fired": not (dm and dm.gate_reasons(txt)),
                                                                    "got": dm.gate_reasons(txt) if dm else None}

    try:
        a = ca.assess(ca.load(data_root, slug), {"outcomes": []})
        k = ((a or {}).get("stated_counts") or {}).get("drug_k", {}).get("value")
    except Exception as exc:  # noqa: BLE001
        k = f"ERROR {type(exc).__name__}"
    out["Q6_drug_specific_trial_count_not_typed"] = {"fired": k != 19, "got": k}

    pc = have("positive_control")
    ctl = next((c for c in pc.load(data_root) if c["id"] == "react-2021-tocilizumab-28d-mortality"), None)
    try:
        got = pc.reproduce(ctl, data_root) if ctl else None
        ce = got["CE"] if got else None
    except Exception as exc:  # noqa: BLE001
        ce = f"ERROR {type(exc).__name__}"
    ok = isinstance(ce, tuple) and abs(ce[0] - 0.825251) < 1e-6
    out["Q7_REACT_tocilizumab_not_reproduced"] = {"fired": not ok, "got": ce}
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness-root", required=True)
    ap.add_argument("--data-root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--out")
    a = ap.parse_args(argv[1:])
    res = run(Path(a.harness_root).resolve(), Path(a.data_root).resolve())
    for k, v in res.items():
        print(("FIRED    " if v["fired"] else "NOT FIRED"), k, v["got"])
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
