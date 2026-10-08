"""The G1 denominator can only shrink with a typed, spanned reason (dispatch 2026-10-04).

outputs/k_gap/G1_DENOMINATOR.json (scripts/g1_denominator_ledger.py) lists every comparator row that left the pinned
367-row baseline (docs/evidence/g1-denominator/baseline-6efd9c00.json) with kind, rule ID and a span copied verbatim from
a held source (sha256 recorded), and every row that joined. These tests close the population: a row that leaves the
tracker WITHOUT a ledger record, a record without rule or span, a span not in its source, or arithmetic that does not
close, fails -- the plant builds each of those and the check must refuse it."""
import copy
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_denominator_ledger as dl  # noqa: E402

LED = json.load(open(dl.LEDGER, encoding="utf-8"))
BASE = json.load(open(dl.BASE, encoding="utf-8"))


def _current():
    out = {}
    for p in glob.glob(os.path.join(ROOT, "outputs", "k_gap", "g1", "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        out[d["slug"]] = d
    return out


def test_every_removal_has_a_rule_and_a_span_found_in_its_held_source():
    assert dl.problems(LED) == []


def test_the_ledger_covers_every_row_that_left_and_every_row_that_joined():
    cur = _current()
    left, joined = set(), set()
    for slug, b in BASE["topics"].items():
        now = {t["label"] for t in (cur.get(slug) or {}).get("trials") or []}
        left |= {(slug, l) for l in b["rows"] if l not in now}
        joined |= {(slug, l) for l in now if l not in b["rows"]}
    recorded = {(r["slug"], r["label"]) for r in LED["removed"]}
    relabels = {(r["slug"], r["now_label"]) for r in LED["removed"] if r["kind"] == "RELABELLED"}
    assert left == recorded, sorted(left ^ recorded)
    assert joined == {(a["slug"], a["label"]) for a in LED["added"]} | relabels
    assert LED["current"]["N"] == sum(d["N_comparator_trials"] for d in cur.values())
    assert LED["baseline"]["N"] == BASE["N"] == 367


def test_PLANT_an_unexplained_or_unspanned_removal_is_refused():
    # a row of a RETIRED comparator (5 Oct swaps 85de6a23 / 09c90901: every baseline row of a retired comparator is typed
    # COMPARATOR_RETIRED, before NOT_A_TRIAL -- the 15 statins subgroup rows were rows of the retired 39076238)
    r0 = next(r for r in LED["removed"] if r["kind"] == "COMPARATOR_RETIRED")
    for mutate, why in ((lambda r: r.update(rule_id=None), "no rule"),
                        (lambda r: r.update(kind="UNEXPLAINED"), "no rule"),
                        (lambda r: r.update(span=None), "no span"),
                        (lambda r: r["span"].update(text="Gitsels et al. 2016 enrolled 4 million patients"), "not in its source"),
                        (lambda r: r["span"].update(source_sha256="0" * 64), "changed")):
        led = copy.deepcopy(LED)
        r = next(x for x in led["removed"] if x["label"] == r0["label"] and x["slug"] == r0["slug"])
        mutate(r)
        assert any(why in p for p in dl.problems(led)), why


def test_PLANT_arithmetic_that_does_not_close_is_refused():
    led = copy.deepcopy(LED)
    led["removed_n"] += 1
    assert any(p.startswith("arithmetic") for p in dl.problems(led))


def test_the_denominator_reasons_are_the_ones_audited():
    kinds = {}
    for r in LED["removed"]:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    # OTHER_AGENT 2 (5 Oct): + VERTIS-CV (dapagliflozin), an ertugliflozin trial scoped by k-gap's identity chain;
    # 4 since 17eb3a55 (SOLOIST-WHF, SCORED: IDENTITY_CHAIN_REGISTRY). COMPARATOR_RETIRED 57 since the 5 Oct comparator
    # swaps (statins 27, melatonin 19, esketamine 6, dpp4 5); 64 since V9-03 (doac 7: van Es 2014 retired for its
    # licence, span from the recorded licence probe); the new comparators' rows come back in as 'added'.
    assert kinds == {"COMPARATOR_RETIRED": 64, "DUPLICATE_UNIT": 1, "OTHER_AGENT": 4, "NOT_IN_COMPARATOR_TABLE": 2,
                     "RELABELLED": 1}
    assert {r["slug"] for r in LED["removed"] if r["kind"] == "COMPARATOR_RETIRED"} == {
        "statins-primary-prevention-elderly", "melatonin-primary-insomnia-sol", "esketamine-trd-madrs", "dpp4-mace-t2d",
        "doac-vte-recurrence"}
    assert all(r["rule_id"].startswith("COMPARATOR_RETIRED:") and r["retired_comparator_pmid"] != r["replaced_by"]
               for r in LED["removed"] if r["kind"] == "COMPARATOR_RETIRED")
    vc = next(r for r in LED["removed"] if r["label"] == "VERTIS-CV")
    assert vc["rule_id"] == "K-GAP:OTHER_AGENT:IDENTITY_CHAIN" and "Ertugliflozin" in vc["span"]["text"]
    smart = next(r for r in LED["removed"] if r["kind"] == "DUPLICATE_UNIT")
    assert smart["label"] == "Semler [15]" and smart["duplicate_of"] == "Semler (SMART trial)"
    assert "29485925" in smart["identity"]["pmids"]
    emp = next(r for r in LED["removed"] if r["kind"] == "OTHER_AGENT"
               and r["rule_id"] == "K-GAP:OTHER_AGENT:REGISTRY_INTERVENTIONS")
    assert "Empagliflozin" in emp["span"]["text"] and emp["slug"] == "dapagliflozin-hfpef-hosp"


def test_the_tracker_artefact_itself_carries_every_removal_with_rule_and_span():
    assert dl.tracker_problems(LED) == []
    src = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "G1_SOURCE.json"), encoding="utf-8"))
    assert src["denominator"]["baseline_N"] == 367 and src["denominator"]["current_N"] == LED["current"]["N"]
    assert src["denominator"]["by_kind"]["COMPARATOR_RETIRED"] == 64             # + doac 7 (V9-03)


