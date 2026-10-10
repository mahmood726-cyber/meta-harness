"""PLANTS for the dual-model forest-plot reader (scripts/g1_forest_reader.py) and its agy recorder
(reproducible_ai/model_call_live.agy_call). Offline: readings are constructed, model runners are fakes.

  an agreeing pair of readings whose rows reproduce the printed pool under the stated model -> ACCEPTED
  one reading perturbed in ONE row                                                           -> that row refused (both
                                                                                                readings shown), figure REFUSED
  both readings agree on a pooled row the rows do not reproduce                              -> figure REFUSED
  a one-stage IPD comparator (COMBINE AF's own wording)                                      -> REFUSED, never approximated
  rows that are outcomes, not studies                                                        -> REFUSED
  accepted rows from meta X never count toward agreement with X                              (anti-circularity)
  an agy record replays byte-identically; a model-pin mismatch or empty answer is RAN_ERROR
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as g  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

HELD_DL = "Hazard ratios were pooled with a random-effects model using the DerSimonian and Laird method."
HELD_IPD = ("We used individual patient data from the database, which includes all patients randomized in the 4 trials, "
            "to perform network meta-analyses using a stratified Cox model with random effects.")
ROWS = [("Trial A 2009", "0.66", "0.53", "0.82"), ("Trial B 2011", "0.88", "0.75", "1.03"),
        ("Trial C 2011", "0.79", "0.66", "0.95"), ("Trial D 2013", "0.87", "0.73", "1.04")]


def reading(rows=ROWS, pooled=("0.81", "0.72", "0.91"), kind="study"):
    return {"legible": True, "row_kind": kind, "measure": "Hazard ratio", "model_printed": None, "notes": "",
            "pooled": {"label": "Overall", "effect": pooled[0], "lower": pooled[1], "upper": pooled[2]},
            "rows": [{"label": a, "effect": e, "lower": lo, "upper": hi, "weight_pct": None, "events_t": None,
                      "n_t": None, "events_c": None, "n_c": None} for a, e, lo, hi in rows]}


ITEM = {"slug": "plant-topic", "pmid": "99999999", "image_sha256": "a" * 64,
        "figure": {"fig_id": "F2", "caption": "Forest plot of stroke or systemic embolism", "panel": None}}


def test_control_the_plant_pool_is_what_DL_gives_from_its_rows():
    rec = g.reconstruct([{"effect": e, "lower": lo, "upper": hi} for _, e, lo, hi in ROWS], True, "HR", ["DL"])["DL"]
    assert [f"{x:.2f}" for x in rec] == ["0.81", "0.72", "0.91"]


def test_PLANT_agreeing_readings_are_accepted_as_secondary_comparator_rows():
    v = g.judge(ITEM, reading(), reading(), "mc-a", "mc-b", HELD_DL)
    assert v["state"] == "ACCEPTED", v["problems"]
    assert v["acceptance"]["methods_reproducing"] == ["DL"]          # ONLY the stated model is tried
    assert len(v["secondary_rows"]) == 4 and not v["refused_rows"]
    r = v["secondary_rows"][0]
    assert r["provenance"] == "MODEL_PROPOSAL_DUAL:mc-a+mc-b" and r["meta_pmid"] == "99999999"
    assert (r["effect"], r["lower"], r["upper"], r["measure"]) == ("0.66", "0.53", "0.82", "HR")
    assert sm.validate(sm.SecondaryRow(**{k: v for k, v in r.items() if k in sm.SecondaryRow.__dataclass_fields__})) == []


def test_PLANT_one_perturbed_reading_never_yields_the_perturbed_number():
    # requirement since decision 5 Oct (RULE SINGLE_NUMBER): a single disputed number is settled by the row's own
    # printed effect and CI -- 0.86 does not fit Trial B's printed CI (0.75-1.03, centre 0.879), 0.88 does, so the row
    # is the PRINTED 0.88 with its basis recorded; the perturbed value never reaches a proposed row
    b = reading()
    b["rows"][1]["effect"] = "0.86"
    v = g.judge(ITEM, reading(), b, "mc-a", "mc-b", HELD_DL)
    row = next(r for r in v["proposed_rows"] if r["label"] == "Trial B 2011")
    assert row["effect"] == "0.88" and row["value_basis"].startswith(g.SINGLE_NUMBER_RESOLVED)
    assert not v["refused_rows"] and "0.86" not in [x[k] for x in v["proposed_rows"] for k in ("effect", "lower", "upper")]


def test_PLANT_same_numbers_different_label_is_LABEL_DISAGREES_and_refused():
    b = reading()
    b["rows"][2]["label"] = "Trial G 2011"           # 'Mewton' read as 'Newton': numbers agree, the trial does not
    v = g.judge(ITEM, reading(), b, "mc-a", "mc-b", HELD_DL)
    assert v["state"] == "REFUSED" and [x["why"] for x in v["refused_rows"]] == ["LABEL_DISAGREES"]
    assert v["refused_rows"][0]["label"] == "Trial C 2011 / Trial G 2011" and v["secondary_rows"] == []


def test_PLANT_a_row_only_one_reader_saw_is_refused():
    b = reading(rows=ROWS[:3])
    v = g.judge(ITEM, reading(), b, "mc-a", "mc-b", HELD_DL)
    assert v["state"] == "REFUSED" and [x["why"] for x in v["refused_rows"]] == ["ONLY_IN_READING_A"]


def test_PLANT_a_perturbed_pooled_row_refuses_the_whole_figure():
    v = g.judge(ITEM, reading(pooled=("0.78", "0.69", "0.88")), reading(pooled=("0.78", "0.69", "0.88")),
                "mc-a", "mc-b", HELD_DL)
    assert v["state"] == "REFUSED"
    assert "RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL" in v["problems"]
    assert v["secondary_rows"] == [] and len(v["proposed_rows"]) == 4      # proposed, never accepted


def test_PLANT_pooled_rows_that_disagree_refuse_the_figure():
    v = g.judge(ITEM, reading(), reading(pooled=("0.81", "0.72", "0.92")), "mc-a", "mc-b", HELD_DL)
    assert v["state"] == "REFUSED" and "POOLED_ROW_DISAGREES" in v["problems"]


def test_PLANT_a_non_stated_model_is_not_used_to_rescue_a_figure():
    """FE gives 0.81 (0.74-0.89) from these rows; a meta that STATES DerSimonian-Laird is checked against DL only."""
    fe = g.reconstruct([{"effect": e, "lower": lo, "upper": hi} for _, e, lo, hi in ROWS], True, "HR", ["FE"])["FE"]
    assert [f"{x:.2f}" for x in fe] == ["0.81", "0.74", "0.89"]
    v = g.judge(ITEM, reading(pooled=("0.81", "0.74", "0.89")), reading(pooled=("0.81", "0.74", "0.89")),
                "mc-a", "mc-b", HELD_DL)
    assert v["state"] == "REFUSED" and "RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL" in v["problems"]


def test_PLANT_one_stage_IPD_comparator_is_refused_not_approximated():
    m = g.stated_model(HELD_IPD)
    assert m["state"] == "NOT_RECONSTRUCTABLE" and "stratified Cox" in m["quotes"]["IPD"]
    v = g.judge(ITEM, reading(pooled=("0.81", "0.74", "0.89")), reading(pooled=("0.81", "0.74", "0.89")),
                "mc-a", "mc-b", HELD_IPD)
    assert v["state"] == "REFUSED" and "STATED_MODEL_NOT_RECONSTRUCTABLE" in v["problems"]


def test_control_a_negated_IPD_mention_is_not_a_one_stage_model():
    m = g.stated_model(HELD_DL + " We did not have individual patient data, so Cox models were not fitted.")
    assert m["state"] == "STATED" and m["methods"] == ["DL"]


def test_PLANT_outcome_rows_are_not_trial_rows():
    v = g.judge(ITEM, reading(kind="outcome"), reading(kind="outcome"), "mc-a", "mc-b", HELD_DL)
    assert v["state"] == "REFUSED" and any(p.startswith("ROWS_ARE_NOT_STUDIES") for p in v["problems"])
    assert v["proposed_rows"] == [] and len(v["agreed_rows_not_trials"]) == 4     # agreed, but never per-trial proposals


REAL = "spironolactone-hfref-mortality"


def _real_readings():
    """The two RECORDED readings of a real comparator figure (PMID 40959489 F4(D)), replayed from evidence/ -- offline."""
    runs = json.load(open(g.RUNS, encoding="utf-8"))
    out = {}
    for rd in ("codex", "agy"):
        k = next(k for k in runs if k.startswith(REAL + "::40959489::") and k.endswith("::" + rd))   # the comparator's
        raw, (d, why) = g.replay_reading(runs[k])
        rec = ms.load_record(os.path.join(g.REC_DIR, runs[k]["record_id"] + ".json"))
        assert why is None and ms.sha256_bytes(raw) == rec["response"]["sha256"]       # byte-identical replay
        out[rd] = (d, runs[k]["record_id"])
    return out


def _real_item():
    res = json.load(open(g.OUT, encoding="utf-8"))["results"][REAL]
    return {"slug": REAL, "pmid": res["pmid"], "image_sha256": res["image"]["sha256"], "figure": res["figure"]}


def test_REAL_FIGURE_the_two_recorded_readings_accept():
    r = _real_readings()
    v = g.judge(_real_item(), r["codex"][0], r["agy"][0], r["codex"][1], r["agy"][1], g.held_text("40959489"),
                g.model_text("40959489"))
    assert v["state"] == "ACCEPTED" and v["acceptance"]["methods_reproducing"] == ["FE"]


def test_REAL_FIGURE_PLANT_one_perturbed_reading_never_yields_the_perturbed_number():
    # since decision 5 Oct (RULE SINGLE_NUMBER): the first row's upper limit, perturbed in ONE recorded reading to 0.84,
    # does not fit that row's own printed effect and CI; the printed value does -- so the row is the PRINTED value, with
    # its basis recorded, and 0.84 is never proposed
    r = _real_readings()
    first = r["codex"][0]["rows"][0]
    b = copy.deepcopy(r["agy"][0])
    b["rows"][0]["upper"] = "0.84"
    v = g.judge(_real_item(), r["codex"][0], b, r["codex"][1], r["agy"][1], g.held_text("40959489"),
                g.model_text("40959489"))
    row = next(x for x in v["proposed_rows"] if x["label"] == first["label"])
    assert row["upper"] == first["upper"] != "0.84" and row["value_basis"].startswith(g.SINGLE_NUMBER_RESOLVED)
    assert v["state"] == "ACCEPTED" and not v["refused_rows"]


def test_REAL_FIGURE_PLANT_a_perturbed_pooled_row_refuses_the_figure():
    r = _real_readings()
    a, b = copy.deepcopy(r["codex"][0]), copy.deepcopy(r["agy"][0])
    for x in (a, b):
        x["pooled"]["effect"], x["pooled"]["lower"], x["pooled"]["upper"] = "0.74", "0.68", "0.81"
    v = g.judge(_real_item(), a, b, r["codex"][1], r["agy"][1], g.held_text("40959489"), g.model_text("40959489"))
    assert v["state"] == "REFUSED" and "RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL" in v["problems"]


def test_slash_estimand_admits_each_named_measure_and_still_refuses_others():
    row = sm.SecondaryRow(meta_pmid="1", meta_doi="", location={}, source_digest="", provenance="x", trial_label="T",
                          measure="HR", outcome_definition="All-cause mortality")
    assert sm.measure_identity(row, "RR/HR") is None
    row.measure = "OR"
    assert sm.measure_identity(row, "RR/HR") == "MEASURE_OR_IS_NOT_ESTIMAND_RR/HR"
    row.measure = "HR"
    assert sm.measure_identity(row, "RR") == "MEASURE_HR_IS_NOT_ESTIMAND_RR"            # unchanged for one estimand


def test_family_resolution_reads_a_year_glued_to_the_label():
    import secondary_meta_build as smb
    ours = [{"id": "PMID 10471456", "acronyms": ["RALES"], "label": "RALES", "author_year": None},
            {"id": "PMID 21073363", "acronyms": ["EMPHASIS-HF"], "label": "EMPHASIS-HF", "author_year": None},
            {"id": "PMID 12668699", "acronyms": ["EPHESUS"], "label": "EPHESUS", "author_year": None}]
    fam = smb.family_of_factory(ours)
    lab = lambda s: sm.SecondaryRow(meta_pmid="1", meta_doi="", location={}, source_digest="", provenance="x",  # noqa: E731
                                    trial_label=s, measure="HR", outcome_definition="d")
    assert fam(lab("RALES2000")) == "PMID 10471456"
    assert fam(lab("EMPHASIS-HF2011")) == "PMID 21073363"
    assert fam(lab("EPHESUS 2003")) == "PMID 12668699"
    assert fam(lab("RALESX")) is None                     # control: only a YEAR is split off, never letters


def test_agreement_is_within_the_printed_rounding():
    assert g.agree_value("0.80", "0.8") == "0.80"
    assert g.agree_value("0.8", "0.81") is None
    assert g.agree_value("1.03", "1.04") is None
    assert g.agree_count("1,207", "1207") == (True, 1207) and g.agree_count("12", "13")[0] is False


def test_ANTI_CIRCULARITY_accepted_rows_never_count_toward_agreement_with_their_own_meta():
    v = g.judge(ITEM, reading(), reading(), "mc-a", "mc-b", HELD_DL)
    rows = [sm.SecondaryRow(**{k: x for k, x in r.items() if k in sm.SecondaryRow.__dataclass_fields__})
            for r in v["secondary_rows"]]
    for r in rows:
        r.state = sm.VERIFIED                      # even when verified against a primary source
    assert sm.g1_countable(rows, {"99999999"}) == []
    assert len(sm.g1_countable(rows, {"12345678"})) == 4      # control: against ANOTHER comparator they may count


def test_parse_reading_fenced_and_schema_checked():
    d = reading()
    assert g.parse_reading(("```json\n" + json.dumps(d) + "\n```").encode())[0] == d
    bad = copy.deepcopy(d)
    del bad["row_kind"]
    assert g.parse_reading(json.dumps(bad).encode()) == (None, "SCHEMA:missing row_kind")
    assert g.parse_reading(b"the HR is 0.81")[1] == "NOT_JSON"


# ------------------------------------------------------------------------------------------------ the agy recorder

def _fake_agy(response, label="Gemini 3.1 Pro (High)", rc=0, status="SUCCESS"):
    def runner(prompt, schema, timeout_s, images=()):
        out = {"status": status, "response": response, "num_turns": 1, "usage": {"total_tokens": 10}, "denied_actions": []}
        log = f'I1002 x model_config_manager.go:327] Propagating selected model override to backend: label="{label}"\n'
        return {"rc": rc, "stdout": json.dumps(out).encode(), "stderr": b"", "log": log.encode(),
                "argv": ["agy", "--print", "<prompt>"]}
    return runner


def _call(runner, tmp_path):
    img = tmp_path / "fig.jpg"
    img.write_bytes(b"\xff\xd8\xff fake")
    return mcl.agy_call(b"read the figure", schema=g.SCHEMA, runner=runner, client_version="agy-test",
                        caller={"file": "tests/test_g1_forest_reader.py", "line": "1", "purpose": "plant", "lane": "test"},
                        input_digests=[{"ref": "fig", "sha256": "b" * 64}], images=(str(img),),
                        settings=("Gemini 3.1 Pro (High)", "c" * 64))


def test_agy_record_replays_byte_identically_through_write_and_load(tmp_path):
    answer = json.dumps(reading())
    rec = _call(_fake_agy(answer), tmp_path)
    assert rec["state"] == "RAN_OK" and rec["model"]["id_reported"] == "Gemini 3.1 Pro (High)"
    assert rec["model"]["provider"] == "google" and rec["client"]["name"] == "agy --print"
    p = ms.write_record(rec, tmp_path / "rec")
    again = ms.load_record(p)
    assert ms.replay(again) == answer.encode("utf-8") == ms.replay(rec)
    assert ms.write_record(again, tmp_path / "rec") == p                 # identical bytes: idempotent, never rewritten
    assert any(d["ref"] == "workdir image_0" for d in rec["input_digests"])


def test_PLANT_agy_model_pin_mismatch_is_RAN_ERROR(tmp_path):
    rec = _call(_fake_agy("{}", label="Claude Opus 4.6 (Thinking)"), tmp_path)
    assert rec["state"] == "RAN_ERROR" and "pin does not hold" in rec["error"]
    with pytest.raises(ms.ReplayRefused):
        ms.replay(rec)


def test_PLANT_agy_empty_answer_or_failed_status_is_RAN_ERROR(tmp_path):
    assert _call(_fake_agy(""), tmp_path)["state"] == "RAN_ERROR"
    assert _call(_fake_agy("{}", status="ERROR"), tmp_path)["state"] == "RAN_ERROR"
    assert _call(_fake_agy("{}", rc=1), tmp_path)["state"] == "RAN_ERROR"


def test_replay_path_reaches_no_model(monkeypatch):
    """The offline evaluation must never run a model: make every model entry point explode and evaluate."""
    def boom(*a, **k):
        raise AssertionError("a model was called on the replay path")
    monkeypatch.setattr(mcl, "call", boom)
    monkeypatch.setattr(mcl, "agy_call", boom)
    g.evaluate([], {})
    g.judge(ITEM, reading(), reading(), "mc-a", "mc-b", HELD_DL)


def test_agy_log_redaction_keeps_only_call_lines_without_paths_identity_or_settings():
    raw = "\n".join([
        r"I1 common.go:175] CLI app data directory: C:\Users\someone\.gemini\antigravity-cli",
        r"I1 cli_setting_manager.go:92] CLI settings initialized: permissions=&{Allow:[command(*)]}",
        r"I1 server_oauth.go:198] applyAuthResult: email=someone@example.org, authMethod=consumer",
        r"I1 session.go:86] Print mode: enabling terminal sandbox for this session in F:\tmp\mcall-ab12cd",
        r"I1 tool_confirmation_manager.go:211] Print mode: soft-denying tool confirmation \"Bash\" at step 2",
        r'I1 model_config_manager.go:327] Propagating selected model override to backend: label="Gemini 3.1 Pro (High)"'])
    red = mcl.agy_redact(raw)
    assert "someone" not in red and "permissions=" not in red and "mcall-ab12cd" not in red and "@" not in red
    assert "<workdir>" in red and "soft-denying" in red and 'label="Gemini 3.1 Pro (High)"' in red
    assert "<3 client-session log lines not published" in red


# ------------------------------------------------------------------------------------------------ counts and labels
COUNT_ROWS = [  # (label, events_t, n_t, events_c, n_c) -- one zero-cell study, one not estimable
    ("S1", 12, 100, 18, 100), ("S2", 8, 90, 15, 92), ("S3", 20, 150, 24, 148), ("S4", 0, 40, 3, 41), ("S5", 0, 30, 0, 30)]


def count_reading(pooled, rows=COUNT_ROWS, label="M-H, Random, 95% CI"):
    out = []
    for lab, a, n1, c, n2 in rows:
        r = {"label": lab, "events_t": a, "n_t": n1, "events_c": c, "n_c": n2}
        yv = g.counts_yv(r, "RR")
        if yv is None:
            e = lo = hi = "Not estimable"
        else:
            import math
            e, lo, hi = (f"{math.exp(yv[0] + s * 1.959963984540054 * math.sqrt(yv[1])):.2f}" for s in (0, -1, 1))
        out.append({"label": lab, "effect": e, "lower": lo, "upper": hi, "weight_pct": None,
                    "events_t": str(a), "n_t": str(n1), "events_c": str(c), "n_c": str(n2)})
    return {"legible": True, "row_kind": "study", "measure": "Risk Ratio", "model_printed": label, "notes": "",
            "pooled": {"label": "Total (95% CI)", "effect": pooled[0], "lower": pooled[1], "upper": pooled[2]}, "rows": out}


def _mhre():
    rows = [{"events_t": a, "n_t": n1, "events_c": c, "n_c": n2} for _, a, n1, c, n2 in COUNT_ROWS]
    return [f"{x:.2f}" for x in g.reconstruct(rows, True, "RR", ["MH-RE"])["MH-RE"]]


def test_PLANT_count_rows_accept_under_the_figures_own_MH_random_label():
    p = _mhre()
    v = g.judge(ITEM, count_reading(p), count_reading(p), "mc-a", "mc-b", "Random-effects (DerSimonian-Laird).")
    assert v["state"] == "ACCEPTED", v["problems"]
    assert v["stated_model"]["methods"] == ["MH-RE"] and v["stated_model"]["quotes"]["FIGURE_LABEL"].startswith("M-H")


def test_PLANT_a_count_misread_is_caught_by_the_rows_own_printed_effect():
    """Both readers agree on a wrong count: the row's printed RR no longer follows from its counts -> refused."""
    p = _mhre()
    a, b = count_reading(p), count_reading(p)
    for r in (a, b):
        r["rows"][0]["events_t"] = "21"                 # printed RR stays the one 12/100 gives
    v = g.judge(ITEM, a, b, "mc-a", "mc-b", "")
    assert v["state"] == "REFUSED" and any(x.startswith("ROW_COUNTS_DO_NOT_GIVE_PRINTED") for x in v["problems"])


