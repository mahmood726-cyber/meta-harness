"""AMENDMENT A1 to the pre-registered NI scorer (signed: Mahmood via Dispatch, 12 Oct 2026, SIGNING_PACKET_NI.md item 4;
outputs/robgrade/AMENDMENTS.json). Real git, no mocks: the pre-registered plants mocked frozen_object, which is how the
cp1252 false refusal went unseen."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_ni_score as sc  # noqa: E402

SPAN = "Among 11 052 patients who were randomized, 10 520 (95.2%) were followed — café"
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def _git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=/dev/null", *a], check=True, env=ENV,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


def _repo(tmp_path):
    repo = tmp_path / "r"
    (repo / "outputs" / "robgrade" / "rob2").mkdir(parents=True)
    (repo / "scripts").mkdir()
    doc = {"trials": {"1": {"domains": {"D3": {"answers": {"3.1": {"answer": "PY", "span": SPAN}}}}}}}
    (repo / "outputs" / "robgrade" / "rob2" / "s.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    (repo / "scripts" / "rob2_ni_score.py").write_text("v1\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "prereg")
    return repo, _git(repo, "rev-parse", "HEAD")


def test_PLANT_frozen_object_decodes_utf8_from_real_git(tmp_path, monkeypatch):
    repo, sha = _repo(tmp_path)
    monkeypatch.setattr(sc, "ROOT", str(repo))
    assert sc.frozen_object(sha, "s")["trials"]["1"]["domains"]["D3"]["answers"]["3.1"]["span"] == SPAN


def _amend(repo, sha, signed=True, to_blob=None):
    (repo / "scripts" / "rob2_ni_score.py").write_text("v2 amended\n", encoding="utf-8")
    entry = {"id": "A1", "file": "scripts/rob2_ni_score.py", "prereg": sha,
             "from_blob": _git(repo, "rev-parse", f"{sha}:scripts/rob2_ni_score.py"),
             "to_blob": to_blob or _git(repo, "hash-object", "--", "scripts/rob2_ni_score.py")}
    if signed:
        entry["signed"] = {"by": "Mahmood", "via": "Dispatch", "date": "2026-10-12"}
    (repo / "outputs" / "robgrade" / "AMENDMENTS.json").write_text(json.dumps({"amendments": [entry]}), encoding="utf-8")


def _use(monkeypatch, repo):
    monkeypatch.setattr(sc, "ROOT", str(repo))
    monkeypatch.setattr(sc, "AMENDMENTS", str(repo / "outputs" / "robgrade" / "AMENDMENTS.json"))


def test_PLANT_a_signed_declared_amendment_is_accepted(tmp_path, monkeypatch):
    repo, sha = _repo(tmp_path)
    _amend(repo, sha)
    _use(monkeypatch, repo)
    assert sc.declared(sha, "scripts/rob2_ni_score.py") is True


def test_PLANT_an_unsigned_amendment_is_refused(tmp_path, monkeypatch):
    repo, sha = _repo(tmp_path)
    _amend(repo, sha, signed=False)
    _use(monkeypatch, repo)
    assert sc.declared(sha, "scripts/rob2_ni_score.py") is False


def test_PLANT_a_file_edited_after_its_amendment_is_refused(tmp_path, monkeypatch):
    repo, sha = _repo(tmp_path)
    _amend(repo, sha)
    (repo / "scripts" / "rob2_ni_score.py").write_text("v3 edited after the amendment\n", encoding="utf-8")
    _use(monkeypatch, repo)
    assert sc.declared(sha, "scripts/rob2_ni_score.py") is False


def test_PLANT_no_amendments_file_means_no_amendment(tmp_path, monkeypatch):
    repo, sha = _repo(tmp_path)
    _use(monkeypatch, repo)
    assert sc.declared(sha, "scripts/rob2_ni_score.py") is False
