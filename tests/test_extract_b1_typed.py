"""B1 real-held-byte regressions; expected values come from the pinned 0d95190c29 served review."""
import json
from pathlib import Path
import pytest
from harness import extract

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("dapagliflozin-hfpef-hosp", "Adverse events", "34711976"),
    ("esketamine-trd-madrs", "Adverse events", "37025256"),
    ("glp1-ra-mace-t2d", "Adverse events leading to discontinuation", "27295427"),
    ("melatonin-primary-insomnia-sol", "Adverse events", "20712869"),
    ("probiotics-aad-prevention", "Any adverse events", "39529939"),
    ("probiotics-aad-prevention", "Any adverse events", "41699149"),
    ("sglt2-ckd-progression", "Diabetic ketoacidosis", "36331190"),
    ("sglt2-ckd-progression", "Lower-limb amputation", "36331190"),
    ("sglt2-primary-prevention-hf", "Hospitalization for heart failure", "26378978"),
    ("sglt2-primary-prevention-hf", "Hospitalization for heart failure", "28605608"),
    ("sglt2-primary-prevention-hf", "Hospitalization for heart failure", "32966714"),
]

def read(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))

@pytest.mark.parametrize("slug,outcome,pid", CASES)
def test_typed_binding_equals_served(slug, outcome, pid):
    from harness.typed_routes import extract_bound
    served = next(t for o in read("tests/fixtures/b1_served_values_0d95190c29.json")["reviews"][slug]["outcomes"]
                  if o["name"] == outcome for t in o["trials"] if t["id"] == f"PMID {pid}")
    got = extract_bound(slug, outcome, pid, root=ROOT)
    keys = ("ai", "n1i", "ci", "n2i") if "ai" in served else ("effect", "ci_low", "ci_high", "scale")
    assert json.dumps({k: got[k] for k in keys}) == json.dumps({k: served[k] for k in keys})
    assert got["provenance"] == "typed_held_source"
    assert got["source_span"] and got["document_sha256"]
    for binding in got["typed_bindings"]:
        path = ROOT / binding["document_ref"].split("#")[0]
        import hashlib
        assert hashlib.sha256(path.read_bytes()).hexdigest() == binding["document_sha256"]
        text = path.read_text(encoding="utf-8")
        if path.name == "records.json":
            text = json.dumps(json.loads(text), ensure_ascii=False)
            # JSON escaping is not the source representation of an abstract.
            def strings(v):
                if isinstance(v, str): yield v
                elif isinstance(v, dict):
                    for x in v.values(): yield from strings(x)
                elif isinstance(v, list):
                    for x in v: yield from strings(x)
            assert any(binding["span"] in x for x in strings(json.loads(text)))
        else:
            assert binding["span"] in text





def test_total_is_not_an_arm():
    import re
    text = (ROOT / "cache/probiotics-aad-prevention/ft_39529939.txt").read_text(encoding="utf-8")
    paragraph = next(p for p in re.findall(r"<p\b[^>]*>.*?</p>", text, re.S) if "10/564" in p)
    sentence = extract._sentences(re.sub(r"<[^>]+>", "", paragraph))[0]
    from harness.typed_routes import _sentence_counts
    assert _sentence_counts(sentence, ["probiotic"], ["placebo"]) == (7, 285, 3, 279)

from functools import lru_cache

@lru_cache(None)
def built(slug, outcome):
    from harness import pipeline
    cfg = read(f"topics/{slug}.json")
    records = read(f"cache/{slug}/records.json")
    inp = pipeline.outcome_inputs(slug, cfg, records)
    specs = [(cfg.get("primary_outcome"), "efficacy")] + [(x, "efficacy") for x in cfg.get("secondary_outcomes", [])] + [(x, "harm") for x in cfg.get("harm_outcomes", [])]
    spec, kind = next((s,k) for s,k in specs if s and s["name"] == outcome)
    return pipeline.build_outcome_from_inputs(inp, spec, kind, slug)

@pytest.mark.parametrize("slug,outcome,pid", CASES)
def test_pipeline_uses_typed_binding(slug, outcome, pid):
    got = next(t for t in built(slug, outcome)["trials"] if t["id"] == f"PMID {pid}")
    assert got["provenance"] == "typed_held_source"
    assert got["typed_bindings"]
    served = next(t for o in read("tests/fixtures/b1_served_values_0d95190c29.json")["reviews"][slug]["outcomes"] if o["name"] == outcome for t in o["trials"] if t["id"] == f"PMID {pid}")
    keys = ("ai", "n1i", "ci", "n2i", "effect", "ci_low", "ci_high")
    assert {k:got.get(k) for k in keys} == {k:served.get(k) for k in keys}





@pytest.mark.parametrize("mutation", ["percentage", "denominator", "arm", "endpoint"])
def test_table_fails_closed_when_binding_changes(mutation):
    from harness.table_rows import read_row
    from harness.typed_routes import ROUTES
    key = ("esketamine-trd-madrs", "Adverse events", "37025256")
    text = (ROOT / "cache/esketamine-trd-madrs/ft_37025256.txt").read_text(encoding="utf-8")
    old, new = {"percentage": ("120 (95.2)", "120 (15.2)"),
                "denominator": ("(n=126)", "(n=226)"),
                "arm": ("Esketamine Plus AD", "Unidentified Plus AD"),
                "endpoint": (">TEAEs<", ">Unspecified endpoint<")}[mutation]
    assert old in text
    with pytest.raises(ValueError):
        read_row(text.replace(old, new), **ROUTES[key])


