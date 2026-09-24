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
    """Load a SERVED script without writing bytecode: exec_module would drop docs/scripts/__pycache__/*.pyc into the tree
    CI publishes, and the deploy would serve a file no commit holds (seen on main from 1153beef: 1186 -> 1187 files)."""
    import sys
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    was, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = was
    return mod


def test_loading_a_served_verifier_writes_nothing_under_docs(tmp_path):
    served = DOCS / "scripts" / "audit_certificate_stdlib.py"
    cache = DOCS / "scripts" / "__pycache__"
    before = sorted(cache.glob("audit_certificate_stdlib*.pyc")) if cache.exists() else []
    _load(served, "_bytecode_probe")
    after = sorted(cache.glob("audit_certificate_stdlib*.pyc")) if cache.exists() else []
    assert after == before, "loading a served script wrote bytecode into the served tree"


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


def test_the_verifier_block_is_not_a_tracked_limitation_block():
    # every tracked block (absent/banner/result-change) on a page must be a limitation object
    # (tests/test_limitations_legacy_compare.py); naming a verifier is not a limitation. CI refused db59eea3 on exactly this.
    from harness.honest_ratchet import blocks
    out = page.render_page_verifier(_review())
    assert MARK in out and blocks(out) == []


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


def test_auditor_reads_the_certificate_its_three_siblings_and_the_pinned_code_and_nothing_else(auditor, capsys, monkeypatch):
    """'no input digest is compared with any file's bytes': record every file the served auditor opens -- the certificate,
    review.json / manifest.json / index.html beside it, the pinned modules; never records.json, a ledger or a held file."""
    opened = []
    real_rt, real_rb = Path.read_text, Path.read_bytes
    monkeypatch.setattr(Path, "read_text", lambda self, *a, **k: (opened.append(self.as_posix()), real_rt(self, *a, **k))[1])
    monkeypatch.setattr(Path, "read_bytes", lambda self, *a, **k: (opened.append(self.as_posix()), real_rb(self, *a, **k))[1])
    rdir = DOCS / "reviews" / "pcsk9-mace"
    cert = rdir / "CERTIFICATE.json"
    rc, out = _audit(auditor, capsys, cert, DOCS)
    assert rc == 0 and "RESULT REPRODUCED [scope: certificate + review.json + manifest.json + index.html]" in out, out
    blobs = json.loads(cert.read_text(encoding="utf-8"))["analysis_code_blobs"]
    siblings = {(rdir / n).resolve().as_posix() for n in ("review.json", "manifest.json", "index.html")}
    allowed = {cert.as_posix(), cert.resolve().as_posix()} | siblings | {(DOCS / p).as_posix() for p in blobs}
    seen = {Path(o).resolve().as_posix() if Path(o).name in ("review.json", "manifest.json", "index.html") else o for o in opened}
    assert siblings <= seen, "the links were not read"          # positive: the new checks really open their files
    assert seen <= allowed, sorted(seen - allowed)
    assert "NOT checked: " + "; ".join(auditor.NOT_CHECKED) in out


def _review_copy(tmp_path, slug="pcsk9-mace"):
    d = tmp_path / slug
    d.mkdir()
    for n in ("CERTIFICATE.json", "review.json", "manifest.json", "index.html"):
        shutil.copyfile(DOCS / "reviews" / slug / n, d / n)
    return d


def test_auditor_without_the_siblings_says_the_links_were_not_checked(auditor, capsys, tmp_path):
    """The limit 'without review.json, manifest.json and index.html ... none of the links is checked (the RESULT line
    then says so)': a forged review_sha256 with a recomputed release_sha256 passes ALONE -- and the RESULT line says the
    links were NOT CHECKED, so the pass cannot be read as a full one. Control: without the recompute it refuses."""
    cert = json.loads((DOCS / "reviews/pcsk9-mace/CERTIFICATE.json").read_text(encoding="utf-8"))
    forged = dict(cert, review_sha256="0" * 64)
    forged["release_sha256"] = auditor.sha256(auditor.canonical({k: v for k, v in forged.items() if k != "release_sha256"}))
    (tmp_path / "forged.json").write_text(json.dumps(forged), encoding="utf-8")
    rc, out = _audit(auditor, capsys, tmp_path / "forged.json")
    assert rc == 0 and "RESULT REPRODUCED [scope: certificate only; links to the numbers and the page NOT CHECKED" in out
    (tmp_path / "naive.json").write_text(json.dumps(dict(cert, review_sha256="0" * 64)), encoding="utf-8")
    rc, out = _audit(auditor, capsys, tmp_path / "naive.json")
    assert rc == 1 and "MISMATCH release_sha256" in out


