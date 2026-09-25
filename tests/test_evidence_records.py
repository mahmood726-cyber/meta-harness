"""The evidence-record verifier must be able to FAIL. Every plant is synthetic (tmp files), so the controls
cannot retire themselves when a real source or record changes. Each plant is paired with the clean record it
mutates, and the clean record must verify first -- otherwise a red plant proves nothing."""
import copy, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "evidence", "scripts"))
import verify_records as V

ABSTRACT = ("TRIAL-X randomized 1,000 adults with heart failure and ejection fraction below 40%. Patients were "
            "assigned to drug A 10 mg daily or placebo. The primary end point was cardiovascular death. "
            "Over a median follow-up of 2.0 years, the hazard ratio was 0.82 (95% CI, 0.70 to 0.96). "
            "All analyses were intention-to-treat.")


def _setup(tmp_path, served=0.82):
    src = tmp_path / "abs.txt"
    src.write_text(ABSTRACT, encoding="utf-8")
    ref = str(src)
    packet = {"sources": [{"ref": ref, "text": ABSTRACT}],
              "served_row": {"effect": served, "ci_low": 0.70, "ci_high": 0.96, "scale": "HR"}}
    f = lambda s: {"ref": ref, "span": s}
    rec = {"verdict": "BOUND", "fields": {
        "population": f("randomized 1,000 adults with heart failure and ejection fraction below 40%"),
        "endpoint": f("The primary end point was cardiovascular death."),
        "estimate": f("the hazard ratio was 0.82 (95% CI, 0.70 to 0.96)"),
        "ci": f("the hazard ratio was 0.82 (95% CI, 0.70 to 0.96)"),
        "analysis_set": f("All analyses were intention-to-treat."),
        "treatment_strategy": f("assigned to drug A 10 mg daily or placebo"),
        "follow_up": f("median follow-up of 2.0 years")},
        "bound_values": {"scale": "HR", "estimate": "0.82", "ci_low": "0.70", "ci_high": "0.96"}}
    return rec, packet, src