def test_hr_component_does_not_take_composite():
    from harness.typed_routes import sentence_hr
    with pytest.raises(ValueError):
        sentence_hr("Cardiovascular death or hospitalization for heart failure (HR, 0.88; 95% CI, 0.70-0.99).")


def test_typed_provenance_cannot_admit_forged_numbers():
    from harness.typed_routes import extract_bound, validate_row
    slug, outcome, pid = CASES[0]
    row = dict(extract_bound(slug, outcome, pid), id=f"PMID {pid}")
    assert validate_row(row, outcome)
    row["ai"] += 1
    assert not validate_row(row, outcome)


def test_row7_remains_hand_entered_and_served():
    from harness.typed_routes import ROUTES
    key = ("probiotics-aad-prevention", "Serious adverse events", "34541475")
    assert key not in ROUTES
    assert "served|probiotics-aad-prevention|Serious adverse events|PMID 34541475" in read("registry/provenance_hand_entered.json")["rows"]
    got = next(t for t in built(*key[:2])["trials"] if t["id"] == "PMID 34541475")
    served = next(t for o in read("tests/fixtures/b1_served_values_0d95190c29.json")["reviews"]["probiotics-aad-prevention"]["outcomes"] if o["name"] == key[1] for t in o["trials"] if t["id"] == "PMID 34541475")
    keys = ("ai", "n1i", "ci", "n2i", "effect", "ci_low", "ci_high")
    assert {k: got.get(k) for k in keys} == {k: served.get(k) for k in keys}


def test_missing_source_refuses_one_row_in_topic(monkeypatch):
    from harness import typed_routes
    original = typed_routes.extract_bound
    def missing(slug, outcome, pid, **kw):
        if pid == '39529939':
            raise FileNotFoundError('missing held source plant')
        return original(slug, outcome, pid, **kw)
    monkeypatch.setattr(typed_routes, 'extract_bound', missing)
    built.cache_clear()
    outcome = built('probiotics-aad-prevention', 'Any adverse events')
    row = next(r for r in outcome['declared_absent_trials'] if r['id'] == 'PMID 39529939')
    assert row['typed_refusal'] and 'missing held source plant' in row['reason']
    assert any(r['id'] == 'PMID 41699149' for r in outcome['trials'])
    built.cache_clear()


@pytest.mark.parametrize("mutation,reason", [
    ("unregistered", "TYPED_ROUTE_UNPINNED"),
    ("missing", "TYPED_ROUTE_UNPINNED"),
    ("value", "TYPED_ROUTE_VALUE_MISMATCH"),
])
def test_pinned_route_build_refusal(monkeypatch, tmp_path, mutation, reason):
    from harness import typed_routes as tr
    key = ("probiotics-aad-prevention", "Any adverse events", "39529939")
    data = read("tests/fixtures/b1_served_values_0d95190c29.json")
    if mutation == "unregistered":
        key = (key[0], key[1], "unregistered-test-route")
        monkeypatch.setitem(tr.ROUTES, key, {"route": "sentence_counts"})
    else:
        outcome = next(o for o in data["reviews"][key[0]]["outcomes"] if o["name"] == key[1])
        row = next(t for t in outcome["trials"] if t["id"] == "PMID " + key[2])
        if mutation == "missing":
            outcome["trials"].remove(row)
        else:
            row["ai"] += 1
    fixture = tmp_path / "pinned.json"
    fixture.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(tr, "PINNED_VALUES", fixture)
    if mutation == "unregistered":
        # This synthetic locator has no included trial in the topic. Check the
        # route refusal directly; the other plants exercise real build rows.
        row = tr.for_outcome(*key[:2])[key[2]]
        assert row["absent"] and row["reason_code"] == reason
        with pytest.raises(ValueError, match=reason):
            tr.extract_bound(*key)
        return
    built.cache_clear()
    try:
        result = built(*key[:2])
        row = next(r for r in result["declared_absent_trials"] if r["id"] == "PMID " + key[2])
        assert row["typed_refusal"] and reason in row["reason"]
        assert not any(r["id"] == "PMID " + key[2] for r in result["trials"])
        assert tr.for_outcome(*key[:2])[key[2]]["reason_code"] == reason
    finally:
        built.cache_clear()


def test_every_route_has_a_pinned_served_value():
    from harness import typed_routes as tr
    for key in tr.ROUTES:
        assert tr._pinned_value(*key)


def test_shared_extractor_p1_1_main_behavior():
    sentence = 'Hypoglycaemia: empagliflozin 3/100 (3%) vs placebo 7/100 (7%), favouring empagliflozin.'
    assert extract.extract_arm_counts(sentence, ['empagliflozin'], ['placebo']) == (3, 100, 7, 100)


def test_shared_extractor_is_exact_pinned_main():
    import subprocess
    assert (ROOT / 'harness/extract.py').read_bytes() == subprocess.check_output(
        ['git', 'show', '0d95190c29:harness/extract.py'])