def test_PLANT_a_label_naming_another_model_refuses():
    p = _mhre()
    v = g.judge(ITEM, count_reading(p, label="M-H, Fixed, 95% CI"), count_reading(p, label="M-H, Fixed, 95% CI"),
                "mc-a", "mc-b", "")
    assert v["state"] == "REFUSED" and "RECONSTRUCTION_DOES_NOT_REPRODUCE_PRINTED_POOL" in v["problems"]


def test_revman_label_mapping_and_thousands_separators():
    assert g.revman_label("IV, Fixed, 95% CI") == ["FE"] and g.revman_label("IV, Random, 95% CI") == ["DL"]
    assert g.revman_label("M-H, Random, 95% CI") == ["MH-RE"] and g.revman_label("Peto, Fixed") is None
    assert g.agree_count("10 637", "10637") == (True, 10637)


def test_stated_model_reads_typographic_hyphens_and_inverse_variance_weighting():
    cochrane = "We used OR using the Mantel‐Haenszel method. We employed a fixed‐effect model in the analysis."
    assert g.stated_model(cochrane)["methods"] == ["FE", "MH-FE"]
    jama = "Treatment effects in individual trials were pooled using inverse variance–weighted meta-analysis."
    assert g.stated_model(jama)["methods"] == ["FE"]
    assert g.stated_model("We did a systematic review.")["state"] == "NOT_STATED"


