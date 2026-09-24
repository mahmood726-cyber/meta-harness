"""Every served review page NAMES ITS VERIFIER: the program a reader runs, where it is served, the sha256 of the served
bytes, the exact commands, and what it does NOT check (harness/page.py::render_page_verifier).

Properties, not numbers: the digest on each page must equal the digest of the served file NOW; the served file must be
byte-identical to the source it claims to mirror; the page must quote every NOT-checked item the verifier's own bytes
state; and each NOT-checked claim the page makes about a verifier is shown TRUE by a plant (tamper the thing the page
says is not checked, and the verifier still passes -- while tampering a thing it does check makes it refuse).
"""
from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import re
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MARK = "data-page-verifier="

from harness import page  # noqa: E402


def _served_pages():
    return sorted(p for p in (DOCS / "reviews").iterdir() if (p / "index.html").is_file())


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------ the served pages
def test_there_are_served_pages_to_check():
    # positive control on the denominator: an empty glob would make every test below vacuously green
    assert len(_served_pages()) >= 32


def test_every_served_review_page_names_a_verifier_that_matches_the_served_bytes():
    problems = []
    for d in _served_pages():
        slug, src = d.name, (d / "index.html").read_text(encoding="utf-8")
        if src.count(MARK) != 1:
            problems.append(f"{slug}: {src.count(MARK)} verifier blocks (want exactly 1)")
            continue
        keys = re.search(MARK + r"'([^']*)'", src).group(1).split(",")
        want = ["certificate"] + (["bundle"] if (d / "BUNDLE.json").is_file() else [])
        if keys != want:
            problems.append(f"{slug}: names {keys}, expected {want}")
        text = html.unescape(src)
        for v in page._VERIFIERS:
            if v["key"] not in keys:
                continue
            served = DOCS / v["served"]
            if not served.is_file():
                problems.append(f"{slug}: names docs/{v['served']}, which is not served")
                continue
            digest = _sha(served)
            if digest not in src:
                problems.append(f"{slug}: does not carry the sha256 of docs/{v['served']} ({digest}); the verifier changed "
                                f"after the page was built -- rebuild it: python scripts/build_topic.py {slug} --now <build date>")
            for item in page._verifier_limits(served.read_text(encoding="utf-8")) or ["<verifier states no limits>"]:
                if item not in text:
                    problems.append(f"{slug}: does not quote the NOT-checked item {item[:60]!r} of {v['served']}")
            for cmd in v["served_cmds"] + v["clone_cmds"]:
                if cmd.format(site=page._SITE_ROOT, slug=slug) not in text:
                    problems.append(f"{slug}: missing command {cmd!r}")
    assert problems == [], "\n".join(problems)


def test_each_served_verifier_is_byte_identical_to_its_source():
    for v in page._VERIFIERS:
        assert (DOCS / v["served"]).read_bytes() == (ROOT / v["source"]).read_bytes(), v["served"]


def test_blind_pages_do_not_name_a_verifier():
    # docs/m/ pages are the neutral, blinded renderings used for comparator judging; the verifier block names the review
    # and would unblind them. The block is added only when neutral=False.
    blind = sorted((DOCS / "m").glob("*/index.html"))
    assert blind, "no blind pages found -- the check would be vacuous"
    assert [p for p in blind if MARK in p.read_text(encoding="utf-8")] == []


def test_site_root_matches_the_bundle_builder():
    src = (ROOT / "scripts" / "build_bundle.py").read_text(encoding="utf-8")
    assert re.search(r'^SITE_ROOT = "([^"]+)"', src, re.M).group(1) == page._SITE_ROOT


