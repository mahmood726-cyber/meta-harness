"""M2 (Mahmood, 2026-09-20): hand-extracted rows are bound to HELD BYTES or they abstain.

Measured on the served release 8b1fb37d through the real route (scripts/build_topic.py + harness.gate):
UNBOUND_LEGACY is the dominant admission path (121 of 145 pooled rows on 30 of 32 pages); on the
hand-verified route a wrong tuple BROKE the abstract binding and the row was admitted because it no
longer matched ("a gate whose failure mode is 'admit' rewards exactly the input it exists to stop"); a
hand-written `source` string saying 0.68 while the held abstract says 0.86 was pooled as 0.68 (0.77-0.96)
with `verified: verified` ("the haystack was the self-authored string").

Requirement: every row that reaches `admit_rows` with hand-extraction provenance is bound by
`target_endpoint.bind_hand_row` to the held document its `document_ref` names -- tuple located losslessly
in ONE span (sentence, or table row + its label / section heading / column headers), ownership read from
that span (or from exactly one definition span in the PROSE), classified by the existing `_classify`.
Ambiguity ABSTAINS (row not pooled, `absent_kind: machine_absent`, `reason_code: ENDPOINT_UNBOUND`,
candidate spans listed) -- it never chooses. Fixtures are the authentic held documents: LEADER's full
text (sha256 ded4c69e...) with its real target tuple and four real wrong-endpoint tuples from the same
Table 1; REWIND's abstract; CARMELINA's full text whose reference list impersonates a definition span.

Plant: on 8b1fb37d every `admit_rows` assertion below that expects a refusal or an abstention FAILS --
the rows are kept with `endpoint_admissibility == "UNBOUND_LEGACY"`.
"""
import json
import pathlib
import re

import pytest

from harness import target_endpoint as te

ROOT = pathlib.Path(__file__).resolve().parents[1]
GLP1 = "glp1-ra-mace-t2d"
LEADER = "27295427"
REWIND = "31189511"
SOUL = "40162642"
PRIMARY = "3-point major adverse cardiovascular events"


def _topic(slug):
    return json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))


def _spec(slug, name):
    cfg = _topic(slug)
    for o in [cfg["primary_outcome"]] + (cfg.get("secondary_outcomes") or []) + (cfg.get("harm_outcomes") or []):
        if o["name"] == name:
            return o
    raise KeyError(name)


def _ft(slug, pid):
    return (ROOT / "cache" / slug / f"ft_{pid}.txt").read_text(encoding="utf-8")


def _abstract(slug, pid):
    recs = json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))["records"]
    return next(r for r in recs if str(r["id"]) == pid)["abstract"]


def _row_of(text, cell_prefix):
    i = text.find(cell_prefix)
    assert i > 0, cell_prefix
    return text[text.rfind("<tr>", 0, i):text.find("</tr>", i) + 5]


def _leader_prose():
    t = _ft(GLP1, LEADER)
    j = t.find("The primary composite outcome occurred in fewer patients in the liraglutide group")
    return t[j:t.find("for superiority)", j) + len("for superiority)")]


def _hand_effect(pid, effect, lo, hi, span, document_ref, **extra):
    """Shaped exactly as pipeline._build_outcome's verified-effects override route emits a row."""
    row = {"label": pid, "id": f"PMID {pid}", "effect": effect, "ci_low": lo, "ci_high": hi, "scale": "HR",
           "provenance": "fulltext_verified", "source": span, "source_span": span,
           "document_ref": document_ref, "source_level": 1, "kind": "extracted_effect"}
    row.update(extra)
    return row


def _admit(spec, row):
    kept, refused = te.admit_rows(spec, [row])
    return kept, refused


LEADER_REF = f"cache/{GLP1}/ft_{LEADER}.txt"
SPEC = _spec(GLP1, PRIMARY)


# ----------------------------------------------------------------------------- the LEADER semantic suite
def test_leader_control_prose_binds_exact_target():
    kept, refused = _admit(SPEC, _hand_effect(LEADER, 0.87, 0.78, 0.97, _leader_prose(), LEADER_REF))
    assert refused == [] and len(kept) == 1
    row = kept[0]
    assert row["endpoint_admissibility"] == "EXACT_TARGET"
    assert row["target_endpoint_class"] == te.EXACT_TARGET
    assert row["endpoint_admissibility"] != "UNBOUND_LEGACY"