PAGE = """<html><body><article><section class="abstract"><p>We pooled odds ratios with a fixed-effect model.</p></section>
<p>Methods text.</p>
<figure id="f1"><h3>Figure 1. Flow diagram</h3><img src="https://cdn.ncbi.nlm.nih.gov/pmc/blobs/aa/1/bb/x-g001.jpg"></figure>
<figure id="f2"><h3>Figure 2. Association Between Drug and Mortality in Each Trial</h3>
<img src="https://cdn.ncbi.nlm.nih.gov/pmc/blobs/aa/1/cc/x-g002.jpg"><a href="#">Open in a new tab</a></figure>
<section class="ref-list"><figure id="ref-fig"><img src="https://cdn.ncbi.nlm.nih.gov/pmc/blobs/aa/1/dd/r.jpg"></figure></section>
</article></body></html>"""


def test_pmc_page_is_stored_and_a_jats_like_file_derived_with_figures_and_model_text(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "COMP", str(tmp_path))
    d = tmp_path / "11111111"
    d.mkdir()
    (d / f"{g.FETCH_DATE}_forest_pmcpage.html").write_bytes(PAGE.encode("utf-8"))   # held page: no network
    out = g.pmc_page_jats("11111111", "PMC1")
    assert out and out.endswith("_forest_pmcpage_jats.xml") and g.jats_path("11111111") == out
    import xml.etree.ElementTree as ET
    root = ET.parse(out).getroot()
    figs = {f.get("id"): (" ".join("".join(c.itertext()) for c in f.iter("caption")),
                          f.find(".//graphic").get("{http://www.w3.org/1999/xlink}href")) for f in root.iter("fig")}
    assert set(figs) == {"f1", "f2"}                           # the reference-list figure is not the article's
    assert figs["f2"] == ("Figure 2. Association Between Drug and Mortality in Each Trial", "x-g002.jpg")
    assert len(root.get("derived-from-sha256")) == 64
    assert g.stated_model(g.model_text("11111111"))["methods"] == ["FE"]