# ------------------------------------------------------------------------------------------------ renderer plants
def _review(slug="glp1-ra-mace-t2d"):
    return json.loads((DOCS / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def test_plant_a_changed_verifier_byte_changes_the_page(tmp_path, monkeypatch):
    fake = tmp_path / "docs" / "scripts"
    fake.mkdir(parents=True)
    for v in page._VERIFIERS:
        shutil.copyfile(DOCS / v["served"], fake / Path(v["served"]).name)
    (tmp_path / "docs" / "reviews" / "glp1-ra-mace-t2d").mkdir(parents=True)
    shutil.copyfile(DOCS / "reviews/glp1-ra-mace-t2d/BUNDLE.json", tmp_path / "docs/reviews/glp1-ra-mace-t2d/BUNDLE.json")
    monkeypatch.setattr(page, "_REPO_ROOT", tmp_path)
    before = page.render_page_verifier(_review())
    with open(fake / "verify_bundle.py", "ab") as f:
        f.write(b"\n# one byte more\n")
    after = page.render_page_verifier(_review())
    assert before != after
    assert _sha(fake / "verify_bundle.py") in after and _sha(fake / "verify_bundle.py") not in before


def test_plant_an_unserved_verifier_is_named_as_a_problem(tmp_path, monkeypatch):
    monkeypatch.setattr(page, "_REPO_ROOT", tmp_path)   # nothing served under tmp_path/docs
    out = page.render_page_verifier(_review("pcsk9-mace"))
    assert "VERIFIER_NOT_SERVED" in out and "sha256 of each served verifier" not in out


def test_plant_a_verifier_with_no_stated_limits_is_named_as_a_problem(tmp_path, monkeypatch):
    fake = tmp_path / "docs" / "scripts"
    fake.mkdir(parents=True)
    src = (DOCS / "scripts/audit_certificate_stdlib.py").read_text(encoding="utf-8")
    stripped = re.sub(r"\nNOT_CHECKED = \[.*?\n\]\n", "\n", src, flags=re.S)
    assert stripped != src, "plant did not remove the list"
    (fake / "audit_certificate_stdlib.py").write_text(stripped, encoding="utf-8")
    monkeypatch.setattr(page, "_REPO_ROOT", tmp_path)
    assert "VERIFIER_STATES_NO_LIMITS" in page.render_page_verifier(_review("pcsk9-mace"))


def test_plant_a_page_with_no_certificate_says_no_verifier_is_named():
    r = _review("pcsk9-mace")
    r["reproduction"] = {k: v for k, v in (r.get("reproduction") or {}).items() if k != "certificate"}
    out = page.render_page_verifier(r)
    assert "NO_VERIFIER_NAMED" in out and "class='absent'" in out


def test_the_limits_reader_takes_both_forms():
    assert page._verifier_limits('NOT_CHECKED = ["a", "b"]\n') == ["a", "b"]
    assert page._verifier_limits('def f(report):\n    report["not_checked"] = ["x"]\n') == ["x"]
    assert page._verifier_limits('NOT_CHECKED = []\n') is None
    assert page._verifier_limits('x = 1\n') is None


# ------------------------------------------------------------------------------------------------ the NOT-checked claims are true
@pytest.fixture
def auditor():
    return _load(DOCS / "scripts" / "audit_certificate_stdlib.py", "_served_audit_certificate_stdlib")


def _audit(auditor, capsys, *argv):
    rc = auditor.main(["audit_certificate_stdlib.py", *map(str, argv)])
    return rc, capsys.readouterr().out


def test_auditor_reads_only_the_certificate_and_the_pinned_code(auditor, capsys, monkeypatch):
    """Claims 'review_sha256 never recomputed from review.json', 'no input digest compared with any file', 'index.html
    never read': record every file the served auditor opens."""
    opened = []
    real_rt, real_rb = Path.read_text, Path.read_bytes
    monkeypatch.setattr(Path, "read_text", lambda self, *a, **k: (opened.append(self.as_posix()), real_rt(self, *a, **k))[1])
    monkeypatch.setattr(Path, "read_bytes", lambda self, *a, **k: (opened.append(self.as_posix()), real_rb(self, *a, **k))[1])
    cert = DOCS / "reviews" / "pcsk9-mace" / "CERTIFICATE.json"
    rc, out = _audit(auditor, capsys, cert, DOCS)
    assert rc == 0 and "RESULT REPRODUCED" in out
    blobs = json.loads(cert.read_text(encoding="utf-8"))["analysis_code_blobs"]
    allowed = {cert.as_posix()} | {(DOCS / p).as_posix() for p in blobs}
    assert opened and set(opened) <= allowed, sorted(set(opened) - allowed)
    assert not any(o.endswith(("review.json", "index.html", "records.json", "manifest.json")) for o in opened)
    assert "NOT checked: " + "; ".join(auditor.NOT_CHECKED) in out


def test_auditor_passes_a_certificate_whose_review_digest_is_wrong_only_if_release_is_recomputed_too(auditor, capsys, tmp_path):
    """The limit 'review_sha256 is never recomputed from review.json', demonstrated: rewrite review_sha256 AND recompute
    release_sha256 the way the auditor does -- it still reports REPRODUCED. Control: change a field without recomputing
    release_sha256 and it refuses."""
    cert = json.loads((DOCS / "reviews/pcsk9-mace/CERTIFICATE.json").read_text(encoding="utf-8"))
    forged = dict(cert, review_sha256="0" * 64)
    body = {k: v for k, v in forged.items() if k != "release_sha256"}
    forged["release_sha256"] = auditor.sha256(auditor.canonical(body))
    (tmp_path / "forged.json").write_text(json.dumps(forged), encoding="utf-8")
    rc, out = _audit(auditor, capsys, tmp_path / "forged.json")
    assert rc == 0 and "RESULT REPRODUCED" in out
    naive = dict(cert, review_sha256="0" * 64)
    (tmp_path / "naive.json").write_text(json.dumps(naive), encoding="utf-8")
    rc, out = _audit(auditor, capsys, tmp_path / "naive.json")
    assert rc == 1 and "MISMATCH release_sha256" in out


def test_auditor_refuses_a_changed_pinned_module_but_not_a_correct_looking_wrong_one(auditor, capsys, tmp_path):
    """What it does check (a pinned byte), and the stated limit (bytes match pins, not that the code is correct)."""
    cert = DOCS / "reviews/pcsk9-mace/CERTIFICATE.json"
    blobs = json.loads(cert.read_text(encoding="utf-8"))["analysis_code_blobs"]
    tree = tmp_path / "tree"
    for p, v in blobs.items():
        if v != "NOT_PRESENT":
            (tree / p).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(DOCS / p, tree / p)
    rc, out = _audit(auditor, capsys, cert, tree)
    assert rc == 0, out
    with open(tree / "harness/synth.py", "a", encoding="utf-8") as f:
        f.write("\n")
    rc, out = _audit(auditor, capsys, cert, tree)
    assert rc == 1 and "harness/synth.py" in out


def test_bundle_verifier_never_reads_the_page_and_recomputes_only_the_primary_pool():
    vb = _load(DOCS / "scripts" / "verify_bundle.py", "_served_verify_bundle")
    slug = "glp1-ra-mace-t2d"
    store = vb.Store(str(DOCS), None)
    rep = vb.run(store, slug, None)
    assert rep["verdict"] == "PASS", rep.get("failures")
    fetched = set(store.cache)
    assert f"reviews/{slug}/review.json" in fetched          # control: the recorder sees what it reads
    assert not any(p.endswith("index.html") for p in fetched), sorted(p for p in fetched if "html" in p)
    review = _review(slug)
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    primary_ids = {str(t.get("id", "")).replace("PMID ", "") for t in primary["trials"]}
    # secondary outcomes reuse the same trials, so membership alone is weak: the rows are exactly the primary's rows
    assert {str(r["pmid"]) for r in rep["rows"]} == primary_ids and len(rep["rows"]) == len(primary["trials"])
    # the page's count of outcomes NOT recomputed is len(outcomes) - 1, computed, not typed
    v = next(x for x in page.page_verifiers(review) if x["key"] == "bundle")
    assert f"the other {len(review['outcomes']) - 1} outcome(s)" in " ".join(v["page_limits"])
    assert v["not_checked"] == rep["not_checked"]     # the page's list IS the list the program prints