def test_leader_control_table_row_binds_through_its_label_and_column_headers():
    row = _row_of(_ft(GLP1, LEADER), "0.87 (0.78")
    kept, refused = _admit(SPEC, _hand_effect(LEADER, 0.87, 0.78, 0.97, row, LEADER_REF))
    assert refused == [] and len(kept) == 1
    assert kept[0]["endpoint_admissibility"] == "EXACT_TARGET"
    spans = kept[0].get("spans") or []
    roles = {s["role"] for s in spans}
    assert "result" in roles and "row_label" in roles, roles
    assert any("Primary composite outcome" in s["text"] for s in spans if s["role"] == "row_label")


@pytest.mark.parametrize("cell, effect, lo, hi, owner", [
    ("0.86 (0.73", 0.86, 0.73, 1.00, "Myocardial infarction"),
    ("0.86 (0.71", 0.86, 0.71, 1.06, "Stroke"),
    ("0.88 (0.81", 0.88, 0.81, 0.96, "Expanded composite outcome"),
    ("0.78 (0.66", 0.78, 0.66, 0.93, "Death from cardiovascular causes"),
])
def test_leader_wrong_endpoint_rows_refuse_with_the_semantic_code(cell, effect, lo, hi, owner):
    row = _row_of(_ft(GLP1, LEADER), cell)
    kept, refused = _admit(SPEC, _hand_effect(LEADER, effect, lo, hi, row, LEADER_REF))
    assert kept == [], f"{owner} row was pooled as 3-point MACE: {kept[0].get('endpoint_admissibility') if kept else None}"
    assert len(refused) == 1
    r = refused[0]
    assert r["reason_code"] == "RESULT_INCOMPATIBLE", r
    assert r["refused_effect"]["effect"] == effect
    assert owner.split()[0].lower() in (r.get("endpoint_definition_span") or r.get("reason") or "").lower()


def test_leader_ambiguous_point_only_over_the_whole_table_abstains():
    t = _ft(GLP1, LEADER)
    i = t.find("0.87 (0.78")
    table = t[t.rfind("<table-wrap", 0, i):t.find("</table-wrap>", i) + len("</table-wrap>")]
    kept, refused = _admit(SPEC, _hand_effect(LEADER, 0.86, None, None, table, LEADER_REF))
    assert kept == []
    assert len(refused) == 1
    r = refused[0]
    assert r["absent_kind"] == "machine_absent" and r["reason_code"] == "ENDPOINT_UNBOUND", r
    assert len(r.get("candidate_locations") or []) >= 2, r.get("candidate_locations")


def test_leader_inverted_direction_tuple_is_not_in_the_held_document():
    kept, refused = _admit(SPEC, _hand_effect(LEADER, 1.15, 1.03, 1.28, _leader_prose(), LEADER_REF,
                                              comparator_direction="placebo vs liraglutide"))
    assert kept == [] and refused[0]["reason_code"] == "ENDPOINT_UNBOUND"
    assert "not located" in refused[0]["reason"] or "no span" in refused[0]["reason"]


def test_leader_declared_direction_contradicting_the_column_headers_refuses():
    row = _row_of(_ft(GLP1, LEADER), "0.87 (0.78")
    kept, refused = _admit(SPEC, _hand_effect(LEADER, 0.87, 0.78, 0.97, row, LEADER_REF,
                                              comparator_direction="placebo vs liraglutide"))
    assert kept == [], "a declared reversed direction was ignored"
    assert refused[0]["reason_code"] == "RESULT_INCOMPATIBLE" and "direction" in refused[0]["reason"]


def test_leader_declared_analysis_set_not_held_abstains():
    kept, refused = _admit(SPEC, _hand_effect(LEADER, 0.87, 0.78, 0.97, _leader_prose(), LEADER_REF,
                                              analysis_set="per-protocol"))
    assert kept == [], "a declared per-protocol analysis set was ignored (the held tuple is the time-to-event primary analysis)"
    assert refused[0]["reason_code"] == "ENDPOINT_UNBOUND" and "per-protocol" in refused[0]["reason"]