def test_a_target_refused_before_reading_needs_its_caption_to_match(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "COMP", str(tmp_path))
    d = tmp_path / "22222222"
    d.mkdir()
    (d / "2026-10-02_kgap_jats.xml").write_text(
        '<article xmlns:xlink="http://www.w3.org/1999/xlink"><body><fig id="F1"><caption><p>A: Fatal MI; B: stroke'
        '</p></caption><graphic xlink:href="f1.jpg"/></fig></body></article>', encoding="utf-8")
    monkeypatch.setitem(g.TARGETS, "plant-slug::22222222", {"fig_id": "F1", "caption_has": "A: Fatal MI", "refuse": "NO_PANEL"})
    assert g.figure_for("plant-slug", "22222222") == (None, "REFUSED_BEFORE_READING:NO_PANEL")
    monkeypatch.setitem(g.TARGETS, "plant-slug::22222222", {"fig_id": "F1", "caption_has": "MACE", "refuse": "NO_PANEL"})
    assert g.figure_for("plant-slug", "22222222") == (None, "TARGET_CAPTION_MISMATCH")      # a target is never trusted


def test_accepted_rows_take_comparator_and_other_metas_of_the_topic_only(tmp_path, monkeypatch):
    row = lambda pm: {"meta_pmid": pm, "trial_label": "T " + pm}  # noqa: E731
    out = {"results": {"topic-a": {"state": "ACCEPTED", "pmid": "1", "secondary_rows": [row("1")]}},
           "meta_results": {"topic-a::2": {"slug": "topic-a", "state": "ACCEPTED", "secondary_rows": [row("2")]},
                            "topic-a::3": {"slug": "topic-a", "state": "REFUSED", "secondary_rows": []},
                            "topic-b::4": {"slug": "topic-b", "state": "ACCEPTED", "secondary_rows": [row("4")]}}}
    p = tmp_path / "out.json"
    p.write_text(json.dumps(out), encoding="utf-8")
    monkeypatch.setattr(g, "OUT", str(p))
    assert sorted(r["meta_pmid"] for r in g.accepted_rows("topic-a")) == ["1", "2"]
    assert [r["meta_pmid"] for r in g.accepted_rows("topic-b")] == ["4"]


