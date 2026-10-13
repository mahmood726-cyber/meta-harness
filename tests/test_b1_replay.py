"""B1: source text stays inside tests; diagnostics contain only status/numbers.

Static: supplied served-number baselines and literal reader selectors.
Dynamic: counts parsed from committed spans; held bytes checked against SHA pins.
Long spans are never printed, summarized, or used to tune a reader.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import extractor_replay as xr
from harness import provenance_class as pc
from harness import verified_inputs as vi

COUNTS = ("ai", "n1i", "ci", "n2i")
EFFECTS = ("effect", "ci_low", "ci_high")
# slug, PMID, outcome, numbers, status; no source text in the fixture matrix.
CASES = [
    ("dapagliflozin-hfpef-hosp", "34711976", "Adverse events", (44, 162, 38, 162), "CONVERTED"),
    ("probiotics-aad-prevention", "39529939", "Any adverse events", (7, 285, 3, 279), "CONVERTED"),
    ("esketamine-trd-madrs", "37025256", "Adverse events", (120, 126, 89, 126), "NOT_CONVERTED"),
    ("glp1-ra-mace-t2d", "27295427", "Adverse events leading to discontinuation", (444, 4668, 339, 4672), "NOT_CONVERTED"),
    ("melatonin-primary-insomnia-sol", "20712869", "Adverse events", (136, 394, 142, 395), "NOT_CONVERTED"),
    ("probiotics-aad-prevention", "41699149", "Any adverse events", (64, 125, 69, 130), "NOT_CONVERTED"),
    ("probiotics-aad-prevention", "39529939", "Serious adverse events", (1, 285, 0, 279), "NOT_CONVERTED"),
    ("probiotics-aad-prevention", "34541475", "Serious adverse events", (4, 181, 6, 178), "NOT_CONVERTED"),
    ("sglt2-ckd-progression", "36331190", "Lower-limb amputation", (1.43, .8, 2.57), "NOT_CONVERTED"),
    ("probiotics-aad-prevention", "39529939", "Antibiotic-associated diarrhoea", (26, 282, 69, 273), "NEEDS_SOURCE"),
    ("probiotics-aad-prevention", "34541475", "Antibiotic-associated diarrhoea", (59, 131, 53, 126), "NEEDS_SOURCE"),
    ("sglt2-ckd-progression", "36331190", "Diabetic ketoacidosis", (6, 3304, 1, 3305), "NEEDS_SOURCE"),
    ("sglt2-primary-prevention-hf", "28605608", "Hospitalization for heart failure", (.67, .52, .87), "NEEDS_SOURCE"),
    ("sglt2-primary-prevention-hf", "26378978", "Hospitalization for heart failure", (.65, .5, .85), "NEEDS_SOURCE"),
    ("sglt2-primary-prevention-hf", "32966714", "Hospitalization for heart failure", (.7, .54, .9), "NEEDS_SOURCE"),
]


def _row(case):
    __tracebackhide__ = True
    slug, pid, outcome, expected, _ = case
    filename = "verified_arms.json" if len(expected) == 4 else "verified_effects.json"
    data = json.loads((ROOT / "cache" / slug / filename).read_text(encoding="utf-8"))
    matches = [r for r in vi.entries(data[pid]) if r["outcome"] == outcome]
    if len(matches) != 1:
        pytest.fail("row identity did not resolve uniquely", pytrace=False)
    return dict(matches[0], id=f"PMID {pid}")


@pytest.mark.parametrize("case", CASES, ids=[f"row-{i+1}" for i in range(len(CASES))])
def test_served_numbers_and_conversion_status(case):
    __tracebackhide__ = True
    row = _row(case)
    fields = COUNTS if len(case[3]) == 4 else EFFECTS
    if tuple(row.get(k) for k in fields) != case[3]:
        pytest.fail("served-number baseline FAIL", pytrace=False)
    if case[4] == "CONVERTED":
        values = xr.read_cache_ae_clause(row["source_span"], row["replay"])
        if tuple(values[k] for k in fields) != case[3] or not xr.replay(row)[0]:
            pytest.fail("typed replay FAIL", pytrace=False)
        if pc.classify_served(row, lambda _: False)[0] != "EXTRACTOR":
            pytest.fail("extractor class FAIL", pytrace=False)
    elif case[4] == "NEEDS_SOURCE":
        if row.get("source_span") or row.get("document_ref"):
            pytest.fail("legacy source baseline FAIL", pytrace=False)
    elif row.get("provenance") in xr.REPLAY_PROV:
        pytest.fail("unsupported long row promoted", pytrace=False)


@pytest.mark.parametrize("case", CASES[:2], ids=["percentages", "fractions"])
@pytest.mark.parametrize("plant", ["span", "count", "tiny_count", "sha", "pmid", "reader", "effect", "outcome", "arms"])
def test_corrupt_replay_is_untraced_never_hand_entered(case, plant):
    __tracebackhide__ = True
    row = copy.deepcopy(_row(case))
    if plant == "span":
        row["source_span"] += " CORRUPTED"
    elif plant == "count":
        row["ai"] += 1
    elif plant == "tiny_count":
        row["ai"] += 0.0000001
    elif plant == "sha":
        row["document_sha256"] = "0" * 64
    elif plant == "pmid":
        row["replay"]["pmid"] = "1"
    elif plant == "reader":
        row["replay"] = {}
    elif plant == "outcome":
        row["outcome"] = "Serious adverse events"
    elif plant == "arms":
        spec = row["replay"]
        spec["arm_t"], spec["arm_c"] = spec["arm_c"], spec["arm_t"]
    else:
        row["effect"] = 1.0
    if xr.replay(row)[0] or pc.classify_served(row, lambda _: True)[0] != "UNTRACED":
        pytest.fail("corrupted replay was not UNTRACED", pytrace=False)


def test_rounded_percentages_must_identify_unique_integer_denominators():
    assert xr._unique_denominator(44, "27.2") == 162
    assert xr._unique_denominator(38, "23.5") == 162
    for n, p in [(1, "1"), (0, "0"), (1, "0.0"), (10, "101")]:
        with pytest.raises(xr.ReadRefused):
            xr._unique_denominator(n, p)


@pytest.mark.parametrize("old,new", [("7/285", "7/284"), ("10/564", "11/564"), ("2.5%", "2.6%"),
                                     ("7/285", "7/0"), ("7/285", "7/2")])
def test_fraction_reader_refuses_inconsistent_counts(old, new):
    __tracebackhide__ = True
    row = _row(CASES[1])
    with pytest.raises(xr.ReadRefused):
        xr.read_cache_ae_clause(row["source_span"].replace(old, new), row["replay"])


@pytest.mark.parametrize("plant", ["bytes", "manifest", "missing_manifest", "wrong_record", "traversal"])
def test_held_bytes_and_manifest_are_independently_required(tmp_path, plant):
    __tracebackhide__ = True
    row = _row(CASES[0])
    # A synthetic abstract-container fixture uses only the permitted short quote.
    path = tmp_path / row["document_ref"]
    path.parent.mkdir(parents=True)
    raw = json.dumps({"records": [{"id": "34711976", "abstract": row["source_span"]}]}).encode()
    text_sha = hashlib.sha256(row["source_span"].encode()).hexdigest()
    sha = hashlib.sha256(raw).hexdigest()
    row["document_sha256"] = sha
    path.write_bytes(raw)
    manifest = tmp_path / "cache" / "b1_replay_manifest.json"
    manifest.write_text(json.dumps({"documents": {row["document_ref"]: {
        "sha256": sha, "text_sha256": text_sha}}}), encoding="utf-8")
    if not xr.replay(row, str(tmp_path))[0]:
        pytest.fail("fixture baseline FAIL", pytrace=False)
    if plant == "bytes":
        path.write_bytes(raw + b" ")
    elif plant == "manifest":
        row["document_sha256"] = "0" * 64
        manifest.write_text(json.dumps({"documents": {row["document_ref"]: {
            "sha256": "0" * 64, "text_sha256": text_sha}}}), encoding="utf-8")
    elif plant == "missing_manifest":
        manifest.unlink()
    elif plant == "wrong_record":
        row["id"] = "PMID 1"
        row["replay"]["pmid"] = "1"
    else:
        row["document_ref"] = "cache/../records.json"
    if xr.replay(row, str(tmp_path))[0]:
        pytest.fail("held integrity plant FAIL", pytrace=False)


@pytest.mark.parametrize("case", CASES[:2], ids=["percentages", "fractions"])
def test_runtime_preserves_replay_metadata(case):
    __tracebackhide__ = True
    row = vi.runtime(_row(case))
    if pc.classify_served(row, lambda _: False)[0] != "EXTRACTOR":
        pytest.fail("runtime metadata replay FAIL", pytrace=False)


@pytest.mark.parametrize("case", CASES[:2], ids=["percentages", "fractions"])
def test_pipeline_keeps_counts_and_replay_class(case):
    __tracebackhide__ = True
    from harness import pipeline
    row = _row(case)
    records = json.loads((ROOT / "cache" / case[0] / "records.json").read_text(encoding="utf-8"))["records"]
    recs = {r["id"]: r for r in records}
    spec = {"name": case[2], "keywords": ["adverse events", "AE"], "estimand": "RR"}
    outcome = pipeline._build_outcome(
        spec, "harm", [{"id": case[1], "id_type": "pmid", "label": case[1]}], recs,
        [row["replay"]["arm_t"]], [row["replay"]["arm_c"]],
        verified_arms={case[1]: row}, slug=case[0])
    trials = [t for t in outcome["trials"] if t["id"] == row["id"]]
    if len(trials) != 1 or tuple(trials[0].get(k) for k in COUNTS) != case[3]:
        pytest.fail("pipeline served counts FAIL", pytrace=False)
    if pc.classify_served(trials[0], lambda _: False)[0] != "EXTRACTOR":
        pytest.fail("pipeline replay class FAIL", pytrace=False)


@pytest.mark.parametrize("case", CASES[2:9], ids=[f"long-{i+1}" for i in range(7)])
def test_long_spans_fail_closed_with_available_grammars(case):
    __tracebackhide__ = True
    row = _row(case)
    with pytest.raises(xr.ReadRefused):
        if len(case[3]) == 3:
            xr.read_abstract_clause(row["source_span"])
        else:
            span = row["source_span"]
            m = re.match(r"Adverse events were similar between (.+?) and (.+?) \(", span)
            if not m:
                raise xr.ReadRefused("unsupported grammar")
            xr.read_cache_ae_clause(span, {"reader": "ae_patient_percentages", "outcome": case[2],
                                          "arm_t": m[1], "arm_c": m[2]})


PRE_B1 = "f694220a7e4ccfe961ae5f11c58bd4a2b170eb24"   # #84 head: the cache before B1 converted any row


def test_cache_edits_preserve_all_original_values_and_quotes():
    __tracebackhide__ = True
    for slug in {case[0] for case in CASES[:2]}:
        rel = f"cache/{slug}/verified_arms.json"
        before = json.loads(subprocess.check_output(["git", "show", f"{PRE_B1}:{rel}"], cwd=ROOT))
        after = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        for case in [c for c in CASES[:2] if c[0] == slug]:
            old = next(r for r in vi.entries(before[case[1]]) if r["outcome"] == case[2])
            new = next(r for r in vi.entries(after[case[1]]) if r["outcome"] == case[2])
            new["provenance"] = old["provenance"]
            new.pop("document_sha256")
            new.pop("replay")
        if before != after:
            pytest.fail("non-metadata cache change FAIL", pytrace=False)


def test_plant_an_interpretive_sentence_that_qualifies_the_percentages_is_refused():
    """codex b1-cap-r1 #1 (P0): the optional second sentence was accepted whatever it said, so 'the percentages are
    Kaplan-Meier estimates, with 200 patients in each arm' still yielded denominators derived from the percentages."""
    from harness.extractor_replay import ReadRefused, read_cache_ae_clause
    spec = {"reader": "ae_patient_percentages", "outcome": "Adverse events", "arm_t": "Drug", "arm_c": "placebo"}
    head = "Adverse events were similar between Drug and placebo (44 (27.2%) versus 38 (23.5%) patients, respectively)."
    for tail in (" These results indicate that the percentages are Kaplan-Meier estimates, with 200 patients in each arm.",
                 " These results indicate that cumulative incidence was estimated at 12 months.",
                 " These results indicate that 200 patients were treated in each arm."):
        with pytest.raises(ReadRefused):
            read_cache_ae_clause(head + tail, spec)
    # the real permitted quote's interpretation (a duration, no denominator, no estimate) still reads
    real = head + (" These results indicate that 12 weeks of dapagliflozin treatment significantly improved "
                   "patient-reported symptoms, physical limitations and exercise function and was well tolerated in "
                   "chronic HFpEF.")
    assert read_cache_ae_clause(real, spec)["ai"] == 44


def test_plant_the_preservation_check_is_pinned_to_the_pre_b1_commit():
    """codex b1-cap-r1 #2: the preservation check diffed HEAD against the working tree, so it went red the moment the
    conversion was committed. It now reads the cache as it was before B1 (PRE_B1)."""
    assert PRE_B1 == "f694220a7" or len(PRE_B1) == 40
    out = subprocess.run(["git", "cat-file", "-t", PRE_B1], cwd=ROOT, capture_output=True, text=True)
    assert out.stdout.strip() == "commit"
