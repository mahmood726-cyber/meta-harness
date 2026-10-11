"""DISPATCH_V14_04: a concept-discovered ELIGIBLE family's report enters the study set only through the GENERATED,
signed register (cache/<slug>/concept_admissions.json), re-verified at every read; never by editing records.json."""
import copy
import json
import os
import shutil
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import concept_admission as ca  # noqa: E402
from harness import fetch  # noqa: E402

SLUG = "glp1-ra-mace-t2d"
CACHE = os.path.join(ROOT, "cache", SLUG)


def _records():
    return json.load(open(os.path.join(CACHE, "records.json"), encoding="utf-8"))


def _cfg():
    return json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))


def test_PLANT_flow_enters_the_study_set_through_the_signed_register():
    raw = _records()
    assert "38785209" not in {str(r["id"]) for r in raw["records"]}            # the search cache is never edited
    got = fetch._with_comparator_records(raw, _cfg(), CACHE)
    flow = [r for r in got["records"] if str(r["id"]) == "38785209"]
    assert len(flow) == 1 and flow[0]["nct"] == "NCT03819153"
    assert flow[0]["concept_admission"]["signed_item"] == "V14-04"
    held = open(os.path.join(ROOT, "outputs", "held_abstracts", "pubmed_38785209.txt"), encoding="utf-8").read()
    assert flow[0]["abstract"] == held and len(held) > 500                     # the held efetch abstract, verbatim


def _sandbox(tmp_path, mutate_entry=None, mutate_text=None, mutate_sig=None, mutate_family=None):
    """A copy of the cache and the registry pieces the overlay reads, with one thing changed."""
    root = tmp_path / "root"
    cache = root / "cache" / SLUG
    cache.mkdir(parents=True)
    for f in ("families.json", "family_discovery.json", ca.REGISTER):
        shutil.copy(os.path.join(CACHE, f), cache / f)
    (root / "registry").mkdir()
    shutil.copy(os.path.join(ROOT, "registry", "v14_signatures.json"), root / "registry" / "v14_signatures.json")
    held = root / "outputs" / "held_abstracts"
    held.mkdir(parents=True)
    for f in ("manifest.json", "pubmed_38785209.txt"):
        shutil.copy(os.path.join(ROOT, "outputs", "held_abstracts", f), held / f)
    if mutate_entry:
        reg = json.load(open(cache / ca.REGISTER, encoding="utf-8"))
        mutate_entry(reg["entries"][0])
        (cache / ca.REGISTER).write_text(json.dumps(reg), encoding="utf-8")
    if mutate_text:
        p = held / "pubmed_38785209.txt"
        p.write_text(mutate_text(p.read_text(encoding="utf-8")), encoding="utf-8", newline="")
    if mutate_sig:
        p = root / "registry" / "v14_signatures.json"
        s = json.load(open(p, encoding="utf-8"))
        mutate_sig(s["items"]["V14-04"])
        p.write_text(json.dumps(s), encoding="utf-8")
    if mutate_family:
        p = cache / "families.json"
        d = json.load(open(p, encoding="utf-8"))
        mutate_family(next(f for f in d["families"] if f["family_id"] == "NCT03819153"))
        p.write_text(json.dumps(d), encoding="utf-8")
    return str(root), str(cache)


def test_the_sandbox_admits_unchanged(tmp_path):
    root, cache = _sandbox(tmp_path)
    assert [r["id"] for r in ca.admitted_records(cache, root)] == ["38785209"]


@pytest.mark.parametrize("kw", [
    {"mutate_text": lambda t: t + " "},                                                      # held bytes moved
    {"mutate_sig": lambda s: s.update(state="OPEN")},                                        # not signed
    {"mutate_sig": lambda s: s.update(item_section_sha256="0" * 64)},                        # another item section
    {"mutate_family": lambda f: f["eligibility"].update(state="INELIGIBLE")},                # family not eligible
    {"mutate_family": lambda f: f.update(reports=[r for r in f["reports"] if r["report_id"] != "38785209"])},
    {"mutate_entry": lambda e: e.update(nct="NCT03819154")},                                 # another trial
    {"mutate_entry": lambda e: e.update(abstract_sha256="f" * 64)},
])
def test_PLANT_a_signed_admission_that_does_not_reverify_raises(tmp_path, kw):
    root, cache = _sandbox(tmp_path, **kw)
    with pytest.raises(ca.AdmissionRefused):
        ca.admitted_records(cache, root)


def test_PLANT_an_entry_that_is_not_admitted_is_never_applied(tmp_path):
    root, cache = _sandbox(tmp_path, mutate_entry=lambda e: e.update(state="LISTED"))
    assert ca.admitted_records(cache, root) == []


def test_a_topic_without_a_register_is_unchanged():
    other = os.path.join(ROOT, "cache", "dpp4-mace-t2d")
    recs = json.load(open(os.path.join(other, "records.json"), encoding="utf-8"))
    assert ca.with_concept_admissions(copy.deepcopy(recs), other) == recs


# ---- codex flow-r1 (PR #85): plants that fail on aa07dec3c ----------------------------------------------------------
@pytest.mark.parametrize("kw", [
    {"mutate_sig": lambda s: (s.pop("choice"), s.pop("item_section_sha256"))},                # r1#1: missing == missing
    {"mutate_entry": lambda e: e.update(signature={})},
])
def test_PLANT_flow_r1_1_an_incomplete_signature_never_matches(tmp_path, kw):
    if "mutate_entry" in kw:
        root, cache = _sandbox(tmp_path, mutate_sig=lambda s: (s.pop("choice"), s.pop("item_section_sha256")), **kw)
    else:
        root, cache = _sandbox(tmp_path, mutate_entry=lambda e: e.update(signature={}), **kw)
    with pytest.raises(ca.AdmissionRefused):
        ca.admitted_records(cache, root)


def test_PLANT_flow_r1_2_the_manifest_entry_must_be_this_papers(tmp_path):
    root, cache = _sandbox(tmp_path)
    p = os.path.join(root, "outputs", "held_abstracts", "manifest.json")
    m = json.load(open(p, encoding="utf-8"))
    m["documents"]["pubmed_38785209.txt"]["pmid"] = "2"
    open(p, "w", encoding="utf-8").write(json.dumps(m))
    with pytest.raises(ca.AdmissionRefused):
        ca.admitted_records(cache, root)


def test_PLANT_flow_r1_3_the_flow_script_refuses_a_text_that_is_not_the_signed_one(tmp_path, monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("v14_04", os.path.join(ROOT, "scripts", "v14_04_flow_mace.py"))
    s = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s)
    held = tmp_path / "held"
    held.mkdir()
    import hashlib
    text = "Synthetic. " + s.DEF_SPAN + ". " + s.RES_SPAN + "."
    (held / s.HELD_NAME).write_text(text, encoding="utf-8", newline="")
    (held / "manifest.json").write_text(json.dumps({"documents": {s.HELD_NAME: {
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "pmid": s.PMID, "pmcid": s.PMCID, "nct": s.NCT}}}),
        encoding="utf-8")
    monkeypatch.setattr(s, "HELD_DIR", str(held))
    # a sandboxed ROOT: no version of the script may write the real cache, even one that wrongly accepts the text
    (tmp_path / "cache" / s.SLUG).mkdir(parents=True)
    (tmp_path / "cache" / s.SLUG / "verified_effects.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(s, "ROOT", str(tmp_path))
    with pytest.raises(SystemExit):
        s.main(["--offline"])
    assert json.loads((tmp_path / "cache" / s.SLUG / "verified_effects.json").read_text(encoding="utf-8")) == {}