def test_footnote_superscripts_repeated_labels_and_NA_rows():
    a = reading(rows=[("REMAP-CAPᵈ", "0.64", "0.47", "0.87"), ("REMAP-CAPᵈ", "0.66", "0.42", "1.04"),
                      ("TOCOVID", "NAᵇ", "NAᵇ", "NAᵇ")])
    b = reading(rows=[("REMAP-CAPd", "0.64", "0.47", "0.87"), ("REMAP-CAPd", "0.66", "0.42", "1.04"),
                      ("TOCOVID", "NAb", "NAb", "NAb")])
    proposed, refused, pooled, probs, ne = g.agree(a, b)
    assert refused == [] and [r["effect"] for r in proposed] == ["0.64", "0.66"]       # matched by occurrence
    assert [r["label"] for r in ne] == ["TOCOVID"]                                       # agreed, never pooled


def test_a_signed_number_is_a_number_and_background_IPD_is_not_the_metas_model():
    assert g._num("+0.50") == 0.5 and g._num("-1.87") == -1.87
    t = ("Recent efforts have also leveraged individual participant data to reassess signals. Hazard ratios were "
         "estimated with Cox models in the trials. We pooled mean differences with a random-effects model.")
    assert g.stated_model(t)["state"] == "STATED"


def test_printed_bounds_and_double_zero_NA_rows_with_counts():
    assert g.printed_matches(0.003, "<0.01") and not g.printed_matches(0.02, "<0.01")
    assert g.printed_matches(120.0, ">100") and g.printed_matches(0.866, "0.87") and not g.printed_matches(0.86, "0.87")
    # REACT: 0/26 vs 0/13 printed 'NA' with no CI -- both readers agree; counts say not estimable; never pooled
    na = {"label": "COVIDSTORM", "effect": "NAᵇ", "lower": None, "upper": None, "weight_pct": None,
          "events_t": "0", "n_t": "26", "events_c": "0", "n_c": "13"}
    nb = dict(na, effect="NAb")
    a, b = reading(), reading()
    a["rows"].append(na)
    b["rows"].append(nb)
    proposed, refused, pooled, probs, ne = g.agree(a, b)
    assert refused == [] and [r["label"] for r in proposed][-1] == "COVIDSTORM"
    row = proposed[-1]
    assert g.row_problems(row, True, "OR") == [] and g.counts_yv(row, "OR") is None


def test_label_from_the_metas_own_references_only_when_exactly_one_is_cited():
    refs = "Heathcote 2013: Heathcote L, et al. Metformin and clomiphene. Mewton N, Roubille F. Colchicine 2019."
    assert g.label_from_references("Hemmings?", "Heathcote 2013", refs)["label"] == "Heathcote 2013"
    assert g.label_from_references("Newton N–2019", "Mewton N-2019", refs)["label"] == "Mewton N-2019"
    assert g.label_from_references("Smith 2010", "Jones 2011", refs) is None             # neither cited
    assert g.label_from_references("Heathcote 2013", "Mewton 2019", refs) is None        # both cited: undecided