def test_leader_declared_harmless_normalisation_passes():
    row = _row_of(_ft(GLP1, LEADER), "0.87 (0.78")
    kept, refused = _admit(SPEC, _hand_effect(LEADER, 0.87, 0.78, 0.97, row, LEADER_REF, ci_pct=95,
                                              normalisation="en dash -> hyphen; 'Hazard Ratio (95% CI)' column header -> HR"))
    assert refused == [] and kept[0]["endpoint_admissibility"] == "EXACT_TARGET"


# ----------------------------------------------------------------------------- the SOUL counterexamples (real route: WRONG_ADMISSION)
def _soul_row(effect, lo, hi, source):
    return {"label": "SOUL", "id": f"PMID {SOUL}", "effect": effect, "ci_low": lo, "ci_high": hi, "scale": "HR",
            "provenance": "fulltext_verified", "source": source,
            "document_ref": f"cache/{GLP1}/records.json#PMID-{SOUL}"}


SOUL_SOURCE = ("SOUL (PMID 40162642, NCT03914326) abstract: primary MACE (CV death, nonfatal MI, nonfatal stroke) "
               "579/4825 vs 668/4825, hazard ratio, 0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006")


def test_soul_control_binds_to_the_abstract():
    kept, refused = _admit(SPEC, _soul_row(0.86, 0.77, 0.96, SOUL_SOURCE))
    assert refused == [] and kept[0]["endpoint_admissibility"] == "EXACT_TARGET"


def test_soul_wrong_interval_does_not_fall_through_to_admission():
    kept, refused = _admit(SPEC, _soul_row(0.86, 0.77, 0.98, SOUL_SOURCE))
    assert kept == [], "ci_high 0.98 broke the binding and the row was admitted BECAUSE it no longer matched"
    assert refused[0]["reason_code"] == "ENDPOINT_UNBOUND"


def test_soul_coherent_lie_is_measured_against_held_bytes_not_the_source_string():
    kept, refused = _admit(SPEC, _soul_row(0.68, 0.77, 0.96, SOUL_SOURCE.replace("0.86", "0.68")))
    assert kept == [], "0.68 (0.77-0.96) -- a point outside its own interval -- was pooled"


def test_PLANT_soul_wrong_scale_refuses_even_when_the_abstract_route_already_classified_it():
    """W1b (M2 battery, both trees): the abstract route matched SOUL's digits, set target_endpoint_class
    EXACT_TARGET, and admissibility returned on that class before the hand binder ran -- the row was pooled as
    an OR. A hand row is bound by the hand binder whatever an earlier route wrote in its class field."""
    row = dict(_soul_row(0.86, 0.77, 0.96, SOUL_SOURCE), scale="OR", provenance="abstract_verified",
               target_endpoint_class="EXACT_TARGET", endpoint_binding="named_endpoint_resolved_to_definition_span")
    kept, refused = _admit(SPEC, row)
    assert kept == [], "scale OR was pooled: the held abstract says hazard ratio"
    assert "OR" in (refused[0].get("reason") or refused[0].get("endpoint_binding_reason") or "")


def test_soul_control_with_a_prior_class_still_binds_and_is_marked_bound():
    row = dict(_soul_row(0.86, 0.77, 0.96, SOUL_SOURCE), provenance="abstract_verified",
               target_endpoint_class="EXACT_TARGET", endpoint_binding="named_endpoint_resolved_to_definition_span")
    kept, refused = _admit(SPEC, row)
    assert refused == [] and kept[0]["endpoint_admissibility"] == "EXACT_TARGET"
    assert kept[0].get("hand_binding_state") == "BOUND"


def test_point_outside_its_own_interval_is_refused_without_a_document():
    verdict = te.admissibility(SPEC, {"effect": 0.14, "ci_low": 0.77, "ci_high": 0.96, "scale": "HR",
                                      "provenance": "fulltext_verified", "source": "x"})
    assert verdict["admissible"] is False and "interval" in verdict["reason"]


