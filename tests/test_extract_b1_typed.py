"""B1 real-held-byte regressions; expected values come from the served review."""
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
    served = next(t for o in read(f"docs/reviews/{slug}/review.json")["outcomes"]
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
    assert extract.extract_arm_counts(sentence, ["probiotic"], ["placebo"]) == (7, 285, 3, 279)

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
    served = next(t for o in read(f"docs/reviews/{slug}/review.json")["outcomes"] if o["name"] == outcome for t in o["trials"] if t["id"] == f"PMID {pid}")
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


def test_severe_is_not_serious_typed_refusal():
    from harness.typed_routes import extract_bound
    got = extract_bound("probiotics-aad-prevention", "Serious adverse events", "34541475", root=ROOT)
    assert got["kind"] == "typed_refusal"
    assert got["reason_code"] == "ENDPOINT_UNBOUND"
    assert "severe != serious" in got["reason"]
    assert not any(k in got for k in ("ai", "ci", "effect"))


def test_pipeline_refuses_serious_severe_mismatch():
    got = built("probiotics-aad-prevention", "Serious adverse events")
    assert not any(t["id"] == "PMID 34541475" for t in got["trials"])
    row = next(t for t in got["declared_absent_trials"] if t["id"] == "PMID 34541475")
    assert row["typed_refusal"]
    assert row["state"] == "RETRIEVED_REFUSED_WITH_REASON"
