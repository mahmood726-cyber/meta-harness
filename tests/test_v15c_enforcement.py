"""V15-C enforcement switch-on (Mahmood, 13 Oct, ruling 1). An UNBOUND_LEGACY row is pooled ONLY under a signed ADMIT
whose served-number snapshot still equals its numbers; anything else leaves the pool, displayed, never deleted."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import enforcement as enf  # noqa: E402

DEC = os.path.join(ROOT, "registry", "v15c_decisions.json")


def _doc(rows, sha=enf.PACKET_SHA256):
    return {"signed": {"packet_sha256": sha, "state": "SEEN_AND_SIGNED"}, "rows": rows}


def _apply(tmp_path, rows, trials, sha=enf.PACKET_SHA256):
    p = tmp_path / f"d{len(rows)}{sha[:4]}.json"
    p.write_text(json.dumps(_doc(rows, sha)), encoding="utf-8")
    return enf.apply("s", {"name": "O"}, trials, path=str(p))


def _t(rid, **k):
    return dict({"id": rid, "label": rid, "endpoint_admissibility": "UNBOUND_LEGACY", "effect": 0.8, "ci_low": 0.7,
                 "ci_high": 0.9}, **k)


ADMIT = {"slug": "s", "outcome": "O", "id": "PMID 1", "decision": "ADMIT", "basis": "b",
         "served": {"effect": 0.8, "ci_low": 0.7, "ci_high": 0.9}, "span": "HR 0.8 (0.7-0.9)"}


def test_plant_an_unbound_row_outside_the_signed_scope_is_neither_refused_nor_admitted(tmp_path):
    """The signed packet's scope was 77 rows (main 66219d315). The preview render found 13 more unbound rows on today's
    main that no panel has read: refusing them would move pools nobody signed; admitting them would claim a signature
    they lack. They keep their legacy state, marked PENDING (counted and listed), until read and signed."""
    kept, absent = _apply(tmp_path, [], [_t("PMID 9")])
    assert absent == [] and kept[0]["endpoint_admissibility"] == "UNBOUND_LEGACY"
    assert kept[0]["enforcement"]["decision"] == "PENDING_TRIAGE"


def test_a_signed_admit_with_its_own_numbers_is_pooled_as_a_signed_binding(tmp_path):
    kept, absent = _apply(tmp_path, [ADMIT], [_t("PMID 1")])
    assert absent == [] and kept[0]["endpoint_admissibility"] == "SIGNED_BINDING"
    assert kept[0]["endpoint_result_span"] == "HR 0.8 (0.7-0.9)"


def test_plant_an_admit_whose_numbers_moved_after_signing_is_refused(tmp_path):
    kept, absent = _apply(tmp_path, [ADMIT], [_t("PMID 1", effect=0.81)])
    assert kept == [] and "not the numbers the signed decision admitted" in absent[0]["reason"]


def test_a_refusal_on_evidence_is_typed_and_an_abstention_is_debt(tmp_path):
    rows = [dict(ADMIT, id="PMID 2", decision="REFUSE", kind="refused_on_evidence", basis="different endpoint"),
            dict(ADMIT, id="PMID 3", decision="REFUSE", kind="abstain", basis="unresolved")]
    kept, absent = _apply(tmp_path, rows, [_t("PMID 2"), _t("PMID 3")])
    assert kept == [] and [a["state"] for a in absent] == ["REFUSED_ON_EVIDENCE", "EXTRACTION_DEBT"]
    assert all(a["refused_effect"] == {"effect": 0.8, "ci_low": 0.7, "ci_high": 0.9} for a in absent)


def test_a_bound_row_is_untouched(tmp_path):
    t = _t("PMID 4", endpoint_admissibility="EXACT_TARGET")
    assert _apply(tmp_path, [], [t]) == ([t], [])


def test_plant_an_unsigned_or_missing_decisions_file_stops_the_build(tmp_path):
    """With rows outside the signed scope kept PENDING, a decisions file that is not the signed one would quietly switch
    enforcement OFF (every row 'outside scope'). The switch is on: a missing or unsigned file is an error, never a no-op."""
    import pytest
    with pytest.raises(enf.EnforcementError):
        _apply(tmp_path, [ADMIT], [_t("PMID 1")], sha="0" * 64)
    with pytest.raises(enf.EnforcementError):
        enf.apply("s", {"name": "O"}, [_t("PMID 1")], path=str(tmp_path / "missing.json"))


def test_the_committed_decisions_are_the_generator_output():
    """Generated, never hand-edited: the script reproduces the committed file byte for byte."""
    import v15c_decisions as g
    doc = g.build()
    want = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    assert open(DEC, encoding="utf-8").read() == want
    assert (doc["n"], doc["admit"], doc["refuse"]) == (77, 64, 13)


def test_plant_the_served_dpp4_pool_no_longer_carries_tecos():
    """The switch is ON in the served build: TECOS (signed refusal) is out of the dpp4 MACE pool and displayed as a
    refusal on evidence; the 53 + 4 admitted rows carry SIGNED_BINDING."""
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "dpp4-mace-t2d", "review.json"), encoding="utf-8"))
    o = [x for x in r["outcomes"] if x.get("name") == "3-point major adverse cardiovascular events"][0]
    assert all("26052984" not in str(t.get("id")) for t in o.get("trials") or [])
    assert any("26052984" in str(a.get("id")) and a.get("state") == "REFUSED_ON_EVIDENCE" for a in o.get("declared_absent_trials") or [])


def test_plant_a_unanimous_panel_whose_numbers_are_in_the_span_is_not_refused_as_unresolved():
    """The signed rule refuses where the panel DISAGREES or the source is ABSENT. Three probiotics rows were 'unresolved'
    only because the bind checker cannot read number words ('four of 119') -- codex, agy and the adjudicator bound the
    same numbers, equal to the served ones. Refusing them flipped the served AAD conclusion across the null (0.62 ->
    0.85, CI 0.65-1.10). They are admitted, each served number located in the verbatim span (word recorded)."""
    d = {(r["slug"], str(r["id"])): r for r in json.load(open(DEC, encoding="utf-8"))["rows"]}
    for pid in ("15740542", "18026577", "18410562"):
        r = d[("probiotics-aad-prevention", f"PMID {pid}")]
        assert r["decision"] == "ADMIT" and r["located"], pid
    for key in (("metformin-pcos-ovulation", "PMID 16769748"), ("metformin-pcos-ovulation", "PMID 19522426"),
                ("ticagrelor-vs-clopidogrel-acs", "PMID 19717846")):
        assert d[key]["decision"] == "REFUSE", key            # the bound numbers are not the served ones / empty binds
    four = d[("probiotics-aad-prevention", "PMID 15740542")]["located"]
    assert four["ai"] == "four" and four["n1i"] == "119"


def test_plant_r1_a_percentage_is_never_located_as_a_count():
    """codex v15cenf-cap-r1 #1 (P0): locate matched by VALUE, so '4%' and '8%' passed as death counts. A count is located
    only as one side of an 'X of N' pair (digits or a number word); no number followed by % is ever used."""
    import v15c_decisions as g
    span = "Deaths occurred in 4% (of 119) and 8% (of 120) of patients."
    assert g.locate(span, {"ai": 4, "n1i": 119, "ci": 8, "n2i": 120}) is None
    ok = g.locate("four of 119 (3.4%) vs. 22 of 127 (17.3%)", {"ai": 4, "n1i": 119, "ci": 22, "n2i": 127})
    assert ok == {"ai": "four", "n1i": "119", "ci": "22", "n2i": "127"}
    assert g.locate("RR 0.33, 95% CI 0.1-1.06", {"effect": 0.33, "ci_low": 0.1, "ci_high": 1.06}) is not None
    assert g.locate("a 33% fall (RR 0.5, 0.2-0.9)", {"effect": 33}) is None


def test_plant_r1_a_signed_keep_admits_only_the_signed_numbers():
    """codex v15cenf-cap-r1 #2 (P0): KEEP / EPAR admitted by paper identity whatever the served numbers were; a
    regenerated row with other numbers would have been 'signed'. The signed value is pinned and must equal the row's."""
    import pytest
    import v15c_decisions as g
    row = {"slug": "noac-vs-warfarin-af-stroke", "id": "PMID 19717844", "outcome": "Stroke or systemic embolism",
           "served": {"effect": 0.01, "ci_low": 0.005, "ci_high": 0.02}, "proposal": {}}
    with pytest.raises(SystemExit):
        g.decide("REFUSE", row)