# ----------------------------------------------------------------------------- the two served glp1 harm rows: BIND, never refuse
def test_rewind_gi_counts_bind_to_the_held_abstract_sentence():
    spec = _spec(GLP1, "Gastrointestinal adverse events")
    row = {"label": "31189511", "id": f"PMID {REWIND}", "ai": 2347, "n1i": 4949, "ci": 1687, "n2i": 4952,
           "provenance": "abstract_verified", "document_ref": f"cache/{GLP1}/records.json#PMID-{REWIND}",
           "source": _abstract(GLP1, REWIND)}
    kept, refused = _admit(spec, [row][0])
    assert refused == [] and kept[0]["endpoint_admissibility"] == "EXACT_TARGET"
    span = kept[0]["endpoint_result_span"]
    assert span.startswith("2347 (47.4%)") and "gastrointestinal adverse event" in span, span


def test_leader_discontinuation_counts_bind_through_table_context():
    spec = _spec(GLP1, "Adverse events leading to discontinuation")
    t = _ft(GLP1, LEADER)
    row_xml = _row_of(t, "444 (9.5)")
    row = {"label": "27295427", "id": f"PMID {LEADER}", "ai": 444, "n1i": 4668, "ci": 339, "n2i": 4672,
           "provenance": "fulltext_verified_arms", "document_ref": LEADER_REF, "source": row_xml, "source_span": row_xml}
    kept, refused = _admit(spec, row)
    assert refused == [] and kept[0]["endpoint_admissibility"] == "EXACT_TARGET"
    roles = {s["role"]: s["text"] for s in kept[0]["spans"]}
    assert "permanent discontinuation" in roles["section_heading"]
    assert "4668" in roles["column_header"] and "4672" in roles["column_header"]


# ----------------------------------------------------------------------------- the fail-open with a confident face
def test_carmelina_definition_span_is_prose_not_a_reference_list_title():
    spec = _spec("dpp4-mace-t2d", PRIMARY)
    t = _ft("dpp4-mace-t2d", "30418475")
    j = t.find("During a median follow-up of 2.2 years, the primary outcome occurred in 434 of 3494")
    sentence = re.sub(r"<[^>]+>", "", t[j:t.find("for", t.find("0.89-1.17", j)) + 3])
    row = _hand_effect("30418475", 1.02, 0.89, 1.17, sentence, "cache/dpp4-mace-t2d/ft_30418475.txt")
    kept, refused = _admit(spec, row)
    assert refused == [] and kept[0]["endpoint_admissibility"] == "EXACT_TARGET"
    definition = kept[0]["endpoint_definition_span"]
    assert "Primary outcome was time to first occurrence of the composite of CV death" in definition, definition
    assert "jama-321-69.pdf" not in definition and "10.1001/" not in definition


# ----------------------------------------------------------------------------- routes this landing does not cover keep their label
# ----------------------------------------------------------------------------- companion-record evidence
SGLT2PP = "sglt2-primary-prevention-hf"
HHF = "Hospitalization for heart failure"


def _sglt2pp_hhf_entry(pid):
    """The committed verified_effects entry for this trial's HHF row, as the pipeline reads it."""
    v = json.loads((ROOT / "cache" / SGLT2PP / "verified_effects.json").read_text(encoding="utf-8"))
    entries = v[pid] if isinstance(v[pid], list) else [v[pid]]
    return next(e for e in entries if e.get("outcome") == HHF)


def _pipeline_row(slug, pid, entry):
    from harness import pipeline
    row = {"label": pid, "id": f"PMID {pid}", "effect": entry["effect"], "ci_low": entry["ci_low"],
           "ci_high": entry["ci_high"], "scale": entry.get("scale") or "HR", "provenance": "fulltext_verified",
           "source": entry.get("source")}
    row.update(pipeline._hand_fields(entry, slug, pid))
    return row


@pytest.mark.parametrize(("pid", "companion_ref"), [
    ("28605608", f"cache/{SGLT2PP}/records.json#PMID-29526832"),        # CANVAS -> its HF paper (held abstract)
    ("32966714", f"cache/{SGLT2PP}/records.json#PMID-33026243"),        # VERTIS CV -> its HF paper
    ("26378978", f"cache/{SGLT2PP}/pmc_26819227_fulltext.txt"),         # EMPA-REG -> its HF paper (held full text)
])
def test_PLANT_companion_document_named_by_the_entry_is_the_first_candidate(pid, companion_ref):
    """Three HHF rows abstained on the repaired tree with 'tuple not located in ... records.json#PMID-<self>':
    the binder read the trial's OWN abstract while the entry names, verbatim, the held companion document that
    carries the number (the reference locator knew this; the harness did not)."""
    from harness import pipeline
    fields = pipeline._hand_fields(_sglt2pp_hhf_entry(pid), SGLT2PP, pid)
    assert fields["document_candidates"][0] == companion_ref


