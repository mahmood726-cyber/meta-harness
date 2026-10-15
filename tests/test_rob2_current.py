"""Offline replay contracts; synthetic identifiers are confined to fixtures."""
import importlib
import json
import copy

import pytest


def test_redaction_preserves_machine_codes_that_coincidentally_match_source(replay):
    obj = {"disagreements": ["1.1"], "answer_provenance": {"1.1": "unavailable"},
           "overall": {"missing_domains": ["D1"]},
           "domains": {"D1": {"domain": "D1", "ni": {"ni_questions": ["1.1"],
                        "decisive_ni_questions": ["1.1"]}}}}
    original = copy.deepcopy(obj)
    replay.redact_remaining_closed_text(obj, {"sources": [
        {"id": "closed", "kind": "fulltext", "licence": "NOT_CC",
         "sha256": "hash", "text": "1.1 unavailable D1"}]})
    assert obj == original


def test_written_object_redacts_all_closed_quotes_and_keeps_cc(replay, monkeypatch):
    closed = ["Private title", "Xu", "Z", "Unpublished wording"]
    cc = "Reusable CC quotation"
    sources = [{"id": "closed", "kind": "fulltext", "licence": "NOT_CC",
                "text": " | ".join(closed), "sha256": "closed-hash"},
               {"id": "open", "kind": "fulltext", "licence": "CC-BY",
                "text": cc, "sha256": "open-hash"}]
    def answer(span, source):
        return {"answer": "Y", "span": span, "source_ref": source,
                "source_sha256": sources[source == "open"]["sha256"]}
    obj = {"domains": {"D1": {"answers": {"1.1": answer(closed[0], "closed")}}},
           "typed_conflicts": [{"question": "1.1", "regex": answer(closed[1], "closed")},
                               {"question": "1.2", "regex": answer(cc, "open")}],
           "extra": {"quote": closed[2], "nested": [closed[3]]}, "sha256": "old"}
    item = {"key": "sample::1::primary", "pmid": "1", "outcome": "primary", "sources": sources}
    monkeypatch.setattr(replay.rd, "_j", lambda _: {item["key"]: {}})
    monkeypatch.setattr(replay.rd, "prefetch_registry", lambda _: None)
    monkeypatch.setattr(replay.rd, "items", lambda *_: [item])
    monkeypatch.setattr(replay.rd, "process", lambda *_: (copy.deepcopy(obj), {}))
    replay.main()  # Real frozen redactor and real JSON writer, neither mocked.
    written = json.loads((replay.ROOT / "outputs/robgrade/rob2_current/sample.json").read_text())
    def strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for key, child in value.items():
                yield key
                yield from strings(child)
        elif isinstance(value, list):
            for child in value:
                yield from strings(child)
    assert not any(quote in text for text in strings(written) for quote in closed)
    trial = written["trials"]["1"]
    regex = trial["typed_conflicts"][0]["regex"]
    assert regex["span"] is None
    assert regex["source_sha256"] == "closed-hash"
    assert regex["span_redacted"] == {
        "why": "the source text is not CC-licensed: the span is not published",
        "span_sha256": replay.rd.rt.sha(closed[1]),
        "start": sources[0]["text"].find(closed[1]), "length": len(closed[1])}
    assert trial["typed_conflicts"][1]["regex"]["span"] == cc
    digest = trial.pop("sha256")
    assert digest == replay.rd.rt.sha(json.dumps(trial, sort_keys=True, ensure_ascii=False))


@pytest.fixture
def replay(tmp_path, monkeypatch):
    module = importlib.import_module("scripts.rob2_current")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setenv("ROBGRADE_LOCAL_FT", "1")
    monkeypatch.setenv("ROBGRADE_DEV_OPEN_CC", "1")
    return module


@pytest.mark.parametrize("setting", ["ROBGRADE_LOCAL_FT", "ROBGRADE_DEV_OPEN_CC"])
@pytest.mark.parametrize("value", [None, "", "0", "true", "01", "1 ", "2"])
def test_refuses_unless_both_exactly_one(replay, monkeypatch, setting, value):
    if value is None:
        monkeypatch.delenv(setting)
    else:
        monkeypatch.setenv(setting, value)
    monkeypatch.setattr(replay.rd, "prefetch_registry", lambda *_: pytest.fail("read before gate"))
    with pytest.raises(SystemExit, match=setting):
        replay.main()
    assert not list(replay.ROOT.rglob("*"))


def test_replays_manifest_redacts_compares_and_only_writes_current(replay, monkeypatch, capsys):
    root = replay.ROOT
    runs = {"sample::1::primary": {}, "sample::2::primary": {}}
    manifest = root / "registry/model_proposals/rob2_dual_runs.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps(runs), encoding="utf-8")
    frozen = root / "outputs/robgrade/rob2"
    for directory, trials in [(frozen, {"1": {"redacted": True}}),
                              (frozen / "dev", {"2": {"old": True}})]:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "sample.json").write_text(json.dumps({
            "outcome": "primary", "trials": trials}), encoding="utf-8")
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    calls = []
    monkeypatch.setattr(replay.rd, "prefetch_registry", lambda groups: calls.append(groups))

    def items(slug, pmids):
        assert calls == [[("sample", ["1", "2"])]]
        return [{"slug": slug, "pmid": p, "outcome": "primary",
                 "key": f"{slug}::{p}::primary"} for p in pmids]

    def process(item, records, live, pools):
        assert records == runs and live is False and pools == {}
        calls.append(item["key"])
        return {"closed": "must be removed"}, records[item["key"]]

    def redact(obj, item):
        obj.clear()
        obj["redacted"] = True

    monkeypatch.setattr(replay.rd, "items", items)
    monkeypatch.setattr(replay.rd, "process", process)
    monkeypatch.setattr(replay.rd, "redact_closed_spans", redact)
    monkeypatch.setattr(replay.rd, "_call", lambda *_: pytest.fail("model call"))
    replay.main()
    target = root / "outputs/robgrade/rob2_current/sample.json"
    assert json.loads(target.read_text(encoding="utf-8")) == {
        "slug": "sample", "family": replay.rd.rf.FAMILY, "outcome": "primary",
        "trials": {"1": {"redacted": True}, "2": {"redacted": True}},
        "generated_by": "scripts/rob2_current.py (replay, no model call)",
    }
    assert all(p.read_bytes() == content for p, content in before.items())
    assert {p for p in root.rglob("*") if p.is_file()} - before.keys() == {target}
    output = capsys.readouterr().out
    assert "sample 1 equals committed: True" in output
    assert "sample 2 equals committed: False" in output
    assert "reproduced 1 of 2" in output