def test_clean_record_verifies_and_matches(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    r = V.verify(rec, pk)
    assert r["errors"] == [] and r["served_compare"]["state"] == "MATCH"


def test_one_character_changed_in_a_span_is_refused(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    assert V.verify(rec, pk)["errors"] == []
    rec["fields"]["population"]["span"] = rec["fields"]["population"]["span"].replace("1,000", "1,001")
    assert any("population: span not found" in e for e in V.verify(rec, pk)["errors"])


def test_ref_outside_the_packet_is_refused(tmp_path):
    rec, pk, src = _setup(tmp_path)
    other = tmp_path / "other.txt"; other.write_text(ABSTRACT, encoding="utf-8")
    rec["fields"]["endpoint"]["ref"] = str(other)
    assert any("not a source in the packet" in e for e in V.verify(rec, pk)["errors"])


def test_bound_number_not_printed_in_span_is_refused(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["bound_values"]["estimate"] = "0.80"
    assert any("bound_values.estimate" in e for e in V.verify(rec, pk)["errors"])


def test_changed_source_bytes_are_refused_against_a_pinned_sha(tmp_path):
    rec, pk, src = _setup(tmp_path)
    pinned = V.verify(rec, pk)["spans"]
    src.write_text(ABSTRACT + " ", encoding="utf-8")   # same rendered text, different bytes
    assert any("sha256 changed" in e for e in V.verify(rec, pk, pinned)["errors"])


def test_bound_verdict_without_a_ci_span_is_refused(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["fields"]["ci"] = None
    rec["bound_values"].pop("ci_low"); rec["bound_values"].pop("ci_high")
    assert any("core fields unbound" in e for e in V.verify(rec, pk)["errors"])


def test_served_value_differing_from_the_bound_span_is_reported_not_hidden(tmp_path):
    rec, pk, _ = _setup(tmp_path, served=0.68)
    r = V.verify(rec, pk)
    assert r["errors"] == [] and r["served_compare"]["state"] == "DIFFERS"


def test_a_number_on_another_scale_is_never_compared_as_the_served_number(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    pk["served_row"] = {"effect": 0.82, "ci_low": 0.70, "ci_high": 0.96, "scale": "RR"}
    r = V.verify(rec, pk)   # the span holds an HR of 0.82; the served RR of 0.82 must NOT read as a MATCH
    assert r["served_compare"]["state"] == "NOT_COMPARABLE"


def test_served_arm_counts_are_compared_count_for_count(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["bound_values"] = {"events_t": "0.82", "n_t": "0.70", "events_c": "0.96", "n_c": "0.82"}  # printed tokens
    pk["served_row"] = {"ai": 0.82, "n1i": 0.70, "ci": 0.96, "n2i": 0.82}
    assert V.verify(rec, pk)["served_compare"]["state"] == "MATCH"
    pk["served_row"]["ci"] = 0.95
    assert V.verify(rec, pk)["served_compare"]["state"] == "DIFFERS"


def test_served_arm_means_in_either_field_shape_are_compared(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["bound_values"] = {"mean_t": "0.82", "sd_t": "0.70", "n_t": "0.96", "mean_c": "0.70", "sd_c": "0.96", "n_c": "0.82"}
    pk["served_row"] = {"mean1": 0.82, "sd1": 0.70, "nc1": 0.96, "mean2": 0.70, "sd2": 0.96, "nc2": 0.82}
    assert V.verify(rec, pk)["served_compare"]["state"] == "MATCH"
    pk["served_row"]["nc2"] = 0.96          # a denominator that is not the one the span prints
    assert V.verify(rec, pk)["served_compare"]["state"] == "DIFFERS"


# ---- adjudications: a confirmation must be checkable against the served numbers
import adjudicate as A


def test_confirmation_refused_when_served_numbers_are_not_in_the_cited_spans(tmp_path):
    served = {"effect": 0.82, "ci_low": 0.70, "ci_high": 0.96}
    ok = {"evidence": {"e": {"span": "hazard ratio was 0.82 (95% CI, 0.70 to 0.96)"}}}
    assert A.confirm_check(ok, served) is None
    bad = {"evidence": {"e": {"span": "hazard ratio was 0.82 (95% CI, 0.70 to 0.97)"}}}
    assert "not printed" in A.confirm_check(bad, served)


def test_confirmation_by_derivation_must_equal_the_served_numbers():
    served = {"effect": 0.44, "ci_low": 0.27, "ci_high": 0.73}
    assert A.confirm_check({"derivation": {"result": [0.44, 0.27, 0.73]}}, served) is None
    assert "!=" in A.confirm_check({"derivation": {"result": [0.44, 0.27, 0.74]}}, served)


def test_trailing_zero_is_the_same_number_but_a_different_number_is_not(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["bound_values"]["ci_low"] = "0.7"          # span prints 0.70
    assert V.verify(rec, pk)["errors"] == []
    rec["bound_values"]["ci_low"] = "0.71"
    assert any("ci_low" in e for e in V.verify(rec, pk)["errors"])


def test_a_comma_between_two_limits_is_not_a_thousands_separator(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["fields"]["estimate"]["span"] = rec["fields"]["ci"]["span"] = "the hazard ratio was 0.82 (95% CI, 0.70 to 0.96)"
    assert V.num_tokens("(0.44,0.73)") == {"0.44", "0.73"}
    import re as _re
    assert V.num_tokens(_re.sub(r"(?<=\d)[,\u2009 ](?=\d{3}\b)", "", "11,052 patients (0.44,0.73)")) == {"11052", "0.44", "0.73"}


def test_registry_render_is_append_only_a_pinned_prefix_never_moves(tmp_path):
    """A span bound against an earlier render must stay a substring: the v1 text of a synthetic record is pinned
    and must remain a PREFIX of the current render (additions go after it)."""
    import textrep
    rec = {"protocolSection": {"identificationModule": {"nctId": "NCT00000000", "briefTitle": "T"},
                               "eligibilityModule": {"eligibilityCriteria": "Adults"}},
           "resultsSection": {"outcomeMeasuresModule": {"outcomeMeasures": [{
               "type": "PRIMARY", "title": "Weight", "dispersionType": "Standard Deviation", "paramType": "MEAN",
               "groups": [{"id": "OG000", "title": "A"}, {"id": "OG001", "title": "B"}],
               "denoms": [{"units": "Participants", "counts": [{"groupId": "OG000", "value": "10"}, {"groupId": "OG001", "value": "9"}]}],
               "classes": [{"title": "In-trial", "denoms": [{"units": "Participants", "counts": [{"groupId": "OG000", "value": "8"}, {"groupId": "OG001", "value": "7"}]}],
                            "categories": [{"measurements": [{"groupId": "OG000", "value": "-5", "spread": "2"}, {"groupId": "OG001", "value": "-1", "spread": "3"}]}]}]}]}}}
    d = tmp_path / "registry"; d.mkdir()
    f = d / "NCT00000000.json"; f.write_text(json.dumps(rec), encoding="utf-8")
    v1 = ("NCT: NCT00000000 | TITLE: T\nELIGIBILITY: Adults\n"
          "RESULT OUTCOME 0 [PRIMARY]: Weight | DESCRIPTION:  | TIME FRAME:  | POPULATION:  | PARAM: MEAN | UNIT: None\n"
          "RESULT OUTCOME 0 GROUP OG000: A | \nRESULT OUTCOME 0 GROUP OG001: B | \n"
          "RESULT OUTCOME 0 DENOM Participants: A=10; B=9\n"
          "RESULT OUTCOME 0 CLASS DENOM In-trial Participants: A=8; B=7\n"
          "RESULT OUTCOME 0 MEASUREMENT In-trial: A=-5 (spread 2); B=-1 (spread 3)")
    out = textrep.render(str(f))
    assert out.startswith(v1), out
    assert "DISPERSION TYPE: Standard Deviation" in out[len(v1):]


def test_a_non_95_percent_interval_is_never_compared_as_the_served_95_percent_interval(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    pk["served_row"] = {"effect": 0.82, "ci_low": 0.72, "ci_high": 0.94, "scale": "HR"}
    assert V.verify(rec, pk)["served_compare"]["state"] == "DIFFERS"      # 95% vs 95%: a real difference
    rec["bound_values"]["ci_level"] = "97.5%"
    assert V.verify(rec, pk)["served_compare"]["state"] == "MATCH_POINT_CI_LEVEL_DIFFERS"


def test_a_count_written_as_a_word_is_that_number_and_no_other(tmp_path):
    assert "4" in V.num_tokens("four of 119 (3.4%)") and V.canon("four") == 4.0
    assert "5" not in V.num_tokens("four of 119 (3.4%)")


def test_arm_size_may_come_from_the_population_span_but_an_event_count_may_not(tmp_path):
    rec, pk, _ = _setup(tmp_path)
    rec["bound_values"] = {"n_t": "1000"}              # printed as '1,000' in the population span only
    assert V.verify(rec, pk)["errors"] == []
    rec["bound_values"] = {"events_t": "1000"}         # an event count must be in the estimate/ci spans
    assert any("events_t" in e for e in V.verify(rec, pk)["errors"])


def test_no_control_characters_in_the_lane_scripts():
    """Three times a shell heredoc turned a regex's \b or \1 into a raw control byte, silently changing what the
    regex matched. A control byte in source is never intended here."""
    import glob, re as _re
    here = os.path.join(os.path.dirname(__file__), "..", "evidence", "scripts", "*.py")
    bad = [p for p in glob.glob(here) if _re.search(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", open(p, "rb").read())]
    assert bad == []


def test_a_space_thousands_separator_is_one_number():
    assert V.canon("10 036") == 10036.0 and V.canon("10\u2009036") == 10036.0
    assert V.canon("0.44 0.73") is None      # two numbers are not one


def test_analysis_set_reader_recognises_itt_spellings_and_restrictions():
    """The sweep miscounted two ITT statements as contradicting ITT: one used a Unicode hyphen, one said 'intent-to-treat'."""
    from draft_from_extraction import set_reading
    for s in ("Analyses were performed according to the intention\u2010to\u2010treat principle.",
              "based on the intent-to-treat approach", "All analyses followed the ITT principle."):
        assert set_reading(s) == "ITT_STATED", s
    for s in ("ITT analysis was performed on the available participants.",
              "all randomized patients treated with at least 1 dose of study drug using the intention-to-treat principle",
              "The primary analysis was conducted using a modified intention\u2010to\u2010treat approach."):
        assert set_reading(s) == "OTHER_SET_STATED", s
    assert set_reading(None) == "NOT_STATED"


def test_gap_source_scope_is_derived_not_remembered():
    """A post-hoc tagging step was once wiped by the next run of the checker; the scope is now a pure function."""
    from gap_check import source_scope
    assert source_scope("evidence/held_local/12345/PMC1.html", "ITT was used.", "12345") == "OWN_REPORT"
    assert source_scope("evidence/held/999/PMC2.xml", "ITT was used.", "12345") == "SAME_TRIAL_OTHER_REPORT"
    assert source_scope("evidence/held/999/PMC2.xml", "Analyses will be conducted on an ITT basis.", "12345") == "SAME_TRIAL_OTHER_REPORT_PLANNED"
    assert source_scope("evidence/held/registry/NCT1.json", "FAS", "12345") == "OWN_REPORT"


def test_a_took_at_least_one_tablet_restriction_is_not_plain_itt():
    from draft_from_extraction import set_reading
    s = "the primary analyses for efficacy will be based on time to first event ... in all randomized patients who took at least 1 tablet of their assigned trial medication"
    assert set_reading(s) == "OTHER_SET_STATED"


# The lane's EYE LABELS for real spans (read 2026-09-24, before this reader was rewritten). Fixture, not tuning:
# any future reader change must keep these; a new eye-labelled case is added, never an old one edited to fit.
EYE_LABELLED = [
    ("We performed intention-to-treat (ITT) analysis of data from 214 patients and per-protocol (PP) analysis of data from 172 patients.", "ITT_STATED"),
    ("Among the 152 randomized patients, AF occurred in 26 patients (17%), including 16% of patients in the colchicine group", "ITT_STATED"),
    ("RESULT OUTCOME 2 DENOM Participants: Eplerenone=111; Placebo=110", "NOT_STATED"),
    ("Intention-to-treat (ITT) analysis was performed on the available participants.", "OTHER_SET_STATED"),
    ("The primary analysis was conducted using a modified intention\u2010to\u2010treat approach.", "OTHER_SET_STATED"),
    ("POPULATION: (mITT) modified Intent To Treat Analysis Set", "OTHER_SET_STATED"),
    ("Analyses were based on allocated treatment and included data from 246 children.", "OTHER_SET_STATED"),
    ("There were 532 patients who were excluded from the analysis (486 patients subsequently refused to provide consent", "OTHER_SET_STATED"),
    ("Outcomes were analyzed in all randomized patients treated with at least 1 dose of study drug (treated set) using the intention-to-treat principle.", "OTHER_SET_STATED"),
    ("All analyses were performed according to the intention-to-treat principle.", "ITT_STATED"),
    ("POPULATION: Randomized set - The randomized set includes all randomized subjects in the treatment groups to which they were randomized", "ITT_STATED"),
    # second eye pass (the SUPPORTED spans), 2026-09-24
    ("All randomized participants with a non-missing primary endpoint (n/N: 59/2609; 71/2635, in apixaban, enoxaparin/warfarin, respectively). Intent-to-treat population.", "OTHER_SET_STATED"),
    ("Full Analysis Set (FAS) included all randomized patients but the following two exclusions: 6 patients who did not qualify for randomization", "OTHER_SET_STATED"),
    # REVISED 2026-09-25 (was ITT_STATED): a blind cross-family reading pointed out that the full sentence continues
    # 'We did a complete case analysis with no imputation' -- the same non-missing restriction the lane labels OTHER for
    # AMPLIFY; the old label was inconsistent. Revised on the lane's own consistency rule, recorded here, not tuned.
    ("All analyses were done on an intention-to-treat basis. For each binary outcome, we calculated risk ratios and 95% CIs and two-sided p values. We did a complete case analysis with no imputation for missing data.", "OTHER_SET_STATED"),
    ("The intention-to-treat (ITT) population consisted of all randomized participants with valid informed consent.", "OTHER_SET_STATED"),
    ("The efficacy objectives were evaluated in all randomized patients using analysis of time from randomization to the first event.", "ITT_STATED"),
    # 'mITT' matched inside 'comMITTee' (case-insensitive, no word boundary) and flipped PLATO to CONTRADICTED
    ("Intention To Treat (ITT) analysis of whole population. Events were adjudicated by an endpoint committee. | POPULATION: The population was the full analysis set, which included all randomized patients", "ITT_STATED"),
    # third eye pass (S16 spans), 2026-09-25
    ("All the patients who underwent randomization were included in the primary and exploratory analyses,", "ITT_STATED"),
    ("FAS included all unique randomized participants who were grouped according to the treatment assigned at randomization.", "ITT_STATED"),
    ("For the primary endpoint the Full Analysis Set was used. This included all patients who were randomized to study treatment.", "ITT_STATED"),
    ("TIME FRAME: From randomization up until the first occurrence of the primary renal composite endpoint | POPULATION: Full analysis set", "OTHER_SET_STATED"),
]


def test_analysis_set_reader_matches_the_lanes_eye_labels():
    from draft_from_extraction import set_reading
    wrong = [(s[:60], want, set_reading(s)) for s, want in EYE_LABELLED if set_reading(s) != want]
    assert wrong == []


def test_no_private_workspace_content_in_tracked_evidence_files():
    """Codex transcripts once leaked the owner's private project index and submission workbook into this public
    repo (its startup instructions read them). No tracked file under evidence/ may carry that content or a
    local absolute path to it; transcripts (*.log) are never tracked."""
    import subprocess, re as _re
    root = os.path.join(os.path.dirname(__file__), "..")
    files = subprocess.run(["git", "ls-files", "evidence"], cwd=root, capture_output=True, text=True).stdout.split()
    assert not [f for f in files if f.endswith(".log")]
    pat = _re.compile(r"rewrite-workbook|YOUR REWRITE|ProjectIndex[\/]INDEX\.md|C:\\Users\\mahmo|F:\\E156")
    bad = [f for f in files if f.endswith((".json", ".md", ".txt", ".py")) and
           pat.search(open(os.path.join(root, f), encoding="utf-8", errors="replace").read())]
    assert bad == [], bad


def test_a_leading_en_dash_is_a_minus_but_a_range_dash_is_not():
    assert V.canon("\u20135.7") == -5.7
    assert V.num_tokens("difference, \u201312.0 to \u20138.6") >= {"-12.0", "-8.6"}
    assert V.num_tokens("95% CI 0.65\u20131.84") >= {"0.65", "1.84"} and "-1.84" not in V.num_tokens("95% CI 0.65\u20131.84")


def test_held_file_is_written_once(tmp_path, monkeypatch, capsys):
    """A held file is pinned by adjudications: an identical re-fetch keeps the FIRST ledger entry (provenance), and a
    re-fetch with different bytes is refused and leaves the held bytes alone (plant: a changed source)."""
    import acquire as A
    monkeypatch.setattr(A, "HELD", str(tmp_path))
    led = {}
    A.store("1/core.json", b"first", "u", led, "k")
    first = dict(led["1/core.json"])
    led["1/core.json"]["fetched_utc"] = "2000-01-01T00:00:00Z"   # mark it, so a rewrite would show
    A.store("1/core.json", b"first", "u", led, "k")
    assert led["1/core.json"]["fetched_utc"] == "2000-01-01T00:00:00Z" and led["1/core.json"]["sha256"] == first["sha256"]
    A.store("1/core.json", b"CHANGED", "u", led, "k")
    assert "REFUSED" in capsys.readouterr().out
    assert (tmp_path / "1" / "core.json").read_bytes() == b"first" and led["1/core.json"]["sha256"] == first["sha256"]


def test_stale_check_names_a_changed_served_row():
    """Plant: main changes a served CI bound (or moves the row to another trial) after the ruling. The unchanged
    control must read clean first, else a red plant proves nothing."""
    import stale_check as S
    then = {"effect": 0.82, "ci_low": 0.70, "ci_high": 0.96, "scale": "HR"}
    assert S.diff(then, dict(then, id="PMID 1"), "PMID 1") == {}
    assert S.diff(then, dict(then, ci_high=0.97, id="PMID 1"), "PMID 1") == {"ci_high": [0.96, 0.97]}
    assert "id" in S.diff(then, dict(then, id="PMID 2"), "PMID 1")
