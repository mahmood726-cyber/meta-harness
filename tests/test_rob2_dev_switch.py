"""Plants for the DEV-only prompt switch (robgrade/rob2_typed.trial_sources local_store='open_cc'): a local-store full
text enters a prompt only for a DEV run, only when its PMC copy's OWN permissions are CC and the shared index registers
it CC; a TEST trial is never opened (scripts/rob2_dual._dev_set), and the default stays regex-only."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_dual as rd  # noqa: E402
import rob2_fulltext_acquire as acq  # noqa: E402
from robgrade import rob2_typed as rt  # noqa: E402

TEXT = "Allocation was concealed using a central web system. " * 60


BY = "http://creativecommons.org/licenses/by/4.0/"
BY_NC = "http://creativecommons.org/licenses/by-nc/4.0/"


def _store(tmp_path, monkeypatch, pmid, licence, via=None, url=BY):
    monkeypatch.setattr(acq, "STORE", str(tmp_path))
    d = tmp_path / pmid
    d.mkdir(parents=True)
    b = TEXT.encode("utf-8")
    (d / "text.txt").write_bytes(b)
    (d / "pmc.xml").write_text(f'<article><permissions><license xlink:href="{url}"/></permissions></article>',
                               encoding="utf-8")
    meta = {"pmid": pmid, "state": "HELD", "text_sha256": rt.sha(b), "licence": licence}
    if via:
        meta["via"] = via
    (d / "meta.json").write_text(json.dumps(meta), encoding="utf-8")


def _ft(srcs):
    return next(s for s in srcs if s["kind"] == "fulltext")


def test_default_is_regex_only(tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, "111", "CC")
    s = _ft(rt.trial_sources("no-such-topic", "111", ft_licences={"111": "CC"}, local_store=True))
    assert s["open_for_prompt"] is False


def test_PLANT_open_cc_needs_the_copy_and_the_index_to_be_cc(tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, "111", "CC")
    assert _ft(rt.trial_sources("t", "111", ft_licences={"111": "CC"}, local_store="open_cc"))["open_for_prompt"] is True
    assert _ft(rt.trial_sources("t", "111", ft_licences={}, local_store="open_cc"))["open_for_prompt"] is False
    _store(tmp_path / "x", monkeypatch, "222", "NOT_OPEN")
    assert _ft(rt.trial_sources("t", "222", ft_licences={"222": "CC"}, local_store="open_cc"))["open_for_prompt"] is False


def test_PLANT_an_unpaywall_copy_is_never_opened(tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, "333", "CC", via="Unpaywall OA copy")
    assert _ft(rt.trial_sources("t", "333", ft_licences={"333": "CC"}, local_store="open_cc"))["open_for_prompt"] is False


def test_PLANT_a_test_trial_is_never_in_the_dev_set():
    split = json.load(open(os.path.join(ROOT, "outputs", "robgrade", "split.json"), encoding="utf-8"))
    assert set(split["test"]).isdisjoint(rd._dev_set())
    assert len(rd._dev_set()) == len(split["dev"])


def test_PLANT_a_cc_by_nc_copy_is_never_opened_though_index_and_meta_say_cc(tmp_path, monkeypatch):
    # 2026-10-12 D8 incident: the broad licence test called CC BY-NC 'CC', and the text reached codex and agy
    _store(tmp_path, monkeypatch, "444", "CC", url=BY_NC)
    assert _ft(rt.trial_sources("t", "444", ft_licences={"444": "CC"}, local_store="open_cc"))["open_for_prompt"] is False


def test_PLANT_a_store_copy_wins_over_a_repo_copy_under_open_cc(tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, "555", "CC")
    monkeypatch.setattr(rt, "ROOT", str(tmp_path / "repo"))
    (tmp_path / "repo" / "cache" / "t").mkdir(parents=True)
    (tmp_path / "repo" / "cache" / "t" / "ft_555.txt").write_text("a different copy", encoding="utf-8")
    fts = [s for s in rt.trial_sources("t", "555", ft_licences={"555": "CC"}, local_store="open_cc")
           if s["kind"] == "fulltext"]
    assert len(fts) == 1 and fts[0]["local_store"] and fts[0]["open_for_prompt"] is True