def test_PLANT_companion_record_in_a_secondary_records_list_is_held():
    from harness import hand_binding
    doc = hand_binding.resolve_document(f"cache/{SGLT2PP}/records.json#PMID-29526832")
    assert doc is not None and "hospitalized HF alone" in doc["text"]


@pytest.mark.parametrize("pid", ["28605608", "32966714", "26378978"])
def test_PLANT_sglt2pp_hhf_rows_bind_to_their_companion_documents(pid):
    spec = _spec(SGLT2PP, HHF)
    kept, refused = _admit(spec, _pipeline_row(SGLT2PP, pid, _sglt2pp_hhf_entry(pid)))
    assert refused == [], (refused or [{}])[0].get("reason")
    assert kept[0]["endpoint_admissibility"] == "EXACT_TARGET" and kept[0]["hand_binding_state"] == "BOUND"
    assert "self" not in kept[0]["held_document"] and pid not in kept[0]["held_document"], kept[0]["held_document"]


def test_PLANT_flattened_text_tables_yield_rows_with_label_caption_and_column_header():
    """pmc_<pid>_fulltext.txt serialises tables as '=== TABLES ===' / 'TABLE <caption>' / ' | '-joined rows.
    Read as prose, the whole section glued into one 'sentence' and every row's tuple was found twice."""
    from harness import hand_binding
    doc = hand_binding.resolve_document(f"cache/{SGLT2PP}/pmc_26819227_fulltext.txt")
    rows = hand_binding.table_rows(doc["text"]) if doc["representation"] == "xml" else hand_binding.text_table_rows(doc["text"])
    hhf = [r for r in rows if r["label"] == "Hospitalization for heart failure"]
    assert len(hhf) == 1
    assert hhf[0]["caption"].startswith("Table 1: Heart failure outcomes") and "HR (95% CI)" in hhf[0]["column_header"]
    assert "=== TABLES" not in hand_binding.prose_of(doc)


def test_PLANT_same_owner_in_prose_and_table_is_not_ambiguity():
    """EMPA-REG's HHF number sits in a results sentence AND in the Table 1 row that names the same endpoint.
    Ambiguity is two OWNERS for one tuple (L9: the MI row and the stroke row), not two copies of one owner."""
    spec = _spec(SGLT2PP, HHF)
    kept, refused = _admit(spec, _pipeline_row(SGLT2PP, "26378978", _sglt2pp_hhf_entry("26378978")))
    assert refused == [], (refused or [{}])[0].get("reason")
    assert kept[0]["hand_binding_state"] == "BOUND" and kept[0].get("duplicate_locations") == 1


def test_PLANT_clause_owns_the_tuple_in_a_multi_result_sentence():
    """CANVAS's HF paper reports three results in ONE sentence (composite 0.78; fatal-or-hospitalised 0.70;
    'hospitalized HF alone (HR, 0.67; 95% CI, 0.52-0.87)'). Sentence-level ownership read the composite named
    first and REFUSED the correct row as a different outcome; the clause that holds the tuple owns it."""
    spec = _spec(SGLT2PP, HHF)
    kept, refused = _admit(spec, _pipeline_row(SGLT2PP, "28605608", _sglt2pp_hhf_entry("28605608")))
    assert refused == [], (refused or [{}])[0].get("reason")
    assert kept[0]["endpoint_admissibility"] == "EXACT_TARGET"
    assert "hospitalized HF alone" in kept[0]["endpoint_definition_span"] and "0.78" not in kept[0]["endpoint_definition_span"]


@pytest.mark.parametrize(("text", "components"), [
    ("hospitalized HF alone", {"heart failure hospitalization"}),
    ("HF hospitalisation", {"heart failure hospitalization"}),
    ("fatal or hospitalized HF", {"heart failure hospitalization", "heart failure death"}),
    ("cardiovascular death or hospitalized HF", {"cardiovascular death", "heart failure hospitalization"}),
])
def test_PLANT_lexicon_reads_abbreviated_hf_hospitalisation_and_fatal_hf(text, components):
    assert te._components_from_text(text, expand_named_composites=False) == components


