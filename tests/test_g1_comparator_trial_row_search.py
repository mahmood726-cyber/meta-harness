"""A comparator's per-trial row for our outcome, searched over its held text (tranexamic, 10 Oct: a WOMAN
death-due-to-bleeding row in 39461793 would give G1 a shared trial; none is printed). Synthetic fixtures + the held
texts pinned by sha256 (a control must never read a mutable artefact)."""
import hashlib
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_comparator_trial_row_search as rs  # noqa: E402

# the topic's OWN keyword list (fixed copy): it includes bare condition words that also name other outcomes
PO = {"name": "Death due to bleeding", "keywords": [
    "death due to bleeding", "death from post-partum haemorrhage", "death from postpartum haemorrhage",
    "death from post-partum hemorrhage", "death from postpartum hemorrhage", "post-partum haemorrhage",
    "postpartum haemorrhage", "postpartum hemorrhage", "primary outcome", "primary end point", "primary endpoint"]}
TRIALS = ["WOMAN", "WOMAN-2", "TRAAP", "TRAAP-2", "TXA-MFMU"]
POOLED = ("<table-wrap><table><tr><td>Death due to bleeding</td><td>WOMAN, 1 WOMAN-2, 10 TRAAP, 11 TRAAP-2, 12 and "
          "TXA-MFMU 13</td><td>159/27 307</td><td>194/27 097</td><td>0·81 (0·66–1·00)</td></tr></table></table-wrap>")


def test_PLANT_a_per_trial_row_for_our_outcome_is_found():
    jats = POOLED.replace("</table>", "<tr><td>Death due to bleeding, WOMAN</td><td>155/10 036</td><td>191/9985</td>"
                                      "<td>0·81 (0·65–1·00)</td></tr></table>")
    rows, _ = rs.search_texts(jats, "", PO, TRIALS)
    assert len(rows) == 1 and rows[0]["trial"] == "WOMAN"


def test_PLANT_the_pooled_row_naming_every_contributor_is_not_a_per_trial_row():
    rows, _ = rs.search_texts(POOLED, "", PO, TRIALS)
    assert rows == []


def test_PLANT_another_outcomes_per_trial_rows_are_not_ours():
    supp = "WOMAN Severely anxious or depressed 30/9805 29/9728 1·03 (0·62-1·71)"
    assert rs.search_texts("", supp, PO, TRIALS)[0] == []
    assert rs.search_texts("", "WOMAN death due to bleeding 155/10036 191/9985 0·81 (0·65-1·00)", PO, TRIALS)[0]


def test_PLANT_a_bare_condition_keyword_does_not_name_our_outcome():
    # 39461793 Table 2: a per-trial hysterectomy row names 'postpartum haemorrhage' (a topic keyword) -- not our outcome
    jats = ("<table-wrap><table><tr><td>Hysterectomy within 24 h (when tranexamic acid given after postpartum "
            "haemorrhage diagnosis)</td><td>WOMAN</td><td>1</td><td>303/10 036</td><td>296/9985</td>"
            "<td>1·02 (0·87–1·20)</td></tr></table></table-wrap>")
    assert rs.search_texts(jats, "", PO, TRIALS)[0] == []


def test_PLANT_a_figure_captioned_with_our_outcome_routes_to_the_dual_reader():
    _, figs = rs.search_texts("<fig><caption>Figure 4: Effect of tranexamic acid on death due to bleeding * OR=odds "
                              "ratio.</caption></fig><fig><caption>Figure 2: Effect of tranexamic acid on "
                              "life-threatening bleeding</caption></fig>", "", PO, TRIALS)
    assert [f["names_our_outcome"] for f in figs] == [True, False]


def test_printed_name_splits_a_label_from_its_citation_number_only_on_the_comparators_own_text():
    jats = "WOMAN 1 WOMAN-2 10 TRAAP 11 TRAAP-2 12 TXA-MFMU 13"
    assert [rs.printed_name(x, jats) for x in ("WOMAN1", "WOMAN-210", "TRAAP-212", "TXA-MFMU13")] == \
        ["WOMAN", "WOMAN-2", "TRAAP-2", "TXA-MFMU"]
    assert rs.printed_name("ABC12", "nothing here") == "ABC12"


HELD = {"cache/comparators/39461793/2026-09-28_kgap_jats.xml":
        "140b0395a4de4c0973f7d22e2e17041e297dc7ac323c6721edecc8abd790d3b0",
        "cache/comparators/39461793/2026-09-29_kgap_supplements.txt":
        "c41fde5791373003d030ae6f45b2a8581ce5cd3503c6c3002a62beafb11bc6e7"}


def test_the_held_tranexamic_comparator_prints_no_per_trial_bleeding_death_row():
    texts = {}
    for p, sha in HELD.items():
        f = os.path.join(ROOT, p)
        if not os.path.exists(f) or hashlib.sha256(open(f, "rb").read()).hexdigest() != sha:
            pytest.skip(f"held text {p} absent or changed: this control is pinned to sha {sha[:12]}")
        texts[p] = open(f, encoding="utf-8", errors="replace").read()
    jats, supp = texts.values()
    rows, figs = rs.search_texts(jats, supp, PO, TRIALS)
    assert rows == [] and not any(f["names_our_outcome"] for f in figs)


def test_PLANT_an_agy_shaped_log_line_is_written(tmp_path):
    # agy_call passed log_call no 'outside_workdir_reads' (codex's transcript_facts does): every REAL agy call raised
    # KeyError after the model answered, so no agy record was ever written. The agy facts shape must log.
    import inspect
    from reproducible_ai import model_call_live as mcl
    src = inspect.getsource(mcl.agy_call)
    assert '"outside_workdir_reads"' in src
    facts = {"tokens_used": 1, "tool_calls_n": 0, "tool_calls_rejected_n": 0, "tool_calls": [], "files_read": [],
             "transcript_redacted": "", "outside_workdir_reads": 0}
    p = tmp_path / "lane.jsonl"
    mcl.log_call({"record_id": "mc-test", "state": "RAN_OK", "caller": {"lane": "g1/binding"}}, facts, p)
    assert p.read_text(encoding="utf-8").count("mc-test") == 1


def test_PLANT_reader_replies_bare_or_one_fenced_block_and_quotes_must_be_in_the_text():
    assert rs._answer('{"per_trial_rows": [], "note": "x"}') == {"per_trial_rows": [], "note": "x"}
    assert rs._answer('```json\n{"per_trial_rows": [], "note": "x"}\n```\n')["per_trial_rows"] == []
    assert rs._answer('Here you go: {"per_trial_rows": []}') is None          # never a substring hunt
    shown = "Death due to bleeding | WOMAN | 155/10 036 | 191/9985"
    assert rs.gate_reader({"per_trial_rows": []}, shown) == "NO_ROW"
    assert rs.gate_reader({"per_trial_rows": [{"trial": "WOMAN", "quote": "Death due to bleeding WOMAN 155/10 036"}]},
                          shown) == "ROWS_CLAIMED"
    assert rs.gate_reader({"per_trial_rows": [{"trial": "WOMAN", "quote": "WOMAN 160/10 036"}]}, shown) == \
        "QUOTE_NOT_IN_TEXT"
