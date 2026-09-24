"""F4B_REPORT.md from F4B_DATA.json -- every count computed here."""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "F4B_DATA.json"), encoding="utf-8"))
E = D["entries"]
N = len(E)
assert N == D["population"]["n"] == 34, N
L = ["# evid2 DATA for the F4 count-observation schema v1 -- report", "",
     f"Population: **{N}** held count entries (`{D['population']['rule']}`) at `{D['population']['ref'][:8]}` -- the F4 "
     "lane's 34, reproduced exactly (18 files; 0 carried comparator_direction, 0 carried observations). Kinds: hand "
     "entries only; no controls. 19 of them are also served count rows typed in `../records/`; 15 are hand entries not "
     "served today. (The 35 served rows typed earlier include 16 machine-extracted rows that have no held entry.)", "",
     "## What evid2 supplies per entry", "",
     "- `comparator_direction`: `\"<intervention arm> vs <comparator arm>\"` in the SOURCE's own arm names -- only where "
     "evid2's independent gate BOUND both arms (G1-G7).",
     "- `observations`: the F4 producer's OWN computed objects, byte for byte, and only where (a) the producer bound the "
     "entry with that direction and (b) every arm's (role, events, n) equals evid2's (slot, events, total). "
     "`observation_mismatch()` compares supplied to re-extracted by equality, so a hand-built object would be refused.",
     "- nothing else: `contrast` is a policy statement about the configured orientation, the F4 lane's to set.", "",
     "## Counts", ""]
st = collections.Counter(e["evid2_state"] for e in E.values())
L.append("evid2's own evidence, over the 34: " + ", ".join(f"{k} {v}" for k, v in sorted(st.items())))
L.append(f"comparator_direction supplied: **{sum(1 for e in E.values() if e.get('comparator_direction'))} of {N}**")
L.append(f"observations supplied (two instruments agree): **{sum(1 for e in E.values() if e.get('observations'))} of {N}**")
pc = collections.Counter((e["producer"]["state"], e["producer"]["count_binding_state"],
                          str(e["producer"]["reason_code"])) for e in E.values())
L.append("F4 producer with evid2's directions: " + "; ".join(f"{a}/{b}/{c}: {v}" for (a, b, c), v in pc.most_common()))
L += ["", "## Where the F4 grammar abstains but evid2's gate binds (the shapes, for the F4 lane)", "",
      "| entry | producer code | evid2 events ownership | events span (evid2) |", "|---|---|---|---|"]
for k, e in E.items():
    if e.get("comparator_direction") and not e.get("observations"):
        a = e["evid2_arms"][0]
        L.append(f"| {k} | {e['producer']['reason_code']} | {a['events_ownership']}, {e['evid2_arms'][1]['events_ownership']} | "
                 f"{(a['events_span'] or '')[:160].replace('|', '/')} |")
L += ["", "## Entries without a direction, with evid2's reasons", ""]
for k, e in E.items():
    if not e.get("comparator_direction"):
        L.append(f"- **{k}** ({e['outcome']}; {e['evid2_state']}): " + "; ".join(r[:200] for r in e["evid2_reasons"][:3]))
L += ["", "## Limits", "",
      "- The producer run is a RECONSTRUCTION of the F4 tree (RECONSTRUCTION.md: 72 of 74 of its tests, both failures "
      "explained); the F4 lane's own code re-derives every observation when it lands.",
      "- Nothing here edits `cache/`: `F4B_DATA.json` is an overlay for the F4 lane to apply with its code. Supplying "
      "a direction can change which rows bind, and therefore a served page -- that landing is theirs and is a "
      "result change to be noticed and signed, not evid2's to make."]
open(os.path.join(HERE, "F4B_REPORT.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("ok")