def test_PLANT_a_tracker_removal_without_rule_or_span_is_refused(tmp_path, monkeypatch):
    import shutil
    d = tmp_path / "outputs" / "k_gap" / "g1"
    shutil.copytree(os.path.join(ROOT, "outputs", "k_gap", "g1"), d)
    p = d / "statins-primary-prevention-elderly.json"
    o = json.load(open(p, encoding="utf-8"))
    o["removed_comparator_rows"][0]["span"] = None
    p.write_text(json.dumps(o), encoding="utf-8")
    monkeypatch.setattr(dl, "OUT", str(tmp_path / "outputs" / "k_gap"))
    assert any("without rule + span" in x for x in dl.tracker_problems(LED))
    o["removed_comparator_rows"] = o["removed_comparator_rows"][1:]           # a removal missing from the tracker
    p.write_text(json.dumps(o), encoding="utf-8")
    assert any("differ from the ledger" in x for x in dl.tracker_problems(LED))


def test_PLANT_a_chain_other_agent_removal_needs_a_held_title_naming_the_agent(monkeypatch):
    # the chain scopes the unit OTHER_AGENT, but no held report title names that agent: no span, so the removal stays
    # unexplained (fail-closed) -- and a unit the tracker does not list as an other agent gets nothing either
    real = dl._j
    def fake(path):
        d = real(path)
        if path == dl.CHAIN:
            d = dict(d, results=dict(d["results"]))
            r = dict(d["results"]["dapagliflozin-hfpef-hosp::VERTIS-CV"], scope="OTHER_AGENT:canagliflozin")
            d["results"]["dapagliflozin-hfpef-hosp::VERTIS-CV"] = r
        return d
    assert dl.chain_other_agent_span("dapagliflozin-hfpef-hosp", "VERTIS-CV", ["VERTIS-CV"])[0]
    assert dl.chain_other_agent_span("dapagliflozin-hfpef-hosp", "VERTIS-CV", [])[0] is None
    monkeypatch.setattr(dl, "_j", fake)
    assert dl.chain_other_agent_span("dapagliflozin-hfpef-hosp", "VERTIS-CV", ["VERTIS-CV"])[0] is None


def test_PLANT_an_identity_chain_registry_removal_needs_the_committed_aact_extract_naming_the_agent(tmp_path, monkeypatch):
    # dapagliflozin SOLOIST-WHF / SCORED: k-gap's chain scopes them OTHER_AGENT:sotagliflozin from their REGISTERED
    # interventions; the ledger accepts it only with the committed AACT interventions extract naming that agent
    import json as _json
    import g1_denominator_ledger as L
    chain = tmp_path / "chain.json"
    chain.write_text(_json.dumps({"results": {"s::U": {"scope": "OTHER_AGENT:sotagliflozin", "nct": "NCT00000009",
                                                        "basis": "AACT_STUDIES_ACRONYM+REGISTERED_INTERVENTIONS", "state": "RESOLVED"}}}),
                     encoding="utf-8")
    monkeypatch.setattr(L, "CHAIN", str(chain))
    monkeypatch.setattr(L, "EVID", str(tmp_path))
    assert L.chain_registry_span("s", "U", ["U"]) == (None, None)                 # no extract -> refused
    (tmp_path / "aact_interventions_NCT00000009.txt").write_text("1|NCT00000009|DRUG|Placebo|x\n", encoding="utf-8")
    assert L.chain_registry_span("s", "U", ["U"]) == (None, None)                 # extract does not name the agent
    (tmp_path / "aact_interventions_NCT00000009.txt").write_text("1|NCT00000009|DRUG|Sotagliflozin|x\n2|NCT00000009|DRUG|Placebo|x\n",
                                                                 encoding="utf-8")
    sp, ev = L.chain_registry_span("s", "U", ["U"])
    assert "Sotagliflozin" in sp["text"] and ev["nct"] == "NCT00000009"
    assert L.chain_registry_span("s", "U", []) == (None, None)                    # not listed among the other-agent units