def test_plant_r1_an_edited_decisions_file_stops_the_build(tmp_path):
    """codex v15cenf-cap-r1 #4 (P0): only the header was checked, so an edited row passed under the original header. The
    file's sha256 is pinned in the gate (enforcement.DECISIONS_SHA256); the committed file must match it."""
    import hashlib
    import pytest
    assert hashlib.sha256(open(DEC, "rb").read()).hexdigest() == enf.DECISIONS_SHA256
    doc = json.load(open(DEC, encoding="utf-8"))
    doc["rows"][0]["served"] = {"effect": 0.01}
    p = tmp_path / "edited.json"
    p.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    with pytest.raises(enf.EnforcementError):
        enf.decisions(str(p), pinned=True)


def test_plant_r1_an_admitted_row_is_revalidated_on_every_pass(tmp_path):
    """codex v15cenf-cap-r1 #5 (P0): apply() marked an admitted row SIGNED_BINDING and a second pass skipped it, so a
    number changed after admission stayed pooled. A SIGNED_BINDING row is checked again against its snapshot."""
    t = _t("PMID 1")
    kept, absent = _apply(tmp_path, [ADMIT], [t])
    assert kept and kept[0]["endpoint_admissibility"] == "SIGNED_BINDING"
    kept[0]["effect"] = 0.81
    kept2, absent2 = _apply(tmp_path, [ADMIT], kept)
    assert kept2 == [] and "not the numbers the signed decision admitted" in absent2[0]["reason"]