def _arms_entry(slug, pid, outcome):
    v = json.loads((ROOT / "cache" / slug / "verified_arms.json").read_text(encoding="utf-8"))
    entries = v[pid] if isinstance(v[pid], list) else [v[pid]]
    return next(e for e in entries if e.get("outcome") == outcome)


def _arms_row(slug, pid, entry, provenance):
    from harness import pipeline
    row = {"label": pid, "id": f"PMID {pid}", "ai": entry["ai"], "n1i": entry["n1i"], "ci": entry["ci"],
           "n2i": entry["n2i"], "provenance": provenance, "source": entry.get("source")}
    row.update(pipeline._hand_fields(entry, slug, pid))
    return row


def test_PLANT_several_foreign_locations_abstain_and_do_not_refuse():
    """colchicine-postop-af 32720823 discontinuation 1/81 vs 1/71: the abstract says 'one patient in each group'
    in words; the digit 1 matched '1 mg', '1-mg' and '(n = 81)'. Census #2 deduplicated the three foreign owners
    into a REFUSAL ('different outcome'); a tuple that was never located is an abstention, not a refusal."""
    entry = _arms_entry("colchicine-postop-af", "32720823", "Treatment discontinuation")
    kept, refused = _admit(_spec("colchicine-postop-af", "Treatment discontinuation"),
                           _arms_row("colchicine-postop-af", "32720823", entry, "abstract_verified"))
    assert kept == []
    assert refused[0]["reason_code"] == "ENDPOINT_UNBOUND", refused[0].get("reason")


def test_PLANT_teaes_table_row_is_the_adverse_events_family():
    """esketamine 37025256 Table 4 'TEAEs | 120 (95.2) | 89 (70.6)' was refused as a different outcome from
    'Adverse events': the family matcher did not read the abbreviation."""
    entry = _arms_entry("esketamine-trd-madrs", "37025256", "Adverse events")
    kept, refused = _admit(_spec("esketamine-trd-madrs", "Adverse events"),
                           _arms_row("esketamine-trd-madrs", "37025256", entry, "fulltext_verified_arms"))
    assert refused == [], refused[0].get("reason") if refused else None
    assert kept[0]["endpoint_admissibility"] == "EXACT_TARGET" and kept[0]["hand_binding_state"] == "BOUND"


OMEGA3 = "omega3-cardiovascular-events"
MVE = "Major vascular events / MACE"


def _effects_entry(slug, pid, outcome):
    v = json.loads((ROOT / "cache" / slug / "verified_effects.json").read_text(encoding="utf-8"))
    entries = v[pid] if isinstance(v[pid], list) else [v[pid]]
    return next(e for e in entries if e.get("outcome") == outcome)


def test_origin_named_composite_without_a_held_definition_abstains_and_names_the_recovery():
    """ORIGIN 22686415: 'no significant effect on the rates of major vascular events (... HR 1.01 ...)'. The spec's
    components derive from its name ('... / MACE' -> the 3-point set) and the held ABSTRACT never defines ORIGIN's
    'major vascular events', so the binder cannot show they are the same composite: ABSTAIN, with the reason; the
    recovery is a full-text document_ref carrying the definition. (Census #1/#2 abstained here; that is correct.)"""
    entry = _effects_entry(OMEGA3, "22686415", MVE)
    assert te.canonical_components(_spec(OMEGA3, MVE)), "the spec carries name-derived components"
    kept, refused = _admit(_spec(OMEGA3, MVE), _pipeline_row(OMEGA3, "22686415", entry))
    assert kept == []
    assert refused[0]["reason_code"] == "ENDPOINT_UNBOUND"
    assert "no definition span" in (refused[0].get("endpoint_binding_reason") or refused[0].get("reason") or "")


# ----------------------------------------------------------------------------- the handed-abstract route
def _handed_row(pid, abstract, **extra):
    row = {"label": pid, "id": f"PMID {pid}", "effect": 0.86, "ci_low": 0.77, "ci_high": 0.96, "scale": "HR",
           "provenance": "abstract_verified", "source": "hand-written description", "handed_abstract": abstract}
    row.update(extra)
    return row


