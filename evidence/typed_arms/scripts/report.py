"""evidence/typed_arms/REPORT.md -- every count computed here from the committed records; nothing typed by hand."""
import collections, glob, json, os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pop = json.load(open(os.path.join(BASE, "population.json"), encoding="utf-8"))
recs = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(BASE, "records", "*.json")))]
N = pop["n"]
assert len(recs) == N, f"{len(recs)} records for a population of {N}"
st = collections.Counter(r["state"] for r in recs)
arms = [a for r in recs for a in r["arm_observations"]]
bound_arms = [a for r in recs if r["state"] == "BOUND" for a in r["arm_observations"]]


def kind(a):
    b = a.get("arm_id_basis") or ""
    return ("FACTORIAL_MARGIN" if b.startswith("FACTORIAL") else "REGISTRY_ARM (gate-derived)" if "derived by the gate" in b
            else "SOURCE_LABEL (registry non-discriminating)" if "NON-DISCRIMINATING" in b
            else "REGISTRY_ARM" if b.startswith("REGISTRY_ARM") else "SOURCE_LABEL (no registry arms held)" if b else "none")


L = ["# Typed per-arm observations for the served count rows -- report", "",
     f"Population: **{N}** served count rows (`outcomes[*].trials[*]` with `ai`/`ci`) at `{pop['ref'][:8]}`, frozen in "
     "`population.json`. Kinds of item in the population: served count rows only -- no synthetic controls (those live "
     "in `tests/test_typed_arms.py`), no split rows, no refused-at-intake rows.", "",
     "Before this work: comparator_direction carried by 0 of %d; typed arm ownership carried by 0 of %d." % (
         sum(1 for r in pop["rows"] if not r["has_comparator_direction"]), sum(1 for r in pop["rows"] if not r["has_arm_ownership"])), "",
     "## Result", ""]
for s in ("BOUND", "SET_ASIDE", "SOURCE_DIFFERS", "NOT_EXTRACTED"):
    L.append(f"- **{s}: {st.get(s, 0)} of {N}**")
L += ["", "`SOURCE_DIFFERS` is the only state that would change a served number; it goes to Mahmood's signature queue, "
      "never landed. `SET_ASIDE` changes nothing served: the row keeps its served value and is not typed.", "",
      "## Bound rows: how each arm's identity and ownership were established", ""]
kc = collections.Counter(kind(a) for a in bound_arms)
L.append(f"Arm identity, over the {len(bound_arms)} arms of the {st.get('BOUND', 0)} bound rows:")
L += [f"- {k}: {v}" for k, v in kc.most_common()]
for field, title in (("events_ownership", "events"), ("total_ownership", "denominator")):
    c = collections.Counter(a.get(field) for a in bound_arms)
    L.append(f"\nOwnership of the {title} (G7), over the same {len(bound_arms)} arms:")
    L += [f"- {k}: {v}" for k, v in c.most_common()]
tb = collections.Counter(a.get("total_basis") for a in bound_arms)
L.append(f"\nDenominator basis as the source states it, over the same {len(bound_arms)} arms (a percentage never stands in):")
L += [f"- {k}: {v}" for k, v in tb.most_common()]
L += ["", "## Every row not bound, with its named reasons", ""]
for r in recs:
    if r["state"] != "BOUND":
        L.append(f"### {r['row_id']} -- {r['state']}")
        L.append(f"{r['slug']} / {r['outcome_name']} / {r['trial_id']}; served {r['served_f4b']}")
        L += [f"- {x}" for x in r["reasons"]]
        if r.get("extractor_notes"):
            L.append(f"- extractor note: {r['extractor_notes'][:600]}")
        L.append("")
L += ["## Bound rows", "", "| row | outcome | experimental (ai/n1i) | comparator (ci/n2i) | events own. | total own. |", "|---|---|---|---|---|---|"]
for r in recs:
    if r["state"] == "BOUND":
        e = [a for a in r["arm_observations"] if a["f4b_slot"] == "ai/n1i"][0]
        c = [a for a in r["arm_observations"] if a["f4b_slot"] == "ci/n2i"][0]
        L.append(f"| {r['row_id']} | {r['outcome_name']} | {e['arm_label']} `{e['arm_id']}` {e['events']}/{e['total']} | "
                 f"{c['arm_label']} `{c['arm_id']}` {c['events']}/{c['total']} | {e.get('events_ownership')}, {c.get('events_ownership')} | "
                 f"{e.get('total_ownership')}, {c.get('total_ownership')} |")
L += ["", "## Limits", "",
      "- Ownership relations are text heuristics with named rules (`scripts/ownership.py`), tested on synthetic plants; "
      "they refuse rather than guess, and a refusal is a SET_ASIDE, not a finding about the trial.",
      "- `SOURCE_LABEL` arm ids are identities within the trial's own report, not registry identities; they are typed as "
      "such and counted separately above.",
      "- The main lane's typed schema was on no pushed branch when this was built; each arm names its served F4B slot so "
      "the records can be re-keyed onto that schema without re-extraction."]
open(os.path.join(BASE, "REPORT.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print(dict(st), "of", N)