def test_PLANT_a_label_resolved_by_references_lets_the_row_count(monkeypatch):
    monkeypatch.setattr(g, "ref_text", lambda pmid: "Trial C 2011. Cited trials: Trial A, Trial B, Trial C, Trial D.")
    b = reading()
    b["rows"][2]["label"] = "Xrial C 2011"           # reader B misreads the label; numbers agree
    v = g.judge(ITEM, reading(), b, "mc-a", "mc-b", HELD_DL)
    assert v["state"] == "ACCEPTED", v["problems"]
    row = next(r for r in v["proposed_rows"] if r["label"] == "Trial C 2011")
    assert row["label_basis"].startswith("LABEL_FROM_META_REFERENCES")


def test_mantel_haenszel_wording_names_the_MH_variant_for_counts_and_is_dropped_otherwise():
    cochrane = "We used OR using the Mantel-Haenszel method. We employed a fixed-effect model in the analysis."
    assert g.stated_model(cochrane, measure="OR")["methods"] == ["MH-FE"]        # never plain IV 'FE' as well
    assert g.stated_model(cochrane, measure="MD")["methods"] == ["FE"]           # M-H cannot apply without counts
    mixed = "Dichotomous: Mantel-Haenszel random-effects; continuous: inverse variance random-effects (DerSimonian-Laird)."
    assert g.stated_model(mixed, measure="RR")["methods"] == ["MH-RE"]
    assert g.stated_model(mixed, measure="MD")["methods"] == ["DL"]


def test_a_typographic_minus_agrees_and_comes_back_as_an_ascii_number():
    assert g.agree_value("−0.22", "-0.22") == "-0.22"
    assert g.agree_value("−0.22", "−0.22") == "-0.22"
    assert g.agree_value("−0.22", "-0.23") is None


def test_a_label_naming_fixed_and_random_states_both_and_jats_references_keep_word_boundaries(tmp_path, monkeypatch):
    assert g.revman_label("MH, Fixed + Random, 95% CI") == ["MH-FE", "MH-RE"]
    assert g.revman_label("IV, Random, 95% CI") == ["DL"]
    monkeypatch.setattr(g, "COMP", str(tmp_path))
    d = tmp_path / "33333333"
    d.mkdir()
    (d / "2026-10-02_kgap_jats.xml").write_text(
        "<article><back><ref-list><ref><person-group><name><surname>Mewton</surname><given-names>N</given-names>"
        "</name></person-group></ref></ref-list></back></article>", encoding="utf-8")
    assert g.label_from_references("Newton N–2019", "Mewton N-2019", g.ref_text("33333333"))["label"] == "Mewton N-2019"


def test_a_typographic_minus_in_a_printed_row_value_is_compared_as_a_number():
    # the PMID sweep crashed in printed_matches on '−0.22' (fp._close floats the raw string)
    assert g.printed_matches(-0.22, "−0.22")
    assert not g.printed_matches(0.22, "−0.22")


def test_oa_probe_tries_every_open_location_and_takes_a_repository_pdf(tmp_path, monkeypatch):
    # the publisher copy is bot-gated (recorded, not solved); the repository's author copy is a plain PDF
    from harness import http
    os.makedirs(tmp_path / "cache" / "t", exist_ok=True)
    (tmp_path / "cache" / "t" / "comparators.json").write_text(json.dumps([{"citation": "X (2020); J; DOI 10.1/x; PMID 1"}]))
    monkeypatch.setattr(g, "ROOT", str(tmp_path))
    monkeypatch.setattr(g, "COMP", str(tmp_path / "comp"))
    upw = {"is_oa": True, "oa_status": "bronze",
           "best_oa_location": {"host_type": "publisher", "url_for_pdf": "https://pub/x.pdf"},
           "oa_locations": [{"host_type": "publisher", "url_for_pdf": "https://pub/x.pdf"},
                            {"host_type": "repository", "url_for_pdf": "https://repo/x.pdf"}]}

    def get_raw(url, *a, **k):
        if "unpaywall" in url:
            return 200, json.dumps(upw).encode()
        if url.startswith("https://pub"):
            raise RuntimeError("403 challenge")
        return 200, b"%PDF-1.7 ..."
    monkeypatch.setattr(http, "get_raw", get_raw)
    o = g.oa_probe("t", "1", True)
    assert [x["fetch"][:7] for x in o["locations"]] == ["REFUSED", "PDF"]
    assert o["state"] == "OPEN_PDF"


def test_topic_retry_note_names_the_review_and_suggests_no_value():
    n = g.topic_note("colchicine-secondary-cv-prevention::40889093")
    assert "Colchicine vs placebo for secondary prevention of cardiovascular events" in n
    assert "legible=false" in n and not any(ch.isdigit() for ch in n.replace("Colchicine", ""))
    # every frozen key names a topic file (a missing one would crash the run, not silently drop the note)
    assert all(os.path.exists(os.path.join(g.ROOT, "topics", k.split("::")[0] + ".json")) for k in g.TOPIC_RETRY)


def test_comparator_extra_figures_are_comparator_role_with_their_own_keys():
    its, skipped = g.items([], False, extras=sorted(g.COMPARATOR_EXTRA))
    assert not skipped
    keys = {it["key"] for it in its}
    assert "spironolactone-hfref-mortality::40959489::F2D" in keys
    assert all(it["role"] == "comparator" and it["pmid"] == g.comparator_of(it["slug"]) for it in its)
    # an extra never shadows the topic's main comparator result (keyed by the bare slug)
    assert not keys & set(g.COMPARATOR_EXTRA)


def test_a_second_concurrent_run_is_refused_by_the_ledger_lock(tmp_path):
    ledger = str(tmp_path / "runs.json")
    with g.RunLock(ledger):
        with pytest.raises(SystemExit):
            with g.RunLock(ledger):
                pass
    with g.RunLock(ledger):                  # released on exit: a later run proceeds
        pass