HANDED = ("The primary outcome was a composite of death from cardiovascular causes, nonfatal myocardial infarction, "
          "or nonfatal stroke. A primary-outcome event occurred less often with drug than placebo (hazard ratio, 0.86; "
          "95% confidence interval, 0.77 to 0.96).")


def test_PLANT_handed_abstract_binds_when_no_held_file_exists_and_is_named_as_such():
    """A trial with no held FILE (a fixture; a record outside records.json) may bind to the abstract the pipeline was
    handed -- and the record must say that is what it bound to, distinctly from a held file."""
    kept, refused = _admit(SPEC, _handed_row("99999999", HANDED))
    assert refused == [] and kept[0]["endpoint_admissibility"] == "EXACT_TARGET"
    ref = kept[0]["held_document"]["ref"]
    assert ref.startswith("record:99999999") and "abstract handed to the pipeline" in ref, ref
    assert kept[0]["held_document"]["representation"] == "abstract"
    assert not ref.startswith("cache/"), "a handed abstract must never be recorded as a held file"


def test_PLANT_handed_abstract_never_overrides_a_held_file():
    """Not interchangeable: when a held file resolves for the trial, the file is the document even if the handed
    abstract would bind more generously (here SOUL's held abstract has 0.86 (0.77-0.96); the handed text claims a
    different tuple that would bind the row to a different number)."""
    from harness import hand_binding
    tampered = HANDED.replace("0.86", "0.68").replace("0.77", "0.60").replace("0.96", "0.75")
    row = _handed_row(SOUL, tampered, effect=0.68, ci_low=0.60, ci_high=0.75,
                      document_candidates=[f"cache/{GLP1}/records.json#PMID-{SOUL}"])
    kept, refused = _admit(SPEC, row)
    assert kept == [], "the handed text bound a tuple the held file does not carry"
    assert refused[0]["reason_code"] == "ENDPOINT_UNBOUND"
    assert refused[0]["held_document"]["ref"] == f"cache/{GLP1}/records.json#PMID-{SOUL}", refused[0]["held_document"]


def test_PLANT_handed_abstract_is_ignored_when_the_entry_names_a_document():
    """An entry that names its document is bound to THAT document; a handed abstract cannot substitute for it."""
    row = _handed_row(SOUL, HANDED, document_ref=f"cache/{GLP1}/ft_{LEADER}.txt")   # names LEADER's full text
    kept, refused = _admit(SPEC, row)
    assert kept == [] and refused[0]["reason_code"] == "ENDPOINT_UNBOUND"
    assert refused[0]["held_document"]["ref"].startswith("cache/")


def test_registry_and_derived_rows_without_an_endpoint_class_abstain_they_are_never_admitted_unbound():
    """Was: `..._keep_unbound_legacy_and_are_still_admitted` -- M2 scoped the binder to hand rows and pinned the other routes as
    ADMITTED UNBOUND_LEGACY. That asserted the fail-open itself (external audit, 2026-09-26: losing endpoint identity must never
    increase admissibility). The requirement now: a registry/derived row with no endpoint class ABSTAINS with
    ENDPOINT_IDENTITY_MISSING, stays visible with its tuple, and is not refused on evidence (it is not shown to be wrong)."""
    for prov in ("ctgov_results", "published_rate", "aact_verified", "pre_specified_dose", "registry_verified"):
        kept, refused = _admit(SPEC, {"label": "x", "id": "PMID 1", "effect": 0.9, "ci_low": 0.8, "ci_high": 1.0,
                                      "scale": "HR", "provenance": prov, "source": "registry measure"})
        assert kept == [], prov
        assert refused[0]["reason_code"] == "ENDPOINT_IDENTITY_MISSING" and refused[0]["state"] == "EXTRACTION_DEBT", prov
        assert refused[0]["candidate_tuple"] == {"effect": 0.9, "ci_low": 0.8, "ci_high": 1.0, "scale": "HR"}, prov
        assert all(r.get("endpoint_admissibility") != "UNBOUND_LEGACY" for r in refused), prov
