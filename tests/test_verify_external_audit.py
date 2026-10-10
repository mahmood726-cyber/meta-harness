"""The external-audit limb must be able to FAIL: a served number drifting from the auditor's independent arithmetic, or an
edited auditor script, is refused (a check that can only pass is not a check)."""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("vea", os.path.join(ROOT, "scripts", "verify_external_audit.py"))
vea = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vea)


def test_the_committed_corpus_agrees_with_every_external_audit_script():
    rows, bad = vea.run()
    assert bad == 0, [r for r in rows if r["verdict"] == "FAIL"]
    assert len(rows) >= 15


def test_PLANT_a_served_number_that_drifts_is_refused(monkeypatch):
    real = vea._served
    def drifted(slug, outcome=None):
        res = dict(real(slug, outcome))
        if slug == "doac-vte-recurrence":
            res["estimate"] = res["estimate"] + 0.001
        return res
    monkeypatch.setattr(vea, "_served", drifted)
    rows, bad = vea.run()
    assert bad >= 1 and any(r["check"] == "doac primary estimate" and r["verdict"] == "FAIL" for r in rows)


def test_PLANT_an_edited_auditor_script_is_refused_and_never_run(monkeypatch, tmp_path):
    import shutil
    ext = tmp_path / "external"
    shutil.copytree(vea.EXT, ext)
    p = ext / "review05_recalculation.py"
    p.write_bytes(p.read_bytes().replace(b"0.9091", b"0.9092"))
    monkeypatch.setattr(vea, "EXT", str(ext))
    rows, bad = vea.run()
    assert any(r["check"] == "review05_recalculation.py bytes" and r["verdict"] == "FAIL" for r in rows)
    assert not any(r["check"].startswith("doac primary") for r in rows)


def test_PLANT_auditor_scripts_are_never_sent_to_a_model_but_our_audit_code_is():
    """D8: audit/external/ quotes held source passages (some non-CC) -- the codex PR reviewer must never send them,
    while our own audit/ code (the independent recompute) must be reviewed."""
    import sys
    sys.path[:0] = [os.path.join(ROOT, "scripts"), ROOT]
    import pr_codex_review as prc
    assert prc._ok_file("audit/independent_recompute.py") and not prc._ok_file("audit/external/review05_recalculation.py")
    assert not prc._ok_file("docs/x.py") and prc._ok_file("scripts/verify_external_audit.py")


def test_PLANT_an_unsigned_supersession_never_excuses_a_disagreement(monkeypatch, tmp_path):
    """codex ext-audit-r1 P0: a supersession must name a SEEN_AND_SIGNED item and pin the served value it excuses."""
    import json as _json
    import shutil
    ext = tmp_path / "external"
    shutil.copytree(vea.EXT, ext)
    real = vea._served
    def drifted(slug, outcome=None):
        res = dict(real(slug, outcome))
        if slug == "doac-vte-recurrence":
            res["estimate"] = 0.95
        return res
    monkeypatch.setattr(vea, "EXT", str(ext))
    monkeypatch.setattr(vea, "_served", drifted)
    for bad in ({"check": "doac primary estimate"},
                {"check": "doac primary estimate", "signed_item": "V99-01", "served": 0.95},
                {"check": "doac primary estimate", "signed_item": "V13-01", "served": 0.94}):
        (ext / "superseded.json").write_text(_json.dumps({"superseded": [bad]}), encoding="utf-8")
        rows, bad_n = vea.run()
        assert any(r["check"] == "doac primary estimate" and r["verdict"] == "FAIL" for r in rows), bad


def test_PLANT_a_script_run_supersession_must_pin_served_values_and_the_expected_failure(monkeypatch, tmp_path):
    """codex ext-audit-r2 P0: a signed item alone excused any later failure of the script and skipped every comparison."""
    import json as _json
    import shutil
    ext = tmp_path / "external"
    shutil.copytree(vea.EXT, ext)
    p = ext / "review05_recalculation.py"
    body = p.read_bytes().replace(b"assert abs(primary[\"estimate\"] - 0.9091)", b"assert abs(primary[\"estimate\"] - 0.5)")
    p.write_bytes(body)
    sums = (ext / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    import hashlib
    sums = [(hashlib.sha256(body).hexdigest() + " *review05_recalculation.py") if l.endswith("review05_recalculation.py") else l for l in sums]
    (ext / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    monkeypatch.setattr(vea, "EXT", str(ext))
    monkeypatch.setattr(vea, "_signed_items", lambda: {"V13-01"})
    (ext / "superseded.json").write_text(_json.dumps({"superseded": [
        {"check": "review05_recalculation.py run", "signed_item": "V13-01"}]}), encoding="utf-8")
    rows, bad = vea.run()
    assert any(r["check"] == "review05_recalculation.py run" and r["verdict"] == "FAIL" for r in rows)


# ------------------------------------------------------------------------------- bundles (reviews 10-21, 10 Oct)
def _bundle_only(monkeypatch, tmp_path, name):
    import shutil
    ext = tmp_path / "external"
    shutil.copytree(vea.EXT, ext)
    monkeypatch.setattr(vea, "EXT", str(ext))
    monkeypatch.setattr(vea, "CHECKS", [])
    monkeypatch.setattr(vea, "BUNDLES", [b for b in vea.BUNDLES if b[0] == name])
    return ext


def test_every_received_bundle_is_checked():
    assert {b[0] for b in vea.BUNDLES} == {"review10", "review12", "review13", "review14", "review15", "review16",
                                          "review18", "review19", "review20", "review21", "review25",
                                          "review27", "review28", "review29"}


def test_PLANT_a_changed_file_anywhere_in_a_bundle_is_refused_and_never_run(monkeypatch, tmp_path):
    ext = _bundle_only(monkeypatch, tmp_path, "review12")
    p = ext / "review12" / "findings.json"
    p.write_bytes(p.read_bytes() + b" ")
    rows, bad = vea.run()
    assert bad == 1 and rows[0]["check"] == "review12 bundle bytes" and "findings.json" in rows[0]["detail"]


def test_PLANT_an_unlisted_file_added_to_a_bundle_is_refused(monkeypatch, tmp_path):
    ext = _bundle_only(monkeypatch, tmp_path, "review12")
    (ext / "review12" / "extra.py").write_text("print(1)\n", encoding="utf-8")
    rows, bad = vea.run()
    assert bad == 1 and "unlisted" in rows[0]["detail"] and "extra.py" in rows[0]["detail"]


def test_PLANT_ignored_paths_drop_only_what_they_name():
    out = {"runtime": {"numpy": "2.4.4"}, "pool": {"estimate": 0.81}}
    ref = {"runtime": {"numpy": "2.3.5"}, "pool": {"estimate": 0.80}}
    assert vea._same_json(vea._drop(out, [("runtime",)]), vea._drop(ref, [("runtime",)])) != []
    assert vea._same_json(vea._drop(out, [("runtime",)]), vea._drop(dict(ref, pool={"estimate": 0.81}), [("runtime",)])) == []