def test_trial_rows_printed_at_99_percent_reconstruct_only_when_the_level_is_declared():
    # two trials (log SE 0.09, 0.08) printed with 99% CIs (z=2.576): fixed effect gives 0.80 (0.71-0.90) at 95%
    import math
    rows = []
    for e, se in ((0.78, 0.09), (0.82, 0.08)):
        y = math.log(e)
        rows.append({"label": f"T{e}", "effect": f"{e:.2f}", "lower": f"{math.exp(y - 2.5758 * se):.2f}",
                     "upper": f"{math.exp(y + 2.5758 * se):.2f}"})
    fe = g.reconstruct(rows, True, "RR", ["FE"], row_z=2.5758293035489004)["FE"]
    assert abs(fe[1] - 0.713) < 0.006 and abs(fe[2] - 0.902) < 0.006
    wrong = g.reconstruct(rows, True, "RR", ["FE"])["FE"]          # read as 95%: too wide (log width x 1.31)
    assert wrong[1] < 0.69 and wrong[2] > 0.93


def test_a_row_ci_level_is_refused_unless_the_caption_states_it(monkeypatch):
    t = dict(g.TARGETS["omega3-cardiovascular-events::29387889"], row_ci_level=90)
    monkeypatch.setitem(g.TARGETS, "omega3-cardiovascular-events::29387889", t)
    assert g.figure_for("omega3-cardiovascular-events", "29387889")[1] == "TARGET_ROW_CI_LEVEL_NOT_IN_CAPTION"


def _docx(paras):
    """A minimal Word file: paras = [('text', None) | ('', image_bytes)]."""
    import io as _io
    import zipfile
    body, rels, media = [], [], {}
    for i, (tx, img) in enumerate(paras):
        if img is None:
            body.append(f"<w:p><w:r><w:t>{tx}</w:t></w:r></w:p>")
        else:
            rid = f"rId{100 + i}"
            rels.append(f'<Relationship Id="{rid}" Type="image" Target="media/image{i}.png"/>')
            media[f"word/media/image{i}.png"] = img
            body.append(f'<w:p><w:r><w:drawing><a:blip r:embed="{rid}"/></w:drawing></w:r></w:p>')
    b = _io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("word/document.xml", "<w:document><w:body>" + "".join(body) + "</w:body></w:document>")
        z.writestr("word/_rels/document.xml.rels", "<Relationships>" + "".join(rels) + "</Relationships>")
        for k, v in media.items():
            z.writestr(k, v)
    return b.getvalue()


def test_a_word_supplement_figure_is_the_image_under_its_caption_and_nothing_else(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "COMP", str(tmp_path))
    os.makedirs(tmp_path / "1")
    sp = str(tmp_path / "1" / "x_forest_supp_s.docx")
    open(sp + ".meta.json", "w").write(json.dumps({"url": "u", "sha256": "h"}))
    t = {"supplement": "s.docx", "caption_has": "Figure S3 MACE by trial"}
    good = _docx([("Figure S3 MACE by trial", None), ("", b"\x89PNG-one"), ("Figure S4 other", None), ("", b"\x89PNG-two")])
    fig, why = g.docx_figure("1", t, sp, good)
    assert why == "SELECTED" and open(os.path.join(str(tmp_path), "1", next(
        f for f in os.listdir(tmp_path / "1") if f.endswith(fig["href"]))), "rb").read() == b"\x89PNG-one"
    # another figure's caption before any image: the image is not this figure's
    bad = _docx([("Figure S3 MACE by trial", None), ("Figure S4 other", None), ("", b"\x89PNG-two")])
    assert g.docx_figure("1", t, sp, bad)[1] == "TARGET_IMAGE_NOT_UNDER_CAPTION"
    assert g.docx_figure("1", dict(t, caption_has="absent words"), sp, good)[1] == "TARGET_CAPTION_MISMATCH"


def test_rows_agreed_but_no_printed_pool_are_marked_second_source_only_never_accepted():
    # tocilizumab meta 35802687 (decision 5 Oct): 14 trial rows agreed by both recorded readings, no pooled row printed
    runs = json.load(open(g.RUNS, encoding="utf-8"))
    ra = runs["tocilizumab-covid19-mortality::35802687::pone.0270668.g003::codex"]
    rb = runs["tocilizumab-covid19-mortality::35802687::pone.0270668.g003::agy"]
    (_, (da, _)), (_, (db, _)) = g.replay_reading(ra), g.replay_reading(rb)
    item = {"pmid": "35802687", "figure": {"fig_id": "pone.0270668.g003", "caption": "c"}, "image_sha256": "x"}
    v = g.judge(item, da, db, ra["record_id"], rb["record_id"], g.held_text("35802687"), g.model_text("35802687"))
    assert v["state"] == g.SECOND_SOURCE_ONLY != "ACCEPTED"
    assert len(v["secondary_rows"]) == 14
    assert all(any(f.startswith(sm.POOL_UNCHECKABLE) for f in r["findings"]) for r in v["secondary_rows"])
    # a figure that repeats a trial label (one block per outcome, e.g. GLP-1 meta 30223891: MI / stroke / HHF / MACE)
    # is not ONE analysis: its rows cannot be second-source rows for any single outcome, so it stays refused
    dup_a, dup_b = copy.deepcopy(da), copy.deepcopy(db)
    dup_a["rows"].append(dict(dup_a["rows"][0]))
    dup_b["rows"].append(dict(dup_b["rows"][0]))
    assert g.judge(item, dup_a, dup_b, "a", "b", "", "")["state"] == "REFUSED"
    # a figure whose readers DISAGREE on the pool is still refused outright
    db2 = copy.deepcopy(db)
    db2["pooled"] = {"label": "Total", "effect": "0.80", "lower": "0.70", "upper": "0.92"}
    assert g.judge(item, da, db2, "a", "b", "", "")["state"] == "REFUSED"


def _rd(rows, pooled=("0.95", "0.80", "1.13")):
    return {"legible": True, "row_kind": "study", "measure": "RR", "model_printed": None, "notes": "",
            "rows": rows, "pooled": {"label": "Total", "effect": pooled[0], "lower": pooled[1], "upper": pooled[2]}}