@pytest.mark.parametrize("plant", ["served_number", "forged_certificate", "embedded_certificate", "manifest_review",
                                   "page_byte", "page_prints_other_release"])
def test_auditor_refuses_each_broken_link_beside_the_certificate(auditor, capsys, tmp_path, plant):
    d = _review_copy(tmp_path)
    rc, out = _audit(auditor, capsys, d / "CERTIFICATE.json")
    assert rc == 0 and "scope: certificate + review.json" in out, out          # the untouched copy passes
    cert = json.loads((d / "CERTIFICATE.json").read_text(encoding="utf-8"))
    rev = json.loads((d / "review.json").read_text(encoding="utf-8"))
    man = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    if plant == "served_number":         # a served number changes; nothing else does
        o = next(o for o in rev["outcomes"] if (o.get("result") or {}).get("estimate") is not None)
        o["result"]["estimate"] = o["result"]["estimate"] * 1.01
        (d / "review.json").write_text(json.dumps(rev, ensure_ascii=False), encoding="utf-8")
        want = "review_sha256: review.json does not hash"
    elif plant == "forged_certificate":  # the certificate's review_sha256 AND release_sha256 re-forged consistently
        cert["review_sha256"] = "0" * 64
        cert["release_sha256"] = auditor.sha256(auditor.canonical({k: v for k, v in cert.items() if k != "release_sha256"}))
        (d / "CERTIFICATE.json").write_text(json.dumps(cert), encoding="utf-8")
        want = "review_sha256: review.json does not hash"
    elif plant == "embedded_certificate":
        rev["reproduction"]["certificate"]["protocol_sha"] = "0" * 40
        (d / "review.json").write_text(json.dumps(rev, ensure_ascii=False), encoding="utf-8")
        want = "embedded certificate differs"
    elif plant == "manifest_review":
        man["review_sha256"] = "0" * 64
        (d / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
        want = "manifest.json review_sha256"
    elif plant == "page_byte":
        (d / "index.html").write_bytes((d / "index.html").read_bytes() + b" ")
        want = "index.html does not hash"
    else:                                 # the page prints another release, and its manifest digest is updated to match
        html = (d / "index.html").read_text(encoding="utf-8").replace(cert["release_sha256"], "f" * 64)
        (d / "index.html").write_bytes(html.encode("utf-8"))
        man["html_sha256"] = hashlib.sha256(html.encode("utf-8")).hexdigest()
        (d / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
        want = "index.html prints release_sha256"
    rc, out = _audit(auditor, capsys, d / "CERTIFICATE.json")
    assert rc == 1 and want in out, (plant, out[-1500:])


def test_auditor_limit_a_page_and_manifest_changed_together_still_pass(auditor, capsys, tmp_path):
    """NOT_CHECKED item 1, demonstrated: change what the page SAYS (a word in its body) and update manifest.json's
    html_sha256 to match -- the auditor still reports REPRODUCED. Only re-rendering from review.json catches this."""
    d = _review_copy(tmp_path)
    html = (d / "index.html").read_text(encoding="utf-8")
    assert "Reproducibility" in html
    html = html.replace("Reproducibility", "Reprod-ucibility", 1)
    (d / "index.html").write_bytes(html.encode("utf-8"))
    man = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    man["html_sha256"] = hashlib.sha256(html.encode("utf-8")).hexdigest()
    (d / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
    rc, out = _audit(auditor, capsys, d / "CERTIFICATE.json")
    assert rc == 0 and "RESULT REPRODUCED [scope: certificate + review.json" in out


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
    # The property is WHAT it reads and WHICH rows it recomputes, not the live verdict: a verifier fix that makes the served
    # bundle FAIL for an unrelated, legitimate reason (enforcement-gate 1fa77f2c: FREEDOM-CVO PARTIAL_TABLE_BINDING) must
    # not break this test. It only requires that the run completed with a verdict (a Refusal would raise).
    assert rep["verdict"] in ("PASS", "FAIL"), rep
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
