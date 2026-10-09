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