_ITEM = {"pmid": "1", "figure": {"fig_id": "F", "caption": "c"}, "image_sha256": "x"}


def test_rule_single_number_a_disputed_count_is_settled_by_the_rows_own_effect_and_ci():
    # decision 5 Oct: 28 / 29 control deaths; only 28 gives the printed RR 1.01 (0.68-1.52) from 58/294 vs 28/144
    base = {"label": "NCT04320615", "effect": "1.01", "lower": "0.68", "upper": "1.52",
            "events_t": "58", "n_t": "294", "events_c": "28", "n_c": "144"}
    other = {"label": "T2", "effect": "0.90", "lower": "0.62", "upper": "1.31"}
    v = g.judge(_ITEM, _rd([base, other]), _rd([dict(base, events_c="29"), other]), "a", "b", "", "fixed-effect")
    row = next(r for r in v["proposed_rows"] if r["label"] == "NCT04320615")
    assert row["events_c"] == 28 and row["value_basis"].startswith(g.SINGLE_NUMBER_RESOLVED)
    assert not v["refused_rows"]


def test_rule_single_number_a_dropped_decimal_is_settled_by_the_interval():
    r1 = {"label": "Lescure", "effect": "0.97", "lower": "0.41", "upper": "2.32"}
    other = {"label": "T2", "effect": "0.90", "lower": "0.62", "upper": "1.31"}
    v = g.judge(_ITEM, _rd([r1, other]), _rd([dict(r1, upper="232"), other]), "a", "b", "", "fixed-effect")
    assert next(r for r in v["proposed_rows"] if r["label"] == "Lescure")["upper"] == "2.32"


def test_rule_single_number_both_candidates_fitting_is_unresolved():
    r1 = {"label": "Einvik 2010", "effect": "0.89", "lower": "0.55", "upper": "1.45"}
    other = {"label": "T2", "effect": "0.90", "lower": "0.62", "upper": "1.31"}
    v = g.judge(_ITEM, _rd([r1, other]), _rd([dict(r1, upper="1.44"), other]), "a", "b", "", "fixed-effect")
    assert [r["why"] for r in v["refused_rows"]] == [f"{g.SINGLE_NUMBER_UNRESOLVED}:UPPER"]
    assert v["state"] == "REFUSED"


def test_rule_weights_the_printed_weights_gate_a_no_pool_figure_and_a_wrong_weight_refuses_it():
    runs = json.load(open(g.RUNS, encoding="utf-8"))
    ra = runs["tocilizumab-covid19-mortality::35802687::pone.0270668.g003::codex"]
    rb = runs["tocilizumab-covid19-mortality::35802687::pone.0270668.g003::agy"]
    (_, (da, _)), (_, (db, _)) = g.replay_reading(ra), g.replay_reading(rb)
    item = {"pmid": "35802687", "figure": {"fig_id": "pone.0270668.g003", "caption": "c"}, "image_sha256": "x"}
    v = g.judge(item, da, db, "a", "b", "", "")
    assert v["state"] == g.SECOND_SOURCE_ONLY
    assert all(g.WEIGHTS_REPRODUCED in " ".join(r["findings"]) for r in v["secondary_rows"])
    da2, db2 = copy.deepcopy(da), copy.deepcopy(db)
    for d in (da2, db2):
        next(r for r in d["rows"] if r["label"] == "RECOVERY")["weight_pct"] = "40.00"   # both agree, both wrong
    v2 = g.judge(item, da2, db2, "a", "b", "", "")
    assert v2["state"] == "REFUSED" and g.WEIGHTS_NOT_REPRODUCED in v2["problems"]


def test_rule_single_number_an_omitted_value_is_not_a_disagreement_and_stays_unresolved():
    # one reader printing nothing is not a second READING of the number: never settled (decision 5 Oct, kept literal)
    base = {"label": "NCT04320615", "effect": "1.01", "lower": "0.68", "upper": "1.52",
            "events_t": "58", "n_t": "294", "events_c": "28", "n_c": "144"}
    other = {"label": "T2", "effect": "0.90", "lower": "0.62", "upper": "1.31"}
    v = g.judge(_ITEM, _rd([base, other]), _rd([dict(base, events_c=None), other]), "a", "b", "", "fixed-effect")
    assert [r["why"] for r in v["refused_rows"]] == [f"{g.SINGLE_NUMBER_UNRESOLVED}:EVENTS_C"]


def test_PLANT_agy_real_call_path_writes_its_lane_log_line(tmp_path, monkeypatch):
    """A REAL agy call is logged through log_call, which requires `outside_workdir_reads` (redaction commit 07cbbc6cb).
    The agy facts lacked it, so every real call raised KeyError AFTER the model answered: the call ran and no record was
    written. The fake runners above never reach log_call (`runner is agy_runner` is False), which is why no test saw it.
    Here the fake is installed AS agy_runner so the real-call branch runs."""
    monkeypatch.setattr(mcl, "agy_runner", _fake_agy(json.dumps(reading())))
    monkeypatch.setattr(mcl, "LANE_LOG_DIR", tmp_path / "lane_log")
    img = tmp_path / "fig.jpg"
    img.write_bytes(b"\xff\xd8\xff fake")
    rec = mcl.agy_call(b"read the figure", schema=g.SCHEMA, client_version="agy-test",
                       caller={"file": "tests/test_g1_forest_reader.py", "line": "1", "purpose": "plant", "lane": "test"},
                       input_digests=[{"ref": "fig", "sha256": "b" * 64}], images=(str(img),),
                       settings=("Gemini 3.1 Pro (High)", "c" * 64))
    assert rec["state"] == "RAN_OK"
    lines = [json.loads(l) for p in (tmp_path / "lane_log").glob("*.jsonl") for l in p.read_text().splitlines()]
    assert len(lines) == 1 and lines[0]["record_id"] == rec["record_id"]
    assert lines[0]["outside_workdir_reads"] is None          # not observable for agy: None, never a made-up 0