def test_plant_r2_no_number_is_read_out_of_a_decimal():
    """codex v15cenf-cap-r2 #1 / agy #1 (P0): '33.3%' and '5.0%' yielded effects 33 and 5 (the regex backtracked to the
    integer part); codex #2 (P0): '0.4 of 119' yielded a count of 4 (the count started after the decimal point)."""
    import v15c_decisions as g
    assert g.locate("mortality fell by 33.3%", {"effect": 33}) is None
    assert g.locate("mortality was 5.0%", {"effect": 5.0}) is None
    assert g.locate("rates 0.4 of 119 and 0.8 of 120", {"ai": 4, "n1i": 119, "ci": 8, "n2i": 120}) is None
    assert g.locate("RR 0.33, 95% CI 0.1-1.06.", {"effect": 0.33, "ci_low": 0.1, "ci_high": 1.06}) is not None


def test_plant_r2_each_arm_needs_its_own_pair():
    """agy v15cenf-cap-r2-agy #2 (P1): one 'X of N' pair located BOTH arms when their numbers were equal -- a span naming
    one arm 'stated' the other. Each arm takes a different pair."""
    import v15c_decisions as g
    assert g.locate("10 of 100 in the intervention group", {"ai": 10, "n1i": 100, "ci": 10, "n2i": 100}) is None
    assert g.locate("10 of 100 v 10 of 100", {"ai": 10, "n1i": 100, "ci": 10, "n2i": 100}) is not None


def test_plant_r2_a_cached_unpinned_load_never_answers_a_pinned_call(tmp_path):
    """codex v15cenf-cap-r2 #3 (P0): the cache was consulted before the pin, so an edited file loaded unpinned once was
    then accepted by a pinned call. The pin is checked on every pinned call."""
    import pytest
    doc = json.load(open(DEC, encoding="utf-8"))
    doc["rows"][0]["served"] = {"effect": 0.01}
    p = tmp_path / "edited.json"
    p.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    enf.decisions(str(p), pinned=False)
    with pytest.raises(enf.EnforcementError):
        enf.decisions(str(p), pinned=True)


# Round 3 of 3 (codex v15cenf-cap-r3, agy v15cenf-cap-r3-agy; review stops at three): KNOWN LIMITS of locate, recorded,
# not fixed. None touches the three rows it admits (probiotics 15740542 / 18026577 / 18410562: distinct arms, no
# thousands separators, no percentage denominators), each also bound identically by codex, agy and the adjudicator.
import pytest  # noqa: E402


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex r3 #1, agy r3 #1): a count may start after a thousands comma "
                                       "-- '1,200 of 10,000' locates 200")
def test_known_limit_a_count_after_a_thousands_comma():
    import v15c_decisions as g
    assert g.locate("1,200 of 10,000 v 300 of 10,000", {"ai": 200, "n1i": 10000, "ci": 300, "n2i": 10000}) is None


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex r3 #2): distinct positions are not distinct ARMS -- two "
                                       "mentions of the intervention arm locate both arms")
def test_known_limit_two_mentions_of_one_arm():
    import v15c_decisions as g
    span = "In the drug group 10 of 100 died; overall, 10 of 100 drug patients died."
    assert g.locate(span, {"ai": 10, "n1i": 100, "ci": 10, "n2i": 100}) is None


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (agy r3 #2): an 'X of N%' pair is accepted as counts")
def test_known_limit_a_percentage_denominator():
    import v15c_decisions as g
    assert g.locate("4 of 50% v 8 of 60%", {"ai": 4, "n1i": 50, "ci": 8, "n2i": 60}) is None
